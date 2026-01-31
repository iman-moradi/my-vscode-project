# -*- coding: utf-8 -*-
"""
فرم گزارش مالی کامل
"""

import datetime
import jdatetime
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QPushButton, QFrame, QScrollArea,
    QTableWidget, QTableWidgetItem, QHeaderView,
    QComboBox, QLineEdit, QDateEdit, QGroupBox,
    QFormLayout, QSpinBox, QCheckBox, QTextEdit,
    QProgressBar, QTabWidget, QSplitter, QSizePolicy
)
from PySide6.QtCore import Qt, Signal, QDate, QTimer, QPointF
from PySide6.QtGui import QFont, QColor, QAction, QPainter
from PySide6.QtCharts import (
    QChart, QChartView, QLineSeries, QBarSeries, QBarSet, QPieSeries,
    QPieSlice, QBarCategoryAxis, QValueAxis
)

# توابع تاریخ شمسی (کمکی)
def get_current_jalali():
    """دریافت تاریخ شمسی فعلی"""
    now = jdatetime.datetime.now()
    return now.strftime('%Y/%m/%d %H:%M:%S')

def gregorian_to_jalali(gregorian_date):
    """تبدیل تاریخ میلادی به شمسی"""
    if not gregorian_date:
        return ""
    
    try:
        if isinstance(gregorian_date, str):
            # حذف زمان اگر وجود دارد
            if ' ' in gregorian_date:
                gregorian_date = gregorian_date.split(' ')[0]
            
            # تبدیل رشته به تاریخ میلادی
            try:
                g_date = datetime.datetime.strptime(gregorian_date, '%Y-%m-%d')
            except:
                try:
                    g_date = datetime.datetime.strptime(gregorian_date, '%Y/%m/%d')
                except:
                    return str(gregorian_date)
        else:
            # اگر از قبل شیء datetime است
            g_date = gregorian_date
        
        # تبدیل به تاریخ شمسی
        j_date = jdatetime.date.fromgregorian(date=g_date.date())
        return j_date.strftime('%Y/%m/%d')
    except Exception as e:
        print(f"⚠️ خطا در تبدیل تاریخ {gregorian_date}: {e}")
        return str(gregorian_date)

def jalali_to_gregorian(jalali_date_str, format_str='%Y-%m-%d'):
    """تبدیل تاریخ شمسی به میلادی"""
    try:
        year, month, day = map(int, jalali_date_str.split('/'))
        jalali_date = jdatetime.date(year, month, day)
        gregorian_date = jalali_date.togregorian()
        return gregorian_date.strftime(format_str)
    except Exception as e:
        print(f"⚠️ خطا در تبدیل تاریخ شمسی {jalali_date_str}: {e}")
        return None

# کلاس FinancialCalculator ساده‌شده
class FinancialCalculator:
    """ماشین حساب مالی ساده"""
    
    def __init__(self, data_manager):
        self.data_manager = data_manager
    
    def get_financial_summary(self, start_date, end_date):
        """خلاصه مالی نمونه"""
        return {
            'total_income': 250000000,
            'total_expense': 180000000,
            'net_profit': 70000000,
            'profit_margin': 28.0,
            'transaction_count': 145,
            'daily_avg_income': 8333333,
            'max_daily_income': 15000000,
            'min_daily_expense': 2000000
        }
    
    def get_daily_financial_data(self, start_date, end_date):
        """داده‌های روزانه نمونه"""
        daily_data = []
        for i in range(15):
            daily_data.append({
                'date': f"1404/11/{10+i:02d}",
                'income': 5000000 + i * 1000000,
                'expense': 3000000 + i * 500000,
                'profit': 2000000 + i * 500000
            })
        return daily_data
    
    def get_expense_distribution(self, start_date, end_date):
        """توزیع هزینه‌ها نمونه"""
        return [
            {'category': 'حقوق', 'total_amount': 40000000, 'percentage': 40},
            {'category': 'اجاره', 'total_amount': 20000000, 'percentage': 20},
            {'category': 'تبلیغات', 'total_amount': 15000000, 'percentage': 15},
            {'category': 'حمل و نقل', 'total_amount': 10000000, 'percentage': 10},
            {'category': 'سایر', 'total_amount': 15000000, 'percentage': 15}
        ]
    
    def get_account_balances(self):
        """موجودی حساب‌ها نمونه"""
        return [
            {'id': 1, 'account_name': 'صندوق', 'current_balance_toman': 5000000},
            {'id': 2, 'account_name': 'بانک ملت', 'current_balance_toman': 25000000},
            {'id': 3, 'account_name': 'بانک ملی', 'current_balance_toman': 18000000}
        ]



