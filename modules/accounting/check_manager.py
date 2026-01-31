"""
مدیریت چک‌های دریافتی و پرداختی
"""

from PySide6.QtCore import QObject, Signal
import jdatetime
from datetime import datetime

class CheckManager(QObject):
    """مدیریت کامل چک‌ها"""
    
    data_changed = Signal(str)
    
    def __init__(self, data_manager):
        super().__init__()
        self.data_manager = data_manager
        self.db = data_manager.db
    
    def create_check(self, check_data):
        """ایجاد چک جدید"""
        try:
            # اعتبارسنجی
            amount = float(check_data.get('amount', 0))
            if amount <= 0:
                return False, "مبلغ چک باید بیشتر از صفر باشد"
            
            # تبدیل مبلغ به ریال
            amount_rial = amount * 10
            
            # تاریخ‌ها
            issue_date_gregorian = self.db.jalali_to_gregorian(check_data.get('issue_date'))
            due_date_gregorian = self.db.jalali_to_gregorian(check_data.get('due_date'))
            
            query = """
            INSERT INTO Checks (
                check_number, bank_name, branch, account_number, amount,
                issue_date, due_date, drawer, payee, status, check_type,
                related_invoice, description
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            
            params = (
                check_data.get('check_number'),
                check_data.get('bank_name'),
                check_data.get('branch', ''),
                check_data.get('account_number', ''),
                amount_rial,
                issue_date_gregorian,
                due_date_gregorian,
                check_data.get('drawer'),
                check_data.get('payee'),
                check_data.get('status', 'وصول نشده'),
                check_data.get('check_type', 'دریافتی'),
                check_data.get('related_invoice'),
                check_data.get('description', '')
            )
            
            success = self.db.execute_query(query, params)
            
            if success:
                # اگر چک دریافتی است، تراکنش ثبت کن
                if check_data.get('check_type') == 'دریافتی':
                    # ثبت تراکنش موقت (وقتی چک وصول شد، تراکنش نهایی ثبت می‌شود)
                    self._record_check_transaction(check_data, amount_rial, 'در انتظار')
                
                self.data_changed.emit("Checks")
                return True, "چک با موفقیت ثبت شد"
            return False, "خطا در ثبت چک"
            
        except Exception as e:
            return False, f"خطا: {str(e)}"
    
    def _record_check_transaction(self, check_data, amount_rial, status):
        """ثبت تراکنش مربوط به چک"""
        # در جدول تراکنش‌های حسابداری ثبت می‌کنیم
        transaction_data = {
            'transaction_type': 'دریافت',
            'to_account_id': check_data.get('account_id'),
            'amount': amount_rial / 10,  # تومان
            'description': f"چک دریافتی #{check_data.get('check_number')} - وضعیت: {status}",
            'employee': check_data.get('employee', 'سیستم')
        }
        
        from .transaction_manager import TransactionManager
        transaction_manager = TransactionManager(self.data_manager)
        transaction_manager.create_transaction(transaction_data)
    
    def update_check_status(self, check_id, status):
        """بروزرسانی وضعیت چک"""
        valid_statuses = ['وصول نشده', 'وصول شده', 'برگشتی', 'پاس شده', 'پاس نشده', 'بلوکه شده']
        
        if status not in valid_statuses:
            return False, "وضعیت نامعتبر"
        
        query = """
        UPDATE Checks 
        SET status = ?, updated_at = CURRENT_TIMESTAMP 
        WHERE id = ?
        """
        
        success = self.db.execute_query(query, (status, check_id))
        
        if success:
            # اگر چک وصول شد، تراکنش نهایی ثبت کن
            if status == 'وصول شده':
                self._finalize_check_transaction(check_id)
            
            self.data_changed.emit("Checks")
            return True, f"وضعیت چک به '{status}' تغییر کرد"
        return False, "خطا در بروزرسانی وضعیت"
    
    def _finalize_check_transaction(self, check_id):
        """ثبت نهایی تراکنش چک وصول شده"""
        check = self.get_check_by_id(check_id)
        if not check or check['check_type'] != 'دریافتی':
            return
        
        # بروزرسانی توضیحات تراکنش قبلی
        self.db.execute_query(
            "UPDATE AccountingTransactions SET description = description || ' (وصول شد)' WHERE description LIKE ?",
            (f"%چک دریافتی #{check['check_number']}%",)
        )
    
    def get_all_checks(self, check_type=None, status=None):
        """دریافت تمام چک‌ها"""
        query = """
        SELECT 
            c.*,
            i.invoice_number,
            p.first_name || ' ' || p.last_name as customer_name
        FROM Checks c
        LEFT JOIN Invoices i ON c.related_invoice = i.id
        LEFT JOIN Persons p ON c.drawer = p.id OR c.payee = p.id
        WHERE 1=1
        """
        
        params = []
        
        if check_type:
            query += " AND c.check_type = ?"
            params.append(check_type)
        
        if status:
            query += " AND c.status = ?"
            params.append(status)
        
        query += " ORDER BY c.due_date"
        
        checks = self.db.fetch_all(query, params)
        
        # تبدیل تاریخ‌ها و مبالغ
        for check in checks:
            check['issue_date_shamsi'] = self.db.gregorian_to_jalali(check['issue_date'])
            check['due_date_shamsi'] = self.db.gregorian_to_jalali(check['due_date'])
            check['amount_toman'] = check['amount'] / 10
        
        return checks
    
    def get_check_by_id(self, check_id):
        """دریافت چک با شناسه"""
        query = """
        SELECT 
            c.*,
            i.invoice_number,
            p.first_name || ' ' || p.last_name as customer_name
        FROM Checks c
        LEFT JOIN Invoices i ON c.related_invoice = i.id
        LEFT JOIN Persons p ON c.drawer = p.id OR c.payee = p.id
        WHERE c.id = ?
        """
        
        check = self.db.fetch_one(query, (check_id,))
        
        if check:
            check['issue_date_shamsi'] = self.db.gregorian_to_jalali(check['issue_date'])
            check['due_date_shamsi'] = self.db.gregorian_to_jalali(check['due_date'])
            check['amount_toman'] = check['amount'] / 10
        
        return check
    
    def get_due_checks(self, days=7):
        """دریافت چک‌های در سررسید نزدیک - نسخه اصلاح شده"""
        try:
            # SQLite نمی‌تواند پارامتر را در date() بپذیرد، پس رشته‌سازی می‌کنیم
            query = f"""
            SELECT 
                c.*,
                p.first_name || ' ' || p.last_name as customer_name
            FROM Checks c
            LEFT JOIN Persons p ON c.drawer = p.id OR c.payee = p.id
            WHERE c.status IN ('وصول نشده', 'پاس نشده')
            AND date(c.due_date) <= date('now', '+{days} days')
            AND date(c.due_date) >= date('now')
            ORDER BY c.due_date
            """
            
            checks = self.db.fetch_all(query)  # بدون پارامتر
            
            # تبدیل تاریخ‌ها و مبالغ
            for check in checks:
                check['issue_date_shamsi'] = self.db.gregorian_to_jalali(check['issue_date'])
                check['due_date_shamsi'] = self.db.gregorian_to_jalali(check['due_date'])
                check['amount_toman'] = check['amount'] / 10
            
            return checks
            
        except Exception as e:
            print(f"⚠️ خطا در دریافت چک‌های سررسید: {e}")
            return []
    
    def get_check_statistics(self):
        """آمار چک‌ها"""
        query = """
        SELECT 
            check_type,
            status,
            COUNT(*) as count,
            SUM(amount) as total_amount
        FROM Checks
        GROUP BY check_type, status
        ORDER BY check_type, status
        """
        
        stats = self.db.fetch_all(query)
        
        # تبدیل به تومان
        for stat in stats:
            stat['total_amount_toman'] = stat['total_amount'] / 10
        
        return stats
    
    def get_bounced_checks(self):
        """دریافت چک‌های برگشتی"""
        query = """
        SELECT 
            c.*,
            p.first_name || ' ' || p.last_name as customer_name
        FROM Checks c
        LEFT JOIN Persons p ON c.drawer = p.id OR c.payee = p.id
        WHERE c.status = 'برگشتی'
        ORDER BY c.due_date DESC
        """
        
        checks = self.db.fetch_all(query)
        
        # تبدیل تاریخ‌ها و مبالغ
        for check in checks:
            check['issue_date_shamsi'] = self.db.gregorian_to_jalali(check['issue_date'])
            check['due_date_shamsi'] = self.db.gregorian_to_jalali(check['due_date'])
            check['amount_toman'] = check['amount'] / 10
        
        return checks