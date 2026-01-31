# ui/forms/part_form.py - نسخه کامل و اصلاح شده
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
    QLineEdit, QPushButton, QMessageBox, QComboBox,
    QFormLayout, QSpinBox, QTextEdit, QGroupBox,
    QScrollArea, QWidget, QFrame, QDoubleSpinBox
)
from PySide6.QtCore import Qt, Signal
import sys
import os

# اضافه کردن مسیر پروژه
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "../../"))
if project_root not in sys.path:
    sys.path.append(project_root)

try:
    from ui.widgets.jalali_date_input import JalaliDateInput
    from ui.widgets.searchable_combo import SearchableCombo
    print("✅ ویجت‌های سفارشی import شدند")
except ImportError as e:
    print(f"⚠️ خطا در import ویجت‌های سفارشی: {e}")
    # ایجاد کلاس‌های جایگزین برای تست
    class JalaliDateInput(QWidget):
        def __init__(self, parent=None):
            super().__init__(parent)
            from PySide6.QtWidgets import QLineEdit, QPushButton, QHBoxLayout
            layout = QHBoxLayout(self)
            self.date_input = QLineEdit()
            self.date_input.setPlaceholderText("تاریخ")
            btn_calendar = QPushButton("📅")
            layout.addWidget(self.date_input)
            layout.addWidget(btn_calendar)
        
        def set_date_to_today(self):
            self.date_input.setText("1403/01/01")
        
        def get_gregorian_date(self):
            return "2024-03-20"
        
        def set_date_from_gregorian(self, date_str):
            self.date_input.setText(date_str.replace("-", "/"))
        
        def is_valid(self):
            return bool(self.date_input.text().strip())
    
    class SearchableCombo(QComboBox):
        def __init__(self, data_manager=None, table_name="", display_field="", 
                    filter_field="", filter_value="", parent=None):
            super().__init__(parent)
            self.addItems(["آیتم ۱", "آیتم ۲", "آیتم ۳"])
        
        def refresh(self):
            self.clear()
            self.addItems(["آیتم ۱", "آیتم ۲", "آیتم ۳"])
        
        def set_current_text(self, text):
            index = self.findText(text)
            if index >= 0:
                self.setCurrentIndex(index)
        
        def current_text(self):
            return self.currentText()


