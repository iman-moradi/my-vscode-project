# settings_window.py

import sys
from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, 
                               QHBoxLayout, QToolBar, QStatusBar, 
                               QMessageBox, QApplication)
from PySide6.QtGui import QIcon, QKeySequence , QAction
from PySide6.QtCore import Qt, Signal
from .settings_main_form import SettingsMainForm

class SettingsWindow(QMainWindow):
    """پنجره مستقل تنظیمات برنامه"""
    
    # سیگنال برای بسته شدن پنجره
    window_closed = Signal()
    
    def __init__(self, data_manager, config_manager=None, parent=None):  # 🔴 config_manager اضافه شد
        super().__init__(parent)
        self.data_manager = data_manager
        self.config_manager = config_manager  # 🔴 ذخیره config_manager
        self.parent = parent
        
        # تنظیمات پنجره
        self.setWindowTitle("⚙️ تنظیمات سیستم مدیریت تعمیرگاه")
        self.setGeometry(100, 100, 1100, 700)
        
        # اعمال تم تاریک
        self.setStyleSheet("""
            QMainWindow {
                background-color: #000000;
                color: #ffffff;
            }
        """)
        
        # ایجاد رابط کاربری
        self.init_ui()
        
        # بارگذاری تنظیمات اولیه
        self.load_initial_settings()
    
    def init_ui(self):
        """ایجاد رابط کاربری پنجره"""
        # ایجاد ویجت مرکزی
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # ایجاد فرم اصلی تنظیمات - 🔴 با config_manager
        self.main_form = SettingsMainForm(self.data_manager, self.config_manager)
        
        # لایه‌بندی
        layout = QVBoxLayout()
        layout.addWidget(self.main_form)
        central_widget.setLayout(layout)
        
        # ایجاد نوار ابزار
        self.create_toolbar()
        
        # ایجاد نوار وضعیت
        self.create_statusbar()
        
        # تنظیم جهت راست به چپ
        self.setLayoutDirection(Qt.RightToLeft)
    
    def create_toolbar(self):
        """ایجاد نوار ابزار"""
        toolbar = QToolBar("نوار ابزار تنظیمات")
        toolbar.setStyleSheet("""
            QToolBar {
                background-color: #111111;
                border: none;
                padding: 5px;
            }
            QToolButton {
                background-color: #2c3e50;
                color: white;
                border: none;
                padding: 8px;
                border-radius: 4px;
                margin: 2px;
            }
            QToolButton:hover {
                background-color: #34495e;
            }
        """)
        self.addToolBar(toolbar)
        
        # دکمه ذخیره
        save_action = QAction("💾 ذخیره", self)
        save_action.setShortcut(QKeySequence("Ctrl+S"))
        save_action.triggered.connect(self.save_all_settings)
        toolbar.addAction(save_action)
        
        toolbar.addSeparator()
        
        # دکمه بازگردانی
        restore_action = QAction("↩️ بازگردانی", self)
        restore_action.triggered.connect(self.restore_defaults)
        toolbar.addAction(restore_action)
        
        # دکمه بستن
        close_action = QAction("❌ بستن", self)
        close_action.setShortcut(QKeySequence("Esc"))
        close_action.triggered.connect(self.close)
        toolbar.addAction(close_action)
    
    def create_statusbar(self):
        """ایجاد نوار وضعیت"""
        statusbar = QStatusBar()
        statusbar.setStyleSheet("""
            QStatusBar {
                background-color: #111111;
                color: #cccccc;
            }
        """)
        self.setStatusBar(statusbar)
        
        # پیام اولیه
        statusbar.showMessage("آماده - تنظیمات سیستم", 3000)
    
    def load_initial_settings(self):
        """بارگذاری تنظیمات اولیه از دیتابیس"""
        try:
            # بارگذاری تنظیمات از config_manager اگر وجود دارد
            if self.config_manager:
                self.statusBar().showMessage("تنظیمات از ConfigManager بارگذاری شد", 2000)
            else:
                # روش قدیمی: بارگیری از دیتابیس
                settings = self.data_manager.get_settings()
                if settings:
                    self.main_form.load_settings(settings)
                    self.statusBar().showMessage("تنظیمات بارگذاری شد", 2000)
        except Exception as e:
            QMessageBox.warning(self, "خطا", f"خطا در بارگذاری تنظیمات: {str(e)}")
    
    def save_all_settings(self):
        """ذخیره تمام تنظیمات"""
        try:
            # ذخیره از طریق فرم اصلی
            success = self.main_form.save_settings()
            
            if success:
                self.statusBar().showMessage("✅ تنظیمات با موفقیت ذخیره شد", 3000)
                
                # اگر پنجره اصلی وجود دارد، آن را به‌روزرسانی کن
                if self.parent and hasattr(self.parent, 'apply_settings'):
                    # دریافت تنظیمات از فرم
                    settings_data = self.main_form.get_all_settings()
                    self.parent.apply_settings(settings_data)
                    
                QMessageBox.information(self, "ذخیره شد", "تنظیمات با موفقیت ذخیره شدند.")
            else:
                QMessageBox.warning(self, "خطا", "خطا در ذخیره تنظیمات.")
                
        except Exception as e:
            QMessageBox.critical(self, "خطا", f"خطا در ذخیره تنظیمات: {str(e)}")
    
    def restore_defaults(self):
        """بازگردانی تنظیمات به پیش‌فرض"""
        reply = QMessageBox.question(
            self, 
            "بازگردانی تنظیمات",
            "آیا مطمئن هستید که می‌خواهید همه تنظیمات به حالت پیش‌فرض بازگردند؟",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                if self.config_manager:
                    # 🔴 بازگردانی تنظیمات پیش‌فرض در config_manager
                    from modules.config_manager import ConfigManager
                    
                    # اگر config_manager یک نمونه از ConfigManager است
                    if isinstance(self.config_manager, ConfigManager):
                        # تنظیمات پیش‌فرض عمومی
                        self.config_manager.set_default_general_config()
                        self.config_manager.set_default_security_config()
                        self.config_manager.set_default_financial_config()
                        self.config_manager.set_default_inventory_config()
                        self.config_manager.set_default_display_config()
                        
                        # بارگذاری مجدد تنظیمات در فرم
                        self.main_form.load_settings_from_config()
                        
                        self.statusBar().showMessage("تنظیمات به پیش‌فرض بازگردانده شدند", 3000)
                        QMessageBox.information(self, "بازگردانی", "تنظیمات به حالت پیش‌فرض بازگردانده شدند.")
                else:
                    # روش قدیمی: بازگردانی تنظیمات پیش‌فرض
                    default_settings = self.data_manager.get_default_settings()
                    self.main_form.load_settings(default_settings)
                    
                    self.statusBar().showMessage("تنظیمات به پیش‌فرض بازگردانده شدند", 3000)
                    QMessageBox.information(self, "بازگردانی", "تنظیمات به حالت پیش‌فرض بازگردانده شدند.")
                
            except Exception as e:
                QMessageBox.critical(self, "خطا", f"خطا در بازگردانی تنظیمات: {str(e)}")
    
    def closeEvent(self, event):
        """رویداد بسته شدن پنجره"""
        # ارسال سیگنال بسته شدن
        self.window_closed.emit()
        super().closeEvent(event)

# تست پنجره تنظیمات - 🔴 نسخه اصلاح شده
if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # برای تست، یک DataManager و ConfigManager ساختگی ایجاد می‌کنیم
    class MockDataManager:
        def get_settings(self):
            return {
                'app_name': 'شیروین',
                'company_name': 'تعمیرگاه لوازم خانگی شیروین',
                'tax_percentage': 9,
                'theme': 'dark'
            }
        
        def update_settings(self, data):
            print("تنظیمات ذخیره شد:", data)
            return True
        
        def get_default_settings(self):
            return {
                'app_name': 'تعمیرگاه من',
                'company_name': 'تعمیرگاه لوازم خانگی',
                'tax_percentage': 9,
                'theme': 'dark'
            }
    
    # ساختگی ConfigManager
    class MockConfigManager:
        def __init__(self):
            self.config_cache = {
                'general': {
                    'app_name': 'سیستم تست',
                    'company_name': 'شرکت تست'
                }
            }
        
        def get(self, category, key=None, default=None):
            if category in self.config_cache:
                if key is None:
                    return self.config_cache[category]
                return self.config_cache[category].get(key, default)
            return default
        
        def set_default_general_config(self):
            self.config_cache['general'] = {
                'app_name': 'سیستم پیش‌فرض',
                'company_name': 'شرکت پیش‌فرض'
            }
            print("✅ تنظیمات عمومی به پیش‌فرض بازگشت")
    
    data_manager = MockDataManager()
    config_manager = MockConfigManager()  # 🔴 ConfigManager ساختگی
    
    # 🔴 ارسال هر دو manager به SettingsWindow
    window = SettingsWindow(data_manager, config_manager)
    window.show()
    sys.exit(app.exec())