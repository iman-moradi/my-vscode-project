# در فایل account_dialog.py

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, 
    QLineEdit, QComboBox, QPushButton, QMessageBox, QLabel, QDoubleSpinBox
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
import jdatetime

class AccountDialog(QDialog):
    """دیالوگ افزودن/ویرایش حساب - نسخه اصلاح شده"""
    
    def __init__(self, data_manager, account_id=None, parent=None):
        super().__init__(parent)
        self.data_manager = data_manager
        self.account_id = account_id
        
        # 🔴 راست‌چین کردن کامل
        self.setLayoutDirection(Qt.RightToLeft)
        
        # تنظیمات پنجره
        self.setWindowTitle("➕ افزودن حساب جدید" if not account_id else "✏️ ویرایش حساب")
        self.resize(500, 500)
        
        # تنظیم استایل
        self.setup_styles()
        
        # ایجاد رابط کاربری
        self.init_ui()
        
        # اگر حساب ID داده شده، اطلاعات را بارگذاری کن
        if account_id:
            self.load_account_data()
    
    def setup_styles(self):
        """تنظیم استایل دیالوگ"""
        self.setStyleSheet("""
            QDialog {
                background-color: #000000;
            }
            
            QLabel {
                color: #ffffff;
                font-family: 'B Nazanin';
                font-size: 11pt;
            }
            
            QLineEdit, QComboBox, QDoubleSpinBox {
                background-color: #222222;
                border: 1px solid #333333;
                border-radius: 4px;
                padding: 8px;
                color: white;
                min-height: 35px;
                font-size: 11pt;
                font-family: 'B Nazanin';
            }
            
            QLineEdit:focus, QComboBox:focus, QDoubleSpinBox:focus {
                border: 2px solid #3498db;
            }
            
            QPushButton {
                padding: 10px 20px;
                border-radius: 5px;
                font-size: 11pt;
                font-weight: bold;
                min-width: 100px;
            }
            
            QPushButton#save_button {
                background-color: #27ae60;
                color: white;
            }
            
            QPushButton#save_button:hover {
                background-color: #219653;
            }
            
            QPushButton#cancel_button {
                background-color: #7f8c8d;
                color: white;
            }
            
            QPushButton#cancel_button:hover {
                background-color: #95a5a6;
            }
        """)
    
    def init_ui(self):
        """ایجاد رابط کاربری"""
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # 🔴 عنوان
        title_label = QLabel("🏦 حساب بانکی / نقدی")
        title_label.setStyleSheet("""
            QLabel {
                font-size: 14pt;
                font-weight: bold;
                color: #3498db;
                padding-bottom: 10px;
                border-bottom: 2px solid #3498db;
            }
        """)
        title_label.setAlignment(Qt.AlignRight)
        layout.addWidget(title_label)
        
        # فرم
        form_layout = QFormLayout()
        form_layout.setSpacing(10)
        form_layout.setLabelAlignment(Qt.AlignRight)
        
        # فیلد شماره حساب
        self.account_number_input = QLineEdit()
        self.account_number_input.setPlaceholderText("مثال: 1234-5678-9012-3456")
        form_layout.addRow("شماره حساب:", self.account_number_input)
        
        # فیلد نام حساب
        self.account_name_input = QLineEdit()
        self.account_name_input.setPlaceholderText("مثال: حساب جاری شرکت")
        form_layout.addRow("نام حساب:", self.account_name_input)
        
        # فیلد نوع حساب
        self.account_type_combo = QComboBox()
        self.account_type_combo.addItems([
            "جاری",
            "پس‌انداز", 
            "صندوق",
            "بانکی",
            "نقدی"
        ])
        form_layout.addRow("نوع حساب:", self.account_type_combo)
        
        # فیلد نام بانک
        self.bank_name_input = QLineEdit()
        self.bank_name_input.setPlaceholderText("مثال: ملی، ملت، صادرات...")
        form_layout.addRow("نام بانک:", self.bank_name_input)
        
        # فیلد نام صاحب حساب
        self.owner_name_input = QLineEdit()
        self.owner_name_input.setPlaceholderText("نام و نام خانوادگی صاحب حساب")
        form_layout.addRow("صاحب حساب:", self.owner_name_input)
        
        # فیلد موجودی اولیه
        self.initial_balance_input = QDoubleSpinBox()
        self.initial_balance_input.setRange(0, 1000000000000)  # تا 1000 میلیارد تومان
        self.initial_balance_input.setValue(0)
        self.initial_balance_input.setSuffix(" تومان")
        self.initial_balance_input.setButtonSymbols(QDoubleSpinBox.NoButtons)
        self.initial_balance_input.setDecimals(0)
        form_layout.addRow("موجودی اولیه:", self.initial_balance_input)
        
        # فیلد توضیحات
        self.description_input = QLineEdit()
        self.description_input.setPlaceholderText("توضیحات اختیاری...")
        form_layout.addRow("توضیحات:", self.description_input)
        
        layout.addLayout(form_layout)
        
        # 🔴 اطلاعات راهنما
        info_label = QLabel("💡 نکته: موجودی در دیتابیس به ریال ذخیره می‌شود (هر تومان = ۱۰ ریال)")
        info_label.setStyleSheet("""
            QLabel {
                color: #f39c12;
                font-size: 10pt;
                padding: 10px;
                background-color: #222;
                border-radius: 5px;
                border: 1px solid #444;
            }
        """)
        info_label.setAlignment(Qt.AlignRight)
        layout.addWidget(info_label)
        
        # دکمه‌ها
        button_layout = QHBoxLayout()
        
        self.save_button = QPushButton("💾 ذخیره")
        self.save_button.setObjectName("save_button")
        self.save_button.clicked.connect(self.save_account)
        
        self.cancel_button = QPushButton("❌ انصراف")
        self.cancel_button.setObjectName("cancel_button")
        self.cancel_button.clicked.connect(self.reject)
        
        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.cancel_button)
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def load_account_data(self):
        """بارگذاری اطلاعات حساب برای ویرایش"""
        try:
            if not self.account_id:
                return
            
            # استفاده از AccountManager برای دریافت اطلاعات حساب
            account = self.data_manager.account_manager.get_account_by_id(self.account_id)
            
            if account:
                # پر کردن فیلدها
                self.account_number_input.setText(account.get('account_number', ''))
                self.account_name_input.setText(account.get('account_name', ''))
                
                # تنظیم نوع حساب
                account_type = account.get('account_type', 'جاری')
                index = self.account_type_combo.findText(account_type)
                if index >= 0:
                    self.account_type_combo.setCurrentIndex(index)
                
                self.bank_name_input.setText(account.get('bank_name', ''))
                self.owner_name_input.setText(account.get('owner_name', ''))
                self.initial_balance_input.setValue(account.get('initial_balance_toman', 0))
                self.description_input.setText(account.get('description', ''))
                
                print(f"✅ اطلاعات حساب {self.account_id} بارگذاری شد")
            else:
                print(f"⚠️ حساب با شناسه {self.account_id} یافت نشد")
                
        except Exception as e:
            print(f"❌ خطا در بارگذاری اطلاعات حساب: {e}")
    
    def save_account(self):
        """ذخیره حساب"""
        try:
            # اعتبارسنجی داده‌ها
            account_number = self.account_number_input.text().strip()
            account_name = self.account_name_input.text().strip()
            
            if not account_number:
                QMessageBox.warning(self, "خطا", "⚠️ شماره حساب نمی‌تواند خالی باشد.")
                return
            
            if not account_name:
                QMessageBox.warning(self, "خطا", "⚠️ نام حساب نمی‌تواند خالی باشد.")
                return
            
            # اعتبارسنجی موجودی
            initial_balance = self.initial_balance_input.value()
            if initial_balance < 0:
                QMessageBox.warning(self, "خطا", "⚠️ موجودی اولیه نمی‌تواند منفی باشد.")
                return
            
            # آماده‌سازی داده‌ها
            data = {
                'account_number': account_number,
                'account_name': account_name,
                'account_type': self.account_type_combo.currentText(),
                'bank_name': self.bank_name_input.text().strip(),
                'owner_name': self.owner_name_input.text().strip(),
                'initial_balance': initial_balance,
                'description': self.description_input.text().strip()
            }
            
            print(f"🔄 در حال ذخیره حساب...")
            print(f"   داده‌ها: {data}")
            
            # ذخیره در دیتابیس
            if self.account_id:
                # ویرایش حساب موجود
                success, message = self.data_manager.account_manager.update_account(self.account_id, data)
                if success:
                    QMessageBox.information(self, "موفق", f"✅ {message}")
                    self.accept()
                else:
                    QMessageBox.critical(self, "خطا", f"❌ {message}")
            else:
                # افزودن حساب جدید
                success, message = self.data_manager.account_manager.add_account(data)
                if success:
                    QMessageBox.information(self, "موفق", f"✅ {message}")
                    self.accept()
                else:
                    QMessageBox.critical(self, "خطا", f"❌ {message}")
                
        except Exception as e:
            print(f"❌ خطا در ذخیره حساب: {e}")
            QMessageBox.critical(self, "خطا", f"❌ خطا در ذخیره حساب:\n\n{str(e)}")