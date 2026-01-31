# database_upgrade.py
import sqlite3
import os
from datetime import datetime

class DatabaseUpgrader:
    def __init__(self, db_path="data/repair_shop.db"):
        self.db_path = db_path
        self.connection = None
        self.cursor = None
        
    def connect(self):
        """اتصال به دیتابیس"""
        try:
            self.connection = sqlite3.connect(self.db_path)
            self.connection.execute("PRAGMA foreign_keys = OFF")
            self.cursor = self.connection.cursor()
            self.connection.row_factory = sqlite3.Row
            return True
        except Exception as e:
            print(f"❌ خطا در اتصال به دیتابیس: {e}")
            return False
    
    def backup_database(self):
        """پشتیبان‌گیری از دیتابیس"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = f"data/repair_shop_backup_{timestamp}.db"
            
            import shutil
            shutil.copy2(self.db_path, backup_path)
            print(f"✅ پشتیبان با موفقیت ایجاد شد: {backup_path}")
            return backup_path
        except Exception as e:
            print(f"❌ خطا در پشتیبان‌گیری: {e}")
            return None
    
    def upgrade_database(self):
        """ارتقای دیتابیس به نسخه جدید"""
        print("🔄 در حال ارتقای دیتابیس...")
        
        # 1. پشتیبان‌گیری
        backup = self.backup_database()
        if not backup:
            print("⚠️ ادامه عملیات بدون پشتیبان...")
        
        try:
            self.connect()
            
            # 2. حذف CHECK constraint از جدول Parts
            print("🔧 در حال حذف CHECK constraint از جدول Parts...")
            self.upgrade_parts_table()
            
            # 3. اضافه کردن ستون company_name به Persons
            print("🔧 در حال اضافه کردن ستون company_name به Persons...")
            self.upgrade_persons_table()
            
            # 4. اضافه کردن دسته‌بندی‌های قطعات به LookupValues
            print("🔧 در حال اضافه کردن دسته‌بندی‌های قطعات...")
            self.add_part_categories()
            
            # 5. رفع مشکل JalaliDateInput
            print("🔧 در حال بررسی JalaliDateInput...")
            
            self.connection.commit()
            print("✅ دیتابیس با موفقیت ارتقا یافت!")
            return True
            
        except Exception as e:
            print(f"❌ خطا در ارتقای دیتابیس: {e}")
            import traceback
            traceback.print_exc()
            if self.connection:
                self.connection.rollback()
            return False
        finally:
            if self.connection:
                self.connection.close()
    
    def upgrade_parts_table(self):
        """حذف CHECK constraint از جدول Parts"""
        try:
            # 1. بررسی وجود جدول
            self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='Parts'")
            if not self.cursor.fetchone():
                print("⚠️ جدول Parts وجود ندارد")
                return False
            
            # 2. ایجاد جدول جدید بدون constraint
            self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS Parts_new (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                part_code TEXT UNIQUE NOT NULL,
                part_name TEXT NOT NULL,
                category TEXT,
                brand TEXT,
                model TEXT,
                unit TEXT CHECK(unit IN ('عدد', 'متر', 'کیلو', 'لیتر', 'ست')) DEFAULT 'عدد',
                min_stock INTEGER DEFAULT 5,
                max_stock INTEGER DEFAULT 100,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            ''')
            
            # 3. کپی داده‌ها
            self.cursor.execute('''
            INSERT INTO Parts_new 
            SELECT id, part_code, part_name, category, brand, model, unit, 
                   min_stock, max_stock, description, created_at
            FROM Parts
            ''')
            
            # 4. حذف جدول قدیمی و rename
            self.cursor.execute('DROP TABLE Parts')
            self.cursor.execute('ALTER TABLE Parts_new RENAME TO Parts')
            
            # 5. ایجاد ایندکس‌ها
            self.cursor.execute('CREATE INDEX IF NOT EXISTS idx_parts_code ON Parts(part_code)')
            self.cursor.execute('CREATE INDEX IF NOT EXISTS idx_parts_category ON Parts(category)')
            
            print("✅ جدول Parts ارتقا یافت")
            return True
            
        except Exception as e:
            print(f"❌ خطا در ارتقای جدول Parts: {e}")
            raise
    
    def upgrade_persons_table(self):
        """اضافه کردن ستون company_name به Persons"""
        try:
            # بررسی وجود ستون
            self.cursor.execute("PRAGMA table_info(Persons)")
            columns = [col[1] for col in self.cursor.fetchall()]
            
            if 'company_name' not in columns:
                self.cursor.execute('ALTER TABLE Persons ADD COLUMN company_name TEXT')
                print("✅ ستون company_name اضافه شد")
            else:
                print("✅ ستون company_name از قبل وجود دارد")
                
            return True
            
        except Exception as e:
            print(f"❌ خطا در ارتقای جدول Persons: {e}")
            return False
    

    # database_upgrade.py - تابع جدید اضافه کنید
    def add_brands_to_lookup(self):
        """اضافه کردن برندها به LookupValues"""
        try:
            brands = [
                ('brand', 'سامسونگ'),
                ('brand', 'ال جی'),
                ('brand', 'پاناسونیک'),
                ('brand', 'توشیبا'),
                ('brand', 'شارپ'),
                ('brand', 'دوو'),
                ('brand', 'کنوود'),
                ('brand', 'بوش'),
                ('brand', 'سیمنز'),
                ('brand', 'میتگ'),
                ('brand', 'هایر'),
                ('brand', 'گرین'),
                ('brand', 'اسنوا'),
                ('brand', 'پارس خزر'),
                ('brand', 'سایر')
            ]
            
            for category, value in brands:
                self.cursor.execute('''
                INSERT OR IGNORE INTO LookupValues (category, value) 
                VALUES (?, ?)
                ''', (category, value))
            
            print(f"✅ {len(brands)} برند اضافه شد")
            return True
            
        except Exception as e:
            print(f"❌ خطا در اضافه کردن برندها: {e}")
            return False

    def add_part_categories(self):
        """اضافه کردن دسته‌بندی‌های قطعات به LookupValues"""
        try:
            # دسته‌بندی‌های پیش‌فرض
            part_categories = [
                ('part_category', 'الکترونیکی'),
                ('part_category', 'مکانیکی'),
                ('part_category', 'برقی'),
                ('part_category', 'الکتریکی'),
                ('part_category', 'ترموستات'),
                ('part_category', 'کمپرسور'),
                ('part_category', 'فن'),
                ('part_category', 'پمپ'),
                ('part_category', 'سنسور'),
                ('part_category', 'شیر'),
                ('part_category', 'لوله'),
                ('part_category', 'کابل'),
                ('part_category', 'سیم'),
                ('part_category', 'فیوز'),
                ('part_category', 'رله'),
                ('part_category', 'برد'),
                ('part_category', 'مدار'),
                ('part_category', 'سایر'),
                ('part_category', 'یخچال'),  # برای سازگاری با داده‌های موجود
                ('part_category', 'فریزر'),
                ('part_category', 'ماشین لباسشویی'),
                ('part_category', 'اجاق گاز'),
                ('part_category', 'مایکروویو'),
                ('part_category', 'پنکه'),
                ('part_category', 'کولر')
            ]
            
            for category, value in part_categories:
                self.cursor.execute('''
                INSERT OR IGNORE INTO LookupValues (category, value) 
                VALUES (?, ?)
                ''', (category, value))
            
            print(f"✅ {len(part_categories)} دسته‌بندی قطعات اضافه شد")
            return True
            
        except Exception as e:
            print(f"❌ خطا در اضافه کردن دسته‌بندی‌ها: {e}")
            return False
    
    def fix_jalali_date_input(self):
        """رفع مشکل JalaliDateInput"""
        try:
            # اینجا می‌توانید داده‌های تاریخ را اصلاح کنید
            # فعلاً فقط پیام می‌دهیم
            print("⚠️ نیاز به اصلاح JalaliDateInput دارید")
            print("   لطفاً متدهای set_date_from_gregorian و set_date_str را اضافه کنید")
            return True
        except Exception as e:
            print(f"⚠️ خطا در بررسی JalaliDateInput: {e}")
            return False

# اجرای ارتقا
if __name__ == "__main__":
    print("🚀 شروع ارتقای دیتابیس")
    upgrader = DatabaseUpgrader()
    
    if upgrader.upgrade_database():
        print("\n🎉 ارتقای دیتابیس با موفقیت تکمیل شد!")
        print("\n📋 تغییرات اعمال شده:")
        print("   1. حذف CHECK constraint از جدول Parts")
        print("   2. اضافه کردن ستون company_name به Persons")
        print("   3. اضافه کردن دسته‌بندی‌های قطعات به LookupValues")
        print("\n⚠️ نکته: باید متدهای JalaliDateInput را نیز اصلاح کنید")
    else:
        print("\n❌ ارتقای دیتابیس با خطا مواجه شد!")
        print("   لطفاً از پشتیبان استفاده کنید و مشکل را بررسی نمایید.")