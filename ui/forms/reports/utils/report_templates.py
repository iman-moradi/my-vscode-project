# ui/forms/reports/utils/report_templates.py
"""
قالب‌های HTML برای چاپ گزارش‌ها
"""

from datetime import datetime
import jdatetime


class ReportTemplate:
    """کلاس پایه برای قالب گزارش"""
    
    def __init__(self, data_manager):
        self.data_manager = data_manager
    
    def generate(self, data, *args, **kwargs):
        """تولید HTML گزارش"""
        raise NotImplementedError("این متد باید در کلاس فرزند پیاده‌سازی شود")
    
    def _get_header(self, title, subtitle=""):
        """ایجاد هدر HTML"""
        return f"""
        <!DOCTYPE html>
        <html dir="rtl" lang="fa">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{title}</title>
            <style>
                /* استایل‌های عمومی */
                * {{
                    margin: 0;
                    padding: 0;
                    box-sizing: border-box;
                }}
                
                body {{
                    font-family: 'B Nazanin', 'Tahoma', 'Arial', sans-serif;
                    line-height: 1.6;
                    color: #333;
                    background-color: #f9f9f9;
                    padding: 20px;
                }}
                
                .report-container {{
                    max-width: 210mm; /* A4 width */
                    margin: 0 auto;
                    background-color: white;
                    padding: 20mm;
                    box-shadow: 0 0 10px rgba(0,0,0,0.1);
                    min-height: 297mm; /* A4 height */
                }}
                
                .header {{
                    text-align: center;
                    margin-bottom: 30px;
                    border-bottom: 3px solid #3498db;
                    padding-bottom: 20px;
                }}
                
                .header h1 {{
                    color: #2c3e50;
                    font-size: 24pt;
                    margin-bottom: 10px;
                }}
                
                .header .subtitle {{
                    color: #7f8c8d;
                    font-size: 14pt;
                }}
                
                .company-info {{
                    text-align: center;
                    margin-bottom: 20px;
                    color: #555;
                    font-size: 11pt;
                }}
                
                .report-info {{
                    display: flex;
                    justify-content: space-between;
                    margin-bottom: 30px;
                    padding: 15px;
                    background-color: #ecf0f1;
                    border-radius: 5px;
                    font-size: 10pt;
                }}
                
                .section {{
                    margin-bottom: 30px;
                    page-break-inside: avoid;
                }}
                
                .section-title {{
                    background-color: #3498db;
                    color: white;
                    padding: 10px 15px;
                    border-radius: 5px;
                    margin-bottom: 15px;
                    font-size: 14pt;
                }}
                
                table {{
                    width: 100%;
                    border-collapse: collapse;
                    margin-bottom: 20px;
                    font-size: 10pt;
                }}
                
                th {{
                    background-color: #2c3e50;
                    color: white;
                    padding: 12px 8px;
                    text-align: center;
                    border: 1px solid #ddd;
                    font-weight: bold;
                }}
                
                td {{
                    padding: 10px 8px;
                    text-align: center;
                    border: 1px solid #ddd;
                }}
                
                tr:nth-child(even) {{
                    background-color: #f8f9fa;
                }}
                
                .stats-grid {{
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                    gap: 15px;
                    margin-bottom: 20px;
                }}
                
                .stat-card {{
                    background-color: #f8f9fa;
                    border-radius: 8px;
                    padding: 15px;
                    text-align: center;
                    border-left: 4px solid #3498db;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                }}
                
                .stat-value {{
                    font-size: 18pt;
                    font-weight: bold;
                    color: #2c3e50;
                    margin: 10px 0;
                }}
                
                .stat-label {{
                    color: #7f8c8d;
                    font-size: 10pt;
                }}
                
                .footer {{
                    text-align: center;
                    margin-top: 40px;
                    padding-top: 20px;
                    border-top: 1px solid #ddd;
                    color: #7f8c8d;
                    font-size: 9pt;
                }}
                
                .page-break {{
                    page-break-before: always;
                }}
                
                @media print {{
                    body {{
                        background-color: white;
                        padding: 0;
                    }}
                    
                    .report-container {{
                        box-shadow: none;
                        padding: 15mm;
                    }}
                    
                    .no-print {{
                        display: none;
                    }}
                }}
            </style>
        </head>
        <body>
            <div class="report-container">
                <div class="header">
                    <h1>{title}</h1>
                    <div class="subtitle">{subtitle}</div>
                </div>
        """
    
    def _get_footer(self):
        """ایجاد فوتر HTML"""
        now = jdatetime.datetime.now()
        jalali_date = now.strftime('%Y/%m/%d')
        jalali_time = now.strftime('%H:%M')
        
        return f"""
                <div class="footer">
                    <p>این گزارش به صورت خودکار توسط سیستم مدیریت تعمیرگاه تولید شده است.</p>
                    <p>تاریخ تولید: {jalali_date} - ساعت: {jalali_time}</p>
                    <p class="no-print">برای چاپ، از گزینه چاپ مرورگر (Ctrl+P) استفاده کنید.</p>
                </div>
            </div>
        </body>
        </html>
        """
    
    def _format_currency(self, amount):
        """فرمت کردن مبلغ به صورت جداکننده هزارگان"""
        return f"{amount:,.0f}".replace(",", "٬")
    
    def _convert_to_toman(self, amount_rial):
        """تبدیل ریال به تومان"""
        return amount_rial / 10 if amount_rial else 0


