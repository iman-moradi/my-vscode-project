# ui/forms/reports/utils/optimizations.py
"""
بهینه‌سازی‌های عملکردی برای ماژول گزارش‌گیری
"""

from PySide6.QtCore import QThread, Signal, QObject
import time
import threading


class ReportDataLoader(QThread):
    """لودر داده‌های گزارش در رشته جداگانه"""
    
    data_loaded = Signal(str, dict)  # signal: report_type, data
    progress_updated = Signal(str, int)  # signal: status, percentage
    
    def __init__(self, data_manager, report_type, params):
        super().__init__()
        self.data_manager = data_manager
        self.report_type = report_type
        self.params = params
        self.is_running = True
    
    def run(self):
        """لود داده‌ها در رشته جداگانه"""
        try:
            self.progress_updated.emit("در حال بارگذاری داده‌ها...", 10)
            
            data = {}
            
            if self.report_type == 'financial':
                data = self.load_financial_data()
            elif self.report_type == 'sales':
                data = self.load_sales_data()
            elif self.report_type == 'inventory':
                data = self.load_inventory_data()
            elif self.report_type == 'customer':
                data = self.load_customer_data()
            
            if self.is_running:
                self.progress_updated.emit("تکمیل شد", 100)
                self.data_loaded.emit(self.report_type, data)
                
        except Exception as e:
            self.progress_updated.emit(f"خطا: {str(e)}", 0)
    
    def load_financial_data(self):
        """لود داده‌های مالی"""
        data = {}
        
        # دریافت تاریخ‌ها
        start_date = self.params.get('start_date')
        end_date = self.params.get('end_date')
        
        self.progress_updated.emit("در حال دریافت خلاصه مالی...", 30)
        
        # خلاصه مالی
        query = """
        SELECT 
            SUM(CASE WHEN transaction_type = 'دریافت' THEN amount ELSE 0 END) as total_income,
            SUM(CASE WHEN transaction_type = 'پرداخت' THEN amount ELSE 0 END) as total_expense,
            COUNT(*) as total_transactions
        FROM AccountingTransactions
        WHERE DATE(transaction_date) BETWEEN ? AND ?
        """
        
        result = self.data_manager.db.fetch_one(query, (start_date, end_date))
        data['summary'] = result or {}
        
        self.progress_updated.emit("در حال دریافت حساب‌ها...", 60)
        
        # حساب‌ها
        query = "SELECT * FROM Accounts WHERE is_active = 1 ORDER BY account_type"
        data['accounts'] = self.data_manager.db.fetch_all(query)
        
        self.progress_updated.emit("در حال دریافت تراکنش‌ها...", 80)
        
        # تراکنش‌ها
        query = """
        SELECT 
            at.transaction_date,
            at.transaction_type,
            a1.account_name as from_account,
            a2.account_name as to_account,
            at.amount,
            at.description
        FROM AccountingTransactions at
        LEFT JOIN Accounts a1 ON at.from_account_id = a1.id
        LEFT JOIN Accounts a2 ON at.to_account_id = a2.id
        WHERE DATE(at.transaction_date) BETWEEN ? AND ?
        ORDER BY at.transaction_date DESC
        LIMIT 100
        """
        
        data['transactions'] = self.data_manager.db.fetch_all(query, (start_date, end_date))
        
        return data
    
    def load_sales_data(self):
        """لود داده‌های فروش"""
        data = {}
        
        start_date = self.params.get('start_date')
        end_date = self.params.get('end_date')
        
        self.progress_updated.emit("در حال دریافت آمار فروش...", 20)
        
        # آمار کلی فروش
        query = """
        SELECT 
            COUNT(*) as total_invoices,
            SUM(total) as total_sales,
            COUNT(DISTINCT customer_id) as unique_customers,
            AVG(total) as avg_invoice_amount,
            SUM(CASE WHEN payment_status = 'نقدی' THEN total ELSE 0 END) as cash_sales,
            SUM(CASE WHEN payment_status = 'چک' THEN total ELSE 0 END) as check_sales,
            SUM(CASE WHEN payment_status = 'کارت' THEN total ELSE 0 END) as card_sales,
            SUM(CASE WHEN payment_status = 'نسیه' THEN total ELSE 0 END) as credit_sales
        FROM Invoices
        WHERE DATE(invoice_date) BETWEEN ? AND ?
        AND invoice_type IN ('فروش', 'خدمات')
        """
        
        result = self.data_manager.db.fetch_one(query, (start_date, end_date))
        data['general_stats'] = result or {}
        
        # محاسبه نرخ تکمیل پرداخت
        if result and result.get('total_sales', 0) > 0:
            total_sales = result['total_sales']
            unpaid = result.get('credit_sales', 0)
            paid = total_sales - unpaid
            data['general_stats']['payment_completion_rate'] = (paid / total_sales * 100) if total_sales > 0 else 0
        
        self.progress_updated.emit("در حال دریافت محصولات پرفروش...", 50)
        
        # محصولات پرفروش
        query = """
        SELECT 
            p.part_name as product_name,
            p.category,
            p.brand,
            COUNT(ii.id) as sale_count,
            SUM(ii.total_price) as total_sales_amount,
            SUM(ii.total_price * 0.3) as estimated_profit  # 30% سود فرضی
        FROM InvoiceItems ii
        JOIN Invoices i ON ii.invoice_id = i.id
        LEFT JOIN Parts p ON ii.item_id = p.id
        WHERE DATE(i.invoice_date) BETWEEN ? AND ?
        AND ii.item_type = 'قطعه'
        GROUP BY p.id
        ORDER BY total_sales_amount DESC
        LIMIT 15
        """
        
        data['top_products'] = self.data_manager.db.fetch_all(query, (start_date, end_date))
        
        self.progress_updated.emit("در حال دریافت مشتریان برتر...", 80)
        
        # مشتریان برتر
        query = """
        SELECT 
            p.first_name || ' ' || p.last_name as customer_name,
            p.mobile,
            COUNT(i.id) as invoice_count,
            SUM(i.total) as total_purchases,
            CASE 
                WHEN SUM(i.total) > 10000000 THEN 'VIP 🏆'
                WHEN COUNT(i.id) > 5 THEN 'وفادار 💎'
                ELSE 'عادی'
            END as customer_type,
            (COUNT(i.id) * 10 + SUM(i.total) / 1000000) as loyalty_score
        FROM Invoices i
        JOIN Persons p ON i.customer_id = p.id
        WHERE DATE(i.invoice_date) BETWEEN ? AND ?
        AND i.invoice_type IN ('فروش', 'خدمات')
        GROUP BY p.id
        ORDER BY total_purchases DESC
        LIMIT 12
        """
        
        data['top_customers'] = self.data_manager.db.fetch_all(query, (start_date, end_date))
        
        return data
    
    def stop(self):
        """توقف لودر"""
        self.is_running = False


