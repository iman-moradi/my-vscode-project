"""
محاسبات آمار تعمیرات - نسخه نهایی و کاملاً ایمن
با تطبیق کامل با ساختار دیتابیس واقعی
"""

from PySide6.QtCore import QObject
import jdatetime
from datetime import datetime, timedelta
from utils.jalali_date_widget import jalali_to_gregorian

class RepairCalculator(QObject):
    """کلاس محاسبات آمار تعمیرات - نسخه نهایی"""
    
    def __init__(self, data_manager):
        super().__init__()
        self.data_manager = data_manager
    
    def get_repair_summary(self, start_date, end_date):
        """دریافت خلاصه تعمیرات در بازه زمانی - با تطبیق ساختار واقعی"""
        # تبدیل تاریخ‌های شمسی به میلادی
        start_date_greg = self._convert_date_for_query(start_date)
        end_date_greg = self._convert_date_for_query(end_date)
        
        if not start_date_greg or not end_date_greg:
            return self._get_default_summary()
        
        # کوئری سازگار با ساختار واقعی دیتابیس
        query = """
        SELECT 
            COUNT(*) as total_repairs,
            SUM(CASE WHEN r.status = 'تعمیر شده' OR r.status = 'تکمیل شده' THEN 1 ELSE 0 END) as completed,
            SUM(CASE WHEN r.status = 'شروع شده' OR r.status = 'در حال تعمیر' THEN 1 ELSE 0 END) as in_progress,
            SUM(CASE WHEN r.status = 'لغو شده' OR r.status = 'انصراف' THEN 1 ELSE 0 END) as cancelled,
            AVG(r.total_cost) as avg_cost,
            SUM(r.total_cost) as total_cost,
            AVG(r.labor_cost) as avg_labor,
            SUM(r.labor_cost) as total_labor,
            SUM(CASE WHEN r.repair_type = 'داخلی' OR r.repair_type = 'تعمیر داخلی' THEN 1 ELSE 0 END) as internal_repairs,
            SUM(CASE WHEN r.repair_type = 'خارجی' OR r.repair_type = 'تعمیر خارجی' THEN 1 ELSE 0 END) as external_repairs
        FROM Repairs r
        WHERE r.repair_date >= ? AND r.repair_date <= ?
        """
        
        try:
            result = self.data_manager.db.fetch_one(query, (start_date_greg, end_date_greg))
            if result:
                return self._clean_result(result)
            return self._get_default_summary()
        except Exception as e:
            print(f"⚠️ خطا در دریافت خلاصه تعمیرات: {e}")
            return self._get_default_summary()
    
    def get_technician_performance(self, start_date, end_date):
        """دریافت عملکرد تعمیرکاران - نسخه واقعی"""
        start_date_greg = self._convert_date_for_query(start_date)
        end_date_greg = self._convert_date_for_query(end_date)
        
        if not start_date_greg or not end_date_greg:
            return []
        
        # کوئری با ساختار واقعی
        query = """
        SELECT 
            p.id as technician_id,
            CASE 
                WHEN p.first_name IS NOT NULL AND p.last_name IS NOT NULL THEN p.first_name || ' ' || p.last_name
                WHEN p.first_name IS NOT NULL THEN p.first_name
                WHEN p.last_name IS NOT NULL THEN p.last_name
                ELSE 'تعمیرکار ناشناس'
            END as technician_name,
            COUNT(r.id) as repair_count,
            SUM(r.total_cost) as total_revenue,
            AVG(r.total_cost) as avg_revenue,
            SUM(r.labor_cost) as total_labor,
            AVG(r.labor_cost) as avg_labor,
            SUM(CASE WHEN r.status IN ('تعمیر شده', 'تکمیل شده') THEN 1 ELSE 0 END) as completed_count
        FROM Repairs r
        LEFT JOIN Persons p ON r.technician_id = p.id
        WHERE r.repair_date >= ? AND r.repair_date <= ?
          AND r.technician_id IS NOT NULL
        GROUP BY r.technician_id
        HAVING COUNT(r.id) > 0
        ORDER BY total_revenue DESC
        """
        
        try:
            results = self.data_manager.db.fetch_all(query, (start_date_greg, end_date_greg))
            return self._clean_results(results)
        except Exception as e:
            print(f"⚠️ خطا در دریافت عملکرد تعمیرکاران: {e}")
            return []
    
    def get_failure_causes(self, start_date, end_date):
        """دریافت علل خرابی از پذیرش‌ها - نسخه واقعی"""
        start_date_greg = self._convert_date_for_query(start_date)
        end_date_greg = self._convert_date_for_query(end_date)
        
        if not start_date_greg or not end_date_greg:
            return []
        
        # کوئری ساده‌تر و مطمئن‌تر
        query = """
        SELECT 
            r.problem_description,
            COUNT(*) as count,
            AVG(r.estimated_cost) as avg_estimated_cost,
            MAX(r.reception_date) as last_reception
        FROM Receptions r
        WHERE r.reception_date >= ? AND r.reception_date <= ?
          AND r.problem_description IS NOT NULL
          AND TRIM(r.problem_description) != ''
        GROUP BY r.problem_description
        HAVING COUNT(*) > 0
        ORDER BY count DESC
        LIMIT 15
        """
        
        try:
            results = self.data_manager.db.fetch_all(query, (start_date_greg, end_date_greg))
            return results or []
        except Exception as e:
            print(f"⚠️ خطا در دریافت علل خرابی: {e}")
            return []
    
    def get_repair_trends(self, start_date, end_date, group_by='day'):
        """دریافت روند تعمیرات - نسخه ساده‌تر"""
        start_date_greg = self._convert_date_for_query(start_date)
        end_date_greg = self._convert_date_for_query(end_date)
        
        if not start_date_greg or not end_date_greg:
            return []
        
        # انتخاب فرمت گروه‌بندی ساده‌تر
        if group_by == 'day':
            date_format = "date(r.repair_date)"
        elif group_by == 'week':
            date_format = "strftime('%Y-%W', r.repair_date)"
        elif group_by == 'month':
            date_format = "strftime('%Y-%m', r.repair_date)"
        else:
            date_format = "date(r.repair_date)"
        
        query = f"""
        SELECT 
            {date_format} as period,
            COUNT(*) as repair_count,
            SUM(r.total_cost) as total_revenue,
            SUM(r.labor_cost) as total_labor,
            AVG(r.total_cost) as avg_revenue,
            SUM(CASE WHEN r.status IN ('تعمیر شده', 'تکمیل شده') THEN 1 ELSE 0 END) as completed_count
        FROM Repairs r
        WHERE r.repair_date >= ? AND r.repair_date <= ?
        GROUP BY {date_format}
        ORDER BY period
        """
        
        try:
            results = self.data_manager.db.fetch_all(query, (start_date_greg, end_date_greg))
            return results or []
        except Exception as e:
            print(f"⚠️ خطا در دریافت روند تعمیرات: {e}")
            return []
    
    def get_device_type_analysis(self, start_date, end_date):
        """تحلیل تعمیرات بر اساس نوع دستگاه - نسخه واقعی"""
        start_date_greg = self._convert_date_for_query(start_date)
        end_date_greg = self._convert_date_for_query(end_date)
        
        if not start_date_greg or not end_date_greg:
            return []
        
        # کوئری با استفاده از ساختار واقعی جدول Devices
        query = """
        SELECT 
            d.device_type,
            COUNT(r.id) as repair_count,
            SUM(rep.total_cost) as total_revenue,
            AVG(rep.total_cost) as avg_revenue,
            SUM(rep.labor_cost) as total_labor,
            AVG(rep.labor_cost) as avg_labor
        FROM Receptions rec
        LEFT JOIN Devices d ON rec.device_id = d.id
        LEFT JOIN Repairs rep ON rec.id = rep.reception_id
        WHERE rec.reception_date >= ? AND rec.reception_date <= ?
          AND rep.id IS NOT NULL
          AND d.device_type IS NOT NULL
        GROUP BY d.device_type
        ORDER BY repair_count DESC
        """
        
        try:
            results = self.data_manager.db.fetch_all(query, (start_date_greg, end_date_greg))
            return results or []
        except Exception as e:
            print(f"⚠️ خطا در تحلیل دستگاه‌ها: {e}")
            return []
    
    def get_repair_parts_analysis(self, start_date, end_date):
        """تحلیل قطعات مصرفی در تعمیرات"""
        start_date_greg = self._convert_date_for_query(start_date)
        end_date_greg = self._convert_date_for_query(end_date)
        
        if not start_date_greg or not end_date_greg:
            return []
        
        # ابتدا بررسی کنیم آیا جدول Repair_Parts وجود دارد
        try:
            check_query = "SELECT name FROM sqlite_master WHERE type='table' AND name='Repair_Parts'"
            exists = self.data_manager.db.fetch_one(check_query)
            
            if not exists:
                return []
            
            query = """
            SELECT 
                p.part_name,
                p.category,
                SUM(rp.quantity) as total_quantity,
                SUM(rp.total_price) as total_cost,
                COUNT(DISTINCT rp.repair_id) as repair_count
            FROM Repair_Parts rp
            LEFT JOIN Parts p ON rp.part_id = p.id
            LEFT JOIN Repairs r ON rp.repair_id = r.id
            WHERE r.repair_date >= ? AND r.repair_date <= ?
            GROUP BY rp.part_id
            HAVING SUM(rp.quantity) > 0
            ORDER BY total_quantity DESC
            LIMIT 20
            """
            
            results = self.data_manager.db.fetch_all(query, (start_date_greg, end_date_greg))
            return results or []
        except Exception as e:
            print(f"⚠️ خطا در تحلیل قطعات (ممکن است جدول وجود نداشته باشد): {e}")
            return []
    
    def get_repair_services_analysis(self, start_date, end_date):
        """تحلیل خدمات ارائه شده در تعمیرات"""
        start_date_greg = self._convert_date_for_query(start_date)
        end_date_greg = self._convert_date_for_query(end_date)
        
        if not start_date_greg or not end_date_greg:
            return []
        
        # بررسی وجود جدول Repair_Services
        try:
            check_query = "SELECT name FROM sqlite_master WHERE type='table' AND name='Repair_Services'"
            exists = self.data_manager.db.fetch_one(check_query)
            
            if not exists:
                return []
            
            query = """
            SELECT 
                sf.service_name,
                sf.category,
                SUM(rs.quantity) as total_quantity,
                SUM(rs.total_price) as total_revenue,
                COUNT(DISTINCT rs.repair_id) as repair_count
            FROM Repair_Services rs
            LEFT JOIN ServiceFees sf ON rs.service_id = sf.id
            LEFT JOIN Repairs r ON rs.repair_id = r.id
            WHERE r.repair_date >= ? AND r.repair_date <= ?
            GROUP BY rs.service_id
            HAVING SUM(rs.quantity) > 0
            ORDER BY total_revenue DESC
            LIMIT 15
            """
            
            results = self.data_manager.db.fetch_all(query, (start_date_greg, end_date_greg))
            return results or []
        except Exception as e:
            print(f"⚠️ خطا در تحلیل خدمات: {e}")
            return []
    
    def get_repair_time_analysis(self, start_date, end_date):
        """تحلیل زمان تعمیرات - نسخه ساده"""
        start_date_greg = self._convert_date_for_query(start_date)
        end_date_greg = self._convert_date_for_query(end_date)
        
        if not start_date_greg or not end_date_greg:
            return []
        
        # کوئری ساده برای تحلیل زمان
        query = """
        SELECT 
            CASE 
                WHEN r.status IN ('تعمیر شده', 'تکمیل شده') THEN 'تکمیل شده'
                WHEN r.status IN ('شروع شده', 'در حال تعمیر') THEN 'در جریان'
                WHEN r.status IN ('لغو شده', 'انصراف') THEN 'لغو شده'
                ELSE 'سایر'
            END as status_group,
            COUNT(*) as repair_count,
            AVG(r.total_cost) as avg_cost,
            SUM(r.total_cost) as total_cost
        FROM Repairs r
        WHERE r.repair_date >= ? AND r.repair_date <= ?
        GROUP BY status_group
        ORDER BY repair_count DESC
        """
        
        try:
            results = self.data_manager.db.fetch_all(query, (start_date_greg, end_date_greg))
            return results or []
        except Exception as e:
            print(f"⚠️ خطا در تحلیل زمان: {e}")
            return []
    
    def get_recent_repairs(self, start_date, end_date, limit=20):
        """دریافت آخرین تعمیرات - نسخه واقعی"""
        start_date_greg = self._convert_date_for_query(start_date)
        end_date_greg = self._convert_date_for_query(end_date)
        
        if not start_date_greg or not end_date_greg:
            return []
        
        # کوئری ساده و مطمئن
        query = """
        SELECT 
            r.id,
            r.repair_date,
            rec.reception_number,
            d.model as device_model,
            p.first_name || ' ' || p.last_name as technician_name,
            r.total_cost,
            r.status,
            r.repair_type,
            d.device_type,
            d.brand
        FROM Repairs r
        LEFT JOIN Receptions rec ON r.reception_id = rec.id
        LEFT JOIN Devices d ON rec.device_id = d.id
        LEFT JOIN Persons p ON r.technician_id = p.id
        WHERE r.repair_date >= ? AND r.repair_date <= ?
        ORDER BY r.repair_date DESC, r.id DESC
        LIMIT ?
        """
        
        try:
            results = self.data_manager.db.fetch_all(query, (start_date_greg, end_date_greg, limit))
            return results or []
        except Exception as e:
            print(f"⚠️ خطا در دریافت آخرین تعمیرات: {e}")
            return []
    
    def _convert_date_for_query(self, jalali_date_str):
        """تبدیل تاریخ شمسی به میلادی برای کوئری - نسخه ایمن"""
        if not jalali_date_str:
            return None
        
        try:
            # استفاده از تابع استاندارد تبدیل
            return jalali_to_gregorian(jalali_date_str)
        except Exception as e:
            print(f"⚠️ خطا در تبدیل تاریخ {jalali_date_str}: {e}")
            return None
    
    def _get_default_summary(self):
        """خلاصه پیش‌فرض در صورت خطا"""
        return {
            'total_repairs': 0,
            'completed': 0,
            'in_progress': 0,
            'cancelled': 0,
            'avg_cost': 0,
            'total_cost': 0,
            'avg_labor': 0,
            'total_labor': 0,
            'internal_repairs': 0,
            'external_repairs': 0
        }
    
    def _clean_result(self, result):
        """پاکسازی و تبدیل مقادیر NULL"""
        if not result:
            return self._get_default_summary()
        
        cleaned = {}
        for key, value in result.items():
            if value is None:
                cleaned[key] = 0
            else:
                cleaned[key] = float(value) if isinstance(value, (int, float)) else value
        
        return cleaned
    
    def _clean_results(self, results):
        """پاکسازی لیست نتایج"""
        if not results:
            return []
        
        cleaned_results = []
        for result in results:
            cleaned = {}
            for key, value in result.items():
                if value is None:
                    cleaned[key] = 0 if key.endswith('_count') or key.startswith('total_') or key.startswith('avg_') else ''
                else:
                    cleaned[key] = value
            cleaned_results.append(cleaned)
        
        return cleaned_results
    
    def get_quick_stats(self):
        """آمار سریع تعمیرات (برای داشبورد)"""
        try:
            # تاریخ 30 روز گذشته
            end_date = jdatetime.datetime.now()
            start_date = end_date - timedelta(days=30)
            
            start_date_str = start_date.strftime('%Y/%m/%d')
            end_date_str = end_date.strftime('%Y/%m/%d')
            
            summary = self.get_repair_summary(start_date_str, end_date_str)
            
            # آمار اضافی
            query_today = """
            SELECT COUNT(*) as today_count 
            FROM Repairs 
            WHERE date(repair_date) = date('now')
            """
            
            query_this_week = """
            SELECT COUNT(*) as week_count 
            FROM Repairs 
            WHERE repair_date >= date('now', '-7 days')
            """
            
            today_result = self.data_manager.db.fetch_one(query_today) or {'today_count': 0}
            week_result = self.data_manager.db.fetch_one(query_this_week) or {'week_count': 0}
            
            return {
                'last_30_days': summary,
                'today': today_result['today_count'],
                'this_week': week_result['week_count'],
                'completion_rate': (summary['completed'] / summary['total_repairs'] * 100) if summary['total_repairs'] > 0 else 0
            }
        except Exception as e:
            print(f"⚠️ خطا در دریافت آمار سریع: {e}")
            return {
                'last_30_days': self._get_default_summary(),
                'today': 0,
                'this_week': 0,
                'completion_rate': 0
            }