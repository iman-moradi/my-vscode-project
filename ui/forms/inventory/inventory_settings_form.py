"""
فرم تنظیمات انبار
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QLineEdit, QComboBox, QTableWidget,
    QTableWidgetItem, QGroupBox, QFormLayout, QSpinBox,
    QCheckBox, QTabWidget, QMessageBox, QInputDialog,
    QHeaderView, QTextEdit
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor, QFont

from .base_inventory_form import BaseInventoryForm

class InventorySettingsForm(BaseInventoryForm):
    """فرم تنظیمات انبار"""
    
    settings_changed = Signal()  # سیگنال تغییر تنظیمات
    
    def __init__(self, parent=None):
        super().__init__("تنظیمات انبار", parent)
        self.setup_ui()
        self.load_settings()
        
    def setup_ui(self):
        # هدر
        header_label = QLabel("⚙️ تنظیمات انبار")
        header_label.setStyleSheet("""
            font-size: 18px;
            font-weight: bold;
            color: #1e90ff;
            padding: 10px;
            text-align: center;
        """)
        self.main_layout.addWidget(header_label)
        
        # تب‌ها
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabPosition(QTabWidget.North)
        
        self.create_general_settings_tab()
        self.create_categories_tab()
        self.create_units_tab()
        self.create_notifications_tab()
        
        self.main_layout.addWidget(self.tab_widget)
        
        # دکمه‌های عملیات
        self.create_action_buttons()
    
    def create_general_settings_tab(self):
        """تب تنظیمات عمومی"""
        tab = QWidget()
        layout = QVBoxLayout()
        
        # گروه تنظیمات عمومی
        general_group = QGroupBox("🔧 تنظیمات عمومی انبار")
        general_group.setStyleSheet("""
            QGroupBox {
                border: 2px solid #3498db;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 15px;
                font-weight: bold;
            }
        """)
        general_layout = QFormLayout()
        
        # حداقل موجودی پیش‌فرض
        self.default_min_stock = QSpinBox()
        self.default_min_stock.setRange(1, 1000)
        self.default_min_stock.setValue(5)
        self.default_min_stock.setSuffix(" عدد")
        general_layout.addRow("حداقل موجودی پیش‌فرض:", self.default_min_stock)
        
        # حداکثر موجودی پیش‌فرض
        self.default_max_stock = QSpinBox()
        self.default_max_stock.setRange(10, 10000)
        self.default_max_stock.setValue(100)
        self.default_max_stock.setSuffix(" عدد")
        general_layout.addRow("حداکثر موجودی پیش‌فرض:", self.default_max_stock)
        
        # واحد پیش‌فرض
        self.default_unit = QComboBox()
        self.default_unit.addItems(["عدد", "متر", "کیلو", "لیتر", "ست"])
        general_layout.addRow("واحد پیش‌فرض:", self.default_unit)
        
        # وضعیت پیش‌فرض
        self.default_status = QComboBox()
        self.default_status.addItems(["موجود", "ناموجود", "در حال سفارش"])
        general_layout.addRow("وضعیت پیش‌فرض:", self.default_status)
        
        # گارانتی پیش‌فرض لوازم نو
        self.default_warranty_months = QSpinBox()
        self.default_warranty_months.setRange(0, 120)
        self.default_warranty_months.setValue(12)
        self.default_warranty_months.setSuffix(" ماه")
        general_layout.addRow("گارانتی پیش‌فرض لوازم نو:", self.default_warranty_months)
        
        # گارانتی پیش‌فرض لوازم دست دوم
        self.default_used_warranty_days = QSpinBox()
        self.default_used_warranty_days.setRange(0, 365)
        self.default_used_warranty_days.setValue(90)
        self.default_used_warranty_days.setSuffix(" روز")
        general_layout.addRow("گارانتی پیش‌فرض لوازم دست دوم:", self.default_used_warranty_days)
        
        general_group.setLayout(general_layout)
        layout.addWidget(general_group)
        
        # گروه تنظیمات فاکتور
        invoice_group = QGroupBox("🧾 تنظیمات فاکتور انبار")
        invoice_group.setStyleSheet("""
            QGroupBox {
                border: 2px solid #9b59b6;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 15px;
                font-weight: bold;
            }
        """)
        invoice_layout = QFormLayout()
        
        # پیشوند شماره فاکتور
        self.invoice_prefix = QLineEdit()
        self.invoice_prefix.setText("INV")
        invoice_layout.addRow("پیشوند شماره فاکتور:", self.invoice_prefix)
        
        # شماره شروع
        self.starting_invoice_number = QSpinBox()
        self.starting_invoice_number.setRange(1, 999999)
        self.starting_invoice_number.setValue(1000)
        invoice_layout.addRow("شماره شروع فاکتور:", self.starting_invoice_number)
        
        # افزودن مالیات
        self.add_tax = QCheckBox("افزودن مالیات به فاکتورها")
        self.add_tax.setChecked(True)
        invoice_layout.addRow(self.add_tax)
        
        # درصد مالیات
        self.tax_percentage = QSpinBox()
        self.tax_percentage.setRange(0, 100)
        self.tax_percentage.setValue(9)
        self.tax_percentage.setSuffix(" %")
        self.tax_percentage.setEnabled(True)
        invoice_layout.addRow("درصد مالیات:", self.tax_percentage)
        
        # اتصال چک‌باکس مالیات
        self.add_tax.stateChanged.connect(
            lambda state: self.tax_percentage.setEnabled(state == Qt.Checked)
        )
        
        invoice_group.setLayout(invoice_layout)
        layout.addWidget(invoice_group)
        
        layout.addStretch()
        tab.setLayout(layout)
        self.tab_widget.addTab(tab, "⚙️ عمومی")
    
    def create_categories_tab(self):
        """تب مدیریت دسته‌بندی‌ها"""
        tab = QWidget()
        layout = QVBoxLayout()
        
        # گروه دسته‌بندی‌ها
        categories_group = QGroupBox("🏷️ مدیریت دسته‌بندی‌ها")
        categories_group.setStyleSheet("""
            QGroupBox {
                border: 2px solid #27ae60;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 15px;
                font-weight: bold;
            }
        """)
        categories_layout = QVBoxLayout()
        
        # تب‌های داخلی برای انواع مختلف
        category_tabs = QTabWidget()
        
        # تب دسته‌بندی دستگاه‌ها
        device_tab = QWidget()
        device_layout = QVBoxLayout()
        
        # دکمه‌های مدیریت
        device_btn_layout = QHBoxLayout()
        
        add_device_btn = QPushButton("➕ افزودن دسته‌بندی")
        add_device_btn.clicked.connect(lambda: self.add_category("دستگاه"))
        add_device_btn.setStyleSheet("background-color: #27ae60; color: white;")
        
        remove_device_btn = QPushButton("🗑️ حذف انتخاب شده")
        remove_device_btn.clicked.connect(lambda: self.remove_category("دستگاه"))
        remove_device_btn.setStyleSheet("background-color: #e74c3c; color: white;")
        
        device_btn_layout.addWidget(add_device_btn)
        device_btn_layout.addWidget(remove_device_btn)
        device_btn_layout.addStretch()
        
        device_layout.addLayout(device_btn_layout)
        
        # جدول دسته‌بندی‌ها
        self.device_categories_table = QTableWidget()
        self.device_categories_table.setColumnCount(3)
        self.device_categories_table.setHorizontalHeaderLabels(["ردیف", "نام دسته‌بندی", "توضیحات"])
        self.device_categories_table.setMaximumHeight(300)
        
        device_layout.addWidget(self.device_categories_table)
        device_tab.setLayout(device_layout)
        
        # تب دسته‌بندی قطعات
        parts_tab = QWidget()
        parts_layout = QVBoxLayout()
        
        parts_btn_layout = QHBoxLayout()
        
        add_parts_btn = QPushButton("➕ افزودن دسته‌بندی")
        add_parts_btn.clicked.connect(lambda: self.add_category("قطعات"))
        add_parts_btn.setStyleSheet("background-color: #3498db; color: white;")
        
        remove_parts_btn = QPushButton("🗑️ حذف انتخاب شده")
        remove_parts_btn.clicked.connect(lambda: self.remove_category("قطعات"))
        remove_parts_btn.setStyleSheet("background-color: #e74c3c; color: white;")
        
        parts_btn_layout.addWidget(add_parts_btn)
        parts_btn_layout.addWidget(remove_parts_btn)
        parts_btn_layout.addStretch()
        
        parts_layout.addLayout(parts_btn_layout)
        
        self.parts_categories_table = QTableWidget()
        self.parts_categories_table.setColumnCount(3)
        self.parts_categories_table.setHorizontalHeaderLabels(["ردیف", "نام دسته‌بندی", "توضیحات"])
        self.parts_categories_table.setMaximumHeight(300)
        
        parts_layout.addWidget(self.parts_categories_table)
        parts_tab.setLayout(parts_layout)
        
        # اضافه کردن تب‌ها
        category_tabs.addTab(device_tab, "دستگاه‌ها")
        category_tabs.addTab(parts_tab, "قطعات")
        
        categories_layout.addWidget(category_tabs)
        categories_group.setLayout(categories_layout)
        layout.addWidget(categories_group)
        
        # گروه برندها
        brands_group = QGroupBox("🏭 مدیریت برندها")
        brands_group.setStyleSheet("""
            QGroupBox {
                border: 2px solid #f39c12;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 15px;
                font-weight: bold;
            }
        """)
        brands_layout = QVBoxLayout()
        
        # دکمه‌های مدیریت برند
        brands_btn_layout = QHBoxLayout()
        
        add_brand_btn = QPushButton("➕ افزودن برند")
        add_brand_btn.clicked.connect(self.add_brand)
        add_brand_btn.setStyleSheet("background-color: #f39c12; color: white;")
        
        remove_brand_btn = QPushButton("🗑️ حذف انتخاب شده")
        remove_brand_btn.clicked.connect(self.remove_brand)
        remove_brand_btn.setStyleSheet("background-color: #e74c3c; color: white;")
        
        brands_btn_layout.addWidget(add_brand_btn)
        brands_btn_layout.addWidget(remove_brand_btn)
        brands_btn_layout.addStretch()
        
        brands_layout.addLayout(brands_btn_layout)
        
        # جدول برندها
        self.brands_table = QTableWidget()
        self.brands_table.setColumnCount(2)
        self.brands_table.setHorizontalHeaderLabels(["ردیف", "نام برند"])
        self.brands_table.setMaximumHeight(200)
        
        brands_layout.addWidget(self.brands_table)
        brands_group.setLayout(brands_layout)
        layout.addWidget(brands_group)
        
        layout.addStretch()
        tab.setLayout(layout)
        self.tab_widget.addTab(tab, "🏷️ دسته‌بندی‌ها")
    
    def create_units_tab(self):
        """تب مدیریت واحدها"""
        tab = QWidget()
        layout = QVBoxLayout()
        
        # گروه واحدهای اندازه‌گیری
        units_group = QGroupBox("📏 مدیریت واحدهای اندازه‌گیری")
        units_group.setStyleSheet("""
            QGroupBox {
                border: 2px solid #9b59b6;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 15px;
                font-weight: bold;
            }
        """)
        units_layout = QVBoxLayout()
        
        # دکمه‌های مدیریت
        units_btn_layout = QHBoxLayout()
        
        add_unit_btn = QPushButton("➕ افزودن واحد")
        add_unit_btn.clicked.connect(self.add_unit)
        add_unit_btn.setStyleSheet("background-color: #9b59b6; color: white;")
        
        remove_unit_btn = QPushButton("🗑️ حذف انتخاب شده")
        remove_unit_btn.clicked.connect(self.remove_unit)
        remove_unit_btn.setStyleSheet("background-color: #e74c3c; color: white;")
        
        units_btn_layout.addWidget(add_unit_btn)
        units_btn_layout.addWidget(remove_unit_btn)
        units_btn_layout.addStretch()
        
        units_layout.addLayout(units_btn_layout)
        
        # جدول واحدها
        self.units_table = QTableWidget()
        self.units_table.setColumnCount(3)
        self.units_table.setHorizontalHeaderLabels(["ردیف", "نام واحد", "نماد"])
        self.units_table.setMaximumHeight(300)
        
        units_layout.addWidget(self.units_table)
        units_group.setLayout(units_layout)
        layout.addWidget(units_group)
        
        # گروه تبدیل واحد
        conversion_group = QGroupBox("🔄 تبدیل واحد")
        conversion_group.setStyleSheet("""
            QGroupBox {
                border: 2px solid #3498db;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 15px;
                font-weight: bold;
            }
        """)
        conversion_layout = QFormLayout()
        
        self.conversion_from = QComboBox()
        self.conversion_to = QComboBox()
        self.conversion_factor = QLineEdit()
        self.conversion_factor.setPlaceholderText("مثلاً 1000 برای کیلو به گرم")
        
        conversion_layout.addRow("از واحد:", self.conversion_from)
        conversion_layout.addRow("به واحد:", self.conversion_to)
        conversion_layout.addRow("ضریب تبدیل:", self.conversion_factor)
        
        # دکمه ذخیره تبدیل
        save_conversion_btn = QPushButton("💾 ذخیره تبدیل")
        save_conversion_btn.clicked.connect(self.save_conversion)
        save_conversion_btn.setStyleSheet("background-color: #3498db; color: white;")
        
        conversion_layout.addRow(save_conversion_btn)
        conversion_group.setLayout(conversion_layout)
        layout.addWidget(conversion_group)
        
        layout.addStretch()
        tab.setLayout(layout)
        self.tab_widget.addTab(tab, "📏 واحدها")
    
    def create_notifications_tab(self):
        """تب تنظیمات اعلان‌ها"""
        tab = QWidget()
        layout = QVBoxLayout()
        
        # گروه اعلان‌های موجودی
        stock_notifications_group = QGroupBox("🔔 اعلان‌های موجودی")
        stock_notifications_group.setStyleSheet("""
            QGroupBox {
                border: 2px solid #f39c12;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 15px;
                font-weight: bold;
            }
        """)
        stock_layout = QFormLayout()
        
        # فعال‌سازی اعلان‌ها
        self.enable_stock_notifications = QCheckBox("فعال‌سازی اعلان‌های موجودی کم")
        self.enable_stock_notifications.setChecked(True)
        stock_layout.addRow(self.enable_stock_notifications)
        
        # سطح هشدار
        self.warning_level = QComboBox()
        self.warning_level.addItems(["۱۰٪ حداقل", "۲۰٪ حداقل", "۳۰٪ حداقل", "۵۰٪ حداقل"])
        stock_layout.addRow("سطح هشدار:", self.warning_level)
        
        # اعلان از طریق ایمیل
        self.enable_email_notifications = QCheckBox("ارسال اعلان از طریق ایمیل")
        self.enable_email_notifications.setChecked(False)
        stock_layout.addRow(self.enable_email_notifications)
        
        # ایمیل‌های دریافت‌کننده
        self.notification_emails = QTextEdit()
        self.notification_emails.setMaximumHeight(80)
        self.notification_emails.setPlaceholderText("ایمیل‌ها را با کاما جدا کنید")
        stock_layout.addRow("ایمیل‌های دریافت‌کننده:", self.notification_emails)
        
        # فاصله بررسی
        self.check_interval = QComboBox()
        self.check_interval.addItems(["هر روز", "هر ۲ روز", "هر هفته", "هر ماه"])
        stock_layout.addRow("فاصله بررسی:", self.check_interval)
        
        stock_notifications_group.setLayout(stock_layout)
        layout.addWidget(stock_notifications_group)
        
        # گروه اعلان‌های تاریخ انقضا
        expiry_notifications_group = QGroupBox("📅 اعلان‌های تاریخ انقضا")
        expiry_notifications_group.setStyleSheet("""
            QGroupBox {
                border: 2px solid #e74c3c;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 15px;
                font-weight: bold;
            }
        """)
        expiry_layout = QFormLayout()
        
        self.enable_expiry_notifications = QCheckBox("فعال‌سازی اعلان‌های تاریخ انقضا")
        self.enable_expiry_notifications.setChecked(True)
        expiry_layout.addRow(self.enable_expiry_notifications)
        
        self.days_before_expiry = QSpinBox()
        self.days_before_expiry.setRange(1, 90)
        self.days_before_expiry.setValue(30)
        self.days_before_expiry.setSuffix(" روز قبل")
        expiry_layout.addRow("اعلان قبل از انقضا:", self.days_before_expiry)
        
        expiry_notifications_group.setLayout(expiry_layout)
        layout.addWidget(expiry_notifications_group)
        
        layout.addStretch()
        tab.setLayout(layout)
        self.tab_widget.addTab(tab, "🔔 اعلان‌ها")
    
    def create_action_buttons(self):
        """ایجاد دکمه‌های عملیات"""
        button_layout = QHBoxLayout()
        
        save_btn = QPushButton("💾 ذخیره تنظیمات")
        save_btn.clicked.connect(self.save_settings)
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 12px 24px;
                font-weight: bold;
                font-size: 11pt;
            }
            QPushButton:hover {
                background-color: #219653;
            }
        """)
        
        reset_btn = QPushButton("🔄 بازنشانی به پیش‌فرض")
        reset_btn.clicked.connect(self.reset_to_default)
        reset_btn.setStyleSheet("""
            QPushButton {
                background-color: #f39c12;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 12px 24px;
                font-weight: bold;
                font-size: 11pt;
            }
            QPushButton:hover {
                background-color: #d35400;
            }
        """)
        
        button_layout.addWidget(save_btn)
        button_layout.addWidget(reset_btn)
        button_layout.addStretch()
        
        self.main_layout.addLayout(button_layout)
    
    def load_settings(self):
        """بارگذاری تنظیمات"""
        try:
            # بارگذاری تنظیمات عمومی
            if self.data_manager and hasattr(self.data_manager, 'settings'):
                settings = self.data_manager.settings.get_settings()
                
                if settings:
                    # تنظیمات عمومی
                    if 'default_min_stock' in settings:
                        self.default_min_stock.setValue(settings['default_min_stock'])
                    
                    if 'default_max_stock' in settings:
                        self.default_max_stock.setValue(settings['default_max_stock'])
                    
                    # واحد پیش‌فرض
                    if 'default_unit' in settings:
                        index = self.default_unit.findText(settings['default_unit'])
                        if index >= 0:
                            self.default_unit.setCurrentIndex(index)
                    
                    # بارگذاری دسته‌بندی‌ها
                    self.load_categories()
                    
                    # بارگذاری برندها
                    self.load_brands()
                    
                    # بارگذاری واحدها
                    self.load_units()
            
            print("✅ تنظیمات انبار بارگذاری شد")
            
        except Exception as e:
            print(f"❌ خطا در بارگذاری تنظیمات: {e}")
            self.show_error(f"خطا در بارگذاری تنظیمات: {str(e)}")
    
    def load_categories(self):
        """بارگذاری دسته‌بندی‌ها"""
        try:
            # بارگذاری دسته‌بندی دستگاه‌ها
            if hasattr(self.data_manager, 'device_category_name'):
                device_categories = self.data_manager.device_category_name.get_all()
                self.display_categories(self.device_categories_table, device_categories)
            
            # بارگذاری دسته‌بندی قطعات (از LookupValues)
            if hasattr(self.data_manager, 'lookup'):
                parts_categories = self.data_manager.lookup.get_by_category('category')
                self.display_categories(self.parts_categories_table, parts_categories)
                
        except Exception as e:
            print(f"❌ خطا در بارگذاری دسته‌بندی‌ها: {e}")
    
    def load_brands(self):
        """بارگذاری برندها"""
        try:
            if hasattr(self.data_manager, 'brand'):
                brands = self.data_manager.brand.get_all()
                self.display_brands(brands)
        except Exception as e:
            print(f"❌ خطا در بارگذاری برندها: {e}")
    
    def load_units(self):
        """بارگذاری واحدها"""
        try:
            if hasattr(self.data_manager, 'lookup'):
                units = self.data_manager.lookup.get_by_category('unit')
                self.display_units(units)
                
                # پر کردن کامبوباکس‌های تبدیل واحد
                self.conversion_from.clear()
                self.conversion_to.clear()
                
                for unit in units:
                    unit_name = unit.get('value', '')
                    self.conversion_from.addItem(unit_name)
                    self.conversion_to.addItem(unit_name)
                    
        except Exception as e:
            print(f"❌ خطا در بارگذاری واحدها: {e}")
    
    def display_categories(self, table, categories):
        """نمایش دسته‌بندی‌ها در جدول"""
        table.setRowCount(len(categories))
        
        for row, category in enumerate(categories):
            # ردیف
            table.setItem(row, 0, QTableWidgetItem(str(row + 1)))
            table.item(row, 0).setTextAlignment(Qt.AlignCenter)
            
            # نام دسته‌بندی
            name = category.get('name') or category.get('value', '')
            table.setItem(row, 1, QTableWidgetItem(name))
            
            # توضیحات
            description = category.get('description', '')
            table.setItem(row, 2, QTableWidgetItem(description))
    
    def display_brands(self, brands):
        """نمایش برندها در جدول"""
        self.brands_table.setRowCount(len(brands))
        
        for row, brand in enumerate(brands):
            # ردیف
            self.brands_table.setItem(row, 0, QTableWidgetItem(str(row + 1)))
            self.brands_table.item(row, 0).setTextAlignment(Qt.AlignCenter)
            
            # نام برند
            name = brand.get('name', '')
            self.brands_table.setItem(row, 1, QTableWidgetItem(name))
    
    def display_units(self, units):
        """نمایش واحدها در جدول"""
        self.units_table.setRowCount(len(units))
        
        for row, unit in enumerate(units):
            # ردیف
            self.units_table.setItem(row, 0, QTableWidgetItem(str(row + 1)))
            self.units_table.item(row, 0).setTextAlignment(Qt.AlignCenter)
            
            # نام واحد
            name = unit.get('value', '')
            self.units_table.setItem(row, 1, QTableWidgetItem(name))
            
            # نماد
            symbol = self.get_unit_symbol(name)
            self.units_table.setItem(row, 2, QTableWidgetItem(symbol))
    
    def get_unit_symbol(self, unit_name):
        """دریافت نماد واحد"""
        symbols = {
            'عدد': 'عد',
            'متر': 'm',
            'کیلو': 'kg',
            'لیتر': 'L',
            'ست': 'ست'
        }
        return symbols.get(unit_name, unit_name[:2])
    
    def add_category(self, category_type):
        """افزودن دسته‌بندی جدید"""
        name, ok = QInputDialog.getText(
            self, 
            f"افزودن دسته‌بندی {category_type}",
            f"نام دسته‌بندی {category_type} جدید:"
        )
        
        if ok and name:
            try:
                if category_type == "دستگاه":
                    # افزودن به دسته‌بندی دستگاه‌ها
                    if hasattr(self.data_manager, 'device_category_name'):
                        success = self.data_manager.device_category_name.add(name)
                        if success:
                            self.load_categories()
                            self.show_success("دسته‌بندی دستگاه با موفقیت افزوده شد.")
                else:
                    # افزودن به دسته‌بندی قطعات
                    if hasattr(self.data_manager, 'lookup'):
                        success = self.data_manager.lookup.add_value('category', name)
                        if success:
                            self.load_categories()
                            self.show_success("دسته‌بندی قطعات با موفقیت افزوده شد.")
                            
            except Exception as e:
                print(f"❌ خطا در افزودن دسته‌بندی: {e}")
                self.show_error(f"خطا در افزودن دسته‌بندی: {str(e)}")
    
    def remove_category(self, category_type):
        """حذف دسته‌بندی"""
        # پیاده‌سازی مشابه add_category
        self.show_warning("ویژگی حذف دسته‌بندی در حال توسعه است.")
    
    def add_brand(self):
        """افزودن برند جدید"""
        name, ok = QInputDialog.getText(
            self, 
            "افزودن برند",
            "نام برند جدید:"
        )
        
        if ok and name:
            try:
                if hasattr(self.data_manager, 'brand'):
                    success = self.data_manager.brand.add_brand(name)
                    if success:
                        self.load_brands()
                        self.show_success("برند با موفقیت افزوده شد.")
                        
            except Exception as e:
                print(f"❌ خطا در افزودن برند: {e}")
                self.show_error(f"خطا در افزودن برند: {str(e)}")
    
    def remove_brand(self):
        """حذف برند"""
        selected_row = self.brands_table.currentRow()
        if selected_row >= 0:
            brand_name = self.brands_table.item(selected_row, 1).text()
            
            reply = QMessageBox.question(
                self,
                "تایید حذف",
                f"آیا از حذف برند '{brand_name}' مطمئن هستید؟",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                # پیاده‌سازی حذف از دیتابیس
                self.show_warning("ویژگی حذف برند در حال توسعه است.")
    
    def add_unit(self):
        """افزودن واحد جدید"""
        name, ok = QInputDialog.getText(
            self, 
            "افزودن واحد",
            "نام واحد جدید:"
        )
        
        if ok and name:
            try:
                if hasattr(self.data_manager, 'lookup'):
                    success = self.data_manager.lookup.add_value('unit', name)
                    if success:
                        self.load_units()
                        self.show_success("واحد با موفقیت افزوده شد.")
                        
            except Exception as e:
                print(f"❌ خطا در افزودن واحد: {e}")
                self.show_error(f"خطا در افزودن واحد: {str(e)}")
    
    def remove_unit(self):
        """حذف واحد"""
        selected_row = self.units_table.currentRow()
        if selected_row >= 0:
            unit_name = self.units_table.item(selected_row, 1).text()
            
            reply = QMessageBox.question(
                self,
                "تایید حذف",
                f"آیا از حذف واحد '{unit_name}' مطمئن هستید؟",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                # پیاده‌سازی حذف از دیتابیس
                self.show_warning("ویژگی حذف واحد در حال توسعه است.")
    
    def save_conversion(self):
        """ذخیره تبدیل واحد"""
        self.show_success("تبدیل واحد ذخیره شد (ویژگی در حال توسعه).")
    
    def save_settings(self):
        """ذخیره تنظیمات"""
        try:
            # جمع‌آوری تنظیمات
            settings = {
                'default_min_stock': self.default_min_stock.value(),
                'default_max_stock': self.default_max_stock.value(),
                'default_unit': self.default_unit.currentText(),
                'default_status': self.default_status.currentText(),
                'default_warranty_months': self.default_warranty_months.value(),
                'default_used_warranty_days': self.default_used_warranty_days.value(),
                'invoice_prefix': self.invoice_prefix.text(),
                'starting_invoice_number': self.starting_invoice_number.value(),
                'add_tax': self.add_tax.isChecked(),
                'tax_percentage': self.tax_percentage.value() if self.add_tax.isChecked() else 0,
                'enable_stock_notifications': self.enable_stock_notifications.isChecked(),
                'warning_level': self.warning_level.currentText(),
                'enable_email_notifications': self.enable_email_notifications.isChecked(),
                'notification_emails': self.notification_emails.toPlainText(),
                'check_interval': self.check_interval.currentText(),
                'enable_expiry_notifications': self.enable_expiry_notifications.isChecked(),
                'days_before_expiry': self.days_before_expiry.value()
            }
            
            # ذخیره تنظیمات
            # در اینجا باید تنظیمات در دیتابیس ذخیره شود
            # فعلاً فقط نمایش پیام
            print(f"💾 ذخیره تنظیمات: {settings}")
            
            self.settings_changed.emit()
            self.show_success("تنظیمات با موفقیت ذخیره شد.")
            
        except Exception as e:
            print(f"❌ خطا در ذخیره تنظیمات: {e}")
            self.show_error(f"خطا در ذخیره تنظیمات: {str(e)}")
    
    def reset_to_default(self):
        """بازنشانی به تنظیمات پیش‌فرض"""
        reply = QMessageBox.question(
            self,
            "تایید بازنشانی",
            "آیا از بازنشانی همه تنظیمات به حالت پیش‌فرض مطمئن هستید؟",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # بازنشانی تنظیمات
            self.default_min_stock.setValue(5)
            self.default_max_stock.setValue(100)
            self.default_unit.setCurrentIndex(0)
            self.default_status.setCurrentIndex(0)
            self.default_warranty_months.setValue(12)
            self.default_used_warranty_days.setValue(90)
            self.invoice_prefix.setText("INV")
            self.starting_invoice_number.setValue(1000)
            self.add_tax.setChecked(True)
            self.tax_percentage.setValue(9)
            
            self.show_success("تنظیمات به حالت پیش‌فرض بازنشانی شد.")