# -*- coding: utf-8 -*-
"""
فرم اصلی گزارش‌گیری با تب‌های مختلف
"""

# در reports_main_form.py هم اگر QAction دارید:
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTabWidget,
    QLabel, QPushButton, QFrame, QScrollArea,
    QGridLayout, QTableWidget, QTableWidgetItem,
    QHeaderView, QComboBox, QLineEdit, QDateEdit,
    QGroupBox, QFormLayout, QSpinBox, QCheckBox,
    QTextEdit, QProgressBar
)
from PySide6.QtCore import Qt, Signal, QDate
from PySide6.QtGui import QFont, QColor, QAction  # QAction از اینجا

import sys
import os

# اضافه کردن مسیر
current_dir = os.path.dirname(os.path.abspath(__file__))
utils_dir = os.path.join(current_dir, "utils")
if utils_dir not in sys.path:
    sys.path.append(utils_dir)

# حالا import کنید
try:
    from utils.financial_calculator import FinancialCalculator
except ImportError:
    # تعریف موقت
    class FinancialCalculator:
        def __init__(self, dm): pass
        def get_financial_summary(self, s, e): return {}

# ui/forms/reports/utils/date_utils.py
"""
توابع کمکی تاریخ شمسی برای ماژول گزارش‌گیری
"""

import jdatetime
from datetime import datetime

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
                g_date = datetime.strptime(gregorian_date, '%Y-%m-%d')
            except:
                try:
                    g_date = datetime.strptime(gregorian_date, '%Y/%m/%d')
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

def format_jalali_date(jalali_date, format_str='%Y/%m/%d'):
    """فرمت تاریخ شمسی"""
    if isinstance(jalali_date, str):
        try:
            year, month, day = map(int, jalali_date.split('/'))
            jalali_date = jdatetime.date(year, month, day)
        except:
            return jalali_date
    
    if isinstance(jalali_date, jdatetime.date):
        return jalali_date.strftime(format_str)
    
    return str(jalali_date)




