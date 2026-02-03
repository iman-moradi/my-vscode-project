# database.py - نسخه کامل با پشتیبانی تاریخ شمسی
import sqlite3
import os  # 🔴 ایمپورت os
from datetime import datetime, date
from PySide6.QtCore import QObject, Signal
import jdatetime

class DatabaseManager(QObject):
    database_initialized = Signal(bool)
    error_occurred = Signal(str)
    
    def __init__(self, db_name="data/repair_shop.db"):  # 🔴 تغییر مسیر پیش‌فرض
        super().__init__()
        self.db_name = db_name
        self.connection = None
        self.cursor = None
        
        # 🔴 ایجاد پوشه data اگر وجود ندارد
        self.ensure_data_directory()
    
    def ensure_data_directory(self):
        """ایجاد پوشه data در صورت عدم وجود"""
        directory = os.path.dirname(self.db_name)
        if directory and not os.path.exists(directory):
            try:
                os.makedirs(directory, exist_ok=True)
                print(f"📁 پوشه '{directory}' ایجاد شد")
            except Exception as e:
                print(f"⚠️ خطا در ایجاد پوشه: {e}")

        
    def connect(self):
        """اتصال به دیتابیس"""
        try:
            self.connection = sqlite3.connect(self.db_name)
            self.connection.execute("PRAGMA foreign_keys = ON")
            self.cursor = self.connection.cursor()
            self.connection.row_factory = sqlite3.Row
            return True
        except Exception as e:
            self.error_occurred.emit(f"خطا در اتصال به دیتابیس: {str(e)}")
            return False
    
    # در کلاس DatabaseManager در database.py

    def fetch_all(self, query, params=()):
        """دریافت تمام ردیف‌های یک کوئری"""
        try:
            # حذف کامنت‌های فارسی از کوئری
            clean_query = query.replace('#', '--')
            self.connect()
            self.cursor.execute(clean_query, params)
            rows = self.cursor.fetchall()
            
            # تبدیل به لیست دیکشنری
            result = []
            for row in rows:
                row_dict = {}
                for idx, col in enumerate(self.cursor.description):
                    row_dict[col[0]] = row[idx]
                result.append(row_dict)
            return result
            
        except Exception as e:
            print(f"خطا در fetch_all: {e}")
            print(f"کوئری اصلی: {query}")
            print(f"کوئری تمیز شده: {clean_query}")
            return []
        finally:
            if self.connection:
                self.connection.close()


    def fetch_one(self, query, params=()):
        """دریافت یک ردیف از کوئری"""
        try:
            # حذف کامنت‌های فارسی از کوئری (جایگزینی # با --)
            clean_query = query.replace('#', '--')
            self.connect()
            self.cursor.execute(clean_query, params)
            row = self.cursor.fetchone()
            
            if row:
                row_dict = {}
                for idx, col in enumerate(self.cursor.description):
                    row_dict[col[0]] = row[idx]
                return row_dict
            return None
            
        except Exception as e:
            print(f"خطا در fetch_one: {e}")
            print(f"کوئری اصلی: {query}")
            print(f"کوئری تمیز شده: {clean_query}")
            print(f"پارامترها: {params}")
            return None
        finally:
            if self.connection:
                self.connection.close()


    def execute_query(self, query, params=()):
        """اجرای کوئری INSERT/UPDATE/DELETE"""
        try:
            self.connect()

            
            self.cursor.execute(query, params)
            self.connection.commit()
            return True
            
        except sqlite3.Error as e:
            print(f"❌ خطای SQLite در execute_query: {e}")
            print(f"   کوئری: {query}")
            print(f"   پارامترها: {params}")
            if self.connection:
                self.connection.rollback()
            return False
        except Exception as e:
            print(f"❌ خطای عمومی در execute_query: {e}")
            if self.connection:
                self.connection.rollback()
            return False
        finally:
            if self.connection:
                self.connection.close()

    # در کلاس DatabaseManager، این توابع را اضافه یا اصلاح کنید:

    def gregorian_to_jalali(self, gregorian_date, format_str="%Y/%m/%d"):
        """تبدیل تاریخ میلادی به شمسی (برای نمایش)"""
        if not gregorian_date:
            return ""
        
        try:
            if isinstance(gregorian_date, str):
                # اگر رشته تاریخ میلادی است
                for fmt in ["%Y-%m-%d", "%Y/%m/%d", "%Y-%m-%d %H:%M:%S", "%Y/%m/%d %H:%M:%S"]:
                    try:
                        date_obj = datetime.strptime(gregorian_date, fmt)
                        jalali = jdatetime.date.fromgregorian(date=date_obj.date())
                        return jalali.strftime(format_str)
                    except:
                        continue
            
            elif isinstance(gregorian_date, date):
                # اگر شیء date است
                jalali = jdatetime.date.fromgregorian(date=gregorian_date)
                return jalali.strftime(format_str)
                
        except Exception as e:
            print(f"خطا در تبدیل تاریخ میلادی به شمسی: {e}")
        
        return str(gregorian_date)

    def jalali_to_gregorian(self, jalali_date_str, format_str="%Y-%m-%d"):
        """تبدیل تاریخ شمسی به میلادی (برای ذخیره در دیتابیس)"""
        if not jalali_date_str:
            return None
        
        try:
            # حذف فاصله و نویسه‌های اضافی
            jalali_date_str = str(jalali_date_str).strip()
            
            # اگر تاریخ میلادی است، برگردان
            if '-' in jalali_date_str and len(jalali_date_str.split('-')) == 3:
                parts = jalali_date_str.split('-')
                if len(parts[0]) == 4 and int(parts[0]) > 1500:
                    return jalali_date_str  # احتمالاً میلادی است
            
            # فرض می‌کنیم تاریخ شمسی است
            # حذف کاراکترهای غیرعددی
            import re
            numbers = re.findall(r'\d+', jalali_date_str)
            
            if len(numbers) >= 3:
                year, month, day = map(int, numbers[:3])
                
                # تشخیص اینکه آیا تاریخ شمسی است (سال بین 1300-1500)
                if 1300 <= year <= 1500:
                    jalali = jdatetime.date(year, month, day)
                    gregorian = jalali.togregorian()
                    return gregorian.strftime(format_str)
                else:
                    # احتمالاً میلادی است
                    return f"{year:04d}-{month:02d}-{day:02d}"
                    
        except Exception as e:
            print(f"خطا در تبدیل تاریخ شمسی به میلادی: {e}")
            print(f"ورودی: {jalali_date_str}")
        
        return jalali_date_str

  
    def get_current_jalali_date(self):
        """دریافت تاریخ شمسی امروز"""
        return jdatetime.datetime.now().strftime("%Y/%m/%d")
    
    def get_current_jalali_datetime(self):
        """دریافت تاریخ و زمان شمسی فعلی"""
        return jdatetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S")
    

    def migrate_used_appliances_warehouse(self):
        """مهاجرت جدول UsedAppliancesWarehouse به ساختار انعطاف‌پذیر"""
        try:
            self.connect()
            
            # 1. بررسی وجود جدول قدیمی
            self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='UsedAppliancesWarehouse'")
            if not self.cursor.fetchone():
                print("جدول UsedAppliancesWarehouse وجود ندارد.")
                return True
            
            # 2. بررسی ساختار فعلی
            self.cursor.execute("PRAGMA table_info(UsedAppliancesWarehouse)")
            columns = [col[1] for col in self.cursor.fetchall()]
            
            if 'device_type_id' in columns:
                print("جدول UsedAppliancesWarehouse قبلاً به ساختار جدید مهاجرت کرده است.")
                return True
            
            print("🔧 شروع مهاجرت جدول UsedAppliancesWarehouse...")
            
            # 3. ایجاد جدول جدید با ساختار انعطاف‌پذیر
            self.cursor.execute('''
            CREATE TABLE UsedAppliancesWarehouse_New (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                device_type_id INTEGER NOT NULL,
                brand_id INTEGER NOT NULL,
                model TEXT NOT NULL,
                serial_number TEXT UNIQUE,
                production_year INTEGER,
                source_type TEXT CHECK(source_type IN ('مشتری', 'تامین کننده', 'تعویض شده')) DEFAULT 'مشتری',
                source_person_id INTEGER,
                original_reception_id INTEGER,
                condition TEXT CHECK(condition IN ('در حد نو', 'خیلی خوب', 'خوب', 'متوسط', 'نیاز به تعمیر جزئی', 'نیاز به تعمیر اساسی')),
                technical_status TEXT,
                last_repair_date DATE,
                repair_history TEXT,
                purchase_price DECIMAL(15, 2) NOT NULL,
                purchase_date DATE DEFAULT CURRENT_DATE,
                purchase_document TEXT,
                sale_price DECIMAL(15, 2) NOT NULL,
                warranty_type TEXT CHECK(warranty_type IN ('گارانتی فروشگاه', 'گارانتی کارخانه', 'فاقد گارانتی')) DEFAULT 'گارانتی فروشگاه',
                warranty_days INTEGER DEFAULT 90,
                warranty_description TEXT,
                quantity INTEGER DEFAULT 0,
                location TEXT,
                status TEXT CHECK(status IN ('موجود', 'ناموجود', 'فروخته شده', 'در حال تعمیر', 'رزرو شده', 'اسقاط')) DEFAULT 'موجود',
                accessories TEXT,
                description TEXT,
                photos_path TEXT,
                entry_date DATE DEFAULT CURRENT_DATE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (device_type_id) REFERENCES DeviceCategories_name(id),
                FOREIGN KEY (brand_id) REFERENCES Brands(id),
                FOREIGN KEY (source_person_id) REFERENCES Persons(id),
                FOREIGN KEY (original_reception_id) REFERENCES Receptions(id)
            )
            ''')
            
            # 4. دریافت داده‌های قدیمی
            self.cursor.execute('''
            SELECT 
                uaw.*,
                d.device_type as old_device_type,
                d.brand as old_brand,
                d.model as old_model,
                d.serial_number as old_serial,
                d.production_year as old_year,
                d.description as old_description
            FROM UsedAppliancesWarehouse uaw
            LEFT JOIN Devices d ON uaw.device_id = d.id
            ''')
            
            old_data = self.cursor.fetchall()
            print(f"📊 تعداد رکوردهای قدیمی: {len(old_data)}")
            
            # 5. انتقال داده‌ها
            for row in old_data:
                # تبدیل device_type به ID
                device_type_name = row['old_device_type'] if row['old_device_type'] else 'سایر'
                self.cursor.execute(
                    "SELECT id FROM DeviceCategories_name WHERE name = ?",
                    (device_type_name,)
                )
                device_type_result = self.cursor.fetchone()
                
                if device_type_result:
                    device_type_id = device_type_result[0]
                else:
                    self.cursor.execute(
                        "INSERT INTO DeviceCategories_name (name) VALUES (?)",
                        (device_type_name,)
                    )
                    device_type_id = self.cursor.lastrowid
                
                # تبدیل brand به ID
                brand_name = row['old_brand'] if row['old_brand'] else 'نامشخص'
                self.cursor.execute(
                    "SELECT id FROM Brands WHERE name = ?",
                    (brand_name,)
                )
                brand_result = self.cursor.fetchone()
                
                if brand_result:
                    brand_id = brand_result[0]
                else:
                    self.cursor.execute(
                        "INSERT INTO Brands (name) VALUES (?)",
                        (brand_name,)
                    )
                    brand_id = self.cursor.lastrowid
                
                # تعیین source_type
                if row['source_customer']:
                    source_type = 'مشتری'
                    source_person_id = row['source_customer']
                else:
                    source_type = 'تامین کننده'
                    source_person_id = row.get('supplier_id')
                
                # درج در جدول جدید
                self.cursor.execute('''
                INSERT INTO UsedAppliancesWarehouse_New (
                    device_type_id, brand_id, model, serial_number, production_year,
                    source_type, source_person_id, condition, purchase_price, sale_price,
                    purchase_date, warranty_days, quantity, location, status, description,
                    created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    device_type_id,
                    brand_id,
                    row['old_model'] if row['old_model'] else 'نامشخص',
                    row['old_serial'],
                    row['old_year'],
                    source_type,
                    source_person_id,
                    row.get('condition', 'خوب'),
                    row['purchase_price'],
                    row['sale_price'],
                    row['purchase_date'],
                    row.get('warranty_days', 90),
                    row['quantity'],
                    row['location'],
                    row['status'],
                    row['old_description'] if row['old_description'] else '',
                    row['created_at']
                ))
            
            # 6. حذف جدول قدیمی و تغییر نام
            self.cursor.execute("DROP TABLE UsedAppliancesWarehouse")
            self.cursor.execute("ALTER TABLE UsedAppliancesWarehouse_New RENAME TO UsedAppliancesWarehouse")
            
            # 7. ایجاد ایندکس‌ها
            indexes = [
                "CREATE INDEX IF NOT EXISTS idx_used_appliances_device_type ON UsedAppliancesWarehouse(device_type_id)",
                "CREATE INDEX IF NOT EXISTS idx_used_appliances_brand ON UsedAppliancesWarehouse(brand_id)",
                "CREATE INDEX IF NOT EXISTS idx_used_appliances_source ON UsedAppliancesWarehouse(source_type, source_person_id)",
                "CREATE INDEX IF NOT EXISTS idx_used_appliances_status ON UsedAppliancesWarehouse(status)",
                "CREATE INDEX IF NOT EXISTS idx_used_appliances_condition ON UsedAppliancesWarehouse(condition)"
            ]
            
            for index_sql in indexes:
                self.cursor.execute(index_sql)
            
            self.connection.commit()
            print("✅ مهاجرت جدول UsedAppliancesWarehouse با موفقیت انجام شد.")
            return True
            
        except Exception as e:
            print(f"❌ خطا در مهاجرت جدول UsedAppliancesWarehouse: {e}")
            import traceback
            traceback.print_exc()
            if self.connection:
                self.connection.rollback()
            return False
        finally:
            if self.connection:
                self.connection.close()

    def initialize_database(self):
        """ایجاد جداول دیتابیس"""
        try:
            self.connect()
            
            # ایجاد جدول تنظیمات
            self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS Settings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                app_name TEXT DEFAULT 'سیستم مدیریت تعمیرگاه لوازم خانگی',
                company_name TEXT,
                company_address TEXT,
                company_phone TEXT,
                company_email TEXT,
                logo_path TEXT,
                date_format TEXT DEFAULT 'شمسی',
                language TEXT DEFAULT 'فارسی',
                theme TEXT DEFAULT 'dark',
                font_name TEXT DEFAULT 'B Nazanin',
                font_size INTEGER DEFAULT 11,
                bg_color TEXT DEFAULT '#000000',      # 🔴 سیاه
                text_color TEXT DEFAULT '#FFFFFF',    # 🔴 سفید
                default_currency TEXT DEFAULT 'تومان',
                tax_percentage REAL DEFAULT 9.0,
                auto_backup INTEGER DEFAULT 1,
                backup_path TEXT DEFAULT 'data/backup/',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            ''')
            
            # ایجاد جدول اشخاص
            self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS Persons (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                person_type TEXT CHECK(person_type IN ('مشتری', 'تامین کننده', 'تعمیرکار بیرونی', 'شریک', 'کارمند')),
                first_name TEXT NOT NULL,
                last_name TEXT NOT NULL,
                full_name TEXT GENERATED ALWAYS AS (first_name || ' ' || last_name) VIRTUAL,
                mobile TEXT UNIQUE,
                phone TEXT,
                address TEXT,
                national_id TEXT,
                economic_code TEXT,
                registration_date DATE DEFAULT CURRENT_DATE,
                is_active BOOLEAN DEFAULT 1,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            ''')

            # در تابع initialize_database() فایل database.py، جایی نزدیک به انتهای لیست CREATE TABLEها:
            self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS LookupValues (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category TEXT NOT NULL,       -- دسته: 'device_type', 'device_brand'
                value TEXT NOT NULL,          -- مقدار: 'یخچال', 'ال جی'
                display_order INTEGER DEFAULT 0, -- ترتیب نمایش
                is_active BOOLEAN DEFAULT 1,     -- فعال/غیرفعال
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(category, value)          -- جلوگیری از تکرار
            )
            ''')


            # ایجاد جدول دستگاه‌ها
            self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS Devices (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                device_type TEXT NOT NULL,
                brand TEXT NOT NULL,
                model TEXT NOT NULL,
                serial_number TEXT UNIQUE,
                production_year INTEGER,
                purchase_date DATE,
                warranty_status BOOLEAN DEFAULT 0,
                warranty_end_date DATE,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            ''')
            

            # در فایل database.py، در تابع initialize_database()، بعد از جدول LookupValues اضافه کنید:
            self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS DeviceCategories_name (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            ''')

            # درج چند دسته‌بندی پیش‌فرض
            default_categories = [
                'سشوار',
                'لباسشویی', 
                'جاروبرقی',
                'پنکه',
                'یخچال',
                'فریزر',
                'ماشین ظرفشویی',
                'مایکروویو',
                'اجاق گاز',
                'هود',
                'کولر',
                'بخاری',
                'آبسردکن',
                'آبگرمکن',
                'اتو',
                'چرخ گوشت',
                'مخلوط کن',
                'آسیاب',
                'قهوه ساز',
                'سایر'
            ]

            for category in default_categories:
                self.cursor.execute('''
                INSERT OR IGNORE INTO DeviceCategories_name (name) 
                VALUES (?)
                ''', (category,))

            #جدول معرفی برندها
            self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS Brands (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            ''')

            # ایجاد جدول پذیرش
            self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS Receptions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                reception_number TEXT UNIQUE NOT NULL,
                customer_id INTEGER NOT NULL,
                device_id INTEGER NOT NULL,
                reception_date DATE DEFAULT CURRENT_DATE,
                reception_time TIME DEFAULT CURRENT_TIME,
                problem_description TEXT NOT NULL,
                device_condition TEXT,
                accessories TEXT,
                estimated_cost DECIMAL(15, 2) DEFAULT 0,
                estimated_delivery_date DATE,
                priority TEXT CHECK(priority IN ('عادی', 'فوری', 'خیلی فوری')) DEFAULT 'عادی',
                status TEXT CHECK(status IN ('در انتظار', 'در حال تعمیر', 'تعمیر شده', 'تحویل داده شده', 'لغو شده')) DEFAULT 'در انتظار',
                reception_employee TEXT,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (customer_id) REFERENCES Persons(id) ON DELETE CASCADE,
                FOREIGN KEY (device_id) REFERENCES Devices(id) ON DELETE CASCADE
            )
            ''')
            
            # ایجاد جدول تعمیرات
            self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS Repairs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                reception_id INTEGER NOT NULL,
                repair_date DATE DEFAULT CURRENT_DATE,
                technician_id INTEGER,
                repair_type TEXT CHECK(repair_type IN ('داخلی', 'بیرون سپاری')) DEFAULT 'داخلی',
                outsourced_to INTEGER,
                outsourced_cost DECIMAL(15, 2) DEFAULT 0,
                outsourced_description TEXT,  -- ✅ اضافه شد
                labor_cost DECIMAL(15, 2) DEFAULT 0,
                total_cost DECIMAL(15, 2) DEFAULT 0,
                repair_description TEXT,
                used_parts TEXT,
                start_time DATETIME,
                end_time DATETIME,
                status TEXT CHECK(status IN ('شروع شده', 'در حال انجام', 'تمام شده', 'متوقف شده')) DEFAULT 'شروع شده',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (reception_id) REFERENCES Receptions(id) ON DELETE CASCADE,
                FOREIGN KEY (technician_id) REFERENCES Persons(id),
                FOREIGN KEY (outsourced_to) REFERENCES Persons(id)
            )
            ''')
            

            self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS Repair_Services (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                repair_id INTEGER NOT NULL,
                service_id INTEGER NOT NULL,  -- ارجاع به ServiceFees
                quantity DECIMAL(5, 2) DEFAULT 1.0,
                unit_price DECIMAL(15, 2) NOT NULL,
                total_price DECIMAL(15, 2) NOT NULL,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (repair_id) REFERENCES Repairs(id) ON DELETE CASCADE,
                FOREIGN KEY (service_id) REFERENCES ServiceFees(id)
            )
            ''')

            # قطعات مصرفی تعمیر
            self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS Repair_Parts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                repair_id INTEGER NOT NULL,
                part_id INTEGER NOT NULL,
                quantity INTEGER NOT NULL,
                unit_price DECIMAL(15, 2) NOT NULL,
                total_price DECIMAL(15, 2) NOT NULL,
                warehouse_type TEXT CHECK(warehouse_type IN ('قطعات نو', 'قطعات دست دوم')),
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (repair_id) REFERENCES Repairs(id) ON DELETE CASCADE,
                FOREIGN KEY (part_id) REFERENCES Parts(id)
            )
            ''')

            # ایجاد جدول قطعات
            self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS Parts (
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
            
            # ایجاد جدول اجرت‌های استاندارد (تعرفه خدمات)
            self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS ServiceFees (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                service_code TEXT UNIQUE NOT NULL,
                service_name TEXT NOT NULL,
                category TEXT NOT NULL,
                default_fee DECIMAL(15, 2) NOT NULL,
                estimated_hours DECIMAL(5, 2) DEFAULT 1.0,
                difficulty_level INTEGER DEFAULT 1 CHECK(difficulty_level BETWEEN 1 AND 5),
                description TEXT,
                is_active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            ''')



            # ایجاد جدول انبار قطعات نو
            self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS NewPartsWarehouse (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                part_id INTEGER NOT NULL,
                quantity INTEGER DEFAULT 0,
                purchase_price DECIMAL(15, 2) NOT NULL,
                sale_price DECIMAL(15, 2) NOT NULL,
                supplier_id INTEGER,
                purchase_date DATE DEFAULT CURRENT_DATE,
                batch_number TEXT,
                location TEXT,
                expiration_date DATE,
                status TEXT CHECK(status IN ('موجود', 'ناموجود', 'در حال سفارش', 'منقضی شده')) DEFAULT 'موجود',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (part_id) REFERENCES Parts(id) ON DELETE CASCADE,
                FOREIGN KEY (supplier_id) REFERENCES Persons(id)
            )
            ''')
            
            # ایجاد جدول انبار قطعات دست دوم
            self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS UsedPartsWarehouse (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                part_id INTEGER NOT NULL,
                quantity INTEGER DEFAULT 0,
                purchase_price DECIMAL(15, 2) NOT NULL,
                sale_price DECIMAL(15, 2) NOT NULL,
                source_device TEXT,
                condition TEXT CHECK(condition IN ('عالی', 'خوب', 'متوسط', 'ضعیف')) DEFAULT 'خوب',
                purchase_date DATE DEFAULT CURRENT_DATE,
                warranty_days INTEGER DEFAULT 30,
                location TEXT,
                status TEXT CHECK(status IN ('موجود', 'ناموجود', 'اسقاط')) DEFAULT 'موجود',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (part_id) REFERENCES Parts(id) ON DELETE CASCADE
            )
            ''')
            
            # ایجاد جدول انبار لوازم خانگی نو
            self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS NewAppliancesWarehouse (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                device_type_id INTEGER NOT NULL,          
                brand_id INTEGER NOT NULL,                 
                model TEXT NOT NULL,                      
                serial_number TEXT,                       
                production_year INTEGER,                  
                quantity INTEGER DEFAULT 0,
                purchase_price DECIMAL(15, 2) NOT NULL,
                sale_price DECIMAL(15, 2) NOT NULL,
                supplier_id INTEGER NOT NULL,
                purchase_date DATE DEFAULT CURRENT_DATE,
                warranty_months INTEGER DEFAULT 12,
                location TEXT,
                status TEXT CHECK(status IN ('موجود', 'ناموجود', 'رزرو شده', 'فروخته شده')) DEFAULT 'موجود',
                description TEXT,                         
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (device_type_id) REFERENCES DeviceCategories_name(id),
                FOREIGN KEY (brand_id) REFERENCES Brands(id),
                FOREIGN KEY (supplier_id) REFERENCES Persons(id)
            )
            ''')

            self.migrate_new_appliances_warehouse()
            
            # ایجاد جدول انبار لوازم خانگی دست دوم
            self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS UsedAppliancesWarehouse (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                
                -- حالت 1: دستگاه از مشتری خریداری شده (بعد از تعمیر یا قبل از تعمیر)
                -- حالت 2: دستگاه از بیرون خریداری شده
                
                -- **مشخصات دستگاه**
                device_type_id INTEGER NOT NULL,  -- نوع دستگاه (از DeviceCategories_name)
                brand_id INTEGER NOT NULL,        -- برند (از Brands)
                model TEXT NOT NULL,              -- مدل
                serial_number TEXT UNIQUE,        -- شماره سریال
                production_year INTEGER,          -- سال تولید
                
                -- **منبع دستگاه**
                source_type TEXT CHECK(source_type IN ('مشتری', 'تامین کننده', 'تعویض شده')) DEFAULT 'مشتری',
                source_person_id INTEGER,         -- آیدی شخص (مشتری یا تامین کننده)
                original_reception_id INTEGER,    -- اگر از مشتری خریداری شده، آیدی پذیرش اصلی
                
                -- **وضعیت فنی**
                condition TEXT CHECK(condition IN ('در حد نو', 'خیلی خوب', 'خوب', 'متوسط', 'نیاز به تعمیر جزئی', 'نیاز به تعمیر اساسی')),
                technical_status TEXT,            -- وضعیت فنی دقیق (JSON یا متن)
                last_repair_date DATE,           -- تاریخ آخرین تعمیر
                repair_history TEXT,              -- تاریخچه تعمیرات
                
                -- **اطلاعات خرید**
                purchase_price DECIMAL(15, 2) NOT NULL,  -- قیمت خرید
                purchase_date DATE DEFAULT CURRENT_DATE, -- تاریخ خرید
                purchase_document TEXT,          -- شماره سند خرید
                
                -- **اطلاعات فروش**
                sale_price DECIMAL(15, 2) NOT NULL,      -- قیمت پیشنهادی فروش
                expected_profit DECIMAL(15, 2) GENERATED ALWAYS AS (sale_price - purchase_price) VIRTUAL,
                
                -- **گارانتی**
                warranty_type TEXT CHECK(warranty_type IN ('گارانتی فروشگاه', 'گارانتی کارخانه', 'فاقد گارانتی')) DEFAULT 'گارانتی فروشگاه',
                warranty_days INTEGER DEFAULT 90,        -- روزهای گارانتی
                warranty_description TEXT,               -- توضیحات گارانتی
                
                -- **انبارداری**
                quantity INTEGER DEFAULT 0,
                location TEXT,                           -- محل انبار
                status TEXT CHECK(status IN ('موجود', 'ناموجود', 'فروخته شده', 'در حال تعمیر', 'رزرو شده', 'اسقاط')) DEFAULT 'موجود',
                
                -- **اطلاعات تکمیلی**
                accessories TEXT,                        -- لوازم همراه (مدارک، ریموت، ...)
                description TEXT,                        -- توضیحات
                photos_path TEXT,                        -- مسیر عکس‌ها (JSON)
                
                -- **زمان‌بندی**
                entry_date DATE DEFAULT CURRENT_DATE,    -- تاریخ ورود به انبار
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                
                -- **کلیدهای خارجی**
                FOREIGN KEY (device_type_id) REFERENCES DeviceCategories_name(id),
                FOREIGN KEY (brand_id) REFERENCES Brands(id),
                FOREIGN KEY (source_person_id) REFERENCES Persons(id),
                FOREIGN KEY (original_reception_id) REFERENCES Receptions(id)
            )
            ''')

                        
            # ایجاد جدول تراکنش‌های انبار
            self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS InventoryTransactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                transaction_type TEXT CHECK(transaction_type IN ('خرید', 'فروش', 'استفاده در تعمیر', 'برگشت', 'تعدیل', 'ضایعات', 'انتقال')),
                warehouse_type TEXT CHECK(warehouse_type IN ('قطعات نو', 'قطعات دست دوم', 'لوازم نو', 'لوازم دست دوم')),
                item_id INTEGER NOT NULL,
                quantity INTEGER NOT NULL,
                unit_price DECIMAL(15, 2) NOT NULL,
                total_price DECIMAL(15, 2) NOT NULL,
                transaction_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                related_document TEXT,
                related_reception INTEGER,
                description TEXT,
                employee TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (related_reception) REFERENCES Receptions(id)
            )
            ''')
            
            # ایجاد جدول فاکتورها
            self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS Invoices (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                invoice_number TEXT UNIQUE NOT NULL,
                invoice_type TEXT CHECK(invoice_type IN ('فروش', 'خدمات', 'بیرون سپاری', 'خرید', 'مرجوعی')),
                customer_id INTEGER,
                reception_id INTEGER,
                invoice_date DATE DEFAULT CURRENT_DATE,
                due_date DATE,
                subtotal DECIMAL(15, 2) DEFAULT 0,
                discount DECIMAL(15, 2) DEFAULT 0,
                tax DECIMAL(15, 2) DEFAULT 0,
                total DECIMAL(15, 2) DEFAULT 0,
                paid_amount DECIMAL(15, 2) DEFAULT 0,
                remaining_amount DECIMAL(15, 2) DEFAULT 0,
                payment_status TEXT CHECK(payment_status IN ('پرداخت شده', 'نقدی', 'نسیه', 'چک', 'کارت')) DEFAULT 'نقدی',
                payment_method TEXT,
                description TEXT,
                outsourced_to INTEGER,
                outsourced_cost DECIMAL(15, 2) DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (customer_id) REFERENCES Persons(id),
                FOREIGN KEY (reception_id) REFERENCES Receptions(id),
                FOREIGN KEY (outsourced_to) REFERENCES Persons(id)
            )
            ''')
            
            # ایجاد جدول اقلام فاکتور
            self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS InvoiceItems (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                invoice_id INTEGER NOT NULL,
                item_type TEXT CHECK(item_type IN ('قطعه', 'خدمات', 'دستگاه', 'اجرت')),
                item_id INTEGER,
                item_name TEXT NOT NULL,
                quantity INTEGER DEFAULT 1,
                unit_price DECIMAL(15, 2) NOT NULL,
                total_price DECIMAL(15, 2) NOT NULL,
                description TEXT,
                partner_percentage DECIMAL(5, 2) DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (invoice_id) REFERENCES Invoices(id) ON DELETE CASCADE
            )
            ''')
            
            # ایجاد جدول شرکا
            self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS Partners (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                person_id INTEGER NOT NULL,
                partnership_start DATE DEFAULT CURRENT_DATE,
                partnership_end DATE,
                active BOOLEAN DEFAULT 1,
                capital DECIMAL(15, 2) DEFAULT 0,
                profit_percentage DECIMAL(5, 2) DEFAULT 0,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (person_id) REFERENCES Persons(id) ON DELETE CASCADE
            )
            ''')
            
            # ایجاد جدول سهم شرکا
            self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS PartnerShares (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                partner_id INTEGER NOT NULL,
                transaction_type TEXT CHECK(transaction_type IN ('فروش قطعات نو', 'فروش قطعات دست دوم', 'فروش لوازم نو', 'فروش لوازم دست دوم', 'خدمات تعمیر', 'بیرون سپاری')),
                transaction_id INTEGER NOT NULL,
                share_percentage DECIMAL(5, 2) NOT NULL,
                share_amount DECIMAL(15, 2) NOT NULL,
                calculation_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (partner_id) REFERENCES Partners(id) ON DELETE CASCADE
            )
            ''')
            
            # ایجاد جدول حساب‌ها
            self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS Accounts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                account_number TEXT UNIQUE NOT NULL,
                account_name TEXT NOT NULL,
                account_type TEXT CHECK(account_type IN ('جاری', 'پس‌انداز', 'صندوق', 'بانکی', 'نقدی')),
                bank_name TEXT,
                initial_balance DECIMAL(15, 2) DEFAULT 0,
                current_balance DECIMAL(15, 2) DEFAULT 0,
                owner_name TEXT,
                is_active BOOLEAN DEFAULT 1,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            ''')
            
            # ایجاد جدول تراکنش‌های حسابداری
            self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS AccountingTransactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                transaction_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                transaction_type TEXT CHECK(transaction_type IN ('دریافت', 'پرداخت', 'انتقال', 'سود', 'هزینه', 'درآمد')),
                from_account_id INTEGER,
                to_account_id INTEGER,
                amount DECIMAL(15, 2) NOT NULL,
                description TEXT NOT NULL,
                reference_id INTEGER,
                reference_type TEXT,
                employee TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (from_account_id) REFERENCES Accounts(id),
                FOREIGN KEY (to_account_id) REFERENCES Accounts(id)
            )
            ''')
            
            # ایجاد جدول چک‌ها
            self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS Checks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                check_number TEXT NOT NULL,
                bank_name TEXT NOT NULL,
                branch TEXT,
                account_number TEXT,
                amount DECIMAL(15, 2) NOT NULL,
                issue_date DATE,
                due_date DATE NOT NULL,
                drawer TEXT NOT NULL,
                payee TEXT NOT NULL,
                status TEXT CHECK(status IN ('وصول نشده', 'وصول شده', 'برگشتی', 'پاس شده', 'پاس نشده', 'بلوکه شده')) DEFAULT 'وصول نشده',
                check_type TEXT CHECK(check_type IN ('دریافتی', 'پرداختی')) DEFAULT 'دریافتی',
                related_invoice INTEGER,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (related_invoice) REFERENCES Invoices(id)
            )
            ''')
            
            # ایجاد جدول پنل پیامکی
            self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS SMSPanel (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                panel_name TEXT NOT NULL,
                api_url TEXT,
                api_key TEXT,
                username TEXT,
                password TEXT,
                line_number TEXT,
                is_active BOOLEAN DEFAULT 0,
                balance INTEGER DEFAULT 0,
                last_update DATETIME,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            ''')
            
            # ایجاد جدول پیام‌ها
            self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS Messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                reception_id INTEGER,
                customer_id INTEGER NOT NULL,
                message_type TEXT CHECK(message_type IN ('ورود دستگاه', 'آماده شدن', 'تحویل', 'تاخیر', 'پیام عمومی', 'اعلان')),
                message_text TEXT NOT NULL,
                send_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                send_status TEXT CHECK(send_status IN ('ارسال شده', 'در صف', 'خطا', 'ذخیره شده')) DEFAULT 'ذخیره شده',
                response TEXT,
                mobile_number TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (reception_id) REFERENCES Receptions(id),
                FOREIGN KEY (customer_id) REFERENCES Persons(id)
            )
            ''')
            
            # ایجاد جدول کاربران سیستم
            self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS Users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                person_id INTEGER,
                role TEXT CHECK(role IN ('مدیر', 'اپراتور', 'انباردار', 'حسابدار', 'مشاهده‌گر')) DEFAULT 'اپراتور',
                is_active BOOLEAN DEFAULT 1,
                last_login DATETIME,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (person_id) REFERENCES Persons(id)
            )
            ''')
            
            # ایجاد جدول تنظیمات امنیتی
            self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS SecuritySettings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                max_login_attempts INTEGER DEFAULT 3,
                lockout_minutes INTEGER DEFAULT 15,
                session_timeout_minutes INTEGER DEFAULT 30,
                force_logout BOOLEAN DEFAULT 1,
                remember_me BOOLEAN DEFAULT 1,
                min_password_length INTEGER DEFAULT 8,
                password_expiry_days INTEGER DEFAULT 90,
                password_history_count INTEGER DEFAULT 5,
                require_uppercase BOOLEAN DEFAULT 1,
                require_lowercase BOOLEAN DEFAULT 1,
                require_numbers BOOLEAN DEFAULT 1,
                require_special BOOLEAN DEFAULT 0,
                enable_2fa BOOLEAN DEFAULT 0,
                twofa_method TEXT DEFAULT 'پیامک',
                twofa_force_admin BOOLEAN DEFAULT 1,
                twofa_force_all BOOLEAN DEFAULT 0,
                encrypt_passwords BOOLEAN DEFAULT 1,
                encrypt_financial BOOLEAN DEFAULT 1,
                encrypt_personal BOOLEAN DEFAULT 0,
                encrypt_backups BOOLEAN DEFAULT 1,
                encryption_key_hash TEXT,
                ssl_required BOOLEAN DEFAULT 0,
                block_external BOOLEAN DEFAULT 1,
                firewall_level TEXT DEFAULT 'متوسط',
                allowed_ips TEXT,
                audit_log BOOLEAN DEFAULT 1,
                auto_logout BOOLEAN DEFAULT 1,
                inactivity_minutes INTEGER DEFAULT 10,
                show_warnings BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            ''')

            # درج تنظیمات پیش‌فرض
            self.cursor.execute('''
            INSERT OR IGNORE INTO SecuritySettings (id) VALUES (1)
            ''')

            # ایجاد جدول لاگ‌ها
            self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS Logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                action TEXT NOT NULL,
                table_name TEXT,
                record_id INTEGER,
                details TEXT,
                ip_address TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES Users(id)
            )
            ''')
            
            # درج تنظیمات پیش‌فرض با تاریخ شمسی
            self.cursor.execute('''
            INSERT OR IGNORE INTO Settings (id, app_name, date_format) 
            VALUES (1, 'سیستم مدیریت تعمیرگاه لوازم خانگی', 'شمسی')
            ''')
            

            self.cursor.execute('''
            INSERT OR IGNORE INTO Users (username, password, role) 
            VALUES ('admin', 'admin123', 'مدیر')
            ''')

            # جدول ثبت حذف انبار 
            self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS InventoryDeleteTransactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                warehouse_type TEXT NOT NULL,
                item_id INTEGER NOT NULL,
                quantity INTEGER NOT NULL DEFAULT 0,
                unit_price REAL NOT NULL DEFAULT 0,
                total_price REAL NOT NULL DEFAULT 0,
                deletion_date TEXT NOT NULL,
                deletion_reason TEXT,
                description TEXT,
                deleted_by TEXT DEFAULT 'سیستم',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            ''')

                # جدول حذف‌های نرم
            self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS InventorySoftDeletions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                warehouse_type TEXT NOT NULL,
                item_id INTEGER NOT NULL,
                quantity INTEGER NOT NULL DEFAULT 0,
                unit_price REAL NOT NULL DEFAULT 0,
                total_price REAL NOT NULL DEFAULT 0,
                deletion_date TEXT NOT NULL,
                deletion_reason TEXT,
                original_status TEXT NOT NULL,
                new_status TEXT NOT NULL,
                description TEXT,
                deleted_by TEXT DEFAULT 'سیستم',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            ''')
            

            self.migrate_missing_columns()
            # ایجاد ایندکس‌ها برای بهبود عملکرد
            self.create_indexes()
            
            self.connection.commit()
            self.database_initialized.emit(True)
            return True
            
        except Exception as e:
            self.error_occurred.emit(f"خطا در ایجاد دیتابیس: {str(e)}")
            return False
        finally:
            if self.connection:
                self.connection.close()

    def migrate_missing_columns(self):
        """اضافه کردن ستون‌های گمشده به جداول"""
        try:
            self.connect()
            
            # 1. بررسی و اضافه کردن issue_date به جدول Checks (اگر وجود ندارد)
            self.cursor.execute("PRAGMA table_info(Checks)")
            check_columns = [col[1] for col in self.cursor.fetchall()]
            
            if 'issue_date' not in check_columns:
                print("🔧 افزودن ستون issue_date به جدول Checks")
                self.cursor.execute("ALTER TABLE Checks ADD COLUMN issue_date DATE DEFAULT CURRENT_DATE")
                self.connection.commit()
            
            # 2. بررسی و اضافه کردن invoice_date به جدول Invoices (اگر وجود ندارد)
            self.cursor.execute("PRAGMA table_info(Invoices)")
            invoice_columns = [col[1] for col in self.cursor.fetchall()]
            
            if 'invoice_date' not in invoice_columns:
                print("🔧 افزودن ستون invoice_date به جدول Invoices")
                self.cursor.execute("ALTER TABLE Invoices ADD COLUMN invoice_date DATE DEFAULT CURRENT_DATE")
                self.connection.commit()
            
            # 3. بروزرسانی داده‌های قدیمی
            print("🔄 بروزرسانی داده‌های قدیمی...")
            
            # برای Checks: اگر issue_date خالی است، از due_date استفاده کن
            self.cursor.execute("UPDATE Checks SET issue_date = due_date WHERE issue_date IS NULL")
            
            # برای Invoices: اگر invoice_date خالی است، از created_at استفاده کن
            self.cursor.execute("UPDATE Invoices SET invoice_date = date(created_at) WHERE invoice_date IS NULL")
            
            self.connection.commit()
            print("✅ مهاجرت ستون‌های گمشده انجام شد")
            return True
            
        except Exception as e:
            print(f"⚠️ خطا در مهاجرت ستون‌های گمشده: {e}")
            return False
        finally:
            if self.connection:
                self.connection.close()


    def create_indexes(self):
        """ایجاد ایندکس‌های مهم برای بهبود عملکرد"""
        indexes = [
            # ایندکس برای جدول پذیرش
            "CREATE INDEX IF NOT EXISTS idx_receptions_customer ON Receptions(customer_id)",
            "CREATE INDEX IF NOT EXISTS idx_receptions_status ON Receptions(status)",
            "CREATE INDEX IF NOT EXISTS idx_receptions_date ON Receptions(reception_date)",
            
            # ایندکس برای جدول تعمیرات
            "CREATE INDEX IF NOT EXISTS idx_repairs_reception ON Repairs(reception_id)",
            "CREATE INDEX IF NOT EXISTS idx_repairs_status ON Repairs(status)",
            
            "CREATE INDEX IF NOT EXISTS idx_delete_warehouse_type ON InventoryDeleteTransactions(warehouse_type)",
            "CREATE INDEX IF NOT EXISTS idx_delete_item_id ON InventoryDeleteTransactions(item_id)",
            "CREATE INDEX IF NOT EXISTS idx_delete_date ON InventoryDeleteTransactions(deletion_date)",
            
            "CREATE INDEX IF NOT EXISTS idx_soft_delete_warehouse ON InventorySoftDeletions(warehouse_type)",
            "CREATE INDEX IF NOT EXISTS idx_soft_delete_item ON InventorySoftDeletions(item_id)",
            "CREATE INDEX IF NOT EXISTS idx_soft_delete_date ON InventorySoftDeletions(deletion_date)",
                    


            "CREATE INDEX IF NOT EXISTS idx_repair_services_repair ON Repair_Services(repair_id)",
         
            "CREATE INDEX IF NOT EXISTS idx_repair_services_service ON Repair_Services(service_id)",



            # ایندکس برای جدول اشخاص
            "CREATE INDEX IF NOT EXISTS idx_persons_type ON Persons(person_type)",
            "CREATE INDEX IF NOT EXISTS idx_persons_mobile ON Persons(mobile)",
            
            # ایندکس برای جدول فاکتورها
            "CREATE INDEX IF NOT EXISTS idx_invoices_customer ON Invoices(customer_id)",
            "CREATE INDEX IF NOT EXISTS idx_invoices_date ON Invoices(invoice_date)",
            "CREATE INDEX IF NOT EXISTS idx_invoices_status ON Invoices(payment_status)",
            
            # ایندکس برای جدول تراکنش‌های حسابداری
            "CREATE INDEX IF NOT EXISTS idx_acc_trans_date ON AccountingTransactions(transaction_date)",
            "CREATE INDEX IF NOT EXISTS idx_acc_trans_type ON AccountingTransactions(transaction_type)",
            
            # ایندکس برای جدول چک‌ها
            "CREATE INDEX IF NOT EXISTS idx_checks_status ON Checks(status)",
            "CREATE INDEX IF NOT EXISTS idx_checks_due_date ON Checks(due_date)",
            
            # ایندکس برای جدول پیام‌ها
            "CREATE INDEX IF NOT EXISTS idx_messages_customer ON Messages(customer_id)",
            "CREATE INDEX IF NOT EXISTS idx_messages_date ON Messages(send_date)",
        ]
        
        for index_sql in indexes:
            self.cursor.execute(index_sql)
    
    def get_table_structure(self):
        """دریافت ساختار تمام جداول"""
        try:
            self.connect()
            self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = self.cursor.fetchall()
            
            structure = {}
            for table in tables:
                table_name = table[0]
                self.cursor.execute(f"PRAGMA table_info({table_name})")
                columns = self.cursor.fetchall()
                structure[table_name] = columns
            
            return structure
            
        except Exception as e:
            self.error_occurred.emit(f"خطا در دریافت ساختار جداول: {str(e)}")
            return {}
        finally:
            if self.connection:
                self.connection.close()
    
    def backup_database(self, backup_path=None):
        """پشتیبان‌گیری از دیتابیس"""
        try:
            if backup_path is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_path = f"backup_repair_shop_{timestamp}.db"
            
            # ایجاد کپی از فایل دیتابیس
            import shutil
            shutil.copy2(self.db_name, backup_path)
            return backup_path
            
        except Exception as e:
            self.error_occurred.emit(f"خطا در پشتیبان‌گیری: {str(e)}")
            return None
    
    def restore_database(self, backup_file):
        """بازیابی دیتابیس از فایل پشتیبان"""
        try:
            if not os.path.exists(backup_file):
                return False
            
            # بستن اتصال فعلی
            if self.connection:
                self.connection.close()
            
            # جایگزینی فایل دیتابیس
            import shutil
            shutil.copy2(backup_file, self.db_name)
            
            # اتصال مجدد
            self.connect()
            return True
            
        except Exception as e:
            self.error_occurred.emit(f"خطا در بازیابی: {str(e)}")
            return False


# تابع اصلی برای تست
if __name__ == "__main__":
    db_manager = DatabaseManager()
    
    print("در حال ایجاد دیتابیس و جداول...")
    if db_manager.initialize_database():
        print("✅ دیتابیس با موفقیت ایجاد شد!")
        
        # نمایش ساختار جداول
        structure = db_manager.get_table_structure()
        print(f"\nتعداد جداول ایجاد شده: {len(structure)}")
        
        for table_name, columns in structure.items():
            print(f"\nجدول: {table_name}")
            print("-" * 50)
            for col in columns:
                print(f"  {col[1]} ({col[2]})")
        
        # تست تاریخ شمسی
        print("\n📅 تست تاریخ شمسی:")
        today_jalali = db_manager.get_current_jalali_date()
        print(f"تاریخ امروز شمسی: {today_jalali}")
        
        # تست تبدیل تاریخ
        test_gregorian = "2025-12-25"
        jalali = db_manager.gregorian_to_jalali(test_gregorian)
        print(f"میلادی {test_gregorian} → شمسی {jalali}")
        
    else:
        print("❌ خطا در ایجاد دیتابیس!")