class PartForm(QDialog):
    """فرم مدیریت قطعات - همراه با اطلاعات خرید برای انبار نو"""
    
    part_saved = Signal(dict)  # سیگنال برای ارسال داده ذخیره شده
    
    def __init__(self, data_manager, part_id=None, parent=None, for_warehouse=False, warehouse_id=None):
        super().__init__(parent)
        self.data_manager = data_manager
        self.part_id = part_id
        self.warehouse_id = warehouse_id  # شناسه رکورد در انبار
        self.for_warehouse = for_warehouse  # آیا برای انبار استفاده می‌شود؟
        self.is_editing = part_id is not None  # آیا در حالت ویرایش هستیم؟
        
        print(f"🔍 PartForm __init__: part_id={part_id}, is_editing={self.is_editing}, for_warehouse={for_warehouse}")
        
        # ابتدا تنظیمات اولیه
        self.setup_ui()
        
        # سپس بارگذاری داده‌های اولیه
        self.load_initial_data()
        
        # در نهایت بارگذاری داده‌های قطعه (اگر در حالت ویرایش هستیم)
        if self.is_editing:
            print(f"📥 در حال بارگذاری داده‌های قطعه برای ویرایش...")
            self.load_part_data()
        
        # راست‌چین کامل
        self.setLayoutDirection(Qt.RightToLeft)
        
        # تنظیم اندازه و موقعیت
        if for_warehouse:
            self.resize(800, 700)
        else:
            self.resize(700, 600)
            
        # نمایش موقعیت فرم
        print(f"📐 اندازه فرم: {self.width()}x{self.height()}")
    
    def setup_ui(self):
        """تنظیم رابط کاربری"""
        print(f"🛠️ setup_ui: is_editing={self.is_editing}, for_warehouse={self.for_warehouse}")
        
        if self.for_warehouse:
            if self.is_editing:
                self.setWindowTitle("ویرایش قطعه و موجودی در انبار")
            else:
                self.setWindowTitle("افزودن قطعه جدید به انبار")
        else:
            if self.is_editing:
                self.setWindowTitle("ویرایش قطعه")
            else:
                self.setWindowTitle("افزودن قطعه جدید")
        
        # لایه اصلی با اسکرول
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)
        
        # ایجاد ویجت اسکرول
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        # ویجت محتوا
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(5, 5, 5, 5)
        content_layout.setSpacing(15)
        
        # ==================== بخش ۱: اطلاعات پایه قطعه ====================
        basic_group = QGroupBox("📦 اطلاعات پایه قطعه")
        basic_group.setLayoutDirection(Qt.RightToLeft)
        basic_layout = QFormLayout(basic_group)
        basic_layout.setLabelAlignment(Qt.AlignRight)
        basic_layout.setSpacing(8)
        
        # ردیف ۱: کد و نام قطعه
        row1_layout = QHBoxLayout()
        row1_layout.setSpacing(10)
        
        # کد قطعه
        code_layout = QVBoxLayout()
        lbl_code = QLabel("کد قطعه*:")
        self.txt_part_code = QLineEdit()
        self.txt_part_code.setPlaceholderText("مثلاً: PCB-001")
        self.txt_part_code.setMinimumHeight(35)
        code_layout.addWidget(lbl_code)
        code_layout.addWidget(self.txt_part_code)
        row1_layout.addLayout(code_layout)
        
        # نام قطعه
        name_layout = QVBoxLayout()
        lbl_name = QLabel("نام قطعه*:")
        self.txt_part_name = QLineEdit()
        self.txt_part_name.setPlaceholderText("مثلاً: برد اصلی یخچال")
        self.txt_part_name.setMinimumHeight(35)
        name_layout.addWidget(lbl_name)
        name_layout.addWidget(self.txt_part_name)
        row1_layout.addLayout(name_layout)
        
        basic_layout.addRow(row1_layout)
        
        # ردیف ۲: دسته‌بندی و برند
        row2_layout = QHBoxLayout()
        row2_layout.setSpacing(10)
        
        # دسته‌بندی
        category_layout = QVBoxLayout()
        lbl_category = QLabel("دسته‌بندی*:")
        self.cmb_category = SearchableCombo(
            data_manager=self.data_manager,
            table_name="LookupValues",
            display_field="value",
            filter_field="category",
            filter_value="part_category",
            parent=self
        )
        category_layout.addWidget(lbl_category)
        category_layout.addWidget(self.cmb_category)
        row2_layout.addLayout(category_layout)
        
        # برند
        brand_layout = QVBoxLayout()
        lbl_brand = QLabel("برند:")
        self.cmb_brand = SearchableCombo(
            data_manager=self.data_manager,
            table_name="LookupValues",
            display_field="value",
            filter_field="category",
            filter_value="brand",
            parent=self
        )
        brand_layout.addWidget(lbl_brand)
        brand_layout.addWidget(self.cmb_brand)
        row2_layout.addLayout(brand_layout)
        
        basic_layout.addRow(row2_layout)
        
        # ردیف ۳: مدل و واحد
        row3_layout = QHBoxLayout()
        row3_layout.setSpacing(10)
        
        # مدل
        model_layout = QVBoxLayout()
        lbl_model = QLabel("مدل:")
        self.txt_model = QLineEdit()
        self.txt_model.setPlaceholderText("مثلاً: X-2000")
        self.txt_model.setMinimumHeight(35)
        model_layout.addWidget(lbl_model)
        model_layout.addWidget(self.txt_model)
        row3_layout.addLayout(model_layout)
        
        # واحد
        unit_layout = QVBoxLayout()
        lbl_unit = QLabel("واحد:")
        self.cmb_unit = QComboBox()
        self.cmb_unit.addItems(["عدد", "متر", "کیلوگرم", "لیتر", "ست", "رول"])
        self.cmb_unit.setMinimumHeight(35)
        unit_layout.addWidget(lbl_unit)
        unit_layout.addWidget(self.cmb_unit)
        row3_layout.addLayout(unit_layout)
        
        basic_layout.addRow(row3_layout)
        
        # ردیف ۴: محدودیت موجودی
        row4_layout = QHBoxLayout()
        row4_layout.setSpacing(10)
        
        # حداقل موجودی
        min_layout = QVBoxLayout()
        lbl_min = QLabel("حداقل موجودی:")
        self.spn_min_stock = QSpinBox()
        self.spn_min_stock.setRange(0, 10000)
        self.spn_min_stock.setValue(5)
        self.spn_min_stock.setMinimumHeight(35)
        self.spn_min_stock.setSuffix(" عدد")
        min_layout.addWidget(lbl_min)
        min_layout.addWidget(self.spn_min_stock)
        row4_layout.addLayout(min_layout)
        
        # حداکثر موجودی
        max_layout = QVBoxLayout()
        lbl_max = QLabel("حداکثر موجودی:")
        self.spn_max_stock = QSpinBox()
        self.spn_max_stock.setRange(1, 100000)
        self.spn_max_stock.setValue(100)
        self.spn_max_stock.setMinimumHeight(35)
        self.spn_max_stock.setSuffix(" عدد")
        max_layout.addWidget(lbl_max)
        max_layout.addWidget(self.spn_max_stock)
        row4_layout.addLayout(max_layout)
        
        basic_layout.addRow(row4_layout)
        
        # توضیحات
        desc_layout = QVBoxLayout()
        lbl_desc = QLabel("توضیحات:")
        self.txt_description = QTextEdit()
        self.txt_description.setMaximumHeight(100)
        self.txt_description.setPlaceholderText("توضیحات اضافی درباره قطعه...")
        desc_layout.addWidget(lbl_desc)
        desc_layout.addWidget(self.txt_description)
        
        basic_layout.addRow(desc_layout)
        
        content_layout.addWidget(basic_group)
        
        # ==================== بخش ۲: اطلاعات خرید (فقط برای انبار) ====================
        if self.for_warehouse:
            purchase_group = QGroupBox("📥 اطلاعات خرید و موجودی")
            purchase_group.setLayoutDirection(Qt.RightToLeft)
            purchase_layout = QFormLayout(purchase_group)
            purchase_layout.setLabelAlignment(Qt.AlignRight)
            purchase_layout.setSpacing(8)
            
            # تامین‌کننده
            lbl_supplier = QLabel("تامین‌کننده*:")
            self.cmb_supplier = QComboBox()
            self.cmb_supplier.setMinimumHeight(35)
            purchase_layout.addRow(lbl_supplier, self.cmb_supplier)
            
            # ردیف ۵: تعداد و قیمت‌ها
            row5_layout = QHBoxLayout()
            row5_layout.setSpacing(10)
            
            # تعداد
            qty_layout = QVBoxLayout()
            lbl_qty = QLabel("تعداد*:")
            self.spn_quantity = QSpinBox()
            self.spn_quantity.setRange(1, 100000)
            self.spn_quantity.setValue(1)
            self.spn_quantity.setMinimumHeight(35)
            self.spn_quantity.setSuffix(" عدد")
            qty_layout.addWidget(lbl_qty)
            qty_layout.addWidget(self.spn_quantity)
            row5_layout.addLayout(qty_layout)
            
            # قیمت خرید
            purchase_price_layout = QVBoxLayout()
            lbl_purchase_price = QLabel("قیمت خرید*:")
            self.spn_purchase_price = QDoubleSpinBox()
            self.spn_purchase_price.setRange(0, 1000000000)
            self.spn_purchase_price.setValue(0)
            self.spn_purchase_price.setMinimumHeight(35)
            self.spn_purchase_price.setDecimals(0)
            self.spn_purchase_price.setSuffix(" ریال")
            purchase_price_layout.addWidget(lbl_purchase_price)
            purchase_price_layout.addWidget(self.spn_purchase_price)
            row5_layout.addLayout(purchase_price_layout)
            
            # قیمت فروش
            sale_price_layout = QVBoxLayout()
            lbl_sale_price = QLabel("قیمت فروش*:")
            self.spn_sale_price = QDoubleSpinBox()
            self.spn_sale_price.setRange(0, 1000000000)
            self.spn_sale_price.setValue(0)
            self.spn_sale_price.setMinimumHeight(35)
            self.spn_sale_price.setDecimals(0)
            self.spn_sale_price.setSuffix(" ریال")
            sale_price_layout.addWidget(lbl_sale_price)
            sale_price_layout.addWidget(self.spn_sale_price)
            row5_layout.addLayout(sale_price_layout)
            
            purchase_layout.addRow(row5_layout)
            
            # ردیف ۶: تاریخ‌ها
            row6_layout = QHBoxLayout()
            row6_layout.setSpacing(10)
            
            # تاریخ خرید
            purchase_date_layout = QVBoxLayout()
            lbl_purchase_date = QLabel("تاریخ خرید*:")
            self.date_purchase = JalaliDateInput()
            self.date_purchase.set_date_to_today()
            purchase_date_layout.addWidget(lbl_purchase_date)
            purchase_date_layout.addWidget(self.date_purchase)
            row6_layout.addLayout(purchase_date_layout)
            
            # تاریخ انقضا
            expiration_layout = QVBoxLayout()
            lbl_expiration = QLabel("تاریخ انقضا:")
            self.date_expiration = JalaliDateInput()
            expiration_layout.addWidget(lbl_expiration)
            expiration_layout.addWidget(self.date_expiration)
            row6_layout.addLayout(expiration_layout)
            
            purchase_layout.addRow(row6_layout)
            
            # ردیف ۷: شماره بچ و محل
            row7_layout = QHBoxLayout()
            row7_layout.setSpacing(10)
            
            # شماره بچ
            batch_layout = QVBoxLayout()
            lbl_batch = QLabel("شماره بچ:")
            self.txt_batch_number = QLineEdit()
            self.txt_batch_number.setPlaceholderText("مثلاً: BATCH-2024-001")
            self.txt_batch_number.setMinimumHeight(35)
            batch_layout.addWidget(lbl_batch)
            batch_layout.addWidget(self.txt_batch_number)
            row7_layout.addLayout(batch_layout)
            
            # محل انبار
            location_layout = QVBoxLayout()
            lbl_location = QLabel("محل انبار:")
            self.txt_location = QLineEdit()
            self.txt_location.setPlaceholderText("مثلاً: قفسه A-1")
            self.txt_location.setMinimumHeight(35)
            location_layout.addWidget(lbl_location)
            location_layout.addWidget(self.txt_location)
            row7_layout.addLayout(location_layout)
            
            purchase_layout.addRow(row7_layout)
            
            content_layout.addWidget(purchase_group)
        
        # خط جداکننده
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        content_layout.addWidget(separator)
        
        # دکمه‌ها
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        if self.for_warehouse:
            if self.is_editing:
                btn_text = "💾 ذخیره تغییرات"
            else:
                btn_text = "💾 ذخیره قطعه و موجودی"
        else:
            if self.is_editing:
                btn_text = "💾 ذخیره تغییرات"
            else:
                btn_text = "💾 ذخیره قطعه"
        
        self.btn_save = QPushButton(btn_text)
        self.btn_save.setMinimumHeight(40)
        self.btn_save.setMinimumWidth(150)
        self.btn_save.clicked.connect(self.save_part)
        btn_layout.addWidget(self.btn_save)
        
        self.btn_cancel = QPushButton("❌ انصراف")
        self.btn_cancel.setMinimumHeight(40)
        self.btn_cancel.setMinimumWidth(120)
        self.btn_cancel.clicked.connect(self.reject)
        btn_layout.addWidget(self.btn_cancel)
        
        content_layout.addLayout(btn_layout)
        
        # تنظیم ویجت اسکرول
        scroll_area.setWidget(content_widget)
        main_layout.addWidget(scroll_area)
        
        # استایل ساده‌تر برای تست
        self.setup_style()
        
        print(f"✅ setup_ui کامل شد")

    def setup_style(self):
        """تنظیم استایل فرم - نسخه ساده‌تر"""
        self.setStyleSheet("""
            /* استایل اصلی */
            PartForm {
                background-color: #ffffff;
                border: 2px solid #4a9eff;
                border-radius: 10px;
            }
            
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            
            /* لیبل‌ها */
            QLabel {
                color: #000000;
                background-color: transparent;
                padding: 3px;
                font-size: 11pt;
                font-family: 'B Nazanin';
                text-align: right;
            }
            
            /* فیلدهای ورودی */
            QLineEdit {
                background-color: #f5f5f5;
                color: #000000;
                border: 1px solid #cccccc;
                border-radius: 4px;
                padding: 8px;
                font-size: 11pt;
                font-family: 'B Nazanin';
                selection-background-color: #4a9eff;
                selection-color: #ffffff;
                text-align: right;
            }
            
            QLineEdit:focus {
                border: 1px solid #4a9eff;
                background-color: #ffffff;
            }
            
            QLineEdit::placeholder {
                color: #888888;
                font-style: italic;
            }
            
            /* کامبوباکس */
            QComboBox {
                background-color: #f5f5f5;
                color: #000000;
                border: 1px solid #cccccc;
                border-radius: 4px;
                padding: 8px;
                font-size: 11pt;
                font-family: 'B Nazanin';
                selection-background-color: #4a9eff;
                selection-color: #ffffff;
                text-align: right;
                min-height: 35px;
            }
            
            QComboBox QAbstractItemView {
                background-color: #ffffff;
                color: #000000;
                border: 1px solid #cccccc;
                selection-background-color: #4a9eff;
                selection-color: #ffffff;
                text-align: right;
            }
            
            /* اسپین‌باکس */
            QSpinBox, QDoubleSpinBox {
                background-color: #f5f5f5;
                color: #000000;
                border: 1px solid #cccccc;
                border-radius: 4px;
                padding: 8px;
                font-size: 11pt;
                font-family: 'B Nazanin';
                text-align: right;
                min-height: 35px;
            }
            
            /* تکست ادیتر */
            QTextEdit {
                background-color: #f5f5f5;
                color: #000000;
                border: 1px solid #cccccc;
                border-radius: 4px;
                font-size: 11pt;
                font-family: 'B Nazanin';
                text-align: right;
            }
            
            /* دکمه‌ها */
            QPushButton {
                background-color: #4a9eff;
                color: #ffffff;
                border: 1px solid #3a8eef;
                border-radius: 6px;
                padding: 12px 24px;
                font-size: 12pt;
                font-family: 'B Nazanin';
                font-weight: bold;
                min-width: 120px;
                min-height: 45px;
            }
            
            QPushButton:hover {
                background-color: #5aaeff;
                border-color: #4a9eff;
            }
            
            QPushButton:pressed {
                background-color: #3a8eef;
            }
            
            /* دکمه انصراف */
            #btn_cancel {
                background-color: #ff6b6b;
                border-color: #ef5b5b;
            }
            
            #btn_cancel:hover {
                background-color: #ff7b7b;
            }
            
            #btn_cancel:pressed {
                background-color: #ef5b5b;
            }
            
            /* گروه */
            QGroupBox {
                border: 2px solid #4a9eff;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 15px;
                font-size: 12pt;
                font-weight: bold;
                color: #4a9eff;
                background-color: #f0f8ff;
            }
            
            QGroupBox::title {
                subcontrol-origin: margin;
                right: 10px;
                padding: 0 10px 0 10px;
                background-color: #f0f8ff;
                color: #4a9eff;
            }
        """)
        
        # ID برای دکمه‌ها
        self.btn_save.setObjectName("btn_save")
        self.btn_cancel.setObjectName("btn_cancel")
    
    def load_initial_data(self):
        """بارگذاری داده‌های اولیه"""
        print("📥 بارگذاری داده‌های اولیه...")
        
        # تنظیم واحد پیش‌فرض
        self.cmb_unit.setCurrentText("عدد")
        print("✅ واحد پیش‌فرض تنظیم شد")
        
        # بارگذاری دسته‌بندی‌ها و برندها
        try:
            self.cmb_category.refresh()
            print("✅ دسته‌بندی‌ها بارگذاری شد")
        except Exception as e:
            print(f"⚠️ خطا در بارگذاری دسته‌بندی‌ها: {e}")
        
        try:
            self.cmb_brand.refresh()
            print("✅ برندها بارگذاری شد")
        except Exception as e:
            print(f"⚠️ خطا در بارگذاری برندها: {e}")
        
        # اگر برای انبار هست، تامین‌کنندگان رو هم بارگذاری کن
        if self.for_warehouse:
            self.load_suppliers()
    
    def load_suppliers(self):
        """بارگذاری لیست تامین‌کنندگان"""
        print("📋 بارگذاری تامین‌کنندگان...")
        
        try:
            query = """
            SELECT 
                id,
                first_name,
                last_name,
                mobile,
                phone
            FROM Persons 
            WHERE person_type = 'تامین کننده'
            ORDER BY first_name, last_name
            """
            
            suppliers = self.data_manager.db.fetch_all(query)
            
            self.cmb_supplier.clear()
            self.cmb_supplier.addItem("-- انتخاب تامین‌کننده --", None)
            
            if suppliers:
                for supplier in suppliers:
                    supplier_id = supplier.get('id')
                    first_name = supplier.get('first_name', '')
                    last_name = supplier.get('last_name', '')
                    mobile = supplier.get('mobile', '')
                    
                    # ایجاد نام نمایشی
                    if first_name and last_name:
                        display_name = f"{first_name} {last_name}"
                    elif first_name:
                        display_name = first_name
                    elif last_name:
                        display_name = last_name
                    elif mobile:
                        display_name = f"تامین‌کننده ({mobile})"
                    else:
                        display_name = f"تامین‌کننده #{supplier_id}"
                    
                    self.cmb_supplier.addItem(display_name, supplier_id)
                
                print(f"✅ {len(suppliers)} تامین‌کننده بارگذاری شد")
            else:
                self.cmb_supplier.addItem("⚠️ ابتدا تامین‌کننده اضافه کنید", 0)
                print("⚠️ هیچ تامین‌کننده‌ای یافت نشد")
            
        except Exception as e:
            print(f"❌ خطا در بارگذاری تامین‌کنندگان: {e}")
            self.cmb_supplier.clear()
            self.cmb_supplier.addItem("⚠️ خطا در بارگذاری", 0)

    def load_part_data(self):
        """بارگذاری داده‌های قطعه برای ویرایش"""
        if not self.part_id:
            return
        
        print(f"📝 در حال بارگذاری قطعه ID: {self.part_id}")
        
        try:
            # دریافت اطلاعات پایه قطعه
            query = """
            SELECT * FROM Parts 
            WHERE id = ?
            """
            part = self.data_manager.db.fetch_one(query, (self.part_id,))
            
            if part:
                print(f"✅ قطعه یافت شد: {part.get('part_code')}")
                
                # پر کردن اطلاعات پایه
                self.txt_part_code.setText(part.get('part_code', ''))
                self.txt_part_name.setText(part.get('part_name', ''))
                
                # دسته‌بندی
                category = part.get('category', '')
                if category:
                    self.cmb_category.set_current_text(category)
                
                # برند
                brand = part.get('brand', '')
                if brand:
                    self.cmb_brand.set_current_text(brand)
                
                self.txt_model.setText(part.get('model', ''))
                
                # واحد
                unit = part.get('unit', 'عدد')
                index = self.cmb_unit.findText(unit)
                if index >= 0:
                    self.cmb_unit.setCurrentIndex(index)
                
                # موجودی
                self.spn_min_stock.setValue(part.get('min_stock', 5))
                self.spn_max_stock.setValue(part.get('max_stock', 100))
                
                # توضیحات
                self.txt_description.setText(part.get('description', ''))
                
                # اگر برای انبار هست، اطلاعات خرید رو هم بارگذاری کن
                if self.for_warehouse:
                    self.load_warehouse_data()
                
                print("✅ داده‌های قطعه بارگذاری شدند")
            else:
                print("❌ قطعه یافت نشد")
            
        except Exception as e:
            print(f"❌ خطا در بارگذاری قطعه: {e}")
            import traceback
            traceback.print_exc()
            QMessageBox.critical(self, "خطا", f"خطا در بارگذاری اطلاعات قطعه: {str(e)}")

    def load_warehouse_data(self):
        """بارگذاری اطلاعات انبار برای ویرایش"""
        print(f"📦 بارگذاری اطلاعات انبار برای قطعه ID: {self.part_id}")
        
        try:
            # دریافت اطلاعات انبار
            if self.warehouse_id:
                # اگر warehouse_id مستقیم داده شده
                query = """
                SELECT * FROM NewPartsWarehouse 
                WHERE id = ?
                """
                params = (self.warehouse_id,)
            else:
                # اگر از روی part_id جستجو کنیم
                query = """
                SELECT * FROM NewPartsWarehouse 
                WHERE part_id = ? AND status = 'موجود'
                ORDER BY purchase_date DESC
                LIMIT 1
                """
                params = (self.part_id,)
            
            warehouse_data = self.data_manager.db.fetch_one(query, params)
            
            if warehouse_data:
                print(f"✅ اطلاعات انبار یافت شد")
                
                # پر کردن اطلاعات خرید
                self.spn_quantity.setValue(warehouse_data.get('quantity', 1))
                self.spn_purchase_price.setValue(warehouse_data.get('purchase_price', 0))
                self.spn_sale_price.setValue(warehouse_data.get('sale_price', 0))
                
                # تامین‌کننده
                supplier_id = warehouse_data.get('supplier_id')
                if supplier_id:
                    # پیدا کردن تامین‌کننده در لیست
                    for i in range(self.cmb_supplier.count()):
                        item_data = self.cmb_supplier.itemData(i)
                        if item_data == supplier_id:
                            self.cmb_supplier.setCurrentIndex(i)
                            break
                
                # تاریخ خرید
                purchase_date = warehouse_data.get('purchase_date')
                if purchase_date:
                    self.date_purchase.set_date_from_gregorian(purchase_date)
                
                # تاریخ انقضا
                expiration_date = warehouse_data.get('expiration_date')
                if expiration_date:
                    self.date_expiration.set_date_from_gregorian(expiration_date)
                
                # شماره بچ
                self.txt_batch_number.setText(warehouse_data.get('batch_number', ''))
                
                # محل انبار
                self.txt_location.setText(warehouse_data.get('location', ''))
                
                # ذخیره warehouse_id برای ویرایش
                if 'id' in warehouse_data:
                    self.warehouse_id = warehouse_data['id']
                
                print("✅ اطلاعات انبار بارگذاری شد")
            else:
                print("⚠️ اطلاعات انبار یافت نشد")
                
        except Exception as e:
            print(f"❌ خطا در بارگذاری اطلاعات انبار: {e}")
            import traceback
            traceback.print_exc()

    def validate_form(self):
        """اعتبارسنجی فرم"""
        errors = []
        
        # کد قطعه
        part_code = self.txt_part_code.text().strip()
        if not part_code:
            errors.append("• کد قطعه الزامی است")
        elif len(part_code) < 2:
            errors.append("• کد قطعه باید حداقل 2 کاراکتر باشد")
        
        # نام قطعه
        part_name = self.txt_part_name.text().strip()
        if not part_name:
            errors.append("• نام قطعه الزامی است")
        elif len(part_name) < 3:
            errors.append("• نام قطعه باید حداقل 3 کاراکتر باشد")
        
        # دسته‌بندی
        category = self.cmb_category.current_text().strip()
        if not category:
            errors.append("• دسته‌بندی الزامی است")
        
        # بررسی حداقل و حداکثر موجودی
        min_stock = self.spn_min_stock.value()
        max_stock = self.spn_max_stock.value()
        if min_stock >= max_stock:
            errors.append("• حداقل موجودی باید کمتر از حداکثر موجودی باشد")
        
        # اگر برای انبار هست، فیلدهای خرید رو هم چک کن
        if self.for_warehouse:
            # تامین‌کننده
            supplier_data = self.cmb_supplier.currentData()
            if supplier_data == 0 or (supplier_data is None and self.cmb_supplier.currentIndex() == 0):
                errors.append("• انتخاب تامین‌کننده الزامی است")
            
            # تعداد
            if self.spn_quantity.value() <= 0:
                errors.append("• تعداد باید بیشتر از صفر باشد")
            
            # قیمت خرید
            if self.spn_purchase_price.value() <= 0:
                errors.append("• قیمت خرید باید بیشتر از صفر باشد")
            
            # قیمت فروش
            if self.spn_sale_price.value() <= 0:
                errors.append("• قیمت فروش باید بیشتر از صفر باشد")
            
            # بررسی تاریخ خرید
            if not self.date_purchase.is_valid():
                errors.append("• تاریخ خرید نامعتبر است")
        
        return errors
    
    def save_part(self):
        """ذخیره قطعه (و موجودی اگر برای انبار باشد)"""
        print("💾 در حال ذخیره قطعه...")
        
        errors = self.validate_form()
        if errors:
            QMessageBox.warning(self, "خطاهای اعتبارسنجی", "\n".join(errors))
            return
        
        try:
            # جمع‌آوری داده‌های پایه
            part_data = {
                'part_code': self.txt_part_code.text().strip(),
                'part_name': self.txt_part_name.text().strip(),
                'category': self.cmb_category.current_text().strip(),
                'brand': self.cmb_brand.current_text().strip(),
                'model': self.txt_model.text().strip(),
                'unit': self.cmb_unit.currentText(),
                'min_stock': self.spn_min_stock.value(),
                'max_stock': self.spn_max_stock.value(),
                'description': self.txt_description.toPlainText().strip()
            }
            
            print(f"📝 ذخیره قطعه: {part_data}")
            print(f"   حالت: {'ویرایش' if self.is_editing else 'افزودن'}")
            print(f"   part_id: {self.part_id}")
            
            if self.is_editing:
                # ویرایش قطعه موجود
                success = self.update_part(part_data)
                message = "✅ قطعه با موفقیت ویرایش شد"
            else:
                # افزودن قطعه جدید
                success = self.add_part(part_data)
                message = "✅ قطعه جدید با موفقیت اضافه شد"
            
            if success:
                # اگر ویرایش بود، ID قبلی رو نگه دار
                if self.is_editing:
                    part_data['id'] = self.part_id
                else:
                    # دریافت آخرین ID قطعه اضافه شده
                    last_id = self.get_last_part_id()
                    if last_id:
                        part_data['id'] = last_id
                        self.part_id = last_id  # به روز رسانی part_id برای استفاده بعدی
                
                # اگر برای انبار هست، اطلاعات خرید رو هم ذخیره کن
                if self.for_warehouse:
                    if self.is_editing and self.warehouse_id:
                        # ویرایش اطلاعات انبار موجود
                        stock_success = self.update_warehouse_stock(part_data)
                        message += "\n✅ اطلاعات خرید و موجودی با موفقیت به‌روزرسانی شد"
                    else:
                        # افزودن اطلاعات انبار جدید
                        stock_success = self.add_warehouse_stock(part_data)
                        message += "\n✅ اطلاعات خرید و موجودی با موفقیت ذخیره شد"
                    
                    if not stock_success:
                        message += "\n⚠️ قطعه ذخیره شد اما خطا در ذخیره اطلاعات خرید"
                
                # ارسال سیگنال
                print(f"📤 ارسال سیگنال part_saved با داده: {part_data}")
                self.part_saved.emit(part_data)
                
                # پیام موفقیت
                QMessageBox.information(self, "موفقیت", message)
                
                # قبول کردن فرم
                self.accept()
            else:
                QMessageBox.critical(self, "خطا", "❌ خطا در ذخیره‌سازی قطعه")
        
        except Exception as e:
            print(f"❌ خطا در ذخیره قطعه: {e}")
            import traceback
            traceback.print_exc()
            QMessageBox.critical(self, "خطا", f"❌ خطا در ذخیره‌سازی: {str(e)}")

    def add_warehouse_stock(self, part_data):
        """افزودن اطلاعات انبار جدید"""
        try:
            stock_data = {
                'part_id': part_data.get('id'),
                'quantity': self.spn_quantity.value(),
                'purchase_price': self.spn_purchase_price.value(),
                'sale_price': self.spn_sale_price.value(),
                'supplier_id': self.cmb_supplier.currentData(),
                'purchase_date': self.date_purchase.get_gregorian_date(),
                'batch_number': self.txt_batch_number.text().strip(),
                'location': self.txt_location.text().strip(),
                'expiration_date': self.date_expiration.get_gregorian_date() if self.date_expiration.is_valid() else None,
                'status': 'موجود'
            }
            
            print(f"📦 ذخیره اطلاعات انبار: {stock_data}")
            
            # ذخیره در انبار
            success = self.data_manager.warehouse.add_to_warehouse('قطعات نو', stock_data)
            
            if success:
                part_data['stock_added'] = True
                part_data['stock_data'] = stock_data
            
            return success
            
        except Exception as e:
            print(f"❌ خطا در ذخیره اطلاعات انبار: {e}")
            return False

    def update_warehouse_stock(self, part_data):
        """ویرایش اطلاعات انبار موجود"""
        try:
            # ساختار داده‌های انبار برای ویرایش
            warehouse_data = {
                'quantity': self.spn_quantity.value(),
                'purchase_price': self.spn_purchase_price.value(),
                'sale_price': self.spn_sale_price.value(),
                'supplier_id': self.cmb_supplier.currentData(),
                'purchase_date': self.date_purchase.get_gregorian_date(),
                'batch_number': self.txt_batch_number.text().strip(),
                'location': self.txt_location.text().strip(),
                'expiration_date': self.date_expiration.get_gregorian_date() if self.date_expiration.is_valid() else None
            }
            
            print(f"✏️ به‌روزرسانی اطلاعات انبار ID: {self.warehouse_id}")
            print(f"   داده‌ها: {warehouse_data}")
            
            # حذف فیلدهای None
            warehouse_data = {k: v for k, v in warehouse_data.items() if v is not None}
            
            # بروزرسانی در دیتابیس
            query = """
            UPDATE NewPartsWarehouse 
            SET quantity = :quantity,
                purchase_price = :purchase_price,
                sale_price = :sale_price,
                supplier_id = :supplier_id,
                purchase_date = :purchase_date,
                batch_number = :batch_number,
                location = :location,
                expiration_date = :expiration_date,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = :id
            """
            
            warehouse_data['id'] = self.warehouse_id
            success = self.data_manager.db.execute_query(query, warehouse_data)
            
            if success:
                part_data['stock_updated'] = True
                part_data['stock_data'] = warehouse_data
            
            return success
            
        except Exception as e:
            print(f"❌ خطا در به‌روزرسانی اطلاعات انبار: {e}")
            import traceback
            traceback.print_exc()
            return False

    def add_part(self, part_data):
        """افزودن قطعه جدید به دیتابیس"""
        try:
            print(f"➕ افزودن قطعه جدید: {part_data}")
            return self.data_manager.part.add_part(part_data)
        except Exception as e:
            print(f"❌ خطا در افزودن قطعه: {e}")
            return False
    
    def update_part(self, part_data):
        """بروزرسانی قطعه در دیتابیس"""
        try:
            query = """
            UPDATE Parts SET
                part_code = ?,
                part_name = ?,
                category = ?,
                brand = ?,
                model = ?,
                unit = ?,
                min_stock = ?,
                max_stock = ?,
                description = ?
            WHERE id = ?
            """
            
            params = (
                part_data['part_code'],
                part_data['part_name'],
                part_data['category'],
                part_data['brand'],
                part_data['model'],
                part_data['unit'],
                part_data['min_stock'],
                part_data['max_stock'],
                part_data['description'],
                self.part_id
            )
            
            print(f"✏️ بروزرسانی قطعه {self.part_id}")
            return self.data_manager.db.execute_query(query, params)
        
        except Exception as e:
            print(f"❌ خطا در بروزرسانی قطعه: {e}")
            return False
    
    def get_last_part_id(self):
        """دریافت آخرین ID قطعه اضافه شده"""
        try:
            query = "SELECT last_insert_rowid() as id"
            result = self.data_manager.db.fetch_one(query)
            last_id = result['id'] if result else None
            print(f"📌 آخرین ID درج شده: {last_id}")
            return last_id
        except Exception as e:
            print(f"❌ خطا در دریافت آخرین ID: {e}")
            return None


