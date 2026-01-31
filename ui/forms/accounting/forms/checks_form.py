"""
فرم مدیریت چک‌های دریافتی و پرداختی
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QLabel, QFrame, QComboBox, QLineEdit, QGroupBox,
    QDateEdit, QHeaderView, QMessageBox, QTabWidget, QSplitter,
    QGridLayout, QScrollArea, QToolBar, QStatusBar, QMenu, QApplication,
    QAbstractItemView, QCheckBox
)
from PySide6.QtCore import Qt, QDate, Signal, QTimer, QPoint
from PySide6.QtGui import QAction, QFont, QIcon, QColor, QBrush
import jdatetime
from datetime import datetime, timedelta

# در بالای فایل 1، importها را اینگونه اصلاح کنید:

try:
    from ui.forms.accounting.widgets.jalali_date_input import JalaliDateInputAccounting as JalaliDateInput
except ImportError:
    try:
        from ui.widgets.jalali_date_widget import JalaliDateWidget as JalaliDateInput
    except ImportError:
        # فالب‌ک آپ
        from PySide6.QtWidgets import QLineEdit
        from PySide6.QtCore import Signal
        
        class JalaliDateInput(QLineEdit):
            """کلاس جایگزین برای تاریخ شمسی"""
            date_changed = Signal(str)
            
            def __init__(self, parent=None):
                super().__init__(parent)
                self.textChanged.connect(self._on_text_changed)
            
            def _on_text_changed(self):
                self.date_changed.emit(self.text())
            
            def get_date(self):
                return self.text()
            
            def set_date(self, date):
                if hasattr(date, 'year'):  # اگر jdatetime.date است
                    try:
                        from datetime import date as datetime_date
                        # بررسی می‌کنیم که آیا تاریخ شمسی است یا میلادی
                        if hasattr(date, 'togregorian'):  # jdatetime.date
                            self.setText(f"{date.year}/{date.month:02d}/{date.day:02d}")
                        else:  # datetime.date
                            jdate = jdatetime.date.fromgregorian(date=date)
                            self.setText(f"{jdate.year}/{jdate.month:02d}/{jdate.day:02d}")
                    except:
                        self.setText(str(date))
                else:
                    self.setText(str(date))
            
            def get_date_string(self):
                return self.text()
            
            def set_date_string(self, date_string):
                self.setText(date_string)


class ChecksForm(QWidget):
    """فرم مدیریت چک‌های دریافتی و پرداختی"""
    
    data_changed = Signal()
    
    def __init__(self, data_manager):
        super().__init__()
        self.data_manager = data_manager
        self.db = data_manager.db
        self.check_manager = data_manager.check_manager
        
        # راست‌چین کامل
        self.setLayoutDirection(Qt.RightToLeft)
        
        # فیلترهای فعلی
        self.filters = {
            'check_type': None,
            'status': None,
            'bank_name': '',
            'drawer': '',
            'payee': '',
            'start_date': None,
            'end_date': None
        }
        
        # راه‌اندازی UI
        self.setup_ui()
        self.setup_styles()
        self.load_checks()
        
        # تایمر برای بررسی چک‌های سررسید
        self.due_check_timer = QTimer()
        self.due_check_timer.timeout.connect(self.check_due_checks)
        self.due_check_timer.start(60000)  # هر دقیقه
        
        print("✅ فرم مدیریت چک‌ها ایجاد شد")
    
    def setup_styles(self):
        """تنظیم استایل فرم"""
        self.setStyleSheet("""
            /* استایل کلی */
            QWidget {
                background-color: #000000;
                color: #ffffff;
                font-family: 'B Nazanin';
                font-size: 11pt;
            }
            
            /* گروه‌باکس‌ها */
            QGroupBox {
                background-color: #111111;
                border: 1px solid #333;
                border-radius: 8px;
                margin-top: 20px;
                padding-top: 10px;
                font-weight: bold;
                color: #2ecc71;
            }
            
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 10px 0 10px;
                background-color: #1a252f;
                border-radius: 4px;
            }
            
            /* جدول چک‌ها */
            QTableWidget {
                background-color: #111111;
                alternate-background-color: #0a0a0a;
                selection-background-color: #2ecc71;
                selection-color: white;
                gridline-color: #333;
                color: white;
                border: none;
                font-size: 10pt;
            }
            
            QTableWidget::item {
                padding: 8px;
                color: white;
            }
            
            QHeaderView::section {
                background-color: #2c3e50;
                color: white;
                padding: 10px;
                border: none;
                font-weight: bold;
                text-align: center;
                font-size: 10pt;
            }
            
            /* دکمه‌ها */
            QPushButton {
                background-color: #2c3e50;
                color: white;
                border: none;
                padding: 8px 15px;
                border-radius: 4px;
                font-weight: bold;
            }
            
            QPushButton:hover {
                background-color: #34495e;
            }
            
            QPushButton:pressed {
                background-color: #1c2833;
            }
            
            /* دکمه عملیات */
            #btn_add {
                background-color: #27ae60;
            }
            
            #btn_add:hover {
                background-color: #2ecc71;
            }
            
            #btn_edit {
                background-color: #3498db;
            }
            
            #btn_edit:hover {
                background-color: #2980b9;
            }
            
            #btn_delete {
                background-color: #e74c3c;
            }
            
            #btn_delete:hover {
                background-color: #c0392b;
            }
            
            /* فیلدهای ورودی */
            QLineEdit, QComboBox {
                background-color: #222222;
                border: 1px solid #333;
                color: white;
                border-radius: 4px;
                padding: 6px;
                min-height: 30px;
            }
            
            QLineEdit:focus, QComboBox:focus {
                border: 2px solid #3498db;
            }
            
            /* تب‌ها */
            QTabWidget::pane {
                border: 1px solid #333;
                background-color: #111111;
                border-radius: 5px;
            }
            
            QTabBar::tab {
                background-color: #2c2c2c;
                color: #bbb;
                padding: 10px 20px;
                margin-left: 2px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }
            
            QTabBar::tab:selected {
                background-color: #2ecc71;
                color: white;
                font-weight: bold;
            }
            
            QTabBar::tab:hover:!selected {
                background-color: #3c3c3c;
            }
            
            /* کارت آمار */
            .stat_card {
                background-color: #111111;
                border: 1px solid #333;
                border-radius: 8px;
                padding: 15px;
            }
            
            .stat_card_title {
                color: #bbb;
                font-size: 12px;
                font-weight: bold;
            }
            
            .stat_card_value {
                color: #ffffff;
                font-size: 18px;
                font-weight: bold;
            }
        """)
    
    def setup_ui(self):
        """ایجاد رابط کاربری"""
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(10, 10, 10, 10)
        
        # 🔴 **هدر فرم**
        header_layout = self.create_header()
        main_layout.addLayout(header_layout)
        
        # 🔴 **نوار ابزار و فیلترها**
        filter_layout = self.create_filter_bar()
        main_layout.addLayout(filter_layout)
        
        # 🔴 **جدول چک‌ها**
        self.table = self.create_checks_table()
        main_layout.addWidget(self.table)
        
        # 🔴 **نوار وضعیت**
        self.status_label = QLabel("تعداد چک‌ها: 0")
        self.status_label.setStyleSheet("color: #bbb; font-size: 10pt;")
        main_layout.addWidget(self.status_label)
    
    def create_header(self):
        """ایجاد هدر فرم"""
        header_layout = QVBoxLayout()
        header_layout.setSpacing(15)
        
        # عنوان و تاریخ
        title_layout = QHBoxLayout()
        
        title_label = QLabel("💳 مدیریت چک‌های دریافتی و پرداختی")
        title_label.setStyleSheet("""
            QLabel {
                font-size: 18pt;
                font-weight: bold;
                color: #2ecc71;
            }
        """)
        
        # تاریخ امروز شمسی
        try:
            today_date = jdatetime.datetime.now().strftime("%Y/%m/%d")
        except:
            today_date = "1403/10/15"  # تاریخ پیش‌فرض
        
        date_label = QLabel(f"📅 تاریخ امروز: {today_date}")
        date_label.setStyleSheet("""
            QLabel {
                font-size: 11pt;
                color: #bbb;
                font-weight: bold;
            }
        """)
        
        title_layout.addWidget(title_label)
        title_layout.addStretch()
        title_layout.addWidget(date_label)
        
        header_layout.addLayout(title_layout)
        
        # 🔴 **کارت‌های آماری**
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(15)
        
        self.stat_cards = {}
        
        stats_config = [
            ("💰 چک‌های دریافتی", "0", "#27ae60", "received"),
            ("💸 چک‌های پرداختی", "0", "#e74c3c", "paid"),
            ("⚠️ چک‌های سررسید", "0", "#f39c12", "due"),
            ("🔄 چک‌های برگشتی", "0", "#9b59b6", "bounced")
        ]
        
        for title, default_value, color, key in stats_config:
            card = self.create_stat_card(title, default_value, color)
            stats_layout.addWidget(card)
            self.stat_cards[key] = card
        
        header_layout.addLayout(stats_layout)
        
        # 🔴 **دکمه‌های عملیاتی سریع**
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        
        quick_buttons = [
            ("➕ ثبت چک دریافتی", self.add_received_check, "#27ae60"),
            ("💸 ثبت چک پرداختی", self.add_paid_check, "#e74c3c"),
            ("🔄 تغییر وضعیت", self.change_check_status, "#3498db"),
            ("📄 چاپ لیست چک‌ها", self.print_checks_list, "#9b59b6"),
            ("📊 گزارش چک‌ها", self.show_checks_report, "#f39c12")
        ]
        
        for text, callback, color in quick_buttons:
            btn = QPushButton(text)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {color};
                    color: white;
                    border: none;
                    padding: 10px 15px;
                    border-radius: 5px;
                    font-size: 10pt;
                    font-weight: bold;
                }}
                QPushButton:hover {{
                    background-color: {self.darken_color(color)};
                }}
            """)
            btn.clicked.connect(callback)
            btn.setMinimumHeight(40)
            button_layout.addWidget(btn)
        
        button_layout.addStretch()
        header_layout.addLayout(button_layout)
        
        return header_layout
    
    def create_stat_card(self, title, value, color):
        """ایجاد کارت آماری"""
        card = QFrame()
        card.setObjectName("stat_card")
        card.setFixedHeight(80)
        
        layout = QVBoxLayout(card)
        layout.setSpacing(5)
        layout.setContentsMargins(15, 10, 15, 10)
        
        # عنوان
        title_label = QLabel(title)
        title_label.setObjectName("stat_card_title")
        title_label.setAlignment(Qt.AlignRight)
        layout.addWidget(title_label)
        
        # مقدار
        value_label = QLabel(value)
        value_label.setObjectName("stat_card_value")
        value_label.setAlignment(Qt.AlignRight)
        value_label.setStyleSheet(f"color: {color}; font-size: 16pt; font-weight: bold;")
        
        layout.addWidget(value_label)
        layout.addStretch()
        
        # ذخیره رفرنس
        card.value_label = value_label
        
        return card
    
    def darken_color(self, color):
        """تیره کردن رنگ برای hover"""
        color = color.lstrip('#')
        r, g, b = tuple(int(color[i:i+2], 16) for i in (0, 2, 4))
        r = max(0, r - 30)
        g = max(0, g - 30)
        b = max(0, b - 30)
        return f'#{r:02x}{g:02x}{b:02x}'
    
    def create_filter_bar(self):
        """ایجاد نوار فیلتر"""
        filter_layout = QVBoxLayout()
        filter_layout.setSpacing(10)
        
        # گروه فیلترها
        filter_group = QGroupBox("🔍 فیلتر چک‌ها")
        filter_group_layout = QGridLayout()
        
        # نوع چک
        filter_group_layout.addWidget(QLabel("نوع چک:"), 0, 0)
        self.type_combo = QComboBox()
        self.type_combo.addItem("همه", None)
        self.type_combo.addItem("دریافتی", "دریافتی")
        self.type_combo.addItem("پرداختی", "پرداختی")
        self.type_combo.currentIndexChanged.connect(self.apply_filters)
        filter_group_layout.addWidget(self.type_combo, 0, 1)
        
        # وضعیت چک
        filter_group_layout.addWidget(QLabel("وضعیت:"), 0, 2)
        self.status_combo = QComboBox()
        self.status_combo.addItem("همه", None)
        self.status_combo.addItem("وصول نشده", "وصول نشده")
        self.status_combo.addItem("وصول شده", "وصول شده")
        self.status_combo.addItem("برگشتی", "برگشتی")
        self.status_combo.addItem("پاس شده", "پاس شده")
        self.status_combo.addItem("پاس نشده", "پاس نشده")
        self.status_combo.addItem("بلوکه شده", "بلوکه شده")
        self.status_combo.currentIndexChanged.connect(self.apply_filters)
        filter_group_layout.addWidget(self.status_combo, 0, 3)
        
        # بانک
        filter_group_layout.addWidget(QLabel("بانک:"), 1, 0)
        self.bank_combo = QComboBox()
        self.bank_combo.setEditable(True)
        self.bank_combo.addItem("همه", "")
        self.bank_combo.currentTextChanged.connect(self.apply_filters)
        filter_group_layout.addWidget(self.bank_combo, 1, 1)
        
        # تاریخ شروع
        filter_group_layout.addWidget(QLabel("از تاریخ:"), 1, 2)
        self.start_date_input = JalaliDateInput()
        self.start_date_input.date_changed.connect(self.apply_filters)
        filter_group_layout.addWidget(self.start_date_input, 1, 3)
        
        # تاریخ پایان
        filter_group_layout.addWidget(QLabel("تا تاریخ:"), 2, 0)
        self.end_date_input = JalaliDateInput()
        self.end_date_input.date_changed.connect(self.apply_filters)
        filter_group_layout.addWidget(self.end_date_input, 2, 1)
        
        # جستجوی صادرکننده/دریافت‌کننده
        filter_group_layout.addWidget(QLabel("جستجوی نام:"), 2, 2)
        self.name_search_input = QLineEdit()
        self.name_search_input.setPlaceholderText("نام صادرکننده یا دریافت‌کننده...")
        self.name_search_input.textChanged.connect(self.apply_filters)
        filter_group_layout.addWidget(self.name_search_input, 2, 3)
        
        # دکمه‌های فیلتر
        button_layout = QHBoxLayout()
        
        btn_clear_filters = QPushButton("🗑️ پاک کردن فیلترها")
        btn_clear_filters.setStyleSheet("""
            QPushButton {
                background-color: #7f8c8d;
                color: white;
                padding: 8px 15px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #95a5a6;
            }
        """)
        btn_clear_filters.clicked.connect(self.clear_filters)
        button_layout.addWidget(btn_clear_filters)
        
        button_layout.addStretch()
        filter_group_layout.addLayout(button_layout, 3, 0, 1, 4)
        
        filter_group.setLayout(filter_group_layout)
        filter_layout.addWidget(filter_group)
        
        return filter_layout
    
    def create_checks_table(self):
        """ایجاد جدول چک‌ها"""
        table = QTableWidget()
        table.setColumnCount(12)
        table.setHorizontalHeaderLabels([
            "ردیف",
            "شماره چک",
            "نوع",
            "بانک",
            "مبلغ (تومان)",
            "صادرکننده",
            "دریافت‌کننده",
            "تاریخ سررسید",
            "وضعیت",
            "شماره فاکتور",
            "توضیحات",
            "عملیات"
        ])
        
        # تنظیمات جدول
        table.setAlternatingRowColors(True)
        table.setSelectionBehavior(QAbstractItemView.SelectRows)
        table.setSelectionMode(QAbstractItemView.SingleSelection)
        table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        
        # اندازه ستون‌ها
        header = table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Fixed)  # ردیف
        header.setSectionResizeMode(1, QHeaderView.Fixed)  # شماره چک
        header.setSectionResizeMode(2, QHeaderView.Fixed)  # نوع
        header.setSectionResizeMode(3, QHeaderView.Stretch)  # بانک
        header.setSectionResizeMode(4, QHeaderView.Fixed)  # مبلغ
        header.setSectionResizeMode(5, QHeaderView.Stretch)  # صادرکننده
        header.setSectionResizeMode(6, QHeaderView.Stretch)  # دریافت‌کننده
        header.setSectionResizeMode(7, QHeaderView.Fixed)  # تاریخ سررسید
        header.setSectionResizeMode(8, QHeaderView.Fixed)  # وضعیت
        header.setSectionResizeMode(9, QHeaderView.Fixed)  # شماره فاکتور
        header.setSectionResizeMode(10, QHeaderView.Stretch)  # توضیحات
        header.setSectionResizeMode(11, QHeaderView.Fixed)  # عملیات
        
        table.setColumnWidth(0, 60)   # ردیف
        table.setColumnWidth(1, 100)  # شماره چک
        table.setColumnWidth(2, 80)   # نوع
        table.setColumnWidth(4, 120)  # مبلغ
        table.setColumnWidth(7, 110)  # تاریخ سررسید
        table.setColumnWidth(8, 100)  # وضعیت
        table.setColumnWidth(9, 100)  # شماره فاکتور
        table.setColumnWidth(11, 150) # عملیات
        
        # راست‌چین کردن هدرها
        for i in range(table.columnCount()):
            table.horizontalHeaderItem(i).setTextAlignment(Qt.AlignCenter)
        
        # کانتکست منو برای جدول
        table.setContextMenuPolicy(Qt.CustomContextMenu)
        table.customContextMenuRequested.connect(self.show_context_menu)
        
        return table
    
    def load_checks(self):
        """بارگذاری چک‌ها از دیتابیس"""
        try:
            # دریافت فیلترها
            filters = self.filters.copy()
            
            # دریافت چک‌ها از CheckManager
            checks = self.check_manager.get_all_checks(
                check_type=filters['check_type'],
                status=filters['status']
            )
            
            # پاک کردن محتوای جدول قبل از پر کردن مجدد
            self.table.clearContents()
            self.table.setRowCount(0)
            
            # پر کردن جدول
            self.table.setRowCount(len(checks))
            
            for row, check in enumerate(checks):
                # برای هر سلول باید آیتم جدید ایجاد کنید
                # هرگز از آیتم‌های قبلی دوباره استفاده نکنید
                
                # ردیف
                item_row = QTableWidgetItem(str(row + 1))
                item_row.setTextAlignment(Qt.AlignCenter)
                item_row.setBackground(self.get_status_color(check.get('status', '')))
                self.table.setItem(row, 0, item_row)
                
                # شماره چک
                item_check_num = QTableWidgetItem(check.get('check_number', ''))
                item_check_num.setTextAlignment(Qt.AlignCenter)
                item_check_num.setBackground(self.get_status_color(check.get('status', '')))
                self.table.setItem(row, 1, item_check_num)
                
                # نوع چک
                check_type = check.get('check_type', '')
                type_text = "💳 دریافتی" if check_type == 'دریافتی' else "💸 پرداختی"
                item_type = QTableWidgetItem(type_text)
                item_type.setTextAlignment(Qt.AlignCenter)
                item_type.setBackground(self.get_status_color(check.get('status', '')))
                self.table.setItem(row, 2, item_type)
                
                # بانک
                item_bank = QTableWidgetItem(check.get('bank_name', ''))
                item_bank.setTextAlignment(Qt.AlignCenter)
                item_bank.setBackground(self.get_status_color(check.get('status', '')))
                self.table.setItem(row, 3, item_bank)
                
                # مبلغ
                amount = check.get('amount_toman', 0)
                item_amount = QTableWidgetItem(f"{amount:,.0f}")
                item_amount.setTextAlignment(Qt.AlignCenter)
                item_amount.setBackground(self.get_status_color(check.get('status', '')))
                self.table.setItem(row, 4, item_amount)
                
                # صادرکننده
                item_drawer = QTableWidgetItem(check.get('drawer', ''))
                item_drawer.setTextAlignment(Qt.AlignRight)
                item_drawer.setBackground(self.get_status_color(check.get('status', '')))
                self.table.setItem(row, 5, item_drawer)
                
                # دریافت‌کننده
                item_payee = QTableWidgetItem(check.get('payee', ''))
                item_payee.setTextAlignment(Qt.AlignRight)
                item_payee.setBackground(self.get_status_color(check.get('status', '')))
                self.table.setItem(row, 6, item_payee)
                
                # تاریخ سررسید - تبدیل به شمسی
                due_date_raw = check.get('due_date', '')
                due_date_str = self.convert_to_jalali(due_date_raw) if due_date_raw else ''
                
                item_due_date = QTableWidgetItem(due_date_str)
                item_due_date.setTextAlignment(Qt.AlignCenter)
                
                # رنگ‌آمیزی تاریخ‌های گذشته
                if self.is_date_past(due_date_str) and check.get('status') in ['وصول نشده', 'پاس نشده']:
                    item_due_date.setForeground(QBrush(QColor('#ff6b6b')))  # قرمز
                
                item_due_date.setBackground(self.get_status_color(check.get('status', '')))
                self.table.setItem(row, 7, item_due_date)
                
                # وضعیت
                status_text = check.get('status', '')
                status_display = self.get_status_display(status_text)
                item_status = QTableWidgetItem(status_display)
                item_status.setTextAlignment(Qt.AlignCenter)
                item_status.setBackground(self.get_status_color(check.get('status', '')))
                self.table.setItem(row, 8, item_status)
                
                # شماره فاکتور
                invoice_num = check.get('invoice_number', '')
                item_invoice = QTableWidgetItem(invoice_num if invoice_num else '-')
                item_invoice.setTextAlignment(Qt.AlignCenter)
                item_invoice.setBackground(self.get_status_color(check.get('status', '')))
                self.table.setItem(row, 9, item_invoice)
                
                # توضیحات
                desc = check.get('description', '')
                if len(desc) > 30:
                    desc = desc[:27] + '...'
                item_desc = QTableWidgetItem(desc)
                item_desc.setTextAlignment(Qt.AlignRight)
                item_desc.setBackground(self.get_status_color(check.get('status', '')))
                self.table.setItem(row, 10, item_desc)
                
                # عملیات
                operations_widget = self.create_operations_widget(check['id'])
                self.table.setCellWidget(row, 11, operations_widget)
            
            # به‌روزرسانی آمار
            self.update_statistics(checks)
            
            # به‌روزرسانی وضعیت
            self.status_label.setText(f"تعداد چک‌ها: {len(checks)}")
            
            # به‌روزرسانی لیست بانک‌ها
            self.update_bank_list(checks)
            
        except Exception as e:
            print(f"⚠️ خطا در بارگذاری چک‌ها: {e}")
            QMessageBox.warning(self, "خطا", f"خطا در بارگذاری چک‌ها:\n{str(e)}")

    def convert_to_jalali(self, date_str):
        """تبدیل تاریخ میلادی به شمسی"""
        if not date_str:
            return ''
        
        try:
            # اگر تاریخ میلادی است (فرمت: YYYY-MM-DD)
            if '-' in date_str and len(date_str) == 10:
                year, month, day = map(int, date_str.split('-'))
                from datetime import date as datetime_date
                gdate = datetime_date(year, month, day)
                jdate = jdatetime.date.fromgregorian(date=gdate)
                return f"{jdate.year}/{jdate.month:02d}/{jdate.day:02d}"
            else:
                # اگر قبلاً شمسی ذخیره شده
                return date_str
        except Exception as e:
            print(f"⚠️ خطا در تبدیل تاریخ: {date_str}, خطا: {e}")
            return date_str


    def get_status_color(self, status):
        """رنگ بر اساس وضعیت چک"""
        colors = {
            'وصول شده': QColor('#27ae60'),  # سبز
            'وصول نشده': QColor('#f39c12'),  # نارنجی
            'برگشتی': QColor('#e74c3c'),  # قرمز
            'پاس شده': QColor('#3498db'),  # آبی
            'پاس نشده': QColor('#9b59b6'),  # بنفش
            'بلوکه شده': QColor('#7f8c8d'),  # خاکستری
        }
        return QBrush(colors.get(status, QColor('#2c3e50')))
    
    def get_status_display(self, status):
        """نمایش وضعیت با آیکون"""
        icons = {
            'وصول شده': '✅',
            'وصول نشده': '⏳',
            'برگشتی': '❌',
            'پاس شده': '✅',
            'پاس نشده': '⏳',
            'بلوکه شده': '🔒'
        }
        return f"{icons.get(status, '📄')} {status}"
    
    def is_date_past(self, date_str):
        """بررسی آیا تاریخ گذشته است"""
        try:
            if not date_str:
                return False
            
            # اگر رشته تاریخ مستقیماً از دیتابیس می‌آید (ممکن است میلادی باشد)
            # ابتدا بررسی می‌کنیم که آیا فرمت شمسی است
            if '/' in date_str:
                parts = date_str.split('/')
                if len(parts) == 3:
                    # اگر سال کوچکتر از 1500 باشد، شمسی است
                    year = int(parts[0])
                    if year < 1500:
                        # تاریخ شمسی
                        month, day = int(parts[1]), int(parts[2])
                        check_date = jdatetime.date(year, month, day)
                    else:
                        # تاریخ میلادی - تبدیل به شمسی
                        from datetime import date as datetime_date
                        gdate = datetime_date(year, int(parts[1]), int(parts[2]))
                        check_date = jdatetime.date.fromgregorian(date=gdate)
                    
                    today = jdatetime.date.today()
                    return check_date < today
                    
            elif '-' in date_str:
                # فرمت میلادی YYYY-MM-DD
                parts = date_str.split('-')
                if len(parts) == 3:
                    year, month, day = map(int, parts)
                    from datetime import date as datetime_date
                    gdate = datetime_date(year, month, day)
                    check_date = jdatetime.date.fromgregorian(date=gdate)
                    today = jdatetime.date.today()
                    return check_date < today
                    
        except Exception as e:
            print(f"⚠️ خطا در بررسی تاریخ گذشته: {e}")
            return False
        return False

    def create_operations_widget(self, check_id):
        """ایجاد ویجت عملیات برای هر ردیف"""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(5, 2, 5, 2)
        layout.setSpacing(5)
        
        # دکمه ویرایش
        btn_edit = QPushButton("✏️")
        btn_edit.setToolTip("ویرایش چک")
        btn_edit.setFixedSize(30, 30)
        btn_edit.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        btn_edit.clicked.connect(lambda: self.edit_check(check_id))
        
        # دکمه تغییر وضعیت
        btn_status = QPushButton("🔄")
        btn_status.setToolTip("تغییر وضعیت")
        btn_status.setFixedSize(30, 30)
        btn_status.setStyleSheet("""
            QPushButton {
                background-color: #f39c12;
                color: white;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #e67e22;
            }
        """)
        btn_status.clicked.connect(lambda: self.change_single_check_status(check_id))
        
        # دکمه حذف
        btn_delete = QPushButton("🗑️")
        btn_delete.setToolTip("حذف چک")
        btn_delete.setFixedSize(30, 30)
        btn_delete.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        btn_delete.clicked.connect(lambda: self.delete_check(check_id))
        
        layout.addWidget(btn_edit)
        layout.addWidget(btn_status)
        layout.addWidget(btn_delete)
        layout.addStretch()
        
        return widget
    
    def update_statistics(self, checks):
        """به‌روزرسانی آمار چک‌ها"""
        try:
            stats = {
                'received': 0,
                'paid': 0,
                'due': 0,
                'bounced': 0
            }
            
            today = jdatetime.date.today()
            
            for check in checks:
                # شمارش بر اساس نوع
                if check.get('check_type') == 'دریافتی':
                    stats['received'] += 1
                else:
                    stats['paid'] += 1
                
                # شمارش چک‌های سررسید
                # در حلقه for چک‌ها، بخش بررسی سررسید:

                # شمارش چک‌های سررسید
                due_date_str = check.get('due_date', '')
                if due_date_str:
                    try:
                        # اگر تاریخ میلادی است
                        if '-' in due_date_str and len(due_date_str) == 10:
                            year, month, day = map(int, due_date_str.split('-'))
                            from datetime import date as datetime_date
                            gdate = datetime_date(year, month, day)
                            due_date = jdatetime.date.fromgregorian(date=gdate)
                        else:
                            # اگر شمسی است
                            parts = due_date_str.split('/')
                            if len(parts) == 3:
                                year, month, day = map(int, parts)
                                due_date = jdatetime.date(year, month, day)
                            else:
                                continue
                                
                        if due_date < today and check.get('status') in ['وصول نشده', 'پاس نشده']:
                            stats['due'] += 1
                    except:
                        pass
                
                # شمارش چک‌های برگشتی
                if check.get('status') == 'برگشتی':
                    stats['bounced'] += 1
            
            # به‌روزرسانی کارت‌ها
            if 'received' in self.stat_cards:
                self.stat_cards['received'].value_label.setText(str(stats['received']))
            
            if 'paid' in self.stat_cards:
                self.stat_cards['paid'].value_label.setText(str(stats['paid']))
            
            if 'due' in self.stat_cards:
                self.stat_cards['due'].value_label.setText(str(stats['due']))
                if stats['due'] > 0:
                    self.stat_cards['due'].value_label.setStyleSheet(
                        "color: #ff6b6b; font-size: 16pt; font-weight: bold;"
                    )
            
            if 'bounced' in self.stat_cards:
                self.stat_cards['bounced'].value_label.setText(str(stats['bounced']))
                
        except Exception as e:
            print(f"⚠️ خطا در به‌روزرسانی آمار: {e}")
    
    def update_bank_list(self, checks):
        """به‌روزرسانی لیست بانک‌ها"""
        try:
            banks = set()
            for check in checks:
                bank = check.get('bank_name', '')
                if bank:
                    banks.add(bank)
            
            current_text = self.bank_combo.currentText()
            self.bank_combo.clear()
            self.bank_combo.addItem("همه", "")
            
            for bank in sorted(banks):
                self.bank_combo.addItem(bank, bank)
            
            # بازگرداندن انتخاب قبلی
            index = self.bank_combo.findData(current_text)
            if index >= 0:
                self.bank_combo.setCurrentIndex(index)
                
        except Exception as e:
            print(f"⚠️ خطا در به‌روزرسانی لیست بانک‌ها: {e}")

    def apply_filters(self):
        """اعمال فیلترها - نسخه اصلاح شده بدون حلقه بی‌نهایت"""
        try:
            # جلوگیری از فراخوانی‌های مکرر
            if hasattr(self, '_is_applying_filters') and self._is_applying_filters:
                return
            
            self._is_applying_filters = True
            
            # جمع‌آوری فیلترها بدون ایجاد سیگنال
            self._collect_filters_silently()
            
            # بارگذاری داده‌ها با تاخیر
            QTimer.singleShot(100, self._load_checks_with_filters)
            
        except Exception as e:
            print(f"⚠️ خطا در اعمال فیلترها: {e}")
        finally:
            # پس از 200ms فلگ را آزاد کن
            QTimer.singleShot(200, lambda: setattr(self, '_is_applying_filters', False))

    def _collect_filters_silently(self):
        """جمع‌آوری فیلترها بدون ایجاد سیگنال"""
        # موقتاً سیگنال‌ها را قطع کن
        try:
            self.type_combo.currentIndexChanged.disconnect()
            self.status_combo.currentIndexChanged.disconnect()
            self.start_date_input.date_changed.disconnect()
            self.end_date_input.date_changed.disconnect()
            self.name_search_input.textChanged.disconnect()
        except:
            pass
        
        # جمع‌آوری فیلترها
        self.filters = {
            'check_type': self.type_combo.currentData(),
            'status': self.status_combo.currentData(),
            'bank_name': self.bank_combo.currentText() if self.bank_combo.currentText() != "همه" else "",
            'start_date': self.start_date_input.get_date(),
            'end_date': self.end_date_input.get_date(),
            'drawer': self.name_search_input.text().strip(),
            'payee': self.name_search_input.text().strip()
        }
        
        # اتصال مجدد سیگنال‌ها
        QTimer.singleShot(300, self._reconnect_filters_signals)

    def _reconnect_filters_signals(self):
        """اتصال مجدد سیگنال‌های فیلتر"""
        try:
            self.type_combo.currentIndexChanged.connect(self.apply_filters)
            self.status_combo.currentIndexChanged.connect(self.apply_filters)
            self.start_date_input.date_changed.connect(self.apply_filters)
            self.end_date_input.date_changed.connect(self.apply_filters)
            self.name_search_input.textChanged.connect(self.apply_filters)
        except:
            pass

    def _load_checks_with_filters(self):
        """بارگذاری چک‌ها با فیلترهای اعمال شده"""
        try:
            self.load_checks()
        except Exception as e:
            print(f"⚠️ خطا در بارگذاری چک‌ها: {e}")
        finally:
            # فلگ را آزاد کن
            if hasattr(self, '_is_applying_filters'):
                self._is_applying_filters = False

