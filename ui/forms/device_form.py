"""
فرم مدیریت دستگاه‌ها
بر اساس جدول Devices در دیتابیس
"""

from PySide6.QtWidgets import (
     QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,  
    QLabel, QPushButton, QLineEdit, QComboBox, QGridLayout,
    QTextEdit, QTableWidget,QTableWidgetItem, QTabWidget, 
    QFrame, QGroupBox, QMessageBox, QHeaderView, QSpinBox, 
    QCheckBox, QFormLayout, QScrollArea, QAbstractSpinBox ,QInputDialog
)
from PySide6.QtCore import Qt, Signal, QTimer
from PySide6.QtGui import QFont, QColor
import jdatetime
from datetime import datetime
import sys
import os

# افزودن مسیر پروژه به sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
sys.path.insert(0, project_root)

# ایمپورت ویجت تاریخ شمسی
from ui.widgets.jalali_date_input import JalaliDateInput


class DeviceForm(QWidget):
    """
    فرم مدیریت دستگاه‌ها
    بر اساس جدول Devices در دیتابیس
    """
    
    # سیگنال‌ها
    device_saved = Signal(dict)  # هنگامی که دستگاه ذخیره می‌شود
    form_closed = Signal()  # هنگامی که فرم بسته می‌شود
    
    def __init__(self, data_manager, device_id=None):
        super().__init__()
        self.data_manager = data_manager
        self.current_device_id = device_id

        self.brand = None
        self.device_type = None


        # لیست کش شده برای جستجو
        self.devices_cache = []
        
        self.init_ui()
        self.setup_connections()
        self.load_initial_data()
        
        # اگر device_id داده شده، دستگاه را بارگذاری کن
        if self.current_device_id:
            QTimer.singleShot(100, self.load_device_data)
    
    def init_ui(self):
        """راه‌اندازی رابط کاربری"""
        self.setWindowTitle("📱 مدیریت دستگاه‌ها - سیستم مدیریت تعمیرگاه")
        self.setMinimumSize(1000, 700)
        
        # 🔴 **راست‌چین کردن کل فرم**
        self.setLayoutDirection(Qt.RightToLeft)
        
        # تنظیم استایل با تم تاریک
        self.setStyleSheet(self.get_style_sheet())
        
        # تنظیم فونت فارسی
        self.set_font()
        
        # ایجاد لایه اصلی
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)
        
        # نوار عنوان
        title_frame = QFrame()
        title_frame.setStyleSheet("""
            QFrame {
                background-color: #2c3e50;
                border-radius: 8px;
                padding: 10px;
            }
        """)
        
        title_layout = QHBoxLayout()
        title_label = QLabel("📱 مدیریت دستگاه‌ها")
        title_label.setStyleSheet("""
            QLabel {
                font-size: 18px;
                font-weight: bold;
                color: white;
            }
        """)
        title_layout.addWidget(title_label)
        title_layout.addStretch()
        
        # وضعیت
        self.device_status_label = QLabel("دستگاه جدید")
        self.device_status_label.setStyleSheet("""
            QLabel {
                font-size: 14px;
                font-weight: bold;
                color: #f39c12;
                background-color: #34495e;
                padding: 5px 10px;
                border-radius: 5px;
            }
        """)
        title_layout.addWidget(self.device_status_label)
        
        title_frame.setLayout(title_layout)
        main_layout.addWidget(title_frame)
        
        # ایجاد ویجت تب‌ها
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #333;
                background-color: #1e1e1e;
                border-radius: 5px;
            }
            QTabBar::tab {
                background-color: #2c2c2c;
                color: #bbb;
                padding: 8px 15px;
                margin-right: 2px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                font-size: 13px;
            }
            QTabBar::tab:selected {
                background-color: #3498db;
                color: white;
                font-weight: bold;
            }
            QTabBar::tab:hover:!selected {
                background-color: #3c3c3c;
            }
        """)
        
        self.brand = QComboBox()
        self.device_type = QComboBox()

        
        # ایجاد تب‌ها
        self.create_search_tab()    # تب 1: جستجو
        self.create_edit_tab()      # تب 2: ویرایش
        
        main_layout.addWidget(self.tabs)
        
        # نوار دکمه‌های عملیاتی
        button_frame = QFrame()
        button_layout = QHBoxLayout()
        
        # دکمه‌های اصلی
        self.btn_new = QPushButton("🆕 جدید")
        self.btn_new.setStyleSheet(self.get_button_style("#27ae60"))
        self.btn_new.clicked.connect(self.new_device)
        
        self.btn_save = QPushButton("💾 ذخیره")
        self.btn_save.setStyleSheet(self.get_button_style("#3498db"))
        self.btn_save.clicked.connect(self.save_device)
        
        self.btn_delete = QPushButton("🗑️ حذف")
        self.btn_delete.setStyleSheet(self.get_button_style("#e74c3c"))
        self.btn_delete.clicked.connect(self.delete_device)
        self.btn_delete.setEnabled(False)  # ابتدا غیرفعال
        
        self.btn_cancel = QPushButton("❌ انصراف")
        self.btn_cancel.setStyleSheet(self.get_button_style("#95a5a6"))
        self.btn_cancel.clicked.connect(self.close_form)
        
        button_layout.addWidget(self.btn_new)
        button_layout.addWidget(self.btn_save)
        button_layout.addWidget(self.btn_delete)
        button_layout.addStretch()
        button_layout.addWidget(self.btn_cancel)
        
        button_frame.setLayout(button_layout)
        main_layout.addWidget(button_frame)
        
        self.setLayout(main_layout)
        
        self.check_widgets()
        self.debug_functions()


        # تایمر برای جستجوی زنده
        self.search_timer = QTimer()
        self.search_timer.setSingleShot(True)
        self.search_timer.timeout.connect(self.perform_search)
    
    def get_style_sheet(self):
        """استایل‌شیت فرم با تم تاریک"""
        return """
        /* استایل کلی فرم */
        QWidget {
            font-family: 'B Nazanin', Tahoma;
            background-color: #000000;
            color: white;
        }
        
        /* GroupBox */
        QGroupBox {
            font-size: 14px;
            font-weight: bold;
            color: #3498db;
            border: 2px solid #3498db;
            border-radius: 8px;
            margin-top: 10px;
            padding-top: 15px;
            background-color: #1e1e1e;
        }
        
        QGroupBox::title {
            subcontrol-origin: margin;
            subcontrol-position: top right;
            padding: 0 10px;
            background-color: #3498db;
            color: white;
            border-radius: 4px;
        }
        
        /* فیلدهای ورودی */
        QLineEdit, QComboBox, QTextEdit, QSpinBox {
            background-color: #2c2c2c;
            color: white;
            border: 1px solid #444;
            border-radius: 4px;
            padding: 6px;
            font-size: 13px;
            selection-background-color: #3498db;
        }
        
        QLineEdit:focus, QComboBox:focus, QTextEdit:focus, QSpinBox:focus {
            border: 2px solid #3498db;
        }
        
        QLineEdit::placeholder, QTextEdit::placeholder {
            color: #666;
        }
        
        /* CheckBox */
        QCheckBox {
            color: white;
            font-size: 13px;
        }
        
        QCheckBox::indicator {
            width: 18px;
            height: 18px;
        }
        
        QCheckBox::indicator:checked {
            background-color: #27ae60;
        }
        
        /* دکمه‌ها */
        QPushButton {
            padding: 8px 15px;
            border-radius: 4px;
            font-weight: bold;
            border: none;
            color: white;
            font-size: 13px;
        }
        
        /* لیست‌ها */
        QListWidget {
            background-color: #2c2c2c;
            border: 1px solid #444;
            border-radius: 4px;
            color: white;
            alternate-background-color: #3c3c3c;
        }
        
        QListWidget::item {
            padding: 8px;
            border-bottom: 1px solid #444;
        }
        
        QListWidget::item:selected {
            background-color: #3498db;
            color: white;
        }
        
        /* جداول */
        QTableWidget {
            background-color: #1e1e1e;
            alternate-background-color: #2c2c2c;
            selection-background-color: #3498db;
            selection-color: white;
            gridline-color: #333;
            color: white;
            font-size: 12px;
        }
        
        QTableWidget::item {
            padding: 5px;
        }
        
        QHeaderView::section {
            background-color: #2c3e50;
            color: white;
            padding: 8px;
            border: none;
            font-weight: bold;
            font-size: 12px;
        }
        
        /* برچسب‌ها */
        QLabel {
            color: white;
            font-size: 13px;
        }
        
        QLabel.required {
            color: #e74c3c;
        }
        
        /* اسکرول بار */
        QScrollBar:vertical {
            background-color: #2c2c2c;
            width: 12px;
            border-radius: 6px;
        }
        
        QScrollBar::handle:vertical {
            background-color: #444;
            border-radius: 6px;
            min-height: 20px;
        }
        
        QScrollBar::handle:vertical:hover {
            background-color: #555;
        }
        """
    
    def get_button_style(self, color):
        """استایل دکمه با رنگ مشخص"""
        return f"""
        QPushButton {{
            background-color: {color};
            color: white;
        }}
        QPushButton:hover {{
            background-color: {self.darken_color(color)};
        }}
        QPushButton:pressed {{
            background-color: {self.darken_color(color, 60)};
        }}
        QPushButton:disabled {{
            background-color: #7f8c8d;
            color: #bdc3c7;
        }}
        """
    
    def darken_color(self, color, amount=30):
        """تیره کردن رنگ"""
        color = color.lstrip('#')
        r, g, b = tuple(int(color[i:i+2], 16) for i in (0, 2, 4))
        
        r = max(0, r - amount)
        g = max(0, g - amount)
        b = max(0, b - amount)
        
        return f'#{r:02x}{g:02x}{b:02x}'
    
    def set_font(self):
        """تنظیم فونت فارسی"""
        font = QFont()
        font.setFamily("B Nazanin")
        font.setPointSize(10)
        self.setFont(font)
    
    def check_buttons_visibility(self):
        """بررسی نمایش دکمه‌ها"""
        # این کد را در انتهای create_edit_tab() اضافه کنید
        print("=== بررسی دکمه‌ها ===")
        
        # پیدا کردن دکمه‌ها در Layout
        for i in range(self.layout().count()):
            widget = self.layout().itemAt(i).widget()
            if widget and isinstance(widget, QPushButton):
                print(f"دکمه یافت شد: {widget.text()} - قابل مشاهده: {widget.isVisible()}")
        
        # یا این کد را بعد از ایجاد فرم در main_window.py امتحان کنید

    # ========== تب 1: جستجو ==========
    def create_search_tab(self):
        """ایجاد تب جستجوی دستگاه‌ها"""
        tab = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(15)
        
        # گروه جستجوی سریع
        search_group = QGroupBox("🔍 جستجوی دستگاه‌ها")
        search_layout = QGridLayout()
        
        # فیلدهای جستجو
        search_layout.addWidget(QLabel("برند:"), 0, 0)
        self.search_brand = QLineEdit()
        self.search_brand.setPlaceholderText("نام برند")
        search_layout.addWidget(self.search_brand, 0, 1)
        
        search_layout.addWidget(QLabel("مدل:"), 0, 2)
        self.search_model = QLineEdit()
        self.search_model.setPlaceholderText("مدل دستگاه")
        search_layout.addWidget(self.search_model, 0, 3)
        
        search_layout.addWidget(QLabel("شماره سریال:"), 1, 0)
        self.search_serial = QLineEdit()
        self.search_serial.setPlaceholderText("شماره سریال")
        search_layout.addWidget(self.search_serial, 1, 1)
        
        search_layout.addWidget(QLabel("نوع دستگاه:"), 1, 2)
        self.search_type = QComboBox()
        self.search_type.addItems(["همه", "یخچال", "فریزر", "ماشین لباسشویی", "ماشین ظرفشویی", 
                                   "اجاق گاز", "هود", "کولر گازی", "پکیج", "آبگرمکن", "سایر"])
        search_layout.addWidget(self.search_type, 1, 3)
        
        # دکمه‌های جستجو
        btn_search = QPushButton("🔍 جستجو")
        btn_search.setStyleSheet(self.get_button_style("#3498db"))
        btn_search.clicked.connect(self.perform_search)
        
        btn_clear = QPushButton("🧹 پاک کردن")
        btn_clear.setStyleSheet(self.get_button_style("#7f8c8d"))
        btn_clear.clicked.connect(self.clear_search)
        
        search_layout.addWidget(btn_search, 2, 0, 1, 2)
        search_layout.addWidget(btn_clear, 2, 2, 1, 2)
        
        search_group.setLayout(search_layout)
        layout.addWidget(search_group)
        
        # جدول نتایج جستجو
        self.search_table = QTableWidget()
        self.search_table.setColumnCount(8)
        self.search_table.setHorizontalHeaderLabels([
            "انتخاب", "نوع", "برند", "مدل", "سریال", 
            "سال تولید", "تاریخ خرید", "عملیات"
        ])
        self.search_table.horizontalHeader().setStretchLastSection(True)
        self.search_table.setAlternatingRowColors(True)
        
        # تنظیم عرض ستون‌ها
        self.search_table.setColumnWidth(0, 60)   # انتخاب
        self.search_table.setColumnWidth(1, 100)  # نوع
        self.search_table.setColumnWidth(2, 120)  # برند
        self.search_table.setColumnWidth(3, 120)  # مدل
        self.search_table.setColumnWidth(4, 150)  # سریال
        self.search_table.setColumnWidth(5, 80)   # سال تولید
        self.search_table.setColumnWidth(6, 100)  # تاریخ خرید
        
        layout.addWidget(self.search_table)
        
        tab.setLayout(layout)
        self.tabs.addTab(tab, "🔍 جستجو")
        
        # اتصال جستجوی زنده
        self.search_brand.textChanged.connect(self.start_search_timer)
        self.search_model.textChanged.connect(self.start_search_timer)
        self.search_serial.textChanged.connect(self.start_search_timer)
    
    def start_search_timer(self):
        """شروع تایمر برای جستجوی زنده"""
        self.search_timer.start(500)  # 500ms delay
    
    # ========== تب 2: ویرایش ==========
    def create_edit_tab(self):
        """ایجاد تب ویرایش دستگاه"""
        tab = QWidget()
        
        # اسکرول برای نمایش تمام محتوا
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
        """)
        
        content_widget = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(15)
        
        # گروه اطلاعات اصلی
        info_group = QGroupBox("📝 اطلاعات دستگاه")
        info_layout = QGridLayout()
        
        # ========== نوع دستگاه ==========
        info_layout.addWidget(QLabel("* نوع دستگاه:"), 0, 0)

        # ۱. ایجاد ویجت نوع دستگاه
        if not hasattr(self, 'device_type') or self.device_type is None:
            self.device_type = QComboBox()

        self.device_type.setEditable(True)
        self.device_type.setInsertPolicy(QComboBox.InsertPolicy.InsertAtTop)

        # بارگذاری از دیتابیس
        try:
            device_types = self.data_manager.get_lookup_list('device_type')
            self.device_type.addItems([''] + device_types)
        except:
            self.device_type.addItems(['', 'یخچال', 'ماشین لباسشویی', 'سایر'])

        # ۲. ایجاد Layout افقی برای ComboBox + دکمه
        device_type_hbox = QHBoxLayout()
        device_type_hbox.addWidget(self.device_type)  # اول ComboBox

        # ۳. ایجاد دکمه +
        btn_add_type = QPushButton("+")
        btn_add_type.setFixedSize(30, 30)  # اندازه ثابت
        btn_add_type.setToolTip("افزودن نوع جدید")
        btn_add_type.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                font-weight: bold;
                font-size: 16px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #219653;
            }
        """)
        btn_add_type.clicked.connect(lambda: self.add_new_lookup_value('device_type', self.device_type))

        # ۴. اضافه کردن دکمه به Layout افقی
        device_type_hbox.addWidget(btn_add_type)

        # ۵. اضافه کردن کل Layout به Grid (نه فقط ComboBox)
        info_layout.addLayout(device_type_hbox, 0, 1)
        



        # ========== برند دستگاه ==========
        info_layout.addWidget(QLabel("* برند:"), 0, 2)

        # ۱. ایجاد ویجت برند
        if not hasattr(self, 'brand') or self.brand is None:
            self.brand = QComboBox()

        self.brand.setEditable(True)
        self.brand.setInsertPolicy(QComboBox.InsertPolicy.InsertAtTop)

        # بارگذاری از دیتابیس
        try:
            brands = self.data_manager.get_lookup_list('device_brand')
            self.brand.addItems([''] + brands)
        except:
            self.brand.addItems(['', 'ال جی', 'سامسونگ', 'سایر'])

        # ۲. ایجاد Layout افقی برای ComboBox + دکمه
        brand_hbox = QHBoxLayout()
        brand_hbox.addWidget(self.brand)  # اول ComboBox

        # ۳. ایجاد دکمه +
        btn_add_brand = QPushButton("+")
        btn_add_brand.setFixedSize(30, 30)  # اندازه ثابت
        btn_add_brand.setToolTip("افزودن برند جدید")
        btn_add_brand.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                font-weight: bold;
                font-size: 16px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        btn_add_brand.clicked.connect(lambda: self.add_new_lookup_value('device_brand', self.brand))

        # ۴. اضافه کردن دکمه به Layout افقی
        brand_hbox.addWidget(btn_add_brand)

        # ۵. اضافه کردن کل Layout به Grid (نه فقط ComboBox)
        info_layout.addLayout(brand_hbox, 0, 3)



        # ========== مدل دستگاه ==========
        info_layout.addWidget(QLabel("* مدل:"), 1, 0)
        self.model = QLineEdit()  # این باید قبلاً تعریف شده باشد
        self.model.setPlaceholderText("مدل دقیق دستگاه")
        info_layout.addWidget(self.model, 1, 1)
        


        # شماره سریال
        info_layout.addWidget(QLabel("شماره سریال:"), 1, 2)
        self.serial_number = QLineEdit()
        self.serial_number.setPlaceholderText("در صورت موجود بودن")
        info_layout.addWidget(self.serial_number, 1, 3)
        
        # سال تولید
        info_layout.addWidget(QLabel("سال تولید:"), 2, 0)
        self.production_year = QSpinBox()
        self.production_year.setRange(1990, 2030)
        self.production_year.setValue(2024)
        self.production_year.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.NoButtons)
        info_layout.addWidget(self.production_year, 2, 1)
        
        # تاریخ خرید
        info_layout.addWidget(QLabel("تاریخ خرید:"), 2, 2)
        self.purchase_date = JalaliDateInput()
        info_layout.addWidget(self.purchase_date, 2, 3)
        
        info_group.setLayout(info_layout)
        layout.addWidget(info_group)
        
        # گروه گارانتی
        warranty_group = QGroupBox("📋 اطلاعات گارانتی")
        warranty_layout = QGridLayout()
        
        # وضعیت گارانتی
        warranty_layout.addWidget(QLabel("وضعیت گارانتی:"), 0, 0)
        self.warranty_status = QCheckBox("دارای گارانتی")
        self.warranty_status.stateChanged.connect(self.on_warranty_status_changed)
        warranty_layout.addWidget(self.warranty_status, 0, 1)
        
        # تاریخ پایان گارانتی
        warranty_layout.addWidget(QLabel("تاریخ پایان گارانتی:"), 1, 0)
        self.warranty_end_date = JalaliDateInput()
        self.warranty_end_date.setEnabled(False)  # ابتدا غیرفعال
        warranty_layout.addWidget(self.warranty_end_date, 1, 1)
        
        warranty_group.setLayout(warranty_layout)
        layout.addWidget(warranty_group)
        
        # گروه توضیحات
        desc_group = QGroupBox("📝 توضیحات")
        desc_layout = QVBoxLayout()
        
        self.description = QTextEdit()
        self.description.setPlaceholderText("توضیحات اضافی درباره دستگاه...")
        self.description.setMaximumHeight(120)
        desc_layout.addWidget(self.description)
        
        desc_group.setLayout(desc_layout)
        layout.addWidget(desc_group)
        
        layout.addStretch()
        
        content_widget.setLayout(layout)
        scroll.setWidget(content_widget)
        
        tab_layout = QVBoxLayout()
        tab_layout.addWidget(scroll)
        tab.setLayout(tab_layout)
        
        self.tabs.addTab(tab, "✏️ ویرایش")


    def check_and_add_lookup_value(self, category, value, combo_box):
        """بررسی و اضافه کردن مقدار جدید به دیتابیس (برای ذخیره خودکار)"""
        if not value or not value.strip():
            return False
        
        value = value.strip()
        
        try:
            # ۱. بررسی وجود در دیتابیس
            existing_values = self.data_manager.get_lookup_list(category)
            
            if value not in existing_values:
                # ۲. اضافه کردن به دیتابیس
                success = self.data_manager.lookup.add_value(category, value)
                if success:
                    print(f"✅ مقدار جدید '{value}' به دسته '{category}' اضافه شد")
                    
                    # ۳. اضافه کردن به ComboBox
                    if value not in [combo_box.itemText(i) for i in range(combo_box.count())]:
                        combo_box.addItem(value)
                    
                    # ۴. انتخاب مقدار جدید
                    combo_box.setCurrentText(value)
                    return True
            return False
        except Exception as e:
            print(f"⚠️ خطا در اضافه کردن مقدار به {category}: {e}")
            return False
    

    def add_new_lookup_value(self, category, combo_box):
        """افزودن مقدار جدید از طریق دیالوگ (برای دکمه +)"""
        
        # نام فارسی برای نمایش به کاربر
        category_names = {
            'device_type': 'نوع دستگاه',
            'device_brand': 'برند دستگاه',
            'part_category': 'دسته‌بندی قطعه'
        }
        
        display_name = category_names.get(category, category)
        
        # دیالوگ دریافت مقدار جدید
        text, ok = QInputDialog.getText(
            self, 
            f"افزودن {display_name} جدید",
            f"نام {display_name} جدید را وارد کنید:\n(مثال: جاروبرقی، پنکه، تلویزیون)",
            QLineEdit.Normal,
            ""
        )
        
        if ok and text and text.strip():
            new_value = text.strip()
            
            # ۱. بررسی خالی نبودن
            if not new_value:
                QMessageBox.warning(self, "خطا", "نام نمی‌تواند خالی باشد.")
                return
            
            # ۲. بررسی تکراری نبودن (در دیتابیس)
            try:
                existing_values = self.data_manager.get_lookup_list(category)
                if new_value in existing_values:
                    QMessageBox.warning(self, "تکراری", 
                        f"«{new_value}» از قبل در لیست وجود دارد.")
                    return
            except Exception as e:
                print(f"خطا در بررسی تکراری: {e}")
            
            # ۳. ذخیره در دیتابیس
            try:
                success = self.data_manager.lookup.add_value(category, new_value)
                
                if success:
                    # ۴. اضافه به ComboBox
                    combo_box.addItem(new_value)
                    combo_box.setCurrentText(new_value)
                    
                    # ۵. پیام موفقیت
                    QMessageBox.information(self, "موفق", 
                        f"«{new_value}» با موفقیت به لیست {display_name}‌ها اضافه شد.")
                    
                    print(f"✅ {display_name} جدید اضافه شد: {new_value}")
                else:
                    QMessageBox.critical(self, "خطا", 
                        "خطا در ذخیره در دیتابیس.")
                    
            except Exception as e:
                QMessageBox.critical(self, "خطا", 
                    f"خطای سیستمی:\n{str(e)}")
                print(f"❌ خطا در ذخیره {category}: {e}")


    def on_warranty_status_changed(self, state):
        """هنگام تغییر وضعیت گارانتی"""
        is_checked = state == 2  # Qt.Checked = 2
        self.warranty_end_date.setEnabled(is_checked)
        if not is_checked:
            self.warranty_end_date.clear()
 
    # ========== متدهای کمکی ==========
    
    def check_widgets(self):
        """بررسی وجود تمام ویجت‌های ضروری"""
        required_widgets = ['brand', 'device_type', 'model']
        missing = []
        
        for widget_name in required_widgets:
            if not hasattr(self, widget_name):
                missing.append(widget_name)
            elif getattr(self, widget_name) is None:
                missing.append(f"{widget_name} (is None)")
        
        if missing:
            print(f"⚠️ ویجت‌های گمشده: {missing}")
            return False
        else:
            print("✅ تمام ویجت‌ها موجود هستند")
            return True

    # در init_ui بعد از ایجاد فرم، این را فراخوانی کنید:
    # self.check_widgets()

    def setup_connections(self):
        """تنظیم اتصالات"""
        pass  # بیشتر اتصالات در init_ui تنظیم شده‌اند
    
    def load_initial_data(self):
        """بارگذاری داده‌های اولیه"""
        # بارگذاری لیست دستگاه‌ها
        self.load_devices()
        
        # نمایش دستگاه‌های موجود
        self.perform_search()
    
    def load_devices(self):
        """بارگذاری لیست دستگاه‌ها از دیتابیس"""
        try:
            self.devices_cache = self.data_manager.device.get_all_devices()
        except Exception as e:
            print(f"خطا در بارگذاری دستگاه‌ها: {e}")
            self.devices_cache = []
    
    def perform_search(self):
        """انجام جستجوی دستگاه‌ها"""
        try:
            # دریافت فیلترهای جستجو
            filters = {}
            
            brand = self.search_brand.text().strip()
            if brand:
                filters['brand'] = brand
            
            model = self.search_model.text().strip()
            if model:
                filters['model'] = model
            
            serial = self.search_serial.text().strip()
            if serial:
                filters['serial_number'] = serial
            
            device_type = self.search_type.currentText()
            if device_type != "همه":
                filters['device_type'] = device_type
            
            # جستجو در کش
            filtered_devices = []
            for device in self.devices_cache:
                match = True
                
                if 'brand' in filters:
                    if filters['brand'].lower() not in device.get('brand', '').lower():
                        match = False
                
                if 'model' in filters and match:
                    if filters['model'].lower() not in device.get('model', '').lower():
                        match = False
                
                if 'serial_number' in filters and match:
                    if filters['serial_number'].lower() not in device.get('serial_number', '').lower():
                        match = False
                
                if 'device_type' in filters and match:
                    if filters['device_type'] != device.get('device_type', ''):
                        match = False
                
                if match:
                    filtered_devices.append(device)
            
            # نمایش نتایج
            self.display_search_results(filtered_devices[:50])  # حداکثر 50 نتیجه
            
        except Exception as e:
            print(f"خطا در جستجو: {e}")
            QMessageBox.warning(self, "خطا", f"خطا در انجام جستجو: {str(e)}")
    
    def display_search_results(self, devices):
        """نمایش نتایج جستجو در جدول"""
        self.search_table.setRowCount(len(devices))
        
        for row, device in enumerate(devices):
            # ستون انتخاب
            select_btn = QPushButton("انتخاب")
            select_btn.setStyleSheet(self.get_button_style("#3498db"))
            select_btn.clicked.connect(lambda checked, d=device: self.load_device(d))
            self.search_table.setCellWidget(row, 0, select_btn)
            
            # اطلاعات دستگاه
            self.search_table.setItem(row, 1, QTableWidgetItem(device.get('device_type', '')))
            self.search_table.setItem(row, 2, QTableWidgetItem(device.get('brand', '')))
            self.search_table.setItem(row, 3, QTableWidgetItem(device.get('model', '')))
            self.search_table.setItem(row, 4, QTableWidgetItem(device.get('serial_number', '')))
            self.search_table.setItem(row, 5, QTableWidgetItem(str(device.get('production_year', ''))))
            
            # تاریخ خرید
            purchase_date = device.get('purchase_date', '')
            if purchase_date:
                try:
                    # تبدیل تاریخ میلادی به شمسی
                    if isinstance(purchase_date, str):
                        year, month, day = map(int, purchase_date.split('-')[:3])
                        jalali_date = jdatetime.date.fromgregorian(year=year, month=month, day=day)
                        date_str = jalali_date.strftime('%Y/%m/%d')
                        self.search_table.setItem(row, 6, QTableWidgetItem(date_str))
                except:
                    self.search_table.setItem(row, 6, QTableWidgetItem(str(purchase_date)))
            else:
                self.search_table.setItem(row, 6, QTableWidgetItem(''))
            
            # دکمه عملیات
            delete_btn = QPushButton("🗑️ حذف")
            delete_btn.setStyleSheet(self.get_button_style("#e74c3c"))
            delete_btn.clicked.connect(lambda checked, d=device: self.confirm_delete_device(d))
            self.search_table.setCellWidget(row, 7, delete_btn)
    
    
    def clear_search(self):
        """پاک کردن فیلدهای جستجو"""
        self.search_brand.clear()
        self.search_model.clear()
        self.search_serial.clear()
        self.search_type.setCurrentIndex(0)
        self.search_table.setRowCount(0)
    
    # ========== عملیات فرم ==========
    
    def new_device(self):
        """ایجاد دستگاه جدید"""
        try:
            # تایید از کاربر
            reply = QMessageBox.question(
                self, "دستگاه جدید",
                "آیا می‌خواهید دستگاه جدید ایجاد کنید؟\nداده‌های فعلی ذخیره نخواهند شد.",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                # پاک کردن فرم
                self.reset_form()
                
                # رفتن به تب ویرایش
                self.tabs.setCurrentIndex(1)
                
                QMessageBox.information(self, "عملیات موفق", "فرم برای ثبت دستگاه جدید آماده است.")
        except Exception as e:
            QMessageBox.critical(self, "خطا", f"خطا در ایجاد دستگاه جدید: {str(e)}")
    

    def save_device(self):
        """ذخیره دستگاه"""
        
        print(f"🔍 بررسی توابع: check_and_add_lookup_value وجود دارد؟ {hasattr(self, 'check_and_add_lookup_value')}")
        
        try:
            # اعتبارسنجی داده‌ها
            if not self.validate_form():
                return
            
            # جمع‌آوری داده‌ها
            device_data = self.collect_device_data()
            
            # 🔴 بخش جدید: بررسی و ذخیره گزینه‌های جدید
            # این باید قبل از ذخیره دستگاه انجام شود
            
            # ۱. برای نوع دستگاه
            device_type_value = device_data.get('device_type', '').strip()
            if device_type_value:
                # بررسی و اضافه کردن به دیتابیس اگر جدید است
                self.check_and_add_lookup_value('device_type', device_type_value, self.device_type)
            
            # ۲. برای برند
            brand_value = device_data.get('brand', '').strip()
            if brand_value:
                # بررسی و اضافه کردن به دیتابیس اگر جدید است
                self.check_and_add_lookup_value('device_brand', brand_value, self.brand)
            
            # ۳. ادامه فرآیند ذخیره دستگاه
            if self.current_device_id:
                # ویرایش دستگاه موجود
                success = self.data_manager.device.update_device(self.current_device_id, device_data)
                message = "ویرایش"
            else:
                # ثبت دستگاه جدید
                success = self.data_manager.device.add_device(device_data)
                message = "ثبت"
            
            if success:
                # ارسال سیگنال
                self.device_saved.emit(device_data)
                
                # نمایش پیام موفقیت
                QMessageBox.information(self, "عملیات موفق", 
                    f"دستگاه با موفقیت {message} شد.")
                
                # تازه‌سازی لیست دستگاه‌ها
                self.load_devices()
                self.perform_search()
                
                # رفتن به تب جستجو
                self.tabs.setCurrentIndex(0)
                
                # غیرفعال کردن دکمه حذف
                if not self.current_device_id:
                    self.btn_delete.setEnabled(False)
                    self.device_status_label.setText("دستگاه جدید")
            else:
                QMessageBox.critical(self, "خطا", f"خطا در {message} دستگاه.")
                
        except Exception as e:
            QMessageBox.critical(self, "خطا", f"خطا در ذخیره دستگاه: {str(e)}")
            print(f"❌ خطای کامل: {e}")


    def validate_form(self):
        """اعتبارسنجی داده‌های فرم"""
        # بررسی نوع دستگاه
        if not self.device_type.currentText().strip():  # 🔴 به جای .text()
            QMessageBox.warning(self, "خطا", "لطفا نوع دستگاه را انتخاب کنید.")
            self.tabs.setCurrentIndex(1)
            self.device_type.setFocus()
            return False
        
        # بررسی برند
        if not self.brand.currentText().strip():  # 🔴 به جای .text()
            QMessageBox.warning(self, "خطا", "لطفا برند دستگاه را وارد کنید.")
            self.tabs.setCurrentIndex(1)
            self.brand.setFocus()
            return False
            
        # بررسی مدل
        if not self.model.text().strip():
            QMessageBox.warning(self, "خطا", "لطفا مدل دستگاه را وارد کنید.")
            self.tabs.setCurrentIndex(1)
            self.model.setFocus()
            return False
        
        # اگر گارانتی فعال است، تاریخ پایان را بررسی کن
        if self.warranty_status.isChecked() and not self.warranty_end_date.get_date():
            QMessageBox.warning(self, "خطا", "لطفا تاریخ پایان گارانتی را وارد کنید.")
            self.tabs.setCurrentIndex(1)
            self.warranty_end_date.setFocus()
            return False
        
        return True


    def collect_device_data(self):
        """جمع‌آوری داده‌های فرم"""
        # جمع‌آوری داده‌ها
        data = {
            'device_type': self.device_type.currentText().strip(),
            'brand': self.brand.currentText().strip(),  
            'model': self.model.text().strip(),
            'serial_number': self.serial_number.text().strip() or None,
            'production_year': self.production_year.value(),
            'purchase_date': self.purchase_date.get_gregorian_date(),
            'warranty_status': 1 if self.warranty_status.isChecked() else 0,
            'warranty_end_date': self.warranty_end_date.get_gregorian_date() if self.warranty_status.isChecked() else None,
            'description': self.description.toPlainText().strip(),
        }
        
        return data


    def load_device(self, device_data):
        """بارگذاری یک دستگاه برای ویرایش"""
        try:
            # ذخیره شناسه
            self.current_device_id = device_data.get('id')
            
            # پر کردن فیلدهای فرم
            self.device_type.setCurrentText(device_data.get('device_type', ''))
            self.brand.setText(device_data.get('brand', ''))
            self.model.setText(device_data.get('model', ''))
            self.serial_number.setText(device_data.get('serial_number', ''))
            self.production_year.setValue(device_data.get('production_year', 2024))
            self.purchase_date.set_gregorian_date(device_data.get('purchase_date'))
            
            # وضعیت گارانتی
            warranty_status = device_data.get('warranty_status', 0)
            self.warranty_status.setChecked(bool(warranty_status))
            self.warranty_end_date.set_gregorian_date(device_data.get('warranty_end_date'))
            self.warranty_end_date.setEnabled(bool(warranty_status))
            
            # توضیحات
            self.description.setText(device_data.get('description', ''))
            
            # به‌روزرسانی وضعیت
            self.device_status_label.setText("در حال ویرایش")
            self.device_status_label.setStyleSheet("""
                QLabel {
                    font-size: 14px;
                    font-weight: bold;
                    color: #3498db;
                    background-color: #34495e;
                    padding: 5px 10px;
                    border-radius: 5px;
                }
            """)
            
            # فعال کردن دکمه حذف
            self.btn_delete.setEnabled(True)
            
            # رفتن به تب ویرایش
            self.tabs.setCurrentIndex(1)
            
            QMessageBox.information(self, "بارگذاری موفق", 
                f"دستگاه {device_data.get('brand', '')} {device_data.get('model', '')} برای ویرایش بارگذاری شد.")
            
        except Exception as e:
            QMessageBox.critical(self, "خطا", f"خطا در بارگذاری دستگاه: {str(e)}")


    def load_device_data(self):
        """بارگذاری دستگاه بر اساس ID"""
        try:
            if not self.current_device_id:
                return
            
            device = self.data_manager.device.get_device_by_id(self.current_device_id)
            if device:
                self.load_device(device)
            else:
                QMessageBox.warning(self, "خطا", "دستگاه مورد نظر یافت نشد.")
                self.current_device_id = None
                
        except Exception as e:
            QMessageBox.critical(self, "خطا", f"خطا در بارگذاری دستگاه: {str(e)}")


    def delete_device(self):
        """حذف دستگاه جاری"""
        if not self.current_device_id:
            QMessageBox.warning(self, "خطا", "هیچ دستگاه‌ای برای حذف انتخاب نشده است.")
            return
        
        try:
            # دریافت اطلاعات دستگاه
            device = self.data_manager.device.get_device_by_id(self.current_device_id)
            if not device:
                QMessageBox.warning(self, "خطا", "دستگاه مورد نظر یافت نشد.")
                return
            
            # تأیید حذف
            reply = QMessageBox.question(
                self, "حذف دستگاه",
                f"آیا مطمئن هستید که می‌خواهید دستگاه زیر را حذف کنید؟\n\n"
                f"برند: {device.get('brand', '')}\n"
                f"مدل: {device.get('model', '')}\n"
                f"سریال: {device.get('serial_number', '')}\n\n"
                f"⚠️ توجه: این عمل قابل بازگشت نیست!",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                # حذف از دیتابیس
                query = "DELETE FROM Devices WHERE id = ?"
                success = self.data_manager.device.execute_query(query, (self.current_device_id,))
                
                if success:
                    QMessageBox.information(self, "حذف موفق", "دستگاه با موفقیت حذف شد.")
                    
                    # پاک کردن فرم
                    self.reset_form()
                    
                    # تازه‌سازی لیست دستگاه‌ها
                    self.load_devices()
                    self.perform_search()
                    
                    # رفتن به تب جستجو
                    self.tabs.setCurrentIndex(0)
                else:
                    QMessageBox.critical(self, "خطا", "خطا در حذف دستگاه.")
                    
        except Exception as e:
            QMessageBox.critical(self, "خطا", f"خطا در حذف دستگاه: {str(e)}")


    def confirm_delete_device(self, device_data):
        """تأیید حذف دستگاه از جدول جستجو"""
        try:
            # تأیید حذف
            reply = QMessageBox.question(
                self, "حذف دستگاه",
                f"آیا مطمئن هستید که می‌خواهید دستگاه زیر را حذف کنید؟\n\n"
                f"برند: {device_data.get('brand', '')}\n"
                f"مدل: {device_data.get('model', '')}\n"
                f"سریال: {device_data.get('serial_number', '')}",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                # حذف از دیتابیس
                query = "DELETE FROM Devices WHERE id = ?"
                success = self.data_manager.device.execute_query(query, (device_data.get('id'),))
                
                if success:
                    QMessageBox.information(self, "حذف موفق", "دستگاه با موفقیت حذف شد.")
                    
                    # تازه‌سازی لیست
                    self.load_devices()
                    self.perform_search()
                else:
                    QMessageBox.critical(self, "خطا", "خطا در حذف دستگاه.")
                    
        except Exception as e:
            QMessageBox.critical(self, "خطا", f"خطا در حذف دستگاه: {str(e)}")


    def reset_form(self):
        """بازنشانی فرم به حالت اولیه"""
        # پاک کردن شناسه
        self.current_device_id = None
        
        # پاک کردن فیلدها
        self.device_type.setCurrentIndex(0)
        self.brand.clear()
        self.model.clear()
        self.serial_number.clear()
        self.production_year.setValue(2024)
        self.purchase_date.clear()
        self.warranty_status.setChecked(False)
        self.warranty_end_date.clear()
        self.warranty_end_date.setEnabled(False)
        self.description.clear()
        
        # به‌روزرسانی وضعیت
        self.device_status_label.setText("دستگاه جدید")
        self.device_status_label.setStyleSheet("""
            QLabel {
                font-size: 14px;
                font-weight: bold;
                color: #f39c12;
                background-color: #34495e;
                padding: 5px 10px;
                border-radius: 5px;
            }
        """)
        
        # غیرفعال کردن دکمه حذف
        self.btn_delete.setEnabled(False)


    def close_form(self):
        """بستن فرم"""
        # بررسی ذخیره نشده
        if self.is_form_modified():
            reply = QMessageBox.question(
                self, "انصراف",
                "آیا مطمئن هستید؟ تغییرات ذخیره نشده از دست خواهند رفت.",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.No:
                return
        
        # ارسال سیگنال بسته شدن
        self.form_closed.emit()
        self.close()  
   
   
    def is_form_modified(self):
        """بررسی تغییرات در فرم"""
        # تغییرات اصلی: استفاده از currentText() برای QComboBox
        if (self.brand.currentText().strip() or  # 🔴 به جای .text()
            self.model.text().strip() or 
            self.device_type.currentText() != ""):  # 🔴 به جای بررسی با "یخچال"
            return True
        return False


    def debug_functions(self):
        """بررسی وجود توابع مورد نیاز"""
        functions_to_check = [
            'check_and_add_lookup_value',
            'add_new_lookup_value', 
            'save_device',
            'validate_form'
        ]
        
        for func_name in functions_to_check:
            if hasattr(self, func_name):
                print(f"✅ تابع {func_name} وجود دارد")
            else:
                print(f"❌ تابع {func_name} وجود ندارد!")
        
        # این را در init_ui بعد از ایجاد فرم صدا بزنید
        # self.debug_functions()

   
    def closeEvent(self, event):
        """مدیریت بسته شدن فرم"""
        self.close_form()
        event.ignore()


# تست فرم
if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication
    import sys
    
    app = QApplication(sys.argv)
    
    # ایجاد یک DataManager نمونه (بدون دیتابیس واقعی)
    from database.database import DatabaseManager
    from database.models import DataManager
    
    db_manager = DatabaseManager(":memory:")  # دیتابیس در حافظه برای تست
    db_manager.initialize_database()
    
    data_manager = DataManager()
    data_manager.db = db_manager
    
    # ایجاد و نمایش فرم
    form = DeviceForm(data_manager)
    form.show()
    
    sys.exit(app.exec())