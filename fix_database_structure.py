# fix_database_structure.py
import sqlite3
import os

def fix_database():
    """رفع ساختار دیتابیس و اضافه کردن ستون‌های missing"""
    db_path = "data/repair_shop.db"
    
    if not os.path.exists(db_path):
        print("❌ فایل دیتابیس یافت نشد!")
        return False
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("🔧 در حال رفع ساختار دیتابیس...")
    
    try:
        # 1. افزودن ستون‌های missing به جدول Settings
        cursor.execute("PRAGMA table_info(Settings)")
        columns = [col[1] for col in cursor.fetchall()]
        
        missing_columns = {
            'default_currency': 'TEXT DEFAULT "تومان"',
            'auto_backup': 'INTEGER DEFAULT 1',
            'backup_path': 'TEXT DEFAULT "data/backup/"',
            'company_name': 'TEXT DEFAULT ""',
            'company_address': 'TEXT DEFAULT ""',
            'company_phone': 'TEXT DEFAULT ""',
            'company_email': 'TEXT DEFAULT ""',
            'logo_path': 'TEXT DEFAULT ""',
            'date_format': 'TEXT DEFAULT "شمسی"',
            'language': 'TEXT DEFAULT "فارسی"',
            'theme': 'TEXT DEFAULT "dark"'
        }
        
        for col_name, col_def in missing_columns.items():
            if col_name not in columns:
                print(f"➕ افزودن ستون {col_name} به Settings")
                cursor.execute(f"ALTER TABLE Settings ADD COLUMN {col_name} {col_def}")
        
        # 2. ایجاد جدول FinancialSettings اگر وجود ندارد
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='FinancialSettings'")
        if not cursor.fetchone():
            print("📊 ایجاد جدول FinancialSettings")
            cursor.execute('''
            CREATE TABLE FinancialSettings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                default_discount REAL DEFAULT 0.0,
                max_credit_amount REAL DEFAULT 10000000,
                check_warning_days INTEGER DEFAULT 3,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            ''')
            
            # درج رکورد پیش‌فرض
            cursor.execute("INSERT INTO FinancialSettings (id) VALUES (1)")
        
        # 3. اطمینان از وجود رکورد Settings
        cursor.execute("SELECT COUNT(*) FROM Settings WHERE id = 1")
        if cursor.fetchone()[0] == 0:
            print("📝 درج رکورد پیش‌فرض Settings")
            cursor.execute("INSERT INTO Settings (id) VALUES (1)")
        
        conn.commit()
        print("✅ ساختار دیتابیس با موفقیت به‌روزرسانی شد")
        return True
        
    except Exception as e:
        print(f"❌ خطا: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    fix_database()