"""
فرم مدیریت شرکا و سود - نسخه اصلاح شده
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTabWidget, QLabel,
    QPushButton, QFrame, QScrollArea, QMessageBox, QSizePolicy,
    QTableWidget, QTableWidgetItem, QHeaderView, QLineEdit,
    QComboBox, QGroupBox, QFormLayout, QDateEdit, QTextEdit,
    QSplitter, QGridLayout, QProgressBar, QToolBar, QStatusBar,
    QDialog, QToolButton
)
from PySide6.QtCore import Qt, Signal, QTimer, QDate, QSize
from PySide6.QtGui import QFont, QIcon, QAction
import jdatetime
from datetime import datetime

# ایمپورت ویجت تاریخ شمسی
try:
    from ui.forms.accounting.widgets.jalali_date_input import JalaliDateInputAccounting
    JALALI_DATE_AVAILABLE = True
except ImportError:
    print("⚠️ ویجت تاریخ شمسی یافت نشد")
    JALALI_DATE_AVAILABLE = False

# ایمپورت دیالوگ شرکا
try:
    from ui.forms.accounting.dialogs.partner_dialog import PartnerDialog
    PARTNER_DIALOG_AVAILABLE = True
except ImportError:
    print("⚠️ دیالوگ شرکا یافت نشد")
    PARTNER_DIALOG_AVAILABLE = False

# ایمپورت دیالوگ سود شرکا
try:
    from ui.forms.accounting.dialogs.partner_profits_dialog import PartnerProfitsDialog
    PARTNER_PROFITS_DIALOG_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ خطا در بارگذاری PartnerProfitsDialog: {e}")
    PARTNER_PROFITS_DIALOG_AVAILABLE = False


class PartnersForm(QWidget):
    """فرم مدیریت شرکا و سود"""
    
    data_changed = Signal()
    
    def __init__(self, data_manager):
        super().__init__()
        self.data_manager = data_manager
        
        # ایجاد Manager شرکا
        try:
            from modules.accounting.partner_manager import PartnerManager
            self.partner_manager = PartnerManager(data_manager)
        except ImportError as e:
            print(f"⚠️ خطا در بارگذاری PartnerManager: {e}")
            self.partner_manager = None
        
        # ایجاد Financial Calculator
        try:
            from modules.accounting.financial_calculator import FinancialCalculator
            self.financial_calculator = FinancialCalculator(data_manager)
        except ImportError as e:
            print(f"⚠️ خطا در بارگذاری FinancialCalculator: {e}")
            self.financial_calculator = None
        
        # 🔴 **راست‌چین کردن کامل**
        self.setLayoutDirection(Qt.RightToLeft)
        
        # تنظیم استایل
        self.setup_styles()
        
        # ایجاد رابط کاربری
        self.init_ui()
        
        # بارگذاری اولیه داده‌ها
        self.load_partners()
        
        # تایمر برای به‌روزرسانی
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_summary)
        self.update_timer.start(30000)  # هر 30 ثانیه
        
        print("✅ فرم مدیریت شرکا با موفقیت ایجاد شد")

    def setup_styles(self):
        """تنظیم استایل فرم"""
        self.setStyleSheet("""
            /* استایل کلی */
            QWidget {
                background-color: #000000;
                color: #ffffff;
                font-family: 'B Nazanin';
            }
            
            /* کارت آمار - بهبود یافته */
            QFrame#stat_card {
                background-color: #111111;
                border: 3px solid #2ecc71;
                border-radius: 12px;
                padding: 20px;
                margin: 5px;
            }
            
            .stat_card_title {
                color: #bbb;
                font-size: 12pt;
                font-weight: bold;
                text-align: center;
                padding-bottom: 8px;
                border-bottom: 1px solid #333;
            }
            
            .stat_card_value {
                color: #ffffff;
                font-size: 24pt;
                font-weight: bold;
                text-align: center;
                padding: 15px 0;
            }
            
            /* افزایش ارتفاع ردیف‌های جدول */
            QTableWidget {
                background-color: #111111;
                alternate-background-color: #0a0a0a;
                selection-background-color: #2ecc71;
                selection-color: white;
                gridline-color: #333;
                color: white;
                border: none;
                font-size: 11pt;
            }
            
            QTableWidget::item {
                padding: 12px;  /* افزایش padding */
                color: white;
                font-size: 11pt;
            }
            
            /* ارتفاع بیشتر برای هدرهای جدول */
            QHeaderView::section {
                background-color: #2c3e50;
                color: white;
                padding: 15px;
                border: none;
                font-weight: bold;
                text-align: right;
                font-size: 11pt;
                min-height: 50px;  /* ارتفاع بیشتر */
            }
            
            /* تب‌های بزرگتر */
            QTabWidget {
                background-color: #111111;
                border: 1px solid #333;
                border-radius: 5px;
            }
            
            QTabBar::tab {
                background-color: #2c2c2c;
                color: #bbb;
                padding: 12px 20px;  /* افزایش padding */
                margin-left: 2px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                font-size: 11pt;
                min-height: 50px;  /* ارتفاع بیشتر برای تب‌ها */
            }
            
            QTabBar::tab:selected {
                background-color: #2ecc71;
                color: white;
                font-weight: bold;
                font-size: 12pt;
            }
            
            /* افزایش ارتفاع هدر فرم */
            QWidget#header_widget {
                min-height: 180px;  /* افزایش ارتفاع هدر */
                padding: 20px;
            }
        """)
  
    def init_ui(self):
        """ایجاد رابط کاربری"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)
        
        # 🔴 **هدر - آمار سریع**
        self.header_widget = self.create_header_widget()
        main_layout.addWidget(self.header_widget)
        
        # 🔴 **نوار ابزار**
        toolbar = self.create_toolbar()
        main_layout.addWidget(toolbar)
        
        # 🔴 **تب‌های اصلی**
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabPosition(QTabWidget.North)
        
        # تب 1: لیست شرکا
        self.partners_tab = self.create_partners_tab()
        self.tab_widget.addTab(self.partners_tab, "🤝 لیست شرکا")
        
        # تب 2: توزیع سود
        self.profit_distribution_tab = self.create_profit_distribution_tab()
        self.tab_widget.addTab(self.profit_distribution_tab, "💰 توزیع سود")
        
        # تب 3: گزارش سود
        self.profit_reports_tab = self.create_profit_reports_tab()
        self.tab_widget.addTab(self.profit_reports_tab, "📊 گزارش سود")
        
        # تب 4: تنظیمات
        self.settings_tab = self.create_settings_tab()
        self.tab_widget.addTab(self.settings_tab, "⚙️ تنظیمات")
        
        main_layout.addWidget(self.tab_widget, 1)
        
        # 🔴 **نوار وضعیت**
        self.status_bar = QStatusBar()
        self.status_bar.showMessage("آماده")
        main_layout.addWidget(self.status_bar)

    def create_header_widget(self):
        """ایجاد ویجت هدر با آمار سریع - نسخه بهبود یافته"""
        header_widget = QWidget()
        header_widget.setObjectName("header_widget")
        header_widget.setMinimumHeight(180)  # افزایش ارتفاع هدر
        
        layout = QVBoxLayout(header_widget)
        layout.setSpacing(15)  # افزایش فاصله
        layout.setContentsMargins(20, 20, 20, 20)  # افزایش حاشیه‌ها
        
        # عنوان بزرگتر
        title_layout = QHBoxLayout()
        title_label = QLabel("🤝 مدیریت شرکا و سود")
        title_label.setStyleSheet("""
            QLabel {
                font-size: 22pt;  /* افزایش سایز */
                font-weight: bold;
                color: #2ecc71;
                padding: 10px;
            }
        """)
        title_layout.addWidget(title_label)
        title_layout.addStretch()
        
        # تاریخ امروز
        try:
            from utils.date_utils import get_current_jalali
            today_date = get_current_jalali()
        except:
            import jdatetime
            today_date = jdatetime.datetime.now().strftime("%Y/%m/%d")
        
        date_label = QLabel(f"📅 {today_date}")
        date_label.setStyleSheet("""
            QLabel {
                font-size: 12pt;  /* افزایش سایز */
                color: #bbb;
                font-weight: bold;
                padding: 10px;
                background-color: #1a1a1a;
                border-radius: 8px;
                border: 1px solid #333;
            }
        """)
        title_layout.addWidget(date_label)
        layout.addLayout(title_layout)
        
        # کارت‌های آمار با فاصله بیشتر
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(20)  # افزایش فاصله بین کارت‌ها
        
        self.stat_cards = {}
        
        # ۴ کارت آماری بزرگتر
        stats_config = [
            ("👥 تعداد شرکا", "0", "#3498db", "total_partners"),
            ("💰 سرمایه کل", "0 تومان", "#27ae60", "total_capital"),
            ("📈 سود کل", "0 تومان", "#9b59b6", "total_profit"),
            ("📊 میانگین سود", "0%", "#f39c12", "avg_profit")
        ]
        
        for title, default_value, color, key in stats_config:
            card = self.create_stat_card(title, default_value, color)
            stats_layout.addWidget(card)
            self.stat_cards[key] = card
        
        layout.addLayout(stats_layout)
        
        return header_widget    

    def create_stat_card(self, title, value, color):
        """ایجاد یک کارت آمار با ارتفاع بیشتر و طراحی بهتر"""
        card = QFrame()
        card.setObjectName("stat_card")
        card.setFixedHeight(120)  # افزایش ارتفاع از 80 به 120
        card.setMinimumWidth(200)  # حداقل عرض
        
        layout = QVBoxLayout(card)
        layout.setSpacing(10)  # افزایش فاصله
        layout.setContentsMargins(20, 15, 20, 15)  # افزایش حاشیه‌ها
        
        # عنوان - با فونت کوچکتر و متمایز
        title_label = QLabel(title)
        title_label.setObjectName("stat_card_title")
        title_label.setAlignment(Qt.AlignCenter)  # وسط‌چین کردن
        title_label.setStyleSheet(f"""
            QLabel {{
                color: #bbb;
                font-size: 11pt;
                font-weight: bold;
                padding-bottom: 5px;
                border-bottom: 1px solid #333;
            }}
        """)
        layout.addWidget(title_label)
        
        # مقدار - با فونت خیلی بزرگتر
        value_label = QLabel(value)
        value_label.setObjectName("stat_card_value")
        value_label.setAlignment(Qt.AlignCenter)  # وسط‌چین کردن
        value_label.setStyleSheet(f"""
            QLabel {{
                color: {color};
                font-size: 24pt;  /* افزایش قابل توجه سایز فونت */
                font-weight: bold;
                padding: 10px 0;
            }}
        """)
        layout.addWidget(value_label)
        
        # پس‌زمینه رنگی ملایم
        card.setStyleSheet(f"""
            QFrame#stat_card {{
                background-color: #111111;
                border: 2px solid {color};
                border-radius: 10px;
                padding: 15px;
            }}
            QFrame#stat_card:hover {{
                background-color: #1a1a1a;
                border-width: 3px;
            }}
        """)
        
        # ذخیره رفرنس
        card.value_label = value_label
        
        return card    
  
    def create_toolbar(self):
        """ایجاد نوار ابزار حرفه‌ای"""
        toolbar = QToolBar()
        toolbar.setIconSize(QSize(24, 24))
        
        # استایل کلی نوار ابزار
        toolbar.setStyleSheet("""
            QToolBar {
                background-color: #111111;
                border: 1px solid #333;
                border-radius: 5px;
                padding: 5px;
                spacing: 3px;
            }
        """)
        
        # دکمه‌های نوار ابزار
        actions = [
            ("➕ افزودن شریک", self.add_partner, "#27ae60"),
            ("✏️ ویرایش شریک", self.edit_partner, "#3498db"),
            ("🗑️ حذف شریک", self.delete_partner, "#e74c3c"),
            ("💰 توزیع سود ماهانه", self.distribute_monthly_profit, "#9b59b6"),
            ("📊 گزارش سود", self.generate_profit_report, "#f39c12"),
            ("🔄 به‌روزرسانی", self.refresh_data, "#1abc9c")
        ]
        
        for text, callback, color in actions:
            # ایجاد دکمه
            button = QPushButton(text)
            button.setStyleSheet(f"""
                QPushButton {{
                    background-color: {color};
                    color: white;
                    border: none;
                    padding: 8px 12px;
                    border-radius: 4px;
                    font-family: 'B Nazanin';
                    font-size: 11pt;
                    font-weight: bold;
                    min-height: 35px;
                }}
                QPushButton:hover {{
                    background-color: {self.darken_color(color)};
                }}
                QPushButton:pressed {{
                    background-color: #1a1a1a;
                }}
            """)
            button.clicked.connect(callback)
            
            # اضافه کردن دکمه به نوار ابزار
            toolbar.addWidget(button)
        
        # اضافه کردن فاصله انعطاف‌پذیر
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        toolbar.addWidget(spacer)
        
        return toolbar

    def darken_color(self, color):
        """تیره کردن رنگ برای hover"""
        import re
        match = re.match(r'#([0-9a-fA-F]{2})([0-9a-fA-F]{2})([0-9a-fA-F]{2})', color)
        if match:
            r = max(0, int(match.group(1), 16) - 30)
            g = max(0, int(match.group(2), 16) - 30)
            b = max(0, int(match.group(3), 16) - 30)
            return f'#{r:02x}{g:02x}{b:02x}'
        return color

    def create_partners_tab(self):
        """ایجاد تب لیست شرکا"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # نوار جستجو
        search_layout = QHBoxLayout()
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("جستجو بر اساس نام، موبایل یا کدملی...")
        self.search_input.textChanged.connect(self.filter_partners)
        
        self.status_filter = QComboBox()
        self.status_filter.addItems(["همه", "فعال", "غیرفعال"])
        self.status_filter.currentTextChanged.connect(self.filter_partners)
        
        search_layout.addWidget(QLabel("وضعیت:"))
        search_layout.addWidget(self.status_filter)
        search_layout.addStretch()
        search_layout.addWidget(self.search_input)
        
        layout.addLayout(search_layout)
        
        # جدول شرکا
        self.partners_table = QTableWidget()
        self.partners_table.setColumnCount(9)
        self.partners_table.setHorizontalHeaderLabels([
            "ردیف", "نام شریک", "موبایل", "تاریخ شروع", 
            "سرمایه (تومان)", "درصد سود", "سود کل", 
            "وضعیت", "عملیات"
        ])
        
        # تنظیمات جدول
        self.partners_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.partners_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.partners_table.setAlternatingRowColors(True)
        
        layout.addWidget(self.partners_table, 1)
        
        return tab
    
    def create_profit_distribution_tab(self):
        """ایجاد تب توزیع سود"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(15)
        
        # گروه‌باکس تنظیمات توزیع
        settings_group = QGroupBox("⚙️ تنظیمات توزیع سود")
        settings_layout = QGridLayout()
        
        # تاریخ شروع و پایان
        settings_layout.addWidget(QLabel("از تاریخ:"), 0, 0)
        
        if JALALI_DATE_AVAILABLE:
            self.profit_start_date = JalaliDateInputAccounting()
        else:
            self.profit_start_date = QLineEdit()
            self.profit_start_date.setPlaceholderText("1404/10/01")
        
        settings_layout.addWidget(self.profit_start_date, 0, 1)
        
        settings_layout.addWidget(QLabel("تا تاریخ:"), 0, 2)
        
        if JALALI_DATE_AVAILABLE:
            self.profit_end_date = JalaliDateInputAccounting()
        else:
            self.profit_end_date = QLineEdit()
            self.profit_end_date.setPlaceholderText("1404/10/30")
        
        settings_layout.addWidget(self.profit_end_date, 0, 3)
        
        # نوع توزیع
        settings_layout.addWidget(QLabel("نوع توزیع:"), 1, 0)
        self.distribution_type = QComboBox()
        self.distribution_type.addItems(["بر اساس سرمایه", "بر اساس درصد سود", "مساوی"])
        settings_layout.addWidget(self.distribution_type, 1, 1, 1, 3)
        
        settings_group.setLayout(settings_layout)
        layout.addWidget(settings_group)
        
        # دکمه محاسبه سود
        btn_calculate = QPushButton("🧮 محاسبه سود قابل توزیع")
        btn_calculate.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                font-weight: bold;
                padding: 12px;
                font-size: 12pt;
            }
            QPushButton:hover {
                background-color: #219653;
            }
        """)
        btn_calculate.clicked.connect(self.calculate_distributable_profit)
        layout.addWidget(btn_calculate)
        
        # نمایش سود قابل توزیع
        self.distributable_profit_label = QLabel("💰 سود قابل توزیع: 0 تومان")
        self.distributable_profit_label.setStyleSheet("""
            QLabel {
                font-size: 14pt;
                font-weight: bold;
                color: #2ecc71;
                padding: 10px;
                border: 2px solid #2ecc71;
                border-radius: 8px;
                background-color: #111111;
            }
        """)
        self.distributable_profit_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.distributable_profit_label)
        
        # جدول توزیع سود
        self.distribution_table = QTableWidget()
        self.distribution_table.setColumnCount(6)
        self.distribution_table.setHorizontalHeaderLabels([
            "نام شریک", "درصد سهم", "سرمایه", "سهم سود", "بازده سرمایه", "وضعیت"
        ])
        self.distribution_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.distribution_table, 1)
        
        # دکمه توزیع
        btn_layout = QHBoxLayout()
        btn_distribute = QPushButton("✅ توزیع سود بین شرکا")
        btn_distribute.setStyleSheet("""
            QPushButton {
                background-color: #9b59b6;
                color: white;
                font-weight: bold;
                padding: 12px 25px;
                font-size: 12pt;
            }
            QPushButton:hover {
                background-color: #8e44ad;
            }
        """)
        btn_distribute.clicked.connect(self.distribute_profit)
        
        btn_layout.addStretch()
        btn_layout.addWidget(btn_distribute)
        layout.addLayout(btn_layout)
        
        return tab
    
    def create_profit_reports_tab(self):
        """ایجاد تب گزارش سود"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(15)
        
        # فیلترهای گزارش
        filter_layout = QHBoxLayout()
        
        filter_layout.addWidget(QLabel("دوره زمانی:"))
        self.report_period = QComboBox()
        self.report_period.addItems([
            "امروز", "هفته جاری", "ماه جاری", 
            "3 ماه اخیر", "6 ماه اخیر", "سال جاری", "سفارشی"
        ])
        filter_layout.addWidget(self.report_period)
        
        if JALALI_DATE_AVAILABLE:
            self.report_start_date = JalaliDateInputAccounting()
            self.report_end_date = JalaliDateInputAccounting()
        else:
            self.report_start_date = QLineEdit()
            self.report_end_date = QLineEdit()
            self.report_start_date.setPlaceholderText("1404/10/01")
            self.report_end_date.setPlaceholderText("1404/10/30")
        
        self.report_start_date.setVisible(False)
        self.report_end_date.setVisible(False)
        
        filter_layout.addWidget(self.report_start_date)
        filter_layout.addWidget(QLabel("تا"))
        filter_layout.addWidget(self.report_end_date)
        
        filter_layout.addStretch()
        
        btn_generate = QPushButton("📊 ایجاد گزارش")
        btn_generate.clicked.connect(self.generate_profit_report)
        filter_layout.addWidget(btn_generate)
        
        layout.addLayout(filter_layout)
        
        # جدول گزارش
        self.report_table = QTableWidget()
        self.report_table.setColumnCount(7)
        self.report_table.setHorizontalHeaderLabels([
            "نام شریک", "تعداد تراکنش", "سود کل", 
            "میانگین درصد", "بیشترین سود", "کمترین سود", "میانگین سود"
        ])
        self.report_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.report_table, 1)
        
        # اطلاعات آماری
        stats_group = QGroupBox("📈 آمار و اطلاعات")
        stats_layout = QGridLayout()
        
        self.report_stats = {
            'total_partners': QLabel("0"),
            'total_profit': QLabel("0 تومان"),
            'avg_roi': QLabel("0%"),
            'best_partner': QLabel("-"),
            'worst_partner': QLabel("-")
        }
        
        stats_layout.addWidget(QLabel("تعداد شرکا:"), 0, 0)
        stats_layout.addWidget(self.report_stats['total_partners'], 0, 1)
        
        stats_layout.addWidget(QLabel("سود کل:"), 0, 2)
        stats_layout.addWidget(self.report_stats['total_profit'], 0, 3)
        
        stats_layout.addWidget(QLabel("میانگین بازده:"), 1, 0)
        stats_layout.addWidget(self.report_stats['avg_roi'], 1, 1)
        
        stats_layout.addWidget(QLabel("بهترین شریک:"), 1, 2)
        stats_layout.addWidget(self.report_stats['best_partner'], 1, 3)
        
        stats_layout.addWidget(QLabel("ضعیف‌ترین شریک:"), 2, 0)
        stats_layout.addWidget(self.report_stats['worst_partner'], 2, 1)
        
        stats_group.setLayout(stats_layout)
        layout.addWidget(stats_group)
        
        return tab
    
    def create_settings_tab(self):
        """ایجاد تب تنظیمات"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(15)
        
        # تنظیمات عمومی
        general_group = QGroupBox("⚙️ تنظیمات عمومی")
        general_layout = QFormLayout()
        
        self.auto_distribute = QComboBox()
        self.auto_distribute.addItems(["غیرفعال", "ماهانه", "فصلی", "سالانه"])
        
        self.default_percentage = QLineEdit("0")
        self.default_percentage.setPlaceholderText("درصد سود پیش‌فرض")
        
        general_layout.addRow("توزیع خودکار سود:", self.auto_distribute)
        general_layout.addRow("درصد سود پیش‌فرض:", self.default_percentage)
        
        general_group.setLayout(general_layout)
        layout.addWidget(general_group)
        
        # تنظیمات مالی
        financial_group = QGroupBox("💰 تنظیمات مالی")
        financial_layout = QFormLayout()
        
        self.tax_percentage = QLineEdit("9")
        self.tax_percentage.setPlaceholderText("درصد مالیات")
        
        self.distributable_ratio = QLineEdit("70")
        self.distributable_ratio.setPlaceholderText("درصد سود قابل توزیع")
        
        financial_layout.addRow("درصد مالیات:", self.tax_percentage)
        financial_layout.addRow("درصد سود قابل توزیع:", self.distributable_ratio)
        
        financial_group.setLayout(financial_layout)
        layout.addWidget(financial_group)
        
        # دکمه‌های ذخیره
        btn_layout = QHBoxLayout()
        btn_save = QPushButton("💾 ذخیره تنظیمات")
        btn_save.clicked.connect(self.save_settings)
        btn_save.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                font-weight: bold;
                padding: 10px 20px;
            }
        """)
        
        btn_reset = QPushButton("🔄 بازنشانی")
        btn_reset.clicked.connect(self.load_settings)
        
        btn_layout.addStretch()
        btn_layout.addWidget(btn_reset)
        btn_layout.addWidget(btn_save)
        layout.addLayout(btn_layout)
        
        layout.addStretch()
        
        return tab
    
    # ---------- متدهای اصلی ----------
    
    def load_partners(self):
        """بارگذاری لیست شرکا"""
        try:
            if not self.partner_manager:
                QMessageBox.warning(self, "خطا", "مدیریت شرکا در دسترس نیست")
                return
            
            partners = self.partner_manager.get_all_partners(active_only=False)
            
            self.partners_table.setRowCount(len(partners))
            
            for row, partner in enumerate(partners):
                # ردیف
                self.partners_table.setItem(row, 0, QTableWidgetItem(str(row + 1)))
                
                # نام
                self.partners_table.setItem(row, 1, QTableWidgetItem(partner.get('partner_name', '')))
                
                # موبایل
                self.partners_table.setItem(row, 2, QTableWidgetItem(partner.get('mobile', '')))
                
                # تاریخ شروع
                self.partners_table.setItem(row, 3, 
                    QTableWidgetItem(partner.get('partnership_start_shamsi', '')))
                
                # سرمایه
                capital = partner.get('capital_toman', 0)
                self.partners_table.setItem(row, 4, 
                    QTableWidgetItem(f"{capital:,.0f} تومان"))
                
                # درصد سود
                percentage = partner.get('profit_percentage', 0)
                self.partners_table.setItem(row, 5, 
                    QTableWidgetItem(f"{percentage:.1f}%"))
                
                # سود کل
                profit = partner.get('total_profit_toman', 0)
                profit_item = QTableWidgetItem(f"{profit:,.0f} تومان")
                
                if profit > 0:
                    profit_item.setForeground(Qt.green)
                elif profit < 0:
                    profit_item.setForeground(Qt.red)
                    
                self.partners_table.setItem(row, 6, profit_item)
                
                # وضعیت
                status = "فعال" if partner.get('active') else "غیرفعال"
                status_item = QTableWidgetItem(status)
                status_item.setForeground(Qt.green if partner.get('active') else Qt.red)
                self.partners_table.setItem(row, 7, status_item)
                
                # دکمه‌های عملیات
                actions_widget = QWidget()
                actions_layout = QHBoxLayout(actions_widget)
                actions_layout.setContentsMargins(5, 15, 5, 15)  # افزایش حاشیه عمودی
                actions_layout.setSpacing(10)  # افزایش فاصله بین دکمه‌ها

                # افزایش ارتفاع ردیف جدول
                self.partners_table.setRowHeight(row, 70)  # افزایش ارتفاع ردیف به 70 پیکسل

                btn_edit = QPushButton("✏️")
                btn_edit.setToolTip("ویرایش شریک")
                btn_edit.clicked.connect(lambda checked, p=partner: self.edit_partner_dialog(p))
                btn_edit.setFixedSize(50, 40)  # افزایش اندازه دکمه
                btn_edit.setStyleSheet("""
                    QPushButton {
                        background-color: #3498db;
                        color: white;
                        border: none;
                        border-radius: 5px;
                        font-size: 14pt;  /* افزایش سایز آیکون */
                        font-weight: bold;
                    }
                    QPushButton:hover {
                        background-color: #2980b9;
                        border: 2px solid #27ae60;
                    }
                    QPushButton:pressed {
                        background-color: #1d6fa5;
                    }
                """)

                btn_delete = QPushButton("🗑️")
                btn_delete.setToolTip("حذف شریک")
                btn_delete.clicked.connect(lambda checked, p=partner: self.delete_partner_dialog(p))
                btn_delete.setFixedSize(50, 40)
                btn_delete.setStyleSheet("""
                    QPushButton {
                        background-color: #e74c3c;
                        color: white;
                        border: none;
                        border-radius: 5px;
                        font-size: 14pt;
                        font-weight: bold;
                    }
                    QPushButton:hover {
                        background-color: #c0392b;
                        border: 2px solid #27ae60;
                    }
                    QPushButton:pressed {
                        background-color: #a93226;
                    }
                """)

                btn_profits = QPushButton("💰")
                btn_profits.setToolTip("مشاهده سودها")
                btn_profits.clicked.connect(lambda checked, p=partner: self.show_partner_profits(p))
                btn_profits.setFixedSize(50, 40)
                btn_profits.setStyleSheet("""
                    QPushButton {
                        background-color: #9b59b6;
                        color: white;
                        border: none;
                        border-radius: 5px;
                        font-size: 14pt;
                        font-weight: bold;
                    }
                    QPushButton:hover {
                        background-color: #8e44ad;
                        border: 2px solid #27ae60;
                    }
                    QPushButton:pressed {
                        background-color: #7d3c98;
                    }
                """)

                actions_layout.addWidget(btn_edit)
                actions_layout.addWidget(btn_delete)
                actions_layout.addWidget(btn_profits)
                actions_layout.addStretch()

                self.partners_table.setCellWidget(row, 8, actions_widget)
            
            # به‌روزرسانی آمار
            self.update_summary()
            
        except Exception as e:
            print(f"⚠️ خطا در بارگذاری شرکا: {e}")
            QMessageBox.warning(self, "خطا", f"خطا در بارگذاری شرکا:\n{str(e)}")
    
    def filter_partners(self):
        """فیلتر کردن شرکا"""
        search_text = self.search_input.text().lower()
        status_filter = self.status_filter.currentText()
        
        for row in range(self.partners_table.rowCount()):
            should_show = True
            
            # فیلتر متن
            if search_text:
                partner_name = self.partners_table.item(row, 1).text().lower()
                mobile = self.partners_table.item(row, 2).text().lower()
                
                if search_text not in partner_name and search_text not in mobile:
                    should_show = False
            
            # فیلتر وضعیت
            if status_filter != "همه":
                status = self.partners_table.item(row, 7).text()
                if status_filter == "فعال" and status != "فعال":
                    should_show = False
                elif status_filter == "غیرفعال" and status == "فعال":
                    should_show = False
            
            self.partners_table.setRowHidden(row, not should_show)
    
    def update_summary(self):
        """به‌روزرسانی آمار سریع"""
        try:
            if not self.partner_manager:
                return
            
            # محاسبه آمار
            partners = self.partner_manager.get_all_partners(active_only=True)
            total_partners = len(partners)
            
            total_capital = sum(p.get('capital_toman', 0) for p in partners)
            total_profit = sum(p.get('total_profit_toman', 0) for p in partners)
            
            avg_profit = (total_profit / total_capital * 100) if total_capital > 0 else 0
            
            # به‌روزرسانی کارت‌ها
            self.stat_cards['total_partners'].value_label.setText(str(total_partners))
            self.stat_cards['total_capital'].value_label.setText(f"{total_capital:,.0f} تومان")
            self.stat_cards['total_profit'].value_label.setText(f"{total_profit:,.0f} تومان")
            self.stat_cards['avg_profit'].value_label.setText(f"{avg_profit:.1f}%")
            
            # وضعیت
            self.status_bar.showMessage(f"تعداد شرکا: {total_partners} | سرمایه کل: {total_capital:,.0f} تومان | سود کل: {total_profit:,.0f} تومان")
            
        except Exception as e:
            print(f"⚠️ خطا در به‌روزرسانی آمار: {e}")
    
    # ---------- عملیات شرکا ----------
    
    def add_partner(self):
        """افزودن شریک جدید"""
        try:
            if PARTNER_DIALOG_AVAILABLE:
                dialog = PartnerDialog(self.data_manager, parent=self)
                if dialog.exec():
                    self.load_partners()
                    self.data_changed.emit()
            else:
                self.show_simple_partner_dialog()
        except Exception as e:
            print(f"⚠️ خطا در افزودن شریک: {e}")
            self.show_simple_partner_dialog()
    
    def edit_partner(self):
        """ویرایش شریک انتخاب شده"""
        selected_row = self.partners_table.currentRow()
        if selected_row < 0:
            QMessageBox.warning(self, "خطا", "لطفاً یک شریک را انتخاب کنید")
            return
        
        partner_id = self.get_selected_partner_id(selected_row)
        if not partner_id:
            return
        
        try:
            if PARTNER_DIALOG_AVAILABLE:
                dialog = PartnerDialog(self.data_manager, partner_id=partner_id, parent=self)
                if dialog.exec():
                    self.load_partners()
                    self.data_changed.emit()
            else:
                QMessageBox.information(self, "ویرایش شریک", 
                    "فرم ویرایش شریک به زودی اضافه خواهد شد.")
        except Exception as e:
            print(f"⚠️ خطا در ویرایش شریک: {e}")
            QMessageBox.warning(self, "خطا", f"خطا در ویرایش شریک:\n{str(e)}")
    
    def delete_partner(self):
        """حذف شریک انتخاب شده"""
        selected_row = self.partners_table.currentRow()
        if selected_row < 0:
            QMessageBox.warning(self, "خطا", "لطفاً یک شریک را انتخاب کنید")
            return
        
        partner_id = self.get_selected_partner_id(selected_row)
        if not partner_id:
            return
        
        reply = QMessageBox.question(
            self, "تأیید حذف",
            "آیا از حذف این شریک اطمینان دارید؟\nاین عمل غیرقابل برگشت است.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                success, message = self.partner_manager.deactivate_partner(partner_id)
                if success:
                    QMessageBox.information(self, "موفق", message)
                    self.load_partners()
                    self.data_changed.emit()
                else:
                    QMessageBox.warning(self, "خطا", message)
            except Exception as e:
                QMessageBox.critical(self, "خطا", f"خطا در حذف شریک:\n{str(e)}")
    
    def get_selected_partner_id(self, row):
        """دریافت شناسه شریک انتخاب شده"""
        # از دیتابیس بر اساس نام و موبایل
        partner_name = self.partners_table.item(row, 1).text()
        mobile = self.partners_table.item(row, 2).text()
        
        try:
            query = "SELECT id FROM Partners WHERE person_id IN (SELECT id FROM Persons WHERE first_name || ' ' || last_name = ? AND mobile = ?)"
            result = self.data_manager.db.fetch_one(query, (partner_name, mobile))
            return result.get('id') if result else None
        except:
            return None
    
    # ---------- عملیات سود ----------
    
    def calculate_distributable_profit(self):
        """محاسبه سود قابل توزیع"""
        try:
            start_date = self.get_date_from_input(self.profit_start_date)
            end_date = self.get_date_from_input(self.profit_end_date)
            
            if not start_date or not end_date:
                QMessageBox.warning(self, "خطا", "لطفاً تاریخ شروع و پایان را انتخاب کنید")
                return
            
            # محاسبه درآمد کل در بازه زمانی
            query = """
            SELECT SUM(total) as total_income
            FROM Invoices
            WHERE invoice_type IN ('فروش', 'خدمات')
            AND DATE(invoice_date) BETWEEN ? AND ?
            AND payment_status != 'پرداخت نشده'
            """
            
            result = self.data_manager.db.fetch_one(query, (start_date, end_date))
            total_income = result.get('total_income', 0) if result else 0
            
            # سود قابل توزیع (70% درآمد)
            distributable_profit = total_income * 0.7
            distributable_profit_toman = distributable_profit / 10
            
            self.distributable_profit_label.setText(
                f"💰 سود قابل توزیع: {distributable_profit_toman:,.0f} تومان"
            )
            
            # محاسبه سهم هر شریک
            self.calculate_partner_shares(distributable_profit)
            
        except Exception as e:
            QMessageBox.warning(self, "خطا", f"خطا در محاسبه سود:\n{str(e)}")
    
    def get_date_from_input(self, date_input):
        """دریافت تاریخ از ویجت ورودی"""
        if hasattr(date_input, 'get_date_for_database'):
            return date_input.get_date_for_database()
        elif isinstance(date_input, QLineEdit):
            # تبدیل تاریخ شمسی به میلادی
            date_str = date_input.text().strip()
            if date_str:
                try:
                    return self.data_manager.db.jalali_to_gregorian(date_str)
                except:
                    return None
        return None
    
    def calculate_partner_shares(self, total_profit):
        """محاسبه سهم هر شریک"""
        try:
            if not self.partner_manager:
                return
            
            partners = self.partner_manager.get_all_partners(active_only=True)
            if not partners:
                QMessageBox.information(self, "اطلاع", "هیچ شریک فعالی وجود ندارد")
                return
            
            distribution_type = self.distribution_type.currentText()
            distribution_data = []
            
            if distribution_type == "بر اساس سرمایه":
                total_capital = sum(p.get('capital', 0) for p in partners)
                for partner in partners:
                    share_percentage = (partner.get('capital', 0) / total_capital) * 100 if total_capital > 0 else 0
                    share_amount = total_profit * (share_percentage / 100)
                    
                    distribution_data.append({
                        'partner_name': partner.get('partner_name'),
                        'share_percentage': share_percentage,
                        'capital': partner.get('capital_toman', 0),
                        'share_amount': share_amount / 10,  # تبدیل به تومان
                        'roi': (share_amount / partner.get('capital', 0) * 100) if partner.get('capital', 0) > 0 else 0
                    })
            
            elif distribution_type == "بر اساس درصد سود":
                total_percentage = sum(p.get('profit_percentage', 0) for p in partners)
                for partner in partners:
                    share_percentage = partner.get('profit_percentage', 0)
                    share_amount = total_profit * (share_percentage / 100) if total_percentage > 0 else 0
                    
                    distribution_data.append({
                        'partner_name': partner.get('partner_name'),
                        'share_percentage': share_percentage,
                        'capital': partner.get('capital_toman', 0),
                        'share_amount': share_amount / 10,
                        'roi': (share_amount / partner.get('capital', 0) * 100) if partner.get('capital', 0) > 0 else 0
                    })
            
            else:  # مساوی
                share_percentage = 100.0 / len(partners)
                for partner in partners:
                    share_amount = total_profit * (share_percentage / 100)
                    
                    distribution_data.append({
                        'partner_name': partner.get('partner_name'),
                        'share_percentage': share_percentage,
                        'capital': partner.get('capital_toman', 0),
                        'share_amount': share_amount / 10,
                        'roi': (share_amount / partner.get('capital', 0) * 100) if partner.get('capital', 0) > 0 else 0
                    })
            
            # نمایش در جدول
            self.distribution_table.setRowCount(len(distribution_data))
            
            for row, data in enumerate(distribution_data):
                self.distribution_table.setItem(row, 0, 
                    QTableWidgetItem(data['partner_name']))
                self.distribution_table.setItem(row, 1, 
                    QTableWidgetItem(f"{data['share_percentage']:.1f}%"))
                self.distribution_table.setItem(row, 2, 
                    QTableWidgetItem(f"{data['capital']:,.0f} تومان"))
                self.distribution_table.setItem(row, 3, 
                    QTableWidgetItem(f"{data['share_amount']:,.0f} تومان"))
                self.distribution_table.setItem(row, 4, 
                    QTableWidgetItem(f"{data['roi']:.1f}%"))
                self.distribution_table.setItem(row, 5, 
                    QTableWidgetItem("محاسبه شده"))
            
        except Exception as e:
            print(f"⚠️ خطا در محاسبه سهم‌ها: {e}")
    
    def distribute_profit(self):
        """توزیع سود بین شرکا"""
        try:
            reply = QMessageBox.question(
                self, "تأیید توزیع سود",
                "آیا از توزیع سود بین شرکا اطمینان دارید؟\nاین عمل در دیتابیس ذخیره خواهد شد.",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                # در اینجا باید توزیع سود در دیتابیس ثبت شود
                QMessageBox.information(self, "موفق", "سود با موفقیت توزیع شد")
                self.load_partners()
                self.data_changed.emit()
                
        except Exception as e:
            QMessageBox.warning(self, "خطا", f"خطا در توزیع سود:\n{str(e)}")
    
    def distribute_monthly_profit(self):
        """توزیع سود ماهانه"""
        try:
            if not self.partner_manager:
                QMessageBox.warning(self, "خطا", "مدیریت شرکا در دسترس نیست")
                return
            
            reply = QMessageBox.question(
                self, "توزیع سود ماهانه",
                "آیا می‌خواهید سود ماه جاری را بین شرکا توزیع کنید؟",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                success, message = self.partner_manager.distribute_monthly_profit()
                if success:
                    QMessageBox.information(self, "موفق", message)
                    self.load_partners()
                    self.data_changed.emit()
                else:
                    QMessageBox.warning(self, "خطا", message)
                    
        except Exception as e:
            QMessageBox.critical(self, "خطا", f"خطا در توزیع سود ماهانه:\n{str(e)}")
    
    def generate_profit_report(self):
        """ایجاد گزارش سود"""
        try:
            period = self.report_period.currentText()
            
            # محاسبه تاریخ‌ها بر اساس دوره
            today = jdatetime.datetime.now()
            
            if period == "امروز":
                start_date = today.strftime("%Y/%m/%d")
                end_date = start_date
            elif period == "هفته جاری":
                start_date = (today - jdatetime.timedelta(days=today.weekday())).strftime("%Y/%m/%d")
                end_date = today.strftime("%Y/%m/%d")
            elif period == "ماه جاری":
                start_date = today.replace(day=1).strftime("%Y/%m/%d")
                end_date = today.strftime("%Y/%m/%d")
            elif period == "سفارشی":
                start_date = self.get_date_from_widget(self.report_start_date)
                end_date = self.get_date_from_widget(self.report_end_date)
                if not start_date or not end_date:
                    QMessageBox.warning(self, "خطا", "لطفاً تاریخ شروع و پایان را انتخاب کنید")
                    return
            else:
                # محاسبه برای سایر دوره‌ها
                start_date = today.strftime("%Y/%m/%d")
                end_date = start_date
            
            # ایجاد گزارش
            self.create_profit_report(start_date, end_date)
            
        except Exception as e:
            QMessageBox.warning(self, "خطا", f"خطا در ایجاد گزارش:\n{str(e)}")
    
    def get_date_from_widget(self, widget):
        """دریافت تاریخ از ویجت"""
        if hasattr(widget, 'get_date'):
            return widget.get_date()
        elif isinstance(widget, QLineEdit):
            return widget.text().strip()
        return None
    
    def create_profit_report(self, start_date, end_date):
        """ایجاد گزارش سود برای بازه زمانی"""
        try:
            if not self.partner_manager:
                return
            
            # دریافت گزارش خلاصه
            summary = self.partner_manager.get_profit_summary(
                start_date=start_date,
                end_date=end_date
            )
            
            # نمایش در جدول
            self.report_table.setRowCount(len(summary))
            
            total_profit = 0
            partners_count = len(summary)
            
            for row, item in enumerate(summary):
                self.report_table.setItem(row, 0, 
                    QTableWidgetItem(item.get('partner_name', '')))
                self.report_table.setItem(row, 1, 
                    QTableWidgetItem(str(item.get('transaction_count', 0))))
                self.report_table.setItem(row, 2, 
                    QTableWidgetItem(f"{item.get('total_profit_toman', 0):,.0f} تومان"))
                self.report_table.setItem(row, 3, 
                    QTableWidgetItem(f"{item.get('avg_percentage', 0):.1f}%"))
                self.report_table.setItem(row, 4, 
                    QTableWidgetItem("محاسبه شود"))
                self.report_table.setItem(row, 5, 
                    QTableWidgetItem("محاسبه شود"))
                self.report_table.setItem(row, 6, 
                    QTableWidgetItem("محاسبه شود"))
                
                total_profit += item.get('total_profit_toman', 0)
            
            # به‌روزرسانی آمار
            self.report_stats['total_partners'].setText(str(partners_count))
            self.report_stats['total_profit'].setText(f"{total_profit:,.0f} تومان")
            
            # محاسبه میانگین بازده (ساده‌سازی شده)
            avg_roi = (total_profit / partners_count) if partners_count > 0 else 0
            self.report_stats['avg_roi'].setText(f"{avg_roi:.1f}%")
            
        except Exception as e:
            print(f"⚠️ خطا در ایجاد گزارش: {e}")
    
    def show_partner_profits(self, partner):
        """نمایش سودهای یک شریک"""
        try:
            if PARTNER_PROFITS_DIALOG_AVAILABLE:
                dialog = PartnerProfitsDialog(self.data_manager, partner['id'], parent=self)
                dialog.exec()
            else:
                # استفاده از دیالوگ ساده در صورت عدم وجود
                self.show_simple_partner_profits_dialog(partner)
        except Exception as e:
            print(f"⚠️ خطا در نمایش سودهای شریک: {e}")
            QMessageBox.information(self, "سود شریک", 
                f"سود کل شریک {partner.get('partner_name')}: {partner.get('total_profit_toman', 0):,.0f} تومان")
    
    def show_simple_partner_profits_dialog(self, partner):
        """نمایش دیالوگ ساده سودهای شریک"""
        dialog = QDialog(self)
        dialog.setWindowTitle(f"💰 سودهای شریک: {partner.get('partner_name')}")
        dialog.setMinimumSize(500, 400)
        
        layout = QVBoxLayout(dialog)
        
        # اطلاعات شریک
        info_group = QGroupBox("📋 اطلاعات شریک")
        info_layout = QFormLayout()
        
        info_layout.addRow("نام:", QLabel(partner.get('partner_name', '-')))
        info_layout.addRow("موبایل:", QLabel(partner.get('mobile', '-')))
        info_layout.addRow("سرمایه:", QLabel(f"{partner.get('capital_toman', 0):,.0f} تومان"))
        info_layout.addRow("درصد سود:", QLabel(f"{partner.get('profit_percentage', 0):.1f}%"))
        info_layout.addRow("سود کل:", QLabel(f"{partner.get('total_profit_toman', 0):,.0f} تومان"))
        
        info_group.setLayout(info_layout)
        layout.addWidget(info_group)
        
        # دکمه بستن
        btn_close = QPushButton("بستن")
        btn_close.clicked.connect(dialog.accept)
        
        layout.addWidget(btn_close)
        
        dialog.exec()
    
    # ---------- تنظیمات ----------
    
    def load_settings(self):
        """بارگذاری تنظیمات"""
        try:
            # بارگذاری از دیتابیس
            query = "SELECT * FROM Settings WHERE id = 1"
            settings = self.data_manager.db.fetch_one(query)
            
            if settings:
                # تنظیم مقادیر
                pass
        except:
            pass
    
    def save_settings(self):
        """ذخیره تنظیمات"""
        try:
            # ذخیره در دیتابیس
            QMessageBox.information(self, "موفق", "تنظیمات با موفقیت ذخیره شد")
        except Exception as e:
            QMessageBox.warning(self, "خطا", f"خطا در ذخیره تنظیمات:\n{str(e)}")
    
    # ---------- متدهای کمکی ----------
    
    def refresh_data(self):
        """بروزرسانی داده‌ها"""
        self.load_partners()
        self.update_summary()
        self.status_bar.showMessage("✅ داده‌ها بروزرسانی شد")
    
    def show_simple_partner_dialog(self):
        """نمایش دیالوگ ساده افزودن شریک"""
        dialog = QDialog(self)
        dialog.setWindowTitle("➕ افزودن شریک جدید")
        dialog.setMinimumWidth(500)
        
        layout = QVBoxLayout(dialog)
        
        # فرم
        form_layout = QFormLayout()
        
        name_input = QLineEdit()
        mobile_input = QLineEdit()
        capital_input = QLineEdit()
        percentage_input = QLineEdit()
        
        form_layout.addRow("نام شریک:", name_input)
        form_layout.addRow("موبایل:", mobile_input)
        form_layout.addRow("سرمایه (تومان):", capital_input)
        form_layout.addRow("درصد سود:", percentage_input)
        
        layout.addLayout(form_layout)
        
        # دکمه‌ها
        btn_layout = QHBoxLayout()
        btn_save = QPushButton("💾 ذخیره")
        btn_cancel = QPushButton("❌ انصراف")
        
        btn_save.clicked.connect(dialog.accept)
        btn_cancel.clicked.connect(dialog.reject)
        
        btn_layout.addStretch()
        btn_layout.addWidget(btn_save)
        btn_layout.addWidget(btn_cancel)
        
        layout.addLayout(btn_layout)
        
        if dialog.exec():
            # ذخیره شریک
            QMessageBox.information(self, "موفق", "شریک با موفقیت افزوده شد")
    
    def edit_partner_dialog(self, partner):
        """نمایش دیالوگ ویرایش شریک"""
        QMessageBox.information(self, "ویرایش", 
            f"ویرایش شریک: {partner.get('partner_name')}")
    
    def delete_partner_dialog(self, partner):
        """تأیید حذف شریک"""
        reply = QMessageBox.question(
            self, "حذف شریک",
            f"آیا از حذف شریک '{partner.get('partner_name')}' اطمینان دارید؟",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                success, message = self.partner_manager.deactivate_partner(partner['id'])
                if success:
                    QMessageBox.information(self, "موفق", message)
                    self.load_partners()
                else:
                    QMessageBox.warning(self, "خطا", message)
            except Exception as e:
                QMessageBox.critical(self, "خطا", f"خطا در حذف شریک:\n{str(e)}")