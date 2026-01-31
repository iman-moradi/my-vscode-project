# در فایل check_dialog.py

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, 
    QLineEdit, QComboBox, QPushButton, QLabel,
    QMessageBox, QDateEdit, QSpinBox, QDoubleSpinBox
)
from PySide6.QtCore import Qt
import jdatetime

# در فایل 2 (check_dialog.py)، importها را اینگونه اصلاح کنید:

try:
    from ui.forms.accounting.widgets.jalali_date_input import JalaliDateInputAccounting as JalaliDateInput
except ImportError:
    from PySide6.QtWidgets import QLineEdit
    from PySide6.QtCore import Signal
    
    class JalaliDateInput(QLineEdit):
        """کلاس جایگزین برای تاریخ شمسی"""
        date_changed = Signal(str)
        
        def __init__(self, parent=None):
            super().__init__(parent)
            self.textChanged.connect(self._on_text_changed)
        
        def _on_text_changed(self):
            self.date_changed.emit(self.text())
        
        def get_date(self):
            return self.text()
        
        def set_date(self, date):
            if hasattr(date, 'year'):  # اگر jdatetime.date است
                try:
                    import jdatetime
                    from datetime import date as datetime_date
                    # بررسی می‌کنیم که آیا تاریخ شمسی است یا میلادی
                    if hasattr(date, 'togregorian'):  # jdatetime.date
                        self.setText(f"{date.year}/{date.month:02d}/{date.day:02d}")
                    else:  # datetime.date
                        jdate = jdatetime.date.fromgregorian(date=date)
                        self.setText(f"{jdate.year}/{jdate.month:02d}/{jdate.day:02d}")
                except:
                    self.setText(str(date))
            else:
                self.setText(str(date))
        
        def get_date_string(self):
            return self.text()
        
        def set_date_string(self, date_string):
            self.setText(date_string)

