# ui/forms/person_form.py - فرم مدیریت اشخاص با اسکرول بار اصلی
"""
📋 فرم مدیریت اشخاص - سیستم تعمیرگاه

🔸 توضیحات:
این فرم برای ثبت و ویرایش اطلاعات اشخاص (مشتریان، تامین‌کنندگان، شرکا و ...) استفاده می‌شود.
فرم دارای 5 تب اصلی است:
1. 🔍 جستجو - جستجوی زنده در بین اشخاص
2. 📋 اطلاعات پایه - اطلاعات اصلی شخص
3. 📞 اطلاعات تماس - شماره‌ها و آدرس
4. 💰 اطلاعات مالی - حساب‌های بانکی
5. 📜 تاریخچه - پذیرش‌ها و تراکنش‌های مالی

🔸 نحوه استفاده:
- برای ثبت شخص جدید: PersonForm(data_manager)
- برای ویرایش شخص: PersonForm(data_manager, person_id=123)
- کلید میانبر Ctrl+S: ذخیره
- کلید میانبر Escape: انصراف
- Tab: حرکت بین فیلدها

🔸 ویژگی‌ها:
- رابط کاربری راست‌چین کامل
- تم تاریک (زمینه سیاه، متن سفید)
- جستجوی زنده در تب جستجو
- اعتبارسنجی فیلدها
- تاریخ شمسی با تقویم فارسی
- اسکرول عمودی و افقی
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QComboBox, QTextEdit, QGroupBox,
    QFormLayout, QMessageBox, QFrame, QTableWidget,
    QTableWidgetItem, QHeaderView, QTabWidget, QCheckBox,
    QScrollArea, QSizePolicy
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QColor, QIcon
import jdatetime

# ایمپورت ویجت تاریخ شمسی
from ui.widgets.jalali_date_input import JalaliDateInput

class PersonForm(QWidget):
    """
    فرم مدیریت اشخاص
    
    📌 پارامترهای ورودی:
        data_manager: نمونه‌ای از DataManager برای دسترسی به دیتابیس
        person_id: شناسه شخص برای ویرایش (اگر None باشد فرم ثبت جدید است)
    """
    
    person_saved = Signal(dict)    # سیگنال هنگام ذخیره شخص
    person_deleted = Signal(int)   # سیگنال هنگام حذف شخص
    form_closed = Signal()         # سیگنال هنگام بستن فرم
    
    def __init__(self, data_manager, person_id=None):
        """
        سازنده فرم
        
        🔹 پارامترها:
            data_manager: مدیر داده‌های برنامه
            person_id: کد شخص برای ویرایش
        """
        super().__init__()
        self.data_manager = data_manager
        self.person_id = person_id
        self.current_person = None
        self.setup_colors()
        self.init_ui()
        self.load_person_data()
        
    def setup_colors(self):
        """تنظیم پالت رنگ با تم تاریک"""
        self.colors = {
            'bg_dark': '#000000',           # زمینه اصلی
            'bg_widget': '#111111',         # زمینه ویجت‌ها
            'bg_input': '#1a1a1a',          # زمینه فیلدهای ورودی
            'text_primary': '#ffffff',      # متن اصلی
            'text_secondary': '#cccccc',    # متن ثانویه
            'border': '#333333',            # حاشیه
            'primary': '#3498db',           # رنگ اصلی (آبی)
            'success': '#27ae60',           # موفقیت (سبز)
            'warning': '#f39c12',           # هشدار (نارنجی)
            'danger': '#e74c3c',            # خطا (قرمز)
            'tab_active': '#2980b9',        # تب فعال
            'tab_inactive': '#2c3e50',      # تب غیرفعال
        }
        
    def init_ui(self):
        """راه‌اندازی رابط کاربری"""
        self.setWindowTitle("👤 مدیریت اشخاص - سیستم تعمیرگاه")
        self.setMinimumSize(1000, 700)
        
        # 🔴 راست‌چین کردن کل فرم
        self.setLayoutDirection(Qt.RightToLeft)
        
        # استایل کلی
        self.setStyleSheet(self.get_style_sheet())
        
        # لایه اصلی با اسکرول
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # ایجاد ناحیه اسکرول
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        # ویجت محتوای اصلی
        self.content_widget = QWidget()
        self.content_widget.setObjectName("content_widget")
        content_layout = QVBoxLayout(self.content_widget)
        content_layout.setContentsMargins(20, 20, 20, 20)
        content_layout.setSpacing(20)
        
        # هدر فرم
        header_frame = self.create_header_frame()
        content_layout.addWidget(header_frame)
        
        # تب‌ها
        self.tab_widget = QTabWidget()
        self.tab_widget.setLayoutDirection(Qt.RightToLeft)
        self.tab_widget.setTabPosition(QTabWidget.North)
        
        # اضافه کردن تب‌ها
        self.tab_widget.addTab(self.create_search_tab(), "🔍 جستجو")
        self.tab_widget.addTab(self.create_basic_info_tab(), "📋 اطلاعات پایه")
        self.tab_widget.addTab(self.create_contact_info_tab(), "📞 اطلاعات تماس")
        self.tab_widget.addTab(self.create_financial_info_tab(), "💰 اطلاعات مالی")
        self.tab_widget.addTab(self.create_history_tab(), "📜 تاریخچه")
        
        content_layout.addWidget(self.tab_widget)
        
        # دکمه‌های اقدام
        actions_frame = self.create_actions_frame()
        content_layout.addWidget(actions_frame)
        
        # کشسان برای فاصله
        content_layout.addStretch()
        
        self.scroll_area.setWidget(self.content_widget)
        main_layout.addWidget(self.scroll_area)
        
        # تنظیم اتصالات
        self.setup_connections()
        
    def get_style_sheet(self):
        """استایل‌شیت فرم با تم تاریک کامل"""
        colors = self.colors
        return f"""
        /* 🔴 استایل کلی - راست‌چین کامل */
        QWidget {{
            layout-direction: rtl;
            font-family: 'B Nazanin', Tahoma;
            background-color: {colors['bg_dark']};
            color: {colors['text_primary']};
            font-size: 12px;
        }}
        
        QScrollArea {{
            background-color: {colors['bg_dark']};
            border: none;
        }}
        
        QLabel, QLineEdit, QTextEdit, QComboBox, QPushButton, 
        QTableWidget, QGroupBox, QTabWidget {{
            layout-direction: rtl;
        }}
        
        QLineEdit, QTextEdit {{
            text-align: right;
            background-color: {colors['bg_input']};
            border: 1px solid {colors['border']};
            border-radius: 4px;
            padding: 8px;
            color: {colors['text_primary']};
            font-size: 13px;
        }}
        
        QLineEdit:focus, QTextEdit:focus {{
            border: 2px solid {colors['primary']};
        }}
        
        QPushButton {{
            padding: 10px 20px;
            border-radius: 5px;
            font-weight: bold;
            border: none;
            font-size: 13px;
            min-height: 40px;
            min-width: 100px;
        }}
        
        QPushButton#saveButton {{
            background-color: {colors['success']};
            color: white;
        }}
        
        QPushButton#deleteButton {{
            background-color: {colors['danger']};
            color: white;
        }}
        
        QPushButton#cancelButton {{
            background-color: #7f8c8d;
            color: white;
        }}
        
        QGroupBox {{
            font-weight: bold;
            border: 2px solid {colors['border']};
            border-radius: 8px;
            margin-top: 10px;
            padding-top: 15px;
            background-color: {colors['bg_widget']};
            color: {colors['text_primary']};
            font-size: 14px;
        }}
        
        QTabWidget::pane {{
            border: 1px solid {colors['border']};
            background-color: {colors['bg_dark']};
        }}
        
        QTabBar::tab {{
            background-color: {colors['tab_inactive']};
            color: {colors['text_secondary']};
            padding: 10px 20px;
            margin-right: 2px;
        }}
        
        QTabBar::tab:selected {{
            background-color: {colors['tab_active']};
            color: white;
            font-weight: bold;
        }}
        
        QTableWidget {{
            background-color: {colors['bg_widget']};
            alternate-background-color: {colors['bg_input']};
            selection-background-color: {colors['primary']};
            gridline-color: {colors['border']};
        }}
        
        QHeaderView::section {{
            background-color: #222222;
            color: white;
            padding: 10px;
            border: none;
            font-weight: bold;
        }}
        
        QScrollBar:vertical, QScrollBar:horizontal {{
            background-color: {colors['bg_widget']};
            width: 16px;
            height: 16px;
            border-radius: 8px;
        }}
        
        QScrollBar::handle:vertical, QScrollBar::handle:horizontal {{
            background-color: {colors['border']};
            border-radius: 8px;
            min-height: 30px;
            min-width: 30px;
        }}
        
        QScrollBar::handle:hover {{
            background-color: #444444;
        }}
        """
    
    def create_header_frame(self):
        """ایجاد هدر فرم با دکمه‌های سریع"""
        frame = QFrame()
        frame.setStyleSheet(f"""
            QFrame {{
                background-color: {self.colors['primary']};
                border-radius: 8px;
                padding: 15px;
            }}
        """)
        
        layout = QHBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        
        # عنوان
        title_text = "👤 ویرایش شخص" if self.person_id else "👤 ثبت شخص جدید"
        title = QLabel(title_text)
        title.setStyleSheet(f"""
            QLabel {{
                font-size: 20px;
                font-weight: bold;
                color: white;
            }}
        """)
        
        layout.addWidget(title)
        layout.addStretch()
        
        # دکمه‌های عملیات سریع
        if self.person_id:
            # دکمه مشاهده پذیرش‌ها
            btn_receptions = QPushButton("📋 پذیرش‌ها")
            btn_receptions.setStyleSheet("""
                QPushButton {
                    background-color: #9b59b6;
                    color: white;
                    padding: 5px 15px;
                    border-radius: 4px;
                    font-size: 11px;
                }
                QPushButton:hover {
                    background-color: #8e44ad;
                }
            """)
            btn_receptions.clicked.connect(self.view_person_receptions)
            layout.addWidget(btn_receptions)
            
            # دکمه مشاهده فاکتورها
            btn_invoices = QPushButton("🧾 فاکتورها")
            btn_invoices.setStyleSheet("""
                QPushButton {
                    background-color: #e67e22;
                    color: white;
                    padding: 5px 15px;
                    border-radius: 4px;
                    font-size: 11px;
                }
                QPushButton:hover {
                    background-color: #d35400;
                }
            """)
            btn_invoices.clicked.connect(self.view_person_invoices)
            layout.addWidget(btn_invoices)
        
        # دکمه جدید
        btn_new = QPushButton("➕ جدید")
        btn_new.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                padding: 5px 15px;
                border-radius: 4px;
                font-size: 11px;
            }
            QPushButton:hover {
                background-color: #219653;
            }
        """)
        btn_new.clicked.connect(self.clear_form)
        layout.addWidget(btn_new)
        
        # شماره شخص
        if self.person_id:
            id_label = QLabel(f"کد: {self.person_id}")
            id_label.setStyleSheet(f"""
                QLabel {{
                    font-size: 14px;
                    color: white;
                    background-color: rgba(0, 0, 0, 0.3);
                    padding: 5px 15px;
                    border-radius: 15px;
                }}
            """)
            layout.addWidget(id_label)
        
        frame.setLayout(layout)
        return frame
    
    def create_search_tab(self):
        """ایجاد تب جستجو با جستجوی زنده"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(15)
        
        # راهنمای جستجو
        help_label = QLabel("🔍 برای جستجوی زنده، در هر یک از فیلدها شروع به تایپ کنید")
        help_label.setStyleSheet(f"""
            QLabel {{
                background-color: {self.colors['primary']};
                color: white;
                padding: 10px;
                border-radius: 5px;
                font-size: 12px;
            }}
        """)
        layout.addWidget(help_label)
        
        # گروه جستجو
        search_group = QGroupBox("جستجوی پیشرفته اشخاص")
        search_layout = QFormLayout()
        search_layout.setSpacing(12)
        search_layout.setLabelAlignment(Qt.AlignRight)
        
        # فیلدهای جستجو
        self.search_name_input = QLineEdit()
        self.search_name_input.setPlaceholderText("نام یا نام خانوادگی")
        self.search_name_input.textChanged.connect(self.perform_search)
        search_layout.addRow("نام:", self.search_name_input)
        
        self.search_mobile_input = QLineEdit()
        self.search_mobile_input.setPlaceholderText("09xxxxxxxxx")
        self.search_mobile_input.textChanged.connect(self.perform_search)
        search_layout.addRow("موبایل:", self.search_mobile_input)
        
        self.search_national_id_input = QLineEdit()
        self.search_national_id_input.setPlaceholderText("کد ملی")
        self.search_national_id_input.textChanged.connect(self.perform_search)
        search_layout.addRow("کد ملی:", self.search_national_id_input)
        
        search_group.setLayout(search_layout)
        layout.addWidget(search_group)
        
        # جدول نتایج
        results_group = QGroupBox("نتایج جستجو")
        results_layout = QVBoxLayout()
        
        self.search_results_table = QTableWidget()
        self.search_results_table.setColumnCount(6)
        self.search_results_table.setHorizontalHeaderLabels([
            "کد", "نام", "نام خانوادگی", "موبایل", "نوع", "تاریخ ثبت"
        ])
        self.search_results_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.search_results_table.setSelectionMode(QTableWidget.SingleSelection)
        self.search_results_table.doubleClicked.connect(self.on_search_result_double_clicked)
        
        # تنظیم سایز ستون‌ها
        header = self.search_results_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # کد
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)  # نام
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)  # نام خانوادگی
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)  # موبایل
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)  # نوع
        header.setSectionResizeMode(5, QHeaderView.Stretch)          # تاریخ ثبت
        
        results_layout.addWidget(self.search_results_table)
        results_group.setLayout(results_layout)
        layout.addWidget(results_group)
        
        layout.addStretch()
        return widget
    
    def perform_search(self):
        """انجام جستجوی زنده"""
        # جمع‌آوری شرایط جستجو
        name = self.search_name_input.text().strip()
        mobile = self.search_mobile_input.text().strip()
        national_id = self.search_national_id_input.text().strip()
        
        # اگر همه فیلدها خالی هستند، جدول را خالی کنید
        if not any([name, mobile, national_id]):
            self.search_results_table.setRowCount(0)
            return
        
        # جستجو در دیتابیس
        results = []
        try:
            if name:
                # استفاده از متد search_persons موجود در models.py
                results = self.data_manager.person.search_persons(name)
            else:
                # اگر فقط موبایل یا کد ملی وارد شده
                all_persons = self.data_manager.person.get_all_persons()
                for person in all_persons:
                    if (mobile and mobile in str(person.get('mobile', ''))) or \
                       (national_id and national_id in str(person.get('national_id', ''))):
                        results.append(person)
        
        except Exception as e:
            print(f"خطا در جستجو: {e}")
            results = []
        
        # نمایش نتایج
        self.display_search_results(results)
    
    def display_search_results(self, results):
        """نمایش نتایج جستجو در جدول"""
        self.search_results_table.setRowCount(len(results))
        
        for row, person in enumerate(results):
            self.search_results_table.setItem(row, 0, 
                QTableWidgetItem(str(person.get('id', ''))))
            self.search_results_table.setItem(row, 1, 
                QTableWidgetItem(person.get('first_name', '')))
            self.search_results_table.setItem(row, 2, 
                QTableWidgetItem(person.get('last_name', '')))
            self.search_results_table.setItem(row, 3, 
                QTableWidgetItem(person.get('mobile', '')))
            self.search_results_table.setItem(row, 4, 
                QTableWidgetItem(person.get('person_type', '')))
            self.search_results_table.setItem(row, 5, 
                QTableWidgetItem(person.get('registration_date', '')))
            
            # تنظیم ارتفاع سطر
            self.search_results_table.setRowHeight(row, 35)
    
    def on_search_result_double_clicked(self, index):
        """هنگام دابل‌کلیک روی نتیجه جستجو"""
        row = index.row()
        person_id_item = self.search_results_table.item(row, 0)
        if person_id_item:
            person_id = int(person_id_item.text())
            
            # بارگذاری شخص انتخاب شده
            self.person_id = person_id
            self.load_person_data()
            
            # تغییر به تب اطلاعات پایه
            self.tab_widget.setCurrentIndex(1)
    
    def create_basic_info_tab(self):
        """ایجاد تب اطلاعات پایه"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(15)
        
        # گروه‌بندی اطلاعات شخصی
        personal_group = QGroupBox("اطلاعات شخصی")
        personal_layout = QFormLayout()
        personal_layout.setSpacing(12)
        personal_layout.setLabelAlignment(Qt.AlignRight)
        
        # نوع شخص
        self.person_type_combo = QComboBox()
        self.person_type_combo.addItems([
            "مشتری", "تامین کننده", "تعمیرکار بیرونی", 
            "شریک", "کارمند"
        ])
        personal_layout.addRow("نوع شخص:", self.person_type_combo)
        
        # نام و نام خانوادگی
        name_layout = QHBoxLayout()
        name_layout.setSpacing(10)
        
        self.first_name_input = QLineEdit()
        self.first_name_input.setPlaceholderText("نام")
        self.first_name_input.setProperty("required", True)
        self.first_name_input.setAlignment(Qt.AlignRight)
        
        self.last_name_input = QLineEdit()
        self.last_name_input.setPlaceholderText("نام خانوادگی")
        self.last_name_input.setProperty("required", True)
        self.last_name_input.setAlignment(Qt.AlignRight)
        
        name_layout.addWidget(self.last_name_input)
        name_layout.addWidget(self.first_name_input)
        
        name_label = QLabel("نام و نام خانوادگی:")
        name_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        personal_layout.addRow(name_label, name_layout)
        
        # کد ملی
        self.national_id_input = QLineEdit()
        self.national_id_input.setPlaceholderText("کد ملی ۱۰ رقمی")
        self.national_id_input.setMaxLength(10)
        personal_layout.addRow("کد ملی:", self.national_id_input)
        
        # کد اقتصادی
        self.economic_code_input = QLineEdit()
        self.economic_code_input.setPlaceholderText("کد اقتصادی")
        personal_layout.addRow("کد اقتصادی:", self.economic_code_input)
        
        # تاریخ ثبت
        self.registration_date_input = JalaliDateInput()
        personal_layout.addRow("تاریخ ثبت:", self.registration_date_input)
        
        # وضعیت
        self.active_checkbox = QCheckBox("فعال")
        self.active_checkbox.setChecked(True)
        personal_layout.addRow("وضعیت:", self.active_checkbox)
        
        personal_group.setLayout(personal_layout)
        layout.addWidget(personal_group)
        
        # توضیحات
        description_group = QGroupBox("توضیحات")
        description_layout = QVBoxLayout()
        
        self.description_input = QTextEdit()
        self.description_input.setMaximumHeight(120)
        self.description_input.setPlaceholderText("توضیحات اضافی درباره این شخص...")
        
        description_layout.addWidget(self.description_input)
        description_group.setLayout(description_layout)
        layout.addWidget(description_group)
        
        layout.addStretch()
        return widget
    
    def create_contact_info_tab(self):
        """ایجاد تب اطلاعات تماس"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(15)
        
        # اطلاعات تماس
        contact_group = QGroupBox("اطلاعات تماس")
        contact_layout = QFormLayout()
        contact_layout.setSpacing(12)
        contact_layout.setLabelAlignment(Qt.AlignRight)
        
        # موبایل
        self.mobile_input = QLineEdit()
        self.mobile_input.setPlaceholderText("09xxxxxxxxx")
        self.mobile_input.setMaxLength(11)
        contact_layout.addRow("موبایل:", self.mobile_input)
        
        # تلفن
        self.phone_input = QLineEdit()
        self.phone_input.setPlaceholderText("021-xxxxxxxx")
        contact_layout.addRow("تلفن:", self.phone_input)
        
        # ایمیل
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("example@domain.com")
        contact_layout.addRow("ایمیل:", self.email_input)
        
        contact_group.setLayout(contact_layout)
        layout.addWidget(contact_group)
        
        # آدرس
        address_group = QGroupBox("آدرس")
        address_layout = QVBoxLayout()
        
        self.address_input = QTextEdit()
        self.address_input.setMaximumHeight(150)
        self.address_input.setPlaceholderText(
            "استان، شهر، خیابان، پلاک، واحد\n\n"
            "مثال: تهران، خیابان آزادی، کوچه گلستان، پلاک ۱۲، واحد ۳"
        )
        
        address_layout.addWidget(self.address_input)
        address_group.setLayout(address_layout)
        layout.addWidget(address_group)
        
        layout.addStretch()
        return widget
    
    def create_financial_info_tab(self):
        """ایجاد تب اطلاعات مالی"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(15)
        
        # اطلاعات بانکی
        bank_group = QGroupBox("اطلاعات بانکی")
        bank_layout = QFormLayout()
        bank_layout.setSpacing(12)
        bank_layout.setLabelAlignment(Qt.AlignRight)
        
        # حساب بانکی
        self.bank_account_input = QLineEdit()
        self.bank_account_input.setPlaceholderText("شماره حساب بانکی")
        bank_layout.addRow("شماره حساب:", self.bank_account_input)
        
        # نام بانک
        self.bank_name_input = QLineEdit()
        self.bank_name_input.setPlaceholderText("نام بانک")
        bank_layout.addRow("نام بانک:", self.bank_name_input)
        
        # شماره کارت
        self.card_number_input = QLineEdit()
        self.card_number_input.setPlaceholderText("۶۲۱۹-۸۶۱۰-xxxx-xxxx")
        self.card_number_input.setMaxLength(19)
        bank_layout.addRow("شماره کارت:", self.card_number_input)
        
        # شبا
        self.sheba_input = QLineEdit()
        self.sheba_input.setPlaceholderText("IRxxxxxxxxxxxxxxxxxxxxxxxxxxxx")
        self.sheba_input.setMaxLength(26)
        bank_layout.addRow("شماره شبا:", self.sheba_input)
        
        bank_group.setLayout(bank_layout)
        layout.addWidget(bank_group)
        
        # یادداشت مالی
        notes_group = QGroupBox("یادداشت‌های مالی")
        notes_layout = QVBoxLayout()
        
        self.financial_notes_input = QTextEdit()
        self.financial_notes_input.setMaximumHeight(120)
        self.financial_notes_input.setPlaceholderText(
            "یادداشت‌های مالی مربوط به این شخص...\n"
            "مثال: اعتبار خرید، سوابق پرداخت، تخفیفات خاص"
        )
        
        notes_layout.addWidget(self.financial_notes_input)
        notes_group.setLayout(notes_layout)
        layout.addWidget(notes_group)
        
        layout.addStretch()
        return widget
    
    def create_history_tab(self):
        """ایجاد تب تاریخچه"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(15)
        
        # جدول تاریخچه پذیرش‌ها
        receptions_group = QGroupBox("تاریخچه پذیرش‌ها")
        receptions_layout = QVBoxLayout()
        
        self.receptions_history_table = QTableWidget()
        self.receptions_history_table.setColumnCount(6)
        self.receptions_history_table.setHorizontalHeaderLabels([
            "شماره پذیرش", "دستگاه", "تاریخ", "هزینه", 
            "وضعیت", "توضیحات"
        ])
        
        # تنظیم سایز ستون‌ها
        header = self.receptions_history_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # شماره پذیرش
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)  # دستگاه
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)  # تاریخ
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)  # هزینه
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)  # وضعیت
        header.setSectionResizeMode(5, QHeaderView.Stretch)          # توضیحات
        
        receptions_layout.addWidget(self.receptions_history_table)
        receptions_group.setLayout(receptions_layout)
        layout.addWidget(receptions_group)
        
        # جدول تاریخچه تراکنش‌ها
        transactions_group = QGroupBox("تاریخچه تراکنش‌های مالی")
        transactions_layout = QVBoxLayout()
        
        self.transactions_history_table = QTableWidget()
        self.transactions_history_table.setColumnCount(5)
        self.transactions_history_table.setHorizontalHeaderLabels([
            "تاریخ", "نوع", "مبلغ", "شرح", "وضعیت"
        ])
        
        # تنظیم سایز ستون‌ها
        header = self.transactions_history_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # تاریخ
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)  # نوع
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)  # مبلغ
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)  # شرح
        header.setSectionResizeMode(4, QHeaderView.Stretch)          # وضعیت
        
        transactions_layout.addWidget(self.transactions_history_table)
        transactions_group.setLayout(transactions_layout)
        layout.addWidget(transactions_group)
        
        layout.addStretch()
        return widget
    
    def create_actions_frame(self):
        """ایجاد فریم دکمه‌های اقدام"""
        frame = QFrame()
        frame.setStyleSheet(f"""
            QFrame {{
                background-color: {self.colors['tab_inactive']};
                border-radius: 8px;
                border: 1px solid {self.colors['border']};
                padding: 15px;
            }}
        """)
        
        layout = QHBoxLayout()
        layout.setSpacing(15)
        
        # دکمه ذخیره
        self.save_button = QPushButton("💾 ذخیره")
        self.save_button.setObjectName("saveButton")
        self.save_button.setToolTip("ذخیره اطلاعات شخص (Ctrl+S)")
        self.save_button.clicked.connect(self.save_person)
        layout.addWidget(self.save_button)
        
        # دکمه حذف (فقط در حالت ویرایش)
        if self.person_id:
            self.delete_button = QPushButton("🗑️ حذف")
            self.delete_button.setObjectName("deleteButton")
            self.delete_button.setToolTip("حذف شخص از سیستم")
            self.delete_button.clicked.connect(self.delete_person)
            layout.addWidget(self.delete_button)
        
        layout.addStretch()
        
        # دکمه انصراف
        self.cancel_button = QPushButton("❌ انصراف")
        self.cancel_button.setObjectName("cancelButton")
        self.cancel_button.setToolTip("بستن فرم (Esc)")
        self.cancel_button.clicked.connect(self.close_form)
        layout.addWidget(self.cancel_button)
        
        frame.setLayout(layout)
        return frame
    
    def setup_connections(self):
        """تنظیم اتصالات سیگنال‌ها"""
        # اتصال اعتبارسنجی هنگام تغییر فیلدها
        self.first_name_input.textChanged.connect(self.validate_field)
        self.last_name_input.textChanged.connect(self.validate_field)
        self.mobile_input.textChanged.connect(self.validate_field)
        self.national_id_input.textChanged.connect(self.validate_field)
        
        # کلیدهای میانبر
        self.save_button.setShortcut("Ctrl+S")
        self.cancel_button.setShortcut("Escape")
    
    def validate_field(self):
        """اعتبارسنجی فیلد هنگام تغییر"""
        sender = self.sender()
        
        if sender == self.first_name_input or sender == self.last_name_input:
            text = sender.text().strip()
            if text:
                sender.setStyleSheet(f"border: 2px solid {self.colors['success']};")
            else:
                sender.setStyleSheet(f"border: 2px solid {self.colors['danger']};")
                
        elif sender == self.mobile_input:
            text = sender.text().strip()
            if text and text.startswith('09') and len(text) == 11:
                sender.setStyleSheet(f"border: 2px solid {self.colors['success']};")
            elif text:
                sender.setStyleSheet(f"border: 2px solid {self.colors['warning']};")
            else:
                sender.setStyleSheet(f"border: 1px solid {self.colors['border']};")
                
        elif sender == self.national_id_input:
            text = sender.text().strip()
            if text and len(text) == 10 and text.isdigit():
                sender.setStyleSheet(f"border: 2px solid {self.colors['success']};")
            elif text:
                sender.setStyleSheet(f"border: 2px solid {self.colors['warning']};")
            else:
                sender.setStyleSheet(f"border: 1px solid {self.colors['border']};")
    
    def load_person_data(self):
        """بارگذاری اطلاعات شخص از دیتابیس"""
        if self.person_id:
            try:
                self.current_person = self.data_manager.person.get_person_by_id(self.person_id)
                if self.current_person:
                    self.fill_form_data()
                    self.load_history_data()
                else:
                    QMessageBox.warning(self, "خطا", "شخص مورد نظر یافت نشد.")
                    self.form_closed.emit()
                    self.close()
            except Exception as e:
                QMessageBox.critical(self, "خطا", f"خطا در بارگذاری اطلاعات:\n{str(e)}")
                self.form_closed.emit()
                self.close()
    
    def fill_form_data(self):
        """پر کردن فرم با داده‌های شخص"""
        if not self.current_person:
            return
        
        # اطلاعات پایه
        self.person_type_combo.setCurrentText(self.current_person.get('person_type', 'مشتری'))
        self.first_name_input.setText(self.current_person.get('first_name', ''))
        self.last_name_input.setText(self.current_person.get('last_name', ''))
        self.national_id_input.setText(self.current_person.get('national_id', ''))
        self.economic_code_input.setText(self.current_person.get('economic_code', ''))
        
        # تاریخ ثبت
        reg_date_str = self.current_person.get('registration_date', '')
        if reg_date_str:
            self.registration_date_input.set_date(reg_date_str)
        else:
            self.registration_date_input.set_date_to_today()
        
        # وضعیت
        is_active = self.current_person.get('is_active', 1)
        self.active_checkbox.setChecked(bool(is_active))
        
        # توضیحات
        self.description_input.setText(self.current_person.get('description', ''))
        
        # اطلاعات تماس
        self.mobile_input.setText(self.current_person.get('mobile', ''))
        self.phone_input.setText(self.current_person.get('phone', ''))
        self.email_input.setText(self.current_person.get('email', ''))
        self.address_input.setText(self.current_person.get('address', ''))
        
        # اطلاعات مالی (اگر در دیتابیس وجود داشته باشند)
        self.bank_account_input.setText(self.current_person.get('bank_account', ''))
        self.bank_name_input.setText(self.current_person.get('bank_name', ''))
        self.card_number_input.setText(self.current_person.get('card_number', ''))
        self.sheba_input.setText(self.current_person.get('sheba_number', ''))
        self.financial_notes_input.setText(self.current_person.get('financial_notes', ''))
        
        # اعتبارسنجی فیلدها
        self.validate_field()
    
    def load_history_data(self):
        """بارگذاری تاریخچه شخص"""
        if not self.person_id:
            return
        
        try:
            # بارگذاری پذیرش‌ها
            receptions = self.data_manager.reception.get_all_receptions()
            person_receptions = [r for r in receptions if r.get('customer_id') == self.person_id]
            
            self.receptions_history_table.setRowCount(len(person_receptions))
            for row, reception in enumerate(person_receptions):
                self.receptions_history_table.setItem(row, 0, 
                    QTableWidgetItem(str(reception.get('reception_number', ''))))
                self.receptions_history_table.setItem(row, 1, 
                    QTableWidgetItem(f"{reception.get('device_type', '')} {reception.get('brand', '')}"))
                self.receptions_history_table.setItem(row, 2, 
                    QTableWidgetItem(reception.get('reception_date', '')))
                self.receptions_history_table.setItem(row, 3, 
                    QTableWidgetItem(f"{reception.get('estimated_cost', 0):,} تومان"))
                
                status_item = QTableWidgetItem(reception.get('status', ''))
                status = reception.get('status', '')
                if status == 'تعمیر شده':
                    status_item.setForeground(QColor(self.colors['success']))
                elif status == 'در حال تعمیر':
                    status_item.setForeground(QColor(self.colors['primary']))
                elif status == 'در انتظار':
                    status_item.setForeground(QColor(self.colors['warning']))
                elif status == 'تحویل داده شده':
                    status_item.setForeground(QColor('#9b59b6'))
                
                self.receptions_history_table.setItem(row, 4, status_item)
                self.receptions_history_table.setItem(row, 5, 
                    QTableWidgetItem(reception.get('problem_description', '')))
            
            # تنظیم ارتفاع سطرها
            for row in range(self.receptions_history_table.rowCount()):
                self.receptions_history_table.setRowHeight(row, 40)
                
        except Exception as e:
            print(f"خطا در بارگذاری تاریخچه پذیرش‌ها: {e}")
            self.receptions_history_table.setRowCount(0)
    
    def validate_form(self):
        """اعتبارسنجی کامل فرم"""
        errors = []
        
        # اعتبارسنجی نام
        first_name = self.first_name_input.text().strip()
        last_name = self.last_name_input.text().strip()
        if not first_name:
            errors.append("• نام الزامی است.")
        if not last_name:
            errors.append("• نام خانوادگی الزامی است.")
        
        # اعتبارسنجی موبایل
        mobile = self.mobile_input.text().strip()
        if mobile and (not mobile.startswith('09') or len(mobile) != 11):
            errors.append("• شماره موبایل باید ۱۱ رقمی و با ۰۹ شروع شود.")
        
        # اعتبارسنجی کد ملی
        national_id = self.national_id_input.text().strip()
        if national_id and (len(national_id) != 10 or not national_id.isdigit()):
            errors.append("• کد ملی باید ۱۰ رقمی و عددی باشد.")
        
        return errors
    
    def save_person(self):
        """ذخیره اطلاعات شخص در دیتابیس"""
        # اعتبارسنجی
        errors = self.validate_form()
        if errors:
            QMessageBox.warning(
                self, 
                "خطا در اعتبارسنجی", 
                "لطفاً خطاهای زیر را اصلاح کنید:\n\n" + "\n".join(errors)
            )
            return
        
        try:
            # جمع‌آوری داده‌ها
            person_data = {
                'person_type': self.person_type_combo.currentText(),
                'first_name': self.first_name_input.text().strip(),
                'last_name': self.last_name_input.text().strip(),
                'mobile': self.mobile_input.text().strip() or None,
                'phone': self.phone_input.text().strip() or None,
                'address': self.address_input.toPlainText().strip() or None,
                'national_id': self.national_id_input.text().strip() or None,
                'economic_code': self.economic_code_input.text().strip() or None,
                'registration_date': self.registration_date_input.get_date_string(),  # تاریخ شمسی
                'is_active': 1 if self.active_checkbox.isChecked() else 0,
                'description': self.description_input.toPlainText().strip() or None,
            }
            
            # ذخیره یا به‌روزرسانی
            if self.person_id:
                success = self.data_manager.person.update_person(self.person_id, person_data)
                message = f"اطلاعات شخص '{person_data['first_name']} {person_data['last_name']}' ویرایش شد."
            else:
                success = self.data_manager.person.add_person(person_data)
                message = f"شخص جدید '{person_data['first_name']} {person_data['last_name']}' ثبت شد."
            
            if success:
                QMessageBox.information(self, "موفقیت", message)
                self.person_saved.emit({'id': self.person_id, 'action': 'update' if self.person_id else 'create'})
                self.form_closed.emit()
                self.close()
            else:
                QMessageBox.critical(self, "خطا", "خطا در ذخیره اطلاعات.")
                
        except Exception as e:
            QMessageBox.critical(self, "خطا", f"خطا در ذخیره اطلاعات:\n{str(e)}")
    
    def delete_person(self):
        """حذف شخص"""
        if not self.person_id:
            return
        
        person_name = f"{self.first_name_input.text()} {self.last_name_input.text()}"
        
        reply = QMessageBox.question(
            self, 
            "تأیید حذف",
            f"آیا مطمئن هستید که می‌خواهید شخص زیر را حذف کنید؟\n\n"
            f"📛 نام: {person_name}\n"
            f"🔢 کد: {self.person_id}\n\n"
            f"⚠️  توجه: این عمل غیرقابل بازگشت است.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                success = self.data_manager.person.delete_person(self.person_id)
                if success:
                    QMessageBox.information(self, "موفقیت", f"شخص '{person_name}' با موفقیت حذف شد.")
                    self.person_deleted.emit(self.person_id)
                    self.form_closed.emit()
                    self.close()
                else:
                    QMessageBox.critical(self, "خطا", "خطا در حذف شخص.")
                
            except Exception as e:
                QMessageBox.critical(
                    self, 
                    "خطا", 
                    f"خطا در حذف شخص:\n\n{str(e)}"
                )
    
    def clear_form(self):
        """پاک کردن فرم برای ثبت جدید"""
        self.person_id = None
        self.current_person = None
        
        # اطلاعات پایه
        self.person_type_combo.setCurrentIndex(0)
        self.first_name_input.clear()
        self.last_name_input.clear()
        self.national_id_input.clear()
        self.economic_code_input.clear()
        self.registration_date_input.set_date_to_today()
        self.active_checkbox.setChecked(True)
        self.description_input.clear()
        
        # اطلاعات تماس
        self.mobile_input.clear()
        self.phone_input.clear()
        self.email_input.clear()
        self.address_input.clear()
        
        # اطلاعات مالی
        self.bank_account_input.clear()
        self.bank_name_input.clear()
        self.card_number_input.clear()
        self.sheba_input.clear()
        self.financial_notes_input.clear()
        
        # تاریخچه
        self.receptions_history_table.setRowCount(0)
        self.transactions_history_table.setRowCount(0)
        
        # تغییر عنوان
        for i in range(self.tab_widget.count()):
            if self.tab_widget.tabText(i) == "📋 اطلاعات پایه":
                self.tab_widget.setTabText(i, "📋 اطلاعات پایه (جدید)")
                break
        
        # فوکوس روی فیلد نام
        self.first_name_input.setFocus()
    
    def view_person_receptions(self):
        """مشاهده پذیرش‌های شخص"""
        if not self.person_id:
            return
        
        QMessageBox.information(self, "اطلاعات", 
            f"مشاهده پذیرش‌های شخص کد {self.person_id}\n\n"
            f"این قابلیت در نسخه بعدی کامل می‌شود.")
        # TODO: اتصال به ماژول پذیرش
    
    def view_person_invoices(self):
        """مشاهده فاکتورهای شخص"""
        if not self.person_id:
            return
        
        QMessageBox.information(self, "اطلاعات", 
            f"مشاهده فاکتورهای شخص کد {self.person_id}\n\n"
            f"این قابلیت در نسخه بعدی کامل می‌شود.")
        # TODO: اتصال به ماژول حسابداری
    
    def close_form(self):
        """بستن فرم"""
        self.form_closed.emit()
        self.close()
    
    def closeEvent(self, event):
        """مدیریت رویداد بسته شدن پنجره"""
        self.form_closed.emit()
        event.accept()


# در انتهای فایل اضافه کنید
if __name__ == "__main__":
    """برای اجرای مستقل فرم (در صورت نیاز)"""
    print("⚠️  این فایل برای تست مستقیم نیست.")
    print("برای تست از فایل‌های تست جداگانه استفاده کنید:")
    print("1. test_person_form.py - تست کامل فرم")
    print("2. test_jalali_date.py - تست تاریخ شمسی")
    print("3. test_theme.py - تست تم تاریک")