class FinancialReportForm(QWidget):
    """فرم گزارش مالی کامل"""
    
    report_updated = Signal(dict)  # سیگنال بروزرسانی گزارش
    
    def __init__(self, data_manager):
        super().__init__()
        self.data_manager = data_manager
        self.financial_calculator = FinancialCalculator(data_manager)  # افزودن ماشین حساب مالی
        self.financial_data = {}
        self.chart_data = {}
        
        # تنظیمات اولیه
        self.init_ui()
        
        # بارگذاری اولیه داده‌ها
        QTimer.singleShot(100, self.load_financial_data)
    
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
        """ایجاد نوار ابزار فیلترهای گزارش مالی"""
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
        
        # انتخاب دوره زمانی
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
            "شش ماهه",
            "امسال",
            "سال گذشته",
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
        
        # دکمه اعمال فیلتر
        self.btn_apply_filter = QPushButton("✅ اعمال فیلتر")
        self.btn_apply_filter.clicked.connect(self.apply_filters)
        filter_layout.addWidget(self.btn_apply_filter, 0, 6)
        
        # دکمه بازنشانی
        self.btn_reset = QPushButton("🔄 بازنشانی")
        self.btn_reset.clicked.connect(self.reset_filters)
        filter_layout.addWidget(self.btn_reset, 0, 7)
        
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
        self.create_summary_tab()
        self.create_charts_tab()
        self.create_transactions_tab()
        self.create_accounts_tab()
        self.create_profit_tab()
        
        parent_layout.addWidget(self.tab_widget, 1)  # stretch factor = 1
    
    def create_summary_tab(self):
        """ایجاد تب خلاصه مالی"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # هدر تب
        header_label = QLabel("💰 خلاصه وضعیت مالی")
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
        
        # کارت‌های خلاصه مالی
        self.create_summary_cards(layout)
        
        # جدول جزئیات
        self.create_summary_table(layout)
        
        self.tab_widget.addTab(tab, "💰 خلاصه")
    
    def create_summary_cards(self, parent_layout):
        """ایجاد کارت‌های خلاصه مالی"""
        # استفاده از Grid Layout برای چیدمان کارت‌ها
        cards_frame = QFrame()
        cards_layout = QGridLayout(cards_frame)
        cards_layout.setSpacing(15)
        
        # کارت درآمد کل
        self.income_card = self.create_summary_card("درآمد کل", "۰ تومان", "#2ecc71", "💰")
        cards_layout.addWidget(self.income_card, 0, 0)
        
        # کارت هزینه کل
        self.expense_card = self.create_summary_card("هزینه کل", "۰ تومان", "#e74c3c", "💸")
        cards_layout.addWidget(self.expense_card, 0, 1)
        
        # کارت سود خالص
        self.profit_card = self.create_summary_card("سود خالص", "۰ تومان", "#3498db", "📈")
        cards_layout.addWidget(self.profit_card, 0, 2)
        
        # کارت حاشیه سود
        self.margin_card = self.create_summary_card("حاشیه سود", "۰٪", "#9b59b6", "📊")
        cards_layout.addWidget(self.margin_card, 0, 3)
        
        # کارت تعداد تراکنش‌ها
        self.transactions_card = self.create_summary_card("تعداد تراکنش‌ها", "۰", "#f39c12", "📋")
        cards_layout.addWidget(self.transactions_card, 1, 0)
        
        # کارت میانگین درآمد روزانه
        self.avg_income_card = self.create_summary_card("میانگین درآمد روزانه", "۰ تومان", "#1abc9c", "📅")
        cards_layout.addWidget(self.avg_income_card, 1, 1)
        
        # کارت بیشترین درآمد
        self.max_income_card = self.create_summary_card("بیشترین درآمد روزانه", "۰ تومان", "#e67e22", "🏆")
        cards_layout.addWidget(self.max_income_card, 1, 2)
        
        # کارت کمترین هزینه
        self.min_expense_card = self.create_summary_card("کمترین هزینه روزانه", "۰ تومان", "#34495e", "📉")
        cards_layout.addWidget(self.min_expense_card, 1, 3)
        
        parent_layout.addWidget(cards_frame)
    
    def create_summary_card(self, title, value, color, icon):
        """ایجاد یک کارت خلاصه مالی"""
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
                font-size: 12pt;
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
                font-size: 16pt;
                font-weight: bold;
                text-align: center;
                padding: 10px 0;
            }
        """)
        layout.addWidget(value_label)
        
        # خط جداکننده
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setStyleSheet(f"background-color: {color};")
        layout.addWidget(separator)
        
        # توضیح
        desc_label = QLabel("کلیک برای جزئیات بیشتر")
        desc_label.setStyleSheet("""
            QLabel {
                color: #bdc3c7;
                font-size: 9pt;
                text-align: center;
            }
        """)
        layout.addWidget(desc_label)
        
        return card
    
    def create_summary_table(self, parent_layout):
        """ایجاد جدول خلاصه مالی"""
        group = QGroupBox("📊 جزئیات مالی به تفکیک روز")
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
        
        # ایجاد جدول
        self.summary_table = QTableWidget(15, 5)
        self.summary_table.setStyleSheet("""
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
        headers = ["تاریخ", "درآمد", "هزینه", "سود", "حاشیه سود"]
        self.summary_table.setHorizontalHeaderLabels(headers)
        
        # تنظیمات ستون‌ها
        header = self.summary_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # تاریخ
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)  # درآمد
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)  # هزینه
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)  # سود
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)  # حاشیه سود
        
        # تنظیم ارتفاع ردیف‌ها
        for i in range(15):
            self.summary_table.setRowHeight(i, 35)
        
        layout.addWidget(self.summary_table)
        parent_layout.addWidget(group)
    
    def create_charts_tab(self):
        """ایجاد تب نمودارهای مالی"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # هدر تب
        header_label = QLabel("📈 نمودارهای تحلیلی مالی")
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
        
        # استفاده از Splitter برای تقسیم صفحه
        splitter = QSplitter(Qt.Vertical)
        
        # نمودار درآمد و هزینه (خطی)
        self.income_expense_chart = self.create_line_chart()
        splitter.addWidget(self.income_expense_chart)
        
        # نمودار توزیع هزینه‌ها (دایره‌ای)
        self.expense_distribution_chart = self.create_pie_chart()
        splitter.addWidget(self.expense_distribution_chart)
        
        # تنظیمات Splitter
        splitter.setSizes([400, 300])
        layout.addWidget(splitter)
        
        self.tab_widget.addTab(tab, "📈 نمودارها")
    
    def create_line_chart(self):
        """ایجاد نمودار خطی برای درآمد و هزینه"""
        chart_view = QChartView()
        chart_view.setRenderHint(QPainter.Antialiasing)
        
        chart = QChart()
        chart.setTitle("📊 روند درآمد و هزینه")
        chart.setTitleFont(QFont("B Nazanin", 12, QFont.Bold))
        chart.setAnimationOptions(QChart.SeriesAnimations)
        
        chart_view.setChart(chart)
        chart_view.setStyleSheet("""
            QChartView {
                background-color: #111111;
                border-radius: 8px;
                border: 1px solid #444;
            }
        """)
        
        return chart_view
    
    def create_pie_chart(self):
        """ایجاد نمودار دایره‌ای برای توزیع هزینه‌ها"""
        chart_view = QChartView()
        chart_view.setRenderHint(QPainter.Antialiasing)
        
        chart = QChart()
        chart.setTitle("🥧 توزیع هزینه‌ها")
        chart.setTitleFont(QFont("B Nazanin", 12, QFont.Bold))
        chart.setAnimationOptions(QChart.SeriesAnimations)
        
        chart_view.setChart(chart)
        chart_view.setStyleSheet("""
            QChartView {
                background-color: #111111;
                border-radius: 8px;
                border: 1px solid #444;
            }
        """)
        
        return chart_view
    
    def create_transactions_tab(self):
        """ایجاد تب تراکنش‌های مالی"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # هدر تب
        header_label = QLabel("💳 تراکنش‌های مالی")
        header_label.setStyleSheet("""
            QLabel {
                color: #f39c12;
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
        
        # ایجاد جدول تراکنش‌ها
        self.create_transactions_table(layout)
        
        self.tab_widget.addTab(tab, "💳 تراکنش‌ها")
    
    def create_transactions_table(self, parent_layout):
        """ایجاد جدول تراکنش‌های مالی"""
        group = QGroupBox("📋 لیست تراکنش‌های مالی")
        group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #f39c12;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 15px;
                color: #f39c12;
                font-size: 12pt;
            }
        """)
        
        layout = QVBoxLayout(group)
        
        # ایجاد جدول با 20 ردیف
        self.transactions_table = QTableWidget(20, 7)
        
        # تنظیم ارتفاع ردیف‌ها
        for i in range(20):
            self.transactions_table.setRowHeight(i, 35)
        
        self.transactions_table.setStyleSheet("""
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
        headers = ["تاریخ", "نوع", "شرح", "حساب مبدا", "حساب مقصد", "مبلغ", "وضعیت"]
        self.transactions_table.setHorizontalHeaderLabels(headers)
        
        # تنظیمات ستون‌ها
        header = self.transactions_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # تاریخ
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)  # نوع
        header.setSectionResizeMode(2, QHeaderView.Stretch)           # شرح
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)  # حساب مبدا
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)  # حساب مقصد
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)  # مبلغ
        header.setSectionResizeMode(6, QHeaderView.ResizeToContents)  # وضعیت
        
        layout.addWidget(self.transactions_table)
        parent_layout.addWidget(group)
    
    def create_accounts_tab(self):
        """ایجاد تب وضعیت حساب‌ها"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # هدر تب
        header_label = QLabel("🏦 وضعیت حساب‌های بانکی")
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
        
        # ایجاد جدول حساب‌ها
        self.create_accounts_table(layout)
        
        self.tab_widget.addTab(tab, "🏦 حساب‌ها")
    
    def create_accounts_table(self, parent_layout):
        """ایجاد جدول وضعیت حساب‌ها"""
        group = QGroupBox("💰 موجودی حساب‌های بانکی و نقدی")
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
        self.accounts_table = QTableWidget(10, 5)
        
        # تنظیم ارتفاع ردیف‌ها
        for i in range(10):
            self.accounts_table.setRowHeight(i, 40)
        
        self.accounts_table.setStyleSheet("""
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
        headers = ["نام حساب", "شماره حساب", "نوع حساب", "موجودی فعلی", "آخرین تراکنش"]
        self.accounts_table.setHorizontalHeaderLabels(headers)
        
        # تنظیمات ستون‌ها
        header = self.accounts_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)           # نام حساب
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)  # شماره حساب
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)  # نوع حساب
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)  # موجودی فعلی
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)  # آخرین تراکنش
        
        layout.addWidget(self.accounts_table)
        parent_layout.addWidget(group)
    
    def create_profit_tab(self):
        """ایجاد تب تحلیل سود"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # هدر تب
        header_label = QLabel("📊 تحلیل سودآوری و کارایی")
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
        
        # کارت‌های تحلیل سود
        self.create_profit_analysis_cards(layout)
        
        # نمودار سود ماهانه
        profit_chart_group = QGroupBox("📈 نمودار سود ماهانه")
        profit_chart_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #1abc9c;
                border-radius: 8px;
                margin-top: 15px;
                padding-top: 15px;
                color: #1abc9c;
                font-size: 12pt;
            }
        """)
        
        profit_layout = QVBoxLayout(profit_chart_group)
        self.profit_chart_view = QChartView()
        self.profit_chart_view.setRenderHint(QPainter.Antialiasing)
        self.profit_chart_view.setStyleSheet("""
            QChartView {
                background-color: #111111;
                border-radius: 8px;
                border: 1px solid #444;
                min-height: 300px;
            }
        """)
        profit_layout.addWidget(self.profit_chart_view)
        layout.addWidget(profit_chart_group)
        
        self.tab_widget.addTab(tab, "📊 تحلیل سود")
    
    def create_profit_analysis_cards(self, parent_layout):
        """ایجاد کارت‌های تحلیل سود"""
        cards_frame = QFrame()
        cards_layout = QGridLayout(cards_frame)
        cards_layout.setSpacing(10)
        
        # کارت‌های تحلیل
        analysis_cards = [
            ("💰 سود خالص ماه جاری", "۰ تومان", "#2ecc71", self.create_profit_card),
            ("📅 میانگین سود روزانه", "۰ تومان", "#3498db", self.create_profit_card),
            ("📈 بیشترین سود روزانه", "۰ تومان", "#9b59b6", self.create_profit_card),
            ("📉 کمترین سود روزانه", "۰ تومان", "#e74c3c", self.create_profit_card),
            ("📊 حاشیه سود متوسط", "۰٪", "#f39c12", self.create_profit_card),
            ("⚡ نرخ بازگشت سرمایه", "۰٪", "#1abc9c", self.create_profit_card),
            ("📆 روزهای سودآور", "۰ روز", "#34495e", self.create_profit_card),
            ("💼 بهره‌وری نیروی کار", "۰ تومان/روز", "#e67e22", self.create_profit_card)
        ]
        
        for i, (title, value, color, creator) in enumerate(analysis_cards):
            row = i // 4
            col = i % 4
            card = creator(title, value, color)
            cards_layout.addWidget(card, row, col)
        
        parent_layout.addWidget(cards_frame)
    
    def create_profit_card(self, title, value, color):
        """ایجاد یک کارت تحلیل سود"""
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background-color: {color}15;
                border: 2px solid {color};
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
                font-size: 14pt;
                font-weight: bold;
                text-align: center;
                padding: 8px 0;
            }
        """)
        layout.addWidget(value_label)
        
        return card
    
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
        self.status_label = QLabel("✅ در حال بارگذاری داده‌های مالی...")
        
        # تعداد تراکنش‌ها
        self.transactions_count_label = QLabel("تعداد تراکنش‌ها: ۰")
        
        # آخرین بروزرسانی
        self.last_update_label = QLabel("آخرین بروزرسانی: --:--")
        
        status_layout.addWidget(self.status_label, 5)
        status_layout.addWidget(self.transactions_count_label, 3)
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
        QTimer.singleShot(100, self.load_financial_data)
    
    def reset_filters(self):
        """بازنشانی فیلترها"""
        self.period_combo.setCurrentIndex(0)  # امروز
        self.start_date_edit.setDate(QDate.currentDate().addDays(-30))
        self.end_date_edit.setDate(QDate.currentDate())
        self.apply_filters()
    
    def load_financial_data(self):
        """بارگذاری داده‌های مالی واقعی از دیتابیس"""
        try:
            self.status_label.setText("📊 در حال دریافت داده‌های مالی از دیتابیس...")
            
            # دریافت تاریخ‌های انتخاب شده
            start_date = self.start_date_edit.date().toString("yyyy-MM-dd")
            end_date = self.end_date_edit.date().toString("yyyy-MM-dd")
            
            # دریافت خلاصه مالی
            self.financial_data = self.financial_calculator.get_financial_summary(start_date, end_date)
            
            # دریافت داده‌های روزانه
            daily_data = self.financial_calculator.get_daily_financial_data(start_date, end_date)
            
            # دریافت توزیع هزینه‌ها
            expense_distribution = self.financial_calculator.get_expense_distribution(start_date, end_date)
            
            # ذخیره داده‌های نمودار
            self.chart_data = {
                "daily_data": daily_data,
                "expense_distribution": expense_distribution
            }
            
            # دریافت حساب‌ها
            self.accounts_list = self.financial_calculator.get_account_balances()
            
            # دریافت تراکنش‌ها
            self.load_real_transactions(start_date, end_date)
            
            # به‌روزرسانی UI
            self.update_financial_summary()
            self.update_transactions_table()
            self.update_accounts_table()
            self.update_charts()
            
            self.status_label.setText("✅ داده‌های مالی با موفقیت بارگذاری شدند")
            self.transactions_count_label.setText(f"تعداد تراکنش‌ها: {self.financial_data.get('transaction_count', 0)}")
            self.last_update_label.setText(f"آخرین بروزرسانی: {get_current_jalali()}")
            
            # ارسال سیگنال بروزرسانی
            self.report_updated.emit(self.financial_data)
            
        except Exception as e:
            self.status_label.setText(f"❌ خطا در بارگذاری داده‌ها: {str(e)}")
            print(f"خطا در load_financial_data: {e}")
            # در صورت خطا، از داده‌های نمونه استفاده کن
            self.load_sample_financial_data()

    def load_real_transactions(self, start_date, end_date):
        """بارگذاری تراکنش‌های واقعی از دیتابیس"""
        try:
            # تبدیل تاریخ‌های شمسی به میلادی
            start_greg = jalali_to_gregorian(start_date, "%Y-%m-%d")
            end_greg = jalali_to_gregorian(end_date, "%Y-%m-%d")
            
            # دریافت تراکنش‌های حسابداری
            query = """
            SELECT 
                at.id,
                at.transaction_date,
                at.transaction_type,
                at.amount,
                at.description,
                a1.account_name as from_account_name,
                a2.account_name as to_account_name,
                at.reference_type,
                at.reference_id
            FROM AccountingTransactions at
            LEFT JOIN Accounts a1 ON at.from_account_id = a1.id
            LEFT JOIN Accounts a2 ON at.to_account_id = a2.id
            WHERE DATE(at.transaction_date) BETWEEN ? AND ?
            ORDER BY at.transaction_date DESC
            LIMIT 50
            """
            
            self.transactions_list = self.data_manager.db.fetch_all(query, (start_greg, end_greg))
            
            # دریافت فاکتورها
            invoice_query = """
            SELECT 
                i.id,
                i.invoice_date,
                'فاکتور' as transaction_type,
                i.total as amount,
                CONCAT('فاکتور ', i.invoice_number, ' - ', p.full_name) as description,
                '' as from_account_name,
                '' as to_account_name,
                'فاکتور' as reference_type,
                i.id as reference_id
            FROM Invoices i
            LEFT JOIN Persons p ON i.customer_id = p.id
            WHERE DATE(i.invoice_date) BETWEEN ? AND ?
            AND i.payment_status IN ('پرداخت شده', 'نقدی')
            ORDER BY i.invoice_date DESC
            LIMIT 50
            """
            
            invoices = self.data_manager.db.fetch_all(invoice_query, (start_greg, end_greg))
            
            # ترکیب تراکنش‌ها و فاکتورها
            self.transactions_list.extend(invoices)
            
            # مرتب‌سازی بر اساس تاریخ
            self.transactions_list.sort(key=lambda x: x.get('transaction_date', ''), reverse=True)
            
            print(f"✅ {len(self.transactions_list)} تراکنش واقعی بارگذاری شد")
            
        except Exception as e:
            print(f"❌ خطا در بارگذاری تراکنش‌ها: {e}")
            self.transactions_list = []
    
    def update_transactions_table(self):
        """به‌روزرسانی جدول تراکنش‌ها با داده‌های واقعی"""
        if not hasattr(self, 'transactions_list') or not self.transactions_list:
            print("⚠️ لیست تراکنش‌ها خالی است")
            return
        
        row_count = len(self.transactions_list)
        self.transactions_table.setRowCount(row_count)
        
        for row, trans in enumerate(self.transactions_list):
            # تاریخ تراکنش
            trans_date = trans.get('transaction_date', '')
            date_shamsi = gregorian_to_jalali(trans_date) if trans_date else ''
            
            # نوع تراکنش
            trans_type = trans.get('transaction_type', '')
            
            # شرح
            description = trans.get('description', '')
            
            # حساب مبدا و مقصد
            from_account = trans.get('from_account_name', '')
            to_account = trans.get('to_account_name', '')
            
            # مبلغ (تبدیل از ریال به تومان)
            amount_rial = trans.get('amount', 0)
            amount_toman = amount_rial / 10
            amount_formatted = f"{self.format_currency(amount_toman)} تومان"
            
            # وضعیت
            status = "تکمیل شده"
            
            # قرار دادن در جدول
            items = [
                date_shamsi,
                trans_type,
                description[:50] + "..." if len(description) > 50 else description,
                from_account,
                to_account,
                amount_formatted,
                status
            ]
            
            for col, text in enumerate(items):
                item = QTableWidgetItem(str(text))
                item.setTextAlignment(Qt.AlignCenter)
                
                # رنگ‌بندی نوع تراکنش
                if col == 1:  # ستون نوع
                    if trans_type in ['دریافت', 'فاکتور', 'درآمد']:
                        item.setForeground(QColor("#2ecc71"))
                        item.setToolTip("درآمد")
                    elif trans_type in ['پرداخت', 'هزینه']:
                        item.setForeground(QColor("#e74c3c"))
                        item.setToolTip("هزینه")
                    elif trans_type == 'انتقال':
                        item.setForeground(QColor("#3498db"))
                        item.setToolTip("انتقال بین حساب‌ها")
                    else:
                        item.setForeground(QColor("#f39c12"))
                        item.setToolTip(trans_type)
                
                # رنگ‌بندی مبلغ
                elif col == 5:  # ستون مبلغ
                    if trans_type in ['دریافت', 'فاکتور', 'درآمد']:
                        item.setForeground(QColor("#2ecc71"))
                    elif trans_type in ['پرداخت', 'هزینه']:
                        item.setForeground(QColor("#e74c3c"))
                
                self.transactions_table.setItem(row, col, item)
        
        # پنهان کردن ردیف‌های خالی
        for row in range(row_count, 20):
            self.transactions_table.hideRow(row)
        
        print(f"✅ جدول تراکنش‌ها با {row_count} ردیف بروزرسانی شد")

    def update_accounts_table(self):
        """به‌روزرسانی جدول حساب‌ها با داده‌های واقعی"""
        if not hasattr(self, 'accounts_list') or not self.accounts_list:
            print("⚠️ لیست حساب‌ها خالی است")
            return
        
        row_count = len(self.accounts_list)
        self.accounts_table.setRowCount(row_count)
        
        for row, account in enumerate(self.accounts_list):
            # نام حساب
            account_name = account.get('account_name', '')
            
            # شماره حساب
            account_number = account.get('account_number', 'بدون شماره')
            
            # نوع حساب
            account_type = account.get('account_type', 'نامشخص')
            
            # موجودی فعلی
            balance_toman = account.get('current_balance_toman', 0)
            balance_formatted = f"{self.format_currency(balance_toman)} تومان"
            
            # دریافت تاریخ آخرین تراکنش
            last_transaction = self.get_last_transaction_for_account(account['id'])
            last_trans_date = gregorian_to_jalali(last_transaction) if last_transaction else 'بدون تراکنش'
            
            # قرار دادن در جدول
            items = [
                account_name,
                account_number,
                account_type,
                balance_formatted,
                last_trans_date
            ]
            
            for col, text in enumerate(items):
                item = QTableWidgetItem(str(text))
                item.setTextAlignment(Qt.AlignCenter)
                
                # رنگ‌بندی موجودی
                if col == 3:  # ستون موجودی
                    if balance_toman > 10000000:  # بیشتر از ۱۰ میلیون تومان
                        item.setForeground(QColor("#2ecc71"))
                    elif balance_toman > 1000000:  # بیشتر از ۱ میلیون تومان
                        item.setForeground(QColor("#f39c12"))
                    else:
                        item.setForeground(QColor("#e74c3c"))
                
                self.accounts_table.setItem(row, col, item)
        
        # پنهان کردن ردیف‌های خالی
        for row in range(row_count, 10):
            self.accounts_table.hideRow(row)
        
        print(f"✅ جدول حساب‌ها با {row_count} حساب بروزرسانی شد")
    
    def get_last_transaction_for_account(self, account_id):
        """دریافت تاریخ آخرین تراکنش یک حساب"""
        try:
            query = """
            SELECT MAX(transaction_date) as last_date
            FROM AccountingTransactions
            WHERE from_account_id = ? OR to_account_id = ?
            """
            
            result = self.data_manager.db.fetch_one(query, (account_id, account_id))
            return result.get('last_date') if result else None
            
        except Exception as e:
            print(f"⚠️ خطا در دریافت آخرین تراکنش: {e}")
            return None
    
    def update_charts(self):
        """به‌روزرسانی نمودارها با داده‌های واقعی"""
        try:
            # ۱. نمودار درآمد و هزینه (خطی)
            self.update_income_expense_chart()
            
            # ۲. نمودار توزیع هزینه‌ها (دایره‌ای)
            self.update_expense_distribution_chart()
            
            # ۳. نمودار سود ماهانه (میله‌ای)
            self.update_profit_chart()
            
            print("✅ نمودارها با داده‌های واقعی بروزرسانی شدند")
            
        except Exception as e:
            print(f"❌ خطا در بروزرسانی نمودارها: {e}")
    
    def update_income_expense_chart(self):
        """به‌روزرسانی نمودار خطی درآمد و هزینه"""
        if not self.chart_data.get('daily_data'):
            return
        
        try:
            chart = self.income_expense_chart.chart()
            chart.removeAllSeries()  # حذف سری‌های قبلی
            
            # سری درآمد
            income_series = QLineSeries()
            income_series.setName("📈 درآمد")
            income_series.setColor(QColor("#2ecc71"))
            
            # سری هزینه
            expense_series = QLineSeries()
            expense_series.setName("📉 هزینه")
            expense_series.setColor(QColor("#e74c3c"))
            
            # اضافه کردن نقاط
            for i, data in enumerate(self.chart_data['daily_data'][:10]):  # 10 روز اخیر
                income_series.append(i, data['income'] / 1000000)  # تقسیم بر 1,000,000 برای نمایش به میلیون
                expense_series.append(i, data['expense'] / 1000000)
            
            # اضافه کردن سری‌ها به نمودار
            chart.addSeries(income_series)
            chart.addSeries(expense_series)
            
            # محور X
            axis_x = QBarCategoryAxis()
            axis_x.setTitleText("روزها")
            dates = [data['date'].split('/')[-1] for data in self.chart_data['daily_data'][:10]]
            axis_x.append(dates)
            chart.addAxis(axis_x, Qt.AlignBottom)
            income_series.attachAxis(axis_x)
            expense_series.attachAxis(axis_x)
            
            # محور Y
            axis_y = QValueAxis()
            axis_y.setTitleText("مبلغ (میلیون تومان)")
            axis_y.setLabelFormat("%.1f")
            chart.addAxis(axis_y, Qt.AlignLeft)
            income_series.attachAxis(axis_y)
            expense_series.attachAxis(axis_y)
            
            chart.setTitle(f"📊 روند درآمد و هزینه - {len(self.chart_data['daily_data'])} روز اخیر")
            chart.legend().setVisible(True)
            chart.legend().setAlignment(Qt.AlignBottom)
            
        except Exception as e:
            print(f"⚠️ خطا در ایجاد نمودار خطی: {e}")
    
    def update_expense_distribution_chart(self):
        """به‌روزرسانی نمودار دایره‌ای توزیع هزینه‌ها"""
        if not self.chart_data.get('expense_distribution'):
            return
        
        try:
            chart = self.expense_distribution_chart.chart()
            chart.removeAllSeries()
            
            # سری دایره‌ای
            pie_series = QPieSeries()
            pie_series.setPieSize(0.7)
            
            # رنگ‌های مختلف برای بخش‌ها
            colors = [
                QColor("#e74c3c"),  # قرمز
                QColor("#3498db"),  # آبی
                QColor("#2ecc71"),  # سبز
                QColor("#f39c12"),  # نارنجی
                QColor("#9b59b6"),  # بنفش
                QColor("#1abc9c"),  # فیروزه‌ای
                QColor("#34495e"),  # خاکستری تیره
            ]
            
            # اضافه کردن بخش‌ها
            for i, item in enumerate(self.chart_data['expense_distribution']):
                category = item.get('category', 'سایر')
                amount = item.get('total_amount', 0) / 10  # تبدیل به تومان
                percentage = item.get('percentage', 0)
                
                if amount > 0:
                    slice = pie_series.append(
                        f"{category}\n{self.format_currency(amount)} تومان ({percentage:.1f}%)", 
                        amount
                    )
                    slice.setColor(colors[i % len(colors)])
                    
                    # نمایش مقدار روی برش
                    slice.setLabelVisible(True)
                    slice.setLabelPosition(QPieSlice.LabelInsideNormal)
                    slice.setLabelBrush(QColor("#FFFFFF"))
            
            chart.addSeries(pie_series)
            chart.setTitle("🥧 توزیع هزینه‌ها بر اساس دسته")
            chart.legend().setVisible(True)
            chart.legend().setAlignment(Qt.AlignRight)
            
        except Exception as e:
            print(f"⚠️ خطا در ایجاد نمودار دایره‌ای: {e}")
    
    def update_profit_chart(self):
        """به‌روزرسانی نمودار سود ماهانه"""
        try:
            # دریافت سود ۶ ماه اخیر
            profit_data = self.get_monthly_profit_data()
            
            chart = self.profit_chart_view.chart()
            chart.removeAllSeries()
            
            # سری میله‌ای
            bar_series = QBarSeries()
            
            # ست میله‌ها
            bar_set = QBarSet("💰 سود ماهانه")
            bar_set.setColor(QColor("#2ecc71"))
            
            # اضافه کردن مقادیر
            for data in profit_data:
                bar_set.append(data['profit'] / 1000000)  # نمایش به میلیون تومان
            
            bar_series.append(bar_set)
            chart.addSeries(bar_series)
            
            # محور X
            axis_x = QBarCategoryAxis()
            months = [data['month_name'] for data in profit_data]
            axis_x.append(months)
            chart.addAxis(axis_x, Qt.AlignBottom)
            bar_series.attachAxis(axis_x)
            
            # محور Y
            axis_y = QValueAxis()
            axis_y.setTitleText("سود (میلیون تومان)")
            axis_y.setLabelFormat("%.0f")
            chart.addAxis(axis_y, Qt.AlignLeft)
            bar_series.attachAxis(axis_y)
            
            chart.setTitle("📈 سود ماهانه (۶ ماه اخیر)")
            chart.legend().setVisible(True)
            chart.legend().setAlignment(Qt.AlignBottom)
            
        except Exception as e:
            print(f"⚠️ خطا در ایجاد نمودار سود: {e}")
    
    def get_monthly_profit_data(self):
        """دریافت داده‌های سود ماهانه"""
        try:
            query = """
            SELECT 
                strftime('%Y-%m', invoice_date) as month,
                SUM(total) as monthly_income,
                (
                    SELECT COALESCE(SUM(amount), 0)
                    FROM AccountingTransactions
                    WHERE transaction_type IN ('پرداخت', 'هزینه')
                    AND strftime('%Y-%m', transaction_date) = strftime('%Y-%m', i.invoice_date)
                ) as monthly_expense
            FROM Invoices i
            WHERE invoice_type IN ('فروش', 'خدمات')
            AND payment_status IN ('پرداخت شده', 'نقدی')
            AND invoice_date >= date('now', '-6 months')
            GROUP BY strftime('%Y-%m', invoice_date)
            ORDER BY month DESC
            LIMIT 6
            """
            
            results = self.data_manager.db.fetch_all(query)
            
            # محاسبه سود و نام ماه
            profit_data = []
            for result in results:
                income = result.get('monthly_income', 0)
                expense = result.get('monthly_expense', 0)
                profit = income - expense
                
                # استخراج سال و ماه
                year_month = result.get('month', '')
                if year_month:
                    year, month = year_month.split('-')
                    month_name = self.get_month_name(int(month))
                    display_name = f"{month_name}\n{year}"
                else:
                    display_name = "نامشخص"
                
                profit_data.append({
                    'month': year_month,
                    'month_name': display_name,
                    'income': income,
                    'expense': expense,
                    'profit': profit
                })
            
            return profit_data[::-1]  # معکوس کردن برای نمایش از قدیم به جدید
            
        except Exception as e:
            print(f"❌ خطا در دریافت سود ماهانه: {e}")
            return []
    
    def get_month_name(self, month_number):
        """دریافت نام ماه شمسی"""
        month_names = {
            1: "فروردین", 2: "اردیبهشت", 3: "خرداد",
            4: "تیر", 5: "مرداد", 6: "شهریور",
            7: "مهر", 8: "آبان", 9: "آذر",
            10: "دی", 11: "بهمن", 12: "اسفند"
        }
        return month_names.get(month_number, "نامشخص")




    def update_financial_summary(self):
        """به‌روزرسانی خلاصه مالی"""
        data = self.financial_data
        
        # به‌روزرسانی کارت‌ها
        self.update_card_text(self.income_card, f"{self.format_currency(data['total_income'])} تومان")
        self.update_card_text(self.expense_card, f"{self.format_currency(data['total_expense'])} تومان")
        self.update_card_text(self.profit_card, f"{self.format_currency(data['net_profit'])} تومان")
        self.update_card_text(self.margin_card, f"{data['profit_margin']:.1f}٪")
        self.update_card_text(self.transactions_card, f"{data['transaction_count']}")
        self.update_card_text(self.avg_income_card, f"{self.format_currency(data['daily_avg_income'])} تومان")
        self.update_card_text(self.max_income_card, f"{self.format_currency(data['max_daily_income'])} تومان")
        self.update_card_text(self.min_expense_card, f"{self.format_currency(data['min_daily_expense'])} تومان")
        
        # به‌روزرسانی جدول خلاصه
        self.update_summary_table()
    
    def update_card_text(self, card, new_text):
        """به‌روزرسانی متن کارت"""
        # کارت شامل یک QVBoxLayout است
        layout = card.layout()
        if layout and layout.count() >= 2:
            value_label = layout.itemAt(1).widget()  # موقعیت دوم = مقدار
            if value_label:
                value_label.setText(new_text)
    
    def format_currency(self, amount):
        """فرمت کردن مبلغ به صورت جداکننده هزارگان"""
        return f"{amount:,}".replace(",", "٬")
    
    def update_summary_table(self):
        """به‌روزرسانی جدول خلاصه مالی"""
        daily_data = self.chart_data["daily_data"]
        
        # تعداد ردیف‌های مورد نیاز
        row_count = min(len(daily_data), 15)
        self.summary_table.setRowCount(row_count)
        
        for row in range(row_count):
            data = daily_data[row]
            
            # تاریخ
            date_item = QTableWidgetItem(data["date"])
            date_item.setTextAlignment(Qt.AlignCenter)
            self.summary_table.setItem(row, 0, date_item)
            
            # درآمد
            income_item = QTableWidgetItem(f"{self.format_currency(data['income'])} تومان")
            income_item.setTextAlignment(Qt.AlignCenter)
            income_item.setForeground(QColor("#2ecc71"))  # سبز
            self.summary_table.setItem(row, 1, income_item)
            
            # هزینه
            expense_item = QTableWidgetItem(f"{self.format_currency(data['expense'])} تومان")
            expense_item.setTextAlignment(Qt.AlignCenter)
            expense_item.setForeground(QColor("#e74c3c"))  # قرمز
            self.summary_table.setItem(row, 2, expense_item)
            
            # سود
            profit_item = QTableWidgetItem(f"{self.format_currency(data['profit'])} تومان")
            profit_item.setTextAlignment(Qt.AlignCenter)
            
            # رنگ‌بندی سود (سبز برای مثبت، قرمز برای منفی)
            if data['profit'] >= 0:
                profit_item.setForeground(QColor("#2ecc71"))
            else:
                profit_item.setForeground(QColor("#e74c3c"))
            
            self.summary_table.setItem(row, 3, profit_item)
            
            # حاشیه سود
            if data['income'] > 0:
                margin = (data['profit'] / data['income']) * 100
                margin_text = f"{margin:.1f}٪"
            else:
                margin_text = "۰٪"
            
            margin_item = QTableWidgetItem(margin_text)
            margin_item.setTextAlignment(Qt.AlignCenter)
            
            # رنگ‌بندی حاشیه سود
            if margin >= 20:
                margin_item.setForeground(QColor("#2ecc71"))
            elif margin >= 10:
                margin_item.setForeground(QColor("#f39c12"))
            else:
                margin_item.setForeground(QColor("#e74c3c"))
            
            self.summary_table.setItem(row, 4, margin_item)
        
        # پنهان کردن ردیف‌های خالی
        for row in range(row_count, 15):
            self.summary_table.hideRow(row)
    



# تابع کمکی برای تست
if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication
    import sys
    
    app = QApplication(sys.argv)
    
    # DataManager ساختگی برای تست
    class MockDataManager:
        def get_data(self, *args):
            return []
    
    form = FinancialReportForm(MockDataManager())
    form.setWindowTitle("گزارش مالی - تست")
    form.resize(1200, 800)
    form.show()
    
    sys.exit(app.exec())