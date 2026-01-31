# ui/forms/reports/utils/financial_calculator.py
"""
ماژول کمکی برای محاسبات مالی از دیتابیس
"""

from PySide6.QtCore import QDate
from utils.date_utils import jalali_to_gregorian, gregorian_to_jalali


class FinancialCalculator:
    """کلاس محاسبه کننده داده‌های مالی از دیتابیس"""
    
    def __init__(self, data_manager):
        self.data_manager = data_manager
    
    def get_financial_summary(self, start_date=None, end_date=None):
        """دریافت خلاصه مالی برای بازه زمانی مشخص"""
        try:
            # تبدیل تاریخ‌های شمسی به میلادی برای جستجو در دیتابیس
            start_greg = None
            end_greg = None
            
            if start_date:
                start_greg = jalali_to_gregorian(start_date, "%Y-%m-%d")
            if end_date:
                end_greg = jalali_to_gregorian(end_date, "%Y-%m-%d")
            
            # ۱. دریافت درآمدها (فاکتورهای پرداخت شده)
            income_data = self.get_income_data(start_greg, end_greg)
            
            # ۲. دریافت هزینه‌ها (تراکنش‌های پرداخت)
            expense_data = self.get_expense_data(start_greg, end_greg)
            
            # ۳. محاسبات
            total_income = sum(item['amount'] for item in income_data)
            total_expense = sum(item['amount'] for item in expense_data)
            net_profit = total_income - total_expense
            profit_margin = (net_profit / total_income * 100) if total_income > 0 else 0
            
            # ۴. تعداد تراکنش‌ها
            transaction_count = len(income_data) + len(expense_data)
            
            # ۵. محاسبه میانگین روزانه
            if start_date and end_date:
                # تعداد روزهای بازه
                days_count = self.get_days_between(start_date, end_date)
                daily_avg_income = total_income / days_count if days_count > 0 else 0
            else:
                daily_avg_income = 0
            
            return {
                'total_income': total_income,
                'total_expense': total_expense,
                'net_profit': net_profit,
                'profit_margin': profit_margin,
                'transaction_count': transaction_count,
                'daily_avg_income': daily_avg_income,
                'income_transactions': len(income_data),
                'expense_transactions': len(expense_data)
            }
            
        except Exception as e:
            print(f"❌ خطا در محاسبه خلاصه مالی: {e}")
            return {
                'total_income': 0,
                'total_expense': 0,
                'net_profit': 0,
                'profit_margin': 0,
                'transaction_count': 0,
                'daily_avg_income': 0,
                'income_transactions': 0,
                'expense_transactions': 0
            }
    
    def get_income_data(self, start_date=None, end_date=None):
        """دریافت درآمدها از فاکتورهای پرداخت شده"""
        try:
            query = """
            SELECT 
                i.id,
                i.invoice_date,
                i.total as amount,
                i.payment_status,
                c.full_name as customer_name
            FROM Invoices i
            LEFT JOIN Persons c ON i.customer_id = c.id
            WHERE i.invoice_type IN ('فروش', 'خدمات')
            AND i.payment_status IN ('پرداخت شده', 'نقدی')
            """
            
            params = []
            if start_date and end_date:
                query += " AND DATE(i.invoice_date) BETWEEN ? AND ?"
                params.extend([start_date, end_date])
            elif start_date:
                query += " AND DATE(i.invoice_date) >= ?"
                params.append(start_date)
            elif end_date:
                query += " AND DATE(i.invoice_date) <= ?"
                params.append(end_date)
            
            query += " ORDER BY i.invoice_date DESC"
            
            return self.data_manager.db.fetch_all(query, params)
            
        except Exception as e:
            print(f"❌ خطا در دریافت درآمدها: {e}")
            return []
    
    def get_expense_data(self, start_date=None, end_date=None):
        """دریافت هزینه‌ها از تراکنش‌های حسابداری"""
        try:
            query = """
            SELECT 
                at.id,
                at.transaction_date,
                at.amount,
                at.transaction_type,
                at.description,
                a1.account_name as from_account,
                a2.account_name as to_account
            FROM AccountingTransactions at
            LEFT JOIN Accounts a1 ON at.from_account_id = a1.id
            LEFT JOIN Accounts a2 ON at.to_account_id = a2.id
            WHERE at.transaction_type IN ('پرداخت', 'هزینه')
            """
            
            params = []
            if start_date and end_date:
                query += " AND DATE(at.transaction_date) BETWEEN ? AND ?"
                params.extend([start_date, end_date])
            elif start_date:
                query += " AND DATE(at.transaction_date) >= ?"
                params.append(start_date)
            elif end_date:
                query += " AND DATE(at.transaction_date) <= ?"
                params.append(end_date)
            
            query += " ORDER BY at.transaction_date DESC"
            
            return self.data_manager.db.fetch_all(query, params)
            
        except Exception as e:
            print(f"❌ خطا در دریافت هزینه‌ها: {e}")
            return []
    
    def get_daily_financial_data(self, start_date=None, end_date=None):
        """دریافت داده‌های مالی روزانه"""
        try:
            # دریافت درآمد روزانه
            income_query = """
            SELECT 
                DATE(i.invoice_date) as date,
                SUM(i.total) as daily_income,
                COUNT(*) as invoice_count
            FROM Invoices i
            WHERE i.invoice_type IN ('فروش', 'خدمات')
            AND i.payment_status IN ('پرداخت شده', 'نقدی')
            """
            
            income_params = []
            if start_date and end_date:
                income_query += " AND DATE(i.invoice_date) BETWEEN ? AND ?"
                income_params.extend([start_date, end_date])
            
            income_query += " GROUP BY DATE(i.invoice_date) ORDER BY date"
            
            daily_income = self.data_manager.db.fetch_all(income_query, income_params)
            
            # دریافت هزینه روزانه
            expense_query = """
            SELECT 
                DATE(at.transaction_date) as date,
                SUM(at.amount) as daily_expense,
                COUNT(*) as expense_count
            FROM AccountingTransactions at
            WHERE at.transaction_type IN ('پرداخت', 'هزینه')
            """
            
            expense_params = []
            if start_date and end_date:
                expense_query += " AND DATE(at.transaction_date) BETWEEN ? AND ?"
                expense_params.extend([start_date, end_date])
            
            expense_query += " GROUP BY DATE(at.transaction_date) ORDER BY date"
            
            daily_expense = self.data_manager.db.fetch_all(expense_query, expense_params)
            
            # ترکیب داده‌ها
            daily_data = {}
            
            # افزودن درآمدها
            for item in daily_income:
                date = item['date']
                daily_data[date] = {
                    'income': item['daily_income'],
                    'expense': 0,
                    'invoice_count': item['invoice_count'],
                    'expense_count': 0
                }
            
            # افزودن هزینه‌ها
            for item in daily_expense:
                date = item['date']
                if date in daily_data:
                    daily_data[date]['expense'] = item['daily_expense']
                    daily_data[date]['expense_count'] = item['expense_count']
                else:
                    daily_data[date] = {
                        'income': 0,
                        'expense': item['daily_expense'],
                        'invoice_count': 0,
                        'expense_count': item['expense_count']
                    }
            
            # تبدیل به لیست و مرتب‌سازی
            result = []
            for date, data in sorted(daily_data.items()):
                profit = data['income'] - data['expense']
                profit_margin = (profit / data['income'] * 100) if data['income'] > 0 else 0
                
                # تبدیل تاریخ به شمسی برای نمایش
                date_shamsi = gregorian_to_jalali(date)
                
                result.append({
                    'date': date_shamsi,
                    'date_gregorian': date,
                    'income': data['income'],
                    'expense': data['expense'],
                    'profit': profit,
                    'profit_margin': profit_margin,
                    'invoice_count': data['invoice_count'],
                    'expense_count': data['expense_count']
                })
            
            return result
            
        except Exception as e:
            print(f"❌ خطا در دریافت داده‌های روزانه: {e}")
            return []
    
    def get_account_balances(self):
        """دریافت موجودی حساب‌ها"""
        try:
            query = """
            SELECT 
                id,
                account_number,
                account_name,
                account_type,
                bank_name,
                current_balance,
                owner_name
            FROM Accounts
            WHERE is_active = 1
            ORDER BY account_type, account_name
            """
            
            accounts = self.data_manager.db.fetch_all(query)
            
            # تبدیل موجودی به تومان
            for account in accounts:
                account['current_balance_toman'] = account['current_balance'] / 10
            
            return accounts
            
        except Exception as e:
            print(f"❌ خطا در دریافت موجودی حساب‌ها: {e}")
            return []
    
    def get_expense_distribution(self, start_date=None, end_date=None):
        """دریافت توزیع هزینه‌ها بر اساس دسته"""
        try:
            query = """
            SELECT 
                CASE 
                    WHEN description LIKE '%دستمزد%' OR description LIKE '%حقوق%' THEN 'دستمزد'
                    WHEN description LIKE '%قطعات%' OR description LIKE '%لوازم%' THEN 'قطعات و لوازم'
                    WHEN description LIKE '%اجاره%' THEN 'اجاره'
                    WHEN description LIKE '%برق%' OR description LIKE '%آب%' OR description LIKE '%گاز%' THEN 'آب و برق و گاز'
                    WHEN description LIKE '%تعمیر%' OR description LIKE '%تعویض%' THEN 'تعمیرات'
                    WHEN description LIKE '%حمل%' OR description LIKE '%نقل%' THEN 'حمل و نقل'
                    WHEN description LIKE '%تبلیغ%' OR description LIKE '%بازاریابی%' THEN 'تبلیغات'
                    ELSE 'سایر'
                END as category,
                SUM(amount) as total_amount,
                COUNT(*) as transaction_count
            FROM AccountingTransactions
            WHERE transaction_type IN ('پرداخت', 'هزینه')
            """
            
            params = []
            if start_date and end_date:
                query += " AND DATE(transaction_date) BETWEEN ? AND ?"
                params.extend([start_date, end_date])
            
            query += " GROUP BY category ORDER BY total_amount DESC"
            
            distribution = self.data_manager.db.fetch_all(query, params)
            
            # محاسبه درصد
            total = sum(item['total_amount'] for item in distribution)
            for item in distribution:
                item['percentage'] = (item['total_amount'] / total * 100) if total > 0 else 0
            
            return distribution
            
        except Exception as e:
            print(f"❌ خطا در دریافت توزیع هزینه‌ها: {e}")
            return []
    
    def get_days_between(self, start_date_shamsi, end_date_shamsi):
        """محاسبه تعداد روز بین دو تاریخ شمسی"""
        try:
            # تبدیل تاریخ‌های شمسی به میلادی
            start_greg = jalali_to_gregorian(start_date_shamsi, "%Y-%m-%d")
            end_greg = jalali_to_gregorian(end_date_shamsi, "%Y-%m-%d")
            
            # محاسبه اختلاف روز
            from datetime import datetime
            start_dt = datetime.strptime(start_greg, "%Y-%m-%d")
            end_dt = datetime.strptime(end_greg, "%Y-%m-%d")
            
            return (end_dt - start_dt).days + 1  # +1 شامل خود روز اول هم می‌شود
            
        except Exception as e:
            print(f"❌ خطا در محاسبه تعداد روزها: {e}")
            return 1