# ui/forms/inventory/inventory_window.py
"""
پنجره مستقل برای مدیریت انبار
"""

from PySide6.QtWidgets import QMainWindow, QVBoxLayout, QWidget
from PySide6.QtCore import Qt

class InventoryWindow(QMainWindow):
    """پنجره مستقل انبار"""
    
    def __init__(self, data_manager, parent=None):
        super().__init__(parent)
        self.data_manager = data_manager
        self.parent_window = parent
        self.inventory_form = None
        self.init_ui()
        
    def init_ui(self):
        """راه‌اندازی رابط کاربری"""
        self.setWindowTitle("📦 مدیریت انبار - سیستم تعمیرگاه شیروین")
        self.setGeometry(100, 50, 1400, 800)
        self.setLayoutDirection(Qt.RightToLeft)
        
        # اعمال تم تاریک
        self.setStyleSheet("""
            QMainWindow {
                background-color: #000000;
            }
            QWidget {
                background-color: #000000;
                color: white;
                font-family: 'B Nazanin', Tahoma;
            }
        """)
        
        # ایجاد ویجت مرکزی
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # ایجاد layout اصلی
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # ایجاد فرم اصلی انبار با ایمپورت lazy
        try:
            # ایمپورت داخل تابع برای جلوگیری از circular import
            from .inventory_main_form import InventoryMainForm
            self.inventory_form = InventoryMainForm(self)
            main_layout.addWidget(self.inventory_form)
        except Exception as e:
            print(f"❌ خطا در ایجاد فرم انبار: {e}")
            from PySide6.QtWidgets import QLabel
            error_label = QLabel(f"خطا در بارگذاری فرم انبار: {e}")
            error_label.setStyleSheet("color: red; font-size: 14pt;")
            main_layout.addWidget(error_label)
        
        # تنظیمات پنجره
        self.setWindowModality(Qt.NonModal)  # غیر مدال باشد
        
    def closeEvent(self, event):
        """مدیریت بسته شدن پنجره"""
        # اگر در parent_window ذخیره شده، آن را None کنیم
        if self.parent_window and hasattr(self.parent_window, 'inventory_window'):
            self.parent_window.inventory_window = None
        event.accept()