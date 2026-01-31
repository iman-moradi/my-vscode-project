# ui/forms/repair_form/repair_parts_tab.py
from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *

class RepairPartsTab(QWidget):
    parts_changed = Signal()
    
    def __init__(self, data_manager, parent=None):
        super().__init__(parent)
        self.data_manager = data_manager
        self.parts = []  # یا self.parts = []
        self.setup_ui()
        # بارگذاری اولیه
    
    def setup_ui(self):
        layout = QVBoxLayout(self)  # لایه مستقیم روی ویجت
        layout.setSpacing(15)
        layout.setContentsMargins(15, 15, 15, 15)
        
        # گروه‌ها را مستقیماً اضافه کنید
        group_search = self.create_search_group()
        group_added = self.create_added_group()
        
        layout.addWidget(group_search)
        layout.addWidget(group_added, 1)  # ضریب کشش 1 برای گروه اضافه شده
        
        self.setLayout(layout)
    
    def create_search_group(self):
        """ایجاد گروه جستجوی قطعات"""
        group = QGroupBox("🔍 جستجو و مدیریت قطعات")
        group.setMinimumHeight(400)
        
        layout = QGridLayout()
        layout.setSpacing(10)
        
        # ردیف 1: جستجوی قطعه
        lbl_search = QLabel("جستجوی قطعه:")
        lbl_search.setStyleSheet("font-weight: bold;")
        layout.addWidget(lbl_search, 0, 0)
        
        self.txt_part_search = QLineEdit()
        self.txt_part_search.setPlaceholderText("نام قطعه، کد یا برند را وارد کنید...")
        self.txt_part_search.textChanged.connect(self.search_parts)
        layout.addWidget(self.txt_part_search, 0, 1, 1, 2)
        
        # ردیف 2: انتخاب انبار
        lbl_warehouse = QLabel("انبار:")
        lbl_warehouse.setStyleSheet("font-weight: bold;")
        layout.addWidget(lbl_warehouse, 1, 0)
        
        self.cmb_warehouse = QComboBox()
        self.cmb_warehouse.addItems(["قطعات نو", "قطعات دست دوم"])
        self.cmb_warehouse.currentTextChanged.connect(self.search_parts)
        self.cmb_warehouse.setMinimumWidth(150)
        layout.addWidget(self.cmb_warehouse, 1, 1, 1, 2)
        
        # ردیف 3: لیست قطعات یافت شده
        self.list_parts = QListWidget()
        self.list_parts.setMinimumHeight(200)
        self.list_parts.setMaximumHeight(300)
        self.list_parts.itemClicked.connect(self.on_part_selected)
        self.list_parts.itemDoubleClicked.connect(self.add_selected_part)
        layout.addWidget(self.list_parts, 2, 0, 1, 3)
        
        # ردیف 4: اطلاعات قطعه انتخاب شده
        self.lbl_part_info = QLabel("💡 قطعه‌ای انتخاب نشده است")
        self.lbl_part_info.setStyleSheet("""
            QLabel {
                color: #95a5a6;
                font-style: italic;
                padding: 10px;
                background-color: #2d2d2d;
                border-radius: 5px;
                border: 1px solid #444444;
                min-height: 80px;
            }
        """)
        self.lbl_part_info.setWordWrap(True)
        layout.addWidget(self.lbl_part_info, 3, 0, 1, 3)
        
        # ردیف 5: کنترل‌های مقدار و قیمت
        control_layout = QGridLayout()
        
        lbl_quantity = QLabel("تعداد:")
        lbl_quantity.setStyleSheet("font-weight: bold;")
        control_layout.addWidget(lbl_quantity, 0, 0)
        
        self.spn_part_quantity = QSpinBox()
        self.spn_part_quantity.setRange(1, 1000)
        self.spn_part_quantity.setValue(1)
        self.spn_part_quantity.setMinimumWidth(120)
        control_layout.addWidget(self.spn_part_quantity, 0, 1)
        
        lbl_price = QLabel("قیمت واحد (تومان):")
        lbl_price.setStyleSheet("font-weight: bold;")
        control_layout.addWidget(lbl_price, 1, 0)
        
        self.spn_part_price = QDoubleSpinBox()
        self.spn_part_price.setRange(0, 10000000)
        self.spn_part_price.setValue(0)
        self.spn_part_price.setMinimumWidth(150)
        self.spn_part_price.setSuffix(" تومان")
        control_layout.addWidget(self.spn_part_price, 1, 1)
        
        # دکمه افزودن
        self.btn_add_part = QPushButton("➕ افزودن به لیست")
        self.btn_add_part.setIcon(QIcon.fromTheme("list-add"))
        self.btn_add_part.clicked.connect(self.add_selected_part)
        self.btn_add_part.setMinimumHeight(40)
        control_layout.addWidget(self.btn_add_part, 0, 2, 2, 1)
        
        layout.addLayout(control_layout, 4, 0, 1, 3)
        
        group.setLayout(layout)
        return group
    
    def create_added_group(self):
        """ایجاد گروه لیست قطعات افزوده شده"""
        group = QGroupBox("📦 لیست قطعات افزوده شده")
        group.setMinimumHeight(300)
        
        layout = QVBoxLayout()
        
        # جدول قطعات
        self.table_parts = QTableWidget()
        self.table_parts.setColumnCount(8)
        self.table_parts.setHorizontalHeaderLabels([
            "ردیف", "نام قطعه", "کد", "انبار", "تعداد", "قیمت واحد", "قیمت کل", "عملیات"
        ])
        self.table_parts.horizontalHeader().setStretchLastSection(True)
        self.table_parts.setAlternatingRowColors(True)
        self.table_parts.setMinimumHeight(200)
        layout.addWidget(self.table_parts)
        
        # جمع هزینه قطعات
        self.lbl_parts_total = QLabel("💰 جمع کل قطعات: ۰ تومان")
        self.lbl_parts_total.setStyleSheet("""
            QLabel {
                font-size: 12pt; 
                font-weight: bold; 
                color: #E74C3C;
                padding: 10px;
                background-color: #2d1f2c;
                border-radius: 5px;
                border: 1px solid #E74C3C;
            }
        """)
        self.lbl_parts_total.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.lbl_parts_total)
        
        group.setLayout(layout)
        return group
    
    # ... بقیه متدها (search_parts, on_part_selected, etc.) بدون تغییر ...
    
    def search_parts(self, search_text=""):
        """جستجوی قطعات در انبار"""
        warehouse = self.cmb_warehouse.currentText()
        search_term = self.txt_part_search.text()
        
        try:
            if warehouse == "قطعات نو":
                query = """
                SELECT 
                    p.id, p.part_code, p.part_name, p.category, p.brand, p.model,
                    COALESCE(np.quantity, 0) as qty,
                    COALESCE(np.sale_price, 0) as price
                FROM Parts p
                LEFT JOIN NewPartsWarehouse np ON p.id = np.part_id
                WHERE np.status = 'موجود' AND COALESCE(np.quantity, 0) > 0
                """
            else:  # قطعات دست دوم
                query = """
                SELECT 
                    p.id, p.part_code, p.part_name, p.category, p.brand, p.model,
                    COALESCE(up.quantity, 0) as qty,
                    COALESCE(up.sale_price, 0) as price
                FROM Parts p
                LEFT JOIN UsedPartsWarehouse up ON p.id = up.part_id
                WHERE up.status = 'موجود' AND COALESCE(up.quantity, 0) > 0
                """
            
            if search_term and len(search_term) >= 2:
                query += " AND (p.part_name LIKE ? OR p.part_code LIKE ? OR p.brand LIKE ?)"
                params = [f"%{search_term}%", f"%{search_term}%", f"%{search_term}%"]
            else:
                params = []
            
            query += " ORDER BY p.part_name"
            
            parts = self.data_manager.db.fetch_all(query, params)
            self.display_parts_list(parts, warehouse)
            
        except Exception as e:
            print(f"خطا در جستجوی قطعات: {e}")
    
    def display_parts_list(self, parts, warehouse):
        """نمایش قطعات در لیست"""
        self.list_parts.clear()
        
        for part in parts:
            # نمایش قیمت به تومان
            price_toman = (part['price'] or 0) / 10
            qty = part['qty'] or 0
            
            item_text = (f"🔩 {part['part_code']} - {part['part_name']}\n"
                        f"   برند: {part.get('brand', 'ندارد')} | دسته: {part.get('category', 'ندارد')}\n"
                        f"   انبار: {warehouse} | موجودی: {qty} عدد | قیمت: {price_toman:,.0f} تومان")
            
            item = QListWidgetItem(item_text)
            item.setData(Qt.UserRole, {
                'id': part['id'],
                'part_code': part['part_code'],
                'part_name': part['part_name'],
                'brand': part.get('brand', ''),
                'category': part.get('category', ''),
                'warehouse': warehouse,
                'price': part['price'] or 0,
                'qty': qty
            })
            self.list_parts.addItem(item)
    
    def on_part_selected(self, item):
        """وقتی یک قطعه از لیست انتخاب شد"""
        part_data = item.data(Qt.UserRole)
        if part_data:
            # نمایش قیمت به تومان
            price_toman = part_data['price'] / 10
            
            info_text = (
                f"📦 کد: {part_data['part_code']}\n"
                f"🏷️ نام: {part_data['part_name']}\n"
                f"🏭 برند: {part_data.get('brand', 'ندارد')}\n"
                f"📁 دسته: {part_data.get('category', 'ندارد')}\n"
                f"🏪 انبار: {part_data['warehouse']}\n"
                f"📊 موجودی: {part_data['qty']} عدد\n"
                f"💰 قیمت پیشنهادی: {price_toman:,.0f} تومان"
            )
            self.lbl_part_info.setText(info_text)
            
            # تنظیم قیمت پیش‌فرض در فیلد قیمت (تومان)
            self.spn_part_price.setValue(price_toman)
            
            # تنظیم حداکثر تعداد بر اساس موجودی
            self.spn_part_quantity.setMaximum(part_data['qty'])
    
    def add_selected_part(self):
        """افزودن قطعه انتخاب شده به لیست"""
        current_item = self.list_parts.currentItem()
        if not current_item:
            QMessageBox.warning(self, "اخطار", "لطفاً ابتدا یک قطعه را انتخاب کنید.")
            return
        
        part_data = current_item.data(Qt.UserRole)
        quantity = self.spn_part_quantity.value()
        unit_price_toman = self.spn_part_price.value()  # قیمت به تومان
        
        if unit_price_toman <= 0:
            QMessageBox.warning(self, "اخطار", "لطفاً قیمت واحد را وارد کنید.")
            return
        
        # تبدیل به ریال برای ذخیره در دیتابیس
        unit_price = unit_price_toman * 10
        total_price = quantity * unit_price
        
        # افزودن به لیست قطعات
        part_item = {
            'part_id': part_data['id'],
            'part_code': part_data['part_code'],
            'part_name': part_data['part_name'],
            'brand': part_data.get('brand', ''),
            'category': part_data.get('category', ''),
            'warehouse_type': part_data['warehouse'],
            'quantity': quantity,
            'unit_price': unit_price,  # ریال
            'total_price': total_price,  # ریال
            'available_qty': part_data['qty']
        }
        
        self.parts.append(part_item)
        self.update_parts_table()
        self.calculate_total()
        self.parts_changed.emit()
    
    def update_parts_table(self):
        """بروزرسانی جدول قطعات"""
        self.table_parts.setRowCount(len(self.parts))
        
        for row, part in enumerate(self.parts):
            # ردیف
            item_row = QTableWidgetItem(str(row + 1))
            item_row.setTextAlignment(Qt.AlignCenter)
            self.table_parts.setItem(row, 0, item_row)
            
            # نام قطعه
            item_name = QTableWidgetItem(part['part_name'])
            self.table_parts.setItem(row, 1, item_name)
            
            # کد
            item_code = QTableWidgetItem(part['part_code'])
            self.table_parts.setItem(row, 2, item_code)
            
            # انبار
            item_warehouse = QTableWidgetItem(part['warehouse_type'])
            self.table_parts.setItem(row, 3, item_warehouse)
            
            # تعداد
            item_qty = QTableWidgetItem(str(part['quantity']))
            item_qty.setTextAlignment(Qt.AlignCenter)
            self.table_parts.setItem(row, 4, item_qty)
            
            # قیمت واحد (تومان)
            unit_price_toman = part['unit_price'] / 10
            item_unit = QTableWidgetItem(f"{unit_price_toman:,.0f}")
            item_unit.setTextAlignment(Qt.AlignCenter)
            self.table_parts.setItem(row, 5, item_unit)
            
            # قیمت کل (تومان)
            total_price_toman = part['total_price'] / 10
            item_total = QTableWidgetItem(f"{total_price_toman:,.0f}")
            item_total.setTextAlignment(Qt.AlignCenter)
            self.table_parts.setItem(row, 6, item_total)
            
            # دکمه حذف
            btn_remove = QPushButton("🗑️ حذف")
            btn_remove.setStyleSheet("""
                QPushButton {
                    background-color: #dc3545;
                    color: white;
                    border-radius: 4px;
                    padding: 5px 10px;
                }
                QPushButton:hover {
                    background-color: #c82333;
                }
            """)
            btn_remove.clicked.connect(lambda _, r=row: self.remove_part(r))
            self.table_parts.setCellWidget(row, 7, btn_remove)
        
        self.table_parts.resizeColumnsToContents()
    
    def remove_part(self, row):
        """حذف یک قطعه از لیست"""
        if 0 <= row < len(self.parts):
            self.parts.pop(row)
            self.update_parts_table()
            self.calculate_total()
            self.parts_changed.emit()
    
    def calculate_total(self):
        """محاسبه جمع کل قطعات (تومان)"""
        total_rials = sum(part['total_price'] for part in self.parts)
        total_toman = total_rials / 10
        self.lbl_parts_total.setText(f"💰 جمع کل قطعات: {total_toman:,.0f} تومان")
        return total_rials  # بازگشت به ریال
    
    def get_parts_data(self):
        """دریافت لیست قطعات"""
        return self.parts
    
    def set_parts(self, parts_data):
        """بارگذاری قطعات از دیتابیس (برای ویرایش)"""
        self.parts = []
        for part in parts_data:
            part_item = {
                'part_id': part['part_id'],
                'part_code': part.get('part_code', ''),
                'part_name': part.get('part_name', ''),
                'brand': part.get('brand', ''),
                'category': part.get('category', ''),
                'warehouse_type': part.get('warehouse_type', 'قطعات نو'),
                'quantity': part['quantity'],
                'unit_price': part['unit_price'],
                'total_price': part['total_price']
            }
            self.parts.append(part_item)
        
        self.update_parts_table()
        self.calculate_total()

    def get_total(self):
        """دریافت جمع کل هزینه قطعات (ریال)"""
        return sum(part['total_price'] for part in self.parts)