# modules/dashboard_manager.py
"""
مدیریت داده‌های داشبورد - اتصال به داده‌های واقعی دیتابیس
"""

from PySide6.QtCore import QObject, Signal
from datetime import datetime, timedelta
import jdatetime
from dateutil import relativedelta


class DashboardManager(QObject):
    """مدیریت داده‌های داشبورد"""
    
    dashboard_data_updated = Signal(dict)  # سیگنال بروزرسانی داده‌های داشبورد
    
    def __init__(self, data_manager):
        super().__init__()
        self.data_manager = data_manager
        
        # کش داده‌ها برای بهبود عملکرد
        self.cache = {
            'stats': None,
            'charts': None,
            'alerts': None,
            'quick_lists': None,
            'timestamp': None
        }
        
        # تنظیم مدت زمان اعتبار کش (ثانیه)
        self.cache_ttl = 300  # 5 دقیقه
    
    def get_dashboard_data(self, force_refresh=False):
        """دریافت تمام داده‌های داشبورد"""
        current_time = datetime.now()
        
        # بررسی کش و اعتبار آن
        if (not force_refresh and 
            self.cache['timestamp'] and 
            (current_time - self.cache['timestamp']).seconds < self.cache_ttl):
            return self.cache
        
        # جمع‌آوری داده‌های جدید
        dashboard_data = {
            'stats': self.get_today_stats(),
            'charts': self.get_charts_data(),
            'alerts': self.get_alerts(),
            'quick_lists': self.get_quick_lists(),
            'timestamp': current_time
        }
        
        # ذخیره در کش
        self.cache = dashboard_data
        
        # ارسال سیگنال بروزرسانی
        self.dashboard_data_updated.emit(dashboard_data)
        
        return dashboard_data
    
    def get_today_stats(self):
        """آمار امروز - محاسبه از دیتابیس"""
        try:
            today = datetime.now().date()
            today_str = today.strftime('%Y-%m-%d')
            today_jalali = jdatetime.date.today()
            today_jalali_str = today_jalali.strftime('%Y-%m-%d')
            
            # 1. تعداد پذیرش‌های امروز
            query = """
            SELECT COUNT(*) as count
            FROM Receptions 
            WHERE DATE(reception_date) = ?
            """
            today_receptions = self.data_manager.db.fetch_one(query, (today_str,))
            today_receptions_count = today_receptions['count'] if today_receptions else 0
            
            # 2. دستگاه‌های در حال تعمیر
            query = """
            SELECT COUNT(*) as count
            FROM Receptions 
            WHERE status IN ('در حال تعمیر', 'در انتظار')
            """
            repairing_receptions = self.data_manager.db.fetch_one(query)
            repairing_count = repairing_receptions['count'] if repairing_receptions else 0
            
            # 3. تعمیرات تکمیل شده امروز
            query = """
            SELECT COUNT(*) as count
            FROM Receptions 
            WHERE status = 'تعمیر شده' 
            AND DATE(reception_date) = ?
            """
            completed_today = self.data_manager.db.fetch_one(query, (today_str,))
            completed_count = completed_today['count'] if completed_today else 0
            
            # 4. فاکتورهای پرداخت نشده امروز
            query = """
            SELECT COUNT(*) as count, COALESCE(SUM(total), 0) as total_amount
            FROM Invoices 
            WHERE payment_status = 'نسیه' 
            AND DATE(invoice_date) = ?
            """
            unpaid_invoices = self.data_manager.db.fetch_one(query, (today_str,))
            unpaid_count = unpaid_invoices['count'] if unpaid_invoices else 0
            unpaid_amount = unpaid_invoices['total_amount'] if unpaid_invoices else 0
            
            # 5. چک‌های سررسید نزدیک (۳ روز آینده)
            three_days_later = today + timedelta(days=3)
            three_days_later_str = three_days_later.strftime('%Y-%m-%d')
            
            query = """
            SELECT COUNT(*) as count, COALESCE(SUM(amount), 0) as total_amount
            FROM Checks 
            WHERE status IN ('وصول نشده', 'پاس نشده')
            AND date(due_date) BETWEEN date(?) AND date(?)
            """
            due_checks = self.data_manager.db.fetch_one(query, (today_str, three_days_later_str))
            due_checks_count = due_checks['count'] if due_checks else 0
            due_checks_amount = due_checks['total_amount'] if due_checks else 0
            
            # 6. موجودی‌های کم انبار
            query = """
            SELECT COUNT(*) as count
            FROM Parts p
            LEFT JOIN (
                SELECT part_id, SUM(quantity) as total_qty 
                FROM NewPartsWarehouse 
                WHERE status = 'موجود'
                GROUP BY part_id
            ) np ON p.id = np.part_id
            LEFT JOIN (
                SELECT part_id, SUM(quantity) as total_qty 
                FROM UsedPartsWarehouse 
                WHERE status = 'موجود'
                GROUP BY part_id
            ) up ON p.id = up.part_id
            WHERE COALESCE(np.total_qty, 0) + COALESCE(up.total_qty, 0) < p.min_stock
            """
            low_stock = self.data_manager.db.fetch_one(query)
            low_stock_count = low_stock['count'] if low_stock else 0
            
            # 7. درآمد امروز
            query = """
            SELECT COALESCE(SUM(paid_amount), 0) as total_income
            FROM Invoices 
            WHERE DATE(invoice_date) = ? 
            AND payment_status IN ('پرداخت شده', 'نقدی')
            """
            today_income = self.data_manager.db.fetch_one(query, (today_str,))
            income_today = today_income['total_income'] if today_income else 0
            
            # 8. هزینه‌های امروز
            query = """
            SELECT COALESCE(SUM(amount), 0) as total_expense
            FROM AccountingTransactions 
            WHERE transaction_type = 'پرداخت'
            AND DATE(transaction_date) = ?
            """
            today_expenses = self.data_manager.db.fetch_one(query, (today_str,))
            expenses_today = today_expenses['total_expense'] if today_expenses else 0
            
            # 9. مشتریان جدید امروز
            query = """
            SELECT COUNT(*) as count
            FROM Persons 
            WHERE person_type = 'مشتری'
            AND DATE(registration_date) = ?
            """
            new_customers = self.data_manager.db.fetch_one(query, (today_str,))
            new_customers_count = new_customers['count'] if new_customers else 0
            
            # 10. سود امروز
            profit_today = income_today - expenses_today
            
            stats = {
                'today_receptions': today_receptions_count,
                'repairing_devices': repairing_count,
                'completed_today': completed_count,
                'unpaid_invoices': {
                    'count': unpaid_count,
                    'amount': unpaid_amount
                },
                'due_checks': {
                    'count': due_checks_count,
                    'amount': due_checks_amount
                },
                'low_stock_items': low_stock_count,
                'today_income': income_today,
                'today_expenses': expenses_today,
                'profit_today': profit_today,
                'new_customers': new_customers_count
            }
            
            return stats
            
        except Exception as e:
            print(f"خطا در محاسبه آمار امروز: {e}")
            return {}
    
    def get_charts_data(self):
        """داده‌های نمودارها"""
        try:
            charts = {
                'reception_status': self.get_reception_status_chart(),
                'daily_income': self.get_daily_income_chart(),
                'monthly_trends': self.get_monthly_trends_chart(),
                'inventory_status': self.get_inventory_status_chart()
            }
            return charts
            
        except Exception as e:
            print(f"خطا در دریافت داده‌های نمودارها: {e}")
            return {}
    
    def get_reception_status_chart(self):
        """نمودار وضعیت پذیرش‌ها"""
        try:
            query = """
            SELECT 
                status,
                COUNT(*) as count
            FROM Receptions
            GROUP BY status
            """
            
            results = self.data_manager.db.fetch_all(query)
            
            # تبدیل به فرمت مناسب برای نمودار
            chart_data = {
                'labels': [],
                'data': [],
                'colors': []
            }
            
            status_colors = {
                'در انتظار': '#f39c12',  # نارنجی
                'در حال تعمیر': '#3498db',  # آبی
                'تعمیر شده': '#27ae60',  # سبز
                'تحویل داده شده': '#9b59b6',  # بنفش
                'لغو شده': '#e74c3c'  # قرمز
            }
            
            for row in results:
                status = row['status']
                if status in status_colors:
                    chart_data['labels'].append(status)
                    chart_data['data'].append(row['count'])
                    chart_data['colors'].append(status_colors[status])
            
            return chart_data
            
        except Exception as e:
            print(f"خطا در دریافت نمودار وضعیت پذیرش: {e}")
            return {'labels': [], 'data': [], 'colors': []}
    
    def get_daily_income_chart(self):
        """نمودار درآمد روزانه هفته جاری"""
        try:
            # تاریخ ۷ روز گذشته
            end_date = datetime.now().date()
            start_date = end_date - timedelta(days=6)
            
            query = """
            SELECT 
                DATE(invoice_date) as date,
                COALESCE(SUM(paid_amount), 0) as daily_income
            FROM Invoices
            WHERE DATE(invoice_date) BETWEEN ? AND ?
            AND payment_status IN ('پرداخت شده', 'نقدی')
            GROUP BY DATE(invoice_date)
            ORDER BY DATE(invoice_date)
            """
            
            results = self.data_manager.db.fetch_all(query, (start_date, end_date))
            
            # ایجاد لیست کامل ۷ روز
            dates = [(start_date + timedelta(days=i)).strftime('%Y-%m-%d') 
                    for i in range(7)]
            
            income_data = {row['date']: row['daily_income'] for row in results}
            
            # پر کردن روزهای بدون درآمد با صفر
            daily_income = [income_data.get(date, 0) for date in dates]
            
            # تبدیل تاریخ‌ها به شمسی برای نمایش
            jalali_dates = []
            for date_str in dates:
                date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
                jalali_date = jdatetime.date.fromgregorian(date=date_obj)
                jalali_dates.append(jalali_date.strftime('%m/%d'))
            
            return {
                'dates': jalali_dates,
                'income': daily_income
            }
            
        except Exception as e:
            print(f"خطا در دریافت نمودار درآمد روزانه: {e}")
            return {'dates': [], 'income': []}
    
    def get_monthly_trends_chart(self):
        """نمودار روند ماهانه"""
        try:
            # ۶ ماه گذشته
            end_date = datetime.now().date()
            start_date = end_date - relativedelta.relativedelta(months=5)
            start_date = start_date.replace(day=1)  # اول ماه
            
            query = """
            SELECT 
                strftime('%Y-%m', invoice_date) as month,
                COUNT(*) as reception_count,
                COALESCE(SUM(total), 0) as total_income
            FROM Invoices
            WHERE DATE(invoice_date) BETWEEN ? AND ?
            GROUP BY strftime('%Y-%m', invoice_date)
            ORDER BY strftime('%Y-%m', invoice_date)
            """
            
            results = self.data_manager.db.fetch_all(query, (start_date, end_date))
            
            # ایجاد لیست کامل ۶ ماه
            months = []
            for i in range(6):
                month_date = end_date - relativedelta.relativedelta(months=(5-i))
                months.append(month_date.strftime('%Y-%m'))
            
            # تبدیل به دیکشنری برای جستجوی آسان
            month_data = {row['month']: row for row in results}
            
            # آماده‌سازی داده‌ها
            reception_counts = []
            incomes = []
            
            for month in months:
                if month in month_data:
                    reception_counts.append(month_data[month]['reception_count'])
                    incomes.append(month_data[month]['total_income'])
                else:
                    reception_counts.append(0)
                    incomes.append(0)
            
            # تبدیل نام ماه‌ها به شمسی
            month_names = []
            for month_str in months:
                year, month = map(int, month_str.split('-'))
                miladi_date = datetime(year, month, 1).date()
                jalali_date = jdatetime.date.fromgregorian(date=miladi_date)
                month_names.append(jalali_date.strftime('%b %y'))
            
            return {
                'months': month_names,
                'receptions': reception_counts,
                'income': incomes
            }
            
        except Exception as e:
            print(f"خطا در دریافت نمودار روند ماهانه: {e}")
            return {'months': [], 'receptions': [], 'income': []}
    
    def get_inventory_status_chart(self):
        """وضعیت موجودی انبار"""
        try:
            # دریافت موجودی انواع انبار
            warehouse_types = ['قطعات نو', 'قطعات دست دوم', 'لوازم نو', 'لوازم دست دوم']
            
            inventory_data = []
            
            for warehouse_type in warehouse_types:
                if 'قطعات' in warehouse_type:
                    # برای قطعات
                    query = """
                    SELECT COUNT(*) as item_count
                    FROM Parts p
                    LEFT JOIN (
                        SELECT part_id, SUM(quantity) as total_qty 
                        FROM NewPartsWarehouse 
                        WHERE status = 'موجود'
                        GROUP BY part_id
                    ) np ON p.id = np.part_id
                    LEFT JOIN (
                        SELECT part_id, SUM(quantity) as total_qty 
                        FROM UsedPartsWarehouse 
                        WHERE status = 'موجود'
                        GROUP BY part_id
                    ) up ON p.id = up.part_id
                    """
                    
                    result = self.data_manager.db.fetch_one(query)
                    item_count = result['item_count'] if result else 0
                    
                elif 'لوازم' in warehouse_type:
                    # برای لوازم
                    if 'نو' in warehouse_type:
                        query = "SELECT COUNT(*) as item_count FROM NewAppliancesWarehouse WHERE status = 'موجود'"
                    else:
                        query = "SELECT COUNT(*) as item_count FROM UsedAppliancesWarehouse WHERE status = 'موجود'"
                    
                    result = self.data_manager.db.fetch_one(query)
                    item_count = result['item_count'] if result else 0
                
                inventory_data.append({
                    'warehouse': warehouse_type,
                    'count': item_count
                })
            
            # آماده‌سازی برای نمودار
            labels = [item['warehouse'] for item in inventory_data]
            counts = [item['count'] for item in inventory_data]
            colors = ['#3498db', '#2ecc71', '#9b59b6', '#f39c12']
            
            return {
                'labels': labels,
                'data': counts,
                'colors': colors
            }
            
        except Exception as e:
            print(f"خطا در دریافت نمودار موجودی: {e}")
            return {'labels': [], 'data': [], 'colors': []}
    
    def get_alerts(self):
        """دریافت هشدارها و اعلان‌ها"""
        try:
            alerts = {
                'urgent': self.get_urgent_alerts(),
                'warning': self.get_warning_alerts(),
                'info': self.get_info_alerts()
            }
            return alerts
            
        except Exception as e:
            print(f"خطا در دریافت هشدارها: {e}")
            return {}
    
    def get_urgent_alerts(self):
        """هشدارهای فوری"""
        alerts = []
        
        try:
            # 1. چک‌های فردا سررسید می‌شوند
            tomorrow = (datetime.now() + timedelta(days=1)).date()
            tomorrow_str = tomorrow.strftime('%Y-%m-%d')
            
            query = """
            SELECT 
                check_number, 
                bank_name, 
                amount,
                drawer
            FROM Checks 
            WHERE status IN ('وصول نشده', 'پاس نشده')
            AND date(due_date) = ?
            """
            
            due_checks = self.data_manager.db.fetch_all(query, (tomorrow_str,))
            
            for check in due_checks:
                alerts.append({
                    'type': 'urgent',
                    'title': 'چک سررسید فردا',
                    'message': f"چک شماره {check['check_number']} بانک {check['bank_name']} مبلغ {check['amount']:,} تومان",
                    'details': f"صادرکننده: {check['drawer']}",
                    'action': 'checks',
                    'timestamp': datetime.now().isoformat()
                })
            
            # 2. پذیرش‌های با اولویت خیلی فوری
            query = """
            SELECT 
                r.reception_number,
                p.first_name || ' ' || p.last_name as customer_name,
                d.device_type,
                d.brand
            FROM Receptions r
            JOIN Persons p ON r.customer_id = p.id
            JOIN Devices d ON r.device_id = d.id
            WHERE r.priority = 'خیلی فوری'
            AND r.status IN ('در انتظار', 'در حال تعمیر')
            LIMIT 5
            """
            
            urgent_receptions = self.data_manager.db.fetch_all(query)
            
            for reception in urgent_receptions:
                alerts.append({
                    'type': 'urgent',
                    'title': 'پذیرش فوری',
                    'message': f"پذیرش شماره {reception['reception_number']} - {reception['device_type']} {reception['brand']}",
                    'details': f"مشتری: {reception['customer_name']}",
                    'action': 'receptions',
                    'timestamp': datetime.now().isoformat()
                })
            
        except Exception as e:
            print(f"خطا در دریافت هشدارهای فوری: {e}")
        
        return alerts
    
    def get_warning_alerts(self):
        """هشدارهای هشداری"""
        alerts = []
        
        try:
            # 1. موجودی‌های زیر حداقل
            query = """
            SELECT 
                p.part_code,
                p.part_name,
                p.min_stock,
                COALESCE(np.total_qty, 0) + COALESCE(up.total_qty, 0) as current_stock
            FROM Parts p
            LEFT JOIN (
                SELECT part_id, SUM(quantity) as total_qty 
                FROM NewPartsWarehouse 
                WHERE status = 'موجود'
                GROUP BY part_id
            ) np ON p.id = np.part_id
            LEFT JOIN (
                SELECT part_id, SUM(quantity) as total_qty 
                FROM UsedPartsWarehouse 
                WHERE status = 'موجود'
                GROUP BY part_id
            ) up ON p.id = up.part_id
            WHERE COALESCE(np.total_qty, 0) + COALESCE(up.total_qty, 0) < p.min_stock
            LIMIT 10
            """
            
            low_stock_items = self.data_manager.db.fetch_all(query)
            
            for item in low_stock_items:
                alerts.append({
                    'type': 'warning',
                    'title': 'موجودی کم',
                    'message': f"{item['part_name']} (کد: {item['part_code']})",
                    'details': f"موجودی: {item['current_stock']} - حداقل: {item['min_stock']}",
                    'action': 'inventory',
                    'timestamp': datetime.now().isoformat()
                })
            
            # 2. دستگاه‌های در انتظار قطعه
            query = """
            SELECT 
                r.reception_number,
                p.first_name || ' ' || p.last_name as customer_name,
                d.device_type,
                d.brand,
                r.problem_description
            FROM Receptions r
            JOIN Persons p ON r.customer_id = p.id
            JOIN Devices d ON r.device_id = d.id
            WHERE r.status = 'در انتظار'
            AND r.notes LIKE '%قطعه%'
            LIMIT 5
            """
            
            waiting_parts = self.data_manager.db.fetch_all(query)
            
            for reception in waiting_parts:
                alerts.append({
                    'type': 'warning',
                    'title': 'منتظر قطعه',
                    'message': f"پذیرش {reception['reception_number']} منتظر قطعه است",
                    'details': f"{reception['device_type']} {reception['brand']} - {reception['customer_name']}",
                    'action': 'receptions',
                    'timestamp': datetime.now().isoformat()
                })
            
        except Exception as e:
            print(f"خطا در دریافت هشدارهای هشدار: {e}")
        
        return alerts
    
    def get_info_alerts(self):
        """اطلاعیه‌ها"""
        alerts = []
        
        try:
            # 1. مشتریان منتظر تماس
            query = """
            SELECT 
                p.first_name || ' ' || p.last_name as customer_name,
                p.mobile,
                r.reception_number,
                d.device_type
            FROM Receptions r
            JOIN Persons p ON r.customer_id = p.id
            JOIN Devices d ON r.device_id = d.id
            WHERE r.status = 'تعمیر شده'
            AND DATE(r.reception_date) = DATE('now', '-1 day')
            LIMIT 5
            """
            
            customers_to_call = self.data_manager.db.fetch_all(query)
            
            for customer in customers_to_call:
                alerts.append({
                    'type': 'info',
                    'title': 'تماس با مشتری',
                    'message': f"{customer['customer_name']} - دستگاه تعمیر شده",
                    'details': f"شماره: {customer['mobile']} - {customer['device_type']}",
                    'action': 'customers',
                    'timestamp': datetime.now().isoformat()
                })
            
            # 2. تعمیرکارانی که کار دارند
            query = """
            SELECT 
                per.first_name || ' ' || per.last_name as technician_name,
                COUNT(r.id) as repair_count
            FROM Repairs rep
            JOIN Persons per ON rep.technician_id = per.id
            JOIN Receptions r ON rep.reception_id = r.id
            WHERE rep.status IN ('شروع شده', 'در حال انجام')
            GROUP BY rep.technician_id
            HAVING COUNT(r.id) > 0
            """
            
            busy_technicians = self.data_manager.db.fetch_all(query)
            
            for tech in busy_technicians:
                alerts.append({
                    'type': 'info',
                    'title': 'تعمیرکار مشغول',
                    'message': f"{tech['technician_name']}",
                    'details': f"تعداد کارهای جاری: {tech['repair_count']}",
                    'action': 'repairs',
                    'timestamp': datetime.now().isoformat()
                })
            
        except Exception as e:
            print(f"خطا در دریافت اطلاعیه‌ها: {e}")
        
        return alerts
    
    def get_quick_lists(self):
        """لیست‌های سریع برای دسترسی آسان"""
        try:
            quick_lists = {
                'urgent_receptions': self.get_urgent_receptions(),
                'due_checks': self.get_due_checks_list(),
                'low_stock': self.get_low_stock_list(),
                'waiting_customers': self.get_waiting_customers()
            }
            return quick_lists
            
        except Exception as e:
            print(f"خطا در دریافت لیست‌های سریع: {e}")
            return {}
    
    def get_urgent_receptions(self, limit=10):
        """پذیرش‌های فوری"""
        try:
            query = """
            SELECT 
                r.reception_number,
                p.first_name || ' ' || p.last_name as customer_name,
                d.device_type,
                d.brand,
                r.priority,
                r.reception_date,
                r.status
            FROM Receptions r
            JOIN Persons p ON r.customer_id = p.id
            JOIN Devices d ON r.device_id = d.id
            WHERE r.priority IN ('فوری', 'خیلی فوری')
            AND r.status NOT IN ('تحویل داده شده', 'لغو شده')
            ORDER BY 
                CASE r.priority 
                    WHEN 'خیلی فوری' THEN 1
                    WHEN 'فوری' THEN 2
                    ELSE 3
                END,
                r.reception_date DESC
            LIMIT ?
            """
            
            return self.data_manager.db.fetch_all(query, (limit,))
            
        except Exception as e:
            print(f"خطا در دریافت پذیرش‌های فوری: {e}")
            return []
    
    def get_due_checks_list(self, limit=10):
        """چک‌های سررسید نزدیک"""
        try:
            seven_days_later = (datetime.now() + timedelta(days=7)).date()
            today_str = datetime.now().date().strftime('%Y-%m-%d')
            seven_days_str = seven_days_later.strftime('%Y-%m-%d')
            
            query = """
            SELECT 
                check_number,
                bank_name,
                amount,
                due_date,
                drawer,
                status
            FROM Checks 
            WHERE status IN ('وصول نشده', 'پاس نشده')
            AND date(due_date) BETWEEN date(?) AND date(?)
            ORDER BY due_date
            LIMIT ?
            """
            
            return self.data_manager.db.fetch_all(query, (today_str, seven_days_str, limit))
            
        except Exception as e:
            print(f"خطا در دریافت چک‌های سررسید: {e}")
            return []
    
    def get_low_stock_list(self, limit=10):
        """موجودی‌های کم"""
        try:
            query = """
            SELECT 
                p.part_code,
                p.part_name,
                p.category,
                p.min_stock,
                COALESCE(np.total_qty, 0) + COALESCE(up.total_qty, 0) as current_stock,
                (p.min_stock - (COALESCE(np.total_qty, 0) + COALESCE(up.total_qty, 0))) as deficit
            FROM Parts p
            LEFT JOIN (
                SELECT part_id, SUM(quantity) as total_qty 
                FROM NewPartsWarehouse 
                WHERE status = 'موجود'
                GROUP BY part_id
            ) np ON p.id = np.part_id
            LEFT JOIN (
                SELECT part_id, SUM(quantity) as total_qty 
                FROM UsedPartsWarehouse 
                WHERE status = 'موجود'
                GROUP BY part_id
            ) up ON p.id = up.part_id
            WHERE COALESCE(np.total_qty, 0) + COALESCE(up.total_qty, 0) < p.min_stock
            ORDER BY deficit DESC
            LIMIT ?
            """
            
            return self.data_manager.db.fetch_all(query, (limit,))
            
        except Exception as e:
            print(f"خطا در دریافت موجودی‌های کم: {e}")
            return []
    
    def get_waiting_customers(self, limit=10):
        """مشتریان منتظر"""
        try:
            query = """
            SELECT 
                p.first_name || ' ' || p.last_name as customer_name,
                p.mobile,
                COUNT(r.id) as waiting_count,
                MAX(r.reception_date) as last_reception
            FROM Receptions r
            JOIN Persons p ON r.customer_id = p.id
            WHERE r.status IN ('در انتظار', 'در حال تعمیر')
            GROUP BY r.customer_id
            HAVING COUNT(r.id) > 0
            ORDER BY MAX(r.reception_date) DESC
            LIMIT ?
            """
            
            return self.data_manager.db.fetch_all(query, (limit,))
            
        except Exception as e:
            print(f"خطا در دریافت مشتریان منتظر: {e}")
            return []
    
    def clear_cache(self):
        """پاک کردن کش"""
        self.cache = {
            'stats': None,
            'charts': None,
            'alerts': None,
            'quick_lists': None,
            'timestamp': None
        }
    
    def refresh_dashboard(self):
        """بروزرسانی اجباری داشبورد"""
        return self.get_dashboard_data(force_refresh=True)