class FinancialReportTemplate(ReportTemplate):
    """قالب گزارش مالی"""
    
    def generate(self, financial_data, start_date, end_date):
        """تولید HTML گزارش مالی"""
        html = self._get_header(
            "گزارش مالی تعمیرگاه",
            f"از تاریخ {start_date} تا {end_date}"
        )
        
        # بخش خلاصه مالی
        if 'summary' in financial_data:
            summary = financial_data['summary']
            html += self._generate_summary_section(summary)
        
        # بخش تراکنش‌ها
        if 'transactions' in financial_data:
            html += self._generate_transactions_section(financial_data['transactions'])
        
        # بخش حساب‌ها
        if 'accounts' in financial_data:
            html += self._generate_accounts_section(financial_data['accounts'])
        
        html += self._get_footer()
        return html
    
    def _generate_summary_section(self, summary):
        """ایجاد بخش خلاصه مالی"""
        html = """
        <div class="section">
            <div class="section-title">📊 خلاصه مالی</div>
            <div class="stats-grid">
        """
        
        stats = [
            ("💰 درآمد کل", f"{self._format_currency(self._convert_to_toman(summary.get('total_income', 0)))} تومان", "#2ecc71"),
            ("📉 هزینه کل", f"{self._format_currency(self._convert_to_toman(summary.get('total_expense', 0)))} تومان", "#e74c3c"),
            ("📊 سود خالص", f"{self._format_currency(self._convert_to_toman(summary.get('net_profit', 0)))} تومان", "#3498db"),
            ("📈 تعداد تراکنش‌ها", self._format_currency(summary.get('total_transactions', 0)), "#9b59b6"),
            ("💼 تعداد فاکتورها", self._format_currency(summary.get('total_invoices', 0)), "#f39c12"),
            ("💵 میانگین درآمد روزانه", f"{self._format_currency(self._convert_to_toman(summary.get('avg_daily_income', 0)))} تومان", "#1abc9c")
        ]
        
        for label, value, color in stats:
            html += f"""
                <div class="stat-card" style="border-left-color: {color};">
                    <div class="stat-label">{label}</div>
                    <div class="stat-value">{value}</div>
                </div>
            """
        
        html += """
            </div>
        </div>
        """
        
        return html
    
    def _generate_transactions_section(self, transactions):
        """ایجاد بخش تراکنش‌ها"""
        if not transactions:
            return ""
        
        html = """
        <div class="section">
            <div class="section-title">💳 تراکنش‌های مالی</div>
            <table>
                <thead>
                    <tr>
                        <th>تاریخ</th>
                        <th>نوع تراکنش</th>
                        <th>حساب مبدا</th>
                        <th>حساب مقصد</th>
                        <th>مبلغ</th>
                        <th>شرح</th>
                    </tr>
                </thead>
                <tbody>
        """
        
        for trans in transactions[:50]:  # فقط ۵۰ تراکنش اول
            amount_toman = self._convert_to_toman(trans.get('amount', 0))
            html += f"""
                    <tr>
                        <td>{trans.get('transaction_date', '')}</td>
                        <td>{trans.get('transaction_type', '')}</td>
                        <td>{trans.get('from_account', '')}</td>
                        <td>{trans.get('to_account', '')}</td>
                        <td>{self._format_currency(amount_toman)} تومان</td>
                        <td>{trans.get('description', '')}</td>
                    </tr>
            """
        
        html += """
                </tbody>
            </table>
        </div>
        """
        
        return html
    
    def _generate_accounts_section(self, accounts):
        """ایجاد بخش حساب‌ها"""
        if not accounts:
            return ""
        
        html = """
        <div class="section">
            <div class="section-title">🏦 وضعیت حساب‌ها</div>
            <table>
                <thead>
                    <tr>
                        <th>شماره حساب</th>
                        <th>نام حساب</th>
                        <th>نوع حساب</th>
                        <th>نام بانک</th>
                        <th>موجودی</th>
                    </tr>
                </thead>
                <tbody>
        """
        
        total_balance = 0
        
        for account in accounts:
            balance_toman = self._convert_to_toman(account.get('current_balance', 0))
            total_balance += balance_toman
            
            html += f"""
                    <tr>
                        <td>{account.get('account_number', '')}</td>
                        <td>{account.get('account_name', '')}</td>
                        <td>{account.get('account_type', '')}</td>
                        <td>{account.get('bank_name', '')}</td>
                        <td>{self._format_currency(balance_toman)} تومان</td>
                    </tr>
            """
        
        html += f"""
                </tbody>
                <tfoot>
                    <tr style="background-color: #2c3e50; color: white; font-weight: bold;">
                        <td colspan="4">مجموع موجودی کلی</td>
                        <td>{self._format_currency(total_balance)} تومان</td>
                    </tr>
                </tfoot>
            </table>
        </div>
        """
        
        return html


