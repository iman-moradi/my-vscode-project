"""
دیالوگ ثبت تراکنش مالی - نسخه شمسی شده با JalaliDateWidget
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QComboBox,
    QPushButton, QMessageBox, QFormLayout, QDoubleSpinBox,
    QTextEdit, QRadioButton, QButtonGroup, QGroupBox, QLineEdit,
    QFrame
)
from PySide6.QtCore import Qt
from utils.jalali_date_widget import JalaliDateWidget
import jdatetime
from datetime import datetime


class TransactionDialog(QDialog):
    """دیالوگ ثبت تراکنش مالی - نسخه شمسی شده"""
    
    def __init__(self, data_manager, transaction_type=None, transaction_id=None, parent=None):
        super().__init__(parent)
        self.data_manager = data_manager
        self.transaction_manager = data_manager.transaction_manager
        self.transaction_type = transaction_type
        self.transaction_id = transaction_id
        self.is_edit = transaction_id is not None
        
        # 🔴 **راست‌چین کردن کامل**
        self.setLayoutDirection(Qt.RightToLeft)
        
        self.setup_ui()
        self.setup_styles()
        self.load_accounts()
        
        # اگر نوع تراکنش مشخص شده، تنظیم کن
        if transaction_type:
            self.set_transaction_type(transaction_type)
        
        # اگر در حالت ویرایش هستیم، اطلاعات را بارگذاری کن
        if self.is_edit:
            self.load_transaction_data()
    
    def setup_ui(self):
        """ایجاد رابط کاربری"""
        title = "📝 ثبت تراکنش جدید" if not self.is_edit else "✏️ ویرایش تراکنش"
        self.setWindowTitle(title)
        self.setMinimumWidth(700)
        
        layout = QVBoxLayout()
        
        # 🔴 **نوع تراکنش (فقط در حالت افزودن جدید قابل تغییر است)**
        if not self.is_edit:
            type_group = QGroupBox("📊 نوع تراکنش")
            type_layout = QHBoxLayout()
            
            self.receive_radio = QRadioButton("💰 دریافت")
            self.pay_radio = QRadioButton("💸 پرداخت")
            self.transfer_radio = QRadioButton("🔄 انتقال")
            
            self.type_group = QButtonGroup()
            self.type_group.addButton(self.receive_radio, 1)
            self.type_group.addButton(self.pay_radio, 2)
            self.type_group.addButton(self.transfer_radio, 3)
            
            # تنظیم نوع پیش‌فرض یا بر اساس ورودی
            if self.transaction_type == "دریافت":
                self.receive_radio.setChecked(True)
            elif self.transaction_type == "پرداخت":
                self.pay_radio.setChecked(True)
            elif self.transaction_type == "انتقال":
                self.transfer_radio.setChecked(True)
            else:
                self.receive_radio.setChecked(True)
            
            type_layout.addWidget(self.receive_radio)
            type_layout.addWidget(self.pay_radio)
            type_layout.addWidget(self.transfer_radio)
            type_layout.addStretch()
            
            type_group.setLayout(type_layout)
            layout.addWidget(type_group)
        
        # 🔴 **فرم اطلاعات**
        form_group = QGroupBox("📋 اطلاعات تراکنش")
        form_layout = QFormLayout()
        
        # تاریخ تراکنش (شمسی)
        self.date_widget = JalaliDateWidget()
        form_layout.addRow("📅 تاریخ تراکنش:", self.date_widget)
        
        # حساب مبدا/مقصد
        self.account_combo = QComboBox()
        form_layout.addRow("🏦 حساب:", self.account_combo)
        
        # حساب مقصد (برای انتقال)
        self.to_account_combo = QComboBox()
        self.to_account_combo.setVisible(False)
        form_layout.addRow("🏦 حساب مقصد:", self.to_account_combo)
        
        # مبلغ (تومان)
        self.amount_input = QDoubleSpinBox()
        self.amount_input.setRange(0, 100000000000)  # تا 10 میلیارد تومان
        self.amount_input.setValue(0)
        self.amount_input.setSuffix(" تومان")
        self.amount_input.setDecimals(0)
        self.amount_input.setSingleStep(10000)
        form_layout.addRow("💵 مبلغ (تومان):", self.amount_input)
        
        # دسته‌بندی
        self.category_combo = QComboBox()
        self.category_combo.addItems([
            "عمومی",
            "فروش خدمات",
            "فروش قطعات",
            "خرید قطعات",
            "حقوق و دستمزد",
            "اجاره و قبوض",
            "تعمیرات و نگهداری",
            "حمل و نقل",
            "تبلیغات",
            "سایر"
        ])
        form_layout.addRow("🏷️ دسته‌بندی:", self.category_combo)
        
        # توضیحات
        self.description_input = QTextEdit()
        self.description_input.setMaximumHeight(100)
        self.description_input.setPlaceholderText("شرح کامل تراکنش...")
        form_layout.addRow("📝 توضیحات:", self.description_input)
        
        # مرجع (اختیاری)
        self.reference_input = QLineEdit()
        self.reference_input.setPlaceholderText("شماره فاکتور، رسید، یا کد مرجع")
        form_layout.addRow("🏷️ مرجع (اختیاری):", self.reference_input)
        
        form_group.setLayout(form_layout)
        layout.addWidget(form_group)
        
        # 🔴 **اطلاعات حساب‌ها**
        info_group = QGroupBox("💼 اطلاعات حساب‌ها")
        info_layout = QVBoxLayout()
        
        self.account_info_label = QLabel("اطلاعات حساب انتخاب‌شده:")
        self.account_info_label.setWordWrap(True)
        self.account_info_label.setStyleSheet("""
            QLabel {
                color: #bdc3c7;
                font-size: 10pt;
                padding: 8px;
                background-color: #2c3e50;
                border-radius: 5px;
            }
        """)
        
        info_layout.addWidget(self.account_info_label)
        info_group.setLayout(info_layout)
        layout.addWidget(info_group)
        
        # اتصال تغییر حساب‌ها
        self.account_combo.currentIndexChanged.connect(self.update_account_info)
        self.to_account_combo.currentIndexChanged.connect(self.update_account_info)
        self.amount_input.valueChanged.connect(self.update_account_info)
        
        # اتصال تغییر نوع تراکنش (فقط در حالت افزودن)
        if not self.is_edit:
            self.receive_radio.toggled.connect(self.on_transaction_type_changed)
            self.pay_radio.toggled.connect(self.on_transaction_type_changed)
            self.transfer_radio.toggled.connect(self.on_transaction_type_changed)
        
        # 🔴 **دکمه‌ها**
        button_layout = QHBoxLayout()
        
        btn_text = "💾 ذخیره تراکنش" if not self.is_edit else "💾 بروزرسانی"
        self.save_button = QPushButton(btn_text)
        self.save_button.setProperty("class", "success_button")
        self.save_button.clicked.connect(self.save_transaction)
        
        self.cancel_button = QPushButton("❌ انصراف")
        self.cancel_button.setProperty("class", "danger_button")
        self.cancel_button.clicked.connect(self.reject)
        
        button_layout.addStretch()
        button_layout.addWidget(self.cancel_button)
        button_layout.addWidget(self.save_button)
        
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
            
            QComboBox, QTextEdit, QDoubleSpinBox, QLineEdit {
                background-color: #2c3e50;
                color: white;
                border: 1px solid #34495e;
                border-radius: 4px;
                padding: 10px;
                font-size: 11pt;
                min-height: 40px;
            }
            
            QComboBox:focus, QTextEdit:focus, QDoubleSpinBox:focus, QLineEdit:focus {
                border: 2px solid #3498db;
                background-color: #34495e;
            }
            
            QRadioButton {
                color: white;
                padding: 8px;
                font-size: 11pt;
                font-weight: bold;
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
            
            self.account_combo.clear()
            self.to_account_combo.clear()
            
            self.account_combo.addItem("-- انتخاب حساب --", None)
            self.to_account_combo.addItem("-- انتخاب حساب --", None)
            
            for account in accounts:
                # تبدیل موجودی از ریال به تومان برای نمایش
                balance_toman = float(account.get('current_balance', 0)) / 10
                display_text = f"{account['account_name']} ({account['account_type']}) - موجودی: {balance_toman:,.0f} تومان"
                
                self.account_combo.addItem(display_text, account['id'])
                self.to_account_combo.addItem(display_text, account['id'])
            
            if accounts:
                self.account_combo.setCurrentIndex(1)  # اولین حساب واقعی
                self.to_account_combo.setCurrentIndex(1)
                self.update_account_info()
                
        except Exception as e:
            print(f"⚠️ خطا در بارگذاری حساب‌ها: {e}")
    
    def set_transaction_type(self, trans_type):
        """تنظیم نوع تراکنش"""
        if not self.is_edit:  # فقط در حالت افزودن قابل تغییر
            if trans_type == "دریافت":
                self.receive_radio.setChecked(True)
            elif trans_type == "پرداخت":
                self.pay_radio.setChecked(True)
            elif trans_type == "انتقال":
                self.transfer_radio.setChecked(True)
            self.on_transaction_type_changed()
    
    def on_transaction_type_changed(self):
        """هنگام تغییر نوع تراکنش"""
        if self.is_edit:
            return  # در حالت ویرایش قابل تغییر نیست
        
        is_transfer = self.transfer_radio.isChecked()
        
        # نمایش/مخفی کردن حساب مقصد
        self.to_account_combo.setVisible(is_transfer)
        
        # به‌روزرسانی لیبل حساب
        for i in range(self.layout().count()):
            widget = self.layout().itemAt(i).widget()
            if isinstance(widget, QGroupBox) and widget.title() == "📋 اطلاعات تراکنش":
                for j in range(widget.layout().count()):
                    if isinstance(widget.layout().itemAt(j), QFormLayout):
                        form_layout = widget.layout().itemAt(j)
                        for k in range(form_layout.rowCount()):
                            item = form_layout.itemAt(k, QFormLayout.LabelRole)
                            if item and item.widget():
                                label = item.widget()
                                if label.text().startswith("🏦 حساب:"):
                                    if self.receive_radio.isChecked():
                                        label.setText("🏦 حساب مقصد (دریافت):")
                                    elif self.pay_radio.isChecked():
                                        label.setText("🏦 حساب مبدا (پرداخت):")
                                    else:  # انتقال
                                        label.setText("🏦 حساب مبدا (انتقال):")
                                    break
        
        self.update_account_info()
    
    def update_account_info(self):
        """به‌روزرسانی اطلاعات حساب‌ها"""
        try:
            trans_type = self.get_transaction_type()
            account_id = self.account_combo.currentData()
            to_account_id = self.to_account_combo.currentData()
            amount = self.amount_input.value()
            
            info_text = ""
            
            if trans_type == "دریافت" and account_id:
                query = "SELECT account_name, account_type, bank_name, current_balance FROM Accounts WHERE id = ?"
                account = self.data_manager.db.fetch_one(query, (account_id,))
                if account:
                    balance_toman = float(account.get('current_balance', 0)) / 10
                    info_text = f"""
                    <b>💼 حساب مقصد (برای دریافت):</b><br>
                    • نام: {account['account_name']}<br>
                    • نوع: {account['account_type']}<br>
                    • موجودی فعلی: <span style='color:#27ae60'>{balance_toman:,.0f} تومان</span><br>
                    • پس از این تراکنش: <span style='color:#27ae60'>{balance_toman + amount:,.0f} تومان</span>
                    """
            
            elif trans_type == "پرداخت" and account_id:
                query = "SELECT account_name, account_type, bank_name, current_balance FROM Accounts WHERE id = ?"
                account = self.data_manager.db.fetch_one(query, (account_id,))
                if account:
                    balance_toman = float(account.get('current_balance', 0)) / 10
                    new_balance = balance_toman - amount
                    
                    info_text = f"""
                    <b>💼 حساب مبدا (برای پرداخت):</b><br>
                    • نام: {account['account_name']}<br>
                    • نوع: {account['account_type']}<br>
                    • موجودی فعلی: <span style='color:#27ae60'>{balance_toman:,.0f} تومان</span><br>
                    • پس از این تراکنش: <span style='color:#{'e74c3c' if new_balance < 0 else '27ae60'}'>{new_balance:,.0f} تومان</span>
                    """
            
            elif trans_type == "انتقال" and account_id and to_account_id:
                # حساب مبدا
                query = "SELECT account_name, current_balance FROM Accounts WHERE id = ?"
                from_account = self.data_manager.db.fetch_one(query, (account_id,))
                
                # حساب مقصد
                to_account = self.data_manager.db.fetch_one(query, (to_account_id,))
                
                if from_account and to_account:
                    from_balance = float(from_account.get('current_balance', 0)) / 10
                    to_balance = float(to_account.get('current_balance', 0)) / 10
                    
                    new_from_balance = from_balance - amount
                    new_to_balance = to_balance + amount
                    
                    info_text = f"""
                    <b>💼 حساب مبدا (انتقال):</b><br>
                    • نام: {from_account['account_name']}<br>
                    • موجودی فعلی: <span style='color:#27ae60'>{from_balance:,.0f} تومان</span><br>
                    • پس از انتقال: <span style='color:#{'e74c3c' if new_from_balance < 0 else '27ae60'}'>{new_from_balance:,.0f} تومان</span><br><br>
                    
                    <b>💼 حساب مقصد (انتقال):</b><br>
                    • نام: {to_account['account_name']}<br>
                    • موجودی فعلی: <span style='color:#27ae60'>{to_balance:,.0f} تومان</span><br>
                    • پس از انتقال: <span style='color:#27ae60'>{new_to_balance:,.0f} تومان</span>
                    """
            
            self.account_info_label.setText(info_text)
            
        except Exception as e:
            print(f"⚠️ خطا در به‌روزرسانی اطلاعات حساب: {e}")
    
    def get_transaction_type(self):
        """تعیین نوع تراکنش"""
        if self.is_edit and self.transaction_type:
            return self.transaction_type
        
        if self.receive_radio.isChecked():
            return "دریافت"
        elif self.pay_radio.isChecked():
            return "پرداخت"
        else:
            return "انتقال"
    
    def load_transaction_data(self):
        """بارگذاری اطلاعات تراکنش در حالت ویرایش"""
        try:
            if not self.transaction_id:
                return
            
            # استفاده از TransactionManager
            transaction = self.transaction_manager.get_transaction_by_id(self.transaction_id)
            
            if transaction:
                # تنظیم نوع تراکنش
                self.transaction_type = transaction.get('transaction_type', 'دریافت')
                
                # تنظیم تاریخ شمسی
                trans_date = transaction.get('transaction_date', '')
                if trans_date:
                    # تاریخ میلادی را به شمسی تبدیل کن
                    jalali_date_str = self.data_manager.db.gregorian_to_jalali(trans_date)
                    # رشته تاریخ شمسی را به شیء jdatetime تبدیل کنیم
                    try:
                        # فرض می‌کنیم فرمت "1403/12/25" است
                        year, month, day = map(int, jalali_date_str.split('/'))
                        jalali_date = jdatetime.date(year, month, day)
                        self.date_widget.set_date(jalali_date)
                    except:
                        print(f"⚠️ خطا در تبدیل تاریخ: {jalali_date_str}")
                
                # تنظیم حساب‌ها
                from_account_id = transaction.get('from_account_id')
                to_account_id = transaction.get('to_account_id')
                
                if self.transaction_type == "دریافت":
                    if to_account_id:
                        index = self.account_combo.findData(to_account_id)
                        if index >= 0:
                            self.account_combo.setCurrentIndex(index)
                elif self.transaction_type == "پرداخت":
                    if from_account_id:
                        index = self.account_combo.findData(from_account_id)
                        if index >= 0:
                            self.account_combo.setCurrentIndex(index)
                else:  # انتقال
                    if from_account_id:
                        index = self.account_combo.findData(from_account_id)
                        if index >= 0:
                            self.account_combo.setCurrentIndex(index)
                    if to_account_id:
                        index = self.to_account_combo.findData(to_account_id)
                        if index >= 0:
                            self.to_account_combo.setCurrentIndex(index)
                    self.to_account_combo.setVisible(True)
                
                # تنظیم مبلغ (تومان)
                amount = transaction.get('amount_toman', 0)
                self.amount_input.setValue(amount)
                
                # تنظیم توضیحات
                self.description_input.setPlainText(transaction.get('description', ''))
                
                # تنظیم مرجع
                reference_id = transaction.get('reference_id', '')
                if reference_id:
                    self.reference_input.setText(str(reference_id))
                
                print(f"✅ اطلاعات تراکنش {self.transaction_id} بارگذاری شد")
            else:
                print(f"⚠️ تراکنش با شناسه {self.transaction_id} یافت نشد")
                
        except Exception as e:
            print(f"❌ خطا در بارگذاری اطلاعات تراکنش: {e}")
            import traceback
            traceback.print_exc()
    
    def validate_inputs(self):
        """اعتبارسنجی ورودی‌ها"""
        # بررسی مبلغ
        amount = self.amount_input.value()
        if amount <= 0:
            return False, "مبلغ باید بزرگتر از صفر باشد"
        
        # بررسی حساب‌ها
        trans_type = self.get_transaction_type()
        account_id = self.account_combo.currentData()
        
        if trans_type == "دریافت":
            if not account_id:
                return False, "حساب مقصد را انتخاب کنید"
        
        elif trans_type == "پرداخت":
            if not account_id:
                return False, "حساب مبدا را انتخاب کنید"
            
            # بررسی موجودی کافی
            query = "SELECT current_balance FROM Accounts WHERE id = ?"
            account = self.data_manager.db.fetch_one(query, (account_id,))
            if account:
                balance_toman = float(account.get('current_balance', 0)) / 10
                if balance_toman < amount:
                    return False, f"موجودی حساب کافی نیست (موجودی: {balance_toman:,.0f} تومان)"
        
        elif trans_type == "انتقال":
            to_account_id = self.to_account_combo.currentData()
            
            if not account_id or not to_account_id:
                return False, "هر دو حساب مبدا و مقصد را انتخاب کنید"
            
            if account_id == to_account_id:
                return False, "حساب مبدا و مقصد نمی‌توانند یکسان باشند"
            
            # بررسی موجودی کافی
            query = "SELECT current_balance FROM Accounts WHERE id = ?"
            from_account = self.data_manager.db.fetch_one(query, (account_id,))
            if from_account:
                balance_toman = float(from_account.get('current_balance', 0)) / 10
                if balance_toman < amount:
                    return False, f"موجودی حساب مبدا کافی نیست (موجودی: {balance_toman:,.0f} تومان)"
        
        return True, "اعتبارسنجی موفق"
    
    def save_transaction(self):
        """ذخیره تراکنش با استفاده از TransactionManager"""
        try:
            # اعتبارسنجی
            valid, message = self.validate_inputs()
            if not valid:
                QMessageBox.warning(self, "خطا", message)
                return
            
            # جمع‌آوری اطلاعات
            transaction_data = {
                'transaction_type': self.get_transaction_type(),
                'amount': self.amount_input.value(),  # تومان
                'description': self.description_input.toPlainText().strip(),
            }
            
            # دریافت تاریخ شمسی و تبدیل به میلادی
            jalali_date = self.date_widget.get_date()
            jalali_date_str = jalali_date.strftime("%Y/%m/%d")
            
            # تبدیل تاریخ شمسی به میلادی برای ذخیره در دیتابیس
            gregorian_date = self.data_manager.db.jalali_to_gregorian(jalali_date_str)
            if not gregorian_date:
                QMessageBox.warning(self, "خطا", "تاریخ نامعتبر است.")
                return
            
            transaction_data['transaction_date'] = gregorian_date
            
            # تنظیم حساب‌ها بر اساس نوع تراکنش
            trans_type = transaction_data['transaction_type']
            
            if trans_type == "دریافت":
                transaction_data['to_account_id'] = self.account_combo.currentData()
            elif trans_type == "پرداخت":
                transaction_data['from_account_id'] = self.account_combo.currentData()
            else:  # انتقال
                transaction_data['from_account_id'] = self.account_combo.currentData()
                transaction_data['to_account_id'] = self.to_account_combo.currentData()
            
            # تنظیم مرجع (اختیاری)
            reference = self.reference_input.text().strip()
            if reference:
                try:
                    transaction_data['reference_id'] = int(reference)
                except:
                    transaction_data['reference_text'] = reference
            
            print(f"🔄 در حال ذخیره تراکنش...")
            print(f"   نوع: {trans_type}")
            print(f"   مبلغ: {transaction_data['amount']:,.0f} تومان")
            print(f"   تاریخ شمسی: {jalali_date_str}")
            print(f"   تاریخ میلادی: {gregorian_date}")
            
            # ذخیره با استفاده از TransactionManager
            if self.is_edit:
                # ویرایش با TransactionManager
                success, message = self.transaction_manager.update_transaction(
                    self.transaction_id,
                    transaction_data
                )
                action = "ویرایش"
            else:
                # ایجاد جدید با TransactionManager
                success, message = self.transaction_manager.create_transaction(transaction_data)
                action = "ثبت"
            
            if success:
                QMessageBox.information(
                    self, "موفق", 
                    f"✅ تراکنش با موفقیت {action} شد.\n\n"
                    f"📊 نوع: {trans_type}\n"
                    f"💰 مبلغ: {transaction_data['amount']:,.0f} تومان\n"
                    f"📅 تاریخ: {jalali_date_str}\n\n"
                    f"{message}"
                )
                self.accept()
            else:
                QMessageBox.critical(self, "خطا", f"❌ خطا در {action} تراکنش:\n\n{message}")
                
        except Exception as e:
            print(f"❌ خطا در ذخیره تراکنش: {e}")
            import traceback
            traceback.print_exc()
            QMessageBox.critical(self, "خطا", f"❌ خطا در ذخیره تراکنش:\n\n{str(e)}")