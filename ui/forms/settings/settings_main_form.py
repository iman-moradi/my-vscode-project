# settings_main_form.py

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, 
                               QTabWidget, QPushButton, QMessageBox,
                               QLabel, QScrollArea)
from PySide6.QtCore import Qt
from .general_settings_form import GeneralSettingsForm
from .financial_settings_form import FinancialSettingsForm
from .user_management_form import UserManagementForm
from .backup_settings_form import BackupSettingsForm
from .sms_settings_form import SMSSettingsForm
from .inventory_settings_form import InventorySettingsForm
from .security_settings_form import SecuritySettingsForm

class SettingsMainForm(QWidget):
    """فرم اصلی تنظیمات با تب‌های مختلف"""
    
    def __init__(self, data_manager):
        super().__init__()
        self.data_manager = data_manager
        self.init_ui()
        self.setup_connections()
        
        # اعمال استایل
        self.apply_styles()
    
    def init_ui(self):
        """ایجاد رابط کاربری"""
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(10, 10, 10, 10)
        
        # عنوان
        title_label = QLabel("⚙️ تنظیمات سیستم")
        title_label.setStyleSheet("""
            QLabel {
                font-size: 18pt;
                font-weight: bold;
                color: #ffffff;
                padding: 10px;
                background-color: #2c3e50;
                border-radius: 5px;
            }
        """)
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)
        
        # ایجاد نوار تب‌ها
        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #444444;
                background-color: #111111;
                border-radius: 5px;
            }
            QTabBar::tab {
                background-color: #333333;
                color: #ffffff;
                padding: 10px 20px;
                margin-right: 5px;
                border-top-left-radius: 5px;
                border-top-right-radius: 5px;
            }
            QTabBar::tab:selected {
                background-color: #2c3e50;
                color: #ffffff;
            }
            QTabBar::tab:hover {
                background-color: #3c4e60;
            }
        """)
        
        # ایجاد فرم‌های مختلف و اضافه کردن به تب‌ها
        self.general_form = GeneralSettingsForm(self.data_manager)
        self.financial_form = FinancialSettingsForm(self.data_manager)
        self.user_form = UserManagementForm(self.data_manager)
        self.backup_form = BackupSettingsForm(self.data_manager)
        self.sms_form = SMSSettingsForm(self.data_manager)
        self.inventory_form = InventorySettingsForm(self.data_manager)
        self.security_form = SecuritySettingsForm(self.data_manager)
        
        # اضافه کردن تب‌ها
        self.tab_widget.addTab(self.create_scrollable(self.general_form), "🌐 عمومی")
        self.tab_widget.addTab(self.create_scrollable(self.financial_form), "💰 مالی")
        self.tab_widget.addTab(self.create_scrollable(self.user_form), "👥 کاربران")
        self.tab_widget.addTab(self.create_scrollable(self.backup_form), "💾 پشتیبان")
        self.tab_widget.addTab(self.create_scrollable(self.sms_form), "📱 پیامک")
        self.tab_widget.addTab(self.create_scrollable(self.inventory_form), "📦 انبار")
        self.tab_widget.addTab(self.create_scrollable(self.security_form), "🔒 امنیت")
        
        main_layout.addWidget(self.tab_widget)
        
        # نوار ابزار پایین
        bottom_layout = QHBoxLayout()
        
        # دکمه ذخیره
        self.btn_save = QPushButton("💾 ذخیره تنظیمات")
        self.btn_save.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2ecc71;
            }
        """)
        bottom_layout.addWidget(self.btn_save)
        
        # دکمه بازگردانی
        self.btn_restore = QPushButton("↩️ بازگردانی پیش‌فرض")
        self.btn_restore.setStyleSheet("""
            QPushButton {
                background-color: #e67e22;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #d35400;
            }
        """)
        bottom_layout.addWidget(self.btn_restore)
        
        # فضای خالی
        bottom_layout.addStretch()
        
        # دکمه لغو
        self.btn_cancel = QPushButton("❌ لغو")
        self.btn_cancel.setStyleSheet("""
            QPushButton {
                background-color: #c0392b;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #e74c3c;
            }
        """)
        bottom_layout.addWidget(self.btn_cancel)
        
        main_layout.addLayout(bottom_layout)
        
        self.setLayout(main_layout)
    
    def create_scrollable(self, widget):
        """ایجاد ویجت قابل اسکرول"""
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(widget)
        scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: #111111;
            }
            QScrollBar:vertical {
                background-color: #222222;
                width: 15px;
                border-radius: 7px;
            }
            QScrollBar::handle:vertical {
                background-color: #444444;
                border-radius: 7px;
                min-height: 30px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #555555;
            }
        """)
        return scroll
    
    def setup_connections(self):
        """اتصال سیگنال‌ها"""
        self.btn_save.clicked.connect(self.save_settings)
        self.btn_restore.clicked.connect(self.restore_defaults)
        self.btn_cancel.clicked.connect(self.cancel_changes)
    
    def apply_styles(self):
        """اعمال استایل کلی"""
        self.setStyleSheet("""
            QWidget {
                background-color: #000000;
                color: #ffffff;
                font-family: 'B Nazanin';
                font-size: 11pt;
            }
        """)
    
    def load_settings(self, settings_data):
        """بارگذاری تنظیمات در فرم‌ها"""
        try:
            # بارگذاری تنظیمات در هر فرم
            self.general_form.load_settings(settings_data)
            self.financial_form.load_settings(settings_data)
            self.user_form.load_settings(settings_data)
            self.backup_form.load_settings(settings_data)
            self.sms_form.load_settings(settings_data)
            self.inventory_form.load_settings(settings_data)
            self.security_form.load_settings(settings_data)
            
        except Exception as e:
            print(f"خطا در بارگذاری تنظیمات: {e}")
    
    def get_all_settings(self):
        """جمع‌آوری تنظیمات از تمام فرم‌ها"""
        settings = {}
        
        try:
            # جمع‌آوری از هر فرم
            settings.update(self.general_form.get_settings())
            settings.update(self.financial_form.get_settings())
            settings.update(self.user_form.get_settings())
            settings.update(self.backup_form.get_settings())
            settings.update(self.sms_form.get_settings())
            settings.update(self.inventory_form.get_settings())
            settings.update(self.security_form.get_settings())
            
        except Exception as e:
            print(f"خطا در جمع‌آوری تنظیمات: {e}")
        
        return settings
    
    def save_settings(self):
        """ذخیره تنظیمات (از بیرون فراخوانی می‌شود)"""
        try:
            settings = self.get_all_settings()
            return settings
        except Exception as e:
            QMessageBox.warning(self, "خطا", f"خطا در ذخیره تنظیمات: {str(e)}")
            return None
    
    def restore_defaults(self):
        """بازگردانی تنظیمات به پیش‌فرض"""
        # این متد از طریق دکمه بازگردانی فراخوانی می‌شود
        # در واقعیت باید تنظیمات پیش‌فرض را از دیتابیس بخواند
        pass
    
    def cancel_changes(self):
        """لغو تغییرات و بستن فرم"""
        # این متد باید پنجره را ببندد
        # در واقعیت از طریق والد فراخوانی می‌شود
        pass