# در متد clear_filters، خطوط مربوط به تاریخ را اصلاح کنید:

    def clear_filters(self):
        """پاک کردن تمام فیلترها"""
        self.type_combo.setCurrentIndex(0)
        self.status_combo.setCurrentIndex(0)
        self.bank_combo.setCurrentIndex(0)
        
        # اصلاح این دو خط - استفاده از متدهای صحیح
        self.start_date_input.set_date(jdatetime.date.today())  # تاریخ امروز
        self.end_date_input.set_date(jdatetime.date.today())    # تاریخ امروز
        
        self.name_search_input.clear()
        
        self.filters = {
            'check_type': None,
            'status': None,
            'bank_name': '',
            'drawer': '',
            'payee': '',
            'start_date': None,
            'end_date': None
        }
        
        self.load_checks()

    def show_context_menu(self, position):
        """نمایش منوی راست‌کلیک"""
        menu = QMenu()
        
        row = self.table.rowAt(position.y())
        if row >= 0:
            # دریافت شناسه چک از ردیف انتخاب شده
            check_id = self.get_check_id_from_row(row)
            
            if check_id:
                menu.addAction("✏️ ویرایش چک", lambda: self.edit_check(check_id))
                menu.addAction("🔄 تغییر وضعیت", lambda: self.change_single_check_status(check_id))
                menu.addAction("🗑️ حذف چک", lambda: self.delete_check(check_id))
                menu.addSeparator()
        
        menu.addAction("➕ ثبت چک جدید", self.add_received_check)
        menu.addAction("📊 مشاهده گزارش", self.show_checks_report)
        menu.addAction("🔄 بارگذاری مجدد", self.load_checks)
        
        menu.exec(self.table.viewport().mapToGlobal(position))
    
    def get_check_id_from_row(self, row):
        """دریافت شناسه چک از ردیف جدول"""
        try:
            # از دکمه‌های عملیات می‌توانیم شناسه را بگیریم
            widget = self.table.cellWidget(row, 11)
            if widget:
                # اولین دکمه (ویرایش) را بگیریم
                btn = widget.layout().itemAt(0).widget()
                if btn:
                    # شناسه را از lambda ذخیره شده بگیریم
                    # این نیاز به پیاده‌سازی متفاوت دارد
                    # برای سادگی، از دیتابیس بر اساس شماره چک می‌گیریم
                    check_number_item = self.table.item(row, 1)
                    if check_number_item:
                        check_number = check_number_item.text()
                        # جستجو در دیتابیس
                        query = "SELECT id FROM Checks WHERE check_number = ?"
                        result = self.db.fetch_one(query, (check_number,))
                        if result:
                            return result.get('id')
        except:
            pass
        return None
    
    # ---------- عملیات اصلی ----------
    
    def add_received_check(self):
        """ثبت چک دریافتی"""
        self.open_check_dialog('دریافتی')
    
    def add_paid_check(self):
        """ثبت چک پرداختی"""
        self.open_check_dialog('پرداختی')
    
    def open_check_dialog(self, check_type):
        """باز کردن دیالوگ ثبت چک"""
        try:
            from ui.forms.accounting.dialogs.check_dialog import CheckDialog
            dialog = CheckDialog(self.data_manager, check_type, parent=self)
            if dialog.exec():
                self.load_checks()
                self.data_changed.emit()
        except ImportError as e:
            print(f"⚠️ دیالوگ چک در دسترس نیست: {e}")
            self.show_simple_check_dialog(check_type)
        except Exception as e:
            print(f"⚠️ خطا در باز کردن دیالوگ چک: {e}")
            self.show_simple_check_dialog(check_type)
    
    def show_simple_check_dialog(self, check_type):
        """دیالوگ ساده برای مواقعی که دیالوگ اصلی در دسترس نیست"""
        from PySide6.QtWidgets import QDialog, QFormLayout, QDialogButtonBox
        
        dialog = QDialog(self)
        dialog.setWindowTitle(f"ثبت چک {check_type}")
        dialog.setFixedSize(500, 600)
        
        layout = QFormLayout(dialog)
        
        # فیلدهای ساده
        from PySide6.QtWidgets import QLineEdit, QComboBox
        from ui.widgets.jalali_date_input import JalaliDateInput
        
        fields = {}
        
        fields['check_number'] = QLineEdit()
        fields['bank_name'] = QLineEdit()
        fields['amount'] = QLineEdit()
        fields['drawer'] = QLineEdit()
        fields['payee'] = QLineEdit()
        fields['due_date'] = JalaliDateInput()
        fields['status'] = QComboBox()
        fields['status'].addItems(['وصول نشده', 'وصول شده', 'برگشتی'])
        fields['description'] = QLineEdit()
        
        for label, field in [
            ("شماره چک:", fields['check_number']),
            ("بانک:", fields['bank_name']),
            ("مبلغ (تومان):", fields['amount']),
            ("صادرکننده:", fields['drawer']),
            ("دریافت‌کننده:", fields['payee']),
            ("تاریخ سررسید:", fields['due_date']),
            ("وضعیت:", fields['status']),
            ("توضیحات:", fields['description'])
        ]:
            layout.addRow(label, field)
        
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        
        layout.addRow(buttons)
        
        if dialog.exec():
            try:
                # ثبت چک
                check_data = {
                    'check_number': fields['check_number'].text(),
                    'bank_name': fields['bank_name'].text(),
                    'amount': float(fields['amount'].text() or 0),
                    'drawer': fields['drawer'].text(),
                    'payee': fields['payee'].text(),
                    'due_date': fields['due_date'].get_date_string(),
                    'status': fields['status'].currentText(),
                    'check_type': check_type,
                    'description': fields['description'].text()
                }
                
                success, message = self.check_manager.create_check(check_data)
                if success:
                    QMessageBox.information(self, "موفق", message)
                    self.load_checks()
                    self.data_changed.emit()
                else:
                    QMessageBox.warning(self, "خطا", message)
                    
            except Exception as e:
                QMessageBox.warning(self, "خطا", f"خطا در ثبت چک:\n{str(e)}")
    
    def edit_check(self, check_id):
        """ویرایش چک"""
        try:
            from ui.forms.accounting.dialogs.check_dialog import CheckDialog
            dialog = CheckDialog(self.data_manager, check_id=check_id, parent=self)
            if dialog.exec():
                self.load_checks()
                self.data_changed.emit()
        except Exception as e:
            print(f"⚠️ خطا در ویرایش چک: {e}")
            QMessageBox.warning(self, "خطا", f"خطا در ویرایش چک:\n{str(e)}")
    
    def change_check_status(self):
        """تغییر وضعیت چک انتخابی"""
        selected_row = self.table.currentRow()
        if selected_row < 0:
            QMessageBox.warning(self, "هشدار", "لطفاً یک چک را انتخاب کنید.")
            return
        
        check_id = self.get_check_id_from_row(selected_row)
        if check_id:
            self.change_single_check_status(check_id)

    def change_single_check_status(self, check_id):
        """تغییر وضعیت یک چک خاص - نسخه اصلاح شده"""
        try:
            # دریافت اطلاعات چک
            check = self.check_manager.get_check_by_id(check_id)
            if not check:
                QMessageBox.warning(self, "خطا", "چک مورد نظر یافت نشد.")
                return
            
            from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QComboBox, QDialogButtonBox
            
            dialog = QDialog(self)
            dialog.setWindowTitle("تغییر وضعیت چک")
            dialog.setFixedSize(350, 200)
            
            layout = QVBoxLayout(dialog)
            
            # اطلاعات چک
            info_label = QLabel(
                f"📄 چک شماره: {check.get('check_number', '')}\n"
                f"💰 مبلغ: {check.get('amount', 0)/10:,.0f} تومان\n"
                f"🏦 بانک: {check.get('bank_name', '')}\n"
                f"📅 سررسید: {self.db.gregorian_to_jalali(check.get('due_date', '')) if check.get('due_date') else ''}"
            )
            layout.addWidget(info_label)
            
            # وضعیت جدید
            status_label = QLabel("وضعیت جدید:")
            layout.addWidget(status_label)
            
            status_combo = QComboBox()
            status_combo.addItems([
                'وصول نشده',
                'وصول شده', 
                'برگشتی',
                'پاس شده',
                'پاس نشده',
                'بلوکه شده'
            ])
            
            # تنظیم وضعیت فعلی
            current_status = check.get('status', 'وصول نشده')
            index = status_combo.findText(current_status)
            if index >= 0:
                status_combo.setCurrentIndex(index)
            
            layout.addWidget(status_combo)
            
            buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
            
            def on_accepted():
                new_status = status_combo.currentText()
                
                # 🔴 **اصلاح این بخش: استفاده از مقدار بازگشتی به درستی**
                result = self.check_manager.update_check_status(check_id, new_status)
                
                if isinstance(result, tuple) and len(result) == 2:
                    success, message = result
                elif isinstance(result, bool):
                    # اگر فقط boolean برگرداند
                    success = result
                    message = "عملیات انجام شد" if success else "خطا در تغییر وضعیت"
                else:
                    success = False
                    message = "خطا در دریافت نتیجه"
                
                if success:
                    QMessageBox.information(self, "موفق", message)
                    self.load_checks()
                    self.data_changed.emit()
                    dialog.accept()
                else:
                    QMessageBox.warning(self, "خطا", message)
            
            buttons.accepted.connect(on_accepted)
            buttons.rejected.connect(dialog.reject)
            
            layout.addWidget(buttons)
            
            dialog.exec()
            
        except Exception as e:
            print(f"⚠️ خطا در تغییر وضعیت: {e}")
            QMessageBox.warning(self, "خطا", f"خطا در تغییر وضعیت:\n{str(e)}")
   
    def delete_check(self, check_id):
        """حذف چک"""
        try:
            reply = QMessageBox.question(
                self, "تأیید حذف",
                "آیا از حذف این چک اطمینان دارید؟\nاین عمل غیرقابل بازگشت است.",
                QMessageBox.Yes | QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                # حذف از دیتابیس
                query = "DELETE FROM Checks WHERE id = ?"
                success = self.db.execute_query(query, (check_id,))
                
                if success:
                    QMessageBox.information(self, "موفق", "چک با موفقیت حذف شد.")
                    self.load_checks()
                    self.data_changed.emit()
                else:
                    QMessageBox.warning(self, "خطا", "خطا در حذف چک.")
                    
        except Exception as e:
            QMessageBox.warning(self, "خطا", f"خطا در حذف چک:\n{str(e)}")
    
    def print_checks_list(self):
        """چاپ لیست چک‌ها"""
        QMessageBox.information(self, "چاپ", "امکان چاپ به زودی اضافه خواهد شد.")
    
    def show_checks_report(self):
        """نمایش گزارش چک‌ها"""
        try:
            from ui.forms.accounting.reports.check_report import CheckReportDialog
            dialog = CheckReportDialog(self.data_manager, parent=self)
            dialog.exec()
        except ImportError as e:
            print(f"⚠️ خطا در بارگذاری گزارش چک‌ها: {e}")
            self.show_simple_report()
    
    def show_simple_report(self):
        """گزارش ساده"""
        try:
            stats = self.check_manager.get_check_statistics()
            
            report_text = "📊 گزارش چک‌ها\n\n"
            
            total_received = 0
            total_paid = 0
            
            for stat in stats:
                check_type = stat.get('check_type', '')
                status = stat.get('status', '')
                count = stat.get('count', 0)
                amount = stat.get('total_amount_toman', 0)
                
                if check_type == 'دریافتی':
                    total_received += amount
                else:
                    total_paid += amount
                
                report_text += f"{check_type} - {status}: {count} چک - {amount:,.0f} تومان\n"
            
            report_text += f"\n💰 جمع دریافتی: {total_received:,.0f} تومان"
            report_text += f"\n💸 جمع پرداختی: {total_paid:,.0f} تومان"
            report_text += f"\n🧮 مانده: {(total_received - total_paid):,.0f} تومان"
            
            # نمایش در دیالوگ
            from PySide6.QtWidgets import QDialog, QVBoxLayout, QTextEdit, QPushButton
            
            dialog = QDialog(self)
            dialog.setWindowTitle("گزارش چک‌ها")
            dialog.setFixedSize(400, 500)
            
            layout = QVBoxLayout(dialog)
            
            text_edit = QTextEdit()
            text_edit.setPlainText(report_text)
            text_edit.setReadOnly(True)
            text_edit.setStyleSheet("""
                QTextEdit {
                    background-color: #111111;
                    color: white;
                    font-family: 'B Nazanin';
                    font-size: 11pt;
                    border: 1px solid #333;
                    border-radius: 5px;
                    padding: 10px;
                }
            """)
            
            layout.addWidget(text_edit)
            
            btn_close = QPushButton("بستن")
            btn_close.clicked.connect(dialog.accept)
            layout.addWidget(btn_close)
            
            dialog.exec()
            
        except Exception as e:
            QMessageBox.warning(self, "خطا", f"خطا در ایجاد گزارش:\n{str(e)}")
    
    def check_due_checks(self):
        """بررسی چک‌های سررسید"""
        try:
            due_checks = self.check_manager.get_due_checks(days=3)
            
            if due_checks:
                check_count = len(due_checks)
                
                # نمایش اعلان
                from PySide6.QtWidgets import QMessageBox
                
                msg = QMessageBox(self)
                msg.setIcon(QMessageBox.Warning)
                msg.setWindowTitle("⚠️ هشدار سررسید چک‌ها")
                msg.setText(f"تعداد {check_count} چک در آستانه سررسید هستند.")
                msg.setInformativeText("برای مشاهده جزئیات به بخش چک‌ها مراجعه کنید.")
                msg.setStandardButtons(QMessageBox.Ok)
                msg.exec()
                
        except Exception as e:
            print(f"⚠️ خطا در بررسی چک‌های سررسید: {e}")
    
    def refresh_data(self):
        """بارگذاری مجدد داده‌ها"""
        self.load_checks()