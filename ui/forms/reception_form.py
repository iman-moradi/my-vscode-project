"""
فرم مدیریت پذیرش دستگاه‌ها
برای ثبت، جستجو و مدیریت پذیرش‌های جدید
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QComboBox, QDateEdit, QTextEdit, QTableWidget,
    QTableWidgetItem, QTabWidget, QFrame, QGroupBox, QMessageBox,
    QHeaderView, QSpinBox, QDoubleSpinBox, QFormLayout,
    QSplitter, QListWidget, QListWidgetItem, QGridLayout,
    QApplication, QStyleFactory, QScrollArea, QSizePolicy , QAbstractSpinBox  
)
from PySide6.QtCore import Qt, QDate, Signal, QTimer, QDateTime
from PySide6.QtGui import QFont, QColor, QIcon
import jdatetime
from datetime import datetime
import sys
import os

# افزودن مسیر پروژه به sys.path برای ایمپورت‌های صحیح
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
sys.path.insert(0, project_root)

# ایمپورت ویجت تاریخ شمسی
from utils.jalali_date_widget import JalaliDateInput


class ReceptionForm(QWidget):
    """
    فرم مدیریت پذیرش دستگاه‌ها
    شامل ثبت پذیرش جدید، جستجو و نمایش پذیرش‌های موجود
    """
    
    # سیگنال‌ها
    reception_saved = Signal(dict)  # هنگامی که پذیرش ذخیره می‌شود
    form_closed = Signal()  # هنگامی که فرم بسته می‌شود
    
    def __init__(self, data_manager):
        super().__init__()
        self.data_manager = data_manager
        self.current_reception_id = None
        self.customer_data = None
        self.device_data = None
        
        # 🔴 اضافه کردن این خط (برای ذخیره فرم دستگاه)
        self.device_form = None

        # لیست‌های کش شده
        self.customers_cache = []
        self.devices_cache = []
        
        self.init_ui()
        self.setup_connections()
        self.load_initial_data()
        
    def init_ui(self):
        """راه‌اندازی رابط کاربری"""
        self.setWindowTitle("📝 فرم پذیرش دستگاه - سیستم مدیریت تعمیرگاه")
        self.setMinimumSize(1200, 700)
        
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
        title_label = QLabel("📝 فرم پذیرش دستگاه جدید")
        title_label.setStyleSheet("""
            QLabel {
                font-size: 18px;
                font-weight: bold;
                color: white;
            }
        """)
        title_layout.addWidget(title_label)
        title_layout.addStretch()
        
        # شماره پذیرش
        self.reception_number_label = QLabel("شماره پذیرش: در حال تولید...")
        self.reception_number_label.setStyleSheet("""
            QLabel {
                font-size: 14px;
                font-weight: bold;
                color: #f39c12;
                background-color: #34495e;
                padding: 5px 10px;
                border-radius: 5px;
            }
        """)
        title_layout.addWidget(self.reception_number_label)
        
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
        
        # ایجاد تب‌ها
        self.create_search_tab()      # تب 1: جستجو
        self.create_customer_tab()    # تب 2: اطلاعات مشتری
        self.create_device_tab()      # تب 3: اطلاعات دستگاه
        self.create_reception_tab()   # تب 4: اطلاعات پذیرش
        self.create_accessories_tab() # تب 5: قطعات همراه
        self.create_history_tab()     # تب 6: تاریخچه
        
        main_layout.addWidget(self.tabs)
        
        # نوار دکمه‌های عملیاتی
        button_frame = QFrame()
        button_layout = QHBoxLayout()

        # دکمه‌های اصلی
        self.btn_new = QPushButton("🆕 پذیرش جدید")
        self.btn_new.setStyleSheet(self.get_button_style("#27ae60"))
        self.btn_new.clicked.connect(self.new_reception)
        
        self.btn_save = QPushButton("💾 ذخیره پذیرش")
        self.btn_save.setStyleSheet(self.get_button_style("#3498db"))
        self.btn_save.clicked.connect(self.save_reception)
        
        self.btn_print = QPushButton("🖨️ چاپ فرم پذیرش")
        self.btn_print.setStyleSheet(self.get_button_style("#9b59b6"))
        self.btn_print.clicked.connect(self.print_reception)
        
        self.btn_to_repair = QPushButton("🔧 ثبت تعمیر")
        self.btn_to_repair.setStyleSheet(self.get_button_style("#9b59b6"))
        self.btn_to_repair.clicked.connect(self.open_repair_form)
        self.btn_to_repair.setEnabled(False)  # ابتدا غیرفعال


        self.btn_cancel = QPushButton("❌ انصراف")
        self.btn_cancel.setStyleSheet(self.get_button_style("#e74c3c"))
        self.btn_cancel.clicked.connect(self.close_form)
        
        button_layout.addWidget(self.btn_new)
        button_layout.addWidget(self.btn_save)
        button_layout.addStretch()
        button_layout.addWidget(self.btn_to_repair)
        button_layout.addWidget(self.btn_print)
        button_layout.addStretch()
        button_layout.addWidget(self.btn_cancel)
            
        button_frame.setLayout(button_layout)
        main_layout.addWidget(button_frame)
        
        self.setLayout(main_layout)
        
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
        QLineEdit, QComboBox, QTextEdit, QSpinBox, QDoubleSpinBox {
            background-color: #2c2c2c;
            color: white;
            border: 1px solid #444;
            border-radius: 4px;
            padding: 6px;
            font-size: 13px;
            selection-background-color: #3498db;
        }
        
        QLineEdit:focus, QComboBox:focus, QTextEdit:focus,
        QSpinBox:focus, QDoubleSpinBox:focus {
            border: 2px solid #3498db;
        }
        
        QLineEdit::placeholder, QTextEdit::placeholder {
            color: #666;
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
        
        QScrollBar:horizontal {
            background-color: #2c2c2c;
            height: 12px;
            border-radius: 6px;
        }
        
        QScrollBar::handle:horizontal {
            background-color: #444;
            border-radius: 6px;
            min-width: 20px;
        }
        
        QScrollBar::handle:horizontal:hover {
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
    
    # ========== تب 1: جستجو ==========
    def create_search_tab(self):
        """ایجاد تب جستجوی پذیرش‌ها"""
        tab = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(15)
        
        # گروه جستجوی سریع
        search_group = QGroupBox("🔍 جستجوی سریع پذیرش‌ها")
        search_layout = QGridLayout()
        
        # فیلدهای جستجو
        search_layout.addWidget(QLabel("شماره پذیرش:"), 0, 0)
        self.search_reception_number = QLineEdit()
        self.search_reception_number.setPlaceholderText("شماره پذیرش")
        search_layout.addWidget(self.search_reception_number, 0, 1)
        
        search_layout.addWidget(QLabel("نام مشتری:"), 0, 2)
        self.search_customer_name = QLineEdit()
        self.search_customer_name.setPlaceholderText("نام یا نام خانوادگی مشتری")
        search_layout.addWidget(self.search_customer_name, 0, 3)
        
        search_layout.addWidget(QLabel("شماره همراه:"), 1, 0)
        self.search_mobile = QLineEdit()
        self.search_mobile.setPlaceholderText("شماره موبایل مشتری")
        search_layout.addWidget(self.search_mobile, 1, 1)
        
        search_layout.addWidget(QLabel("وضعیت:"), 1, 2)
        self.search_status = QComboBox()
        self.search_status.addItems(["همه", "در انتظار", "در حال تعمیر", "تعمیر شده", "تحویل داده شده", "لغو شده"])
        search_layout.addWidget(self.search_status, 1, 3)
        
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
        self.search_table.setColumnCount(9)
        self.search_table.setHorizontalHeaderLabels([
            "انتخاب", "شماره پذیرش", "مشتری", "دستگاه", "تاریخ", 
            "هزینه تخمینی", "اولویت", "وضعیت", "عملیات"
        ])
        self.search_table.horizontalHeader().setStretchLastSection(True)
        self.search_table.setAlternatingRowColors(True)
        
        # تنظیم عرض ستون‌ها
        self.search_table.setColumnWidth(0, 60)   # انتخاب
        self.search_table.setColumnWidth(1, 120)  # شماره پذیرش
        self.search_table.setColumnWidth(2, 150)  # مشتری
        self.search_table.setColumnWidth(3, 150)  # دستگاه
        self.search_table.setColumnWidth(4, 100)  # تاریخ
        self.search_table.setColumnWidth(5, 120)  # هزینه
        self.search_table.setColumnWidth(6, 80)   # اولویت
        self.search_table.setColumnWidth(7, 100)  # وضعیت
        
        layout.addWidget(self.search_table)
        
        tab.setLayout(layout)
        self.tabs.addTab(tab, "🔍 جستجو")
        
        # اتصال جستجوی زنده
        self.search_reception_number.textChanged.connect(self.start_search_timer)
        self.search_customer_name.textChanged.connect(self.start_search_timer)
        self.search_mobile.textChanged.connect(self.start_search_timer)
    
    def start_search_timer(self):
        """شروع تایمر برای جستجوی زنده"""
        self.search_timer.start(500)  # 500ms delay
    
    # ========== تب 2: اطلاعات مشتری ==========
    def create_customer_tab(self):
        """ایجاد تب اطلاعات مشتری"""
        tab = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(15)
        
        # گروه انتخاب مشتری
        customer_group = QGroupBox("👥 اطلاعات مشتری")
        customer_layout = QVBoxLayout()
        
        # انتخاب مشتری موجود
        select_customer_layout = QHBoxLayout()
        select_customer_layout.addWidget(QLabel("انتخاب مشتری موجود:"))
        
        self.customer_search = QLineEdit()
        self.customer_search.setPlaceholderText("جستجوی مشتری (نام، نام خانوادگی، شماره همراه)")
        self.customer_search.textChanged.connect(self.search_customers)
        select_customer_layout.addWidget(self.customer_search)
        
        self.customer_list = QListWidget()
        self.customer_list.setMaximumHeight(150)
        self.customer_list.itemClicked.connect(self.select_customer)
        select_customer_layout.addWidget(self.customer_list)
        
        customer_layout.addLayout(select_customer_layout)
        
        # یا ثبت مشتری جدید
        new_customer_layout = QHBoxLayout()
        new_customer_layout.addWidget(QLabel("ثبت مشتری جدید:"))
        
        self.btn_new_customer = QPushButton("➕ ثبت مشتری جدید")
        self.btn_new_customer.setStyleSheet(self.get_button_style("#27ae60"))
        self.btn_new_customer.clicked.connect(self.open_new_customer_form)
        new_customer_layout.addWidget(self.btn_new_customer)
        
        new_customer_layout.addStretch()
        customer_layout.addLayout(new_customer_layout)
        
        # اطلاعات مشتری انتخاب شده
        self.customer_info_frame = QFrame()
        self.customer_info_frame.setStyleSheet("""
            QFrame {
                background-color: #2c2c2c;
                border: 1px solid #444;
                border-radius: 5px;
                padding: 15px;
            }
        """)
        self.customer_info_frame.setVisible(False)
        
        customer_info_layout = QGridLayout()
        
        customer_info_layout.addWidget(QLabel("نام:"), 0, 0)
        self.customer_first_name = QLabel("---")
        customer_info_layout.addWidget(self.customer_first_name, 0, 1)
        
        customer_info_layout.addWidget(QLabel("نام خانوادگی:"), 0, 2)
        self.customer_last_name = QLabel("---")
        customer_info_layout.addWidget(self.customer_last_name, 0, 3)
        
        customer_info_layout.addWidget(QLabel("شماره همراه:"), 1, 0)
        self.customer_mobile = QLabel("---")
        customer_info_layout.addWidget(self.customer_mobile, 1, 1)
        
        customer_info_layout.addWidget(QLabel("تلفن ثابت:"), 1, 2)
        self.customer_phone = QLabel("---")
        customer_info_layout.addWidget(self.customer_phone, 1, 3)
        
        customer_info_layout.addWidget(QLabel("آدرس:"), 2, 0)
        self.customer_address = QLabel("---")
        self.customer_address.setWordWrap(True)
        customer_info_layout.addWidget(self.customer_address, 2, 1, 1, 3)
        
        self.customer_info_frame.setLayout(customer_info_layout)
        customer_layout.addWidget(self.customer_info_frame)
        
        customer_group.setLayout(customer_layout)
        layout.addWidget(customer_group)
        layout.addStretch()
        
        tab.setLayout(layout)
        self.tabs.addTab(tab, "👥 مشتری")
    
    # ========== تب 3: اطلاعات دستگاه ==========
    # ========== تب 3: اطلاعات دستگاه ==========
    def create_device_tab(self):
        """ایجاد تب اطلاعات دستگاه"""
        tab = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(15)
        
        # گروه انتخاب دستگاه
        device_group = QGroupBox("📱 اطلاعات دستگاه")
        device_layout = QVBoxLayout()
        
        # انتخاب دستگاه موجود
        select_device_layout = QHBoxLayout()
        select_device_layout.addWidget(QLabel("انتخاب دستگاه موجود:"))
        
        self.device_search = QLineEdit()
        self.device_search.setPlaceholderText("جستجوی دستگاه (برند، مدل، سریال)")
        self.device_search.textChanged.connect(self.search_devices)
        select_device_layout.addWidget(self.device_search)
        
        self.device_list = QListWidget()
        self.device_list.setMaximumHeight(150)
        self.device_list.itemClicked.connect(self.select_device)
        select_device_layout.addWidget(self.device_list)
        
        device_layout.addLayout(select_device_layout)
        
        # 🔴 یا ثبت دستگاه جدید (اصلاح شده)
        new_device_layout = QHBoxLayout()
        new_device_layout.addWidget(QLabel("ثبت دستگاه جدید:"))
        
        self.btn_new_device = QPushButton("➕ ثبت دستگاه جدید")
        self.btn_new_device.setStyleSheet(self.get_button_style("#27ae60"))
        self.btn_new_device.clicked.connect(self.open_new_device_form)  # 🔴 تغییر این خط
        new_device_layout.addWidget(self.btn_new_device)
        
        new_device_layout.addStretch()
        device_layout.addLayout(new_device_layout)
        
        # اطلاعات دستگاه انتخاب شده
        self.device_info_frame = QFrame()
        self.device_info_frame.setStyleSheet("""
            QFrame {
                background-color: #2c2c2c;
                border: 1px solid #444;
                border-radius: 5px;
                padding: 15px;
            }
        """)
        self.device_info_frame.setVisible(False)
        
        device_info_layout = QGridLayout()
        
        device_info_layout.addWidget(QLabel("نوع دستگاه:"), 0, 0)
        self.device_type_label = QLabel("---")  # 🔴 تغییر نام از device_type به device_type_label
        device_info_layout.addWidget(self.device_type_label, 0, 1)
        
        device_info_layout.addWidget(QLabel("برند:"), 0, 2)
        self.device_brand_label = QLabel("---")  # 🔴 تغییر نام از device_brand به device_brand_label
        device_info_layout.addWidget(self.device_brand_label, 0, 3)
        
        device_info_layout.addWidget(QLabel("مدل:"), 1, 0)
        self.device_model_label = QLabel("---")  # 🔴 تغییر نام از device_model به device_model_label
        device_info_layout.addWidget(self.device_model_label, 1, 1)
        
        device_info_layout.addWidget(QLabel("شماره سریال:"), 1, 2)
        self.device_serial_label = QLabel("---")  # 🔴 تغییر نام از device_serial به device_serial_label
        device_info_layout.addWidget(self.device_serial_label, 1, 3)
        
        device_info_layout.addWidget(QLabel("سال تولید:"), 2, 0)
        self.device_year_label = QLabel("---")  # 🔴 تغییر نام از device_year به device_year_label
        device_info_layout.addWidget(self.device_year_label, 2, 1)
        
        device_info_layout.addWidget(QLabel("وضعیت گارانتی:"), 2, 2)
        self.device_warranty_label = QLabel("---")  # 🔴 تغییر نام از device_warranty به device_warranty_label
        device_info_layout.addWidget(self.device_warranty_label, 2, 3)
        
        self.device_info_frame.setLayout(device_info_layout)
        device_layout.addWidget(self.device_info_frame)
        
        device_group.setLayout(device_layout)
        layout.addWidget(device_group)
        layout.addStretch()
        
        tab.setLayout(layout)
        self.tabs.addTab(tab, "📱 دستگاه")
    
    # ========== تب 4: اطلاعات پذیرش ==========
    def create_reception_tab(self):
        """ایجاد تب اطلاعات پذیرش"""
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
        
        # گروه اطلاعات پذیرش
        reception_group = QGroupBox("📋 اطلاعات پذیرش")
        reception_layout = QGridLayout()
        
        # تاریخ پذیرش
        reception_layout.addWidget(QLabel("📅 تاریخ پذیرش:"), 0, 0)
        self.reception_date = JalaliDateInput()
        reception_layout.addWidget(self.reception_date, 0, 1)
        
        # زمان پذیرش
        reception_layout.addWidget(QLabel("🕒 زمان پذیرش:"), 0, 2)
        self.reception_time = QLineEdit()
        self.reception_time.setText(QDateTime.currentDateTime().toString("HH:mm"))
        reception_layout.addWidget(self.reception_time, 0, 3)
        
        # اولویت
        reception_layout.addWidget(QLabel("⚠️ اولویت:"), 1, 0)
        self.priority = QComboBox()
        self.priority.addItems(["عادی", "فوری", "خیلی فوری"])
        reception_layout.addWidget(self.priority, 1, 1)
        
        # وضعیت
        reception_layout.addWidget(QLabel("📊 وضعیت:"), 1, 2)
        self.status = QComboBox()
        self.status.addItems(["در انتظار", "در حال تعمیر", "تعمیر شده", "تحویل داده شده", "لغو شده"])
        reception_layout.addWidget(self.status, 1, 3)
        
        # هزینه تخمینی
        reception_layout.addWidget(QLabel("💰 هزینه تخمینی (تومان):"), 2, 0)
        self.estimated_cost = QDoubleSpinBox()
        self.estimated_cost.setRange(0, 100000000)
        self.estimated_cost.setValue(0)
        self.estimated_cost.setPrefix("")
        self.estimated_cost.setSuffix(" تومان")
        self.estimated_cost.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.NoButtons)
        reception_layout.addWidget(self.estimated_cost, 2, 1)
        
        # تاریخ تحویل تخمینی
        reception_layout.addWidget(QLabel("📅 تاریخ تحویل تخمینی:"), 2, 2)
        self.estimated_delivery_date = JalaliDateInput()
        reception_layout.addWidget(self.estimated_delivery_date, 2, 3)
        
        # کارمند پذیرش
        reception_layout.addWidget(QLabel("👤 کارمند پذیرش:"), 3, 0)
        self.reception_employee = QLineEdit()
        self.reception_employee.setText("سیستم")
        reception_layout.addWidget(self.reception_employee, 3, 1)
        
        reception_group.setLayout(reception_layout)
        layout.addWidget(reception_group)
        
        # گروه شرح خرابی
        problem_group = QGroupBox("🔧 شرح خرابی دستگاه")
        problem_layout = QVBoxLayout()
        
        self.problem_description = QTextEdit()
        self.problem_description.setPlaceholderText("شرح کامل خرابی دستگاه را وارد کنید...")
        self.problem_description.setMaximumHeight(150)
        problem_layout.addWidget(self.problem_description)
        
        problem_group.setLayout(problem_layout)
        layout.addWidget(problem_group)
        
        # گروه وضعیت ظاهری دستگاه
        condition_group = QGroupBox("🔍 وضعیت ظاهری دستگاه")
        condition_layout = QVBoxLayout()
        
        self.device_condition = QTextEdit()
        self.device_condition.setPlaceholderText("وضعیت ظاهری دستگاه (خراش، ضربه، شکستگی و ...)")
        self.device_condition.setMaximumHeight(100)
        condition_layout.addWidget(self.device_condition)
        
        condition_group.setLayout(condition_layout)
        layout.addWidget(condition_group)
        
        # گروه توضیحات اضافی
        notes_group = QGroupBox("📝 توضیحات اضافی")
        notes_layout = QVBoxLayout()
        
        self.notes = QTextEdit()
        self.notes.setPlaceholderText("هر گونه توضیح اضافی...")
        self.notes.setMaximumHeight(100)
        notes_layout.addWidget(self.notes)
        
        notes_group.setLayout(notes_layout)
        layout.addWidget(notes_group)
        
        layout.addStretch()
        
        content_widget.setLayout(layout)
        scroll.setWidget(content_widget)
        
        tab_layout = QVBoxLayout()
        tab_layout.addWidget(scroll)
        tab.setLayout(tab_layout)
        
        self.tabs.addTab(tab, "📋 پذیرش")
    
    # ========== تب 5: قطعات همراه ==========
    def create_accessories_tab(self):
        """ایجاد تب قطعات همراه"""
        tab = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(15)
        
        # گروه قطعات همراه
        accessories_group = QGroupBox("🔩 قطعات همراه دستگاه")
        accessories_layout = QVBoxLayout()
        
        # دکمه افزودن قطعه
        add_accessory_layout = QHBoxLayout()
        
        self.accessory_name = QLineEdit()
        self.accessory_name.setPlaceholderText("نام قطعه (مثال: کابل برق، ریموت، پایه و ...)")
        add_accessory_layout.addWidget(self.accessory_name)
        
        self.accessory_quantity = QSpinBox()
        self.accessory_quantity.setRange(1, 100)
        self.accessory_quantity.setValue(1)
        self.accessory_quantity.setPrefix("تعداد: ")
        add_accessory_layout.addWidget(self.accessory_quantity)
        
        self.btn_add_accessory = QPushButton("➕ افزودن قطعه")
        self.btn_add_accessory.setStyleSheet(self.get_button_style("#27ae60"))
        self.btn_add_accessory.clicked.connect(self.add_accessory)
        add_accessory_layout.addWidget(self.btn_add_accessory)
        
        accessories_layout.addLayout(add_accessory_layout)
        
        # جدول قطعات
        self.accessories_table = QTableWidget()
        self.accessories_table.setColumnCount(3)
        self.accessories_table.setHorizontalHeaderLabels(["نام قطعه", "تعداد", "عملیات"])
        self.accessories_table.horizontalHeader().setStretchLastSection(True)
        self.accessories_table.setAlternatingRowColors(True)
        
        accessories_layout.addWidget(self.accessories_table)
        accessories_group.setLayout(accessories_layout)
        layout.addWidget(accessories_group)
        
        # گروه یادآوری به مشتری
        reminder_group = QGroupBox("🔔 یادآوری به مشتری")
        reminder_layout = QVBoxLayout()
        
        self.customer_reminder = QTextEdit()
        self.customer_reminder.setPlaceholderText("یادآوری‌های لازم به مشتری (مثال: همراه داشتن کارت گارانتی، رسید و ...)")
        self.customer_reminder.setMaximumHeight(100)
        reminder_layout.addWidget(self.customer_reminder)
        
        reminder_group.setLayout(reminder_layout)
        layout.addWidget(reminder_group)
        
        layout.addStretch()
        
        tab.setLayout(layout)
        self.tabs.addTab(tab, "🔩 قطعات")
    
    # ========== تب 6: تاریخچه ==========
    def create_history_tab(self):
        """ایجاد تب تاریخچه پذیرش"""
        tab = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(15)
        
        # گروه تاریخچه
        history_group = QGroupBox("📜 تاریخچه تغییرات")
        history_layout = QVBoxLayout()
        
        # جدول تاریخچه
        self.history_table = QTableWidget()
        self.history_table.setColumnCount(4)
        self.history_table.setHorizontalHeaderLabels(["تاریخ", "زمان", "عملیات", "توضیحات"])
        self.history_table.horizontalHeader().setStretchLastSection(True)
        self.history_table.setAlternatingRowColors(True)
        
        history_layout.addWidget(self.history_table)
        history_group.setLayout(history_layout)
        layout.addWidget(history_group)
        
        # گروه آمار
        stats_group = QGroupBox("📊 آمار پذیرش")
        stats_layout = QGridLayout()
        
        stats_layout.addWidget(QLabel("تعداد کل پذیرش‌ها:"), 0, 0)
        self.total_receptions_label = QLabel("0")
        self.total_receptions_label.setStyleSheet("color: #3498db; font-weight: bold;")
        stats_layout.addWidget(self.total_receptions_label, 0, 1)
        
        stats_layout.addWidget(QLabel("پذیرش‌های امروز:"), 0, 2)
        self.today_receptions_label = QLabel("0")
        self.today_receptions_label.setStyleSheet("color: #27ae60; font-weight: bold;")
        stats_layout.addWidget(self.today_receptions_label, 0, 3)
        
        stats_layout.addWidget(QLabel("در حال تعمیر:"), 1, 0)
        self.repairing_label = QLabel("0")
        self.repairing_label.setStyleSheet("color: #f39c12; font-weight: bold;")
        stats_layout.addWidget(self.repairing_label, 1, 1)
        
        stats_layout.addWidget(QLabel("تعمیر شده:"), 1, 2)
        self.repaired_label = QLabel("0")
        self.repaired_label.setStyleSheet("color: #9b59b6; font-weight: bold;")
        stats_layout.addWidget(self.repaired_label, 1, 3)
        
        stats_group.setLayout(stats_layout)
        layout.addWidget(stats_group)
        
        layout.addStretch()
        
        tab.setLayout(layout)
        self.tabs.addTab(tab, "📜 تاریخچه")
    
    # ========== متدهای کمکی ==========
    
    def setup_connections(self):
        """تنظیم اتصالات"""
        # تایمر برای به‌روزرسانی شماره پذیرش
        QTimer.singleShot(100, self.generate_reception_number)
    
    def load_initial_data(self):
        """بارگذاری داده‌های اولیه"""
        # بارگذاری لیست مشتریان
        self.load_customers()
        
        # بارگذاری لیست دستگاه‌ها
        self.load_devices()
        
        # بارگذاری پذیرش‌های اخیر
        self.load_recent_receptions()
        
        # بارگذاری آمار
        self.load_stats()
    
    def load_customers(self):
        """بارگذاری لیست مشتریان"""
        try:
            self.customers_cache = self.data_manager.person.get_all_persons()
            # فقط مشتریان
            self.customers_cache = [p for p in self.customers_cache if p.get('person_type') == 'مشتری']
        except Exception as e:
            print(f"خطا در بارگذاری مشتریان: {e}")
            self.customers_cache = []
    
    def load_devices(self):
        """بارگذاری لیست دستگاه‌ها"""
        try:
            self.devices_cache = self.data_manager.device.get_all_devices()
        except Exception as e:
            print(f"خطا در بارگذاری دستگاه‌ها: {e}")
            self.devices_cache = []
    
    def search_customers(self, keyword):
        """جستجوی مشتریان"""
        if not keyword:
            self.customer_list.clear()
            return
        
        filtered = []
        for customer in self.customers_cache:
            search_text = f"{customer.get('first_name', '')} {customer.get('last_name', '')} {customer.get('mobile', '')}".lower()
            if keyword.lower() in search_text:
                filtered.append(customer)
        
        self.customer_list.clear()
        for customer in filtered[:10]:  # حداکثر 10 نتیجه
            item = QListWidgetItem()
            item.setText(f"{customer.get('first_name', '')} {customer.get('last_name', '')} - {customer.get('mobile', '')}")
            item.setData(Qt.UserRole, customer)
            self.customer_list.addItem(item)
    
    def search_devices(self, keyword):
        """جستجوی دستگاه‌ها"""
        if not keyword:
            # 🔴 اگر جستجو خالی است، همه دستگاه‌ها را نشان بده
            self.device_list.clear()
            for device in self.devices_cache[:20]:  # حداکثر ۲۰ دستگاه
                item = QListWidgetItem()
                item.setText(f"{device.get('device_type', '')} {device.get('brand', '')} {device.get('model', '')} - سریال: {device.get('serial_number', '')}")
                item.setData(Qt.UserRole, device)
                self.device_list.addItem(item)
            return
        
        # 🔴 کد جستجوی قبلی...
        filtered = []
        for device in self.devices_cache:
            search_text = f"{device.get('device_type', '')} {device.get('brand', '')} {device.get('model', '')} {device.get('serial_number', '')}".lower()
            if keyword.lower() in search_text:
                filtered.append(device)
        
        self.device_list.clear()
        for device in filtered[:10]:  # حداکثر ۱۰ نتیجه
            item = QListWidgetItem()
            item.setText(f"{device.get('device_type', '')} {device.get('brand', '')} {device.get('model', '')} - سریال: {device.get('serial_number', '')}")
            item.setData(Qt.UserRole, device)
            self.device_list.addItem(item)
    
    def select_customer(self, item):
        """انتخاب مشتری از لیست"""
        self.customer_data = item.data(Qt.UserRole)
        self.display_customer_info()
    
    def select_device(self, item):
        """انتخاب دستگاه از لیست"""
        self.device_data = item.data(Qt.UserRole)
        self.display_device_info()
    
    def display_customer_info(self):
        """نمایش اطلاعات مشتری انتخاب شده"""
        if not self.customer_data:
            return
        
        self.customer_first_name.setText(self.customer_data.get('first_name', '---'))
        self.customer_last_name.setText(self.customer_data.get('last_name', '---'))
        self.customer_mobile.setText(self.customer_data.get('mobile', '---'))
        self.customer_phone.setText(self.customer_data.get('phone', '---'))
        self.customer_address.setText(self.customer_data.get('address', '---'))
        
        self.customer_info_frame.setVisible(True)
    
    def display_device_info(self):
        """نمایش اطلاعات دستگاه انتخاب شده"""
        if not self.device_data:
            return
        
        # 🔴 این خطوط را اصلاح کن:
        self.device_type_label.setText(self.device_data.get('device_type', '---'))
        self.device_brand_label.setText(self.device_data.get('brand', '---'))
        self.device_model_label.setText(self.device_data.get('model', '---'))
        self.device_serial_label.setText(self.device_data.get('serial_number', '---'))
        self.device_year_label.setText(str(self.device_data.get('production_year', '---')))
        
        warranty_status = self.device_data.get('warranty_status', 0)
        warranty_text = "دارد" if warranty_status else "ندارد"
        if warranty_status and self.device_data.get('warranty_end_date'):
            warranty_text += f" (تا {self.device_data.get('warranty_end_date')})"
        
        self.device_warranty_label.setText(warranty_text)
        
        self.device_info_frame.setVisible(True)

    
    def generate_reception_number(self):
        """تولید شماره پذیرش خودکار"""
        try:
            # استفاده از مدل Reception برای تولید شماره
            reception_number = self.data_manager.reception.generate_reception_number()
            self.reception_number_label.setText(f"شماره پذیرش: {reception_number}")
            return reception_number
        except Exception as e:
            print(f"خطا در تولید شماره پذیرش: {e}")
            # تولید دستی شماره
            today = datetime.now()
            reception_number = f"REC-{today.year}{today.month:02d}{today.day:02d}-001"
            self.reception_number_label.setText(f"شماره پذیرش: {reception_number}")
            return reception_number
    
    def perform_search(self):
        """انجام جستجوی پذیرش‌ها"""
        try:
            # دریافت فیلترهای جستجو
            filters = {}
            
            reception_number = self.search_reception_number.text().strip()
            if reception_number:
                filters['reception_number'] = reception_number
            
            customer_name = self.search_customer_name.text().strip()
            if customer_name:
                filters['customer_name'] = customer_name
            
            mobile = self.search_mobile.text().strip()
            if mobile:
                filters['mobile'] = mobile
            
            status = self.search_status.currentText()
            if status != "همه":
                filters['status'] = status
            
            # درخواست از دیتابیس
            receptions = self.data_manager.reception.get_all_receptions()
            
            # اعمال فیلترها
            filtered_receptions = []
            for reception in receptions:
                match = True
                
                if 'reception_number' in filters:
                    if filters['reception_number'] not in reception.get('reception_number', ''):
                        match = False
                
                if 'customer_name' in filters and match:
                    customer_full = reception.get('customer_name', '')
                    if filters['customer_name'].lower() not in customer_full.lower():
                        match = False
                
                if 'mobile' in filters and match:
                    # نیاز به JOIN با جدول Persons دارد
                    pass  # فعلاً نادیده بگیر
                
                if 'status' in filters and match:
                    if filters['status'] != reception.get('status', ''):
                        match = False
                
                if match:
                    filtered_receptions.append(reception)
            
            # نمایش نتایج
            self.display_search_results(filtered_receptions[:50])  # حداکثر 50 نتیجه
            
        except Exception as e:
            print(f"خطا در جستجو: {e}")
            QMessageBox.warning(self, "خطا", f"خطا در انجام جستجو: {str(e)}")
    
    def display_search_results(self, receptions):
        """نمایش نتایج جستجو در جدول"""
        self.search_table.setRowCount(len(receptions))
        
        for row, reception in enumerate(receptions):
            # ستون انتخاب
            select_btn = QPushButton("انتخاب")
            select_btn.setStyleSheet(self.get_button_style("#3498db"))
            select_btn.clicked.connect(lambda checked, r=reception: self.load_reception(r))
            self.search_table.setCellWidget(row, 0, select_btn)
            
            # اطلاعات پذیرش
            self.search_table.setItem(row, 1, QTableWidgetItem(reception.get('reception_number', '')))
            self.search_table.setItem(row, 2, QTableWidgetItem(reception.get('customer_name', '')))
            self.search_table.setItem(row, 3, QTableWidgetItem(f"{reception.get('device_type', '')} {reception.get('brand', '')}"))
            
            # تبدیل تاریخ میلادی به شمسی
            reception_date = reception.get('reception_date', '')
            if reception_date:
                try:
                    # فرض می‌کنیم تاریخ در فرمت YYYY-MM-DD است
                    if isinstance(reception_date, str):
                        year, month, day = map(int, reception_date.split('-')[:3])
                        jalali_date = jdatetime.date.fromgregorian(year=year, month=month, day=day)
                        date_str = jalali_date.strftime('%Y/%m/%d')
                        self.search_table.setItem(row, 4, QTableWidgetItem(date_str))
                except:
                    self.search_table.setItem(row, 4, QTableWidgetItem(str(reception_date)))
            else:
                self.search_table.setItem(row, 4, QTableWidgetItem(''))
            
            # هزینه تخمینی
            estimated_cost = reception.get('estimated_cost', 0)
            self.search_table.setItem(row, 5, QTableWidgetItem(f"{estimated_cost:,} تومان"))
            
            # اولویت
            self.search_table.setItem(row, 6, QTableWidgetItem(reception.get('priority', '')))
            
            # وضعیت با رنگ‌بندی
            status_item = QTableWidgetItem(reception.get('status', ''))
            status = reception.get('status', '')
            if status == 'تعمیر شده':
                status_item.setForeground(QColor('#27ae60'))
            elif status == 'در حال تعمیر':
                status_item.setForeground(QColor('#3498db'))
            elif status == 'در انتظار':
                status_item.setForeground(QColor('#f39c12'))
            elif status == 'تحویل داده شده':
                status_item.setForeground(QColor('#9b59b6'))
            elif status == 'لغو شده':
                status_item.setForeground(QColor('#e74c3c'))
            
            self.search_table.setItem(row, 7, status_item)
            
            # دکمه عملیات
            action_btn = QPushButton("مشاهده")
            action_btn.setStyleSheet(self.get_button_style("#95a5a6"))
            action_btn.clicked.connect(lambda checked, r=reception: self.view_reception_details(r))
            self.search_table.setCellWidget(row, 8, action_btn)
    
    def clear_search(self):
        """پاک کردن فیلدهای جستجو"""
        self.search_reception_number.clear()
        self.search_customer_name.clear()
        self.search_mobile.clear()
        self.search_status.setCurrentIndex(0)
        self.search_table.setRowCount(0)
    
    def add_accessory(self):
        """افزودن قطعه همراه به جدول"""
        name = self.accessory_name.text().strip()
        quantity = self.accessory_quantity.value()
        
        if not name:
            QMessageBox.warning(self, "خطا", "لطفا نام قطعه را وارد کنید.")
            return
        
        row = self.accessories_table.rowCount()
        self.accessories_table.insertRow(row)
        
        # نام قطعه
        self.accessories_table.setItem(row, 0, QTableWidgetItem(name))
        
        # تعداد
        self.accessories_table.setItem(row, 1, QTableWidgetItem(str(quantity)))
        
        # دکمه حذف
        delete_btn = QPushButton("🗑️ حذف")
        delete_btn.setStyleSheet(self.get_button_style("#e74c3c"))
        delete_btn.clicked.connect(lambda: self.remove_accessory(row))
        self.accessories_table.setCellWidget(row, 2, delete_btn)
        
        # پاک کردن فیلدها
        self.accessory_name.clear()
        self.accessory_quantity.setValue(1)
    
    def remove_accessory(self, row):
        """حذف قطعه از جدول"""
        self.accessories_table.removeRow(row)
        
        # به‌روزرسانی ردیف‌های باقی مانده
        for i in range(row, self.accessories_table.rowCount()):
            delete_btn = QPushButton("🗑️ حذف")
            delete_btn.setStyleSheet(self.get_button_style("#e74c3c"))
            delete_btn.clicked.connect(lambda checked, r=i: self.remove_accessory(r))
            self.accessories_table.setCellWidget(i, 2, delete_btn)
    
    def load_recent_receptions(self):
        """بارگذاری پذیرش‌های اخیر"""
        try:
            receptions = self.data_manager.reception.get_all_receptions()
            # نمایش 10 مورد آخر
            recent = receptions[:10] if len(receptions) > 10 else receptions
            # می‌توانید این لیست را در یک ویجت دیگر نمایش دهید
        except Exception as e:
            print(f"خطا در بارگذاری پذیرش‌های اخیر: {e}")
    
    def load_stats(self):
        """بارگذاری آمار پذیرش"""
        try:
            all_receptions = self.data_manager.reception.get_all_receptions()
            
            # آمار کلی
            total = len(all_receptions)
            self.total_receptions_label.setText(str(total))
            
            # پذیرش‌های امروز
            today = datetime.now().date()
            today_str = today.strftime('%Y-%m-%d')
            today_count = sum(1 for r in all_receptions 
                            if str(r.get('reception_date', '')).startswith(today_str))
            self.today_receptions_label.setText(str(today_count))
            
            # در حال تعمیر
            repairing = sum(1 for r in all_receptions 
                          if r.get('status') == 'در حال تعمیر')
            self.repairing_label.setText(str(repairing))
            
            # تعمیر شده
            repaired = sum(1 for r in all_receptions 
                         if r.get('status') == 'تعمیر شده')
            self.repaired_label.setText(str(repaired))
            
        except Exception as e:
            print(f"خطا در بارگذاری آمار: {e}")
    
    # ========== عملیات فرم ==========
    
    def open_repair_form(self):
        """باز کردن فرم تعمیرات برای پذیرش جاری"""
        if not self.current_reception_id:
            QMessageBox.warning(self, "خطا", "لطفا ابتدا یک پذیرش را انتخاب کنید.")
            return
        
        # دریافت اطلاعات پذیرش فعلی
        reception = self.data_manager.reception.get_reception_by_id(self.current_reception_id)
        if not reception:
            QMessageBox.warning(self, "خطا", "پذیرش انتخاب شده یافت نشد.")
            return
        
        # بررسی وضعیت پذیرش
        status = reception.get('status', 'در انتظار')
        if status not in ['در انتظار', 'در حال تعمیر']:
            reply = QMessageBox.question(
                self, "تایید",
                f"این پذیرش در وضعیت '{status}' است. آیا می‌خواهید تعمیر جدید ثبت کنید؟",
                QMessageBox.Yes | QMessageBox.No
            )
            if reply == QMessageBox.No:
                return
        
        # باز کردن فرم تعمیرات
        try:
            from ui.forms.repair_form import RepairForm
            self.repair_form = RepairForm(self.data_manager, self.current_reception_id)
            self.repair_form.repair_saved.connect(self.on_repair_saved)
            self.repair_form.show()
        except Exception as e:
            QMessageBox.critical(self, "خطا", f"خطا در باز کردن فرم تعمیرات: {str(e)}")

    def on_repair_saved(self, repair_data):
        """هنگام ذخیره تعمیر"""
        # تازه‌سازی داده‌های فرم پذیرش
        self.refresh_data()
        QMessageBox.information(self, "موفق", "تعمیر ثبت شد. وضعیت پذیرش به‌روزرسانی می‌شود.")

    # در تابع load_reception_data (یا هر جایی که پذیرش بارگذاری می‌شود):
    def load_reception_data(self, reception_id):
        """بارگذاری اطلاعات پذیرش"""
        self.current_reception_id = reception_id
        
        # فعال/غیرفعال کردن دکمه تعمیر
        if reception_id:
            self.btn_to_repair.setEnabled(True)
        else:
            self.btn_to_repair.setEnabled(False)


    def new_reception(self):
        """ایجاد پذیرش جدید"""
        try:
            # تایید از کاربر
            reply = QMessageBox.question(
                self, "پذیرش جدید",
                "آیا می‌خواهید پذیرش جدید ایجاد کنید؟\nداده‌های فعلی ذخیره نخواهند شد.",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                # پاک کردن فرم
                self.reset_form()
                
                # تولید شماره پذیرش جدید
                self.generate_reception_number()
                
                # رفتن به تب اول
                self.tabs.setCurrentIndex(0)
                
                QMessageBox.information(self, "عملیات موفق", "فرم برای پذیرش جدید آماده است.")
        except Exception as e:
            QMessageBox.critical(self, "خطا", f"خطا در ایجاد پذیرش جدید: {str(e)}")
    
    def save_reception(self):
        """ذخیره پذیرش"""
        try:
            # اعتبارسنجی داده‌ها
            if not self.validate_form():
                return
            
            # جمع‌آوری داده‌ها
            reception_data = self.collect_reception_data()
            
            # ذخیره در دیتابیس
            if self.current_reception_id:
                # ویرایش پذیرش موجود
                success = self.data_manager.reception.update_reception(
                    self.current_reception_id, reception_data)
                message = "ویرایش"
            else:
                # ثبت پذیرش جدید
                reception_number = self.data_manager.reception.add_reception(reception_data)
                if reception_number:
                    success = True
                    message = "ثبت"
                    # ذخیره شماره پذیرش
                    reception_data['reception_number'] = reception_number
                else:
                    success = False
            
            if success:
                # ارسال سیگنال
                self.reception_saved.emit(reception_data)
                
                # نمایش پیام موفقیت
                QMessageBox.information(self, "عملیات موفق", 
                    f"پذیرش با موفقیت {message} شد.\nشماره پذیرش: {reception_data.get('reception_number', '')}")
                
                # تازه‌سازی لیست جستجو
                self.perform_search()
                
                # رفتن به تب جستجو
                self.tabs.setCurrentIndex(0)
            else:
                QMessageBox.critical(self, "خطا", f"خطا در {message} پذیرش.")
                
        except Exception as e:
            QMessageBox.critical(self, "خطا", f"خطا در ذخیره پذیرش: {str(e)}")
    
    def validate_form(self):
        """اعتبارسنجی داده‌های فرم"""
        # بررسی مشتری
        if not self.customer_data:
            QMessageBox.warning(self, "خطا", "لطفا یک مشتری انتخاب کنید.")
            self.tabs.setCurrentIndex(1)  # رفتن به تب مشتری
            return False
        
        # بررسی دستگاه
        if not self.device_data:
            QMessageBox.warning(self, "خطا", "لطفا یک دستگاه انتخاب کنید.")
            self.tabs.setCurrentIndex(2)  # رفتن به تب دستگاه
            return False
        
        # بررسی شرح خرابی
        if not self.problem_description.toPlainText().strip():
            QMessageBox.warning(self, "خطا", "لطفا شرح خرابی دستگاه را وارد کنید.")
            self.tabs.setCurrentIndex(3)  # رفتن به تب پذیرش
            self.problem_description.setFocus()
            return False
        
        # بررسی تاریخ پذیرش
        if not self.reception_date.get_date():
            QMessageBox.warning(self, "خطا", "لطفا تاریخ پذیرش را وارد کنید.")
            self.tabs.setCurrentIndex(3)
            self.reception_date.setFocus()
            return False
        
        return True
    
    def collect_reception_data(self):
        """جمع‌آوری داده‌های فرم"""
        # قطعات همراه
        accessories = []
        for row in range(self.accessories_table.rowCount()):
            name = self.accessories_table.item(row, 0).text()
            quantity = self.accessories_table.item(row, 1).text()
            accessories.append(f"{quantity} x {name}")
        
        # جمع‌آوری داده‌ها
        data = {
            # اطلاعات مشتری و دستگاه
            'customer_id': self.customer_data.get('id'),
            'device_id': self.device_data.get('id'),
            
            # اطلاعات پذیرش
            'reception_date': self.reception_date.get_gregorian_date(),
            'reception_time': self.reception_time.text(),
            'problem_description': self.problem_description.toPlainText(),
            'device_condition': self.device_condition.toPlainText(),
            'accessories': '\n'.join(accessories),
            'estimated_cost': self.estimated_cost.value(),
            'estimated_delivery_date': self.estimated_delivery_date.get_gregorian_date(),
            'priority': self.priority.currentText(),
            'status': self.status.currentText(),
            'reception_employee': self.reception_employee.text(),
            'notes': self.notes.toPlainText(),
            'customer_reminder': self.customer_reminder.toPlainText(),
        }
        
        return data
    
    def load_reception(self, reception_data):
        """بارگذاری یک پذیرش برای ویرایش"""
        try:
            # ذخیره شناسه
            self.current_reception_id = reception_data.get('id')
            
            # بارگذاری کامل پذیرش
            full_reception = self.data_manager.reception.get_reception_by_id(self.current_reception_id)
            if not full_reception:
                QMessageBox.warning(self, "خطا", "پذیرش مورد نظر یافت نشد.")
                return
            
            # بارگذاری مشتری
            customer_id = full_reception.get('customer_id')
            if customer_id:
                self.customer_data = self.data_manager.person.get_person_by_id(customer_id)
                self.display_customer_info()
            
            # بارگذاری دستگاه
            device_id = full_reception.get('device_id')
            if device_id:
                self.device_data = self.data_manager.device.get_device_by_id(device_id)
                self.display_device_info()
            
            # پر کردن فیلدهای پذیرش
            self.reception_date.set_gregorian_date(full_reception.get('reception_date'))
            self.reception_time.setText(full_reception.get('reception_time', ''))
            self.problem_description.setText(full_reception.get('problem_description', ''))
            self.device_condition.setText(full_reception.get('device_condition', ''))
            self.estimated_cost.setValue(float(full_reception.get('estimated_cost', 0)))
            self.estimated_delivery_date.set_gregorian_date(full_reception.get('estimated_delivery_date'))
            self.priority.setCurrentText(full_reception.get('priority', 'عادی'))
            self.status.setCurrentText(full_reception.get('status', 'در انتظار'))
            self.reception_employee.setText(full_reception.get('reception_employee', ''))
            self.notes.setText(full_reception.get('notes', ''))
            
            # بارگذاری قطعات همراه
            accessories_text = full_reception.get('accessories', '')
            if accessories_text:
                self.load_accessories_from_text(accessories_text)
            
            # نمایش شماره پذیرش
            reception_number = full_reception.get('reception_number', '')
            self.reception_number_label.setText(f"شماره پذیرش: {reception_number} (ویرایش)")
            
            # رفتن به تب پذیرش
            self.tabs.setCurrentIndex(3)
            
            QMessageBox.information(self, "بارگذاری موفق", 
                f"پذیرش شماره {reception_number} برای ویرایش بارگذاری شد.")
            
        except Exception as e:
            QMessageBox.critical(self, "خطا", f"خطا در بارگذاری پذیرش: {str(e)}")
    
    def load_accessories_from_text(self, accessories_text):
        """بارگذاری قطعات همراه از متن"""
        self.accessories_table.setRowCount(0)
        
        lines = accessories_text.split('\n')
        for line in lines:
            if ' x ' in line:
                parts = line.split(' x ', 1)
                if len(parts) == 2:
                    quantity, name = parts
                    
                    row = self.accessories_table.rowCount()
                    self.accessories_table.insertRow(row)
                    
                    self.accessories_table.setItem(row, 0, QTableWidgetItem(name.strip()))
                    self.accessories_table.setItem(row, 1, QTableWidgetItem(quantity.strip()))
                    
                    delete_btn = QPushButton("🗑️ حذف")
                    delete_btn.setStyleSheet(self.get_button_style("#e74c3c"))
                    delete_btn.clicked.connect(lambda checked, r=row: self.remove_accessory(r))
                    self.accessories_table.setCellWidget(row, 2, delete_btn)
    
    def view_reception_details(self, reception_data):
        """مشاهده جزئیات پذیرش (فقط نمایش)"""
        try:
            from PySide6.QtWidgets import QDialog, QVBoxLayout, QTextEdit, QPushButton
            
            dialog = QDialog(self)
            dialog.setWindowTitle(f"جزئیات پذیرش - {reception_data.get('reception_number', '')}")
            dialog.setMinimumSize(600, 500)
            
            layout = QVBoxLayout()
            
            # نمایش اطلاعات
            details_text = f"""
            📋 <b>جزئیات پذیرش</b>
            {'='*50}
            
            🔢 <b>شماره پذیرش:</b> {reception_data.get('reception_number', '')}
            👥 <b>مشتری:</b> {reception_data.get('customer_name', '')}
            📱 <b>دستگاه:</b> {reception_data.get('device_type', '')} {reception_data.get('brand', '')} {reception_data.get('model', '')}
            📅 <b>تاریخ پذیرش:</b> {reception_data.get('reception_date', '')}
            ⚠️ <b>اولویت:</b> {reception_data.get('priority', '')}
            📊 <b>وضعیت:</b> {reception_data.get('status', '')}
            💰 <b>هزینه تخمینی:</b> {reception_data.get('estimated_cost', 0):,} تومان
            
            🔧 <b>شرح خرابی:</b>
            {reception_data.get('problem_description', '')}
            """
            
            text_edit = QTextEdit()
            text_edit.setHtml(details_text)
            text_edit.setReadOnly(True)
            layout.addWidget(text_edit)
            
            # دکمه بستن
            btn_close = QPushButton("بستن")
            btn_close.setStyleSheet(self.get_button_style("#e74c3c"))
            btn_close.clicked.connect(dialog.close)
            layout.addWidget(btn_close)
            
            dialog.setLayout(layout)
            dialog.exec()
            
        except Exception as e:
            QMessageBox.warning(self, "خطا", f"خطا در نمایش جزئیات: {str(e)}")
    
    def print_reception(self):
        """چاپ فرم پذیرش"""
        QMessageBox.information(self, "چاپ", "امکان چاپ فرم پذیرش فراهم خواهد شد.")
        # TODO: پیاده‌سازی چاپ فرم
    
    def reset_form(self):
        """بازنشانی فرم به حالت اولیه"""
        # پاک کردن داده‌ها
        self.current_reception_id = None
        self.customer_data = None
        self.device_data = None
        
        # پاک کردن فیلدهای مشتری
        self.customer_first_name.setText("---")
        self.customer_last_name.setText("---")
        self.customer_mobile.setText("---")
        self.customer_phone.setText("---")
        self.customer_address.setText("---")
        self.customer_info_frame.setVisible(False)
        self.customer_search.clear()
        self.customer_list.clear()
        
        # پاک کردن فیلدهای دستگاه
        self.device_type.setText("---")
        self.device_brand.setText("---")
        self.device_model.setText("---")
        self.device_serial.setText("---")
        self.device_year.setText("---")
        self.device_warranty.setText("---")
        self.device_info_frame.setVisible(False)
        self.device_search.clear()
        self.device_list.clear()
        
        # پاک کردن فیلدهای پذیرش
        self.reception_date.clear()
        self.reception_time.setText(QDateTime.currentDateTime().toString("HH:mm"))
        self.priority.setCurrentIndex(0)
        self.status.setCurrentIndex(0)
        self.estimated_cost.setValue(0)
        self.estimated_delivery_date.clear()
        self.reception_employee.setText("سیستم")
        self.problem_description.clear()
        self.device_condition.clear()
        self.notes.clear()
        
        # پاک کردن قطعات همراه
        self.accessories_table.setRowCount(0)
        self.accessory_name.clear()
        self.accessory_quantity.setValue(1)
        self.customer_reminder.clear()
        
        # تولید شماره پذیرش جدید
        self.generate_reception_number()
    
    def open_new_customer_form(self):
        """باز کردن فرم ثبت مشتری جدید"""
        try:
            # ایمپورت فرم اشخاص
            from ui.forms.person_form import PersonForm
            
            self.customer_form = PersonForm(self.data_manager, person_id=None)
            self.customer_form.setWindowTitle("ثبت مشتری جدید")
            self.customer_form.setMinimumSize(1000, 700)
            
            # تنظیم نوع شخص به مشتری
            if hasattr(self.customer_form, 'person_type_combo'):
                self.customer_form.person_type_combo.setCurrentText("مشتری")
            
            # موقعیت فرم
            main_geometry = self.geometry()
            self.customer_form.move(main_geometry.x() + 50, main_geometry.y() + 50)
            
            # اتصال سیگنال ذخیره
            self.customer_form.person_saved.connect(self.on_customer_saved)
            
            self.customer_form.show()
            
        except Exception as e:
            QMessageBox.critical(self, "خطا", f"خطا در باز کردن فرم مشتری: {str(e)}")
    
    def open_new_device_form(self):
        """باز کردن فرم ثبت دستگاه جدید"""
        QMessageBox.information(self, "ثبت دستگاه جدید", 
            "فرم ثبت دستگاه جدید در نسخه‌های بعدی اضافه خواهد شد.")
        # TODO: ایجاد فرم دستگاه‌ها
    
    def on_customer_saved(self, person_data):
        """هنگام ذخیره مشتری جدید"""
        # تازه‌سازی لیست مشتریان
        self.load_customers()
        
        # انتخاب مشتری جدید
        for customer in self.customers_cache:
            if customer.get('id') == person_data.get('id'):
                self.customer_data = customer
                self.display_customer_info()
                break
        
        # نمایش پیام
        QMessageBox.information(self, "عملیات موفق", 
            f"مشتری '{person_data.get('first_name', '')} {person_data.get('last_name', '')}' با موفقیت ثبت شد.")
    
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
        # بررسی ساده: اگر داده‌ای وارد شده باشد
        if (self.customer_data or self.device_data or 
            self.problem_description.toPlainText().strip()):
            return True
        return False
    
    # ========== توابع جدید برای مدیریت دستگاه ==========
    
    def open_new_device_form(self):
        """باز کردن فرم ثبت دستگاه جدید از داخل فرم پذیرش"""
        try:
            from ui.forms.device_form import DeviceForm
            
            # ایجاد فرم دستگاه جدید
            self.device_form = DeviceForm(self.data_manager, device_id=None)
            self.device_form.setWindowTitle("ثبت دستگاه جدید از فرم پذیرش")
            self.device_form.setMinimumSize(1000, 700)
            
            # موقعیت فرم نسبت به فرم پذیرش
            reception_geometry = self.geometry()
            self.device_form.move(reception_geometry.x() + 50, reception_geometry.y() + 50)
            
            # اتصال سیگنال ذخیره دستگاه
            self.device_form.device_saved.connect(self.on_device_saved_in_reception)
            self.device_form.form_closed.connect(self.on_device_form_closed)
            
            # نمایش فرم
            self.device_form.show()
            
        except Exception as e:
            QMessageBox.critical(self, "خطا", f"خطا در باز کردن فرم دستگاه: {str(e)}")
    
    def on_device_saved_in_reception(self, device_data):
        """هنگام ذخیره دستگاه جدید از داخل پذیرش"""
        try:
            # 🔴 دستگاه جدید را به لیست اضافه کن
            self.load_devices()
            
            # 🔴 دستگاه جدید را پیدا کن (از آخرین دستگاه‌ها)
            if self.devices_cache:
                # فرض می‌کنیم آخرین دستگاه همان دستگاه جدید است
                new_device = self.devices_cache[-1]
                
                # یا جستجو بر اساس اطلاعات
                for device in self.devices_cache:
                    if (device.get('brand') == device_data.get('brand') and 
                        device.get('model') == device_data.get('model') and
                        device.get('serial_number') == device_data.get('serial_number')):
                        new_device = device
                        break
                
                # دستگاه جدید را انتخاب کن
                self.device_data = new_device
                self.display_device_info()
                
                # به‌روزرسانی لیست جستجو
                self.search_devices("")
                
                # نمایش پیام
                QMessageBox.information(
                    self, 
                    "ثبت موفق", 
                    f"دستگاه {device_data.get('brand', '')} {device_data.get('model', '')} با موفقیت ثبت و انتخاب شد."
                )
            else:
                QMessageBox.warning(self, "خطا", "دستگاه ثبت شده یافت نشد!")
                
        except Exception as e:
            print(f"خطا در پردازش دستگاه جدید: {e}")
            QMessageBox.critical(self, "خطا", f"خطا در پردازش دستگاه جدید: {str(e)}")
    
    def on_device_form_closed(self):
        """هنگام بسته شدن فرم دستگاه"""
        print("فرم دستگاه بسته شد")
        # اگر فرم دستگاه باز بود، آن را None کن
        self.device_form = None
        
    def select_new_device(self, device_data):
        """انتخاب دستگاه جدید از لیست"""
        # این تابع ممکن است در آینده استفاده شود
        # فعلاً همان on_device_saved_in_reception کار را انجام می‌دهد
        pass

    def closeEvent(self, event):
        """مدیریت بسته شدن فرم"""
        self.close_form()
        event.ignore()  # اجازه می‌دهیم close_form کنترل کند


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
    form = ReceptionForm(data_manager)
    form.show()
    
    sys.exit(app.exec())