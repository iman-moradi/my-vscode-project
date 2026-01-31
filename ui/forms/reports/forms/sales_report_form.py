# ui/forms/reports/forms/sales_report_form.py
"""
فرم گزارش فروش کامل
شامل: آمار فروش، محصولات پرفروش، مشتریان برتر، تحلیل سودآوری
"""

import datetime
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QPushButton, QFrame, QScrollArea,
    QTableWidget, QTableWidgetItem, QHeaderView,
    QComboBox, QLineEdit, QDateEdit, QGroupBox,
    QFormLayout, QSpinBox, QCheckBox, QTextEdit,
    QProgressBar, QTabWidget, QSplitter, QSizePolicy
)
from PySide6.QtCore import Qt, Signal, QDate, QTimer
from PySide6.QtGui import QFont, QColor, QAction, QPainter, QBrush
from PySide6.QtCharts import QChart, QChartView, QBarSeries, QBarSet, QPieSeries, QPieSlice, QLineSeries, QValueAxis, QBarCategoryAxis
from utils.date_utils import get_current_jalali, gregorian_to_jalali, jalali_to_gregorian
from ui.forms.reports.utils.sales_calculator import SalesCalculator


class SalesReportForm(QWidget):
    """فرم گزارش فروش کامل"""
    
    report_updated = Signal(dict)  # سیگنال بروزرسانی گزارش
    
    def __init__(self, data_manager):
        super().__init__()
        self.data_manager = data_manager
        self.sales_calculator = SalesCalculator(data_manager)
        self.sales_data = {}
        
        # تنظیمات اولیه
        self.init_ui()
        
        # بارگذاری اولیه داده‌ها
        QTimer.singleShot(100, self.load_sales_data)
    
    def init_ui(self):
        """ایجاد رابط کاربری فرم"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)
        
        # نوار ابزار فیلترها
        self.create_filter_toolbar(main_layout)
        
        # ایجاد ویجت تب‌ها برای بخش‌های مختلف
        self.create_tab_widget(main_layout)
        
        # نوار وضعیت
        self.create_status_bar(main_layout)
    
    def create_filter_toolbar(self, parent_layout):
        """ایجاد نوار ابزار فیلترهای گزارش فروش"""
        filter_frame = QFrame()
        filter_frame.setFrameStyle(QFrame.StyledPanel | QFrame.Raised)
        filter_frame.setStyleSheet("""
            QFrame {
                background-color: #1a1a2e;
                border-radius: 6px;
                padding: 10px;
            }
            QLabel {
                color: #ffffff;
                font-weight: bold;
            }
            QComboBox, QLineEdit, QDateEdit {
                background-color: #2c3e50;
                color: white;
                border: 1px solid #34495e;
                border-radius: 4px;
                padding: 5px;
                min-height: 30px;
            }
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 8px 15px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        
        filter_layout = QGridLayout(filter_frame)
        
        # دوره زمانی
        filter_layout.addWidget(QLabel("📅 دوره زمانی:"), 0, 0)
        self.period_combo = QComboBox()
        self.period_combo.addItems([
            "امروز", 
            "دیروز", 
            "این هفته", 
            "هفته گذشته", 
            "این ماه", 
            "ماه گذشته",
            "سه ماهه",
            "بازه دلخواه"
        ])
        self.period_combo.currentIndexChanged.connect(self.on_period_changed)
        filter_layout.addWidget(self.period_combo, 0, 1)
        
        # تاریخ شروع
        filter_layout.addWidget(QLabel("از تاریخ:"), 0, 2)
        self.start_date_edit = QDateEdit()
        self.start_date_edit.setCalendarPopup(True)
        self.start_date_edit.setDate(QDate.currentDate().addDays(-30))
        filter_layout.addWidget(self.start_date_edit, 0, 3)
        
        # تاریخ پایان
        filter_layout.addWidget(QLabel("تا تاریخ:"), 0, 4)
        self.end_date_edit = QDateEdit()
        self.end_date_edit.setCalendarPopup(True)
        self.end_date_edit.setDate(QDate.currentDate())
        filter_layout.addWidget(self.end_date_edit, 0, 5)
        
        # نوع محصول/خدمات
        # نوع محصول/خدمات
        filter_layout.addWidget(QLabel("نوع:"), 0, 6)
        self.type_combo = QComboBox()
        self.type_combo.addItems([
            "همه",
            "لوازم نو",
            "لوازم دست دوم",
            "قطعات نو",
            "قطعات دست دوم",
            "خدمات"
        ])
        filter_layout.addWidget(self.type_combo, 0, 7)
        
        # دکمه اعمال فیلتر
        self.btn_apply_filter = QPushButton("✅ اعمال فیلتر")
        self.btn_apply_filter.clicked.connect(self.apply_filters)
        filter_layout.addWidget(self.btn_apply_filter, 0, 8)
        
        # دکمه بازنشانی
        self.btn_reset = QPushButton("🔄 بازنشانی")
        self.btn_reset.clicked.connect(self.reset_filters)
        filter_layout.addWidget(self.btn_reset, 0, 9)
        
        parent_layout.addWidget(filter_frame)
    
    def create_tab_widget(self, parent_layout):
        """ایجاد ویجت تب‌های مختلف"""
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabPosition(QTabWidget.North)
        
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
        
        # ایجاد تب‌های مختلف
        self.create_overview_tab()
        self.create_products_tab()
        self.create_customers_tab()
        self.create_profitability_tab()
        self.create_trends_tab()
        
        parent_layout.addWidget(self.tab_widget, 1)
    
    def create_overview_tab(self):
        """ایجاد تب نمای کلی فروش"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # هدر تب
        header_label = QLabel("📊 نمای کلی فروش")
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
        
        # کارت‌های آمار سریع
        self.create_quick_stats_cards(layout)
        
        # نمودار فروش
        self.create_sales_chart(layout)
        
        # آخرین فروش‌ها
        self.create_recent_sales_table(layout)
        
        self.tab_widget.addTab(tab, "📊 نمای کلی")
    
    def create_quick_stats_cards(self, parent_layout):
        """ایجاد کارت‌های آمار سریع"""
        cards_frame = QFrame()
        cards_layout = QGridLayout(cards_frame)
        cards_layout.setSpacing(15)
        
        # کارت فروش کل
        self.total_sales_card = self.create_stat_card("💰 فروش کل", "۰ تومان", "#2ecc71", "📈")
        cards_layout.addWidget(self.total_sales_card, 0, 0)
        
        # کارت تعداد فاکتورها
        self.invoices_card = self.create_stat_card("📋 تعداد فاکتورها", "۰", "#3498db", "📄")
        cards_layout.addWidget(self.invoices_card, 0, 1)
        
        # کارت مشتریان منحصربفرد
        self.customers_card = self.create_stat_card("👥 مشتریان", "۰", "#9b59b6", "👤")
        cards_layout.addWidget(self.customers_card, 0, 2)
        
        # کارت میانگین فاکتور
        self.avg_invoice_card = self.create_stat_card("📊 میانگین فاکتور", "۰ تومان", "#e74c3c", "📝")
        cards_layout.addWidget(self.avg_invoice_card, 0, 3)
        
        # کارت نقدی
        self.cash_sales_card = self.create_stat_card("💵 فروش نقدی", "۰ تومان", "#27ae60", "💵")
        cards_layout.addWidget(self.cash_sales_card, 1, 0)
        
        # کارت چک
        self.check_sales_card = self.create_stat_card("🏦 فروش چک", "۰ تومان", "#2980b9", "🏦")
        cards_layout.addWidget(self.check_sales_card, 1, 1)
        
        # کارت کارت
        self.card_sales_card = self.create_stat_card("💳 فروش کارت", "۰ تومان", "#8e44ad", "💳")
        cards_layout.addWidget(self.card_sales_card, 1, 2)
        
        # کارت نسیه
        self.credit_sales_card = self.create_stat_card("📅 فروش نسیه", "۰ تومان", "#d35400", "📅")
        cards_layout.addWidget(self.credit_sales_card, 1, 3)
        
        parent_layout.addWidget(cards_frame)
    
    def create_stat_card(self, title, value, color, icon):
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
        title_label = QLabel(f"{icon} {title}")
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
    
    def create_sales_chart(self, parent_layout):
        """ایجاد نمودار فروش"""
        group = QGroupBox("📈 نمودار روند فروش")
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
        
        # نمودار خطی
        self.sales_chart_view = QChartView()
        self.sales_chart_view.setRenderHint(QPainter.Antialiasing)
        self.sales_chart_view.setMinimumHeight(300)
        self.sales_chart_view.setStyleSheet("""
            QChartView {
                background-color: #111111;
                border-radius: 8px;
                border: 1px solid #444;
            }
        """)
        
        layout.addWidget(self.sales_chart_view)
        parent_layout.addWidget(group)
    
    def create_recent_sales_table(self, parent_layout):
        """ایجاد جدول آخرین فروش‌ها"""
        group = QGroupBox("🆕 آخرین فروش‌ها")
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
        
        # ایجاد جدول
        self.recent_sales_table = QTableWidget(10, 6)
        
        # تنظیم ارتفاع ردیف‌ها
        for i in range(10):
            self.recent_sales_table.setRowHeight(i, 35)
        
        self.recent_sales_table.setStyleSheet("""
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
        
        # تنظیم هدرهای جدول
        headers = ["شماره فاکتور", "تاریخ", "مشتری", "مبلغ کل", "وضعیت پرداخت", "تعداد آیتم"]
        self.recent_sales_table.setHorizontalHeaderLabels(headers)
        
        # تنظیمات ستون‌ها
        header = self.recent_sales_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # شماره فاکتور
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)  # تاریخ
        header.setSectionResizeMode(2, QHeaderView.Stretch)           # مشتری
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)  # مبلغ کل
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)  # وضعیت پرداخت
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)  # تعداد آیتم
        
        layout.addWidget(self.recent_sales_table)
        parent_layout.addWidget(group)
    
    def create_products_tab(self):
        """ایجاد تب محصولات پرفروش"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # هدر تب
        header_label = QLabel("🏆 محصولات پرفروش")
        header_label.setStyleSheet("""
            QLabel {
                color: #e74c3c;
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
        
        # جدول محصولات پرفروش
        self.create_top_products_table(layout)
        
        # نمودار توزیع فروش بر اساس دسته
        self.create_products_chart(layout)
        
        self.tab_widget.addTab(tab, "🏆 محصولات")
    
    def create_top_products_table(self, parent_layout):
        """ایجاد جدول محصولات پرفروش"""
        group = QGroupBox("📊 رتبه‌بندی محصولات پرفروش")
        group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #e74c3c;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 15px;
                color: #e74c3c;
                font-size: 12pt;
            }
        """)
        
        layout = QVBoxLayout(group)
        
        # ایجاد جدول
        self.top_products_table = QTableWidget(15, 7)
        
        # تنظیم ارتفاع ردیف‌ها
        for i in range(15):
            self.top_products_table.setRowHeight(i, 35)
        
        self.top_products_table.setStyleSheet("""
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
                background-color: #e74c3c;
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
        
        # تنظیم هدرهای جدول
        headers = ["رتبه", "محصول", "دسته", "برند", "تعداد فروش", "مبلغ فروش", "سود تخمینی"]
        self.top_products_table.setHorizontalHeaderLabels(headers)
        
        # تنظیمات ستون‌ها
        header = self.top_products_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # رتبه
        header.setSectionResizeMode(1, QHeaderView.Stretch)           # محصول
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)  # دسته
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)  # برند
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)  # تعداد فروش
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)  # مبلغ فروش
        header.setSectionResizeMode(6, QHeaderView.ResizeToContents)  # سود تخمینی
        
        layout.addWidget(self.top_products_table)
        parent_layout.addWidget(group)
    
    def create_products_chart(self, parent_layout):
        """ایجاد نمودار توزیع فروش محصولات"""
        group = QGroupBox("📈 توزیع فروش بر اساس دسته")
        group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #f39c12;
                border-radius: 8px;
                margin-top: 15px;
                padding-top: 15px;
                color: #f39c12;
                font-size: 12pt;
            }
        """)
        
        layout = QVBoxLayout(group)
        
        # نمودار دایره‌ای
        self.products_chart_view = QChartView()
        self.products_chart_view.setRenderHint(QPainter.Antialiasing)
        self.products_chart_view.setMinimumHeight(250)
        self.products_chart_view.setStyleSheet("""
            QChartView {
                background-color: #111111;
                border-radius: 8px;
                border: 1px solid #444;
            }
        """)
        
        layout.addWidget(self.products_chart_view)
        parent_layout.addWidget(group)
    
    def create_customers_tab(self):
        """ایجاد تب مشتریان برتر"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # هدر تب
        header_label = QLabel("👑 مشتریان برتر")
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
        
        # جدول مشتریان برتر
        self.create_top_customers_table(layout)
        
        # کارت‌های تحلیل مشتریان
        self.create_customer_analysis_cards(layout)
        
        self.tab_widget.addTab(tab, "👑 مشتریان")
    
    def create_top_customers_table(self, parent_layout):
        """ایجاد جدول مشتریان برتر"""
        group = QGroupBox("📊 رتبه‌بندی مشتریان برتر")
        group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #9b59b6;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 15px;
                color: #9b59b6;
                font-size: 12pt;
            }
        """)
        
        layout = QVBoxLayout(group)
        
        # ایجاد جدول
        self.top_customers_table = QTableWidget(12, 7)
        
        # تنظیم ارتفاع ردیف‌ها
        for i in range(12):
            self.top_customers_table.setRowHeight(i, 40)
        
        self.top_customers_table.setStyleSheet("""
            QTableWidget {
                background-color: #111111;
                alternate-background-color: #0a0a0a;
                gridline-color: #333333;
                color: #ffffff;
                font-size: 10pt;
                font-family: 'B Nazanin';
            }
            QTableWidget::item {
                padding: 10px;
            }
            QTableWidget::item:selected {
                background-color: #9b59b6;
                color: white;
            }
            QHeaderView::section {
                background-color: #2c3e50;
                color: white;
                padding: 12px;
                border: none;
                font-weight: bold;
                font-size: 11pt;
                font-family: 'B Nazanin';
            }
        """)
        
        # تنظیم هدرهای جدول
        headers = ["رتبه", "مشتری", "موبایل", "تعداد خرید", "مبلغ خرید", "نوع مشتری", "امتیاز وفاداری"]
        self.top_customers_table.setHorizontalHeaderLabels(headers)
        
        # تنظیمات ستون‌ها
        header = self.top_customers_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # رتبه
        header.setSectionResizeMode(1, QHeaderView.Stretch)           # مشتری
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)  # موبایل
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)  # تعداد خرید
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)  # مبلغ خرید
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)  # نوع مشتری
        header.setSectionResizeMode(6, QHeaderView.ResizeToContents)  # امتیاز وفاداری
        
        layout.addWidget(self.top_customers_table)
        parent_layout.addWidget(group)
    
    def create_customer_analysis_cards(self, parent_layout):
        """ایجاد کارت‌های تحلیل مشتریان"""
        cards_frame = QFrame()
        cards_layout = QGridLayout(cards_frame)
        cards_layout.setSpacing(10)
        
        # کارت‌های تحلیل
        analysis_cards = [
            ("🏆 مشتری VIP", "۰ نفر", "#e74c3c", self.create_analysis_card),
            ("💎 مشتری وفادار", "۰ نفر", "#3498db", self.create_analysis_card),
            ("⭐ مشتری منظم", "۰ نفر", "#2ecc71", self.create_analysis_card),
            ("🌱 مشتری جدید", "۰ نفر", "#f39c12", self.create_analysis_card),
            ("📊 میانگین خرید", "۰ تومان", "#9b59b6", self.create_analysis_card),
            ("📈 بیشترین خرید", "۰ تومان", "#1abc9c", self.create_analysis_card),
            ("📉 کمترین خرید", "۰ تومان", "#34495e", self.create_analysis_card),
            ("⚡ نرخ بازگشت", "۰٪", "#e67e22", self.create_analysis_card)
        ]
        
        for i, (title, value, color, creator) in enumerate(analysis_cards):
            row = i // 4
            col = i % 4
            card = creator(title, value, color)
            cards_layout.addWidget(card, row, col)
        
        parent_layout.addWidget(cards_frame)
    
    def create_analysis_card(self, title, value, color):
        """ایجاد یک کارت تحلیل"""
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background-color: {color}15;
                border: 1px solid {color};
                border-radius: 8px;
                padding: 12px;
            }}
        """)
        
        layout = QVBoxLayout(card)
        
        title_label = QLabel(title)
        title_label.setStyleSheet(f"""
            QLabel {{
                color: {color};
                font-size: 10pt;
                font-weight: bold;
                text-align: center;
            }}
        """)
        layout.addWidget(title_label)
        
        value_label = QLabel(value)
        value_label.setStyleSheet("""
            QLabel {
                color: #ffffff;
                font-size: 12pt;
                font-weight: bold;
                text-align: center;
                padding: 8px 0;
            }
        """)
        layout.addWidget(value_label)
        
        return card
    
    def create_profitability_tab(self):
        """ایجاد تب تحلیل سودآوری"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # هدر تب
        header_label = QLabel("💰 تحلیل سودآوری")
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
        
        # کارت‌های سودآوری
        self.create_profitability_cards(layout)
        
        # نمودار سودآوری
        self.create_profitability_chart(layout)
        
        # جدول مقایسه انبارها
        self.create_warehouse_comparison_table(layout)
        
        self.tab_widget.addTab(tab, "💰 سودآوری")
    
    def create_profitability_cards(self, parent_layout):
        """ایجاد کارت‌های سودآوری"""
        cards_frame = QFrame()
        cards_layout = QGridLayout(cards_frame)
        cards_layout.setSpacing(15)
        
        # کارت سود کل
        self.total_profit_card = self.create_stat_card("💰 سود کل", "۰ تومان", "#2ecc71", "💵")
        cards_layout.addWidget(self.total_profit_card, 0, 0)
        
        # کارت حاشیه سود
        self.profit_margin_card = self.create_stat_card("📊 حاشیه سود", "۰٪", "#27ae60", "📈")
        cards_layout.addWidget(self.profit_margin_card, 0, 1)
        
        # کارت سود لوازم نو
        self.new_appliances_profit_card = self.create_stat_card("🏠 سود لوازم نو", "۰ تومان", "#3498db", "🏠")
        cards_layout.addWidget(self.new_appliances_profit_card, 0, 2)
        
        # کارت سود لوازم دست دوم
        self.used_appliances_profit_card = self.create_stat_card("🔄 سود لوازم دست دوم", "۰ تومان", "#2980b9", "🔄")
        cards_layout.addWidget(self.used_appliances_profit_card, 0, 3)
        
        # کارت سود قطعات نو
        self.new_parts_profit_card = self.create_stat_card("🔩 سود قطعات نو", "۰ تومان", "#e74c3c", "🔩")
        cards_layout.addWidget(self.new_parts_profit_card, 1, 0)
        
        # کارت سود قطعات دست دوم
        self.used_parts_profit_card = self.create_stat_card("🔧 سود قطعات دست دوم", "۰ تومان", "#c0392b", "🔧")
        cards_layout.addWidget(self.used_parts_profit_card, 1, 1)
        
        # کارت سود خدمات
        self.services_profit_card = self.create_stat_card("🛠️ سود خدمات", "۰ تومان", "#f39c12", "🛠️")
        cards_layout.addWidget(self.services_profit_card, 1, 2)
        
        # کارت بازگشت سرمایه
        self.roi_card = self.create_stat_card("📈 بازگشت سرمایه", "۰٪", "#9b59b6", "📊")
        cards_layout.addWidget(self.roi_card, 1, 3)
        
        parent_layout.addWidget(cards_frame)
    
    def create_profitability_chart(self, parent_layout):
        """ایجاد نمودار سودآوری"""
        group = QGroupBox("📈 نمودار سودآوری بر اساس دسته")
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
        
        # نمودار میله‌ای
        self.profitability_chart_view = QChartView()
        self.profitability_chart_view.setRenderHint(QPainter.Antialiasing)
        self.profitability_chart_view.setMinimumHeight(250)
        self.profitability_chart_view.setStyleSheet("""
            QChartView {
                background-color: #111111;
                border-radius: 8px;
                border: 1px solid #444;
            }
        """)
        
        layout.addWidget(self.profitability_chart_view)
        parent_layout.addWidget(group)
    
    def create_warehouse_comparison_table(self, parent_layout):
        """ایجاد جدول مقایسه فروش انبارها"""
        group = QGroupBox("🏪 مقایسه فروش انبارها")
        group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #f39c12;
                border-radius: 8px;
                margin-top: 15px;
                padding-top: 15px;
                color: #f39c12;
                font-size: 12pt;
            }
        """)
        
        layout = QVBoxLayout(group)
        
        # ایجاد جدول
        self.warehouse_comparison_table = QTableWidget(5, 6)
        
        # تنظیم ارتفاع ردیف‌ها
        for i in range(5):
            self.warehouse_comparison_table.setRowHeight(i, 40)
        
        self.warehouse_comparison_table.setStyleSheet("""
            QTableWidget {
                background-color: #111111;
                alternate-background-color: #0a0a0a;
                gridline-color: #333333;
                color: #ffffff;
                font-size: 10pt;
                font-family: 'B Nazanin';
            }
            QTableWidget::item {
                padding: 10px;
            }
            QTableWidget::item:selected {
                background-color: #f39c12;
                color: white;
            }
            QHeaderView::section {
                background-color: #2c3e50;
                color: white;
                padding: 12px;
                border: none;
                font-weight: bold;
                font-size: 11pt;
                font-family: 'B Nazanin';
            }
        """)
        
        # تنظیم هدرهای جدول
        headers = ["انبار", "تعداد فروش", "فروش کل", "سود تخمینی", "حاشیه سود", "میانگین ارزش فروش"]
        self.warehouse_comparison_table.setHorizontalHeaderLabels(headers)
        
        # تنظیمات ستون‌ها
        header = self.warehouse_comparison_table.horizontalHeader()
        for i in range(6):
            header.setSectionResizeMode(i, QHeaderView.ResizeToContents)
        
        layout.addWidget(self.warehouse_comparison_table)
        parent_layout.addWidget(group)
    
    def create_trends_tab(self):
        """ایجاد تب روندهای فروش"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # هدر تب
        header_label = QLabel("📈 روندهای فروش")
        header_label.setStyleSheet("""
            QLabel {
                color: #1abc9c;
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
        
        # انتخاب بازه زمانی
        self.create_trends_period_selection(layout)
        
        # نمودار روند فروش
        self.create_trends_chart(layout)
        
        # جدول روندها
        self.create_trends_table(layout)
        
        self.tab_widget.addTab(tab, "📈 روندها")
    
    def create_trends_period_selection(self, parent_layout):
        """ایجاد انتخاب‌گر بازه زمانی برای روندها"""
        selection_frame = QFrame()
        selection_layout = QHBoxLayout(selection_frame)
        
        selection_layout.addWidget(QLabel("بازه زمانی:"))
        
        self.trends_period_combo = QComboBox()
        self.trends_period_combo.addItems([
            "روزانه (۳۰ روز اخیر)",
            "هفتگی (۱۲ هفته اخیر)",
            "ماهانه (۱۲ ماه اخیر)"
        ])
        self.trends_period_combo.currentIndexChanged.connect(self.load_trends_data)
        selection_layout.addWidget(self.trends_period_combo)
        
        # دکمه بازنشانی
        btn_refresh = QPushButton("🔄 بروزرسانی")
        btn_refresh.clicked.connect(self.load_trends_data)
        selection_layout.addWidget(btn_refresh)
        
        selection_layout.addStretch()
        parent_layout.addWidget(selection_frame)
    
    def create_trends_chart(self, parent_layout):
        """ایجاد نمودار روند فروش"""
        group = QGroupBox("📊 نمودار روند فروش")
        group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #1abc9c;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 15px;
                color: #1abc9c;
                font-size: 12pt;
            }
        """)
        
        layout = QVBoxLayout(group)
        
        # نمودار خطی
        self.trends_chart_view = QChartView()
        self.trends_chart_view.setRenderHint(QPainter.Antialiasing)
        self.trends_chart_view.setMinimumHeight(300)
        self.trends_chart_view.setStyleSheet("""
            QChartView {
                background-color: #111111;
                border-radius: 8px;
                border: 1px solid #444;
            }
        """)
        
        layout.addWidget(self.trends_chart_view)
        parent_layout.addWidget(group)
    
    def create_trends_table(self, parent_layout):
        """ایجاد جدول روندهای فروش"""
        group = QGroupBox("📋 داده‌های روند فروش")
        group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #34495e;
                border-radius: 8px;
                margin-top: 15px;
                padding-top: 15px;
                color: #34495e;
                font-size: 12pt;
            }
        """)
        
        layout = QVBoxLayout(group)
        
        # ایجاد جدول
        self.trends_table = QTableWidget(12, 6)
        
        # تنظیم ارتفاع ردیف‌ها
        for i in range(12):
            self.trends_table.setRowHeight(i, 35)
        
        self.trends_table.setStyleSheet("""
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
                background-color: #34495e;
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
        
        # تنظیم هدرهای جدول
        headers = ["دوره", "تعداد فاکتور", "فروش کل", "مشتریان منحصربفرد", "میانگین فاکتور", "نرخ تکمیل پرداخت"]
        self.trends_table.setHorizontalHeaderLabels(headers)
        
        # تنظیمات ستون‌ها
        header = self.trends_table.horizontalHeader()
        for i in range(6):
            header.setSectionResizeMode(i, QHeaderView.ResizeToContents)
        
        layout.addWidget(self.trends_table)
        parent_layout.addWidget(group)
    
    def create_status_bar(self, parent_layout):
        """ایجاد نوار وضعیت پایین فرم"""
        status_frame = QFrame()
        status_frame.setFrameStyle(QFrame.StyledPanel | QFrame.Sunken)
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
        
        status_layout = QHBoxLayout(status_frame)
        
        # وضعیت سیستم
        self.status_label = QLabel("✅ در حال بارگذاری داده‌های فروش...")
        
        # تعداد فاکتورها
        self.invoices_count_label = QLabel("تعداد فاکتورها: ۰")
        
        # آخرین بروزرسانی
        self.last_update_label = QLabel("آخرین بروزرسانی: --:--")
        
        status_layout.addWidget(self.status_label, 5)
        status_layout.addWidget(self.invoices_count_label, 3)
        status_layout.addWidget(self.last_update_label, 3)
        
        parent_layout.addWidget(status_frame)
    
    def on_period_changed(self, index):
        """رویداد تغییر دوره زمانی"""
        # غیرفعال کردن انتخاب تاریخ برای دوره‌های غیر دلخواه
        is_custom = (index == self.period_combo.count() - 1)  # آخرین آیتم = بازه دلخواه
        self.start_date_edit.setEnabled(is_custom)
        self.end_date_edit.setEnabled(is_custom)
    
    def apply_filters(self):
        """اعمال فیلترهای انتخاب شده"""
        self.status_label.setText("🔄 در حال اعمال فیلترها...")
        QTimer.singleShot(100, self.load_sales_data)
    
    def reset_filters(self):
        """بازنشانی فیلترها"""
        self.period_combo.setCurrentIndex(0)  # امروز
        self.start_date_edit.setDate(QDate.currentDate().addDays(-30))
        self.end_date_edit.setDate(QDate.currentDate())
        self.type_combo.setCurrentIndex(0)  # همه
        self.apply_filters()
    
    def load_sales_data(self):
        """بارگذاری داده‌های فروش"""
        try:
            self.status_label.setText("📊 در حال دریافت داده‌های فروش از دیتابیس...")
            
            # دریافت تاریخ‌های انتخاب شده
            start_date = self.start_date_edit.date().toString("yyyy-MM-dd")
            end_date = self.end_date_edit.date().toString("yyyy-MM-dd")
            
            # دریافت داده‌های فروش
            self.sales_data = self.sales_calculator.get_sales_summary(start_date, end_date)
            
            # دریافت آخرین فروش‌ها
            self.recent_sales_list = self.sales_calculator.get_recent_sales(10)
            
            # دریافت روندهای فروش
            self.load_trends_data()
            
            # به‌روزرسانی UI
            self.update_overview_tab()
            self.update_products_tab()
            self.update_customers_tab()
            self.update_profitability_tab()
            
            self.status_label.setText("✅ داده‌های فروش با موفقیت بارگذاری شدند")
            self.invoices_count_label.setText(
                f"تعداد فاکتورها: {self.sales_data.get('general_stats', {}).get('total_invoices', 0)}"
            )
            self.last_update_label.setText(f"آخرین بروزرسانی: {get_current_jalali()}")
            
            # ارسال سیگنال بروزرسانی
            self.report_updated.emit(self.sales_data)
            
        except Exception as e:
            self.status_label.setText(f"❌ خطا در بارگذاری داده‌ها: {str(e)}")
            print(f"خطا در load_sales_data: {e}")
            # در صورت خطا، از داده‌های نمونه استفاده کن
            self.load_sample_sales_data()
    
    def load_trends_data(self):
        """بارگذاری داده‌های روند فروش"""
        try:
            period_index = self.trends_period_combo.currentIndex()
            period = 'daily' if period_index == 0 else ('weekly' if period_index == 1 else 'monthly')
            
            self.trends_data = self.sales_calculator.get_sales_trends(period)
            
            # به‌روزرسانی تب روندها
            self.update_trends_tab()
            
        except Exception as e:
            print(f"❌ خطا در بارگذاری داده‌های روند: {e}")
            self.trends_data = []
    
    def load_sample_sales_data(self):
        """بارگذاری داده‌های نمونه فروش (در صورت خطا)"""
        self.sales_data = {
            'general_stats': {
                'total_invoices': 45,
                'total_sales': 85000000,
                'total_paid': 72000000,
                'total_credit': 13000000,
                'avg_invoice_amount': 1888889,
                'unique_customers': 28,
                'cash_sales': 45000000,
                'check_sales': 25000000,
                'card_sales': 12000000,
                'credit_sales': 3000000,
                'payment_completion_rate': 84.7
            },
            'top_products': [
                {'product_name': 'کمپرسور یخچال', 'category': 'قطعات نو', 'brand': 'ال جی', 
                 'sale_count': 12, 'total_sales_amount': 2400000, 'estimated_profit': 600000},
                {'product_name': 'یخچال ۲۴ فوت', 'category': 'لوازم نو', 'brand': 'سامسونگ',
                 'sale_count': 8, 'total_sales_amount': 32000000, 'estimated_profit': 9600000},
                {'product_name': 'ماشین لباسشویی دست دوم', 'category': 'لوازم دست دوم', 'brand': 'شارپ',
                 'sale_count': 6, 'total_sales_amount': 18000000, 'estimated_profit': 7200000}
            ],
            'top_customers': [
                {'customer_name': 'رضا محمدی', 'mobile': '09121234567', 'invoice_count': 8,
                 'total_purchases': 25000000, 'customer_type': 'VIP 🏆', 'loyalty_score': 85},
                {'customer_name': 'سارا احمدی', 'mobile': '09351234567', 'invoice_count': 5,
                 'total_purchases': 18000000, 'customer_type': 'وفادار 💎', 'loyalty_score': 68}
            ],
            'profitability_analysis': {
                'total_sales': 85000000,
                'total_profit': 25500000,
                'overall_profit_margin': 30.0,
                'categories': {
                    'new_appliances': {'sales': 40000000, 'profit': 12000000, 'margin': 30.0},
                    'used_appliances': {'sales': 20000000, 'profit': 8000000, 'margin': 40.0},
                    'new_parts': {'sales': 15000000, 'profit': 7500000, 'margin': 50.0},
                    'used_parts': {'sales': 8000000, 'profit': 4800000, 'margin': 60.0},
                    'services': {'sales': 2000000, 'profit': 1600000, 'margin': 80.0}
                }
            },
            'warehouse_comparison': [
                {'warehouse': 'لوازم نو', 'sale_count': 15, 'total_sales': 40000000, 
                 'estimated_profit': 12000000, 'profit_margin': 30.0, 'avg_sale_value': 2666667},
                {'warehouse': 'لوازم دست دوم', 'sale_count': 12, 'total_sales': 20000000,
                 'estimated_profit': 8000000, 'profit_margin': 40.0, 'avg_sale_value': 1666667}
            ]
        }
    
    def update_overview_tab(self):
        """به‌روزرسانی تب نمای کلی"""
        general_stats = self.sales_data.get('general_stats', {})
        
        # به‌روزرسانی کارت‌ها
        self.update_stat_card(self.total_sales_card, f"{self.format_currency(general_stats.get('total_sales', 0) / 10)} تومان")
        self.update_stat_card(self.invoices_card, f"{general_stats.get('total_invoices', 0)}")
        self.update_stat_card(self.customers_card, f"{general_stats.get('unique_customers', 0)}")
        self.update_stat_card(self.avg_invoice_card, f"{self.format_currency(general_stats.get('avg_invoice_amount', 0) / 10)} تومان")
        self.update_stat_card(self.cash_sales_card, f"{self.format_currency(general_stats.get('cash_sales', 0) / 10)} تومان")
        self.update_stat_card(self.check_sales_card, f"{self.format_currency(general_stats.get('check_sales', 0) / 10)} تومان")
        self.update_stat_card(self.card_sales_card, f"{self.format_currency(general_stats.get('card_sales', 0) / 10)} تومان")
        self.update_stat_card(self.credit_sales_card, f"{self.format_currency(general_stats.get('credit_sales', 0) / 10)} تومان")
        
        # به‌روزرسانی جدول آخرین فروش‌ها
        self.update_recent_sales_table()
        
        # به‌روزرسانی نمودار فروش
        self.update_sales_chart()
    
    def update_stat_card(self, card, new_value):
        """به‌روزرسانی کارت آمار"""
        layout = card.layout()
        if layout and layout.count() >= 2:
            value_label = layout.itemAt(1).widget()  # موقعیت دوم = مقدار
            if value_label:
                value_label.setText(new_value)
    
    def update_recent_sales_table(self):
        """به‌روزرسانی جدول آخرین فروش‌ها"""
        if not hasattr(self, 'recent_sales_list') or not self.recent_sales_list:
            return
        
        row_count = len(self.recent_sales_list)
        self.recent_sales_table.setRowCount(row_count)
        
        for row, sale in enumerate(self.recent_sales_list):
            # شماره فاکتور
            invoice_number = sale.get('invoice_number', '')
            
            # تاریخ (تبدیل به شمسی)
            invoice_date = sale.get('invoice_date', '')
            date_shamsi = gregorian_to_jalali(invoice_date) if invoice_date else ''
            
            # مشتری
            customer_name = sale.get('customer_name', '')
            
            # مبلغ کل (تبدیل از ریال به تومان)
            total = (sale.get('total', 0) or 0) / 10
            total_formatted = f"{self.format_currency(total)} تومان"
            
            # وضعیت پرداخت
            payment_status = sale.get('payment_status', '')
            
            # تعداد آیتم
            item_count = sale.get('item_count', 0)
            
            # قرار دادن در جدول
            items = [
                invoice_number,
                date_shamsi,
                customer_name,
                total_formatted,
                payment_status,
                str(item_count)
            ]
            
            for col, text in enumerate(items):
                item = QTableWidgetItem(str(text))
                item.setTextAlignment(Qt.AlignCenter)
                
                # رنگ‌بندی وضعیت پرداخت
                if col == 4:  # ستون وضعیت پرداخت
                    if payment_status in ['پرداخت شده', 'نقدی']:
                        item.setForeground(QColor("#2ecc71"))
                    elif payment_status == 'چک':
                        item.setForeground(QColor("#3498db"))
                    elif payment_status == 'کارت':
                        item.setForeground(QColor("#9b59b6"))
                    elif payment_status == 'نسیه':
                        item.setForeground(QColor("#f39c12"))
                
                self.recent_sales_table.setItem(row, col, item)
        
        # پنهان کردن ردیف‌های خالی
        for row in range(row_count, 10):
            self.recent_sales_table.hideRow(row)
    
    def update_sales_chart(self):
        """به‌روزرسانی نمودار فروش"""
        try:
            # استفاده از داده‌های روند ماهانه
            monthly_trends = self.sales_calculator.get_sales_trends('monthly')
            
            if not monthly_trends:
                return
            
            chart = QChart()
            chart.setTitle("📈 روند فروش ماهانه")
            chart.setTitleFont(QFont("B Nazanin", 12, QFont.Bold))
            chart.setAnimationOptions(QChart.SeriesAnimations)
            
            # سری فروش
            sales_series = QLineSeries()
            sales_series.setName("فروش کل")
            sales_series.setColor(QColor("#2ecc71"))
            
            # اضافه کردن نقاط
            for i, trend in enumerate(monthly_trends):
                sales = trend.get('total_sales', 0) or 0
                sales_series.append(i, sales / 1000000)  # تقسیم بر 1,000,000 برای نمایش به میلیون
            
            # اضافه کردن سری به نمودار
            chart.addSeries(sales_series)
            
            # محور X
            axis_x = QBarCategoryAxis()
            axis_x.setTitleText("ماه‌ها")
            periods = [trend.get('period', '')[-5:] for trend in monthly_trends]  # فقط ماه-سال
            axis_x.append(periods)
            chart.addAxis(axis_x, Qt.AlignBottom)
            sales_series.attachAxis(axis_x)
            
            # محور Y
            axis_y = QValueAxis()
            axis_y.setTitleText("فروش (میلیون تومان)")
            axis_y.setLabelFormat("%.0f")
            chart.addAxis(axis_y, Qt.AlignLeft)
            sales_series.attachAxis(axis_y)
            
            chart.legend().setVisible(True)
            chart.legend().setAlignment(Qt.AlignBottom)
            
            self.sales_chart_view.setChart(chart)
            
        except Exception as e:
            print(f"⚠️ خطا در ایجاد نمودار فروش: {e}")
    
    def update_products_tab(self):
        """به‌روزرسانی تب محصولات پرفروش"""
        top_products = self.sales_data.get('top_products', [])
        
        # به‌روزرسانی جدول محصولات
        self.update_top_products_table(top_products)
        
        # به‌روزرسانی نمودار محصولات
        self.update_products_chart(top_products)
    
    def update_top_products_table(self, products):
        """به‌روزرسانی جدول محصولات پرفروش"""
        row_count = len(products)
        self.top_products_table.setRowCount(row_count)
        
        for row, product in enumerate(products):
            # رتبه
            rank = row + 1
            
            # نام محصول
            product_name = product.get('product_name', '')
            
            # دسته
            category = product.get('category', '')
            
            # برند
            brand = product.get('brand', '')
            
            # تعداد فروش
            sale_count = product.get('sale_count', 0)
            
            # مبلغ فروش (تبدیل از ریال به تومان)
            sales_amount = (product.get('total_sales_amount', 0) or 0) / 10
            sales_formatted = f"{self.format_currency(sales_amount)} تومان"
            
            # سود تخمینی (تبدیل از ریال به تومان)
            estimated_profit = (product.get('estimated_profit', 0) or 0) / 10
            profit_formatted = f"{self.format_currency(estimated_profit)} تومان"
            
            # قرار دادن در جدول
            items = [
                str(rank),
                product_name,
                category,
                brand,
                str(sale_count),
                sales_formatted,
                profit_formatted
            ]
            
            for col, text in enumerate(items):
                item = QTableWidgetItem(str(text))
                item.setTextAlignment(Qt.AlignCenter)
                
                # رنگ‌بندی بر اساس رتبه
                if col == 0:  # ستون رتبه
                    if rank == 1:
                        item.setForeground(QColor("#f1c40f"))  # طلایی
                    elif rank == 2:
                        item.setForeground(QColor("#95a5a6"))  # نقرهای
                    elif rank == 3:
                        item.setForeground(QColor("#cd7f32"))  # برنزی
                
                # رنگ‌بندی مبلغ فروش
                elif col == 5:  # ستون مبلغ فروش
                    if sales_amount > 10000000:  # بیش از ۱۰ میلیون تومان
                        item.setForeground(QColor("#2ecc71"))
                    elif sales_amount > 5000000:  # بیش از ۵ میلیون تومان
                        item.setForeground(QColor("#f39c12"))
                    else:
                        item.setForeground(QColor("#e74c3c"))
                
                self.top_products_table.setItem(row, col, item)
        
        # پنهان کردن ردیف‌های خالی
        for row in range(row_count, 15):
            self.top_products_table.hideRow(row)
    
    def update_products_chart(self, products):
        """به‌روزرسانی نمودار توزیع فروش محصولات"""
        try:
            # گروه‌بندی محصولات بر اساس دسته
            categories = {}
            for product in products:
                category = product.get('category', 'سایر')
                sales_amount = product.get('total_sales_amount', 0) or 0
                
                if category in categories:
                    categories[category] += sales_amount
                else:
                    categories[category] = sales_amount
            
            if not categories:
                return
            
            chart = QChart()
            chart.setTitle("📊 توزیع فروش بر اساس دسته")
            chart.setTitleFont(QFont("B Nazanin", 12, QFont.Bold))
            chart.setAnimationOptions(QChart.SeriesAnimations)
            
            # سری دایره‌ای
            pie_series = QPieSeries()
            pie_series.setPieSize(0.7)
            
            # رنگ‌های مختلف برای دسته‌ها
            colors = {
                'لوازم نو': QColor("#3498db"),
                'لوازم دست دوم': QColor("#2ecc71"),
                'قطعات نو': QColor("#e74c3c"),
                'قطعات دست دوم': QColor("#f39c12"),
                'خدمات': QColor("#9b59b6"),
                'سایر': QColor("#34495e")
            }
            
            # اضافه کردن بخش‌ها
            total_sales = sum(categories.values())
            
            for category, sales in categories.items():
                percentage = (sales / total_sales * 100) if total_sales > 0 else 0
                
                slice = pie_series.append(
                    f"{category}\n{self.format_currency(sales / 10)} تومان ({percentage:.1f}%)", 
                    sales
                )
                slice.setColor(colors.get(category, QColor("#95a5a6")))
                
                # نمایش مقدار روی برش
                slice.setLabelVisible(True)
                slice.setLabelPosition(QPieSlice.LabelInsideNormal)
                slice.setLabelBrush(QColor("#FFFFFF"))
            
            chart.addSeries(pie_series)
            chart.legend().setVisible(True)
            chart.legend().setAlignment(Qt.AlignRight)
            
            self.products_chart_view.setChart(chart)
            
        except Exception as e:
            print(f"⚠️ خطا در ایجاد نمودار محصولات: {e}")
    
    def update_customers_tab(self):
        """به‌روزرسانی تب مشتریان برتر"""
        top_customers = self.sales_data.get('top_customers', [])
        
        # به‌روزرسانی جدول مشتریان
        self.update_top_customers_table(top_customers)
        
        # به‌روزرسانی کارت‌های تحلیل مشتریان
        self.update_customer_analysis_cards(top_customers)
    
    def update_top_customers_table(self, customers):
        """به‌روزرسانی جدول مشتریان برتر"""
        row_count = len(customers)
        self.top_customers_table.setRowCount(row_count)
        
        for row, customer in enumerate(customers):
            # رتبه
            rank = row + 1
            
            # نام مشتری
            customer_name = customer.get('customer_name', '')
            
            # موبایل
            mobile = customer.get('mobile', '')
            
            # تعداد خرید
            invoice_count = customer.get('invoice_count', 0)
            
            # مبلغ خرید (تبدیل از ریال به تومان)
            total_purchases = (customer.get('total_purchases', 0) or 0) / 10
            purchases_formatted = f"{self.format_currency(total_purchases)} تومان"
            
            # نوع مشتری
            customer_type = customer.get('customer_type', '')
            
            # امتیاز وفاداری
            loyalty_score = customer.get('loyalty_score', 0)
            
            # قرار دادن در جدول
            items = [
                str(rank),
                customer_name,
                mobile,
                str(invoice_count),
                purchases_formatted,
                customer_type,
                f"{loyalty_score:.0f}"
            ]
            
            for col, text in enumerate(items):
                item = QTableWidgetItem(str(text))
                item.setTextAlignment(Qt.AlignCenter)
                
                # رنگ‌بندی بر اساس رتبه
                if col == 0:  # ستون رتبه
                    if rank == 1:
                        item.setForeground(QColor("#f1c40f"))  # طلایی
                    elif rank == 2:
                        item.setForeground(QColor("#95a5a6"))  # نقرهای
                    elif rank == 3:
                        item.setForeground(QColor("#cd7f32"))  # برنزی
                
                # رنگ‌بندی نوع مشتری
                elif col == 5:  # ستون نوع مشتری
                    if 'VIP' in customer_type:
                        item.setForeground(QColor("#e74c3c"))
                    elif 'وفادار' in customer_type:
                        item.setForeground(QColor("#3498db"))
                    elif 'منظم' in customer_type:
                        item.setForeground(QColor("#2ecc71"))
                    elif 'جدید' in customer_type:
                        item.setForeground(QColor("#f39c12"))
                    else:
                        item.setForeground(QColor("#95a5a6"))
                
                # رنگ‌بندی امتیاز وفاداری
                elif col == 6:  # ستون امتیاز وفاداری
                    if loyalty_score >= 80:
                        item.setForeground(QColor("#2ecc71"))
                    elif loyalty_score >= 60:
                        item.setForeground(QColor("#f39c12"))
                    else:
                        item.setForeground(QColor("#e74c3c"))
                
                self.top_customers_table.setItem(row, col, item)
        
        # پنهان کردن ردیف‌های خالی
        for row in range(row_count, 12):
            self.top_customers_table.hideRow(row)
    
    def update_customer_analysis_cards(self, customers):
        """به‌روزرسانی کارت‌های تحلیل مشتریان"""
        if not customers:
            return
        
        # شمارش انواع مشتریان
        customer_types = {
            'VIP 🏆': 0,
            'وفادار 💎': 0,
            'منظم ⭐': 0,
            'جدید 🌱': 0,
            'غیرفعال ⏸️': 0
        }
        
        total_purchases = []
        
        for customer in customers:
            customer_type = customer.get('customer_type', '')
            purchases = customer.get('total_purchases', 0) or 0
            
            if customer_type in customer_types:
                customer_types[customer_type] += 1
            
            total_purchases.append(purchases)
        
        # محاسبه آمار
        avg_purchase = sum(total_purchases) / len(total_purchases) if total_purchases else 0
        max_purchase = max(total_purchases) if total_purchases else 0
        min_purchase = min(total_purchases) if total_purchases else 0
        
        # نرخ بازگشت (تعداد مشتریان با بیش از ۱ خرید)
        returning_customers = sum(1 for c in customers if (c.get('invoice_count', 0) or 0) > 1)
        return_rate = (returning_customers / len(customers) * 100) if customers else 0
        
        # به‌روزرسانی کارت‌ها (فرض می‌کنیم layout مشخص است)
        # این بخش نیاز به اتصال به ویجت‌های واقعی دارد
        print(f"📊 تحلیل مشتریان: {customer_types}")
    
    def update_profitability_tab(self):
        """به‌روزرسانی تب تحلیل سودآوری"""
        profitability = self.sales_data.get('profitability_analysis', {})
        comparison = self.sales_data.get('warehouse_comparison', [])
        
        # به‌روزرسانی کارت‌ها
        self.update_profitability_cards(profitability)
        
        # به‌روزرسانی نمودار سودآوری
        self.update_profitability_chart(profitability)
        
        # به‌روزرسانی جدول مقایسه انبارها
        self.update_warehouse_comparison_table(comparison)
    
    def update_profitability_cards(self, profitability):
        """به‌روزرسانی کارت‌های سودآوری"""
        total_profit = profitability.get('total_profit', 0) or 0
        total_sales = profitability.get('total_sales', 0) or 0
        overall_margin = profitability.get('overall_profit_margin', 0) or 0
        
        categories = profitability.get('categories', {})
        
        # به‌روزرسانی کارت‌ها
        self.update_stat_card(self.total_profit_card, f"{self.format_currency(total_profit / 10)} تومان")
        self.update_stat_card(self.profit_margin_card, f"{overall_margin:.1f}٪")
        
        # سود دسته‌ها
        new_appliances_profit = categories.get('new_appliances', {}).get('profit', 0) or 0
        used_appliances_profit = categories.get('used_appliances', {}).get('profit', 0) or 0
        new_parts_profit = categories.get('new_parts', {}).get('profit', 0) or 0
        used_parts_profit = categories.get('used_parts', {}).get('profit', 0) or 0
        services_profit = categories.get('services', {}).get('profit', 0) or 0
        
        self.update_stat_card(self.new_appliances_profit_card, f"{self.format_currency(new_appliances_profit / 10)} تومان")
        self.update_stat_card(self.used_appliances_profit_card, f"{self.format_currency(used_appliances_profit / 10)} تومان")
        self.update_stat_card(self.new_parts_profit_card, f"{self.format_currency(new_parts_profit / 10)} تومان")
        self.update_stat_card(self.used_parts_profit_card, f"{self.format_currency(used_parts_profit / 10)} تومان")
        self.update_stat_card(self.services_profit_card, f"{self.format_currency(services_profit / 10)} تومان")
        
        # بازگشت سرمایه (محاسبه ساده)
        investment = total_sales - total_profit  # سرمایه‌گذاری فرضی
        roi = (total_profit / investment * 100) if investment > 0 else 0
        self.update_stat_card(self.roi_card, f"{roi:.1f}٪")
    
    def update_profitability_chart(self, profitability):
        """به‌روزرسانی نمودار سودآوری"""
        try:
            categories = profitability.get('categories', {})
            
            if not categories:
                return
            
            chart = QChart()
            chart.setTitle("📊 سودآوری بر اساس دسته")
            chart.setTitleFont(QFont("B Nazanin", 12, QFont.Bold))
            chart.setAnimationOptions(QChart.SeriesAnimations)
            
            # سری میله‌ای برای سود
            bar_series = QBarSeries()
            
            # نام دسته‌ها
            category_names = ['لوازم نو', 'لوازم دست دوم', 'قطعات نو', 'قطعات دست دوم', 'خدمات']
            colors = [QColor("#3498db"), QColor("#2ecc71"), QColor("#e74c3c"), QColor("#f39c12"), QColor("#9b59b6")]
            
            for i, category_name in enumerate(category_names):
                # کلید مناسب برای دسترسی به داده‌ها
                key_map = {
                    'لوازم نو': 'new_appliances',
                    'لوازم دست دوم': 'used_appliances',
                    'قطعات نو': 'new_parts',
                    'قطعات دست دوم': 'used_parts',
                    'خدمات': 'services'
                }
                
                key = key_map.get(category_name)
                if key in categories:
                    profit = categories[key].get('profit', 0) or 0
                    
                    bar_set = QBarSet(category_name)
                    bar_set.append(profit / 1000000)  # تقسیم بر ۱,۰۰۰,۰۰۰ برای نمایش به میلیون
                    bar_set.setColor(colors[i])
                    bar_series.append(bar_set)
            
            chart.addSeries(bar_series)
            
            # محور X
            axis_x = QBarCategoryAxis()
            axis_x.append([''])
            chart.addAxis(axis_x, Qt.AlignBottom)
            bar_series.attachAxis(axis_x)
            
            # محور Y
            axis_y = QValueAxis()
            axis_y.setTitleText("سود (میلیون تومان)")
            axis_y.setLabelFormat("%.0f")
            chart.addAxis(axis_y, Qt.AlignLeft)
            bar_series.attachAxis(axis_y)
            
            chart.legend().setVisible(True)
            chart.legend().setAlignment(Qt.AlignBottom)
            
            self.profitability_chart_view.setChart(chart)
            
        except Exception as e:
            print(f"⚠️ خطا در ایجاد نمودار سودآوری: {e}")
    
    def update_warehouse_comparison_table(self, comparison):
        """به‌روزرسانی جدول مقایسه فروش انبارها"""
        row_count = len(comparison)
        self.warehouse_comparison_table.setRowCount(row_count)
        
        for row, warehouse in enumerate(comparison):
            # نام انبار
            warehouse_name = warehouse.get('warehouse', '')
            
            # تعداد فروش
            sale_count = warehouse.get('sale_count', 0)
            
            # فروش کل (تبدیل از ریال به تومان)
            total_sales = (warehouse.get('total_sales', 0) or 0) / 10
            sales_formatted = f"{self.format_currency(total_sales)} تومان"
            
            # سود تخمینی (تبدیل از ریال به تومان)
            estimated_profit = (warehouse.get('estimated_profit', 0) or 0) / 10
            profit_formatted = f"{self.format_currency(estimated_profit)} تومان"
            
            # حاشیه سود
            profit_margin = warehouse.get('profit_margin', 0) or 0
            margin_formatted = f"{profit_margin:.1f}٪"
            
            # میانگین ارزش فروش (تبدیل از ریال به تومان)
            avg_sale_value = (warehouse.get('avg_sale_value', 0) or 0) / 10
            avg_formatted = f"{self.format_currency(avg_sale_value)} تومان"
            
            # قرار دادن در جدول
            items = [
                warehouse_name,
                str(sale_count),
                sales_formatted,
                profit_formatted,
                margin_formatted,
                avg_formatted
            ]
            
            for col, text in enumerate(items):
                item = QTableWidgetItem(str(text))
                item.setTextAlignment(Qt.AlignCenter)
                
                # رنگ‌بندی حاشیه سود
                if col == 4:  # ستون حاشیه سود
                    if profit_margin >= 50:
                        item.setForeground(QColor("#2ecc71"))
                    elif profit_margin >= 30:
                        item.setForeground(QColor("#f39c12"))
                    else:
                        item.setForeground(QColor("#e74c3c"))
                
                self.warehouse_comparison_table.setItem(row, col, item)
        
        # پنهان کردن ردیف‌های خالی
        for row in range(row_count, 5):
            self.warehouse_comparison_table.hideRow(row)
    
    def update_trends_tab(self):
        """به‌روزرسانی تب روندهای فروش"""
        if not hasattr(self, 'trends_data') or not self.trends_data:
            return
        
        # به‌روزرسانی جدول روندها
        self.update_trends_table()
        
        # به‌روزرسانی نمودار روندها
        self.update_trends_chart()
    
    def update_trends_table(self):
        """به‌روزرسانی جدول روندهای فروش"""
        row_count = len(self.trends_data)
        self.trends_table.setRowCount(row_count)
        
        for row, trend in enumerate(self.trends_data):
            # دوره
            period = trend.get('period', '')
            
            # تعداد فاکتور
            invoice_count = trend.get('invoice_count', 0)
            
            # فروش کل (تبدیل از ریال به تومان)
            total_sales = (trend.get('total_sales', 0) or 0) / 10
            sales_formatted = f"{self.format_currency(total_sales)} تومان"
            
            # مشتریان منحصربفرد
            unique_customers = trend.get('unique_customers', 0)
            
            # میانگین فاکتور (تبدیل از ریال به تومان)
            avg_invoice_amount = (trend.get('avg_invoice_amount', 0) or 0) / 10
            avg_formatted = f"{self.format_currency(avg_invoice_amount)} تومان"
            
            # نرخ تکمیل پرداخت
            payment_completion_rate = trend.get('payment_completion_rate', 0) or 0
            rate_formatted = f"{payment_completion_rate:.1f}٪"
            
            # قرار دادن در جدول
            items = [
                period,
                str(invoice_count),
                sales_formatted,
                str(unique_customers),
                avg_formatted,
                rate_formatted
            ]
            
            for col, text in enumerate(items):
                item = QTableWidgetItem(str(text))
                item.setTextAlignment(Qt.AlignCenter)
                
                # رنگ‌بندی نرخ تکمیل پرداخت
                if col == 5:  # ستون نرخ تکمیل پرداخت
                    if payment_completion_rate >= 90:
                        item.setForeground(QColor("#2ecc71"))
                    elif payment_completion_rate >= 70:
                        item.setForeground(QColor("#f39c12"))
                    else:
                        item.setForeground(QColor("#e74c3c"))
                
                self.trends_table.setItem(row, col, item)
        
        # پنهان کردن ردیف‌های خالی
        for row in range(row_count, 12):
            self.trends_table.hideRow(row)
    
    def update_trends_chart(self):
        """به‌روزرسانی نمودار روندهای فروش"""
        try:
            if not self.trends_data:
                return
            
            chart = QChart()
            chart.setTitle("📈 روند فروش")
            chart.setTitleFont(QFont("B Nazanin", 12, QFont.Bold))
            chart.setAnimationOptions(QChart.SeriesAnimations)
            
            # سری فروش
            sales_series = QLineSeries()
            sales_series.setName("فروش کل")
            sales_series.setColor(QColor("#2ecc71"))
            
            # سری تعداد فاکتورها
            invoice_series = QLineSeries()
            invoice_series.setName("تعداد فاکتورها")
            invoice_series.setColor(QColor("#3498db"))
            
            # اضافه کردن نقاط
            for i, trend in enumerate(self.trends_data):
                sales = trend.get('total_sales', 0) or 0
                invoices = trend.get('invoice_count', 0) or 0
                
                sales_series.append(i, sales / 1000000)  # نمایش به میلیون تومان
                invoice_series.append(i, invoices)  # تعداد فاکتورها
            
            # اضافه کردن سری‌ها به نمودار
            chart.addSeries(sales_series)
            chart.addSeries(invoice_series)
            
            # محور X
            axis_x = QBarCategoryAxis()
            axis_x.setTitleText("دوره‌ها")
            periods = [trend.get('period', '') for trend in self.trends_data]
            axis_x.append(periods)
            chart.addAxis(axis_x, Qt.AlignBottom)
            sales_series.attachAxis(axis_x)
            invoice_series.attachAxis(axis_x)
            
            # محور Y اول (برای فروش)
            axis_y1 = QValueAxis()
            axis_y1.setTitleText("فروش (میلیون تومان)")
            axis_y1.setLabelFormat("%.0f")
            chart.addAxis(axis_y1, Qt.AlignLeft)
            sales_series.attachAxis(axis_y1)
            
            # محور Y دوم (برای تعداد فاکتورها)
            axis_y2 = QValueAxis()
            axis_y2.setTitleText("تعداد فاکتورها")
            chart.addAxis(axis_y2, Qt.AlignRight)
            invoice_series.attachAxis(axis_y2)
            
            chart.legend().setVisible(True)
            chart.legend().setAlignment(Qt.AlignBottom)
            
            self.trends_chart_view.setChart(chart)
            
        except Exception as e:
            print(f"⚠️ خطا در ایجاد نمودار روندها: {e}")
    
    def format_currency(self, amount):
        """فرمت کردن مبلغ به صورت جداکننده هزارگان"""
        return f"{amount:,.0f}".replace(",", "٬")