class SalesReportTemplate(ReportTemplate):
    """قالب گزارش فروش"""
    
    def generate(self, sales_data, start_date, end_date):
        """تولید HTML گزارش فروش"""
        html = self._get_header(
            "گزارش فروش تعمیرگاه",
            f"از تاریخ {start_date} تا {end_date}"
        )
        
        # بخش خلاصه فروش
        if 'general_stats' in sales_data:
            html += self._generate_sales_summary(sales_data['general_stats'])
        
        # بخش محصولات پرفروش
        if 'top_products' in sales_data and sales_data['top_products']:
            html += self._generate_top_products(sales_data['top_products'])
        
        # بخش مشتریان برتر
        if 'top_customers' in sales_data and sales_data['top_customers']:
            html += self._generate_top_customers(sales_data['top_customers'])
        
        html += self._get_footer()
        return html
    
    def _generate_sales_summary(self, stats):
        """ایجاد بخش خلاصه فروش"""
        html = """
        <div class="section">
            <div class="section-title">📊 خلاصه فروش</div>
            <div class="stats-grid">
        """
        
        summary_stats = [
            ("💰 فروش کل", f"{self._format_currency(self._convert_to_toman(stats.get('total_sales', 0)))} تومان", "#2ecc71"),
            ("📋 تعداد فاکتورها", self._format_currency(stats.get('total_invoices', 0)), "#3498db"),
            ("👥 مشتریان منحصربفرد", self._format_currency(stats.get('unique_customers', 0)), "#9b59b6"),
            ("📊 میانگین فاکتور", f"{self._format_currency(self._convert_to_toman(stats.get('avg_invoice_amount', 0)))} تومان", "#f39c12"),
            ("💵 فروش نقدی", f"{self._format_currency(self._convert_to_toman(stats.get('cash_sales', 0)))} تومان", "#27ae60"),
            ("📈 نرخ تکمیل پرداخت", f"{stats.get('payment_completion_rate', 0):.1f}%", "#1abc9c")
        ]
        
        for label, value, color in summary_stats:
            html += f"""
                <div class="stat-card" style="border-left-color: {color};">
                    <div class="stat-label">{label}</div>
                    <div class="stat-value">{value}</div>
                </div>
            """
        
        html += """
            </div>
        </div>
        """
        
        return html
    
    def _generate_top_products(self, products):
        """ایجاد بخش محصولات پرفروش"""
        html = """
        <div class="section">
            <div class="section-title">🏆 محصولات پرفروش</div>
            <table>
                <thead>
                    <tr>
                        <th>ردیف</th>
                        <th>نام محصول</th>
                        <th>دسته</th>
                        <th>برند</th>
                        <th>تعداد فروش</th>
                        <th>مبلغ فروش</th>
                        <th>سود تخمینی</th>
                    </tr>
                </thead>
                <tbody>
        """
        
        for i, product in enumerate(products[:15], 1):  # ۱۵ محصول برتر
            sales_amount = self._convert_to_toman(product.get('total_sales_amount', 0))
            profit = self._convert_to_toman(product.get('estimated_profit', 0))
            
            html += f"""
                    <tr>
                        <td>{i}</td>
                        <td>{product.get('product_name', '')}</td>
                        <td>{product.get('category', '')}</td>
                        <td>{product.get('brand', '')}</td>
                        <td>{self._format_currency(product.get('sale_count', 0))}</td>
                        <td>{self._format_currency(sales_amount)} تومان</td>
                        <td>{self._format_currency(profit)} تومان</td>
                    </tr>
            """
        
        html += """
                </tbody>
            </table>
        </div>
        """
        
        return html
    
    def _generate_top_customers(self, customers):
        """ایجاد بخش مشتریان برتر"""
        html = """
        <div class="page-break"></div>
        <div class="section">
            <div class="section-title">👑 مشتریان برتر</div>
            <table>
                <thead>
                    <tr>
                        <th>ردیف</th>
                        <th>نام مشتری</th>
                        <th>موبایل</th>
                        <th>تعداد خرید</th>
                        <th>مبلغ خرید</th>
                        <th>نوع مشتری</th>
                        <th>امتیاز وفاداری</th>
                    </tr>
                </thead>
                <tbody>
        """
        
        for i, customer in enumerate(customers[:12], 1):  # ۱۲ مشتری برتر
            purchases = self._convert_to_toman(customer.get('total_purchases', 0))
            
            html += f"""
                    <tr>
                        <td>{i}</td>
                        <td>{customer.get('customer_name', '')}</td>
                        <td>{customer.get('mobile', '')}</td>
                        <td>{self._format_currency(customer.get('invoice_count', 0))}</td>
                        <td>{self._format_currency(purchases)} تومان</td>
                        <td>{customer.get('customer_type', '')}</td>
                        <td>{customer.get('loyalty_score', 0):.0f}</td>
                    </tr>
            """
        
        html += """
                </tbody>
            </table>
        </div>
        """
        
        return html


