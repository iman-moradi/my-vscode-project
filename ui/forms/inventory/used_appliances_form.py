# ui/forms/inventory/used_appliances_form.py
"""
فرم مدیریت انبار لوازم دست دوم - نسخه کامل متصل به دیتابیس
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QLineEdit, QComboBox, QTableWidget,
    QTableWidgetItem, QHeaderView, QMessageBox,
    QGroupBox, QFormLayout, QSpinBox, QDoubleSpinBox,
    QTextEdit, QFrame, QSizePolicy, QTabWidget,
    QStackedWidget, QCheckBox, QDateEdit, QFileDialog, QInputDialog
)
from PySide6.QtCore import Qt, QDate
from PySide6.QtGui import QFont, QColor, QPixmap
import jdatetime
from datetime import datetime
import os
import json

from .base_inventory_form import BaseInventoryForm
from .widgets.currency_converter import CurrencyConverter
from .widgets.inventory_date_input import InventoryDateInput
from .widgets.enhanced_combo import EnhancedComboBox
from .widgets.image_upload_widget import ImageUploadWidget


class UsedAppliancesForm(BaseInventoryForm):
    """فرم مدیریت انبار لوازم دست دوم - نسخه متصل به دیتابیس"""
    
    def __init__(self, parent=None):
        super().__init__("انبار لوازم دست دوم", parent)
        self.current_edit_id = None
        self.all_data = []
        self.photos_data = {}
        self.setup_ui()
        
        # بارگذاری داده‌ها با تاخیر
        from PySide6.QtCore import QTimer
        QTimer.singleShot(100, self.load_data)
    
    def setup_ui(self):
        """تنظیم رابط کاربری"""
        # هدر فرم
        self.create_header()
        
        # تب‌های مختلف
        self.tabs = QTabWidget()
        self.main_layout.addWidget(self.tabs)
        
        # تب اطلاعات اصلی
        self.create_main_tab()
        
        # تب اطلاعات فنی و تعمیرات
        self.create_technical_tab()
        
        # تب اطلاعات خرید و فروش
        self.create_financial_tab()
        
        # تب عکس‌ها و مدارک
        self.create_images_tab()
        
        # بخش جستجو
        self.create_search_section()
        
        # بخش لیست دستگاه‌ها
        self.create_table_section()
        
        # دکمه‌های عملیات
        self.create_action_buttons()
        
        # بخش خلاصه
        self.create_summary_section()
    
    def create_header(self):
        """ایجاد هدر فرم"""
        header_frame = QFrame()
        header_frame.setFrameShape(QFrame.StyledPanel)
        header_layout = QHBoxLayout()
        
        title_label = QLabel("🔄 انبار لوازم دست دوم")
        title_label.setStyleSheet("""
            QLabel {
                font-size: 18px;
                font-weight: bold;
                color: #ff9900;
                padding: 10px;
            }
        """)
        
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        
        # آمار سریع
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(20)
        
        self.total_items_label = QLabel("تعداد کل: 0 دستگاه")
        self.total_items_label.setStyleSheet("color: #27ae60; font-weight: bold;")
        
        self.available_label = QLabel("موجود: 0 دستگاه")
        self.available_label.setStyleSheet("color: #3498db; font-weight: bold;")
        
        self.sold_label = QLabel("فروخته شده: 0 دستگاه")
        self.sold_label.setStyleSheet("color: #e74c3c; font-weight: bold;")
        
        self.total_profit_label = QLabel("سود کل: 0 تومان")
        self.total_profit_label.setStyleSheet("color: #9b59b6; font-weight: bold;")
        
        stats_layout.addWidget(self.total_profit_label)
        stats_layout.addWidget(self.sold_label)
        stats_layout.addWidget(self.available_label)
        stats_layout.addWidget(self.total_items_label)
        
        header_layout.addLayout(stats_layout)
        header_frame.setLayout(header_layout)
        
        self.main_layout.addWidget(header_frame)
    
    def create_main_tab(self):
        """ایجاد تب اطلاعات اصلی"""
        main_tab = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(15)
        
        # بخش اطلاعات دستگاه
        device_group, device_layout = self.create_form_group("📱 اطلاعات دستگاه")
        
        # ردیف 1: دسته‌بندی و برند
        row1_layout = QHBoxLayout()
        row1_layout.setSpacing(15)
        
        self.device_type = EnhancedComboBox('category')
        self.device_type.combo.setPlaceholderText("-- انتخاب دسته‌بندی --")
        
        self.brand = EnhancedComboBox('brand')
        self.brand.combo.setPlaceholderText("-- انتخاب برند --")
        
        row1_layout.addWidget(QLabel("برند:"))
        row1_layout.addWidget(self.brand, 2)
        row1_layout.addWidget(QLabel("دسته‌بندی:"))
        row1_layout.addWidget(self.device_type, 1)
        
        device_layout.addRow(row1_layout)
        
        # ردیف 2: مدل و شماره سریال
        row2_layout = QHBoxLayout()
        row2_layout.setSpacing(15)
        
        self.model = QLineEdit()
        self.model.setPlaceholderText("مدل دستگاه")
        
        self.serial_number = QLineEdit()
        self.serial_number.setPlaceholderText("شماره سریال (اختیاری)")
        
        row2_layout.addWidget(QLabel("شماره سریال:"))
        row2_layout.addWidget(self.serial_number, 1)
        row2_layout.addWidget(QLabel("مدل:"))
        row2_layout.addWidget(self.model, 2)
        
        device_layout.addRow(row2_layout)
        
        # ردیف 3: سال تولید و وضعیت
        row3_layout = QHBoxLayout()
        row3_layout.setSpacing(15)
        
        self.production_year = QSpinBox()
        self.production_year.setRange(1300, 1410)
        self.production_year.setValue(1400)
        self.production_year.setMaximumWidth(120)
        
        self.condition = QComboBox()
        self.condition.addItems([
            "در حد نو",
            "خیلی خوب", 
            "خوب",
            "متوسط",
            "نیاز به تعمیر جزئی",
            "نیاز به تعمیر اساسی"
        ])
        
        row3_layout.addWidget(QLabel("وضعیت:"))
        row3_layout.addWidget(self.condition, 2)
        row3_layout.addWidget(QLabel("سال تولید:"))
        row3_layout.addWidget(self.production_year, 1)
        
        device_layout.addRow(row3_layout)
        
        # ردیف 4: تعداد و محل نگهداری
        row4_layout = QHBoxLayout()
        row4_layout.setSpacing(15)
        
        self.quantity = QSpinBox()
        self.quantity.setRange(1, 100)
        self.quantity.setValue(1)
        self.quantity.setMaximumWidth(100)
        
        self.location = QLineEdit()
        self.location.setPlaceholderText("مثلاً: انبار شماره ۱، قفسه A-3")
        
        row4_layout.addWidget(QLabel("محل نگهداری:"))
        row4_layout.addWidget(self.location, 2)
        row4_layout.addWidget(QLabel("تعداد:"))
        row4_layout.addWidget(self.quantity, 1)
        
        device_layout.addRow(row4_layout)
        
        layout.addWidget(device_group)
        
        # بخش منبع دستگاه
        source_group, source_layout = self.create_form_group("🏷️ منبع دستگاه")
        
        # انتخاب نوع منبع
        row5_layout = QHBoxLayout()
        row5_layout.setSpacing(15)
        
        self.source_type = QComboBox()
        self.source_type.addItems(["مشتری", "تامین کننده", "تعویض شده"])
        self.source_type.currentIndexChanged.connect(self.on_source_type_changed)
        
        row5_layout.addWidget(QLabel("نوع منبع:"))
        row5_layout.addWidget(self.source_type, 1)
        row5_layout.addStretch()
        
        source_layout.addRow(row5_layout)
        
        # StackedWidget برای نمایش فیلد مناسب
        self.source_stack = QStackedWidget()
        
        # ویجت برای مشتری
        customer_widget = QWidget()
        customer_layout = QHBoxLayout()
        customer_layout.setContentsMargins(0, 0, 0, 0)
        
        self.customer = EnhancedComboBox('customer')
        self.customer.combo.setPlaceholderText("-- انتخاب مشتری --")
        
        customer_layout.addWidget(QLabel("مشتری:"))
        customer_layout.addWidget(self.customer)
        customer_widget.setLayout(customer_layout)
        
        # ویجت برای تامین‌کننده
        supplier_widget = QWidget()
        supplier_layout = QHBoxLayout()
        supplier_layout.setContentsMargins(0, 0, 0, 0)
        
        self.supplier = EnhancedComboBox('supplier')
        self.supplier.combo.setPlaceholderText("-- انتخاب تامین‌کننده --")
        
        supplier_layout.addWidget(QLabel("تامین‌کننده:"))
        supplier_layout.addWidget(self.supplier)
        supplier_widget.setLayout(supplier_layout)
        
        # ویجت برای تعویض شده (پذیرش)
        exchange_widget = QWidget()
        exchange_layout = QHBoxLayout()
        exchange_layout.setContentsMargins(0, 0, 0, 0)
        
        self.reception = EnhancedComboBox('reception')
        self.reception.combo.setPlaceholderText("-- انتخاب پذیرش --")
        
        exchange_layout.addWidget(QLabel("پذیرش:"))
        exchange_layout.addWidget(self.reception)
        exchange_widget.setLayout(exchange_layout)
        
        self.source_stack.addWidget(customer_widget)
        self.source_stack.addWidget(supplier_widget)
        self.source_stack.addWidget(exchange_widget)
        
        source_layout.addRow(self.source_stack)
        
        # ردیف 6: تاریخ خرید و سند خرید
        row6_layout = QHBoxLayout()
        row6_layout.setSpacing(15)
        
        self.purchase_date = InventoryDateInput()
        self.purchase_date.set_date_to_today()
        
        self.purchase_document = QLineEdit()
        self.purchase_document.setPlaceholderText("شماره سند خرید (اختیاری)")
        
        row6_layout.addWidget(QLabel("سند خرید:"))
        row6_layout.addWidget(self.purchase_document, 2)
        row6_layout.addWidget(QLabel("تاریخ خرید:"))
        row6_layout.addWidget(self.purchase_date, 1)
        
        source_layout.addRow(row6_layout)
        
        layout.addWidget(source_group)
        
        # بخش لوازم همراه
        accessories_group, accessories_layout = self.create_form_group("🎁 لوازم همراه")
        
        self.accessories = QTextEdit()
        self.accessories.setMaximumHeight(80)
        self.accessories.setPlaceholderText("لوازم همراه (ریموت، دفترچه راهنما، کابل، ...)")
        
        accessories_layout.addRow(self.accessories)
        
        layout.addWidget(accessories_group)
        
        # بخش توضیحات
        description_group, description_layout = self.create_form_group("📝 توضیحات")
        
        self.description = QTextEdit()
        self.description.setMaximumHeight(100)
        self.description.setPlaceholderText("توضیحات تکمیلی درباره دستگاه...")
        
        description_layout.addRow(self.description)
        
        layout.addWidget(description_group)
        
        main_tab.setLayout(layout)
        self.tabs.addTab(main_tab, "اطلاعات اصلی")
    
    def create_technical_tab(self):
        """ایجاد تب اطلاعات فنی"""
        tech_tab = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(15)
        
        # بخش وضعیت فنی
        tech_group, tech_layout = self.create_form_group("⚙️ وضعیت فنی")
        
        self.technical_status = QTextEdit()
        self.technical_status.setMaximumHeight(100)
        self.technical_status.setPlaceholderText("شرح دقیق وضعیت فنی دستگاه...")
        
        tech_layout.addRow(self.technical_status)
        
        # ردیف 1: تاریخ آخرین تعمیر
        row1_layout = QHBoxLayout()
        row1_layout.setSpacing(15)
        
        self.last_repair_date = InventoryDateInput()
        
        row1_layout.addWidget(QLabel("تاریخ آخرین تعمیر:"))
        row1_layout.addWidget(self.last_repair_date)
        row1_layout.addStretch()
        
        tech_layout.addRow(row1_layout)
        
        # بخش تاریخچه تعمیرات
        history_group, history_layout = self.create_form_group("📋 تاریخچه تعمیرات")
        
        self.repair_history = QTextEdit()
        self.repair_history.setMaximumHeight(150)
        self.repair_history.setPlaceholderText("تاریخچه کامل تعمیرات انجام شده...")
        
        history_layout.addRow(self.repair_history)
        
        layout.addWidget(tech_group)
        layout.addWidget(history_group)
        
        tech_tab.setLayout(layout)
        self.tabs.addTab(tech_tab, "اطلاعات فنی")
    
    def create_financial_tab(self):
        """ایجاد تب اطلاعات مالی"""
        financial_tab = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(15)
        
        # بخش قیمت‌ها
        price_group, price_layout = self.create_form_group("💰 قیمت‌گذاری")
        
        # ردیف 1: قیمت خرید
        row1_layout = QHBoxLayout()
        row1_layout.setSpacing(15)
        
        self.purchase_price = CurrencyConverter()
        self.purchase_price.set_value(0)
        
        row1_layout.addWidget(QLabel("قیمت خرید:"))
        row1_layout.addWidget(self.purchase_price)
        row1_layout.addStretch()
        
        price_layout.addRow(row1_layout)
        
        # ردیف 2: قیمت فروش و سود
        row2_layout = QHBoxLayout()
        row2_layout.setSpacing(15)
        
        self.sale_price = CurrencyConverter()
        self.sale_price.set_value(0)
        self.sale_price.value_changed.connect(self.calculate_profit)
        
        self.profit_label = QLabel("سود مورد انتظار: ۰ تومان")
        self.profit_label.setStyleSheet("color: #27ae60; font-weight: bold;")
        
        row2_layout.addWidget(self.profit_label)
        row2_layout.addWidget(QLabel("قیمت فروش:"))
        row2_layout.addWidget(self.sale_price)
        
        price_layout.addRow(row2_layout)
        
        layout.addWidget(price_group)
        
        # بخش گارانتی
        warranty_group, warranty_layout = self.create_form_group("🛡️ گارانتی")
        
        # ردیف 1: نوع گارانتی
        row3_layout = QHBoxLayout()
        row3_layout.setSpacing(15)
        
        self.warranty_type = QComboBox()
        self.warranty_type.addItems([
            "گارانتی فروشگاه",
            "گارانتی کارخانه", 
            "فاقد گارانتی"
        ])
        
        row3_layout.addWidget(QLabel("نوع گارانتی:"))
        row3_layout.addWidget(self.warranty_type, 1)
        row3_layout.addStretch()
        
        warranty_layout.addRow(row3_layout)
        
        # ردیف 2: روزهای گارانتی
        row4_layout = QHBoxLayout()
        row4_layout.setSpacing(15)
        
        self.warranty_days = QSpinBox()
        self.warranty_days.setRange(0, 3650)
        self.warranty_days.setValue(90)
        self.warranty_days.setMaximumWidth(120)
        
        self.warranty_description = QLineEdit()
        self.warranty_description.setPlaceholderText("شرح گارانتی (اختیاری)")
        
        row4_layout.addWidget(QLabel("شرح گارانتی:"))
        row4_layout.addWidget(self.warranty_description, 2)
        row4_layout.addWidget(QLabel("روزهای گارانتی:"))
        row4_layout.addWidget(self.warranty_days, 1)
        
        warranty_layout.addRow(row4_layout)
        
        layout.addWidget(warranty_group)
        
        # بخش وضعیت
        status_group, status_layout = self.create_form_group("📊 وضعیت")
        
        # ردیف 1: وضعیت فعلی
        row5_layout = QHBoxLayout()
        row5_layout.setSpacing(15)
        
        self.status = QComboBox()
        self.status.addItems([
            "موجود",
            "ناموجود",
            "فروخته شده",
            "در حال تعمیر",
            "رزرو شده",
            "اسقاط"
        ])
        
        self.entry_date = InventoryDateInput()
        self.entry_date.set_date_to_today()
        
        row5_layout.addWidget(QLabel("تاریخ ورود:"))
        row5_layout.addWidget(self.entry_date, 1)
        row5_layout.addWidget(QLabel("وضعیت:"))
        row5_layout.addWidget(self.status, 1)
        
        status_layout.addRow(row5_layout)
        
        layout.addWidget(status_group)
        
        financial_tab.setLayout(layout)
        self.tabs.addTab(financial_tab, "اطلاعات مالی")
    
    def create_images_tab(self):
        """ایجاد تب عکس‌ها"""
        images_tab = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(15)
        
        # ویجت آپلود عکس
        self.image_uploader = ImageUploadWidget()
        self.image_uploader.images_uploaded.connect(self.on_images_uploaded)
        
        layout.addWidget(self.image_uploader)
        
        images_tab.setLayout(layout)
        self.tabs.addTab(images_tab, "📷 عکس‌ها و مدارک")
    
    def create_search_section(self):
        """ایجاد بخش جستجو"""
        search_group, search_layout = self.create_form_group("🔍 جستجوی پیشرفته")
        
        # ردیف اول جستجو
        row1_layout = QHBoxLayout()
        row1_layout.setSpacing(15)
        
        # جستجوی متن آزاد
        self.search_keyword = QLineEdit()
        self.search_keyword.setPlaceholderText("جستجو در مدل، سریال، توضیحات...")
        
        # فیلتر وضعیت
        self.status_filter = QComboBox()
        self.status_filter.addItems([
            "همه وضعیت‌ها", 
            "موجود", 
            "فروخته شده", 
            "در حال تعمیر",
            "رزرو شده"
        ])
        
        # فیلتر وضعیت فنی
        self.condition_filter = QComboBox()
        self.condition_filter.addItems([
            "همه وضعیت‌ها",
            "در حد نو",
            "خیلی خوب",
            "خوب",
            "متوسط",
            "نیاز به تعمیر"
        ])
        
        row1_layout.addWidget(QLabel("وضعیت فنی:"))
        row1_layout.addWidget(self.condition_filter)
        row1_layout.addWidget(QLabel("وضعیت:"))
        row1_layout.addWidget(self.status_filter)
        row1_layout.addWidget(QLabel("جستجو:"))
        row1_layout.addWidget(self.search_keyword, 2)
        
        search_layout.addRow(row1_layout)
        
        # ردیف دوم: فیلترهای پیشرفته
        row2_layout = QHBoxLayout()
        row2_layout.setSpacing(15)
        
        # فیلتر دسته‌بندی
        self.filter_device_type = EnhancedComboBox('category')
        self.filter_device_type.combo.setPlaceholderText("همه دسته‌بندی‌ها")
        
        # فیلتر برند
        self.filter_brand = EnhancedComboBox('brand')
        self.filter_brand.combo.setPlaceholderText("همه برندها")
        
        # فیلتر منبع
        self.filter_source = QComboBox()
        self.filter_source.addItems([
            "همه منابع",
            "مشتری",
            "تامین کننده",
            "تعویض شده"
        ])
        
        row2_layout.addWidget(QLabel("منبع:"))
        row2_layout.addWidget(self.filter_source)
        row2_layout.addWidget(QLabel("برند:"))
        row2_layout.addWidget(self.filter_brand)
        row2_layout.addWidget(QLabel("دسته‌بندی:"))
        row2_layout.addWidget(self.filter_device_type)
        
        search_layout.addRow(row2_layout)
        
        # ردیف سوم: بازه قیمت و سال
        row3_layout = QHBoxLayout()
        row3_layout.setSpacing(15)
        
        # بازه قیمت خرید
        self.min_purchase_price = QLineEdit()
        self.min_purchase_price.setPlaceholderText("حداقل قیمت خرید")
        self.min_purchase_price.setMaximumWidth(150)
        
        self.max_purchase_price = QLineEdit()
        self.max_purchase_price.setPlaceholderText("حداکثر قیمت خرید")
        self.max_purchase_price.setMaximumWidth(150)
        
        # بازه سال تولید
        self.min_year = QSpinBox()
        self.min_year.setRange(1300, 1410)
        self.min_year.setValue(1380)
        self.min_year.setMaximumWidth(100)
        
        self.max_year = QSpinBox()
        self.max_year.setRange(1300, 1410)
        self.max_year.setValue(1410)
        self.max_year.setMaximumWidth(100)
        
        row3_layout.addWidget(QLabel("تا سال:"))
        row3_layout.addWidget(self.max_year)
        row3_layout.addWidget(QLabel("از سال:"))
        row3_layout.addWidget(self.min_year)
        row3_layout.addWidget(QLabel("حداکثر قیمت خرید:"))
        row3_layout.addWidget(self.max_purchase_price)
        row3_layout.addWidget(QLabel("حداقل قیمت خرید:"))
        row3_layout.addWidget(self.min_purchase_price)
        
        search_layout.addRow(row3_layout)
        
        # دکمه‌های جستجو
        btn_layout = QHBoxLayout()
        
        btn_clear = QPushButton("🗑️ پاک کردن فیلترها")
        btn_clear.clicked.connect(self.clear_search_filters)
        btn_clear.setMaximumWidth(150)
        
        btn_search = QPushButton("🔍 جستجوی پیشرفته")
        btn_search.clicked.connect(self.perform_search)
        btn_search.setMaximumWidth(150)
        
        btn_layout.addStretch()
        btn_layout.addWidget(btn_clear)
        btn_layout.addWidget(btn_search)
        
        search_layout.addRow(btn_layout)
        
        self.main_layout.addWidget(search_group)
        
        # تنظیم جستجوی زنده
        search_fields = [
            self.search_keyword,
            self.min_purchase_price,
            self.max_purchase_price
        ]
        
        for field in search_fields:
            self.setup_live_search(field, self.perform_search)
        
        # برای کامبوباکس‌ها
        self.filter_device_type.value_changed.connect(self.perform_search)
        self.filter_brand.value_changed.connect(self.perform_search)
        self.status_filter.currentIndexChanged.connect(self.perform_search)
        self.condition_filter.currentIndexChanged.connect(self.perform_search)
        self.filter_source.currentIndexChanged.connect(self.perform_search)
        
        # برای spin box‌ها
        self.min_year.valueChanged.connect(self.perform_search)
        self.max_year.valueChanged.connect(self.perform_search)
    
    def create_table_section(self):
        """ایجاد بخش جدول نمایش دستگاه‌ها"""
        table_group, table_layout = self.create_form_group("📋 لیست دستگاه‌های دست دوم")
        
        self.table = self.create_table([
            "ردیف",
            "دسته‌بندی",
            "برند/مدل",
            "سریال",
            "وضعیت فنی",
            "منبع",
            "قیمت خرید",
            "قیمت فروش",
            "سود",
            "وضعیت",
            "عملیات"
        ])
        
        # تنظیم عرض ستون‌ها
        self.table.setColumnWidth(0, 60)   # ردیف
        self.table.setColumnWidth(1, 120)  # دسته‌بندی
        self.table.setColumnWidth(2, 180)  # برند/مدل
        self.table.setColumnWidth(3, 120)  # سریال
        self.table.setColumnWidth(4, 120)  # وضعیت فنی
        self.table.setColumnWidth(5, 100)  # منبع
        self.table.setColumnWidth(6, 120)  # قیمت خرید
        self.table.setColumnWidth(7, 120)  # قیمت فروش
        self.table.setColumnWidth(8, 120)  # سود
        self.table.setColumnWidth(9, 100)  # وضعیت
        
        # تنظیم حداقل ارتفاع
        self.table.setMinimumHeight(350)
        
        table_layout.addRow(self.table)
        self.main_layout.addWidget(table_group)
    
    def create_action_buttons(self):
        """ایجاد دکمه‌های عملیات"""
        btn_group = QGroupBox("⚡ عملیات")
        btn_layout = QHBoxLayout()
        
        self.btn_save = QPushButton("💾 ذخیره دستگاه")
        self.btn_save.clicked.connect(self.save_data)
        self.btn_save.setProperty("style", "primary")
        
        self.btn_new = QPushButton("🆕 دستگاه جدید")
        self.btn_new.clicked.connect(self.clear_form)
        self.btn_new.setProperty("style", "info")
        
        self.btn_edit = QPushButton("✏️ ویرایش انتخاب شده")
        self.btn_edit.setEnabled(False)
        self.btn_edit.clicked.connect(self.on_edit)
        self.btn_edit.setProperty("style", "warning")
        
        # تغییر دکمه حذف به حذف با تراکنش
        self.btn_delete = QPushButton("🗑️ حذف با ثبت تراکنش")
        self.btn_delete.setEnabled(False)
        self.btn_delete.clicked.connect(self.on_delete_with_transaction)
        self.btn_delete.setProperty("style", "danger")
        
        # دکمه جدید برای حذف نرم
        self.btn_soft_delete = QPushButton("📝 حذف نرم (تغییر وضعیت)")
        self.btn_soft_delete.setEnabled(False)
        self.btn_soft_delete.clicked.connect(self.on_soft_delete)
        self.btn_soft_delete.setProperty("style", "secondary")
        
        self.btn_sell = QPushButton("💰 ثبت فروش")
        self.btn_sell.setEnabled(False)
        self.btn_sell.clicked.connect(self.on_sell)
        self.btn_sell.setProperty("style", "success")
        
        self.btn_export = QPushButton("📊 خروجی Excel")
        self.btn_export.clicked.connect(self.export_excel)
        
        btn_layout.addWidget(self.btn_save)
        btn_layout.addWidget(self.btn_new)
        btn_layout.addWidget(self.btn_edit)
        btn_layout.addWidget(self.btn_delete)
        btn_layout.addWidget(self.btn_soft_delete)  # اضافه کردن دکمه حذف نرم
        btn_layout.addWidget(self.btn_sell)
        btn_layout.addWidget(self.btn_export)
        
        btn_group.setLayout(btn_layout)
        self.main_layout.addWidget(btn_group)
        
        # اتصال انتخاب جدول
        self.table.itemSelectionChanged.connect(self.on_table_selection_changed)
    
    def create_summary_section(self):
        """ایجاد بخش خلاصه"""
        summary_group = QGroupBox("📊 خلاصه آمار")
        summary_layout = QHBoxLayout()
        
        # کارت‌های آمار
        stats = [
            ("تعداد کل", "📦", "3498db", "0 دستگاه"),
            ("ارزش کل", "💰", "27ae60", "0 تومان"),
            ("سود کل", "📈", "9b59b6", "0 تومان"),
            ("میانگین سود", "💹", "f39c12", "0 تومان"),
        ]
        
        for title, icon, color, value in stats:
            card = self.create_stat_card(title, icon, color, value)
            summary_layout.addWidget(card)
        
        summary_group.setLayout(summary_layout)
        self.main_layout.addWidget(summary_group)
    
    def on_source_type_changed(self, index):
        """هنگام تغییر نوع منبع"""
        self.source_stack.setCurrentIndex(index)
    
    def calculate_profit(self):
        """محاسبه سود"""
        try:
            purchase_price = self.purchase_price.get_value_toman()
            sale_price = self.sale_price.get_value_toman()
            profit = sale_price - purchase_price
            
            self.profit_label.setText(f"سود مورد انتظار: {self.format_currency(profit)}")
            
            # تغییر رنگ بر اساس مثبت/منفی بودن سود
            if profit > 0:
                self.profit_label.setStyleSheet("color: #27ae60; font-weight: bold;")
            elif profit < 0:
                self.profit_label.setStyleSheet("color: #e74c3c; font-weight: bold;")
            else:
                self.profit_label.setStyleSheet("color: #f39c12; font-weight: bold;")
                
        except:
            self.profit_label.setText("سود مورد انتظار: ۰ تومان")
    
    def on_images_uploaded(self, image_paths):
        """هنگام آپلود عکس‌ها"""
        self.photos_data = image_paths
    
    def load_data(self):
        """بارگذاری داده‌ها از دیتابیس"""
        print("🔄 در حال بارگذاری داده‌های لوازم دست دوم از دیتابیس...")
        try:
            if self.data_manager and hasattr(self.data_manager, 'warehouse'):
                self.load_from_database()
            else:
                print("⚠️ data_manager یا warehouse موجود نیست")
                self.load_sample_data()
        except Exception as e:
            print(f"❌ خطا در بارگذاری داده‌ها: {e}")
            import traceback
            traceback.print_exc()
            self.load_sample_data()
    
    def load_from_database(self):
        """بارگذاری از دیتابیس واقعی"""
        print("💾 بارگذاری از دیتابیس واقعی...")
        try:
            # دریافت داده‌ها از دیتابیس
            warehouse_items = self.data_manager.warehouse.get_used_appliances_stock()
            
            if warehouse_items:
                self.all_data = []
                for item in warehouse_items:
                    # تبدیل داده‌های دیتابیس به فرمت قابل نمایش در فرم
                    data_item = {
                        'id': item.get('id'),
                        'device_type': item.get('device_type_name', 'نامشخص'),
                        'device_type_id': item.get('device_type_id'),
                        'brand': item.get('brand_name', 'نامشخص'),
                        'brand_id': item.get('brand_id'),
                        'model': item.get('model', ''),
                        'serial_number': item.get('serial_number', ''),
                        'production_year': item.get('production_year', 1400),
                        'condition': item.get('condition', 'خوب'),
                        'source_type': item.get('source_type', 'مشتری'),
                        'source_name': item.get('source_name', ''),
                        'source_person_id': item.get('source_person_id'),
                        'purchase_price': item.get('purchase_price', 0),
                        'sale_price': item.get('sale_price', 0),
                        'status': item.get('status', 'موجود'),
                        'purchase_date': item.get('purchase_date', ''),
                        'entry_date': item.get('entry_date', ''),
                        'location': item.get('location', ''),
                        'technical_status': item.get('technical_status', ''),
                        'warranty_type': item.get('warranty_type', 'گارانتی فروشگاه'),
                        'warranty_days': item.get('warranty_days', 90),
                        'description': item.get('description', ''),
                        'accessories': item.get('accessories', ''),
                        'quantity': item.get('quantity', 1)
                    }
                    
                    # اگر منبع تعویض شده است، reception_id را اضافه کن
                    if item.get('source_type') == 'تعویض شده' and item.get('original_reception_id'):
                        data_item['reception_id'] = item.get('original_reception_id')
                    
                    self.all_data.append(data_item)
                
                print(f"✅ {len(self.all_data)} دستگاه از دیتابیس بارگذاری شد")
                self.populate_table(self.all_data)
                self.update_stats(self.all_data)
            else:
                print("⚠️ دیتابیس لوازم دست دوم خالی است")
                self.load_sample_data()
                
        except Exception as e:
            print(f"❌ خطا در بارگذاری از دیتابیس: {e}")
            import traceback
            traceback.print_exc()
            self.load_sample_data()
    
    def load_sample_data(self):
        """بارگذاری داده‌های نمونه (برای مواقعی که دیتابیس خالی است)"""
        print("📋 بارگذاری داده‌های نمونه...")
        
        # ابتدا سعی می‌کنیم از دیتابیس اطلاعات پایه بگیریم
        try:
            # دریافت دسته‌بندی‌ها و برندها از دیتابیس
            categories = self.data_manager.device_category.get_all_devices() if hasattr(self.data_manager, 'device_category') else []
            brands = self.data_manager.brand.get_all_brands() if hasattr(self.data_manager, 'brand') else []
            
            sample_data = []
            
            # فقط اگر دیتابیس خالی است، نمونه‌های ساختگی ایجاد کن
            if not categories or not brands:
                print("⚠️ دیتابیس پایه خالی است، از داده‌های نمونه استفاده می‌کنیم")
                sample_data = [
                    {
                        'id': 1,
                        'device_type': 'یخچال',
                        'device_type_id': 1,
                        'brand': 'سامسونگ',
                        'brand_id': 1,
                        'model': 'RT38K5932SL',
                        'serial_number': 'SN-2023-001',
                        'production_year': 1400,
                        'condition': 'خیلی خوب',
                        'source_type': 'مشتری',
                        'source_name': 'رضا احمدی (09121234567)',
                        'source_person_id': 1,
                        'purchase_price': 15000000,
                        'sale_price': 20000000,
                        'status': 'موجود',
                        'purchase_date': '1402-10-15',
                        'entry_date': '1402-10-15',
                        'location': 'انبار شماره ۱',
                        'technical_status': 'کاملاً سالم، کمپرسور تعویض شده',
                        'warranty_type': 'گارانتی فروشگاه',
                        'warranty_days': 90,
                        'description': 'یخچال ساید سامسونگ، تعمیر شده',
                        'accessories': 'ریموت، دفترچه راهنما',
                        'quantity': 1
                    }
                ]
            else:
                print("✅ داده‌های پایه از دیتابیس بارگذاری شدند")
                # از داده‌های واقعی استفاده می‌کنیم اما نمایش نمونه نداریم
                return
            
            self.all_data = sample_data
            self.populate_table(sample_data)
            self.update_stats(sample_data)
            print(f"✅ {len(sample_data)} دستگاه نمونه بارگذاری شد")
            
        except Exception as e:
            print(f"❌ خطا در بارگذاری داده‌های نمونه: {e}")
            # اگر خطا داشتیم، یک لیست خالی نمایش بده
            self.all_data = []
            self.populate_table([])
            self.update_stats([])
    
    def populate_table(self, data):
        """پر کردن جدول با داده‌ها"""
        self.table.setRowCount(len(data))
        
        for row, item in enumerate(data):
            # ردیف
            self.table.setItem(row, 0, QTableWidgetItem(str(row + 1)))
            self.table.item(row, 0).setTextAlignment(Qt.AlignCenter)
            
            # دسته‌بندی
            self.table.setItem(row, 1, QTableWidgetItem(item.get('device_type', '')))
            
            # برند/مدل
            brand_model = f"{item.get('brand', '')} - {item.get('model', '')}"
            self.table.setItem(row, 2, QTableWidgetItem(brand_model))
            
            # شماره سریال
            self.table.setItem(row, 3, QTableWidgetItem(item.get('serial_number', '')))
            
            # وضعیت فنی
            condition_item = QTableWidgetItem(item.get('condition', ''))
            condition_item.setTextAlignment(Qt.AlignCenter)
            
            # رنگ‌آمیزی وضعیت فنی
            condition = item.get('condition', '')
            if condition == 'در حد نو':
                condition_item.setBackground(QColor('#27ae60'))
            elif condition == 'خیلی خوب':
                condition_item.setBackground(QColor('#2ecc71'))
            elif condition == 'خوب':
                condition_item.setBackground(QColor('#f39c12'))
            elif condition == 'متوسط':
                condition_item.setBackground(QColor('#e67e22'))
            elif 'تعمیر' in condition:
                condition_item.setBackground(QColor('#e74c3c'))
            
            condition_item.setForeground(QColor('white'))
            self.table.setItem(row, 4, condition_item)
            
            # منبع
            source_type = item.get('source_type', '')
            source_text = source_type
            if source_type == 'مشتری':
                source_text = 'مشتری'
            elif source_type == 'تامین کننده':
                source_text = 'تامین‌کننده'
            elif source_type == 'تعویض شده':
                source_text = 'تعویض شده'
            
            source_item = QTableWidgetItem(source_text)
            source_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row, 5, source_item)
            
            # قیمت خرید
            purchase_price = item.get('purchase_price', 0)
            self.table.setItem(row, 6, QTableWidgetItem(self.format_currency(purchase_price)))
            
            # قیمت فروش
            sale_price = item.get('sale_price', 0)
            self.table.setItem(row, 7, QTableWidgetItem(self.format_currency(sale_price)))
            
            # سود
            profit = sale_price - purchase_price
            profit_item = QTableWidgetItem(self.format_currency(profit))
            profit_item.setTextAlignment(Qt.AlignCenter)
            
            if profit > 0:
                profit_item.setForeground(QColor('#27ae60'))
            elif profit < 0:
                profit_item.setForeground(QColor('#e74c3c'))
            
            self.table.setItem(row, 8, profit_item)
            
            # وضعیت
            status = item.get('status', '')
            status_item = QTableWidgetItem(status)
            status_item.setTextAlignment(Qt.AlignCenter)
            
            # رنگ‌آمیزی وضعیت
            if status == 'موجود':
                status_item.setBackground(QColor('#27ae60'))
            elif status == 'فروخته شده':
                status_item.setBackground(QColor('#3498db'))
            elif status == 'در حال تعمیر':
                status_item.setBackground(QColor('#f39c12'))
            elif status == 'رزرو شده':
                status_item.setBackground(QColor('#9b59b6'))
            elif status == 'اسقاط':
                status_item.setBackground(QColor('#7f8c8d'))
            
            status_item.setForeground(QColor('white'))
            self.table.setItem(row, 9, status_item)
            
            # عملیات
            btn_widget = QWidget()
            btn_layout = QHBoxLayout()
            btn_layout.setContentsMargins(2, 2, 2, 2)

            btn_view = QPushButton("👁️")
            btn_view.setFixedSize(35, 35)
            btn_view.setToolTip("مشاهده جزئیات")
            btn_view.clicked.connect(lambda checked, idx=item['id']: self.view_item(idx))

            btn_edit = QPushButton("✏️")
            btn_edit.setFixedSize(35, 35)
            btn_edit.setToolTip("ویرایش دستگاه")
            btn_edit.clicked.connect(lambda checked, idx=item['id']: self.edit_item(idx))

            # دکمه حذف اصلی - حذف با تراکنش
            btn_delete = QPushButton("🗑️")
            btn_delete.setFixedSize(35, 35)
            btn_delete.setToolTip("حذف با ثبت تراکنش")
            btn_delete.clicked.connect(lambda checked, idx=item['id']: self.on_delete_with_transaction_for_item(idx))

            # دکمه حذف نرم
            btn_soft_delete = QPushButton("📝")
            btn_soft_delete.setFixedSize(35, 35)
            btn_soft_delete.setToolTip("حذف نرم (تغییر وضعیت)")
            btn_soft_delete.clicked.connect(lambda checked, idx=item['id']: self.on_soft_delete_for_item(idx))

            btn_layout.addWidget(btn_view)
            btn_layout.addWidget(btn_edit)
            btn_layout.addWidget(btn_delete)
            btn_layout.addWidget(btn_soft_delete)
            btn_layout.addStretch()

            btn_widget.setLayout(btn_layout)
            self.table.setCellWidget(row, 10, btn_widget)
    
    def update_stats(self, data):
        """به‌روزرسانی آمار"""
        try:
            total_items = len(data)
            available = sum(1 for item in data if item.get('status') == 'موجود')
            sold = sum(1 for item in data if item.get('status') == 'فروخته شده')
            
            total_purchase_value = sum(item.get('purchase_price', 0) for item in data)
            total_sale_value = sum(item.get('sale_price', 0) for item in data if item.get('status') != 'فروخته شده')
            total_profit = sum((item.get('sale_price', 0) - item.get('purchase_price', 0)) 
                              for item in data if item.get('status') == 'فروخته شده')
            
            avg_profit = total_profit / sold if sold > 0 else 0
            
            # به‌روزرسانی برچسب‌های هدر
            self.total_items_label.setText(f"تعداد کل: {total_items:,} دستگاه")
            self.available_label.setText(f"موجود: {available:,} دستگاه")
            self.sold_label.setText(f"فروخته شده: {sold:,} دستگاه")
            self.total_profit_label.setText(f"سود کل: {self.format_currency(total_profit)}")
            
            # به‌روزرسانی کارت‌های خلاصه
            for i in range(self.main_layout.count()):
                item = self.main_layout.itemAt(i)
                if item and hasattr(item.widget(), 'title'):
                    card = item.widget()
                    if card.title == "تعداد کل":
                        card.value_label.setText(f"{total_items:,} دستگاه")
                    elif card.title == "ارزش کل":
                        card.value_label.setText(self.format_currency(total_purchase_value))
                    elif card.title == "سود کل":
                        card.value_label.setText(self.format_currency(total_profit))
                    elif card.title == "میانگین سود":
                        card.value_label.setText(self.format_currency(avg_profit))
        except Exception as e:
            print(f"خطا در به‌روزرسانی آمار: {e}")
    
    def clear_search_filters(self):
        """پاک کردن فیلترهای جستجو"""
        self.search_keyword.clear()
        self.status_filter.setCurrentIndex(0)
        self.condition_filter.setCurrentIndex(0)
        self.filter_device_type.clear()
        self.filter_brand.clear()
        self.filter_source.setCurrentIndex(0)
        self.min_purchase_price.clear()
        self.max_purchase_price.clear()
        self.min_year.setValue(1380)
        self.max_year.setValue(1410)
        
        self.perform_search()
    
    def perform_search(self):
        """انجام جستجو"""
        try:
            # جمع‌آوری پارامترها
            filters = {
                'keyword': self.search_keyword.text().strip().lower(),
                'status': self.status_filter.currentText(),
                'condition': self.condition_filter.currentText(),
                'device_type_id': self.filter_device_type.get_value(),
                'brand_id': self.filter_brand.get_value(),
                'source_type': self.filter_source.currentText(),
                'min_price': self.min_purchase_price.text().strip(),
                'max_price': self.max_purchase_price.text().strip(),
                'min_year': self.min_year.value(),
                'max_year': self.max_year.value()
            }
            
            # فیلتر کردن داده‌ها
            filtered_data = []
            
            for item in self.all_data:
                match = True
                
                # فیلتر کلمه کلیدی
                if match and filters['keyword']:
                    keyword = filters['keyword']
                    search_fields = [
                        item.get('model', ''),
                        item.get('serial_number', ''),
                        item.get('description', ''),
                        item.get('brand', ''),
                        item.get('device_type', '')
                    ]
                    
                    if not any(keyword in str(field).lower() for field in search_fields):
                        match = False
                
                # فیلتر وضعیت
                if match and filters['status'] != 'همه وضعیت‌ها':
                    if filters['status'] != item.get('status', ''):
                        match = False
                
                # فیلتر وضعیت فنی
                if match and filters['condition'] != 'همه وضعیت‌ها':
                    if filters['condition'] != item.get('condition', ''):
                        if filters['condition'] == 'نیاز به تعمیر' and 'تعمیر' not in item.get('condition', ''):
                            match = False
                
                # فیلتر دسته‌بندی
                if match and filters['device_type_id']:
                    if filters['device_type_id'] != item.get('device_type_id', 0):
                        match = False
                
                # فیلتر برند
                if match and filters['brand_id']:
                    if filters['brand_id'] != item.get('brand_id', 0):
                        match = False
                
                # فیلتر منبع
                if match and filters['source_type'] != 'همه منابع':
                    if filters['source_type'] != item.get('source_type', ''):
                        match = False
                
                # فیلتر قیمت
                if match:
                    try:
                        purchase_price = item.get('purchase_price', 0)
                        
                        if filters['min_price']:
                            min_price = float(filters['min_price'])
                            if purchase_price < min_price:
                                match = False
                        
                        if match and filters['max_price']:
                            max_price = float(filters['max_price'])
                            if purchase_price > max_price:
                                match = False
                    except:
                        pass
                
                # فیلتر سال تولید
                if match:
                    year = item.get('production_year', 1400)
                    if year < filters['min_year'] or year > filters['max_year']:
                        match = False
                
                if match:
                    filtered_data.append(item)
            
            # نمایش نتایج
            self.populate_table(filtered_data)
            self.update_stats(filtered_data)
            
        except Exception as e:
            print(f"خطا در جستجو: {e}")
       
    def clear_form(self):
        """پاک کردن فرم"""
        self.current_edit_id = None
        self.tabs.setCurrentIndex(0)
        
        # تب اطلاعات اصلی
        self.device_type.clear()
        self.brand.clear()
        self.model.clear()
        self.serial_number.clear()
        self.production_year.setValue(1400)
        self.condition.setCurrentIndex(0)
        self.quantity.setValue(1)
        self.location.clear()
        self.source_type.setCurrentIndex(0)
        self.customer.clear()
        self.supplier.clear()
        self.reception.clear()
        self.purchase_date.set_date_to_today()
        self.purchase_document.clear()
        self.accessories.clear()
        self.description.clear()
        
        # تب اطلاعات فنی
        self.technical_status.clear()
        self.last_repair_date.clear()
        self.repair_history.clear()
        
        # تب اطلاعات مالی
        self.purchase_price.set_value(0)
        self.sale_price.set_value(0)
        self.calculate_profit()
        self.warranty_type.setCurrentIndex(0)
        self.warranty_days.setValue(90)
        self.warranty_description.clear()
        self.status.setCurrentIndex(0)
        self.entry_date.set_date_to_today()
        
        # تب عکس‌ها
        if hasattr(self, 'image_uploader'):
            self.image_uploader.clear()
        self.photos_data = {}
        
        self.btn_save.setText("💾 ذخیره دستگاه")
        self.btn_save.setProperty("style", "primary")
        self.table.clearSelection()
    
    # در انتهای فایل UsedAppliancesForm.py، بعد از تابع save_data:

    def validate_form(self):
        """اعتبارسنجی فرم - نسخه اصلاح شده"""
        errors = []
        
        # فقط فیلدهای ضروری را چک کن
        if self.device_type.get_value() == 0:
            errors.append("دسته‌بندی دستگاه الزامی است.")
        
        if self.brand.get_value() == 0:
            errors.append("برند دستگاه الزامی است.")
        
        if not self.model.text().strip():
            errors.append("مدل دستگاه الزامی است.")
        
        try:
            purchase_price = float(self.purchase_price.get_value_toman())
            if purchase_price <= 0:
                errors.append("قیمت خرید باید بزرگتر از صفر باشد.")
        except:
            errors.append("قیمت خرید نامعتبر است.")
        
        if errors:
            error_msg = "\n".join(f"• {error}" for error in errors)
            self.show_error(f"لطفا خطاهای زیر را اصلاح کنید:\n\n{error_msg}")
            return False
        
        return True


    def save_data(self):
        """ذخیره دستگاه در دیتابیس - نسخه اصلاح شده"""
        try:
            if not self.validate_form():
                return
            
            # آماده‌سازی داده‌ها
            source_type = self.source_type.currentText()
            source_person_id = None
            original_reception_id = None
            
            if source_type == "مشتری":
                source_person_id = self.customer.get_value()
            elif source_type == "تامین کننده":
                source_person_id = self.supplier.get_value()
            elif source_type == "تعویض شده":
                # برای تعویض شده، source_person_id را NULL می‌گذاریم
                source_person_id = None
                original_reception_id = self.reception.get_value()
            
            # تولید شماره سریال خودکار اگر خالی است
            serial_number = self.serial_number.text().strip()
            if not serial_number:
                import time
                timestamp = int(time.time() * 1000)
                serial_number = f"GEN-{timestamp}"
            
            # گرفتن تاریخ‌های شمسی
            purchase_date_shamsi = self.purchase_date.get_date_string() if self.purchase_date.text() else None
            last_repair_date_shamsi = self.last_repair_date.get_date_string() if self.last_repair_date.text() else None
            entry_date_shamsi = self.entry_date.get_date_string() if self.entry_date.text() else None
            
            # تبدیل به میلادی
            purchase_date_miladi = self.shamsi_to_miladi(purchase_date_shamsi) if purchase_date_shamsi else None
            last_repair_date_miladi = self.shamsi_to_miladi(last_repair_date_shamsi) if last_repair_date_shamsi else None
            entry_date_miladi = self.shamsi_to_miladi(entry_date_shamsi) if entry_date_shamsi else None
            
            # اگر تبدیل موفق نبود، از تاریخ امروز استفاده کن
            from PySide6.QtCore import QDate
            if not purchase_date_miladi:
                purchase_date_miladi = QDate.currentDate().toString("yyyy-MM-dd")
            if not entry_date_miladi:
                entry_date_miladi = QDate.currentDate().toString("yyyy-MM-dd")
            
            # ساختار داده صحیح برای جدول UsedAppliancesWarehouse
            data = {
                'device_type_id': self.device_type.get_value(),
                'brand_id': self.brand.get_value(),
                'model': self.model.text().strip(),
                'serial_number': serial_number,
                'production_year': self.production_year.value(),
                'source_type': source_type,
                'source_person_id': source_person_id,  # اینجا باید source_person_id باشد
                'original_reception_id': original_reception_id,
                'condition': self.condition.currentText(),
                'purchase_price': float(self.purchase_price.get_value_toman()),
                'purchase_date': purchase_date_miladi,
                'sale_price': float(self.sale_price.get_value_toman()),
                'quantity': self.quantity.value(),
                'status': self.status.currentText(),
                'description': self.description.toPlainText().strip(),
                'entry_date': entry_date_miladi,
                'purchase_document': self.purchase_document.text().strip(),
                'location': self.location.text().strip(),
                'technical_status': self.technical_status.toPlainText().strip(),
                'repair_history': self.repair_history.toPlainText().strip(),
                'warranty_type': self.warranty_type.currentText(),
                'warranty_days': self.warranty_days.value(),
                'warranty_description': self.warranty_description.text().strip(),
                'accessories': self.accessories.toPlainText().strip()
            }
            
            # اضافه کردن تاریخ آخرین تعمیر اگر وجود دارد
            if last_repair_date_miladi:
                data['last_repair_date'] = last_repair_date_miladi
            
            print(f"🔄 در حال ذخیره دستگاه...")
            print(f"   source_type: {source_type}")
            print(f"   source_person_id: {source_person_id}")
            print(f"   original_reception_id: {original_reception_id}")
            
            if self.current_edit_id:
                # ویرایش دستگاه موجود
                success = self.data_manager.warehouse.update_warehouse_item(
                    'لوازم دست دوم', 
                    self.current_edit_id, 
                    data
                )
                message = "ویرایش"
            else:
                # افزودن دستگاه جدید
                if source_type == "مشتری" or source_type == "تعویض شده":
                    result = self.data_manager.warehouse.add_used_appliance_from_customer(data)
                else:  # تامین کننده
                    result = self.data_manager.warehouse.add_used_appliance_from_supplier(data)
                
                message = "ثبت"
                # بررسی نتیجه
                if isinstance(result, tuple) and len(result) > 0:
                    success = result[0]
                else:
                    success = result
            
            if success:
                # نمایش پیام موفقیت
                self.show_success(f"دستگاه با موفقیت {message} شد.")
                
                # پاک کردن فرم و تازه‌سازی
                self.clear_form()
                self.load_data()
            else:
                self.show_error(f"خطا در {message} دستگاه. لطفاً مجدداً تلاش کنید.")
            
        except Exception as e:
            print(f"❌ خطا در ذخیره دستگاه: {e}")
            import traceback
            traceback.print_exc()
            self.show_error(f"خطا در ذخیره دستگاه: {str(e)}")

    def shamsi_to_miladi(self, shamsi_date_str, format_str="%Y-%m-%d"):
        """تبدیل تاریخ شمسی به میلادی"""
        if not shamsi_date_str:
            return None
        
        try:
            # وارد کردن jdatetime
            import jdatetime
            
            # جدا کردن اجزای تاریخ شمسی
            # فرمت می‌تواند YYYY-MM-DD یا YYYY/MM/DD باشد
            shamsi_date_str = str(shamsi_date_str).strip()
            
            # حذف کاراکترهای غیرعددی
            import re
            numbers = re.findall(r'\d+', shamsi_date_str)
            
            if len(numbers) >= 3:
                year, month, day = map(int, numbers[:3])
                
                # اگر سال بین 1300-1500 است، یعنی شمسی است
                if 1300 <= year <= 1500:
                    # تبدیل شمسی به میلادی
                    jalali = jdatetime.date(year, month, day)
                    gregorian = jalali.togregorian()
                    
                    if format_str == "%Y-%m-%d":
                        return gregorian.strftime("%Y-%m-%d")
                    elif format_str == "%Y/%m/%d":
                        return gregorian.strftime("%Y/%m/%d")
                    else:
                        return gregorian.strftime(format_str)
                else:
                    # احتمالاً میلادی است
                    return f"{year:04d}-{month:02d}-{day:02d}"
            else:
                # اگر نمی‌توانیم تبدیل کنیم، تاریخ امروز را برگردان
                from PySide6.QtCore import QDate
                return QDate.currentDate().toString("yyyy-MM-dd")
                
        except Exception as e:
            print(f"خطا در تبدیل تاریخ شمسی به میلادی: {e}")
            # در صورت خطا، تاریخ امروز برگردان
            from PySide6.QtCore import QDate
            return QDate.currentDate().toString("yyyy-MM-dd")

    def miladi_to_shamsi(self, miladi_date_str, format_str="%Y-%m-%d"):
        """تبدیل تاریخ میلادی به شمسی"""
        if not miladi_date_str:
            return ""
        
        try:
            import jdatetime
            
            # جدا کردن اجزای تاریخ میلادی
            miladi_date_str = str(miladi_date_str).strip()
            
            # حذف کاراکترهای غیرعددی
            import re
            numbers = re.findall(r'\d+', miladi_date_str)
            
            if len(numbers) >= 3:
                year, month, day = map(int, numbers[:3])
                
                # اگر سال بزرگتر از 1500 است، یعنی میلادی است
                if year > 1500:
                    # تبدیل میلادی به شمسی
                    from datetime import date
                    gregorian_date = date(year, month, day)
                    jalali = jdatetime.date.fromgregorian(date=gregorian_date)
                    
                    if format_str == "%Y-%m-%d":
                        return jalali.strftime("%Y-%m-%d")
                    elif format_str == "%Y/%m/%d":
                        return jalali.strftime("%Y/%m/%d")
                    else:
                        return jalali.strftime(format_str)
                else:
                    # احتمالاً شمسی است
                    return f"{year:04d}-{month:02d}-{day:02d}"
            else:
                return miladi_date_str
                
        except Exception as e:
            print(f"خطا در تبدیل تاریخ میلادی به شمسی: {e}")
            return miladi_date_str


    def view_item(self, item_id):
        """مشاهده جزئیات دستگاه"""
        try:
            # دریافت دستگاه از دیتابیس
            item_to_view = None
            for item in self.all_data:
                if item['id'] == item_id:
                    item_to_view = item
                    break
            
            if not item_to_view:
                self.show_error("دستگاه مورد نظر یافت نشد.")
                return
            
            # نمایش اطلاعات در یک پیام‌باکس
            details = f"""
            <b>🔍 جزئیات دستگاه #{item_id}</b>
            <hr>
            <b>دسته‌بندی:</b> {item_to_view.get('device_type', '')}<br>
            <b>برند/مدل:</b> {item_to_view.get('brand', '')} - {item_to_view.get('model', '')}<br>
            <b>شماره سریال:</b> {item_to_view.get('serial_number', '')}<br>
            <b>سال تولید:</b> {item_to_view.get('production_year', '')}<br>
            <b>وضعیت فنی:</b> {item_to_view.get('condition', '')}<br>
            <b>منبع:</b> {item_to_view.get('source_type', '')} - {item_to_view.get('source_name', '')}<br>
            <b>قیمت خرید:</b> {self.format_currency(item_to_view.get('purchase_price', 0))}<br>
            <b>قیمت فروش:</b> {self.format_currency(item_to_view.get('sale_price', 0))}<br>
            <b>سود:</b> {self.format_currency(item_to_view.get('sale_price', 0) - item_to_view.get('purchase_price', 0))}<br>
            <b>وضعیت:</b> {item_to_view.get('status', '')}<br>
            <b>محل نگهداری:</b> {item_to_view.get('location', '')}<br>
            <hr>
            <b>توضیحات:</b><br>
            {item_to_view.get('description', '')}
            """
            
            msg_box = QMessageBox(self)
            msg_box.setWindowTitle(f"جزئیات دستگاه #{item_id}")
            msg_box.setTextFormat(Qt.RichText)
            msg_box.setText(details)
            msg_box.setIcon(QMessageBox.Information)
            msg_box.exec()
            
        except Exception as e:
            print(f"خطا در مشاهده دستگاه: {e}")
    
    def edit_item(self, item_id):
        """ویرایش دستگاه - با تبدیل تاریخ میلادی به شمسی"""
        try:
            print(f"✏️ در حال بارگذاری دستگاه برای ویرایش ID: {item_id}")
            
            # پیدا کردن دستگاه در لیست
            item_to_edit = None
            for item in self.all_data:
                if item['id'] == item_id:
                    item_to_edit = item
                    break
            
            if not item_to_edit:
                self.show_error("دستگاه مورد نظر یافت نشد.")
                return
            
            self.current_edit_id = item_id
            
            # پر کردن فرم
            self.device_type.set_value(item_to_edit.get('device_type_id', 0))
            self.brand.set_value(item_to_edit.get('brand_id', 0))
            self.model.setText(item_to_edit.get('model', ''))
            self.serial_number.setText(item_to_edit.get('serial_number', ''))
            self.production_year.setValue(item_to_edit.get('production_year', 1400))
            
            # وضعیت فنی
            condition_index = self.condition.findText(item_to_edit.get('condition', 'خوب'))
            if condition_index >= 0:
                self.condition.setCurrentIndex(condition_index)
            
            self.quantity.setValue(item_to_edit.get('quantity', 1))
            self.location.setText(item_to_edit.get('location', ''))
            
            # منبع
            source_type = item_to_edit.get('source_type', 'مشتری')
            source_index = self.source_type.findText(source_type)
            if source_index >= 0:
                self.source_type.setCurrentIndex(source_index)
            
            # تنظیم فیلد منبع مناسب
            if source_type == 'مشتری':
                self.customer.set_value(item_to_edit.get('source_person_id', 0))
            elif source_type == 'تامین کننده':
                self.supplier.set_value(item_to_edit.get('source_person_id', 0))
            elif source_type == 'تعویض شده' and 'reception_id' in item_to_edit:
                self.reception.set_value(item_to_edit.get('reception_id', 0))
            
            # 🔴 **تبدیل تاریخ میلادی به شمسی برای نمایش در فرم**
            purchase_date_miladi = item_to_edit.get('purchase_date', '')
            if purchase_date_miladi:
                purchase_date_shamsi = self.miladi_to_shamsi(purchase_date_miladi)
                self.purchase_date.set_date(purchase_date_shamsi)
            
            last_repair_date_miladi = item_to_edit.get('last_repair_date', '')
            if last_repair_date_miladi:
                last_repair_date_shamsi = self.miladi_to_shamsi(last_repair_date_miladi)
                self.last_repair_date.set_date(last_repair_date_shamsi)
            
            entry_date_miladi = item_to_edit.get('entry_date', '')
            if entry_date_miladi:
                entry_date_shamsi = self.miladi_to_shamsi(entry_date_miladi)
                self.entry_date.set_date(entry_date_shamsi)
            
            self.purchase_document.setText(item_to_edit.get('purchase_document', ''))
            self.accessories.setPlainText(item_to_edit.get('accessories', ''))
            self.description.setPlainText(item_to_edit.get('description', ''))
            
            # تب اطلاعات فنی
            self.technical_status.setPlainText(item_to_edit.get('technical_status', ''))
            self.repair_history.setPlainText(item_to_edit.get('repair_history', ''))
            
            # تب اطلاعات مالی
            self.purchase_price.set_value(item_to_edit.get('purchase_price', 0))
            self.sale_price.set_value(item_to_edit.get('sale_price', 0))
            self.calculate_profit()
            
            warranty_index = self.warranty_type.findText(item_to_edit.get('warranty_type', 'گارانتی فروشگاه'))
            if warranty_index >= 0:
                self.warranty_type.setCurrentIndex(warranty_index)
            
            self.warranty_days.setValue(item_to_edit.get('warranty_days', 90))
            self.warranty_description.setText(item_to_edit.get('warranty_description', ''))
            
            status_index = self.status.findText(item_to_edit.get('status', 'موجود'))
            if status_index >= 0:
                self.status.setCurrentIndex(status_index)
            
            # تغییر دکمه ذخیره
            self.btn_save.setText("💾 به‌روزرسانی دستگاه")
            self.btn_save.setProperty("style", "warning")
            
            # اسکرول به بالا
            self.scroll_area.verticalScrollBar().setValue(0)
            
            print(f"✅ دستگاه ID: {item_id} برای ویرایش بارگذاری شد")
            
        except Exception as e:
            print(f"❌ خطا در ویرایش دستگاه: {e}")
            import traceback
            traceback.print_exc()
            self.show_error(f"خطا در ویرایش دستگاه: {str(e)}")
 
    def on_edit(self):
        """ویرایش دستگاه انتخاب شده"""
        selected_rows = self.table.selectionModel().selectedRows()
        if selected_rows:
            row = selected_rows[0].row()
            if row < len(self.all_data):
                item_id = self.all_data[row]['id']
                self.edit_item(item_id)

    def delete_item_with_transaction(self, item_id, reason="حذف دستی"):
        """حذف آیتم از انبار با ثبت تراکنش - نسخه اصلاح شده"""
        print(f"🔴 delete_item_with_transaction شروع شد برای item_id: {item_id}")
        
        try:
            if not self.data_manager or not hasattr(self.data_manager, 'warehouse'):
                self.show_error("اتصال به دیتابیس برقرار نیست!")
                return False
            
            # دریافت اطلاعات کامل آیتم قبل از حذف
            print(f"🔴 در حال دریافت اطلاعات آیتم {item_id}...")
            item_info = self.data_manager.warehouse.get_warehouse_item_info('لوازم دست دوم', item_id)
            
            if not item_info:
                self.show_error("آیتم مورد نظر یافت نشد!")
                return False
            
            # نمایش تاییدیه ساده با QMessageBox
            print(f"🔴 نمایش تاییدیه حذف...")
            
            # ساخت پیام اطلاعاتی
            message_text = f"""
            <div style='font-family: B Nazanin; font-size: 12pt;'>
            <b style='color: red;'>⚠️ تایید حذف دستگاه با ثبت تراکنش</b>
            <hr>
            <b>دستگاه:</b> {item_info.get('brand_name', 'نامشخص')} - {item_info.get('model', 'نامشخص')}
            <br><b>دسته‌بندی:</b> {item_info.get('device_type_name', 'نامشخص')}
            <br><b>شماره سریال:</b> {item_info.get('serial_number', 'نامشخص')}
            <br><b>وضعیت:</b> {item_info.get('condition', 'نامشخص')}
            <br><b>منبع:</b> {item_info.get('source_type', 'نامشخص')}
            <br><b>قیمت خرید:</b> {self.format_currency(item_info.get('purchase_price', 0))}
            <br><b>ارزش کل:</b> {self.format_currency(item_info.get('quantity', 0) * item_info.get('purchase_price', 0))}
            <hr>
            <b style='color: darkred;'>این عمل قابل بازگشت نیست!</b>
            </div>
            """
            
            # نمایش تاییدیه اولیه
            reply = QMessageBox.question(
                self,
                "تایید حذف دستگاه",
                message_text,
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply != QMessageBox.Yes:
                print("🔴 کاربر حذف را لغو کرد")
                return False
            
            # دریافت دلیل حذف از کاربر
            print(f"🔴 دریافت دلیل حذف...")
            reason_text, ok = QInputDialog.getText(
                self,
                "دلیل حذف",
                "لطفاً دلیل حذف را وارد کنید:",
                text=reason
            )
            
            if not ok:
                print("🔴 کاربر دلیل حذف را وارد نکرد")
                return False
            
            if not reason_text.strip():
                reason_text = "حذف دستی توسط کاربر"
            
            print(f"🔴 در حال حذف آیتم {item_id}...")
            print(f"   دلیل: {reason_text}")
            
            # فراخوانی تابع حذف از WarehouseManager
            success = self.data_manager.warehouse.delete_warehouse_item(
                warehouse_type='لوازم دست دوم',
                item_id=item_id,
                soft_delete=False,  # حذف سخت با ثبت تراکنش
                reason=reason_text
            )
            
            if success:
                print(f"✅ آیتم {item_id} با موفقیت حذف شد.")
                
                # نمایش پیام موفقیت
                QMessageBox.information(
                    self,
                    "حذف موفق",
                    f"دستگاه '{item_info.get('brand_name', '')} - {item_info.get('model', '')}' با موفقیت حذف شد.\nتراکنش حذف در سیستم ثبت گردید."
                )
                
                # ثبت لاگ
                log_data = {
                    'user_id': 1,
                    'action': 'حذف لوازم دست دوم',
                    'table_name': 'UsedAppliancesWarehouse',
                    'record_id': item_id,
                    'details': f"حذف دستگاه {item_info.get('brand_name', '')} - {item_info.get('model', '')} ({item_info.get('serial_number', '')}) - دلیل: {reason_text}",
                    'ip_address': '127.0.0.1'
                }
                
                self.log_action(log_data)
                
                return True
            else:
                print(f"❌ خطا در حذف آیتم {item_id}")
                self.show_error("خطا در حذف آیتم از دیتابیس!")
                return False
                
        except Exception as e:
            print(f"❌ خطا در حذف آیتم: {e}")
            import traceback
            traceback.print_exc()
            self.show_error(f"خطا در حذف آیتم: {str(e)}")
            return False

    def on_delete_with_transaction(self):
        """حذف آیتم انتخاب شده با ثبت تراکنش - نسخه بهبود یافته"""
        print("🔴 on_delete_with_transaction فراخوانی شد")
        
        try:
            selected_rows = self.table.selectionModel().selectedRows()
            if not selected_rows:
                self.show_warning("لطفاً یک آیتم را از جدول انتخاب کنید.")
                return
            
            row = selected_rows[0].row()
            print(f"🔴 ردیف انتخاب شده: {row}")
            
            # بررسی وجود داده در ردیف انتخاب شده
            if row >= self.table.rowCount():
                self.show_error("ردیف انتخاب شده معتبر نیست.")
                return
            
            # گرفتن کد دستگاه از ستون دوم (دسته‌بندی) یا مدل
            brand_model_item = self.table.item(row, 2)
            serial_item = self.table.item(row, 3)
            
            if not brand_model_item:
                self.show_error("نمی‌توان اطلاعات دستگاه را پیدا کرد.")
                return
            
            brand_model = brand_model_item.text()
            serial_number = serial_item.text() if serial_item else ""
            
            print(f"🔴 دستگاه: {brand_model}")
            print(f"🔴 شماره سریال: {serial_number}")
            
            # پیدا کردن آیتم در all_data
            item_id = None
            for item in self.all_data:
                # تلاش برای مطابقت با مدل یا شماره سریال
                item_brand_model = f"{item.get('brand', '')} - {item.get('model', '')}"
                item_serial = item.get('serial_number', '')
                
                if (serial_number and item_serial == serial_number) or \
                (brand_model and item_brand_model == brand_model):
                    item_id = item.get('id')
                    print(f"🔴 یافتن item_id: {item_id}")
                    break
            
            if not item_id:
                # اگر از طریق روش بالا پیدا نکردیم، از طریق شماره ردیف در جدول امتحان کنیم
                if row < len(self.all_data):
                    item_id = self.all_data[row].get('id')
                    print(f"🔴 item_id از طریق ردیف: {item_id}")
            
            if not item_id:
                self.show_error("آیتم انتخاب شده در داده‌ها یافت نشد.")
                return
            
            # حذف با ثبت تراکنش
            print(f"🔴 فراخوانی delete_item_with_transaction با item_id: {item_id}")
            if self.delete_item_with_transaction(item_id):
                self.show_success("دستگاه با موفقیت حذف شد و تراکنش ثبت گردید.")
                
                # تازه‌سازی داده‌ها
                print("🔴 تازه‌سازی داده‌ها...")
                self.load_data()
                
                # ارسال سیگنال تغییر داده
                if hasattr(self, 'data_changed'):
                    self.data_changed.emit()
                
        except Exception as e:
            print(f"❌ خطا در on_delete_with_transaction: {e}")
            import traceback
            traceback.print_exc()
            self.show_error(f"خطا در حذف: {str(e)}")

    def on_delete_with_transaction_for_item(self, item_id):
        """حذف مستقیم از دکمه در جدول"""
        if self.delete_item_with_transaction(item_id):
            self.show_success("دستگاه با موفقیت حذف شد و تراکنش ثبت گردید.")
            self.load_data()
            if hasattr(self, 'data_changed'):
                self.data_changed.emit()

    def soft_delete_item(self, item_id, reason="حذف نرم"):
        """حذف نرم آیتم (تغییر وضعیت به 'اسقاط')"""
        try:
            if not self.data_manager or not hasattr(self.data_manager, 'warehouse'):
                self.show_error("اتصال به دیتابیس برقرار نیست!")
                return False
            
            # نمایش تاییدیه
            reply = QMessageBox.question(
                self,
                "تایید حذف نرم",
                "آیا از تغییر وضعیت این دستگاه به 'اسقاط' اطمینان دارید؟\n\n(این دستگاه از لیست موجودی حذف می‌شود اما در دیتابیس باقی می‌ماند)",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply != QMessageBox.Yes:
                return False
            
            # دریافت دلیل
            reason_text, ok = QInputDialog.getText(
                self, 
                "دلیل حذف نرم", 
                "دلیل تغییر وضعیت را وارد کنید:", 
                text=reason
            )
            
            if not ok:
                return False
            
            if not reason_text.strip():
                reason_text = "حذف نرم توسط کاربر"
            
            print(f"🔄 در حال حذف نرم آیتم {item_id}...")
            
            # فراخوانی تابع حذف نرم
            success = self.data_manager.warehouse.soft_delete_warehouse_item(
                warehouse_type='لوازم دست دوم',
                item_id=item_id,
                reason=reason_text
            )
            
            if success:
                print(f"✅ حذف نرم آیتم {item_id} با موفقیت انجام شد.")
                return True
            else:
                print(f"❌ خطا در حذف نرم آیتم {item_id}")
                return False
                
        except Exception as e:
            print(f"❌ خطا در حذف نرم آیتم: {e}")
            self.show_error(f"خطا در حذف نرم آیتم: {str(e)}")
            return False

    def on_soft_delete_for_item(self, item_id):
        """حذف نرم مستقیم از دکمه در جدول"""
        if self.soft_delete_item(item_id):
            self.show_success("حذف نرم با موفقیت انجام شد (وضعیت تغییر یافت).")
            self.load_data()
            if hasattr(self, 'data_changed'):
                self.data_changed.emit()

    def on_soft_delete(self):
        """حذف نرم آیتم انتخاب شده"""
        selected_rows = self.table.selectionModel().selectedRows()
        if selected_rows:
            row = selected_rows[0].row()
            if row < len(self.all_data):
                item_id = self.all_data[row]['id']
                
                # حذف نرم
                if self.soft_delete_item(item_id):
                    self.show_success("حذف نرم با موفقیت انجام شد (وضعیت تغییر یافت).")
                    
                    # تازه‌سازی داده‌ها
                    self.load_data()
                    if hasattr(self, 'data_changed'):
                        self.data_changed.emit()

    def log_action(self, log_data):
        """ثبت لاگ عملیات"""
        try:
            if self.data_manager and hasattr(self.data_manager.db, 'execute_query'):
                query = """
                INSERT INTO Logs (user_id, action, table_name, record_id, details, ip_address)
                VALUES (?, ?, ?, ?, ?, ?)
                """
                
                params = (
                    log_data.get('user_id', 1),
                    log_data.get('action', ''),
                    log_data.get('table_name', ''),
                    log_data.get('record_id', 0),
                    log_data.get('details', ''),
                    log_data.get('ip_address', '127.0.0.1')
                )
                
                self.data_manager.db.execute_query(query, params)
                print(f"📝 لاگ ثبت شد: {log_data.get('action')}")
        except Exception as e:
            print(f"⚠️ خطا در ثبت لاگ: {e}")

    def on_table_selection_changed(self):
        """هنگام تغییر انتخاب در جدول"""
        selected_rows = self.table.selectionModel().selectedRows()
        has_selection = len(selected_rows) > 0
        
        self.btn_edit.setEnabled(has_selection)
        self.btn_delete.setEnabled(has_selection)
        self.btn_soft_delete.setEnabled(has_selection)  # اضافه کردن این خط
        self.btn_sell.setEnabled(has_selection)

    def on_delete(self):
        """حذف دستگاه انتخاب شده - تغییر نام به on_delete_with_transaction"""
        self.on_delete_with_transaction()

    def on_sell(self):
        """ثبت فروش دستگاه"""
        selected_rows = self.table.selectionModel().selectedRows()
        if not selected_rows:
            return
        
        row = selected_rows[0].row()
        if row >= len(self.all_data):
            return
        
        item_id = self.all_data[row]['id']
        item = self.all_data[row]
        
        if item.get('status') == 'فروخته شده':
            self.show_warning("این دستگاه قبلاً فروخته شده است.")
            return
        
        if not self.confirm_action("ثبت فروش", "آیا می‌خواهید فروش این دستگاه را ثبت کنید؟"):
            return
        
        try:
            print(f"💰 در حال ثبت فروش دستگاه ID: {item_id}")
            
            # به‌روزرسانی وضعیت دستگاه به "فروخته شده"
            update_data = {
                'status': 'فروخته شده',
                'location': 'فروخته شده'
            }
            
            success = self.data_manager.warehouse.update_warehouse_item(
                'لوازم دست دوم', 
                item_id, 
                update_data
            )
            
            if success:
                print(f"✅ فروش دستگاه ID: {item_id} ثبت شد")
                
                # سیگنال تغییر داده
                self.data_changed.emit()
                
                # نمایش پیام موفقیت
                self.show_success("فروش دستگاه با موفقیت ثبت شد.")
                
                # تازه‌سازی داده‌ها
                self.load_data()
            else:
                print(f"❌ خطا در ثبت فروش دستگاه ID: {item_id}")
                self.show_error("خطا در ثبت فروش دستگاه. لطفاً مجدداً تلاش کنید.")
                
        except Exception as e:
            print(f"❌ خطا در ثبت فروش: {e}")
            import traceback
            traceback.print_exc()
            self.show_error(f"خطا در ثبت فروش: {str(e)}")
    
    def export_excel(self):
        """خروجی Excel"""
        self.show_success("خروجی Excel تولید شد (ویژگی در حال توسعه).")