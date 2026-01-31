"""
مدیریت تراکنش‌های مالی
"""

from PySide6.QtCore import QObject, Signal
import jdatetime
from datetime import datetime

class TransactionManager(QObject):
    """مدیریت کامل تراکنش‌های مالی"""
    
    data_changed = Signal(str)
    
    def __init__(self, data_manager):
        super().__init__()
        self.data_manager = data_manager
        self.db = data_manager.db
    
    # ---------- تراکنش‌ها ----------
    
    def create_transaction(self, transaction_data):
        """ایجاد تراکنش جدید"""
        try:
            # اعتبارسنجی داده‌ها
            validation_result = self._validate_transaction(transaction_data)
            if not validation_result['success']:
                return False, validation_result['message']
            
            # تبدیل مبلغ به ریال
            amount_rial = float(transaction_data.get('amount', 0)) * 10
            
            # تاریخ تراکنش (اگر داده نشده، امروز)
            transaction_date = transaction_data.get('transaction_date')
            if not transaction_date:
                transaction_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            query = """
            INSERT INTO AccountingTransactions (
                transaction_date, transaction_type, from_account_id, to_account_id,
                amount, description, employee, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, datetime('now'))
            """
            
            params = (
                transaction_date,
                transaction_data.get('transaction_type'),
                transaction_data.get('from_account_id'),
                transaction_data.get('to_account_id'),
                amount_rial,
                transaction_data.get('description', ''),
                transaction_data.get('employee', 'سیستم')
            )
            
            success = self.db.execute_query(query, params)
            
            if success:
                # بروزرسانی موجودی حساب‌ها
                self._update_account_balances(transaction_data, amount_rial)
                
                self.data_changed.emit("AccountingTransactions")
                return True, "تراکنش با موفقیت ثبت شد"
            return False, "خطا در ثبت تراکنش"
            
        except Exception as e:
            return False, f"خطا: {str(e)}"
    
    def _validate_transaction(self, transaction_data):
        """اعتبارسنجی تراکنش"""
        transaction_type = transaction_data.get('transaction_type')
        from_account_id = transaction_data.get('from_account_id')
        to_account_id = transaction_data.get('to_account_id')
        amount = float(transaction_data.get('amount', 0))
        
        # بررسی مبلغ
        if amount <= 0:
            return {'success': False, 'message': 'مبلغ باید بیشتر از صفر باشد'}
        
        # بر اساس نوع تراکنش، اعتبارسنجی
        if transaction_type == 'انتقال':
            if not from_account_id or not to_account_id:
                return {'success': False, 'message': 'برای انتقال باید حساب مبدا و مقصد مشخص باشد'}
            
            if from_account_id == to_account_id:
                return {'success': False, 'message': 'حساب مبدا و مقصد نمی‌توانند یکی باشند'}
            
            # بررسی موجودی کافی در حساب مبدا
            from_account = self.db.fetch_one(
                "SELECT current_balance FROM Accounts WHERE id = ?", 
                (from_account_id,)
            )
            
            if not from_account:
                return {'success': False, 'message': 'حساب مبدا یافت نشد'}
            
            if from_account['current_balance'] < (amount * 10):
                return {'success': False, 'message': 'موجودی حساب مبدا کافی نیست'}
                
        elif transaction_type == 'دریافت':
            if not to_account_id:
                return {'success': False, 'message': 'برای دریافت باید حساب مقصد مشخص باشد'}
                
        elif transaction_type == 'پرداخت':
            if not from_account_id:
                return {'success': False, 'message': 'برای پرداخت باید حساب مبدا مشخص باشد'}
            
            # بررسی موجودی کافی
            from_account = self.db.fetch_one(
                "SELECT current_balance FROM Accounts WHERE id = ?", 
                (from_account_id,)
            )
            
            if not from_account:
                return {'success': False, 'message': 'حساب مبدا یافت نشد'}
            
            if from_account['current_balance'] < (amount * 10):
                return {'success': False, 'message': 'موجودی حساب مبدا کافی نیست'}
        
        return {'success': True, 'message': 'اعتبارسنجی موفق'}
    
    def _update_account_balances(self, transaction_data, amount_rial):
        """بروزرسانی موجودی حساب‌ها پس از تراکنش"""
        transaction_type = transaction_data.get('transaction_type')
        from_account_id = transaction_data.get('from_account_id')
        to_account_id = transaction_data.get('to_account_id')
        
        if transaction_type == 'انتقال':
            # کسر از حساب مبدا
            self.db.execute_query(
                "UPDATE Accounts SET current_balance = current_balance - ? WHERE id = ?",
                (amount_rial, from_account_id)
            )
            
            # افزودن به حساب مقصد
            self.db.execute_query(
                "UPDATE Accounts SET current_balance = current_balance + ? WHERE id = ?",
                (amount_rial, to_account_id)
            )
            
        elif transaction_type == 'دریافت' and to_account_id:
            # افزودن به حساب
            self.db.execute_query(
                "UPDATE Accounts SET current_balance = current_balance + ? WHERE id = ?",
                (amount_rial, to_account_id)
            )
            
        elif transaction_type == 'پرداخت' and from_account_id:
            # کسر از حساب
            self.db.execute_query(
                "UPDATE Accounts SET current_balance = current_balance - ? WHERE id = ?",
                (amount_rial, from_account_id)
            )
        
        self.data_changed.emit("Accounts")
    
    def get_all_transactions(self, start_date=None, end_date=None, transaction_type=None):
        """دریافت تمام تراکنش‌ها"""
        query = """
        SELECT 
            at.*,
            a1.account_name as from_account_name,
            a2.account_name as to_account_name
        FROM AccountingTransactions at
        LEFT JOIN Accounts a1 ON at.from_account_id = a1.id
        LEFT JOIN Accounts a2 ON at.to_account_id = a2.id
        WHERE 1=1
        """
        
        params = []
        
        if start_date:
            query += " AND DATE(at.transaction_date) >= ?"
            params.append(start_date)
        
        if end_date:
            query += " AND DATE(at.transaction_date) <= ?"
            params.append(end_date)
        
        if transaction_type:
            query += " AND at.transaction_type = ?"
            params.append(transaction_type)
        
        query += " ORDER BY at.transaction_date DESC"
        
        transactions = self.db.fetch_all(query, params)
        
        # تبدیل تاریخ و مبلغ
        for transaction in transactions:
            transaction['transaction_date_shamsi'] = self.db.gregorian_to_jalali(
                transaction['transaction_date']
            )
            transaction['amount_toman'] = transaction['amount'] / 10
        
        return transactions
    
    def get_transaction_by_id(self, transaction_id):
        """دریافت تراکنش با شناسه"""
        query = """
        SELECT 
            at.*,
            a1.account_name as from_account_name,
            a2.account_name as to_account_name
        FROM AccountingTransactions at
        LEFT JOIN Accounts a1 ON at.from_account_id = a1.id
        LEFT JOIN Accounts a2 ON at.to_account_id = a2.id
        WHERE at.id = ?
        """
        
        transaction = self.db.fetch_one(query, (transaction_id,))
        
        if transaction:
            transaction['transaction_date_shamsi'] = self.db.gregorian_to_jalali(
                transaction['transaction_date']
            )
            transaction['amount_toman'] = transaction['amount'] / 10
        
        return transaction
    
    def update_transaction(self, transaction_id, transaction_data):
        """ویرایش تراکنش - پیچیده است، معمولاً نباید اجازه داد"""
        # در سیستم‌های حسابداری حرفه‌ای، ویرایش تراکنش مجاز نیست
        # فقط می‌توان تراکنش معکوس ایجاد کرد
        return False, "ویرایش تراکنش مجاز نیست. لطفاً تراکنش معکوس ایجاد کنید."
    
    def reverse_transaction(self, transaction_id, reason=""):
        """ایجاد تراکنش معکوس"""
        try:
            # دریافت تراکنش اصلی
            original = self.get_transaction_by_id(transaction_id)
            if not original:
                return False, "تراکنش یافت نشد"
            
            # ایجاد تراکنش معکوس
            reverse_data = {
                'transaction_type': original['transaction_type'],
                'from_account_id': original['to_account_id'],
                'to_account_id': original['from_account_id'],
                'amount': original['amount_toman'],
                'description': f"تراکنش معکوس #{transaction_id}" + (f" - {reason}" if reason else ""),
                'employee': 'سیستم'
            }
            
            success, message = self.create_transaction(reverse_data)
            
            if success:
                # علامت گذاری تراکنش اصلی به عنوان معکوس شده
                self.db.execute_query(
                    "UPDATE AccountingTransactions SET description = description || ' (معکوس شده)' WHERE id = ?",
                    (transaction_id,)
                )
                return True, "تراکنش معکوس با موفقیت ایجاد شد"
            return False, message
            
        except Exception as e:
            return False, f"خطا: {str(e)}"
    
    def get_daily_summary(self, date=None):
        """خلاصه تراکنش‌های روز"""
        if not date:
            # تاریخ امروز
            date = datetime.now().strftime("%Y-%m-%d")
        
        query = """
        SELECT 
            transaction_type,
            COUNT(*) as count,
            SUM(amount) as total_amount
        FROM AccountingTransactions
        WHERE DATE(transaction_date) = ?
        GROUP BY transaction_type
        ORDER BY transaction_type
        """
        
        summary = self.db.fetch_all(query, (date,))
        
        # تبدیل به تومان
        for item in summary:
            item['total_amount_toman'] = item['total_amount'] / 10
        
        # محاسبه جمع کل
        total_income = sum(item['total_amount'] for item in summary if item['transaction_type'] == 'دریافت')
        total_expense = sum(item['total_amount'] for item in summary if item['transaction_type'] == 'پرداخت')
        net_change = total_income - total_expense
        
        return {
            'date': date,
            'date_shamsi': self.db.gregorian_to_jalali(date),
            'summary': summary,
            'total_income': total_income / 10,
            'total_expense': total_expense / 10,
            'net_change': net_change / 10,
            'total_transactions': sum(item['count'] for item in summary)
        }
    
    def get_monthly_summary(self, year=None, month=None):
        """خلاصه تراکنش‌های ماه"""
        if not year or not month:
            today = jdatetime.datetime.now()
            year = today.year
            month = today.month
        
        # تبدیل به محدوده میلادی
        start_jalali = f"{year}/{month:02d}/01"
        end_jalali = f"{year}/{month:02d}/31"
        
        start_gregorian = self.db.jalali_to_gregorian(start_jalali)
        end_gregorian = self.db.jalali_to_gregorian(end_jalali)
        
        query = """
        SELECT 
            transaction_type,
            COUNT(*) as count,
            SUM(amount) as total_amount
        FROM AccountingTransactions
        WHERE DATE(transaction_date) BETWEEN ? AND ?
        GROUP BY transaction_type
        ORDER BY transaction_type
        """
        
        summary = self.db.fetch_all(query, (start_gregorian, end_gregorian))
        
        # تبدیل به تومان
        for item in summary:
            item['total_amount_toman'] = item['total_amount'] / 10
        
        # محاسبه جمع کل
        total_income = sum(item['total_amount'] for item in summary if item['transaction_type'] == 'دریافت')
        total_expense = sum(item['total_amount'] for item in summary if item['transaction_type'] == 'پرداخت')
        net_change = total_income - total_expense
        
        month_name = self._get_persian_month_name(month)
        
        return {
            'year': year,
            'month': month,
            'month_name': month_name,
            'summary': summary,
            'total_income': total_income / 10,
            'total_expense': total_expense / 10,
            'net_change': net_change / 10,
            'total_transactions': sum(item['count'] for item in summary)
        }
    
    def _get_persian_month_name(self, month):
        """نام ماه فارسی"""
        months = {
            1: "فروردین", 2: "اردیبهشت", 3: "خرداد",
            4: "تیر", 5: "مرداد", 6: "شهریور",
            7: "مهر", 8: "آبان", 9: "آذر",
            10: "دی", 11: "بهمن", 12: "اسفند"
        }
        return months.get(month, "")
    
    def get_cash_flow(self, start_date, end_date):
        """گزارش گردش نقدی"""
        query = """
        SELECT 
            DATE(transaction_date) as date,
            SUM(CASE WHEN transaction_type = 'دریافت' THEN amount ELSE 0 END) as income,
            SUM(CASE WHEN transaction_type = 'پرداخت' THEN amount ELSE 0 END) as expense,
            SUM(CASE WHEN transaction_type = 'دریافت' THEN amount ELSE -amount END) as net_cash_flow
        FROM AccountingTransactions
        WHERE DATE(transaction_date) BETWEEN ? AND ?
        GROUP BY DATE(transaction_date)
        ORDER BY DATE(transaction_date)
        """
        
        cash_flow = self.db.fetch_all(query, (start_date, end_date))
        
        # تبدیل به تومان و تاریخ شمسی
        for item in cash_flow:
            item['date_shamsi'] = self.db.gregorian_to_jalali(item['date'])
            item['income_toman'] = item['income'] / 10
            item['expense_toman'] = item['expense'] / 10
            item['net_cash_flow_toman'] = item['net_cash_flow'] / 10
        
        return cash_flow