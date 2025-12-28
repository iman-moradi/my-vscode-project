"""
فرم مدیریت تعمیرات - نسخه کاملاً بازطراحی شده
با اتصال کامل به دیتابیس اجرت‌ها و جستجوی زنده
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QComboBox, QTextEdit, QTableWidget, QCompleter,
    QTableWidgetItem, QTabWidget, QFrame, QGroupBox, QMessageBox,
    QHeaderView, QSpinBox, QCheckBox, QFormLayout, QDoubleSpinBox,
    QScrollArea, QAbstractSpinBox, QGridLayout, QDateEdit, QTimeEdit,
    QListWidget, QListWidgetItem, QDialog, QApplication
)
from PySide6.QtCore import Qt, Signal, QTimer, QDate, QTime, QStringListModel
from PySide6.QtGui import QFont, QColor, QIcon
import jdatetime
from datetime import datetime
import sys
import os
import re
import json 


# افزودن مسیر پروژه
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
sys.path.insert(0, project_root)

from ui.widgets.jalali_date_input import JalaliDateInput
from ui.dialogs.smart_search_dialog import SmartSearchDialog

class CustomComboBox(QComboBox):
    """کامبوباکس سفارشی برای جلوگیری از تغییر ناخواسته متن"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._user_text = ""
        self._is_typing = False
        
    def focusOutEvent(self, event):
        """هنگام از دست دادن فوکوس، متن را حفظ کن"""
        if self._is_typing:
            self.setCurrentText(self._user_text)
            self._is_typing = False
        super().focusOutEvent(event)
    
    def keyPressEvent(self, event):
        """ردیابی تایپ کاربر"""
        if event.key() in [Qt.Key_Return, Qt.Key_Enter]:
            self._is_typing = False
        else:
            self._is_typing = True
            self._user_text = self.currentText()
        super().keyPressEvent(event)


