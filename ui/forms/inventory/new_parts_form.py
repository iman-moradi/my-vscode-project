# ui/forms/inventory/new_parts_form_fixed.py
"""
فرم مدیریت انبار قطعات نو - نسخه نهایی اصلاح شده با الگوی used_parts_form.py
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QLineEdit, QComboBox, QTableWidget,
    QTableWidgetItem, QHeaderView, QMessageBox,
    QGroupBox, QFormLayout, QSpinBox, QDoubleSpinBox,
    QTextEdit, QFrame, QSizePolicy, QInputDialog
)
from PySide6.QtCore import Qt, QDate, QTimer
from PySide6.QtGui import QFont, QColor, QIcon
import jdatetime
from datetime import datetime

from .base_inventory_form import BaseInventoryForm
from .widgets.currency_converter import CurrencyConverter
from .widgets.inventory_date_input import InventoryDateInput
from .widgets.enhanced_combo import EnhancedComboBox

class NewPartsForm(BaseInventoryForm):
    """فرم مدیریت انبار قطعات نو با کامبوباکس‌های پیشرفته"""
    
    def __init__(self, parent=None, data_manager=None):
        """سازنده فرم قطعات نو"""
        print("=" * 50)
        print("🚀 NewPartsForm.__init__() شروع شد")
        print("=" * 50)
        
        # ابتدا سازنده والد را فراخوانی کنیم
        super().__init__("انبار قطعات نو", parent)
        
        # شمارنده برای دیباگ
        self.form_counter = 0
        
        # تنظیم data_manager
        if data_manager:
            self.data_manager = data_manager
        elif parent and hasattr(parent, 'data_manager'):
            self.data_manager = parent.data_manager
        else:
            self.data_manager = None
        
        self.current_edit_id = None
        self.all_data = []
        
        print(f"✅ NewPartsForm ایجاد شد. data_manager: {self.data_manager is not None}")
        
        # حالا setup_ui را فراخوانی کنیم
        self.setup_ui()
        
        # بارگذاری داده‌ها
        self.load_data()
        
        print("=" * 50)
        print("🏁 NewPartsForm.__init__() پایان یافت")
        print("=" * 50)
    
    def setup_ui(self):
        """تنظیم رابط کاربری"""
        # هدر فرم
        self.create_header()
        
        # بخش فرم ورود داده
        self.create_form_section()

        # بخش جستجو
        self.create_search_section()
        
        # بخش لیست قطعات
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
        
        title_label = QLabel("📦 انبار قطعات نو")
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
        """ایجاد بخش فرم ورود داده قطعات نو"""
        form_group, form_layout = self.create_form_group("📝 ثبت/ویرایش قطعه نو")
        
        # ردیف 1: کد و نام قطعه
        row1_layout = QHBoxLayout()
        row1_layout.setSpacing(15)
        
        self.part_code = QLineEdit()
        self.part_code.setPlaceholderText("کد یکتا قطعه")
        self.part_code.setMaximumWidth(200)
        
        self.part_name = QLineEdit()
        self.part_name.setPlaceholderText("نام کامل قطعه")
        
        row1_layout.addWidget(QLabel("نام قطعه:"))
        row1_layout.addWidget(self.part_name, 3)
        row1_layout.addWidget(QLabel("کد قطعه:"))
        row1_layout.addWidget(self.part_code, 1)
        
        form_layout.addRow(row1_layout)
        
        # ردیف 2: دسته‌بندی و برند (با کامبوباکس‌های پیشرفته)
        row2_layout = QHBoxLayout()
        row2_layout.setSpacing(15)
        
        self.category = EnhancedComboBox('category')
        
        self.brand = EnhancedComboBox('brand')
        
        row2_layout.addWidget(QLabel("برند:"))
        row2_layout.addWidget(self.brand, 2)
        row2_layout.addWidget(QLabel("دسته‌بندی:"))
        row2_layout.addWidget(self.category, 1)
        
        form_layout.addRow(row2_layout)
        
        # ردیف 3: واحد و مدل
        row3_layout = QHBoxLayout()
        row3_layout.setSpacing(15)
        
        self.unit = QComboBox()
        self.unit.addItems(["عدد", "متر", "کیلو", "لیتر", "ست"])
        self.unit.setMaximumWidth(150)
        
        self.model = QLineEdit()
        self.model.setPlaceholderText("مدل (اختیاری)")
        self.model.setMaximumWidth(250)
        
        row3_layout.addWidget(QLabel("مدل:"))
        row3_layout.addWidget(self.model, 2)
        row3_layout.addWidget(QLabel("واحد:"))
        row3_layout.addWidget(self.unit, 1)
        
        form_layout.addRow(row3_layout)
        
        # ردیف 4: موجودی
        row4_layout = QHBoxLayout()
        row4_layout.setSpacing(15)
        
        self.quantity = QSpinBox()
        self.quantity.setRange(0, 99999)
        self.quantity.setValue(0)
        self.quantity.setMaximumWidth(120)
        
        self.min_stock = QSpinBox()
        self.min_stock.setRange(0, 9999)
        self.min_stock.setValue(5)
        self.min_stock.setMaximumWidth(120)
        
        self.max_stock = QSpinBox()
        self.max_stock.setRange(0, 99999)
        self.max_stock.setValue(100)
        self.max_stock.setMaximumWidth(120)
        
        row4_layout.addWidget(QLabel("حداکثر:"))
        row4_layout.addWidget(self.max_stock)
        row4_layout.addWidget(QLabel("حداقل:"))
        row4_layout.addWidget(self.min_stock)
        row4_layout.addWidget(QLabel("موجودی:"))
        row4_layout.addWidget(self.quantity)
        
        form_layout.addRow(row4_layout)
        
        # ردیف 5: قیمت‌ها
        row5_layout = QHBoxLayout()
        row5_layout.setSpacing(15)
        
        # قیمت خرید
        purchase_label = QLabel("قیمت خرید:")
        self.purchase_price = CurrencyConverter()
        self.purchase_price.set_value(0)
        
        # قیمت فروش
        sale_label = QLabel("قیمت فروش:")
        self.sale_price = CurrencyConverter()
        self.sale_price.set_value(0)
        
        row5_layout.addWidget(sale_label)
        row5_layout.addWidget(self.sale_price, 2)
        row5_layout.addWidget(purchase_label)
        row5_layout.addWidget(self.purchase_price, 2)
        
        form_layout.addRow(row5_layout)
        
        # ردیف 6: تامین‌کننده و تاریخ خرید
        row6_layout = QHBoxLayout()
        row6_layout.setSpacing(15)
        
        self.supplier = EnhancedComboBox('supplier')
        
        self.purchase_date = InventoryDateInput()
        self.purchase_date.set_date_to_today()
        
        row6_layout.addWidget(QLabel("تاریخ خرید:"))
        row6_layout.addWidget(self.purchase_date)
        row6_layout.addWidget(QLabel("تامین‌کننده:"))
        row6_layout.addWidget(self.supplier, 2)
        
        form_layout.addRow(row6_layout)
        
        # ردیف 7: شماره بچ و انقضا
        row7_layout = QHBoxLayout()
        row7_layout.setSpacing(15)
        
        self.batch_number = QLineEdit()
        self.batch_number.setPlaceholderText("شماره بچ/سری (اختیاری)")
        self.batch_number.setMaximumWidth(200)
        
        self.expiration_date = InventoryDateInput()
        
        row7_layout.addWidget(QLabel("تاریخ انقضا:"))
        row7_layout.addWidget(self.expiration_date)
        row7_layout.addWidget(QLabel("شماره بچ:"))
        row7_layout.addWidget(self.batch_number, 2)
        
        form_layout.addRow(row7_layout)
        
        # ردیف 8: محل نگهداری و وضعیت
        row8_layout = QHBoxLayout()
        row8_layout.setSpacing(15)
        
        self.location = QLineEdit()
        self.location.setPlaceholderText("مثلاً: قفسه A-12")
        self.location.setMaximumWidth(200)
        
        self.status = QComboBox()
        self.status.addItems(["موجود", "ناموجود", "در حال سفارش"])
        self.status.setMaximumWidth(150)
        
        row8_layout.addWidget(QLabel("وضعیت:"))
        row8_layout.addWidget(self.status)
        row8_layout.addWidget(QLabel("محل نگهداری:"))
        row6_layout.addWidget(self.location, 2)
        
        form_layout.addRow(row8_layout)
        
        # ردیف 9: توضیحات
        self.description = QTextEdit()
        self.description.setMaximumHeight(100)
        self.description.setPlaceholderText("توضیحات تکمیلی درباره قطعه...")
        
        form_layout.addRow("توضیحات:", self.description)
        
        self.main_layout.addWidget(form_group)
    
    def create_search_section(self):
        """ایجاد بخش جستجو با جستجوی زنده"""
        search_group, search_layout = self.create_form_group("🔍 جستجوی پیشرفته قطعات نو")
        
        # ردیف اول جستجو
        row1_layout = QHBoxLayout()
        row1_layout.setSpacing(15)
        
        # کد قطعه
        self.search_code = QLineEdit()
        self.search_code.setPlaceholderText("کد قطعه...")
        self.search_code.setMaximumWidth(200)
        
        # نام قطعه
        self.search_name = QLineEdit()
        self.search_name.setPlaceholderText("نام قطعه...")
        self.search_name.setMaximumWidth(250)
        
        # دسته‌بندی (با کامبوباکس پیشرفته)
        self.search_category = EnhancedComboBox('category')
        self.search_category.combo.setPlaceholderText("همه دسته‌بندی‌ها")
        self.search_category.combo.setMaximumWidth(200)
        
        row1_layout.addWidget(QLabel("دسته‌بندی:"))
        row1_layout.addWidget(self.search_category)
        row1_layout.addWidget(QLabel("نام قطعه:"))
        row1_layout.addWidget(self.search_name)
        row1_layout.addWidget(QLabel("کد قطعه:"))
        row1_layout.addWidget(self.search_code)
        
        search_layout.addRow(row1_layout)
        
        # ردیف دوم جستجو
        row2_layout = QHBoxLayout()
        row2_layout.setSpacing(15)
        
        # برند (با کامبوباکس پیشرفته)
        self.search_brand = EnhancedComboBox('brand')
        self.search_brand.combo.setPlaceholderText("همه برندها")
        self.search_brand.combo.setMaximumWidth(200)
        
        # تامین‌کننده (با کامبوباکس پیشرفته)
        self.search_supplier = EnhancedComboBox('supplier')
        self.search_supplier.combo.setPlaceholderText("همه تامین‌کنندگان")
        self.search_supplier.combo.setMaximumWidth(250)
        
        # وضعیت
        self.status_filter = QComboBox()
        self.status_filter.addItems(["همه وضعیت‌ها", "موجود", "ناموجود", "در حال سفارش"])
        self.status_filter.setMaximumWidth(150)
        
        row2_layout.addWidget(QLabel("وضعیت:"))
        row2_layout.addWidget(self.status_filter)
        row2_layout.addWidget(QLabel("تامین‌کننده:"))
        row2_layout.addWidget(self.search_supplier)
        row2_layout.addWidget(QLabel("برند:"))
        row2_layout.addWidget(self.search_brand)
        
        search_layout.addRow(row2_layout)
        
        # ردیف سوم: بازه قیمت و موجودی
        row3_layout = QHBoxLayout()
        row3_layout.setSpacing(15)
        
        # بازه قیمت
        self.min_price = QLineEdit()
        self.min_price.setPlaceholderText("حداقل قیمت")
        self.min_price.setMaximumWidth(120)
        
        self.max_price = QLineEdit()
        self.max_price.setPlaceholderText("حداکثر قیمت")
        self.max_price.setMaximumWidth(120)
        
        # بازه موجودی
        self.min_stock_filter = QSpinBox()
        self.min_stock_filter.setRange(0, 9999)
        self.min_stock_filter.setMaximumWidth(100)
        
        self.max_stock_filter = QSpinBox()
        self.max_stock_filter.setRange(0, 99999)
        self.max_stock_filter.setValue(1000)
        self.max_stock_filter.setMaximumWidth(100)
        
        row3_layout.addWidget(QLabel("حداکثر موجودی:"))
        row3_layout.addWidget(self.max_stock_filter)
        row3_layout.addWidget(QLabel("حداقل موجودی:"))
        row3_layout.addWidget(self.min_stock_filter)
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
        search_fields = [
            self.search_code, self.search_name,
            self.min_price, self.max_price
        ]
        
        for field in search_fields:
            self.setup_live_search(field, self.perform_search)
        
        # برای کامبوباکس‌ها
        self.search_category.value_changed.connect(self.perform_search)
        self.search_brand.value_changed.connect(self.perform_search)
        self.search_supplier.value_changed.connect(self.perform_search)
        self.status_filter.currentIndexChanged.connect(self.perform_search)
        
        # برای spin box‌ها
        self.min_stock_filter.valueChanged.connect(self.perform_search)
        self.max_stock_filter.valueChanged.connect(self.perform_search)
    
    def create_table_section(self):
        """ایجاد بخش جدول نمایش قطعات نو"""
        table_group, table_layout = self.create_form_group("📋 لیست قطعات نو")
        
        self.table = self.create_table([
            "ردیف",
            "کد قطعه",
            "نام قطعه",
            "دسته‌بندی",
            "برند",
            "موجودی",
            "قیمت خرید",
            "قیمت فروش",
            "وضعیت",
            "تاریخ خرید",
            "عملیات"
        ])
        
        # تنظیم عرض ستون‌ها
        self.table.setColumnWidth(0, 60)   # ردیف
        self.table.setColumnWidth(1, 120)  # کد قطعه
        self.table.setColumnWidth(2, 180)  # نام قطعه
        self.table.setColumnWidth(3, 120)  # دسته‌بندی
        self.table.setColumnWidth(4, 120)  # برند
        self.table.setColumnWidth(5, 90)   # موجودی
        self.table.setColumnWidth(6, 140)  # قیمت خرید
        self.table.setColumnWidth(7, 140)  # قیمت فروش
        self.table.setColumnWidth(8, 100)  # وضعیت
        self.table.setColumnWidth(9, 110)  # تاریخ خرید
        
        # تنظیم حداقل ارتفاع
        self.table.setMinimumHeight(300)
        
        table_layout.addRow(self.table)
        self.main_layout.addWidget(table_group)
    
    def create_action_buttons(self):
        """ایجاد دکمه‌های عملیات"""
        btn_group = QGroupBox("⚡ عملیات")
        btn_layout = QHBoxLayout()
        
        self.btn_save = QPushButton("💾 ذخیره قطعه")
        self.btn_save.clicked.connect(self.save_data)
        self.btn_save.setProperty("style", "primary")
        
        self.btn_new = QPushButton("🆕 قطعه جدید")
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
        
        self.btn_export = QPushButton("📊 خروجی Excel")
        self.btn_export.clicked.connect(self.export_excel)
        
        self.btn_print = QPushButton("🖨️ چاپ گزارش")
        self.btn_print.clicked.connect(self.print_report)
        
        btn_layout.addWidget(self.btn_save)
        btn_layout.addWidget(self.btn_new)
        btn_layout.addWidget(self.btn_edit)
        btn_layout.addWidget(self.btn_delete)
        btn_layout.addWidget(self.btn_soft_delete)  # اضافه کردن دکمه حذف نرم
        btn_layout.addWidget(self.btn_export)
        btn_layout.addWidget(self.btn_print)
        
        btn_group.setLayout(btn_layout)
        self.main_layout.addWidget(btn_group)
        
        # اتصال انتخاب جدول
        self.table.itemSelectionChanged.connect(self.on_table_selection_changed)
    
    def create_summary_section(self):
        """ایجاد بخش خلاصه در پایین فرم"""
        summary_group = QGroupBox("📊 خلاصه وضعیت انبار قطعات نو")
        summary_layout = QHBoxLayout()
        
        # کارت آمار
        stats = [
            ("موجودی کل", "📦", "27ae60", "0 عدد"),
            ("موجودی کم", "⚠️", "f39c12", "0 عدد"),
            ("ارزش کل", "💰", "3498db", "0 تومان"),
            ("میانگین قیمت", "📈", "9b59b6", "0 تومان"),
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
        
        # ذخیره reference برای به‌روزرسانی
        setattr(card, 'value_label', value_label)
        setattr(card, 'title', title)
        
        card.setLayout(layout)
        return card
    
    def perform_search(self):
        """اجرای جستجوی زنده برای قطعات نو"""
        try:
            # جمع‌آوری پارامترهای جستجو
            filters = {
                'code': self.search_code.text().strip(),
                'name': self.search_name.text().strip(),
                'category_id': self.search_category.get_value(),
                'brand_id': self.search_brand.get_value(),
                'supplier_id': self.search_supplier.get_value(),
                'status': self.status_filter.currentText(),
                'min_price': self.min_price.text().strip(),
                'max_price': self.max_price.text().strip(),
                'min_stock': self.min_stock_filter.value(),
                'max_stock': self.max_stock_filter.value()
            }
            
            # فیلتر کردن داده‌ها
            filtered_data = []
            
            for item in self.all_data:
                match = True
                
                # فیلتر کد
                if match and filters['code']:
                    code_lower = item.get('part_code', '').lower()
                    if filters['code'].lower() not in code_lower:
                        match = False
                
                # فیلتر نام
                if match and filters['name']:
                    name_lower = item.get('part_name', '').lower()
                    if filters['name'].lower() not in name_lower:
                        match = False
                
                # فیلتر وضعیت
                if match and filters['status'] and filters['status'] != 'همه وضعیت‌ها':
                    if filters['status'] != item.get('status', ''):
                        match = False
                
                # فیلتر قیمت
                if match:
                    try:
                        if filters['min_price']:
                            min_price = float(filters['min_price'])
                            if item.get('purchase_price', 0) < min_price:
                                match = False
                        
                        if match and filters['max_price']:
                            max_price = float(filters['max_price'])
                            if item.get('purchase_price', 0) > max_price:
                                match = False
                    except:
                        pass
                
                # فیلتر موجودی
                if match:
                    quantity = item.get('quantity', 0)
                    if quantity < filters['min_stock']:
                        match = False
                    
                    if match and quantity > filters['max_stock']:
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
        self.search_code.clear()
        self.search_name.clear()
        self.search_category.clear()
        self.search_brand.clear()
        self.search_supplier.clear()
        self.status_filter.setCurrentIndex(0)
        self.min_price.clear()
        self.max_price.clear()
        self.min_stock_filter.setValue(0)
        self.max_stock_filter.setValue(1000)
        
        self.perform_search()
    
    def load_data(self):
        """بارگذاری داده‌های قطعات نو"""
        print("🔄 در حال بارگذاری داده‌های قطعات نو...")
        try:
            # ابتدا سعی کن از دیتابیس بارگذاری کنی
            if self.data_manager and hasattr(self.data_manager, 'warehouse'):
                self.load_from_database()
            else:
                # اگر دیتابیس در دسترس نیست، از داده‌های نمونه استفاده کن
                self.load_sample_data()
                
        except Exception as e:
            print(f"❌ خطا در بارگذاری داده‌ها: {e}")
            # در صورت خطا، داده‌های نمونه بارگذاری شوند
            self.load_sample_data()
    
    def load_sample_data(self):
        """بارگذاری داده‌های نمونه برای قطعات نو"""
        print("📋 بارگذاری داده‌های نمونه قطعات نو...")
        sample_data = [
            {
                'id': 1,
                'part_code': 'PN-001',
                'part_name': 'کمپرسور یخچال ساید نو',
                'category': 'یخچال',
                'brand': 'سامسونگ',
                'quantity': 12,
                'purchase_price': 850000,
                'sale_price': 1200000,
                'status': 'موجود',
                'purchase_date': '1402-10-15',
                'supplier': 'تامین‌کننده A',
                'location': 'قفسه A-12'
            },
            {
                'id': 2,
                'part_code': 'PN-002',
                'part_name': 'مدار الکترونیکی مایکروویو نو',
                'category': 'مایکروویو',
                'brand': 'ال جی',
                'quantity': 8,
                'purchase_price': 320000,
                'sale_price': 450000,
                'status': 'موجود',
                'purchase_date': '1402-11-05',
                'supplier': 'تامین‌کننده B',
                'location': 'قفسه B-8'
            },
            {
                'id': 3,
                'part_code': 'PN-003',
                'part_name': 'موتور جاروبرقی صنعتی نو',
                'category': 'جاروبرقی',
                'brand': 'پاناسونیک',
                'quantity': 2,
                'purchase_price': 280000,
                'sale_price': 380000,
                'status': 'موجودی کم',
                'purchase_date': '1402-09-20',
                'supplier': 'تامین‌کننده C',
                'location': 'قفسه C-3'
            },
        ]
        
        self.all_data = sample_data
        self.populate_table(sample_data)
        self.update_stats(sample_data)
        print(f"✅ {len(sample_data)} آیتم نمونه بارگذاری شد")


    def load_from_database(self):
        """بارگذاری داده‌ها از دیتابیس - نسخه بهینه"""
        print("💾 بارگذاری از دیتابیس...")
        try:
            # دریافت قطعات نو از انبار
            warehouse_items = self.data_manager.warehouse.get_new_parts_stock(show_all=True)
            
            if warehouse_items:
                self.all_data = []
                for item in warehouse_items:
                    # تبدیل تاریخ میلادی به شمسی برای نمایش
                    purchase_date_shamsi = self.miladi_to_shamsi(item.get('purchase_date', ''))
                    expiration_date_shamsi = self.miladi_to_shamsi(item.get('expiration_date', ''))
                    
                    # 🔴 اصلاح شده: برند از فیلدهای مختلف دریافت می‌شود
                    brand = item.get('brand', '')  # ابتدا از جدول Parts
                    if not brand:
                        brand = item.get('brand_name', '')  # سپس از نام برند
                    
                    if brand is None or brand == '':
                        brand = 'نامشخص'
                    
                    self.all_data.append({
                        'id': item['id'],
                        'part_id': item['part_id'],
                        'part_code': item.get('part_code', ''),
                        'part_name': item.get('part_name', ''),
                        'category': item.get('category', ''),
                        'brand': brand,  # 🔴 استفاده از برند اصلاح شده
                        'quantity': item.get('quantity', 0),
                        'purchase_price': item.get('purchase_price', 0),
                        'sale_price': item.get('sale_price', 0),
                        'status': item.get('status', 'موجود'),
                        'purchase_date': purchase_date_shamsi,  # شمسی برای نمایش
                        'purchase_date_miladi': item.get('purchase_date', ''),  # میلادی ذخیره
                        'expiration_date': expiration_date_shamsi,  # شمسی برای نمایش
                        'expiration_date_miladi': item.get('expiration_date', ''),  # میلادی ذخیره
                        'supplier': item.get('supplier_name', ''),
                        'batch_number': item.get('batch_number', ''),
                        'location': item.get('location', '')
                    })
                
                print(f"✅ {len(self.all_data)} آیتم از دیتابیس بارگذاری شد")
                self.populate_table(self.all_data)
                self.update_stats(self.all_data)
            else:
                print("⚠️ دیتابیس قطعات نو خالی است")
                self.all_data = []
                self.populate_table([])
                
        except Exception as e:
            print(f"❌ خطا در بارگذاری از دیتابیس: {e}")
            import traceback
            traceback.print_exc()
            self.show_error(f"خطا در بارگذاری داده‌ها: {str(e)}")
            self.all_data = []
            self.populate_table([])

    def populate_table(self, data):
        """پر کردن جدول با داده‌های قطعات نو"""
        self.table.setRowCount(len(data))
        
        for row, item in enumerate(data):
            # ردیف
            self.table.setItem(row, 0, QTableWidgetItem(str(row + 1)))
            self.table.item(row, 0).setTextAlignment(Qt.AlignCenter)
            
            # کد قطعه
            self.table.setItem(row, 1, QTableWidgetItem(item.get('part_code', '')))
            
            # نام قطعه
            self.table.setItem(row, 2, QTableWidgetItem(item.get('part_name', '')))
            
            # دسته‌بندی
            self.table.setItem(row, 3, QTableWidgetItem(item.get('category', '')))
            
            # برند - اگر خالی بود، "نامشخص" قرار بده
            brand = item.get('brand', 'نامشخص')
            if brand is None or brand == '':
                brand = 'نامشخص'
            
            brand_item = QTableWidgetItem(brand)
            self.table.setItem(row, 4, brand_item)
            
            # موجودی
            quantity = item.get('quantity', 0)
            stock_item = QTableWidgetItem(str(quantity))
            stock_item.setTextAlignment(Qt.AlignCenter)
            
            # رنگ‌آمیزی موجودی کم
            if quantity == 0:
                stock_item.setBackground(QColor('#e74c3c'))
                stock_item.setForeground(QColor('white'))
            elif quantity <= 3:
                stock_item.setBackground(QColor('#f39c12'))
                stock_item.setForeground(QColor('white'))
            
            self.table.setItem(row, 5, stock_item)
            
            # قیمت خرید (تومان)
            purchase_price = item.get('purchase_price', 0)
            price_item = QTableWidgetItem(self.format_currency(purchase_price))
            price_item.setTextAlignment(Qt.AlignLeft)
            self.table.setItem(row, 6, price_item)
            
            # قیمت فروش (تومان)
            sale_price = item.get('sale_price', 0)
            sale_item = QTableWidgetItem(self.format_currency(sale_price))
            sale_item.setTextAlignment(Qt.AlignLeft)
            self.table.setItem(row, 7, sale_item)
            
            # وضعیت
            status = item.get('status', '')
            status_item = QTableWidgetItem(status)
            status_item.setTextAlignment(Qt.AlignCenter)
            
            # رنگ وضعیت
            if status == 'موجود':
                status_item.setBackground(QColor('#27ae60'))
            elif status == 'موجودی کم':
                status_item.setBackground(QColor('#f39c12'))
            elif status == 'ناموجود':
                status_item.setBackground(QColor('#e74c3c'))
            elif status == 'در حال سفارش':
                status_item.setBackground(QColor('#3498db'))
            
            status_item.setForeground(QColor('white'))
            self.table.setItem(row, 8, status_item)
            
            # تاریخ خرید
            date_item = QTableWidgetItem(item.get('purchase_date', ''))
            date_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row, 9, date_item)
            
            # عملیات
            btn_widget = QWidget()
            btn_layout = QHBoxLayout()
            btn_layout.setContentsMargins(2, 2, 2, 2)

            btn_edit = QPushButton("✏️")
            btn_edit.setFixedSize(35, 35)
            btn_edit.setToolTip("ویرایش قطعه")
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

            btn_layout.addWidget(btn_edit)
            btn_layout.addWidget(btn_delete)
            btn_layout.addWidget(btn_soft_delete)
            btn_layout.addStretch()

            btn_widget.setLayout(btn_layout)
            self.table.setCellWidget(row, 10, btn_widget)
    
    def update_stats(self, data):
        """به‌روزرسانی آمار"""
        try:
            total_quantity = sum(item.get('quantity', 0) for item in data)
            low_stock = sum(1 for item in data if item.get('quantity', 0) <= 3 and item.get('quantity', 0) > 0)
            out_of_stock = sum(1 for item in data if item.get('quantity', 0) == 0)
            total_value = sum(item.get('purchase_price', 0) * item.get('quantity', 0) for item in data)
            avg_price = total_value / total_quantity if total_quantity > 0 else 0
            
            # به‌روزرسانی برچسب‌های هدر
            self.total_items_label.setText(f"موجودی کل: {total_quantity:,} عدد")
            self.low_stock_label.setText(f"موجودی کم: {low_stock + out_of_stock:,} عدد")
            self.total_value_label.setText(f"ارزش کل: {self.format_currency(total_value)}")
            
            # به‌روزرسانی کارت‌های خلاصه
            for i in range(self.main_layout.count()):
                item = self.main_layout.itemAt(i)
                if item and hasattr(item.widget(), 'title'):
                    card = item.widget()
                    if card.title == "موجودی کل":
                        card.value_label.setText(f"{total_quantity:,} عدد")
                    elif card.title == "موجودی کم":
                        card.value_label.setText(f"{low_stock + out_of_stock:,} عدد")
                    elif card.title == "ارزش کل":
                        card.value_label.setText(self.format_currency(total_value))
                    elif card.title == "میانگین قیمت":
                        card.value_label.setText(self.format_currency(avg_price))
        except Exception as e:
            print(f"خطا در به‌روزرسانی آمار: {e}")
    

    
    def clear_form(self):
        """پاک کردن فرم"""
        self.current_edit_id = None
        self.part_code.clear()
        self.part_name.clear()
        self.category.clear()
        self.brand.clear()
        self.model.clear()
        self.unit.setCurrentIndex(0)
        self.quantity.setValue(0)
        self.min_stock.setValue(5)
        self.max_stock.setValue(100)
        self.purchase_price.set_value(0)
        self.sale_price.set_value(0)
        self.supplier.clear()
        self.purchase_date.set_date_to_today()
        self.batch_number.clear()
        self.expiration_date.clear()
        self.location.clear()
        self.status.setCurrentIndex(0)
        self.description.clear()
        
        self.btn_save.setText("💾 ذخیره قطعه")
        self.btn_save.setProperty("style", "primary")
        self.table.clearSelection()
    
    def save_data(self):
        """ذخیره داده‌های قطعه نو - نسخه اصلاح شده"""
        try:
            # 🔴 تعریف متغیر message با مقدار پیش‌فرض
            message = "ثبت"
            
            # اعتبارسنجی
            if not self.validate_form():
                return
            
            # 🔴 گرفتن تاریخ شمسی از ویجت
            purchase_date_shamsi = self.purchase_date.get_date_string()
            print(f"📅 تاریخ خرید (شمسی): {purchase_date_shamsi}")
            
            # 🔴 تبدیل تاریخ شمسی به میلادی برای ذخیره در دیتابیس
            purchase_date_miladi = self.shamsi_to_miladi(purchase_date_shamsi)
            print(f"📅 تاریخ خرید (میلادی): {purchase_date_miladi}")
            
            # 🔴 گرفتن تاریخ انقضا
            expiration_date_shamsi = self.expiration_date.get_date_string()
            expiration_date_miladi = None
            if expiration_date_shamsi:
                expiration_date_miladi = self.shamsi_to_miladi(expiration_date_shamsi)
                print(f"📅 تاریخ انقضا (میلادی): {expiration_date_miladi}")
            
            # 🔴 تولید کد یکتا برای قطعه اگر خالی است
            part_code = self.part_code.text().strip()
            if not part_code:
                import time
                import random
                timestamp = int(time.time() * 1000)
                random_part = random.randint(1000, 9999)
                part_code = f"NP-{timestamp}-{random_part}"
                print(f"📝 کد قطعه خودکار: {part_code}")
                self.part_code.setText(part_code)
            
            # 🔴 اصلاح شده: مدیریت supplier_id - اگر 0 است، None قرار بده
            supplier_id = self.supplier.get_value()
            if supplier_id == 0:
                supplier_id = None
            
            # آماده‌سازی داده‌ها
            data = {
                'part_code': self.part_code.text().strip(),
                'part_name': self.part_name.text().strip(),
                'category_id': self.category.get_value(),
                'category_name': self.category.combo.currentText() if self.category.combo.currentText() else self.category.get_text(),
                'brand_id': self.brand.get_value(),
                'brand_name': self.brand.combo.currentText() if self.brand.combo.currentText() else self.brand.get_text(),
                'model': self.model.text().strip(),
                'unit': self.unit.currentText(),
                'quantity': self.quantity.value(),
                'min_stock': self.min_stock.value(),
                'max_stock': self.max_stock.value(),
                'purchase_price': float(self.purchase_price.get_value_toman()),
                'sale_price': float(self.sale_price.get_value_toman()),
                'supplier_id': supplier_id,  # 🔴 استفاده از supplier_id اصلاح شده
                'purchase_date': purchase_date_miladi,  # میلادی برای دیتابیس
                'batch_number': self.batch_number.text().strip(),
                'expiration_date': expiration_date_miladi,  # میلادی برای دیتابیس
                'location': self.location.text().strip(),
                'status': self.status.currentText(),
                'description': self.description.toPlainText().strip(),
                'employee': 'سیستم'  # برای ثبت تراکنش
            }
            
            print(f"🔄 در حال ذخیره قطعه نو...")
            print(f"   نام: {data['part_name']}")
            print(f"   کد: {data['part_code']}")
            print(f"   تعداد: {data['quantity']}")
            print(f"   قیمت خرید: {data['purchase_price']:,}")
            print(f"   supplier_id: {data['supplier_id']}")
            
            # ذخیره در دیتابیس
            if self.data_manager and hasattr(self.data_manager, 'warehouse'):
                if self.current_edit_id:
                    # 🔴 حالت ویرایش
                    message = "ویرایش"
                    
                    # دریافت اطلاعات قبلی برای مقایسه
                    old_item_query = """
                    SELECT quantity, purchase_price, part_id, supplier_id
                    FROM NewPartsWarehouse 
                    WHERE id = ?
                    """
                    old_item = self.data_manager.db.fetch_one(old_item_query, (self.current_edit_id,))
                    
                    if not old_item:
                        self.show_error("آیتم مورد نظر برای ویرایش یافت نشد!")
                        return
                    
                    # 1. ابتدا بررسی می‌کنیم قطعه در جدول Parts وجود دارد یا خیر
                    part_record = self.data_manager.part.get_part_by_code(data['part_code'])
                    
                    if part_record:
                        part_id = part_record['id']
                        print(f"✅ قطعه با کد {data['part_code']} در دیتابیس موجود است. part_id: {part_id}")
                    else:
                        # قطعه جدید در جدول Parts ایجاد می‌کنیم
                        part_data = {
                            'part_code': data['part_code'],
                            'part_name': data['part_name'],
                            'category': data['category_name'],
                            'brand': data['brand_name'],
                            'model': data['model'],
                            'unit': data['unit'],
                            'min_stock': data['min_stock'],
                            'max_stock': data['max_stock'],
                            'description': data['description']
                        }
                        
                        print(f"➕ ایجاد قطعه جدید در جدول Parts: {part_data}")
                        
                        success = self.data_manager.part.add_part(part_data)
                        if not success:
                            self.show_error("خطا در ایجاد قطعه جدید در جدول Parts")
                            return
                        
                        part_record = self.data_manager.part.get_part_by_code(data['part_code'])
                        if not part_record:
                            self.show_error("خطا در دریافت شناسه قطعه ایجاد شده")
                            return
                        
                        part_id = part_record['id']
                        print(f"✅ قطعه جدید با part_id {part_id} ایجاد شد")
                    
                    # 🔴 آماده‌سازی داده‌ها برای به‌روزرسانی در انبار
                    update_data = {
                        'part_id': part_id,
                        'quantity': data['quantity'],
                        'purchase_price': data['purchase_price'],
                        'sale_price': data['sale_price'],
                        'supplier_id': data['supplier_id'],
                        'purchase_date': data['purchase_date'],  # میلادی
                        'batch_number': data['batch_number'],
                        'expiration_date': data['expiration_date'],
                        'location': data['location'],
                        'status': data['status']
                    }
                    
                    print(f"✏️ در حال ویرایش قطعه ID: {self.current_edit_id}")
                    print(f"   داده‌های به‌روزرسانی: {update_data}")
                    
                    # 🔴 کوئری UPDATE اصلاح شده - بررسی NULL برای supplier_id
                    update_query = """
                    UPDATE NewPartsWarehouse 
                    SET 
                        part_id = ?,
                        quantity = ?,
                        purchase_price = ?,
                        sale_price = ?,
                        supplier_id = ?,
                        purchase_date = ?,
                        batch_number = ?,
                        expiration_date = ?,
                        location = ?,
                        status = ?
                    WHERE id = ?
                    """
                    
                    # 🔴 تبدیل None به NULL برای دیتابیس
                    supplier_param = update_data['supplier_id']
                    expiration_param = update_data['expiration_date']
                    
                    params = (
                        update_data['part_id'],
                        update_data['quantity'],
                        update_data['purchase_price'],
                        update_data['sale_price'],
                        supplier_param,  # می‌تواند None باشد
                        update_data['purchase_date'],
                        update_data['batch_number'],
                        expiration_param,  # می‌تواند None باشد
                        update_data['location'],
                        update_data['status'],
                        self.current_edit_id
                    )
                    
                    success = self.data_manager.db.execute_query(update_query, params)
                    
                    if success:
                        # 🔴 محاسبه تغییرات برای ثبت تراکنش
                        old_quantity = old_item.get('quantity', 0)
                        old_price = old_item.get('purchase_price', 0)
                        
                        quantity_change = data['quantity'] - old_quantity
                        price_change = data['purchase_price'] - old_price
                        
                        # اگر تغییر در تعداد یا قیمت وجود داشت، تراکنش ثبت کن
                        if quantity_change != 0 or price_change != 0:
                            transaction_type = 'ویرایش موجودی' if quantity_change != 0 else 'تغییر قیمت'
                            
                            # 🔴 ثبت تراکنش انبار
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
                                    'قطعات نو',
                                    self.current_edit_id,
                                    quantity_change,
                                    data['purchase_price'],
                                    abs(quantity_change * data['purchase_price']),
                                    transaction_date,
                                    data.get('batch_number', 'بدون شماره سند'),
                                    f"{transaction_type} - {data['part_name']} ({data['part_code']})",
                                    data['employee']
                                )
                            # برای تغییر قیمت
                            else:
                                transaction_params = (
                                    transaction_type,
                                    'قطعات نو',
                                    self.current_edit_id,
                                    0,
                                    data['purchase_price'],
                                    0,
                                    transaction_date,
                                    data.get('batch_number', 'بدون شماره سند'),
                                    f"{transaction_type} - {data['part_name']} ({data['part_code']})",
                                    data['employee']
                                )
                            
                            self.data_manager.db.execute_query(transaction_query, transaction_params)
                            print(f"   ✅ تراکنش {transaction_type} ثبت شد")
                        
                        result = True
                    else:
                        result = False
                else:
                    # 🔴 حالت افزودن جدید
                    message = "ثبت"
                    
                    # 1. ابتدا بررسی می‌کنیم قطعه در جدول Parts وجود دارد یا خیر
                    part_record = self.data_manager.part.get_part_by_code(data['part_code'])
                    
                    if part_record:
                        part_id = part_record['id']
                        print(f"✅ قطعه با کد {data['part_code']} در دیتابیس موجود است. part_id: {part_id}")
                    else:
                        # قطعه جدید در جدول Parts ایجاد می‌کنیم
                        part_data = {
                            'part_code': data['part_code'],
                            'part_name': data['part_name'],
                            'category': data['category_name'],
                            'brand': data['brand_name'],
                            'model': data['model'],
                            'unit': data['unit'],
                            'min_stock': data['min_stock'],
                            'max_stock': data['max_stock'],
                            'description': data['description']
                        }
                        
                        print(f"➕ ایجاد قطعه جدید در جدول Parts: {part_data}")
                        
                        success = self.data_manager.part.add_part(part_data)
                        if not success:
                            self.show_error("خطا در ایجاد قطعه جدید در جدول Parts")
                            return
                        
                        part_record = self.data_manager.part.get_part_by_code(data['part_code'])
                        if not part_record:
                            self.show_error("خطا در دریافت شناسه قطعه ایجاد شده")
                            return
                        
                        part_id = part_record['id']
                        print(f"✅ قطعه جدید با part_id {part_id} ایجاد شد")
                    
                    # 🔴 آماده‌سازی داده‌ها برای ذخیره در انبار قطعات نو
                    warehouse_data = {
                        'part_id': part_id,
                        'quantity': data['quantity'],
                        'purchase_price': data['purchase_price'],
                        'sale_price': data['sale_price'],
                        'supplier_id': data['supplier_id'],
                        'purchase_date': data['purchase_date'],  # میلادی
                        'batch_number': data['batch_number'],
                        'expiration_date': data['expiration_date'],
                        'location': data['location'],
                        'status': data['status']
                    }
                    
                    print(f"📦 داده‌های انبار برای ذخیره: {warehouse_data}")
                    
                    # 🔴 کوئری INSERT اصلاح شده - بررسی NULL برای supplier_id و expiration_date
                    insert_query = """
                    INSERT INTO NewPartsWarehouse (
                        part_id, quantity, purchase_price, sale_price, supplier_id,
                        purchase_date, batch_number, expiration_date, location, status
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """
                    
                    # 🔴 تبدیل None به NULL برای دیتابیس
                    supplier_param = warehouse_data['supplier_id']
                    expiration_param = warehouse_data['expiration_date']
                    
                    params = (
                        warehouse_data['part_id'],
                        warehouse_data['quantity'],
                        warehouse_data['purchase_price'],
                        warehouse_data['sale_price'],
                        supplier_param,  # می‌تواند None باشد
                        warehouse_data['purchase_date'],
                        warehouse_data['batch_number'],
                        expiration_param,  # می‌تواند None باشد
                        warehouse_data['location'],
                        warehouse_data['status']
                    )
                    
                    success = self.data_manager.db.execute_query(insert_query, params)
                    
                    if success:
                        # دریافت ID قطعه اضافه شده (با استفاده از part_id و purchase_date)
                        get_id_query = """
                        SELECT id FROM NewPartsWarehouse 
                        WHERE part_id = ? AND purchase_date = ?
                        ORDER BY id DESC LIMIT 1
                        """
                        
                        result = self.data_manager.db.fetch_one(get_id_query, (part_id, data['purchase_date']))
                        
                        if result and 'id' in result:
                            item_id = result['id']
                            print(f"   🎯 قطعه نو با شناسه {item_id} ثبت شد")
                            
                            # 🔴 ثبت تراکنش انبار
                            try:
                                print(f"   📝 در حال ثبت تراکنش انبار...")
                                
                                transaction_query = """
                                INSERT INTO InventoryTransactions (
                                    transaction_type, warehouse_type, item_id, quantity, unit_price,
                                    total_price, transaction_date, related_document, description, employee
                                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                                """
                                
                                from PySide6.QtCore import QDateTime
                                transaction_date = QDateTime.currentDateTime().toString("yyyy-MM-dd HH:mm:ss")
                                
                                quantity = data['quantity']
                                purchase_price = data['purchase_price']
                                total_price = quantity * purchase_price
                                
                                transaction_params = (
                                    'خرید',
                                    'قطعات نو',
                                    item_id,
                                    quantity,
                                    purchase_price,
                                    total_price,
                                    transaction_date,
                                    data.get('batch_number', 'بدون شماره سند'),
                                    f"خرید قطعه نو - {data['part_name']} ({data['part_code']})",
                                    data['employee']
                                )
                                
                                transaction_success = self.data_manager.db.execute_query(transaction_query, transaction_params)
                                
                                if transaction_success:
                                    print(f"   ✅ تراکنش انبار برای قطعه #{item_id} ثبت شد")
                                else:
                                    print(f"   ⚠️ خطا در ثبت تراکنش انبار (اما قطعه ذخیره شد)")
                                
                            except Exception as trans_error:
                                print(f"   ⚠️ خطا در ثبت تراکنش انبار: {trans_error}")
                            
                            result = True
                        else:
                            print(f"   ❌ نتوانستیم ID قطعه را پیدا کنیم")
                            result = False
                    else:
                        result = False
                
                if result:
                    # سیگنال تغییر داده
                    if hasattr(self, 'data_changed'):
                        self.data_changed.emit()
                    
                    # نمایش پیام موفقیت
                    self.show_success(f"قطعه نو با موفقیت {message} شد.")
                    
                    # پاک کردن فرم و تازه‌سازی
                    self.clear_form()
                    self.load_from_database()  # بارگذاری مجدد از دیتابیس
                else:
                    self.show_error(f"خطا در {message} قطعه!")
            else:
                self.show_error("اتصال به دیتابیس برقرار نیست!")
                
        except Exception as e:
            print(f"❌ خطا در ذخیره قطعه: {e}")
            import traceback
            traceback.print_exc()
            self.show_error(f"خطا در ذخیره قطعه: {str(e)}")


    def shamsi_to_miladi(self, shamsi_date_str):
        """تبدیل تاریخ شمسی به میلادی"""
        if not shamsi_date_str:
            return None
        
        try:
            # جدا کردن اجزای تاریخ
            import re
            numbers = re.findall(r'\d+', str(shamsi_date_str))
            
            if len(numbers) >= 3:
                year, month, day = map(int, numbers[:3])
                
                # اگر سال بین 1300-1500 است، یعنی شمسی است
                if 1300 <= year <= 1500:
                    jalali = jdatetime.date(year, month, day)
                    gregorian = jalali.togregorian()
                    return gregorian.strftime("%Y-%m-%d")
                else:
                    # احتمالاً میلادی است
                    return f"{year:04d}-{month:02d}-{day:02d}"
            else:
                # تاریخ نامعتبر
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
            # جدا کردن اجزای تاریخ
            import re
            numbers = re.findall(r'\d+', str(miladi_date_str))
            
            if len(numbers) >= 3:
                year, month, day = map(int, numbers[:3])
                
                # اگر سال بزرگتر از 1500 است، یعنی میلادی است
                if year > 1500:
                    from datetime import date
                    gregorian_date = date(year, month, day)
                    jalali = jdatetime.date.fromgregorian(date=gregorian_date)
                    return jalali.strftime("%Y/%m/%d")
                else:
                    # احتمالاً شمسی است
                    return f"{year:04d}/{month:02d}/{day:02d}"
            else:
                return str(miladi_date_str)
                
        except Exception as e:
            print(f"خطا در تبدیل میلادی به شمسی: {e}")
            return str(miladi_date_str)
    
    def validate_form(self):
        """اعتبارسنجی فرم"""
        errors = []
        
        if not self.part_code.text().strip():
            errors.append("کد قطعه الزامی است.")
        
        if not self.part_name.text().strip():
            errors.append("نام قطعه الزامی است.")
        
        if self.category.get_value() == 0:
            errors.append("دسته‌بندی الزامی است.")
        
        if self.quantity.value() < 0:
            errors.append("موجودی نمی‌تواند منفی باشد.")
        
        purchase_price = self.purchase_price.get_value_toman()
        if purchase_price <= 0:
            errors.append("قیمت خرید باید بزرگتر از صفر باشد.")
        
        sale_price = self.sale_price.get_value_toman()
        if sale_price <= 0:
            errors.append("قیمت فروش باید بزرگتر از صفر باشد.")
        
        if errors:
            error_msg = "\n".join(f"• {error}" for error in errors)
            self.show_error(f"لطفا خطاهای زیر را اصلاح کنید:\n\n{error_msg}")
            return False
        
        return True

    def edit_item(self, item_id):
        """ویرایش قطعه نو - نسخه اصلاح شده"""
        try:
            # پیدا کردن قطعه
            item_to_edit = None
            for item in self.all_data:
                if item['id'] == item_id:
                    item_to_edit = item
                    break
            
            if not item_to_edit:
                self.show_error("قطعه مورد نظر یافت نشد.")
                return
            
            self.current_edit_id = item_id
            
            # پر کردن فرم
            self.part_code.setText(item_to_edit.get('part_code', ''))
            self.part_name.setText(item_to_edit.get('part_name', ''))
            
            # 🔴 **اصلاح بخش دسته‌بندی - استفاده از set_text**
            category_name = item_to_edit.get('category', '')
            print(f"🔍 تنظیم دسته‌بندی: '{category_name}'")
            if category_name:
                self.category.set_text(category_name)
            
            # 🔴 **اصلاح بخش برند - استفاده از set_text**
            brand_name = item_to_edit.get('brand', '')
            print(f"🔍 تنظیم برند: '{brand_name}'")
            if brand_name:
                self.brand.set_text(brand_name)
            
            # تنظیم مدل
            self.model.setText(item_to_edit.get('model', ''))
            
            # تنظیم واحد
            unit = item_to_edit.get('unit', 'عدد')
            print(f"🔍 تنظیم واحد: '{unit}'")
            if unit:
                self.unit.setCurrentText(unit)
            
            self.quantity.setValue(item_to_edit.get('quantity', 0))
            self.min_stock.setValue(item_to_edit.get('min_stock', 5))
            self.max_stock.setValue(item_to_edit.get('max_stock', 100))
            
            # تنظیم قیمت‌ها
            self.purchase_price.set_value(item_to_edit.get('purchase_price', 0))
            self.sale_price.set_value(item_to_edit.get('sale_price', 0))
            
            # 🔴 **اصلاح بخش تامین‌کننده - استفاده از set_text**
            supplier_name = item_to_edit.get('supplier', '')
            print(f"🔍 تنظیم تامین‌کننده: '{supplier_name}'")
            if supplier_name:
                self.supplier.set_text(supplier_name)
            
            # تنظیم تاریخ خرید (شمسی)
            purchase_date = item_to_edit.get('purchase_date', '')
            print(f"🔍 تنظیم تاریخ خرید: '{purchase_date}'")
            if purchase_date:
                # حذف کاراکترهای نامربوط از تاریخ
                import re
                numbers = re.findall(r'\d+', str(purchase_date))
                if len(numbers) >= 3:
                    # فرمت تاریخ: YYYY/MM/DD یا YYYY-MM-DD
                    year, month, day = numbers[:3]
                    formatted_date = f"{year}/{month}/{day}"
                    self.purchase_date.set_date(formatted_date)
                else:
                    self.purchase_date.set_date(str(purchase_date))
            
            self.batch_number.setText(item_to_edit.get('batch_number', ''))
            
            # تنظیم تاریخ انقضا (شمسی)
            expiration_date = item_to_edit.get('expiration_date', '')
            print(f"🔍 تنظیم تاریخ انقضا: '{expiration_date}'")
            if expiration_date:
                # حذف کاراکترهای نامربوط از تاریخ
                import re
                numbers = re.findall(r'\d+', str(expiration_date))
                if len(numbers) >= 3:
                    # فرمت تاریخ: YYYY/MM/DD یا YYYY-MM-DD
                    year, month, day = numbers[:3]
                    formatted_date = f"{year}/{month}/{day}"
                    self.expiration_date.set_date(formatted_date)
                else:
                    self.expiration_date.set_date(str(expiration_date))
            
            self.location.setText(item_to_edit.get('location', ''))
            
            # تنظیم وضعیت
            status = item_to_edit.get('status', 'موجود')
            print(f"🔍 تنظیم وضعیت: '{status}'")
            if status:
                self.status.setCurrentText(status)
            
            self.description.setPlainText(item_to_edit.get('description', ''))
            
            # تغییر دکمه ذخیره
            self.btn_save.setText("💾 به‌روزرسانی قطعه")
            self.btn_save.setProperty("style", "warning")
            
            # اسکرول به بالا
            self.scroll_area.verticalScrollBar().setValue(0)
            
        except Exception as e:
            print(f"❌ خطا در ویرایش قطعه: {e}")
            import traceback
            traceback.print_exc()
            self.show_error(f"خطا در ویرایش قطعه: {str(e)}")

    def set_combo_value(self, combo, value):
        """تنظیم مقدار کامبوباکس به صورت هوشمند"""
        if not value:
            combo.setCurrentIndex(0)
            return
        
        # ابتدا سعی می‌کنیم متن را پیدا کنیم
        index = combo.findText(str(value), Qt.MatchFixedString)
        if index >= 0:
            combo.setCurrentIndex(index)
            return
        
        # اگر پیدا نشد، جستجوی جزئی
        for i in range(combo.count()):
            item_text = combo.itemText(i)
            if str(value) in item_text:
                combo.setCurrentIndex(i)
                return
        
        # اگر باز هم پیدا نشد، متن را تنظیم می‌کنیم
        combo.setEditText(str(value))

    def delete_item_with_transaction(self, item_id, reason="حذف دستی"):
        """حذف آیتم از انبار با ثبت تراکنش - نسخه اصلاح شده"""
        print(f"🔴 delete_item_with_transaction شروع شد برای item_id: {item_id}")
        
        try:
            if not self.data_manager or not hasattr(self.data_manager, 'warehouse'):
                self.show_error("اتصال به دیتابیس برقرار نیست!")
                return False
            
            # دریافت اطلاعات کامل آیتم قبل از حذف
            print(f"🔴 در حال دریافت اطلاعات آیتم {item_id}...")
            item_info = self.data_manager.warehouse.get_warehouse_item_info('قطعات نو', item_id)
            
            if not item_info:
                self.show_error("آیتم مورد نظر یافت نشد!")
                return False
            
            # نمایش تاییدیه ساده با QMessageBox
            print(f"🔴 نمایش تاییدیه حذف...")
            
            # ساخت پیام اطلاعاتی
            message_text = f"""
            <div style='font-family: B Nazanin; font-size: 12pt;'>
            <b style='color: red;'>⚠️ تایید حذف قطعه با ثبت تراکنش</b>
            <hr>
            <b>نام قطعه:</b> {item_info.get('part_name', 'نامشخص')}
            <br><b>کد قطعه:</b> {item_info.get('part_code', 'نامشخص')}
            <br><b>دسته‌بندی:</b> {item_info.get('category', 'نامشخص')}
            <br><b>برند:</b> {item_info.get('brand', 'نامشخص')}
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
                "تایید حذف قطعه",
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
                warehouse_type='قطعات نو',
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
                    f"قطعه '{item_info.get('part_name')}' با موفقیت حذف شد.\nتراکنش حذف در سیستم ثبت گردید."
                )
                
                # ثبت لاگ
                log_data = {
                    'user_id': 1,
                    'action': 'حذف قطعه نو',
                    'table_name': 'NewPartsWarehouse',
                    'record_id': item_id,
                    'details': f"حذف قطعه {item_info.get('part_name')} ({item_info.get('part_code')}) - دلیل: {reason_text}",
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
            
            # گرفتن کد قطعه از ستون دوم (ستون 1)
            part_code_item = self.table.item(row, 1)
            if not part_code_item:
                self.show_error("نمی‌توان کد قطعه را پیدا کرد.")
                return
            
            part_code = part_code_item.text()
            print(f"🔴 کد قطعه: {part_code}")
            
            # پیدا کردن آیتم در all_data
            item_id = None
            for item in self.all_data:
                if str(item.get('part_code', '')) == part_code:
                    item_id = item.get('id')
                    print(f"🔴 یافتن item_id: {item_id}")
                    break
            
            if not item_id:
                # اگر از طریق کد پیدا نکردیم، از طریق شماره ردیف در جدول امتحان کنیم
                if row < len(self.all_data):
                    item_id = self.all_data[row].get('id')
                    print(f"🔴 item_id از طریق ردیف: {item_id}")
            
            if not item_id:
                self.show_error("آیتم انتخاب شده در داده‌ها یافت نشد.")
                return
            
            # حذف با ثبت تراکنش
            print(f"🔴 فراخوانی delete_item_with_transaction با item_id: {item_id}")
            if self.delete_item_with_transaction(item_id):
                self.show_success("قطعه با موفقیت حذف شد و تراکنش ثبت گردید.")
                
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
            self.show_success("قطعه با موفقیت حذف شد و تراکنش ثبت گردید.")
            self.load_from_database()
            if hasattr(self, 'data_changed'):
                self.data_changed.emit()

    def soft_delete_item(self, item_id, reason="حذف نرم"):
        """حذف نرم آیتم (تغییر وضعیت به 'ناموجود')"""
        try:
            if not self.data_manager or not hasattr(self.data_manager, 'warehouse'):
                self.show_error("اتصال به دیتابیس برقرار نیست!")
                return False
            
            # نمایش تاییدیه
            reply = QMessageBox.question(
                self,
                "تایید حذف نرم",
                "آیا از تغییر وضعیت این قطعه به 'ناموجود' اطمینان دارید؟\n\n(این قطعه از لیست موجودی حذف می‌شود اما در دیتابیس باقی می‌ماند)",
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
                warehouse_type='قطعات نو',
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
            self.load_from_database()
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
                    self.load_from_database()
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

    def on_edit(self):
        """ویرایش قطعه انتخاب شده"""
        selected_rows = self.table.selectionModel().selectedRows()
        if selected_rows:
            row = selected_rows[0].row()
            if row < len(self.all_data):
                item_id = self.all_data[row]['id']
                self.edit_item(item_id)   
   
    def export_excel(self):
        """خروجی Excel"""
        self.show_success("خروجی Excel تولید شد (ویژگی در حال توسعه).")
    
    def print_report(self):
        """چاپ گزارش"""
        self.show_success("گزارش آماده چاپ است (ویژگی در حال توسعه).")