class ReportsMainForm(QWidget):
    """فرم اصلی با تب‌های مختلف برای گزارش‌ها"""
    
    report_generated = Signal(str, dict)  # signal: report_type, report_data
    
    def __init__(self, data_manager):
        super().__init__()
        self.data_manager = data_manager
        
        # داده‌های گزارش
        self.report_data = {}
        self.current_report_type = ""
        
        # تنظیمات اولیه
        self.setup_ui()
        
        # بارگذاری اولیه داده‌ها
        self.load_initial_data()
    
    def setup_ui(self):
        """تنظیم رابط کاربری فرم"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(5, 5, 5, 5)
        main_layout.setSpacing(10)
        
        # نوار ابزار بالای تب‌ها
        self.create_toolbar(main_layout)
        
        # ایجاد ویجت تب‌ها
        self.create_tab_widget(main_layout)
        
        # نوار وضعیت پایین
        self.create_status_bar(main_layout)
    
    def create_toolbar(self, parent_layout):
        """ایجاد نوار ابزار بالای تب‌ها"""
        toolbar_frame = QFrame()
        toolbar_frame.setFrameStyle(QFrame.StyledPanel | QFrame.Raised)
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
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QLabel {
                color: #ffffff;
                font-weight: bold;
            }
        """)
        
        toolbar_layout = QHBoxLayout(toolbar_frame)
        
        # تاریخ شمسی
        jalali_date = get_current_jalali()
        date_label = QLabel(f"📅 تاریخ امروز: {jalali_date}")
        
        # دکمه‌های نوار ابزار
        btn_refresh = QPushButton("🔄 بروزرسانی")
        btn_refresh.clicked.connect(self.refresh_all_data)
        
        btn_quick_stats = QPushButton("📊 آمار سریع")
        btn_quick_stats.clicked.connect(self.show_quick_stats)
        
        btn_export = QPushButton("📤 خروجی")
        btn_export.clicked.connect(self.export_current_report)
        
        btn_print = QPushButton("🖨️ چاپ")
        btn_print.clicked.connect(self.print_current_report)
        
        toolbar_layout.addWidget(date_label, 4)
        toolbar_layout.addWidget(btn_refresh, 1)
        toolbar_layout.addWidget(btn_quick_stats, 1)
        toolbar_layout.addWidget(btn_export, 1)
        toolbar_layout.addWidget(btn_print, 1)
        
        parent_layout.addWidget(toolbar_frame)
    
    def create_tab_widget(self, parent_layout):
        """ایجاد ویجت تب‌ها"""
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
                padding: 8px 20px;
                margin-right: 2px;
                border-top-left-radius: 5px;
                border-top-right-radius: 5px;
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
        self.create_daily_report_tab()
        self.create_weekly_report_tab()
        self.create_monthly_report_tab()
        self.create_financial_report_tab()
        self.create_inventory_report_tab()
        self.create_repair_report_tab()
        self.create_sales_report_tab()
        self.create_customer_report_tab()
        
        parent_layout.addWidget(self.tab_widget, 1)  # stretch factor = 1

    def create_daily_report_tab(self):
        """ایجاد تب گزارش روزانه"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # هدر تب
        header_label = QLabel("📅 گزارش روزانه فعالیت‌ها")
        header_label.setStyleSheet("""
            QLabel {
                color: #3498db;
                font-size: 14pt;
                font-weight: bold;
                padding: 10px;
                background-color: #1a1a2e;
                border-radius: 5px;
            }
        """)
        header_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(header_label)
        
        # بخش فیلترها
        filter_group = self.create_daily_filters()
        layout.addWidget(filter_group)
        
        # بخش آمار سریع
        stats_group = self.create_daily_stats()
        layout.addWidget(stats_group)
        
        # بخش جدول داده‌ها - افزایش stretch factor به 2 برای فضای بیشتر
        table_group = self.create_daily_table()
        layout.addWidget(table_group, 2)  # تغییر: stretch factor = 2 (به جای 1)
        
        self.tab_widget.addTab(tab, "📅 روزانه")    
   
    def create_daily_filters(self):
        """ایجاد فیلترهای گزارش روزانه"""
        group = QGroupBox("🔍 فیلترهای گزارش")
        group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #3498db;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
                color: #3498db;
                font-size: 11pt;
            }
            QLabel {
                font-size: 11pt;
                font-family: 'B Nazanin';
            }
            QComboBox, QPushButton {
                font-size: 11pt;
                font-family: 'B Nazanin';
                padding: 6px;
            }
        """)
        
        layout = QGridLayout(group)
        
        # تاریخ
        layout.addWidget(QLabel("تاریخ:"), 0, 0)
        date_combo = QComboBox()
        date_combo.addItems(["امروز", "دیروز", "انتخاب تاریخ خاص"])
        layout.addWidget(date_combo, 0, 1)
        
        # نوع فعالیت
        layout.addWidget(QLabel("نوع فعالیت:"), 0, 2)
        activity_combo = QComboBox()
        activity_combo.addItems(["همه", "پذیرش", "تعمیر", "فروش", "خرید"])
        layout.addWidget(activity_combo, 0, 3)
        
        # وضعیت
        layout.addWidget(QLabel("وضعیت:"), 1, 0)
        status_combo = QComboBox()
        status_combo.addItems(["همه", "تکمیل شده", "در جریان", "لغو شده"])
        layout.addWidget(status_combo, 1, 1)
        
        # دکمه اعمال فیلتر
        btn_apply = QPushButton("✅ اعمال فیلتر")
        btn_apply.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                font-weight: bold;
                padding: 8px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #219653;
            }
        """)
        layout.addWidget(btn_apply, 1, 2, 1, 2)
        
        return group
    
    def create_daily_stats(self):
        """ایجاد آمار سریع گزارش روزانه"""
        group = QGroupBox("📊 آمار سریع امروز")
        group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #2ecc71;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
                color: #2ecc71;
            }
        """)
        
        layout = QGridLayout(group)
        
        # کارت‌های آمار
        stats = [
            ("پذیرش جدید", "15", "#3498db"),
            ("تعمیرات تکمیل شده", "10", "#2ecc71"),
            ("فاکتور صادر شده", "8", "#9b59b6"),
            ("دریافتی نقدی", "۲,۵۰۰,۰۰۰ تومان", "#f39c12"),
            ("مشتریان جدید", "5", "#e74c3c"),
            ("قطعات مصرف شده", "23", "#1abc9c")
        ]
        
        for i, (title, value, color) in enumerate(stats):
            stat_frame = QFrame()
            stat_frame.setStyleSheet(f"""
                QFrame {{
                    background-color: {color}15;
                    border: 2px solid {color};
                    border-radius: 8px;
                    padding: 10px;
                }}
                QLabel {{
                    color: #ffffff;
                }}
            """)
            
            stat_layout = QVBoxLayout(stat_frame)
            
            title_label = QLabel(title)
            title_label.setAlignment(Qt.AlignCenter)
            title_label.setStyleSheet(f"color: {color}; font-size: 10pt;")
            
            value_label = QLabel(value)
            value_label.setAlignment(Qt.AlignCenter)
            value_label.setStyleSheet("""
                QLabel {
                    color: #ffffff;
                    font-size: 16pt;
                    font-weight: bold;
                }
            """)
            
            stat_layout.addWidget(title_label)
            stat_layout.addWidget(value_label)
            
            row = i // 3
            col = i % 3
            layout.addWidget(stat_frame, row, col)
        
        return group

    def create_daily_table(self):
        """ایجاد جدول گزارش روزانه"""
        group = QGroupBox("📋 لیست فعالیت‌های امروز")
        group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #f39c12;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
                color: #f39c12;
            }
        """)
        
        layout = QVBoxLayout(group)
        
        # ایجاد جدول با 20 ردیف (افزایش از 10 به 20)
        self.daily_table = QTableWidget(20, 6)  # تغییر: 20 ردیف
        
        # تنظیم ارتفاع ردیف‌ها
        for i in range(20):
            self.daily_table.setRowHeight(i, 30)  # ارتفاع هر ردیف 30 پیکسل
        
        self.daily_table.setStyleSheet("""
            QTableWidget {
                background-color: #111111;
                alternate-background-color: #0a0a0a;
                gridline-color: #333333;
                color: #ffffff;
                font-size: 10pt;
                font-family: 'B Nazanin';
            }
            QTableWidget::item {
                padding: 6px;
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
                font-size: 11pt;
                font-family: 'B Nazanin';
            }
        """)
        
        # تنظیم هدرهای جدول
        headers = ["زمان", "نوع فعالیت", "شرح", "مشتری", "مبلغ", "وضعیت"]
        self.daily_table.setHorizontalHeaderLabels(headers)
        
        # تنظیمات ستون‌ها
        header = self.daily_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # زمان
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)  # نوع
        header.setSectionResizeMode(2, QHeaderView.Stretch)           # شرح
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)  # مشتری
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)  # مبلغ
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)  # وضعیت
        
        # تنظیم حداقل و حداکثر عرض ستون‌ها
        self.daily_table.setColumnWidth(0, 80)   # زمان
        self.daily_table.setColumnWidth(1, 100)  # نوع فعالیت
        self.daily_table.setColumnWidth(3, 120)  # مشتری
        self.daily_table.setColumnWidth(4, 120)  # مبلغ
        self.daily_table.setColumnWidth(5, 120)  # وضعیت
        
        # پر کردن جدول با داده‌های نمونه
        self.populate_daily_table_with_sample_data()
        
        # ایجاد اسکرول‌بار عمودی همیشه فعال
        self.daily_table.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.daily_table.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        layout.addWidget(self.daily_table, 1)  # stretch factor = 1
        
        return group
  
    def populate_daily_table_with_sample_data(self):
        """پر کردن جدول با داده‌های نمونه"""
        sample_data = [
            ["۰۸:۳۰", "پذیرش", "یخچال سامسونگ - عدم سرمادهی", "احمد احمدی", "۱۵۰,۰۰۰", "در انتظار"],
            ["۰۹:۱۵", "تعمیر", "تعویض کمپرسور یخچال", "رضا رضایی", "۴۵۰,۰۰۰", "تکمیل شده"],
            ["۱۰:۰۰", "فاکتور", "صدور فاکتور خدمات", "محمد محمدی", "۳۲۰,۰۰۰", "پرداخت شده"],
            ["۱۱:۳۰", "پذیرش", "ماشین لباسشویی ال جی - نشتی آب", "فاطمه فلاحی", "۱۲۰,۰۰۰", "در انتظار"],
            ["۱۳:۴۵", "خرید", "خرید قطعات از تامین کننده", "شرکت بهسان", "۸۰۰,۰۰۰", "تسویه شده"],
            ["۱۴:۲۰", "تعمیر", "تعویض برد ماشین لباسشویی", "سارا سارایی", "۲۸۰,۰۰۰", "در حال تعمیر"],
            ["۱۵:۱۰", "فروش", "فروش لوازم دست دوم", "علی علیزاده", "۱,۲۰۰,۰۰۰", "تحویل شده"],
            ["۱۶:۰۰", "پذیرش", "جاروبرقی - کاهش قدرت مکش", "نرگس نوروزی", "۹۰,۰۰۰", "در انتظار"],
            ["۱۶:۴۵", "تعمیر", "سرویس کولر گازی", "حسین حسینی", "۵۵۰,۰۰۰", "تکمیل شده"],
            ["۱۷:۳۰", "فاکتور", "صدور فاکتور قطعات", "مریم مرادی", "۱۸۰,۰۰۰", "در انتظار پرداخت"]
        ]
        
        for row, data in enumerate(sample_data):
            for col, value in enumerate(data):
                item = QTableWidgetItem(value)
                item.setTextAlignment(Qt.AlignCenter)
                
                # رنگ‌بندی بر اساس وضعیت
                if col == 5:  # ستون وضعیت
                    if value == "تکمیل شده":
                        item.setBackground(QColor(46, 204, 113, 50))
                    elif value == "در حال تعمیر":
                        item.setBackground(QColor(52, 152, 219, 50))
                    elif value == "در انتظار":
                        item.setBackground(QColor(241, 196, 15, 50))
                    elif value == "پرداخت شده":
                        item.setBackground(QColor(155, 89, 182, 50))
                
                self.daily_table.setItem(row, col, item)

    def create_weekly_report_tab(self):
        """ایجاد تب گزارش هفتگی"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        placeholder = QLabel("📆 گزارش هفتگی - به زودی...")
        placeholder.setAlignment(Qt.AlignCenter)
        placeholder.setStyleSheet("""
            QLabel {
                color: #7f8c8d;
                font-size: 24pt;
                font-weight: bold;
                padding: 50px;
                background-color: #111;
                border-radius: 10px;
            }
        """)
        
        layout.addWidget(placeholder)
        self.tab_widget.addTab(tab, "📆 هفتگی")
    
    def create_monthly_report_tab(self):
        """ایجاد تب گزارش ماهانه"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        placeholder = QLabel("📅 گزارش ماهانه - به زودی...")
        placeholder.setAlignment(Qt.AlignCenter)
        placeholder.setStyleSheet("""
            QLabel {
                color: #7f8c8d;
                font-size: 24pt;
                font-weight: bold;
                padding: 50px;
                background-color: #111;
                border-radius: 10px;
            }
        """)
        
        layout.addWidget(placeholder)
        self.tab_widget.addTab(tab, "📅 ماهانه")
    
# در reports_main_form.py، تابع create_financial_report_tab را اصلاح کنید:

    def create_financial_report_tab(self):
        """ایجاد تب گزارش مالی"""
        try:
            from ui.forms.reports.forms.financial_report_form import FinancialReportForm
            self.financial_form = FinancialReportForm(self.data_manager)
            tab = self.financial_form
        except ImportError as e:
            print(f"⚠️ خطا در بارگذاری فرم گزارش مالی: {e}")
            tab = QWidget()
            layout = QVBoxLayout(tab)
            
            error_label = QLabel(f"❌ خطا در بارگذاری گزارش مالی:\n{str(e)}")
            error_label.setAlignment(Qt.AlignCenter)
            error_label.setStyleSheet("""
                QLabel {
                    color: #e74c3c;
                    font-size: 12pt;
                    padding: 50px;
                }
            """)
            layout.addWidget(error_label)
        
        self.tab_widget.addTab(tab, "💰 مالی")

    def create_inventory_report_tab(self):
        """ایجاد تب گزارش انبار"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        placeholder = QLabel("📦 گزارش انبار - به زودی...")
        placeholder.setAlignment(Qt.AlignCenter)
        placeholder.setStyleSheet("""
            QLabel {
                color: #7f8c8d;
                font-size: 24pt;
                font-weight: bold;
                padding: 50px;
                background-color: #111;
                border-radius: 10px;
            }
        """)
        
        layout.addWidget(placeholder)
        self.tab_widget.addTab(tab, "📦 انبار")
    
    def create_repair_report_tab(self):
        """ایجاد تب گزارش تعمیرات"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        placeholder = QLabel("🔧 گزارش تعمیرات - به زودی...")
        placeholder.setAlignment(Qt.AlignCenter)
        placeholder.setStyleSheet("""
            QLabel {
                color: #7f8c8d;
                font-size: 24pt;
                font-weight: bold;
                padding: 50px;
                background-color: #111;
                border-radius: 10px;
            }
        """)
        
        layout.addWidget(placeholder)
        self.tab_widget.addTab(tab, "🔧 تعمیرات")
    
    def create_sales_report_tab(self):
        """ایجاد تب گزارش فروش"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        placeholder = QLabel("🛒 گزارش فروش - به زودی...")
        placeholder.setAlignment(Qt.AlignCenter)
        placeholder.setStyleSheet("""
            QLabel {
                color: #7f8c8d;
                font-size: 24pt;
                font-weight: bold;
                padding: 50px;
                background-color: #111;
                border-radius: 10px;
            }
        """)
        
        layout.addWidget(placeholder)
        self.tab_widget.addTab(tab, "🛒 فروش")
    
    def create_customer_report_tab(self):
        """ایجاد تب گزارش مشتریان"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        placeholder = QLabel("👥 گزارش مشتریان - به زودی...")
        placeholder.setAlignment(Qt.AlignCenter)
        placeholder.setStyleSheet("""
            QLabel {
                color: #7f8c8d;
                font-size: 24pt;
                font-weight: bold;
                padding: 50px;
                background-color: #111;
                border-radius: 10px;
            }
        """)
        
        layout.addWidget(placeholder)
        self.tab_widget.addTab(tab, "👥 مشتریان")
    
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
        self.status_label = QLabel("✅ سیستم گزارش‌گیری آماده است")
        
        # تعداد رکوردها
        self.records_label = QLabel("تعداد رکوردها: ۰")
        
        # زمان آخرین بروزرسانی
        self.last_update_label = QLabel("آخرین بروزرسانی: --:--")
        
        status_layout.addWidget(self.status_label, 4)
        status_layout.addWidget(self.records_label, 3)
        status_layout.addWidget(self.last_update_label, 3)
        
        parent_layout.addWidget(status_frame)
    

    def load_daily_report(self):
        """بارگذاری گزارش روزانه از دیتابیس واقعی"""
        try:
            # تاریخ انتخاب شده
            selected_date = self.daily_date_edit.date()
            
            # اگر تاریخ انتخاب نشده، امروز
            if not selected_date.isValid():
                selected_date = QDate.currentDate()
            
            # تبدیل تاریخ به رشته شمسی
            date_str = selected_date.toString("yyyy-MM-dd")
            date_shamsi = gregorian_to_jalali(date_str, "%Y-%m-%d")
            
            self.status_label.setText(f"📊 در حال بارگذاری گزارش روز {date_shamsi}...")
            
            # ۱. دریافت پذیرش‌های روز
            receptions = self.get_daily_receptions(date_str)
            
            # ۲. دریافت فاکتورهای روز
            invoices = self.get_daily_invoices(date_str)
            
            # ۳. دریافت تراکنش‌های روز
            transactions = self.get_daily_transactions(date_str)
            
            # ۴. پر کردن جدول گزارش روزانه
            self.update_daily_report_table(receptions, invoices, transactions)
            
            # ۵. به‌روزرسانی کارت‌های آماری
            self.update_daily_stats_cards(receptions, invoices, transactions)
            
            self.status_label.setText(f"✅ گزارش روز {date_shamsi} بارگذاری شد")
            
        except Exception as e:
            self.status_label.setText(f"❌ خطا در بارگذاری گزارش روزانه: {str(e)}")
            print(f"خطا در load_daily_report: {e}")
    
    def get_daily_receptions(self, date_str):
        """دریافت پذیرش‌های یک روز خاص"""
        try:
            query = """
            SELECT 
                r.id,
                r.reception_number,
                r.reception_date,
                r.status,
                r.estimated_cost,
                d.device_type,
                d.brand,
                d.model,
                p.full_name as customer_name
            FROM Receptions r
            JOIN Devices d ON r.device_id = d.id
            JOIN Persons p ON r.customer_id = p.id
            WHERE DATE(r.reception_date) = ?
            ORDER BY r.reception_time DESC
            """
            
            return self.data_manager.db.fetch_all(query, (date_str,))
            
        except Exception as e:
            print(f"❌ خطا در دریافت پذیرش‌های روزانه: {e}")
            return []
    
    def get_daily_invoices(self, date_str):
        """دریافت فاکتورهای یک روز خاص"""
        try:
            query = """
            SELECT 
                i.id,
                i.invoice_number,
                i.invoice_date,
                i.invoice_type,
                i.total,
                i.payment_status,
                p.full_name as customer_name
            FROM Invoices i
            LEFT JOIN Persons p ON i.customer_id = p.id
            WHERE DATE(i.invoice_date) = ?
            ORDER BY i.invoice_date DESC
            """
            
            return self.data_manager.db.fetch_all(query, (date_str,))
            
        except Exception as e:
            print(f"❌ خطا در دریافت فاکتورهای روزانه: {e}")
            return []
    
    def get_daily_transactions(self, date_str):
        """دریافت تراکنش‌های یک روز خاص"""
        try:
            query = """
            SELECT 
                at.id,
                at.transaction_date,
                at.transaction_type,
                at.amount,
                at.description,
                a1.account_name as from_account,
                a2.account_name as to_account
            FROM AccountingTransactions at
            LEFT JOIN Accounts a1 ON at.from_account_id = a1.id
            LEFT JOIN Accounts a2 ON at.to_account_id = a2.id
            WHERE DATE(at.transaction_date) = ?
            ORDER BY at.transaction_date DESC
            """
            
            return self.data_manager.db.fetch_all(query, (date_str,))
            
        except Exception as e:
            print(f"❌ خطا در دریافت تراکنش‌های روزانه: {e}")
            return []
    
    def update_daily_report_table(self, receptions, invoices, transactions):
        """به‌روزرسانی جدول گزارش روزانه"""
        # ترکیب همه رکوردها
        all_records = []
        
        # افزودن پذیرش‌ها
        for rec in receptions:
            all_records.append({
                'type': 'پذیرش',
                'id': rec.get('reception_number', ''),
                'date': rec.get('reception_date', ''),
                'description': f"{rec.get('device_type', '')} - {rec.get('brand', '')} ({rec.get('customer_name', '')})",
                'status': rec.get('status', ''),
                'amount': rec.get('estimated_cost', 0),
                'color': self.get_status_color(rec.get('status', ''))
            })
        
        # افزودن فاکتورها
        for inv in invoices:
            all_records.append({
                'type': 'فاکتور',
                'id': inv.get('invoice_number', ''),
                'date': inv.get('invoice_date', ''),
                'description': f"{inv.get('invoice_type', '')} - {inv.get('customer_name', '')}",
                'status': inv.get('payment_status', ''),
                'amount': inv.get('total', 0),
                'color': self.get_payment_color(inv.get('payment_status', ''))
            })
        
        # افزودن تراکنش‌ها
        for trans in transactions:
            all_records.append({
                'type': 'تراکنش',
                'id': trans.get('id', ''),
                'date': trans.get('transaction_date', ''),
                'description': trans.get('description', ''),
                'status': trans.get('transaction_type', ''),
                'amount': trans.get('amount', 0),
                'color': self.get_transaction_color(trans.get('transaction_type', ''))
            })
        
        # مرتب‌سازی بر اساس تاریخ
        all_records.sort(key=lambda x: x.get('date', ''), reverse=True)
        
        # پر کردن جدول
        row_count = min(len(all_records), 20)
        self.daily_table.setRowCount(row_count)
        
        for row in range(row_count):
            record = all_records[row]
            
            # نوع
            type_item = QTableWidgetItem(record['type'])
            type_item.setTextAlignment(Qt.AlignCenter)
            self.daily_table.setItem(row, 0, type_item)
            
            # شناسه
            id_item = QTableWidgetItem(str(record['id']))
            id_item.setTextAlignment(Qt.AlignCenter)
            self.daily_table.setItem(row, 1, id_item)
            
            # تاریخ (تبدیل به شمسی)
            date_shamsi = gregorian_to_jalali(record['date']) if record['date'] else ''
            date_item = QTableWidgetItem(date_shamsi)
            date_item.setTextAlignment(Qt.AlignCenter)
            self.daily_table.setItem(row, 2, date_item)
            
            # شرح
            desc_item = QTableWidgetItem(record['description'][:40] + "..." if len(record['description']) > 40 else record['description'])
            desc_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.daily_table.setItem(row, 3, desc_item)
            
            # وضعیت
            status_item = QTableWidgetItem(record['status'])
            status_item.setTextAlignment(Qt.AlignCenter)
            status_item.setForeground(QColor(record['color']))
            self.daily_table.setItem(row, 4, status_item)
            
            # مبلغ (تبدیل به تومان)
            amount_toman = record['amount'] / 10
            amount_item = QTableWidgetItem(self.format_currency(amount_toman))
            amount_item.setTextAlignment(Qt.AlignCenter)
            
            # رنگ‌بندی مبلغ
            if record['type'] == 'فاکتور' and record['status'] in ['پرداخت شده', 'نقدی']:
                amount_item.setForeground(QColor("#2ecc71"))  # سبز برای درآمد
            elif record['type'] == 'تراکنش' and record['status'] in ['پرداخت', 'هزینه']:
                amount_item.setForeground(QColor("#e74c3c"))  # قرمز برای هزینه
            else:
                amount_item.setForeground(QColor("#f39c12"))  # نارنجی برای سایر
            
            self.daily_table.setItem(row, 5, amount_item)
        
        # پنهان کردن ردیف‌های خالی
        for row in range(row_count, 20):
            self.daily_table.hideRow(row)
    
    def get_status_color(self, status):
        """رنگ بر اساس وضعیت پذیرش"""
        color_map = {
            'در انتظار': '#f39c12',      # نارنجی
            'در حال تعمیر': '#3498db',    # آبی
            'تعمیر شده': '#2ecc71',       # سبز
            'تحویل داده شده': '#27ae60',  # سبز تیره
            'لغو شده': '#e74c3c'          # قرمز
        }
        return color_map.get(status, '#95a5a6')  # خاکستری
    
    def get_payment_color(self, status):
        """رنگ بر اساس وضعیت پرداخت"""
        color_map = {
            'پرداخت شده': '#2ecc71',      # سبز
            'نقدی': '#27ae60',            # سبز تیره
            'نسیه': '#f39c12',            # نارنجی
            'چک': '#3498db',              # آبی
            'کارت': '#9b59b6'             # بنفش
        }
        return color_map.get(status, '#95a5a6')  # خاکستری
    
    def get_transaction_color(self, transaction_type):
        """رنگ بر اساس نوع تراکنش"""
        color_map = {
            'دریافت': '#2ecc71',      # سبز
            'درآمد': '#27ae60',       # سبز تیره
            'پرداخت': '#e74c3c',      # قرمز
            'هزینه': '#c0392b',       # قرمز تیره
            'انتقال': '#3498db'       # آبی
        }
        return color_map.get(transaction_type, '#95a5a6')  # خاکستری




    def load_initial_data(self):
        """بارگذاری اولیه داده‌ها"""
        # TODO: بارگذاری داده‌های واقعی از دیتابیس
        self.status_label.setText("✅ داده‌های اولیه بارگذاری شدند")
        self.records_label.setText("تعداد رکوردها: ۱۰")
        self.last_update_label.setText("آخرین بروزرسانی: " + get_current_jalali())
    
    def refresh_all_data(self):
        """بروزرسانی تمام داده‌ها"""
        # TODO: پیاده‌سازی بروزرسانی داده‌ها از دیتابیس
        self.status_label.setText("🔄 در حال بروزرسانی داده‌ها...")
        
        # شبیه‌سازی بروزرسانی
        import time
        time.sleep(0.5)  # شبیه‌سازی تاخیر
        
        self.status_label.setText("✅ داده‌ها با موفقیت بروزرسانی شدند")
        self.last_update_label.setText("آخرین بروزرسانی: " + get_current_jalali())
    
    def show_quick_stats(self):
        """نمایش آمار سریع"""
        # TODO: پیاده‌سازی نمایش آمار سریع
        pass
    
    def export_current_report(self):
        """صدور خروجی از گزارش جاری"""
        current_tab = self.tab_widget.currentIndex()
        tab_names = ["روزانه", "هفتگی", "ماهانه", "مالی", "انبار", "تعمیرات", "فروش", "مشتریان"]
        
        # TODO: پیاده‌سازی خروجی واقعی
        print(f"صدور خروجی از گزارش {tab_names[current_tab]}")
    
    def print_current_report(self):
        """چاپ گزارش جاری"""
        current_tab = self.tab_widget.currentIndex()
        tab_names = ["روزانه", "هفتگی", "ماهانه", "مالی", "انبار", "تعمیرات", "فروش", "مشتریان"]
        
        # TODO: پیاده‌سازی چاپ واقعی
        print(f"چاپ گزارش {tab_names[current_tab]}")
    
    def show_tab(self, tab_index):
        """نمایش تب مشخص شده"""
        if 0 <= tab_index < self.tab_widget.count():
            self.tab_widget.setCurrentIndex(tab_index)


# تابع کمکی برای تست
if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication
    import sys
    
    app = QApplication(sys.argv)
    
    # DataManager ساختگی برای تست
    class MockDataManager:
        def get_data(self, *args):
            return []
    
    form = ReportsMainForm(MockDataManager())
    form.setWindowTitle("فرم گزارش‌گیری - تست")
    form.resize(1000, 700)
    form.show()
    
    sys.exit(app.exec())