# تست مستقیم فرم
if __name__ == "__main__":
    print("🧪 تست مستقیم PartForm")
    
    # ایجاد یک تست ساده
    from PySide6.QtWidgets import QApplication
    import sys
    
    app = QApplication(sys.argv)
    
    # ایجاد DataManager مصنوعی برای تست
    class MockDataManager:
        class db:
            @staticmethod
            def fetch_all(query, params=()):
                print(f"📊 fetch_all: {query[:50]}...")
                return [{'id': 1, 'part_code': 'TEST001', 'part_name': 'قطعه تست'}]
            
            @staticmethod
            def fetch_one(query, params=()):
                print(f"📊 fetch_one: {query[:50]}...")
                if "Parts" in query:
                    return {'id': 1, 'part_code': 'TEST001', 'part_name': 'قطعه تست', 
                           'category': 'الکترونیکی', 'brand': 'سامسونگ', 'model': 'X-100',
                           'unit': 'عدد', 'min_stock': 5, 'max_stock': 50, 'description': 'قطعه تست'}
                return None
            
            @staticmethod
            def execute_query(query, params=()):
                print(f"📝 اجرای کوئری: {query[:50]}...")
                return True
        
        class part:
            @staticmethod
            def add_part(data):
                print(f"➕ افزودن قطعه: {data}")
                return True
        
        class warehouse:
            @staticmethod
            def add_to_warehouse(warehouse_type, data):
                print(f"📦 افزودن به انبار {warehouse_type}: {data}")
                return True
    
    # ایجاد فرم
    form = PartForm(MockDataManager(), for_warehouse=True)
    form.setWindowTitle("تست PartForm")
    
    # نمایش فرم
    form.show()
    print("✅ فرم نمایش داده شد")
    
    sys.exit(app.exec())