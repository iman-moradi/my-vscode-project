# ui/forms/repair_form/repair_services_tab.py
from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *

class RepairServicesTab(QWidget):
    services_changed = Signal()
    add_service_requested = Signal()
    
    def __init__(self, data_manager, parent=None):
        super().__init__(parent)
        self.data_manager = data_manager
        self.services = []
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(15, 15, 15, 15)
        
        group_search = self.create_search_group()
        group_added = self.create_added_group()
        
        layout.addWidget(group_search)
        layout.addWidget(group_added, 1)
        
        self.setLayout(layout)
    
    def create_search_group(self):
        """ایجاد گروه جستجوی خدمات"""
        group = QGroupBox("🔍 جستجو و مدیریت اجرت‌ها")
        group.setMinimumHeight(400)
        
        layout = QGridLayout()
        layout.setSpacing(10)
        
        # ردیف 1: فیلتر دسته‌بندی
        lbl_category = QLabel("دسته‌بندی:")
        lbl_category.setStyleSheet("font-weight: bold;")
        layout.addWidget(lbl_category, 0, 0)
        
        self.cmb_category = QComboBox()
        self.cmb_category.setMinimumWidth(200)
        self.cmb_category.currentTextChanged.connect(self.search_services)
        layout.addWidget(self.cmb_category, 0, 1)
        
        # دکمه افزودن دسته
        self.btn_add_category = QPushButton("➕ افزودن دسته")
        self.btn_add_category.clicked.connect(self.add_new_category)
        layout.addWidget(self.btn_add_category, 0, 2)
        
        # دکمه مدیریت اجرت‌ها
        self.btn_manage_services = QPushButton("⚙️ مدیریت اجرت‌ها")
        self.btn_manage_services.setIcon(QIcon.fromTheme("preferences-system"))
        self.btn_manage_services.clicked.connect(self.open_service_manager)
        layout.addWidget(self.btn_manage_services, 0, 3)
        
        # ردیف 2: جستجوی متن
        lbl_search = QLabel("جستجوی خدمت:")
        lbl_search.setStyleSheet("font-weight: bold;")
        layout.addWidget(lbl_search, 1, 0)
        
        self.txt_service_search = QLineEdit()
        self.txt_service_search.setPlaceholderText("نام خدمت یا کد آن را وارد کنید...")
        self.txt_service_search.textChanged.connect(self.search_services)
        layout.addWidget(self.txt_service_search, 1, 1, 1, 3)
        
        # ردیف 3: لیست خدمات یافت شده
        self.list_services = QListWidget()
        self.list_services.setMinimumHeight(200)
        self.list_services.setMaximumHeight(300)
        self.list_services.itemClicked.connect(self.on_service_selected)
        self.list_services.itemDoubleClicked.connect(self.add_selected_service)
        layout.addWidget(self.list_services, 2, 0, 1, 4)
        
        # ردیف 4: اطلاعات خدمت انتخاب شده
        self.lbl_service_info = QLabel("💡 خدمتی انتخاب نشده است")
        self.lbl_service_info.setStyleSheet("""
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
        self.lbl_service_info.setWordWrap(True)
        layout.addWidget(self.lbl_service_info, 3, 0, 1, 4)
        
        # ردیف 5: کنترل‌های مقدار و قیمت
        control_layout = QGridLayout()
        
        lbl_quantity = QLabel("تعداد/مقدار:")
        lbl_quantity.setStyleSheet("font-weight: bold;")
        control_layout.addWidget(lbl_quantity, 0, 0)
        
        self.spn_quantity = QDoubleSpinBox()
        self.spn_quantity.setRange(0.1, 100)
        self.spn_quantity.setValue(1.0)
        self.spn_quantity.setSingleStep(0.5)
        self.spn_quantity.setSuffix(" واحد")
        self.spn_quantity.setMinimumWidth(120)
        control_layout.addWidget(self.spn_quantity, 0, 1)
        
        lbl_price = QLabel("قیمت واحد (تومان):")
        lbl_price.setStyleSheet("font-weight: bold;")
        control_layout.addWidget(lbl_price, 1, 0)
        
        self.spn_unit_price = QDoubleSpinBox()
        self.spn_unit_price.setRange(0, 100000000)
        self.spn_unit_price.setValue(0)
        self.spn_unit_price.setMinimumWidth(150)
        self.spn_unit_price.setSuffix(" تومان")
        control_layout.addWidget(self.spn_unit_price, 1, 1)
        
        # دکمه افزودن
        self.btn_add_service = QPushButton("➕ افزودن به لیست")
        self.btn_add_service.setIcon(QIcon.fromTheme("list-add"))
        self.btn_add_service.clicked.connect(self.add_selected_service)
        self.btn_add_service.setMinimumHeight(40)
        control_layout.addWidget(self.btn_add_service, 0, 2, 2, 1)
        
        layout.addLayout(control_layout, 4, 0, 1, 4)
        
        group.setLayout(layout)
        return group
    
    def create_added_group(self):
        """ایجاد گروه لیست خدمات افزوده شده"""
        group = QGroupBox("📋 لیست خدمات افزوده شده")
        group.setMinimumHeight(300)
        
        layout = QVBoxLayout()
        
        self.table_services = QTableWidget()
        self.table_services.setColumnCount(7)
        self.table_services.setHorizontalHeaderLabels([
            "ردیف", "نام خدمت", "دسته", "تعداد", "قیمت واحد", "قیمت کل", "عملیات"
        ])
        self.table_services.horizontalHeader().setStretchLastSection(True)
        self.table_services.setAlternatingRowColors(True)
        self.table_services.setMinimumHeight(200)
        layout.addWidget(self.table_services)
        
        self.lbl_services_total = QLabel("💰 جمع کل خدمات: ۰ تومان")
        self.lbl_services_total.setStyleSheet("""
            QLabel {
                font-size: 12pt; 
                font-weight: bold; 
                color: #27AE60;
                padding: 10px;
                background-color: #1a1f2c;
                border-radius: 5px;
                border: 1px solid #27AE60;
            }
        """)
        self.lbl_services_total.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.lbl_services_total)
        
        group.setLayout(layout)
        return group
    
    def load_categories(self):
        """بارگذاری دسته‌بندی‌ها"""
        print("🔄 در حال بارگذاری دسته‌بندی‌ها از دیتابیس...")
        
        current_text = self.cmb_category.currentText() if self.cmb_category.count() > 0 else ""
        
        self.cmb_category.clear()
        self.cmb_category.addItem("همه دسته‌ها", "")
        
        try:
            query = """
                SELECT DISTINCT category 
                FROM ServiceFees 
                WHERE is_active = 1 
                    AND category IS NOT NULL 
                    AND TRIM(category) != ''
                ORDER BY category
            """
            
            categories = self.data_manager.db.fetch_all(query)
            
            if categories and len(categories) > 0:
                print(f"✅ {len(categories)} دسته‌بندی از دیتابیس بارگذاری شد")
                for item in categories:
                    category_name = item['category']
                    if category_name:
                        self.cmb_category.addItem(category_name, category_name)
                
                if current_text and current_text != "همه دسته‌ها":
                    index = self.cmb_category.findText(current_text)
                    if index >= 0:
                        self.cmb_category.setCurrentIndex(index)
            else:
                print("⚠️ هیچ دسته‌بندی فعالی در دیتابیس یافت نشد")
                default_cats = ["عمومی", "یخچال", "کولر گازی", "ماشین لباسشویی", "آبگرمکن"]
                for cat in default_cats:
                    self.cmb_category.addItem(cat, cat)
                    
        except Exception as e:
            print(f"❌ خطا در بارگذاری دسته‌بندی‌ها: {e}")
            import traceback
            traceback.print_exc()
    
    def add_new_category(self):
        """افزودن دسته جدید"""
        new_category, ok = QInputDialog.getText(
            self, 
            "افزودن دسته جدید",
            "نام دسته جدید را وارد کنید:",
            QLineEdit.Normal,
            ""
        )
        
        if ok and new_category.strip():
            category_name = new_category.strip()
            self.cmb_category.addItem(category_name, category_name)
            self.cmb_category.setCurrentText(category_name)
            
            # ذخیره موقت در حافظه
            QMessageBox.information(self, "موفقیت", 
                f"دسته '{category_name}' به لیست اضافه شد.\n\n"
                f"توجه: این دسته فقط در این جلسه برنامه ذخیره می‌شود.")
    
    def search_services(self):
        """جستجوی خدمات"""
        category = self.cmb_category.currentData()
        search_term = self.txt_service_search.text()
        
        try:
            query = """
            SELECT id, service_code, service_name, category, default_fee, estimated_hours, description
            FROM ServiceFees
            WHERE is_active = 1
            """
            
            params = []
            
            if category:
                query += " AND category = ?"
                params.append(category)
            
            if search_term and len(search_term) >= 2:
                query += " AND (service_name LIKE ? OR service_code LIKE ?)"
                params.extend([f"%{search_term}%", f"%{search_term}%"])
            
            query += " ORDER BY service_name"
            
            services = self.data_manager.db.fetch_all(query, params)
            self.display_services_list(services)
            
        except Exception as e:
            print(f"خطا در جستجوی خدمات: {e}")
    
    def display_services_list(self, services):
        """نمایش خدمات در لیست"""
        self.list_services.clear()
        
        for service in services:
            fee_toman = service['default_fee'] / 10
            
            item_text = (f"🔹 {service['service_code']} - {service['service_name']}\n"
                        f"   دسته: {service['category']} | تعرفه: {fee_toman:,.0f} تومان")
            
            if service.get('estimated_hours'):
                item_text += f" | زمان: {service['estimated_hours']} ساعت"
            
            item = QListWidgetItem(item_text)
            item.setData(Qt.UserRole, service)
            self.list_services.addItem(item)
    
    def on_service_selected(self, item):
        """وقتی یک خدمت از لیست انتخاب شد"""
        service_data = item.data(Qt.UserRole)
        if service_data:
            fee_toman = service_data['default_fee'] / 10
            
            info_text = (
                f"📋 کد: {service_data['service_code']}\n"
                f"🏷️ نام: {service_data['service_name']}\n"
                f"📁 دسته: {service_data['category']}\n"
                f"💰 تعرفه استاندارد: {fee_toman:,.0f} تومان\n"
                f"⏱️ زمان تخمینی: {service_data.get('estimated_hours', 'ندارد')} ساعت\n"
                f"📝 توضیحات: {service_data.get('description', 'ندارد')}"
            )
            self.lbl_service_info.setText(info_text)
            
            self.spn_unit_price.setValue(fee_toman)
    
    def add_selected_service(self):
        """افزودن خدمت انتخاب شده به لیست"""
        current_item = self.list_services.currentItem()
        if not current_item:
            QMessageBox.warning(self, "اخطار", "لطفاً ابتدا یک خدمت را انتخاب کنید.")
            return
        
        service_data = current_item.data(Qt.UserRole)
        quantity = self.spn_quantity.value()
        unit_price_toman = self.spn_unit_price.value()
        
        if unit_price_toman <= 0:
            QMessageBox.warning(self, "اخطار", "لطفاً قیمت واحد را وارد کنید.")
            return
        
        unit_price = unit_price_toman * 10
        total_price = quantity * unit_price
        
        service_item = {
            'service_id': service_data['id'],
            'service_code': service_data['service_code'],
            'service_name': service_data['service_name'],
            'category': service_data['category'],
            'quantity': quantity,
            'unit_price': unit_price,
            'total_price': total_price,
            'description': service_data.get('description', '')
        }
        
        self.services.append(service_item)
        self.update_services_table()
        self.calculate_total()
        self.services_changed.emit()
    
    def update_services_table(self):
        """بروزرسانی جدول خدمات"""
        self.table_services.setRowCount(len(self.services))
        
        for row, service in enumerate(self.services):
            # ردیف
            item_row = QTableWidgetItem(str(row + 1))
            item_row.setTextAlignment(Qt.AlignCenter)
            self.table_services.setItem(row, 0, item_row)
            
            # نام خدمت
            item_name = QTableWidgetItem(service['service_name'])
            self.table_services.setItem(row, 1, item_name)
            
            # دسته
            item_category = QTableWidgetItem(service['category'])
            self.table_services.setItem(row, 2, item_category)
            
            # تعداد
            item_qty = QTableWidgetItem(str(service['quantity']))
            item_qty.setTextAlignment(Qt.AlignCenter)
            self.table_services.setItem(row, 3, item_qty)
            
            # قیمت واحد (تومان)
            unit_price_toman = service['unit_price'] / 10
            item_unit = QTableWidgetItem(f"{unit_price_toman:,.0f}")
            item_unit.setTextAlignment(Qt.AlignCenter)
            self.table_services.setItem(row, 4, item_unit)
            
            # قیمت کل (تومان)
            total_price_toman = service['total_price'] / 10
            item_total = QTableWidgetItem(f"{total_price_toman:,.0f}")
            item_total.setTextAlignment(Qt.AlignCenter)
            self.table_services.setItem(row, 5, item_total)
            
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
            btn_remove.clicked.connect(lambda _, r=row: self.remove_service(r))
            self.table_services.setCellWidget(row, 6, btn_remove)
        
        self.table_services.resizeColumnsToContents()
    
    def remove_service(self, row):
        """حذف یک خدمت از لیست"""
        if 0 <= row < len(self.services):
            self.services.pop(row)
            self.update_services_table()
            self.calculate_total()
            self.services_changed.emit()
    
    def calculate_total(self):
        """محاسبه جمع کل خدمات (تومان)"""
        total_rials = sum(service['total_price'] for service in self.services)
        total_toman = total_rials / 10
        self.lbl_services_total.setText(f"💰 جمع کل خدمات: {total_toman:,.0f} تومان")
        return total_rials
    
    def set_services(self, services_data):
        """بارگذاری خدمات از دیتابیس"""
        self.services = []
        for service in services_data:
            service_item = {
                'service_id': service['service_id'],
                'service_code': service.get('service_code', ''),
                'service_name': service.get('service_name', ''),
                'category': service.get('category', ''),
                'quantity': service['quantity'],
                'unit_price': service['unit_price'],
                'total_price': service['total_price'],
                'description': service.get('description', '')
            }
            self.services.append(service_item)
        
        self.update_services_table()
        self.calculate_total()
    
    def showEvent(self, event):
        """وقتی تب نمایش داده می‌شود"""
        super().showEvent(event)
        print(f"🎯 تب خدمات نمایش داده شد. بارگذاری داده‌ها...")
        self.refresh_data()
    
    def refresh_data(self):
        """تازه‌سازی داده‌های تب"""
        print("🔃 در حال تازه‌سازی داده‌های تب خدمات...")
        self.load_categories()
        self.search_services()
    
    def get_services_data(self):
        """دریافت لیست خدمات"""
        return self.services
    
    def get_total(self):
        """دریافت جمع کل هزینه خدمات"""
        return sum(service['total_price'] for service in self.services)
    
    def open_service_manager(self):
        """باز کردن فرم مدیریت اجرت‌ها"""
        from ui.forms.service_fee_form import ServiceFeeForm
        
        dialog = ServiceFeeForm(self.data_manager, self)
        dialog.setWindowTitle("💰 مدیریت اجرت‌های استاندارد")
        
        # وصل کردن سیگنال به‌روزرسانی
        dialog.data_updated.connect(self.on_service_data_updated)
        
        result = dialog.exec()
        
        print(f"🗂️ فرم مدیریت اجرت‌ها بسته شد. نتیجه: {result}")
        self.refresh_data()
        
        return result
    
    def on_service_data_updated(self):
        """وقتی داده‌های اجرت‌ها به‌روز شد"""
        print("📢 داده‌های اجرت‌ها به‌روز شد. تازه‌سازی تب خدمات...")
        self.refresh_data()
    
    def force_refresh(self):
        """اجبار به تازه‌سازی داده‌ها"""
        print("🔄 درخواست تازه‌سازی اجباری داده‌ها...")
        self.load_categories()
        self.search_services()
        return True