# main.py - نقطه ورود اصلی برنامه
import sys
import os

# اضافه کردن مسیر پوشه‌ها به sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ui.login_window import LoginWindow
from ui.main_window import MainWindow
from database.models import DataManager
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QFont
from PySide6.QtCore import QTranslator, QLocale
import jdatetime

def setup_application():
    """تنظیمات اولیه برنامه"""
    # ایجاد برنامه
    app = QApplication(sys.argv)
    
    # تنظیم ترجمه برای تاریخ و اعداد فارسی
    translator = QTranslator()
    translator.load(QLocale(QLocale.Persian, QLocale.Iran), "qtbase")
    app.installTranslator(translator)
    
    # تنظیم فونت فارسی
    try:
        font = QFont("B Nazanin", 10)
        app.setFont(font)
        print("✅ فونت فارسی تنظیم شد")
    except:
        font = app.font()
        font.setPointSize(10)
        app.setFont(font)
        print("⚠️ فونت 'B Nazanin' یافت نشد. از فونت پیش‌فرض استفاده می‌شود.")
    
    return app

def create_data_directory():
    """ایجاد پوشه داده‌ها در صورت عدم وجود"""
    data_dir = "data"
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
        print(f"📁 پوشه '{data_dir}' ایجاد شد")
    
    backup_dir = os.path.join(data_dir, "backup")
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)
        print(f"📁 پوشه '{backup_dir}' ایجاد شد")

class ApplicationController:
    """کنترلر اصلی برنامه"""
    
    def __init__(self, app, data_manager):
        self.app = app
        self.data_manager = data_manager
        self.login_window = None
        self.main_window = None
    
    def start(self):
        """شروع برنامه"""
        print("🚀 در حال راه‌اندازی سیستم مدیریت تعمیرگاه...")
        
        # ایجاد فرم ورود
        self.login_window = LoginWindow(self.data_manager)
        self.login_window.login_successful.connect(self.on_login_successful)
        self.login_window.show()
        
        print("✅ برنامه آماده است. فرم ورود نمایش داده می‌شود.")
    
    def on_login_successful(self, user_data):
        """هنگام موفقیت‌آمیز بودن ورود"""
        print(f"✅ ورود موفق: {user_data.get('full_name', user_data['username'])}")
        
        # بستن فرم ورود
        self.login_window.close()
        
        # ایجاد پنجره اصلی
        self.main_window = MainWindow(user_data, self.data_manager)
        self.main_window.show()
        
        print("🏪 پنجره اصلی برنامه نمایش داده شد.")

def main():
    """تابع اصلی اجرای برنامه"""
    # ایجاد پوشه‌های مورد نیاز
    create_data_directory()
    
    # تنظیم برنامه
    app = setup_application()
    
    # ایجاد مدیر داده با مسیر صحیح دیتابیس
    print("📦 در حال راه‌اندازی پایگاه داده...")
    db_path = "data/repair_shop.db"  # 🔴 تغییر مسیر به پوشه data
    data_manager = DataManager(db_path)
    
    # نمایش اطلاعات اولیه
    today = jdatetime.datetime.now()
    print(f"📅 تاریخ امروز: {today.strftime('%Y/%m/%d')}")
    print(f"🏪 سیستم مدیریت تعمیرگاه لوازم خانگی")
    print("=" * 50)
    
    # ایجاد کنترلر و شروع برنامه
    controller = ApplicationController(app, data_manager)
    controller.start()
    
    # اجرای برنامه
    sys.exit(app.exec())

if __name__ == "__main__":
    main()