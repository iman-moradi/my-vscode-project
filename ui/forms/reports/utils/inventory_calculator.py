# ui/forms/reports/utils/inventory_calculator.py
"""
ماژول کمکی برای محاسبات انبار
"""

from PySide6.QtCore import QDate
from utils.date_utils import jalali_to_gregorian, gregorian_to_jalali


class InventoryCalculator:
    """کلاس محاسبه کننده داده‌های انبار"""
    
    def __init__(self, data_manager):
        self.data_manager = data_manager
        self.warehouse_types = [
            'قطعات نو',
            'قطعات دست دوم', 
            'لوازم نو',
            'لوازم دست دوم'
        ]
    
    def get_inventory_summary(self):
        """دریافت خلاصه وضعیت انبار"""
        try:
            summary = {}
            total_items = 0
            total_value = 0
            
            for warehouse_type in self.warehouse_types:
                stats = self.get_warehouse_stats(warehouse_type)
                summary[warehouse_type] = stats
                
                total_items += stats.get('total_items', 0)
                total_value += stats.get('total_value', 0)
            
            # محاسبه هشدارهای موجودی کم
            low_stock_alerts = self.get_low_stock_alerts()
            
            return {
                'warehouses': summary,
                'total_items': total_items,
                'total_value': total_value,
                'low_stock_alerts': low_stock_alerts
            }
            
        except Exception as e:
            print(f"❌ خطا در محاسبه خلاصه انبار: {e}")
            return {
                'warehouses': {},
                'total_items': 0,
                'total_value': 0,
                'low_stock_alerts': []
            }
    
    def get_warehouse_stats(self, warehouse_type):
        """دریافت آمار یک انبار خاص"""
        try:
            # تعداد کل آیتم‌ها
            total_items_query = self._get_count_query(warehouse_type)
            total_items = self._execute_scalar_query(total_items_query) or 0
            
            # تعداد آیتم‌های موجود
            available_items_query = self._get_count_query(warehouse_type, "status = 'موجود'")
            available_items = self._execute_scalar_query(available_items_query) or 0
            
            # مقدار کل (ارزش)
            total_value_query = self._get_value_query(warehouse_type)
            total_value = self._execute_scalar_query(total_value_query) or 0
            
            # مقدار موجودی
            available_value_query = self._get_value_query(warehouse_type, "status = 'موجود'")
            available_value = self._execute_scalar_query(available_value_query) or 0
            
            return {
                'warehouse_type': warehouse_type,
                'total_items': total_items,
                'available_items': available_items,
                'total_value': total_value,
                'available_value': available_value,
                'availability_rate': (available_items / total_items * 100) if total_items > 0 else 0
            }
            
        except Exception as e:
            print(f"❌ خطا در دریافت آمار انبار {warehouse_type}: {e}")
            return {
                'warehouse_type': warehouse_type,
                'total_items': 0,
                'available_items': 0,
                'total_value': 0,
                'available_value': 0,
                'availability_rate': 0
            }
    
    def _get_count_query(self, warehouse_type, where_clause=""):
        """ایجاد کوئری شمارش بر اساس نوع انبار"""
        table_map = {
            'قطعات نو': 'NewPartsWarehouse',
            'قطعات دست دوم': 'UsedPartsWarehouse',
            'لوازم نو': 'NewAppliancesWarehouse',
            'لوازم دست دوم': 'UsedAppliancesWarehouse'
        }
        
        table_name = table_map.get(warehouse_type)
        if not table_name:
            return ""
        
        query = f"SELECT COUNT(*) FROM {table_name}"
        if where_clause:
            query += f" WHERE {where_clause}"
        
        return query
    
    def _get_value_query(self, warehouse_type, where_clause=""):
        """ایجاد کوئری مقدار بر اساس نوع انبار"""
        table_map = {
            'قطعات نو': 'NewPartsWarehouse',
            'قطعات دست دوم': 'UsedPartsWarehouse',
            'لوازم نو': 'NewAppliancesWarehouse',
            'لوازم دست دوم': 'UsedAppliancesWarehouse'
        }
        
        table_name = table_map.get(warehouse_type)
        if not table_name:
            return ""
        
        query = f"SELECT SUM(quantity * sale_price) FROM {table_name}"
        if where_clause:
            query += f" WHERE {where_clause}"
        
        return query
    
    def _execute_scalar_query(self, query):
        """اجرای کوئری اسکالر و برگرداندن مقدار"""
        try:
            if not query:
                return None
            result = self.data_manager.db.fetch_one(query)
            return list(result.values())[0] if result else None
        except Exception as e:
            print(f"❌ خطا در اجرای کوئری اسکالر: {e}")
            return None
    
    def get_low_stock_alerts(self, threshold=5):
        """دریافت هشدارهای موجودی کم"""
        try:
            alerts = []
            
            # بررسی قطعات نو با موجودی کم
            query_parts = """
            SELECT 
                npw.id,
                p.part_name,
                p.part_code,
                npw.quantity,
                p.min_stock,
                npw.location
            FROM NewPartsWarehouse npw
            JOIN Parts p ON npw.part_id = p.id
            WHERE npw.status = 'موجود' 
            AND npw.quantity <= p.min_stock
            """
            
            low_parts = self.data_manager.db.fetch_all(query_parts)
            for part in low_parts:
                alerts.append({
                    'type': 'قطعات نو',
                    'item_name': part.get('part_name', ''),
                    'current_stock': part.get('quantity', 0),
                    'min_stock': part.get('min_stock', 0),
                    'location': part.get('location', ''),
                    'severity': 'high' if part.get('quantity', 0) == 0 else 'medium'
                })
            
            return alerts[:10]  # فقط 10 هشدار اول
            
        except Exception as e:
            print(f"❌ خطا در دریافت هشدارهای موجودی کم: {e}")
            return []
    
    def get_inventory_movements(self, start_date=None, end_date=None):
        """دریافت حرکات انبار"""
        try:
            query = """
            SELECT 
                it.transaction_type,
                it.warehouse_type,
                it.item_id,
                it.quantity,
                it.unit_price,
                it.total_price,
                it.transaction_date,
                it.description,
                CASE 
                    WHEN it.warehouse_type = 'قطعات نو' THEN p.part_name
                    WHEN it.warehouse_type = 'لوازم نو' THEN naw.model
                    WHEN it.warehouse_type = 'قطعات دست دوم' THEN p2.part_name
                    WHEN it.warehouse_type = 'لوازم دست دوم' THEN uaw.model
                    ELSE 'نامشخص'
                END as item_name
            FROM InventoryTransactions it
            LEFT JOIN NewPartsWarehouse npw ON it.item_id = npw.id AND it.warehouse_type = 'قطعات نو'
            LEFT JOIN Parts p ON npw.part_id = p.id
            LEFT JOIN NewAppliancesWarehouse naw ON it.item_id = naw.id AND it.warehouse_type = 'لوازم نو'
            LEFT JOIN UsedPartsWarehouse upw ON it.item_id = upw.id AND it.warehouse_type = 'قطعات دست دوم'
            LEFT JOIN Parts p2 ON upw.part_id = p2.id
            LEFT JOIN UsedAppliancesWarehouse uaw ON it.item_id = uaw.id AND it.warehouse_type = 'لوازم دست دوم'
            WHERE 1=1
            """
            
            params = []
            if start_date and end_date:
                start_greg = jalali_to_gregorian(start_date, "%Y-%m-%d")
                end_greg = jalali_to_gregorian(end_date, "%Y-%m-%d")
                query += " AND DATE(it.transaction_date) BETWEEN ? AND ?"
                params.extend([start_greg, end_greg])
            
            query += " ORDER BY it.transaction_date DESC LIMIT 50"
            
            movements = self.data_manager.db.fetch_all(query, params)
            
            # تبدیل تاریخ به شمسی
            for movement in movements:
                if movement.get('transaction_date'):
                    movement['transaction_date_shamsi'] = gregorian_to_jalali(
                        movement['transaction_date']
                    )
            
            return movements
            
        except Exception as e:
            print(f"❌ خطا در دریافت حرکات انبار: {e}")
            return []
    
    def get_warehouse_details(self, warehouse_type):
        """دریافت جزئیات یک انبار خاص"""
        try:
            table_map = {
                'قطعات نو': 'NewPartsWarehouse',
                'قطعات دست دوم': 'UsedPartsWarehouse',
                'لوازم نو': 'NewAppliancesWarehouse',
                'لوازم دست دوم': 'UsedAppliancesWarehouse'
            }
            
            table_name = table_map.get(warehouse_type)
            if not table_name:
                return []
            
            if warehouse_type == 'قطعات نو':
                query = """
                SELECT 
                    npw.*,
                    p.part_code,
                    p.part_name,
                    p.category,
                    p.brand,
                    p.unit,
                    p.min_stock,
                    p.max_stock,
                    per.full_name as supplier_name
                FROM NewPartsWarehouse npw
                LEFT JOIN Parts p ON npw.part_id = p.id
                LEFT JOIN Persons per ON npw.supplier_id = per.id
                WHERE npw.status = 'موجود'
                ORDER BY npw.quantity ASC, p.part_name
                """
                
            elif warehouse_type == 'قطعات دست دوم':
                query = """
                SELECT 
                    upw.*,
                    p.part_code,
                    p.part_name,
                    p.category,
                    p.brand,
                    p.unit,
                    p.min_stock,
                    p.max_stock
                FROM UsedPartsWarehouse upw
                LEFT JOIN Parts p ON upw.part_id = p.id
                WHERE upw.status = 'موجود'
                ORDER BY upw.quantity ASC, p.part_name
                """
                
            elif warehouse_type == 'لوازم نو':
                query = """
                SELECT 
                    naw.*,
                    dc.name as device_type_name,
                    b.name as brand_name,
                    per.full_name as supplier_name
                FROM NewAppliancesWarehouse naw
                LEFT JOIN DeviceCategories_name dc ON naw.device_type_id = dc.id
                LEFT JOIN Brands b ON naw.brand_id = b.id
                LEFT JOIN Persons per ON naw.supplier_id = per.id
                WHERE naw.status = 'موجود'
                ORDER BY naw.quantity ASC, naw.model
                """
                
            elif warehouse_type == 'لوازم دست دوم':
                query = """
                SELECT 
                    uaw.*,
                    dc.name as device_type_name,
                    b.name as brand_name,
                    per.full_name as source_name
                FROM UsedAppliancesWarehouse uaw
                LEFT JOIN DeviceCategories_name dc ON uaw.device_type_id = dc.id
                LEFT JOIN Brands b ON uaw.brand_id = b.id
                LEFT JOIN Persons per ON uaw.source_person_id = per.id
                WHERE uaw.status = 'موجود'
                ORDER BY uaw.quantity ASC, uaw.model
                """
            
            return self.data_manager.db.fetch_all(query)
            
        except Exception as e:
            print(f"❌ خطا در دریافت جزئیات انبار {warehouse_type}: {e}")
            return []