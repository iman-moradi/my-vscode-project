# ui/forms/reports/forms/weekly_report_form.py
"""
فرم گزارش هفتگی کامل
"""

from PySide6.QtWidgets import *
from PySide6.QtCore import Qt, Signal, QDate, QTimer
from PySide6.QtGui import QFont, QColor, QPainter
from ui.forms.reports.utils.date_utils import get_current_jalali, gregorian_to_jalali
from PySide6.QtCharts import QChart, QChartView, QLineSeries, QBarSeries, QBarSet
from PySide6.QtCharts import QValueAxis, QBarCategoryAxis
import datetime


class WeeklyReportForm(QWidget):
    """فرم گزارش هفتگی"""
    
    report_updated = Signal(dict)
    
    def __init__(self, data_manager):
        super().__init__()
        self.data_manager = data_manager
        self.weekly_data = {}
        
        self.setup_ui()
        self.load_weekly_data()
    
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
        btn_refresh.clicked.connect(self.load_weekly_data)
        
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
        
        # انتخاب هفته
        layout.addWidget(QLabel("هفته:"), 0, 0)
        self.week_combo = QComboBox()
        
        # تولید لیست هفته‌های اخیر
        current_date = QDate.currentDate()
        for i in range(12):  # ۱۲ هفته اخیر
            week_start = current_date.addDays(-i * 7)
            week_number = week_start.weekNumber()[0]
            year = week_start.year()
            self.week_combo.addItem(f"هفته {week_number} - {year}")
        
        layout.addWidget(self.week_combo, 0, 1)
        
        # نوع گزارش
        layout.addWidget(QLabel("نوع گزارش:"), 0, 2)
        self.report_type_combo = QComboBox()
        self.report_type_combo.addItems([
            "فعالیت‌ها",
            "مالی",
            "فروش",
            "تعمیرات",
            "انبار"
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
                background-color: #3498db;
                color: white;
            }
            QTabBar::tab:hover:!selected {
                background-color: #34495e;
            }
        """)
        
        # ایجاد تب‌ها
        self.create_summary_tab()
        self.create_daily_tab()
        self.create_analysis_tab()
        self.create_comparison_tab()
        
        parent_layout.addWidget(self.tab_widget, 1)
    
    def create_summary_tab(self):
        """ایجاد تب خلاصه هفته"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # هدر
        header_label = QLabel("📊 خلاصه عملکرد هفته")
        header_label.setStyleSheet("""
            QLabel {
                color: #3498db;
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
        
        # نمودار روند هفتگی
        self.create_weekly_trend_chart(layout)
        
        # جدول روزهای هفته
        self.create_days_table(layout)
        
        self.tab_widget.addTab(tab, "📊 خلاصه")
    
    def create_summary_cards(self, parent_layout):
        """ایجاد کارت‌های آمار خلاصه"""
        cards_frame = QFrame()
        cards_layout = QGridLayout(cards_frame)
        cards_layout.setSpacing(15)
        
        # کارت‌های مختلف
        stats = [
            ("📋 کل فعالیت‌ها", "۰", "#3498db"),
            ("💰 درآمد هفته", "۰ تومان", "#2ecc71"),
            ("📉 هزینه هفته", "۰ تومان", "#e74c3c"),
            ("📊 سود هفته", "۰ تومان", "#f39c12"),
            ("🔧 تعمیرات تکمیل شده", "۰", "#1abc9c"),
            ("🛒 فاکتورهای صادر شده", "۰", "#9b59b6"),
            ("👥 مشتریان جدید", "۰", "#27ae60"),
            ("📦 موجودی اضافه شده", "۰ قلم", "#e67e22")
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
    
    def create_weekly_trend_chart(self, parent_layout):
        """ایجاد نمودار روند هفتگی"""
        group = QGroupBox("📈 روند روزانه هفته")
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
        
        # نمودار
        self.trend_chart_view = QChartView()
        self.trend_chart_view.setRenderHint(QPainter.Antialiasing)
        self.trend_chart_view.setMinimumHeight(250)
        
        layout.addWidget(self.trend_chart_view)
        parent_layout.addWidget(group)
    
    def create_days_table(self, parent_layout):
        """ایجاد جدول روزهای هفته"""
        group = QGroupBox("📋 عملکرد روزهای هفته")
        group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #2ecc71;
                border-radius: 8px;
                margin-top: 15px;
                padding-top: 15px;
                color: #2ecc71;
                font-size: 12pt;
            }
        """)
        
        layout = QVBoxLayout(group)
        
        # جدول
        self.days_table = QTableWidget(7, 6)
        
        # تنظیمات
        for i in range(7):
            self.days_table.setRowHeight(i, 35)
        
        self.days_table.setStyleSheet("""
            QTableWidget {
                background-color: #111111;
                alternate-background-color: #0a0a0a;
                gridline-color: #333333;
                color: #ffffff;
                font-size: 10pt;
                font-family: 'B Nazanin';
            }
            QTableWidget::item {
                padding: 8px;
            }
            QTableWidget::item:selected {
                background-color: #3498db;
                color: white;
            }
            QHeaderView::section {
                background-color: #2c3e50;
                color: white;
                padding: 10px;
                border: none;
                font-weight: bold;
                font-size: 11pt;
                font-family: 'B Nazanin';
            }
        """)
        
        # هدرها
        headers = ["روز", "تاریخ", "فعالیت‌ها", "درآمد", "هزینه", "سود"]
        self.days_table.setHorizontalHeaderLabels(headers)
        
        # تنظیم ستون‌ها
        header = self.days_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)
        
        # نام روزها
        days = ["شنبه", "یکشنبه", "دوشنبه", "سه‌شنبه", "چهارشنبه", "پنجشنبه", "جمعه"]
        for i, day in enumerate(days):
            day_item = QTableWidgetItem(day)
            day_item.setTextAlignment(Qt.AlignCenter)
            self.days_table.setItem(i, 0, day_item)
        
        layout.addWidget(self.days_table)
        parent_layout.addWidget(group)
    
    def create_daily_tab(self):
        """ایجاد تب روزانه"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # محتوای تب روزانه
        label = QLabel("📅 گزارش روزانه هفته - به زودی...")
        label.setAlignment(Qt.AlignCenter)
        label.setStyleSheet("""
            QLabel {
                color: #7f8c8d;
                font-size: 18pt;
                padding: 50px;
            }
        """)
        
        layout.addWidget(label)
        self.tab_widget.addTab(tab, "📅 روزانه")
    
    def create_analysis_tab(self):
        """ایجاد تب تحلیل"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # محتوای تب تحلیل
        label = QLabel("📈 تحلیل هفتگی - به زودی...")
        label.setAlignment(Qt.AlignCenter)
        label.setStyleSheet("""
            QLabel {
                color: #7f8c8d;
                font-size: 18pt;
                padding: 50px;
            }
        """)
        
        layout.addWidget(label)
        self.tab_widget.addTab(tab, "📈 تحلیل")
    
    def create_comparison_tab(self):
        """ایجاد تب مقایسه"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # محتوای تب مقایسه
        label = QLabel("📊 مقایسه با هفته قبل - به زودی...")
        label.setAlignment(Qt.AlignCenter)
        label.setStyleSheet("""
            QLabel {
                color: #7f8c8d;
                font-size: 18pt;
                padding: 50px;
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
        
        self.status_label = QLabel("✅ سیستم گزارش هفتگی آماده است")
        self.week_info_label = QLabel("هفته جاری: --")
        self.last_update_label = QLabel("آخرین بروزرسانی: --:--")
        
        layout.addWidget(self.status_label, 5)
        layout.addWidget(self.week_info_label, 3)
        layout.addWidget(self.last_update_label, 3)
        
        parent_layout.addWidget(status_frame)
    
    def load_weekly_data(self):
        """بارگذاری داده‌های هفتگی"""
        try:
            self.status_label.setText("📊 در حال دریافت داده‌های هفتگی...")
            
            # دریافت تاریخ‌های هفته
            week_start, week_end = self.get_current_week_dates()
            
            # دریافت داده‌ها از دیتابیس
            self.load_data_from_database(week_start, week_end)
            
            # به‌روزرسانی UI
            self.update_summary_tab()
            
            self.status_label.setText("✅ داده‌های هفتگی بارگذاری شد")
            self.week_info_label.setText(f"هفته: {week_start} تا {week_end}")
            self.last_update_label.setText(f"آخرین بروزرسانی: {get_current_jalali()}")
            
        except Exception as e:
            self.status_label.setText(f"❌ خطا در بارگذاری داده‌ها: {str(e)}")
            print(f"خطا در load_weekly_data: {e}")
            self.load_sample_weekly_data()
    
    def get_current_week_dates(self):
        """دریافت تاریخ شروع و پایان هفته جاری"""
        today = QDate.currentDate()
        
        # پیدا کردن شنبه (اول هفته)
        days_since_saturday = (today.dayOfWeek() + 1) % 7
        week_start = today.addDays(-days_since_saturday)
        
        # جمعه (آخر هفته)
        week_end = week_start.addDays(6)
        
        return (
            week_start.toString("yyyy-MM-dd"),
            week_end.toString("yyyy-MM-dd")
        )
    
    def load_data_from_database(self, start_date, end_date):
        """بارگذاری داده‌ها از دیتابیس"""
        try:
            # آمار کلی هفته
            query = """
            SELECT 
                COUNT(r.id) as total_activities,
                SUM(CASE WHEN r.status = 'تعمیر شده' THEN 1 ELSE 0 END) as completed_repairs,
                SUM(CASE WHEN r.status = 'تحویل داده شده' THEN 1 ELSE 0 END) as delivered,
                SUM(r.estimated_cost) as total_estimated
            FROM Receptions r
            WHERE r.reception_date BETWEEN ? AND ?
            """
            
            activities_result = self.data_manager.db.fetch_one(query, (start_date, end_date))
            
            # آمار مالی هفته
            query = """
            SELECT 
                SUM(CASE WHEN transaction_type = 'دریافت' THEN amount ELSE 0 END) as total_income,
                SUM(CASE WHEN transaction_type = 'پرداخت' THEN amount ELSE 0 END) as total_expense,
                COUNT(*) as total_transactions
            FROM AccountingTransactions
            WHERE transaction_date BETWEEN ? AND ?
            """
            
            financial_result = self.data_manager.db.fetch_one(query, (start_date, end_date))
            
            # پردازش داده‌ها
            self.weekly_data = {
                'summary': {
                    'total_activities': activities_result.get('total_activities', 0) if activities_result else 0,
                    'completed_repairs': activities_result.get('completed_repairs', 0) if activities_result else 0,
                    'total_income': financial_result.get('total_income', 0) if financial_result else 0,
                    'total_expense': financial_result.get('total_expense', 0) if financial_result else 0,
                    'net_profit': (financial_result.get('total_income', 0) - financial_result.get('total_expense', 0)) 
                        if financial_result else 0
                },
                'daily_data': self.load_daily_data(start_date, end_date)
            }
            
        except Exception as e:
            print(f"❌ خطا در بارگذاری داده‌های هفتگی: {e}")
            raise
    
    def load_daily_data(self, start_date, end_date):
        """بارگذاری داده‌های روزانه هفته"""
        daily_data = []
        
        # تبدیل رشته تاریخ به QDate
        from PySide6.QtCore import QDate
        
        start_qdate = QDate.fromString(start_date, "yyyy-MM-dd")
        end_qdate = QDate.fromString(end_date, "yyyy-MM-dd")
        
        current_date = start_qdate
        while current_date <= end_qdate:
            date_str = current_date.toString("yyyy-MM-dd")
            
            # دریافت آمار روز
            query = """
            SELECT 
                COUNT(r.id) as activities,
                SUM(CASE WHEN at.transaction_type = 'دریافت' THEN at.amount ELSE 0 END) as income,
                SUM(CASE WHEN at.transaction_type = 'پرداخت' THEN at.amount ELSE 0 END) as expense
            FROM Receptions r
            LEFT JOIN AccountingTransactions at ON DATE(at.transaction_date) = ?
            WHERE r.reception_date = ?
            GROUP BY r.reception_date
            """
            
            result = self.data_manager.db.fetch_one(query, (date_str, date_str))
            
            daily_data.append({
                'date': date_str,
                'day_name': self.get_day_name(current_date.dayOfWeek()),
                'activities': result.get('activities', 0) if result else 0,
                'income': result.get('income', 0) if result else 0,
                'expense': result.get('expense', 0) if result else 0,
                'profit': (result.get('income', 0) - result.get('expense', 0)) if result else 0
            })
            
            current_date = current_date.addDays(1)
        
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
    
    def load_sample_weekly_data(self):
        """بارگذاری داده‌های نمونه"""
        self.weekly_data = {
            'summary': {
                'total_activities': 45,
                'completed_repairs': 32,
                'total_income': 8500000,
                'total_expense': 4200000,
                'net_profit': 4300000
            },
            'daily_data': [
                {'date': '2024-01-01', 'day_name': 'شنبه', 'activities': 8, 'income': 1500000, 'expense': 700000, 'profit': 800000},
                {'date': '2024-01-02', 'day_name': 'یکشنبه', 'activities': 7, 'income': 1200000, 'expense': 600000, 'profit': 600000},
                {'date': '2024-01-03', 'day_name': 'دوشنبه', 'activities': 6, 'income': 1000000, 'expense': 500000, 'profit': 500000},
                {'date': '2024-01-04', 'day_name': 'سه‌شنبه', 'activities': 9, 'income': 1800000, 'expense': 800000, 'profit': 1000000},
                {'date': '2024-01-05', 'day_name': 'چهارشنبه', 'activities': 5, 'income': 900000, 'expense': 400000, 'profit': 500000},
                {'date': '2024-01-06', 'day_name': 'پنجشنبه', 'activities': 7, 'income': 1300000, 'expense': 700000, 'profit': 600000},
                {'date': '2024-01-07', 'day_name': 'جمعه', 'activities': 3, 'income': 800000, 'expense': 500000, 'profit': 300000}
            ]
        }
    
    def update_summary_tab(self):
        """به‌روزرسانی تب خلاصه"""
        summary = self.weekly_data.get('summary', {})
        daily_data = self.weekly_data.get('daily_data', [])
        
        # به‌روزرسانی کارت‌ها (این بخش نیاز به اتصال به ویجت‌های واقعی دارد)
        print(f"📊 آمار هفته: {summary}")
        
        # به‌روزرسانی جدول روزها
        self.update_days_table(daily_data)
        
        # به‌روزرسانی نمودار روند
        self.update_trend_chart(daily_data)
    
    def update_days_table(self, daily_data):
        """به‌روزرسانی جدول روزها"""
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
            
            # رنگ‌بندی سود
            if profit_toman > 0:
                profit_item.setForeground(QColor("#2ecc71"))
            elif profit_toman < 0:
                profit_item.setForeground(QColor("#e74c3c"))
            
            # قرار دادن در جدول
            self.days_table.setItem(i, 1, QTableWidgetItem(date_shamsi))
            self.days_table.setItem(i, 2, activities_item)
            self.days_table.setItem(i, 3, income_item)
            self.days_table.setItem(i, 4, expense_item)
            self.days_table.setItem(i, 5, profit_item)
    
    def update_trend_chart(self, daily_data):
        """به‌روزرسانی نمودار روند"""
        try:
            chart = QChart()
            chart.setTitle("📈 روند درآمد و هزینه روزانه هفته")
            chart.setTitleFont(QFont("B Nazanin", 12, QFont.Bold))
            chart.setAnimationOptions(QChart.SeriesAnimations)
            
            # سری درآمد
            income_series = QLineSeries()
            income_series.setName("درآمد")
            income_series.setColor(QColor("#2ecc71"))
            
            # سری هزینه
            expense_series = QLineSeries()
            expense_series.setName("هزینه")
            expense_series.setColor(QColor("#e74c3c"))
            
            # اضافه کردن نقاط
            for i, day in enumerate(daily_data):
                income_toman = day['income'] / 10 / 1000  # تبدیل به هزار تومان
                expense_toman = day['expense'] / 10 / 1000  # تبدیل به هزار تومان
                
                income_series.append(i, income_toman)
                expense_series.append(i, expense_toman)
            
            # اضافه کردن سری‌ها به نمودار
            chart.addSeries(income_series)
            chart.addSeries(expense_series)
            
            # محور X
            axis_x = QBarCategoryAxis()
            axis_x.setTitleText("روزهای هفته")
            day_names = [day['day_name'] for day in daily_data]
            axis_x.append(day_names)
            chart.addAxis(axis_x, Qt.AlignBottom)
            income_series.attachAxis(axis_x)
            expense_series.attachAxis(axis_x)
            
            # محور Y
            axis_y = QValueAxis()
            axis_y.setTitleText("مبلغ (هزار تومان)")
            axis_y.setLabelFormat("%.0f")
            chart.addAxis(axis_y, Qt.AlignLeft)
            income_series.attachAxis(axis_y)
            expense_series.attachAxis(axis_y)
            
            chart.legend().setVisible(True)
            chart.legend().setAlignment(Qt.AlignBottom)
            
            self.trend_chart_view.setChart(chart)
            
        except Exception as e:
            print(f"⚠️ خطا در ایجاد نمودار: {e}")
    
    def apply_filters(self):
        """اعمال فیلترها"""
        self.status_label.setText("🔄 در حال اعمال فیلترها...")
        QTimer.singleShot(100, self.load_weekly_data)
    
    def reset_filters(self):
        """بازنشانی فیلترها"""
        self.week_combo.setCurrentIndex(0)
        self.report_type_combo.setCurrentIndex(0)
        self.apply_filters()
    
    def export_to_excel(self):
        """صدور گزارش به Excel"""
        try:
            from ui.forms.reports.utils.exporters import ExcelExporter
            
            exporter = ExcelExporter(self.data_manager)
            
            # دریافت تاریخ‌های هفته
            week_start, week_end = self.get_current_week_dates()
            
            # آماده‌سازی داده‌ها برای export
            weekly_data = self.prepare_weekly_data_for_export()
            
            success, message = exporter.export_weekly_report(
                weekly_data, week_start, week_end
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
            
            # دریافت تاریخ‌های هفته
            week_start, week_end = self.get_current_week_dates()
            
            # چاپ
            success, message = printer.print_weekly_report(self.weekly_data, week_start, week_end)
            
            if success:
                QMessageBox.information(self, "✅ موفق", message)
            else:
                QMessageBox.warning(self, "⚠️ خطا", message)
                
        except Exception as e:
            QMessageBox.critical(self, "❌ خطا", f"خطا در چاپ:\n{str(e)}")
    
    def prepare_weekly_data_for_export(self):
        """آماده‌سازی داده‌های هفتگی برای خروجی"""
        return self.weekly_data