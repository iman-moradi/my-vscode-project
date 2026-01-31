# populate_test_data.py - نسخه اصلاح شده
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import DatabaseManager
from datetime import datetime, timedelta
import random
import sqlite3

def insert_test_data():
    """درج داده‌های آزمایشی برای تمام جداول"""
    print("📊 شروع درج داده‌های آزمایشی...")
    
    # ایجاد اتصال به دیتابیس
    db = DatabaseManager()
    
    try:
        # اتصال به دیتابیس و نگه داشتن آن باز
        db.connect()
        
        # 1. درج تنظیمات
        print("⚙️  در حال درج تنظیمات...")
        try:
            db.cursor.execute('''
            INSERT OR REPLACE INTO Settings (id, app_name, company_name, company_address, company_phone, company_email)
            VALUES (1, 'تعمیرگاه لوازم خانگی امیر', 'تعمیرگاه امیر', 'تهران، خیابان ولیعصر، پلاک 123', '021-12345678', 'info@amir-repair.com')
            ''')
        except sqlite3.Error as e:
            print(f"   ⚠️ خطا در تنظیمات (ممکن است وجود داشته باشد): {e}")
        
        # 2. درج دسته‌بندی‌های دستگاه‌ها
        print("📱 در حال درج دسته‌بندی دستگاه‌ها...")
        device_categories = [
            ('یخچال',),
            ('ماشین لباسشویی',),
            ('تلویزیون',),
            ('مایکروویو',),
            ('کولر',),
            ('پنکه',),
            ('سشوار',),
            ('جاروبرقی',),
            ('مخلوط کن',),
            ('آبمیوه‌گیری',),
            ('قهوه‌ساز',),
            ('سایر',)
        ]
        
        for category in device_categories:
            try:
                db.cursor.execute('''
                INSERT OR IGNORE INTO DeviceCategories_name (name) VALUES (?)
                ''', category)
            except sqlite3.Error as e:
                print(f"   ⚠️ خطا در دسته‌بندی {category[0]}: {e}")
        
        # 3. درج برندها
        print("🏷️  در حال درج برندها...")
        brands = [
            ('ال جی',),
            ('سامسونگ',),
            ('سونی',),
            ('پاناسونیک',),
            ('ایسر',),
            ('اسنوا',),
            ('بوش',),
            ('شارپ',),
            ('کنوود',),
            ('فیلپس',),
            ('جنرال',),
            ('میتگ',),
            ('پارس خزر',),
            ('ایران رادیاتور',)
        ]
        
        for brand in brands:
            try:
                db.cursor.execute('''
                INSERT OR IGNORE INTO Brands (name) VALUES (?)
                ''', brand)
            except sqlite3.Error as e:
                print(f"   ⚠️ خطا در برند {brand[0]}: {e}")
        
        # 4. درج اشخاص (مشتریان، تامین‌کنندگان، تعمیرکاران)
        print("👥 در حال درج اشخاص...")
        persons = [
            ('مشتری', 'امیر', 'محمدی', '09123456789', 'تهران، نارمک', '1234567890'),
            ('مشتری', 'فاطمه', 'احمدی', '09129876543', 'تهران، صادقیه', '9876543210'),
            ('مشتری', 'محمد', 'کریمی', '09137778899', 'کرج، گوهردشت', '4567891230'),
            ('مشتری', 'زهرا', 'رحیمی', '09156667788', 'تهران، پاسداران', '7891234560'),
            ('تامین کننده', 'شرکت پارس الکترونیک', '', '021-22223333', 'تهران، جنت آباد', '1011121314'),
            ('تامین کننده', 'تعاونی لوازم خانگی', '', '021-33334444', 'تهران، ستارخان', '1516171819'),
            ('تعمیرکار بیرونی', 'رضا', 'نظری', '09181112233', 'تهران، شریعتی', '2021222324'),
            ('تعمیرکار بیرونی', 'علی', 'مهدوی', '09194445566', 'تهران، ونک', '2526272829'),
            ('کارمند', 'حسین', 'اکبری', '09197778899', 'تهران، تهرانپارس', '3031323334'),
        ]
        
        for person in persons:
            try:
                db.cursor.execute('''
                INSERT OR IGNORE INTO Persons (person_type, first_name, last_name, mobile, address, national_id)
                VALUES (?, ?, ?, ?, ?, ?)
                ''', person)
            except sqlite3.Error as e:
                print(f"   ⚠️ خطا در شخص {person[1]} {person[2]}: {e}")
        
        # 5. درج دستگاه‌ها
        print("📺 در حال درج دستگاه‌ها...")
        
        # دریافت ID دسته‌بندی‌ها و برندها
        db.cursor.execute("SELECT id, name FROM DeviceCategories_name")
        categories = db.cursor.fetchall()
        
        db.cursor.execute("SELECT id, name FROM Brands")
        brands_list = db.cursor.fetchall()
        
        db.cursor.execute("SELECT id FROM Persons WHERE person_type = 'مشتری'")
        customers = db.cursor.fetchall()
        
        devices = []
        for i in range(10):
            if categories and brands_list and customers:
                category = random.choice(categories)
                brand = random.choice(brands_list)
                customer = random.choice(customers)
                
                device = (
                    category[1],  # device_type (نام دسته‌بندی)
                    brand[1],    # brand (نام برند)
                    f'مدل {i+1}',
                    f'SN-{1000 + i}',
                    2020 + i % 5,
                    f'2023-{random.randint(1,12):02d}-{random.randint(1,28):02d}',
                    1 if i % 3 == 0 else 0,
                    f'2025-{random.randint(1,12):02d}-{random.randint(1,28):02d}' if i % 3 == 0 else None,
                    f'دستگاه تست {i+1}'
                )
                devices.append(device)
        
        for device in devices:
            try:
                db.cursor.execute('''
                INSERT OR IGNORE INTO Devices (device_type, brand, model, serial_number, production_year, 
                                            purchase_date, warranty_status, warranty_end_date, description)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', device)
            except sqlite3.Error as e:
                print(f"   ⚠️ خطا در دستگاه {device[2]}: {e}")
        
        # 6. درج پذیرش‌ها
        print("🏢 در حال درج پذیرش‌ها...")
        
        db.cursor.execute("SELECT id FROM Devices")
        devices_list = db.cursor.fetchall()
        
        employees = ['حسین اکبری', 'رضا محمدی', 'علی کریمی']
        
        for i in range(8):
            if customers and devices_list:
                customer = random.choice(customers)
                device = random.choice(devices_list)
                
                reception_date = f'2024-{random.randint(1,12):02d}-{random.randint(1,28):02d}'
                try:
                    estimated_delivery = (datetime.strptime(reception_date, '%Y-%m-%d') + 
                                         timedelta(days=random.randint(3, 14))).strftime('%Y-%m-%d')
                except:
                    estimated_delivery = reception_date
                
                reception = (
                    f'RCP-{2024}{i+1:04d}',
                    customer[0],
                    device[0],
                    reception_date,
                    f'{random.randint(8, 18):02d}:{random.randint(0, 59):02d}:00',
                    f'مشکل {["تصویر", "صدا", "برق", "آب", "گرمایش", "سرمایش"][i % 6]}',
                    ['خوب', 'متوسط', 'ضعیف'][i % 3],
                    f'{"ریموت، دفترچه" if i % 2 == 0 else "بدون لوازم جانبی"}',
                    random.randint(100000, 500000),
                    estimated_delivery,
                    ['عادی', 'فوری', 'خیلی فوری'][i % 3],
                    ['در انتظار', 'در حال تعمیر', 'تعمیر شده', 'تحویل داده شده'][i % 4],
                    random.choice(employees),
                    f'یادداشت تست برای پذیرش {i+1}'
                )
                
                try:
                    db.cursor.execute('''
                    INSERT OR IGNORE INTO Receptions (reception_number, customer_id, device_id, reception_date, 
                                                    reception_time, problem_description, device_condition, 
                                                    accessories, estimated_cost, estimated_delivery_date, 
                                                    priority, status, reception_employee, notes)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', reception)
                except sqlite3.Error as e:
                    print(f"   ⚠️ خطا در پذیرش {reception[0]}: {e}")
        
        # 7. درج قطعات
        print("🔧 در حال درج قطعات...")
        parts = [
            ('P-001', 'برد اصلی', 'الکترونیکی', 'ال جی', 'MB-123', 'عدد', 5, 50, 'برد اصلی یخچال'),
            ('P-002', 'کمپرسور', 'مکانیکی', 'جنرال', 'COMP-456', 'عدد', 3, 20, 'کمپرسور یخچال'),
            ('P-003', 'پمپ آب', 'مکانیکی', 'سامسونگ', 'PUMP-789', 'عدد', 4, 30, 'پمپ آب لباسشویی'),
            ('P-004', 'لامپ ال ای دی', 'الکترونیکی', 'شارپ', 'LED-012', 'عدد', 20, 200, 'لامپ نمایشگر'),
            ('P-005', 'شیلنگ آب', 'لوازم جانبی', 'پارس', 'HOSE-345', 'متر', 10, 100, 'شیلنگ 1 متری'),
            ('P-006', 'فیلتر آب', 'تصفیه', 'ایسر', 'FIL-678', 'عدد', 15, 100, 'فیلتر تصفیه آب'),
            ('P-007', 'سیم رابط', 'الکترونیکی', 'پاناسونیک', 'CABLE-901', 'عدد', 25, 150, 'سیم برق 3 متری'),
            ('P-008', 'ترموستات', 'الکترونیکی', 'بوش', 'THERM-234', 'عدد', 8, 40, 'ترموستات کنترل دما'),
        ]
        
        for part in parts:
            try:
                db.cursor.execute('''
                INSERT OR IGNORE INTO Parts (part_code, part_name, category, brand, model, unit, min_stock, max_stock, description)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', part)
            except sqlite3.Error as e:
                print(f"   ⚠️ خطا در قطعه {part[1]}: {e}")
        
        # 8. درج اجرت خدمات
        print("💰 در حال درج اجرت خدمات...")
        services = [
            ('S-001', 'تعمیر برد اصلی', 'تعمیرات الکترونیکی', 150000, 2.5, 3, 'تعمیر یا تعویض برد'),
            ('S-002', 'تعویض کمپرسور', 'تعمیرات مکانیکی', 300000, 4.0, 4, 'تعویض کامل کمپرسور'),
            ('S-003', 'تعمیر پمپ آب', 'تعمیرات مکانیکی', 120000, 2.0, 2, 'تعمیر یا تعویض پمپ'),
            ('S-004', 'تعویض لامپ', 'تعمیرات ساده', 50000, 0.5, 1, 'تعویض لامپ نمایشگر'),
            ('S-005', 'نصب شیلنگ', 'نصب و راه‌اندازی', 80000, 1.0, 1, 'نصب شیلنگ جدید'),
            ('S-006', 'تعویض فیلتر', 'تعمیرات ساده', 60000, 0.5, 1, 'تعویض فیلتر آب'),
            ('S-007', 'عیب‌یابی کلی', 'تشخیصی', 100000, 1.5, 2, 'عیب‌یابی کامل دستگاه'),
            ('S-008', 'سرویس دوره‌ای', 'نگهداری', 200000, 3.0, 2, 'سرویس کامل دستگاه'),
        ]
        
        for service in services:
            try:
                db.cursor.execute('''
                INSERT OR IGNORE INTO ServiceFees (service_code, service_name, category, default_fee, estimated_hours, difficulty_level, description)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', service)
            except sqlite3.Error as e:
                print(f"   ⚠️ خطا در خدمت {service[1]}: {e}")
        
        # 9. درج تعمیرات
        print("🔨 در حال درج تعمیرات...")
        db.cursor.execute("SELECT id FROM Receptions WHERE status = 'تعمیر شده'")
        receptions = db.cursor.fetchall()
        
        db.cursor.execute("SELECT id FROM Persons WHERE person_type = 'تعمیرکار بیرونی'")
        technicians = db.cursor.fetchall()
        
        for i, reception in enumerate(receptions[:5] if receptions else []):
            repair = (
                reception[0],
                f'2024-{random.randint(1,12):02d}-{random.randint(1,28):02d}',
                technicians[0][0] if technicians else None,
                'داخلی',
                None,
                0,
                random.randint(50000, 200000),
                random.randint(200000, 800000),
                f'تعمیر کامل دستگاه، تعویض {["برد", "کمپرسور", "پمپ"][i % 3]}',
                f'{"برد، سیم، لامپ" if i % 2 == 0 else "کمپرسور، شیلنگ"}',
                f'2024-{random.randint(1,12):02d} {random.randint(8, 12):02d}:00:00',
                f'2024-{random.randint(1,12):02d} {random.randint(13, 18):02d}:00:00',
                'تمام شده'
            )
            
            try:
                db.cursor.execute('''
                INSERT OR IGNORE INTO Repairs (reception_id, repair_date, technician_id, repair_type, 
                                            outsourced_to, outsourced_cost, labor_cost, total_cost,
                                            repair_description, used_parts, start_time, end_time, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', repair)
            except sqlite3.Error as e:
                print(f"   ⚠️ خطا در تعمیر {repair[0]}: {e}")
        
        # 10. درج انبار قطعات نو
        print("📦 در حال درج انبار قطعات نو...")
        db.cursor.execute("SELECT id FROM Parts")
        parts_list = db.cursor.fetchall()
        
        db.cursor.execute("SELECT id FROM Persons WHERE person_type = 'تامین کننده'")
        suppliers = db.cursor.fetchall()
        
        for i, part in enumerate(parts_list[:6] if parts_list else []):
            new_part = (
                part[0],
                random.randint(10, 100),
                random.randint(50000, 300000),
                random.randint(60000, 350000),
                suppliers[0][0] if suppliers else None,
                f'2024-{random.randint(1,12):02d}-{random.randint(1,28):02d}',
                f'BATCH-{1000 + i}',
                f'قفسه {random.randint(1, 10)}، ردیف {random.randint(1, 5)}',
                f'2026-{random.randint(1,12):02d}-{random.randint(1,28):02d}',
                'موجود'
            )
            
            try:
                db.cursor.execute('''
                INSERT OR IGNORE INTO NewPartsWarehouse (part_id, quantity, purchase_price, sale_price, 
                                                        supplier_id, purchase_date, batch_number, 
                                                        location, expiration_date, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', new_part)
            except sqlite3.Error as e:
                print(f"   ⚠️ خطا در انبار قطعات نو {i}: {e}")
        
        # 11. درج انبار قطعات دست دوم
        print("♻️  در حال درج انبار قطعات دست دوم...")
        for i, part in enumerate(parts_list[3:7] if parts_list and len(parts_list) > 3 else []):
            used_part = (
                part[0],
                random.randint(5, 50),
                random.randint(20000, 150000),
                random.randint(30000, 180000),
                f'دستگاه {["یخچال", "لباسشویی", "تلویزیون"][i % 3]} مدل {1000 + i}',
                'خوب',
                f'2024-{random.randint(1,12):02d}-{random.randint(1,28):02d}',
                random.randint(30, 90),
                f'انبار دست دوم، بخش {random.randint(1, 5)}',
                'موجود'
            )
            
            try:
                db.cursor.execute('''
                INSERT OR IGNORE INTO UsedPartsWarehouse (part_id, quantity, purchase_price, sale_price, 
                                                         source_device, condition, purchase_date, 
                                                         warranty_days, location, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', used_part)
            except sqlite3.Error as e:
                print(f"   ⚠️ خطا در انبار قطعات دست دوم {i}: {e}")
        
        # 12. درج انبار لوازم نو
        print("🆕 در حال درج انبار لوازم نو...")
        db.cursor.execute("SELECT id FROM DeviceCategories_name WHERE name IN ('یخچال', 'ماشین لباسشویی', 'تلویزیون')")
        categories = db.cursor.fetchall()
        
        db.cursor.execute("SELECT id FROM Brands WHERE name IN ('ال جی', 'سامسونگ', 'سونی')")
        brands = db.cursor.fetchall()
        
        for i in range(4):
            if categories and brands and suppliers:
                new_appliance = (
                    categories[i % len(categories)][0],
                    brands[i % len(brands)][0],
                    f'مدل نو {i+1}',
                    f'SN-NEW-{2000 + i}',
                    2023,
                    random.randint(1, 5),
                    random.randint(5000000, 15000000),
                    random.randint(6000000, 18000000),
                    suppliers[0][0] if suppliers else None,
                    f'2024-{random.randint(1,12):02d}-{random.randint(1,28):02d}',
                    random.randint(12, 24),
                    f'انبار اصلی، بخش {i+1}',
                    'موجود',
                    f'لوازم خانگی نو با گارانتی {random.randint(12, 24)} ماهه'
                )
                
                try:
                    db.cursor.execute('''
                    INSERT OR IGNORE INTO NewAppliancesWarehouse (device_type_id, brand_id, model, serial_number, 
                                                                 production_year, quantity, purchase_price, sale_price,
                                                                 supplier_id, purchase_date, warranty_months, 
                                                                 location, status, description)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', new_appliance)
                except sqlite3.Error as e:
                    print(f"   ⚠️ خطا در انبار لوازم نو {i}: {e}")
        
        # 13. درج انبار لوازم دست دوم
        print("🔄 در حال درج انبار لوازم دست دوم...")
        db.cursor.execute("SELECT id FROM Receptions LIMIT 3")
        receptions_for_used = db.cursor.fetchall()
        
        for i in range(3):
            if categories and brands and customers and receptions_for_used:
                used_appliance = (
                    categories[i % len(categories)][0],
                    brands[i % len(brands)][0],
                    f'مدل دست دوم {i+1}',
                    f'SN-USED-{3000 + i}',
                    2020 + i,
                    'مشتری',
                    customers[i][0],
                    receptions_for_used[i][0] if i < len(receptions_for_used) else None,
                    ['در حد نو', 'خیلی خوب', 'خوب'][i],
                    'وضعیت فنی سالم',
                    f'2024-{random.randint(1,12):02d}-{random.randint(1,28):02d}',
                    'تعمیرات جزئی انجام شده',
                    random.randint(2000000, 8000000),
                    f'2024-{random.randint(1,12):02d}-{random.randint(1,28):02d}',
                    f'سند-{4000 + i}',
                    random.randint(3000000, 10000000),
                    'گارانتی فروشگاه',
                    random.randint(30, 180),
                    f'گارانتی {random.randint(3, 6)} ماهه فروشگاه',
                    1,
                    f'انبار دست دوم، بخش {i+1}',
                    'موجود',
                    'ریموت، دفترچه راهنما',
                    f'لوازم دست دوم با کیفیت خوب',
                    '',
                    f'2024-{random.randint(1,12):02d}-{random.randint(1,28):02d}'
                )
                
                try:
                    db.cursor.execute('''
                    INSERT OR IGNORE INTO UsedAppliancesWarehouse (
                        device_type_id, brand_id, model, serial_number, production_year,
                        source_type, source_person_id, original_reception_id,
                        condition, technical_status, last_repair_date, repair_history,
                        purchase_price, purchase_date, purchase_document,
                        sale_price, warranty_type, warranty_days, warranty_description,
                        quantity, location, status, accessories, description, photos_path,
                        entry_date
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', used_appliance)
                except sqlite3.Error as e:
                    print(f"   ⚠️ خطا در انبار لوازم دست دوم {i}: {e}")
        
        # 14. درج حساب‌ها
        print("🏦 در حال درج حساب‌ها...")
        accounts = [
            ('ACC-001', 'صندوق نقدی', 'صندوق', None, 5000000, 5000000, 'حسین اکبری'),
            ('ACC-002', 'حساب جاری ملی', 'بانکی', 'بانک ملی', 20000000, 20000000, 'تعمیرگاه امیر'),
            ('ACC-003', 'حساب پس‌انداز', 'بانکی', 'بانک صادرات', 10000000, 10000000, 'تعمیرگاه امیر'),
            ('ACC-004', 'کارتخوان', 'بانکی', 'بانک ملت', 0, 0, 'تعمیرگاه امیر'),
        ]
        
        for account in accounts:
            try:
                db.cursor.execute('''
                INSERT OR IGNORE INTO Accounts (account_number, account_name, account_type, bank_name, 
                                              initial_balance, current_balance, owner_name)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', account)
            except sqlite3.Error as e:
                print(f"   ⚠️ خطا در حساب {account[1]}: {e}")
        
        # 15. درج فاکتورها
        print("🧾 در حال درج فاکتورها...")
        db.cursor.execute("SELECT id FROM Receptions WHERE status = 'تعمیر شده'")
        repaired_receptions = db.cursor.fetchall()
        
        for i, reception in enumerate(repaired_receptions[:3] if repaired_receptions else []):
            if i < len(customers):
                invoice = (
                    f'INV-{2024}{1000 + i}',
                    'خدمات',
                    customers[i][0],
                    reception[0],
                    f'2024-{random.randint(1,12):02d}-{random.randint(1,28):02d}',
                    f'2024-{random.randint(1,12):02d}-{random.randint(1,28):02d}',
                    random.randint(300000, 1000000),
                    random.randint(0, 50000),
                    random.randint(27000, 90000),
                    random.randint(327000, 1090000),
                    random.randint(327000, 1090000),
                    0,
                    'نقدی',
                    'پرداخت نقدی',
                    f'فاکتور خدمات تعمیر پذیرش {reception[0]}',
                    None,
                    0
                )
                
                try:
                    db.cursor.execute('''
                    INSERT OR IGNORE INTO Invoices (invoice_number, invoice_type, customer_id, reception_id,
                                                   invoice_date, due_date, subtotal, discount, tax, total,
                                                   paid_amount, remaining_amount, payment_status, 
                                                   payment_method, description, outsourced_to, outsourced_cost)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', invoice)
                except sqlite3.Error as e:
                    print(f"   ⚠️ خطا در فاکتور {invoice[0]}: {e}")
        
        # 16. درج کاربران
        print("👤 در حال درج کاربران...")
        db.cursor.execute("SELECT id FROM Persons WHERE person_type = 'کارمند' LIMIT 1")
        employees_db = db.cursor.fetchall()
        
        users = [
            ('admin', 'admin123', employees_db[0][0] if employees_db else None, 'مدیر', 1),
            ('operator', 'operator123', None, 'اپراتور', 1),
            ('accountant', 'accountant123', None, 'حسابدار', 1),
        ]
        
        for user in users:
            try:
                db.cursor.execute('''
                INSERT OR IGNORE INTO Users (username, password, person_id, role, is_active)
                VALUES (?, ?, ?, ?, ?)
                ''', user)
            except sqlite3.Error as e:
                print(f"   ⚠️ خطا در کاربر {user[0]}: {e}")
        
        # 17. درج چک‌ها
        print("💳 در حال درج چک‌ها...")
        db.cursor.execute("SELECT id FROM Invoices")
        invoices_list = db.cursor.fetchall()
        
        for i in range(2):
            if i < len(customers) and i < len(invoices_list if invoices_list else []):
                check = (
                    f'CHK-{1000 + i}',
                    'بانک ملی',
                    'شعبه مرکزی',
                    '1234567890',
                    random.randint(500000, 2000000),
                    f'2024-{random.randint(1,6):02d}-{random.randint(1,28):02d}',
                    f'2024-{random.randint(7,12):02d}-{random.randint(1,28):02d}',
                    'تعمیرگاه امیر',
                    'مشتری',
                    'وصول نشده',
                    'دریافتی',
                    invoices_list[i][0] if invoices_list else None,
                    f'چک دریافتی از مشتری'
                )
                
                try:
                    db.cursor.execute('''
                    INSERT OR IGNORE INTO Checks (check_number, bank_name, branch, account_number, amount,
                                                 issue_date, due_date, drawer, payee, status, check_type,
                                                 related_invoice, description)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', check)
                except sqlite3.Error as e:
                    print(f"   ⚠️ خطا در چک {check[0]}: {e}")
        
        # 18. درج پیام‌ها
        print("📱 در حال درج پیام‌ها...")
        db.cursor.execute("SELECT id FROM Receptions LIMIT 3")
        receptions_for_msg = db.cursor.fetchall()
        
        for i, reception in enumerate(receptions_for_msg[:3] if receptions_for_msg else []):
            if i < len(customers):
                message = (
                    reception[0],
                    customers[i][0],
                    ['ورود دستگاه', 'آماده شدن', 'تحویل'][i],
                    f'دستگاه شما {["پذیرش شد", "آماده تحویل است", "تحویل داده شد"][i]}',
                    f'2024-{random.randint(1,12):02d} {random.randint(9, 17):02d}:00:00',
                    'ارسال شده',
                    'پیام با موفقیت ارسال شد',
                    '09123456789'
                )
                
                try:
                    db.cursor.execute('''
                    INSERT OR IGNORE INTO Messages (reception_id, customer_id, message_type, message_text,
                                                   send_date, send_status, response, mobile_number)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    ''', message)
                except sqlite3.Error as e:
                    print(f"   ⚠️ خطا در پیام {message[2]}: {e}")
        
        # 19. درج شرکا
        print("🤝 در حال درج شرکا...")
        db.cursor.execute("SELECT id FROM Persons WHERE person_type IN ('کارمند', 'تعمیرکار بیرونی') LIMIT 2")
        partners_persons = db.cursor.fetchall()
        
        for i, person in enumerate(partners_persons[:2] if partners_persons else []):
            partner = (
                person[0],
                '2024-01-01',
                '2026-12-31',
                1,
                [50000000, 30000000][i],
                [60, 40][i],
                f'شریک {["اصلی", "فرعی"][i]}'
            )
            
            try:
                db.cursor.execute('''
                INSERT OR IGNORE INTO Partners (person_id, partnership_start, partnership_end, active,
                                               capital, profit_percentage, description)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', partner)
            except sqlite3.Error as e:
                print(f"   ⚠️ خطا در شریک {partner[6]}: {e}")
        
        # 20. ثبت تراکنش‌های اولیه انبار
        print("📈 در حال ثبت تراکنش‌های انبار...")
        db.cursor.execute("SELECT id FROM NewPartsWarehouse LIMIT 3")
        warehouse_items = db.cursor.fetchall()
        
        for i, item in enumerate(warehouse_items[:3] if warehouse_items else []):
            transaction = (
                'خرید',
                'قطعات نو',
                item[0],
                random.randint(10, 50),
                random.randint(50000, 200000),
                random.randint(500000, 10000000),
                f'2024-{random.randint(1,12):02d} {random.randint(9, 16):02d}:00:00',
                f'سند خرید {1000 + i}',
                None,
                f'خرید قطعات نو از تامین کننده',
                'سیستم'
            )
            
            try:
                db.cursor.execute('''
                INSERT OR IGNORE INTO InventoryTransactions (transaction_type, warehouse_type, item_id,
                                                          quantity, unit_price, total_price,
                                                          transaction_date, related_document,
                                                          related_reception, description, employee)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', transaction)
            except sqlite3.Error as e:
                print(f"   ⚠️ خطا در تراکنش انبار {i}: {e}")
        
        # 21. درج LookupValues
        print("🗂️  در حال درج مقادیر ثابت...")
        lookups = [
            ('device_type', 'یخچال', 1),
            ('device_type', 'ماشین لباسشویی', 2),
            ('device_type', 'تلویزیون', 3),
            ('device_type', 'کولر', 4),
            ('device_brand', 'ال جی', 1),
            ('device_brand', 'سامسونگ', 2),
            ('device_brand', 'سونی', 3),
            ('device_brand', 'شارپ', 4),
            ('repair_status', 'در انتظار', 1),
            ('repair_status', 'در حال تعمیر', 2),
            ('repair_status', 'تعمیر شده', 3),
            ('repair_status', 'تحویل داده شده', 4),
        ]
        
        for lookup in lookups:
            try:
                db.cursor.execute('''
                INSERT OR IGNORE INTO LookupValues (category, value, display_order)
                VALUES (?, ?, ?)
                ''', lookup)
            except sqlite3.Error as e:
                print(f"   ⚠️ خطا در lookup {lookup[1]}: {e}")
        
        # تایید تغییرات
        db.connection.commit()
        print("✅ تمام داده‌های آزمایشی با موفقیت درج شدند!")
        
        # نمایش خلاصه
        print("\n📊 خلاصه داده‌های درج شده:")
        tables = [
            'Persons', 'Devices', 'Receptions', 'Parts', 
            'Repairs', 'NewPartsWarehouse', 'UsedPartsWarehouse',
            'NewAppliancesWarehouse', 'UsedAppliancesWarehouse',
            'Invoices', 'Accounts', 'Users', 'Messages'
        ]
        
        for table in tables:
            try:
                db.cursor.execute(f"SELECT COUNT(*) as count FROM {table}")
                result = db.cursor.fetchone()
                print(f"   {table}: {result[0]} رکورد")
            except:
                print(f"   {table}: خطا در شمارش")
        
        return True
        
    except Exception as e:
        print(f"❌ خطا در درج داده‌های آزمایشی: {e}")
        import traceback
        traceback.print_exc()
        if 'db' in locals() and db.connection:
            db.connection.rollback()
        return False
    
    finally:
        if 'db' in locals() and db.connection:
            db.connection.close()

def show_sample_data():
    """نمایش نمونه‌ای از داده‌های درج شده"""
    print("\n🔍 نمایش نمونه داده‌ها:")
    
    db = DatabaseManager()
    db.connect()
    
    try:
        # 1. نمایش چند مشتری
        print("\n👥 مشتریان نمونه:")
        db.cursor.execute("SELECT * FROM Persons WHERE person_type = 'مشتری' LIMIT 3")
        customers = db.cursor.fetchall()
        for cust in customers:
            print(f"   {cust[0]}: {cust[2]} {cust[3]} - {cust[5]}")
        
        # 2. نمایش چند دستگاه
        print("\n📺 دستگاه‌های نمونه:")
        db.cursor.execute("SELECT * FROM Devices LIMIT 3")
        devices = db.cursor.fetchall()
        for dev in devices:
            print(f"   {dev[0]}: {dev[2]} {dev[3]} - سریال: {dev[4]}")
        
        # 3. نمایش پذیرش‌ها
        print("\n🏢 پذیرش‌های نمونه:")
        db.cursor.execute('''
        SELECT r.id, r.reception_number, p.first_name, p.last_name, d.model, r.status 
        FROM Receptions r
        JOIN Persons p ON r.customer_id = p.id
        JOIN Devices d ON r.device_id = d.id
        LIMIT 3
        ''')
        receptions = db.cursor.fetchall()
        for rec in receptions:
            print(f"   {rec[0]}: پذیرش {rec[1]} - {rec[2]} {rec[3]} - {rec[4]} - وضعیت: {rec[5]}")
        
        # 4. نمایش موجودی انبار
        print("\n📦 موجودی انبار قطعات نو:")
        db.cursor.execute('''
        SELECT p.part_name, npw.quantity, npw.purchase_price, npw.sale_price
        FROM NewPartsWarehouse npw
        JOIN Parts p ON npw.part_id = p.id
        WHERE npw.status = 'موجود'
        LIMIT 3
        ''')
        inventory = db.cursor.fetchall()
        for inv in inventory:
            print(f"   {inv[0]}: {inv[1]} عدد - خرید: {inv[2]:,} ریال - فروش: {inv[3]:,} ریال")
        
        # 5. نمایش فاکتورها
        print("\n🧾 فاکتورهای نمونه:")
        db.cursor.execute('''
        SELECT i.invoice_number, p.first_name, p.last_name, i.total, i.payment_status
        FROM Invoices i
        JOIN Persons p ON i.customer_id = p.id
        LIMIT 3
        ''')
        invoices = db.cursor.fetchall()
        for inv in invoices:
            print(f"   {inv[0]}: {inv[1]} {inv[2]} - مبلغ: {inv[3]:,} ریال - وضعیت: {inv[4]}")
            
    finally:
        if db.connection:
            db.connection.close()

def main():
    """تابع اصلی"""
    print("=" * 60)
    print("🛠️  اسکریپت درج داده‌های آزمایشی")
    print("=" * 60)
    
    # درخواست تأیید از کاربر
    response = input("آیا می‌خواهید داده‌های آزمایشی را در دیتابیس درج کنید؟ (y/n): ")
    
    if response.lower() == 'y':
        success = insert_test_data()
        if success:
            show_sample_data()
            print("\n🎉 عملیات با موفقیت انجام شد!")
            print("✅ اکنون می‌توانید با استفاده از نام کاربری 'admin' و رمز عبور 'admin123' وارد سیستم شوید.")
    else:
        print("❌ عملیات لغو شد.")
    
    print("\nبرای خروج Enter بزنید...")
    input()

if __name__ == "__main__":
    main()