"""
فرم گزارش تعمیرات - نسخه کامل با ویجت تاریخ شمسی و کوئری‌های اصلاح شده
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTabWidget,
    QLabel, QPushButton, QFrame, QTableWidget,
    QTableWidgetItem, QHeaderView, QGroupBox,
    QGridLayout, QComboBox, QLineEdit, QDateEdit,
    QFormLayout, QSpinBox, QCheckBox, QTextEdit,
    QProgressBar, QStackedWidget, QApplication,
    QMessageBox, QSizePolicy
)
from PySide6.QtCore import Qt, Signal, QDate, QTimer, QSize
from PySide6.QtGui import QFont, QColor, QBrush, QIcon
import jdatetime
from datetime import datetime, timedelta
import sys
import os

# اضافه کردن مسیر برای import ماژول‌های داخلی
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

# import ویجت تاریخ شمسی
try:
    from utils.jalali_date_widget import JalaliDateInput
    JALALI_DATE_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ خطا در بارگذاری ویجت تاریخ شمسی: {e}")
    print("استفاده از QDateEdit به جای ویجت تاریخ شمسی")
    JALALI_DATE_AVAILABLE = False

# import توابع تاریخ شمسی
try:
    from utils.jalali_date_widget import (
        get_current_jalali, gregorian_to_jalali, jalali_to_gregorian
    )
    DATE_UTILS_AVAILABLE = True
except ImportError:
    # تعریف موقت
    DATE_UTILS_AVAILABLE = False
    def get_current_jalali():
        now = jdatetime.datetime.now()
        return now.strftime('%Y/%m/%d %H:%M:%S')
    
    def gregorian_to_jalali(gregorian_date):
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
                g_date = gregorian_date
            
            # تبدیل به تاریخ شمسی
            j_date = jdatetime.date.fromgregorian(date=g_date.date())
            return j_date.strftime("%Y/%m/%d")
        except Exception as e:
            print(f"⚠️ خطا در تبدیل تاریخ {gregorian_date}: {e}")
            return str(gregorian_date)
    
    def jalali_to_gregorian(jalali_date_str):
        if not jalali_date_str:
            return None
        
        try:
            # پاکسازی رشته
            date_str = str(jalali_date_str).strip()
            
            # اگر فرمت yyyy/mm/dd است
            if '/' in date_str:
                parts = date_str.split('/')
                if len(parts) == 3:
                    year = int(parts[0])
                    month = int(parts[1])
                    day = int(parts[2])
                else:
                    return None
            # اگر فرمت yyyy-mm-dd است
            elif '-' in date_str:
                parts = date_str.split('-')
                if len(parts) == 3:
                    year = int(parts[0])
                    month = int(parts[1])
                    day = int(parts[2])
                else:
                    return None
            else:
                return None
            
            # ایجاد تاریخ شمسی
            jalali_date = jdatetime.date(year, month, day)
            
            # تبدیل به میلادی
            gregorian_date = jalali_date.togregorian()
            
            return gregorian_date.strftime("%Y-%m-%d")
            
        except Exception as e:
            print(f"⚠️ خطا در تبدیل تاریخ شمسی {jalali_date_str}: {e}")
            return None


class RepairReportForm(QWidget):
    """فرم گزارش تعمیرات - نسخه کامل و اصلاح شده"""
    
    def __init__(self, data_manager):
        super().__init__()
        self.data_manager = data_manager
        
        # داده‌های گزارش
        self.report_data = {}
        self.current_filters = {
            'start_date': None,
            'end_date': None,
            'technician_id': None,
            'status': None,
            'repair_type': None,
            'device_type': None
        }
        
        # تست تاریخ شمسی
        self.test_jalali_date_conversion()
        
        # تنظیم رابط کاربری
        self.setup_ui()
        
        # بارگذاری اولیه داده‌ها
        QTimer.singleShot(100, self.load_initial_data)
    
    def test_jalali_date_conversion(self):
        """تست تبدیل تاریخ شمسی"""
        print("=" * 50)
        print("🔍 تست تبدیل تاریخ شمسی:")
        print("=" * 50)
        
        # تاریخ امروز شمسی
        today_jalali = jdatetime.date.today()
        today_jalali_str = today_jalali.strftime("%Y/%m/%d")
        print(f"📅 تاریخ امروز شمسی: {today_jalali_str}")
        
        # تبدیل به میلادی
        gregorian_date = today_jalali.togregorian()
        print(f"📅 تاریخ امروز میلادی: {gregorian_date}")
        
        # تبدیل برگشت به شمسی
        jalali_converted = gregorian_to_jalali(str(gregorian_date))
        print(f"📅 تبدیل برگشت به شمسی: {jalali_converted}")
        
        # تست تبدیل رشته تاریخ
        test_dates = [
            "1403/01/01",
            "1404/11/15",
            "2025-01-15",
            "2025/01/15"
        ]
        
        for test_date in test_dates:
            try:
                if '/' in test_date and len(test_date.split('/')[0]) == 4:
                    # احتمالاً تاریخ شمسی
                    converted = jalali_to_gregorian(test_date)
                    print(f"✅ {test_date} (شمسی) → {converted} (میلادی)")
                else:
                    # احتمالاً تاریخ میلادی
                    converted = gregorian_to_jalali(test_date)
                    print(f"✅ {test_date} (میلادی) → {converted} (شمسی)")
            except Exception as e:
                print(f"❌ خطا در تبدیل {test_date}: {e}")
        
        print("=" * 50)
    
    def setup_ui(self):
        """تنظیم رابط کاربری فرم"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(5, 5, 5, 5)
        main_layout.setSpacing(10)
        
        # هدر فرم
        self.create_header(main_layout)
        
        # بخش تست تاریخ شمسی
        self.create_date_test_section(main_layout)
        
        # فیلترها
        self.create_filters(main_layout)
        
        # تب‌ها
        self.create_tabs(main_layout)
        
        # نوار وضعیت
        self.create_status_bar(main_layout)
    
    def create_date_test_section(self, parent_layout):
        """ایجاد بخش تست تاریخ شمسی"""
        test_frame = QFrame()
        test_frame.setStyleSheet("""
            QFrame {
                background-color: #2c3e50;
                border-radius: 6px;
                padding: 10px;
                border: 2px solid #3498db;
            }
            QLabel {
                color: #ecf0f1;
                font-size: 10pt;
                font-family: 'B Nazanin';
            }
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 8px 15px;
                border-radius: 4px;
                font-weight: bold;
                font-size: 10pt;
                font-family: 'B Nazanin';
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        
        test_layout = QVBoxLayout(test_frame)
        
        title_label = QLabel("🔧 تست تاریخ شمسی")
        title_label.setStyleSheet("color: #3498db; font-size: 12pt; font-weight: bold;")
        
        test_content = QLabel(
            "این بخش برای تست صحت تبدیل تاریخ‌های شمسی و میلادی ایجاد شده است.\n"
            "اطمینان حاصل کنید که تاریخ‌ها به درستی تبدیل می‌شوند."
        )
        test_content.setStyleSheet("color: #bdc3c7; font-size: 10pt;")
        
        test_btn = QPushButton("🔄 تست تبدیل تاریخ")
        test_btn.clicked.connect(self.run_date_conversion_test)
        
        test_layout.addWidget(title_label)
        test_layout.addWidget(test_content)
        test_layout.addWidget(test_btn)
        
        parent_layout.addWidget(test_frame)
    
    def create_header(self, parent_layout):
        """ایجاد هدر فرم"""
        header_frame = QFrame()
        header_frame.setStyleSheet("""
            QFrame {
                background-color: #1a1a2e;
                border-radius: 8px;
                padding: 15px;
            }
            QLabel {
                color: white;
            }
        """)
        
        header_layout = QVBoxLayout(header_frame)
        
        # عنوان اصلی
        title_label = QLabel("🔧 گزارش تعمیرات")
        title_label.setStyleSheet("""
            QLabel {
                color: #3498db;
                font-size: 18pt;
                font-weight: bold;
            }
        """)
        title_label.setAlignment(Qt.AlignCenter)
        
        # زیرعنوان
        subtitle_label = QLabel("تحلیل و آمار تعمیرات انجام شده - نسخه اصلاح شده")
        subtitle_label.setStyleSheet("""
            QLabel {
                color: #bdc3c7;
                font-size: 11pt;
            }
        """)
        subtitle_label.setAlignment(Qt.AlignCenter)
        
        # آمار سریع
        quick_stats_layout = QHBoxLayout()
        
        self.quick_stats_labels = []
        quick_stats_data = [
            ("تعمیرات امروز", "0", "#3498db"),
            ("تعمیرات ماه", "0", "#2ecc71"),
            ("تعمیرکاران فعال", "0", "#f39c12"),
            ("میانگین هزینه", "0", "#9b59b6")
        ]
        
        for title, value, color in quick_stats_data:
            stat_frame = QFrame()
            stat_frame.setStyleSheet(f"""
                QFrame {{
                    background-color: {color}20;
                    border: 1px solid {color};
                    border-radius: 6px;
                    padding: 8px;
                }}
            """)
            
            stat_layout = QVBoxLayout(stat_frame)
            stat_layout.setSpacing(2)
            
            title_lbl = QLabel(title)
            title_lbl.setAlignment(Qt.AlignCenter)
            title_lbl.setStyleSheet(f"color: {color}; font-size: 9pt;")
            
            value_lbl = QLabel(value)
            value_lbl.setAlignment(Qt.AlignCenter)
            value_lbl.setStyleSheet("""
                QLabel {
                    color: white;
                    font-size: 12pt;
                    font-weight: bold;
                }
            """)
            
            stat_layout.addWidget(title_lbl)
            stat_layout.addWidget(value_lbl)
            quick_stats_layout.addWidget(stat_frame)
            
            self.quick_stats_labels.append(value_lbl)
        
        header_layout.addWidget(title_label)
        header_layout.addWidget(subtitle_label)
        header_layout.addLayout(quick_stats_layout)
        
        parent_layout.addWidget(header_frame)
    
    def create_filters(self, parent_layout):
        """ایجاد بخش فیلترها با ویجت تاریخ شمسی"""
        filter_frame = QFrame()
        filter_frame.setStyleSheet("""
            QFrame {
                background-color: #2c3e50;
                border-radius: 6px;
                padding: 10px;
            }
            QLabel {
                color: #ecf0f1;
                font-size: 10pt;
                font-family: 'B Nazanin';
            }
            QComboBox, QLineEdit {
                background-color: #34495e;
                color: white;
                border: 1px solid #7f8c8d;
                border-radius: 4px;
                padding: 6px;
                font-size: 10pt;
                font-family: 'B Nazanin';
                min-width: 120px;
            }
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 8px 15px;
                border-radius: 4px;
                font-weight: bold;
                font-size: 10pt;
                font-family: 'B Nazanin';
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton#reset_btn {
                background-color: #e74c3c;
            }
            QPushButton#reset_btn:hover {
                background-color: #c0392b;
            }
        """)
        
        filter_layout = QGridLayout(filter_frame)
        filter_layout.setVerticalSpacing(10)
        filter_layout.setHorizontalSpacing(15)
        
        # ردیف ۱: تاریخ‌ها
        # تاریخ شروع
        filter_layout.addWidget(QLabel("از تاریخ:"), 0, 0, Qt.AlignRight)
        
        if JALALI_DATE_AVAILABLE:
            self.start_date_input = JalaliDateInput(mode='edit', theme='dark')
            self.start_date_input.setFixedWidth(130)
        else:
            self.start_date_input = QDateEdit()
            self.start_date_input.setCalendarPopup(True)
            self.start_date_input.setDisplayFormat("yyyy/MM/dd")
            self.start_date_input.setDate(QDate.currentDate().addMonths(-1))
        
        filter_layout.addWidget(self.start_date_input, 0, 1)
        
        # تاریخ پایان
        filter_layout.addWidget(QLabel("تا تاریخ:"), 0, 2, Qt.AlignRight)
        
        if JALALI_DATE_AVAILABLE:
            self.end_date_input = JalaliDateInput(mode='edit', theme='dark')
            self.end_date_input.setFixedWidth(130)
            # تنظیم تاریخ امروز به صورت پیش‌فرض
            self.end_date_input.set_today()
        else:
            self.end_date_input = QDateEdit()
            self.end_date_input.setCalendarPopup(True)
            self.end_date_input.setDisplayFormat("yyyy/MM/dd")
            self.end_date_input.setDate(QDate.currentDate())
        
        filter_layout.addWidget(self.end_date_input, 0, 3)
        
        # ردیف ۲: فیلترهای دیگر
        # تعمیرکار
        filter_layout.addWidget(QLabel("تعمیرکار:"), 1, 0, Qt.AlignRight)
        self.technician_combo = QComboBox()
        self.technician_combo.addItem("همه تعمیرکاران", None)
        filter_layout.addWidget(self.technician_combo, 1, 1)
        
        # وضعیت
        filter_layout.addWidget(QLabel("وضعیت:"), 1, 2, Qt.AlignRight)
        self.status_combo = QComboBox()
        self.status_combo.addItem("همه وضعیت‌ها", None)
        self.status_combo.addItem("تمام شده", "تمام شده")
        self.status_combo.addItem("شروع شده", "شروع شده")
        self.status_combo.addItem("در حال انجام", "در حال انجام")
        self.status_combo.addItem("متوقف شده", "متوقف شده")
        self.status_combo.addItem("در انتظار", "در انتظار")
        filter_layout.addWidget(self.status_combo, 1, 3)
        
        # ردیف ۳: فیلترهای اضافی
        # نوع تعمیر
        filter_layout.addWidget(QLabel("نوع تعمیر:"), 2, 0, Qt.AlignRight)
        self.repair_type_combo = QComboBox()
        self.repair_type_combo.addItem("همه انواع", None)
        self.repair_type_combo.addItem("داخلی", "داخلی")
        self.repair_type_combo.addItem("بیرون سپاری", "بیرون سپاری")
        filter_layout.addWidget(self.repair_type_combo, 2, 1)
        
        # نوع دستگاه
        filter_layout.addWidget(QLabel("نوع دستگاه:"), 2, 2, Qt.AlignRight)
        self.device_type_combo = QComboBox()
        self.device_type_combo.addItem("همه دستگاه‌ها", None)
        filter_layout.addWidget(self.device_type_combo, 2, 3)
        
        # ردیف ۴: دکمه‌ها
        btn_layout = QHBoxLayout()
        
        # دکمه اعمال فیلتر
        btn_apply = QPushButton("🔍 اعمال فیلتر")
        btn_apply.clicked.connect(self.apply_filters)
        btn_apply.setMinimumWidth(120)
        
        # دکمه بازنشانی
        btn_reset = QPushButton("🔄 بازنشانی")
        btn_reset.clicked.connect(self.reset_filters)
        btn_reset.setMinimumWidth(120)
        btn_reset.setObjectName("reset_btn")
        
        # دکمه خروجی
        btn_export = QPushButton("📤 خروجی Excel")
        btn_export.clicked.connect(self.export_report)
        btn_export.setMinimumWidth(120)
        
        # دکمه تست کوئری
        btn_test_query = QPushButton("🧪 تست کوئری")
        btn_test_query.clicked.connect(self.test_database_queries)
        btn_test_query.setMinimumWidth(120)
        
        btn_layout.addWidget(btn_apply)
        btn_layout.addWidget(btn_reset)
        btn_layout.addWidget(btn_export)
        btn_layout.addWidget(btn_test_query)
        btn_layout.addStretch()
        
        filter_layout.addLayout(btn_layout, 3, 0, 1, 4)
        
        parent_layout.addWidget(filter_frame)
    
    def create_tabs(self, parent_layout):
        """ایجاد تب‌های گزارش"""
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
                font-size: 10pt;
                font-family: 'B Nazanin';
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
        self.create_technician_tab()
        self.create_failure_tab()
        self.create_trends_tab()
        self.create_devices_tab()
        self.create_parts_tab()
        self.create_services_tab()
        self.create_time_analysis_tab()
        
        parent_layout.addWidget(self.tab_widget, 1)
    
    def create_summary_tab(self):
        """ایجاد تب خلاصه تعمیرات"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(10)
        
        # کارت‌های آمار
        self.stats_frame = QFrame()
        stats_layout = QGridLayout(self.stats_frame)
        stats_layout.setSpacing(10)
        
        # ایجاد ۹ کارت آماری
        self.stat_cards = []
        stat_titles = [
            ("کل تعمیرات", "total_repairs", "#3498db"),
            ("تکمیل شده", "completed", "#2ecc71"),
            ("در جریان", "in_progress", "#f39c12"),
            ("لغو شده", "cancelled", "#e74c3c"),
            ("میانگین هزینه", "avg_cost", "#9b59b6"),
            ("هزینه کل", "total_cost", "#1abc9c"),
            ("دستمزد کل", "total_labor", "#34495e"),
            ("داخلی", "internal_repairs", "#27ae60"),
            ("خارجی", "external_repairs", "#8e44ad")
        ]
        
        for i, (title, key, color) in enumerate(stat_titles):
            card = self.create_stat_card(title, "0", color)
            self.stat_cards.append((card, key))
            row = i // 3
            col = i % 3
            stats_layout.addWidget(card, row, col)
        
        layout.addWidget(self.stats_frame)
        
        # جدول آخرین تعمیرات
        group = QGroupBox("📋 آخرین تعمیرات")
        group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #f39c12;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
                color: #f39c12;
                font-size: 11pt;
                font-family: 'B Nazanin';
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 10px 0 10px;
            }
        """)
        
        group_layout = QVBoxLayout(group)
        
        self.recent_repairs_table = QTableWidget(0, 8)
        self.recent_repairs_table.setStyleSheet("""
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
                font-size: 10pt;
                font-family: 'B Nazanin';
            }
        """)
        
        headers = ["تاریخ", "شماره پذیرش", "دستگاه", "نوع", "تعمیرکار", "هزینه کل", "وضعیت", "نوع تعمیر"]
        self.recent_repairs_table.setHorizontalHeaderLabels(headers)
        
        header = self.recent_repairs_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # تاریخ
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)  # شماره پذیرش
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)  # تعمیرکار
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)  # هزینه کل
        header.setSectionResizeMode(6, QHeaderView.ResizeToContents)  # وضعیت
        header.setSectionResizeMode(7, QHeaderView.ResizeToContents)  # نوع تعمیر
        
        group_layout.addWidget(self.recent_repairs_table)
        layout.addWidget(group, 1)
        
        self.tab_widget.addTab(tab, "📊 خلاصه")
    
    def create_stat_card(self, title, value, color):
        """ایجاد کارت آماری"""
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background-color: {color}15;
                border: 2px solid {color};
                border-radius: 8px;
                padding: 15px;
            }}
            QLabel {{
                color: #ffffff;
                font-family: 'B Nazanin';
            }}
        """)
        
        layout = QVBoxLayout(card)
        layout.setSpacing(5)
        
        title_label = QLabel(title)
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet(f"color: {color}; font-size: 11pt; font-weight: bold;")
        
        value_label = QLabel(value)
        value_label.setAlignment(Qt.AlignCenter)
        value_label.setStyleSheet("""
            QLabel {
                color: #ffffff;
                font-size: 18pt;
                font-weight: bold;
                margin-top: 5px;
            }
        """)
        
        layout.addWidget(title_label)
        layout.addWidget(value_label)
        
        return card
    
    def create_technician_tab(self):
        """ایجاد تب تحلیل تعمیرکاران"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # توضیحات
        desc_label = QLabel("📈 عملکرد تعمیرکاران بر اساس تعداد تعمیرات و درآمد تولیدی")
        desc_label.setStyleSheet("color: #7f8c8d; font-size: 10pt; padding: 10px; font-family: 'B Nazanin';")
        desc_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(desc_label)
        
        # جدول تعمیرکاران
        self.technician_table = QTableWidget(0, 8)
        self.technician_table.setStyleSheet("""
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
                font-size: 10pt;
                font-family: 'B Nazanin';
            }
        """)
        
        headers = ["نام تعمیرکار", "تعداد تعمیر", "درآمد کل", "میانگین درآمد", "دستمزد کل", "تعمیرات تکمیل", "میانگین زمان (ساعت)", "اولین/آخرین تعمیر"]
        self.technician_table.setHorizontalHeaderLabels(headers)
        
        header = self.technician_table.horizontalHeader()
        for i in range(8):
            header.setSectionResizeMode(i, QHeaderView.Stretch)
        
        layout.addWidget(self.technician_table, 1)
        
        self.tab_widget.addTab(tab, "👨‍🔧 تعمیرکاران")
    
    def create_failure_tab(self):
        """ایجاد تب علل خرابی"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # توضیحات
        desc_label = QLabel("🔍 شایع‌ترین علل خرابی دستگاه‌ها و هزینه تعمیر مرتبط")
        desc_label.setStyleSheet("color: #7f8c8d; font-size: 10pt; padding: 10px; font-family: 'B Nazanin';")
        desc_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(desc_label)
        
        # جدول علل خرابی
        self.failure_table = QTableWidget(0, 6)
        self.failure_table.setStyleSheet("""
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
                font-size: 10pt;
                font-family: 'B Nazanin';
            }
        """)
        
        headers = ["علت خرابی", "تعداد", "میانگین هزینه", "هزینه کل", "میانگین دستمزد", "دستگاه/برند"]
        self.failure_table.setHorizontalHeaderLabels(headers)
        
        header = self.failure_table.horizontalHeader()
        for i in range(6):
            header.setSectionResizeMode(i, QHeaderView.Stretch)
        
        layout.addWidget(self.failure_table, 1)
        
        self.tab_widget.addTab(tab, "🔍 علل خرابی")
    
    def create_trends_tab(self):
        """ایجاد تب روندها"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # کنترل‌های گروه‌بندی
        control_layout = QHBoxLayout()
        control_layout.addWidget(QLabel("گروه‌بندی بر اساس:"))
        
        self.trend_group_combo = QComboBox()
        self.trend_group_combo.addItems(["روز", "هفته", "ماه"])
        self.trend_group_combo.currentTextChanged.connect(self.load_trends_data)
        self.trend_group_combo.setStyleSheet("""
            QComboBox {
                background-color: #34495e;
                color: white;
                border: 1px solid #7f8c8d;
                border-radius: 4px;
                padding: 6px;
                font-family: 'B Nazanin';
            }
        """)
        
        control_layout.addWidget(self.trend_group_combo)
        control_layout.addStretch()
        
        layout.addLayout(control_layout)
        
        # جدول روندها
        self.trends_table = QTableWidget(0, 6)
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
                font-size: 10pt;
                font-family: 'B Nazanin';
            }
        """)
        
        headers = ["دوره", "تعداد تعمیر", "تکمیل شده", "درآمد کل", "دستمزد کل", "میانگین درآمد"]
        self.trends_table.setHorizontalHeaderLabels(headers)
        
        header = self.trends_table.horizontalHeader()
        for i in range(6):
            header.setSectionResizeMode(i, QHeaderView.Stretch)
        
        layout.addWidget(self.trends_table, 1)
        
        self.tab_widget.addTab(tab, "📈 روندها")
    
    def create_devices_tab(self):
        """ایجاد تب تحلیل دستگاه‌ها"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # توضیحات
        desc_label = QLabel("📊 تحلیل تعمیرات بر اساس نوع دستگاه")
        desc_label.setStyleSheet("color: #7f8c8d; font-size: 10pt; padding: 10px; font-family: 'B Nazanin';")
        desc_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(desc_label)
        
        # جدول دستگاه‌ها
        self.devices_table = QTableWidget(0, 8)
        self.devices_table.setStyleSheet("""
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
                font-size: 10pt;
                font-family: 'B Nazanin';
            }
        """)
        
        headers = ["نوع دستگاه", "تعداد تعمیر", "درآمد کل", "میانگین درآمد", "دستمزد کل", "میانگین دستمزد", "تعمیرکاران", "نرخ تکمیل"]
        self.devices_table.setHorizontalHeaderLabels(headers)
        
        header = self.devices_table.horizontalHeader()
        for i in range(8):
            header.setSectionResizeMode(i, QHeaderView.Stretch)
        
        layout.addWidget(self.devices_table, 1)
        
        self.tab_widget.addTab(tab, "📱 دستگاه‌ها")
    
    def create_parts_tab(self):
        """ایجاد تب تحلیل قطعات"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # توضیحات
        desc_label = QLabel("🔩 تحلیل قطعات مصرفی در تعمیرات")
        desc_label.setStyleSheet("color: #7f8c8d; font-size: 10pt; padding: 10px; font-family: 'B Nazanin';")
        desc_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(desc_label)
        
        # جدول قطعات
        self.parts_table = QTableWidget(0, 7)
        self.parts_table.setStyleSheet("""
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
                font-size: 10pt;
                font-family: 'B Nazanin';
            }
        """)
        
        headers = ["نام قطعه", "کد", "دسته", "برند", "تعداد مصرف", "هزینه کل", "تعداد تعمیرات"]
        self.parts_table.setHorizontalHeaderLabels(headers)
        
        header = self.parts_table.horizontalHeader()
        for i in range(7):
            header.setSectionResizeMode(i, QHeaderView.Stretch)
        
        layout.addWidget(self.parts_table, 1)
        
        self.tab_widget.addTab(tab, "🔩 قطعات")
    
    def create_services_tab(self):
        """ایجاد تب تحلیل خدمات"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # توضیحات
        desc_label = QLabel("⚙️ تحلیل خدمات ارائه شده در تعمیرات")
        desc_label.setStyleSheet("color: #7f8c8d; font-size: 10pt; padding: 10px; font-family: 'B Nazanin';")
        desc_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(desc_label)
        
        # جدول خدمات
        self.services_table = QTableWidget(0, 6)
        self.services_table.setStyleSheet("""
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
                font-size: 10pt;
                font-family: 'B Nazanin';
            }
        """)
        
        headers = ["نام خدمت", "کد", "دسته", "تعداد ارائه", "درآمد کل", "تعداد تعمیرات"]
        self.services_table.setHorizontalHeaderLabels(headers)
        
        header = self.services_table.horizontalHeader()
        for i in range(6):
            header.setSectionResizeMode(i, QHeaderView.Stretch)
        
        layout.addWidget(self.services_table, 1)
        
        self.tab_widget.addTab(tab, "⚙️ خدمات")
    
    def create_time_analysis_tab(self):
        """ایجاد تب تحلیل زمان"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # توضیحات
        desc_label = QLabel("⏱️ تحلیل زمان‌بندی و کارایی تعمیرات")
        desc_label.setStyleSheet("color: #7f8c8d; font-size: 10pt; padding: 10px; font-family: 'B Nazanin';")
        desc_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(desc_label)
        
        # جدول تحلیل زمان
        self.time_table = QTableWidget(0, 6)
        self.time_table.setStyleSheet("""
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
                font-size: 10pt;
                font-family: 'B Nazanin';
            }
        """)
        
        headers = ["بازه زمانی", "تعداد تعمیر", "میانگین هزینه", "هزینه کل", "میانگین دستمزد", "میانگین روز"]
        self.time_table.setHorizontalHeaderLabels(headers)
        
        header = self.time_table.horizontalHeader()
        for i in range(6):
            header.setSectionResizeMode(i, QHeaderView.Stretch)
        
        layout.addWidget(self.time_table, 1)
        
        self.tab_widget.addTab(tab, "⏱️ زمان‌بندی")
    
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
                font-family: 'B Nazanin';
            }
        """)
        
        status_layout = QHBoxLayout(status_frame)
        
        self.status_label = QLabel("✅ سیستم گزارش‌گیری تعمیرات آماده است")
        self.records_label = QLabel("تعداد رکوردها: ۰")
        self.update_label = QLabel("آخرین بروزرسانی: --:--")
        
        status_layout.addWidget(self.status_label, 4)
        status_layout.addWidget(self.records_label, 3)
        status_layout.addWidget(self.update_label, 3)
        
        parent_layout.addWidget(status_frame)
    
    def load_initial_data(self):
        """بارگذاری اولیه داده‌ها"""
        self.status_label.setText("📥 در حال بارگذاری داده‌های اولیه...")
        QApplication.processEvents()
        
        # بارگذاری لیست تعمیرکاران
        self.load_technicians()
        
        # بارگذاری لیست انواع دستگاه
        self.load_device_types()
        
        # تنظیم تاریخ‌های پیش‌فرض
        self.set_default_dates()
        
        # اعمال فیلترهای پیش‌فرض
        self.apply_filters()
        
        # بارگذاری آمار سریع
        self.load_quick_stats()
        
        self.status_label.setText("✅ داده‌های اولیه بارگذاری شدند")
        self.update_label.setText(f"آخرین بروزرسانی: {get_current_jalali()}")
    
    def load_technicians(self):
        """بارگذاری لیست تعمیرکاران"""
        try:
            # دریافت تعمیرکاران از جدول Persons
            query = """
            SELECT id, 
                   CASE 
                       WHEN first_name IS NOT NULL AND last_name IS NOT NULL 
                       THEN first_name || ' ' || last_name
                       WHEN first_name IS NOT NULL THEN first_name
                       WHEN last_name IS NOT NULL THEN last_name
                       ELSE 'تعمیرکار #' || id
                   END as full_name
            FROM Persons 
            WHERE person_type LIKE '%تعمیرکار%' 
               OR person_type LIKE '%تکنسین%'
               OR person_type LIKE '%کارشناس%'
            ORDER BY full_name
            """
            
            technicians = self.data_manager.db.fetch_all(query)
            
            self.technician_combo.clear()
            self.technician_combo.addItem("همه تعمیرکاران", None)
            
            for tech in technicians:
                self.technician_combo.addItem(tech['full_name'], tech['id'])
                
            print(f"✅ {len(technicians)} تعمیرکار بارگذاری شد")
                
        except Exception as e:
            print(f"خطا در بارگذاری تعمیرکاران: {e}")
    
    def load_device_types(self):
        """بارگذاری لیست انواع دستگاه"""
        try:
            # دریافت انواع دستگاه از جدول DeviceCategories_name
            query = "SELECT id, name FROM DeviceCategories_name ORDER BY name"
            device_types = self.data_manager.db.fetch_all(query)
            
            self.device_type_combo.clear()
            self.device_type_combo.addItem("همه دستگاه‌ها", None)
            
            for dt in device_types:
                self.device_type_combo.addItem(dt['name'], dt['id'])
                
            print(f"✅ {len(device_types)} نوع دستگاه بارگذاری شد")
                
        except Exception as e:
            print(f"خطا در بارگذاری انواع دستگاه: {e}")
    
    def set_default_dates(self):
        """تنظیم تاریخ‌های پیش‌فرض"""
        # تنظیم تاریخ شروع: اول ماه جاری شمسی
        today_jalali = jdatetime.date.today()
        first_of_month = jdatetime.date(today_jalali.year, today_jalali.month, 1)
        
        if JALALI_DATE_AVAILABLE:
            self.start_date_input.set_date(first_of_month.strftime("%Y/%m/%d"))
        else:
            # تبدیل به میلادی برای QDateEdit
            gregorian_date = first_of_month.togregorian()
            qdate = QDate(gregorian_date.year, gregorian_date.month, gregorian_date.day)
            self.start_date_input.setDate(qdate)

    def apply_filters(self):
        """اعمال فیلترهای انتخاب شده - نسخه ایمن"""
        try:
            # دریافت مقادیر فیلترها
            if JALALI_DATE_AVAILABLE:
                # استفاده از get_date() که ممکن است None باشد
                start_date = self.start_date_input.get_date()
                end_date = self.end_date_input.get_date()
                
                # اگر get_date() None برگرداند، از متن ورودی استفاده کن
                if not start_date:
                    start_date = self.start_date_input.date_input.text().strip()
                if not end_date:
                    end_date = self.end_date_input.date_input.text().strip()
            else:
                start_date = self.start_date_input.date().toString("yyyy/MM/dd")
                end_date = self.end_date_input.date().toString("yyyy/MM/dd")
            
            # اعتبارسنجی تاریخ‌ها
            if not start_date or not end_date:
                QMessageBox.warning(self, "خطا", "تاریخ شروع و پایان باید مشخص شوند.")
                return
            
            # اعتبارسنجی فرمت تاریخ (باید شامل / باشد)
            if '/' not in start_date or '/' not in end_date:
                QMessageBox.warning(self, "خطا", "فرمت تاریخ نامعتبر است. از فرمت 1404/01/01 استفاده کنید.")
                return
            
            # تبدیل تاریخ‌های شمسی به میلادی برای کوئری دیتابیس
            start_date_gregorian = jalali_to_gregorian(start_date)
            end_date_gregorian = jalali_to_gregorian(end_date)
            
            if not start_date_gregorian or not end_date_gregorian:
                QMessageBox.warning(self, "خطا", "تاریخ‌ها معتبر نیستند.")
                return
            
            technician_id = self.technician_combo.currentData()
            status = self.status_combo.currentData()
            repair_type = self.repair_type_combo.currentData()
            device_type = self.device_type_combo.currentData()
            
            # ذخیره فیلترها
            self.current_filters = {
                'start_date': start_date,
                'end_date': end_date,
                'start_date_gregorian': start_date_gregorian,
                'end_date_gregorian': end_date_gregorian,
                'technician_id': technician_id,
                'status': status,
                'repair_type': repair_type,
                'device_type': device_type
            }
            
            print(f"🔍 اعمال فیلترها:")
            print(f"   - از تاریخ شمسی: {start_date}")
            print(f"   - تا تاریخ شمسی: {end_date}")
            print(f"   - از تاریخ میلادی: {start_date_gregorian}")
            print(f"   - تا تاریخ میلادی: {end_date_gregorian}")
            print(f"   - تعمیرکار: {technician_id}")
            print(f"   - وضعیت: {status}")
            
            # بارگذاری داده‌ها با فیلترها
            self.load_report_data()
            
        except Exception as e:
            self.status_label.setText(f"❌ خطا در اعمال فیلترها: {str(e)}")
            print(f"خطا در apply_filters: {e}")
            import traceback
            traceback.print_exc()    
   
    def reset_filters(self):
        """بازنشانی فیلترها به حالت پیش‌فرض"""
        try:
            # تنظیم مجدد تاریخ‌ها
            self.set_default_dates()
            
            if JALALI_DATE_AVAILABLE:
                self.end_date_input.set_today()
            else:
                self.end_date_input.setDate(QDate.currentDate())
            
            # تنظیم سایر فیلترها
            self.technician_combo.setCurrentIndex(0)
            self.status_combo.setCurrentIndex(0)
            self.repair_type_combo.setCurrentIndex(0)
            self.device_type_combo.setCurrentIndex(0)
            
            # اعمال فیلترها
            self.apply_filters()
            
        except Exception as e:
            print(f"خطا در reset_filters: {e}")
    
    def load_report_data(self):
        """بارگذاری داده‌های گزارش با فیلترهای فعلی - نسخه ایمن"""
        try:
            self.status_label.setText("📊 در حال بارگذاری گزارش...")
            QApplication.processEvents()
            
            start_date = self.current_filters['start_date_gregorian']
            end_date = self.current_filters['end_date_gregorian']
            
            print(f"🔍 بارگذاری گزارش با فیلترها:")
            print(f"   - از تاریخ میلادی: {start_date}")
            print(f"   - تا تاریخ میلادی: {end_date}")
            print(f"   - تعمیرکار: {self.current_filters['technician_id']}")
            print(f"   - وضعیت: {self.current_filters['status']}")
            
            # بارگذاری خلاصه گزارش
            print("📊 در حال دریافت خلاصه گزارش...")
            summary = self.get_repair_summary_data(start_date, end_date)
            print(f"   نتایج: {summary}")
            self.update_summary_cards(summary)
            
            # بارگذاری آخرین تعمیرات
            print("📋 در حال دریافت آخرین تعمیرات...")
            recent_repairs = self.get_recent_repairs_data(start_date, end_date)
            print(f"   تعداد: {len(recent_repairs)} رکورد")
            self.update_recent_repairs_table(recent_repairs)
            
            # بارگذاری داده‌های تعمیرکاران
            print("👨‍🔧 در حال دریافت عملکرد تعمیرکاران...")
            technicians = self.get_technician_performance_data(start_date, end_date)
            print(f"   تعداد: {len(technicians)} تعمیرکار")
            self.update_technician_table(technicians)
            
            # بارگذاری علل خرابی
            print("🔍 در حال دریافت علل خرابی...")
            failures = self.get_failure_causes_data(start_date, end_date)
            print(f"   تعداد: {len(failures)} علت")
            self.update_failure_table(failures)
            
            # بارگذاری روندها
            print("📈 در حال دریافت روندها...")
            self.load_trends_data()
            
            # بارگذاری تحلیل دستگاه‌ها
            print("📱 در حال تحلیل دستگاه‌ها...")
            devices = self.get_device_type_analysis_data(start_date, end_date)
            print(f"   تعداد: {len(devices)} نوع دستگاه")
            self.update_devices_table(devices)
            
            # بارگذاری تحلیل قطعات
            print("🔩 در حال تحلیل قطعات...")
            parts = self.get_repair_parts_analysis_data(start_date, end_date)
            print(f"   تعداد: {len(parts)} قطعه")
            self.update_parts_table(parts)
            
            # بارگذاری تحلیل خدمات
            print("⚙️ در حال تحلیل خدمات...")
            services = self.get_repair_services_analysis_data(start_date, end_date)
            print(f"   تعداد: {len(services)} خدمت")
            self.update_services_table(services)
            
            # بارگذاری تحلیل زمان
            print("⏱️ در حال تحلیل زمان...")
            time_analysis = self.get_repair_time_analysis_data(start_date, end_date)
            print(f"   تعداد: {len(time_analysis)} بازه زمانی")
            self.update_time_table(time_analysis)
            
            # به‌روزرسانی نوار وضعیت
            total_records = summary.get('total_repairs', 0)
            self.records_label.setText(f"تعداد رکوردها: {total_records}")
            self.status_label.setText("✅ گزارش بارگذاری شد")
            self.update_label.setText(f"آخرین بروزرسانی: {get_current_jalali()}")
            
            print(f"✅ گزارش با موفقیت بارگذاری شد. {total_records} رکورد یافت شد.")
            
        except Exception as e:
            self.status_label.setText(f"❌ خطا در بارگذاری گزارش: {str(e)}")
            print(f"❌ خطا در load_report_data: {e}")
            import traceback
            traceback.print_exc()

    # ============================================================
    # توابع جدید برای دریافت داده‌ها از دیتابیس
    # ============================================================
    
    def get_repair_summary_data(self, start_date, end_date):
        """دریافت خلاصه گزارش تعمیرات"""
        query = """
        SELECT 
            COUNT(rep.id) as total_repairs,
            SUM(CASE WHEN rep.status = 'تمام شده' THEN 1 ELSE 0 END) as completed,
            SUM(CASE WHEN rep.status IN ('شروع شده', 'در حال انجام') THEN 1 ELSE 0 END) as in_progress,
            SUM(CASE WHEN rep.status = 'متوقف شده' THEN 1 ELSE 0 END) as cancelled,
            AVG(rep.total_cost) as avg_cost,
            SUM(rep.total_cost) as total_cost,
            AVG(rep.labor_cost) as avg_labor,
            SUM(rep.labor_cost) as total_labor,
            SUM(CASE WHEN rep.repair_type = 'داخلی' THEN 1 ELSE 0 END) as internal_repairs,
            SUM(CASE WHEN rep.repair_type IN ('بیرون سپاری', 'خارجی') THEN 1 ELSE 0 END) as external_repairs
        FROM Repairs rep
        LEFT JOIN Receptions rec ON rep.reception_id = rec.id
        WHERE rec.reception_date >= ? AND rec.reception_date <= ?
        """
        return self.data_manager.db.fetch_one(query, (start_date, end_date)) or {}
    
    def get_recent_repairs_data(self, start_date, end_date):
        """دریافت آخرین تعمیرات"""
        query = """
        SELECT 
            rep.id,
            rep.repair_date,
            rec.reception_number,
            d.device_type,
            d.model as device_model,
            d.brand,
            CASE 
                WHEN p.first_name IS NOT NULL AND p.last_name IS NOT NULL 
                THEN p.first_name || ' ' || p.last_name
                WHEN p.first_name IS NOT NULL THEN p.first_name
                WHEN p.last_name IS NOT NULL THEN p.last_name
                ELSE 'تعمیرکار #' || rep.technician_id
            END as technician_name,
            rep.total_cost,
            rep.status,
            rep.repair_type
        FROM Repairs rep
        LEFT JOIN Receptions rec ON rep.reception_id = rec.id
        LEFT JOIN Devices d ON rec.device_id = d.id
        LEFT JOIN Persons p ON rep.technician_id = p.id
        WHERE rec.reception_date >= ? AND rec.reception_date <= ?
        ORDER BY rep.repair_date DESC
        LIMIT 50
        """
        return self.data_manager.db.fetch_all(query, (start_date, end_date)) or []
    
    def get_technician_performance_data(self, start_date, end_date):
        """دریافت عملکرد تعمیرکاران"""
        query = """
        SELECT 
            p.id as technician_id,
            CASE 
                WHEN p.first_name IS NOT NULL AND p.last_name IS NOT NULL 
                THEN p.first_name || ' ' || p.last_name
                WHEN p.first_name IS NOT NULL THEN p.first_name
                WHEN p.last_name IS NOT NULL THEN p.last_name
                ELSE 'تعمیرکار #' || p.id
            END as technician_name,
            COUNT(rep.id) as repair_count,
            SUM(rep.total_cost) as total_revenue,
            AVG(rep.total_cost) as avg_revenue,
            SUM(rep.labor_cost) as total_labor,
            AVG(rep.labor_cost) as avg_labor,
            SUM(CASE WHEN rep.status = 'تمام شده' THEN 1 ELSE 0 END) as completed_count,
            MIN(rep.repair_date) as first_repair,
            MAX(rep.repair_date) as last_repair
        FROM Repairs rep
        LEFT JOIN Persons p ON rep.technician_id = p.id
        LEFT JOIN Receptions rec ON rep.reception_id = rec.id
        WHERE rec.reception_date >= ? AND rec.reception_date <= ?
          AND rep.technician_id IS NOT NULL
        GROUP BY p.id
        ORDER BY repair_count DESC
        """
        return self.data_manager.db.fetch_all(query, (start_date, end_date)) or []
    
    def get_failure_causes_data(self, start_date, end_date):
        """دریافت علل خرابی"""
        query = """
        SELECT 
            SUBSTR(rec.problem_description, 1, 100) as problem_description,
            COUNT(rep.id) as count,
            AVG(rep.total_cost) as avg_repair_cost,
            SUM(rep.total_cost) as total_cost,
            AVG(rep.labor_cost) as avg_labor_cost,
            d.device_type,
            d.brand
        FROM Repairs rep
        LEFT JOIN Receptions rec ON rep.reception_id = rec.id
        LEFT JOIN Devices d ON rec.device_id = d.id
        WHERE rec.reception_date >= ? AND rec.reception_date <= ?
          AND rec.problem_description IS NOT NULL
          AND rec.problem_description != ''
        GROUP BY SUBSTR(rec.problem_description, 1, 100), d.device_type, d.brand
        ORDER BY count DESC
        LIMIT 20
        """
        return self.data_manager.db.fetch_all(query, (start_date, end_date)) or []
    
    def get_device_type_analysis_data(self, start_date, end_date):
        """تحلیل تعمیرات بر اساس نوع دستگاه"""
        query = """
        SELECT
            d.device_type,
            COUNT(rep.id) as repair_count,
            SUM(rep.total_cost) as total_revenue,
            AVG(rep.total_cost) as avg_revenue,
            SUM(rep.labor_cost) as total_labor,
            AVG(rep.labor_cost) as avg_labor,
            COUNT(DISTINCT rep.technician_id) as technician_count
        FROM Receptions rec
        LEFT JOIN Devices d ON rec.device_id = d.id
        LEFT JOIN Repairs rep ON rec.id = rep.reception_id
        WHERE rec.reception_date >= ? AND rec.reception_date <= ?
          AND rep.id IS NOT NULL
          AND d.device_type IS NOT NULL
        GROUP BY d.device_type
        ORDER BY repair_count DESC
        """
        return self.data_manager.db.fetch_all(query, (start_date, end_date)) or []
    
    def get_repair_parts_analysis_data(self, start_date, end_date):
        """تحلیل قطعات مصرفی در تعمیرات"""
        query = """
        SELECT 
            p.part_name,
            p.part_code,
            p.category,
            p.brand,
            SUM(rp.quantity) as total_quantity,
            SUM(rp.total_price) as total_cost,
            COUNT(DISTINCT rp.repair_id) as repair_count
        FROM Repair_Parts rp
        LEFT JOIN Parts p ON rp.part_id = p.id
        LEFT JOIN Repairs rep ON rp.repair_id = rep.id
        LEFT JOIN Receptions rec ON rep.reception_id = rec.id
        WHERE rec.reception_date >= ? AND rec.reception_date <= ?
          AND p.part_name IS NOT NULL
        GROUP BY p.id
        ORDER BY total_quantity DESC
        LIMIT 20
        """
        return self.data_manager.db.fetch_all(query, (start_date, end_date)) or []
    
    def get_repair_services_analysis_data(self, start_date, end_date):
        """تحلیل خدمات ارائه شده در تعمیرات"""
        query = """
        SELECT 
            sf.service_name,
            sf.service_code,
            sf.category,
            SUM(rs.quantity) as total_quantity,
            SUM(rs.total_price) as total_revenue,
            COUNT(DISTINCT rs.repair_id) as repair_count
        FROM Repair_Services rs
        LEFT JOIN ServiceFees sf ON rs.service_id = sf.id
        LEFT JOIN Repairs rep ON rs.repair_id = rep.id
        LEFT JOIN Receptions rec ON rep.reception_id = rec.id
        WHERE rec.reception_date >= ? AND rec.reception_date <= ?
          AND sf.service_name IS NOT NULL
        GROUP BY sf.id
        ORDER BY total_quantity DESC
        LIMIT 20
        """
        return self.data_manager.db.fetch_all(query, (start_date, end_date)) or []
    
    def get_repair_time_analysis_data(self, start_date, end_date):
        """تحلیل زمان‌بندی تعمیرات"""
        query = """
        SELECT 
            CASE 
                WHEN julianday(rep.end_time) - julianday(rep.start_time) <= 1 THEN 'کمتر از 1 روز'
                WHEN julianday(rep.end_time) - julianday(rep.start_time) <= 3 THEN '1-3 روز'
                WHEN julianday(rep.end_time) - julianday(rep.start_time) <= 7 THEN '4-7 روز'
                WHEN julianday(rep.end_time) - julianday(rep.start_time) <= 14 THEN '1-2 هفته'
                ELSE 'بیش از 2 هفته'
            END as duration_category,
            COUNT(rep.id) as repair_count,
            AVG(rep.total_cost) as avg_cost,
            SUM(rep.total_cost) as total_cost,
            AVG(rep.labor_cost) as avg_labor,
            AVG(julianday(rep.end_time) - julianday(rep.start_time)) as avg_days
        FROM Repairs rep
        LEFT JOIN Receptions rec ON rep.reception_id = rec.id
        WHERE rec.reception_date >= ? AND rec.reception_date <= ?
          AND rep.start_time IS NOT NULL
          AND rep.end_time IS NOT NULL
        GROUP BY duration_category
        ORDER BY repair_count DESC
        """
        return self.data_manager.db.fetch_all(query, (start_date, end_date)) or []
    
    def update_summary_cards(self, summary):
        """به‌روزرسانی کارت‌های آماری - نسخه ایمن"""
        for card, key in self.stat_cards:
            value = summary.get(key, 0)
            
            # اطمینان از اینکه مقدار None نباشد
            if value is None:
                value = 0
            
            # تبدیل به عدد برای فرمت کردن
            try:
                value = float(value) if isinstance(value, (int, float)) else 0
            except (ValueError, TypeError):
                value = 0
            
            if key in ['avg_cost', 'total_cost', 'avg_labor', 'total_labor']:
                # فرمت‌بندی مبلغ به تومان
                if value:
                    value_toman = value / 10
                    formatted_value = f"{value_toman:,.0f} تومان"
                else:
                    formatted_value = "۰ تومان"
            else:
                # برای مقادیر عددی
                formatted_value = f"{int(value):,}"
            
            # پیدا کردن لیبل مقدار در کارت
            value_label = card.layout().itemAt(1).widget()
            if value_label:
                value_label.setText(formatted_value)
    
    def update_recent_repairs_table(self, repairs):
        """به‌روزرسانی جدول آخرین تعمیرات"""
        self.recent_repairs_table.setRowCount(len(repairs))
        
        for row, repair in enumerate(repairs):
            # تاریخ (تبدیل به شمسی)
            date_shamsi = gregorian_to_jalali(repair.get('repair_date', ''))
            date_item = QTableWidgetItem(date_shamsi)
            date_item.setTextAlignment(Qt.AlignCenter)
            self.recent_repairs_table.setItem(row, 0, date_item)
            
            # شماره پذیرش
            reception_item = QTableWidgetItem(repair.get('reception_number', ''))
            reception_item.setTextAlignment(Qt.AlignCenter)
            self.recent_repairs_table.setItem(row, 1, reception_item)
            
            # دستگاه
            device_text = f"{repair.get('device_type', '')} - {repair.get('device_model', '')}"
            device_item = QTableWidgetItem(device_text)
            device_item.setTextAlignment(Qt.AlignCenter)
            self.recent_repairs_table.setItem(row, 2, device_item)
            
            # برند
            brand_item = QTableWidgetItem(repair.get('brand', ''))
            brand_item.setTextAlignment(Qt.AlignCenter)
            self.recent_repairs_table.setItem(row, 3, brand_item)
            
            # تعمیرکار
            tech_item = QTableWidgetItem(repair.get('technician_name', ''))
            tech_item.setTextAlignment(Qt.AlignCenter)
            self.recent_repairs_table.setItem(row, 4, tech_item)
            
            # هزینه کل (تبدیل به تومان)
            cost = repair.get('total_cost', 0)
            cost_toman = cost / 10 if cost else 0
            cost_item = QTableWidgetItem(f"{cost_toman:,.0f}")
            cost_item.setTextAlignment(Qt.AlignCenter)
            
            # رنگ‌بندی بر اساس مبلغ
            if cost_toman > 500000:
                cost_item.setForeground(QBrush(QColor("#e74c3c")))  # قرمز برای مبالغ بالا
            elif cost_toman > 200000:
                cost_item.setForeground(QBrush(QColor("#f39c12")))  # نارنجی
            else:
                cost_item.setForeground(QBrush(QColor("#2ecc71")))  # سبز
            
            self.recent_repairs_table.setItem(row, 5, cost_item)
            
            # وضعیت
            status = repair.get('status', '')
            status_item = QTableWidgetItem(status)
            status_item.setTextAlignment(Qt.AlignCenter)
            
            # رنگ‌بندی وضعیت
            if status == 'تمام شده':
                status_item.setForeground(QBrush(QColor("#2ecc71")))  # سبز
            elif status in ['شروع شده', 'در حال انجام']:
                status_item.setForeground(QBrush(QColor("#3498db")))  # آبی
            elif status == 'متوقف شده':
                status_item.setForeground(QBrush(QColor("#e74c3c")))  # قرمز
            elif status == 'در انتظار':
                status_item.setForeground(QBrush(QColor("#f39c12")))  # نارنجی
            
            self.recent_repairs_table.setItem(row, 6, status_item)
            
            # نوع تعمیر
            repair_type = repair.get('repair_type', '')
            type_item = QTableWidgetItem(repair_type)
            type_item.setTextAlignment(Qt.AlignCenter)
            self.recent_repairs_table.setItem(row, 7, type_item)
    
    def update_technician_table(self, technicians):
        """به‌روزرسانی جدول تعمیرکاران"""
        self.technician_table.setRowCount(len(technicians))
        
        for row, tech in enumerate(technicians):
            # نام تعمیرکار
            name_item = QTableWidgetItem(tech.get('technician_name', 'نامشخص'))
            name_item.setTextAlignment(Qt.AlignCenter)
            self.technician_table.setItem(row, 0, name_item)
            
            # تعداد تعمیر
            count_item = QTableWidgetItem(str(tech.get('repair_count', 0)))
            count_item.setTextAlignment(Qt.AlignCenter)
            self.technician_table.setItem(row, 1, count_item)
            
            # درآمد کل (تبدیل به تومان)
            revenue = tech.get('total_revenue', 0)
            revenue_toman = revenue / 10 if revenue else 0
            revenue_item = QTableWidgetItem(f"{revenue_toman:,.0f} تومان")
            revenue_item.setTextAlignment(Qt.AlignCenter)
            self.technician_table.setItem(row, 2, revenue_item)
            
            # میانگین درآمد
            avg_revenue = tech.get('avg_revenue', 0)
            avg_revenue_toman = avg_revenue / 10 if avg_revenue else 0
            avg_revenue_item = QTableWidgetItem(f"{avg_revenue_toman:,.0f} تومان")
            avg_revenue_item.setTextAlignment(Qt.AlignCenter)
            self.technician_table.setItem(row, 3, avg_revenue_item)
            
            # دستمزد کل
            labor = tech.get('total_labor', 0)
            labor_toman = labor / 10 if labor else 0
            labor_item = QTableWidgetItem(f"{labor_toman:,.0f} تومان")
            labor_item.setTextAlignment(Qt.AlignCenter)
            self.technician_table.setItem(row, 4, labor_item)
            
            # تعمیرات تکمیل شده
            completed_item = QTableWidgetItem(str(tech.get('completed_count', 0)))
            completed_item.setTextAlignment(Qt.AlignCenter)
            self.technician_table.setItem(row, 5, completed_item)
            
            # میانگین زمان
            first_date = tech.get('first_repair', '')
            last_date = tech.get('last_repair', '')
            if first_date and last_date:
                try:
                    first_dt = datetime.strptime(first_date, '%Y-%m-%d')
                    last_dt = datetime.strptime(last_date, '%Y-%m-%d')
                    days_diff = (last_dt - first_dt).days
                    avg_days = days_diff / tech.get('repair_count', 1) if tech.get('repair_count', 0) > 0 else 0
                    hours_item = QTableWidgetItem(f"{avg_days:,.1f} روز")
                except:
                    hours_item = QTableWidgetItem("نامشخص")
            else:
                hours_item = QTableWidgetItem("نامشخص")
            hours_item.setTextAlignment(Qt.AlignCenter)
            self.technician_table.setItem(row, 6, hours_item)
            
            # اولین/آخرین تعمیر
            first_date_shamsi = gregorian_to_jalali(first_date)
            last_date_shamsi = gregorian_to_jalali(last_date)
            dates_item = QTableWidgetItem(f"{first_date_shamsi} تا {last_date_shamsi}")
            dates_item.setTextAlignment(Qt.AlignCenter)
            self.technician_table.setItem(row, 7, dates_item)
    
    def update_failure_table(self, failures):
        """به‌روزرسانی جدول علل خرابی"""
        self.failure_table.setRowCount(len(failures))
        
        for row, failure in enumerate(failures):
            # علت خرابی
            cause = failure.get('problem_description', 'نامشخص')
            if len(cause) > 50:
                cause = cause[:47] + "..."
            cause_item = QTableWidgetItem(cause)
            cause_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.failure_table.setItem(row, 0, cause_item)
            
            # تعداد
            count_item = QTableWidgetItem(str(failure.get('count', 0)))
            count_item.setTextAlignment(Qt.AlignCenter)
            self.failure_table.setItem(row, 1, count_item)
            
            # میانگین هزینه تعمیر (تبدیل به تومان)
            avg_cost = failure.get('avg_repair_cost', 0)
            avg_cost_toman = avg_cost / 10 if avg_cost else 0
            avg_cost_item = QTableWidgetItem(f"{avg_cost_toman:,.0f} تومان")
            avg_cost_item.setTextAlignment(Qt.AlignCenter)
            self.failure_table.setItem(row, 2, avg_cost_item)
            
            # هزینه کل
            total_cost = failure.get('total_cost', 0)
            total_cost_toman = total_cost / 10 if total_cost else 0
            total_cost_item = QTableWidgetItem(f"{total_cost_toman:,.0f} تومان")
            total_cost_item.setTextAlignment(Qt.AlignCenter)
            self.failure_table.setItem(row, 3, total_cost_item)
            
            # میانگین دستمزد
            avg_labor = failure.get('avg_labor_cost', 0)
            avg_labor_toman = avg_labor / 10 if avg_labor else 0
            avg_labor_item = QTableWidgetItem(f"{avg_labor_toman:,.0f} تومان")
            avg_labor_item.setTextAlignment(Qt.AlignCenter)
            self.failure_table.setItem(row, 4, avg_labor_item)
            
            # دستگاه/برند
            device_info = f"{failure.get('device_type', '')} - {failure.get('brand', '')}"
            device_item = QTableWidgetItem(device_info)
            device_item.setTextAlignment(Qt.AlignCenter)
            self.failure_table.setItem(row, 5, device_item)
    
    def load_trends_data(self):
        """بارگذاری داده‌های روند"""
        try:
            start_date = self.current_filters['start_date_gregorian']
            end_date = self.current_filters['end_date_gregorian']
            
            group_by_text = self.trend_group_combo.currentText()
            
            if group_by_text == "روز":
                query = """
                SELECT 
                    DATE(rep.repair_date) as period,
                    COUNT(rep.id) as repair_count,
                    SUM(CASE WHEN rep.status = 'تمام شده' THEN 1 ELSE 0 END) as completed_count,
                    SUM(rep.total_cost) as total_revenue,
                    SUM(rep.labor_cost) as total_labor,
                    AVG(rep.total_cost) as avg_revenue
                FROM Repairs rep
                LEFT JOIN Receptions rec ON rep.reception_id = rec.id
                WHERE rec.reception_date >= ? AND rec.reception_date <= ?
                GROUP BY DATE(rep.repair_date)
                ORDER BY period
                """
            elif group_by_text == "هفته":
                query = """
                SELECT 
                    strftime('%Y-%W', rep.repair_date) as period,
                    COUNT(rep.id) as repair_count,
                    SUM(CASE WHEN rep.status = 'تمام شده' THEN 1 ELSE 0 END) as completed_count,
                    SUM(rep.total_cost) as total_revenue,
                    SUM(rep.labor_cost) as total_labor,
                    AVG(rep.total_cost) as avg_revenue
                FROM Repairs rep
                LEFT JOIN Receptions rec ON rep.reception_id = rec.id
                WHERE rec.reception_date >= ? AND rec.reception_date <= ?
                GROUP BY strftime('%Y-%W', rep.repair_date)
                ORDER BY period
                """
            else:  # ماه
                query = """
                SELECT 
                    strftime('%Y-%m', rep.repair_date) as period,
                    COUNT(rep.id) as repair_count,
                    SUM(CASE WHEN rep.status = 'تمام شده' THEN 1 ELSE 0 END) as completed_count,
                    SUM(rep.total_cost) as total_revenue,
                    SUM(rep.labor_cost) as total_labor,
                    AVG(rep.total_cost) as avg_revenue
                FROM Repairs rep
                LEFT JOIN Receptions rec ON rep.reception_id = rec.id
                WHERE rec.reception_date >= ? AND rec.reception_date <= ?
                GROUP BY strftime('%Y-%m', rep.repair_date)
                ORDER BY period
                """
            
            trends = self.data_manager.db.fetch_all(query, (start_date, end_date)) or []
            self.update_trends_table(trends, group_by_text)
            
        except Exception as e:
            print(f"خطا در بارگذاری داده‌های روند: {e}")
    
    def update_trends_table(self, trends, group_by):
        """به‌روزرسانی جدول روندها"""
        self.trends_table.setRowCount(len(trends))
        
        for row, trend in enumerate(trends):
            # دوره
            period = trend.get('period', '')
            # تبدیل به شمسی اگر تاریخ است
            if '-' in str(period) and len(str(period).split('-')) == 3:
                period = gregorian_to_jalali(str(period))
            period_item = QTableWidgetItem(str(period))
            period_item.setTextAlignment(Qt.AlignCenter)
            self.trends_table.setItem(row, 0, period_item)
            
            # تعداد تعمیر
            count_item = QTableWidgetItem(str(trend.get('repair_count', 0)))
            count_item.setTextAlignment(Qt.AlignCenter)
            self.trends_table.setItem(row, 1, count_item)
            
            # تکمیل شده
            completed_item = QTableWidgetItem(str(trend.get('completed_count', 0)))
            completed_item.setTextAlignment(Qt.AlignCenter)
            self.trends_table.setItem(row, 2, completed_item)
            
            # درآمد کل (تبدیل به تومان)
            revenue = trend.get('total_revenue', 0)
            revenue_toman = revenue / 10 if revenue else 0
            revenue_item = QTableWidgetItem(f"{revenue_toman:,.0f} تومان")
            revenue_item.setTextAlignment(Qt.AlignCenter)
            self.trends_table.setItem(row, 3, revenue_item)
            
            # دستمزد کل
            labor = trend.get('total_labor', 0)
            labor_toman = labor / 10 if labor else 0
            labor_item = QTableWidgetItem(f"{labor_toman:,.0f} تومان")
            labor_item.setTextAlignment(Qt.AlignCenter)
            self.trends_table.setItem(row, 4, labor_item)
            
            # میانگین درآمد
            avg_revenue = trend.get('avg_revenue', 0)
            avg_revenue_toman = avg_revenue / 10 if avg_revenue else 0
            avg_revenue_item = QTableWidgetItem(f"{avg_revenue_toman:,.0f} تومان")
            avg_revenue_item.setTextAlignment(Qt.AlignCenter)
            self.trends_table.setItem(row, 5, avg_revenue_item)
    
    def update_devices_table(self, devices):
        """به‌روزرسانی جدول دستگاه‌ها"""
        self.devices_table.setRowCount(len(devices))
        
        for row, device in enumerate(devices):
            # نوع دستگاه
            device_type = device.get('device_type', 'نامشخص')
            device_item = QTableWidgetItem(device_type)
            device_item.setTextAlignment(Qt.AlignCenter)
            self.devices_table.setItem(row, 0, device_item)
            
            # تعداد تعمیر
            count_item = QTableWidgetItem(str(device.get('repair_count', 0)))
            count_item.setTextAlignment(Qt.AlignCenter)
            self.devices_table.setItem(row, 1, count_item)
            
            # درآمد کل (تبدیل به تومان)
            revenue = device.get('total_revenue', 0)
            revenue_toman = revenue / 10 if revenue else 0
            revenue_item = QTableWidgetItem(f"{revenue_toman:,.0f} تومان")
            revenue_item.setTextAlignment(Qt.AlignCenter)
            self.devices_table.setItem(row, 2, revenue_item)
            
            # میانگین درآمد
            avg_revenue = device.get('avg_revenue', 0)
            avg_revenue_toman = avg_revenue / 10 if avg_revenue else 0
            avg_revenue_item = QTableWidgetItem(f"{avg_revenue_toman:,.0f} تومان")
            avg_revenue_item.setTextAlignment(Qt.AlignCenter)
            self.devices_table.setItem(row, 3, avg_revenue_item)
            
            # دستمزد کل
            labor = device.get('total_labor', 0)
            labor_toman = labor / 10 if labor else 0
            labor_item = QTableWidgetItem(f"{labor_toman:,.0f} تومان")
            labor_item.setTextAlignment(Qt.AlignCenter)
            self.devices_table.setItem(row, 4, labor_item)
            
            # میانگین دستمزد
            avg_labor = device.get('avg_labor', 0)
            avg_labor_toman = avg_labor / 10 if avg_labor else 0
            avg_labor_item = QTableWidgetItem(f"{avg_labor_toman:,.0f} تومان")
            avg_labor_item.setTextAlignment(Qt.AlignCenter)
            self.devices_table.setItem(row, 5, avg_labor_item)
            
            # تعمیرکاران
            tech_count = device.get('technician_count', 0)
            tech_item = QTableWidgetItem(str(tech_count))
            tech_item.setTextAlignment(Qt.AlignCenter)
            self.devices_table.setItem(row, 6, tech_item)
            
            # نرخ تکمیل (محاسبه فرضی)
            completion_rate = "80%"  # در نسخه واقعی از دیتابیس محاسبه می‌شود
            rate_item = QTableWidgetItem(completion_rate)
            rate_item.setTextAlignment(Qt.AlignCenter)
            self.devices_table.setItem(row, 7, rate_item)
    
    def update_parts_table(self, parts):
        """به‌روزرسانی جدول قطعات"""
        self.parts_table.setRowCount(len(parts))
        
        for row, part in enumerate(parts):
            # نام قطعه
            name_item = QTableWidgetItem(part.get('part_name', 'نامشخص'))
            name_item.setTextAlignment(Qt.AlignCenter)
            self.parts_table.setItem(row, 0, name_item)
            
            # کد
            code_item = QTableWidgetItem(part.get('part_code', ''))
            code_item.setTextAlignment(Qt.AlignCenter)
            self.parts_table.setItem(row, 1, code_item)
            
            # دسته
            category_item = QTableWidgetItem(part.get('category', ''))
            category_item.setTextAlignment(Qt.AlignCenter)
            self.parts_table.setItem(row, 2, category_item)
            
            # برند
            brand_item = QTableWidgetItem(part.get('brand', ''))
            brand_item.setTextAlignment(Qt.AlignCenter)
            self.parts_table.setItem(row, 3, brand_item)
            
            # تعداد مصرف
            qty_item = QTableWidgetItem(str(part.get('total_quantity', 0)))
            qty_item.setTextAlignment(Qt.AlignCenter)
            self.parts_table.setItem(row, 4, qty_item)
            
            # هزینه کل (تبدیل به تومان)
            cost = part.get('total_cost', 0)
            cost_toman = cost / 10 if cost else 0
            cost_item = QTableWidgetItem(f"{cost_toman:,.0f} تومان")
            cost_item.setTextAlignment(Qt.AlignCenter)
            self.parts_table.setItem(row, 5, cost_item)
            
            # تعداد تعمیرات
            repair_count_item = QTableWidgetItem(str(part.get('repair_count', 0)))
            repair_count_item.setTextAlignment(Qt.AlignCenter)
            self.parts_table.setItem(row, 6, repair_count_item)
    
    def update_services_table(self, services):
        """به‌روزرسانی جدول خدمات"""
        self.services_table.setRowCount(len(services))
        
        for row, service in enumerate(services):
            # نام خدمت
            name_item = QTableWidgetItem(service.get('service_name', 'نامشخص'))
            name_item.setTextAlignment(Qt.AlignCenter)
            self.services_table.setItem(row, 0, name_item)
            
            # کد
            code_item = QTableWidgetItem(service.get('service_code', ''))
            code_item.setTextAlignment(Qt.AlignCenter)
            self.services_table.setItem(row, 1, code_item)
            
            # دسته
            category_item = QTableWidgetItem(service.get('category', ''))
            category_item.setTextAlignment(Qt.AlignCenter)
            self.services_table.setItem(row, 2, category_item)
            
            # تعداد ارائه
            qty_item = QTableWidgetItem(str(service.get('total_quantity', 0)))
            qty_item.setTextAlignment(Qt.AlignCenter)
            self.services_table.setItem(row, 3, qty_item)
            
            # درآمد کل (تبدیل به تومان)
            revenue = service.get('total_revenue', 0)
            revenue_toman = revenue / 10 if revenue else 0
            revenue_item = QTableWidgetItem(f"{revenue_toman:,.0f} تومان")
            revenue_item.setTextAlignment(Qt.AlignCenter)
            self.services_table.setItem(row, 4, revenue_item)
            
            # تعداد تعمیرات
            repair_count_item = QTableWidgetItem(str(service.get('repair_count', 0)))
            repair_count_item.setTextAlignment(Qt.AlignCenter)
            self.services_table.setItem(row, 5, repair_count_item)
    
    def update_time_table(self, time_analysis):
        """به‌روزرسانی جدول تحلیل زمان"""
        self.time_table.setRowCount(len(time_analysis))
        
        for row, item in enumerate(time_analysis):
            # بازه زمانی
            duration_item = QTableWidgetItem(item.get('duration_category', ''))
            duration_item.setTextAlignment(Qt.AlignCenter)
            self.time_table.setItem(row, 0, duration_item)
            
            # تعداد تعمیر
            count_item = QTableWidgetItem(str(item.get('repair_count', 0)))
            count_item.setTextAlignment(Qt.AlignCenter)
            self.time_table.setItem(row, 1, count_item)
            
            # میانگین هزینه (تبدیل به تومان)
            avg_cost = item.get('avg_cost', 0)
            avg_cost_toman = avg_cost / 10 if avg_cost else 0
            avg_cost_item = QTableWidgetItem(f"{avg_cost_toman:,.0f} تومان")
            avg_cost_item.setTextAlignment(Qt.AlignCenter)
            self.time_table.setItem(row, 2, avg_cost_item)
            
            # هزینه کل
            total_cost = item.get('total_cost', 0)
            total_cost_toman = total_cost / 10 if total_cost else 0
            total_cost_item = QTableWidgetItem(f"{total_cost_toman:,.0f} تومان")
            total_cost_item.setTextAlignment(Qt.AlignCenter)
            self.time_table.setItem(row, 3, total_cost_item)
            
            # میانگین دستمزد
            avg_labor = item.get('avg_labor', 0)
            avg_labor_toman = avg_labor / 10 if avg_labor else 0
            avg_labor_item = QTableWidgetItem(f"{avg_labor_toman:,.0f} تومان")
            avg_labor_item.setTextAlignment(Qt.AlignCenter)
            self.time_table.setItem(row, 4, avg_labor_item)
            
            # میانگین روز
            avg_days = item.get('avg_days', 0)
            days_item = QTableWidgetItem(f"{avg_days:,.1f} روز")
            days_item.setTextAlignment(Qt.AlignCenter)
            self.time_table.setItem(row, 5, days_item)
    
    def load_quick_stats(self):
        """بارگذاری آمار سریع"""
        try:
            # آمار امروز
            today_jalali = jdatetime.date.today()
            today_str = today_jalali.strftime("%Y/%m/%d")
            today_gregorian = jalali_to_gregorian(today_str)
            
            # آمار ماه
            first_of_month = jdatetime.date(today_jalali.year, today_jalali.month, 1)
            month_start_str = first_of_month.strftime("%Y/%m/%d")
            month_start_gregorian = jalali_to_gregorian(month_start_str)
            
            # تعمیرات امروز
            today_stats = self.get_repair_summary_data(today_gregorian, today_gregorian)
            today_count = today_stats.get('total_repairs', 0)
            self.quick_stats_labels[0].setText(str(today_count))
            
            # تعمیرات ماه
            month_stats = self.get_repair_summary_data(month_start_gregorian, today_gregorian)
            month_count = month_stats.get('total_repairs', 0)
            self.quick_stats_labels[1].setText(str(month_count))
            
            # تعمیرکاران فعال
            technicians = self.get_technician_performance_data(month_start_gregorian, today_gregorian)
            active_techs = len([t for t in technicians if t.get('repair_count', 0) > 0])
            self.quick_stats_labels[2].setText(str(active_techs))
            
            # میانگین هزینه
            avg_cost = month_stats.get('avg_cost', 0)
            avg_cost_toman = avg_cost / 10 if avg_cost else 0
            self.quick_stats_labels[3].setText(f"{avg_cost_toman:,.0f}")
            
        except Exception as e:
            print(f"خطا در بارگذاری آمار سریع: {e}")
    
    def export_report(self):
        """صدور خروجی Excel از گزارش"""
        try:
            from PySide6.QtWidgets import QMessageBox, QFileDialog
            import pandas as pd
            
            # درخواست مسیر ذخیره فایل
            file_path, _ = QFileDialog.getSaveFileName(
                self, "ذخیره گزارش Excel", 
                f"گزارش_تعمیرات_{jdatetime.date.today().strftime('%Y%m%d')}.xlsx",
                "Excel Files (*.xlsx);;All Files (*)"
            )
            
            if not file_path:
                return
            
            # اگر مسیر فایل پسوند .xlsx ندارد، اضافه کن
            if not file_path.endswith('.xlsx'):
                file_path += '.xlsx'
            
            QMessageBox.information(
                self, "در حال توسعه", 
                "این ویژگی در حال توسعه است و به زودی اضافه خواهد شد."
            )
            
        except ImportError:
            QMessageBox.warning(
                self, "خطا", 
                "برای خروجی Excel نیاز به نصب کتابخانه pandas و openpyxl است.\n"
                "لطفا با دستور زیر نصب کنید:\n"
                "pip install pandas openpyxl"
            )
        except Exception as e:
            QMessageBox.critical(self, "خطا در خروجی", f"خطا در ایجاد فایل Excel:\n{str(e)}")
    
    def run_date_conversion_test(self):
        """اجرای تست تبدیل تاریخ"""
        try:
            # تست تبدیل تاریخ‌های مختلف
            test_cases = [
                ("1403/01/01", "شمسی"),
                ("1404/11/15", "شمسی"),
                ("2025-01-15", "میلادی"),
                ("2025/01/15", "میلادی"),
                ("", "خالی"),
            ]
            
            results = []
            
            for test_date, date_type in test_cases:
                try:
                    if date_type == "شمسی":
                        gregorian = jalali_to_gregorian(test_date)
                        back_to_jalali = gregorian_to_jalali(gregorian) if gregorian else "خطا"
                        results.append(f"📅 {test_date} (شمسی) → {gregorian} (میلادی) → {back_to_jalali} (برگشت)")
                    elif date_type == "میلادی":
                        jalali = gregorian_to_jalali(test_date)
                        results.append(f"📅 {test_date} (میلادی) → {jalali} (شمسی)")
                    else:
                        results.append(f"📅 {test_date}: تاریخ {date_type}")
                except Exception as e:
                    results.append(f"❌ {test_date}: خطا - {str(e)}")
            
            # نمایش نتایج
            message = "نتایج تست تبدیل تاریخ:\n\n" + "\n".join(results)
            QMessageBox.information(self, "نتایج تست تاریخ", message)
            
        except Exception as e:
            QMessageBox.critical(self, "خطا در تست", f"خطا در اجرای تست:\n{str(e)}")
    
    def test_database_queries(self):
        """تست کوئری‌های دیتابیس"""
        try:
            # تاریخ امروز شمسی
            today_jalali = jdatetime.date.today()
            today_str = today_jalali.strftime("%Y/%m/%d")
            today_gregorian = jalali_to_gregorian(today_str)
            
            # تاریخ یک ماه پیش
            one_month_ago = today_jalali - jdatetime.timedelta(days=30)
            one_month_ago_str = one_month_ago.strftime("%Y/%m/%d")
            one_month_ago_gregorian = jalali_to_gregorian(one_month_ago_str)
            
            # تست کوئری‌ها
            tests = [
                ("خلاصه گزارش", self.get_repair_summary_data, (one_month_ago_gregorian, today_gregorian)),
                ("آخرین تعمیرات", self.get_recent_repairs_data, (one_month_ago_gregorian, today_gregorian)),
                ("تعمیرکاران", self.get_technician_performance_data, (one_month_ago_gregorian, today_gregorian)),
                ("دستگاه‌ها", self.get_device_type_analysis_data, (one_month_ago_gregorian, today_gregorian)),
            ]
            
            results = []
            
            for test_name, test_func, params in tests:
                try:
                    data = test_func(*params)
                    count = len(data) if isinstance(data, list) else 1
                    results.append(f"✅ {test_name}: {count} رکورد")
                except Exception as e:
                    results.append(f"❌ {test_name}: خطا - {str(e)[:50]}...")
            
            # بررسی جداول دیتابیس
            try:
                tables_query = "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
                tables = self.data_manager.db.fetch_all(tables_query)
                table_list = ", ".join([t['name'] for t in tables[:10]]) + (f" ... و {len(tables)-10} جدول دیگر" if len(tables) > 10 else "")
                results.append(f"📊 تعداد جداول: {len(tables)} ({table_list})")
            except:
                results.append("⚠️ خطا در دریافت لیست جداول")
            
            # نمایش نتایج
            message = "نتایج تست کوئری‌های دیتابیس:\n\n" + "\n".join(results)
            QMessageBox.information(self, "نتایج تست دیتابیس", message)
            
        except Exception as e:
            QMessageBox.critical(self, "خطا در تست", f"خطا در اجرای تست کوئری‌ها:\n{str(e)}")


# تست فرم
if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication
    import sys
    
    app = QApplication(sys.argv)
    
    # تنظیم فونت فارسی
    font = QFont("B Nazanin", 11)
    app.setFont(font)
    
    # ساخت DataManager ساختگی برای تست
    class MockDataManager:
        class db:
            @staticmethod
            def fetch_one(query, params=()):
                print(f"fetch_one: {query[:50]}...")
                print(f"  پارامترها: {params}")
                if "COUNT(*)" in query or "COUNT(rep.id)" in query:
                    return {
                        'total_repairs': 25, 'completed': 18, 'in_progress': 5, 'cancelled': 2,
                        'avg_cost': 250000, 'total_cost': 6250000, 'avg_labor': 80000, 
                        'total_labor': 2000000, 'internal_repairs': 20, 'external_repairs': 5
                    }
                return {}
            
            @staticmethod
            def fetch_all(query, params=()):
                print(f"fetch_all: {query[:50]}...")
                print(f"  پارامترها: {params}")
                if "technician" in query.lower():
                    return [
                        {'technician_id': 1, 'technician_name': 'احمد احمدی', 'repair_count': 10, 
                         'total_revenue': 3000000, 'avg_revenue': 300000, 'total_labor': 800000, 
                         'avg_labor': 80000, 'completed_count': 8, 'avg_hours': 4.5,
                         'first_repair': '2024-05-01', 'last_repair': '2024-05-15'},
                        {'technician_id': 2, 'technician_name': 'رضا رضایی', 'repair_count': 8, 
                         'total_revenue': 2000000, 'avg_revenue': 250000, 'total_labor': 600000, 
                         'avg_labor': 75000, 'completed_count': 6, 'avg_hours': 3.8,
                         'first_repair': '2024-05-03', 'last_repair': '2024-05-14'},
                        {'technician_id': 3, 'technician_name': 'محمد محمدی', 'repair_count': 7, 
                         'total_revenue': 1250000, 'avg_revenue': 178571, 'total_labor': 600000, 
                         'avg_labor': 85714, 'completed_count': 4, 'avg_hours': 5.2,
                         'first_repair': '2024-04-28', 'last_repair': '2024-05-13'}
                    ]
                elif "failure" in query.lower() or "problem_description" in query:
                    return [
                        {'problem_description': 'عدم سرمادهی یخچال', 'count': 8, 
                         'avg_repair_cost': 300000, 'avg_labor_cost': 100000,
                         'total_cost': 2400000, 'device_type': 'یخچال', 'brand': 'سامسونگ'},
                        {'problem_description': 'نشتی آب ماشین لباسشویی', 'count': 6, 
                         'avg_repair_cost': 200000, 'avg_labor_cost': 80000,
                         'total_cost': 1200000, 'device_type': 'ماشین لباسشویی', 'brand': 'ال جی'},
                        {'problem_description': 'خرابی برد الکترونیکی', 'count': 5, 
                         'avg_repair_cost': 450000, 'avg_labor_cost': 120000,
                         'total_cost': 2250000, 'device_type': 'یخچال', 'brand': 'ایران راد'}
                    ]
                elif "recent" in query.lower() or "Repairs rep" in query:
                    return [
                        {'id': 1, 'repair_date': '2024-05-15', 'reception_number': 'REC001',
                         'device_model': 'مدل A', 'technician_name': 'احمد احمدی', 
                         'total_cost': 350000, 'status': 'تمام شده', 'repair_type': 'داخلی',
                         'device_type': 'یخچال', 'brand': 'سامسونگ'},
                        {'id': 2, 'repair_date': '2024-05-14', 'reception_number': 'REC002',
                         'device_model': 'مدل B', 'technician_name': 'رضا رضایی', 
                         'total_cost': 280000, 'status': 'شروع شده', 'repair_type': 'داخلی',
                         'device_type': 'ماشین لباسشویی', 'brand': 'ال جی'},
                        {'id': 3, 'repair_date': '2024-05-13', 'reception_number': 'REC003',
                         'device_model': 'مدل C', 'technician_name': 'محمد محمدی', 
                         'total_cost': 420000, 'status': 'تمام شده', 'repair_type': 'بیرون سپاری',
                         'device_type': 'جاروبرقی', 'brand': 'پاناسونیک'}
                    ]
                elif "device_type" in query.lower():
                    return [
                        {'device_type': 'یخچال', 'repair_count': 15, 'total_revenue': 4500000, 
                         'avg_revenue': 300000, 'total_labor': 1200000, 'avg_labor': 80000, 
                         'technician_count': 3},
                        {'device_type': 'ماشین لباسشویی', 'repair_count': 8, 'total_revenue': 2000000, 
                         'avg_revenue': 250000, 'total_labor': 600000, 'avg_labor': 75000, 
                         'technician_count': 2},
                        {'device_type': 'جاروبرقی', 'repair_count': 5, 'total_revenue': 1250000, 
                         'avg_revenue': 250000, 'total_labor': 400000, 'avg_labor': 80000, 
                         'technician_count': 2}
                    ]
                else:
                    return []
    
    data_manager = MockDataManager()
    
    form = RepairReportForm(data_manager)
    form.setWindowTitle("گزارش تعمیرات - نسخه کامل و اصلاح شده")
    form.resize(1200, 800)
    form.show()
    
    sys.exit(app.exec())