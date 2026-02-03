
# user_management_form.py

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, 
                               QFormLayout, QLabel, QLineEdit, 
                               QComboBox, QPushButton, QTableWidget,
                               QTableWidgetItem, QHeaderView, QMessageBox,
                               QGroupBox, QCheckBox, QTabWidget,
                               QTextEdit, QDateEdit, QSpinBox)
from PySide6.QtCore import Qt, QDate
from PySide6.QtGui import QFont

class UserManagementForm(QWidget):
    """فرم مدیریت کاربران و سطوح دسترسی"""
    
    def __init__(self, data_manager, config_manager=None):
        super().__init__()
        self.data_manager = data_manager
        self.config_manager = config_manager
        self.current_user_id = None
        self.init_ui()
        self.apply_styles()
        self.load_users()
    
    def init_ui(self):
        """ایجاد رابط کاربری"""
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # ایجاد تب‌ها
        self.tab_widget = QTabWidget()
        
        # تب لیست کاربران
        self.users_tab = QWidget()
        self.setup_users_tab()
        self.tab_widget.addTab(self.users_tab, "👥 لیست کاربران")
        
        # تب افزودن کاربر
        self.add_user_tab = QWidget()
        self.setup_add_user_tab()
        self.tab_widget.addTab(self.add_user_tab, "➕ افزودن کاربر")
        
        # تب سطوح دسترسی
        self.roles_tab = QWidget()
        self.setup_roles_tab()
        self.tab_widget.addTab(self.roles_tab, "🔐 سطوح دسترسی")
        
        main_layout.addWidget(self.tab_widget)
        self.setLayout(main_layout)
    
    def setup_users_tab(self):
        """تنظیم تب لیست کاربران"""
        layout = QVBoxLayout()
        
        # نوار ابزار
        toolbar = QHBoxLayout()
        
        self.btn_refresh = QPushButton("🔄 بروزرسانی")
        self.btn_refresh.clicked.connect(self.load_users)
        
        self.btn_edit = QPushButton("✏️ ویرایش")
        self.btn_edit.clicked.connect(self.edit_user)
        
        self.btn_delete = QPushButton("🗑️ حذف")
        self.btn_delete.clicked.connect(self.delete_user)
        
        self.btn_change_password = QPushButton("🔑 تغییر رمز")
        self.btn_change_password.clicked.connect(self.change_password)
        
        toolbar.addWidget(self.btn_refresh)
        toolbar.addStretch()
        toolbar.addWidget(self.btn_edit)
        toolbar.addWidget(self.btn_delete)
        toolbar.addWidget(self.btn_change_password)
        
        layout.addLayout(toolbar)
        
        # جدول کاربران
        self.table_users = QTableWidget()
        self.table_users.setColumnCount(7)
        self.table_users.setHorizontalHeaderLabels([
            "شناسه", "نام کاربری", "نام کامل", "نقش", 
            "آخرین ورود", "تاریخ ایجاد", "وضعیت"
        ])
        
        # تنظیمات جدول
        self.table_users.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table_users.setSelectionBehavior(QTableWidget.SelectRows)
        self.table_users.setSelectionMode(QTableWidget.SingleSelection)
        self.table_users.setEditTriggers(QTableWidget.NoEditTriggers)
        
        layout.addWidget(self.table_users)
        
        # اطلاعات آماری
        stats_layout = QHBoxLayout()
        
        self.lbl_total_users = QLabel("تعداد کل کاربران: 0")
        self.lbl_active_users = QLabel("کاربران فعال: 0")
        self.lbl_admins = QLabel("مدیران: 0")
        self.lbl_operators = QLabel("اپراتورها: 0")
        
        stats_layout.addWidget(self.lbl_total_users)
        stats_layout.addWidget(self.lbl_active_users)
        stats_layout.addWidget(self.lbl_admins)
        stats_layout.addWidget(self.lbl_operators)
        stats_layout.addStretch()
        
        layout.addLayout(stats_layout)
        self.users_tab.setLayout(layout)
    
    def setup_add_user_tab(self):
        """تنظیم تب افزودن کاربر"""
        layout = QVBoxLayout()
        
        # فرم اطلاعات کاربر
        form_group = QGroupBox("اطلاعات کاربر جدید")
        form_layout = QFormLayout()
        
        self.txt_new_username = QLineEdit()
        self.txt_new_username.setPlaceholderText("نام کاربری (انگلیسی)")
        
        self.txt_new_password = QLineEdit()
        self.txt_new_password.setPlaceholderText("رمز عبور")
        self.txt_new_password.setEchoMode(QLineEdit.Password)
        
        self.txt_confirm_password = QLineEdit()
        self.txt_confirm_password.setPlaceholderText("تکرار رمز عبور")
        self.txt_confirm_password.setEchoMode(QLineEdit.Password)
        
        self.txt_full_name = QLineEdit()
        self.txt_full_name.setPlaceholderText("نام و نام خانوادگی")
        
        self.cmb_user_role = QComboBox()
        self.cmb_user_role.addItems([
            "مدیر سیستم",
            "مدیر مالی",
            "مدیر انبار", 
            "اپراتور پذیرش",
            "اپراتور تعمیرات",
            "کارمند",
            "مشاهده‌گر"
        ])
        
        self.chk_is_active = QCheckBox("کاربر فعال است")
        self.chk_is_active.setChecked(True)
        
        self.txt_email = QLineEdit()
        self.txt_email.setPlaceholderText("ایمیل")
        
        self.txt_phone = QLineEdit()
        self.txt_phone.setPlaceholderText("تلفن همراه")
        
        # محدودیت دسترسی
        access_group = QGroupBox("محدودیت‌های دسترسی")
        access_layout = QVBoxLayout()
        
        self.chk_access_persons = QCheckBox("دسترسی به مدیریت اشخاص")
        self.chk_access_persons.setChecked(True)
        
        self.chk_access_devices = QCheckBox("دسترسی به مدیریت دستگاه‌ها")
        self.chk_access_devices.setChecked(True)
        
        self.chk_access_receptions = QCheckBox("دسترسی به پذیرش")
        self.chk_access_receptions.setChecked(True)
        
        self.chk_access_repairs = QCheckBox("دسترسی به تعمیرات")
        self.chk_access_repairs.setChecked(True)
        
        self.chk_access_inventory = QCheckBox("دسترسی به انبار")
        self.chk_access_inventory.setChecked(True)
        
        self.chk_access_accounting = QCheckBox("دسترسی به حسابداری")
        self.chk_access_accounting.setChecked(False)
        
        self.chk_access_reports = QCheckBox("دسترسی به گزارش‌ها")
        self.chk_access_reports.setChecked(True)
        
        self.chk_access_settings = QCheckBox("دسترسی به تنظیمات")
        self.chk_access_settings.setChecked(False)
        
        access_layout.addWidget(self.chk_access_persons)
        access_layout.addWidget(self.chk_access_devices)
        access_layout.addWidget(self.chk_access_receptions)
        access_layout.addWidget(self.chk_access_repairs)
        access_layout.addWidget(self.chk_access_inventory)
        access_layout.addWidget(self.chk_access_accounting)
        access_layout.addWidget(self.chk_access_reports)
        access_layout.addWidget(self.chk_access_settings)
        access_group.setLayout(access_layout)
        
        form_layout.addRow("نام کاربری:", self.txt_new_username)
        form_layout.addRow("رمز عبور:", self.txt_new_password)
        form_layout.addRow("تکرار رمز:", self.txt_confirm_password)
        form_layout.addRow("نام کامل:", self.txt_full_name)
        form_layout.addRow("نقش:", self.cmb_user_role)
        form_layout.addRow("ایمیل:", self.txt_email)
        form_layout.addRow("تلفن:", self.txt_phone)
        form_layout.addRow("", self.chk_is_active)
        
        form_group.setLayout(form_layout)
        layout.addWidget(form_group)
        layout.addWidget(access_group)
        
        # دکمه‌های اقدام
        action_layout = QHBoxLayout()
        
        self.btn_add_user = QPushButton("➕ افزودن کاربر")
        self.btn_add_user.clicked.connect(self.add_user)
        
        self.btn_clear_form = QPushButton("🧹 پاک کردن فرم")
        self.btn_clear_form.clicked.connect(self.clear_form)
        
        action_layout.addWidget(self.btn_add_user)
        action_layout.addWidget(self.btn_clear_form)
        action_layout.addStretch()
        
        layout.addLayout(action_layout)
        layout.addStretch()
        
        self.add_user_tab.setLayout(layout)
    
    def setup_roles_tab(self):
        """تنظیم تب سطوح دسترسی"""
        layout = QVBoxLayout()
        
        # توضیحات
        desc_label = QLabel("""
        در این بخش می‌توانید سطوح دسترسی پیش‌فرض برای هر نقش را تعیین کنید.
        هر نقش مجموعه‌ای از مجوزها دارد که تعیین می‌کند کاربر چه کارهایی می‌تواند انجام دهد.
        """)
        desc_label.setWordWrap(True)
        layout.addWidget(desc_label)
        
        # جدول سطوح دسترسی
        self.table_roles = QTableWidget()
        self.table_roles.setColumnCount(10)
        self.table_roles.setHorizontalHeaderLabels([
            "نقش", "اشخاص", "دستگاه‌ها", "پذیرش", "تعمیرات", 
            "انبار", "حسابداری", "گزارش", "تنظیمات", "حذف"
        ])
        
        # تنظیمات جدول
        self.table_roles.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        
        # پر کردن جدول با داده‌های پیش‌فرض
        self.load_roles_data()
        
        layout.addWidget(self.table_roles)
        
        # دکمه ذخیره
        self.btn_save_roles = QPushButton("💾 ذخیره سطوح دسترسی")
        self.btn_save_roles.clicked.connect(self.save_roles)
        layout.addWidget(self.btn_save_roles, 0, Qt.AlignRight)
        
        self.roles_tab.setLayout(layout)
    
    def apply_styles(self):
        """اعمال استایل"""
        self.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 12pt;
                color: #3498db;
                border: 2px solid #3498db;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                padding: 0 10px;
            }
            QLineEdit, QComboBox {
                background-color: #222222;
                color: #ffffff;
                border: 1px solid #444444;
                border-radius: 3px;
                padding: 5px;
                min-height: 25px;
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
            QCheckBox {
                color: #ffffff;
            }
        """)
    
    def load_users(self):
        """بارگذاری لیست کاربران"""
        try:
            # TODO: دریافت کاربران از دیتابیس
            # نمونه داده‌های ساختگی برای تست
            users = [
                (1, "admin", "مدیر سیستم", "مدیر", "۱۴۰۳/۱۰/۰۵ ۱۲:۳۰", "۱۴۰۳/۰۱/۱۵", "فعال"),
                (2, "accountant", "حسابدار", "مدیر مالی", "۱۴۰۳/۱۰/۰۴ ۰۹:۱۵", "۱۴۰۳/۰۳/۲۰", "فعال"),
                (3, "inventory", "انباردار", "مدیر انبار", "۱۴۰۳/۱۰/۰۳ ۱۴:۲۰", "۱۴۰۳/۰۵/۱۰", "فعال"),
                (4, "operator1", "اپراتور ۱", "اپراتور", "۱۴۰۳/۱۰/۰۵ ۱۱:۰۰", "۱۴۰۳/۰۷/۲۲", "فعال"),
                (5, "viewer", "مشاهده‌گر", "مشاهده‌گر", "۱۴۰۳/۰۹/۲۸ ۱۰:۴۵", "۱۴۰۳/۰۸/۰۵", "غیرفعال"),
            ]
            
            self.table_users.setRowCount(len(users))
            
            for row, user in enumerate(users):
                for col, value in enumerate(user):
                    item = QTableWidgetItem(str(value))
                    item.setTextAlignment(Qt.AlignCenter)
                    
                    # رنگ‌بندی بر اساس وضعیت
                    if col == 6:  # ستون وضعیت
                        if value == "فعال":
                            item.setForeground(Qt.green)
                        else:
                            item.setForeground(Qt.red)
                    
                    self.table_users.setItem(row, col, item)
            
            # به‌روزرسانی آمار
            self.update_stats(len(users), 4, 1, 1)
            
        except Exception as e:
            QMessageBox.critical(self, "خطا", f"خطا در بارگذاری کاربران: {str(e)}")
    
    def update_stats(self, total, active, admins, operators):
        """به‌روزرسانی آمار کاربران"""
        self.lbl_total_users.setText(f"تعداد کل کاربران: {total}")
        self.lbl_active_users.setText(f"کاربران فعال: {active}")
        self.lbl_admins.setText(f"مدیران: {admins}")
        self.lbl_operators.setText(f"اپراتورها: {operators}")
    
    def load_roles_data(self):
        """بارگذاری داده‌های سطوح دسترسی"""
        roles_data = [
            ["مدیر سیستم", "✓", "✓", "✓", "✓", "✓", "✓", "✓", "✓", "✓"],
            ["مدیر مالی", "✓", "✓", "✓", "✓", "✓", "✓", "✓", "✗", "✗"],
            ["مدیر انبار", "✓", "✓", "✓", "✓", "✓", "✗", "✓", "✗", "✗"],
            ["اپراتور پذیرش", "✓", "✓", "✓", "✗", "✗", "✗", "✗", "✗", "✗"],
            ["اپراتور تعمیرات", "✓", "✓", "✓", "✓", "✗", "✗", "✗", "✗", "✗"],
            ["کارمند", "✗", "✗", "✗", "✗", "✗", "✗", "✗", "✗", "✗"],
            ["مشاهده‌گر", "✓", "✓", "✓", "✓", "✓", "✓", "✓", "✗", "✗"],
        ]
        
        self.table_roles.setRowCount(len(roles_data))
        
        for row, role in enumerate(roles_data):
            for col, value in enumerate(role):
                item = QTableWidgetItem(value)
                item.setTextAlignment(Qt.AlignCenter)
                
                # رنگ‌بندی
                if value == "✓":
                    item.setForeground(Qt.green)
                elif value == "✗":
                    item.setForeground(Qt.red)
                
                self.table_roles.setItem(row, col, item)
    
    def add_user(self):
        """افزودن کاربر جدید"""
        # اعتبارسنجی
        if not self.validate_user_form():
            return
        
        try:
            # TODO: ذخیره کاربر در دیتابیس
            username = self.txt_new_username.text().strip()
            full_name = self.txt_full_name.text().strip()
            role = self.cmb_user_role.currentText()
            
            QMessageBox.information(
                self, 
                "موفقیت", 
                f"کاربر '{username}' با نقش '{role}' اضافه شد."
            )
            
            # پاک کردن فرم
            self.clear_form()
            
            # بروزرسانی لیست
            self.load_users()
            
        except Exception as e:
            QMessageBox.critical(self, "خطا", f"خطا در افزودن کاربر: {str(e)}")
    
    def validate_user_form(self):
        """اعتبارسنجی فرم کاربر"""
        errors = []
        
        username = self.txt_new_username.text().strip()
        password = self.txt_new_password.text().strip()
        confirm = self.txt_confirm_password.text().strip()
        full_name = self.txt_full_name.text().strip()
        
        if not username:
            errors.append("نام کاربری الزامی است")
        elif len(username) < 3:
            errors.append("نام کاربری باید حداقل ۳ حرف باشد")
        
        if not password:
            errors.append("رمز عبور الزامی است")
        elif len(password) < 6:
            errors.append("رمز عبور باید حداقل ۶ حرف باشد")
        
        if password != confirm:
            errors.append("رمز عبور و تکرار آن مطابقت ندارند")
        
        if not full_name:
            errors.append("نام کامل الزامی است")
        
        if errors:
            QMessageBox.warning(self, "خطاهای ورودی", "\n".join(errors))
            return False
        
        return True
    
    def clear_form(self):
        """پاک کردن فرم"""
        self.txt_new_username.clear()
        self.txt_new_password.clear()
        self.txt_confirm_password.clear()
        self.txt_full_name.clear()
        self.txt_email.clear()
        self.txt_phone.clear()
        self.cmb_user_role.setCurrentIndex(0)
        self.chk_is_active.setChecked(True)
        
        # بازگردانی دسترسی‌ها به حالت پیش‌فرض
        self.chk_access_persons.setChecked(True)
        self.chk_access_devices.setChecked(True)
        self.chk_access_receptions.setChecked(True)
        self.chk_access_repairs.setChecked(True)
        self.chk_access_inventory.setChecked(True)
        self.chk_access_accounting.setChecked(False)
        self.chk_access_reports.setChecked(True)
        self.chk_access_settings.setChecked(False)
    
    def edit_user(self):
        """ویرایش کاربر انتخاب شده"""
        selected = self.table_users.currentRow()
        if selected < 0:
            QMessageBox.warning(self, "هشدار", "لطفاً یک کاربر را انتخاب کنید")
            return
        
        # TODO: باز کردن فرم ویرایش
        user_id = self.table_users.item(selected, 0).text()
        QMessageBox.information(self, "ویرایش", f"ویرایش کاربر با شناسه {user_id}")
    
    def delete_user(self):
        """حذف کاربر انتخاب شده"""
        selected = self.table_users.currentRow()
        if selected < 0:
            QMessageBox.warning(self, "هشدار", "لطفاً یک کاربر را انتخاب کنید")
            return
        
        username = self.table_users.item(selected, 1).text()
        
        reply = QMessageBox.question(
            self,
            "تأیید حذف",
            f"آیا مطمئن هستید که می‌خواهید کاربر '{username}' را حذف کنید؟",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # TODO: حذف از دیتابیس
            QMessageBox.information(self, "موفقیت", f"کاربر '{username}' حذف شد")
            self.load_users()
    
    def change_password(self):
        """تغییر رمز عبور کاربر"""
        selected = self.table_users.currentRow()
        if selected < 0:
            QMessageBox.warning(self, "هشدار", "لطفاً یک کاربر را انتخاب کنید")
            return
        
        # TODO: باز کردن دیالوگ تغییر رمز
        username = self.table_users.item(selected, 1).text()
        QMessageBox.information(self, "تغییر رمز", f"تغییر رمز برای کاربر '{username}'")
    
    def save_roles(self):
        """ذخیره سطوح دسترسی"""
        try:
            # TODO: ذخیره در دیتابیس
            QMessageBox.information(self, "موفقیت", "سطوح دسترسی با موفقیت ذخیره شدند")
        except Exception as e:
            QMessageBox.critical(self, "خطا", f"خطا در ذخیره سطوح دسترسی: {str(e)}")
    
    def load_settings(self, settings_data):
        """بارگذاری تنظیمات"""
        # این فرم تنظیمات خاصی ندارد
        pass
    
    def get_settings(self):
        """جمع‌آوری تنظیمات"""
        # این فرم تنظیمات خاصی ندارد
        return {}