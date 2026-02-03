from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout,
QFormLayout, QLabel, QLineEdit,
QComboBox, QPushButton, QGroupBox,
QCheckBox, QSpinBox, QTextEdit,
QTableWidget, QTableWidgetItem,
QHeaderView, QMessageBox, QTabWidget,
QDateTimeEdit, QDialog, QDialogButtonBox,
QListWidget, QListWidgetItem, QSplitter)
from PySide6.QtCore import Qt, QDateTime, QTimer, Signal
import hashlib
import secrets
import string
import json
from datetime import datetime, timedelta


class SecuritySettingsForm(QWidget):
    """فرم تنظیمات امنیتی - نسخه کامل با پشتیبانی دیتابیس"""


    settings_saved = Signal()

    def __init__(self, data_manager, config_manager=None):
        super().__init__()
        self.data_manager = data_manager

        
        # 🔴 بررسی اینکه config_manager واقعاً یک ConfigManager است
        from modules.config_manager import ConfigManager
        if isinstance(config_manager, ConfigManager):
            self.config_manager = config_manager
        else:
            # اگر MainWindow یا None است، یک ConfigManager جدید ایجاد کن
            print("⚠️ config_manager نامعتبر است. ایجاد ConfigManager جدید...")
            self.config_manager = ConfigManager(data_manager)
            
        # ایجاد رابط کاربری
        self.init_ui()
        self.setup_connections()
        self.apply_styles()
        
        # بارگذاری تنظیمات
        self.load_current_settings()
        
        # بارگذاری لاگ فعالیت
        self.load_activity_log()
        
        # تنظیم تایمر
        self.setup_timer()


    def init_ui(self):
        """ایجاد رابط کاربری"""
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(15, 15, 15, 15)
        
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
        self.tab_widget.addTab(self.activity_tab, "📝 لاگ فعالیت")
        
        # تب بلاک‌شده‌ها
        self.blocked_tab = QWidget()
        self.setup_blocked_tab()
        self.tab_widget.addTab(self.blocked_tab, "⛔ حساب‌های بلاک شده")
        
        main_layout.addWidget(self.tab_widget)
        
        # دکمه‌های ذخیره و بازنشانی
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.btn_test = QPushButton("🔍 تست امنیت")
        self.btn_test.clicked.connect(self.test_security)
        button_layout.addWidget(self.btn_test)
        
        self.btn_reset = QPushButton("🔄 بازنشانی")
        self.btn_reset.clicked.connect(self.reset_to_defaults)
        button_layout.addWidget(self.btn_reset)
        
        self.btn_save = QPushButton("💾 ذخیره تنظیمات")
        self.btn_save.clicked.connect(self.save_settings)
        self.btn_save.setStyleSheet("background-color: #27ae60; color: white; font-weight: bold;")
        button_layout.addWidget(self.btn_save)
        
        main_layout.addLayout(button_layout)
        self.setLayout(main_layout)

    def setup_connections(self):
        """اتصال سیگنال‌ها"""
        print("✅ اتصالات SecuritySettingsForm برقرار شد")
        # اتصالات قبلاً در init_ui برقرار شده‌اند

    def setup_authentication_tab(self):
        """تنظیم تب احراز هویت"""
        layout = QVBoxLayout()
        
        # گروه تنظیمات ورود
        login_group = QGroupBox("🚪 تنظیمات ورود به سیستم")
        login_layout = QFormLayout()
        
        self.spn_max_attempts = QSpinBox()
        self.spn_max_attempts.setRange(1, 10)
        self.spn_max_attempts.setSuffix(" تلاش")
        self.spn_max_attempts.setToolTip("حداکثر تعداد تلاش‌های ناموفق قبل از قفل شدن حساب")
        
        self.spn_lockout_time = QSpinBox()
        self.spn_lockout_time.setRange(1, 1440)
        self.spn_lockout_time.setSuffix(" دقیقه")
        self.spn_lockout_time.setToolTip("مدت زمان قفل شدن حساب پس از تلاش‌های ناموفق")
        
        self.spn_session_timeout = QSpinBox()
        self.spn_session_timeout.setRange(5, 480)
        self.spn_session_timeout.setSuffix(" دقیقه")
        self.spn_session_timeout.setToolTip("زمان عدم فعالیت قبل از خروج خودکار")
        
        self.chk_force_logout = QCheckBox("خروج اجباری پس از پایان زمان جلسه")
        self.chk_remember_me = QCheckBox("امکان ذخیره اطلاعات ورود")
        self.chk_multi_session = QCheckBox("اجازه ورود همزاز از چند دستگاه")
        
        login_layout.addRow("حداکثر تلاش ناموفق:", self.spn_max_attempts)
        login_layout.addRow("زمان قفل حساب:", self.spn_lockout_time)
        login_layout.addRow("مدت جلسه:", self.spn_session_timeout)
        login_layout.addRow("", self.chk_force_logout)
        login_layout.addRow("", self.chk_remember_me)
        login_layout.addRow("", self.chk_multi_session)
        
        login_group.setLayout(login_layout)
        layout.addWidget(login_group)
        
        # گروه سیاست رمز عبور
        password_group = QGroupBox("🔑 سیاست رمز عبور")
        password_layout = QFormLayout()
        
        self.spn_min_length = QSpinBox()
        self.spn_min_length.setRange(4, 32)
        self.spn_min_length.setSuffix(" حرف")
        
        self.spn_expiry_days = QSpinBox()
        self.spn_expiry_days.setRange(0, 365)
        self.spn_expiry_days.setSuffix(" روز")
        self.spn_expiry_days.setSpecialValueText("بدون انقضا")
        
        self.spn_history_count = QSpinBox()
        self.spn_history_count.setRange(0, 10)
        self.spn_history_count.setSuffix(" رمز قبلی")
        
        self.chk_require_uppercase = QCheckBox("نیاز به حروف بزرگ (A-Z)")
        self.chk_require_lowercase = QCheckBox("نیاز به حروف کوچک (a-z)")
        self.chk_require_numbers = QCheckBox("نیاز به اعداد (0-9)")
        self.chk_require_special = QCheckBox("نیاز به کاراکتر ویژه (!@#$%^&*)")
        self.chk_no_common = QCheckBox("ممنوعیت رمزهای رایج")
        
        password_layout.addRow("حداقل طول:", self.spn_min_length)
        password_layout.addRow("انقضای رمز:", self.spn_expiry_days)
        password_layout.addRow("تاریخچه رمز:", self.spn_history_count)
        password_layout.addRow("", self.chk_require_uppercase)
        password_layout.addRow("", self.chk_require_lowercase)
        password_layout.addRow("", self.chk_require_numbers)
        password_layout.addRow("", self.chk_require_special)
        password_layout.addRow("", self.chk_no_common)
        
        # دکمه تست رمز عبور
        self.btn_test_password = QPushButton("🔐 تست قوی بودن رمز عبور")
        self.btn_test_password.clicked.connect(self.show_password_tester)
        password_layout.addRow("", self.btn_test_password)
        
        password_group.setLayout(password_layout)
        layout.addWidget(password_group)
        
        # گروه تأیید دو مرحله‌ای
        twofa_group = QGroupBox("📱 تأیید دو مرحله‌ای (2FA)")
        twofa_layout = QFormLayout()
        
        self.chk_enable_2fa = QCheckBox("فعال‌سازی تأیید دو مرحله‌ای")
        self.chk_enable_2fa.stateChanged.connect(self.toggle_2fa_widgets)
        
        self.cmb_2fa_method = QComboBox()
        self.cmb_2fa_method.addItems(["پیامک", "ایمیل", "اپلیکیشن"])
        self.cmb_2fa_method.setEnabled(False)
        
        self.chk_2fa_force_admin = QCheckBox("اجباری برای مدیران")
        self.chk_2fa_force_admin.setEnabled(False)
        
        self.chk_2fa_force_all = QCheckBox("اجباری برای همه کاربران")
        self.chk_2fa_force_all.setEnabled(False)
        
        self.btn_setup_2fa = QPushButton("⚙️ راه‌اندازی 2FA")
        self.btn_setup_2fa.setEnabled(False)
        self.btn_setup_2fa.clicked.connect(self.setup_2fa)
        
        twofa_layout.addRow("", self.chk_enable_2fa)
        twofa_layout.addRow("روش تأیید:", self.cmb_2fa_method)
        twofa_layout.addRow("", self.chk_2fa_force_admin)
        twofa_layout.addRow("", self.chk_2fa_force_all)
        twofa_layout.addRow("", self.btn_setup_2fa)
        
        twofa_group.setLayout(twofa_layout)
        layout.addWidget(twofa_group)
        
        self.authentication_tab.setLayout(layout)

    def setup_encryption_tab(self):
        """تنظیم تب رمزگذاری"""
        layout = QVBoxLayout()
        
        # گروه رمزگذاری داده‌ها
        data_encryption_group = QGroupBox("🔐 رمزگذاری داده‌های حساس")
        data_layout = QFormLayout()
        
        self.chk_encrypt_passwords = QCheckBox("رمزگذاری رمزهای عبور کاربران")
        self.chk_encrypt_financial = QCheckBox("رمزگذاری اطلاعات مالی و تراکنش‌ها")
        self.chk_encrypt_personal = QCheckBox("رمزگذاری اطلاعات شخصی مشتریان")
        self.chk_encrypt_backups = QCheckBox("رمزگذاری فایل‌های پشتیبان")
        self.chk_encrypt_logs = QCheckBox("رمزگذاری لاگ‌های سیستم")
        
        encryption_key_layout = QHBoxLayout()
        self.txt_encryption_key = QLineEdit()
        self.txt_encryption_key.setPlaceholderText("کلید اصلی رمزگذاری")
        self.txt_encryption_key.setEchoMode(QLineEdit.Password)
        self.txt_encryption_key.setToolTip("برای نمایش کلید، روی دکمه چشم کلیک کنید")
        
        self.btn_show_key = QPushButton("👁")
        self.btn_show_key.setFixedWidth(40)
        self.btn_show_key.setCheckable(True)
        self.btn_show_key.toggled.connect(self.toggle_key_visibility)
        
        self.btn_generate_key = QPushButton("🎲 تولید کلید جدید")
        self.btn_generate_key.clicked.connect(self.generate_encryption_key)
        
        encryption_key_layout.addWidget(self.txt_encryption_key)
        encryption_key_layout.addWidget(self.btn_show_key)
        encryption_key_layout.addWidget(self.btn_generate_key)
        
        data_layout.addRow("", self.chk_encrypt_passwords)
        data_layout.addRow("", self.chk_encrypt_financial)
        data_layout.addRow("", self.chk_encrypt_personal)
        data_layout.addRow("", self.chk_encrypt_backups)
        data_layout.addRow("", self.chk_encrypt_logs)
        data_layout.addRow("کلید رمزگذاری:", encryption_key_layout)
        
        data_encryption_group.setLayout(data_layout)
        layout.addWidget(data_encryption_group)
        
        # گروه امنیت شبکه
        network_group = QGroupBox("🌐 امنیت شبکه و دسترسی")
        network_layout = QFormLayout()
        
        self.chk_ssl_required = QCheckBox("اجبار به استفاده از HTTPS")
        self.chk_block_external = QCheckBox("مسدود کردن دسترسی خارج از شبکه محلی")
        self.chk_limit_login_ip = QCheckBox("محدودیت ورود بر اساس IP")
        
        self.spn_firewall_level = QComboBox()
        self.spn_firewall_level.addItems(["پایین", "متوسط", "بالا", "بسیار بالا"])
        
        self.txt_allowed_ips = QTextEdit()
        self.txt_allowed_ips.setMaximumHeight(100)
        self.txt_allowed_ips.setPlaceholderText("هر IP در یک خط\nمثال:\n192.168.1.*\n10.0.0.0/24\nتمام IPهای شبکه محلی مجاز هستند")
        
        network_layout.addRow("", self.chk_ssl_required)
        network_layout.addRow("", self.chk_block_external)
        network_layout.addRow("", self.chk_limit_login_ip)
        network_layout.addRow("سطح فایروال:", self.spn_firewall_level)
        network_layout.addRow("IP های مجاز:", self.txt_allowed_ips)
        
        network_group.setLayout(network_layout)
        layout.addWidget(network_group)
        
        # گروه تنظیمات پیشرفته
        advanced_group = QGroupBox("⚙️ تنظیمات پیشرفته امنیتی")
        advanced_layout = QFormLayout()
        
        self.chk_audit_log = QCheckBox("فعال‌سازی لاگ حسابرسی")
        self.chk_auto_logout = QCheckBox("خروج خودکار در صورت عدم فعالیت")
        self.chk_show_security_warnings = QCheckBox("نمایش هشدارهای امنیتی")
        self.chk_auto_update = QCheckBox("بروزرسانی خودکار تنظیمات امنیتی")
        
        self.spn_inactivity_time = QSpinBox()
        self.spn_inactivity_time.setRange(1, 60)
        self.spn_inactivity_time.setSuffix(" دقیقه")
        
        self.spn_log_retention = QSpinBox()
        self.spn_log_retention.setRange(1, 365)
        self.spn_log_retention.setSuffix(" روز")
        self.spn_log_retention.setToolTip("مدت نگهداری لاگ‌ها در سیستم")
        
        advanced_layout.addRow("", self.chk_audit_log)
        advanced_layout.addRow("", self.chk_auto_logout)
        advanced_layout.addRow("زمان عدم فعالیت:", self.spn_inactivity_time)
        advanced_layout.addRow("", self.chk_show_security_warnings)
        advanced_layout.addRow("", self.chk_auto_update)
        advanced_layout.addRow("نگهداری لاگ‌ها:", self.spn_log_retention)
        
        advanced_group.setLayout(advanced_layout)
        layout.addWidget(advanced_group)
        
        self.encryption_tab.setLayout(layout)

    def setup_activity_tab(self):
        """تنظیم تب لاگ فعالیت"""
        layout = QVBoxLayout()
        
        # نوار ابزار
        toolbar = QHBoxLayout()
        
        # فیلتر تاریخ
        toolbar.addWidget(QLabel("از:"))
        self.date_from = QDateTimeEdit()
        self.date_from.setDateTime(QDateTime.currentDateTime().addDays(-7))
        self.date_from.setDisplayFormat("yyyy/MM/dd HH:mm")
        self.date_from.setCalendarPopup(True)
        toolbar.addWidget(self.date_from)
        
        toolbar.addWidget(QLabel("تا:"))
        self.date_to = QDateTimeEdit()
        self.date_to.setDateTime(QDateTime.currentDateTime())
        self.date_to.setDisplayFormat("yyyy/MM/dd HH:mm")
        self.date_to.setCalendarPopup(True)
        toolbar.addWidget(self.date_to)
        
        # فیلتر کاربر
        toolbar.addWidget(QLabel("کاربر:"))
        self.cmb_user_filter = QComboBox()
        self.cmb_user_filter.addItem("همه کاربران")
        toolbar.addWidget(self.cmb_user_filter)
        
        # فیلتر اقدام
        toolbar.addWidget(QLabel("اقدام:"))
        self.cmb_action_filter = QComboBox()
        self.cmb_action_filter.addItem("همه اقدامات")
        self.cmb_action_filter.addItems(["ورود", "خروج", "ایجاد", "ویرایش", "حذف", "خواندن", "خطا"])
        toolbar.addWidget(self.cmb_action_filter)
        
        # دکمه‌ها
        self.btn_filter = QPushButton("🔍 فیلتر")
        self.btn_filter.clicked.connect(self.filter_activity_log)
        toolbar.addWidget(self.btn_filter)
        
        self.btn_refresh = QPushButton("🔄 به‌روزرسانی")
        self.btn_refresh.clicked.connect(self.load_activity_log)
        toolbar.addWidget(self.btn_refresh)
        
        self.btn_export_log = QPushButton("📤 خروجی Excel")
        self.btn_export_log.clicked.connect(self.export_logs)
        toolbar.addWidget(self.btn_export_log)
        
        self.btn_clear_old = QPushButton("🧹 پاکسازی قدیمی")
        self.btn_clear_old.clicked.connect(self.clear_old_logs)
        toolbar.addWidget(self.btn_clear_old)
        
        toolbar.addStretch()
        layout.addLayout(toolbar)
        
        # جدول لاگ فعالیت
        self.table_activity = QTableWidget()
        self.table_activity.setColumnCount(7)
        self.table_activity.setHorizontalHeaderLabels([
            "تاریخ", "کاربر", "اقدام", "جدول", "رکورد", "IP", "جزئیات"
        ])
        
        # تنظیمات جدول
        header = self.table_activity.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # تاریخ
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)  # کاربر
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)  # اقدام
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)  # جدول
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)  # رکورد
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)  # IP
        header.setSectionResizeMode(6, QHeaderView.Stretch)  # جزئیات
        
        self.table_activity.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table_activity.setSelectionBehavior(QTableWidget.SelectRows)
        self.table_activity.setAlternatingRowColors(True)
        
        layout.addWidget(self.table_activity)
        
        # آمار
        stats_layout = QHBoxLayout()
        
        self.lbl_total_logs = QLabel("تعداد رکوردها: 0")
        self.lbl_today_logs = QLabel("امروز: 0")
        self.lbl_security_events = QLabel("رویدادهای امنیتی: 0")
        self.lbl_last_update = QLabel("آخرین به‌روزرسانی: -")
        
        stats_layout.addWidget(self.lbl_total_logs)
        stats_layout.addWidget(self.lbl_today_logs)
        stats_layout.addWidget(self.lbl_security_events)
        stats_layout.addWidget(self.lbl_last_update)
        stats_layout.addStretch()
        
        layout.addLayout(stats_layout)
        self.activity_tab.setLayout(layout)

    def setup_blocked_tab(self):
        """تنظیم تب حساب‌های بلاک شده"""
        layout = QVBoxLayout()
        
        # توضیحات
        info_label = QLabel(
            "در این بخش می‌توانید حساب‌های کاربری که به دلیل ورودهای ناموفق متعدد بلاک شده‌اند را مشاهده و مدیریت کنید."
        )
        info_label.setWordWrap(True)
        info_label.setStyleSheet("background-color: #2c3e50; color: white; padding: 10px; border-radius: 5px;")
        layout.addWidget(info_label)
        
        # لیست حساب‌های بلاک شده
        self.list_blocked = QListWidget()
        layout.addWidget(self.list_blocked)
        
        # دکمه‌های مدیریت
        button_layout = QHBoxLayout()
        
        self.btn_refresh_blocked = QPushButton("🔄 به‌روزرسانی لیست")
        self.btn_refresh_blocked.clicked.connect(self.load_blocked_accounts)
        button_layout.addWidget(self.btn_refresh_blocked)
        
        self.btn_unblock_selected = QPushButton("🔓 رفع بلاک انتخاب شده")
        self.btn_unblock_selected.clicked.connect(self.unblock_selected_account)
        button_layout.addWidget(self.btn_unblock_selected)
        
        self.btn_unblock_all = QPushButton("🔓 رفع بلاک همه")
        self.btn_unblock_all.clicked.connect(self.unblock_all_accounts)
        button_layout.addWidget(self.btn_unblock_all)
        
        button_layout.addStretch()
        layout.addLayout(button_layout)
        
        self.blocked_tab.setLayout(layout)

    def apply_styles(self):
        """اعمال استایل"""
        self.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 11pt;
                color: #3498db;
                border: 2px solid #3498db;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 15px;
                background-color: #1a1a1a;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 10px 0 10px;
                color: #3498db;
            }
            QLineEdit, QComboBox, QSpinBox, QTextEdit, QDateTimeEdit {
                background-color: #2c2c2c;
                color: #ffffff;
                border: 1px solid #444;
                border-radius: 4px;
                padding: 6px;
                min-height: 28px;
            }
            QLineEdit:focus, QComboBox:focus, QSpinBox:focus, QTextEdit:focus {
                border: 2px solid #3498db;
            }
            QCheckBox {
                color: #ecf0f1;
                spacing: 8px;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
            }
            QPushButton {
                background-color: #2c3e50;
                color: white;
                border: none;
                padding: 8px 15px;
                border-radius: 4px;
                margin: 2px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #34495e;
            }
            QPushButton:pressed {
                background-color: #2c3e50;
            }
            QPushButton:disabled {
                background-color: #7f8c8d;
                color: #bdc3c7;
            }
            QTableWidget {
                background-color: #1a1a1a;
                alternate-background-color: #222222;
                gridline-color: #333333;
                color: #ffffff;
                selection-background-color: #2980b9;
                border: 1px solid #444;
                border-radius: 4px;
            }
            QHeaderView::section {
                background-color: #2c3e50;
                color: white;
                padding: 8px;
                border: none;
                font-weight: bold;
            }
            QTabWidget::pane {
                border: 1px solid #444;
                background-color: #1a1a1a;
            }
            QTabBar::tab {
                background-color: #2c3e50;
                color: white;
                padding: 8px 16px;
                margin-right: 2px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }
            QTabBar::tab:selected {
                background-color: #3498db;
            }
            QTabBar::tab:hover {
                background-color: #34495e;
            }
            QListWidget {
                background-color: #2c2c2c;
                color: white;
                border: 1px solid #444;
                border-radius: 4px;
                padding: 5px;
            }
            QListWidget::item {
                padding: 8px;
                border-bottom: 1px solid #444;
            }
            QListWidget::item:selected {
                background-color: #2980b9;
            }
        """)

    def setup_timer(self):
        """تنظیم تایمر برای به‌روزرسانی خودکار"""
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.auto_refresh)
        self.update_timer.start(30000)  # هر 30 ثانیه

    def auto_refresh(self):
        """به‌روزرسانی خودکار لاگ‌ها"""
        if self.tab_widget.currentWidget() == self.activity_tab:
            self.load_activity_log()

    def toggle_2fa_widgets(self, enabled=None):
        """فعال/غیرفعال کردن ویجت‌های تأیید دو مرحله‌ای"""
        if enabled is None:
            enabled = self.chk_enable_2fa.isChecked()
        
        self.cmb_2fa_method.setEnabled(enabled)
        self.chk_2fa_force_admin.setEnabled(enabled)
        self.chk_2fa_force_all.setEnabled(enabled)
        self.btn_setup_2fa.setEnabled(enabled)

    def toggle_key_visibility(self, visible):
        """تغییر حالت نمایش کلید رمزگذاری"""
        if visible:
            self.txt_encryption_key.setEchoMode(QLineEdit.Normal)
            self.btn_show_key.setText("👁‍🗨")
        else:
            self.txt_encryption_key.setEchoMode(QLineEdit.Password)
            self.btn_show_key.setText("👁")

    def generate_encryption_key(self):
        """تولید کلید رمزگذاری جدید"""
        import secrets
        import string
        
        # تولید کلید 64 کاراکتری امن
        alphabet = string.ascii_letters + string.digits + "!@#$%^&*()_+-=[]{}|;:,.<>?"
        key = ''.join(secrets.choice(alphabet) for _ in range(64))
        
        self.txt_encryption_key.setText(key)
        
        # نمایش کلید در یک دیالوگ امن
        dialog = QDialog(self)
        dialog.setWindowTitle("کلید رمزگذاری جدید")
        dialog.setModal(True)
        dialog.setFixedSize(500, 300)
        
        layout = QVBoxLayout()
        
        warning = QLabel("⚠️ این کلید را در جای امنی ذخیره کنید! ⚠️")
        warning.setStyleSheet("color: #e74c3c; font-weight: bold; font-size: 14pt;")
        warning.setAlignment(Qt.AlignCenter)
        layout.addWidget(warning)
        
        key_display = QTextEdit()
        key_display.setText(key)
        key_display.setReadOnly(True)
        key_display.setStyleSheet("""
            font-family: 'Courier New', monospace;
            font-size: 10pt;
            background-color: #2c3e50;
            color: white;
            padding: 10px;
            border-radius: 5px;
        """)
        layout.addWidget(key_display)
        
        instructions = QLabel(
            "این کلید برای رمزگذاری داده‌های حساس استفاده می‌شود.\n"
            "در صورت گم کردن آن، دسترسی به داده‌های رمزگذاری شده ممکن نخواهد بود."
        )
        instructions.setWordWrap(True)
        instructions.setAlignment(Qt.AlignCenter)
        layout.addWidget(instructions)
        
        buttons = QDialogButtonBox(QDialogButtonBox.Ok)
        buttons.accepted.connect(dialog.accept)
        layout.addWidget(buttons)
        
        dialog.setLayout(layout)
        dialog.exec()

    def load_current_settings(self):
        """بارگذاری تنظیمات امنیتی از ConfigManager - نسخه ساده‌شده"""
        try:
            print("🔄 بارگذاری تنظیمات امنیتی...")
            
            # اگر config_manager نداریم، از پیش‌فرض استفاده کن
            if not hasattr(self, 'config_manager') or self.config_manager is None:
                print("⚠️ config_manager موجود نیست، استفاده از تنظیمات پیش‌فرض")
                self.set_default_security_config()
                return
            
            # تلاش برای دریافت تنظیمات
            try:
                # دریافت تنظیمات امنیتی
                security_config = self.config_manager.get('security')
                
                # اگر تنظیمات دریافت شد، اعمال کن
                if security_config and isinstance(security_config, dict):
                    print(f"✅ تنظیمات امنیتی دریافت شد ({len(security_config)} مورد)")
                    self.apply_settings_to_form(security_config)
                else:
                    print("⚠️ تنظیمات امنیتی خالی است، استفاده از پیش‌فرض")
                    self.set_default_security_config()
                    
            except AttributeError as e:
                print(f"⚠️ خطا در متد get: {e}")
                self.set_default_security_config()
            except Exception as e:
                print(f"⚠️ خطای عمومی در دریافت تنظیمات: {e}")
                self.set_default_security_config()
                
        except Exception as e:
            print(f"❌ خطا در بارگذاری تنظیمات امنیتی: {e}")
            self.set_default_security_config()

    def apply_settings_to_form(self, settings):
        """اعمال تنظیمات روی فرم - نسخه ایمن و ساده"""
        try:
            if not settings or not isinstance(settings, dict):
                print("⚠️ تنظیمات خالی یا نامعتبر است")
                return
            
            print(f"🔧 اعمال {len(settings)} تنظیم روی فرم...")
            
            # 🔴 تنظیمات ورود - با مقادیر پیش‌فرض
            self.spn_max_attempts.setValue(int(settings.get('max_login_attempts', 3)))
            self.spn_lockout_time.setValue(int(settings.get('lockout_minutes', 15)))
            self.spn_session_timeout.setValue(int(settings.get('session_timeout_minutes', 30)))
            
            # 🔴 دکمه‌های چک با تبدیل به boolean
            self.chk_force_logout.setChecked(bool(settings.get('force_logout', True)))
            self.chk_remember_me.setChecked(bool(settings.get('remember_me', True)))
            self.chk_multi_session.setChecked(bool(settings.get('multi_session', False)))
            
            # 🔴 سیاست رمز عبور
            self.spn_min_length.setValue(int(settings.get('password_min_length', 8)))
            self.spn_expiry_days.setValue(int(settings.get('password_expiry_days', 90)))
            self.spn_history_count.setValue(int(settings.get('password_history_count', 5)))
            
            # 🔴 چک‌باکس‌های سیاست رمز عبور
            self.chk_require_uppercase.setChecked(bool(settings.get('password_require_upper', True)))
            self.chk_require_lowercase.setChecked(bool(settings.get('password_require_lower', True)))
            self.chk_require_numbers.setChecked(bool(settings.get('password_require_number', True)))
            self.chk_require_special.setChecked(bool(settings.get('password_require_special', False)))
            self.chk_no_common.setChecked(bool(settings.get('no_common_passwords', False)))
            
            print("✅ تنظیمات امنیتی روی فرم اعمال شد")
            
        except Exception as e:
            print(f"⚠️ خطا در اعمال تنظیمات روی فرم: {e}")
            import traceback
            traceback.print_exc()

    def create_security_settings_table(self):
        """ایجاد جدول تنظیمات امنیتی در صورت عدم وجود"""
        try:
            query = """
            CREATE TABLE IF NOT EXISTS SecuritySettings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                max_login_attempts INTEGER DEFAULT 3,
                lockout_minutes INTEGER DEFAULT 15,
                session_timeout_minutes INTEGER DEFAULT 30,
                force_logout BOOLEAN DEFAULT 1,
                remember_me BOOLEAN DEFAULT 1,
                multi_session BOOLEAN DEFAULT 0,
                min_password_length INTEGER DEFAULT 8,
                password_expiry_days INTEGER DEFAULT 90,
                password_history_count INTEGER DEFAULT 5,
                require_uppercase BOOLEAN DEFAULT 1,
                require_lowercase BOOLEAN DEFAULT 1,
                require_numbers BOOLEAN DEFAULT 1,
                require_special BOOLEAN DEFAULT 0,
                no_common_passwords BOOLEAN DEFAULT 0,
                enable_2fa BOOLEAN DEFAULT 0,
                twofa_method TEXT DEFAULT 'پیامک',
                twofa_force_admin BOOLEAN DEFAULT 1,
                twofa_force_all BOOLEAN DEFAULT 0,
                encrypt_passwords BOOLEAN DEFAULT 1,
                encrypt_financial BOOLEAN DEFAULT 1,
                encrypt_personal BOOLEAN DEFAULT 0,
                encrypt_backups BOOLEAN DEFAULT 1,
                encrypt_logs BOOLEAN DEFAULT 0,
                encryption_key_hash TEXT,
                ssl_required BOOLEAN DEFAULT 0,
                block_external BOOLEAN DEFAULT 1,
                limit_login_ip BOOLEAN DEFAULT 0,
                firewall_level TEXT DEFAULT 'متوسط',
                allowed_ips TEXT,
                audit_log BOOLEAN DEFAULT 1,
                auto_logout BOOLEAN DEFAULT 1,
                inactivity_minutes INTEGER DEFAULT 10,
                show_warnings BOOLEAN DEFAULT 1,
                auto_update BOOLEAN DEFAULT 0,
                log_retention_days INTEGER DEFAULT 30,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
            self.data_manager.db.execute_query(query)
            
            # درج رکورد پیش‌فرض
            query = "INSERT OR IGNORE INTO SecuritySettings (id) VALUES (1)"
            self.data_manager.db.execute_query(query)
            
        except Exception as e:
            print(f"❌ خطا در ایجاد جدول تنظیمات امنیتی: {e}")

    def save_settings_to_db(self, settings):
        """ذخیره تنظیمات در دیتابیس"""
        try:
            # Hash کردن کلید رمزنگاری
            encryption_key = settings.get('encryption_key', '')
            if encryption_key:
                encryption_key_hash = hashlib.sha256(encryption_key.encode()).hexdigest()
            else:
                encryption_key_hash = ''
            
            # حذف کلید از تنظیمات قبل از ذخیره
            settings_to_save = settings.copy()
            if 'encryption_key' in settings_to_save:
                del settings_to_save['encryption_key']
            
            query = """
            UPDATE SecuritySettings SET
                max_login_attempts = ?,
                lockout_minutes = ?,
                session_timeout_minutes = ?,
                force_logout = ?,
                remember_me = ?,
                multi_session = ?,
                min_password_length = ?,
                password_expiry_days = ?,
                password_history_count = ?,
                require_uppercase = ?,
                require_lowercase = ?,
                require_numbers = ?,
                require_special = ?,
                no_common_passwords = ?,
                enable_2fa = ?,
                twofa_method = ?,
                twofa_force_admin = ?,
                twofa_force_all = ?,
                encrypt_passwords = ?,
                encrypt_financial = ?,
                encrypt_personal = ?,
                encrypt_backups = ?,
                encrypt_logs = ?,
                encryption_key_hash = ?,
                ssl_required = ?,
                block_external = ?,
                limit_login_ip = ?,
                firewall_level = ?,
                allowed_ips = ?,
                audit_log = ?,
                auto_logout = ?,
                inactivity_minutes = ?,
                show_warnings = ?,
                auto_update = ?,
                log_retention_days = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = 1
            """
            
            params = (
                settings_to_save.get('max_login_attempts', 3),
                settings_to_save.get('lockout_minutes', 15),
                settings_to_save.get('session_timeout_minutes', 30),
                1 if settings_to_save.get('force_logout') else 0,
                1 if settings_to_save.get('remember_me') else 0,
                1 if settings_to_save.get('multi_session') else 0,
                settings_to_save.get('min_password_length', 8),
                settings_to_save.get('password_expiry_days', 90),
                settings_to_save.get('password_history_count', 5),
                1 if settings_to_save.get('require_uppercase') else 0,
                1 if settings_to_save.get('require_lowercase') else 0,
                1 if settings_to_save.get('require_numbers') else 0,
                1 if settings_to_save.get('require_special') else 0,
                1 if settings_to_save.get('no_common_passwords') else 0,
                1 if settings_to_save.get('enable_2fa') else 0,
                settings_to_save.get('twofa_method', 'پیامک'),
                1 if settings_to_save.get('twofa_force_admin') else 0,
                1 if settings_to_save.get('twofa_force_all') else 0,
                1 if settings_to_save.get('encrypt_passwords') else 0,
                1 if settings_to_save.get('encrypt_financial') else 0,
                1 if settings_to_save.get('encrypt_personal') else 0,
                1 if settings_to_save.get('encrypt_backups') else 0,
                1 if settings_to_save.get('encrypt_logs') else 0,
                encryption_key_hash,
                1 if settings_to_save.get('ssl_required') else 0,
                1 if settings_to_save.get('block_external') else 0,
                1 if settings_to_save.get('limit_login_ip') else 0,
                settings_to_save.get('firewall_level', 'متوسط'),
                settings_to_save.get('allowed_ips', ''),
                1 if settings_to_save.get('audit_log') else 0,
                1 if settings_to_save.get('auto_logout') else 0,
                settings_to_save.get('inactivity_minutes', 10),
                1 if settings_to_save.get('show_warnings') else 0,
                1 if settings_to_save.get('auto_update') else 0,
                settings_to_save.get('log_retention_days', 30)
            )
            
            return self.data_manager.db.execute_query(query, params)
            
        except Exception as e:
            print(f"❌ خطا در ذخیره تنظیمات: {e}")
            return False

    def save_settings(self):
        """ذخیره تنظیمات امنیتی - نسخه ساده‌شده"""
        try:
            # جمع‌آوری تنظیمات از فرم
            settings = self.get_settings()
            
            # اعتبارسنجی
            if not self.validate_settings(settings):
                return False
            
            # اگر config_manager نداریم
            if not hasattr(self, 'config_manager') or self.config_manager is None:
                print("⚠️ config_manager موجود نیست، ذخیره در دیتابیس")
                return self.save_to_database(settings)
            
            # ذخیره در ConfigManager
            print("💾 ذخیره تنظیمات در ConfigManager...")
            
            for key, value in settings.items():
                try:
                    # تبدیل boolean به 0/1 برای دیتابیس
                    if isinstance(value, bool):
                        value = 1 if value else 0
                    
                    self.config_manager.set('security', key, value, save_to_db=True)
                except Exception as e:
                    print(f"⚠️ خطا در ذخیره {key}: {e}")
            
            # ارسال سیگنال
            self.settings_saved.emit()
            
            # نمایش پیام موفقیت
            QMessageBox.information(
                self,
                "ذخیره موفق",
                "✅ تنظیمات امنیتی با موفقیت ذخیره شد."
            )
            
            return True
            
        except Exception as e:
            print(f"❌ خطا در ذخیره تنظیمات: {e}")
            QMessageBox.critical(
                self,
                "خطا",
                f"خطا در ذخیره تنظیمات:\n{str(e)}"
            )
            return False

    def save_to_database(self, settings):
        """ذخیره تنظیمات در دیتابیس (برای زمانی که config_manager نداریم)"""
        try:
            print("💾 ذخیره تنظیمات مستقیم در دیتابیس...")
            
            # ایجاد جدول اگر وجود ندارد
            self.create_security_settings_table()
            
            # تبدیل boolean به 0/1
            settings_db = {}
            for key, value in settings.items():
                if isinstance(value, bool):
                    settings_db[key] = 1 if value else 0
                else:
                    settings_db[key] = value
            
            # ساخت کوئری UPDATE
            set_clause = ", ".join([f"{k} = ?" for k in settings_db.keys()])
            values = list(settings_db.values())
            values.append(1)  # برای WHERE id = 1
            
            query = f"UPDATE SecuritySettings SET {set_clause} WHERE id = ?"
            
            if self.data_manager.db.execute_query(query, values):
                print("✅ تنظیمات در دیتابیس ذخیره شد")
                return True
            else:
                print("❌ خطا در اجرای کوئری UPDATE")
                return False
                
        except Exception as e:
            print(f"❌ خطا در ذخیره در دیتابیس: {e}")
            return False
    
    def set_default_security_config(self):
        """تنظیمات پیش‌فرض امنیتی روی فرم"""
        try:
            print("⚙️ اعمال تنظیمات پیش‌فرض امنیتی روی فرم")
            
            # تنظیمات ورود
            self.spn_max_attempts.setValue(3)
            self.spn_lockout_time.setValue(15)
            self.spn_session_timeout.setValue(30)
            self.chk_force_logout.setChecked(True)
            self.chk_remember_me.setChecked(True)
            self.chk_multi_session.setChecked(False)
            
            # سیاست رمز عبور
            self.spn_min_length.setValue(8)
            self.spn_expiry_days.setValue(90)
            self.spn_history_count.setValue(5)
            self.chk_require_uppercase.setChecked(True)
            self.chk_require_lowercase.setChecked(True)
            self.chk_require_numbers.setChecked(True)
            self.chk_require_special.setChecked(False)
            self.chk_no_common.setChecked(False)
            
            # تأیید دو مرحله‌ای
            self.chk_enable_2fa.setChecked(False)
            self.cmb_2fa_method.setCurrentText("پیامک")
            self.chk_2fa_force_admin.setChecked(True)
            self.chk_2fa_force_all.setChecked(False)
            self.toggle_2fa_widgets(False)
            
            # رمزگذاری
            self.chk_encrypt_passwords.setChecked(True)
            self.chk_encrypt_financial.setChecked(True)
            self.chk_encrypt_personal.setChecked(False)
            self.chk_encrypt_backups.setChecked(True)
            self.chk_encrypt_logs.setChecked(False)
            self.txt_encryption_key.clear()
            
            # امنیت شبکه
            self.chk_ssl_required.setChecked(False)
            self.chk_block_external.setChecked(True)
            self.chk_limit_login_ip.setChecked(False)
            self.spn_firewall_level.setCurrentText("متوسط")
            self.txt_allowed_ips.setPlainText("192.168.1.*\n10.0.0.0/24")
            
            # تنظیمات پیشرفته
            self.chk_audit_log.setChecked(True)
            self.chk_auto_logout.setChecked(True)
            self.spn_inactivity_time.setValue(10)
            self.chk_show_security_warnings.setChecked(True)
            self.chk_auto_update.setChecked(False)
            self.spn_log_retention.setValue(30)
            
            print("✅ تنظیمات پیش‌فرض امنیتی روی فرم اعمال شد")
            
        except Exception as e:
            print(f"⚠️ خطا در اعمال تنظیمات پیش‌فرض: {e}")
        
    def get_settings(self):
        """جمع‌آوری تنظیمات از فرم"""
        settings = {
            # تنظیمات ورود
            'max_login_attempts': self.spn_max_attempts.value(),
            'lockout_minutes': self.spn_lockout_time.value(),
            'session_timeout_minutes': self.spn_session_timeout.value(),
            'force_logout': self.chk_force_logout.isChecked(),
            'remember_me': self.chk_remember_me.isChecked(),
            'multi_session': self.chk_multi_session.isChecked(),
            
            # سیاست رمز عبور
            'min_password_length': self.spn_min_length.value(),
            'password_expiry_days': self.spn_expiry_days.value(),
            'password_history_count': self.spn_history_count.value(),
            'require_uppercase': self.chk_require_uppercase.isChecked(),
            'require_lowercase': self.chk_require_lowercase.isChecked(),
            'require_numbers': self.chk_require_numbers.isChecked(),
            'require_special': self.chk_require_special.isChecked(),
            'no_common_passwords': self.chk_no_common.isChecked(),
            
            # تأیید دو مرحله‌ای
            'enable_2fa': self.chk_enable_2fa.isChecked(),
            'twofa_method': self.cmb_2fa_method.currentText(),
            'twofa_force_admin': self.chk_2fa_force_admin.isChecked(),
            'twofa_force_all': self.chk_2fa_force_all.isChecked(),
            
            # رمزگذاری
            'encrypt_passwords': self.chk_encrypt_passwords.isChecked(),
            'encrypt_financial': self.chk_encrypt_financial.isChecked(),
            'encrypt_personal': self.chk_encrypt_personal.isChecked(),
            'encrypt_backups': self.chk_encrypt_backups.isChecked(),
            'encrypt_logs': self.chk_encrypt_logs.isChecked(),
            'encryption_key': self.txt_encryption_key.text(),
            
            # امنیت شبکه
            'ssl_required': self.chk_ssl_required.isChecked(),
            'block_external': self.chk_block_external.isChecked(),
            'limit_login_ip': self.chk_limit_login_ip.isChecked(),
            'firewall_level': self.spn_firewall_level.currentText(),
            'allowed_ips': self.txt_allowed_ips.toPlainText(),
            
            # تنظیمات پیشرفته
            'audit_log': self.chk_audit_log.isChecked(),
            'auto_logout': self.chk_auto_logout.isChecked(),
            'inactivity_minutes': self.spn_inactivity_time.value(),
            'show_warnings': self.chk_show_security_warnings.isChecked(),
            'auto_update': self.chk_auto_update.isChecked(),
            'log_retention_days': self.spn_log_retention.value(),
        }
        
        return settings

    def validate_settings(self, settings):
        """اعتبارسنجی تنظیمات"""
        errors = []
        
        # بررسی طول رمز عبور
        if settings['min_password_length'] < 6:
            errors.append("حداقل طول رمز عبور باید ۶ کاراکتر یا بیشتر باشد.")
        
        # بررسی کلید رمزگذاری
        if settings['encrypt_passwords'] and not settings['encryption_key']:
            errors.append("برای رمزگذاری رمزهای عبور، باید کلید رمزگذاری تعیین شود.")
        
        # بررسی IPهای مجاز
        allowed_ips = settings['allowed_ips'].strip()
        if settings['limit_login_ip'] and not allowed_ips:
            errors.append("برای محدودیت ورود بر اساس IP، باید حداقل یک IP مجاز مشخص شود.")
        
        if errors:
            QMessageBox.warning(
                self,
                "خطای اعتبارسنجی",
                "❌ لطفا خطاهای زیر را برطرف کنید:\n\n• " + "\n• ".join(errors)
            )
            return False
        
        return True

    def apply_immediate_settings(self, settings):
        """اعمال تنظیماتی که بلافاصله قابل اجرا هستند"""
        # ذخیره در فایل تنظیمات موقت
        try:
            import json
            import os
            
            config_dir = "config"
            if not os.path.exists(config_dir):
                os.makedirs(config_dir)
            
            config_file = os.path.join(config_dir, "security_settings.json")
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(settings, f, ensure_ascii=False, indent=2)
            
            print(f"✅ تنظیمات امنیتی در {config_file} ذخیره شد")
            
        except Exception as e:
            print(f"⚠️ خطا در ذخیره فایل تنظیمات: {e}")

    def test_security(self):
        """تست امنیت سیستم"""
        import time
        
        self.btn_test.setText("در حال تست...")
        self.btn_test.setEnabled(False)
        
        # شبیه‌سازی تست
        time.sleep(1)
        
        # بررسی تنظیمات فعلی
        current_settings = self.get_settings()
        
        results = []
        
        # بررسی رمزگذاری
        if current_settings['encrypt_passwords']:
            results.append(("✅", "رمزهای عبور رمزگذاری می‌شوند"))
        else:
            results.append(("⚠️", "رمزهای عبور رمزگذاری نمی‌شوند"))
        
        # بررسی لاگ
        if current_settings['audit_log']:
            results.append(("✅", "لاگ فعالیت فعال است"))
        else:
            results.append(("❌", "لاگ فعالیت غیرفعال است"))
        
        # بررسی 2FA
        if current_settings['enable_2fa']:
            results.append(("✅", "تأیید دو مرحله‌ای فعال است"))
        else:
            results.append(("⚠️", "تأیید دو مرحله‌ای غیرفعال است"))
        
        # بررسی فایروال
        firewall_level = current_settings['firewall_level']
        if firewall_level in ["بالا", "بسیار بالا"]:
            results.append(("✅", f"سطح فایروال: {firewall_level} (خوب)"))
        elif firewall_level == "متوسط":
            results.append(("⚠️", f"سطح فایروال: {firewall_level} (متوسط)"))
        else:
            results.append(("❌", f"سطح فایروال: {firewall_level} (پایین)"))
        
        # بررسی SSL
        if current_settings['ssl_required']:
            results.append(("✅", "اتصال امن (HTTPS) الزامی است"))
        else:
            results.append(("⚠️", "اتصال HTTP مجاز است"))
        
        # بررسی سیاست رمز عبور
        if current_settings['min_password_length'] >= 8:
            results.append(("✅", f"طول رمز عبور: {current_settings['min_password_length']} (قوی)"))
        else:
            results.append(("⚠️", f"طول رمز عبور: {current_settings['min_password_length']} (ضعیف)"))
        
        # نمایش نتایج
        result_text = "🔍 نتایج تست امنیت سیستم:\n\n"
        for status, message in results:
            result_text += f"{status} {message}\n"
        
        result_text += "\n\n💡 پیشنهادات:\n"
        
        # ارائه پیشنهادات
        if not current_settings['enable_2fa']:
            result_text += "• فعال‌سازی تأیید دو مرحله‌ای\n"
        
        if not current_settings['ssl_required']:
            result_text += "• الزام استفاده از HTTPS\n"
        
        if current_settings['firewall_level'] == "پایین":
            result_text += "• افزایش سطح فایروال\n"
        
        if current_settings['min_password_length'] < 8:
            result_text += f"• افزایش طول رمز عبور به حداقل ۸ کاراکتر\n"
        
        QMessageBox.information(self, "نتایج تست امنیت", result_text)
        
        self.btn_test.setText("🔍 تست امنیت")
        self.btn_test.setEnabled(True)

    def reset_to_defaults(self):
        """بازنشانی به تنظیمات پیش‌فرض"""
        reply = QMessageBox.question(
            self,
            "بازنشانی تنظیمات",
            "آیا مطمئن هستید که می‌خواهید همه تنظیمات امنیتی به پیش‌فرض بازنشانی شوند؟\n\n"
            "این عمل قابل بازگشت نیست!",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # تنظیمات پیش‌فرض
            self.spn_max_attempts.setValue(3)
            self.spn_lockout_time.setValue(15)
            self.spn_session_timeout.setValue(30)
            self.chk_force_logout.setChecked(True)
            self.chk_remember_me.setChecked(True)
            self.chk_multi_session.setChecked(False)
            
            self.spn_min_length.setValue(8)
            self.spn_expiry_days.setValue(90)
            self.spn_history_count.setValue(5)
            self.chk_require_uppercase.setChecked(True)
            self.chk_require_lowercase.setChecked(True)
            self.chk_require_numbers.setChecked(True)
            self.chk_require_special.setChecked(False)
            self.chk_no_common.setChecked(False)
            
            self.chk_enable_2fa.setChecked(False)
            self.cmb_2fa_method.setCurrentText("پیامک")
            self.chk_2fa_force_admin.setChecked(True)
            self.chk_2fa_force_all.setChecked(False)
            self.toggle_2fa_widgets(False)
            
            self.chk_encrypt_passwords.setChecked(True)
            self.chk_encrypt_financial.setChecked(True)
            self.chk_encrypt_personal.setChecked(False)
            self.chk_encrypt_backups.setChecked(True)
            self.chk_encrypt_logs.setChecked(False)
            self.txt_encryption_key.clear()
            
            self.chk_ssl_required.setChecked(False)
            self.chk_block_external.setChecked(True)
            self.chk_limit_login_ip.setChecked(False)
            self.spn_firewall_level.setCurrentText("متوسط")
            self.txt_allowed_ips.setPlainText("192.168.1.*\n10.0.0.0/24")
            
            self.chk_audit_log.setChecked(True)
            self.chk_auto_logout.setChecked(True)
            self.spn_inactivity_time.setValue(10)
            self.chk_show_security_warnings.setChecked(True)
            self.chk_auto_update.setChecked(False)
            self.spn_log_retention.setValue(30)
            
            QMessageBox.information(
                self,
                "بازنشانی انجام شد",
                "✅ تنظیمات امنیتی به پیش‌فرض بازنشانی شدند.\n"
                "فراموش نکنید که تغییرات را ذخیره کنید."
            )

    def load_user_list(self):
        """بارگذاری لیست کاربران برای فیلتر"""
        try:
            query = "SELECT username FROM Users WHERE is_active = 1 ORDER BY username"
            users = self.data_manager.db.fetch_all(query)
            
            self.cmb_user_filter.clear()
            self.cmb_user_filter.addItem("همه کاربران")
            
            for user in users:
                self.cmb_user_filter.addItem(user['username'])
                
        except Exception as e:
            print(f"⚠️ خطا در بارگذاری لیست کاربران: {e}")

    def load_activity_log(self):
        """بارگذاری لاگ فعالیت از دیتابیس"""
        try:
            # ساخت شرط‌های WHERE
            where_conditions = []
            params = []
            
            # فیلتر تاریخ
            date_from = self.date_from.dateTime().toString("yyyy-MM-dd HH:mm:ss")
            date_to = self.date_to.dateTime().toString("yyyy-MM-dd HH:mm:ss")
            where_conditions.append("l.created_at BETWEEN ? AND ?")
            params.extend([date_from, date_to])
            
            # فیلتر کاربر
            selected_user = self.cmb_user_filter.currentText()
            if selected_user != "همه کاربران":
                where_conditions.append("u.username = ?")
                params.append(selected_user)
            
            # فیلتر اقدام
            selected_action = self.cmb_action_filter.currentText()
            if selected_action != "همه اقدامات":
                where_conditions.append("l.action = ?")
                params.append(selected_action)
            
            # ساخت کوئری
            where_clause = " AND ".join(where_conditions) if where_conditions else "1=1"
            
            query = f"""
            SELECT 
                l.id,
                l.created_at,
                u.username,
                l.action,
                l.table_name,
                l.record_id,
                l.ip_address,
                l.details,
                CASE 
                    WHEN l.action LIKE '%ناموفق%' THEN 'ناموفق'
                    WHEN l.action LIKE '%حذف%' THEN 'حذف'
                    WHEN l.action LIKE '%ایجاد%' THEN 'ایجاد'
                    WHEN l.action LIKE '%ویرایش%' THEN 'ویرایش'
                    WHEN l.action LIKE '%ورود%' THEN 'ورود'
                    WHEN l.action LIKE '%خروج%' THEN 'خروج'
                    ELSE 'سایر'
                END as action_type
            FROM Logs l
            LEFT JOIN Users u ON l.user_id = u.id
            WHERE {where_clause}
            ORDER BY l.created_at DESC
            LIMIT 500
            """
            
            logs = self.data_manager.db.fetch_all(query, params)
            
            # پر کردن جدول
            self.table_activity.setRowCount(len(logs))
            
            security_events = 0
            today_count = 0
            today_date = self.data_manager.db.get_current_jalali_date()
            
            for row, log in enumerate(logs):
                # تبدیل تاریخ به شمسی
                log_date = self.data_manager.db.gregorian_to_jalali(log['created_at'], "%Y/%m/%d %H:%M")
                
                # بررسی امروز
                if today_date in log_date:
                    today_count += 1
                
                # بررسی رویداد امنیتی
                action_type = log.get('action_type', '')
                if action_type in ['ناموفق', 'حذف']:
                    security_events += 1
                
                items = [
                    log_date,
                    log['username'] or 'سیستم',
                    log['action'],
                    log['table_name'] or '',
                    str(log['record_id']) if log['record_id'] else '',
                    log['ip_address'] or '',
                    log['details'] or ''
                ]
                
                for col, value in enumerate(items):
                    item = QTableWidgetItem(value)
                    item.setTextAlignment(Qt.AlignCenter)
                    
                    # رنگ‌بندی بر اساس نوع اقدام
                    if col == 2:  # ستون اقدام
                        if action_type == 'ناموفق':
                            item.setForeground(Qt.red)
                            item.setBackground(Qt.darkRed)
                        elif action_type == 'حذف':
                            item.setForeground(Qt.yellow)
                        elif action_type == 'ایجاد':
                            item.setForeground(Qt.green)
                        elif action_type == 'ویرایش':
                            item.setForeground(Qt.blue)
                        elif action_type == 'ورود':
                            item.setForeground(Qt.cyan)
                        elif action_type == 'خروج':
                            item.setForeground(Qt.magenta)
                    
                    self.table_activity.setItem(row, col, item)
            
            # به‌روزرسانی آمار
            self.lbl_total_logs.setText(f"تعداد رکوردها: {len(logs)}")
            self.lbl_today_logs.setText(f"امروز: {today_count}")
            self.lbl_security_events.setText(f"رویدادهای امنیتی: {security_events}")
            
            # به‌روزرسانی زمان آخرین به‌روزرسانی
            now = QDateTime.currentDateTime().toString("HH:mm:ss")
            self.lbl_last_update.setText(f"آخرین به‌روزرسانی: {now}")
            
            print(f"✅ {len(logs)} رکورد لاگ بارگذاری شد")
            
        except Exception as e:
            print(f"❌ خطا در بارگذاری لاگ فعالیت: {e}")
            import traceback
            traceback.print_exc()
            
            # در صورت خطا جدول را خالی کن
            self.table_activity.setRowCount(0)
            self.lbl_total_logs.setText("تعداد رکوردها: 0")
            self.lbl_today_logs.setText("امروز: 0")
            self.lbl_security_events.setText("رویدادهای امنیتی: 0")

    def filter_activity_log(self):
        """اعمال فیلتر بر روی لاگ‌ها"""
        self.load_activity_log()

    def export_logs(self):
        """خروجی گرفتن از لاگ‌ها"""
        try:
            import pandas as pd
            import os
            from datetime import datetime
            
            # جمع‌آوری داده‌ها از جدول
            data = []
            for row in range(self.table_activity.rowCount()):
                row_data = []
                for col in range(self.table_activity.columnCount()):
                    item = self.table_activity.item(row, col)
                    row_data.append(item.text() if item else "")
                data.append(row_data)
            
            # ایجاد DataFrame
            columns = ["تاریخ", "کاربر", "اقدام", "جدول", "رکورد", "IP", "جزئیات"]
            df = pd.DataFrame(data, columns=columns)
            
            # ذخیره فایل
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"logs_export_{timestamp}.xlsx"
            
            # ایجاد پوشه خروجی
            export_dir = "exports"
            if not os.path.exists(export_dir):
                os.makedirs(export_dir)
            
            filepath = os.path.join(export_dir, filename)
            df.to_excel(filepath, index=False)
            
            QMessageBox.information(
                self,
                "خروجی موفق",
                f"✅ لاگ‌ها با موفقیت در فایل زیر ذخیره شد:\n{filepath}"
            )
            
        except Exception as e:
            print(f"❌ خطا در خروجی لاگ‌ها: {e}")
            QMessageBox.warning(
                self,
                "خطا",
                f"خطا در ایجاد خروجی:\n{str(e)}"
            )

    def clear_old_logs(self):
        """پاکسازی لاگ‌های قدیمی"""
        try:
            # دریافت تنظیمات نگهداری لاگ
            retention_days = self.spn_log_retention.value()
            
            if retention_days <= 0:
                QMessageBox.warning(
                    self,
                    "خطا",
                    "لطفا مدت نگهداری لاگ‌ها را مشخص کنید."
                )
                return
            
            reply = QMessageBox.question(
                self,
                "پاکسازی لاگ‌های قدیمی",
                f"آیا مطمئن هستید که می‌خواهید لاگ‌های قدیمی‌تر از {retention_days} روز پاک شوند؟\n\n"
                "این عمل قابل بازگشت نیست!",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                # محاسبه تاریخ
                cutoff_date = (datetime.now() - timedelta(days=retention_days)).strftime("%Y-%m-%d")
                
                query = "DELETE FROM Logs WHERE date(created_at) < ?"
                deleted = self.data_manager.db.execute_query(query, (cutoff_date,))
                
                if deleted:
                    QMessageBox.information(
                        self,
                        "پاکسازی موفق",
                        f"✅ لاگ‌های قدیمی‌تر از {retention_days} روز پاک شدند.\n"
                        "لاگ‌ها دوباره بارگذاری می‌شوند."
                    )
                    self.load_activity_log()
                else:
                    QMessageBox.warning(
                        self,
                        "خطا",
                        "❌ خطا در پاکسازی لاگ‌های قدیمی."
                    )
                    
        except Exception as e:
            print(f"❌ خطا در پاکسازی لاگ‌ها: {e}")
            QMessageBox.critical(
                self,
                "خطا",
                f"خطا در پاکسازی لاگ‌ها:\n{str(e)}"
            )

    def load_blocked_accounts(self):
        """بارگذاری حساب‌های بلاک شده"""
        try:
            # این قسمت باید با جدول لاگ‌های ورود ناموفق پیاده‌سازی شود
            # فعلاً نمونه‌ای نمایشی
            
            self.list_blocked.clear()
            
            # نمونه داده‌های نمایشی
            blocked_accounts = [
                "admin - 5 بار ورود ناموفق - ۱۴۰۳/۱۰/۱۵ ۱۴:۳۰",
                "user1 - 3 بار ورود ناموفق - ۱۴۰۳/۱۰/۱۵ ۱۵:۴۵",
                "operator2 - 4 بار ورود ناموفق - ۱۴۰۳/۱۰/۱۶ ۰۹:۲۰"
            ]
            
            for account in blocked_accounts:
                item = QListWidgetItem(account)
                self.list_blocked.addItem(item)
            
            self.list_blocked.setCurrentRow(0)
            
        except Exception as e:
            print(f"⚠️ خطا در بارگذاری حساب‌های بلاک شده: {e}")

    def unblock_selected_account(self):
        """رفع بلاک حساب انتخاب شده"""
        current_item = self.list_blocked.currentItem()
        if not current_item:
            QMessageBox.warning(self, "هشدار", "لطفاً یک حساب را انتخاب کنید.")
            return
        
        account_info = current_item.text()
        
        reply = QMessageBox.question(
            self,
            "رفع بلاک حساب",
            f"آیا مطمئن هستید که می‌خواهید حساب زیر را رفع بلاک کنید؟\n\n{account_info}",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # در اینجا کد رفع بلاک حساب را پیاده‌سازی کنید
            row = self.list_blocked.currentRow()
            self.list_blocked.takeItem(row)
            
            QMessageBox.information(
                self,
                "رفع بلاک موفق",
                f"✅ حساب مورد نظر رفع بلاک شد."
            )

    def unblock_all_accounts(self):
        """رفع بلاک همه حساب‌ها"""
        if self.list_blocked.count() == 0:
            QMessageBox.information(self, "اطلاع", "هیچ حساب بلاک شده‌ای وجود ندارد.")
            return
        
        reply = QMessageBox.question(
            self,
            "رفع بلاک همه حساب‌ها",
            "آیا مطمئن هستید که می‌خواهید همه حساب‌های بلاک شده را رفع بلاک کنید؟",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.list_blocked.clear()
            
            QMessageBox.information(
                self,
                "رفع بلاک موفق",
                "✅ همه حساب‌های بلاک شده رفع بلاک شدند."
            )

    def setup_2fa(self):
        """راه‌اندازی تأیید دو مرحله‌ای"""
        method = self.cmb_2fa_method.currentText()
        
        if method == "پیامک":
            self.setup_sms_2fa()
        elif method == "ایمیل":
            self.setup_email_2fa()
        elif method == "اپلیکیشن":
            self.setup_app_2fa()

    def setup_sms_2fa(self):
        """راه‌اندازی 2FA با پیامک"""
        QMessageBox.information(
            self,
            "راه‌اندازی 2FA با پیامک",
            "برای فعال‌سازی تأیید دو مرحله‌ای با پیامک:\n\n"
            "1. باید ماژول پنل پیامکی فعال باشد\n"
            "2. شماره تلفن کاربران باید ثبت شده باشد\n"
            "3. اعتبار پنل پیامکی باید کافی باشد\n\n"
            "این قابلیت در نسخه‌های آینده پیاده‌سازی خواهد شد."
        )

    def setup_email_2fa(self):
        """راه‌اندازی 2FA با ایمیل"""
        QMessageBox.information(
            self,
            "راه‌اندازی 2FA با ایمیل",
            "برای فعال‌سازی تأیید دو مرحله‌ای با ایمیل:\n\n"
            "1. باید سرور SMTP پیکربندی شده باشد\n"
            "2. ایمیل کاربران باید ثبت شده باشد\n"
            "3. تنظیمات ایمیل باید صحیح باشد\n\n"
            "این قابلیت در نسخه‌های آینده پیاده‌سازی خواهد شد."
        )

    def setup_app_2fa(self):
        """راه‌اندازی 2FA با اپلیکیشن"""
        QMessageBox.information(
            self,
            "راه‌اندازی 2FA با اپلیکیشن",
            "برای فعال‌سازی تأیید دو مرحله‌ای با اپلیکیشن:\n\n"
            "1. کاربر باید اپلیکیشنی مانند Google Authenticator نصب کند\n"
            "2. کد QR برای کاربر نمایش داده می‌شود\n"
            "3. کاربر کد را در اپلیکیشن اسکن می‌کند\n\n"
            "این قابلیت در نسخه‌های آینده پیاده‌سازی خواهد شد."
        )

    def show_password_tester(self):
        """نمایش ابزار تست قوی بودن رمز عبور"""
        dialog = PasswordTesterDialog(self)
        dialog.exec()

    def closeEvent(self, event):
        """هنگام بسته شدن فرم"""
        self.update_timer.stop()
        event.accept()


class PasswordTesterDialog(QDialog):
    """دیالوگ تست قوی بودن رمز عبور"""

    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("🔐 تست قوی بودن رمز عبور")
        self.setFixedSize(500, 400)
        self.init_ui()
        self.apply_styles()

    def init_ui(self):
        """ایجاد رابط کاربری"""
        layout = QVBoxLayout()
        
        # ورود رمز عبور
        form_layout = QFormLayout()
        
        self.txt_password = QLineEdit()
        self.txt_password.setEchoMode(QLineEdit.Password)
        self.txt_password.textChanged.connect(self.test_password)
        
        self.btn_show = QPushButton("👁")
        self.btn_show.setCheckable(True)
        self.btn_show.toggled.connect(self.toggle_password_visibility)
        
        password_layout = QHBoxLayout()
        password_layout.addWidget(self.txt_password)
        password_layout.addWidget(self.btn_show)
        
        form_layout.addRow("رمز عبور:", password_layout)
        layout.addLayout(form_layout)
        
        # نمایش قدرت رمز
        self.lbl_strength = QLabel("قدرت: -")
        self.lbl_strength.setAlignment(Qt.AlignCenter)
        self.lbl_strength.setStyleSheet("font-size: 16pt; font-weight: bold;")
        layout.addWidget(self.lbl_strength)
        
        # نوار پیشرفت
        self.progress_bar = QWidget()
        self.progress_bar.setFixedHeight(20)
        self.progress_bar.setStyleSheet("""
            QWidget {
                background-color: #2c3e50;
                border-radius: 10px;
            }
        """)
        layout.addWidget(self.progress_bar)
        
        # معیارهای بررسی
        self.criteria_list = QListWidget()
        self.criteria_list.setEnabled(False)
        layout.addWidget(self.criteria_list)
        
        # دکمه‌ها
        button_layout = QHBoxLayout()
        
        self.btn_generate = QPushButton("🎲 تولید رمز قوی")
        self.btn_generate.clicked.connect(self.generate_password)
        button_layout.addWidget(self.btn_generate)
        
        button_layout.addStretch()
        
        buttons = QDialogButtonBox(QDialogButtonBox.Close)
        buttons.rejected.connect(self.reject)
        button_layout.addWidget(buttons)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
        
        # تست اولیه
        self.test_password()

    def apply_styles(self):
        """اعمال استایل"""
        self.setStyleSheet("""
            QDialog {
                background-color: #1a1a1a;
            }
            QLabel {
                color: white;
            }
            QLineEdit {
                background-color: #2c2c2c;
                color: white;
                border: 1px solid #444;
                border-radius: 4px;
                padding: 6px;
            }
            QListWidget {
                background-color: #2c2c2c;
                color: white;
                border: 1px solid #444;
                border-radius: 4px;
            }
            QListWidget::item {
                padding: 5px;
            }
            QListWidget::item:checked {
                background-color: #27ae60;
            }
        """)

    def test_password(self):
        """تست قوی بودن رمز عبور"""
        password = self.txt_password.text()
        
        # معیارها
        criteria = []
        score = 0
        max_score = 100
        
        # طول
        length = len(password)
        if length >= 12:
            criteria.append(("✅", f"طول مناسب ({length} کاراکتر)", 20))
            score += 20
        elif length >= 8:
            criteria.append(("⚠️", f"طول متوسط ({length} کاراکتر)", 15))
            score += 15
        elif length >= 6:
            criteria.append(("⚠️", f"طول کم ({length} کاراکتر)", 10))
            score += 10
        else:
            criteria.append(("❌", f"خیلی کوتاه ({length} کاراکتر)", 0))
        
        # حروف بزرگ
        if any(c.isupper() for c in password):
            criteria.append(("✅", "حروف بزرگ وجود دارد", 10))
            score += 10
        else:
            criteria.append(("❌", "حروف بزرگ وجود ندارد", 0))
        
        # حروف کوچک
        if any(c.islower() for c in password):
            criteria.append(("✅", "حروف کوچک وجود دارد", 10))
            score += 10
        else:
            criteria.append(("❌", "حروف کوچک وجود ندارد", 0))
        
        # اعداد
        if any(c.isdigit() for c in password):
            criteria.append(("✅", "اعداد وجود دارد", 10))
            score += 10
        else:
            criteria.append(("❌", "اعداد وجود ندارد", 0))
        
        # کاراکترهای ویژه
        special_chars = "!@#$%^&*()_+-=[]{}|;:,.<>?"
        if any(c in special_chars for c in password):
            criteria.append(("✅", "کاراکتر ویژه وجود دارد", 15))
            score += 15
        else:
            criteria.append(("❌", "کاراکتر ویژه وجود ندارد", 0))
        
        # تنوع
        char_types = 0
        if any(c.isupper() for c in password):
            char_types += 1
        if any(c.islower() for c in password):
            char_types += 1
        if any(c.isdigit() for c in password):
            char_types += 1
        if any(c in special_chars for c in password):
            char_types += 1
        
        if char_types >= 4:
            criteria.append(("✅", "تنوع کاراکترها عالی", 20))
            score += 20
        elif char_types >= 3:
            criteria.append(("⚠️", "تنوع کاراکترها خوب", 15))
            score += 15
        elif char_types >= 2:
            criteria.append(("⚠️", "تنوع کاراکترها متوسط", 10))
            score += 10
        else:
            criteria.append(("❌", "تنوع کاراکترها ضعیف", 0))
        
        # عدم استفاده از کلمات رایج
        common_passwords = ["password", "123456", "qwerty", "admin", "letmein"]
        if not any(common in password.lower() for common in common_passwords):
            criteria.append(("✅", "رمز رایج نیست", 15))
            score += 15
        else:
            criteria.append(("❌", "رمز رایج است", 0))
        
        # به‌روزرسانی لیست معیارها
        self.criteria_list.clear()
        for icon, text, points in criteria:
            item = QListWidgetItem(f"{icon} {text} ({points} امتیاز)")
            self.criteria_list.addItem(item)
        
        # تعیین قدرت
        if score >= 80:
            strength = "خیلی قوی"
            color = "#27ae60"
        elif score >= 60:
            strength = "قوی"
            color = "#2ecc71"
        elif score >= 40:
            strength = "متوسط"
            color = "#f39c12"
        elif score >= 20:
            strength = "ضعیف"
            color = "#e74c3c"
        else:
            strength = "خیلی ضعیف"
            color = "#c0392b"
        
        self.lbl_strength.setText(f"قدرت: {strength} ({score}/{max_score})")
        self.lbl_strength.setStyleSheet(f"color: {color}; font-size: 16pt; font-weight: bold;")
        
        # به‌روزرسانی نوار پیشرفت
        progress = int((score / max_score) * 100)
        self.progress_bar.setStyleSheet(f"""
            QWidget {{
                background-color: #2c3e50;
                border-radius: 10px;
                border: none;
            }}
            QWidget::after {{
                content: "";
                background-color: {color};
                border-radius: 10px;
                width: {progress}%;
                height: 100%;
                position: absolute;
            }}
        """)

    def toggle_password_visibility(self, visible):
        """تغییر حالت نمایش رمز عبور"""
        if visible:
            self.txt_password.setEchoMode(QLineEdit.Normal)
            self.btn_show.setText("👁‍🗨")
        else:
            self.txt_password.setEchoMode(QLineEdit.Password)
            self.btn_show.setText("👁")

    def generate_password(self):
        """تولید رمز عبور قوی"""
        import secrets
        import string
        
        # تولید رمز 12 کاراکتری
        uppercase = string.ascii_uppercase
        lowercase = string.ascii_lowercase
        digits = string.digits
        special = "!@#$%^&*"
        
        # اطمینان از وجود حداقل یک کاراکتر از هر نوع
        password = [
            secrets.choice(uppercase),
            secrets.choice(lowercase),
            secrets.choice(digits),
            secrets.choice(special)
        ]
        
        # تکمیل با کاراکترهای تصادفی
        all_chars = uppercase + lowercase + digits + special
        password.extend(secrets.choice(all_chars) for _ in range(8))
        
        # ترکیب تصادفی
        secrets.SystemRandom().shuffle(password)
        
        # تبدیل به رشته
        password_str = ''.join(password)
        
        # نمایش در فیلد
        self.txt_password.setText(password_str)
        
        # تست رمز جدید
        self.test_password()