if __name__ == "__main__":
    # تست ماژول
    from database.models import DataManager
    
    print("🔄 تست ماژول DashboardManager...")
    
    data_manager = DataManager()
    dashboard_manager = DashboardManager(data_manager)
    
    print("📊 دریافت آمار امروز...")
    stats = dashboard_manager.get_today_stats()
    print(f"تعداد پذیرش امروز: {stats.get('today_receptions', 0)}")
    print(f"دستگاه در حال تعمیر: {stats.get('repairing_devices', 0)}")
    print(f"درآمد امروز: {stats.get('today_income', 0):,} تومان")
    
    print("\n📈 دریافت داده‌های نمودار...")
    charts = dashboard_manager.get_charts_data()
    if charts:
        print(f"وضعیت پذیرش‌ها: {len(charts.get('reception_status', {}).get('labels', []))} وضعیت")
        print(f"درآمد روزانه: {len(charts.get('daily_income', {}).get('dates', []))} روز")
    
    print("\n⚠️ دریافت هشدارها...")
    alerts = dashboard_manager.get_alerts()
    total_alerts = (
        len(alerts.get('urgent', [])) + 
        len(alerts.get('warning', [])) + 
        len(alerts.get('info', []))
    )
    print(f"تعداد هشدارها: {total_alerts}")
    
    print("\n✅ تست ماژول DashboardManager با موفقیت انجام شد!")