class InventoryReportTemplate(ReportTemplate):
    """قالب گزارش انبار"""
    
    def generate(self, inventory_data, warehouse_type):
        """تولید HTML گزارش انبار"""
        html = self._get_header(
            f"گزارش انبار {warehouse_type}",
            f"وضعیت موجودی به تاریخ {jdatetime.datetime.now().strftime('%Y/%m/%d')}"
        )
        
        # بخش خلاصه موجودی
        if 'summary' in inventory_data:
            html += self._generate_inventory_summary(inventory_data['summary'], warehouse_type)
        
        # بخش لیست موجودی
        if 'items' in inventory_data and inventory_data['items']:
            html += self._generate_inventory_items(inventory_data['items'], warehouse_type)
        
        # بخش هشدارهای موجودی کم
        if 'low_stock_items' in inventory_data and inventory_data['low_stock_items']:
            html += self._generate_low_stock_warnings(inventory_data['low_stock_items'])
        
        html += self._get_footer()
        return html
    
    def _generate_inventory_summary(self, summary, warehouse_type):
        """ایجاد بخش خلاصه موجودی"""
        html = f"""
        <div class="section">
            <div class="section-title">📦 خلاصه موجودی {warehouse_type}</div>
            <div class="stats-grid">
        """
        
        summary_stats = [
            ("📊 تعداد آیتم‌ها", self._format_currency(summary.get('total_items', 0)), "#3498db"),
            ("💰 ارزش کل موجودی", f"{self._format_currency(self._convert_to_toman(summary.get('total_value', 0)))} تومان", "#2ecc71"),
            ("⚠️ آیتم‌های با موجودی کم", self._format_currency(summary.get('low_stock_count', 0)), "#e74c3c"),
            ("📈 میانگین موجودی", self._format_currency(summary.get('avg_quantity', 0)), "#f39c12"),
            ("🔧 تعداد برندها", self._format_currency(summary.get('total_brands', 0)), "#9b59b6"),
            ("🏪 تعداد دسته‌ها", self._format_currency(summary.get('total_categories', 0)), "#1abc9c")
        ]
        
        for label, value, color in summary_stats:
            html += f"""
                <div class="stat-card" style="border-left-color: {color};">
                    <div class="stat-label">{label}</div>
                    <div class="stat-value">{value}</div>
                </div>
            """
        
        html += """
            </div>
        </div>
        """
        
        return html
    
    def _generate_inventory_items(self, items, warehouse_type):
        """ایجاد بخش لیست موجودی"""
        if warehouse_type == 'قطعات نو':
            return self._generate_new_parts_table(items)
        elif warehouse_type == 'لوازم نو':
            return self._generate_new_appliances_table(items)
        elif warehouse_type == 'قطعات دست دوم':
            return self._generate_used_parts_table(items)
        elif warehouse_type == 'لوازم دست دوم':
            return self._generate_used_appliances_table(items)
        else:
            return ""
    
    def _generate_new_parts_table(self, items):
        """ایجاد جدول قطعات نو"""
        html = """
        <div class="section">
            <div class="section-title">🔩 لیست قطعات نو</div>
            <table>
                <thead>
                    <tr>
                        <th>کد قطعه</th>
                        <th>نام قطعه</th>
                        <th>دسته</th>
                        <th>برند</th>
                        <th>موجودی</th>
                        <th>حداقل</th>
                        <th>حداکثر</th>
                        <th>وضعیت</th>
                    </tr>
                </thead>
                <tbody>
        """
        
        for item in items[:50]:
            stock_status = "✅ مناسب"
            if item.get('quantity', 0) < item.get('min_stock', 0):
                stock_status = "⚠️ کم"
            elif item.get('quantity', 0) > item.get('max_stock', 0):
                stock_status = "📦 زیاد"
            
            html += f"""
                    <tr>
                        <td>{item.get('part_code', '')}</td>
                        <td>{item.get('part_name', '')}</td>
                        <td>{item.get('category', '')}</td>
                        <td>{item.get('brand', '')}</td>
                        <td>{self._format_currency(item.get('quantity', 0))}</td>
                        <td>{self._format_currency(item.get('min_stock', 0))}</td>
                        <td>{self._format_currency(item.get('max_stock', 0))}</td>
                        <td>{stock_status}</td>
                    </tr>
            """
        
        html += """
                </tbody>
            </table>
        </div>
        """
        
        return html
    
    def _generate_low_stock_warnings(self, low_stock_items):
        """ایجاد بخش هشدارهای موجودی کم"""
        if not low_stock_items:
            return ""
        
        html = """
        <div class="section" style="border: 2px solid #e74c3c; border-radius: 8px;">
            <div class="section-title" style="background-color: #e74c3c;">⚠️ هشدار: موجودی کم</div>
            <table>
                <thead>
                    <tr>
                        <th>نام آیتم</th>
                        <th>موجودی فعلی</th>
                        <th>حداقل مجاز</th>
                        <th>کمبود</th>
                        <th>اولویت</th>
                    </tr>
                </thead>
                <tbody>
        """
        
        for item in low_stock_items:
            current = item.get('current_stock', 0)
            min_stock = item.get('min_stock', 0)
            shortage = min_stock - current
            
            priority = "کم"
            if shortage > 10:
                priority = "بالا"
            elif shortage > 5:
                priority = "متوسط"
            
            html += f"""
                    <tr>
                        <td>{item.get('item_name', '')}</td>
                        <td>{self._format_currency(current)}</td>
                        <td>{self._format_currency(min_stock)}</td>
                        <td>{self._format_currency(shortage)}</td>
                        <td>{priority}</td>
                    </tr>
            """
        
        html += """
                </tbody>
            </table>
        </div>
        """
        
        return html