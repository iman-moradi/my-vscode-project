# security_settings_form.py

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout,
                               QFormLayout, QLabel, QLineEdit,
                               QComboBox, QPushButton, QGroupBox,
                               QCheckBox, QSpinBox, QTextEdit,
                               QTableWidget, QTableWidgetItem,
                               QHeaderView, QMessageBox, QTabWidget,
                               QDateTimeEdit)
from PySide6.QtCore import Qt, QDateTime
import hashlib

class SecuritySettingsForm(QWidget):
    """فرم تنظیمات امنیتی"""
    
    def __init__(self, data_manager):
        super().__init__()
        self.data_manager = data_manager
        self.init_ui()
        self.apply_styles()
        self.load_activity_log()
    
    def init_ui(self):
        """ایجاد رابط کاربری"""
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # ایجاد تب‌ها
        self.tab_widget = QTabWidget()
        
        # تب احراز هویت
        self.authentication_tab = QWidget()
        self.setup_authentication_tab()
        self.tab_widget.addTab(self.authentication_tab, "🔐 احراز هویت")
        
        # تب رمزگذاری
        self.encryption_tab = QWidget()
        self.setup_encryption_tab()
        self.tab_widget.addTab(self.encryption_tab, "🔒 رمزگذاری")
        
        # تب لاگ فعالیت
        self.activity_tab = QWidget()
        self.setup_activity_tab()
        self.tab_widget.addTab(self.activity_tab, "📝 فعالیت‌ها")
        
        main_layout.addWidget(self.tab_widget)
        self.setLayout(main_layout)
    
    def setup_authentication_tab(self):
        """تنظیم تب احراز هویت"""
        layout = QVBoxLayout()
        
        # گروه تنظیمات ورود
        login_group = QGroupBox("🚪 تنظیمات ورود به سیستم")
        login_layout = QFormLayout()
        
        self.spn_max_attempts = QSpinBox()
        self.spn_max_attempts.setRange(1, 10)
        self.spn_max_attempts.setValue(3)
        self.spn_max_attempts.setSuffix(" تلاش")
        
        self.spn_lockout_time = QSpinBox()
        self.spn_lockout_time.setRange(1, 60)
        self.spn_lockout_time.setValue(15)
        self.spn_lockout_time.setSuffix(" دقیقه")
        
        self.spn_session_timeout = QSpinBox()
        self.spn_session_timeout.setRange(5, 480)
        self.spn_session_timeout.setValue(30)
        self.spn_session_timeout.setSuffix(" دقیقه")
        
        self.chk_force_logout = QCheckBox("خروج اجباری پس از پایان زمان")
        self.chk_force_logout.setChecked(True)
        
        self.chk_remember_me = QCheckBox("امکان ذخیره ورود")
        self.chk_remember_me.setChecked(True)
        
        login_layout.addRow("حداکثر تلاش ناموفق:", self.spn_max_attempts)
        login_layout.addRow("زمان قفل حساب:", self.spn_lockout_time)
        login_layout.addRow("مدت جلسه:", self.spn_session_timeout)
        login_layout.addRow("", self.chk_force_logout)
        login_layout.addRow("", self.chk_remember_me)
        
        login_group.setLayout(login_layout)
        layout.addWidget(login_group)
        
        # گروه سیاست رمز عبور
        password_group = QGroupBox("🔑 سیاست رمز عبور")
        password_layout = QFormLayout()
        
        self.spn_min_length = QSpinBox()
        self.spn_min_length.setRange(4, 20)
        self.spn_min_length.setValue(8)
        self.spn_min_length.setSuffix(" حرف")
        
        self.spn_expiry_days = QSpinBox()
        self.spn_expiry_days.setRange(0, 365)
        self.spn_expiry_days.setValue(90)
        self.spn_expiry_days.setSuffix(" روز")
        
        self.spn_history_count = QSpinBox()
        self.spn_history_count.setRange(0, 10)
        self.spn_history_count.setValue(5)
        self.spn_history_count.setSuffix(" رمز قبلی")
        
        self.chk_require_uppercase = QCheckBox("نیاز به حروف بزرگ")
        self.chk_require_uppercase.setChecked(True)
        
        self.chk_require_lowercase = QCheckBox("نیاز به حروف کوچک")
        self.chk_require_lowercase.setChecked(True)
        
        self.chk_require_numbers = QCheckBox("نیاز به اعداد")
        self.chk_require_numbers.setChecked(True)
        
        self.chk_require_special = QCheckBox("نیاز به کاراکتر ویژه")
        self.chk_require_special.setChecked(False)
        
        password_layout.addRow("حداقل طول:", self.spn_min_length)
        password_layout.addRow("انقضای رمز:", self.spn_expiry_days)
        password_layout.addRow("تاریخچه رمز:", self.spn_history_count)
        password_layout.addRow("", self.chk_require_uppercase)
        password_layout.addRow("", self.chk_require_lowercase)
        password_layout.addRow("", self.chk_require_numbers)
        password_layout.addRow("", self.chk_require_special)
        
        password_group.setLayout(password_layout)
        layout.addWidget(password_group)
        
        # گروه تأیید دو مرحله‌ای
        twofa_group = QGroupBox("📱 تأیید دو مرحله‌ای (2FA)")
        twofa_layout = QFormLayout()
        
        self.chk_enable_2fa = QCheckBox("فعال‌سازی تأیید دو مرحله‌ای")
        self.chk_enable_2fa.setChecked(False)
        
        self.cmb_2fa_method = QComboBox()
        self.cmb_2fa_method.addItems(["پیامک", "ایمیل", "اپلیکیشن"])
        self.cmb_2fa_method.setEnabled(False)
        
        self.chk_2fa_force_admin = QCheckBox("اجباری برای مدیران")
        self.chk_2fa_force_admin.setChecked(True)
        self.chk_2fa_force_admin.setEnabled(False)
        
        self.chk_2fa_force_all = QCheckBox("اجباری برای همه کاربران")
        self.chk_2fa_force_all.setChecked(False)
        self.chk_2fa_force_all.setEnabled(False)
        
        twofa_layout.addRow("", self.chk_enable_2fa)
        twofa_layout.addRow("روش تأیید:", self.cmb_2fa_method)
        twofa_layout.addRow("", self.chk_2fa_force_admin)
        twofa_layout.addRow("", self.chk_2fa_force_all)
        
        # اتصال برای فعال‌سازی/غیرفعال‌سازی
        self.chk_enable_2fa.stateChanged.connect(
            lambda: self.toggle_2fa_widgets(self.chk_enable_2fa.isChecked())
        )
        
        twofa_group.setLayout(twofa_layout)
        layout.addWidget(twofa_group)
        
        self.authentication_tab.setLayout(layout)
    
    def setup_encryption_tab(self):
        """تنظیم تب رمزگذاری"""
        layout = QVBoxLayout()
        
        # گروه رمزگذاری داده‌ها
        data_encryption_group = QGroupBox("🔐 رمزگذاری داده‌های حساس")
        data_layout = QFormLayout()
        
        self.chk_encrypt_passwords = QCheckBox("رمزگذاری رمزهای عبور")
        self.chk_encrypt_passwords.setChecked(True)
        
        self.chk_encrypt_financial = QCheckBox("رمزگذاری اطلاعات مالی")
        self.chk_encrypt_financial.setChecked(True)
        
        self.chk_encrypt_personal = QCheckBox("رمزگذاری اطلاعات شخصی")
        self.chk_encrypt_personal.setChecked(False)
        
        self.chk_encrypt_backups = QCheckBox("رمزگذاری پشتیبان‌ها")
        self.chk_encrypt_backups.setChecked(True)
        
        self.txt_encryption_key = QLineEdit()
        self.txt_encryption_key.setPlaceholderText("کلید اصلی رمزگذاری")
        self.txt_encryption_key.setEchoMode(QLineEdit.Password)
        
        self.btn_generate_key = QPushButton("🎲 تولید کلید جدید")
        self.btn_generate_key.clicked.connect(self.generate_encryption_key)
        
        key_layout = QHBoxLayout()
        key_layout.addWidget(self.txt_encryption_key)
        key_layout.addWidget(self.btn_generate_key)
        
        data_layout.addRow("", self.chk_encrypt_passwords)
        data_layout.addRow("", self.chk_encrypt_financial)
        data_layout.addRow("", self.chk_encrypt_personal)
        data_layout.addRow("", self.chk_encrypt_backups)
        data_layout.addRow("کلید رمزگذاری:", key_layout)
        
        data_encryption_group.setLayout(data_layout)
        layout.addWidget(data_encryption_group)
        
        # گروه امنیت شبکه
        network_group = QGroupBox("🌐 امنیت شبکه")
        network_layout = QFormLayout()
        
        self.chk_ssl_required = QCheckBox("نیاز به اتصال امن (SSL)")
        self.chk_ssl_required.setChecked(False)
        
        self.chk_block_external = QCheckBox("مسدود کردن دسترسی خارجی")
        self.chk_block_external.setChecked(True)
        
        self.spn_firewall_level = QComboBox()
        self.spn_firewall_level.addItems(["پایین", "متوسط", "بالا", "بسیار بالا"])
        self.spn_firewall_level.setCurrentIndex(1)
        
        self.txt_allowed_ips = QTextEdit()
        self.txt_allowed_ips.setMaximumHeight(80)
        self.txt_allowed_ips.setPlaceholderText("هر IP در یک خط\nمثال:\n192.168.1.*\n10.0.0.0/24")
        
        network_layout.addRow("", self.chk_ssl_required)
        network_layout.addRow("", self.chk_block_external)
        network_layout.addRow("سطح فایروال:", self.spn_firewall_level)
        network_layout.addRow("IP های مجاز:", self.txt_allowed_ips)
        
        network_group.setLayout(network_layout)
        layout.addWidget(network_group)
        
        # گروه تنظیمات پیشرفته
        advanced_group = QGroupBox("⚙️ تنظیمات پیشرفته امنیتی")
        advanced_layout = QFormLayout()
        
        self.chk_audit_log = QCheckBox("فعال‌سازی لاگ حسابرسی")
        self.chk_audit_log.setChecked(True)
        
        self.chk_auto_logout = QCheckBox("خروج خودکار در صورت عدم فعالیت")
        self.chk_auto_logout.setChecked(True)
        
        self.spn_inactivity_time = QSpinBox()
        self.spn_inactivity_time.setRange(1, 60)
        self.spn_inactivity_time.setValue(10)
        self.spn_inactivity_time.setSuffix(" دقیقه")
        
        self.chk_show_security_warnings = QCheckBox("نمایش هشدارهای امنیتی")
        self.chk_show_security_warnings.setChecked(True)
        
        advanced_layout.addRow("", self.chk_audit_log)
        advanced_layout.addRow("", self.chk_auto_logout)
        advanced_layout.addRow("زمان عدم فعالیت:", self.spn_inactivity_time)
        advanced_layout.addRow("", self.chk_show_security_warnings)
        
        advanced_group.setLayout(advanced_layout)
        layout.addWidget(advanced_group)
        
        # دکمه تست امنیت
        self.btn_test_security = QPushButton("🔍 تست امنیت سیستم")
        self.btn_test_security.clicked.connect(self.test_security)
        layout.addWidget(self.btn_test_security, 0, Qt.AlignRight)
        
        self.encryption_tab.setLayout(layout)
    
    def setup_activity_tab(self):
        """تنظیم تب لاگ فعالیت"""
        layout = QVBoxLayout()
        
        # نوار ابزار
        toolbar = QHBoxLayout()
        
        self.date_from = QDateTimeEdit()
        self.date_from.setDateTime(QDateTime.currentDateTime().addDays(-7))
        self.date_from.setDisplayFormat("yyyy/MM/dd HH:mm")
        
        self.date_to = QDateTimeEdit()
        self.date_to.setDateTime(QDateTime.currentDateTime())
        self.date_to.setDisplayFormat("yyyy/MM/dd HH:mm")
        
        self.cmb_user_filter = QComboBox()
        self.cmb_user_filter.addItem("همه کاربران")
        self.cmb_user_filter.addItems(["admin", "accountant", "inventory", "operator1"])
        
        self.cmb_action_filter = QComboBox()
        self.cmb_action_filter.addItem("همه اقدامات")
        self.cmb_action_filter.addItems(["ورود", "خروج", "ایجاد", "ویرایش", "حذف", "خواندن"])
        
        self.btn_filter = QPushButton("🔍 فیلتر")
        self.btn_filter.clicked.connect(self.filter_activity_log)
        
        self.btn_export_log = QPushButton("📤 خروجی لاگ")
        self.btn_clear_log = QPushButton("🧹 پاکسازی لاگ")
        
        toolbar.addWidget(QLabel("از:"))
        toolbar.addWidget(self.date_from)
        toolbar.addWidget(QLabel("تا:"))
        toolbar.addWidget(self.date_to)
        toolbar.addWidget(self.cmb_user_filter)
        toolbar.addWidget(self.cmb_action_filter)
        toolbar.addWidget(self.btn_filter)
        toolbar.addWidget(self.btn_export_log)
        toolbar.addWidget(self.btn_clear_log)
        
        layout.addLayout(toolbar)
        
        # جدول لاگ فعالیت
        self.table_activity = QTableWidget()
        self.table_activity.setColumnCount(6)
        self.table_activity.setHorizontalHeaderLabels([
            "تاریخ", "کاربر", "اقدام", "جدول", "رکورد", "جزئیات"
        ])
        
        # تنظیمات جدول
        self.table_activity.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table_activity.setEditTriggers(QTableWidget.NoEditTriggers)
        
        layout.addWidget(self.table_activity)
        
        # آمار
        stats_layout = QHBoxLayout()
        
        self.lbl_total_logs = QLabel("تعداد رکوردها: 0")
        self.lbl_today_logs = QLabel("امروز: 0")
        self.lbl_security_events = QLabel("رویدادهای امنیتی: 0")
        
        stats_layout.addWidget(self.lbl_total_logs)
        stats_layout.addWidget(self.lbl_today_logs)
        stats_layout.addWidget(self.lbl_security_events)
        stats_layout.addStretch()
        
        layout.addLayout(stats_layout)
        self.activity_tab.setLayout(layout)
    
    def apply_styles(self):
        """اعمال استایل"""
        self.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 12pt;
                color: #e74c3c;
                border: 2px solid #e74c3c;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                padding: 0 10px;
            }
            QLineEdit, QComboBox, QSpinBox, QTextEdit, QDateTimeEdit {
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
    
    def toggle_2fa_widgets(self, enabled):
        """فعال/غیرفعال کردن ویجت‌های تأیید دو مرحله‌ای"""
        self.cmb_2fa_method.setEnabled(enabled)
        self.chk_2fa_force_admin.setEnabled(enabled)
        self.chk_2fa_force_all.setEnabled(enabled)
    
    def generate_encryption_key(self):
        """تولید کلید رمزگذاری جدید"""
        import secrets
        import string
        
        # تولید کلید 32 کاراکتری
        alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
        key = ''.join(secrets.choice(alphabet) for _ in range(32))
        
        self.txt_encryption_key.setText(key)
        
        QMessageBox.information(
            self,
            "کلید جدید",
            "کلید رمزگذاری جدید تولید شد.\n"
            "این کلید را در جای امنی ذخیره کنید."
        )
    
    def test_security(self):
        """تست امنیت سیستم"""
        import time
        
        # شبیه‌سازی تست امنیت
        self.btn_test_security.setText("در حال تست...")
        self.btn_test_security.setEnabled(False)
        
        # شبیه‌سازی تاخیر
        time.sleep(2)
        
        # نتایج تست
        results = [
            ("✅", "رمزهای عبور رمزگذاری شده‌اند"),
            ("✅", "لاگ فعالیت فعال است"),
            ("⚠️", "تأیید دو مرحله‌ای غیرفعال است"),
            ("✅", "فایروال روی سطح متوسط است"),
            ("❌", "اتصال SSL فعال نیست"),
            ("✅", "سیاست رمز عبور قوی است"),
        ]
        
        # نمایش نتایج
        result_text = "نتایج تست امنیت:\n\n"
        for status, message in results:
            result_text += f"{status} {message}\n"
        
        QMessageBox.information(self, "نتایج تست امنیت", result_text)
        
        self.btn_test_security.setText("🔍 تست امنیت سیستم")
        self.btn_test_security.setEnabled(True)
    
    def filter_activity_log(self):
        """فیلتر لاگ فعالیت"""
        QMessageBox.information(self, "فیلتر", "لاگ فعالیت بر اساس فیلترها نمایش داده شد.")
        self.load_activity_log()
    
    def load_activity_log(self):
        """بارگذاری لاگ فعالیت"""
        # نمونه داده‌های ساختگی
        logs = [
            ["۱۴۰۳/۱۰/۱۵ ۱۲:۳۰", "admin", "ورود", "", "", "ورود موفق از IP: 192.168.1.100"],
            ["۱۴۰۳/۱۰/۱۵ ۱۲:۳۵", "admin", "ایجاد", "Persons", "125", "ایجاد شخص جدید: احمدی"],
            ["۱۴۰۳/۱۰/۱۵ ۱۳:۱۵", "accountant", "ورود", "", "", "ورود موفق از IP: 192.168.1.101"],
            ["۱۴۰۳/۱۰/۱۵ ۱۳:۲۰", "accountant", "ویرایش", "Invoices", "45", "ویرایش فاکتور شماره ۱۰۱"],
            ["۱۴۰۳/۱۰/۱۵ ۱۴:۰۰", "inventory", "ورود", "", "", "ورود موفق از IP: 192.168.1.102"],
            ["۱۴۰۳/۱۰/۱۵ ۱۴:۱۰", "inventory", "خواندن", "Inventory", "", "مشاهده گزارش موجودی"],
            ["۱۴۰۳/۱۰/۱۵ ۱۴:۳۰", "operator1", "ورود", "", "", "ورود ناموفق از IP: 192.168.1.103"],
            ["۱۴۰۳/۱۰/۱۵ ۱۴:۳۱", "operator1", "ورود", "", "", "ورود موفق از IP: 192.168.1.103"],
            ["۱۴۰۳/۱۰/۱۵ ۱۵:۰۰", "admin", "خروج", "", "", "خروج از سیستم"],
            ["۱۴۰۳/۱۰/۱۵ ۱۵:۳۰", "admin", "حذف", "Devices", "78", "حذف دستگاه قدیمی"],
        ]
        
        self.table_activity.setRowCount(len(logs))
        
        for row, log in enumerate(logs):
            for col, value in enumerate(log):
                item = QTableWidgetItem(value)
                item.setTextAlignment(Qt.AlignCenter)
                
                # رنگ‌بندی بر اساس نوع اقدام
                if col == 2:  # ستون اقدام
                    if value == "ورود ناموفق":
                        item.setForeground(Qt.red)
                    elif value == "حذف":
                        item.setForeground(Qt.yellow)
                    elif value == "ایجاد":
                        item.setForeground(Qt.green)
                
                self.table_activity.setItem(row, col, item)
        
        # به‌روزرسانی آمار
        self.lbl_total_logs.setText(f"تعداد رکوردها: {len(logs)}")
        self.lbl_today_logs.setText("امروز: ۱۰")
        self.lbl_security_events.setText("رویدادهای امنیتی: ۱")
    
    def load_settings(self, settings_data):
        """بارگذاری تنظیمات"""
        try:
            # تنظیمات ورود
            self.spn_max_attempts.setValue(settings_data.get('max_login_attempts', 3))
            self.spn_lockout_time.setValue(settings_data.get('lockout_minutes', 15))
            self.spn_session_timeout.setValue(settings_data.get('session_timeout', 30))
            self.chk_force_logout.setChecked(settings_data.get('force_logout', True))
            self.chk_remember_me.setChecked(settings_data.get('remember_me', True))
            
            # سیاست رمز عبور
            self.spn_min_length.setValue(settings_data.get('min_password_length', 8))
            self.spn_expiry_days.setValue(settings_data.get('password_expiry_days', 90))
            self.spn_history_count.setValue(settings_data.get('password_history', 5))
            self.chk_require_uppercase.setChecked(settings_data.get('require_uppercase', True))
            self.chk_require_lowercase.setChecked(settings_data.get('require_lowercase', True))
            self.chk_require_numbers.setChecked(settings_data.get('require_numbers', True))
            self.chk_require_special.setChecked(settings_data.get('require_special', False))
            
            # تأیید دو مرحله‌ای
            self.chk_enable_2fa.setChecked(settings_data.get('enable_2fa', False))
            self.toggle_2fa_widgets(settings_data.get('enable_2fa', False))
            
            method = settings_data.get('2fa_method', 'پیامک')
            method_index = self.cmb_2fa_method.findText(method)
            if method_index >= 0:
                self.cmb_2fa_method.setCurrentIndex(method_index)
            
            self.chk_2fa_force_admin.setChecked(settings_data.get('2fa_force_admin', True))
            self.chk_2fa_force_all.setChecked(settings_data.get('2fa_force_all', False))
            
            # رمزگذاری
            self.chk_encrypt_passwords.setChecked(settings_data.get('encrypt_passwords', True))
            self.chk_encrypt_financial.setChecked(settings_data.get('encrypt_financial', True))
            self.chk_encrypt_personal.setChecked(settings_data.get('encrypt_personal', False))
            self.chk_encrypt_backups.setChecked(settings_data.get('encrypt_backups', True))
            self.txt_encryption_key.setText(settings_data.get('encryption_key', ''))
            
            # امنیت شبکه
            self.chk_ssl_required.setChecked(settings_data.get('ssl_required', False))
            self.chk_block_external.setChecked(settings_data.get('block_external', True))
            
            firewall_level = settings_data.get('firewall_level', 'متوسط')
            firewall_index = self.spn_firewall_level.findText(firewall_level)
            if firewall_index >= 0:
                self.spn_firewall_level.setCurrentIndex(firewall_level)
            
            self.txt_allowed_ips.setText(settings_data.get('allowed_ips', ''))
            
            # تنظیمات پیشرفته
            self.chk_audit_log.setChecked(settings_data.get('audit_log', True))
            self.chk_auto_logout.setChecked(settings_data.get('auto_logout', True))
            self.spn_inactivity_time.setValue(settings_data.get('inactivity_minutes', 10))
            self.chk_show_security_warnings.setChecked(settings_data.get('show_warnings', True))
            
        except Exception as e:
            print(f"خطا در بارگذاری تنظیمات امنیتی: {e}")
    
    def get_settings(self):
        """جمع‌آوری تنظیمات"""
        settings = {
            # تنظیمات ورود
            'max_login_attempts': self.spn_max_attempts.value(),
            'lockout_minutes': self.spn_lockout_time.value(),
            'session_timeout': self.spn_session_timeout.value(),
            'force_logout': self.chk_force_logout.isChecked(),
            'remember_me': self.chk_remember_me.isChecked(),
            
            # سیاست رمز عبور
            'min_password_length': self.spn_min_length.value(),
            'password_expiry_days': self.spn_expiry_days.value(),
            'password_history': self.spn_history_count.value(),
            'require_uppercase': self.chk_require_uppercase.isChecked(),
            'require_lowercase': self.chk_require_lowercase.isChecked(),
            'require_numbers': self.chk_require_numbers.isChecked(),
            'require_special': self.chk_require_special.isChecked(),
            
            # تأیید دو مرحله‌ای
            'enable_2fa': self.chk_enable_2fa.isChecked(),
            '2fa_method': self.cmb_2fa_method.currentText(),
            '2fa_force_admin': self.chk_2fa_force_admin.isChecked(),
            '2fa_force_all': self.chk_2fa_force_all.isChecked(),
            
            # رمزگذاری
            'encrypt_passwords': self.chk_encrypt_passwords.isChecked(),
            'encrypt_financial': self.chk_encrypt_financial.isChecked(),
            'encrypt_personal': self.chk_encrypt_personal.isChecked(),
            'encrypt_backups': self.chk_encrypt_backups.isChecked(),
            'encryption_key': self.txt_encryption_key.text(),
            
            # امنیت شبکه
            'ssl_required': self.chk_ssl_required.isChecked(),
            'block_external': self.chk_block_external.isChecked(),
            'firewall_level': self.spn_firewall_level.currentText(),
            'allowed_ips': self.txt_allowed_ips.toPlainText(),
            
            # تنظیمات پیشرفته
            'audit_log': self.chk_audit_log.isChecked(),
            'auto_logout': self.chk_auto_logout.isChecked(),
            'inactivity_minutes': self.spn_inactivity_time.value(),
            'show_warnings': self.chk_show_security_warnings.isChecked(),
        }
        
        return settings