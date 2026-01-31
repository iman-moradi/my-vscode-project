"""
دیالوگ ثبت پرداخت برای فاکتور
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QComboBox, QDoubleSpinBox, QTextEdit, QGroupBox,
    QRadioButton, QButtonGroup, QMessageBox, QDateEdit,
    QTableWidget, QTableWidgetItem, QHeaderView
)
from PySide6.QtCore import Qt, QDate, Signal
from PySide6.QtGui import QFont


class PaymentDialog(QDialog):
    """دیالوگ ثبت پرداخت برای فاکتور"""
    
    payment_recorded = Signal(dict)  # ارسال اطلاعات پرداخت ثبت شده
    
    def __init__(self, data_manager, invoice_id, parent=None):
        super().__init__(parent)
        self.data_manager = data_manager
        self.invoice_id = invoice_id
        self.payment_amount = 0
        
        # تنظیمات پنجره
        self.setWindowTitle("ثبت پرداخت فاکتور")
        self.setMinimumSize(600, 500)
        self.setLayoutDirection(Qt.RightToLeft)
        
        # استایل
        self.setStyleSheet("""
            QDialog {
                background-color: #000000;
                color: #ffffff;
                font-family: 'B Nazanin';
            }
            QGroupBox {
                background-color: #111111;
                border: 2px solid #333;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 15px;
                font-weight: bold;
                color: #2ecc71;
            }
            QLabel {
                color: #ffffff;
            }
            QComboBox, QDoubleSpinBox, QTextEdit {
                background-color: #222222;
                border: 1px solid #333;
                color: white;
                border-radius: 4px;
                padding: 6px;
            }
            QPushButton {
                padding: 8px 15px;
                border-radius: 5px;
                font-weight: bold;
                border: none;
                color: white;
            }
        """)
        
        self.init_ui()
        self.load_invoice_info()
        self.load_accounts()
    
    def init_ui(self):
        """ایجاد رابط کاربری"""
        layout = QVBoxLayout(self)
        
        # اطلاعات فاکتور
        info_group = QGroupBox("اطلاعات فاکتور")
        info_layout = QVBoxLayout(info_group)
        
        self.invoice_info_label = QLabel("در حال بارگذاری...")
        self.invoice_info_label.setStyleSheet("font-size: 12pt; color: #f39c12;")
        info_layout.addWidget(self.invoice_info_label)
        
        layout.addWidget(info_group)
        
        # مبلغ قابل پرداخت
        amount_group = QGroupBox("مبلغ پرداختی")
        amount_layout = QVBoxLayout(amount_group)
        
        amount_info_layout = QHBoxLayout()
        payable_label = QLabel("مبلغ قابل پرداخت:")
        self.payable_amount = QLabel("0 تومان")
        self.payable_amount.setStyleSheet("font-size: 14pt; font-weight: bold; color: #e74c3c;")
        
        amount_info_layout.addWidget(payable_label)
        amount_info_layout.addWidget(self.payable_amount)
        amount_info_layout.addStretch()
        
        amount_layout.addLayout(amount_info_layout)
        
        # مبلغ پرداختی
        payment_layout = QHBoxLayout()
        payment_label = QLabel("مبلغ پرداختی:")
        self.payment_spin = QDoubleSpinBox()
        self.payment_spin.setRange(0, 1000000000)  # تا 100 میلیون تومان
        self.payment_spin.setValue(0)
        self.payment_spin.setSuffix(" تومان")
        self.payment_spin.setSingleStep(10000)  # گام 10 هزار تومان
        self.payment_spin.valueChanged.connect(self.calculate_remaining)
        
        payment_layout.addWidget(payment_label)
        payment_layout.addWidget(self.payment_spin)
        payment_layout.addStretch()
        
        amount_layout.addLayout(payment_layout)
        
        # مانده
        remaining_layout = QHBoxLayout()
        remaining_label = QLabel("مانده حساب:")
        self.remaining_amount = QLabel("0 تومان")
        self.remaining_amount.setStyleSheet("font-size: 14pt; font-weight: bold; color: #2ecc71;")
        
        remaining_layout.addWidget(remaining_label)
        remaining_layout.addWidget(self.remaining_amount)
        remaining_layout.addStretch()
        
        amount_layout.addLayout(remaining_layout)
        
        layout.addWidget(amount_group)
        
        # روش پرداخت
        method_group = QGroupBox("روش پرداخت")
        method_layout = QVBoxLayout(method_group)
        
        self.payment_method_combo = QComboBox()
        self.payment_method_combo.addItems([
            "💵 نقدی",
            "💳 کارت خوان",
            "🏦 کارت به کارت",
            "📄 چک",
            "💸 اعتبار"
        ])
        self.payment_method_combo.currentIndexChanged.connect(self.on_payment_method_changed)
        
        method_layout.addWidget(self.payment_method_combo)
        
        # حساب بانکی (برای انتقال و کارت)
        account_layout = QHBoxLayout()
        account_label = QLabel("حساب بانکی:")
        self.account_combo = QComboBox()
        self.account_combo.setEnabled(False)
        
        account_layout.addWidget(account_label)
        account_layout.addWidget(self.account_combo)
        
        method_layout.addLayout(account_layout)
        
        layout.addWidget(method_group)
        
        # توضیحات
        desc_group = QGroupBox("توضیحات")
        desc_layout = QVBoxLayout(desc_group)
        
        self.description_input = QTextEdit()
        self.description_input.setMaximumHeight(80)
        self.description_input.setPlaceholderText("توضیحات پرداخت (اختیاری)...")
        
        desc_layout.addWidget(self.description_input)
        
        layout.addWidget(desc_group)
        
        # دکمه‌ها
        button_layout = QHBoxLayout()
        
        self.record_btn = QPushButton("💾 ثبت پرداخت")
        self.record_btn.setStyleSheet("background-color: #27ae60;")
        self.record_btn.clicked.connect(self.record_payment)
        
        cancel_btn = QPushButton("❌ انصراف")
        cancel_btn.setStyleSheet("background-color: #e74c3c;")
        cancel_btn.clicked.connect(self.reject)
        
        button_layout.addWidget(self.record_btn)
        button_layout.addStretch()
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
    
    def load_invoice_info(self):
        """بارگذاری اطلاعات فاکتور"""
        try:
            if not self.invoice_id:
                return
            
            query = """
            SELECT 
                invoice_number,
                total,
                paid_amount,
                (total - paid_amount) as remaining
            FROM Invoices 
            WHERE id = ?
            """
            
            invoice = self.data_manager.db.fetch_one(query, (self.invoice_id,))
            
            if invoice:
                total_toman = invoice.get('total', 0) / 10
                paid_toman = invoice.get('paid_amount', 0) / 10
                remaining_toman = invoice.get('remaining', 0) / 10
                
                self.invoice_info_label.setText(
                    f"فاکتور شماره: {invoice.get('invoice_number', '--')} | "
                    f"مبلغ کل: {total_toman:,.0f} تومان | "
                    f"پرداخت شده: {paid_toman:,.0f} تومان"
                )
                
                self.payable_amount.setText(f"{remaining_toman:,.0f} تومان")
                self.payment_spin.setValue(remaining_toman)
                self.payment_spin.setMaximum(remaining_toman)
                
                self.calculate_remaining()
                
        except Exception as e:
            print(f"⚠️ خطا در بارگذاری اطلاعات فاکتور: {e}")
    
    def load_accounts(self):
        """بارگذاری حساب‌های بانکی"""
        try:
            self.account_combo.clear()
            self.account_combo.addItem("-- انتخاب حساب --", None)
            
            query = """
            SELECT id, account_name, bank_name, account_number
            FROM Accounts 
            WHERE is_active = 1 AND account_type != 'صندوق'
            ORDER BY account_name
            """
            
            accounts = self.data_manager.db.fetch_all(query)
            
            for account in accounts:
                display_text = f"{account['account_name']} - {account['bank_name']} ({account['account_number']})"
                self.account_combo.addItem(display_text, account['id'])
                
        except Exception as e:
            print(f"⚠️ خطا در بارگذاری حساب‌ها: {e}")
    
    def calculate_remaining(self):
        """محاسبه مانده پس از پرداخت"""
        try:
            payable_text = self.payable_amount.text()
            payable = float(payable_text.replace("تومان", "").replace(",", "").strip())
            
            payment_amount = self.payment_spin.value()
            remaining = payable - payment_amount
            
            self.remaining_amount.setText(f"{remaining:,.0f} تومان")
            
            if remaining < 0:
                self.remaining_amount.setStyleSheet("font-size: 14pt; font-weight: bold; color: #e74c3c;")
                self.record_btn.setEnabled(False)
            elif remaining == 0:
                self.remaining_amount.setStyleSheet("font-size: 14pt; font-weight: bold; color: #27ae60;")
                self.record_btn.setEnabled(True)
            else:
                self.remaining_amount.setStyleSheet("font-size: 14pt; font-weight: bold; color: #f39c12;")
                self.record_btn.setEnabled(True)
                
        except:
            self.remaining_amount.setText("0 تومان")
    
    def on_payment_method_changed(self):
        """هنگام تغییر روش پرداخت"""
        method = self.payment_method_combo.currentText()
        
        if "کارت" in method or "چک" in method or "انتقال" in method:
            self.account_combo.setEnabled(True)
        else:
            self.account_combo.setEnabled(False)
    
    def record_payment(self):
        """ثبت پرداخت"""
        try:
            # اعتبارسنجی
            payment_amount = self.payment_spin.value()
            if payment_amount <= 0:
                QMessageBox.warning(self, "خطا", "مبلغ پرداختی باید بزرگتر از صفر باشد.")
                return
            
            method = self.payment_method_combo.currentText()
            
            # اگر روش پرداخت نیاز به حساب دارد، حساب را بررسی کن
            account_id = None
            if self.account_combo.isEnabled():
                account_id = self.account_combo.currentData()
                if not account_id:
                    QMessageBox.warning(self, "خطا", "لطفاً یک حساب بانکی انتخاب کنید.")
                    return
            
            # تأیید نهایی
            reply = QMessageBox.question(
                self, "تأیید پرداخت",
                f"آیا از ثبت پرداخت به مبلغ {payment_amount:,.0f} تومان مطمئن هستید؟",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply != QMessageBox.Yes:
                return
            
            # ثبت پرداخت در دیتابیس
            payment_data = {
                'invoice_id': self.invoice_id,
                'amount': payment_amount * 10,  # تبدیل به ریال
                'payment_method': method,
                'account_id': account_id,
                'description': self.description_input.toPlainText().strip()
            }
            
            success = self.save_payment_to_db(payment_data)
            
            if success:
                QMessageBox.information(self, "ثبت پرداخت", 
                    f"✅ پرداخت به مبلغ {payment_amount:,.0f} تومان با موفقیت ثبت شد.")
                
                self.payment_recorded.emit(payment_data)
                self.accept()
            else:
                QMessageBox.critical(self, "خطا", "خطا در ثبت پرداخت.")
                
        except Exception as e:
            QMessageBox.critical(self, "خطا", f"خطا در ثبت پرداخت:\n{str(e)}")
    
    def save_payment_to_db(self, payment_data):
        """ذخیره پرداخت در دیتابیس"""
        try:
            # 1. بروزرسانی مبلغ پرداخت شده در فاکتور
            update_query = """
            UPDATE Invoices 
            SET paid_amount = paid_amount + ?,
                remaining_amount = total - (paid_amount + ?),
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """
            
            amount_rial = payment_data['amount']
            self.data_manager.db.execute_query(update_query, 
                (amount_rial, amount_rial, payment_data['invoice_id']))
            
            # 2. ثبت تراکنش حسابداری
            transaction_type = "دریافت"
            account_id = payment_data.get('account_id')
            
            # اگر حساب انتخاب نشده، حساب پیش‌فرض صندوق را پیدا کن
            if not account_id:
                query = "SELECT id FROM Accounts WHERE account_type = 'صندوق' AND is_active = 1 LIMIT 1"
                result = self.data_manager.db.fetch_one(query)
                if result:
                    account_id = result['id']
            
            if account_id:
                transaction_query = """
                INSERT INTO AccountingTransactions (
                    transaction_date, transaction_type, to_account_id,
                    amount, description, reference_type, reference_id, employee
                ) VALUES (datetime('now'), ?, ?, ?, ?, 'فاکتور', ?, 'سیستم')
                """
                
                description = f"پرداخت فاکتور - {payment_data['payment_method']}"
                if payment_data['description']:
                    description += f" - {payment_data['description']}"
                
                params = (
                    transaction_type,
                    account_id,
                    amount_rial,
                    description,
                    payment_data['invoice_id']
                )
                
                self.data_manager.db.execute_query(transaction_query, params)
                
                # 3. بروزرسانی موجودی حساب
                update_balance_query = """
                UPDATE Accounts 
                SET current_balance = current_balance + ? 
                WHERE id = ?
                """
                
                self.data_manager.db.execute_query(update_balance_query, 
                    (amount_rial, account_id))
            
            return True
            
        except Exception as e:
            print(f"❌ خطا در ذخیره پرداخت: {e}")
            return False