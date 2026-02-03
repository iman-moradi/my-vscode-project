# inventory_settings_form.py

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout,
                               QFormLayout, QLabel, QLineEdit,
                               QComboBox, QPushButton, QGroupBox,
                               QCheckBox, QSpinBox, QDoubleSpinBox,
                               QTableWidget, QTableWidgetItem,
                               QHeaderView, QMessageBox, QTabWidget)
from PySide6.QtCore import Qt

class InventorySettingsForm(QWidget):
    """فرم تنظیمات انبار"""
    
    def __init__(self, data_manager, config_manager=None):
        super().__init__()
        self.data_manager = data_manager
        self.config_manager = config_manager
        self.init_ui()
        self.apply_styles()
        self.load_categories()
    
    def init_ui(self):
        """ایجاد رابط کاربری"""
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # ایجاد تب‌ها
        self.tab_widget = QTabWidget()
        
        # تب تنظیمات کلی
        self.general_tab = QWidget()
        self.setup_general_tab()
        self.tab_widget.addTab(self.general_tab, "⚙️ عمومی")
        
        # تب هشدارهای موجودی
        self.alerts_tab = QWidget()
        self.setup_alerts_tab()
        self.tab_widget.addTab(self.alerts_tab, "⚠️ هشدارها")
        
        # تب دسته‌بندی‌ها
        self.categories_tab = QWidget()
        self.setup_categories_tab()
        self.tab_widget.addTab(self.categories_tab, "📂 دسته‌بندی‌ها")
        
        main_layout.addWidget(self.tab_widget)
        self.setLayout(main_layout)
    
    def setup_general_tab(self):
        """تنظیم تب عمومی"""
        layout = QVBoxLayout()
        
        # گروه واحدهای اندازه‌گیری
        units_group = QGroupBox("📏 واحدهای اندازه‌گیری")
        units_layout = QFormLayout()
        
        self.cmb_length_unit = QComboBox()
        self.cmb_length_unit.addItems(["سانتی‌متر", "متر", "میلی‌متر", "اینچ"])
        
        self.cmb_weight_unit = QComboBox()
        self.cmb_weight_unit.addItems(["گرم", "کیلوگرم"])
        
        self.cmb_volume_unit = QComboBox()
        self.cmb_volume_unit.addItems(["لیتر", "میلی‌لیتر"])
        
        units_layout.addRow("واحد طول:", self.cmb_length_unit)
        units_layout.addRow("واحد وزن:", self.cmb_weight_unit)
        units_layout.addRow("واحد حجم:", self.cmb_volume_unit)
        
        units_group.setLayout(units_layout)
        layout.addWidget(units_group)
        
        # گروه تنظیمات شمارش
        counting_group = QGroupBox("🔢 تنظیمات شمارش موجودی")
        counting_layout = QFormLayout()
        
        self.spn_decimal_places = QSpinBox()
        self.spn_decimal_places.setRange(0, 4)
        self.spn_decimal_places.setValue(2)
        self.spn_decimal_places.setSuffix(" رقم اعشار")
        
        self.chk_auto_calculate = QCheckBox("محاسبه خودکار موجودی پس از تراکنش")
        self.chk_auto_calculate.setChecked(True)
        
        self.chk_allow_negative = QCheckBox("مجوز موجودی منفی")
        self.chk_allow_negative.setChecked(False)
        
        self.chk_fifo_method = QCheckBox("روش FIFO (اولین وارد - اولین خارج)")
        self.chk_fifo_method.setChecked(True)
        
        counting_layout.addRow("رقم اعشار:", self.spn_decimal_places)
        counting_layout.addRow("", self.chk_auto_calculate)
        counting_layout.addRow("", self.chk_allow_negative)
        counting_layout.addRow("", self.chk_fifo_method)
        
        counting_group.setLayout(counting_layout)
        layout.addWidget(counting_group)
        
        # گروه تنظیمات قیمت
        pricing_group = QGroupBox("💰 تنظیمات قیمت‌گذاری")
        pricing_layout = QFormLayout()
        
        self.spn_price_decimal = QSpinBox()
        self.spn_price_decimal.setRange(0, 4)
        self.spn_price_decimal.setValue(0)
        self.spn_price_decimal.setSuffix(" رقم اعشار قیمت")
        
        self.dbl_default_markup = QDoubleSpinBox()
        self.dbl_default_markup.setRange(0, 500)
        self.dbl_default_markup.setValue(30)
        self.dbl_default_markup.setSuffix(" %")
        
        self.chk_auto_update_price = QCheckBox("بروزرسانی خودکار قیمت فروش")
        self.chk_auto_update_price.setChecked(True)
        
        self.chk_include_tax = QCheckBox("شامل مالیات در قیمت")
        self.chk_include_tax.setChecked(True)
        
        pricing_layout.addRow("رقم اعشار قیمت:", self.spn_price_decimal)
        pricing_layout.addRow("نشان‌گذاری پیش‌فرض:", self.dbl_default_markup)
        pricing_layout.addRow("", self.chk_auto_update_price)
        pricing_layout.addRow("", self.chk_include_tax)
        
        pricing_group.setLayout(pricing_layout)
        layout.addWidget(pricing_group)
        
        self.general_tab.setLayout(layout)
    
    def setup_alerts_tab(self):
        """تنظیم تب هشدارهای موجودی"""
        layout = QVBoxLayout()
        
        # تنظیمات هشدارهای عمومی
        general_alerts_group = QGroupBox("🔔 تنظیمات هشدار عمومی")
        general_layout = QFormLayout()
        
        self.chk_enable_alerts = QCheckBox("فعال‌سازی هشدارهای موجودی")
        self.chk_enable_alerts.setChecked(True)
        
        self.spn_alert_frequency = QSpinBox()
        self.spn_alert_frequency.setRange(1, 24)
        self.spn_alert_frequency.setValue(4)
        self.spn_alert_frequency.setSuffix(" ساعت")
        
        self.chk_email_alerts = QCheckBox("ارسال هشدار از طریق ایمیل")
        self.chk_email_alerts.setChecked(False)
        
        self.chk_sms_alerts = QCheckBox("ارسال هشدار از طریق پیامک")
        self.chk_sms_alerts.setChecked(False)
        
        general_layout.addRow("", self.chk_enable_alerts)
        general_layout.addRow("تناوب بررسی:", self.spn_alert_frequency)
        general_layout.addRow("", self.chk_email_alerts)
        general_layout.addRow("", self.chk_sms_alerts)
        
        general_alerts_group.setLayout(general_layout)
        layout.addWidget(general_alerts_group)
        
        # حداقل موجودی برای هر انبار
        min_stock_group = QGroupBox("📊 حداقل موجودی هر انبار")
        min_stock_layout = QFormLayout()
        
        self.spn_new_parts_min = QSpinBox()
        self.spn_new_parts_min.setRange(1, 1000)
        self.spn_new_parts_min.setValue(10)
        self.spn_new_parts_min.setSuffix(" عدد")
        
        self.spn_used_parts_min = QSpinBox()
        self.spn_used_parts_min.setRange(1, 1000)
        self.spn_used_parts_min.setValue(5)
        self.spn_used_parts_min.setSuffix(" عدد")
        
        self.spn_new_appliances_min = QSpinBox()
        self.spn_new_appliances_min.setRange(1, 100)
        self.spn_new_appliances_min.setValue(3)
        self.spn_new_appliances_min.setSuffix(" عدد")
        
        self.spn_used_appliances_min = QSpinBox()
        self.spn_used_appliances_min.setRange(1, 100)
        self.spn_used_appliances_min.setValue(2)
        self.spn_used_appliances_min.setSuffix(" عدد")
        
        min_stock_layout.addRow("قطعات نو:", self.spn_new_parts_min)
        min_stock_layout.addRow("قطعات دست دوم:", self.spn_used_parts_min)
        min_stock_layout.addRow("لوازم نو:", self.spn_new_appliances_min)
        min_stock_layout.addRow("لوازم دست دوم:", self.spn_used_appliances_min)
        
        min_stock_group.setLayout(min_stock_layout)
        layout.addWidget(min_stock_group)
        
        # آستانه‌های هشدار
        thresholds_group = QGroupBox("📈 آستانه‌های هشدار")
        thresholds_layout = QFormLayout()
        
        self.spn_critical_threshold = QSpinBox()
        self.spn_critical_threshold.setRange(1, 100)
        self.spn_critical_threshold.setValue(10)
        self.spn_critical_threshold.setSuffix(" % از حداقل")
        
        self.spn_warning_threshold = QSpinBox()
        self.spn_warning_threshold.setRange(1, 100)
        self.spn_warning_threshold.setValue(30)
        self.spn_warning_threshold.setSuffix(" % از حداقل")
        
        self.spn_expiry_threshold = QSpinBox()
        self.spn_expiry_threshold.setRange(1, 365)
        self.spn_expiry_threshold.setValue(30)
        self.spn_expiry_threshold.setSuffix(" روز")
        
        thresholds_layout.addRow("آستانه بحرانی:", self.spn_critical_threshold)
        thresholds_layout.addRow("آستانه هشدار:", self.spn_warning_threshold)
        thresholds_layout.addRow("هشدار انقضا:", self.spn_expiry_threshold)
        
        thresholds_group.setLayout(thresholds_layout)
        layout.addWidget(thresholds_group)
        
        # دکمه تست هشدار
        self.btn_test_alert = QPushButton("🔔 تست هشدار موجودی")
        self.btn_test_alert.clicked.connect(self.test_alert)
        layout.addWidget(self.btn_test_alert, 0, Qt.AlignRight)
        
        self.alerts_tab.setLayout(layout)
    
    def setup_categories_tab(self):
        """تنظیم تب دسته‌بندی‌ها"""
        layout = QVBoxLayout()
        
        # گروه دسته‌بندی قطعات
        parts_group = QGroupBox("🔩 دسته‌بندی قطعات")
        parts_layout = QVBoxLayout()
        
        # جدول دسته‌بندی‌های قطعات
        self.table_part_categories = QTableWidget()
        self.table_part_categories.setColumnCount(3)
        self.table_part_categories.setHorizontalHeaderLabels([
            "کد دسته", "نام دسته", "توضیحات"
        ])
        
        # تنظیمات جدول
        self.table_part_categories.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table_part_categories.setEditTriggers(QTableWidget.NoEditTriggers)
        
        parts_layout.addWidget(self.table_part_categories)
        
        # دکمه‌های مدیریت دسته‌بندی قطعات
        parts_actions = QHBoxLayout()
        
        self.btn_add_part_category = QPushButton("➕ افزودن دسته")
        self.btn_edit_part_category = QPushButton("✏️ ویرایش")
        self.btn_delete_part_category = QPushButton("🗑️ حذف")
        
        parts_actions.addWidget(self.btn_add_part_category)
        parts_actions.addWidget(self.btn_edit_part_category)
        parts_actions.addWidget(self.btn_delete_part_category)
        parts_actions.addStretch()
        
        parts_layout.addLayout(parts_actions)
        parts_group.setLayout(parts_layout)
        
        # گروه دسته‌بندی دستگاه‌ها
        devices_group = QGroupBox("📱 دسته‌بندی دستگاه‌ها")
        devices_layout = QVBoxLayout()
        
        # جدول دسته‌بندی‌های دستگاه‌ها
        self.table_device_categories = QTableWidget()
        self.table_device_categories.setColumnCount(3)
        self.table_device_categories.setHorizontalHeaderLabels([
            "کد دسته", "نام دسته", "نمونه دستگاه"
        ])
        
        # تنظیمات جدول
        self.table_device_categories.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table_device_categories.setEditTriggers(QTableWidget.NoEditTriggers)
        
        devices_layout.addWidget(self.table_device_categories)
        
        # دکمه‌های مدیریت دسته‌بندی دستگاه‌ها
        devices_actions = QHBoxLayout()
        
        self.btn_add_device_category = QPushButton("➕ افزودن دسته")
        self.btn_edit_device_category = QPushButton("✏️ ویرایش")
        self.btn_delete_device_category = QPushButton("🗑️ حذف")
        
        devices_actions.addWidget(self.btn_add_device_category)
        devices_actions.addWidget(self.btn_edit_device_category)
        devices_actions.addWidget(self.btn_delete_device_category)
        devices_actions.addStretch()
        
        devices_layout.addLayout(devices_actions)
        devices_group.setLayout(devices_layout)
        
        layout.addWidget(parts_group)
        layout.addWidget(devices_group)
        
        self.categories_tab.setLayout(layout)
    
    def apply_styles(self):
        """اعمال استایل"""
        self.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 12pt;
                color: #1abc9c;
                border: 2px solid #1abc9c;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                padding: 0 10px;
            }
            QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox {
                background-color: #222222;
                color: #ffffff;
                border: 1px solid #444444;
                border-radius: 3px;
                padding: 5px;
                min-height: 25px;
            }
            QCheckBox {
                color: #ffffff;
            }
            QPushButton {
                background-color: #2c3e50;
                color: white;
                border: none;
                padding: 8px 15px;
                border-radius: 4px;
                margin: 2px;
            }
            QPushButton:hover {
                background-color: #34495e;
            }
            QTableWidget {
                background-color: #111111;
                alternate-background-color: #0a0a0a;
                gridline-color: #333333;
                color: #ffffff;
                selection-background-color: #2c3e50;
            }
            QHeaderView::section {
                background-color: #2c3e50;
                color: white;
                padding: 5px;
                border: none;
            }
        """)
    
    def test_alert(self):
        """تست هشدار موجودی"""
        QMessageBox.information(
            self,
            "تست هشدار",
            "سیستم هشدار موجودی تست شد.\n"
            "در صورت وجود اقلام زیر حداقل، اعلان نمایش داده خواهد شد."
        )
    
    def load_categories(self):
        """بارگذاری دسته‌بندی‌ها"""
        # دسته‌بندی‌های قطعات
        part_categories = [
            ["P001", "الکترونیکی", "برد، آیسی، خازن، مقاومت"],
            ["P002", "مکانیکی", "گیربکس، بلبرینگ، شفت، بوش"],
            ["P003", "برقی", "موتور، سیم پیچ، کلید، فیوز"],
            ["P004", "تهویه", "کمپرسور، کندانسور، اواپراتور"],
            ["P005", "آب‌بندی", "اورینگ، گاسکت، واشر"],
        ]
        
        self.table_part_categories.setRowCount(len(part_categories))
        
        for row, category in enumerate(part_categories):
            for col, value in enumerate(category):
                item = QTableWidgetItem(value)
                item.setTextAlignment(Qt.AlignCenter)
                self.table_part_categories.setItem(row, col, item)
        
        # دسته‌بندی‌های دستگاه‌ها
        device_categories = [
            ["D001", "یخچال/فریزر", "یخچال ساید، فریزر عمودی، یخچال معمولی"],
            ["D002", "ماشین لباسشویی", "لباسشویی اتوماتیک، نیمه اتوماتیک"],
            ["D003", "ماشین ظرفشویی", "ظرفشویی معمولی، ساید بای ساید"],
            ["D004", "اجاق گاز", "گاز رومیزی، صفحه‌ای، توکار"],
            ["D005", "هود", "هود دیواری، هود جزیرهی"],
            ["D006", "جاروبرقی", "جاروبرقی معمولی، روباتیک، دستی"],
        ]
        
        self.table_device_categories.setRowCount(len(device_categories))
        
        for row, category in enumerate(device_categories):
            for col, value in enumerate(category):
                item = QTableWidgetItem(value)
                item.setTextAlignment(Qt.AlignCenter)
                self.table_device_categories.setItem(row, col, item)
    
    def load_settings(self, settings_data):
        """بارگذاری تنظیمات"""
        try:
            # واحدهای اندازه‌گیری
            length_unit = settings_data.get('length_unit', 'سانتی‌متر')
            length_index = self.cmb_length_unit.findText(length_unit)
            if length_index >= 0:
                self.cmb_length_unit.setCurrentIndex(length_index)
            
            weight_unit = settings_data.get('weight_unit', 'کیلوگرم')
            weight_index = self.cmb_weight_unit.findText(weight_unit)
            if weight_index >= 0:
                self.cmb_weight_unit.setCurrentIndex(weight_index)
            
            volume_unit = settings_data.get('volume_unit', 'لیتر')
            volume_index = self.cmb_volume_unit.findText(volume_unit)
            if volume_index >= 0:
                self.cmb_volume_unit.setCurrentIndex(volume_index)
            
            # تنظیمات شمارش
            self.spn_decimal_places.setValue(settings_data.get('decimal_places', 2))
            self.chk_auto_calculate.setChecked(settings_data.get('auto_calculate', True))
            self.chk_allow_negative.setChecked(settings_data.get('allow_negative', False))
            self.chk_fifo_method.setChecked(settings_data.get('fifo_method', True))
            
            # تنظیمات قیمت
            self.spn_price_decimal.setValue(settings_data.get('price_decimal', 0))
            self.dbl_default_markup.setValue(settings_data.get('default_markup', 30))
            self.chk_auto_update_price.setChecked(settings_data.get('auto_update_price', True))
            self.chk_include_tax.setChecked(settings_data.get('include_tax', True))
            
            # هشدارها
            self.chk_enable_alerts.setChecked(settings_data.get('enable_alerts', True))
            self.spn_alert_frequency.setValue(settings_data.get('alert_frequency', 4))
            self.chk_email_alerts.setChecked(settings_data.get('email_alerts', False))
            self.chk_sms_alerts.setChecked(settings_data.get('sms_alerts', False))
            
            # حداقل موجودی
            self.spn_new_parts_min.setValue(settings_data.get('new_parts_min', 10))
            self.spn_used_parts_min.setValue(settings_data.get('used_parts_min', 5))
            self.spn_new_appliances_min.setValue(settings_data.get('new_appliances_min', 3))
            self.spn_used_appliances_min.setValue(settings_data.get('used_appliances_min', 2))
            
            # آستانه‌ها
            self.spn_critical_threshold.setValue(settings_data.get('critical_threshold', 10))
            self.spn_warning_threshold.setValue(settings_data.get('warning_threshold', 30))
            self.spn_expiry_threshold.setValue(settings_data.get('expiry_threshold', 30))
            
        except Exception as e:
            print(f"خطا در بارگذاری تنظیمات انبار: {e}")
    
    def get_settings(self):
        """جمع‌آوری تنظیمات"""
        settings = {
            # واحدهای اندازه‌گیری
            'length_unit': self.cmb_length_unit.currentText(),
            'weight_unit': self.cmb_weight_unit.currentText(),
            'volume_unit': self.cmb_volume_unit.currentText(),
            
            # تنظیمات شمارش
            'decimal_places': self.spn_decimal_places.value(),
            'auto_calculate': self.chk_auto_calculate.isChecked(),
            'allow_negative': self.chk_allow_negative.isChecked(),
            'fifo_method': self.chk_fifo_method.isChecked(),
            
            # تنظیمات قیمت
            'price_decimal': self.spn_price_decimal.value(),
            'default_markup': self.dbl_default_markup.value(),
            'auto_update_price': self.chk_auto_update_price.isChecked(),
            'include_tax': self.chk_include_tax.isChecked(),
            
            # هشدارها
            'enable_alerts': self.chk_enable_alerts.isChecked(),
            'alert_frequency': self.spn_alert_frequency.value(),
            'email_alerts': self.chk_email_alerts.isChecked(),
            'sms_alerts': self.chk_sms_alerts.isChecked(),
            
            # حداقل موجودی
            'new_parts_min': self.spn_new_parts_min.value(),
            'used_parts_min': self.spn_used_parts_min.value(),
            'new_appliances_min': self.spn_new_appliances_min.value(),
            'used_appliances_min': self.spn_used_appliances_min.value(),
            
            # آستانه‌ها
            'critical_threshold': self.spn_critical_threshold.value(),
            'warning_threshold': self.spn_warning_threshold.value(),
            'expiry_threshold': self.spn_expiry_threshold.value(),
        }
        
        return settings