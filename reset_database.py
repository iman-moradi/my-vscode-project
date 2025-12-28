# reset_database.py
from database import DatabaseManager

def reset_database():
    db = DatabaseManager()
    
    # حذف فایل دیتابیس موجود (اگر وجود دارد)
    import os
    if os.path.exists("repair_shop.db"):
        os.remove("repair_shop.db")
        print("✅ فایل دیتابیس قدیمی حذف شد")
    
    # ایجاد دیتابیس و جداول جدید
    if db.initialize_database():
        print("✅ دیتابیس و جداول با موفقیت ایجاد شدند")
        
        # درج تنظیمات پیش‌فرض
        db.connect()
        db.cursor.execute('''
        INSERT OR REPLACE INTO Settings (id, app_name, date_format, font_name, font_size, 
                                        bg_color, text_color, company_name, tax_percentage)
        VALUES (1, 'سیستم مدیریت تعمیرگاه لوازم خانگی', 'yyyy/MM/dd', 
                'B Nazanin', 10, '#FFFFFF', '#000000', 'تعمیرگاه شیروین', 9)
        ''')
        
        # درج یک مشتری نمونه
        db.cursor.execute('''
        INSERT INTO Persons (person_type, first_name, last_name, mobile, phone, address)
        VALUES ('مشتری', 'علی', 'محمدی', '09123456789', '021-1234567', 'تهران، خیابان آزادی')
        ''')
        
        # درج یک دستگاه نمونه
        db.cursor.execute('''
        INSERT INTO Devices (device_type, brand, model, serial_number, production_year)
        VALUES ('یخچال', 'سامسونگ', 'RT38K5932SL', 'SN123456', 2023)
        ''')
        
        db.connection.commit()
        db.connection.close()
        
        print("✅ داده‌های نمونه با موفقیت درج شدند")
        return True
    else:
        print("❌ خطا در ایجاد دیتابیس")
        return False

if __name__ == "__main__":
    reset_database()