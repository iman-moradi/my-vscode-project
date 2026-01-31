"""
دیالوگ انتقال وجه بین حساب‌ها - نسخه شمسی شده
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QComboBox,
    QPushButton, QMessageBox, QFormLayout, QDoubleSpinBox,
    QTextEdit, QGroupBox, QFrame
)
from PySide6.QtCore import Qt
from ui.widgets.jalali_date_widget import JalaliDateWidget
import jdatetime


class TransferDialog(QDialog):
    """دیالوگ انتقال وجه بین حساب‌ها - نسخه شمسی شده"""
    
    def __init__(self, data_manager, parent=None):
        super().__init__(parent)
        self.data_manager = data_manager
        self.transaction_manager = data_manager.transaction_manager
        
        # 🔴 **راست‌چین کردن کامل**
        self.setLayoutDirection(Qt.RightToLeft)
        
        self.setup_ui()
        self.setup_styles()
        self.load_accounts()
    
    def setup_ui(self):
        """ایجاد رابط کاربری"""
        self.setWindowTitle("🔄 انتقال وجه بین حساب‌ها")
        self.setMinimumWidth(650)
        
        layout = QVBoxLayout()
        
        # 🔴 **عنوان**
        title_label = QLabel("🔄 انتقال وجه")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("""
            QLabel {
                font-size: 16pt;
                font-weight: bold;
                color: #3498db;
                padding: 15px;
                background-color: #1a1a1a;
                border-radius: 8px;
                border: 2px solid #3498db;
            }
        """)
        layout.addWidget(title_label)
        
        # 🔴 **فرم انتقال**
        form_group = QGroupBox("📋 اطلاعات انتقال")
        form_layout = QFormLayout()
        
        # حساب مبدا
        self.from_account_combo = QComboBox()
        form_layout.addRow("🏦 حساب مبدا:", self.from_account_combo)
        
        # حساب مقصد
        self.to_account_combo = QComboBox()
        form_layout.addRow("🏦 حساب مقصد:", self.to_account_combo)
        
        # مبلغ انتقال (تومان)
        self.amount_input = QDoubleSpinBox()
        self.amount_input.setRange(0, 100000000000)  # تا 10 میلیارد تومان
        self.amount_input.setValue(0)
        self.amount_input.setSuffix(" تومان")
        self.amount_input.setDecimals(0)
        self.amount_input.setSingleStep(10000)
        form_layout.addRow("💰 مبلغ انتقال:", self.amount_input)
        
        # تاریخ انتقال (شمسی)
        self.date_widget = JalaliDateWidget()
        form_layout.addRow("📅 تاریخ انتقال:", self.date_widget)
        
        # توضیحات
        self.description_input = QTextEdit()
        self.description_input.setMaximumHeight(80)
        self.description_input.setPlaceholderText("شرح انتقال...")
        form_layout.addRow("📝 توضیحات:", self.description_input)
        
        form_group.setLayout(form_layout)
        layout.addWidget(form_group)
        
        # 🔴 **اطلاعات حساب‌ها**
        info_group = QGroupBox("💼 وضعیت حساب‌ها")
        info_layout = QVBoxLayout()
        
        self.balance_frame = QFrame()
        self.balance_frame.setFrameStyle(QFrame.Box)
        self.balance_frame.setStyleSheet("""
            QFrame {
                background-color: #1a1a1a;
                border: 2px solid #34495e;
                border-radius: 8px;
                padding: 15px;
            }
        """)
        
        balance_layout = QVBoxLayout()
        
        self.from_balance_label = QLabel("💼 حساب مبدا: در حال بارگذاری...")
        self.from_balance_label.setWordWrap(True)
        
        self.to_balance_label = QLabel("💼 حساب مقصد: در حال بارگذاری...")
        self.to_balance_label.setWordWrap(True)
        
        self.result_label = QLabel("📊 نتیجه انتقال: مبلغ را وارد کنید")
        self.result_label.setWordWrap(True)
        self.result_label.setStyleSheet("color: #f39c12; font-weight: bold;")
        
        balance_layout.addWidget(self.from_balance_label)
        balance_layout.addWidget(self.to_balance_label)
        balance_layout.addWidget(self.result_label)
        
        self.balance_frame.setLayout(balance_layout)
        info_layout.addWidget(self.balance_frame)
        
        info_group.setLayout(info_layout)
        layout.addWidget(info_group)
        
        # اتصال تغییرات
        self.from_account_combo.currentIndexChanged.connect(self.update_balances)
        self.to_account_combo.currentIndexChanged.connect(self.update_balances)
        self.amount_input.valueChanged.connect(self.update_balances)
        
        # 🔴 **دکمه‌ها**
        button_layout = QHBoxLayout()
        
        self.transfer_button = QPushButton("🔄 انجام انتقال")
        self.transfer_button.setProperty("class", "success_button")
        self.transfer_button.clicked.connect(self.do_transfer)
        
        self.preview_button = QPushButton("👁️ پیش نمایش")
        self.preview_button.setProperty("class", "info_button")
        self.preview_button.clicked.connect(self.preview_transfer)
        
        self.cancel_button = QPushButton("❌ انصراف")
        self.cancel_button.setProperty("class", "danger_button")
        self.cancel_button.clicked.connect(self.reject)
        
        button_layout.addStretch()
        button_layout.addWidget(self.cancel_button)
        button_layout.addWidget(self.preview_button)
        button_layout.addWidget(self.transfer_button)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def setup_styles(self):
        """تنظیم استایل"""
        self.setStyleSheet("""
            QDialog {
                background-color: #0a0a0a;
                color: #ffffff;
                font-family: 'B Nazanin';
                font-size: 11pt;
            }
            
            QGroupBox {
                font-weight: bold;
                border: 2px solid #34495e;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 15px;
                background-color: #1a1a1a;
            }
            
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top right;
                right: 15px;
                padding: 0 15px;
                color: #3498db;
                font-size: 12pt;
            }
            
            QLabel {
                color: #ecf0f1;
                font-size: 11pt;
                min-height: 25px;
            }
            
            QComboBox, QTextEdit, QDoubleSpinBox {
                background-color: #2c3e50;
                color: white;
                border: 1px solid #34495e;
                border-radius: 4px;
                padding: 10px;
                font-size: 11pt;
                min-height: 40px;
            }
            
            QComboBox:focus, QTextEdit:focus, QDoubleSpinBox:focus {
                border: 2px solid #3498db;
                background-color: #34495e;
            }
            
            QPushButton {
                padding: 12px 25px;
                border-radius: 5px;
                font-weight: bold;
                font-size: 11pt;
                min-width: 140px;
            }
            
            .success_button {
                background-color: #27ae60;
                color: white;
            }
            
            .success_button:hover {
                background-color: #219653;
            }
            
            .danger_button {
                background-color: #e74c3c;
                color: white;
            }
            
            .danger_button:hover {
                background-color: #c0392b;
            }
            
            .info_button {
                background-color: #3498db;
                color: white;
            }
            
            .info_button:hover {
                background-color: #2980b9;
            }
        """)
    
    def load_accounts(self):
        """بارگذاری لیست حساب‌ها"""
        try:
            query = """
            SELECT id, account_name, account_type, bank_name, current_balance 
            FROM Accounts 
            WHERE is_active = 1
            ORDER BY account_type, account_name
            """
            accounts = self.data_manager.db.fetch_all(query)
            
            self.from_account_combo.clear()
            self.to_account_combo.clear()
            
            self.from_account_combo.addItem("-- انتخاب حساب مبدا --", None)
            self.to_account_combo.addItem("-- انتخاب حساب مقصد --", None)
            
            for account in accounts:
                # تبدیل موجودی از ریال به تومان برای نمایش
                balance_toman = float(account.get('current_balance', 0)) / 10
                display_text = f"{account['account_name']} ({account['account_type']}) - موجودی: {balance_toman:,.0f} تومان"
                
                self.from_account_combo.addItem(display_text, account['id'])
                self.to_account_combo.addItem(display_text, account['id'])
            
            if accounts:
                self.from_account_combo.setCurrentIndex(1)  # اولین حساب واقعی
                if len(accounts) > 1:
                    self.to_account_combo.setCurrentIndex(2)  # دومین حساب
                self.update_balances()
                
        except Exception as e:
            print(f"⚠️ خطا در بارگذاری حساب‌ها: {e}")
    
    def update_balances(self):
        """به‌روزرسانی نمایش موجودی حساب‌ها"""
        try:
            from_id = self.from_account_combo.currentData()
            to_id = self.to_account_combo.currentData()
            amount = self.amount_input.value()
            
            from_info = ""
            to_info = ""
            result_info = ""
            
            if from_id:
                query = "SELECT account_name, current_balance FROM Accounts WHERE id = ?"
                from_account = self.data_manager.db.fetch_one(query, (from_id,))
                if from_account:
                    balance_toman = float(from_account.get('current_balance', 0)) / 10
                    new_balance = balance_toman - amount
                    
                    from_info = f"""
                    <b>💼 حساب مبدا:</b> {from_account['account_name']}<br>
                    • موجودی فعلی: <span style='color:#27ae60'>{balance_toman:,.0f} تومان</span><br>
                    • موجودی پس از انتقال: <span style='color:#{'e74c3c' if new_balance < 0 else '27ae60'}'>{new_balance:,.0f} تومان</span>
                    """
                    
                    if new_balance < 0:
                        result_info = f"⚠️ <span style='color:#e74c3c'>موجودی حساب مبدا کافی نیست!</span>"
                    else:
                        result_info = f"✅ <span style='color:#27ae60'>انتقال امکان‌پذیر است</span>"
            
            if to_id:
                query = "SELECT account_name, current_balance FROM Accounts WHERE id = ?"
                to_account = self.data_manager.db.fetch_one(query, (to_id,))
                if to_account:
                    balance_toman = float(to_account.get('current_balance', 0)) / 10
                    new_balance = balance_toman + amount
                    
                    to_info = f"""
                    <b>💼 حساب مقصد:</b> {to_account['account_name']}<br>
                    • موجودی فعلی: <span style='color:#27ae60'>{balance_toman:,.0f} تومان</span><br>
                    • موجودی پس از انتقال: <span style='color:#27ae60'>{new_balance:,.0f} تومان</span>
                    """
            
            if from_id and to_id and from_id == to_id:
                result_info = "⚠️ <span style='color:#e74c3c'>حساب مبدا و مقصد نمی‌توانند یکسان باشند!</span>"
            
            self.from_balance_label.setText(from_info)
            self.to_balance_label.setText(to_info)
            self.result_label.setText(result_info)
            
        except Exception as e:
            print(f"⚠️ خطا در بروزرسانی موجودی: {e}")
    
    def validate_transfer(self):
        """اعتبارسنجی انتقال"""
        amount = self.amount_input.value()
        if amount <= 0:
            return False, "مبلغ انتقال باید بزرگتر از صفر باشد"
        
        from_account_id = self.from_account_combo.currentData()
        to_account_id = self.to_account_combo.currentData()
        
        if not from_account_id or not to_account_id:
            return False, "لطفاً هر دو حساب را انتخاب کنید"
        
        if from_account_id == to_account_id:
            return False, "حساب مبدا و مقصد نمی‌توانند یکسان باشند"
        
        # بررسی موجودی کافی
        try:
            query = "SELECT current_balance FROM Accounts WHERE id = ?"
            from_balance = self.data_manager.db.fetch_one(query, (from_account_id,))
            
            if from_balance:
                balance_toman = float(from_balance.get('current_balance', 0)) / 10
                if balance_toman < amount:
                    return False, f"موجودی حساب مبدا کافی نیست\n\nموجودی قابل برداشت: {balance_toman:,.0f} تومان\nمبلغ درخواستی: {amount:,.0f} تومان"
        except Exception as e:
            print(f"⚠️ خطا در بررسی موجودی: {e}")
        
        return True, "اعتبارسنجی موفق"
    
    def preview_transfer(self):
        """پیش نمایش انتقال"""
        valid, message = self.validate_transfer()
        if not valid:
            QMessageBox.warning(self, "خطا", message)
            return
        
        amount = self.amount_input.value()
        from_account = self.from_account_combo.currentText()
        to_account = self.to_account_combo.currentText()
        jalali_date = self.date_widget.get_date_string()
        description = self.description_input.toPlainText().strip()
        
        preview_text = f"""
        <b>🔍 پیش نمایش انتقال وجه</b>
        <hr>
        <b>🏦 حساب مبدا:</b> {from_account}<br>
        <b>🏦 حساب مقصد:</b> {to_account}<br>
        <b>💰 مبلغ انتقال:</b> <span style='color:#27ae60'>{amount:,.0f} تومان</span><br>
        <b>📅 تاریخ انتقال:</b> {jalali_date}<br>
        <b>📝 شرح:</b> {description[:100]}...
        <hr>
        <span style='color:#f39c12'>⚠️ لطفاً اطلاعات را بررسی کنید.</span>
        """
        
        QMessageBox.information(self, "پیش نمایش انتقال", preview_text)
    
    def do_transfer(self):
        """انجام عملیات انتقال با استفاده از TransactionManager"""
        try:
            # اعتبارسنجی
            valid, message = self.validate_transfer()
            if not valid:
                QMessageBox.warning(self, "خطا", message)
                return
            
            # جمع‌آوری اطلاعات
            amount = self.amount_input.value()
            from_account_id = self.from_account_combo.currentData()
            to_account_id = self.to_account_combo.currentData()
            description = self.description_input.toPlainText().strip()
            
            # دریافت تاریخ شمسی و تبدیل به میلادی
            jalali_date = self.date_widget.get_date()
            jalali_date_str = jalali_date.strftime("%Y/%m/%d")
            
            # تبدیل تاریخ شمسی به میلادی برای ذخیره در دیتابیس
            gregorian_date = self.data_manager.db.jalali_to_gregorian(jalali_date_str)
            if not gregorian_date:
                QMessageBox.warning(self, "خطا", "تاریخ نامعتبر است.")
                return
            
            # تأیید نهایی
            reply = QMessageBox.question(
                self, "تأیید انتقال",
                f"<b>آیا از انتقال وجه اطمینان دارید؟</b><br><br>"
                f"💰 مبلغ: <span style='color:#27ae60'>{amount:,.0f} تومان</span><br>"
                f"🏦 از حساب: {self.from_account_combo.currentText()}<br>"
                f"🏦 به حساب: {self.to_account_combo.currentText()}<br>"
                f"📅 تاریخ: {jalali_date_str}",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply != QMessageBox.Yes:
                return
            
            # آماده‌سازی داده‌ها برای TransactionManager
            transaction_data = {
                'transaction_type': 'انتقال',
                'from_account_id': from_account_id,
                'to_account_id': to_account_id,
                'amount': amount,  # تومان
                'description': description,
                'transaction_date': gregorian_date
            }
            
            print(f"🔄 در حال انجام انتقال...")
            print(f"   از حساب: {from_account_id}")
            print(f"   به حساب: {to_account_id}")
            print(f"   مبلغ: {amount:,.0f} تومان")
            print(f"   تاریخ شمسی: {jalali_date_str}")
            print(f"   تاریخ میلادی: {gregorian_date}")
            
            # انجام انتقال با استفاده از TransactionManager
            success, message = self.transaction_manager.create_transaction(transaction_data)
            
            if success:
                QMessageBox.information(
                    self, "موفق", 
                    f"✅ انتقال وجه با موفقیت انجام شد.\n\n"
                    f"💰 مبلغ: {amount:,.0f} تومان\n"
                    f"🏦 از حساب: {self.from_account_combo.currentText()}\n"
                    f"🏦 به حساب: {self.to_account_combo.currentText()}\n"
                    f"📅 تاریخ: {jalali_date_str}"
                )
                self.accept()
            else:
                QMessageBox.critical(self, "خطا", f"❌ {message}")
            
        except Exception as e:
            print(f"❌ خطا در انجام انتقال: {e}")
            import traceback
            traceback.print_exc()
            QMessageBox.critical(self, "خطا", f"❌ خطا در انجام انتقال:\n\n{str(e)}")