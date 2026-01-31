from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QComboBox, QPushButton, QTableWidget, QTableWidgetItem,
    QMessageBox, QFormLayout, QDoubleSpinBox, QSpinBox,
    QTextEdit, QCheckBox, QDialogButtonBox
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor

class ServiceFeeForm(QDialog):
    """فرم مدیریت اجرت‌های استاندارد"""
    
    data_updated = Signal()  # سیگنال برای اطلاع‌رسانی تغییرات
    
    def __init__(self, data_manager, parent=None):
        super().__init__(parent)
        self.data_manager = data_manager
        self.setWindowTitle("💰 مدیریت اجرت‌های استاندارد")
        self.setMinimumSize(900, 700)
        self.setup_ui()
        self.load_data()
    
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # نوار جستجو
        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel("جستجو:"))
        
        self.txt_search = QLineEdit()
        self.txt_search.setPlaceholderText("نام خدمت، کد یا دسته‌بندی...")
        self.txt_search.textChanged.connect(self.on_search)
        search_layout.addWidget(self.txt_search)
        
        self.cmb_category = QComboBox()
        self.cmb_category.addItem("همه دسته‌بندی‌ها", "")
        self.cmb_category.currentTextChanged.connect(self.on_search)
        search_layout.addWidget(self.cmb_category)
        
        layout.addLayout(search_layout)
        
        # دکمه‌های عملیات
        btn_layout = QHBoxLayout()
        
        self.btn_add = QPushButton("➕ افزودن اجرت جدید")
        self.btn_add.clicked.connect(self.add_service)
        btn_layout.addWidget(self.btn_add)
        
        self.btn_edit = QPushButton("✏️ ویرایش")
        self.btn_edit.clicked.connect(self.edit_service)
        btn_layout.addWidget(self.btn_edit)
        
        self.btn_delete = QPushButton("🗑️ حذف")
        self.btn_delete.clicked.connect(self.delete_service)
        btn_layout.addWidget(self.btn_delete)
        
        btn_layout.addStretch()
        
        self.btn_refresh = QPushButton("🔄 به‌روزرسانی")
        self.btn_refresh.clicked.connect(self.load_data)
        btn_layout.addWidget(self.btn_refresh)
        
        self.btn_close = QPushButton("❌ بستن")
        self.btn_close.clicked.connect(self.reject)
        btn_layout.addWidget(self.btn_close)
        
        layout.addLayout(btn_layout)
        
        # جدول اجرت‌ها
        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels([
            "کد", "نام خدمت", "دسته‌بندی", "تعرفه استاندارد (ریال)", 
            "زمان تخمینی (ساعت)", "سطح دشواری", "وضعیت", "توضیحات"
        ])
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.cellDoubleClicked.connect(self.edit_service)
        
        layout.addWidget(self.table)
        
        self.lbl_total = QLabel("مجموع: ۰ اجرت")
        self.lbl_total.setStyleSheet("font-weight: bold; color: #3498db;")
        layout.addWidget(self.lbl_total)
        
        self.setLayout(layout)
    
    def load_data(self):
        """بارگذاری داده‌ها"""
        try:
            # بارگذاری دسته‌بندی‌ها
            categories = self.data_manager.service_fee.fetch_all(
                "SELECT DISTINCT category FROM ServiceFees ORDER BY category"
            )
            self.cmb_category.clear()
            self.cmb_category.addItem("همه دسته‌بندی‌ها", "")
            for cat in categories:
                self.cmb_category.addItem(cat['category'], cat['category'])
            
            # بارگذاری اجرت‌ها
            services = self.data_manager.service_fee.get_all_services(active_only=False)
            self.display_services(services)
            
        except Exception as e:
            QMessageBox.critical(self, "خطا", f"خطا در بارگذاری داده‌ها: {e}")
    
    def display_services(self, services):
        """نمایش اجرت‌ها در جدول"""
        self.table.setRowCount(len(services))
        
        for row, service in enumerate(services):
            self.table.setItem(row, 0, QTableWidgetItem(service.get('service_code', '')))
            self.table.setItem(row, 1, QTableWidgetItem(service.get('service_name', '')))
            self.table.setItem(row, 2, QTableWidgetItem(service.get('category', '')))
            
            fee = service.get('default_fee', 0)
            self.table.setItem(row, 3, QTableWidgetItem(f"{fee:,}"))
            
            hours = service.get('estimated_hours', 0)
            self.table.setItem(row, 4, QTableWidgetItem(str(hours)))
            
            difficulty = service.get('difficulty_level', 1)
            stars = "★" * difficulty
            self.table.setItem(row, 5, QTableWidgetItem(stars))
            
            is_active = service.get('is_active', 0)
            status = "✅ فعال" if is_active else "❌ غیرفعال"
            status_item = QTableWidgetItem(status)
            if not is_active:
                status_item.setForeground(QColor('#e74c3c'))
            self.table.setItem(row, 6, status_item)
            
            self.table.setItem(row, 7, QTableWidgetItem(service.get('description', '')))
        
        self.table.resizeColumnsToContents()
        self.lbl_total.setText(f"مجموع: {len(services)} اجرت")
    
    def on_search(self):
        """جستجوی اجرت‌ها"""
        search_text = self.txt_search.text()
        category = self.cmb_category.currentData()
        
        try:
            if search_text and len(search_text) >= 2:
                services = self.data_manager.service_fee.search_services(search_text)
            elif category:
                services = self.data_manager.service_fee.get_by_category(category)
            else:
                services = self.data_manager.service_fee.get_all_services(active_only=False)
            
            if category:
                services = [s for s in services if s.get('category') == category]
            
            self.display_services(services)
            
        except Exception as e:
            print(f"خطا در جستجو: {e}")
    
    def add_service(self):
        """افزودن اجرت جدید"""
        dialog = QDialog(self)
        dialog.setWindowTitle("➕ افزودن اجرت جدید")
        dialog.setMinimumWidth(500)
        
        layout = QFormLayout()
        
        # کد خدمت
        txt_code = QLineEdit()
        txt_code.setPlaceholderText("مثلاً: SVC-101")
        layout.addRow("کد خدمت:", txt_code)
        
        # نام خدمت
        txt_name = QLineEdit()
        txt_name.setPlaceholderText("نام کامل خدمت را وارد کنید")
        layout.addRow("نام خدمت:", txt_name)
        
        # دسته‌بندی - قابل ویرایش
        cmb_category = QComboBox()
        cmb_category.setEditable(True)  # قابل ویرایش
        cmb_category.setInsertPolicy(QComboBox.InsertAtTop)
        
        # بارگذاری دسته‌های موجود
        categories = self.data_manager.db.fetch_all(
            "SELECT DISTINCT category FROM ServiceFees ORDER BY category"
        )
        
        cmb_category.addItem("-- یک دسته انتخاب یا تایپ کنید --", "")
        if categories:
            for cat in categories:
                if cat['category']:
                    cmb_category.addItem(cat['category'], cat['category'])
        
        layout.addRow("دسته‌بندی:", cmb_category)
        
        # تعرفه استاندارد
        spn_fee = QDoubleSpinBox()
        spn_fee.setRange(0, 100000000)
        spn_fee.setValue(0)
        spn_fee.setSuffix(" ریال")
        layout.addRow("تعرفه استاندارد:", spn_fee)
        
        # زمان تخمینی
        spn_hours = QDoubleSpinBox()
        spn_hours.setRange(0.1, 100)
        spn_hours.setValue(1.0)
        spn_hours.setSingleStep(0.5)
        spn_hours.setSuffix(" ساعت")
        layout.addRow("زمان تخمینی:", spn_hours)
        
        # سطح دشواری
        spn_difficulty = QSpinBox()
        spn_difficulty.setRange(1, 5)
        spn_difficulty.setValue(1)
        layout.addRow("سطح دشواری (۱-۵):", spn_difficulty)
        
        # توضیحات
        txt_desc = QTextEdit()
        txt_desc.setMaximumHeight(100)
        txt_desc.setPlaceholderText("توضیحات اختیاری...")
        layout.addRow("توضیحات:", txt_desc)
        
        # دکمه‌ها
        btn_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        btn_box.accepted.connect(dialog.accept)
        btn_box.rejected.connect(dialog.reject)
        layout.addRow(btn_box)
        
        dialog.setLayout(layout)
        
        if dialog.exec() == QDialog.Accepted:
            # پردازش و ذخیره
            category_text = cmb_category.currentText().strip()
            
            # اعتبارسنجی
            if not txt_code.text().strip():
                QMessageBox.warning(self, "خطا", "کد خدمت را وارد کنید.")
                return
                
            if not txt_name.text().strip():
                QMessageBox.warning(self, "خطا", "نام خدمت را وارد کنید.")
                return
                
            if not category_text or category_text == "-- یک دسته انتخاب یا تایپ کنید --":
                QMessageBox.warning(self, "خطا", "دسته‌بندی را وارد کنید.")
                return
            
            # ذخیره سرویس جدید
            service_data = {
                'service_code': txt_code.text().strip(),
                'service_name': txt_name.text().strip(),
                'category': category_text,
                'default_fee': spn_fee.value(),
                'estimated_hours': spn_hours.value(),
                'difficulty_level': spn_difficulty.value(),
                'description': txt_desc.toPlainText().strip(),
                'is_active': 1
            }
            
            try:
                success = self.data_manager.service_fee.add_service(service_data)
                if success:
                    QMessageBox.information(self, "موفقیت", 
                        f"خدمت جدید با موفقیت اضافه شد.\n\n"
                        f"کد: {service_data['service_code']}\n"
                        f"نام: {service_data['service_name']}\n"
                        f"دسته: {service_data['category']}")
                    
                    # ارسال سیگنال به‌روزرسانی
                    self.data_updated.emit()
                    
                    self.load_data()
                else:
                    QMessageBox.warning(self, "خطا", "خطا در افزودن خدمت جدید.")
            except Exception as e:
                QMessageBox.critical(self, "خطا", f"خطا در ذخیره اجرت: {str(e)}")
    
    def edit_service(self, row=None):
        """ویرایش اجرت"""
        if row is None:
            selected_rows = self.table.selectionModel().selectedRows()
            if not selected_rows:
                QMessageBox.warning(self, "هشدار", "لطفاً یک اجرت را انتخاب کنید.")
                return
            row = selected_rows[0].row()
        
        service_code = self.table.item(row, 0).text()
        
        try:
            service = self.data_manager.service_fee.get_service_by_code(service_code)
            if not service:
                QMessageBox.warning(self, "هشدار", "اجرت مورد نظر یافت نشد.")
                return
            
            dialog = QDialog(self)
            dialog.setWindowTitle("✏️ ویرایش اجرت")
            dialog.setMinimumWidth(500)
            
            layout = QFormLayout()
            
            # کد خدمت
            txt_code = QLineEdit(service['service_code'])
            txt_code.setReadOnly(True)
            layout.addRow("کد خدمت:", txt_code)
            
            # نام خدمت
            txt_name = QLineEdit(service['service_name'])
            layout.addRow("نام خدمت:", txt_name)
            
            # دسته‌بندی - قابل ویرایش
            cmb_category = QComboBox()
            cmb_category.setEditable(True)
            cmb_category.setInsertPolicy(QComboBox.InsertAtTop)
            
            categories = self.data_manager.db.fetch_all(
                "SELECT DISTINCT category FROM ServiceFees ORDER BY category"
            )
            
            current_category = service.get('category', '')
            cmb_category.addItem("-- یک دسته انتخاب یا تایپ کنید --", "")
            if categories:
                for cat in categories:
                    if cat['category']:
                        cmb_category.addItem(cat['category'], cat['category'])
            
            cmb_category.setCurrentText(current_category)
            layout.addRow("دسته‌بندی:", cmb_category)
            
            # تعرفه استاندارد
            spn_fee = QDoubleSpinBox()
            spn_fee.setRange(0, 100000000)
            spn_fee.setValue(service.get('default_fee', 0))
            spn_fee.setSuffix(" ریال")
            layout.addRow("تعرفه استاندارد:", spn_fee)
            
            # زمان تخمینی
            spn_hours = QDoubleSpinBox()
            spn_hours.setRange(0.1, 100)
            spn_hours.setValue(service.get('estimated_hours', 1.0))
            spn_hours.setSingleStep(0.5)
            spn_hours.setSuffix(" ساعت")
            layout.addRow("زمان تخمینی:", spn_hours)
            
            # سطح دشواری
            spn_difficulty = QSpinBox()
            spn_difficulty.setRange(1, 5)
            spn_difficulty.setValue(service.get('difficulty_level', 1))
            layout.addRow("سطح دشواری (۱-۵):", spn_difficulty)
            
            # وضعیت
            chk_active = QCheckBox("فعال")
            chk_active.setChecked(bool(service.get('is_active', 1)))
            layout.addRow("وضعیت:", chk_active)
            
            # توضیحات
            txt_desc = QTextEdit()
            txt_desc.setPlainText(service.get('description', ''))
            txt_desc.setMaximumHeight(100)
            layout.addRow("توضیحات:", txt_desc)
            
            btn_box = QDialogButtonBox(
                QDialogButtonBox.Ok | QDialogButtonBox.Cancel
            )
            btn_box.accepted.connect(dialog.accept)
            btn_box.rejected.connect(dialog.reject)
            layout.addRow(btn_box)
            
            dialog.setLayout(layout)
            
            if dialog.exec() == QDialog.Accepted:
                service_data = {
                    'service_name': txt_name.text().strip(),
                    'category': cmb_category.currentText().strip(),
                    'default_fee': spn_fee.value(),
                    'estimated_hours': spn_hours.value(),
                    'difficulty_level': spn_difficulty.value(),
                    'description': txt_desc.toPlainText().strip(),
                    'is_active': 1 if chk_active.isChecked() else 0
                }
                
                success = self.data_manager.service_fee.update_service(service['id'], service_data)
                if success:
                    QMessageBox.information(self, "موفقیت", "اجرت با موفقیت ویرایش شد.")
                    
                    # ارسال سیگنال به‌روزرسانی
                    self.data_updated.emit()
                    
                    self.load_data()
                else:
                    QMessageBox.warning(self, "خطا", "خطا در ویرایش اجرت.")
                    
        except Exception as e:
            QMessageBox.critical(self, "خطا", f"خطا در ویرایش اجرت: {e}")
    
    def delete_service(self):
        """حذف اجرت"""
        selected_rows = self.table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "هشدار", "لطفاً حداقل یک اجرت را انتخاب کنید.")
            return
        
        reply = QMessageBox.question(
            self, 
            "تأیید حذف", 
            "آیا از حذف اجرت(های) انتخاب شده مطمئن هستید؟",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            for index in selected_rows:
                row = index.row()
                service_code = self.table.item(row, 0).text()
                
                try:
                    service = self.data_manager.service_fee.get_service_by_code(service_code)
                    if service:
                        update_data = {
                            'service_name': service['service_name'],
                            'category': service.get('category', ''),
                            'default_fee': service.get('default_fee', 0),
                            'estimated_hours': service.get('estimated_hours', 1.0),
                            'difficulty_level': service.get('difficulty_level', 1),
                            'description': service.get('description', ''),
                            'is_active': 0
                        }
                        
                        self.data_manager.service_fee.update_service(service['id'], update_data)
                
                except Exception as e:
                    print(f"خطا در حذف اجرت {service_code}: {e}")
            
            QMessageBox.information(self, "حذف", "اجرت(های) انتخاب شده غیرفعال شدند.")
            
            # ارسال سیگنال به‌روزرسانی
            self.data_updated.emit()
            
            self.load_data()