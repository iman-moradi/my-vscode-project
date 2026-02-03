# ui/forms/reports/forms/monthly_report_form.py
"""
فرم گزارش ماهانه کامل
"""

from PySide6.QtWidgets import *
from PySide6.QtCore import Qt, Signal, QDate, QTimer
from PySide6.QtGui import QFont, QColor, QPainter
from utils.jalali_date_widget import get_current_jalali, gregorian_to_jalali
from PySide6.QtCharts import QChart, QChartView, QLineSeries, QBarSeries, QBarSet, QPieSeries, QPieSlice
from PySide6.QtCharts import QValueAxis, QBarCategoryAxis
import jdatetime


class MonthlyReportForm(QWidget):
    """فرم گزارش ماهانه"""
    
    report_updated = Signal(dict)
    
    def __init__(self, data_manager):
        super().__init__()
        self.data_manager = data_manager
        self.monthly_data = {}
        
        self.setup_ui()
        self.load_monthly_data()
    
    def setup_ui(self):
        """تنظیم رابط کاربری"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)
        
        # نوار ابزار
        self.create_toolbar(main_layout)
        
        # فیلترها
        self.create_filters(main_layout)
        
        # ویجت تب‌ها
        self.create_tab_widget(main_layout)
        
        # نوار وضعیت
        self.create_status_bar(main_layout)
    
    def create_toolbar(self, parent_layout):
        """ایجاد نوار ابزار"""
        toolbar_frame = QFrame()
        toolbar_frame.setStyleSheet("""
            QFrame {
                background-color: #1a1a2e;
                border-radius: 6px;
                padding: 8px;
            }
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 8px 15px;
                border-radius: 4px;
                font-weight: bold;
                font-family: 'B Nazanin';
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        
        layout = QHBoxLayout(toolbar_frame)
        
        # دکمه‌ها
        btn_refresh = QPushButton("🔄 بروزرسانی")
        btn_refresh.clicked.connect(self.load_monthly_data)
        
        btn_export = QPushButton("📊 خروجی Excel")
        btn_export.clicked.connect(self.export_to_excel)
        
        btn_print = QPushButton("🖨️ چاپ")
        btn_print.clicked.connect(self.print_report)
        
        layout.addWidget(btn_refresh)
        layout.addWidget(btn_export)
        layout.addWidget(btn_print)
        layout.addStretch()
        
        parent_layout.addWidget(toolbar_frame)
    
    def create_filters(self, parent_layout):
        """ایجاد فیلترها"""
        filter_frame = QFrame()
        filter_frame.setStyleSheet("""
            QFrame {
                background-color: #2c3e50;
                border-radius: 6px;
                padding: 10px;
            }
            QLabel {
                color: #ecf0f1;
                font-weight: bold;
            }
            QComboBox, QDateEdit {
                background-color: #34495e;
                color: white;
                border: 1px solid #4a6278;
                border-radius: 4px;
                padding: 5px;
                font-family: 'B Nazanin';
            }
        """)
        
        layout = QGridLayout(filter_frame)
        
        # انتخاب ماه
        layout.addWidget(QLabel("ماه:"), 0, 0)
        self.month_combo = QComboBox()
        
        # تولید لیست ماه‌های اخیر
        current_date = QDate.currentDate()
        for i in range(12):  # ۱۲ ماه اخیر
            month_date = current_date.addMonths(-i)
            month_name = self.get_month_name(month_date.month())
            year = month_date.year()
            self.month_combo.addItem(f"{month_name} {year}")
        
        layout.addWidget(self.month_combo, 0, 1)
        
        # نوع گزارش
        layout.addWidget(QLabel("نوع گزارش:"), 0, 2)
        self.report_type_combo = QComboBox()
        self.report_type_combo.addItems([
            "کلی",
            "مالی",
            "فروش",
            "تعمیرات",
            "انبار",
            "مشتریان"
        ])
        layout.addWidget(self.report_type_combo, 0, 3)
        
        # دکمه اعمال فیلتر
        btn_apply = QPushButton("✅ اعمال فیلتر")
        btn_apply.clicked.connect(self.apply_filters)
        layout.addWidget(btn_apply, 0, 4)
        
        # دکمه بازنشانی
        btn_reset = QPushButton("🔄 بازنشانی")
        btn_reset.clicked.connect(self.reset_filters)
        layout.addWidget(btn_reset, 0, 5)
        
        parent_layout.addWidget(filter_frame)
    
    def get_month_name(self, month_number):
        """دریافت نام ماه"""
        months = {
            1: "فروردین",
            2: "اردیبهشت",
            3: "خرداد",
            4: "تیر",
            5: "مرداد",
            6: "شهریور",
            7: "مهر",
            8: "آبان",
            9: "آذر",
            10: "دی",
            11: "بهمن",
            12: "اسفند"
        }
        return months.get(month_number, "")
    
    def create_tab_widget(self, parent_layout):
        """ایجاد ویجت تب‌ها"""
        self.tab_widget = QTabWidget()
        
        # استایل تب‌ها
        self.tab_widget.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #444;
                background-color: #111;
                border-radius: 5px;
            }
            QTabBar::tab {
                background-color: #2c3e50;
                color: white;
                padding: 10px 20px;
                margin-right: 2px;
                border-top-left-radius: 5px;
                border-top-right-radius: 5px;
                font-weight: bold;
            }
            QTabBar::tab:selected {
                background-color: #9b59b6;
                color: white;
            }
            QTabBar::tab:hover:!selected {
                background-color: #34495e;
            }
        """)
        
        # ایجاد تب‌ها
        self.create_summary_tab()
        self.create_financial_tab()
        self.create_analysis_tab()
        self.create_comparison_tab()
        
        parent_layout.addWidget(self.tab_widget, 1)
    
    def create_summary_tab(self):
        """ایجاد تب خلاصه ماه"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # هدر
        header_label = QLabel("📊 خلاصه عملکرد ماه")
        header_label.setStyleSheet("""
            QLabel {
                color: #9b59b6;
                font-size: 16pt;
                font-weight: bold;
                padding: 10px;
                background-color: #1a1a2e;
                border-radius: 8px;
                text-align: center;
            }
        """)
        header_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(header_label)
        
        # کارت‌های آمار
        self.create_summary_cards(layout)
        
        # نمودارهای کلی
        self.create_summary_charts(layout)
        
        # جدول آمار روزانه
        self.create_daily_stats_table(layout)
        
        self.tab_widget.addTab(tab, "📊 خلاصه")
    
    def create_summary_cards(self, parent_layout):
        """ایجاد کارت‌های آمار خلاصه"""
        cards_frame = QFrame()
        cards_layout = QGridLayout(cards_frame)
        cards_layout.setSpacing(15)
        
        # کارت‌های مختلف
        stats = [
            ("📋 کل فعالیت‌ها", "۰", "#3498db"),
            ("💰 درآمد ماه", "۰ تومان", "#2ecc71"),
            ("📉 هزینه ماه", "۰ تومان", "#e74c3c"),
            ("📊 سود ماه", "۰ تومان", "#f39c12"),
            ("🔧 تعمیرات تکمیل شده", "۰", "#1abc9c"),
            ("🛒 فاکتورهای صادر شده", "۰", "#e74c3c"),
            ("👥 مشتریان جدید", "۰", "#27ae60"),
            ("📦 اقلام اضافه شده", "۰", "#e67e22"),
            ("📈 میانگین درآمد روزانه", "۰ تومان", "#9b59b6"),
            ("📉 میانگین هزینه روزانه", "۰ تومان", "#d35400"),
            ("🏆 بهترین روز", "۰ تومان", "#f1c40f"),
            ("📊 نرخ رشد ماهانه", "۰٪", "#16a085")
        ]
        
        for i, (title, value, color) in enumerate(stats):
            row = i // 4
            col = i % 4
            card = self.create_stat_card(title, value, color)
            cards_layout.addWidget(card, row, col)
        
        parent_layout.addWidget(cards_frame)
    
    def create_stat_card(self, title, value, color):
        """ایجاد یک کارت آمار"""
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background-color: {color}20;
                border: 2px solid {color};
                border-radius: 10px;
                padding: 15px;
            }}
        """)
        
        layout = QVBoxLayout(card)
        
        # عنوان
        title_label = QLabel(title)
        title_label.setStyleSheet(f"""
            QLabel {{
                color: {color};
                font-size: 11pt;
                font-weight: bold;
                text-align: center;
            }}
        """)
        layout.addWidget(title_label)
        
        # مقدار
        value_label = QLabel(value)
        value_label.setStyleSheet("""
            QLabel {
                color: #ffffff;
                font-size: 14pt;
                font-weight: bold;
                text-align: center;
                padding: 8px 0;
            }
        """)
        layout.addWidget(value_label)
        
        return card
    
    def create_summary_charts(self, parent_layout):
        """ایجاد نمودارهای خلاصه"""
        charts_frame = QFrame()
        charts_layout = QHBoxLayout(charts_frame)
        
        # نمودار دایره‌ای درآمد
        pie_group = QGroupBox("📊 توزیع درآمد")
        pie_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #2ecc71;
                border-radius: 8px;
                padding-top: 15px;
                color: #2ecc71;
                font-size: 12pt;
            }
        """)
        
        pie_layout = QVBoxLayout(pie_group)
        self.income_pie_chart = QChartView()
        self.income_pie_chart.setRenderHint(QPainter.Antialiasing)
        self.income_pie_chart.setMinimumHeight(250)
        pie_layout.addWidget(self.income_pie_chart)
        
        # نمودار میله‌ای هزینه
        bar_group = QGroupBox("📉 توزیع هزینه")
        bar_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #e74c3c;
                border-radius: 8px;
                padding-top: 15px;
                color: #e74c3c;
                font-size: 12pt;
            }
        """)
        
        bar_layout = QVBoxLayout(bar_group)
        self.expense_bar_chart = QChartView()
        self.expense_bar_chart.setRenderHint(QPainter.Antialiasing)
        self.expense_bar_chart.setMinimumHeight(250)
        bar_layout.addWidget(self.expense_bar_chart)
        
        charts_layout.addWidget(pie_group, 1)
        charts_layout.addWidget(bar_group, 1)
        
        parent_layout.addWidget(charts_frame)
    
    def create_daily_stats_table(self, parent_layout):
        """ایجاد جدول آمار روزانه"""
        group = QGroupBox("📋 آمار روزانه ماه")
        group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #3498db;
                border-radius: 8px;
                margin-top: 15px;
                padding-top: 15px;
                color: #3498db;
                font-size: 12pt;
            }
        """)
        
        layout = QVBoxLayout(group)
        
        # جدول
        self.daily_stats_table = QTableWidget(31, 7)
        
        # تنظیمات
        for i in range(31):
            self.daily_stats_table.setRowHeight(i, 30)
        
        self.daily_stats_table.setStyleSheet("""
            QTableWidget {
                background-color: #111111;
                alternate-background-color: #0a0a0a;
                gridline-color: #333333;
                color: #ffffff;
                font-size: 9pt;
                font-family: 'B Nazanin';
            }
            QTableWidget::item {
                padding: 5px;
            }
            QTableWidget::item:selected {
                background-color: #3498db;
                color: white;
            }
            QHeaderView::section {
                background-color: #2c3e50;
                color: white;
                padding: 8px;
                border: none;
                font-weight: bold;
                font-size: 10pt;
                font-family: 'B Nazanin';
            }
        """)
        
        # هدرها
        headers = ["روز", "تاریخ", "فعالیت‌ها", "درآمد", "هزینه", "سود", "کارایی"]
        self.daily_stats_table.setHorizontalHeaderLabels(headers)
        
        # تنظیم ستون‌ها
        header = self.daily_stats_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(6, QHeaderView.ResizeToContents)
        
        layout.addWidget(self.daily_stats_table)
        parent_layout.addWidget(group)
    
    def create_financial_tab(self):
        """ایجاد تب مالی"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # هدر
        header_label = QLabel("💰 تحلیل مالی ماهانه")
        header_label.setStyleSheet("""
            QLabel {
                color: #2ecc71;
                font-size: 16pt;
                font-weight: bold;
                padding: 10px;
                background-color: #1a1a2e;
                border-radius: 8px;
                text-align: center;
            }
        """)
        header_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(header_label)
        
        # محتوای تب مالی
        label = QLabel("تحلیل مالی دقیق ماه - به زودی...")
        label.setAlignment(Qt.AlignCenter)
        label.setStyleSheet("""
            QLabel {
                color: #7f8c8d;
                font-size: 14pt;
                padding: 100px;
            }
        """)
        
        layout.addWidget(label)
        self.tab_widget.addTab(tab, "💰 مالی")
    
    def create_analysis_tab(self):
        """ایجاد تب تحلیل"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # محتوای تب تحلیل
        label = QLabel("📈 تحلیل عمیق ماهانه - به زودی...")
        label.setAlignment(Qt.AlignCenter)
        label.setStyleSheet("""
            QLabel {
                color: #7f8c8d;
                font-size: 14pt;
                padding: 100px;
            }
        """)
        
        layout.addWidget(label)
        self.tab_widget.addTab(tab, "📈 تحلیل")
    
    def create_comparison_tab(self):
        """ایجاد تب مقایسه"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # محتوای تب مقایسه
        label = QLabel("📊 مقایسه با ماه‌های قبل - به زودی...")
        label.setAlignment(Qt.AlignCenter)
        label.setStyleSheet("""
            QLabel {
                color: #7f8c8d;
                font-size: 14pt;
                padding: 100px;
            }
        """)
        
        layout.addWidget(label)
        self.tab_widget.addTab(tab, "📊 مقایسه")
    
    def create_status_bar(self, parent_layout):
        """ایجاد نوار وضعیت"""
        status_frame = QFrame()
        status_frame.setStyleSheet("""
            QFrame {
                background-color: #2c3e50;
                border-radius: 3px;
                padding: 5px;
            }
            QLabel {
                color: #ecf0f1;
                font-size: 9pt;
            }
        """)
        
        layout = QHBoxLayout(status_frame)
        
        self.status_label = QLabel("✅ سیستم گزارش ماهانه آماده است")
        self.month_info_label = QLabel("ماه جاری: --")
        self.last_update_label = QLabel("آخرین بروزرسانی: --:--")
        
        layout.addWidget(self.status_label, 5)
        layout.addWidget(self.month_info_label, 3)
        layout.addWidget(self.last_update_label, 3)
        
        parent_layout.addWidget(status_frame)
    
    def load_monthly_data(self):
        """بارگذاری داده‌های ماهانه"""
        try:
            self.status_label.setText("📊 در حال دریافت داده‌های ماهانه...")
            
            # دریافت تاریخ‌های ماه
            month_start, month_end = self.get_current_month_dates()
            
            # دریافت داده‌ها از دیتابیس
            self.load_data_from_database(month_start, month_end)
            
            # به‌روزرسانی UI
            self.update_summary_tab()
            
            self.status_label.setText("✅ داده‌های ماهانه بارگذاری شد")
            self.month_info_label.setText(f"ماه: {month_start} تا {month_end}")
            self.last_update_label.setText(f"آخرین بروزرسانی: {get_current_jalali()}")
            
        except Exception as e:
            self.status_label.setText(f"❌ خطا در بارگذاری داده‌ها: {str(e)}")
            print(f"خطا در load_monthly_data: {e}")
            self.load_sample_monthly_data()
    
    def get_current_month_dates(self):
        """دریافت تاریخ شروع و پایان ماه جاری"""
        current_date = QDate.currentDate()
        
        # اول ماه
        month_start = QDate(current_date.year(), current_date.month(), 1)
        
        # آخر ماه
        month_end = QDate(current_date.year(), current_date.month(), current_date.daysInMonth())
        
        return (
            month_start.toString("yyyy-MM-dd"),
            month_end.toString("yyyy-MM-dd")
        )
    
    def load_data_from_database(self, start_date, end_date):
        """بارگذاری داده‌ها از دیتابیس"""
        try:
            # آمار کلی ماه
            query = """
            SELECT 
                COUNT(r.id) as total_activities,
                SUM(CASE WHEN r.status = 'تعمیر شده' THEN 1 ELSE 0 END) as completed_repairs,
                SUM(CASE WHEN r.status = 'تحویل داده شده' THEN 1 ELSE 0 END) as delivered,
                COUNT(DISTINCT r.customer_id) as unique_customers
            FROM Receptions r
            WHERE r.reception_date BETWEEN ? AND ?
            """
            
            activities_result = self.data_manager.db.fetch_one(query, (start_date, end_date))
            
            # آمار مالی ماه
            query = """
            SELECT 
                SUM(CASE WHEN transaction_type = 'دریافت' THEN amount ELSE 0 END) as total_income,
                SUM(CASE WHEN transaction_type = 'پرداخت' THEN amount ELSE 0 END) as total_expense,
                COUNT(*) as total_transactions
            FROM AccountingTransactions
            WHERE transaction_date BETWEEN ? AND ?
            """
            
            financial_result = self.data_manager.db.fetch_one(query, (start_date, end_date))
            
            # آمار فروش ماه
            query = """
            SELECT 
                COUNT(*) as total_invoices,
                SUM(total) as total_sales,
                AVG(total) as avg_invoice_amount
            FROM Invoices
            WHERE invoice_date BETWEEN ? AND ?
            AND invoice_type IN ('فروش', 'خدمات')
            """
            
            sales_result = self.data_manager.db.fetch_one(query, (start_date, end_date))
            
            # پردازش داده‌ها
            self.monthly_data = {
                'summary': {
                    'total_activities': activities_result.get('total_activities', 0) if activities_result else 0,
                    'completed_repairs': activities_result.get('completed_repairs', 0) if activities_result else 0,
                    'unique_customers': activities_result.get('unique_customers', 0) if activities_result else 0,
                    'total_income': financial_result.get('total_income', 0) if financial_result else 0,
                    'total_expense': financial_result.get('total_expense', 0) if financial_result else 0,
                    'net_profit': (financial_result.get('total_income', 0) - financial_result.get('total_expense', 0)) 
                        if financial_result else 0,
                    'total_invoices': sales_result.get('total_invoices', 0) if sales_result else 0,
                    'total_sales': sales_result.get('total_sales', 0) if sales_result else 0,
                    'avg_invoice_amount': sales_result.get('avg_invoice_amount', 0) if sales_result else 0
                },
                'daily_data': self.load_daily_data(start_date, end_date),
                'income_by_category': self.load_income_by_category(start_date, end_date),
                'expense_by_category': self.load_expense_by_category(start_date, end_date)
            }
            
            # محاسبات اضافی
            days_in_month = QDate.fromString(end_date, "yyyy-MM-dd").day()
            self.monthly_data['summary']['avg_daily_income'] = self.monthly_data['summary']['total_income'] / days_in_month
            self.monthly_data['summary']['avg_daily_expense'] = self.monthly_data['summary']['total_expense'] / days_in_month
            
        except Exception as e:
            print(f"❌ خطا در بارگذاری داده‌های ماهانه: {e}")
            raise
    
    def load_daily_data(self, start_date, end_date):
        """بارگذاری داده‌های روزانه ماه"""
        daily_data = []
        
        # تبدیل رشته تاریخ به QDate
        from PySide6.QtCore import QDate
        
        start_qdate = QDate.fromString(start_date, "yyyy-MM-dd")
        end_qdate = QDate.fromString(end_date, "yyyy-MM-dd")
        
        current_date = start_qdate
        day_count = 1
        
        while current_date <= end_qdate:
            date_str = current_date.toString("yyyy-MM-dd")
            day_of_week = current_date.dayOfWeek()
            day_name = self.get_day_name(day_of_week)
            
            # دریافت آمار روز
            query = """
            SELECT 
                COUNT(r.id) as activities,
                SUM(CASE WHEN at.transaction_type = 'دریافت' THEN at.amount ELSE 0 END) as income,
                SUM(CASE WHEN at.transaction_type = 'پرداخت' THEN at.amount ELSE 0 END) as expense,
                COUNT(i.id) as invoices
            FROM Receptions r
            LEFT JOIN AccountingTransactions at ON DATE(at.transaction_date) = ?
            LEFT JOIN Invoices i ON DATE(i.invoice_date) = ?
            WHERE r.reception_date = ?
            """
            
            result = self.data_manager.db.fetch_one(query, (date_str, date_str, date_str))
            
            income = result.get('income', 0) if result else 0
            expense = result.get('expense', 0) if result else 0
            profit = income - expense
            
            # محاسبه کارایی (درصد سود)
            efficiency = (profit / income * 100) if income > 0 else 0
            
            daily_data.append({
                'day_number': day_count,
                'date': date_str,
                'day_name': day_name,
                'activities': result.get('activities', 0) if result else 0,
                'income': income,
                'expense': expense,
                'profit': profit,
                'invoices': result.get('invoices', 0) if result else 0,
                'efficiency': efficiency
            })
            
            current_date = current_date.addDays(1)
            day_count += 1
        
        return daily_data
    
    def get_day_name(self, day_of_week):
        """دریافت نام روز"""
        days = {
            1: "دوشنبه",
            2: "سه‌شنبه",
            3: "چهارشنبه",
            4: "پنجشنبه",
            5: "جمعه",
            6: "شنبه",
            7: "یکشنبه"
        }
        return days.get(day_of_week, "")
    
    def load_income_by_category(self, start_date, end_date):
        """بارگذاری درآمد بر اساس دسته"""
        try:
            query = """
            SELECT 
                it.description as category,
                SUM(it.amount) as amount
            FROM AccountingTransactions it
            WHERE it.transaction_type = 'دریافت'
            AND it.transaction_date BETWEEN ? AND ?
            GROUP BY it.description
            ORDER BY amount DESC
            """
            
            results = self.data_manager.db.fetch_all(query, (start_date, end_date))
            
            income_by_category = {}
            for result in results:
                category = result.get('description', 'سایر')
                amount = result.get('amount', 0)
                income_by_category[category] = amount
            
            return income_by_category
            
        except Exception as e:
            print(f"⚠️ خطا در دریافت درآمد بر اساس دسته: {e}")
            return {}
    
    def load_expense_by_category(self, start_date, end_date):
        """بارگذاری هزینه بر اساس دسته"""
        try:
            query = """
            SELECT 
                it.description as category,
                SUM(it.amount) as amount
            FROM AccountingTransactions it
            WHERE it.transaction_type = 'پرداخت'
            AND it.transaction_date BETWEEN ? AND ?
            GROUP BY it.description
            ORDER BY amount DESC
            """
            
            results = self.data_manager.db.fetch_all(query, (start_date, end_date))
            
            expense_by_category = {}
            for result in results:
                category = result.get('description', 'سایر')
                amount = result.get('amount', 0)
                expense_by_category[category] = amount
            
            return expense_by_category
            
        except Exception as e:
            print(f"⚠️ خطا در دریافت هزینه بر اساس دسته: {e}")
            return {}
    
    def load_sample_monthly_data(self):
        """بارگذاری داده‌های نمونه"""
        self.monthly_data = {
            'summary': {
                'total_activities': 180,
                'completed_repairs': 145,
                'unique_customers': 65,
                'total_income': 42000000,
                'total_expense': 21000000,
                'net_profit': 21000000,
                'total_invoices': 85,
                'total_sales': 38000000,
                'avg_invoice_amount': 447000,
                'avg_daily_income': 1400000,
                'avg_daily_expense': 700000
            },
            'daily_data': [
                {'day_number': 1, 'date': '2024-01-01', 'day_name': 'شنبه', 'activities': 8, 'income': 1500000, 'expense': 700000, 'profit': 800000, 'invoices': 3, 'efficiency': 53.3},
                {'day_number': 2, 'date': '2024-01-02', 'day_name': 'یکشنبه', 'activities': 7, 'income': 1200000, 'expense': 600000, 'profit': 600000, 'invoices': 2, 'efficiency': 50.0},
                # ... داده‌های سایر روزها
            ],
            'income_by_category': {
                'تعمیرات': 25000000,
                'فروش قطعات': 12000000,
                'سایر': 5000000
            },
            'expense_by_category': {
                'حقوق کارکنان': 8000000,
                'خرید قطعات': 7000000,
                'اجاره': 3000000,
                'آب و برق': 1000000,
                'سایر': 2000000
            }
        }
    
    def update_summary_tab(self):
        """به‌روزرسانی تب خلاصه"""
        summary = self.monthly_data.get('summary', {})
        daily_data = self.monthly_data.get('daily_data', [])
        income_by_category = self.monthly_data.get('income_by_category', {})
        expense_by_category = self.monthly_data.get('expense_by_category', {})
        
        # به‌روزرسانی کارت‌ها (این بخش نیاز به اتصال به ویجت‌های واقعی دارد)
        print(f"📊 آمار ماه: {summary}")
        
        # به‌روزرسانی جدول روزها
        self.update_daily_stats_table(daily_data)
        
        # به‌روزرسانی نمودارها
        self.update_summary_charts(income_by_category, expense_by_category)
    
    def update_daily_stats_table(self, daily_data):
        """به‌روزرسانی جدول آمار روزانه"""
        for i, day in enumerate(daily_data):
            # تاریخ شمسی
            date_shamsi = gregorian_to_jalali(day['date'])
            
            # فعالیت‌ها
            activities_item = QTableWidgetItem(str(day['activities']))
            activities_item.setTextAlignment(Qt.AlignCenter)
            
            # درآمد (تبدیل به تومان)
            income_toman = day['income'] / 10
            income_item = QTableWidgetItem(f"{income_toman:,.0f}")
            income_item.setTextAlignment(Qt.AlignCenter)
            
            # هزینه (تبدیل به تومان)
            expense_toman = day['expense'] / 10
            expense_item = QTableWidgetItem(f"{expense_toman:,.0f}")
            expense_item.setTextAlignment(Qt.AlignCenter)
            
            # سود (تبدیل به تومان)
            profit_toman = day['profit'] / 10
            profit_item = QTableWidgetItem(f"{profit_toman:,.0f}")
            profit_item.setTextAlignment(Qt.AlignCenter)
            
            # کارایی
            efficiency_item = QTableWidgetItem(f"{day['efficiency']:.1f}%")
            efficiency_item.setTextAlignment(Qt.AlignCenter)
            
            # رنگ‌بندی سود
            if profit_toman > 0:
                profit_item.setForeground(QColor("#2ecc71"))
                efficiency_item.setForeground(QColor("#2ecc71"))
            elif profit_toman < 0:
                profit_item.setForeground(QColor("#e74c3c"))
                efficiency_item.setForeground(QColor("#e74c3c"))
            
            # قرار دادن در جدول
            self.daily_stats_table.setItem(i, 0, QTableWidgetItem(str(day['day_number'])))
            self.daily_stats_table.setItem(i, 1, QTableWidgetItem(date_shamsi))
            self.daily_stats_table.setItem(i, 2, activities_item)
            self.daily_stats_table.setItem(i, 3, income_item)
            self.daily_stats_table.setItem(i, 4, expense_item)
            self.daily_stats_table.setItem(i, 5, profit_item)
            self.daily_stats_table.setItem(i, 6, efficiency_item)
    
    def update_summary_charts(self, income_by_category, expense_by_category):
        """به‌روزرسانی نمودارهای خلاصه"""
        # نمودار دایره‌ای درآمد
        self.update_income_pie_chart(income_by_category)
        
        # نمودار میله‌ای هزینه
        self.update_expense_bar_chart(expense_by_category)
    
    def update_income_pie_chart(self, income_by_category):
        """به‌روزرسانی نمودار دایره‌ای درآمد"""
        try:
            if not income_by_category:
                return
            
            chart = QChart()
            chart.setTitle("توزیع درآمد بر اساس دسته")
            chart.setTitleFont(QFont("B Nazanin", 11, QFont.Bold))
            chart.setAnimationOptions(QChart.SeriesAnimations)
            
            pie_series = QPieSeries()
            pie_series.setPieSize(0.7)
            
            # رنگ‌های مختلف برای دسته‌ها
            colors = {
                'تعمیرات': QColor("#3498db"),
                'فروش قطعات': QColor("#2ecc71"),
                'فروش لوازم': QColor("#9b59b6"),
                'خدمات': QColor("#f39c12"),
                'سایر': QColor("#95a5a6")
            }
            
            total_income = sum(income_by_category.values())
            
            for category, amount in income_by_category.items():
                percentage = (amount / total_income * 100) if total_income > 0 else 0
                amount_toman = amount / 10
                
                slice = pie_series.append(
                    f"{category}\n{self._format_currency(amount_toman)} تومان ({percentage:.1f}%)", 
                    amount
                )
                slice.setColor(colors.get(category, QColor("#95a5a6")))
                
                # نمایش مقدار روی برش
                slice.setLabelVisible(True)
                slice.setLabelPosition(QPieSlice.LabelInsideNormal)
                slice.setLabelBrush(QColor("#FFFFFF"))
            
            chart.addSeries(pie_series)
            chart.legend().setVisible(True)
            chart.legend().setAlignment(Qt.AlignRight)
            
            self.income_pie_chart.setChart(chart)
            
        except Exception as e:
            print(f"⚠️ خطا در ایجاد نمودار درآمد: {e}")
    
    def update_expense_bar_chart(self, expense_by_category):
        """به‌روزرسانی نمودار میله‌ای هزینه"""
        try:
            if not expense_by_category:
                return
            
            chart = QChart()
            chart.setTitle("توزیع هزینه بر اساس دسته")
            chart.setTitleFont(QFont("B Nazanin", 11, QFont.Bold))
            chart.setAnimationOptions(QChart.SeriesAnimations)
            
            bar_series = QBarSeries()
            
            # رنگ‌های مختلف برای دسته‌ها
            colors = {
                'حقوق کارکنان': QColor("#e74c3c"),
                'خرید قطعات': QColor("#3498db"),
                'اجاره': QColor("#f39c12"),
                'آب و برق': QColor("#1abc9c"),
                'سایر': QColor("#95a5a6")
            }
            
            # ایجاد بارست برای هر دسته
            categories = list(expense_by_category.keys())[:5]  # فقط ۵ دسته اول
            for category in categories:
                amount = expense_by_category[category]
                amount_toman = amount / 10 / 1000  # تبدیل به هزار تومان
                
                bar_set = QBarSet(category)
                bar_set.append(amount_toman)
                bar_set.setColor(colors.get(category, QColor("#95a5a6")))
                bar_series.append(bar_set)
            
            chart.addSeries(bar_series)
            
            # محور X
            axis_x = QBarCategoryAxis()
            axis_x.append([''])
            chart.addAxis(axis_x, Qt.AlignBottom)
            bar_series.attachAxis(axis_x)
            
            # محور Y
            axis_y = QValueAxis()
            axis_y.setTitleText("مبلغ (هزار تومان)")
            axis_y.setLabelFormat("%.0f")
            chart.addAxis(axis_y, Qt.AlignLeft)
            bar_series.attachAxis(axis_y)
            
            chart.legend().setVisible(True)
            chart.legend().setAlignment(Qt.AlignBottom)
            
            self.expense_bar_chart.setChart(chart)
            
        except Exception as e:
            print(f"⚠️ خطا در ایجاد نمودار هزینه: {e}")
    
    def _format_currency(self, amount):
        """فرمت کردن مبلغ به صورت جداکننده هزارگان"""
        return f"{amount:,.0f}".replace(",", "٬")
    
    def apply_filters(self):
        """اعمال فیلترها"""
        self.status_label.setText("🔄 در حال اعمال فیلترها...")
        QTimer.singleShot(100, self.load_monthly_data)
    
    def reset_filters(self):
        """بازنشانی فیلترها"""
        self.month_combo.setCurrentIndex(0)
        self.report_type_combo.setCurrentIndex(0)
        self.apply_filters()
    
    def export_to_excel(self):
        """صدور گزارش به Excel"""
        try:
            from ui.forms.reports.utils.exporters import ExcelExporter
            
            exporter = ExcelExporter(self.data_manager)
            
            # دریافت تاریخ‌های ماه
            month_start, month_end = self.get_current_month_dates()
            
            # آماده‌سازی داده‌ها برای export
            monthly_data = self.prepare_monthly_data_for_export()
            
            success, message = exporter.export_monthly_report(
                monthly_data, month_start, month_end
            )
            
            if success:
                QMessageBox.information(self, "✅ موفق", message)
            else:
                QMessageBox.warning(self, "⚠️ خطا", message)
                
        except Exception as e:
            QMessageBox.critical(self, "❌ خطا", f"خطا در صدور خروجی:\n{str(e)}")
    
    def print_report(self):
        """چاپ گزارش"""
        try:
            from ui.forms.reports.utils.printers import ReportPrinter
            
            printer = ReportPrinter(self.data_manager)
            
            # دریافت تاریخ‌های ماه
            month_start, month_end = self.get_current_month_dates()
            
            # چاپ
            success, message = printer.print_monthly_report(self.monthly_data, month_start, month_end)
            
            if success:
                QMessageBox.information(self, "✅ موفق", message)
            else:
                QMessageBox.warning(self, "⚠️ خطا", message)
                
        except Exception as e:
            QMessageBox.critical(self, "❌ خطا", f"خطا در چاپ:\n{str(e)}")
    
    def prepare_monthly_data_for_export(self):
        """آماده‌سازی داده‌های ماهانه برای خروجی"""
        return self.monthly_data