class ReportCache:
    """کش برای گزارش‌ها"""
    
    def __init__(self, max_size=10):
        self.cache = {}
        self.max_size = max_size
        self.lock = threading.Lock()
    
    def get(self, key):
        """دریافت از کش"""
        with self.lock:
            if key in self.cache:
                # بروزرسانی زمان دسترسی
                self.cache[key]['access_time'] = time.time()
                return self.cache[key]['data']
            return None
    
    def set(self, key, data, ttl=300):  # TTL = 5 دقیقه
        """ذخیره در کش"""
        with self.lock:
            # اگر کش پر است، قدیمی‌ترین آیتم را حذف کن
            if len(self.cache) >= self.max_size:
                oldest_key = min(self.cache.keys(), key=lambda k: self.cache[k]['access_time'])
                del self.cache[oldest_key]
            
            self.cache[key] = {
                'data': data,
                'access_time': time.time(),
                'expire_time': time.time() + ttl
            }
    
    def clear_expired(self):
        """پاک کردن آیتم‌های منقضی شده"""
        with self.lock:
            current_time = time.time()
            expired_keys = [k for k, v in self.cache.items() if v['expire_time'] < current_time]
            for key in expired_keys:
                del self.cache[key]
    
    def clear(self):
        """پاک کردن کامل کش"""
        with self.lock:
            self.cache.clear()


class PerformanceMonitor:
    """مانیتورینگ عملکرد گزارش‌ها"""
    
    def __init__(self):
        self.stats = {
            'load_times': {},
            'query_counts': {},
            'cache_hits': 0,
            'cache_misses': 0
        }
    
    def record_load_time(self, report_type, duration):
        """ثبت زمان لود گزارش"""
        if report_type not in self.stats['load_times']:
            self.stats['load_times'][report_type] = []
        
        self.stats['load_times'][report_type].append(duration)
        
        # حفظ فقط ۱۰ مورد آخر
        if len(self.stats['load_times'][report_type]) > 10:
            self.stats['load_times'][report_type] = self.stats['load_times'][report_type][-10:]
    
    def record_query(self, query_type):
        """ثبت کوئری"""
        if query_type not in self.stats['query_counts']:
            self.stats['query_counts'][query_type] = 0
        
        self.stats['query_counts'][query_type] += 1
    
    def record_cache_hit(self):
        """ثبت hit کش"""
        self.stats['cache_hits'] += 1
    
    def record_cache_miss(self):
        """ثبت miss کش"""
        self.stats['cache_misses'] += 1
    
    def get_stats(self):
        """دریافت آمار"""
        stats_summary = {
            'total_cache_hits': self.stats['cache_hits'],
            'total_cache_misses': self.stats['cache_misses'],
            'cache_hit_rate': (self.stats['cache_hits'] / (self.stats['cache_hits'] + self.stats['cache_misses'])) * 100 
                if (self.stats['cache_hits'] + self.stats['cache_misses']) > 0 else 0,
            'avg_load_times': {},
            'query_counts': self.stats['query_counts']
        }
        
        # محاسبه میانگین زمان‌ها
        for report_type, times in self.stats['load_times'].items():
            if times:
                stats_summary['avg_load_times'][report_type] = sum(times) / len(times)
        
        return stats_summary