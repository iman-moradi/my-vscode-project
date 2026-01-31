"""
فرم مدیریت تراکنش‌های مالی - نسخه کامل با TransactionManager و تاریخ شمسی
"""

import os
import sys
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QLineEdit, QComboBox, QLabel, QMessageBox, QHeaderView,
    QScrollArea, QFrame, QGroupBox, QDateEdit, QSplitter, QToolBar,
    QProgressBar, QTabWidget, QDialog
)
from PySide6.QtCore import Qt, Signal, QDate
from PySide6.QtGui import QColor, QFont, QIcon
import jdatetime
from datetime import datetime, timedelta
import json

# اضافه کردن مسیر برای import دیالوگ‌ها و ویجت‌ها
current_dir = os.path.dirname(os.path.abspath(__file__))
# اضافه کردن مسیر پدر (یک سطح بالاتر)
parent_dir = os.path.dirname(current_dir)
# اضافه کردن مسیر ویجت‌ها
widgets_dir = os.path.join(parent_dir, "widgets")
sys.path.insert(0, parent_dir)
sys.path.insert(0, widgets_dir)

# وارد کردن ویجت تاریخ شمسی حرفه‌ای
try:
    # سعی می‌کنیم از چندین مسیر مختلف import کنیم
    try:
        # مسیر مستقیم
        from widgets.jalali_date_widget import JalaliDateWidget
        print("✅ ویجت تاریخ شمسی از jalali_date_widget بارگذاری شد")
    except ImportError:
        # مسیر دیگر
        from widgets.jalali_date_widget import JalaliDateWidget
        print("✅ ویجت تاریخ شمسی از widgets.jalali_date_widget بارگذاری شد")
    
    JALALI_WIDGET_AVAILABLE = True
    
except ImportError as e:
    print(f"⚠️ خطا در بارگذاری ویجت تاریخ شمسی: {e}")
    print(f"📁 current_dir: {current_dir}")
    print(f"📁 parent_dir: {parent_dir}")
    print(f"📁 widgets_dir: {widgets_dir}")
    print(f"📁 sys.path: {sys.path}")
    JALALI_WIDGET_AVAILABLE = False

# وارد کردن دیالوگ‌ها
try:
    from ui.forms.accounting.dialogs.transaction_dialog import TransactionDialog
    from ui.forms.accounting.dialogs.transfer_dialog import TransferDialog
    from ui.forms.accounting.dialogs.transaction_details_dialog import TransactionDetailsDialog
    DIALOGS_AVAILABLE = True
    print("✅ دیالوگ‌ها بارگذاری شدند")
except ImportError as e:
    print(f"⚠️ خطا در بارگذاری دیالوگ‌ها: {e}")
    # سعی با مسیر دیگر
    try:
        from dialogs.transaction_dialog import TransactionDialog
        from dialogs.transfer_dialog import TransferDialog
        from dialogs.transaction_details_dialog import TransactionDetailsDialog
        DIALOGS_AVAILABLE = True
    except ImportError:
        DIALOGS_AVAILABLE = False


