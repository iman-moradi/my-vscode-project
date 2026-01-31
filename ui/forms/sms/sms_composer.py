# ui/forms/sms/sms_composer.py
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout,
                               QLabel, QTextEdit, QLineEdit,
                               QPushButton, QComboBox, QGroupBox,
                               QMessageBox, QCheckBox)
from PySide6.QtCore import Qt, Signal

class SMSComposerForm(QWidget):
    """فرم نوشتن و ارسال پیامک"""
    
    # سیگنال برای ارسال پیامک
    message_sent = Signal(dict)
    
    def __init__(self, sms_manager, parent=None):
        super().__init__(parent)
        self.sms_manager = sms_manager
        self.init_ui()
        self.apply_styles()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # انتخاب گیرنده
        receiver_group = QGroupBox("📱 گیرنده پیامک")
        receiver_layout = QVBoxLayout()
        
        self.txt_phone_number = QLineEdit()
        self.txt_phone_number.setPlaceholderText("شماره موبایل گیرنده (مثال: 989121234567)")
        
        # دکمه انتخاب از مشتریان
        self.btn_select_customer = QPushButton("انتخاب از مشتریان")
        self.btn_select_customer.clicked.connect(self.select_from_customers)
        
        receiver_layout.addWidget(QLabel("شماره موبایل:"))
        receiver_layout.addWidget(self.txt_phone_number)
        receiver_layout.addWidget(self.btn_select_customer)
        receiver_group.setLayout(receiver_layout)
        
        # متن پیام
        message_group = QGroupBox("📝 متن پیام")
        message_layout = QVBoxLayout()
        
        self.txt_message = QTextEdit()
        self.txt_message.setPlaceholderText("متن پیامک خود را اینجا بنویسید...")
        self.txt_message.setMaximumHeight(150)
        
        # شمارشگر کاراکتر
        self.lbl_char_count = QLabel("طول پیام: 0 کاراکتر (0 پیامک)")
        
        message_layout.addWidget(self.txt_message)
        message_layout.addWidget(self.lbl_char_count)
        message_group.setLayout(message_layout)
        
        # تنظیمات ارسال
        settings_group = QGroupBox("⚙️ تنظیمات ارسال")
        settings_layout = QVBoxLayout()
        
        self.cmb_line_number = QComboBox()
        self.cmb_line_number.addItems(["خط پیش‌فرض (5000xxx)", "خط تبلیغاتی", "خط خدماتی"])
        
        self.chk_save_template = QCheckBox("ذخیره به عنوان قالب")
        
        settings_layout.addWidget(QLabel("شماره خط ارسال:"))
        settings_layout.addWidget(self.cmb_line_number)
        settings_layout.addWidget(self.chk_save_template)
        settings_group.setLayout(settings_layout)
        
        # دکمه‌های اقدام
        action_layout = QHBoxLayout()
        
        self.btn_send = QPushButton("🚀 ارسال پیامک")
        self.btn_send.clicked.connect(self.send_sms)
        self.btn_send.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                font-weight: bold;
                padding: 10px;
                font-size: 12pt;
            }
            QPushButton:hover {
                background-color: #2ecc71;
            }
        """)
        
        self.btn_clear = QPushButton("🧹 پاک کردن")
        self.btn_clear.clicked.connect(self.clear_form)
        
        self.btn_test_api = QPushButton("🔍 تست اتصال API")
        self.btn_test_api.clicked.connect(self.test_api_connection)
        
        action_layout.addWidget(self.btn_send)
        action_layout.addWidget(self.btn_clear)
        action_layout.addWidget(self.btn_test_api)
        action_layout.addStretch()
        
        # وضعیت اعتبار
        self.lbl_credit = QLabel("اعتبار پنل: در حال بررسی...")
        
        # جمع‌آندی تمام بخش‌ها
        layout.addWidget(receiver_group)
        layout.addWidget(message_group)
        layout.addWidget(settings_group)
        layout.addLayout(action_layout)
        layout.addWidget(self.lbl_credit)
        layout.addStretch()
        
        self.setLayout(layout)
        
        # اتصال سیگنال برای شمارش کاراکتر
        self.txt_message.textChanged.connect(self.update_char_count)
        
        # بارگذاری اعتبار اولیه
        self.update_credit()
    
    def apply_styles(self):
        # استایل مشابه سایر فرم‌ها
        pass
    
    def update_char_count(self):
        text = self.txt_message.toPlainText()
        length = len(text)
        
        # محاسبه تعداد پیامک (هر 70 کاراکتر یک پیامک)
        sms_count = (length // 70) + 1 if length % 70 > 0 else length // 70
        
        self.lbl_char_count.setText(
            f"طول پیام: {length} کاراکتر ({sms_count} پیامک)")
    
    def update_credit(self):
        try:
            credit = self.sms_manager.get_credit()
            self.lbl_credit.setText(f"اعتبار پنل: {credit:,} تومان")
        except:
            self.lbl_credit.setText("اعتبار پنل: نامشخص")
    
    def send_sms(self):
        """ارسال پیامک"""
        phone = self.txt_phone_number.text().strip()
        message = self.txt_message.toPlainText().strip()
        
        # اعتبارسنجی
        if not phone:
            QMessageBox.warning(self, "خطا", "لطفاً شماره موبایل گیرنده را وارد کنید.")
            return
        
        if not message:
            QMessageBox.warning(self, "خطا", "لطفاً متن پیام را وارد کنید.")
            return
        
        # تأیید نهایی[citation:2]
        reply = QMessageBox.question(
            self,
            "تأیید ارسال",
            f"آیا از ارسال پیامک به شماره {phone} اطمینان دارید؟\n\n"
            f"هزینه: تقریباً {len(message)//70 + 1} پیامک",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # غیرفعال کردن دکمه در حین ارسال
            self.btn_send.setEnabled(False)
            self.btn_send.setText("در حال ارسال...")
            
            # ارسال پیامک
            result = self.sms_manager.send_single_sms(
                to_number=phone,
                message=message
            )
            
            # نمایش نتیجه
            if result.get('success'):
                QMessageBox.information(
                    self, 
                    "موفقیت", 
                    f"پیامک با موفقیت ارسال شد.\nکد پیگیری: {result.get('message_id')}"
                )
                self.message_sent.emit(result)
                self.clear_form()
            else:
                QMessageBox.critical(
                    self, 
                    "خطا", 
                    f"ارسال پیامک ناموفق بود.\nخطا: {result.get('error')}"
                )
            
            # بازنشانی دکمه
            self.btn_send.setEnabled(True)
            self.btn_send.setText("🚀 ارسال پیامک")
            
            # به‌روزرسانی اعتبار
            self.update_credit()
    
    def select_from_customers(self):
        """انتخاب گیرنده از لیست مشتریان"""
        # این متد باید لیست مشتریان را نمایش دهد
        # فعلاً نمونه‌سازی می‌شود
        from ui.forms.person_form import PersonForm
        # باز کردن دیالوگ انتخاب مشتری
        pass
    
    def test_api_connection(self):
        """تست اتصال به API پنل پیامکی"""
        try:
            credit = self.sms_manager.get_credit()
            if credit > 0:
                QMessageBox.information(
                    self,
                    "اتصال موفق",
                    f"اتصال به پنل پیامکی با موفقیت برقرار شد.\nاعتبار باقی‌مانده: {credit:,} تومان"
                )
            else:
                QMessageBox.warning(
                    self,
                    "هشدار",
                    "اتصال برقرار شد اما اعتبار پنل صفر است."
                )
        except Exception as e:
            QMessageBox.critical(
                self,
                "خطای اتصال",
                f"خطا در اتصال به پنل پیامکی:\n{str(e)}"
            )
    
    def clear_form(self):
        """پاک کردن فرم"""
        self.txt_phone_number.clear()
        self.txt_message.clear()
        self.chk_save_template.setChecked(False)