class RepairForm(QWidget):
    """
    فرم مدیریت تعمیرات - نسخه بازطراحی شده
    با اتصال کامل به دیتابیس اجرت‌ها
    """
    
    # سیگنال‌ها
    repair_saved = Signal(dict)
    form_closed = Signal()
    
    def __init__(self, data_manager, reception_id=None):
        super().__init__()
        self.data_manager = data_manager
        self.reception_id = reception_id
        self.current_repair_id = None
        self.selected_customer = None
        self.selected_device = None
        
        # کش داده‌ها
        self.receptions_cache = []
        self.technicians_cache = []
        self.parts_cache = []
        self.all_services = []
        self.all_categories = []
        
        # جدول خدمات اضافه شده
        self.services_added = []  # لیست خدمات اضافه شده به این تعمیر
        
        self.init_ui()
        self.load_initial_data()
        
        if self.reception_id:
            QTimer.singleShot(100, self.load_reception_data)
    
    def init_ui(self):
        """راه‌اندازی رابط کاربری"""
        self.setWindowTitle("🔧 مدیریت تعمیرات - سیستم تعمیرگاه شیروین")
        self.setMinimumSize(1400, 900)
        self.setLayoutDirection(Qt.RightToLeft)
        
        # استایل
        self.setStyleSheet(self.get_style_sheet())
        self.set_font()
        
        # لایه اصلی
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)
        
        # نوار عنوان
        title_frame = self.create_title_frame()
        main_layout.addWidget(title_frame)
        
        # ایجاد ویجت تب‌ها
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet(self.get_tab_style_sheet())
        self.tabs.setMinimumHeight(700)
        
        # ایجاد تب‌ها
        self.create_basic_info_tab()
        self.create_parts_tab()
        self.create_costs_tab()
        
        main_layout.addWidget(self.tabs)
        
        # نوار دکمه‌ها
        button_frame = self.create_button_frame()
        main_layout.addWidget(button_frame)
        
        self.setLayout(main_layout)
        
    def create_title_frame(self):
        """ایجاد نوار عنوان"""
        frame = QFrame()
        frame.setStyleSheet("""
            QFrame {
                background-color: #2c3e50;
                border-radius: 8px;
                padding: 10px;
            }
        """)
        
        layout = QHBoxLayout()
        
        title_label = QLabel("🔧 مدیریت تعمیرات")
        title_label.setStyleSheet("""
            QLabel {
                font-size: 18px;
                font-weight: bold;
                color: white;
            }
        """)
        layout.addWidget(title_label)
        layout.addStretch()
        
        # وضعیت
        self.repair_status_label = QLabel("تعمیر جدید")
        self.repair_status_label.setStyleSheet("""
            QLabel {
                font-size: 14px;
                font-weight: bold;
                color: #f39c12;
                background-color: #34495e;
                padding: 5px 10px;
                border-radius: 5px;
            }
        """)
        layout.addWidget(self.repair_status_label)
        
        frame.setLayout(layout)
        return frame
    
    def create_button_frame(self):
        """ایجاد نوار دکمه‌ها"""
        frame = QFrame()
        layout = QHBoxLayout()
        
        # دکمه‌های اصلی
        self.btn_new = QPushButton("🆕 جدید")
        self.btn_new.setStyleSheet(self.get_button_style("#27ae60"))
        self.btn_new.clicked.connect(self.new_repair)
        
        self.btn_save = QPushButton("💾 ذخیره تعمیر")
        self.btn_save.setStyleSheet(self.get_button_style("#3498db"))
        self.btn_save.clicked.connect(self.save_repair)
        
        self.btn_finish = QPushButton("✅ تکمیل تعمیر")
        self.btn_finish.setStyleSheet(self.get_button_style("#9b59b6"))
        self.btn_finish.clicked.connect(self.finish_repair)
        
        self.btn_cancel = QPushButton("❌ انصراف")
        self.btn_cancel.setStyleSheet(self.get_button_style("#95a5a6"))
        self.btn_cancel.clicked.connect(self.close_form)
        
        layout.addWidget(self.btn_new)
        layout.addWidget(self.btn_save)
        layout.addWidget(self.btn_finish)
        layout.addStretch()
        layout.addWidget(self.btn_cancel)
        
        frame.setLayout(layout)
        return frame
    
    # ========== تب 1: اطلاعات پایه ==========

    def create_basic_info_tab(self):
        """ایجاد تب اطلاعات پایه"""
        tab = QWidget()
        
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("""
            QScrollArea {
                background-color: transparent;
                border: none;
            }
            QScrollBar:vertical {
                background-color: #2c2c2c;
                width: 12px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical {
                background-color: #3498db;
                border-radius: 6px;
                min-height: 30px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #2980b9;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                border: none;
                background: none;
            }
        """)
        
        content_widget = QWidget()
        layout = QVBoxLayout(content_widget)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(15)
        
        # ==================== بخش ۱: جستجوی هوشمند ====================
        search_group = QGroupBox("🔍 جستجوی هوشمند مشتری و دستگاه")
        search_group.setStyleSheet(self.get_groupbox_style("#3498db"))
        search_layout = QGridLayout()
        search_layout.setSpacing(12)
        
        # ردیف ۱: دکمه جستجو
        self.btn_smart_search = QPushButton("🔍 جستجوی هوشمند با موبایل")
        self.btn_smart_search.setStyleSheet(self.get_button_style("#9b59b6"))
        self.btn_smart_search.clicked.connect(self.open_smart_search)
        self.btn_smart_search.setMinimumHeight(45)
        search_layout.addWidget(self.btn_smart_search, 0, 0, 1, 4)
        
        # ردیف ۲: جداکننده
        separator1 = QFrame()
        separator1.setFrameShape(QFrame.HLine)
        separator1.setFrameShadow(QFrame.Sunken)
        separator1.setStyleSheet("background-color: #444; margin: 10px 0; height: 2px;")
        search_layout.addWidget(separator1, 1, 0, 1, 4)
        
        # ردیف ۳: اطلاعات مشتری
        search_layout.addWidget(QLabel("👤 مشتری انتخاب شده:"), 2, 0)
        self.customer_info_label = QLabel("--")
        self.customer_info_label.setStyleSheet("""
            QLabel {
                color: #3498db;
                font-weight: bold;
                background-color: #2c2c2c;
                padding: 12px;
                border-radius: 6px;
                border: 2px solid #3498db;
                min-height: 50px;
            }
        """)
        search_layout.addWidget(self.customer_info_label, 2, 1, 1, 3)
        
        # ردیف ۴: موبایل
        search_layout.addWidget(QLabel("📱 موبایل:"), 3, 0)
        self.customer_mobile_label = QLabel("--")
        self.customer_mobile_label.setStyleSheet("""
            QLabel {
                color: #e74c3c;
                font-weight: bold;
                background-color: #2c2c2c;
                padding: 12px;
                border-radius: 6px;
                border: 2px solid #e74c3c;
            }
        """)
        search_layout.addWidget(self.customer_mobile_label, 3, 1)
        
        # ردیف ۵: دستگاه
        search_layout.addWidget(QLabel("📺 دستگاه:"), 3, 2)
        self.device_info_label = QLabel("--")
        self.device_info_label.setStyleSheet("""
            QLabel {
                color: #2ecc71;
                font-weight: bold;
                background-color: #2c2c2c;
                padding: 12px;
                border-radius: 6px;
                border: 2px solid #2ecc71;
            }
        """)
        search_layout.addWidget(self.device_info_label, 3, 3)
        
        # ردیف ۶: سریال
        search_layout.addWidget(QLabel("🔢 شماره سریال:"), 4, 0)
        self.device_serial_label = QLabel("--")
        self.device_serial_label.setStyleSheet("""
            QLabel {
                color: #f39c12;
                font-weight: bold;
                background-color: #2c2c2c;
                padding: 12px;
                border-radius: 6px;
                border: 2px solid #f39c12;
            }
        """)
        search_layout.addWidget(self.device_serial_label, 4, 1, 1, 3)
        
        search_group.setLayout(search_layout)
        layout.addWidget(search_group)
        
        # ==================== بخش ۲: اطلاعات پذیرش ====================
        self.reception_group = QGroupBox("📋 اطلاعات پذیرش")
        self.reception_group.setStyleSheet(self.get_groupbox_style("#9b59b6"))
        self.reception_group.setVisible(False)
        reception_layout = QGridLayout()
        reception_layout.setSpacing(12)
        
        # ردیف ۱: شماره پذیرش
        reception_layout.addWidget(QLabel("🔢 شماره پذیرش:"), 0, 0)
        self.reception_number_label = QLabel("--")
        self.reception_number_label.setStyleSheet("font-weight: bold; color: #3498db;")
        reception_layout.addWidget(self.reception_number_label, 0, 1)
        
        # ردیف ۱: تاریخ پذیرش
        reception_layout.addWidget(QLabel("📅 تاریخ پذیرش:"), 0, 2)
        self.reception_date_label = QLabel("--")
        self.reception_date_label.setStyleSheet("font-weight: bold; color: #f39c12;")
        reception_layout.addWidget(self.reception_date_label, 0, 3)
        
        # ردیف ۲: وضعیت
        reception_layout.addWidget(QLabel("📊 وضعیت:"), 1, 0)
        self.reception_status_label = QLabel("--")
        self.reception_status_label.setStyleSheet("""
            QLabel {
                font-weight: bold;
                padding: 8px 16px;
                border-radius: 5px;
            }
        """)
        reception_layout.addWidget(self.reception_status_label, 1, 1)
        
        # ردیف ۲: هزینه تخمینی
        reception_layout.addWidget(QLabel("💰 هزینه تخمینی:"), 1, 2)
        self.estimated_cost_label = QLabel("--")
        self.estimated_cost_label.setStyleSheet("color: #f39c12; font-weight: bold;")
        reception_layout.addWidget(self.estimated_cost_label, 1, 3)
        
        # ردیف ۳: مشکل دستگاه
        reception_layout.addWidget(QLabel("📝 مشکل گزارش شده:"), 2, 0)
        self.problem_description_text = QTextEdit()
        self.problem_description_text.setMaximumHeight(100)
        self.problem_description_text.setReadOnly(True)
        self.problem_description_text.setStyleSheet("""
            QTextEdit {
                background-color: #2c2c2c;
                border: 1px solid #444;
                border-radius: 5px;
                padding: 10px;
                font-size: 13px;
            }
        """)
        reception_layout.addWidget(self.problem_description_text, 2, 1, 1, 3)
        
        self.reception_group.setLayout(reception_layout)
        layout.addWidget(self.reception_group)
        
        # ==================== بخش ۳: اطلاعات تعمیر ====================
        repair_info_group = QGroupBox("🔧 اطلاعات تعمیر")
        repair_info_group.setStyleSheet(self.get_groupbox_style("#e74c3c"))
        repair_info_layout = QGridLayout()
        repair_info_layout.setSpacing(12)
        
        # ردیف ۱: تاریخ تعمیر
        repair_info_layout.addWidget(QLabel("📅 تاریخ تعمیر:"), 0, 0)
        self.repair_date = JalaliDateInput()
        self.repair_date.set_date(jdatetime.date.today().strftime('%Y/%m/%d'))
        repair_info_layout.addWidget(self.repair_date, 0, 1)
        
        # ردیف ۱: تعمیرکار
        repair_info_layout.addWidget(QLabel("👨‍🔧 تعمیرکار:"), 0, 2)
        self.technician_combo = QComboBox()
        self.technician_combo.setEditable(False)
        self.technician_combo.setMinimumHeight(35)
        repair_info_layout.addWidget(self.technician_combo, 0, 3)
        
        # ردیف ۲: نوع تعمیر
        repair_info_layout.addWidget(QLabel("🏭 نوع تعمیر:"), 1, 0)
        self.repair_type_combo = QComboBox()
        self.repair_type_combo.addItems(["داخلی", "بیرون سپاری"])
        self.repair_type_combo.currentTextChanged.connect(self.on_repair_type_changed)
        self.repair_type_combo.setMinimumHeight(35)
        repair_info_layout.addWidget(self.repair_type_combo, 1, 1)
        
        # ردیف ۲: بیرون‌سپاری به
        repair_info_layout.addWidget(QLabel("🤝 بیرون‌سپاری به:"), 1, 2)
        self.outsourced_combo = QComboBox()
        self.outsourced_combo.setEnabled(False)
        self.outsourced_combo.setMinimumHeight(35)
        repair_info_layout.addWidget(self.outsourced_combo, 1, 3)
        
        # ردیف ۳: وضعیت تعمیر
        repair_info_layout.addWidget(QLabel("📊 وضعیت تعمیر:"), 2, 0)
        self.status_combo = QComboBox()
        self.status_combo.addItems(["شروع شده", "در حال انجام", "تمام شده", "متوقف شده"])
        self.status_combo.setMinimumHeight(35)
        repair_info_layout.addWidget(self.status_combo, 2, 1)
        
        repair_info_group.setLayout(repair_info_layout)
        layout.addWidget(repair_info_group)
        
        # ==================== بخش ۴: زمان‌بندی ====================
        time_group = QGroupBox("⏰ زمان‌بندی تعمیر")
        time_group.setStyleSheet(self.get_groupbox_style("#f39c12"))
        time_layout = QGridLayout()
        time_layout.setSpacing(12)
        
        # زمان شروع
        time_layout.addWidget(QLabel("⏱️ زمان شروع:"), 0, 0)
        self.start_time = QTimeEdit()
        self.start_time.setTime(QTime.currentTime())
        self.start_time.setDisplayFormat("HH:mm")
        self.start_time.setMinimumHeight(35)
        time_layout.addWidget(self.start_time, 0, 1)
        
        # زمان پایان
        time_layout.addWidget(QLabel("🕒 زمان پایان:"), 0, 2)
        self.end_time = QTimeEdit()
        self.end_time.setDisplayFormat("HH:mm")
        self.end_time.setMinimumHeight(35)
        time_layout.addWidget(self.end_time, 0, 3)
        
        # دکمه تنظیم زمان پایان به حال
        btn_set_end_time = QPushButton("⏱️ تنظیم زمان پایان به حال")
        btn_set_end_time.clicked.connect(lambda: self.end_time.setTime(QTime.currentTime()))
        btn_set_end_time.setStyleSheet(self.get_button_style("#7f8c8d"))
        time_layout.addWidget(btn_set_end_time, 1, 0, 1, 4)
        
        time_group.setLayout(time_layout)
        layout.addWidget(time_group)
        
        # ==================== بخش ۵: توضیحات ====================
        desc_group = QGroupBox("📝 توضیحات و نکات تعمیر")
        desc_group.setStyleSheet(self.get_groupbox_style("#27ae60"))
        desc_layout = QVBoxLayout()
        
        self.repair_description = QTextEdit()
        self.repair_description.setPlaceholderText(
            "شرح کامل تعمیر انجام شده...\n"
            "• قطعات تعویض شده\n"
            "• آزمایش‌های انجام شده\n"
            "• مشکلات خاص\n"
            "• توصیه‌ها به مشتری"
        )
        self.repair_description.setMinimumHeight(150)
        self.repair_description.setStyleSheet("""
            QTextEdit {
                background-color: #2c2c2c;
                border: 1px solid #444;
                border-radius: 5px;
                padding: 15px;
                font-size: 13px;
                line-height: 1.5;
            }
            QTextEdit:focus {
                border: 2px solid #27ae60;
            }
        """)
        desc_layout.addWidget(self.repair_description)
        
        # کاراکتر شمار
        self.char_count_label = QLabel("۰ کاراکتر")
        self.char_count_label.setAlignment(Qt.AlignLeft)
        self.char_count_label.setStyleSheet("color: #95a5a6; font-size: 11px;")
        desc_layout.addWidget(self.char_count_label)
        
        # اتصال تغییرات متن به شمارشگر
        self.repair_description.textChanged.connect(
            lambda: self.char_count_label.setText(f"{len(self.repair_description.toPlainText())} کاراکتر")
        )
        
        desc_group.setLayout(desc_layout)
        layout.addWidget(desc_group)
        
        # اسپیس‌ر در انتها
        layout.addStretch()
        
        # تنظیم ویجت محتوا برای اسکرول
        scroll_area.setWidget(content_widget)
        
        # لایه اصلی تب
        tab_layout = QVBoxLayout(tab)
        tab_layout.addWidget(scroll_area)
        
        # اضافه کردن تب به ویجت تب‌ها
        self.tabs.addTab(tab, "📋 اطلاعات پایه")
        
        return tab

    # ========== تب 2: قطعات استفاده شده ==========
    def create_parts_tab(self):
        """ایجاد تب قطعات استفاده شده"""
        tab = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(15)
        
        # گروه اضافه کردن قطعه
        add_group = QGroupBox("➕ افزودن قطعه استفاده شده")
        add_layout = QGridLayout()
        
        # انتخاب قطعه
        add_layout.addWidget(QLabel("قطعه:"), 0, 0)
        self.part_combo = QComboBox()
        self.part_combo.setEditable(True)
        self.part_combo.completer().setCompletionMode(QCompleter.PopupCompletion)
        add_layout.addWidget(self.part_combo, 0, 1)
        
        # تعداد
        add_layout.addWidget(QLabel("تعداد:"), 0, 2)
        self.part_quantity = QSpinBox()
        self.part_quantity.setRange(1, 100)
        self.part_quantity.setValue(1)
        add_layout.addWidget(self.part_quantity, 0, 3)
        
        # قیمت واحد
        add_layout.addWidget(QLabel("قیمت واحد (تومان):"), 1, 0)
        self.part_unit_price = QLineEdit()
        self.part_unit_price.setPlaceholderText("0")
        add_layout.addWidget(self.part_unit_price, 1, 1)
        
        # انبار
        add_layout.addWidget(QLabel("از انبار:"), 1, 2)
        self.warehouse_combo = QComboBox()
        self.warehouse_combo.addItems(["قطعات نو", "قطعات دست دوم"])
        add_layout.addWidget(self.warehouse_combo, 1, 3)
        
        # دکمه اضافه کردن
        btn_add_part = QPushButton("➕ افزودن به لیست")
        btn_add_part.setStyleSheet(self.get_button_style("#27ae60"))
        btn_add_part.clicked.connect(self.add_part_to_list)
        add_layout.addWidget(btn_add_part, 2, 0, 1, 4)
        
        add_group.setLayout(add_layout)
        layout.addWidget(add_group)
        
        # جدول قطعات استفاده شده
        self.parts_table = QTableWidget()
        self.parts_table.setColumnCount(6)
        self.parts_table.setHorizontalHeaderLabels([
            "ردیف", "نام قطعه", "تعداد", "قیمت واحد", "قیمت کل", "حذف"
        ])
        self.parts_table.horizontalHeader().setStretchLastSection(True)
        
        # تنظیم عرض ستون‌ها
        self.parts_table.setColumnWidth(0, 60)
        self.parts_table.setColumnWidth(1, 200)
        self.parts_table.setColumnWidth(2, 80)
        self.parts_table.setColumnWidth(3, 120)
        self.parts_table.setColumnWidth(4, 120)
        
        layout.addWidget(self.parts_table)
        
        # جمع کل قطعات
        total_layout = QHBoxLayout()
        total_layout.addWidget(QLabel("💰 جمع کل قطعات:"))
        self.parts_total_label = QLabel("0 تومان")
        self.parts_total_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #27ae60;")
        total_layout.addWidget(self.parts_total_label)
        total_layout.addStretch()
        layout.addLayout(total_layout)
        
        tab.setLayout(layout)
        self.tabs.addTab(tab, "🔩 قطعات استفاده شده")
    
    # ========== تب 3: هزینه‌ها (اجرت) ==========
    def create_costs_tab(self):
        """ایجاد تب هزینه‌ها - با جستجوی زنده"""
        tab = QWidget()
        
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("""
            QScrollArea {
                background-color: #1e1e1e;
                border: none;
            }
        """)
        
        content_widget = QWidget()
        main_layout = QVBoxLayout(content_widget)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(20)
        
        # ===== بخش 1: اضافه کردن اجرت جدید =====
        add_service_group = QGroupBox("➕ افزودن اجرت جدید")
        add_service_group.setStyleSheet(self.get_groupbox_style("#3498db"))
        
        add_layout = QGridLayout()
        add_layout.setContentsMargins(15, 20, 15, 15)
        add_layout.setVerticalSpacing(15)
        add_layout.setHorizontalSpacing(15)
        
        # ردیف 1: دسته‌بندی
        add_layout.addWidget(QLabel("دسته‌بندی:"), 0, 0, Qt.AlignRight)
        
        self.service_category_combo = CustomComboBox()
        self.service_category_combo.setEditable(True)
        self.service_category_combo.setInsertPolicy(QComboBox.NoInsert)
        self.service_category_combo.setFixedHeight(35)
        self.service_category_combo.setMinimumWidth(200)
        self.service_category_combo.lineEdit().setPlaceholderText("جستجو یا وارد کردن دسته جدید...")
        self.service_category_combo.setCompleter(None)
        
        # دکمه اضافه کردن دسته جدید
        self.btn_add_category = QPushButton("➕")
        self.btn_add_category.setFixedSize(35, 35)
        self.btn_add_category.setToolTip("افزودن دسته جدید")
        self.btn_add_category.setStyleSheet(self.get_button_style("#f39c12"))
        self.btn_add_category.clicked.connect(self.add_new_category)
        
        # دکمه بروزرسانی
        self.btn_refresh_categories = QPushButton("🔄")
        self.btn_refresh_categories.setFixedSize(35, 35)
        self.btn_refresh_categories.setToolTip("بروزرسانی دسته‌بندی‌ها")
        self.btn_refresh_categories.setStyleSheet(self.get_button_style("#3498db"))
        self.btn_refresh_categories.clicked.connect(self.load_service_categories)
        
        category_layout = QHBoxLayout()
        category_layout.addWidget(self.service_category_combo)
        category_layout.addWidget(self.btn_add_category)
        category_layout.addWidget(self.btn_refresh_categories)
        
        add_layout.addLayout(category_layout, 0, 1)
        
        # اتصال سیگنال‌های دسته‌بندی
        self.service_category_combo.lineEdit().textEdited.connect(self.on_category_text_edited)
        self.service_category_combo.lineEdit().editingFinished.connect(self.on_category_editing_finished)
        self.service_category_combo.activated.connect(self.on_category_activated)
        
        # Timer برای جستجوی تاخیری
        self.category_search_timer = QTimer()
        self.category_search_timer.setSingleShot(True)
        self.category_search_timer.timeout.connect(self.on_category_search_timeout)
        
        # ردیف 2: جستجوی اجرت
        add_layout.addWidget(QLabel("جستجوی اجرت:"), 1, 0, Qt.AlignRight)
        
        self.service_search = QComboBox()
        self.service_search.setEditable(True)
        self.service_search.setInsertPolicy(QComboBox.NoInsert)
        self.service_search.completer().setCompletionMode(QCompleter.PopupCompletion)
        self.service_search.setFixedHeight(35)
        self.service_search.setMinimumWidth(250)
        self.service_search.currentIndexChanged.connect(self.on_service_selected)
        
        # دکمه مدیریت اجرت‌ها
        self.btn_manage_services = QPushButton("⚙️ مدیریت اجرت‌ها")
        self.btn_manage_services.setFixedHeight(35)
        self.btn_manage_services.setStyleSheet(self.get_button_style("#9b59b6"))
        self.btn_manage_services.clicked.connect(self.open_service_fee_manager)
        
        search_layout = QHBoxLayout()
        search_layout.addWidget(self.service_search)
        search_layout.addWidget(self.btn_manage_services)
        
        add_layout.addLayout(search_layout, 1, 1)
        
        # ردیف 3: قیمت و تعداد
        add_layout.addWidget(QLabel("قیمت (تومان):"), 2, 0, Qt.AlignRight)
        self.service_price = QLineEdit()
        self.service_price.setPlaceholderText("قیمت به صورت خودکار پر می‌شود")
        self.service_price.setFixedHeight(35)
        self.service_price.setMinimumWidth(200)
        add_layout.addWidget(self.service_price, 2, 1)
        
        add_layout.addWidget(QLabel("تعداد/ضریب:"), 3, 0, Qt.AlignRight)
        self.service_multiplier = QDoubleSpinBox()
        self.service_multiplier.setRange(0.1, 10.0)
        self.service_multiplier.setValue(1.0)
        self.service_multiplier.setSingleStep(0.5)
        self.service_multiplier.setDecimals(1)
        self.service_multiplier.setFixedHeight(35)
        self.service_multiplier.setMinimumWidth(150)
        add_layout.addWidget(self.service_multiplier, 3, 1)
        
        # ردیف 4: دکمه اضافه کردن
        btn_add_service = QPushButton("➕ افزودن به لیست اجرت‌ها")
        btn_add_service.setFixedHeight(40)
        btn_add_service.setStyleSheet(self.get_button_style("#27ae60"))
        btn_add_service.clicked.connect(self.add_service_to_list)
        add_layout.addWidget(btn_add_service, 4, 0, 1, 2, Qt.AlignCenter)
        
        add_service_group.setLayout(add_layout)
        main_layout.addWidget(add_service_group)
        
        # ===== بخش 2: جدول اجرت‌های انتخاب شده =====
        services_group = QGroupBox("📋 لیست اجرت‌های این تعمیر")
        services_group.setStyleSheet(self.get_groupbox_style("#e74c3c"))
        services_group.setMinimumHeight(350)

        services_layout = QVBoxLayout()
        services_layout.setContentsMargins(10, 20, 10, 15)
        services_layout.setSpacing(15)

        self.services_table = QTableWidget()
        self.services_table.setColumnCount(6)
        self.services_table.setHorizontalHeaderLabels([
            "ردیف", "نام خدمت", "قیمت واحد", "تعداد/ضریب", "قیمت کل", "حذف"
        ])
        self.services_table.setMinimumHeight(250)
        self.services_table.setMaximumHeight(350)

        self.services_table.verticalHeader().setDefaultSectionSize(50)

        # تنظیمات جدول
        header = self.services_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Fixed)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.Fixed)
        header.setSectionResizeMode(3, QHeaderView.Fixed)
        header.setSectionResizeMode(4, QHeaderView.Fixed)
        header.setSectionResizeMode(5, QHeaderView.Fixed)

        self.services_table.setColumnWidth(0, 60)
        self.services_table.setColumnWidth(2, 120)
        self.services_table.setColumnWidth(3, 100)
        self.services_table.setColumnWidth(4, 120)
        self.services_table.setColumnWidth(5, 80)

        # قالب‌بندی بهتر برای جدول
        self.services_table.setAlternatingRowColors(True)
        self.services_table.setStyleSheet("""
            QTableWidget {
                background-color: #2c2c2c;
                alternate-background-color: #3c3c3c;
                gridline-color: #444;
                font-size: 12px;
            }
            QTableWidget::item {
                padding: 8px 4px;
                border-bottom: 1px solid #444;
            }
            QHeaderView::section {
                background-color: #2c3e50;
                color: white;
                padding: 8px;
                border: none;
                font-weight: bold;
                font-size: 11px;
            }
        """)

        services_layout.addWidget(self.services_table)
        main_layout.addWidget(services_group)
        
        # ===== بخش 3: هزینه بیرون‌سپاری =====
        outsourcing_group = QGroupBox("🏢 هزینه بیرون‌سپاری (در صورت نیاز)")
        outsourcing_group.setStyleSheet(self.get_groupbox_style("#f39c12"))
        
        outsourcing_layout = QGridLayout()
        outsourcing_layout.setContentsMargins(15, 20, 15, 15)
        
        outsourcing_layout.addWidget(QLabel("هزینه بیرون‌سپاری:"), 0, 0, Qt.AlignRight)
        self.outsourced_cost_input = QLineEdit()
        self.outsourced_cost_input.setPlaceholderText("مبلغ به تومان")
        self.outsourced_cost_input.setText("0")
        self.outsourced_cost_input.setFixedHeight(35)
        outsourcing_layout.addWidget(self.outsourced_cost_input, 0, 1)
        
        outsourcing_layout.addWidget(QLabel("توضیحات:"), 0, 2, Qt.AlignRight)
        self.outsourced_desc_input = QLineEdit()
        self.outsourced_desc_input.setPlaceholderText("توضیحات بیرون‌سپاری")
        self.outsourced_desc_input.setFixedHeight(35)
        outsourcing_layout.addWidget(self.outsourced_desc_input, 0, 3)
        
        outsourcing_group.setLayout(outsourcing_layout)
        main_layout.addWidget(outsourcing_group)
        
        # ===== بخش 4: خلاصه نهایی =====
        summary_group = QGroupBox("🧮 خلاصه نهایی هزینه‌ها")
        summary_group.setStyleSheet(self.get_groupbox_style("#27ae60"))
        
        summary_layout = QGridLayout()
        summary_layout.setContentsMargins(20, 25, 20, 25)
        summary_layout.setVerticalSpacing(15)
        
        # هزینه قطعات
        summary_layout.addWidget(QLabel("💰 هزینه قطعات:"), 0, 0, Qt.AlignRight)
        self.summary_parts = QLabel("0 تومان")
        self.summary_parts.setStyleSheet(self.get_summary_label_style("#3498db"))
        summary_layout.addWidget(self.summary_parts, 0, 1)
        
        # هزینه اجرت‌ها
        summary_layout.addWidget(QLabel("🔧 هزینه اجرت‌ها:"), 1, 0, Qt.AlignRight)
        self.summary_services = QLabel("0 تومان")
        self.summary_services.setStyleSheet(self.get_summary_label_style("#e74c3c"))
        summary_layout.addWidget(self.summary_services, 1, 1)
        
        # هزینه بیرون‌سپاری
        summary_layout.addWidget(QLabel("🏢 هزینه بیرون‌سپاری:"), 2, 0, Qt.AlignRight)
        self.summary_outsourced = QLabel("0 تومان")
        self.summary_outsourced.setStyleSheet(self.get_summary_label_style("#f39c12"))
        summary_layout.addWidget(self.summary_outsourced, 2, 1)
        
        # جداکننده
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        separator.setStyleSheet("background-color: #444; margin: 15px 0;")
        summary_layout.addWidget(separator, 3, 0, 1, 2)
        
        # جمع کل
        summary_layout.addWidget(QLabel("🧾 جمع کل تعمیر:"), 4, 0, Qt.AlignRight)
        self.summary_total = QLabel("0 تومان")
        self.summary_total.setStyleSheet("""
            QLabel {
                font-size: 18px;
                font-weight: bold;
                color: #27ae60;
                background-color: #2c2c2c;
                padding: 15px 30px;
                border-radius: 8px;
                border: 2px solid #27ae60;
            }
        """)
        summary_layout.addWidget(self.summary_total, 4, 1)
        
        summary_group.setLayout(summary_layout)
        main_layout.addWidget(summary_group)
        
        # ===== بخش 5: دکمه‌های عملیاتی =====
        button_layout = QHBoxLayout()
        button_layout.setSpacing(20)
        
        btn_calculate = QPushButton("🧮 محاسبه کل هزینه‌ها")
        btn_calculate.setFixedHeight(45)
        btn_calculate.setStyleSheet(self.get_button_style("#9b59b6"))
        btn_calculate.clicked.connect(self.calculate_all_costs)
        button_layout.addWidget(btn_calculate)
        
        btn_clear = QPushButton("🗑️ پاک کردن همه")
        btn_clear.setFixedHeight(45)
        btn_clear.setStyleSheet(self.get_button_style("#e74c3c"))
        btn_clear.clicked.connect(self.clear_costs_tab)
        button_layout.addWidget(btn_clear)
        
        button_layout.addStretch()
        main_layout.addLayout(button_layout)
        
        main_layout.addStretch()
        
        scroll_area.setWidget(content_widget)
        
        # لایه تب
        tab_layout = QVBoxLayout(tab)
        tab_layout.addWidget(scroll_area)
        
        self.tabs.addTab(tab, "💰 هزینه‌ها (اجرت)")
        
        # بارگذاری اولیه
        QTimer.singleShot(100, self.load_service_categories)
        QTimer.singleShot(150, self.load_services)
        
        return tab
    
    # ========== توابع مربوط به تب هزینه‌ها ==========
    
    def load_service_categories(self):
        """بارگذاری دسته‌بندی‌های خدمات از دیتابیس"""
        try:
            print("📥 در حال بارگذاری دسته‌بندی‌های خدمات...")
            
            self.service_category_combo.blockSignals(True)
            
            current_text = self.service_category_combo.currentText()
            
            query = """
            SELECT DISTINCT category 
            FROM ServiceFees 
            WHERE category IS NOT NULL AND category != '' 
            AND is_active = 1
            ORDER BY category
            """
            categories = self.data_manager.service_fee.fetch_all(query)
            
            if categories:
                self.all_categories = [cat['category'] for cat in categories]
            else:
                self.all_categories = [
                    "عمومی", "یخچال", "کولر گازی", "ماشین لباسشویی",
                    "آبگرمکن", "ماشین ظرفشویی", "اجاق گاز", "هود",
                    "جاروبرقی", "پنکه", "سایر"
                ]
            
            print(f"   ✅ {len(self.all_categories)} دسته‌بندی بارگذاری شد")
            
            self.service_category_combo.clear()
            self.service_category_combo.addItems(self.all_categories)
            
            # تنظیم تکمیل‌کننده
            completer = QCompleter(self.all_categories)
            completer.setCaseSensitivity(Qt.CaseInsensitive)
            completer.setFilterMode(Qt.MatchContains)
            completer.setCompletionMode(QCompleter.PopupCompletion)
            self.service_category_combo.setCompleter(completer)
            
            if current_text and current_text.strip():
                index = self.service_category_combo.findText(current_text, Qt.MatchFixedString)
                if index >= 0:
                    self.service_category_combo.setCurrentIndex(index)
                else:
                    self.service_category_combo.setCurrentText(current_text)
            
            self.service_category_combo.blockSignals(False)
            
            final_text = self.service_category_combo.currentText().strip()
            if final_text:
                QTimer.singleShot(100, lambda: self.filter_services_by_category(final_text))
            
        except Exception as e:
            print(f"❌ خطا در بارگذاری دسته‌بندی‌ها: {e}")
            self.service_category_combo.blockSignals(False)
            self.all_categories = ["عمومی", "یخچال", "کولر گازی", "سایر"]
            self.service_category_combo.clear()
            self.service_category_combo.addItems(self.all_categories)
    
    def load_services(self):
        """بارگذاری خدمات از دیتابیس"""
        try:
            print("📥 در حال بارگذاری خدمات...")
            
            self.all_services = self.data_manager.service_fee.get_active_services()
            
            if not self.all_services:
                print("   ⚠️ هیچ خدمت فعالی در دیتابیس یافت نشد")
                self.all_services = []
                self.service_search.clear()
                self.service_search.addItem("❌ هیچ خدمتی یافت نشد")
                return
            
            print(f"   ✅ {len(self.all_services)} خدمت بارگذاری شد")
            
            self.update_service_search_list()
            
        except Exception as e:
            print(f"❌ خطا در بارگذاری خدمات: {e}")
            self.all_services = []
            self.service_search.clear()
            self.service_search.addItem("❌ خطا در بارگذاری خدمات")
    
    def update_service_search_list(self, category_filter=None):
        """به‌روزرسانی لیست خدمات برای جستجو"""
        try:
            current_text = self.service_search.currentText()
            self.service_search.clear()
            
            if not self.all_services:
                self.service_search.addItem("❌ هیچ خدمتی یافت نشد")
                return
            
            if category_filter and category_filter != "همه":
                filtered_services = [
                    s for s in self.all_services 
                    if s.get('category', '').lower() == category_filter.lower()
                ]
            else:
                filtered_services = self.all_services
            
            if not filtered_services:
                self.service_search.addItem(f"❌ خدمتی در دسته '{category_filter}' یافت نشد")
                return
            
            for service in filtered_services:
                display_text = f"{service['service_name']} ({service['default_fee']:,} تومان)"
                self.service_search.addItem(display_text, service)
            
            service_names = [f"{s['service_name']} ({s['default_fee']:,} تومان)" for s in filtered_services]
            completer = QCompleter(service_names)
            completer.setCaseSensitivity(Qt.CaseInsensitive)
            completer.setFilterMode(Qt.MatchContains)
            self.service_search.setCompleter(completer)
            
            if current_text:
                index = self.service_search.findText(current_text, Qt.MatchContains)
                if index >= 0:
                    self.service_search.setCurrentIndex(index)
            
        except Exception as e:
            print(f"❌ خطا در به‌روزرسانی لیست خدمات: {e}")
    
    def on_category_text_edited(self, text):
        """هنگام ویرایش متن دسته‌بندی"""
        self.category_search_timer.stop()
        self.category_search_timer.start(300)
    
    def on_category_search_timeout(self):
        """پس از تاخیر، جستجو انجام شود"""
        text = self.service_category_combo.currentText().strip()
        if text:
            self.filter_services_by_category(text)
    
    def on_category_editing_finished(self):
        """هنگام اتمام ویرایش"""
        text = self.service_category_combo.currentText().strip()
        if text:
            index = self.service_category_combo.findText(text, Qt.MatchFixedString)
            if index >= 0:
                self.service_category_combo.setCurrentIndex(index)
            self.filter_services_by_category(text)
    
    def on_category_activated(self, index):
        """هنگام انتخاب یک آیتم از لیست"""
        if index >= 0:
            text = self.service_category_combo.currentText()
            self.filter_services_by_category(text)
    
    def add_new_category(self):
        """افزودن دسته‌بندی جدید"""
        try:
            category = self.service_category_combo.currentText().strip()
            
            if not category:
                QMessageBox.warning(self, "خطا", "لطفا نام دسته‌بندی را وارد کنید.")
                return
            
            if category in self.all_categories:
                QMessageBox.information(self, "تکراری", 
                    f"دسته‌بندی '{category}' قبلاً در لیست وجود دارد.")
                return
            
            reply = QMessageBox.question(
                self, "افزودن دسته جدید",
                f"آیا می‌خواهید دسته '{category}' را اضافه کنید؟",
                QMessageBox.Yes | QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                self.all_categories.append(category)
                self.all_categories.sort()
                
                self.service_category_combo.blockSignals(True)
                self.service_category_combo.clear()
                self.service_category_combo.addItems(self.all_categories)
                self.service_category_combo.setCurrentText(category)
                self.service_category_combo.blockSignals(False)
                
                try:
                    import time
                    timestamp = int(time.time() % 10000)
                    service_code = f"CAT-{timestamp:04d}"
                    
                    sample_service = {
                        'service_code': service_code,
                        'service_name': f"خدمت نمونه - {category}",
                        'category': category,
                        'default_fee': 10000,
                        'estimated_hours': 1.0,
                        'difficulty_level': 1,
                        'description': f"دسته‌بندی نمونه: {category}",
                        'is_active': 0
                    }
                    
                    self.data_manager.service_fee.add_service(sample_service)
                    print(f"✅ دسته '{category}' در دیتابیس ذخیره شد")
                    
                except Exception as db_error:
                    print(f"⚠️ خطا در ذخیره دسته در دیتابیس: {db_error}")
                
                QMessageBox.information(self, "موفق", 
                    f"دسته‌بندی '{category}' با موفقیت اضافه شد.")
                
                self.load_services()
                
        except Exception as e:
            QMessageBox.critical(self, "خطا", f"خطا در افزودن دسته‌بندی: {str(e)}")
            print(f"❌ خطا در add_new_category: {e}")
    
    def filter_services_by_category(self, category):
        """فیلتر خدمات بر اساس دسته‌بندی"""
        try:
            previous_text = self.service_search.currentText()
            
            if not category or category.strip() == "":
                self.update_service_search_list()
                return
            
            print(f"🔍 فیلتر کردن بر اساس دسته: '{category}'")
            
            filtered_services = []
            for service in self.all_services:
                service_category = service.get('category', '').lower()
                search_category = category.lower().strip()
                
                if (search_category in service_category or 
                    service_category == search_category or
                    any(word in service_category for word in search_category.split())):
                    filtered_services.append(service)
            
            if not filtered_services:
                for service in self.all_services:
                    if any(word in service.get('service_name', '').lower() 
                          for word in category.lower().split()):
                        filtered_services.append(service)
            
            if not filtered_services:
                self.service_search.clear()
                self.service_search.addItem(f"❌ خدمتی در '{category}' یافت نشد")
            else:
                self.service_search.clear()
                for service in filtered_services:
                    display_text = f"{service['service_name']} ({service['default_fee']:,} تومان)"
                    self.service_search.addItem(display_text, service)
                
                service_names = [f"{s['service_name']} ({s['default_fee']:,} تومان)" 
                               for s in filtered_services]
                completer = QCompleter(service_names)
                completer.setCaseSensitivity(Qt.CaseInsensitive)
                completer.setFilterMode(Qt.MatchContains)
                self.service_search.setCompleter(completer)
                
                if previous_text:
                    index = self.service_search.findText(previous_text, Qt.MatchContains)
                    if index >= 0:
                        self.service_search.setCurrentIndex(index)
            
            print(f"   ✅ {len(filtered_services)} خدمت یافت شد")
            
        except Exception as e:
            print(f"❌ خطا در فیلتر خدمات: {e}")
            import traceback
            traceback.print_exc()
    
    def on_service_selected(self, index):
        """هنگام انتخاب خدمت از لیست"""
        if index < 0:
            return
        
        try:
            service_data = self.service_search.itemData(index)
            if not service_data:
                text = self.service_search.currentText()
                for service in self.all_services:
                    if service['service_name'] in text:
                        service_data = service
                        break
            
            if service_data:
                self.service_price.setText(str(service_data.get('default_fee', 0)))
                
                category = service_data.get('category')
                if category:
                    cat_index = self.service_category_combo.findText(category, Qt.MatchExactly)
                    if cat_index >= 0:
                        self.service_category_combo.setCurrentIndex(cat_index)
                    else:
                        self.service_category_combo.setCurrentText(category)
                
                print(f"✅ خدمت انتخاب شد: {service_data.get('service_name', '')}")
        
        except Exception as e:
            print(f"❌ خطا در انتخاب خدمت: {e}")
    
    def add_service_to_list(self):
        """اضافه کردن خدمت به لیست اجرت‌های این تعمیر"""
        try:
            service_name = ""
            unit_price = 0
            
            index = self.service_search.currentIndex()
            if index >= 0:
                service_data = self.service_search.itemData(index)
                if service_data:
                    service_name = service_data.get('service_name', '')
                    unit_price = service_data.get('default_fee', 0)
                else:
                    text = self.service_search.currentText()
                    if ' (' in text:
                        service_name = text.split(' (')[0]
                        import re
                        price_match = re.search(r'\(([\d,]+)', text)
                        if price_match:
                            unit_price = int(price_match.group(1).replace(',', ''))
            
            if not service_name:
                service_name = self.service_search.currentText()
                if not service_name or service_name.startswith("❌"):
                    QMessageBox.warning(self, "خطا", "لطفا یک خدمت انتخاب کنید.")
                    return
            
            price_text = self.service_price.text().strip()
            if price_text:
                try:
                    unit_price = int(price_text.replace(',', ''))
                except:
                    QMessageBox.warning(self, "خطا", "لطفا قیمت معتبر وارد کنید.")
                    return
            elif unit_price <= 0:
                QMessageBox.warning(self, "خطا", "لطفا قیمت را وارد کنید.")
                return
            
            multiplier = self.service_multiplier.value()
            total_price = unit_price * multiplier
            
            row = self.services_table.rowCount()
            self.services_table.insertRow(row)
            
            service_item = {
                'service_name': service_name,
                'unit_price': unit_price,
                'multiplier': multiplier,
                'total_price': total_price,
                'category': self.service_category_combo.currentText()
            }
            
            self.services_table.setItem(row, 0, QTableWidgetItem(str(row + 1)))
            self.services_table.setItem(row, 1, QTableWidgetItem(service_name))
            self.services_table.setItem(row, 2, QTableWidgetItem(f"{unit_price:,} تومان"))
            self.services_table.setItem(row, 3, QTableWidgetItem(str(multiplier)))
            self.services_table.setItem(row, 4, QTableWidgetItem(f"{total_price:,} تومان"))
            
            btn_delete = QPushButton("🗑️")
            btn_delete.setStyleSheet(self.get_button_style("#e74c3c"))
            btn_delete.clicked.connect(lambda: self.delete_service_from_list(row))
            self.services_table.setCellWidget(row, 5, btn_delete)
            
            self.services_table.item(row, 1).setData(Qt.UserRole, service_item)
            
            self.update_services_total()

            self.service_search.setCurrentIndex(-1)
            self.service_price.clear()
            self.service_multiplier.setValue(1.0)
            
            print(f"✅ خدمت '{service_name}' به لیست اضافه شد")
            
        except Exception as e:
            QMessageBox.critical(self, "خطا", f"خطا در اضافه کردن خدمت:\n{str(e)}")
    
    def delete_service_from_list(self, row):
        """حذف خدمت از لیست"""
        try:
            self.services_table.removeRow(row)
            
            for i in range(self.services_table.rowCount()):
                self.services_table.setItem(i, 0, QTableWidgetItem(str(i + 1)))
            
            self.update_services_total()
            
        except Exception as e:
            print(f"❌ خطا در حذف خدمت: {e}")


    def update_services_total(self):
        """به‌روزرسانی جمع کل هزینه اجرت‌ها"""
        total = 0
        for row in range(self.services_table.rowCount()):
            item = self.services_table.item(row, 4)
            if item:
                text = item.text().replace('تومان', '').replace(',', '').strip()
                try:
                    total += int(float(text))
                except:
                    pass
        
        # بروزرسانی برچسب در تب هزینه‌ها
        if hasattr(self, 'services_total_label'):
            self.services_total_label.setText(f"{total:,} تومان")
        
        # همچنین برچسب خلاصه را نیز به روز کنید
        if hasattr(self, 'summary_services'):
            self.summary_services.setText(f"{total:,} تومان")
        
        return total
    
    def clear_costs_tab(self):
        """پاک کردن تمام محتوای تب هزینه‌ها"""
        reply = QMessageBox.question(
            self, "پاک کردن هزینه‌ها",
            "آیا مطمئن هستید که می‌خواهید همه هزینه‌ها را پاک کنید؟",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.services_table.setRowCount(0)
            self.outsourced_cost_input.setText("0")
            self.outsourced_desc_input.clear()
            self.update_services_total()
            self.calculate_all_costs()
            QMessageBox.information(self, "موفق", "هزینه‌ها پاک شدند.")
    
    def calculate_all_costs(self):
        """محاسبه تمام هزینه‌ها"""
        try:
            parts_cost = self.update_parts_total()
            self.summary_parts.setText(f"{parts_cost:,} تومان")
            
            services_cost = self.update_services_total()
            self.summary_services.setText(f"{services_cost:,} تومان")
            
            try:
                outsourced_cost = int(self.outsourced_cost_input.text().replace(',', '') or 0)
            except:
                outsourced_cost = 0
            self.summary_outsourced.setText(f"{outsourced_cost:,} تومان")
            
            total_cost = parts_cost + services_cost + outsourced_cost
            self.summary_total.setText(f"{total_cost:,} تومان")
            
            self.total_cost = total_cost
            
            QMessageBox.information(
                self, "محاسبه", 
                f"✅ هزینه‌ها محاسبه شد:\n\n"
                f"• قطعات: {parts_cost:,} تومان\n"
                f"• اجرت‌ها: {services_cost:,} تومان\n"
                f"• بیرون‌سپاری: {outsourced_cost:,} تومان\n"
                f"• جمع کل: {total_cost:,} تومان"
            )
            
            return total_cost
            
        except Exception as e:
            QMessageBox.critical(self, "خطا", f"خطا در محاسبه: {str(e)}")
            return 0
    
    def open_service_fee_manager(self):
        """باز کردن فرم مدیریت اجرت‌ها"""
        try:
            from ui.widgets.service_fee_manager import ServiceFeeManager
            
            dialog = ServiceFeeManager(self.data_manager)
            dialog.service_fee_updated.connect(self.refresh_service_list)
            dialog.exec()
            
            self.refresh_service_list()
            
        except Exception as e:
            QMessageBox.critical(self, "خطا", f"خطا در باز کردن مدیر اجرت‌ها:\n{str(e)}")
    
    def refresh_service_list(self):
        """تازه‌سازی لیست خدمات پس از به‌روزرسانی"""
        try:
            print("🔄 تازه‌سازی لیست خدمات...")
            
            self.load_service_categories()
            self.load_services()
            
            current_category = self.service_category_combo.currentText()
            if current_category:
                self.filter_services_by_category(current_category)
            
            QMessageBox.information(
                self, "✅ به‌روزرسانی", 
                "لیست اجرت‌ها با موفقیت به‌روز شد."
            )
            
        except Exception as e:
            print(f"❌ خطا در تازه‌سازی: {e}")
    
    # ========== توابع مشترک تب‌ها ==========
    
    def load_initial_data(self):
        """بارگذاری داده‌های اولیه"""
        self.load_technicians()
        self.load_parts()
        self.update_parts_total()
        
        QTimer.singleShot(100, self.load_service_categories)
        QTimer.singleShot(150, self.load_services)
        
    def load_technicians(self):
        """بارگذاری لیست تعمیرکاران"""
        try:
            if not hasattr(self, 'technician_combo') or self.technician_combo is None:
                print("⚠️ technician_combo هنوز ایجاد نشده")
                return
            
            persons = self.data_manager.person.get_all_persons()
            self.technicians_cache = [p for p in persons 
                                    if p.get('person_type') in ['تعمیرکار بیرونی', 'کارمند', 'تعمیرکار']]
            
            if self.technician_combo:
                self.technician_combo.clear()
                for tech in self.technicians_cache:
                    name = f"{tech.get('first_name', '')} {tech.get('last_name', '')}"
                    self.technician_combo.addItem(name, tech['id'])
            
            if hasattr(self, 'outsourced_combo') and self.outsourced_combo:
                self.outsourced_combo.clear()
                for tech in self.technicians_cache:
                    name = f"{tech.get('first_name', '')} {tech.get('last_name', '')}"
                    self.outsourced_combo.addItem(name, tech['id'])
            
            print(f"✅ {len(self.technicians_cache)} تعمیرکار بارگذاری شد")
            
        except Exception as e:
            print(f"❌ خطا در بارگذاری تعمیرکاران: {e}")
            import traceback
            traceback.print_exc()
    
    def load_parts(self):
        """بارگذاری لیست قطعات"""
        try:
            self.parts_cache = self.data_manager.part.get_all_parts()
            
            self.part_combo.clear()
            for part in self.parts_cache:
                self.part_combo.addItem(part['part_name'])
            
            part_names = [p['part_name'] for p in self.parts_cache]
            completer = QCompleter(part_names)
            completer.setCaseSensitivity(Qt.CaseInsensitive)
            self.part_combo.setCompleter(completer)
            
            print(f"✅ {len(self.parts_cache)} قطعه بارگذاری شد")
            
        except Exception as e:
            print(f"❌ خطا در بارگذاری قطعات: {e}")
    
    def on_repair_type_changed(self, text):
        """هنگام تغییر نوع تعمیر"""
        is_outsourced = (text == "بیرون سپاری")
        self.outsourced_combo.setEnabled(is_outsourced)
        self.outsourced_cost_input.setEnabled(is_outsourced)
    
    def add_part_to_list(self):
        """اضافه کردن قطعه به لیست"""
        try:
            part_name = self.part_combo.currentText().strip()
            if not part_name:
                QMessageBox.warning(self, "خطا", "لطفا نام قطعه را وارد کنید.")
                return
            
            quantity = self.part_quantity.value()
            unit_price_text = self.part_unit_price.text().strip()
            
            if not unit_price_text:
                QMessageBox.warning(self, "خطا", "لطفا قیمت واحد را وارد کنید.")
                return
            
            try:
                unit_price = int(unit_price_text.replace(',', ''))
            except:
                QMessageBox.warning(self, "خطا", "لطفا قیمت معتبر وارد کنید.")
                return
            
            total_price = quantity * unit_price
            
            row = self.parts_table.rowCount()
            self.parts_table.insertRow(row)
            
            self.parts_table.setItem(row, 0, QTableWidgetItem(str(row + 1)))
            self.parts_table.setItem(row, 1, QTableWidgetItem(part_name))
            self.parts_table.setItem(row, 2, QTableWidgetItem(str(quantity)))
            self.parts_table.setItem(row, 3, QTableWidgetItem(f"{unit_price:,} تومان"))
            self.parts_table.setItem(row, 4, QTableWidgetItem(f"{total_price:,} تومان"))
            
            btn_delete = QPushButton("🗑️")
            btn_delete.setStyleSheet(self.get_button_style("#e74c3c"))
            btn_delete.clicked.connect(lambda: self.delete_part_from_list(row))
            self.parts_table.setCellWidget(row, 5, btn_delete)
            
            self.update_parts_total()
            
            self.part_combo.setCurrentText("")
            self.part_quantity.setValue(1)
            self.part_unit_price.clear()
            
        except Exception as e:
            QMessageBox.critical(self, "خطا", f"خطا در اضافه کردن قطعه: {str(e)}")
    
    def delete_part_from_list(self, row):
        """حذف قطعه از لیست"""
        self.parts_table.removeRow(row)
        
        for i in range(self.parts_table.rowCount()):
            self.parts_table.setItem(i, 0, QTableWidgetItem(str(i + 1)))
        
        self.update_parts_total()
    
    def update_parts_total(self):
        """به‌روزرسانی جمع کل هزینه قطعات"""
        total = 0
        for row in range(self.parts_table.rowCount()):
            item = self.parts_table.item(row, 4)
            if item:
                text = item.text().replace('تومان', '').replace(',', '').strip()
                try:
                    total += int(float(text))
                except:
                    pass
        
        self.parts_total_label.setText(f"{total:,} تومان")
        return total
    
    def load_reception_data(self):
        """بارگذاری اطلاعات پذیرش انتخاب شده"""
        if not self.reception_id:
            return
        
        try:
            reception = self.data_manager.reception.get_reception_by_id(self.reception_id)
            if reception:
                self.update_reception_display(reception)
                
                self.selected_customer = {
                    'id': reception['customer_id'],
                    'name': reception.get('customer_name', '--'),
                    'mobile': reception.get('mobile', '--')
                }
                
                self.selected_device = {
                    'id': reception['device_id'],
                    'device_type': reception.get('device_type', ''),
                    'brand': reception.get('brand', ''),
                    'model': reception.get('model', ''),
                    'serial_number': reception.get('serial_number', '')
                }
                
                self.update_customer_device_display()
                self.enable_repair_sections()
                self.repair_status_label.setText(f"پذیرش: {reception.get('reception_number', '')}")
                
        except Exception as e:
            print(f"❌ خطا در بارگذاری اطلاعات پذیرش: {e}")
    
    # ========== عملیات فرم ==========
    
    def new_repair(self):
        """تعمیر جدید"""
        reply = QMessageBox.question(
            self, "تعمیر جدید",
            "آیا می‌خواهید تعمیر جدید ایجاد کنید؟\nتمام داده‌های ذخیره نشده از بین خواهند رفت.",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.reset_form()
    
    def save_repair(self):
        """ذخیره تعمیر"""
        try:
            if not self.validate_form():
                return
            
            repair_data = self.collect_repair_data()
            
            if self.current_repair_id:
                success = self.data_manager.repair.update_repair(self.current_repair_id, repair_data)
                message = "ویرایش"
            else:
                success = self.data_manager.repair.add_repair(repair_data)
                message = "ثبت"
            
            if success:
                if self.reception_id:
                    self.data_manager.reception.update_status(self.reception_id, 'در حال تعمیر')
                
                self.repair_saved.emit(repair_data)
                QMessageBox.information(self, "موفق", f"تعمیر با موفقیت {message} شد.")
                self.repair_status_label.setText(f"تعمیر {message} شد")
            else:
                QMessageBox.critical(self, "خطا", f"خطا در {message} تعمیر.")
                
        except Exception as e:
            QMessageBox.critical(self, "خطا", f"خطا در ذخیره تعمیر:\n{str(e)}")
    
    def finish_repair(self):
        """تکمیل تعمیر"""
        try:
            reply = QMessageBox.question(
                self, "تکمیل تعمیر",
                "آیا تعمیر کامل شده است؟\nپس از تأیید، وضعیت پذیرش به 'تعمیر شده' تغییر می‌کند.",
                QMessageBox.Yes | QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                self.save_repair()
                self.status_combo.setCurrentText("تمام شده")
                
                if self.reception_id:
                    self.data_manager.reception.update_status(self.reception_id, 'تعمیر شده')
                    QMessageBox.information(self, "موفق", 
                        "✅ تعمیر تکمیل شد و وضعیت پذیرش به روز شد.")
        except Exception as e:
            QMessageBox.critical(self, "خطا", f"خطا در تکمیل تعمیر: {str(e)}")
    
    def validate_form(self):
        """اعتبارسنجی فرم"""
        if not self.reception_id:
            QMessageBox.warning(self, "خطا", "لطفا یک پذیرش انتخاب کنید.")
            self.tabs.setCurrentIndex(0)
            self.btn_smart_search.setFocus()
            return False
        
        if not self.repair_date.get_date():
            QMessageBox.warning(self, "خطا", "لطفا تاریخ تعمیر را وارد کنید.")
            self.tabs.setCurrentIndex(0)
            self.repair_date.setFocus()
            return False
        
        if self.repair_type_combo.currentText() == "بیرون سپاری":
            if self.outsourced_combo.currentIndex() < 0:
                QMessageBox.warning(self, "خطا", "برای بیرون‌سپاری، شخص را انتخاب کنید.")
                self.tabs.setCurrentIndex(0)
                self.outsourced_combo.setFocus()
                return False
        
        if self.technician_combo.currentIndex() < 0:
            QMessageBox.warning(self, "خطا", "لطفا تعمیرکار را انتخاب کنید.")
            self.tabs.setCurrentIndex(0)
            self.technician_combo.setFocus()
            return False
        
        parts_count = self.parts_table.rowCount()
        services_count = self.services_table.rowCount()
        
        if parts_count == 0 and services_count == 0:
            reply = QMessageBox.question(
                self, "تأیید", 
                "هیچ قطعه یا خدمتی اضافه نشده است. آیا مطمئن هستید که می‌خواهید ادامه دهید؟",
                QMessageBox.Yes | QMessageBox.No
            )
            if reply == QMessageBox.No:
                return False
        
        return True
    
    def collect_repair_data(self):
        """جمع‌آوری داده‌های فرم برای ذخیره"""
        repair_data = {}
        
        # اطلاعات پایه
        repair_data['reception_id'] = self.reception_id
        
        # تبدیل تاریخ شمسی به میلادی برای ذخیره در دیتابیس
        repair_date_jalali = self.repair_date.get_date()
        if repair_date_jalali:
            # تبدیل تاریخ شمسی به میلادی
            repair_data['repair_date'] = self.data_manager.db.jalali_to_gregorian(
                repair_date_jalali.strftime('%Y/%m/%d')
            )
        else:
            repair_data['repair_date'] = self.data_manager.db.get_current_jalali_date()
        
        repair_data['technician_id'] = self.technician_combo.currentData()
        repair_data['repair_type'] = self.repair_type_combo.currentText()
        
        if self.repair_type_combo.currentText() == "بیرون سپاری":
            repair_data['outsourced_to'] = self.outsourced_combo.currentData()
        else:
            repair_data['outsourced_to'] = None
            
        repair_data['status'] = self.status_combo.currentText()
        repair_data['start_time'] = self.start_time.time().toString("HH:mm")
        repair_data['end_time'] = self.end_time.time().toString("HH:mm")
        repair_data['repair_description'] = self.repair_description.toPlainText()
        
        # قطعات استفاده شده
        parts = []
        for row in range(self.parts_table.rowCount()):
            part = {}
            part['part_name'] = self.parts_table.item(row, 1).text()
            part['quantity'] = int(self.parts_table.item(row, 2).text())
            part['unit_price'] = int(self.parts_table.item(row, 3).text().replace('تومان', '').replace(',', '').strip())
            part['total_price'] = int(self.parts_table.item(row, 4).text().replace('تومان', '').replace(',', '').strip())
            parts.append(part)
        repair_data['used_parts'] = json.dumps(parts) if parts else None
        
        # خدمات (اجرت‌ها)
        services = []
        for row in range(self.services_table.rowCount()):
            service = {}
            service_item = self.services_table.item(row, 1).data(Qt.UserRole)
            if service_item:
                service.update(service_item)
            else:
                service['service_name'] = self.services_table.item(row, 1).text()
                service['unit_price'] = int(self.services_table.item(row, 2).text().replace('تومان', '').replace(',', '').strip())
                service['multiplier'] = float(self.services_table.item(row, 3).text())
                service['total_price'] = int(self.services_table.item(row, 4).text().replace('تومان', '').replace(',', '').strip())
            services.append(service)
        repair_data['labor_cost'] = sum(service.get('total_price', 0) for service in services)
        
        # هزینه بیرون‌سپاری
        try:
            repair_data['outsourced_cost'] = int(self.outsourced_cost_input.text().replace(',', '') or 0)
        except:
            repair_data['outsourced_cost'] = 0
        
        # محاسبه جمع کل
        parts_cost = self.update_parts_total()
        services_cost = self.update_services_total()
        repair_data['total_cost'] = parts_cost + services_cost + repair_data['outsourced_cost']
        
        return repair_data
    
    def reset_form(self):
        """بازنشانی فرم"""
        self.current_repair_id = None
        self.reception_id = None
        self.selected_customer = None
        self.selected_device = None
        
        # تب 1
        self.reception_group.setVisible(False)
        self.customer_info_label.setText("--")
        self.customer_mobile_label.setText("--")
        self.device_info_label.setText("--")
        self.device_serial_label.setText("--")
        self.repair_date.set_date(jdatetime.date.today().strftime('%Y/%m/%d'))
        self.technician_combo.setCurrentIndex(-1)
        self.repair_type_combo.setCurrentIndex(0)
        self.outsourced_combo.setCurrentIndex(-1)
        self.status_combo.setCurrentIndex(0)
        self.start_time.setTime(QTime.currentTime())
        self.end_time.setTime(QTime(0, 0))
        self.repair_description.clear()
        
        # تب 2
        self.parts_table.setRowCount(0)
        self.update_parts_total()
        
        # تب 3
        self.services_table.setRowCount(0)
        self.update_services_total()
        self.outsourced_cost_input.setText("0")
        self.outsourced_desc_input.clear()
        
        # خلاصه
        self.summary_parts.setText("0 تومان")
        self.summary_services.setText("0 تومان")
        self.summary_outsourced.setText("0 تومان")
        self.summary_total.setText("0 تومان")
        
        # وضعیت
        self.repair_status_label.setText("تعمیر جدید")
        
        # غیرفعال کردن تب‌های ۲ و ۳
        for i in range(1, self.tabs.count()):
            self.tabs.setTabEnabled(i, False)
    
    def close_form(self):
        """بستن فرم"""
        reply = QMessageBox.question(
            self, "بستن فرم",
            "آیا مطمئن هستید؟ تغییرات ذخیره نشده از دست خواهند رفت.",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.form_closed.emit()
            self.close()
    
    def update_customer_device_display(self):
        """بروزرسانی نمایش اطلاعات مشتری و دستگاه"""
        try:
            if self.selected_customer:
                name = self.selected_customer.get('name', '--')
                mobile = self.selected_customer.get('mobile', '--')
                self.customer_info_label.setText(name)
                self.customer_mobile_label.setText(mobile if mobile else '--')
            else:
                self.customer_info_label.setText("--")
                self.customer_mobile_label.setText("--")
            
            if self.selected_device:
                device_text = f"{self.selected_device.get('device_type', '')} - {self.selected_device.get('brand', '')} {self.selected_device.get('model', '')}"
                serial = self.selected_device.get('serial_number', '--')
                self.device_info_label.setText(device_text)
                self.device_serial_label.setText(serial if serial else '--')
            else:
                self.device_info_label.setText("--")
                self.device_serial_label.setText("--")
                
            print(f"✅ نمایش مشتری و دستگاه به‌روزرسانی شد")
            
        except Exception as e:
            print(f"⚠️ خطا در به‌روزرسانی نمایش: {e}")

    def update_reception_display(self, reception_data):
        """بروزرسانی نمایش اطلاعات پذیرش"""
        if reception_data:
            self.reception_group.setVisible(True)
            
            # شماره پذیرش
            self.reception_number_label.setText(reception_data.get('reception_number', '--'))
            
            # تاریخ پذیرش (تبدیل از میلادی به شمسی برای نمایش)
            reception_date = reception_data.get('reception_date')
            if reception_date:
                jalali_date = self.data_manager.db.gregorian_to_jalali(reception_date)
                self.reception_date_label.setText(jalali_date)
            else:
                self.reception_date_label.setText("--")
            
            # وضعیت
            status = reception_data.get('status', '--')
            self.reception_status_label.setText(status)
            
            if status == 'در انتظار':
                self.reception_status_label.setStyleSheet("background-color: #f39c12; color: white; padding: 6px 12px; border-radius: 4px;")
            elif status == 'در حال تعمیر':
                self.reception_status_label.setStyleSheet("background-color: #3498db; color: white; padding: 6px 12px; border-radius: 4px;")
            elif status == 'تعمیر شده':
                self.reception_status_label.setStyleSheet("background-color: #2ecc71; color: white; padding: 6px 12px; border-radius: 4px;")
            else:
                self.reception_status_label.setStyleSheet("background-color: #95a5a6; color: white; padding: 6px 12px; border-radius: 4px;")
            
            # هزینه تخمینی
            estimated_cost = reception_data.get('estimated_cost', 0)
            if estimated_cost:
                self.estimated_cost_label.setText(f"{estimated_cost:,} تومان")
            else:
                self.estimated_cost_label.setText("--")
            
            # مشکل دستگاه
            problem = reception_data.get('problem_description', '')
            self.problem_description_text.setText(problem)
            
            self.enable_repair_sections()

    def enable_repair_sections(self):
        """فعال کردن بخش‌های تعمیر"""
        for i in range(1, self.tabs.count()):
            self.tabs.setTabEnabled(i, True)
        
        self.btn_save.setEnabled(True)
        self.btn_finish.setEnabled(True)

    def open_smart_search(self):
        """باز کردن دیالوگ جستجوی هوشمند"""
        try:
            from ui.dialogs.smart_search_dialog import SmartSearchDialog
            
            dialog = SmartSearchDialog(self.data_manager)
            dialog.reception_selected.connect(self.on_reception_selected)
            
            if dialog.exec() == QDialog.Accepted:
                print("✅ پذیرش از دیالوگ جستجو انتخاب شد")
            else:
                print("❌ جستجو لغو شد")
                
        except ImportError as e:
            QMessageBox.warning(self, "خطا", f"دیالوگ جستجو در دسترس نیست:\n{str(e)}")
            print(f"⚠️ خطای ایمپورت: {e}")
        except Exception as e:
            QMessageBox.critical(self, "خطا", f"خطا در باز کردن جستجوی هوشمند:\n{str(e)}")
            print(f"❌ خطا در open_smart_search: {e}")

    def on_reception_selected(self, data):
        """هنگام انتخاب پذیرش از دیالوگ جستجوی هوشمند"""
        if not data:
            print("⚠️ داده‌ای از دیالوگ دریافت نشد")
            return
        
        try:
            print(f"📥 داده‌های دریافت شده از دیالوگ: {data.keys()}")
            
            self.reception_id = data.get('reception_id')
            self.current_customer_id = data.get('customer_id')
            self.current_device_id = data.get('device_id')
            
            print(f"🔍 شناسه‌های دریافت شده: reception_id={self.reception_id}, "
                f"customer_id={self.current_customer_id}, device_id={self.current_device_id}")
            
            if self.reception_id:
                reception_data = self.data_manager.reception.get_reception_by_id(self.reception_id)
                
                if not reception_data:
                    QMessageBox.warning(self, "خطا", "اطلاعات پذیرش در دیتابیس یافت نشد.")
                    return
                
                print(f"✅ اطلاعات پذیرش از دیتابیس بارگذاری شد: {reception_data.get('reception_number')}")
                
                self.update_reception_display(reception_data)
                
                customer_id = reception_data.get('customer_id')
                device_id = reception_data.get('device_id')
                
                if customer_id:
                    customer = self.data_manager.person.get_person_by_id(customer_id)
                    if customer:
                        self.selected_customer = {
                            'id': customer_id,
                            'name': f"{customer.get('first_name', '')} {customer.get('last_name', '')}",
                            'mobile': customer.get('mobile', ''),
                            'person_type': customer.get('person_type', 'مشتری')
                        }
                
                if device_id:
                    device = self.data_manager.device.get_device_by_id(device_id)
                    if device:
                        self.selected_device = {
                            'id': device_id,
                            'device_type': device.get('device_type', ''),
                            'brand': device.get('brand', ''),
                            'model': device.get('model', ''),
                            'serial_number': device.get('serial_number', '')
                        }
                
                self.update_customer_device_display()
                self.populate_form_fields(reception_data)
                self.enable_repair_sections()
                
                self.repair_status_label.setText(f"پذیرش: {reception_data.get('reception_number', '')}")
                
                QMessageBox.information(
                    self, 
                    "✅ انتخاب موفق", 
                    f"پذیرش شماره {reception_data.get('reception_number', '')} با موفقیت انتخاب شد.\n\n"
                    f"مشتری: {self.selected_customer.get('name', '') if self.selected_customer else '--'}\n"
                    f"دستگاه: {self.selected_device.get('brand', '') if self.selected_device else '--'} "
                    f"{self.selected_device.get('model', '') if self.selected_device else ''}\n"
                    f"وضعیت: {reception_data.get('status', '--')}"
                )
                
                self.tabs.setCurrentIndex(0)
                
            else:
                QMessageBox.warning(self, "خطا", "شناسه پذیرش دریافت نشد.")
                
        except Exception as e:
            print(f"❌ خطا در پردازش انتخاب پذیرش: {e}")
            import traceback
            traceback.print_exc()
            QMessageBox.critical(
                self, 
                "خطا", 
                f"خطا در پردازش اطلاعات پذیرش:\n{str(e)}\n\n"
                "لطفا دوباره تلاش کنید یا با پشتیبانی تماس بگیرید."
            )

    def populate_form_fields(self, reception_data):
        """پر کردن فیلدهای فرم با اطلاعات پذیرش"""
        try:
            print("🔄 پر کردن فیلدهای فرم...")
            
            # تنظیم تاریخ امروز شمسی
            today = jdatetime.datetime.now().strftime('%Y/%m/%d')
            self.repair_date.set_date(today)
            
            self.start_time.setTime(QTime.currentTime())
            
            # اگر مشکل دستگاه وجود دارد، به توضیحات تعمیر اضافه کن
            problem = reception_data.get('problem_description', '')
            if problem:
                current_desc = self.repair_description.toPlainText()
                if not current_desc.strip():
                    self.repair_description.setText(f"مشکل گزارش شده:\n{problem}\n\nتوضیحات تعمیر:")
            
            self.status_combo.setCurrentText("شروع شده")
            
            print("✅ فیلدهای فرم با موفقیت پر شدند")
            
        except Exception as e:
            print(f"⚠️ خطا در پر کردن فیلدها: {e}")

    # ========== استایل‌ها ==========
    
    def get_style_sheet(self):
        """استایل‌شیت کلی"""
        return """
        QWidget {
            font-family: 'B Nazanin', Tahoma;
            background-color: #1e1e1e;
            color: white;
            font-size: 13px;
        }
        QLabel {
            font-size: 13px;
        }
        QPushButton {
            font-size: 13px;
        }
        QComboBox {
            font-size: 13px;
        }
        QLineEdit {
            font-size: 13px;
        }
        QTextEdit {
            font-size: 13px;
        }
        """
    
    def get_tab_style_sheet(self):
        """استایل تب‌ها"""
        return """
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
        """
    
    def get_groupbox_style(self, color):
        """استایل GroupBox"""
        return f"""
        QGroupBox {{
            font-size: 14px;
            font-weight: bold;
            color: {color};
            border: 2px solid {color};
            border-radius: 8px;
            margin-top: 10px;
            padding-top: 15px;
            background-color: #1e1e1e;
        }}
        QGroupBox::title {{
            subcontrol-origin: margin;
            subcontrol-position: top right;
            padding: 5px 15px;
            background-color: {color};
            color: white;
            border-radius: 4px;
        }}
        """
    
    def get_summary_label_style(self, color):
        """استایل برچسب خلاصه"""
        return f"""
        QLabel {{
            font-size: 14px;
            font-weight: bold;
            color: {color};
            background-color: #2c2c2c;
            padding: 12px 20px;
            border-radius: 6px;
            border: 1px solid {color};
        }}
        """
    
    def get_button_style(self, color):
        """استایل دکمه"""
        return f"""
        QPushButton {{
            background-color: {color};
            color: white;
            padding: 8px 15px;
            border-radius: 4px;
            font-weight: bold;
            border: none;
        }}
        QPushButton:hover {{
            background-color: {self.darken_color(color)};
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
        r, g, b = max(0, r-amount), max(0, g-amount), max(0, b-amount)
        return f'#{r:02x}{g:02x}{b:02x}'
    
    def set_font(self):
        """تنظیم فونت"""
        font = QFont()
        font.setFamily("B Nazanin")
        font.setPointSize(10)
        self.setFont(font)

    def closeEvent(self, event):
        """مدیریت بسته شدن پنجره"""
        self.close_form()
        event.ignore()