class JalaliDateEdit(QWidget):
    """ویجت ساده تاریخ شمسی برای استفاده در صورت عدم دسترسی به JalaliDateWidget"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_date = jdatetime.date.today()
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.date_input = QLineEdit()
        self.date_input.setReadOnly(True)
        self.date_input.setStyleSheet("""
            QLineEdit {
                background-color: #2c3e50;
                border: 1px solid #34495e;
                border-radius: 4px;
                padding: 10px;
                color: white;
                font-family: 'B Nazanin';
                font-size: 13pt;
                min-height: 45px;
                text-align: center;
            }
        """)
        
        # دکمه تقویم
        self.calendar_btn = QPushButton("📅")
        self.calendar_btn.setFixedSize(40, 40)
        self.calendar_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 4px;
                font-size: 14pt;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        
        layout.addWidget(self.date_input)
        self.setLayout(layout)
        self.update_display()
    
    def update_display(self):
        """به‌روزرسانی نمایش تاریخ"""
        date_str = f"{self.current_date.year:04d}/{self.current_date.month:02d}/{self.current_date.day:02d}"
        self.date_input.setText(date_str)
    
    def set_date(self, jalali_date):
        """تنظیم تاریخ شمسی"""
        if isinstance(jalali_date, jdatetime.datetime):
            jalali_date = jalali_date.date()
        
        self.current_date = jalali_date
        self.update_display()
    
    def get_date(self):
        """دریافت تاریخ شمسی"""
        return self.current_date
    
    def setCalendarPopup(self, enabled):
        """متد سازگاری با JalaliDateWidget"""
        pass


class TransactionsForm(QWidget):
    """فرم مدیریت تراکنش‌های مالی - نسخه کامل"""
    
    # سیگنال‌ها
    data_changed = Signal()
    transaction_added = Signal(dict)
    transaction_deleted = Signal(int)
    
    def __init__(self, data_manager):
        super().__init__()
        self.data_manager = data_manager
        self.transaction_manager = data_manager.transaction_manager
        self.selected_transaction_id = None
        
        # 🔴 **راست‌چین کردن کامل**
        self.setLayoutDirection(Qt.RightToLeft)
        
        # تنظیم استایل
        self.setup_styles()
        
        # ایجاد رابط کاربری
        self.init_ui()
        
        # بارگذاری داده‌ها
        self.load_transactions()
        
        print("✅ فرم تراکنش‌ها ایجاد شد (نسخه کامل با تاریخ شمسی)")
    
    def setup_styles(self):
        """تنظیم استایل فرم"""
        self.setStyleSheet("""
            /* استایل کلی فرم */
            QWidget {
                background-color: #0a0a0a;
                color: #ffffff;
                font-family: 'B Nazanin';
                font-size: 11pt;
            }
            
            /* گروه‌بندی */
            QGroupBox {
                font-weight: bold;
                border: 2px solid #2c3e50;
                border-radius: 8px;
                margin-top: 15px;
                padding-top: 15px;
                background-color: #1a1a1a;
            }
            
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top right;
                right: 15px;
                padding: 0 15px;
                color: #3498db;
                font-size: 12pt;
            }
            
            /* جدول تراکنش‌ها */
            #transactions_table {
                background-color: #1a1a1a;
                alternate-background-color: #111111;
                gridline-color: #2c3e50;
                selection-background-color: #2c3e50;
                selection-color: white;
                border: 1px solid #2c3e50;
            }
            
            #transactions_table::item {
                padding: 8px;
                border-bottom: 1px solid #2c3e50;
            }
            
            #transactions_table::item:selected {
                background-color: #3498db;
                color: white;
            }
            
            QHeaderView::section {
                background-color: #2c3e50;
                color: white;
                padding: 8px;
                border: none;
                font-weight: bold;
            }
            
            /* دکمه‌ها */
            .success_button {
                background-color: #27ae60;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-size: 11pt;
                font-weight: bold;
                min-width: 140px;
            }
            
            .success_button:hover {
                background-color: #219653;
            }
            
            .info_button {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-size: 11pt;
                font-weight: bold;
                min-width: 140px;
            }
            
            .info_button:hover {
                background-color: #2980b9;
            }
            
            .warning_button {
                background-color: #f39c12;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-size: 11pt;
                font-weight: bold;
                min-width: 140px;
            }
            
            .warning_button:hover {
                background-color: #d68910;
            }
            
            .danger_button {
                background-color: #e74c3c;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-size: 11pt;
                font-weight: bold;
                min-width: 140px;
            }
            
            .danger_button:hover {
                background-color: #c0392b;
            }
            
            /* فیلدهای ورودی */
            QLineEdit, QComboBox {
                background-color: #2c3e50;
                border: 1px solid #34495e;
                border-radius: 4px;
                padding: 8px 12px;
                color: white;
                min-height: 40px;
                font-size: 11pt;
            }
            
            QLineEdit:focus, QComboBox:focus {
                border: 2px solid #3498db;
                background-color: #34495e;
            }
            
            QLineEdit::placeholder {
                color: #7f8c8d;
            }
            
            /* برچسب‌ها */
            QLabel {
                color: #ecf0f1;
                font-size: 11pt;
                padding: 2px;
            }
            
            .section_title {
                font-size: 16pt;
                font-weight: bold;
                color: #3498db;
                padding: 15px 0;
                border-bottom: 2px solid #3498db;
                background-color: #1a1a1a;
                border-radius: 5px;
                margin-bottom: 10px;
            }
            
            /* تب‌ها */
            QTabWidget::pane {
                border: 1px solid #2c3e50;
                background-color: #1a1a1a;
                border-radius: 5px;
            }
            
            QTabBar::tab {
                background-color: #2c3e50;
                color: #bdc3c7;
                padding: 10px 20px;
                margin-right: 2px;
                border-top-left-radius: 5px;
                border-top-right-radius: 5px;
            }
            
            QTabBar::tab:selected {
                background-color: #3498db;
                color: white;
                font-weight: bold;
            }
            
            QTabBar::tab:hover:!selected {
                background-color: #34495e;
            }
        """)
    
    def init_ui(self):
        """ایجاد رابط کاربری"""
        # لیوت اصلی
        main_layout = QVBoxLayout()
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(15, 15, 15, 15)
        
        # 🔴 **عنوان بخش**
        title_label = QLabel("💰 مدیریت تراکنش‌های مالی")
        title_label.setProperty("class", "section_title")
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)
        
        # 🔴 **تاب‌های مختلف**
        self.tab_widget = QTabWidget()
        
        # تب تراکنش‌ها
        self.transactions_tab = self.create_transactions_tab()
        self.tab_widget.addTab(self.transactions_tab, "📋 تراکنش‌ها")
        
        # تب گزارش‌ها
        self.reports_tab = self.create_reports_tab()
        self.tab_widget.addTab(self.reports_tab, "📊 گزارش‌ها")
        
        # تب آمار
        self.stats_tab = self.create_stats_tab()
        self.tab_widget.addTab(self.stats_tab, "📈 آمار")
        
        main_layout.addWidget(self.tab_widget)
        
        # 🔴 **نوار وضعیت**
        status_layout = QHBoxLayout()
        
        self.status_label = QLabel("آماده")
        self.status_label.setStyleSheet("""
            QLabel {
                color: #bdc3c7;
                font-size: 10pt;
                padding: 8px;
                background-color: #2c3e50;
                border-radius: 5px;
            }
        """)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setTextVisible(True)
        
        status_layout.addWidget(self.status_label)
        status_layout.addStretch()
        status_layout.addWidget(self.progress_bar)
        
        main_layout.addLayout(status_layout)
        
        self.setLayout(main_layout)
    
    def create_transactions_tab(self):
        """ایجاد تب تراکنش‌ها"""
        tab = QWidget()
        layout = QVBoxLayout()
        
        # 🔴 **نوار ابزار عملیات**
        toolbar = QToolBar()
        
        # دکمه‌های اصلی
        actions = [
            ("📥 دریافت", self.add_receipt, "#27ae60", "ثبت دریافت جدید"),
            ("📤 پرداخت", self.add_payment, "#e74c3c", "ثبت پرداخت جدید"),
            ("🔄 انتقال", self.add_transfer, "#3498db", "انتقال وجه بین حساب‌ها"),
            ("✏️ ویرایش", self.edit_transaction, "#9b59b6", "ویرایش تراکنش انتخاب شده"),
            ("🗑️ حذف", self.delete_transaction, "#e74c3c", "حذف تراکنش انتخاب شده"),
            ("↩️ برگشت", self.reverse_transaction, "#f39c12", "ایجاد تراکنش معکوس")
        ]
        
        for text, callback, color, tooltip in actions:
            btn = QPushButton(text)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {color};
                    color: white;
                    border: none;
                    padding: 10px 15px;
                    border-radius: 4px;
                    font-size: 11pt;
                    font-weight: bold;
                    min-width: 130px;
                    margin-right: 5px;
                }}
                QPushButton:hover {{
                    background-color: {self.darken_color(color)};
                }}
                QPushButton:disabled {{
                    background-color: #666;
                    color: #999;
                }}
            """)
            btn.clicked.connect(callback)
            btn.setToolTip(tooltip)
            toolbar.addWidget(btn)
        
        # فیلد جستجو
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 جستجوی تراکنش‌ها...")
        self.search_input.textChanged.connect(self.on_search_changed)
        
        search_btn = QPushButton("جستجو")
        search_btn.setProperty("class", "info_button")
        search_btn.clicked.connect(self.search_transactions)
        
        toolbar.addWidget(self.search_input)
        toolbar.addWidget(search_btn)
        
        layout.addWidget(toolbar)
        
        # 🔴 **فیلترهای پیشرفته - کاملاً شمسی شده**
        filter_group = QGroupBox("فیلترهای پیشرفته")
        filter_layout = QVBoxLayout()
        
        # ردیف اول فیلترها
        filter_row1 = QHBoxLayout()
        
        self.type_filter = QComboBox()
        self.type_filter.addItems([
            "همه انواع",
            "دریافت",
            "پرداخت", 
            "انتقال",
            "سود",
            "هزینه",
            "درآمد"
        ])
        
        self.account_filter = QComboBox()
        self.account_filter.addItem("همه حساب‌ها")
        self.load_accounts_to_filter()
        
        self.category_filter = QComboBox()
        self.category_filter.addItems([
            "همه دسته‌بندی‌ها",
            "عمومی",
            "فروش خدمات",
            "فروش قطعات",
            "خرید قطعات",
            "حقوق و دستمزد",
            "اجاره و قبوض",
            "تعمیرات و نگهداری",
            "حمل و نقل",
            "تبلیغات",
            "سایر"
        ])
        
        filter_row1.addWidget(QLabel("نوع:"))
        filter_row1.addWidget(self.type_filter)
        filter_row1.addWidget(QLabel("حساب:"))
        filter_row1.addWidget(self.account_filter)
        filter_row1.addWidget(QLabel("دسته‌بندی:"))
        filter_row1.addWidget(self.category_filter)
        filter_row1.addStretch()
        
        # ردیف دوم فیلترها (تاریخ - کاملاً شمسی)
        filter_row2 = QHBoxLayout()
        
        # 🔴 **استفاده از ویجت تاریخ شمسی**
        if JALALI_WIDGET_AVAILABLE:
            # استفاده از JalaliDateWidget اصلی
            self.date_from = JalaliDateWidget()
            self.date_to = JalaliDateWidget()
        else:
            # استفاده از نسخه جایگزین
            self.date_from = JalaliDateEdit()
            self.date_to = JalaliDateEdit()
        
        # تنظیم تاریخ 30 روز قبل به شمسی
        today_jalali = jdatetime.date.today()
        from_date_jalali = today_jalali - jdatetime.timedelta(days=30)
        
        self.date_from.set_date(from_date_jalali)
        self.date_to.set_date(today_jalali)
        
        self.amount_min = QLineEdit()
        self.amount_min.setPlaceholderText("حداقل مبلغ (تومان)")
        
        self.amount_max = QLineEdit()
        self.amount_max.setPlaceholderText("حداکثر مبلغ (تومان)")
        
        btn_apply_filter = QPushButton("اعمال فیلتر")
        btn_apply_filter.setProperty("class", "info_button")
        btn_apply_filter.clicked.connect(self.apply_advanced_filters)
        
        btn_clear_filter = QPushButton("پاک کردن")
        btn_clear_filter.setProperty("class", "danger_button")
        btn_clear_filter.clicked.connect(self.clear_filters)
        
        filter_row2.addWidget(QLabel("از تاریخ:"))
        filter_row2.addWidget(self.date_from)
        filter_row2.addWidget(QLabel("تا تاریخ:"))
        filter_row2.addWidget(self.date_to)
        filter_row2.addWidget(QLabel("مبلغ:"))
        filter_row2.addWidget(self.amount_min)
        filter_row2.addWidget(QLabel("تا"))
        filter_row2.addWidget(self.amount_max)
        filter_row2.addWidget(btn_apply_filter)
        filter_row2.addWidget(btn_clear_filter)
        
        filter_layout.addLayout(filter_row1)
        filter_layout.addLayout(filter_row2)
        filter_group.setLayout(filter_layout)
        layout.addWidget(filter_group)
        
        # 🔴 **جدول تراکنش‌ها**
        table_group = QGroupBox("لیست تراکنش‌ها")
        table_layout = QVBoxLayout()
        
        self.transactions_table = QTableWidget()
        self.transactions_table.setObjectName("transactions_table")
        self.transactions_table.setColumnCount(11)
        self.transactions_table.setHorizontalHeaderLabels([
            "ردیف",
            "کد تراکنش",
            "تاریخ",
            "نوع",
            "از حساب", 
            "به حساب",
            "مبلغ (تومان)",
            "شرح",
            "مرجع",
            "وضعیت",
            "عملیات"
        ])
        
        # تنظیمات جدول
        self.transactions_table.setAlternatingRowColors(True)
        self.transactions_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.transactions_table.setSelectionMode(QTableWidget.SingleSelection)
        self.transactions_table.horizontalHeader().setStretchLastSection(True)
        
        # تنظیم عرض ستون‌ها
        header = self.transactions_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Fixed)       # ردیف
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)  # کد
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)  # تاریخ
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)  # نوع
        header.setSectionResizeMode(4, QHeaderView.Stretch)     # از حساب
        header.setSectionResizeMode(5, QHeaderView.Stretch)     # به حساب
        header.setSectionResizeMode(6, QHeaderView.ResizeToContents)  # مبلغ
        header.setSectionResizeMode(7, QHeaderView.Stretch)     # شرح
        header.setSectionResizeMode(8, QHeaderView.ResizeToContents)  # مرجع
        header.setSectionResizeMode(9, QHeaderView.ResizeToContents)  # وضعیت
        header.setSectionResizeMode(10, QHeaderView.ResizeToContents) # عملیات
        
        self.transactions_table.setColumnWidth(0, 60)   # ردیف
        self.transactions_table.setColumnWidth(1, 100)  # کد
        self.transactions_table.setColumnWidth(2, 110)  # تاریخ
        self.transactions_table.setColumnWidth(3, 100)  # نوع
        self.transactions_table.setColumnWidth(6, 150)  # مبلغ
        self.transactions_table.setColumnWidth(8, 120)  # مرجع
        self.transactions_table.setColumnWidth(9, 100)  # وضعیت
        self.transactions_table.setColumnWidth(10, 150) # عملیات
        
        table_layout.addWidget(self.transactions_table)
        
        # 🔴 **نوار اطلاعات پایین جدول**
        info_layout = QHBoxLayout()
        
        self.summary_label = QLabel("در حال بارگذاری...")
        self.summary_label.setStyleSheet("""
            QLabel {
                color: #3498db;
                font-size: 11pt;
                font-weight: bold;
                padding: 8px;
                background-color: #1a1a1a;
                border-radius: 5px;
                border: 1px solid #3498db;
            }
        """)
        
        btn_refresh = QPushButton("🔄 بروزرسانی")
        btn_refresh.setProperty("class", "info_button")
        btn_refresh.clicked.connect(self.load_transactions)
        
        btn_export = QPushButton("📤 خروجی")
        btn_export.setProperty("class", "warning_button")
        btn_export.clicked.connect(self.export_transactions)
        
        btn_print = QPushButton("🖨️ چاپ")
        btn_print.setProperty("class", "info_button")
        btn_print.clicked.connect(self.print_report)
        
        info_layout.addWidget(self.summary_label)
        info_layout.addStretch()
        info_layout.addWidget(btn_export)
        info_layout.addWidget(btn_print)
        info_layout.addWidget(btn_refresh)
        
        table_layout.addLayout(info_layout)
        table_group.setLayout(table_layout)
        layout.addWidget(table_group)
        
        tab.setLayout(layout)
        
        # اتصال سیگنال‌ها
        self.transactions_table.itemSelectionChanged.connect(self.on_transaction_selected)
        self.transactions_table.doubleClicked.connect(self.view_transaction_details)
        
        return tab
    
    def create_reports_tab(self):
        """ایجاد تب گزارش‌ها"""
        tab = QWidget()
        layout = QVBoxLayout()
        
        # گزارش روزانه
        daily_group = QGroupBox("📅 گزارش روزانه")
        daily_layout = QVBoxLayout()
        
        self.daily_report_table = QTableWidget()
        self.daily_report_table.setColumnCount(4)
        self.daily_report_table.setHorizontalHeaderLabels([
            "نوع تراکنش",
            "تعداد",
            "مبلغ کل (تومان)",
            "میانگین (تومان)"
        ])
        
        daily_layout.addWidget(self.daily_report_table)
        
        btn_generate_daily = QPushButton("تولید گزارش روزانه")
        btn_generate_daily.setProperty("class", "success_button")
        btn_generate_daily.clicked.connect(self.generate_daily_report)
        
        daily_layout.addWidget(btn_generate_daily)
        daily_group.setLayout(daily_layout)
        layout.addWidget(daily_group)
        
        # گزارش ماهانه
        monthly_group = QGroupBox("📆 گزارش ماهانه")
        monthly_layout = QVBoxLayout()
        
        self.monthly_report_table = QTableWidget()
        self.monthly_report_table.setColumnCount(4)
        self.monthly_report_table.setHorizontalHeaderLabels([
            "نوع تراکنش",
            "تعداد",
            "مبلغ کل (تومان)",
            "درصد از کل"
        ])
        
        monthly_layout.addWidget(self.monthly_report_table)
        
        btn_generate_monthly = QPushButton("تولید گزارش ماهانه")
        btn_generate_monthly.setProperty("class", "success_button")
        btn_generate_monthly.clicked.connect(self.generate_monthly_report)
        
        monthly_layout.addWidget(btn_generate_monthly)
        monthly_group.setLayout(monthly_layout)
        layout.addWidget(monthly_group)
        
        # گردش نقدی
        cashflow_group = QGroupBox("💸 گردش نقدی")
        cashflow_layout = QVBoxLayout()
        
        self.cashflow_table = QTableWidget()
        self.cashflow_table.setColumnCount(5)
        self.cashflow_table.setHorizontalHeaderLabels([
            "تاریخ",
            "دریافتی",
            "پرداختی",
            "خالص",
            "موجودی"
        ])
        
        cashflow_layout.addWidget(self.cashflow_table)
        
        btn_generate_cashflow = QPushButton("تولید گردش نقدی")
        btn_generate_cashflow.setProperty("class", "success_button")
        btn_generate_cashflow.clicked.connect(self.generate_cashflow)
        
        cashflow_layout.addWidget(btn_generate_cashflow)
        cashflow_group.setLayout(cashflow_layout)
        layout.addWidget(cashflow_group)
        
        tab.setLayout(layout)
        return tab
    
    def create_stats_tab(self):
        """ایجاد تب آمار"""
        tab = QWidget()
        layout = QVBoxLayout()
        
        # آمار کلی
        stats_group = QGroupBox("📊 آمار کلی")
        stats_layout = QVBoxLayout()
        
        self.stats_labels = {}
        stats = [
            ("کل تراکنش‌ها", "total_transactions", "#3498db"),
            ("مجموع دریافتی", "total_income", "#27ae60"),
            ("مجموع پرداختی", "total_expense", "#e74c3c"),
            ("موجودی خالص", "net_balance", "#f39c12"),
            ("میانگین دریافتی", "avg_income", "#2ecc71"),
            ("میانگین پرداختی", "avg_expense", "#e74c3c"),
            ("بیشترین تراکنش", "max_transaction", "#9b59b6"),
            ("کمترین تراکنش", "min_transaction", "#34495e")
        ]
        
        for label_text, key, color in stats:
            frame = QFrame()
            frame.setFrameStyle(QFrame.Box)
            frame.setStyleSheet(f"""
                QFrame {{
                    background-color: #1a1a1a;
                    border: 2px solid {color};
                    border-radius: 8px;
                    padding: 10px;
                }}
            """)
            
            frame_layout = QHBoxLayout()
            
            label = QLabel(f"{label_text}:")
            label.setStyleSheet("font-weight: bold; font-size: 11pt;")
            
            value_label = QLabel("در حال محاسبه...")
            value_label.setStyleSheet(f"""
                QLabel {{
                    color: {color};
                    font-weight: bold;
                    font-size: 12pt;
                }}
            """)
            
            frame_layout.addWidget(label)
            frame_layout.addStretch()
            frame_layout.addWidget(value_label)
            frame.setLayout(frame_layout)
            
            stats_layout.addWidget(frame)
            self.stats_labels[key] = value_label
        
        btn_calc_stats = QPushButton("محاسبه آمار")
        btn_calc_stats.setProperty("class", "info_button")
        btn_calc_stats.clicked.connect(self.calculate_statistics)
        
        stats_layout.addWidget(btn_calc_stats)
        stats_group.setLayout(stats_layout)
        layout.addWidget(stats_group)
        
        # نمودار توزیع (ساده)
        chart_group = QGroupBox("📈 توزیع تراکنش‌ها")
        chart_layout = QVBoxLayout()
        
        self.chart_text = QLabel("نمودار به زودی اضافه خواهد شد...")
        self.chart_text.setAlignment(Qt.AlignCenter)
        self.chart_text.setStyleSheet("""
            QLabel {
                color: #7f8c8d;
                font-size: 12pt;
                padding: 40px;
                background-color: #1a1a1a;
                border-radius: 8px;
                border: 2px dashed #34495e;
            }
        """)
        
        chart_layout.addWidget(self.chart_text)
        chart_group.setLayout(chart_layout)
        layout.addWidget(chart_group)
        
        tab.setLayout(layout)
        return tab
    
    def darken_color(self, color):
        """تیره کردن رنگ برای hover"""
        color = color.lstrip('#')
        r, g, b = tuple(int(color[i:i+2], 16) for i in (0, 2, 4))
        r = max(0, r - 30)
        g = max(0, g - 30)
        b = max(0, b - 30)
        return f'#{r:02x}{g:02x}{b:02x}'
    
    def load_accounts_to_filter(self):
        """بارگذاری حساب‌ها در فیلتر"""
        try:
            query = """
            SELECT id, account_name, account_number 
            FROM Accounts 
            WHERE is_active = 1 
            ORDER BY account_name
            """
            accounts = self.data_manager.db.fetch_all(query)
            
            for account in accounts:
                display_text = f"{account.get('account_name')} ({account.get('account_number')})"
                self.account_filter.addItem(display_text, account.get('id'))
                
        except Exception as e:
            print(f"⚠️ خطا در بارگذاری حساب‌ها برای فیلتر: {e}")
    
    def load_transactions(self, filters=None):
        """بارگذاری تراکنش‌ها از دیتابیس با استفاده از TransactionManager"""
        try:
            self.status_label.setText("در حال بارگذاری تراکنش‌ها...")
            self.progress_bar.setVisible(True)
            self.progress_bar.setValue(10)
            
            # استفاده از TransactionManager
            transactions = []
            
            if filters:
                # استخراج پارامترهای فیلتر
                transaction_type = filters.get('transaction_type')
                if transaction_type == "همه انواع":
                    transaction_type = None
                
                # تاریخ‌ها (شمسی)
                start_date = filters.get('start_date')
                end_date = filters.get('end_date')
                
                # دریافت تراکنش‌ها با فیلتر
                transactions = self.transaction_manager.get_all_transactions(
                    start_date=start_date,
                    end_date=end_date,
                    transaction_type=transaction_type
                )
            else:
                # دریافت همه تراکنش‌ها
                transactions = self.transaction_manager.get_all_transactions()
            
            self.progress_bar.setValue(50)
            
            # پاک کردن جدول
            self.transactions_table.setRowCount(0)
            
            # متغیرهای آمار
            total_income = 0
            total_expense = 0
            transfer_count = 0
            
            # پر کردن جدول
            for row, transaction in enumerate(transactions):
                self.transactions_table.insertRow(row)
                
                # شماره ردیف
                self.transactions_table.setItem(row, 0, 
                    QTableWidgetItem(str(row + 1)))
                
                # کد تراکنش
                trans_id = transaction.get('id', '')
                self.transactions_table.setItem(row, 1, 
                    QTableWidgetItem(f"TRX{trans_id:06d}"))
                
                # تاریخ شمسی
                trans_date = transaction.get('transaction_date_shamsi', '')
                self.transactions_table.setItem(row, 2, 
                    QTableWidgetItem(trans_date))
                
                # نوع تراکنش
                trans_type = transaction.get('transaction_type', '')
                type_item = QTableWidgetItem(trans_type)
                
                # رنگ‌بندی بر اساس نوع
                if trans_type == "دریافت":
                    type_item.setForeground(QColor('#27ae60'))
                    total_income += transaction.get('amount_toman', 0)
                elif trans_type == "پرداخت":
                    type_item.setForeground(QColor('#e74c3c'))
                    total_expense += transaction.get('amount_toman', 0)
                elif trans_type == "انتقال":
                    type_item.setForeground(QColor('#3498db'))
                    transfer_count += 1
                elif trans_type == "سود":
                    type_item.setForeground(QColor('#f39c12'))
                else:
                    type_item.setForeground(QColor('#9b59b6'))
                
                type_item.setTextAlignment(Qt.AlignCenter)
                self.transactions_table.setItem(row, 3, type_item)
                
                # از حساب
                from_account = transaction.get('from_account_name', '---')
                self.transactions_table.setItem(row, 4, 
                    QTableWidgetItem(from_account))
                
                # به حساب
                to_account = transaction.get('to_account_name', '---')
                self.transactions_table.setItem(row, 5, 
                    QTableWidgetItem(to_account))
                
                # مبلغ (تومان)
                amount = transaction.get('amount_toman', 0)
                amount_item = QTableWidgetItem(f"{amount:,.0f} تومان")
                amount_item.setTextAlignment(Qt.AlignRight)
                
                # رنگ‌بندی مبلغ
                if trans_type == "دریافت":
                    amount_item.setForeground(QColor('#27ae60'))
                elif trans_type == "پرداخت":
                    amount_item.setForeground(QColor('#e74c3c'))
                else:
                    amount_item.setForeground(QColor('#f39c12'))
                
                self.transactions_table.setItem(row, 6, amount_item)
                
                # شرح
                description = transaction.get('description', '')
                self.transactions_table.setItem(row, 7, 
                    QTableWidgetItem(description[:50] + "..." if len(description) > 50 else description))
                
                # مرجع
                reference_type = transaction.get('reference_type', '')
                reference_id = transaction.get('reference_id', '')
                reference_text = ""
                
                if reference_type and reference_id:
                    reference_text = f"{reference_type} #{reference_id}"
                elif reference_id:
                    reference_text = f"#{reference_id}"
                else:
                    reference_text = "---"
                
                self.transactions_table.setItem(row, 8, 
                    QTableWidgetItem(reference_text))
                
                # وضعیت
                status = transaction.get('status', 'انجام شده')
                status_item = QTableWidgetItem(status)
                
                if status == "انجام شده":
                    status_item.setForeground(QColor('#27ae60'))
                elif status == "لغو شده":
                    status_item.setForeground(QColor('#e74c3c'))
                elif status == "در انتظار":
                    status_item.setForeground(QColor('#f39c12'))
                else:
                    status_item.setForeground(QColor('#7f8c8d'))
                
                status_item.setTextAlignment(Qt.AlignCenter)
                self.transactions_table.setItem(row, 9, status_item)
                
                # عملیات
                btn_layout = QHBoxLayout()
                btn_widget = QWidget()
                
                btn_view = QPushButton("👁️ مشاهده")
                btn_view.setStyleSheet("""
                    QPushButton {
                        background-color: #3498db;
                        color: white;
                        border: none;
                        padding: 5px 10px;
                        border-radius: 3px;
                        font-size: 9pt;
                        min-width: 80px;
                    }
                    QPushButton:hover {
                        background-color: #2980b9;
                    }
                """)
                btn_view.clicked.connect(lambda checked, tid=transaction['id']: self.view_transaction_details(tid))
                
                btn_reverse = QPushButton("↩️ برگشت")
                btn_reverse.setStyleSheet("""
                    QPushButton {
                        background-color: #f39c12;
                        color: white;
                        border: none;
                        padding: 5px 10px;
                        border-radius: 3px;
                        font-size: 9pt;
                        min-width: 80px;
                    }
                    QPushButton:hover {
                        background-color: #d68910;
                    }
                """)
                btn_reverse.clicked.connect(lambda checked, tid=transaction['id']: self.reverse_selected_transaction(tid))
                
                btn_layout.addWidget(btn_view)
                btn_layout.addWidget(btn_reverse)
                btn_layout.setContentsMargins(2, 2, 2, 2)
                btn_widget.setLayout(btn_layout)
                
                self.transactions_table.setCellWidget(row, 10, btn_widget)
                
                # ذخیره شناسه تراکنش در ردیف
                for col in range(self.transactions_table.columnCount()):
                    item = self.transactions_table.item(row, col)
                    if item:
                        item.setData(Qt.UserRole, transaction.get('id'))
            
            self.progress_bar.setValue(90)
            
            # به‌روزرسانی آمار
            net_balance = total_income - total_expense
            
            self.summary_label.setText(
                f"📊 {len(transactions)} تراکنش | "
                f"📥 {total_income:,.0f} تومان | "
                f"📤 {total_expense:,.0f} تومان | "
                f"💰 خالص: {net_balance:,.0f} تومان | "
                f"🔄 {transfer_count} انتقال"
            )
            
            # به‌روزرسانی آمار کلی
            if hasattr(self, 'stats_labels'):
                self.update_statistics_labels(transactions, total_income, total_expense, net_balance)
            
            self.progress_bar.setValue(100)
            self.status_label.setText(f"✅ {len(transactions)} تراکنش بارگذاری شد")
            self.progress_bar.setVisible(False)
            
            print(f"✅ {len(transactions)} تراکنش بارگذاری شد (از TransactionManager)")
            
        except Exception as e:
            self.progress_bar.setVisible(False)
            self.status_label.setText("❌ خطا در بارگذاری")
            print(f"❌ خطا در بارگذاری تراکنش‌ها: {e}")
            QMessageBox.critical(self, "خطا", f"خطا در بارگذاری تراکنش‌ها:\n\n{str(e)}")
    
    def convert_jalali_to_gregorian(self, jalali_date):
        """تبدیل تاریخ شمسی به میلادی"""
        try:
            if isinstance(jalali_date, jdatetime.date):
                gregorian_date = jalali_date.togregorian()
                return gregorian_date.strftime("%Y-%m-%d")
            elif isinstance(jalali_date, str):
                # تبدیل رشته تاریخ شمسی به میلادی
                parts = jalali_date.split('/')
                if len(parts) == 3:
                    year, month, day = map(int, parts)
                    jalali_date_obj = jdatetime.date(year, month, day)
                    gregorian_date = jalali_date_obj.togregorian()
                    return gregorian_date.strftime("%Y-%m-%d")
        except Exception as e:
            print(f"⚠️ خطا در تبدیل تاریخ شمسی به میلادی: {e}")
        
        return None
    
    def update_statistics_labels(self, transactions, total_income, total_expense, net_balance):
        """به‌روزرسانی برچسب‌های آمار"""
        try:
            # محاسبه آمار
            total_count = len(transactions)
            income_count = len([t for t in transactions if t.get('transaction_type') == 'دریافت'])
            expense_count = len([t for t in transactions if t.get('transaction_type') == 'پرداخت'])
            
            avg_income = total_income / income_count if income_count > 0 else 0
            avg_expense = total_expense / expense_count if expense_count > 0 else 0
            
            # پیدا کردن بیشترین و کمترین مبلغ
            amounts = [t.get('amount_toman', 0) for t in transactions if t.get('amount_toman', 0) > 0]
            max_amount = max(amounts) if amounts else 0
            min_amount = min(amounts) if amounts else 0
            
            # به‌روزرسانی برچسب‌ها
            self.stats_labels['total_transactions'].setText(f"{total_count:,}")
            self.stats_labels['total_income'].setText(f"{total_income:,.0f} تومان")
            self.stats_labels['total_expense'].setText(f"{total_expense:,.0f} تومان")
            self.stats_labels['net_balance'].setText(f"{net_balance:,.0f} تومان")
            self.stats_labels['avg_income'].setText(f"{avg_income:,.0f} تومان")
            self.stats_labels['avg_expense'].setText(f"{avg_expense:,.0f} تومان")
            self.stats_labels['max_transaction'].setText(f"{max_amount:,.0f} تومان")
            self.stats_labels['min_transaction'].setText(f"{min_amount:,.0f} تومان" if min_amount > 0 else "---")
            
        except Exception as e:
            print(f"⚠️ خطا در به‌روزرسانی آمار: {e}")
    
    def apply_advanced_filters(self):
        """اعمال فیلترهای پیشرفته - کاملاً شمسی"""
        try:
            filters = {}
            
            # فیلتر نوع
            trans_type = self.type_filter.currentText()
            if trans_type != "همه انواع":
                filters['transaction_type'] = trans_type
            
            # فیلتر حساب
            account_idx = self.account_filter.currentIndex()
            if account_idx > 0:
                account_id = self.account_filter.currentData()
                if account_id:
                    filters['account_id'] = account_id
            
            # 🔴 **فیلتر تاریخ شمسی - استفاده از ویجت تاریخ شمسی**
            date_from_jalali = self.date_from.get_date()
            date_to_jalali = self.date_to.get_date()
            
            # 🔴 **تبدیل تاریخ‌های شمسی به میلادی برای جستجو در دیتابیس**
            date_from_gregorian = self.convert_jalali_to_gregorian(date_from_jalali)
            date_to_gregorian = self.convert_jalali_to_gregorian(date_to_jalali)
            
            filters['start_date'] = date_from_gregorian
            filters['end_date'] = date_to_gregorian
            
            # فیلتر مبلغ
            amount_min = self.amount_min.text().strip()
            amount_max = self.amount_max.text().strip()
            
            if amount_min:
                try:
                    filters['amount_min'] = float(amount_min)
                except:
                    pass
            
            if amount_max:
                try:
                    filters['amount_max'] = float(amount_max)
                except:
                    pass
            
            self.load_transactions(filters)
            
        except Exception as e:
            QMessageBox.critical(self, "خطا", f"❌ خطا در اعمال فیلترها:\n\n{str(e)}")
    
    def clear_filters(self):
        """پاک کردن فیلترها"""
        self.type_filter.setCurrentIndex(0)
        self.account_filter.setCurrentIndex(0)
        self.category_filter.setCurrentIndex(0)
        
        # 🔴 **بازنشانی تاریخ‌های شمسی به تاریخ امروز و 30 روز قبل**
        today_jalali = jdatetime.date.today()
        from_date_jalali = today_jalali - jdatetime.timedelta(days=30)
        
        self.date_from.set_date(from_date_jalali)
        self.date_to.set_date(today_jalali)
        
        self.amount_min.clear()
        self.amount_max.clear()
        self.search_input.clear()
        
        self.load_transactions()
    
    def on_transaction_selected(self):
        """هنگام انتخاب تراکنش از جدول"""
        selected_items = self.transactions_table.selectedItems()
        if selected_items:
            first_item = selected_items[0]
            self.selected_transaction_id = first_item.data(Qt.UserRole)
    
    def on_search_changed(self, text):
        """هنگام تغییر متن جستجو"""
        if len(text.strip()) >= 2:
            self.search_transactions()
    
    def search_transactions(self):
        """جستجوی تراکنش‌ها"""
        search_text = self.search_input.text().strip()
        if not search_text:
            return
        
        try:
            # جستجو با استفاده از TransactionManager
            transactions = self.transaction_manager.get_all_transactions()
            
            # فیلتر کردن نتایج بر اساس متن جستجو
            filtered_transactions = []
            for transaction in transactions:
                # جستجو در فیلدهای مختلف
                search_fields = [
                    transaction.get('description', ''),
                    transaction.get('transaction_type', ''),
                    transaction.get('from_account_name', ''),
                    transaction.get('to_account_name', ''),
                    f"TRX{transaction.get('id', ''):06d}"
                ]
                
                # بررسی وجود متن جستجو در هر یک از فیلدها
                found = any(search_text.lower() in str(field).lower() for field in search_fields)
                if found:
                    filtered_transactions.append(transaction)
            
            # به‌روزرسانی جدول
            self.update_table_with_data(filtered_transactions)
            
            self.status_label.setText(f"🔍 {len(filtered_transactions)} تراکنش یافت شد")
            
        except Exception as e:
            print(f"❌ خطا در جستجو: {e}")
    
    def update_table_with_data(self, transactions):
        """به‌روزرسانی جدول با داده‌های جدید"""
        self.transactions_table.setRowCount(0)
        
        # متغیرهای آمار
        total_income = 0
        total_expense = 0
        transfer_count = 0
        
        for row, transaction in enumerate(transactions):
            self.transactions_table.insertRow(row)
            
            # شماره ردیف
            self.transactions_table.setItem(row, 0, QTableWidgetItem(str(row + 1)))
            
            # کد تراکنش
            trans_id = transaction.get('id', '')
            self.transactions_table.setItem(row, 1, QTableWidgetItem(f"TRX{trans_id:06d}"))
            
            # تاریخ شمسی
            trans_date = transaction.get('transaction_date_shamsi', '')
            self.transactions_table.setItem(row, 2, QTableWidgetItem(trans_date))
            
            # نوع تراکنش
            trans_type = transaction.get('transaction_type', '')
            type_item = QTableWidgetItem(trans_type)
            
            # رنگ‌بندی بر اساس نوع
            if trans_type == "دریافت":
                type_item.setForeground(QColor('#27ae60'))
                total_income += transaction.get('amount_toman', 0)
            elif trans_type == "پرداخت":
                type_item.setForeground(QColor('#e74c3c'))
                total_expense += transaction.get('amount_toman', 0)
            elif trans_type == "انتقال":
                type_item.setForeground(QColor('#3498db'))
                transfer_count += 1
            elif trans_type == "سود":
                type_item.setForeground(QColor('#f39c12'))
            else:
                type_item.setForeground(QColor('#9b59b6'))
            
            type_item.setTextAlignment(Qt.AlignCenter)
            self.transactions_table.setItem(row, 3, type_item)
            
            # بقیه سلول‌ها
            self.transactions_table.setItem(row, 4, QTableWidgetItem(transaction.get('from_account_name', '---')))
            self.transactions_table.setItem(row, 5, QTableWidgetItem(transaction.get('to_account_name', '---')))
            self.transactions_table.setItem(row, 6, QTableWidgetItem(f"{transaction.get('amount_toman', 0):,.0f} تومان"))
            self.transactions_table.setItem(row, 7, QTableWidgetItem(transaction.get('description', '')[:50]))
            
            # ذخیره شناسه
            for col in range(self.transactions_table.columnCount()):
                item = self.transactions_table.item(row, col)
                if item:
                    item.setData(Qt.UserRole, transaction.get('id'))
        
        # به‌روزرسانی آمار
        net_balance = total_income - total_expense
        
        self.summary_label.setText(
            f"📊 {len(transactions)} تراکنش | "
            f"📥 {total_income:,.0f} تومان | "
            f"📤 {total_expense:,.0f} تومان | "
            f"💰 خالص: {net_balance:,.0f} تومان | "
            f"🔄 {transfer_count} انتقال"
        )
    
    # ---------- عملیات اصلی ----------
    
    def add_receipt(self):
        """ثبت دریافت جدید"""
        if not DIALOGS_AVAILABLE:
            QMessageBox.information(self, "ثبت دریافت", 
                "فرم ثبت دریافت به زودی اضافه خواهد شد.")
            return
        
        dialog = TransactionDialog(self.data_manager, 
                                transaction_type="دریافت",
                                parent=self)
        if dialog.exec():
            # بارگذاری مجدد تراکنش‌ها
            self.load_transactions()
            self.data_changed.emit()
            
            # ارسال سیگنال
            self.transaction_added.emit({"type": "دریافت"})

    def add_payment(self):
        """ثبت پرداخت جدید"""
        if not DIALOGS_AVAILABLE:
            QMessageBox.information(self, "ثبت پرداخت", 
                "فرم ثبت پرداخت به زودی اضافه خواهد شد.")
            return
        
        dialog = TransactionDialog(self.data_manager, 
                                transaction_type="پرداخت",
                                parent=self)
        if dialog.exec():
            self.load_transactions()
            self.data_changed.emit()
            self.transaction_added.emit({"type": "پرداخت"})

    def add_transfer(self):
        """ثبت انتقال وجه"""
        if not DIALOGS_AVAILABLE:
            QMessageBox.information(self, "انتقال وجه", 
                "فرم انتقال وجه به زودی اضافه خواهد شد.")
            return
        
        dialog = TransferDialog(self.data_manager, parent=self)
        if dialog.exec():
            self.load_transactions()
            self.data_changed.emit()
            self.transaction_added.emit({"type": "انتقال"})

    def edit_transaction(self):
        """ویرایش تراکنش انتخاب شده"""
        if not self.selected_transaction_id:
            QMessageBox.warning(self, "هشدار", "⚠️ لطفاً ابتدا یک تراکنش را انتخاب کنید.")
            return
        
        if not DIALOGS_AVAILABLE:
            QMessageBox.information(self, "ویرایش تراکنش", 
                "فرم ویرایش تراکنش به زودی اضافه خواهد شد.")
            return
        
        dialog = TransactionDialog(self.data_manager, 
                                transaction_id=self.selected_transaction_id,
                                parent=self)
        if dialog.exec():
            self.load_transactions()
            self.data_changed.emit()

    def delete_transaction(self):
        """حذف تراکنش انتخاب شده"""
        if not self.selected_transaction_id:
            QMessageBox.warning(self, "هشدار", "⚠️ لطفاً ابتدا یک تراکنش را انتخاب کنید.")
            return
        
        reply = QMessageBox.question(
            self, "تأیید حذف",
            "⚠️ آیا از حذف این تراکنش اطمینان دارید؟\n\n"
            "توجه: در سیستم‌های مالی حرفه‌ای، حذف تراکنش توصیه نمی‌شود.\n"
            "بهتر است از قابلیت برگشت تراکنش استفاده کنید.",
            QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel,
            QMessageBox.Cancel
        )
        
        if reply == QMessageBox.Yes:
            try:
                # حذف با استفاده از TransactionManager
                success, message = self.transaction_manager.reverse_transaction(
                    self.selected_transaction_id,
                    reason="حذف دستی توسط کاربر"
                )
                
                if success:
                    QMessageBox.information(self, "موفق", f"✅ {message}")
                    self.load_transactions()
                    self.data_changed.emit()
                    self.transaction_deleted.emit(self.selected_transaction_id)
                    self.selected_transaction_id = None
                else:
                    QMessageBox.critical(self, "خطا", f"❌ {message}")
                    
            except Exception as e:
                QMessageBox.critical(self, "خطا", f"❌ خطا در حذف تراکنش:\n\n{str(e)}")
    
    def reverse_selected_transaction(self, transaction_id=None):
        """ایجاد تراکنش معکوس برای تراکنش انتخاب شده"""
        if not transaction_id:
            if not self.selected_transaction_id:
                QMessageBox.warning(self, "هشدار", "⚠️ لطفاً ابتدا یک تراکنش را انتخاب کنید.")
                return
            transaction_id = self.selected_transaction_id
        
        # دریافت تایید از کاربر
        reply = QMessageBox.question(
            self, "تأیید برگشت",
            "آیا می‌خواهید این تراکنش را برگشت دهید؟\n\n"
            "این عمل یک تراکنش معکوس ایجاد می‌کند که اثرات مالی\n"
            "تراکنش فعلی را خنثی می‌کند.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                # استفاده از TransactionManager
                success, message = self.transaction_manager.reverse_transaction(
                    transaction_id,
                    reason="برگشت دستی توسط کاربر"
                )
                
                if success:
                    QMessageBox.information(self, "موفق", f"✅ {message}")
                    self.load_transactions()
                    self.data_changed.emit()
                else:
                    QMessageBox.critical(self, "خطا", f"❌ {message}")
                    
            except Exception as e:
                QMessageBox.critical(self, "خطا", f"❌ خطا در برگشت تراکنش:\n\n{str(e)}")
    
    def reverse_transaction(self):
        """دکمه برگشت در نوار ابزار"""
        self.reverse_selected_transaction()
    
    def view_transaction_details(self, transaction_id=None):
        """مشاهده جزئیات تراکنش"""
        if not transaction_id:
            if not self.selected_transaction_id:
                QMessageBox.warning(self, "هشدار", "⚠️ لطفاً ابتدا یک تراکنش را انتخاب کنید.")
                return
            transaction_id = self.selected_transaction_id
        
        if not DIALOGS_AVAILABLE:
            QMessageBox.information(self, "جزئیات تراکنش", 
                "فرم جزئیات تراکنش به زودی اضافه خواهد شد.")
            return
        
        dialog = TransactionDetailsDialog(self.data_manager, 
                                        transaction_id, 
                                        parent=self)
        dialog.exec()
    
    # ---------- گزارش‌ها ----------
    
    def generate_daily_report(self):
        """تولید گزارش روزانه"""
        try:
            # استفاده از TransactionManager
            today = datetime.now().strftime("%Y-%m-%d")
            summary = self.transaction_manager.get_daily_summary(today)
            
            # پر کردن جدول گزارش روزانه
            self.daily_report_table.setRowCount(0)
            
            for row, item in enumerate(summary.get('summary', [])):
                self.daily_report_table.insertRow(row)
                
                self.daily_report_table.setItem(row, 0, 
                    QTableWidgetItem(item.get('transaction_type', '')))
                self.daily_report_table.setItem(row, 1, 
                    QTableWidgetItem(str(item.get('count', 0))))
                self.daily_report_table.setItem(row, 2, 
                    QTableWidgetItem(f"{item.get('total_amount_toman', 0):,.0f}"))
                
                # محاسبه میانگین
                count = item.get('count', 0)
                total = item.get('total_amount_toman', 0)
                avg = total / count if count > 0 else 0
                self.daily_report_table.setItem(row, 3, 
                    QTableWidgetItem(f"{avg:,.0f}"))
            
            # اضافه کردن جمع کل
            self.daily_report_table.insertRow(self.daily_report_table.rowCount())
            row = self.daily_report_table.rowCount() - 1
            
            self.daily_report_table.setItem(row, 0, 
                QTableWidgetItem("جمع کل"))
            self.daily_report_table.setItem(row, 1, 
                QTableWidgetItem(str(summary.get('total_transactions', 0))))
            self.daily_report_table.setItem(row, 2, 
                QTableWidgetItem(f"{summary.get('total_income', 0) + summary.get('total_expense', 0):,.0f}"))
            self.daily_report_table.setItem(row, 3, 
                QTableWidgetItem("---"))
            
            # تنظیم رنگ برای جمع کل
            for col in range(4):
                item = self.daily_report_table.item(row, col)
                if item:
                    item.setBackground(QColor('#2c3e50'))
                    item.setForeground(QColor('#ffffff'))
                    font = item.font()
                    font.setBold(True)
                    item.setFont(font)
            
            self.status_label.setText(f"✅ گزارش روزانه {summary.get('date_shamsi', '')} تولید شد")
            
        except Exception as e:
            QMessageBox.critical(self, "خطا", f"❌ خطا در تولید گزارش روزانه:\n\n{str(e)}")
    
    def generate_monthly_report(self):
        """تولید گزارش ماهانه"""
        try:
            # تاریخ جاری شمسی
            today = jdatetime.datetime.now()
            summary = self.transaction_manager.get_monthly_summary(today.year, today.month)
            
            # پر کردن جدول گزارش ماهانه
            self.monthly_report_table.setRowCount(0)
            
            total_amount = sum(item.get('total_amount_toman', 0) for item in summary.get('summary', []))
            
            for row, item in enumerate(summary.get('summary', [])):
                self.monthly_report_table.insertRow(row)
                
                self.monthly_report_table.setItem(row, 0, 
                    QTableWidgetItem(item.get('transaction_type', '')))
                self.monthly_report_table.setItem(row, 1, 
                    QTableWidgetItem(str(item.get('count', 0))))
                self.monthly_report_table.setItem(row, 2, 
                    QTableWidgetItem(f"{item.get('total_amount_toman', 0):,.0f}"))
                
                # محاسبه درصد
                item_amount = item.get('total_amount_toman', 0)
                percentage = (item_amount / total_amount * 100) if total_amount > 0 else 0
                self.monthly_report_table.setItem(row, 3, 
                    QTableWidgetItem(f"{percentage:.1f}%"))
            
            # اضافه کردن جمع کل
            self.monthly_report_table.insertRow(self.monthly_report_table.rowCount())
            row = self.monthly_report_table.rowCount() - 1
            
            self.monthly_report_table.setItem(row, 0, 
                QTableWidgetItem("جمع کل"))
            self.monthly_report_table.setItem(row, 1, 
                QTableWidgetItem(str(summary.get('total_transactions', 0))))
            self.monthly_report_table.setItem(row, 2, 
                QTableWidgetItem(f"{summary.get('total_income', 0) + summary.get('total_expense', 0):,.0f}"))
            self.monthly_report_table.setItem(row, 3, 
                QTableWidgetItem("100%"))
            
            # تنظیم رنگ برای جمع کل
            for col in range(4):
                item = self.monthly_report_table.item(row, col)
                if item:
                    item.setBackground(QColor('#2c3e50'))
                    item.setForeground(QColor('#ffffff'))
                    font = item.font()
                    font.setBold(True)
                    item.setFont(font)
            
            month_name = summary.get('month_name', '')
            self.status_label.setText(f"✅ گزارش ماهانه {month_name} {summary.get('year', '')} تولید شد")
            
        except Exception as e:
            QMessageBox.critical(self, "خطا", f"❌ خطا در تولید گزارش ماهانه:\n\n{str(e)}")
    
    def generate_cashflow(self):
        """تولید گزارش گردش نقدی"""
        try:
            # محاسبه برای 30 روز گذشته
            end_date = datetime.now().strftime("%Y-%m-%d")
            start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
            
            cashflow = self.transaction_manager.get_cash_flow(start_date, end_date)
            
            # پر کردن جدول گردش نقدی
            self.cashflow_table.setRowCount(0)
            
            running_balance = 0
            for row, item in enumerate(cashflow):
                self.cashflow_table.insertRow(row)
                
                self.cashflow_table.setItem(row, 0, 
                    QTableWidgetItem(item.get('date_shamsi', '')))
                self.cashflow_table.setItem(row, 1, 
                    QTableWidgetItem(f"{item.get('income_toman', 0):,.0f}"))
                self.cashflow_table.setItem(row, 2, 
                    QTableWidgetItem(f"{item.get('expense_toman', 0):,.0f}"))
                self.cashflow_table.setItem(row, 3, 
                    QTableWidgetItem(f"{item.get('net_cash_flow_toman', 0):,.0f}"))
                
                # محاسبه موجودی انباشته
                running_balance += item.get('net_cash_flow_toman', 0)
                self.cashflow_table.setItem(row, 4, 
                    QTableWidgetItem(f"{running_balance:,.0f}"))
            
            self.status_label.setText(f"✅ گزارش گردش نقدی برای {len(cashflow)} روز تولید شد")
            
        except Exception as e:
            QMessageBox.critical(self, "خطا", f"❌ خطا در تولید گردش نقدی:\n\n{str(e)}")
    
    def calculate_statistics(self):
        """محاسبه آمار کلی"""
        try:
            # دریافت همه تراکنش‌ها
            transactions = self.transaction_manager.get_all_transactions()
            
            # محاسبه آمار
            total_income = sum(t.get('amount_toman', 0) for t in transactions if t.get('transaction_type') == 'دریافت')
            total_expense = sum(t.get('amount_toman', 0) for t in transactions if t.get('transaction_type') == 'پرداخت')
            net_balance = total_income - total_expense
            
            # به‌روزرسانی برچسب‌ها
            self.update_statistics_labels(transactions, total_income, total_expense, net_balance)
            
            self.status_label.setText("✅ آمار محاسبه شد")
            
        except Exception as e:
            self.status_label.setText("❌ خطا در محاسبه آمار")
            print(f"❌ خطا در محاسبه آمار: {e}")
    
    def export_transactions(self):
        """خروجی گرفتن از تراکنش‌ها"""
        try:
            # در این نسخه ساده، فقط یک پیام نمایش می‌دهیم
            QMessageBox.information(
                self, "خروجی تراکنش‌ها",
                "🔄 در حال آماده‌سازی خروجی...\n\n"
                "این قابلیت در نسخه‌های بعدی فعال خواهد شد.\n\n"
                "خروجی‌های پیشنهادی:\n"
                "• خروجی Excel (CSV)\n"
                "• خروجی PDF\n"
                "• خروجی JSON\n"
                "• چاپ مستقیم"
            )
        except Exception as e:
            print(f"❌ خطا در خروجی: {e}")
    
    def print_report(self):
        """چاپ گزارش"""
        try:
            QMessageBox.information(
                self, "چاپ گزارش",
                "🖨️ آماده چاپ...\n\n"
                "این قابلیت در نسخه‌های بعدی فعال خواهد شد."
            )
        except Exception as e:
            print(f"❌ خطا در چاپ: {e}")
    
    def refresh_data(self):
        """بروزرسانی داده‌های فرم"""
        self.status_label.setText("در حال بروزرسانی...")
        self.load_transactions()
        self.data_changed.emit()
        self.status_label.setText("آماده")


# تست مستقل
if __name__ == "__main__":
    import sys
    from PySide6.QtWidgets import QApplication
    from database.database import DatabaseManager
    from database.models import DataManager
    
    app = QApplication(sys.argv)
    
    # ایجاد مدیر داده
    data_manager = DataManager("data/repair_shop.db")
    
    # ایجاد فرم تراکنش‌ها
    form = TransactionsForm(data_manager)
    form.setWindowTitle("مدیریت تراکنش‌های مالی - نسخه کامل")
    form.resize(1200, 800)
    form.show()
    
    sys.exit(app.exec())