# ui/forms/reports/utils/sales_calculator.py
"""
ماژول کمکی برای محاسبات فروش
"""

from PySide6.QtCore import QDate
from utils.jalali_date_widget import jalali_to_gregorian, gregorian_to_jalali


class SalesCalculator:
    """کلاس محاسبه کننده داده‌های فروش"""
    
    def __init__(self, data_manager):
        self.data_manager = data_manager
    
    def get_sales_summary(self, start_date=None, end_date=None):
        """دریافت خلاصه آمار فروش"""
        try:
            # تبدیل تاریخ‌ها به میلادی برای جستجو در دیتابیس
            start_greg = None
            end_greg = None
            
            if start_date:
                start_greg = jalali_to_gregorian(start_date, "%Y-%m-%d")
            if end_date:
                end_greg = jalali_to_gregorian(end_date, "%Y-%m-%d")
            
            # ۱. آمار کلی فروش
            general_stats = self.get_general_sales_stats(start_greg, end_greg)
            
            # ۲. تحلیل محصولات پرفروش
            top_products = self.get_top_products(start_greg, end_greg)
            
            # ۳. تحلیل مشتریان برتر
            top_customers = self.get_top_customers(start_greg, end_greg)
            
            # ۴. تحلیل سودآوری
            profitability_analysis = self.get_profitability_analysis(start_greg, end_greg)
            
            # ۵. مقایسه فروش انبارها
            warehouse_comparison = self.get_warehouse_sales_comparison(start_greg, end_greg)
            
            return {
                'general_stats': general_stats,
                'top_products': top_products,
                'top_customers': top_customers,
                'profitability_analysis': profitability_analysis,
                'warehouse_comparison': warehouse_comparison
            }
            
        except Exception as e:
            print(f"❌ خطا در محاسبه خلاصه فروش: {e}")
            return {
                'general_stats': {},
                'top_products': [],
                'top_customers': [],
                'profitability_analysis': {},
                'warehouse_comparison': []
            }
    
    def get_general_sales_stats(self, start_date=None, end_date=None):
        """دریافت آمار کلی فروش"""
        try:
            query = """
            SELECT 
                COUNT(*) as total_invoices,
                SUM(total) as total_sales,
                SUM(paid_amount) as total_paid,
                SUM(total - paid_amount) as total_credit,
                AVG(total) as avg_invoice_amount,
                COUNT(DISTINCT customer_id) as unique_customers,
                SUM(CASE WHEN payment_status IN ('پرداخت شده', 'نقدی') THEN total ELSE 0 END) as cash_sales,
                SUM(CASE WHEN payment_status = 'چک' THEN total ELSE 0 END) as check_sales,
                SUM(CASE WHEN payment_status = 'کارت' THEN total ELSE 0 END) as card_sales,
                SUM(CASE WHEN payment_status = 'نسیه' THEN total ELSE 0 END) as credit_sales
            FROM Invoices
            WHERE invoice_type IN ('فروش', 'خدمات')
            """
            
            params = []
            if start_date and end_date:
                query += " AND DATE(invoice_date) BETWEEN ? AND ?"
                params.extend([start_date, end_date])
            elif start_date:
                query += " AND DATE(invoice_date) >= ?"
                params.append(start_date)
            elif end_date:
                query += " AND DATE(invoice_date) <= ?"
                params.append(end_date)
            
            result = self.data_manager.db.fetch_one(query, params)
            
            if result:
                total_sales = result['total_sales'] or 0
                total_paid = result['total_paid'] or 0
                
                return {
                    'total_invoices': result['total_invoices'] or 0,
                    'total_sales': total_sales,
                    'total_paid': total_paid,
                    'total_credit': result['total_credit'] or 0,
                    'avg_invoice_amount': result['avg_invoice_amount'] or 0,
                    'unique_customers': result['unique_customers'] or 0,
                    'cash_sales': result['cash_sales'] or 0,
                    'check_sales': result['check_sales'] or 0,
                    'card_sales': result['card_sales'] or 0,
                    'credit_sales': result['credit_sales'] or 0,
                    'payment_completion_rate': (total_paid / total_sales * 100) if total_sales > 0 else 0
                }
            
            return {}
            
        except Exception as e:
            print(f"❌ خطا در دریافت آمار کلی فروش: {e}")
            return {}
    
    def get_top_products(self, start_date=None, end_date=None, limit=10):
        """دریافت محصولات پرفروش"""
        try:
            # فروش لوازم نو
            query_new_appliances = """
            SELECT 
                'لوازم نو' as category,
                naw.model as product_name,
                naw.device_type_id,
                dc.name as device_type,
                b.name as brand,
                COUNT(ii.id) as sale_count,
                SUM(ii.quantity) as total_quantity,
                SUM(ii.total_price) as total_sales_amount
            FROM InvoiceItems ii
            JOIN Invoices i ON ii.invoice_id = i.id
            JOIN NewAppliancesWarehouse naw ON ii.item_id = naw.id
            JOIN DeviceCategories_name dc ON naw.device_type_id = dc.id
            JOIN Brands b ON naw.brand_id = b.id
            WHERE ii.item_type = 'دستگاه'
            AND i.invoice_type IN ('فروش', 'خدمات')
            """
            
            # فروش لوازم دست دوم
            query_used_appliances = """
            SELECT 
                'لوازم دست دوم' as category,
                uaw.model as product_name,
                uaw.device_type_id,
                dc.name as device_type,
                b.name as brand,
                COUNT(ii.id) as sale_count,
                SUM(ii.quantity) as total_quantity,
                SUM(ii.total_price) as total_sales_amount
            FROM InvoiceItems ii
            JOIN Invoices i ON ii.invoice_id = i.id
            JOIN UsedAppliancesWarehouse uaw ON ii.item_id = uaw.id
            JOIN DeviceCategories_name dc ON uaw.device_type_id = dc.id
            JOIN Brands b ON uaw.brand_id = b.id
            WHERE ii.item_type = 'دستگاه'
            AND i.invoice_type IN ('فروش', 'خدمات')
            """
            
            # فروش قطعات نو
            query_new_parts = """
            SELECT 
                'قطعات نو' as category,
                p.part_name as product_name,
                p.category as device_type,
                p.brand,
                COUNT(ii.id) as sale_count,
                SUM(ii.quantity) as total_quantity,
                SUM(ii.total_price) as total_sales_amount
            FROM InvoiceItems ii
            JOIN Invoices i ON ii.invoice_id = i.id
            JOIN NewPartsWarehouse npw ON ii.item_id = npw.id
            JOIN Parts p ON npw.part_id = p.id
            WHERE ii.item_type = 'قطعه'
            AND i.invoice_type IN ('فروش', 'خدمات')
            """
            
            # فروش قطعات دست دوم
            query_used_parts = """
            SELECT 
                'قطعات دست دوم' as category,
                p.part_name as product_name,
                p.category as device_type,
                p.brand,
                COUNT(ii.id) as sale_count,
                SUM(ii.quantity) as total_quantity,
                SUM(ii.total_price) as total_sales_amount
            FROM InvoiceItems ii
            JOIN Invoices i ON ii.invoice_id = i.id
            JOIN UsedPartsWarehouse upw ON ii.item_id = upw.id
            JOIN Parts p ON upw.part_id = p.id
            WHERE ii.item_type = 'قطعه'
            AND i.invoice_type IN ('فروش', 'خدمات')
            """
            
            # اضافه کردن شرط تاریخ
            date_condition = ""
            params = []
            if start_date and end_date:
                date_condition = " AND DATE(i.invoice_date) BETWEEN ? AND ?"
                params.extend([start_date, end_date])
            
            # ترکیب تمام کوئری‌ها
            union_query = f"""
            {query_new_appliances} {date_condition}
            GROUP BY naw.model, naw.device_type_id, dc.name, b.name
            HAVING COUNT(ii.id) > 0
            
            UNION ALL
            
            {query_used_appliances} {date_condition}
            GROUP BY uaw.model, uaw.device_type_id, dc.name, b.name
            HAVING COUNT(ii.id) > 0
            
            UNION ALL
            
            {query_new_parts} {date_condition}
            GROUP BY p.part_name, p.category, p.brand
            HAVING COUNT(ii.id) > 0
            
            UNION ALL
            
            {query_used_parts} {date_condition}
            GROUP BY p.part_name, p.category, p.brand
            HAVING COUNT(ii.id) > 0
            
            ORDER BY total_sales_amount DESC
            LIMIT ?
            """
            
            params.append(limit)
            
            products = self.data_manager.db.fetch_all(union_query, params)
            
            # محاسبه سود برای هر محصول (بر اساس تفاوت قیمت خرید و فروش)
            for product in products:
                # اینجا می‌توانیم سود را با دسترسی به قیمت خرید محاسبه کنیم
                # فعلاً از یک درصد ثابت استفاده می‌کنیم
                sales_amount = product['total_sales_amount'] or 0
                profit_percentage = 25  # درصد سود فرضی
                product['estimated_profit'] = sales_amount * profit_percentage / 100
                product['profit_margin'] = profit_percentage
            
            return products
            
        except Exception as e:
            print(f"❌ خطا در دریافت محصولات پرفروش: {e}")
            return []
    
    def get_top_customers(self, start_date=None, end_date=None, limit=10):
        """دریافت مشتریان برتر"""
        try:
            query = """
            SELECT 
                p.id as customer_id,
                p.first_name || ' ' || p.last_name as customer_name,
                p.mobile,
                p.person_type,
                COUNT(i.id) as invoice_count,
                SUM(i.total) as total_purchases,
                SUM(i.paid_amount) as total_paid,
                MAX(i.invoice_date) as last_purchase_date,
                AVG(i.total) as avg_purchase_amount
            FROM Invoices i
            JOIN Persons p ON i.customer_id = p.id
            WHERE i.invoice_type IN ('فروش', 'خدمات')
            """
            
            params = []
            if start_date and end_date:
                query += " AND DATE(i.invoice_date) BETWEEN ? AND ?"
                params.extend([start_date, end_date])
            
            query += """
            GROUP BY p.id, customer_name, p.mobile, p.person_type
            HAVING COUNT(i.id) > 0
            ORDER BY total_purchases DESC
            LIMIT ?
            """
            
            params.append(limit)
            
            customers = self.data_manager.db.fetch_all(query, params)
            
            # محاسبه وفاداری و امتیاز مشتری
            for customer in customers:
                invoice_count = customer['invoice_count'] or 0
                total_purchases = customer['total_purchases'] or 0
                avg_amount = customer['avg_purchase_amount'] or 0
                
                # امتیاز وفاداری (بر اساس تعداد خریدها و مبلغ)
                loyalty_score = min(invoice_count * 10, 50)  # حداکثر ۵۰ امتیاز برای تعداد
                amount_score = min(total_purchases / 1000000, 30)  # حداکثر ۳۰ امتیاز برای مبلغ
                
                customer['loyalty_score'] = loyalty_score + amount_score
                customer['customer_type'] = self.get_customer_type(invoice_count, total_purchases)
                
                # وضعیت پرداخت
                total_paid = customer['total_paid'] or 0
                customer['payment_rate'] = (total_paid / total_purchases * 100) if total_purchases > 0 else 0
            
            return customers
            
        except Exception as e:
            print(f"❌ خطا در دریافت مشتریان برتر: {e}")
            return []
    
    def get_customer_type(self, invoice_count, total_purchases):
        """تعیین نوع مشتری بر اساس رفتار خرید"""
        if invoice_count >= 10 and total_purchases >= 10000000:
            return "VIP 🏆"
        elif invoice_count >= 5 and total_purchases >= 5000000:
            return "وفادار 💎"
        elif invoice_count >= 3:
            return "منظم ⭐"
        elif invoice_count >= 1:
            return "جدید 🌱"
        else:
            return "غیرفعال ⏸️"
    
    def get_profitability_analysis(self, start_date=None, end_date=None):
        """تحلیل سودآوری"""
        try:
            # دریافت فروش و سود تخمینی
            query = """
            SELECT 
                -- فروش لوازم نو
                (SELECT COALESCE(SUM(ii.total_price), 0)
                 FROM InvoiceItems ii
                 JOIN Invoices i ON ii.invoice_id = i.id
                 JOIN NewAppliancesWarehouse naw ON ii.item_id = naw.id
                 WHERE ii.item_type = 'دستگاه'
                 AND i.invoice_type IN ('فروش', 'خدمات')
                 {date_condition}) as new_appliances_sales,
                
                -- سود تخمینی لوازم نو (۳۰٪)
                (SELECT COALESCE(SUM(ii.total_price) * 0.3, 0)
                 FROM InvoiceItems ii
                 JOIN Invoices i ON ii.invoice_id = i.id
                 JOIN NewAppliancesWarehouse naw ON ii.item_id = naw.id
                 WHERE ii.item_type = 'دستگاه'
                 AND i.invoice_type IN ('فروش', 'خدمات')
                 {date_condition}) as new_appliances_profit,
                
                -- فروش لوازم دست دوم
                (SELECT COALESCE(SUM(ii.total_price), 0)
                 FROM InvoiceItems ii
                 JOIN Invoices i ON ii.invoice_id = i.id
                 JOIN UsedAppliancesWarehouse uaw ON ii.item_id = uaw.id
                 WHERE ii.item_type = 'دستگاه'
                 AND i.invoice_type IN ('فروش', 'خدمات')
                 {date_condition}) as used_appliances_sales,
                
                -- سود تخمینی لوازم دست دوم (۴۰٪)
                (SELECT COALESCE(SUM(ii.total_price) * 0.4, 0)
                 FROM InvoiceItems ii
                 JOIN Invoices i ON ii.invoice_id = i.id
                 JOIN UsedAppliancesWarehouse uaw ON ii.item_id = uaw.id
                 WHERE ii.item_type = 'دستگاه'
                 AND i.invoice_type IN ('فروش', 'خدمات')
                 {date_condition}) as used_appliances_profit,
                
                -- فروش قطعات نو
                (SELECT COALESCE(SUM(ii.total_price), 0)
                 FROM InvoiceItems ii
                 JOIN Invoices i ON ii.invoice_id = i.id
                 JOIN NewPartsWarehouse npw ON ii.item_id = npw.id
                 WHERE ii.item_type = 'قطعه'
                 AND i.invoice_type IN ('فروش', 'خدمات')
                 {date_condition}) as new_parts_sales,
                
                -- سود تخمینی قطعات نو (۵۰٪)
                (SELECT COALESCE(SUM(ii.total_price) * 0.5, 0)
                 FROM InvoiceItems ii
                 JOIN Invoices i ON ii.invoice_id = i.id
                 JOIN NewPartsWarehouse npw ON ii.item_id = npw.id
                 WHERE ii.item_type = 'قطعه'
                 AND i.invoice_type IN ('فروش', 'خدمات')
                 {date_condition}) as new_parts_profit,
                
                -- فروش قطعات دست دوم
                (SELECT COALESCE(SUM(ii.total_price), 0)
                 FROM InvoiceItems ii
                 JOIN Invoices i ON ii.invoice_id = i.id
                 JOIN UsedPartsWarehouse upw ON ii.item_id = upw.id
                 WHERE ii.item_type = 'قطعه'
                 AND i.invoice_type IN ('فروش', 'خدمات')
                 {date_condition}) as used_parts_sales,
                
                -- سود تخمینی قطعات دست دوم (۶۰٪)
                (SELECT COALESCE(SUM(ii.total_price) * 0.6, 0)
                 FROM InvoiceItems ii
                 JOIN Invoices i ON ii.invoice_id = i.id
                 JOIN UsedPartsWarehouse upw ON ii.item_id = upw.id
                 WHERE ii.item_type = 'قطعه'
                 AND i.invoice_type IN ('فروش', 'خدمات')
                 {date_condition}) as used_parts_profit,
                
                -- فروش خدمات
                (SELECT COALESCE(SUM(ii.total_price), 0)
                 FROM InvoiceItems ii
                 JOIN Invoices i ON ii.invoice_id = i.id
                 WHERE ii.item_type = 'خدمات'
                 AND i.invoice_type = 'خدمات'
                 {date_condition}) as services_sales,
                
                -- سود تخمینی خدمات (۸۰٪)
                (SELECT COALESCE(SUM(ii.total_price) * 0.8, 0)
                 FROM InvoiceItems ii
                 JOIN Invoices i ON ii.invoice_id = i.id
                 WHERE ii.item_type = 'خدمات'
                 AND i.invoice_type = 'خدمات'
                 {date_condition}) as services_profit
            """
            
            # اضافه کردن شرط تاریخ
            date_condition = ""
            params = []
            if start_date and end_date:
                date_condition = " AND DATE(i.invoice_date) BETWEEN ? AND ?"
                params = [start_date, end_date, start_date, end_date, start_date, end_date, 
                         start_date, end_date, start_date, end_date, start_date, end_date,
                         start_date, end_date, start_date, end_date, start_date, end_date,
                         start_date, end_date, start_date, end_date]
            
            query = query.format(date_condition=date_condition)
            
            result = self.data_manager.db.fetch_one(query, params)
            
            if result:
                # محاسبات کل
                total_sales = (
                    (result['new_appliances_sales'] or 0) +
                    (result['used_appliances_sales'] or 0) +
                    (result['new_parts_sales'] or 0) +
                    (result['used_parts_sales'] or 0) +
                    (result['services_sales'] or 0)
                )
                
                total_profit = (
                    (result['new_appliances_profit'] or 0) +
                    (result['used_appliances_profit'] or 0) +
                    (result['new_parts_profit'] or 0) +
                    (result['used_parts_profit'] or 0) +
                    (result['services_profit'] or 0)
                )
                
                overall_profit_margin = (total_profit / total_sales * 100) if total_sales > 0 else 0
                
                return {
                    'total_sales': total_sales,
                    'total_profit': total_profit,
                    'overall_profit_margin': overall_profit_margin,
                    'categories': {
                        'new_appliances': {
                            'sales': result['new_appliances_sales'] or 0,
                            'profit': result['new_appliances_profit'] or 0,
                            'margin': ((result['new_appliances_profit'] or 0) / (result['new_appliances_sales'] or 1) * 100) if result['new_appliances_sales'] else 0
                        },
                        'used_appliances': {
                            'sales': result['used_appliances_sales'] or 0,
                            'profit': result['used_appliances_profit'] or 0,
                            'margin': ((result['used_appliances_profit'] or 0) / (result['used_appliances_sales'] or 1) * 100) if result['used_appliances_sales'] else 0
                        },
                        'new_parts': {
                            'sales': result['new_parts_sales'] or 0,
                            'profit': result['new_parts_profit'] or 0,
                            'margin': ((result['new_parts_profit'] or 0) / (result['new_parts_sales'] or 1) * 100) if result['new_parts_sales'] else 0
                        },
                        'used_parts': {
                            'sales': result['used_parts_sales'] or 0,
                            'profit': result['used_parts_profit'] or 0,
                            'margin': ((result['used_parts_profit'] or 0) / (result['used_parts_sales'] or 1) * 100) if result['used_parts_sales'] else 0
                        },
                        'services': {
                            'sales': result['services_sales'] or 0,
                            'profit': result['services_profit'] or 0,
                            'margin': ((result['services_profit'] or 0) / (result['services_sales'] or 1) * 100) if result['services_sales'] else 0
                        }
                    }
                }
            
            return {}
            
        except Exception as e:
            print(f"❌ خطا در تحلیل سودآوری: {e}")
            return {}
    
    def get_warehouse_sales_comparison(self, start_date=None, end_date=None):
        """مقایسه فروش انبارها"""
        try:
            # برای هر انبار، فروش و سود را محاسبه می‌کنیم
            warehouses = ['لوازم نو', 'لوازم دست دوم', 'قطعات نو', 'قطعات دست دوم', 'خدمات']
            
            comparison_data = []
            
            for warehouse in warehouses:
                if warehouse == 'خدمات':
                    query = """
                    SELECT 
                        COUNT(ii.id) as sale_count,
                        SUM(ii.total_price) as total_sales,
                        SUM(ii.total_price) * 0.8 as estimated_profit
                    FROM InvoiceItems ii
                    JOIN Invoices i ON ii.invoice_id = i.id
                    WHERE ii.item_type = 'خدمات'
                    AND i.invoice_type = 'خدمات'
                    """
                else:
                    # تشخیص نوع آیتم بر اساس انبار
                    item_type = 'دستگاه' if 'لوازم' in warehouse else 'قطعه'
                    table_name = 'New' if 'نو' in warehouse else 'Used'
                    
                    if 'لوازم' in warehouse:
                        table_name += 'AppliancesWarehouse'
                        join_condition = f"JOIN {table_name} aw ON ii.item_id = aw.id"
                    else:
                        table_name += 'PartsWarehouse'
                        join_condition = f"JOIN {table_name} pw ON ii.item_id = pw.id"
                    
                    query = f"""
                    SELECT 
                        COUNT(ii.id) as sale_count,
                        SUM(ii.total_price) as total_sales,
                        SUM(ii.total_price) * CASE 
                            WHEN '{warehouse}' = 'لوازم نو' THEN 0.3
                            WHEN '{warehouse}' = 'لوازم دست دوم' THEN 0.4
                            WHEN '{warehouse}' = 'قطعات نو' THEN 0.5
                            WHEN '{warehouse}' = 'قطعات دست دوم' THEN 0.6
                            ELSE 0
                        END as estimated_profit
                    FROM InvoiceItems ii
                    JOIN Invoices i ON ii.invoice_id = i.id
                    {join_condition}
                    WHERE ii.item_type = '{item_type}'
                    AND i.invoice_type IN ('فروش', 'خدمات')
                    """
                
                # اضافه کردن شرط تاریخ
                params = []
                if start_date and end_date:
                    if warehouse == 'خدمات':
                        query += " AND DATE(i.invoice_date) BETWEEN ? AND ?"
                    else:
                        query += " AND DATE(i.invoice_date) BETWEEN ? AND ?"
                    params.extend([start_date, end_date])
                
                result = self.data_manager.db.fetch_one(query, params)
                
                if result:
                    total_sales = result['total_sales'] or 0
                    estimated_profit = result['estimated_profit'] or 0
                    profit_margin = (estimated_profit / total_sales * 100) if total_sales > 0 else 0
                    
                    comparison_data.append({
                        'warehouse': warehouse,
                        'sale_count': result['sale_count'] or 0,
                        'total_sales': total_sales,
                        'estimated_profit': estimated_profit,
                        'profit_margin': profit_margin,
                        'avg_sale_value': (total_sales / (result['sale_count'] or 1))
                    })
            
            # مرتب‌سازی بر اساس فروش کل
            comparison_data.sort(key=lambda x: x['total_sales'], reverse=True)
            
            return comparison_data
            
        except Exception as e:
            print(f"❌ خطا در مقایسه فروش انبارها: {e}")
            return []
    
    def get_sales_trends(self, period='monthly'):
        """دریافت روند فروش در بازه زمانی"""
        try:
            if period == 'monthly':
                query = """
                SELECT 
                    strftime('%Y-%m', invoice_date) as period,
                    COUNT(*) as invoice_count,
                    SUM(total) as total_sales,
                    SUM(paid_amount) as total_paid,
                    COUNT(DISTINCT customer_id) as unique_customers
                FROM Invoices
                WHERE invoice_type IN ('فروش', 'خدمات')
                AND invoice_date IS NOT NULL
                GROUP BY strftime('%Y-%m', invoice_date)
                ORDER BY period DESC
                LIMIT 12
                """
            elif period == 'weekly':
                query = """
                SELECT 
                    strftime('%Y-W%W', invoice_date) as period,
                    COUNT(*) as invoice_count,
                    SUM(total) as total_sales,
                    SUM(paid_amount) as total_paid,
                    COUNT(DISTINCT customer_id) as unique_customers
                FROM Invoices
                WHERE invoice_type IN ('فروش', 'خدمات')
                AND invoice_date IS NOT NULL
                GROUP BY strftime('%Y-W%W', invoice_date)
                ORDER BY period DESC
                LIMIT 12
                """
            else:  # daily
                query = """
                SELECT 
                    DATE(invoice_date) as period,
                    COUNT(*) as invoice_count,
                    SUM(total) as total_sales,
                    SUM(paid_amount) as total_paid,
                    COUNT(DISTINCT customer_id) as unique_customers
                FROM Invoices
                WHERE invoice_type IN ('فروش', 'خدمات')
                AND invoice_date IS NOT NULL
                GROUP BY DATE(invoice_date)
                ORDER BY period DESC
                LIMIT 30
                """
            
            trends = self.data_manager.db.fetch_all(query)
            
            # محاسبه نرخ تکمیل پرداخت برای هر دوره
            for trend in trends:
                total_sales = trend['total_sales'] or 0
                total_paid = trend['total_paid'] or 0
                trend['payment_completion_rate'] = (total_paid / total_sales * 100) if total_sales > 0 else 0
                
                # محاسبه میانگین فاکتور
                invoice_count = trend['invoice_count'] or 0
                trend['avg_invoice_amount'] = (total_sales / invoice_count) if invoice_count > 0 else 0
            
            # معکوس کردن برای نمایش از قدیم به جدید
            return trends[::-1]
            
        except Exception as e:
            print(f"❌ خطا در دریافت روند فروش: {e}")
            return []
    
    def get_recent_sales(self, limit=10):
        """دریافت آخرین فروش‌ها"""
        try:
            query = """
            SELECT 
                i.id,
                i.invoice_number,
                i.invoice_date,
                i.total,
                i.payment_status,
                p.first_name || ' ' || p.last_name as customer_name,
                p.mobile,
                COUNT(ii.id) as item_count
            FROM Invoices i
            JOIN Persons p ON i.customer_id = p.id
            LEFT JOIN InvoiceItems ii ON i.id = ii.invoice_id
            WHERE i.invoice_type IN ('فروش', 'خدمات')
            GROUP BY i.id, i.invoice_number, i.invoice_date, i.total, i.payment_status, customer_name, p.mobile
            ORDER BY i.invoice_date DESC
            LIMIT ?
            """
            
            return self.data_manager.db.fetch_all(query, (limit,))
            
        except Exception as e:
            print(f"❌ خطا در دریافت آخرین فروش‌ها: {e}")
            return []