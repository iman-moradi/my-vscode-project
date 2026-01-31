# modules/accounting/report_generator.py
"""
ماژول تولید گزارش‌های مالی
"""

import jdatetime
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import json
from io import BytesIO

# Import FinancialCalculator از فایل جداگانه
try:
    from .financial_calculator import FinancialCalculator
except ImportError:
    # اگر import نسبی کار نکرد
    from financial_calculator import FinancialCalculator

try:
    from reportlab.lib.pagesizes import A4, landscape
    from reportlab.lib import colors
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch, cm
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    REPORTLAB_AVAILABLE = True
except ImportError:
    print("⚠️ reportlab در دسترس نیست - قابلیت PDF غیرفعال")
    REPORTLAB_AVAILABLE = False


class ReportGenerator:
    """کلاس تولید گزارش‌های مالی"""
    
    def __init__(self, data_manager):
        """
        مقداردهی اولیه تولیدکننده گزارش
        
        Args:
            data_manager: شیء مدیریت داده‌ها
        """
        self.data_manager = data_manager
        self.financial_calculator = FinancialCalculator(data_manager)
        
    # ==================== گزارش‌های آماری ====================
    
    def generate_daily_report(self, report_date: Optional[str] = None) -> Dict:
        """
        تولید گزارش روزانه
        
        Args:
            report_date: تاریخ گزارش (شمسی) - اگر None باشد امروز
            
        Returns:
            dict: گزارش روزانه
        """
        try:
            if not report_date:
                report_date = jdatetime.datetime.now().strftime("%Y/%m/%d")
            
            report_gregorian = self.data_manager.db.jalali_to_gregorian(report_date)
            
            # 1. اطلاعات کلی
            report = {
                'report_date': report_date,
                'report_type': 'گزارش روزانه',
                'generated_at': jdatetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S")
            }
            
            # 2. تراکنش‌های روز
            transactions_query = """
            SELECT 
                transaction_type,
                COUNT(*) as count,
                SUM(amount) as total_amount
            FROM AccountingTransactions
            WHERE DATE(transaction_date) = ?
            GROUP BY transaction_type
            ORDER BY transaction_type
            """
            
            transactions_result = self.data_manager.db.fetch_all(
                transactions_query, 
                (report_gregorian,)
            )
            
            report['transactions_summary'] = transactions_result
            
            # 3. فاکتورهای روز
            invoices_query = """
            SELECT 
                invoice_type,
                COUNT(*) as count,
                SUM(total) as total_amount,
                SUM(paid_amount) as total_paid
            FROM Invoices
            WHERE DATE(invoice_date) = ?
            GROUP BY invoice_type
            ORDER BY invoice_type
            """
            
            invoices_result = self.data_manager.db.fetch_all(
                invoices_query, 
                (report_gregorian,)
            )
            
            report['invoices_summary'] = invoices_result
            
            # 4. چک‌های وصول شده/پاس شده
            checks_query = """
            SELECT 
                check_type,
                status,
                COUNT(*) as count,
                SUM(amount) as total_amount
            FROM Checks
            WHERE DATE(updated_at) = ?
            GROUP BY check_type, status
            ORDER BY check_type, status
            """
            
            checks_result = self.data_manager.db.fetch_all(
                checks_query, 
                (report_gregorian,)
            )
            
            report['checks_summary'] = checks_result
            
            # 5. مانده حساب‌ها در پایان روز
            accounts_query = """
            SELECT 
                account_name,
                account_type,
                current_balance
            FROM Accounts
            WHERE is_active = 1
            ORDER BY account_type, account_name
            """
            
            accounts_result = self.data_manager.db.fetch_all(accounts_query)
            report['accounts_balance'] = accounts_result
            
            # 6. جمع‌بندی مالی
            total_income = sum(item.get('total_amount', 0) or 0 for item in transactions_result 
                            if item.get('transaction_type') in ['دریافت', 'درآمد'])

            total_expense = sum(item.get('total_amount', 0) or 0 for item in transactions_result 
                            if item.get('transaction_type') in ['پرداخت', 'هزینه'])
            net_cash_flow = total_income - total_expense
            
            report['financial_summary'] = {
                'total_income': total_income,
                'total_expense': total_expense,
                'net_cash_flow': net_cash_flow,
                'total_invoices': sum(item['count'] for item in invoices_result),
                'total_invoices_amount': sum(item['total_amount'] for item in invoices_result),
                'total_paid': sum(item['total_paid'] for item in invoices_result),
                'accounts_total_balance': sum(item['current_balance'] for item in accounts_result)
            }
            
            # 7. تحلیل سریع
            report['quick_analysis'] = {
                'income_to_expense_ratio': (total_income / total_expense) if total_expense > 0 else 0,
                'average_invoice_amount': (
                    sum(item['total_amount'] for item in invoices_result) / 
                    sum(item['count'] for item in invoices_result)
                ) if sum(item['count'] for item in invoices_result) > 0 else 0,
                'cash_flow_status': 'مثبت' if net_cash_flow > 0 else 'منفی' if net_cash_flow < 0 else 'متوازن'
            }
            
            return report
            
        except Exception as e:
            print(f"❌ خطا در تولید گزارش روزانه: {e}")
            return {'error': str(e)}
    
    def generate_monthly_report(self, year: Optional[int] = None, 
                               month: Optional[int] = None) -> Dict:
        """
        تولید گزارش ماهانه
        
        Args:
            year: سال شمسی
            month: ماه شمسی
            
        Returns:
            dict: گزارش ماهانه
        """
        try:
            if not year or not month:
                today = jdatetime.datetime.now()
                year = today.year
                month = today.month
            
            # تاریخ‌های شروع و پایان ماه
            start_date = f"{year}/{month:02d}/01"
            if month == 12:
                end_date = f"{year}/{month:02d}/29"  # اسفند
            else:
                end_date = f"{year}/{month:02d}/30"
            
            start_gregorian = self.data_manager.db.jalali_to_gregorian(start_date)
            end_gregorian = self.data_manager.db.jalali_to_gregorian(end_date)
            
            # نام ماه
            month_names = [
                'فروردین', 'اردیبهشت', 'خرداد', 'تیر', 'مرداد', 'شهریور',
                'مهر', 'آبان', 'آذر', 'دی', 'بهمن', 'اسفند'
            ]
            month_name = month_names[month - 1] if 1 <= month <= 12 else 'نامشخص'
            
            report = {
                'report_period': f"{month_name} {year}",
                'start_date': start_date,
                'end_date': end_date,
                'report_type': 'گزارش ماهانه',
                'generated_at': jdatetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S")
            }
            
            # 1. خلاصه مالی ماه
            financial_query = """
            SELECT 
                transaction_type,
                COUNT(*) as count,
                SUM(amount) as total_amount
            FROM AccountingTransactions
            WHERE DATE(transaction_date) BETWEEN ? AND ?
            GROUP BY transaction_type
            ORDER BY transaction_type
            """
            
            financial_result = self.data_manager.db.fetch_all(
                financial_query, 
                (start_gregorian, end_gregorian)
            )
            
            report['monthly_financial_summary'] = financial_result
            
            # 2. فاکتورهای ماه
            invoices_query = """
            SELECT 
                invoice_type,
                COUNT(*) as count,
                SUM(total) as total_amount,
                SUM(paid_amount) as total_paid,
                AVG(total) as average_amount
            FROM Invoices
            WHERE DATE(invoice_date) BETWEEN ? AND ?
            GROUP BY invoice_type
            ORDER BY invoice_type
            """
            
            invoices_result = self.data_manager.db.fetch_all(
                invoices_query, 
                (start_gregorian, end_gregorian)
            )
            
            report['monthly_invoices'] = invoices_result
            
            # 3. چک‌های ماه
            checks_query = """
            SELECT 
                check_type,
                status,
                COUNT(*) as count,
                SUM(amount) as total_amount
            FROM Checks
            WHERE DATE(issue_date) BETWEEN ? AND ?
            GROUP BY check_type, status
            ORDER BY check_type, status
            """
            
            checks_result = self.data_manager.db.fetch_all(
                checks_query, 
                (start_gregorian, end_gregorian)
            )
            
            report['monthly_checks'] = checks_result
            
            # 4. مقایسه با ماه قبل
            prev_month = month - 1 if month > 1 else 12
            prev_year = year if month > 1 else year - 1
            
            prev_start_date = f"{prev_year}/{prev_month:02d}/01"
            prev_end_date = f"{prev_year}/{prev_month:02d}/30"
            
            prev_start_gregorian = self.data_manager.db.jalali_to_gregorian(prev_start_date)
            prev_end_gregorian = self.data_manager.db.jalali_to_gregorian(prev_end_date)
            
            comparison_query = """
            SELECT 
                'ماه جاری' as period,
                SUM(CASE WHEN transaction_type IN ('دریافت', 'درآمد') THEN amount ELSE 0 END) as income,
                SUM(CASE WHEN transaction_type IN ('پرداخت', 'هزینه') THEN amount ELSE 0 END) as expense
            FROM AccountingTransactions
            WHERE DATE(transaction_date) BETWEEN ? AND ?
            UNION ALL
            SELECT 
                'ماه قبل' as period,
                SUM(CASE WHEN transaction_type IN ('دریافت', 'درآمد') THEN amount ELSE 0 END) as income,
                SUM(CASE WHEN transaction_type IN ('پرداخت', 'هزینه') THEN amount ELSE 0 END) as expense
            FROM AccountingTransactions
            WHERE DATE(transaction_date) BETWEEN ? AND ?
            """
            
            comparison_result = self.data_manager.db.fetch_all(
                comparison_query, 
                (start_gregorian, end_gregorian, prev_start_gregorian, prev_end_gregorian)
            )
            
            report['monthly_comparison'] = comparison_result
            
            # 5. تحلیل روند روزانه
            daily_trend_query = """
            SELECT 
                DATE(transaction_date) as day,
                SUM(CASE WHEN transaction_type IN ('دریافت', 'درآمد') THEN amount ELSE 0 END) as daily_income,
                SUM(CASE WHEN transaction_type IN ('پرداخت', 'هزینه') THEN amount ELSE 0 END) as daily_expense
            FROM AccountingTransactions
            WHERE DATE(transaction_date) BETWEEN ? AND ?
            GROUP BY DATE(transaction_date)
            ORDER BY day
            """
            
            daily_trend = self.data_manager.db.fetch_all(
                daily_trend_query, 
                (start_gregorian, end_gregorian)
            )
            
            report['daily_trend'] = daily_trend
            
            # 6. محاسبات پیشرفته
            total_income = sum(item['total_amount'] for item in financial_result 
                             if item['transaction_type'] in ['دریافت', 'درآمد'])
            total_expense = sum(item['total_amount'] for item in financial_result 
                              if item['transaction_type'] in ['پرداخت', 'هزینه'])
            
            report['advanced_analysis'] = {
                'total_income': total_income,
                'total_expense': total_expense,
                'net_profit': total_income - total_expense,
                'profit_margin': ((total_income - total_expense) / total_income * 100) 
                               if total_income > 0 else 0,
                'expense_ratio': (total_expense / total_income * 100) if total_income > 0 else 0,
                'average_daily_income': total_income / 30,
                'average_daily_expense': total_expense / 30
            }
            
            # 7. توصیه‌ها
            report['recommendations'] = self._generate_monthly_recommendations(
                total_income, total_expense, report['advanced_analysis']['profit_margin']
            )
            
            return report
            
        except Exception as e:
            print(f"❌ خطا در تولید گزارش ماهانه: {e}")
            return {'error': str(e)}
    
    def _generate_monthly_recommendations(self, income: float, expense: float, 
                                         profit_margin: float) -> List[str]:
        """تولید توصیه‌های ماهانه"""
        recommendations = []
        
        if profit_margin < 10:
            recommendations.append("حاشیه سود پایین است. هزینه‌ها را بررسی و بهینه‌سازی کنید.")
        
        if expense > income * 0.7:  # هزینه‌ها بیش از 70% درآمد
            recommendations.append("سهم هزینه‌ها از درآمد بالا است. کنترل هزینه‌ها ضروری است.")
        
        if income == 0:
            recommendations.append("درآمدی در این ماه ثبت نشده است. استراتژی فروش را بازبینی کنید.")
        
        if profit_margin > 30:
            recommendations.append("عملکرد عالی! می‌توانید بخشی از سود را سرمایه‌گذاری مجدد کنید.")
        
        if len(recommendations) == 0:
            recommendations.append("عملکرد مالی ماه در محدوده مطلوب است.")
        
        return recommendations
    
    # ==================== گزارش‌های تحلیلی ====================

    def generate_profit_loss_statement(self, start_date: str, end_date: str) -> Dict:
        """
        تولید صورت سود و زیان - نسخه اصلاح شده
        """
        try:
            start_gregorian = self.data_manager.db.jalali_to_gregorian(start_date)
            end_gregorian = self.data_manager.db.jalali_to_gregorian(end_date)
            
            report = {
                'report_type': 'صورت سود و زیان',
                'period': f"{start_date} تا {end_date}",
                'generated_at': jdatetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S")
            }
            
            # درآمدها - با کنترل مقادیر None
            revenue_query = """
            SELECT 
                'درآمد خدمات' as category,
                COALESCE(SUM(ii.total_price), 0) as amount
            FROM InvoiceItems ii
            JOIN Invoices i ON ii.invoice_id = i.id
            WHERE i.invoice_date BETWEEN ? AND ?
            AND ii.item_type = 'خدمات'
            
            UNION ALL
            
            SELECT 
                'فروش قطعات' as category,
                COALESCE(SUM(ii.total_price), 0) as amount
            FROM InvoiceItems ii
            JOIN Invoices i ON ii.invoice_id = i.id
            WHERE i.invoice_date BETWEEN ? AND ?
            AND ii.item_type = 'قطعه'
            
            UNION ALL
            
            SELECT 
                'سایر درآمدها' as category,
                COALESCE(SUM(at.amount), 0) as amount
            FROM AccountingTransactions at
            WHERE at.transaction_date BETWEEN ? AND ?
            AND at.transaction_type = 'درآمد'
            AND at.description NOT LIKE '%خدمات%'
            AND at.description NOT LIKE '%قطعات%'
            """
            
            revenue_result = self.data_manager.db.fetch_all(
                revenue_query, 
                (start_gregorian, end_gregorian, 
                start_gregorian, end_gregorian,
                start_gregorian, end_gregorian)
            )
            
            report['revenues'] = revenue_result
            total_revenue = sum(item.get('amount', 0) or 0 for item in revenue_result)
            
            # هزینه‌ها - با کنترل مقادیر None
            expense_query = """
            SELECT 
                'هزینه مواد و قطعات' as category,
                COALESCE(SUM(amount), 0) as amount
            FROM AccountingTransactions
            WHERE transaction_date BETWEEN ? AND ?
            AND transaction_type = 'هزینه'
            AND (description LIKE '%قطعه%' OR description LIKE '%لوازم%')
            
            UNION ALL
            
            SELECT 
                'هزینه حقوق و دستمزد' as category,
                COALESCE(SUM(amount), 0) as amount
            FROM AccountingTransactions
            WHERE transaction_date BETWEEN ? AND ?
            AND transaction_type = 'هزینه'
            AND (description LIKE '%حقوق%' OR description LIKE '%اجرت%')
            
            UNION ALL
            
            SELECT 
                'هزینه‌های اداری' as category,
                COALESCE(SUM(amount), 0) as amount
            FROM AccountingTransactions
            WHERE transaction_date BETWEEN ? AND ?
            AND transaction_type = 'هزینه'
            AND description LIKE '%اداری%'
            
            UNION ALL
            
            SELECT 
                'سایر هزینه‌ها' as category,
                COALESCE(SUM(amount), 0) as amount
            FROM AccountingTransactions
            WHERE transaction_date BETWEEN ? AND ?
            AND transaction_type = 'هزینه'
            AND description NOT LIKE '%قطعه%'
            AND description NOT LIKE '%حقوق%'
            AND description NOT LIKE '%اداری%'
            """
            
            expense_result = self.data_manager.db.fetch_all(
                expense_query, 
                (start_gregorian, end_gregorian,
                start_gregorian, end_gregorian,
                start_gregorian, end_gregorian,
                start_gregorian, end_gregorian)
            )
            
            report['expenses'] = expense_result
            total_expense = sum(item.get('amount', 0) or 0 for item in expense_result)
            
            # سود ناخالص و خالص - با کنترل مقادیر None
            material_costs = sum((item.get('amount', 0) or 0) for item in expense_result 
                            if item.get('category') == 'هزینه مواد و قطعات')
            gross_profit = total_revenue - material_costs
            
            net_profit = total_revenue - total_expense
            
            report['summary'] = {
                'total_revenue': total_revenue,
                'total_expense': total_expense,
                'gross_profit': gross_profit,
                'net_profit': net_profit,
                'gross_profit_margin': (gross_profit / total_revenue * 100) if total_revenue > 0 else 0,
                'net_profit_margin': (net_profit / total_revenue * 100) if total_revenue > 0 else 0
            }
            
            # تحلیل
            report['analysis'] = {
                'revenue_composition': [
                    {'category': item['category'], 
                    'percentage': ((item.get('amount', 0) or 0) / total_revenue * 100) if total_revenue > 0 else 0}
                    for item in revenue_result
                ],
                'expense_composition': [
                    {'category': item['category'], 
                    'percentage': ((item.get('amount', 0) or 0) / total_expense * 100) if total_expense > 0 else 0}
                    for item in expense_result
                ],
                'key_metrics': self.financial_calculator.calculate_financial_ratios(start_date, end_date)
            }
            
            return report
            
        except Exception as e:
            print(f"❌ خطا در تولید صورت سود و زیان: {e}")
            return {'error': str(e)}    
   
    def generate_cash_flow_statement(self, start_date: str, end_date: str) -> Dict:
        """
        تولید صورت جریان وجوه نقد
        
        Args:
            start_date: تاریخ شروع
            end_date: تاریخ پایان
            
        Returns:
            dict: صورت جریان وجوه نقد
        """
        try:
            start_gregorian = self.data_manager.db.jalali_to_gregorian(start_date)
            end_gregorian = self.data_manager.db.jalali_to_gregorian(end_date)
            
            report = {
                'report_type': 'صورت جریان وجوه نقد',
                'period': f"{start_date} تا {end_date}",
                'generated_at': jdatetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S")
            }
            
            # جریان نقدی حاصل از فعالیت‌های عملیاتی
            operating_query = """
            SELECT 
                'فعالیت‌های عملیاتی' as category,
                'دریافت از مشتریان' as subcategory,
                SUM(CASE 
                    WHEN transaction_type = 'دریافت' 
                    AND description LIKE '%مشتری%' 
                    THEN amount ELSE 0 
                END) as inflow,
                SUM(CASE 
                    WHEN transaction_type = 'پرداخت' 
                    AND description LIKE '%تامین کننده%' 
                    THEN amount ELSE 0 
                END) as outflow
            FROM AccountingTransactions
            WHERE transaction_date BETWEEN ? AND ?
            """
            
            operating_result = self.data_manager.db.fetch_one(
                operating_query, 
                (start_gregorian, end_gregorian)
            )
            
            # جریان نقدی حاصل از فعالیت‌های سرمایه‌گذاری
            investing_query = """
            SELECT 
                'فعالیت‌های سرمایه‌گذاری' as category,
                'خرید دارایی' as subcategory,
                0 as inflow,
                SUM(CASE 
                    WHEN transaction_type = 'پرداخت' 
                    AND description LIKE '%خرید دارایی%' 
                    THEN amount ELSE 0 
                END) as outflow
            FROM AccountingTransactions
            WHERE transaction_date BETWEEN ? AND ?
            """
            
            investing_result = self.data_manager.db.fetch_one(
                investing_query, 
                (start_gregorian, end_gregorian)
            )
            
            # جریان نقدی حاصل از فعالیت‌های تأمین مالی
            financing_query = """
            SELECT 
                'فعالیت‌های تأمین مالی' as category,
                'افزایش سرمایه' as subcategory,
                SUM(CASE 
                    WHEN transaction_type = 'دریافت' 
                    AND description LIKE '%سرمایه%' 
                    THEN amount ELSE 0 
                END) as inflow,
                SUM(CASE 
                    WHEN transaction_type = 'پرداخت' 
                    AND description LIKE '%سود%' 
                    THEN amount ELSE 0 
                END) as outflow
            FROM AccountingTransactions
            WHERE transaction_date BETWEEN ? AND ?
            """
            
            financing_result = self.data_manager.db.fetch_one(
                financing_query, 
                (start_gregorian, end_gregorian)
            )
            
            report['cash_flows'] = [
                operating_result,
                investing_result,
                financing_result
            ]
            
            # خلاصه
            total_inflow = sum(item['inflow'] for item in report['cash_flows'] if item)
            total_outflow = sum(item['outflow'] for item in report['cash_flows'] if item)
            net_cash_flow = total_inflow - total_outflow
            
            report['summary'] = {
                'total_cash_inflow': total_inflow,
                'total_cash_outflow': total_outflow,
                'net_cash_flow': net_cash_flow,
                'operating_cash_flow': operating_result['inflow'] - operating_result['outflow'] 
                                      if operating_result else 0,
                'cash_flow_adequacy_ratio': self._calculate_cash_flow_adequacy(
                    operating_result['inflow'] - operating_result['outflow'] if operating_result else 0,
                    total_outflow
                )
            }
            
            return report
            
        except Exception as e:
            print(f"❌ خطا در تولید صورت جریان وجوه نقد: {e}")
            return {'error': str(e)}
    
    def _calculate_cash_flow_adequacy(self, operating_cash_flow: float, 
                                     total_outflow: float) -> float:
        """محاسبه نسبت کفایت جریان نقدی"""
        return (operating_cash_flow / total_outflow * 100) if total_outflow > 0 else 0
    
    def generate_balance_sheet(self, as_of_date: str) -> Dict:
        """
        تولید ترازنامه
        
        Args:
            as_of_date: تاریخ ترازنامه
            
        Returns:
            dict: ترازنامه
        """
        try:
            as_of_gregorian = self.data_manager.db.jalali_to_gregorian(as_of_date)
            
            report = {
                'report_type': 'ترازنامه',
                'as_of_date': as_of_date,
                'generated_at': jdatetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S")
            }
            
            # دارایی‌ها
            assets_query = """
            SELECT 
                'دارایی‌های جاری' as category,
                'موجودی نقد' as subcategory,
                SUM(current_balance) as amount
            FROM Accounts
            WHERE account_type IN ('نقدی', 'صندوق', 'جاری')
            AND is_active = 1
            
            UNION ALL
            
            SELECT 
                'دارایی‌های جاری' as category,
                'حساب‌های دریافتنی' as subcategory,
                SUM(remaining_amount) as amount
            FROM Invoices
            WHERE payment_status IN ('نسیه', 'چک')
            
            UNION ALL
            
            SELECT 
                'دارایی‌های ثابت' as category,
                'ماشین آلات و تجهیزات' as subcategory,
                0 as amount -- نیاز به جدول دارایی‌های ثابت دارد
            
            UNION ALL
            
            SELECT 
                'سایر دارایی‌ها' as category,
                'پیش پرداخت‌ها' as subcategory,
                SUM(amount) as amount
            FROM AccountingTransactions
            WHERE transaction_type = 'پرداخت'
            AND description LIKE '%پیش پرداخت%'
            """
            
            assets_result = self.data_manager.db.fetch_all(assets_query)
            report['assets'] = assets_result
            total_assets = sum(item.get('amount', 0) or 0 for item in assets_result)
            
            # بدهی‌ها
            liabilities_query = """
            SELECT 
                'بدهی‌های جاری' as category,
                'حساب‌های پرداختنی' as subcategory,
                SUM(amount) as amount
            FROM Checks
            WHERE check_type = 'پرداختی'
            AND status IN ('وصول نشده', 'پاس نشده')
            
            UNION ALL
            
            SELECT 
                'بدهی‌های جاری' as category,
                'وام‌های کوتاه مدت' as subcategory,
                0 as amount -- نیاز به جدول وام‌ها دارد
            
            UNION ALL
            
            SELECT 
                'بدهی‌های بلندمدت' as category,
                'وام‌های بلندمدت' as subcategory,
                0 as amount -- نیاز به جدول وام‌ها دارد
            """
            
            liabilities_result = self.data_manager.db.fetch_all(liabilities_query)
            report['liabilities'] = liabilities_result
            total_liabilities = sum(item.get('amount', 0) or 0 for item in liabilities_result)
            
            # سرمایه
            equity_query = """
            SELECT 
                'سرمایه' as category,
                'سرمایه اولیه' as subcategory,
                SUM(capital) as amount
            FROM Partners
            WHERE active = 1
            
            UNION ALL
            
            SELECT 
                'سود انباشته' as category,
                'سود سال جاری' as subcategory,
                (
                    SELECT SUM(share_amount) 
                    FROM PartnerShares 
                    WHERE strftime('%Y', calculation_date) = strftime('%Y', ?)
                ) as amount
            """
            
            equity_result = self.data_manager.db.fetch_all(equity_query, (as_of_gregorian,))
            report['equity'] = equity_result
            total_equity = sum(item.get('amount', 0) or 0 for item in equity_result)
            
            # بررسی معادله حسابداری
            accounting_equation = total_assets - (total_liabilities + total_equity)
            
            report['summary'] = {
                'total_assets': total_assets,
                'total_liabilities': total_liabilities,
                'total_equity': total_equity,
                'accounting_equation_check': abs(accounting_equation) < 0.01,
                'equation_difference': accounting_equation
            }
            
            # نسبت‌های مالی
            report['financial_ratios'] = {
                'current_ratio': total_assets / total_liabilities if total_liabilities > 0 else 0,
                'debt_to_equity': total_liabilities / total_equity if total_equity > 0 else 0,
                'asset_turnover': 0  # نیاز به درآمد دارد
            }
            
            return report
            
        except Exception as e:
            print(f"❌ خطا در تولید ترازنامه: {e}")
            return {'error': str(e)}
    
    # ==================== گزارش‌های شرکا ====================
    
    def generate_partner_profit_report(self, start_date: str, end_date: str) -> Dict:
        """
        تولید گزارش سود شرکا
        
        Args:
            start_date: تاریخ شروع
            end_date: تاریخ پایان
            
        Returns:
            dict: گزارش سود شرکا
        """
        try:
            report = {
                'report_type': 'گزارش سود شرکا',
                'period': f"{start_date} تا {end_date}",
                'generated_at': jdatetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S")
            }
            
            # دریافت داده از PartnerManager
            if self.data_manager.partner_manager:
                profit_summary = self.data_manager.partner_manager.get_profit_summary()
                profit_trend = self.data_manager.partner_manager.get_profit_trend(6)  # 6 ماه اخیر
                
                report['profit_summary'] = profit_summary
                report['profit_trend'] = profit_trend
                
                # محاسبات اضافی
                total_profit = sum(item.get('total_profit_toman', 0) for item in profit_summary)
                avg_profit_per_partner = total_profit / len(profit_summary) if profit_summary else 0
                
                report['analysis'] = {
                    'total_profit_distributed': total_profit,
                    'average_profit_per_partner': avg_profit_per_partner,
                    'partner_count': len(profit_summary),
                    'highest_profit': max([p.get('total_profit_toman', 0) for p in profit_summary]) 
                                    if profit_summary else 0,
                    'lowest_profit': min([p.get('total_profit_toman', 0) for p in profit_summary]) 
                                   if profit_summary else 0
                }
            else:
                report['error'] = 'PartnerManager در دسترس نیست'
            
            return report
            
        except Exception as e:
            print(f"❌ خطا در تولید گزارش سود شرکا: {e}")
            return {'error': str(e)}
    
    def generate_partner_roi_report(self, partner_id: Optional[int] = None) -> Dict:
        """
        تولید گزارش بازده سرمایه (ROI) شرکا
        
        Args:
            partner_id: شناسه شریک (اگر None برای همه)
            
        Returns:
            dict: گزارش ROI
        """
        try:
            report = {
                'report_type': 'گزارش بازده سرمایه شرکا',
                'generated_at': jdatetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S")
            }
            
            if partner_id:
                # ROI برای یک شریک خاص
                roi_data = self.financial_calculator.calculate_partner_roi(
                    partner_id,
                    '1404/01/01',  # شروع سال
                    jdatetime.datetime.now().strftime("%Y/%m/%d")
                )
                
                if 'error' not in roi_data:
                    report['partner_roi'] = roi_data
                    report['assessment'] = self._assess_roi_performance(roi_data.get('roi_percentage', 0))
                else:
                    report['error'] = roi_data['error']
            else:
                # ROI برای همه شرکا
                partners_query = """
                SELECT p.id, per.first_name || ' ' || per.last_name as partner_name
                FROM Partners p
                JOIN Persons per ON p.person_id = per.id
                WHERE p.active = 1
                """
                
                partners = self.data_manager.db.fetch_all(partners_query)
                
                roi_list = []
                for partner in partners:
                    roi_data = self.financial_calculator.calculate_partner_roi(
                        partner['id'],
                        '1404/01/01',
                        jdatetime.datetime.now().strftime("%Y/%m/%d")
                    )
                    
                    if 'error' not in roi_data:
                        roi_list.append(roi_data)
                
                report['all_partners_roi'] = roi_list
                
                # تحلیل کلی
                if roi_list:
                    avg_roi = sum(item.get('roi_percentage', 0) for item in roi_list) / len(roi_list)
                    total_capital = sum(item.get('capital', 0) for item in roi_list)
                    total_profit = sum(item.get('total_profit', 0) for item in roi_list)
                    
                    report['summary'] = {
                        'average_roi': avg_roi,
                        'total_capital': total_capital,
                        'total_profit': total_profit,
                        'overall_roi': (total_profit / total_capital * 100) if total_capital > 0 else 0,
                        'best_performer': max(roi_list, key=lambda x: x.get('roi_percentage', 0)),
                        'worst_performer': min(roi_list, key=lambda x: x.get('roi_percentage', 0))
                    }
            
            return report
            
        except Exception as e:
            print(f"❌ خطا در تولید گزارش ROI: {e}")
            return {'error': str(e)}
    
    def _assess_roi_performance(self, roi: float) -> Dict:
        """ارزیابی عملکرد ROI"""
        if roi >= 50:
            return {'grade': 'A+', 'assessment': 'عالی', 'color': '#27ae60', 'recommendation': 'سرمایه‌گذاری ادامه دار'}
        elif roi >= 30:
            return {'grade': 'A', 'assessment': 'خیلی خوب', 'color': '#2ecc71', 'recommendation': 'حفظ سرمایه‌گذاری'}
        elif roi >= 20:
            return {'grade': 'B', 'assessment': 'خوب', 'color': '#3498db', 'recommendation': 'نظارت مستمر'}
        elif roi >= 10:
            return {'grade': 'C', 'assessment': 'متوسط', 'color': '#f39c12', 'recommendation': 'بررسی عملکرد'}
        elif roi >= 0:
            return {'grade': 'D', 'assessment': 'ضعیف', 'color': '#e74c3c', 'recommendation': 'بازنگری ضروری'}
        else:
            return {'grade': 'F', 'assessment': 'زیان‌ده', 'color': '#c0392b', 'recommendation': 'خروج فوری'}
    
    # ==================== خروجی‌های مختلف ====================
    
    def export_to_json(self, report_data: Dict, filename: str) -> bool:
        """
        ذخیره گزارش به فرمت JSON
        
        Args:
            report_data: داده‌های گزارش
            filename: نام فایل
            
        Returns:
            bool: موفقیت آمیز بودن
        """
        try:
            # افزودن .json اگر نبود
            if not filename.endswith('.json'):
                filename += '.json'
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(report_data, f, ensure_ascii=False, indent=2)
            
            print(f"✅ گزارش با موفقیت در {filename} ذخیره شد")
            return True
            
        except Exception as e:
            print(f"❌ خطا در ذخیره JSON: {e}")
            return False
    
    def export_to_pdf(self, report_data: Dict, filename: str) -> bool:
        """
        ذخیره گزارش به فرمت PDF
        
        Args:
            report_data: داده‌های گزارش
            filename: نام فایل
            
        Returns:
            bool: موفقیت آمیز بودن
        """
        if not REPORTLAB_AVAILABLE:
            print("❌ reportlab نصب نیست - قادر به تولید PDF نیستیم")
            return False
        
        try:
            # افزودن .pdf اگر نبود
            if not filename.endswith('.pdf'):
                filename += '.pdf'
            
            # تنظیمات اولیه PDF
            doc = SimpleDocTemplate(
                filename,
                pagesize=landscape(A4),
                rightMargin=30,
                leftMargin=30,
                topMargin=30,
                bottomMargin=30
            )
            
            elements = []
            
            # استایل‌ها
            styles = getSampleStyleSheet()
            
            # عنوان اصلی
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Title'],
                fontSize=18,
                textColor=colors.darkblue,
                alignment=1  # center
            )
            
            # اضافه کردن تایتل
            report_type = report_data.get('report_type', 'گزارش مالی')
            period = report_data.get('period', '')
            
            title_text = f"{report_type}"
            if period:
                title_text += f" - {period}"
            
            elements.append(Paragraph(title_text, title_style))
            elements.append(Spacer(1, 20))
            
            # تاریخ تولید
            generated_at = report_data.get('generated_at', '')
            date_text = f"تاریخ تولید: {generated_at}"
            elements.append(Paragraph(date_text, styles['Normal']))
            elements.append(Spacer(1, 30))
            
            # تولید جداول بر اساس نوع گزارش
            if report_type == 'گزارش روزانه':
                self._add_daily_report_to_pdf(elements, report_data, styles)
            elif report_type == 'گزارش ماهانه':
                self._add_monthly_report_to_pdf(elements, report_data, styles)
            elif report_type == 'صورت سود و زیان':
                self._add_profit_loss_to_pdf(elements, report_data, styles)
            elif report_type == 'صورت جریان وجوه نقد':
                self._add_cash_flow_to_pdf(elements, report_data, styles)
            elif report_type == 'ترازنامه':
                self._add_balance_sheet_to_pdf(elements, report_data, styles)
            
            # ساخت PDF
            doc.build(elements)
            
            print(f"✅ گزارش PDF با موفقیت در {filename} ذخیره شد")
            return True
            
        except Exception as e:
            print(f"❌ خطا در تولید PDF: {e}")
            return False
    
    def _add_daily_report_to_pdf(self, elements, report_data, styles):
        """اضافه کردن گزارش روزانه به PDF"""
        # خلاصه مالی
        if 'financial_summary' in report_data:
            summary = report_data['financial_summary']
            data = [
                ['شرح', 'مبلغ (ریال)'],
                ['کل درآمد', f"{summary.get('total_income', 0):,.0f}"],
                ['کل هزینه', f"{summary.get('total_expense', 0):,.0f}"],
                ['جریان نقدی خالص', f"{summary.get('net_cash_flow', 0):,.0f}"],
                ['کل فاکتورها', f"{summary.get('total_invoices', 0):,.0f}"],
                ['مانده کل حساب‌ها', f"{summary.get('accounts_total_balance', 0):,.0f}"]
            ]
            
            table = Table(data, colWidths=[200, 150])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            elements.append(Paragraph("خلاصه مالی روز", styles['Heading2']))
            elements.append(table)
            elements.append(Spacer(1, 20))
    
    def _add_monthly_report_to_pdf(self, elements, report_data, styles):
        """اضافه کردن گزارش ماهانه به PDF"""
        # تحلیل ماهانه
        if 'advanced_analysis' in report_data:
            analysis = report_data['advanced_analysis']
            data = [
                ['شاخص', 'مقدار'],
                ['کل درآمد ماه', f"{analysis.get('total_income', 0):,.0f} ریال"],
                ['کل هزینه ماه', f"{analysis.get('total_expense', 0):,.0f} ریال"],
                ['سود خالص', f"{analysis.get('net_profit', 0):,.0f} ریال"],
                ['حاشیه سود', f"{analysis.get('profit_margin', 0):.1f}%"],
                ['نسبت هزینه', f"{analysis.get('expense_ratio', 0):.1f}%"],
                ['میانگین درآمد روزانه', f"{analysis.get('average_daily_income', 0):,.0f} ریال"],
                ['میانگین هزینه روزانه', f"{analysis.get('average_daily_expense', 0):,.0f} ریال"]
            ]
            
            table = Table(data, colWidths=[200, 150])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.lightblue),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            elements.append(Paragraph("تحلیل ماهانه", styles['Heading2']))
            elements.append(table)
            elements.append(Spacer(1, 20))
    
    def _add_profit_loss_to_pdf(self, elements, report_data, styles):
        """اضافه کردن صورت سود و زیان به PDF"""
        # خلاصه سود و زیان
        if 'summary' in report_data:
            summary = report_data['summary']
            data = [
                ['آیتم', 'مبلغ (ریال)'],
                ['کل درآمد', f"{summary.get('total_revenue', 0):,.0f}"],
                ['کل هزینه', f"{summary.get('total_expense', 0):,.0f}"],
                ['سود ناخالص', f"{summary.get('gross_profit', 0):,.0f}"],
                ['سود خالص', f"{summary.get('net_profit', 0):,.0f}"],
                ['حاشیه سود ناخالص', f"{summary.get('gross_profit_margin', 0):.1f}%"],
                ['حاشیه سود خالص', f"{summary.get('net_profit_margin', 0):.1f}%"]
            ]
            
            table = Table(data, colWidths=[200, 150])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.darkgreen),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, 3), colors.lightgreen),  # درآمد
                ('BACKGROUND', (0, 4), (-1, 4), colors.orange),  # سود خالص
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            elements.append(Paragraph("خلاصه سود و زیان", styles['Heading2']))
            elements.append(table)
            elements.append(Spacer(1, 20))
    
    def _add_cash_flow_to_pdf(self, elements, report_data, styles):
        """اضافه کردن صورت جریان وجوه نقد به PDF"""
        # خلاصه جریان نقدی
        if 'summary' in report_data:
            summary = report_data['summary']
            data = [
                ['آیتم', 'مبلغ (ریال)'],
                ['کل ورود نقدی', f"{summary.get('total_cash_inflow', 0):,.0f}"],
                ['کل خروج نقدی', f"{summary.get('total_cash_outflow', 0):,.0f}"],
                ['جریان نقدی خالص', f"{summary.get('net_cash_flow', 0):,.0f}"],
                ['جریان نقدی عملیاتی', f"{summary.get('operating_cash_flow', 0):,.0f}"],
                ['نسبت کفایت نقدی', f"{summary.get('cash_flow_adequacy_ratio', 0):.1f}%"]
            ]
            
            table = Table(data, colWidths=[200, 150])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, 1), colors.lightblue),  # ورود
                ('BACKGROUND', (0, 2), (-1, 2), colors.pink),  # خروج
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            elements.append(Paragraph("خلاصه جریان وجوه نقد", styles['Heading2']))
            elements.append(table)
            elements.append(Spacer(1, 20))
    
    def _add_balance_sheet_to_pdf(self, elements, report_data, styles):
        """اضافه کردن ترازنامه به PDF"""
        # معادله حسابداری
        if 'summary' in report_data:
            summary = report_data['summary']
            data = [
                ['دارایی‌ها', f"{summary.get('total_assets', 0):,.0f} ریال"],
                ['بدهی‌ها', f"{summary.get('total_liabilities', 0):,.0f} ریال"],
                ['سرمایه', f"{summary.get('total_equity', 0):,.0f} ریال"],
                ['بررسی معادله', 'صحیح' if summary.get('accounting_equation_check') else 'ناصحیح'],
                ['اختلاف', f"{summary.get('equation_difference', 0):,.0f} ریال"]
            ]
            
            table = Table(data, colWidths=[200, 150])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.purple),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (0, 1), colors.lightgrey),  # دارایی
                ('BACKGROUND', (0, 2), (0, 2), colors.orange),  # بدهی
                ('BACKGROUND', (0, 3), (0, 3), colors.lightgreen),  # سرمایه
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            elements.append(Paragraph("ترازنامه - معادله حسابداری", styles['Heading2']))
            elements.append(table)
            elements.append(Spacer(1, 20))
    
    def generate_report(self, report_type: str, **kwargs) -> Dict:
        """
        تولید گزارش بر اساس نوع
        
        Args:
            report_type: نوع گزارش
            **kwargs: پارامترهای اضافی
            
        Returns:
            dict: گزارش
        """
        report_map = {
            'daily': self.generate_daily_report,
            'monthly': self.generate_monthly_report,
            'profit_loss': self.generate_profit_loss_statement,
            'cash_flow': self.generate_cash_flow_statement,
            'balance_sheet': self.generate_balance_sheet,
            'partner_profit': self.generate_partner_profit_report,
            'partner_roi': self.generate_partner_roi_report
        }
        
        if report_type in report_map:
            return report_map[report_type](**kwargs)
        else:
            return {'error': f'نوع گزارش نامعتبر: {report_type}'}
    
    def export_report(self, report_data: Dict, format: str = 'json', 
                     filename: str = 'report') -> bool:
        """
        خروجی گرفتن از گزارش
        
        Args:
            report_data: داده‌های گزارش
            format: فرمت خروجی (json/pdf)
            filename: نام فایل
            
        Returns:
            bool: موفقیت آمیز بودن
        """
        if format.lower() == 'json':
            return self.export_to_json(report_data, filename)
        elif format.lower() == 'pdf':
            return self.export_to_pdf(report_data, filename)
        else:
            print(f"❌ فرمت نامعتبر: {format}")
            return False