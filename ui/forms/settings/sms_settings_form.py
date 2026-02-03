# sms_settings_form.py

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout,
                               QFormLayout, QLabel, QLineEdit,
                               QComboBox, QPushButton, QGroupBox,
                               QCheckBox, QSpinBox, QTextEdit,
                               QTableWidget, QTableWidgetItem,
                               QHeaderView, QMessageBox, QTabWidget)
from PySide6.QtCore import Qt
import requests

class SMSSettingsForm(QWidget):
    """فرم تنظیمات پنل پیامکی"""
    
    def __init__(self, data_manager, config_manager=None):
        super().__init__()
        self.data_manager = data_manager
        self.config_manager = config_manager
        self.init_ui()
        self.apply_styles()
        self.load_templates()
    
    def init_ui(self):
        """ایجاد رابط کاربری"""
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # ایجاد تب‌ها
        self.tab_widget = QTabWidget()
        
        # تب تنظیمات اتصال
        self.connection_tab = QWidget()
        self.setup_connection_tab()
        self.tab_widget.addTab(self.connection_tab, "🔌 اتصال")
        
        # تب قالب‌های پیام
        self.templates_tab = QWidget()
        self.setup_templates_tab()
        self.tab_widget.addTab(self.templates_tab, "📝 قالب‌ها")
        
        # تب تنظیمات ارسال
        self.sending_tab = QWidget()
        self.setup_sending_tab()
        self.tab_widget.addTab(self.sending_tab, "🚀 ارسال")
        
        main_layout.addWidget(self.tab_widget)
        self.setLayout(main_layout)
    
    def setup_connection_tab(self):
        """تنظیم تب اتصال"""
        layout = QVBoxLayout()
        
        # گروه تنظیمات API
        api_group = QGroupBox("🌐 تنظیمات API پنل پیامکی")
        api_layout = QFormLayout()
        
        # انتخاب پنل
        self.cmb_sms_panel = QComboBox()
        self.cmb_sms_panel.addItems([
            "کاوه نگار",
            "مدیران سامانه",
            "آوینا گیت",
            "ملت پیامک",
            "سامانه پیامک",
            "سفارشی"
        ])
        self.cmb_sms_panel.currentTextChanged.connect(self.on_panel_changed)
        
        # URL API
        self.txt_api_url = QLineEdit()
        self.txt_api_url.setPlaceholderText("https://example.com/api/send")
        
        # کلید API
        self.txt_api_key = QLineEdit()
        self.txt_api_key.setPlaceholderText("کلید API")
        
        # نام کاربری و رمز عبور
        self.txt_username = QLineEdit()
        self.txt_username.setPlaceholderText("نام کاربری")
        
        self.txt_password = QLineEdit()
        self.txt_password.setPlaceholderText("رمز عبور")
        self.txt_password.setEchoMode(QLineEdit.Password)
        
        # شماره خط
        self.txt_line_number = QLineEdit()
        self.txt_line_number.setPlaceholderText("شماره خط ارسال")
        
        # فعال‌سازی
        self.chk_sms_active = QCheckBox("فعال‌سازی ارسال پیامک")
        self.chk_sms_active.setChecked(True)
        
        api_layout.addRow("پنل پیامکی:", self.cmb_sms_panel)
        api_layout.addRow("URL API:", self.txt_api_url)
        api_layout.addRow("کلید API:", self.txt_api_key)
        api_layout.addRow("نام کاربری:", self.txt_username)
        api_layout.addRow("رمز عبور:", self.txt_password)
        api_layout.addRow("شماره خط:", self.txt_line_number)
        api_layout.addRow("", self.chk_sms_active)
        
        api_group.setLayout(api_layout)
        layout.addWidget(api_group)
        
        # دکمه تست اتصال
        self.btn_test_connection = QPushButton("🔍 تست اتصال به پنل")
        self.btn_test_connection.clicked.connect(self.test_connection)
        layout.addWidget(self.btn_test_connection, 0, Qt.AlignRight)
        
        # وضعیت اتصال
        status_layout = QHBoxLayout()
        
        self.lbl_connection_status = QLabel("وضعیت: قطع")
        self.lbl_connection_status.setStyleSheet("color: #e74c3c; font-weight: bold;")
        
        self.lbl_credit = QLabel("اعتبار: نامشخص")
        self.lbl_credit.setStyleSheet("color: #f39c12;")
        
        status_layout.addWidget(self.lbl_connection_status)
        status_layout.addWidget(self.lbl_credit)
        status_layout.addStretch()
        
        layout.addLayout(status_layout)
        self.connection_tab.setLayout(layout)
    
    def setup_templates_tab(self):
        """تنظیم تب قالب‌های پیام"""
        layout = QVBoxLayout()
        
        # جدول قالب‌ها
        self.table_templates = QTableWidget()
        self.table_templates.setColumnCount(4)
        self.table_templates.setHorizontalHeaderLabels([
            "نوع پیام", "قالب متن", "متغیرها", "وضعیت"
        ])
        
        # تنظیمات جدول
        self.table_templates.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table_templates.setEditTriggers(QTableWidget.NoEditTriggers)
        
        layout.addWidget(self.table_templates)
        
        # دکمه‌های مدیریت قالب
        template_actions = QHBoxLayout()
        
        self.btn_add_template = QPushButton("➕ افزودن قالب")
        self.btn_edit_template = QPushButton("✏️ ویرایش")
        self.btn_delete_template = QPushButton("🗑️ حذف")
        self.btn_preview_template = QPushButton("👁️ پیش‌نمایش")
        
        template_actions.addWidget(self.btn_add_template)
        template_actions.addWidget(self.btn_edit_template)
        template_actions.addWidget(self.btn_delete_template)
        template_actions.addWidget(self.btn_preview_template)
        template_actions.addStretch()
        
        layout.addLayout(template_actions)
        
        # متغیرهای قابل استفاده
        vars_group = QGroupBox("📋 متغیرهای قابل استفاده در قالب‌ها")
        vars_layout = QVBoxLayout()
        
        vars_text = QLabel("""
        {customer_name} - نام مشتری
        {device_name} - نام دستگاه
        {reception_number} - شماره پذیرش
        {repair_status} - وضعیت تعمیر
        {estimated_cost} - هزینه تخمینی
        {final_cost} - هزینه نهایی
        {delivery_date} - تاریخ تحویل
        {repair_date} - تاریخ تعمیر
        {technician_name} - نام تعمیرکار
        {company_name} - نام شرکت
        {company_phone} - تلفن شرکت
        """)
        vars_text.setStyleSheet("font-family: monospace; background-color: #222; padding: 10px; border-radius: 5px;")
        
        vars_layout.addWidget(vars_text)
        vars_group.setLayout(vars_layout)
        
        layout.addWidget(vars_group)
        self.templates_tab.setLayout(layout)
    
    def setup_sending_tab(self):
        """تنظیم تب تنظیمات ارسال"""
        layout = QVBoxLayout()
        
        # گروه تنظیمات خودکار
        auto_group = QGroupBox("🔄 ارسال خودکار پیامک")
        auto_layout = QFormLayout()
        
        self.chk_send_on_reception = QCheckBox("ارسال پیام هنگام ثبت پذیرش")
        self.chk_send_on_reception.setChecked(True)
        
        self.chk_send_on_repair_start = QCheckBox("ارسال پیام هنگام شروع تعمیر")
        self.chk_send_on_repair_start.setChecked(True)
        
        self.chk_send_on_repair_complete = QCheckBox("ارسال پیام هنگام اتمام تعمیر")
        self.chk_send_on_repair_complete.setChecked(True)
        
        self.chk_send_on_delivery = QCheckBox("ارسال پیام هنگام آماده تحویل")
        self.chk_send_on_delivery.setChecked(True)
        
        self.chk_send_reminders = QCheckBox("ارسال یادآوری به مشتریان")
        self.chk_send_reminders.setChecked(False)
        
        self.spn_reminder_days = QSpinBox()
        self.spn_reminder_days.setRange(1, 30)
        self.spn_reminder_days.setValue(3)
        self.spn_reminder_days.setSuffix(" روز قبل")
        
        auto_layout.addRow("", self.chk_send_on_reception)
        auto_layout.addRow("", self.chk_send_on_repair_start)
        auto_layout.addRow("", self.chk_send_on_repair_complete)
        auto_layout.addRow("", self.chk_send_on_delivery)
        auto_layout.addRow("", self.chk_send_reminders)
        auto_layout.addRow("زمان یادآوری:", self.spn_reminder_days)
        
        auto_group.setLayout(auto_layout)
        layout.addWidget(auto_group)
        
        # گروه محدودیت‌ها
        limits_group = QGroupBox("⚡ محدودیت‌های ارسال")
        limits_layout = QFormLayout()
        
        self.spn_max_daily = QSpinBox()
        self.spn_max_daily.setRange(10, 10000)
        self.spn_max_daily.setValue(500)
        self.spn_max_daily.setSuffix(" پیام در روز")
        
        self.spn_delay_between = QSpinBox()
        self.spn_delay_between.setRange(1, 60)
        self.spn_delay_between.setValue(5)
        self.spn_delay_between.setSuffix(" ثانیه")
        
        self.chk_night_mode = QCheckBox("عدم ارسال در ساعات شب")
        self.chk_night_mode.setChecked(True)
        
        self.txt_night_start = QLineEdit("22:00")
        self.txt_night_end = QLineEdit("08:00")
        
        limits_layout.addRow("حداکثر ارسال روزانه:", self.spn_max_daily)
        limits_layout.addRow("تأخیر بین ارسال:", self.spn_delay_between)
        limits_layout.addRow("", self.chk_night_mode)
        limits_layout.addRow("شروع شب:", self.txt_night_start)
        limits_layout.addRow("پایان شب:", self.txt_night_end)
        
        limits_group.setLayout(limits_layout)
        layout.addWidget(limits_group)
        
        # گروه گزارش
        report_group = QGroupBox("📊 آمار ارسال")
        report_layout = QHBoxLayout()
        
        self.lbl_today_sent = QLabel("امروز: ۰ پیام")
        self.lbl_month_sent = QLabel("این ماه: ۰ پیام")
        self.lbl_total_sent = QLabel("کل: ۰ پیام")
        self.lbl_remaining = QLabel("مانده: نامحدود")
        
        report_layout.addWidget(self.lbl_today_sent)
        report_layout.addWidget(self.lbl_month_sent)
        report_layout.addWidget(self.lbl_total_sent)
        report_layout.addWidget(self.lbl_remaining)
        report_layout.addStretch()
        
        report_group.setLayout(report_layout)
        layout.addWidget(report_group)
        
        # دکمه پاکسازی تاریخچه
        self.btn_clear_history = QPushButton("🧹 پاکسازی تاریخچه پیام‌ها")
        layout.addWidget(self.btn_clear_history, 0, Qt.AlignRight)
        
        self.sending_tab.setLayout(layout)
    
    def apply_styles(self):
        """اعمال استایل"""
        self.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 12pt;
                color: #9b59b6;
                border: 2px solid #9b59b6;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                padding: 0 10px;
            }
            QLineEdit, QComboBox, QSpinBox, QTextEdit {
                background-color: #222222;
                color: #ffffff;
                border: 1px solid #444444;
                border-radius: 3px;
                padding: 5px;
                min-height: 25px;
            }
            QCheckBox {
                color: #ffffff;
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
        """)
    
    def on_panel_changed(self, panel_name):
        """وقتی پنل پیامکی تغییر کرد"""
        # تنظیم مقادیر پیش‌فرض بر اساس پنل انتخاب شده
        defaults = {
            "کاوه نگار": {
                "url": "https://api.kavenegar.com/v1/{API_KEY}/sms/send.json",
                "username": "",
                "password": ""
            },
            "مدیران سامانه": {
                "url": "https://rest.payamak-panel.com/api/SendSMS/SendSMS",
                "username": "",
                "password": ""
            },
            "آوینا گیت": {
                "url": "https://sms.avinagate.com/api/v1/sms/send",
                "username": "",
                "password": ""
            },
            "ملت پیامک": {
                "url": "https://mellipayamak.ir/post/send.asmx?WSDL",
                "username": "",
                "password": ""
            },
            "سامانه پیامک": {
                "url": "https://api.samantapayamak.ir/v1/sms/send",
                "username": "",
                "password": ""
            },
            "سفارشی": {
                "url": "",
                "username": "",
                "password": ""
            }
        }
        
        if panel_name in defaults:
            default = defaults[panel_name]
            self.txt_api_url.setText(default["url"])
            self.txt_username.setText(default["username"])
            self.txt_password.setText(default["password"])
    
    def test_connection(self):
        """تست اتصال به پنل پیامکی"""
        api_url = self.txt_api_url.text().strip()
        api_key = self.txt_api_key.text().strip()
        
        if not api_url or not api_key:
            QMessageBox.warning(self, "خطا", "لطفاً URL و کلید API را وارد کنید.")
            return
        
        # نمایش پیام در حال تست
        self.lbl_connection_status.setText("وضعیت: در حال تست...")
        self.lbl_connection_status.setStyleSheet("color: #f39c12; font-weight: bold;")
        
        # در اینجا باید درخواست واقعی به API ارسال شود
        # فعلاً شبیه‌سازی می‌کنیم
        
        try:
            # شبیه‌سازی تاخیر شبکه
            import time
            time.sleep(2)
            
            # شبیه‌سازی پاسخ موفق
            success = True  # در حالت واقعی از پاسخ API مشخص می‌شود
            
            if success:
                self.lbl_connection_status.setText("وضعیت: متصل ✓")
                self.lbl_connection_status.setStyleSheet("color: #27ae60; font-weight: bold;")
                self.lbl_credit.setText("اعتبار: ۵۰۰۰ تومان")
                QMessageBox.information(self, "موفقیت", "اتصال به پنل پیامکی با موفقیت برقرار شد.")
            else:
                raise Exception("خطا در اتصال")
                
        except Exception as e:
            self.lbl_connection_status.setText("وضعیت: قطع ✗")
            self.lbl_connection_status.setStyleSheet("color: #e74c3c; font-weight: bold;")
            QMessageBox.critical(self, "خطا", f"اتصال به پنل پیامکی ناموفق بود.\n{str(e)}")
    
    def load_templates(self):
        """بارگذاری قالب‌های پیام"""
        templates = [
            ["ثبت پذیرش", "مشتری گرامی {customer_name}، دستگاه {device_name} شما ثبت شد. شماره پذیرش: {reception_number}", "{customer_name}, {device_name}, {reception_number}", "فعال"],
            ["شروع تعمیر", "مشتری گرامی {customer_name}، تعمیر دستگاه شما آغاز شد.", "{customer_name}", "فعال"],
            ["اتمام تعمیر", "مشتری گرامی {customer_name}، دستگاه شما آماده تحویل است. هزینه: {final_cost}", "{customer_name}, {final_cost}", "فعال"],
            ["یادآوری", "مشتری گرامی {customer_name}، لطفاً جهت تحویل دستگاه مراجعه فرمایید.", "{customer_name}", "غیرفعال"],
            ["تخفیف", "مشتری گرامی {customer_name}، ویژه‌نامه تخفیف‌های جدید ما را ببینید.", "{customer_name}", "فعال"],
        ]
        
        self.table_templates.setRowCount(len(templates))
        
        for row, template in enumerate(templates):
            for col, value in enumerate(template):
                item = QTableWidgetItem(value)
                item.setTextAlignment(Qt.AlignRight)
                
                if col == 3:  # ستون وضعیت
                    if value == "فعال":
                        item.setForeground(Qt.green)
                    else:
                        item.setForeground(Qt.red)
                
                self.table_templates.setItem(row, col, item)
    
    def load_settings(self, settings_data):
        """بارگذاری تنظیمات"""
        try:
            # تنظیمات اتصال
            panel = settings_data.get('sms_panel', 'کاوه نگار')
            panel_index = self.cmb_sms_panel.findText(panel)
            if panel_index >= 0:
                self.cmb_sms_panel.setCurrentIndex(panel_index)
            
            self.txt_api_url.setText(settings_data.get('api_url', ''))
            self.txt_api_key.setText(settings_data.get('api_key', ''))
            self.txt_username.setText(settings_data.get('sms_username', ''))
            self.txt_password.setText(settings_data.get('sms_password', ''))
            self.txt_line_number.setText(settings_data.get('line_number', ''))
            self.chk_sms_active.setChecked(settings_data.get('sms_active', True))
            
            # تنظیمات ارسال خودکار
            self.chk_send_on_reception.setChecked(settings_data.get('send_on_reception', True))
            self.chk_send_on_repair_start.setChecked(settings_data.get('send_on_repair_start', True))
            self.chk_send_on_repair_complete.setChecked(settings_data.get('send_on_repair_complete', True))
            self.chk_send_on_delivery.setChecked(settings_data.get('send_on_delivery', True))
            self.chk_send_reminders.setChecked(settings_data.get('send_reminders', False))
            self.spn_reminder_days.setValue(settings_data.get('reminder_days', 3))
            
            # محدودیت‌ها
            self.spn_max_daily.setValue(settings_data.get('max_daily_sms', 500))
            self.spn_delay_between.setValue(settings_data.get('delay_between_sms', 5))
            self.chk_night_mode.setChecked(settings_data.get('night_mode', True))
            self.txt_night_start.setText(settings_data.get('night_start', '22:00'))
            self.txt_night_end.setText(settings_data.get('night_end', '08:00'))
            
        except Exception as e:
            print(f"خطا در بارگذاری تنظیمات پیامکی: {e}")
    
    def get_settings(self):
        """جمع‌آوری تنظیمات"""
        settings = {
            # تنظیمات اتصال
            'sms_panel': self.cmb_sms_panel.currentText(),
            'api_url': self.txt_api_url.text(),
            'api_key': self.txt_api_key.text(),
            'sms_username': self.txt_username.text(),
            'sms_password': self.txt_password.text(),
            'line_number': self.txt_line_number.text(),
            'sms_active': self.chk_sms_active.isChecked(),
            
            # تنظیمات ارسال خودکار
            'send_on_reception': self.chk_send_on_reception.isChecked(),
            'send_on_repair_start': self.chk_send_on_repair_start.isChecked(),
            'send_on_repair_complete': self.chk_send_on_repair_complete.isChecked(),
            'send_on_delivery': self.chk_send_on_delivery.isChecked(),
            'send_reminders': self.chk_send_reminders.isChecked(),
            'reminder_days': self.spn_reminder_days.value(),
            
            # محدودیت‌ها
            'max_daily_sms': self.spn_max_daily.value(),
            'delay_between_sms': self.spn_delay_between.value(),
            'night_mode': self.chk_night_mode.isChecked(),
            'night_start': self.txt_night_start.text(),
            'night_end': self.txt_night_end.text(),
        }
        
        return settings