class CheckDialog(QDialog):
    """دیالوگ ثبت/ویرایش چک"""
    
    def __init__(self, data_manager, check_type=None, check_id=None, parent=None):
        super().__init__(parent)
        self.data_manager = data_manager
        self.db = data_manager.db
        self.check_type = check_type  # 'دریافتی' یا 'پرداختی'
        self.check_id = check_id  # برای حالت ویرایش
        
        self.setup_ui()
        self.setup_styles()
        
        if check_id:
            self.load_check_data()
        else:
            self.set_default_values()
    
    def setup_ui(self):
        """ایجاد رابط کاربری"""
        self.setWindowTitle(f"{'ویرایش' if self.check_id else 'ثبت'} چک {self.check_type}")
        self.setMinimumSize(500, 600)
        
        layout = QVBoxLayout(self)
        
        # فرم اصلی
        form_layout = QFormLayout()
        
        # شماره چک
        self.txt_check_number = QLineEdit()  # 🔴 این خط را اضافه کنید
        self.txt_check_number.setPlaceholderText("مثال: 123456")
        form_layout.addRow("شماره چک:", self.txt_check_number)
        
        # بانک
        self.cmb_bank = QComboBox()
        self.cmb_bank.setEditable(True)
        # بارگذاری بانک‌های موجود
        self.load_banks()
        form_layout.addRow("بانک:", self.cmb_bank)
        
        # شعبه
        self.txt_branch = QLineEdit()
        self.txt_branch.setPlaceholderText("شعبه بانک")
        form_layout.addRow("شعبه:", self.txt_branch)
        
        # شماره حساب
        self.txt_account_number = QLineEdit()
        self.txt_account_number.setPlaceholderText("شماره حساب صادرکننده")
        form_layout.addRow("شماره حساب:", self.txt_account_number)
        
        # مبلغ
        self.spn_amount = QDoubleSpinBox()
        self.spn_amount.setRange(0, 1000000000)
        self.spn_amount.setValue(0)
        self.spn_amount.setSuffix(" تومان")
        self.spn_amount.setSingleStep(10000)
        form_layout.addRow("مبلغ:", self.spn_amount)
        
        # تاریخ صدور
        self.date_issue = JalaliDateInput(mode='edit', theme='dark')
        self.date_issue.set_date(jdatetime.date.today())  # تاریخ امروز شمسی
        form_layout.addRow("تاریخ صدور:", self.date_issue)
        
        # تاریخ سررسید
        self.date_due = JalaliDateInput(mode='edit', theme='dark')
        # 3 ماه بعد برای سررسید
        due_date = jdatetime.date.today() + jdatetime.timedelta(days=90)
        self.date_due.set_date(due_date)
        form_layout.addRow("تاریخ سررسید:", self.date_due)

        # صادرکننده
        self.txt_drawer = QLineEdit()
        self.txt_drawer.setPlaceholderText("نام صادرکننده چک")
        form_layout.addRow("صادرکننده:", self.txt_drawer)
        
        # دریافت‌کننده
        self.txt_payee = QLineEdit()
        self.txt_payee.setPlaceholderText("نام دریافت‌کننده چک")
        form_layout.addRow("دریافت‌کننده:", self.txt_payee)
        
        # وضعیت
        self.cmb_status = QComboBox()
        statuses = ['وصول نشده', 'وصول شده', 'برگشتی', 'پاس شده', 'پاس نشده', 'بلوکه شده']
        self.cmb_status.addItems(statuses)
        form_layout.addRow("وضعیت:", self.cmb_status)
        
        # توضیحات
        self.txt_description = QLineEdit()
        self.txt_description.setPlaceholderText("توضیحات اختیاری")
        form_layout.addRow("توضیحات:", self.txt_description)
        
        layout.addLayout(form_layout)
        
        # دکمه‌ها
        button_layout = QHBoxLayout()
        
        btn_save = QPushButton("💾 ذخیره")
        btn_save.clicked.connect(self.save_check)
        button_layout.addWidget(btn_save)
        
        btn_cancel = QPushButton("❌ لغو")
        btn_cancel.clicked.connect(self.reject)
        button_layout.addWidget(btn_cancel)
        
        layout.addLayout(button_layout)
    
    def load_banks(self):
        """بارگذاری لیست بانک‌ها"""
        try:
            query = "SELECT DISTINCT bank_name FROM Checks WHERE bank_name IS NOT NULL AND bank_name != ''"
            banks = self.db.fetch_all(query)
            
            self.cmb_bank.clear()
            self.cmb_bank.addItem("")
            
            for bank in banks:
                self.cmb_bank.addItem(bank['bank_name'])
        except:
            pass
    
    def load_check_data(self):
        """بارگذاری اطلاعات چک برای ویرایش"""
        try:
            query = """
            SELECT * FROM Checks WHERE id = ?
            """
            check = self.db.fetch_one(query, (self.check_id,))
            
            if check:
                # پر کردن فیلدها
                self.txt_check_number.setText(check.get('check_number', ''))
                
                # بانک
                bank_name = check.get('bank_name', '')
                index = self.cmb_bank.findText(bank_name)
                if index >= 0:
                    self.cmb_bank.setCurrentIndex(index)
                else:
                    self.cmb_bank.setCurrentText(bank_name)
                
                self.txt_branch.setText(check.get('branch', ''))
                self.txt_account_number.setText(check.get('account_number', ''))
                self.spn_amount.setValue(check.get('amount', 0) / 10)  # تبدیل به تومان
                
                # تاریخ‌ها
                # تاریخ‌ها - اگر میلادی هستند، به شمسی تبدیل می‌شوند
                if check.get('issue_date'):
                    # set_date می‌تواند رشته میلادی را بگیرد و خودش به شمسی تبدیل کند
                    self.date_issue.set_date(check['issue_date'])

                if check.get('due_date'):
                    self.date_due.set_date(check['due_date'])
                
                self.txt_drawer.setText(check.get('drawer', ''))
                self.txt_payee.setText(check.get('payee', ''))
                
                # وضعیت
                status = check.get('status', 'وصول نشده')
                index = self.cmb_status.findText(status)
                if index >= 0:
                    self.cmb_status.setCurrentIndex(index)
                
                self.txt_description.setText(check.get('description', ''))
                
        except Exception as e:
            print(f"⚠️ خطا در بارگذاری اطلاعات چک: {e}")
    
    def set_default_values(self):
        """تنظیم مقادیر پیش‌فرض"""
        # شماره چک خودکار
        import random
        check_number = f"{jdatetime.datetime.now().strftime('%y%m%d')}{random.randint(1000, 9999)}"
        self.txt_check_number.setText(check_number)
        
        # تاریخ امروز برای صدور
        self.date_issue.set_date(jdatetime.date.today())
        
        # 3 ماه بعد برای سررسید
        due_date = jdatetime.date.today() + jdatetime.timedelta(days=90)
        self.date_due.set_date(due_date)
        
        # وضعیت پیش‌فرض
        self.cmb_status.setCurrentText('وصول نشده')
    
    def save_check(self):
        """ذخیره چک"""
        try:
            # اعتبارسنجی
            check_number = self.txt_check_number.text().strip()
            if not check_number:
                QMessageBox.warning(self, "خطا", "شماره چک را وارد کنید.")
                return
            
            bank_name = self.cmb_bank.currentText().strip()
            if not bank_name:
                QMessageBox.warning(self, "خطا", "نام بانک را وارد کنید.")
                return
            
            amount = self.spn_amount.value()
            if amount <= 0:
                QMessageBox.warning(self, "خطا", "مبلغ چک باید بیشتر از صفر باشد.")
                return
            
            due_date = self.date_due.get_date_string()
            if not due_date:
                QMessageBox.warning(self, "خطا", "تاریخ سررسید را انتخاب کنید.")
                return
            
            drawer = self.txt_drawer.text().strip()
            if not drawer:
                QMessageBox.warning(self, "خطا", "نام صادرکننده را وارد کنید.")
                return
            
            # آماده کردن داده‌ها
            check_data = {
                'check_number': check_number,
                'bank_name': bank_name,
                'branch': self.txt_branch.text().strip(),
                'account_number': self.txt_account_number.text().strip(),
                'amount': amount * 10,  # تبدیل به ریال
                'issue_date': self.date_issue.get_date(),  # تاریخ شمسی
                'due_date': self.date_due.get_date(),      # تاریخ شمسی
                'drawer': drawer,
                'payee': self.txt_payee.text().strip(),
                'status': self.cmb_status.currentText(),
                'check_type': self.check_type,
                'description': self.txt_description.text().strip()
            }
            
            # ذخیره در دیتابیس
            if self.check_id:
                # ویرایش
                query = """
                UPDATE Checks SET
                    check_number = ?,
                    bank_name = ?,
                    branch = ?,
                    account_number = ?,
                    amount = ?,
                    issue_date = ?,
                    due_date = ?,
                    drawer = ?,
                    payee = ?,
                    status = ?,
                    description = ?
                WHERE id = ?
                """
                
                params = (
                    check_data['check_number'],
                    check_data['bank_name'],
                    check_data['branch'],
                    check_data['account_number'],
                    check_data['amount'],
                    check_data['issue_date'],  # تاریخ شمسی
                    check_data['due_date'],    # تاریخ شمسی
                    check_data['drawer'],
                    check_data['payee'],
                    check_data['status'],
                    check_data['description'],
                    self.check_id
                )
                
                success = self.db.execute_query(query, params)
                message = "ویرایش"
            else:
                # ثبت جدید
                query = """
                INSERT INTO Checks (
                    check_number, bank_name, branch, account_number, 
                    amount, issue_date, due_date, drawer, payee, 
                    status, check_type, description
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """
                
                params = (
                    check_data['check_number'],
                    check_data['bank_name'],
                    check_data['branch'],
                    check_data['account_number'],
                    check_data['amount'],
                    check_data['issue_date'],  # تاریخ شمسی
                    check_data['due_date'],    # تاریخ شمسی
                    check_data['drawer'],
                    check_data['payee'],
                    check_data['status'],
                    check_data['check_type'],
                    check_data['description']
                )
                
                success = self.db.execute_query(query, params)
                message = "ثبت"
            
            if success:
                QMessageBox.information(self, "موفق", f"چک با موفقیت {message} شد.")
                self.accept()
            else:
                QMessageBox.warning(self, "خطا", f"خطا در {message} چک.")
        
        except Exception as e:
            print(f"⚠️ خطا در ذخیره چک: {e}")
            QMessageBox.warning(self, "خطا", f"خطا در ذخیره چک:\n{str(e)}")
    
    def setup_styles(self):
        """تنظیم استایل"""
        self.setStyleSheet("""
            QDialog {
                background-color: #111111;
            }
            QLabel {
                color: #ffffff;
                font-size: 11pt;
                min-width: 120px;
            }
            QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox {
                background-color: #222222;
                color: white;
                border: 1px solid #333;
                border-radius: 4px;
                padding: 6px;
                min-height: 30px;
                font-size: 11pt;
            }
            QPushButton {
                background-color: #2ecc71;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-size: 11pt;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #27ae60;
            }
        """)