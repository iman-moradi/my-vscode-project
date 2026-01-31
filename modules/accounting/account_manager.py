"""
مدیریت حساب‌ها و موجودی‌ها
"""

from PySide6.QtCore import QObject, Signal
import jdatetime
from datetime import datetime

class AccountManager(QObject):
    """مدیریت کامل حساب‌های بانکی و نقدی"""
    
    data_changed = Signal(str)
    
    def __init__(self, data_manager):
        super().__init__()
        self.data_manager = data_manager
        self.db = data_manager.db
    
    # ---------- حساب‌ها ----------
    
    def get_all_accounts(self, active_only=True):
        """دریافت تمام حساب‌ها"""
        if active_only:
            query = "SELECT * FROM Accounts WHERE is_active = 1 ORDER BY account_type, account_name"
        else:
            query = "SELECT * FROM Accounts ORDER BY account_type, account_name"
        
        accounts = self.db.fetch_all(query)
        
        # تبدیل موجودی‌ها به تومان برای نمایش
        for account in accounts:
            account['current_balance_display'] = account['current_balance'] / 10
            account['initial_balance_display'] = account['initial_balance'] / 10
        
        return accounts
    
    def get_account_by_id(self, account_id):
        """دریافت حساب با شناسه"""
        query = "SELECT * FROM Accounts WHERE id = ?"
        account = self.db.fetch_one(query, (account_id,))
        
        if account:
            account['current_balance_display'] = account['current_balance'] / 10
            account['initial_balance_display'] = account['initial_balance'] / 10
        
        return account
    
    def create_account(self, account_data):
        """ایجاد حساب جدید"""
        try:
            # تبدیل موجودی به ریال
            initial_balance = float(account_data.get('initial_balance', 0)) * 10
            
            query = """
            INSERT INTO Accounts (
                account_number, account_name, account_type, bank_name,
                initial_balance, current_balance, owner_name, description, is_active
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            
            params = (
                account_data.get('account_number', ''),
                account_data.get('account_name', ''),
                account_data.get('account_type', 'جاری'),
                account_data.get('bank_name', ''),
                initial_balance,
                initial_balance,  # موجودی فعلی برابر با موجودی اولیه
                account_data.get('owner_name', ''),
                account_data.get('description', ''),
                1  # فعال
            )
            
            success = self.db.execute_query(query, params)
            if success:
                self.data_changed.emit("Accounts")
                return True, "حساب با موفقیت ایجاد شد"
            return False, "خطا در ایجاد حساب"
            
        except Exception as e:
            return False, f"خطا: {str(e)}"
    
    def update_account(self, account_id, account_data):
        """ویرایش حساب"""
        query = """
        UPDATE Accounts SET
            account_number = ?,
            account_name = ?,
            account_type = ?,
            bank_name = ?,
            owner_name = ?,
            description = ?,
            updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
        """
        
        params = (
            account_data.get('account_number', ''),
            account_data.get('account_name', ''),
            account_data.get('account_type', 'جاری'),
            account_data.get('bank_name', ''),
            account_data.get('owner_name', ''),
            account_data.get('description', ''),
            account_id
        )
        
        success = self.db.execute_query(query, params)
        if success:
            self.data_changed.emit("Accounts")
            return True, "حساب با موفقیت ویرایش شد"
        return False, "خطا در ویرایش حساب"
    
    def delete_account(self, account_id):
        """غیرفعال کردن حساب"""
        query = "UPDATE Accounts SET is_active = 0 WHERE id = ?"
        success = self.db.execute_query(query, (account_id,))
        
        if success:
            self.data_changed.emit("Accounts")
            return True, "حساب غیرفعال شد"
        return False, "خطا در غیرفعال کردن حساب"
    
    def get_total_balance(self):
        """محاسبه موجودی کل تمام حساب‌ها"""
        query = """
        SELECT SUM(current_balance) as total_balance
        FROM Accounts 
        WHERE is_active = 1
        """
        
        result = self.db.fetch_one(query)
        total_balance = result.get('total_balance', 0) if result else 0
        
        return {
            'total_rial': total_balance,
            'total_toman': total_balance / 10
        }
    
    def get_accounts_summary(self):
        """خلاصه وضعیت حساب‌ها"""
        query = """
        SELECT 
            account_type,
            COUNT(*) as count,
            SUM(current_balance) as total_balance
        FROM Accounts 
        WHERE is_active = 1
        GROUP BY account_type
        ORDER BY total_balance DESC
        """
        
        summary = self.db.fetch_all(query)
        
        # تبدیل به تومان
        for item in summary:
            item['total_balance_toman'] = item['total_balance'] / 10
        
        return summary
    
    # ---------- تراکنش‌های حساب ----------
    
    def get_account_transactions(self, account_id, start_date=None, end_date=None):
        """دریافت تراکنش‌های یک حساب"""
        query = """
        SELECT 
            at.*,
            a1.account_name as from_account_name,
            a2.account_name as to_account_name,
            CASE 
                WHEN at.from_account_id = ? THEN 'برداشت'
                WHEN at.to_account_id = ? THEN 'واریز'
                ELSE 'نامشخص'
            END as transaction_direction
        FROM AccountingTransactions at
        LEFT JOIN Accounts a1 ON at.from_account_id = a1.id
        LEFT JOIN Accounts a2 ON at.to_account_id = a2.id
        WHERE (at.from_account_id = ? OR at.to_account_id = ?)
        """
        
        params = [account_id, account_id, account_id, account_id]
        
        if start_date:
            query += " AND DATE(at.transaction_date) >= ?"
            params.append(start_date)
        
        if end_date:
            query += " AND DATE(at.transaction_date) <= ?"
            params.append(end_date)
        
        query += " ORDER BY at.transaction_date DESC"
        
        transactions = self.db.fetch_all(query, params)
        
        # تبدیل تاریخ‌ها به شمسی
        for transaction in transactions:
            transaction['transaction_date_shamsi'] = self.db.gregorian_to_jalali(
                transaction['transaction_date']
            )
            transaction['amount_toman'] = transaction['amount'] / 10
        
        return transactions
    
    def get_account_balance_history(self, account_id, days=30):
        """تاریخچه موجودی حساب"""
        import datetime as dt
        
        end_date = dt.datetime.now()
        start_date = end_date - dt.timedelta(days=days)
        
        query = """
        SELECT 
            DATE(transaction_date) as date,
            SUM(CASE 
                WHEN to_account_id = ? THEN amount 
                WHEN from_account_id = ? THEN -amount 
                ELSE 0 
            END) as daily_change
        FROM AccountingTransactions
        WHERE transaction_date BETWEEN ? AND ?
            AND (from_account_id = ? OR to_account_id = ?)
        GROUP BY DATE(transaction_date)
        ORDER BY DATE(transaction_date)
        """
        
        params = [account_id, account_id, 
                 start_date.strftime("%Y-%m-%d"), 
                 end_date.strftime("%Y-%m-%d"),
                 account_id, account_id]
        
        return self.db.fetch_all(query, params)