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
    
    def gregorian_to_jalali(self, gregorian_date):
        """تبدیل تاریخ میلادی به شمسی (برای نمایش)"""
        if not gregorian_date:
            return ""
        
        try:
            if isinstance(gregorian_date, str):
                # اگر رشته تاریخ میلادی است
                parts = gregorian_date.split('-')
                if len(parts) == 3:
                    year, month, day = map(int, parts)
                    jalali = jdatetime.date.fromgregorian(year=year, month=month, day=day)
                    return jalali.strftime("%Y/%m/%d")
            
            elif isinstance(gregorian_date, date):
                # اگر شیء date است
                jalali = jdatetime.date.fromgregorian(date=gregorian_date)
                return jalali.strftime("%Y/%m/%d")
                
        except Exception as e:
            print(f"خطا در تبدیل تاریخ: {e}")
        
        return str(gregorian_date)
    
    def jalali_to_gregorian(self, jalali_date_str):
        """تبدیل تاریخ شمسی به میلادی (برای ذخیره در دیتابیس)"""
        if not jalali_date_str:
            return None
        
        try:
            # فرض می‌کنیم فرمت تاریخ شمسی yyyy/mm/dd است
            parts = jalali_date_str.split('/')
            if len(parts) == 3:
                year, month, day = map(int, parts)
                jalali = jdatetime.date(year, month, day)
                gregorian = jalali.togregorian()
                return gregorian.strftime("%Y-%m-%d")
        except Exception as e:
            print(f"خطا در تبدیل تاریخ شمسی: {e}")
        
        return jalali_date_str
    
    def get_current_jalali_date(self):
        """دریافت تاریخ شمسی امروز"""
        return jdatetime.datetime.now().strftime("%Y/%m/%d")
    
    def get_current_jalali_datetime(self):
        """دریافت تاریخ و زمان شمسی فعلی"""
        return jdatetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S")
    
    def initialize_database(self):
        """ایجاد جداول دیتابیس"""
        try:
            self.connect()
            
            # ایجاد جدول تنظیمات
            self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS Settings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                app_name TEXT DEFAULT 'سیستم مدیریت تعمیرگاه لوازم خانگی',
                date_format TEXT DEFAULT 'شمسی',
                font_name TEXT DEFAULT 'B Nazanin',
                font_size INTEGER DEFAULT 10,
                bg_color TEXT DEFAULT '#FFFFFF',
                text_color TEXT DEFAULT '#000000',
                logo_path TEXT,
                company_name TEXT,
                company_address TEXT,
                company_phone TEXT,
                company_email TEXT,
                tax_percentage REAL DEFAULT 9,
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
            
            # ایجاد جدول قطعات
            self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS Parts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                part_code TEXT UNIQUE NOT NULL,
                part_name TEXT NOT NULL,
                category TEXT CHECK(category IN ('الکترونیکی', 'مکانیکی', 'برقی', 'الکتریکی', 'ترموستات', 'کمپرسور', 'سایر')),
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
                device_id INTEGER NOT NULL,
                quantity INTEGER DEFAULT 0,
                purchase_price DECIMAL(15, 2) NOT NULL,
                sale_price DECIMAL(15, 2) NOT NULL,
                supplier_id INTEGER NOT NULL,
                purchase_date DATE DEFAULT CURRENT_DATE,
                warranty_months INTEGER DEFAULT 12,
                location TEXT,
                status TEXT CHECK(status IN ('موجود', 'ناموجود', 'رزرو شده', 'فروخته شده')) DEFAULT 'موجود',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (device_id) REFERENCES Devices(id) ON DELETE CASCADE,
                FOREIGN KEY (supplier_id) REFERENCES Persons(id)
            )
            ''')
            
            # ایجاد جدول انبار لوازم خانگی دست دوم
            self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS UsedAppliancesWarehouse (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                device_id INTEGER NOT NULL,
                quantity INTEGER DEFAULT 0,
                purchase_price DECIMAL(15, 2) NOT NULL,
                sale_price DECIMAL(15, 2) NOT NULL,
                source_customer INTEGER,
                condition TEXT CHECK(condition IN ('در حد نو', 'خیلی خوب', 'خوب', 'متوسط', 'نیاز به تعمیر')),
                purchase_date DATE DEFAULT CURRENT_DATE,
                warranty_days INTEGER DEFAULT 90,
                repair_history TEXT,
                location TEXT,
                status TEXT CHECK(status IN ('موجود', 'ناموجود', 'فروخته شده', 'در حال تعمیر')) DEFAULT 'موجود',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (device_id) REFERENCES Devices(id) ON DELETE CASCADE,
                FOREIGN KEY (source_customer) REFERENCES Persons(id)
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
            
            # درج کاربر پیش‌فرض
            self.cursor.execute('''
            INSERT OR IGNORE INTO Users (username, password, role) 
            VALUES ('admin', 'admin123', 'مدیر')
            ''')
            
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