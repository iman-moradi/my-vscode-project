"""
فرم مدیریت انبار لوازم خانگی نو - نسخه کامل با استفاده از دیتابیس
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QLineEdit, QComboBox, QTableWidget,
    QTableWidgetItem, QHeaderView, QMessageBox,
    QGroupBox, QFormLayout, QSpinBox, QDoubleSpinBox,
    QTextEdit, QFrame, QCheckBox, QApplication, QInputDialog
)
from PySide6.QtCore import Qt, QDate, QTimer
from PySide6.QtGui import QColor, QFont
import jdatetime
from datetime import datetime
import re

from .base_inventory_form import BaseInventoryForm
from .widgets.currency_converter import CurrencyConverter
from .widgets.inventory_date_input import InventoryDateInput
from .widgets.enhanced_combo import EnhancedComboBox


class NewAppliancesForm(BaseInventoryForm):
    """فرم مدیریت انبار لوازم خانگی نو - نسخه اصلاح شده"""

    def __init__(self, parent=None):
        super().__init__("انبار لوازم خانگی نو", parent)
        self.current_edit_id = None
        self.all_data = []

        # 🔴 حتماً data_manager را از parent بگیریم
        if parent and hasattr(parent, 'data_manager'):
            self.data_manager = parent.data_manager
        else:
            self.data_manager = None

        self.setup_ui()
        
        # بارگذاری داده‌ها با تاخیر
        QTimer.singleShot(100, self.load_data)

    def setup_ui(self):
        """تنظیم رابط کاربری"""
        # هدر فرم
        self.create_header()
        
        # بخش فرم ورود داده
        self.create_form_section()
        
        # بخش جستجو
        self.create_search_section()
        
        # بخش لیست لوازم
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
        
        title_label = QLabel("🏠 انبار لوازم خانگی نو")
        title_label.setStyleSheet("""
            QLabel {
                font-size: 18px;
                font-weight: bold;
                color: #1e90ff;
                padding: 10px;
            }
        """)
        
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        
        # آمار سریع
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(20)
        
        self.total_items_label = QLabel("موجودی کل: 0 عدد")
        self.total_items_label.setStyleSheet("color: #27ae60; font-weight: bold;")
        
        self.low_stock_label = QLabel("موجودی کم: 0 عدد")
        self.low_stock_label.setStyleSheet("color: #f39c12; font-weight: bold;")
        
        self.total_value_label = QLabel("ارزش کل: 0 تومان")
        self.total_value_label.setStyleSheet("color: #3498db; font-weight: bold;")
        
        stats_layout.addWidget(self.total_value_label)
        stats_layout.addWidget(self.low_stock_label)
        stats_layout.addWidget(self.total_items_label)
        
        header_layout.addLayout(stats_layout)
        header_frame.setLayout(header_layout)
        
        self.main_layout.addWidget(header_frame)

    def create_form_section(self):
        """ایجاد بخش فرم ورود داده"""
        form_group, form_layout = self.create_form_group("📝 ثبت/ویرایش لوازم خانگی نو")
        
        # ردیف 1: نوع دستگاه و برند
        row1_layout = QHBoxLayout()
        row1_layout.setSpacing(15)
        
        self.device_type = EnhancedComboBox('category')
        self.device_type.combo.setMinimumWidth(200)
        self.device_type.combo.setPlaceholderText("-- انتخاب دسته‌بندی --")
        
        self.brand = EnhancedComboBox('brand')
        self.brand.combo.setMinimumWidth(200)
        self.brand.combo.setPlaceholderText("-- انتخاب برند --")
        
        row1_layout.addWidget(QLabel("برند:"))
        row1_layout.addWidget(self.brand, 2)
        row1_layout.addWidget(QLabel("نوع دستگاه:"))
        row1_layout.addWidget(self.device_type, 1)
        
        form_layout.addRow(row1_layout)
        
        # ردیف 2: مدل و شماره سریال
        row2_layout = QHBoxLayout()
        row2_layout.setSpacing(15)
        
        self.model = QLineEdit()
        self.model.setPlaceholderText("مدل دستگاه")
        
        self.serial_number = QLineEdit()
        self.serial_number.setPlaceholderText("شماره سریال (اختیاری)")
        self.serial_number.setMaximumWidth(250)
        
        row2_layout.addWidget(QLabel("شماره سریال:"))
        row2_layout.addWidget(self.serial_number, 1)
        row2_layout.addWidget(QLabel("مدل:"))
        row2_layout.addWidget(self.model, 2)
        
        form_layout.addRow(row2_layout)
        
        # ردیف 3: سال تولید و تعداد
        row3_layout = QHBoxLayout()
        row3_layout.setSpacing(15)
        
        self.production_year = QSpinBox()
        self.production_year.setRange(1300, 1500)
        self.production_year.setValue(jdatetime.datetime.now().year)
        self.production_year.setMaximumWidth(120)
        
        self.quantity = QSpinBox()
        self.quantity.setRange(1, 9999)
        self.quantity.setValue(1)
        self.quantity.setMaximumWidth(120)
        
        row3_layout.addWidget(QLabel("تعداد:"))
        row3_layout.addWidget(self.quantity)
        row3_layout.addWidget(QLabel("سال تولید:"))
        row3_layout.addWidget(self.production_year)
        
        form_layout.addRow(row3_layout)
        
        # ردیف 4: قیمت‌ها
        row4_layout = QHBoxLayout()
        row4_layout.setSpacing(15)
        
        purchase_label = QLabel("قیمت خرید:")
        self.purchase_price = CurrencyConverter()
        self.purchase_price.set_value(0)
        
        sale_label = QLabel("قیمت فروش:")
        self.sale_price = CurrencyConverter()
        self.sale_price.set_value(0)
        
        row4_layout.addWidget(sale_label)
        row4_layout.addWidget(self.sale_price, 2)
        row4_layout.addWidget(purchase_label)
        row4_layout.addWidget(self.purchase_price, 2)
        
        form_layout.addRow(row4_layout)
        
        # ردیف 5: تامین‌کننده و تاریخ خرید
        row5_layout = QHBoxLayout()
        row5_layout.setSpacing(15)
        
        self.supplier = EnhancedComboBox('supplier')
        self.supplier.combo.setPlaceholderText("-- انتخاب تامین‌کننده --")
        
        self.purchase_date = InventoryDateInput()
        self.purchase_date.set_date_to_today()
        
        row5_layout.addWidget(QLabel("تاریخ خرید:"))
        row5_layout.addWidget(self.purchase_date)
        row5_layout.addWidget(QLabel("تامین‌کننده:"))
        row5_layout.addWidget(self.supplier, 2)
        
        form_layout.addRow(row5_layout)
        
        # ردیف 6: گارانتی و محل نگهداری
        row6_layout = QHBoxLayout()
        row6_layout.setSpacing(15)
        
        self.warranty_months = QSpinBox()
        self.warranty_months.setRange(0, 120)
        self.warranty_months.setValue(12)
        self.warranty_months.setSuffix(" ماه")
        self.warranty_months.setMaximumWidth(150)
        
        self.location = QLineEdit()
        self.location.setPlaceholderText("مثلاً: قفسه اصلی، انبار سرد")
        self.location.setMaximumWidth(200)
        
        row6_layout.addWidget(QLabel("محل نگهداری:"))
        row6_layout.addWidget(self.location, 2)
        row6_layout.addWidget(QLabel("مدت گارانتی:"))
        row6_layout.addWidget(self.warranty_months)
        
        form_layout.addRow(row6_layout)
        
        # ردیف 7: وضعیت
        row7_layout = QHBoxLayout()
        row7_layout.setSpacing(15)
        
        self.status = QComboBox()
        self.status.addItems(["موجود", "ناموجود", "رزرو شده", "فروخته شده"])
        self.status.setMaximumWidth(150)
        
        row7_layout.addWidget(QLabel("وضعیت:"))
        row7_layout.addWidget(self.status)
        row7_layout.addStretch()
        
        form_layout.addRow(row7_layout)
        
        # ردیف 8: توضیحات
        self.description = QTextEdit()
        self.description.setMaximumHeight(100)
        self.description.setPlaceholderText("توضیحات تکمیلی درباره دستگاه...")
        
        form_layout.addRow("توضیحات:", self.description)
        
        self.main_layout.addWidget(form_group)

    def create_search_section(self):
        """ایجاد بخش جستجو"""
        search_group, search_layout = self.create_form_group("🔍 جستجوی پیشرفته")
        
        # ردیف اول جستجو
        row1_layout = QHBoxLayout()
        row1_layout.setSpacing(15)
        
        self.search_model = QLineEdit()
        self.search_model.setPlaceholderText("مدل دستگاه...")
        self.search_model.setMaximumWidth(200)
        
        self.search_serial = QLineEdit()
        self.search_serial.setPlaceholderText("شماره سریال...")
        self.search_serial.setMaximumWidth(200)
        
        self.search_device_type = EnhancedComboBox('category')
        self.search_device_type.combo.setPlaceholderText("همه انواع")
        self.search_device_type.combo.setMaximumWidth(200)
        
        row1_layout.addWidget(QLabel("نوع دستگاه:"))
        row1_layout.addWidget(self.search_device_type)
        row1_layout.addWidget(QLabel("شماره سریال:"))
        row1_layout.addWidget(self.search_serial)
        row1_layout.addWidget(QLabel("مدل:"))
        row1_layout.addWidget(self.search_model)
        
        search_layout.addRow(row1_layout)
        
        # ردیف دوم جستجو
        row2_layout = QHBoxLayout()
        row2_layout.setSpacing(15)
        
        self.search_brand = EnhancedComboBox('brand')
        self.search_brand.combo.setPlaceholderText("همه برندها")
        self.search_brand.combo.setMaximumWidth(200)
        
        self.search_supplier = EnhancedComboBox('supplier')
        self.search_supplier.combo.setPlaceholderText("همه تامین‌کنندگان")
        self.search_supplier.combo.setMaximumWidth(250)
        
        self.search_status = QComboBox()
        self.search_status.addItems(["همه وضعیت‌ها", "موجود", "ناموجود", "رزرو شده"])
        self.search_status.setMaximumWidth(150)
        
        row2_layout.addWidget(QLabel("وضعیت:"))
        row2_layout.addWidget(self.search_status)
        row2_layout.addWidget(QLabel("تامین‌کننده:"))
        row2_layout.addWidget(self.search_supplier)
        row2_layout.addWidget(QLabel("برند:"))
        row2_layout.addWidget(self.search_brand)
        
        search_layout.addRow(row2_layout)
        
        # ردیف سوم: بازه قیمت و سال تولید
        row3_layout = QHBoxLayout()
        row3_layout.setSpacing(15)
        
        self.min_price = QLineEdit()
        self.min_price.setPlaceholderText("حداقل قیمت")
        self.min_price.setMaximumWidth(120)
        
        self.max_price = QLineEdit()
        self.max_price.setPlaceholderText("حداکثر قیمت")
        self.max_price.setMaximumWidth(120)
        
        self.min_year = QSpinBox()
        self.min_year.setRange(1300, 1500)
        self.min_year.setValue(1390)
        self.min_year.setMaximumWidth(100)
        
        self.max_year = QSpinBox()
        self.max_year.setRange(1300, 1500)
        self.max_year.setValue(jdatetime.datetime.now().year)
        self.max_year.setMaximumWidth(100)
        
        row3_layout.addWidget(QLabel("حداکثر سال:"))
        row3_layout.addWidget(self.max_year)
        row3_layout.addWidget(QLabel("حداقل سال:"))
        row3_layout.addWidget(self.min_year)
        row3_layout.addWidget(QLabel("حداکثر قیمت:"))
        row3_layout.addWidget(self.max_price)
        row3_layout.addWidget(QLabel("حداقل قیمت:"))
        row3_layout.addWidget(self.min_price)
        
        search_layout.addRow(row3_layout)
        
        # دکمه‌های جستجو
        btn_layout = QHBoxLayout()
        
        btn_clear_search = QPushButton("🗑️ پاک کردن فیلترها")
        btn_clear_search.clicked.connect(self.clear_search_filters)
        btn_clear_search.setMaximumWidth(150)
        
        btn_search = QPushButton("🔍 جستجوی پیشرفته")
        btn_search.clicked.connect(self.perform_search)
        btn_search.setMaximumWidth(150)
        
        btn_layout.addStretch()
        btn_layout.addWidget(btn_clear_search)
        btn_layout.addWidget(btn_search)
        
        search_layout.addRow(btn_layout)
        
        self.main_layout.addWidget(search_group)
        
        # تنظیم جستجوی زنده
        search_fields = [self.search_model, self.search_serial, self.min_price, self.max_price]
        for field in search_fields:
            self.setup_live_search(field, self.perform_search)
        
        # برای کامبوباکس‌ها
        self.search_device_type.value_changed.connect(self.perform_search)
        self.search_brand.value_changed.connect(self.perform_search)
        self.search_supplier.value_changed.connect(self.perform_search)
        self.search_status.currentIndexChanged.connect(self.perform_search)
        
        # برای spin box‌ها
        self.min_year.valueChanged.connect(self.perform_search)
        self.max_year.valueChanged.connect(self.perform_search)

    def create_table_section(self):
        """ایجاد بخش جدول نمایش لوازم"""
        table_group, table_layout = self.create_form_group("📋 لیست لوازم خانگی نو")
        
        self.table = self.create_table([
            "ردیف",
            "نوع دستگاه",
            "برند",
            "مدل",
            "شماره سریال",
            "سال تولید",
            "تعداد",
            "قیمت خرید",
            "قیمت فروش",
            "وضعیت",
            "تاریخ خرید",
            "عملیات"
        ])
        
        # تنظیم عرض ستون‌ها
        self.table.setColumnWidth(0, 60)   # ردیف
        self.table.setColumnWidth(1, 120)  # نوع دستگاه
        self.table.setColumnWidth(2, 120)  # برند
        self.table.setColumnWidth(3, 150)  # مدل
        self.table.setColumnWidth(4, 150)  # شماره سریال
        self.table.setColumnWidth(5, 90)   # سال تولید
        self.table.setColumnWidth(6, 80)   # تعداد
        self.table.setColumnWidth(7, 130)  # قیمت خرید
        self.table.setColumnWidth(8, 130)  # قیمت فروش
        self.table.setColumnWidth(9, 100)  # وضعیت
        self.table.setColumnWidth(10, 110) # تاریخ خرید
        
        # تنظیم حداقل ارتفاع
        self.table.setMinimumHeight(300)
        
        table_layout.addRow(self.table)
        self.main_layout.addWidget(table_group)

    def create_action_buttons(self):
        """ایجاد دکمه‌های عملیات"""
        btn_group = QGroupBox("⚡ عملیات")
        btn_layout = QHBoxLayout()
        
        self.btn_save = QPushButton("💾 ذخیره لوازم")
        self.btn_save.clicked.connect(self.save_data)
        self.btn_save.setProperty("style", "primary")
        
        self.btn_new = QPushButton("🆕 لوازم جدید")
        self.btn_new.clicked.connect(self.clear_form)
        self.btn_new.setProperty("style", "info")
        
        self.btn_edit = QPushButton("✏️ ویرایش انتخاب شده")
        self.btn_edit.setEnabled(False)
        self.btn_edit.clicked.connect(self.on_edit)
        self.btn_edit.setProperty("style", "warning")
        
        # دکمه حذف با تراکنش
        self.btn_delete = QPushButton("🗑️ حذف با ثبت تراکنش")
        self.btn_delete.setEnabled(False)
        self.btn_delete.clicked.connect(self.on_delete_with_transaction)  # متصل به تابع جدید
        self.btn_delete.setProperty("style", "danger")
        
        # دکمه حذف نرم
        self.btn_soft_delete = QPushButton("📝 حذف نرم (تغییر وضعیت)")
        self.btn_soft_delete.setEnabled(False)
        self.btn_soft_delete.clicked.connect(self.on_soft_delete)  # متصل به تابع جدید
        self.btn_soft_delete.setProperty("style", "secondary")
        
        self.btn_export = QPushButton("📊 خروجی Excel")
        self.btn_export.clicked.connect(self.export_excel)
        
        self.btn_print = QPushButton("🖨️ چاپ گزارش")
        self.btn_print.clicked.connect(self.print_report)
        
        btn_layout.addWidget(self.btn_save)
        btn_layout.addWidget(self.btn_new)
        btn_layout.addWidget(self.btn_edit)
        btn_layout.addWidget(self.btn_delete)
        btn_layout.addWidget(self.btn_soft_delete)
        btn_layout.addWidget(self.btn_export)
        btn_layout.addWidget(self.btn_print)
        
        btn_group.setLayout(btn_layout)
        self.main_layout.addWidget(btn_group)
        
        # اتصال انتخاب جدول
        self.table.itemSelectionChanged.connect(self.on_table_selection_changed)

    def create_summary_section(self):
        """ایجاد بخش خلاصه"""
        summary_group = QGroupBox("📊 خلاصه وضعیت انبار")
        summary_layout = QHBoxLayout()
        
        # کارت‌های آمار
        stats = [
            ("موجودی کل", "📦", "27ae60", "0 عدد"),
            ("انواع مختلف", "🏷️", "9b59b6", "0 نوع"),
            ("ارزش کل", "💰", "3498db", "0 تومان"),
            ("میانگین قیمت", "📈", "f39c12", "0 تومان"),
        ]
        
        for title, icon, color, value in stats:
            card = self.create_stat_card(title, icon, color, value)
            summary_layout.addWidget(card)
        
        summary_group.setLayout(summary_layout)
        self.main_layout.addWidget(summary_group)

    def create_stat_card(self, title, icon, color, value):
        """ایجاد کارت آمار"""
        card = QFrame()
        card.setFrameShape(QFrame.StyledPanel)
        card.setStyleSheet(f"""
            QFrame {{
                background-color: #{color}20;
                border: 2px solid #{color};
                border-radius: 10px;
                padding: 15px;
            }}
        """)
        
        layout = QVBoxLayout()
        
        # هدر کارت
        header_layout = QHBoxLayout()
        icon_label = QLabel(icon)
        icon_label.setStyleSheet(f"font-size: 24px; color: #{color};")
        
        title_label = QLabel(title)
        title_label.setStyleSheet(f"""
            QLabel {{
                color: #{color};
                font-size: 12pt;
                font-weight: bold;
            }}
        """)
        
        header_layout.addWidget(icon_label)
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        
        layout.addLayout(header_layout)
        
        # مقدار
        value_label = QLabel(value)
        value_label.setStyleSheet("""
            QLabel {
                color: #ffffff;
                font-size: 14pt;
                font-weight: bold;
                padding: 10px 0;
            }
        """)
        value_label.setAlignment(Qt.AlignCenter)
        
        layout.addWidget(value_label)
        
        # ذخیره reference
        setattr(card, 'value_label', value_label)
        setattr(card, 'title', title)
        
        card.setLayout(layout)
        return card

    def perform_search(self):
        """اجرای جستجوی زنده"""
        try:
            # جمع‌آوری پارامترهای جستجو
            filters = {
                'model': self.search_model.text().strip(),
                'serial': self.search_serial.text().strip(),
                'device_type_id': self.search_device_type.get_value(),
                'brand_id': self.search_brand.get_value(),
                'supplier_id': self.search_supplier.get_value(),
                'status': self.search_status.currentText(),
                'min_price': self.min_price.text().strip(),
                'max_price': self.max_price.text().strip(),
                'min_year': self.min_year.value(),
                'max_year': self.max_year.value()
            }
            
            # فیلتر کردن داده‌ها
            filtered_data = []
            
            for item in self.all_data:
                match = True
                
                # فیلتر مدل
                if match and filters['model']:
                    model_lower = item.get('model', '').lower()
                    if filters['model'].lower() not in model_lower:
                        match = False
                
                # فیلتر شماره سریال
                if match and filters['serial']:
                    serial_lower = item.get('serial_number', '').lower()
                    if filters['serial'].lower() not in serial_lower:
                        match = False
                
                # فیلتر وضعیت
                if match and filters['status'] != 'همه وضعیت‌ها':
                    if filters['status'] != item.get('status', ''):
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
                    production_year = item.get('production_year', 0)
                    if production_year < filters['min_year']:
                        match = False
                    
                    if match and production_year > filters['max_year']:
                        match = False
                
                if match:
                    filtered_data.append(item)
            
            # نمایش نتایج
            self.populate_table(filtered_data)
            self.update_stats(filtered_data)
            
        except Exception as e:
            print(f"خطا در جستجو: {e}")

    def clear_search_filters(self):
        """پاک کردن تمام فیلترهای جستجو"""
        self.search_model.clear()
        self.search_serial.clear()
        self.search_device_type.clear()
        self.search_brand.clear()
        self.search_supplier.clear()
        self.search_status.setCurrentIndex(0)
        self.min_price.clear()
        self.max_price.clear()
        self.min_year.setValue(1390)
        self.max_year.setValue(jdatetime.datetime.now().year)
        
        self.perform_search()

    def load_data(self):
        """بارگذاری داده‌های لوازم نو از دیتابیس"""
        print("🔄 در حال بارگذاری داده‌های لوازم نو از دیتابیس...")
        
        try:
            if self.data_manager and hasattr(self.data_manager, 'warehouse'):
                # بارگذاری از دیتابیس
                warehouse_items = self.data_manager.warehouse.get_new_appliances_stock(show_all=True)
                
                if warehouse_items:
                    self.all_data = []
                    for item in warehouse_items:
                        # تبدیل تاریخ میلادی به شمسی برای نمایش
                        purchase_date_shamsi = self.miladi_to_shamsi(item.get('purchase_date', ''))
                        
                        data_item = {
                            'id': item.get('id'),
                            'device_type': item.get('device_type_name', 'نامشخص'),
                            'device_type_id': item.get('device_type_id'),
                            'brand': item.get('brand_name', 'نامشخص'),
                            'brand_id': item.get('brand_id'),
                            'model': item.get('model', 'بدون مدل'),
                            'serial_number': item.get('serial_number', ''),
                            'production_year': item.get('production_year', 1400),
                            'quantity': item.get('quantity', 0),
                            'purchase_price': item.get('purchase_price', 0),
                            'sale_price': item.get('sale_price', 0),
                            'status': item.get('status', 'موجود'),
                            'purchase_date': purchase_date_shamsi,  # شمسی برای نمایش
                            'purchase_date_miladi': item.get('purchase_date', ''),  # میلادی ذخیره
                            'supplier': item.get('supplier_name', ''),
                            'supplier_id': item.get('supplier_id'),
                            'location': item.get('location', ''),
                            'warranty_months': item.get('warranty_months', 12),
                            'description': item.get('description', '')
                        }
                        self.all_data.append(data_item)
                    
                    print(f"✅ {len(self.all_data)} آیتم از دیتابیس بارگذاری شد")
                    self.populate_table(self.all_data)
                    self.update_stats(self.all_data)
                else:
                    print("⚠️ دیتابیس لوازم نو خالی است")
                    self.show_warning("دیتابیس لوازم نو خالی است. لطفاً ابتدا داده اضافه کنید.")
                    self.all_data = []
            else:
                print("❌ data_manager یا warehouse موجود نیست")
                self.show_error("اتصال به دیتابیس برقرار نیست!")
                
        except Exception as e:
            print(f"❌ خطا در بارگذاری از دیتابیس: {e}")
            self.show_error(f"خطا در بارگذاری از دیتابیس: {str(e)}")

    def populate_table(self, data):
        """پر کردن جدول با داده‌ها"""
        self.table.setRowCount(len(data))
        
        for row, item in enumerate(data):
            # ردیف
            self.table.setItem(row, 0, QTableWidgetItem(str(row + 1)))
            self.table.item(row, 0).setTextAlignment(Qt.AlignCenter)
            
            # نوع دستگاه
            self.table.setItem(row, 1, QTableWidgetItem(item.get('device_type', '')))
            
            # برند
            self.table.setItem(row, 2, QTableWidgetItem(item.get('brand', '')))
            
            # مدل
            self.table.setItem(row, 3, QTableWidgetItem(item.get('model', '')))
            
            # شماره سریال
            self.table.setItem(row, 4, QTableWidgetItem(item.get('serial_number', '')))
            
            # سال تولید
            year_item = QTableWidgetItem(str(item.get('production_year', '')))
            year_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row, 5, year_item)
            
            # تعداد
            quantity = item.get('quantity', 0)
            qty_item = QTableWidgetItem(str(quantity))
            qty_item.setTextAlignment(Qt.AlignCenter)
            
            # رنگ‌آمیزی تعداد کم
            if quantity == 0:
                qty_item.setBackground(QColor('#e74c3c'))
                qty_item.setForeground(QColor('white'))
            elif quantity <= 2:
                qty_item.setBackground(QColor('#f39c12'))
                qty_item.setForeground(QColor('white'))
            
            self.table.setItem(row, 6, qty_item)
            
            # قیمت خرید
            purchase_price = item.get('purchase_price', 0)
            purchase_item = QTableWidgetItem(self.format_currency(purchase_price))
            purchase_item.setTextAlignment(Qt.AlignLeft)
            self.table.setItem(row, 7, purchase_item)
            
            # قیمت فروش
            sale_price = item.get('sale_price', 0)
            sale_item = QTableWidgetItem(self.format_currency(sale_price))
            sale_item.setTextAlignment(Qt.AlignLeft)
            self.table.setItem(row, 8, sale_item)
            
            # وضعیت
            status = item.get('status', '')
            status_item = QTableWidgetItem(status)
            status_item.setTextAlignment(Qt.AlignCenter)
            
            # رنگ وضعیت
            if status == 'موجود':
                status_item.setBackground(QColor('#27ae60'))
            elif status == 'رزرو شده':
                status_item.setBackground(QColor('#3498db'))
            elif status == 'ناموجود':
                status_item.setBackground(QColor('#e74c3c'))
            elif status == 'فروخته شده':
                status_item.setBackground(QColor('#9b59b6'))
            
            status_item.setForeground(QColor('white'))
            self.table.setItem(row, 9, status_item)
            
            # تاریخ خرید (شمسی)
            date_item = QTableWidgetItem(item.get('purchase_date', ''))
            date_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row, 10, date_item)
            
            # عملیات
            btn_widget = QWidget()
            btn_layout = QHBoxLayout()
            btn_layout.setContentsMargins(2, 2, 2, 2)
            
            btn_edit = QPushButton("✏️")
            btn_edit.setFixedSize(35, 35)
            btn_edit.setToolTip("ویرایش لوازم")
            btn_edit.clicked.connect(lambda checked, idx=item['id']: self.edit_item(idx))
            
            # دکمه حذف با تراکنش
            btn_delete = QPushButton("🗑️")
            btn_delete.setFixedSize(35, 35)
            btn_delete.setToolTip("حذف با ثبت تراکنش")
            btn_delete.clicked.connect(lambda checked, idx=item['id']: self.on_delete_with_transaction_for_item(idx))
            
            # دکمه حذف نرم
            btn_soft_delete = QPushButton("📝")
            btn_soft_delete.setFixedSize(35, 35)
            btn_soft_delete.setToolTip("حذف نرم (تغییر وضعیت)")
            btn_soft_delete.clicked.connect(lambda checked, idx=item['id']: self.on_soft_delete_for_item(idx))
            
            btn_layout.addWidget(btn_edit)
            btn_layout.addWidget(btn_delete)
            btn_layout.addWidget(btn_soft_delete)
            btn_layout.addStretch()
            
            btn_widget.setLayout(btn_layout)
            self.table.setCellWidget(row, 11, btn_widget)  # 🔴 ستون 11 برای عملیات


    def update_stats(self, data):
        """به‌روزرسانی آمار"""
        try:
            total_quantity = sum(item.get('quantity', 0) for item in data)
            unique_types = len(set(item.get('device_type', '') for item in data))
            total_value = sum(item.get('purchase_price', 0) * item.get('quantity', 0) for item in data)
            avg_price = total_value / total_quantity if total_quantity > 0 else 0
            
            # به‌روزرسانی برچسب‌های هدر
            self.total_items_label.setText(f"موجودی کل: {total_quantity:,} عدد")
            self.low_stock_label.setText(f"انواع مختلف: {unique_types:,} نوع")
            self.total_value_label.setText(f"ارزش کل: {self.format_currency(total_value)}")
            
            # به‌روزرسانی کارت‌های خلاصه
            for i in range(self.main_layout.count()):
                item = self.main_layout.itemAt(i)
                if item and hasattr(item.widget(), 'title'):
                    card = item.widget()
                    if card.title == "موجودی کل":
                        card.value_label.setText(f"{total_quantity:,} عدد")
                    elif card.title == "انواع مختلف":
                        card.value_label.setText(f"{unique_types:,} نوع")
                    elif card.title == "ارزش کل":
                        card.value_label.setText(self.format_currency(total_value))
                    elif card.title == "میانگین قیمت":
                        card.value_label.setText(self.format_currency(avg_price))
        except Exception as e:
            print(f"خطا در به‌روزرسانی آمار: {e}")

    def on_table_selection_changed(self):
        """هنگام تغییر انتخاب در جدول"""
        selected_rows = self.table.selectionModel().selectedRows()
        has_selection = len(selected_rows) > 0
        
        self.btn_edit.setEnabled(has_selection)
        self.btn_delete.setEnabled(has_selection)

    def clear_form(self):
        """پاک کردن فرم"""
        self.current_edit_id = None
        self.device_type.clear()
        self.brand.clear()
        self.model.clear()
        self.serial_number.clear()
        self.production_year.setValue(jdatetime.datetime.now().year)
        self.quantity.setValue(1)
        self.purchase_price.set_value(0)
        self.sale_price.set_value(0)
        self.supplier.clear()
        self.purchase_date.set_date_to_today()
        self.warranty_months.setValue(12)
        self.location.clear()
        self.status.setCurrentIndex(0)
        self.description.clear()
        
        self.btn_save.setText("💾 ذخیره لوازم")
        self.btn_save.setProperty("style", "primary")
        self.table.clearSelection()

    def validate_form(self):
        """اعتبارسنجی فرم - نسخه اصلاح شده"""
        errors = []
        
        if self.device_type.get_value() == 0:
            errors.append("نوع دستگاه الزامی است.")
        
        if self.brand.get_value() == 0:
            errors.append("برند الزامی است.")
        
        if not self.model.text().strip():
            errors.append("مدل دستگاه الزامی است.")
        
        if self.quantity.value() <= 0:
            errors.append("تعداد باید بزرگتر از صفر باشد.")
        
        try:
            purchase_price = float(self.purchase_price.get_value_toman())
            if purchase_price <= 0:
                errors.append("قیمت خرید باید بزرگتر از صفر باشد.")
        except:
            errors.append("قیمت خرید نامعتبر است.")
        
        try:
            sale_price = float(self.sale_price.get_value_toman())
            if sale_price <= 0:
                errors.append("قیمت فروش باید بزرگتر از صفر باشد.")
        except:
            errors.append("قیمت فروش نامعتبر است.")
        
        if self.supplier.get_value() == 0:
            errors.append("تامین‌کننده الزامی است.")
        
        if errors:
            error_msg = "\n".join(f"• {error}" for error in errors)
            self.show_error(f"لطفا خطاهای زیر را اصلاح کنید:\n\n{error_msg}")
            return False
        
        return True

    def save_data(self):
        """ذخیره داده‌های لوازم در دیتابیس - نسخه اصلاح شده با ثبت تراکنش انبار"""
        try:
            # 🔴 تعریف متغیر message با مقدار پیش‌فرض
            message = "ثبت"
            
            # اعتبارسنجی
            if not self.validate_form():
                return
            
            # 🔴 گرفتن تاریخ شمسی از ویجت
            purchase_date_shamsi = self.purchase_date.get_date_string()
            print(f"📅 تاریخ خرید (شمسی): {purchase_date_shamsi}")
            
            # 🔴 تبدیل تاریخ شمسی به میلادی
            purchase_date_miladi = self.shamsi_to_miladi(purchase_date_shamsi)
            print(f"📅 تاریخ خرید (میلادی): {purchase_date_miladi}")
            
            # 🔴 تولید شماره سریال اگر خالی است
            serial_number = self.serial_number.text().strip()
            if not serial_number:
                import time
                timestamp = int(time.time() * 1000)
                serial_number = f"NEW-{timestamp}"
                print(f"📝 شماره سریال خودکار: {serial_number}")
            
            # آماده‌سازی داده‌ها
            data = {
                'device_type_id': self.device_type.get_value(),
                'brand_id': self.brand.get_value(),
                'model': self.model.text().strip(),
                'serial_number': serial_number,
                'production_year': self.production_year.value(),
                'quantity': self.quantity.value(),
                'purchase_price': float(self.purchase_price.get_value_toman()),
                'sale_price': float(self.sale_price.get_value_toman()),
                'supplier_id': self.supplier.get_value(),
                'purchase_date': purchase_date_miladi,  # میلادی
                'warranty_months': self.warranty_months.value(),
                'location': self.location.text().strip(),
                'status': self.status.currentText(),
                'description': self.description.toPlainText().strip(),
                'employee': 'سیستم'  # برای ثبت تراکنش
            }
            
            print(f"🔄 در حال ذخیره لوازم خانگی نو...")
            print(f"   مدل: {data['model']}")
            print(f"   تعداد: {data['quantity']}")
            print(f"   قیمت خرید: {data['purchase_price']:,}")
            
            # ذخیره در دیتابیس
            if self.data_manager and hasattr(self.data_manager, 'warehouse'):
                if self.current_edit_id:
                    # 🔴 برای حالت ویرایش، مستقیماً از کوئری UPDATE استفاده می‌کنیم
                    # زیرا تابع update_warehouse_item ستون updated_at را اضافه می‌کند که وجود ندارد
                    message = "ویرایش"
                    
                    # دریافت اطلاعات قبلی برای مقایسه
                    old_item_query = """
                    SELECT quantity, purchase_price, model, device_type_id, brand_id,
                        serial_number, production_year, sale_price, supplier_id,
                        purchase_date, warranty_months, location, status, description
                    FROM NewAppliancesWarehouse 
                    WHERE id = ?
                    """
                    old_item = self.data_manager.db.fetch_one(old_item_query, (self.current_edit_id,))
                    
                    if not old_item:
                        self.show_error("آیتم مورد نظر برای ویرایش یافت نشد!")
                        return
                    
                    old_quantity = old_item.get('quantity', 0)
                    old_price = old_item.get('purchase_price', 0)
                    old_model = old_item.get('model', '')
                    
                    # 🔴 کوئری UPDATE بدون ستون updated_at
                    update_query = """
                    UPDATE NewAppliancesWarehouse 
                    SET device_type_id = ?, brand_id = ?, model = ?, serial_number = ?, 
                        production_year = ?, quantity = ?, purchase_price = ?, sale_price = ?, 
                        supplier_id = ?, purchase_date = ?, warranty_months = ?, 
                        location = ?, status = ?, description = ?
                    WHERE id = ?
                    """
                    
                    params = (
                        data['device_type_id'],
                        data['brand_id'],
                        data['model'],
                        data['serial_number'],
                        data['production_year'],
                        data['quantity'],
                        data['purchase_price'],
                        data['sale_price'],
                        data['supplier_id'],
                        data['purchase_date'],
                        data['warranty_months'],
                        data['location'],
                        data['status'],
                        data['description'],
                        self.current_edit_id
                    )
                    
                    success = self.data_manager.db.execute_query(update_query, params)
                    
                    if success:
                        # 🔴 محاسبه تغییرات برای ثبت تراکنش
                        quantity_change = data['quantity'] - old_quantity
                        price_change = data['purchase_price'] - old_price
                        
                        # اگر تغییر در تعداد یا قیمت وجود داشت، تراکنش ثبت کن
                        if quantity_change != 0 or price_change != 0:
                            transaction_type = 'ویرایش موجودی' if quantity_change != 0 else 'تغییر قیمت'
                            
                            transaction_query = """
                            INSERT INTO InventoryTransactions (
                                transaction_type, warehouse_type, item_id, quantity, unit_price,
                                total_price, transaction_date, related_document, description, employee
                            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                            """
                            
                            from PySide6.QtCore import QDateTime
                            transaction_date = QDateTime.currentDateTime().toString("yyyy-MM-dd HH:mm:ss")
                            
                            # برای تغییر تعداد
                            if quantity_change != 0:
                                transaction_params = (
                                    transaction_type,
                                    'لوازم نو',
                                    self.current_edit_id,
                                    quantity_change,
                                    data['purchase_price'],
                                    abs(quantity_change * data['purchase_price']),
                                    transaction_date,
                                    'بدون شماره سند',
                                    f"{transaction_type} - {data['model']} (قبلی: {old_quantity} عدد)",
                                    data['employee']
                                )
                            # برای تغییر قیمت
                            else:
                                transaction_params = (
                                    transaction_type,
                                    'لوازم نو',
                                    self.current_edit_id,
                                    0,
                                    data['purchase_price'],
                                    0,
                                    transaction_date,
                                    'بدون شماره سند',
                                    f"{transaction_type} - {data['model']} (قبلی: {old_price:,} تومان)",
                                    data['employee']
                                )
                            
                            self.data_manager.db.execute_query(transaction_query, transaction_params)
                            print(f"   ✅ تراکنش {transaction_type} ثبت شد")
                        
                        result = (True, self.current_edit_id)
                    else:
                        result = (False, None)
                else:
                    # 🔴 افزودن جدید با استفاده از تابع جدید
                    result = self.add_new_appliance_to_warehouse(data)
                
                # بررسی نتیجه
                if isinstance(result, tuple) and len(result) > 0:
                    success = result[0]
                    if success:
                        if len(result) > 1:
                            item_id = result[1]
                            print(f"✅ لوازم #{item_id} با موفقیت {message} شد.")
                        else:
                            print(f"✅ لوازم با موفقیت {message} شد.")
                        
                        # سیگنال تغییر داده
                        if hasattr(self, 'data_changed'):
                            self.data_changed.emit()
                        
                        # نمایش پیام موفقیت
                        self.show_success(f"لوازم خانگی با موفقیت {message} شد.")
                        
                        # پاک کردن فرم و تازه‌سازی
                        self.clear_form()
                        self.load_data()  # بارگذاری مجدد از دیتابیس
                    else:
                        self.show_error(f"خطا در {message} لوازم!")
                else:
                    success = result
                    if success:
                        print(f"✅ لوازم با موفقیت {message} شد.")
                        
                        # سیگنال تغییر داده
                        if hasattr(self, 'data_changed'):
                            self.data_changed.emit()
                        
                        self.show_success(f"لوازم خانگی با موفقیت {message} شد.")
                        self.clear_form()
                        self.load_data()
                    else:
                        self.show_error(f"خطا در {message} لوازم!")
            else:
                self.show_error("اتصال به دیتابیس برقرار نیست!")
                
        except Exception as e:
            print(f"❌ خطا در ذخیره لوازم: {e}")
            import traceback
            traceback.print_exc()
            self.show_error(f"خطا در ذخیره لوازم: {str(e)}")


    def add_new_appliance_to_warehouse(self, data):
        """افزودن لوازم نو به انبار و ثبت تراکنش"""
        try:
            print(f"   🔄 افزودن لوازم نو به انبار...")
            
            # 🔴 ثبت در جدول NewAppliancesWarehouse
            query = """
            INSERT INTO NewAppliancesWarehouse (
                device_type_id, brand_id, model, serial_number, production_year,
                quantity, purchase_price, sale_price, supplier_id,
                purchase_date, warranty_months, location, status, description
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            
            params = (
                data['device_type_id'],
                data['brand_id'],
                data['model'],
                data['serial_number'],
                data['production_year'],
                data['quantity'],
                data['purchase_price'],
                data['sale_price'],
                data['supplier_id'],
                data['purchase_date'],
                data['warranty_months'],
                data['location'],
                data['status'],
                data['description']
            )
            
            # اجرای کوئری اصلی
            success = self.data_manager.db.execute_query(query, params)
            
            if not success:
                print(f"   ❌ خطا در ثبت لوازم نو")
                return (False, None)
            
            # 🔴 دریافت ID دستگاه اضافه شده
            get_id_query = """
            SELECT id FROM NewAppliancesWarehouse 
            WHERE serial_number = ? 
            ORDER BY id DESC LIMIT 1
            """
            
            result = self.data_manager.db.fetch_one(get_id_query, (data['serial_number'],))
            
            if result and 'id' in result:
                item_id = result['id']
                print(f"   🎯 لوازم نو با شناسه {item_id} ثبت شد")
                
                # 🔴 ثبت تراکنش انبار
                try:
                    print(f"   📝 در حال ثبت تراکنش انبار...")
                    
                    transaction_query = """
                    INSERT INTO InventoryTransactions (
                        transaction_type, warehouse_type, item_id, quantity, unit_price,
                        total_price, transaction_date, related_document, description, employee
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """
                    
                    # تاریخ و زمان فعلی (میلادی)
                    from PySide6.QtCore import QDateTime
                    transaction_date = QDateTime.currentDateTime().toString("yyyy-MM-dd HH:mm:ss")
                    
                    # محاسبه قیمت کل
                    quantity = data['quantity']
                    purchase_price = data['purchase_price']
                    total_price = quantity * purchase_price
                    
                    transaction_params = (
                        'خرید',
                        'لوازم نو',
                        item_id,
                        quantity,
                        purchase_price,
                        total_price,
                        transaction_date,
                        'بدون شماره سند',
                        f"خرید لوازم نو - {data['model']}",
                        data.get('employee', 'سیستم')
                    )
                    
                    transaction_success = self.data_manager.db.execute_query(transaction_query, transaction_params)
                    
                    if transaction_success:
                        print(f"   ✅ تراکنش انبار برای لوازم #{item_id} ثبت شد")
                    else:
                        print(f"   ⚠️ خطا در ثبت تراکنش انبار (اما لوازم ذخیره شد)")
                    
                except Exception as trans_error:
                    print(f"   ⚠️ خطا در ثبت تراکنش انبار: {trans_error}")
                    # خطای تراکنش نباید ذخیره لوازم را مختل کند
                
                return (True, item_id)
            else:
                print(f"   ❌ نتوانستیم ID لوازم را پیدا کنیم")
                return (False, None)
                
        except Exception as e:
            print(f"   ❌ خطا در افزودن لوازم نو: {e}")
            import traceback
            traceback.print_exc()
            return (False, None)

    def on_edit(self):
        """ویرایش لوازم انتخاب شده"""
        selected_rows = self.table.selectionModel().selectedRows()
        if selected_rows:
            row = selected_rows[0].row()
            if row < len(self.all_data):
                item_id = self.all_data[row]['id']
                self.edit_item(item_id)

    def _convert_days_to_months(self, days):
        """تبدیل روز به ماه برای گارانتی"""
        if days == 0:
            return 'بدون گارانتی'
        elif days <= 30:
            return f'{days} روز'
        elif days <= 90:
            months = days // 30
            return f'{months} ماه'
        else:
            years = days // 365
            if years > 0:
                return f'{years} سال'
            else:
                months = days // 30
                return f'{months} ماه'

    # 🔴 افزودن تابع تبدیل ماه به روز برای گارانتی
    def _convert_months_to_days(self, warranty_text):
        """تبدیل متن گارانتی به تعداد روز"""
        if not warranty_text:
            return 0
        
        if 'روز' in warranty_text:
            try:
                days = int(warranty_text.split()[0])
                return days
            except:
                return 30
        elif 'ماه' in warranty_text:
            try:
                months = int(warranty_text.split()[0])
                return months * 30
            except:
                return 365
        elif 'سال' in warranty_text:
            try:
                years = int(warranty_text.split()[0])
                return years * 365
            except:
                return 365
        else:
            return 0


    def delete_item_with_transaction(self, item_id, reason="حذف دستی"):
        """حذف لوازم نو با ثبت تراکنش - دقیقاً مشابه UsedPartsForm"""
        print(f"🔴 delete_item_with_transaction شروع شد برای item_id: {item_id}")
        
        try:
            if not self.data_manager or not hasattr(self.data_manager, 'warehouse'):
                self.show_error("اتصال به دیتابیس برقرار نیست!")
                return False
            
            # دریافت اطلاعات کامل آیتم قبل از حذف
            print(f"🔴 در حال دریافت اطلاعات آیتم {item_id}...")
            item_info = self.data_manager.warehouse.get_warehouse_item_info('لوازم نو', item_id)
            
            if not item_info:
                self.show_error("آیتم مورد نظر یافت نشد!")
                return False
            
            # نمایش تاییدیه ساده با QMessageBox
            print(f"🔴 نمایش تاییدیه حذف...")
            
            # ساخت پیام اطلاعاتی
            message_text = f"""
            <div style='font-family: B Nazanin; font-size: 12pt;'>
            <b style='color: red;'>⚠️ تایید حذف لوازم با ثبت تراکنش</b>
            <hr>
            <b>نوع دستگاه:</b> {item_info.get('device_type_name', 'نامشخص')}
            <br><b>برند:</b> {item_info.get('brand_name', 'نامشخص')}
            <br><b>مدل:</b> {item_info.get('model', 'نامشخص')}
            <br><b>شماره سریال:</b> {item_info.get('serial_number', 'نامشخص')}
            <br><b>موجودی:</b> {item_info.get('quantity', 0):,} عدد
            <br><b>قیمت خرید:</b> {self.format_currency(item_info.get('purchase_price', 0))}
            <br><b>ارزش کل:</b> {self.format_currency(item_info.get('quantity', 0) * item_info.get('purchase_price', 0))}
            <hr>
            <b style='color: darkred;'>این عمل قابل بازگشت نیست!</b>
            </div>
            """
            
            # نمایش تاییدیه اولیه
            reply = QMessageBox.question(
                self,
                "تایید حذف لوازم",
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
            
            # فراخوانی تابع حذف از WarehouseManager - بدون transaction_type
            success = self.data_manager.warehouse.delete_warehouse_item(
                warehouse_type='لوازم نو',
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
                    f"لوازم '{item_info.get('model')}' با موفقیت حذف شد.\nتراکنش حذف در سیستم ثبت گردید."
                )
                
                # ثبت لاگ
                log_data = {
                    'user_id': 1,
                    'action': 'حذف لوازم نو',
                    'table_name': 'NewAppliancesWarehouse',
                    'record_id': item_id,
                    'details': f"حذف لوازم {item_info.get('model')} ({item_info.get('serial_number')}) - دلیل: {reason_text}",
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
            
            # پیدا کردن آیتم در all_data با استفاده از ردیف
            if row < len(self.all_data):
                item_id = self.all_data[row]['id']
                print(f"🔴 item_id از طریق ردیف: {item_id}")
            else:
                # اگر نتوانستیم از all_data پیدا کنیم، سعی می‌کنیم از جدول اطلاعات بگیریم
                # گرفتن مدل از ستون سوم (ستون 2)
                model_item = self.table.item(row, 2)
                if not model_item:
                    self.show_error("نمی‌توان مدل را پیدا کرد.")
                    return
                
                model_name = model_item.text()
                
                # جستجو در all_data بر اساس مدل
                item_id = None
                for item in self.all_data:
                    if item.get('model') == model_name:
                        item_id = item.get('id')
                        break
                
                if not item_id:
                    self.show_error("آیتم انتخاب شده در داده‌ها یافت نشد.")
                    return
            
            # حذف با ثبت تراکنش
            print(f"🔴 فراخوانی delete_item_with_transaction با item_id: {item_id}")
            if self.delete_item_with_transaction(item_id):
                self.show_success("لوازم با موفقیت حذف شد و تراکنش ثبت گردید.")
                
                # تازه‌سازی داده‌ها
                print("🔴 تازه‌سازی داده‌ها...")
                self.load_from_database()
                
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
            self.show_success("لوازم با موفقیت حذف شد و تراکنش ثبت گردید.")
            self.load_from_database()
            if hasattr(self, 'data_changed'):
                self.data_changed.emit()

    def soft_delete_item(self, item_id, reason="حذف نرم"):
        """حذف نرم لوازم (تغییر وضعیت) - نسخه ساده شده"""
        try:
            if not self.data_manager or not hasattr(self.data_manager, 'warehouse'):
                self.show_error("اتصال به دیتابیس برقرار نیست!")
                return False
            
            # نمایش تاییدیه
            reply = QMessageBox.question(
                self,
                "تایید حذف نرم",
                "آیا از تغییر وضعیت این لوازم به 'ناموجود' اطمینان دارید؟\n\n(این لوازم از لیست موجودی حذف می‌شود اما در دیتابیس باقی می‌ماند)",
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
            
            # فراخوانی تابع حذف نرم - بدون transaction_type
            success = self.data_manager.warehouse.delete_warehouse_item(
                warehouse_type='لوازم نو',
                item_id=item_id,
                soft_delete=True,  # حذف نرم
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
            self.load_from_database()
            if hasattr(self, 'data_changed'):
                self.data_changed.emit()

    def on_soft_delete(self):
        """حذف نرم برای لوازم انتخاب شده"""
        selected_rows = self.table.selectionModel().selectedRows()
        if selected_rows:
            row = selected_rows[0].row()
            if row < len(self.all_data):
                item_id = self.all_data[row]['id']
                
                if self.soft_delete_item(item_id):
                    self.show_success("حذف نرم با موفقیت انجام شد (وضعیت تغییر یافت).")
                    self.load_from_database()
                    if hasattr(self, 'data_changed'):
                        self.data_changed.emit()

    # 🔴 تصحیح تابع on_delete_with_transaction
    def on_delete_with_transaction(self):
        """حذف با ثبت تراکنش برای لوازم انتخاب شده"""
        try:
            selected_rows = self.table.selectionModel().selectedRows()
            if not selected_rows:
                self.show_warning("لطفاً یک آیتم را از جدول انتخاب کنید.")
                return
            
            row = selected_rows[0].row()
            print(f"🔴 ردیف انتخاب شده: {row}")
            
            if row >= self.table.rowCount():
                self.show_error("ردیف انتخاب شده معتبر نیست.")
                return
            
            # گرفتن شماره سریال از ستون چهارم (ستون 4)
            serial_item = self.table.item(row, 4)
            if not serial_item:
                self.show_error("نمی‌توان شماره سریال را پیدا کرد.")
                return
            
            serial_number = serial_item.text()
            print(f"🔴 شماره سریال: {serial_number}")
            
            # پیدا کردن آیتم در all_data
            item_id = None
            for item in self.all_data:
                if str(item.get('serial_number', '')) == serial_number:
                    item_id = item.get('id')
                    print(f"🔴 یافتن item_id: {item_id}")
                    break
            
            if not item_id:
                if row < len(self.all_data):
                    item_id = self.all_data[row].get('id')
                    print(f"🔴 item_id از طریق ردیف: {item_id}")
            
            if not item_id:
                self.show_error("آیتم انتخاب شده در داده‌ها یافت نشد.")
                return
            
            # حذف با ثبت تراکنش
            print(f"🔴 فراخوانی delete_item_with_transaction با item_id: {item_id}")
            if self.delete_item_with_transaction(item_id):
                self.show_success("لوازم با موفقیت حذف شد و تراکنش ثبت گردید.")
                
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

    # 🔴 تصحیح تابع edit_item برای کار با تاریخ شمسی
    def edit_item(self, item_id):
        """ویرایش لوازم"""
        try:
            # پیدا کردن لوازم
            item_to_edit = None
            for item in self.all_data:
                if item['id'] == item_id:
                    item_to_edit = item
                    break
            
            if not item_to_edit:
                self.show_error("لوازم مورد نظر یافت نشد.")
                return
            
            self.current_edit_id = item_id
            
            # پر کردن فرم
            self.device_type.set_value(item_to_edit.get('device_type_id', 0))
            self.brand.set_value(item_to_edit.get('brand_id', 0))
            self.model.setText(item_to_edit.get('model', ''))
            self.serial_number.setText(item_to_edit.get('serial_number', ''))
            self.production_year.setValue(item_to_edit.get('production_year', jdatetime.datetime.now().year))
            self.quantity.setValue(item_to_edit.get('quantity', 1))
            self.purchase_price.set_value(item_to_edit.get('purchase_price', 0))
            self.sale_price.set_value(item_to_edit.get('sale_price', 0))
            self.supplier.set_value(item_to_edit.get('supplier_id', 0))
            
            # تنظیم تاریخ شمسی
            purchase_date_miladi = item_to_edit.get('purchase_date_miladi', '')
            if purchase_date_miladi:
                purchase_date_shamsi = self.miladi_to_shamsi(purchase_date_miladi)
                self.purchase_date.set_date(purchase_date_shamsi)
            
            # تبدیل گارانتی ماه به متن
            warranty_months = item_to_edit.get('warranty_months', 12)
            self.warranty_months.setValue(warranty_months)
            
            self.location.setText(item_to_edit.get('location', ''))
            
            status_index = self.status.findText(item_to_edit.get('status', 'موجود'))
            if status_index >= 0:
                self.status.setCurrentIndex(status_index)
            
            self.description.setText(item_to_edit.get('description', ''))
            
            # تغییر دکمه ذخیره
            self.btn_save.setText("💾 به‌روزرسانی لوازم")
            self.btn_save.setProperty("style", "warning")
            
            # اسکرول به بالا
            if hasattr(self, 'scroll_area'):
                self.scroll_area.verticalScrollBar().setValue(0)
            
        except Exception as e:
            print(f"خطا در ویرایش لوازم: {e}")
            self.show_error(f"خطا در ویرایش لوازم: {str(e)}")

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

    def shamsi_to_miladi(self, shamsi_date_str):
        """تبدیل تاریخ شمسی به میلادی"""
        if not shamsi_date_str:
            return None
        
        try:
            import re
            numbers = re.findall(r'\d+', str(shamsi_date_str))
            
            if len(numbers) >= 3:
                year, month, day = map(int, numbers[:3])
                
                if 1300 <= year <= 1500:
                    jalali = jdatetime.date(year, month, day)
                    gregorian = jalali.togregorian()
                    return gregorian.strftime("%Y-%m-%d")
                else:
                    return f"{year:04d}-{month:02d}-{day:02d}"
            else:
                from PySide6.QtCore import QDate
                return QDate.currentDate().toString("yyyy-MM-dd")
                
        except Exception as e:
            print(f"خطا در تبدیل شمسی به میلادی: {e}")
            from PySide6.QtCore import QDate
            return QDate.currentDate().toString("yyyy-MM-dd")

    def miladi_to_shamsi(self, miladi_date_str, format_str="%Y-%m-%d"):
        """تبدیل تاریخ میلادی به شمسی"""
        if not miladi_date_str:
            return ""
        
        try:
            import re
            numbers = re.findall(r'\d+', str(miladi_date_str))
            
            if len(numbers) >= 3:
                year, month, day = map(int, numbers[:3])
                
                if year > 1500:
                    from datetime import date
                    gregorian_date = date(year, month, day)
                    jalali = jdatetime.date.fromgregorian(date=gregorian_date)
                    return jalali.strftime("%Y/%m/%d")
                else:
                    return f"{year:04d}/{month:02d}/{day:02d}"
            else:
                return str(miladi_date_str)
                
        except Exception as e:
            print(f"خطا در تبدیل میلادی به شمسی: {e}")
            return str(miladi_date_str)


    def export_excel(self):
        """خروجی Excel"""
        self.show_success("خروجی Excel تولید شد (ویژگی در حال توسعه).")

    def print_report(self):
        """چاپ گزارش"""
        self.show_success("گزارش آماده چاپ است (ویژگی در حال توسعه).")