# test_config_manager.py
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_config_manager():
    # ساخت DataManager ساختگی
    class MockDataManager:
        def __init__(self):
            from database.database import DatabaseManager
            self.db = DatabaseManager()
    
    # ایجاد ConfigManager
    from modules.config_manager import ConfigManager
    
    data_manager = MockDataManager()
    config_manager = ConfigManager(data_manager)
    
    print("🔍 تست ConfigManager")
    print("=" * 50)
    
    # تست دریافت تنظیمات
    general_config = config_manager.get('general')
    print(f"تنظیمات عمومی: {general_config}")
    
    # تست دریافت مقادیر خاص
    app_name = config_manager.get('general', 'app_name', 'پیش‌فرض')
    print(f"نام برنامه: {app_name}")
    
    # تست ذخیره تنظیمات
    success = config_manager.set('general', 'app_name', 'تست برنامه', save_to_db=True)
    print(f"ذخیره تنظیمات: {'موفق' if success else 'ناموفق'}")
    
    # خواندن مجدد
    new_app_name = config_manager.get('general', 'app_name', 'پیش‌فرض')
    print(f"نام برنامه پس از ذخیره: {new_app_name}")

if __name__ == "__main__":
    test_config_manager()