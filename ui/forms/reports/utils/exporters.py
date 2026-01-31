# ui/forms/reports/utils/exporters.py
"""
ماژول خروجی اکسل برای گزارش‌ها
"""

import pandas as pd
from PySide6.QtWidgets import QFileDialog, QMessageBox
from PySide6.QtCore import QDate
import os


class ExcelExporter:
    """کلاس خروجی اکسل برای گزارش‌های مختلف"""
    
    def __init__(self, data_manager):
        self.data_manager = data_manager
    
    def export_financial_report(self, financial_data, start_date, end_date):
        """صدور گزارش مالی به اکسل"""
        try:
            # انتخاب مسیر ذخیره‌سازی
            file_path, _ = QFileDialog.getSaveFileName(
                None,
                "ذخیره گزارش مالی به صورت Excel",
                f"گزارش_مالی_{start_date}_تا_{end_date}.xlsx",
                "Excel Files (*.xlsx);;All Files (*)"
            )
            
            if not file_path:
                return False, "عملیات ذخیره‌سازی لغو شد"
            
            # ایجاد writer برای Excel
            with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
                # 1. خلاصه مالی
                self._export_financial_summary(writer, financial_data)
                
                # 2. تراکنش‌ها
                self._export_transactions(writer, start_date, end_date)
                
                # 3. حساب‌ها
                self._export_accounts(writer)
                
                # 4. فاکتورها
                self._export_invoices(writer, start_date, end_date)
            
            return True, f"گزارش با موفقیت در {file_path} ذخیره شد"
            
        except Exception as e:
            return False, f"خطا در صدور خروجی: {str(e)}"
    
    def _export_financial_summary(self, writer, financial_data):
        """صدور برگه خلاصه مالی"""
        summary_data = []
        
        # کارت‌های آماری
        if 'summary' in financial_data:
            summary = financial_data['summary']
            summary_data.append(['💰 درآمد کل', f"{summary.get('total_income', 0):,.0f} تومان"])
            summary_data.append(['📉 هزینه کل', f"{summary.get('total_expense', 0):,.0f} تومان"])
            summary_data.append(['📊 سود خالص', f"{summary.get('net_profit', 0):,.0f} تومان"])
            summary_data.append(['📈 تعداد تراکنش‌ها', summary.get('total_transactions', 0)])
            summary_data.append(['💼 تعداد فاکتورها', summary.get('total_invoices', 0)])
            summary_data.append(['💵 میانگین درآمد روزانه', f"{summary.get('avg_daily_income', 0):,.0f} تومان"])
        
        # درآمد بر اساس دسته
        if 'income_by_category' in financial_data:
            for category, amount in financial_data['income_by_category'].items():
                summary_data.append([f"درآمد {category}", f"{amount:,.0f} تومان"])
        
        # هزینه بر اساس دسته
        if 'expense_by_category' in financial_data:
            for category, amount in financial_data['expense_by_category'].items():
                summary_data.append([f"هزینه {category}", f"{amount:,.0f} تومان"])
        
        df = pd.DataFrame(summary_data, columns=['عنوان', 'مقدار'])
        df.to_excel(writer, sheet_name='خلاصه مالی', index=False)
        
        # فرمت‌دهی ستون‌ها
        worksheet = writer.sheets['خلاصه مالی']
        worksheet.column_dimensions['A'].width = 30
        worksheet.column_dimensions['B'].width = 25
    
    def _export_transactions(self, writer, start_date, end_date):
        """صدور برگه تراکنش‌ها"""
        try:
            # دریافت تراکنش‌ها از دیتابیس
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
            """
            
            transactions = self.data_manager.db.fetch_all(query, (start_date, end_date))
            
            if transactions:
                # تبدیل به DataFrame
                df = pd.DataFrame(transactions)
                
                # تبدیل مبلغ به تومان و افزودن واحد
                df['amount'] = df['amount'].apply(lambda x: f"{x/10:,.0f} تومان")
                
                # تغییر نام ستون‌ها به فارسی
                df.rename(columns={
                    'transaction_date': 'تاریخ',
                    'transaction_type': 'نوع تراکنش',
                    'from_account': 'حساب مبدا',
                    'to_account': 'حساب مقصد',
                    'amount': 'مبلغ',
                    'description': 'شرح'
                }, inplace=True)
                
                df.to_excel(writer, sheet_name='تراکنش‌ها', index=False)
                
                # فرمت‌دهی
                worksheet = writer.sheets['تراکنش‌ها']
                for col in ['A', 'B', 'C', 'D', 'E', 'F']:
                    worksheet.column_dimensions[col].width = 20
                
                return len(transactions)
            return 0
            
        except Exception as e:
            print(f"خطا در صدور تراکنش‌ها: {e}")
            return 0
    
    def _export_accounts(self, writer):
        """صدور برگه حساب‌ها"""
        try:
            # دریافت حساب‌ها
            query = """
            SELECT 
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
            
            if accounts:
                df = pd.DataFrame(accounts)
                
                # تبدیل موجودی به تومان
                df['current_balance'] = df['current_balance'].apply(lambda x: f"{x/10:,.0f} تومان")
                
                # تغییر نام ستون‌ها
                df.rename(columns={
                    'account_number': 'شماره حساب',
                    'account_name': 'نام حساب',
                    'account_type': 'نوع حساب',
                    'bank_name': 'نام بانک',
                    'current_balance': 'موجودی فعلی',
                    'owner_name': 'صاحب حساب'
                }, inplace=True)
                
                df.to_excel(writer, sheet_name='حساب‌ها', index=False)
                
                # فرمت‌دهی
                worksheet = writer.sheets['حساب‌ها']
                for col in ['A', 'B', 'C', 'D', 'E', 'F']:
                    worksheet.column_dimensions[col].width = 20
                
                return len(accounts)
            return 0
            
        except Exception as e:
            print(f"خطا در صدور حساب‌ها: {e}")
            return 0
    
    def _export_invoices(self, writer, start_date, end_date):
        """صدور برگه فاکتورها"""
        try:
            query = """
            SELECT 
                i.invoice_number,
                i.invoice_date,
                i.invoice_type,
                p.full_name as customer_name,
                i.total,
                i.paid_amount,
                i.payment_status,
                i.description
            FROM Invoices i
            LEFT JOIN Persons p ON i.customer_id = p.id
            WHERE DATE(i.invoice_date) BETWEEN ? AND ?
            ORDER BY i.invoice_date DESC
            """
            
            invoices = self.data_manager.db.fetch_all(query, (start_date, end_date))
            
            if invoices:
                df = pd.DataFrame(invoices)
                
                # تبدیل مبالغ به تومان
                df['total'] = df['total'].apply(lambda x: f"{x/10:,.0f} تومان")
                df['paid_amount'] = df['paid_amount'].apply(lambda x: f"{x/10:,.0f} تومان")
                
                # تغییر نام ستون‌ها
                df.rename(columns={
                    'invoice_number': 'شماره فاکتور',
                    'invoice_date': 'تاریخ',
                    'invoice_type': 'نوع فاکتور',
                    'customer_name': 'مشتری',
                    'total': 'مبلغ کل',
                    'paid_amount': 'مبلغ پرداخت شده',
                    'payment_status': 'وضعیت پرداخت',
                    'description': 'شرح'
                }, inplace=True)
                
                df.to_excel(writer, sheet_name='فاکتورها', index=False)
                
                # فرمت‌دهی
                worksheet = writer.sheets['فاکتورها']
                for col in ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']:
                    worksheet.column_dimensions[col].width = 18
                
                return len(invoices)
            return 0
            
        except Exception as e:
            print(f"خطا در صدور فاکتورها: {e}")
            return 0
    
    def export_sales_report(self, sales_data, start_date, end_date):
        """صدور گزارش فروش به اکسل"""
        try:
            file_path, _ = QFileDialog.getSaveFileName(
                None,
                "ذخیره گزارش فروش به صورت Excel",
                f"گزارش_فروش_{start_date}_تا_{end_date}.xlsx",
                "Excel Files (*.xlsx);;All Files (*)"
            )
            
            if not file_path:
                return False, "عملیات ذخیره‌سازی لغو شد"
            
            with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
                # 1. خلاصه فروش
                self._export_sales_summary(writer, sales_data)
                
                # 2. محصولات پرفروش
                self._export_top_products(writer, sales_data)
                
                # 3. مشتریان برتر
                self._export_top_customers(writer, sales_data)
                
                # 4. روند فروش
                self._export_sales_trends(writer, sales_data)
            
            return True, f"گزارش فروش در {file_path} ذخیره شد"
            
        except Exception as e:
            return False, f"خطا در صدور گزارش فروش: {str(e)}"
    
    def _export_sales_summary(self, writer, sales_data):
        """صدور خلاصه فروش"""
        summary_data = []
        
        if 'general_stats' in sales_data:
            stats = sales_data['general_stats']
            
            summary_data.append(['📊 کل فروش', f"{stats.get('total_sales', 0)/10:,.0f} تومان"])
            summary_data.append(['📋 تعداد فاکتورها', stats.get('total_invoices', 0)])
            summary_data.append(['👥 مشتریان منحصربفرد', stats.get('unique_customers', 0)])
            summary_data.append(['💰 میانگین فاکتور', f"{stats.get('avg_invoice_amount', 0)/10:,.0f} تومان"])
            summary_data.append(['💵 فروش نقدی', f"{stats.get('cash_sales', 0)/10:,.0f} تومان"])
            summary_data.append(['🏦 فروش چک', f"{stats.get('check_sales', 0)/10:,.0f} تومان"])
            summary_data.append(['💳 فروش کارت', f"{stats.get('card_sales', 0)/10:,.0f} تومان"])
            summary_data.append(['📅 فروش نسیه', f"{stats.get('credit_sales', 0)/10:,.0f} تومان"])
            summary_data.append(['📈 نرخ تکمیل پرداخت', f"{stats.get('payment_completion_rate', 0):.1f}%"])
        
        df = pd.DataFrame(summary_data, columns=['آمار', 'مقدار'])
        df.to_excel(writer, sheet_name='خلاصه فروش', index=False)
        
        worksheet = writer.sheets['خلاصه فروش']
        worksheet.column_dimensions['A'].width = 25
        worksheet.column_dimensions['B'].width = 25
    
    def _export_top_products(self, writer, sales_data):
        """صدور محصولات پرفروش"""
        if 'top_products' in sales_data and sales_data['top_products']:
            products = sales_data['top_products']
            df = pd.DataFrame(products)
            
            # تغییر نام ستون‌ها
            df.rename(columns={
                'product_name': 'نام محصول',
                'category': 'دسته',
                'brand': 'برند',
                'sale_count': 'تعداد فروش',
                'total_sales_amount': 'مبلغ فروش',
                'estimated_profit': 'سود تخمینی'
            }, inplace=True)
            
            # تبدیل مبالغ به تومان
            df['مبلغ فروش'] = df['مبلغ فروش'].apply(lambda x: f"{x/10:,.0f} تومان")
            df['سود تخمینی'] = df['سود تخمینی'].apply(lambda x: f"{x/10:,.0f} تومان")
            
            df.to_excel(writer, sheet_name='محصولات پرفروش', index=False)
            
            worksheet = writer.sheets['محصولات پرفروش']
            for col in ['A', 'B', 'C', 'D', 'E', 'F']:
                worksheet.column_dimensions[col].width = 20
    
    def _export_top_customers(self, writer, sales_data):
        """صدور مشتریان برتر"""
        if 'top_customers' in sales_data and sales_data['top_customers']:
            customers = sales_data['top_customers']
            df = pd.DataFrame(customers)
            
            # تغییر نام ستون‌ها
            df.rename(columns={
                'customer_name': 'نام مشتری',
                'mobile': 'موبایل',
                'invoice_count': 'تعداد خرید',
                'total_purchases': 'مبلغ خرید',
                'customer_type': 'نوع مشتری',
                'loyalty_score': 'امتیاز وفاداری'
            }, inplace=True)
            
            # تبدیل مبالغ به تومان
            df['مبلغ خرید'] = df['مبلغ خرید'].apply(lambda x: f"{x/10:,.0f} تومان")
            
            df.to_excel(writer, sheet_name='مشتریان برتر', index=False)
            
            worksheet = writer.sheets['مشتریان برتر']
            for col in ['A', 'B', 'C', 'D', 'E', 'F']:
                worksheet.column_dimensions[col].width = 20
    
    def _export_sales_trends(self, writer, sales_data):
        """صدور روند فروش"""
        if 'trends_data' in sales_data and sales_data['trends_data']:
            trends = sales_data['trends_data']
            df = pd.DataFrame(trends)
            
            # تغییر نام ستون‌ها
            df.rename(columns={
                'period': 'دوره',
                'invoice_count': 'تعداد فاکتور',
                'total_sales': 'فروش کل',
                'unique_customers': 'مشتریان منحصربفرد',
                'avg_invoice_amount': 'میانگین فاکتور',
                'payment_completion_rate': 'نرخ تکمیل پرداخت'
            }, inplace=True)
            
            # تبدیل مبالغ به تومان
            df['فروش کل'] = df['فروش کل'].apply(lambda x: f"{x/10:,.0f} تومان")
            df['میانگین فاکتور'] = df['میانگین فاکتور'].apply(lambda x: f"{x/10:,.0f} تومان")
            
            df.to_excel(writer, sheet_name='روند فروش', index=False)
            
            worksheet = writer.sheets['روند فروش']
            for col in ['A', 'B', 'C', 'D', 'E', 'F']:
                worksheet.column_dimensions[col].width = 20



    def export_customer_report(self, customer_data, start_date, end_date):
        """صدور گزارش مشتریان به اکسل"""
        try:
            file_path, _ = QFileDialog.getSaveFileName(
                None,
                "ذخیره گزارش مشتریان به صورت Excel",
                f"گزارش_مشتریان_{start_date}_تا_{end_date}.xlsx",
                "Excel Files (*.xlsx);;All Files (*)"
            )
            
            if not file_path:
                return False, "عملیات ذخیره‌سازی لغو شد"
            
            with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
                # 1. خلاصه مشتریان
                self._export_customer_summary(writer, customer_data)
                
                # 2. لیست مشتریان
                self._export_customer_list(writer, customer_data)
                
                # 3. تحلیل وفاداری
                self._export_loyalty_analysis(writer, customer_data)
                
                # 4. تحلیل RFM
                self._export_rfm_analysis(writer, customer_data)
            
            return True, f"گزارش مشتریان در {file_path} ذخیره شد"
            
        except Exception as e:
            return False, f"خطا در صدور گزارش مشتریان: {str(e)}"
    
    def _export_customer_summary(self, writer, customer_data):
        """صدور خلاصه مشتریان"""
        summary_data = []
        
        summary_data.append(['👥 کل مشتریان', customer_data.get('total_customers', 0)])
        summary_data.append(['💰 مشتریان فعال', customer_data.get('active_customers', 0)])
        summary_data.append(['⭐ مشتریان VIP', customer_data.get('vip_customers', 0)])
        summary_data.append(['📅 مشتریان جدید', customer_data.get('new_customers', 0)])
        summary_data.append(['📊 میانگین خرید', f"{customer_data.get('avg_purchase', 0)/10:,.0f} تومان"])
        summary_data.append(['🏆 بیشترین خرید', f"{customer_data.get('max_purchase', 0)/10:,.0f} تومان"])
        summary_data.append(['📈 نرخ بازگشت', f"{self._calculate_return_rate(customer_data):.1f}%"])
        summary_data.append(['📉 مشتریان غیرفعال', 
            customer_data.get('total_customers', 0) - customer_data.get('active_customers', 0)])
        
        df = pd.DataFrame(summary_data, columns=['آمار', 'مقدار'])
        df.to_excel(writer, sheet_name='خلاصه مشتریان', index=False)
        
        worksheet = writer.sheets['خلاصه مشتریان']
        worksheet.column_dimensions['A'].width = 25
        worksheet.column_dimensions['B'].width = 25
    
    def _export_customer_list(self, writer, customer_data):
        """صدور لیست مشتریان"""
        if 'recent_customers' in customer_data and customer_data['recent_customers']:
            customers = customer_data['recent_customers']
            
            # تبدیل به لیست قابل نمایش
            customer_list = []
            for cust in customers:
                customer_list.append({
                    'نام': f"{cust.get('first_name', '')} {cust.get('last_name', '')}",
                    'موبایل': cust.get('mobile', ''),
                    'تاریخ ثبت': cust.get('registration_date', ''),
                    'تعداد خرید': cust.get('invoice_count', 0),
                    'مجموع خرید': f"{cust.get('total_purchases', 0)/10:,.0f} تومان",
                    'آخرین خرید': cust.get('last_purchase_date', '')
                })
            
            if customer_list:
                df = pd.DataFrame(customer_list)
                df.to_excel(writer, sheet_name='لیست مشتریان', index=False)
                
                worksheet = writer.sheets['لیست مشتریان']
                for col in ['A', 'B', 'C', 'D', 'E', 'F']:
                    worksheet.column_dimensions[col].width = 20
    
    def _export_loyalty_analysis(self, writer, customer_data):
        """صدور تحلیل وفاداری"""
        # این بخش می‌تواند پیچیده باشد - فعلاً نمونه ساده
        loyalty_data = [
            ['مشتریان وفادار (بیش از ۵ خرید)', self._count_loyal_customers(customer_data)],
            ['مشتریان معمولی (۲-۵ خرید)', self._count_regular_customers(customer_data)],
            ['مشتریان جدید (۱ خرید)', self._count_new_customers(customer_data)],
            ['مشتریان یک‌باره (فقط ۱ خرید)', self._count_one_time_customers(customer_data)]
        ]
        
        df = pd.DataFrame(loyalty_data, columns=['سطح وفاداری', 'تعداد'])
        df.to_excel(writer, sheet_name='تحلیل وفاداری', index=False)
        
        worksheet = writer.sheets['تحلیل وفاداری']
        worksheet.column_dimensions['A'].width = 30
        worksheet.column_dimensions['B'].width = 15
    
    def _export_rfm_analysis(self, writer, customer_data):
        """صدور تحلیل RFM"""
        rfm_data = [
            ['Champions (اخیراً، اغلب، زیاد)', 0],
            ['Loyal Customers (اغلب، زیاد)', 0],
            ['Potential Loyalists (اخیراً، زیاد)', 0],
            ['Recent Customers (اخیراً)', 0],
            ['Promising (اخیراً، متوسط)', 0],
            ['Customers Needing Attention (متوسط)', 0],
            ['About To Sleep (نه اخیراً، متوسط)', 0],
            ['At Risk (زیاد، نه اخیراً)', 0],
            ['Can’t Lose Them (زیاد، نه اخیراً، اغلب)', 0],
            ['Hibernating (نه اخیراً، کم)', 0],
            ['Lost (نه اخیراً، کم، کم)', 0]
        ]
        
        df = pd.DataFrame(rfm_data, columns=['دسته RFM', 'تعداد'])
        df.to_excel(writer, sheet_name='تحلیل RFM', index=False)
        
        worksheet = writer.sheets['تحلیل RFM']
        worksheet.column_dimensions['A'].width = 40
        worksheet.column_dimensions['B'].width = 15
    
    def _calculate_return_rate(self, customer_data):
        """محاسبه نرخ بازگشت مشتریان"""
        total_customers = customer_data.get('total_customers', 0)
        active_customers = customer_data.get('active_customers', 0)
        
        if total_customers > 0:
            return (active_customers / total_customers) * 100
        return 0
    
    def _count_loyal_customers(self, customer_data):
        """شمارش مشتریان وفادار"""
        customers = customer_data.get('recent_customers', [])
        return sum(1 for c in customers if c.get('invoice_count', 0) > 5)
    
    def _count_regular_customers(self, customer_data):
        """شمارش مشتریان معمولی"""
        customers = customer_data.get('recent_customers', [])
        return sum(1 for c in customers if 2 <= c.get('invoice_count', 0) <= 5)
    
    def _count_new_customers(self, customer_data):
        """شمارش مشتریان جدید"""
        customers = customer_data.get('recent_customers', [])
        return sum(1 for c in customers if c.get('invoice_count', 0) == 1)
    
    def _count_one_time_customers(self, customer_data):
        """شمارش مشتریان یک‌باره"""
        customers = customer_data.get('recent_customers', [])
        return sum(1 for c in customers if c.get('invoice_count', 0) == 1)












