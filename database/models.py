# models.py
from PySide6.QtCore import QObject, Signal, QDate, QDateTime
from datetime import datetime, date
from .database import DatabaseManager
import sqlite3
import json
import jdatetime

try:
    from modules.accounting import AccountManager, TransactionManager
    ACCOUNTING_MODULES_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ خطا در بارگذاری ماژول‌های حسابداری: {e}")
    ACCOUNTING_MODULES_AVAILABLE = False


from modules.accounting.financial_calculator import FinancialCalculator

class BaseModel(QObject):
    data_changed = Signal(str)
    
    def __init__(self, db_manager):
        super().__init__()
        self.db = db_manager
        # تنظیم نام جدول به صورت دستی در کلاس‌های فرزند
    
    def execute_query(self, query, params=()):
        """اجرای کوئری با مدیریت خطا"""
        try:
            return self.db.execute_query(query, params)
        except Exception as e:
            print(f"خطا در اجرای کوئری: {str(e)}")
            print(f"کوئری: {query}")
            return False
    
    def fetch_all(self, query, params=()):
        """دریافت تمام ردیف‌ها"""
        try:
            return self.db.fetch_all(query, params)
        except Exception as e:
            print(f"خطا در fetch_all: {str(e)}")
            print(f"کوئری: {query}")
            return []
    
    def fetch_one(self, query, params=()):
        """دریافت یک ردیف"""
        try:
            return self.db.fetch_one(query, params)
        except Exception as e:
            print(f"خطا در fetch_one: {str(e)}")
            print(f"کوئری: {query}")
            return None
        
        

class Person(BaseModel):
    """مدل مدیریت اشخاص (مشتریان، تامین‌کنندگان، شرکا، ...)"""
    
    def __init__(self, db_manager):
        super().__init__(db_manager)
        self.table_name = "Persons"
    
    def add_person(self, data):
        """افزودن شخص جدید"""
        # بررسی ساختار واقعی جدول
        query = f"""
        INSERT INTO {self.table_name} (
            person_type, first_name, last_name, 
            mobile, phone, address, 
            national_id, economic_code, 
            registration_date, description
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        
        params = (
            data.get('person_type', 'مشتری'),
            data.get('first_name', ''),
            data.get('last_name', ''),
            data.get('mobile', ''),
            data.get('phone', ''),
            data.get('address', ''),
            data.get('national_id', ''),
            data.get('economic_code', ''),
            data.get('registration_date', ''),  # رشته تاریخ
            data.get('description', '')
        )
        
        try:
            return self.execute_query(query, params)
        except Exception as e:
            print(f"خطا در اضافه کردن شخص: {e}")
            return False
    
    def update_person(self, person_id, data):
        """ویرایش اطلاعات شخص"""
        query = f"""
        UPDATE {self.table_name} SET
            person_type = ?,
            first_name = ?,
            last_name = ?,
            mobile = ?,
            phone = ?,
            address = ?,
            national_id = ?,
            economic_code = ?,
            description = ?,
            updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
        """
        
        params = (
            data.get('person_type'),
            data.get('first_name'),
            data.get('last_name'),
            data.get('mobile'),
            data.get('phone'),
            data.get('address'),
            data.get('national_id'),
            data.get('economic_code'),
            data.get('description'),
            person_id
        )
        
        try:
            return self.execute_query(query, params)
        except Exception as e:
            print(f"خطا در ویرایش شخص: {e}")
            return False
    
    def get_person_by_id(self, person_id):
        """دریافت شخص با شناسه"""
        query = f"SELECT * FROM {self.table_name} WHERE id = ?"
        return self.fetch_one(query, (person_id,))
    
    def search_persons(self, keyword):
        """جستجوی اشخاص"""
        query = f"""
        SELECT * FROM {self.table_name} 
        WHERE first_name LIKE ? OR last_name LIKE ? OR mobile LIKE ? OR national_id LIKE ?
        ORDER BY last_name, first_name
        """
        search_term = f"%{keyword}%"
        return self.fetch_all(query, (search_term, search_term, search_term, search_term))

    def get_all_persons(self):
        """دریافت تمام اشخاص"""
        query = f"SELECT * FROM {self.table_name} ORDER BY last_name, first_name"
        return self.fetch_all(query)
    
    def get_by_type(self, person_type):
        """دریافت اشخاص بر اساس نوع"""
        query = f"SELECT * FROM {self.table_name} WHERE person_type = ? ORDER BY last_name, first_name"
        return self.fetch_all(query, (person_type,))

    def get_by_type_with_full_name(self, person_type):
        """دریافت اشخاص بر اساس نوع همراه با نام کامل"""
        query = f"""
        SELECT *, 
               CASE 
                   WHEN first_name IS NOT NULL AND last_name IS NOT NULL THEN first_name || ' ' || last_name
                   WHEN first_name IS NOT NULL THEN first_name
                   WHEN last_name IS NOT NULL THEN last_name
                   WHEN mobile IS NOT NULL THEN 'تامین‌کننده (' || mobile || ')'
                   ELSE 'شخص #' || id
               END as full_name
        FROM {self.table_name} 
        WHERE person_type = ? 
        ORDER BY 
            CASE WHEN first_name IS NOT NULL THEN 0 ELSE 1 END,
            last_name, first_name
        """
        return self.fetch_all(query, (person_type,))
    

    
class Device(BaseModel):
    """مدل مدیریت دستگاه‌ها"""
    
    def __init__(self, db_manager):
        super().__init__(db_manager)
        self.table_name = "Devices"
    
    def add_device(self, data):
        """افزودن دستگاه جدید"""
        query = f"""
        INSERT INTO {self.table_name} (
            device_type, brand, model, serial_number, production_year,
            purchase_date, warranty_status, warranty_end_date, description
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        
        params = (
            data.get('device_type'),
            data.get('brand'),
            data.get('model'),
            data.get('serial_number'),
            data.get('production_year'),
            data.get('purchase_date'),
            data.get('warranty_status', 0),
            data.get('warranty_end_date'),
            data.get('description', '')
        )
        
        if self.execute_query(query, params):
            self.data_changed.emit(self.table_name)
            return True
        return False
    
    def update_device(self, device_id, data):
        """ویرایش دستگاه"""
        query = f"""
        UPDATE {self.table_name} SET
            device_type = ?,
            brand = ?,
            model = ?,
            serial_number = ?,
            production_year = ?,
            purchase_date = ?,
            warranty_status = ?,
            warranty_end_date = ?,
            description = ?,
            updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
        """
        
        params = (
            data.get('device_type'),
            data.get('brand'),
            data.get('model'),
            data.get('serial_number'),
            data.get('production_year'),
            data.get('purchase_date'),
            data.get('warranty_status', 0),
            data.get('warranty_end_date'),
            data.get('description', ''),
            device_id
        )
        
        if self.execute_query(query, params):
            self.data_changed.emit(self.table_name)
            return True
        return False
    
    def get_all_devices(self):
        """دریافت تمام دستگاه‌ها"""
        query = f"SELECT * FROM {self.table_name} ORDER BY brand, model"
        return self.fetch_all(query)
    
    def get_device_by_id(self, device_id):
        """دریافت دستگاه با شناسه"""
        query = f"SELECT * FROM {self.table_name} WHERE id = ?"
        return self.fetch_one(query, (device_id,))
    
    def get_devices_by_type(self, device_type):
        """دریافت دستگاه‌ها بر اساس نوع"""
        query = f"SELECT * FROM {self.table_name} WHERE device_type = ? ORDER BY brand, model"
        return self.fetch_all(query, (device_type,))

class Reception(BaseModel):
    """مدل مدیریت پذیرش دستگاه‌ها"""
    
    def __init__(self, db_manager):
        super().__init__(db_manager)
        self.table_name = "Receptions"
    
    def generate_reception_number(self):
        """تولید شماره پذیرش خودکار"""
        year = QDate.currentDate().year()
        month = QDate.currentDate().month()
        
        # شماره گذاری به صورت: سال-ماه-شماره
        query = f"""
        SELECT COUNT(*) as count FROM {self.table_name} 
        WHERE strftime('%Y', reception_date) = ? AND strftime('%m', reception_date) = ?
        """
        
        result = self.fetch_one(query, (str(year), f"{month:02d}"))
        count = result['count'] + 1 if result else 1
        
        return f"{year}{month:02d}{count:04d}"
    
    def add_reception(self, data):
        """افزودن پذیرش جدید"""
        reception_number = self.generate_reception_number()
        
        query = f"""
        INSERT INTO {self.table_name} (
            reception_number, customer_id, device_id, reception_date, reception_time,
            problem_description, device_condition, accessories, estimated_cost,
            estimated_delivery_date, priority, status, reception_employee, notes
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        
        params = (
            reception_number,
            data.get('customer_id'),
            data.get('device_id'),
            data.get('reception_date', QDate.currentDate().toString('yyyy-MM-dd')),
            QDateTime.currentDateTime().toString('HH:mm:ss'),
            data.get('problem_description'),
            data.get('device_condition', ''),
            data.get('accessories', ''),
            data.get('estimated_cost', 0),
            data.get('estimated_delivery_date'),
            data.get('priority', 'عادی'),
            data.get('status', 'در انتظار'),
            data.get('reception_employee', ''),
            data.get('notes', '')
        )
        
        if self.execute_query(query, params):
            self.data_changed.emit(self.table_name)
            return reception_number
        return None
    
    def update_status(self, reception_id, status):
        """بروزرسانی وضعیت پذیرش"""
        query = f"""
        UPDATE {self.table_name} 
        SET status = ?, updated_at = CURRENT_TIMESTAMP 
        WHERE id = ?
        """
        
        if self.execute_query(query, (status, reception_id)):
            self.data_changed.emit(self.table_name)
            return True
        return False
    
    def get_all_receptions(self, status=None):
        """دریافت تمام پذیرش‌ها (با فیلتر وضعیت)"""
        if status:
            query = f"""
            SELECT r.*, p.first_name || ' ' || p.last_name as customer_name, 
                   d.device_type, d.brand, d.model
            FROM {self.table_name} r
            JOIN Persons p ON r.customer_id = p.id
            JOIN Devices d ON r.device_id = d.id
            WHERE r.status = ?
            ORDER BY r.reception_date DESC, r.reception_time DESC
            """
            return self.fetch_all(query, (status,))
        else:
            query = f"""
            SELECT r.*, p.first_name || ' ' || p.last_name as customer_name, 
                   d.device_type, d.brand, d.model
            FROM {self.table_name} r
            JOIN Persons p ON r.customer_id = p.id
            JOIN Devices d ON r.device_id = d.id
            ORDER BY r.reception_date DESC, r.reception_time DESC
            """
            return self.fetch_all(query)
    
    def get_reception_by_id(self, reception_id):
        """دریافت پذیرش با شناسه"""
        query = f"""
        SELECT r.*, p.first_name || ' ' || p.last_name as customer_name,
               p.mobile, p.phone, p.address,
               d.device_type, d.brand, d.model, d.serial_number
        FROM {self.table_name} r
        JOIN Persons p ON r.customer_id = p.id
        JOIN Devices d ON r.device_id = d.id
        WHERE r.id = ?
        """
        return self.fetch_one(query, (reception_id,))

class Repair(BaseModel):
    """مدل مدیریت تعمیرات"""
    def __init__(self, db_manager):
        super().__init__(db_manager)
        self.table_name = "Repairs"
    
    def add_repair(self, data):
        """افزودن تعمیر جدید - نسخه اصلاح شده"""
        print(f"🛠️ در حال افزودن تعمیر جدید...")
        print(f"   داده‌های ورودی: {data.keys()}")
        
        query = f"""
        INSERT INTO {self.table_name} (
            reception_id, repair_date, technician_id, repair_type,
            outsourced_to, outsourced_cost, labor_cost, total_cost,
            repair_description, used_parts, start_time, end_time, status
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        
        params = (
            data.get('reception_id'),
            data.get('repair_date'),
            data.get('technician_id'),
            data.get('repair_type', 'داخلی'),
            data.get('outsourced_to'),
            data.get('outsourced_cost', 0),
            data.get('labor_cost', 0),
            data.get('total_cost', 0),
            data.get('repair_description', ''),
            data.get('used_parts'),
            data.get('start_time'),
            data.get('end_time'),
            data.get('status', 'شروع شده')
        )
        
        print(f"   پارامترها: {params}")
        
        try:
            self.db.connect()
            self.db.cursor.execute(query, params)
            self.db.connection.commit()
            
            # دریافت شناسه رکورد درج شده
            repair_id = self.db.cursor.lastrowid
            print(f"   ✅ تعمیر با موفقیت ثبت شد. ID: {repair_id}")
            
            if repair_id:
                self.data_changed.emit(self.table_name)
                return repair_id
            else:
                print("   ⚠️ هیچ شناسه‌ای بازگردانده نشد!")
                return False
                
        except Exception as e:
            print(f"❌ خطا در افزودن تعمیر: {e}")
            import traceback
            traceback.print_exc()
            return False
        finally:
            if self.db.connection:
                self.db.connection.close()
    
    def update_repair(self, repair_id, data):
        """ویرایش تعمیر - نسخه اصلاح شده"""
        print(f"✏️ در حال ویرایش تعمیر ID: {repair_id}")
        
        query = f"""
        UPDATE {self.table_name} SET
            reception_id = ?,
            repair_date = ?,
            technician_id = ?,
            repair_type = ?,
            outsourced_to = ?,
            outsourced_cost = ?,
            labor_cost = ?,
            total_cost = ?,
            repair_description = ?,
            used_parts = ?,
            start_time = ?,
            end_time = ?,
            status = ?
        WHERE id = ?
        """
        
        params = (
            data.get('reception_id'),
            data.get('repair_date'),
            data.get('technician_id'),
            data.get('repair_type'),
            data.get('outsourced_to'),
            data.get('outsourced_cost', 0),
            data.get('labor_cost', 0),
            data.get('total_cost', 0),
            data.get('repair_description', ''),
            data.get('used_parts'),
            data.get('start_time'),
            data.get('end_time'),
            data.get('status'),
            repair_id
        )
        
        print(f"   پارامترها: {params}")
        
        success = self.execute_query(query, params)
        print(f"   ✅ نتیجه ویرایش: {success}")
        
        return success

    # در کلاس Repair در models.py

    def add_repair_service(self, repair_id, service_id, quantity, unit_price, description=""):
        """افزودن خدمت به تعمیر (جدول واسط)"""
        total_price = quantity * unit_price
        query = """
        INSERT INTO Repair_Services (repair_id, service_id, quantity, unit_price, total_price, description)
        VALUES (?, ?, ?, ?, ?, ?)
        """
        params = (repair_id, service_id, quantity, unit_price, total_price, description)
        return self.execute_query(query, params)
    
    def delete_repair_services(self, repair_id):
        """حذف تمام خدمات یک تعمیر"""
        query = "DELETE FROM Repair_Services WHERE repair_id = ?"
        return self.execute_query(query, (repair_id,))
    
    def update_repair_service(self, repair_service_id, data):
        """ویرایش یک خدمت در تعمیر"""
        query = """
        UPDATE Repair_Services SET
            quantity = ?,
            unit_price = ?,
            total_price = ?,
            description = ?
        WHERE id = ?
        """
        quantity = data.get('quantity', 1)
        unit_price = data.get('unit_price', 0)
        total_price = quantity * unit_price
        params = (quantity, unit_price, total_price, data.get('description', ''), repair_service_id)
        return self.execute_query(query, params)
    
    def get_repair_summary(self, repair_id):
        """دریافت خلاصه هزینه‌های یک تعمیر"""
        query = """
        SELECT 
            r.total_cost,
            COALESCE(SUM(rs.total_price), 0) as services_cost,
            r.outsourced_cost,
            r.labor_cost
        FROM Repairs r
        LEFT JOIN Repair_Services rs ON r.id = rs.repair_id
        WHERE r.id = ?
        GROUP BY r.id
        """
        return self.fetch_one(query, (repair_id,))

    def repair_exists_for_reception(self, reception_id):
        """بررسی وجود تعمیر برای پذیرش"""
        query = f"SELECT COUNT(*) as count FROM {self.table_name} WHERE reception_id = ?"
        result = self.fetch_one(query, (reception_id,))
        return result['count'] > 0 if result else False

    def get_repair_by_reception_id(self, reception_id):
        """دریافت تعمیر بر اساس reception_id"""
        query = f"SELECT * FROM {self.table_name} WHERE reception_id = ? ORDER BY id DESC LIMIT 1"
        return self.fetch_one(query, (reception_id,))
    
    def get_repair_services(self, repair_id):
        """دریافت خدمات یک تعمیر"""
        query = """
        SELECT rs.*, sf.service_name, sf.category
        FROM Repair_Services rs
        JOIN ServiceFees sf ON rs.service_id = sf.id
        WHERE rs.repair_id = ?
        ORDER BY rs.id
        """
        return self.fetch_all(query, (repair_id,))

    def add_repair_part(self, repair_id, part_id, quantity, unit_price, warehouse_type, description=""):
        """افزودن قطعه به تعمیر"""
        total_price = quantity * unit_price
        query = """
        INSERT INTO Repair_Parts (repair_id, part_id, quantity, unit_price, total_price, warehouse_type, description)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        params = (repair_id, part_id, quantity, unit_price, total_price, warehouse_type, description)
        try:
            self.execute_query(query, params)
            return True
        except Exception as e:
            print(f"خطا در افزودن قطعه به تعمیر: {e}")
            return False
    
    def delete_repair_parts(self, repair_id):
        """حذف تمام قطعات یک تعمیر"""
        query = "DELETE FROM Repair_Parts WHERE repair_id = ?"
        return self.execute_query(query, (repair_id,))
    
    def get_repair_parts(self, repair_id):
        """دریافت قطعات یک تعمیر"""
        query = """
        SELECT 
            rp.id,
            rp.repair_id,
            rp.part_id,
            rp.quantity,
            rp.unit_price,
            rp.total_price,
            rp.warehouse_type,
            rp.description,
            p.part_code,
            p.part_name,
            p.brand,
            p.category
        FROM Repair_Parts rp
        LEFT JOIN Parts p ON rp.part_id = p.id
        WHERE rp.repair_id = ?
        ORDER BY rp.id
        """
        return self.fetch_all(query, (repair_id,))
    
    def repair_part_exists(self, repair_id, part_id):
        """بررسی وجود قطعه در تعمیر"""
        query = "SELECT COUNT(*) as count FROM Repair_Parts WHERE repair_id = ? AND part_id = ?"
        result = self.fetch_one(query, (repair_id, part_id))
        return result['count'] > 0 if result else False


class Part(BaseModel):
    """مدل مدیریت قطعات"""
    
    def __init__(self, db_manager):
        super().__init__(db_manager)
        self.table_name = "Parts"
    
    def add_part(self, data):
        """افزودن قطعه جدید"""
        query = f"""
        INSERT INTO {self.table_name} (
            part_code, part_name, category, brand, model, unit, min_stock, max_stock, description
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        
        params = (
            data.get('part_code'),
            data.get('part_name'),
            data.get('category', 'سایر'),
            data.get('brand', ''),
            data.get('model', ''),
            data.get('unit', 'عدد'),
            data.get('min_stock', 5),
            data.get('max_stock', 100),
            data.get('description', '')
        )
        
        if self.execute_query(query, params):
            self.data_changed.emit(self.table_name)
            return True
        return False
    
    def get_all_parts(self):
        """دریافت تمام قطعات"""
        query = f"SELECT * FROM {self.table_name} ORDER BY part_name"
        return self.fetch_all(query)
    
    def get_part_by_code(self, part_code):
        """دریافت قطعه با کد"""
        query = f"SELECT * FROM {self.table_name} WHERE part_code = ?"
        return self.fetch_one(query, (part_code,))
    
    def get_low_stock_parts(self):
        """دریافت قطعات با موجودی کم - نسخه اصلاح شده"""
        query = """
        SELECT 
            p.id,
            p.part_code,
            p.part_name,
            p.category,
            p.brand,
            p.model,
            p.unit,
            p.min_stock,
            p.max_stock,
            p.description,
            COALESCE(new_stock.new_quantity, 0) as new_quantity,
            COALESCE(used_stock.used_quantity, 0) as used_quantity,
            (COALESCE(new_stock.new_quantity, 0) + COALESCE(used_stock.used_quantity, 0)) as total_quantity
        FROM Parts p
        LEFT JOIN (
            SELECT 
                part_id, 
                SUM(quantity) as new_quantity
            FROM NewPartsWarehouse 
            WHERE status = 'موجود' 
            GROUP BY part_id
        ) new_stock ON p.id = new_stock.part_id
        LEFT JOIN (
            SELECT 
                part_id, 
                SUM(quantity) as used_quantity
            FROM UsedPartsWarehouse 
            WHERE status = 'موجود' 
            GROUP BY part_id
        ) used_stock ON p.id = used_stock.part_id
        WHERE 
            (COALESCE(new_stock.new_quantity, 0) + COALESCE(used_stock.used_quantity, 0)) < p.min_stock
            OR (new_stock.new_quantity IS NULL AND used_stock.used_quantity IS NULL)
        ORDER BY p.part_name
        """
        return self.fetch_all(query)
    
    def get_part_stock(self, part_id):
        """دریافت موجودی یک قطعه خاص"""
        query_new = """
        SELECT COALESCE(SUM(quantity), 0) as total 
        FROM NewPartsWarehouse 
        WHERE part_id = ? AND status = 'موجود'
        """
        
        query_used = """
        SELECT COALESCE(SUM(quantity), 0) as total
        FROM UsedPartsWarehouse 
        WHERE part_id = ? AND status = 'موجود'
        """
        
        try:
            new_stock = self.fetch_one(query_new, (part_id,))
            used_stock = self.fetch_one(query_used, (part_id,))
            
            total_new = new_stock['total'] if new_stock else 0
            total_used = used_stock['total'] if used_stock else 0
            
            return {
                'new_parts': total_new,
                'used_parts': total_used,
                'total': total_new + total_used
            }
        except Exception as e:
            print(f"خطا در دریافت موجودی قطعه {part_id}: {e}")
            return {'new_parts': 0, 'used_parts': 0, 'total': 0}
        
# models.py - کلاس WarehouseManager کامل و اصلاح شده

from PySide6.QtCore import QDateTime

class WarehouseManager(BaseModel):
    """مدل مدیریت انبارهای مختلف - نسخه کامل و اصلاح شده"""
    
    def __init__(self, db_manager):
        super().__init__(db_manager)
        self.ensure_inventory_tables_exist()

    def ensure_inventory_tables_exist(self):
        """بررسی و ایجاد جداول مربوط به تراکنش‌های حذف در صورت عدم وجود"""
        try:
            # بررسی وجود جدول InventoryDeleteTransactions
            check_query = "SELECT name FROM sqlite_master WHERE type='table' AND name='InventoryDeleteTransactions'"
            result = self.fetch_one(check_query)
            
            if not result:
                print("🔧 جدول InventoryDeleteTransactions وجود ندارد. در حال ایجاد...")
                create_query = '''
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
                '''
                if self.execute_query(create_query):
                    print("✅ جدول InventoryDeleteTransactions ایجاد شد.")
            
            # بررسی وجود جدول InventorySoftDeletions
            check_query = "SELECT name FROM sqlite_master WHERE type='table' AND name='InventorySoftDeletions'"
            result = self.fetch_one(check_query)
            
            if not result:
                print("🔧 جدول InventorySoftDeletions وجود ندارد. در حال ایجاد...")
                create_query = '''
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
                '''
                if self.execute_query(create_query):
                    print("✅ جدول InventorySoftDeletions ایجاد شد.")
                    
        except Exception as e:
            print(f"⚠️ خطا در بررسی/ایجاد جداول حذف: {e}")

    def add_to_warehouse(self, warehouse_type, data):
        """افزودن به انبار (نو یا دست دوم) - نسخه به‌روز شده"""
        table_map = {
            'قطعات نو': 'NewPartsWarehouse',
            'قطعات دست دوم': 'UsedPartsWarehouse',
            'لوازم نو': 'NewAppliancesWarehouse',
            'لوازم دست دوم': 'UsedAppliancesWarehouse'
        }
        
        table_name = table_map.get(warehouse_type)
        if not table_name:
            return False
        
        try:
            if warehouse_type == 'لوازم نو':
                # ساختار جدید لوازم نو
                query = f"""
                INSERT INTO {table_name} (
                    device_type_id, brand_id, model, serial_number, production_year,
                    quantity, purchase_price, sale_price, supplier_id,
                    purchase_date, warranty_months, location, status, description
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """
                
                params = (
                    data.get('device_type_id'),
                    data.get('brand_id'),
                    data.get('model', ''),
                    data.get('serial_number', ''),
                    data.get('production_year'),
                    data.get('quantity', 1),
                    data.get('purchase_price', 0),
                    data.get('sale_price', 0),
                    data.get('supplier_id'),
                    data.get('purchase_date'),
                    data.get('warranty_months', 12),
                    data.get('location', ''),
                    data.get('status', 'موجود'),
                    data.get('description', '')
                )
                
            elif warehouse_type == 'لوازم دست دوم':
                # استفاده از تابع مخصوص برای لوازم دست دوم
                if data.get('source_type') == 'تامین کننده':
                    return self.add_used_appliance_from_supplier(data)
                else:
                    return self.add_used_appliance_from_customer(data)
                
            elif warehouse_type == 'قطعات نو':
                query = f"""
                INSERT INTO {table_name} (
                    part_id, quantity, purchase_price, sale_price, supplier_id,
                    purchase_date, batch_number, location, expiration_date, status
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """
                
                params = (
                    data.get('part_id'),
                    data.get('quantity', 0),
                    data.get('purchase_price', 0),
                    data.get('sale_price', 0),
                    data.get('supplier_id'),
                    data.get('purchase_date'),
                    data.get('batch_number', ''),
                    data.get('location', ''),
                    data.get('expiration_date'),
                    data.get('status', 'موجود')
                )
                
            elif warehouse_type == 'قطعات دست دوم':
                query = f"""
                INSERT INTO {table_name} (
                    part_id, quantity, purchase_price, sale_price, source_device,
                    condition, purchase_date, warranty_days, location, status
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """
                
                params = (
                    data.get('part_id'),
                    data.get('quantity', 0),
                    data.get('purchase_price', 0),
                    data.get('sale_price', 0),
                    data.get('source_device', ''),
                    data.get('condition', 'خوب'),
                    data.get('purchase_date'),
                    data.get('warranty_days', 30),
                    data.get('location', ''),
                    data.get('status', 'موجود')
                )
            
            # اجرای کوئری (فقط برای انواعی که در این تابع پیاده‌سازی شده‌اند)
            if warehouse_type != 'لوازم دست دوم':  # لوازم دست دوم با توابع جداگانه مدیریت می‌شود
                if self.execute_query(query, params):
                    self.data_changed.emit(table_name)
                    # ثبت تراکنش انبار
                    self._add_inventory_transaction(warehouse_type, 'خرید', data)
                    return True
                return False
            else:
                return True  # لوازم دست دوم قبلاً در توابع جداگانه ثبت شده
                
        except Exception as e:
            print(f"خطا در ذخیره‌سازی در انبار {warehouse_type}: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def _add_inventory_transaction(self, warehouse_type, transaction_type, data):
        """ثبت تراکنش انبار - ساده شده"""
        try:
            # بررسی وجود item_id
            item_id = data.get('id') or data.get('item_id')
            
            if not item_id:
                print(f"⚠️ تراکنش {transaction_type} بدون item_id - ثبت نمی‌شود")
                return False
            
            # تاریخ و زمان فعلی به میلادی
            from PySide6.QtCore import QDateTime
            transaction_date = QDateTime.currentDateTime().toString("yyyy-MM-dd HH:mm:ss")
            
            # محاسبه قیمت
            quantity = data.get('quantity', 1)
            unit_price = data.get('purchase_price', 0) or data.get('unit_price', 0)
            total_price = quantity * unit_price
            
            query = """
            INSERT INTO InventoryTransactions (
                transaction_type, warehouse_type, item_id, quantity, unit_price,
                total_price, transaction_date, related_document, description, employee
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            
            params = (
                transaction_type,
                warehouse_type,
                item_id,
                quantity,
                unit_price,
                total_price,
                transaction_date,  # تاریخ میلادی
                data.get('purchase_document', '') or data.get('batch_number', ''),
                f"{transaction_type} {warehouse_type} - {data.get('model', '')}",
                data.get('employee', 'سیستم')
            )
            
            print(f"📝 ثبت تراکنش: {transaction_type} برای آیتم {item_id}")
            return self.execute_query(query, params)
            
        except Exception as e:
            print(f"❌ خطا در ثبت تراکنش: {e}")
            return False
    
    def get_warehouse_stock(self, warehouse_type, item_id=None, show_all=False):
        """دریافت موجودی انبار - نسخه کامل"""
        table_map = {
            'قطعات نو': 'NewPartsWarehouse',
            'قطعات دست دوم': 'UsedPartsWarehouse',
            'لوازم نو': 'NewAppliancesWarehouse',
            'لوازم دست دوم': 'UsedAppliancesWarehouse'
        }
        
        table_name = table_map.get(warehouse_type)
        if not table_name:
            return []
        
        if warehouse_type == 'لوازم نو':
            return self.get_new_appliances_stock(item_id, show_all)
        elif warehouse_type == 'لوازم دست دوم':
            return self.get_used_appliances_stock(item_id, show_all)
        elif warehouse_type == 'قطعات نو':
            return self.get_new_parts_stock(item_id, show_all)
        elif warehouse_type == 'قطعات دست دوم':
            return self.get_used_parts_stock(item_id, show_all)
        
        return []
    
    def get_new_appliances_stock(self, item_id=None, show_all=False):
        """دریافت موجودی لوازم نو"""
        if item_id:
            query = """
            SELECT 
                naw.*,
                dc.name as device_type_name,
                b.name as brand_name,
                p.full_name as supplier_name
            FROM NewAppliancesWarehouse naw
            LEFT JOIN DeviceCategories_name dc ON naw.device_type_id = dc.id
            LEFT JOIN Brands b ON naw.brand_id = b.id
            LEFT JOIN Persons p ON naw.supplier_id = p.id
            WHERE naw.id = ?
            """
            params = (item_id,)
        else:
            query = """
            SELECT 
                naw.*,
                dc.name as device_type_name,
                b.name as brand_name,
                p.full_name as supplier_name
            FROM NewAppliancesWarehouse naw
            LEFT JOIN DeviceCategories_name dc ON naw.device_type_id = dc.id
            LEFT JOIN Brands b ON naw.brand_id = b.id
            LEFT JOIN Persons p ON naw.supplier_id = p.id
            """
            
            if not show_all:
                query += " WHERE naw.status = 'موجود'"
            
            query += " ORDER BY naw.purchase_date DESC"
            params = ()
        
        return self.fetch_all(query, params)
    
    def get_used_appliances_stock(self, item_id=None, show_all=False):
        """دریافت موجودی لوازم دست دوم"""
        if item_id:
            query = """
            SELECT 
                uaw.*,
                dc.name as device_type_name,
                b.name as brand_name,
                p.full_name as source_name,
                r.reception_number
            FROM UsedAppliancesWarehouse uaw
            LEFT JOIN DeviceCategories_name dc ON uaw.device_type_id = dc.id
            LEFT JOIN Brands b ON uaw.brand_id = b.id
            LEFT JOIN Persons p ON uaw.source_person_id = p.id
            LEFT JOIN Receptions r ON uaw.original_reception_id = r.id
            WHERE uaw.id = ?
            """
            params = (item_id,)
        else:
            query = """
            SELECT 
                uaw.*,
                dc.name as device_type_name,
                b.name as brand_name,
                p.full_name as source_name,
                r.reception_number,
                CASE 
                    WHEN uaw.source_type = 'مشتری' THEN 'خرید از مشتری'
                    WHEN uaw.source_type = 'تامین کننده' THEN 'خرید از تامین‌کننده'
                    WHEN uaw.source_type = 'تعویض شده' THEN 'تعویض شده'
                    ELSE uaw.source_type
                END as source_type_fa
            FROM UsedAppliancesWarehouse uaw
            LEFT JOIN DeviceCategories_name dc ON uaw.device_type_id = dc.id
            LEFT JOIN Brands b ON uaw.brand_id = b.id
            LEFT JOIN Persons p ON uaw.source_person_id = p.id
            LEFT JOIN Receptions r ON uaw.original_reception_id = r.id
            """
            
            if not show_all:
                query += " WHERE uaw.status = 'موجود'"
            
            query += " ORDER BY uaw.entry_date DESC"
            params = ()
        
        return self.fetch_all(query, params)

    def get_new_parts_stock(self, item_id=None, show_all=False):
        """دریافت موجودی قطعات نو - نسخه اصلاح شده"""
        if item_id:
            query = """
            SELECT 
                npw.*,
                p.part_code,
                p.part_name,
                p.category,
                p.brand,  # 🔴 اضافه شد - برند از جدول Parts
                p.unit,
                per.full_name as supplier_name
            FROM NewPartsWarehouse npw
            LEFT JOIN Parts p ON npw.part_id = p.id
            LEFT JOIN Persons per ON npw.supplier_id = per.id
            WHERE npw.id = ?
            """
            params = (item_id,)
        else:
            query = """
            SELECT 
                npw.*,
                p.part_code,
                p.part_name,
                p.category,
                p.brand,  # 🔴 اضافه شد - برند از جدول Parts
                p.unit,
                per.full_name as supplier_name
            FROM NewPartsWarehouse npw
            LEFT JOIN Parts p ON npw.part_id = p.id
            LEFT JOIN Persons per ON npw.supplier_id = per.id
            """
            
            if not show_all:
                query += " WHERE npw.status = 'موجود'"
            
            query += " ORDER BY npw.purchase_date DESC"
            params = ()
        
        return self.fetch_all(query, params)    
   
    def get_used_parts_stock(self, item_id=None, show_all=False):
        """دریافت موجودی قطعات دست دوم - نسخه اصلاح شده"""
        if item_id:
            query = """
            SELECT 
                upw.*,
                p.part_code,
                p.part_name,
                p.category,
                p.brand,  # 🔴 اضافه شد
                p.unit
            FROM UsedPartsWarehouse upw
            LEFT JOIN Parts p ON upw.part_id = p.id
            WHERE upw.id = ?
            """
            params = (item_id,)
        else:
            query = """
            SELECT 
                upw.*,
                p.part_code,
                p.part_name,
                p.category,
                p.brand,  # 🔴 اضافه شد
                p.unit
            FROM UsedPartsWarehouse upw
            LEFT JOIN Parts p ON upw.part_id = p.id
            """
            
            if not show_all:
                query += " WHERE upw.status = 'موجود'"
            
            query += " ORDER BY upw.purchase_date DESC"
            params = ()
        
        print(f"🔍 اجرای کوئری get_used_parts_stock")  # 🔴 دیباگ
        results = self.fetch_all(query, params)
        
        # 🔴 چاپ نمونه‌ای از نتایج برای دیباگ
        if results and len(results) > 0:
            print(f"🔍 تعداد نتایج: {len(results)}")
            print(f"🔍 ساختار اولین آیتم: {results[0].keys()}")
            print(f"🔍 اولین آیتم - برند: {results[0].get('brand')}")
        
        return results  

    def add_used_appliance_from_customer(self, data):
        """افزودن لوازم دست دوم از مشتری - نسخه کاملاً اصلاح شده"""
        try:
            print(f"🔄 شروع افزودن لوازم دست دوم از مشتری...")
            
            # تولید شماره سریال خودکار اگر خالی است
            serial_number = data.get('serial_number', '').strip()
            if not serial_number:
                import time
                import random
                timestamp = int(time.time() * 1000)
                random_part = random.randint(1000, 9999)
                serial_number = f"CUST-{timestamp}-{random_part}"
                print(f"   📝 شماره سریال خودکار تولید شد: {serial_number}")
            
            # تهیه پارامترهای کوئری
            query = """
            INSERT INTO UsedAppliancesWarehouse (
                device_type_id, brand_id, model, serial_number, production_year,
                source_type, source_person_id, original_reception_id,
                condition, technical_status, last_repair_date, repair_history,
                purchase_price, purchase_date, purchase_document,
                sale_price, warranty_type, warranty_days, warranty_description,
                quantity, location, status, accessories, description, photos_path,
                entry_date
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            
            # تنظیم پارامترها
            params = (
                data.get('device_type_id'),
                data.get('brand_id'),
                data.get('model', 'بدون مدل'),
                serial_number,
                data.get('production_year', 1400),
                'مشتری',  # source_type
                data.get('customer_id') or data.get('source_person_id'),
                data.get('reception_id'),  # original_reception_id
                data.get('condition', 'خوب'),
                data.get('technical_status', ''),
                data.get('last_repair_date'),
                data.get('repair_history', ''),
                float(data.get('purchase_price', 0)),
                data.get('purchase_date'),
                data.get('purchase_document', ''),
                float(data.get('sale_price', 0)),
                data.get('warranty_type', 'گارانتی فروشگاه'),
                data.get('warranty_days', 90),
                data.get('warranty_description', ''),
                data.get('quantity', 1),
                data.get('location', 'انبار عمومی'),
                data.get('status', 'موجود'),
                data.get('accessories', ''),
                data.get('description', ''),
                data.get('photos_path', ''),
                data.get('entry_date')
            )
            
            print(f"   🔧 پارامترهای کوئری آماده شدند")
            print(f"   📊 مدل: {params[2]}")
            print(f"   💰 قیمت خرید: {params[12]:,}")
            
            # 🔴 **استفاده از self.db.execute_query برای اجرای کوئری اصلی**
            # ابتدا دستگاه را ثبت می‌کنیم
            success = self.db.execute_query(query, params)
            
            if not success:
                print(f"   ❌ خطا در اجرای کوئری اصلی")
                return (False, None)
            
            # 🔴 **دریافت ID دستگاه اضافه شده**
            # برای این کار باید آخرین رکورد را پیدا کنیم
            get_id_query = """
            SELECT id FROM UsedAppliancesWarehouse 
            WHERE serial_number = ? 
            ORDER BY id DESC LIMIT 1
            """
            
            result = self.db.fetch_one(get_id_query, (serial_number,))
            
            if result and 'id' in result:
                item_id = result['id']
                print(f"   🎯 دستگاه با شناسه {item_id} در دیتابیس ثبت شد")
                
                # 🔴 **ثبت تراکنش انبار**
                try:
                    print(f"   📝 در حال ثبت تراکنش انبار...")
                    
                    transaction_query = """
                    INSERT INTO InventoryTransactions (
                        transaction_type, warehouse_type, item_id, quantity, unit_price,
                        total_price, transaction_date, related_document, description, employee
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """
                    
                    # تاریخ و زمان فعلی
                    from PySide6.QtCore import QDateTime
                    transaction_date = QDateTime.currentDateTime().toString("yyyy-MM-dd HH:mm:ss")
                    
                    # محاسبه قیمت کل
                    quantity = data.get('quantity', 1)
                    purchase_price = float(data.get('purchase_price', 0))
                    total_price = quantity * purchase_price
                    
                    transaction_params = (
                        'خرید',
                        'لوازم دست دوم',
                        item_id,
                        quantity,
                        purchase_price,
                        total_price,
                        transaction_date,
                        data.get('purchase_document', '') or data.get('document_number', '') or 'بدون شماره سند',
                        f"خرید لوازم دست دوم - {data.get('model', 'دستگاه')} از مشتری",
                        data.get('employee', 'سیستم')
                    )
                    
                    # اجرای کوئری تراکنش
                    transaction_success = self.db.execute_query(transaction_query, transaction_params)
                    
                    if transaction_success:
                        print(f"   ✅ تراکنش انبار برای دستگاه #{item_id} ثبت شد")
                    else:
                        print(f"   ⚠️ خطا در ثبت تراکنش انبار (اما دستگاه ذخیره شد)")
                    
                except Exception as trans_error:
                    print(f"   ⚠️ خطا در ثبت تراکنش انبار: {trans_error}")
                    # خطای تراکنش نباید ذخیره دستگاه را مختل کند
                
                # 🔴 **سیگنال تغییر داده**
                self.data_changed.emit("UsedAppliancesWarehouse")
                print(f"   📢 سیگنال data_changed ارسال شد")
                
                # 🔴 **برگرداندن موفقیت و شناسه دستگاه**
                return (True, item_id)
            else:
                print(f"   ❌ نتوانستیم ID دستگاه را پیدا کنیم")
                return (False, None)
                
        except Exception as e:
            print(f"   ❌ خطای غیرمنتظره: {e}")
            import traceback
            traceback.print_exc()
            return (False, None)
    

    def add_used_appliance_from_supplier(self, data):
        """افزودن لوازم دست دوم از تامین کننده - نسخه اصلاح شده"""
        try:
            print(f"🔄 شروع افزودن لوازم دست دوم از تامین کننده...")
            
            # تولید شماره سریال خودکار اگر خالی است
            serial_number = data.get('serial_number', '').strip()
            if not serial_number:
                import time
                import random
                timestamp = int(time.time() * 1000)
                random_part = random.randint(1000, 9999)
                serial_number = f"SUPP-{timestamp}-{random_part}"
                print(f"   📝 شماره سریال خودکار تولید شد: {serial_number}")
            
            # تهیه پارامترهای کوئری (بدون original_reception_id)
            query = """
            INSERT INTO UsedAppliancesWarehouse (
                device_type_id, brand_id, model, serial_number, production_year,
                source_type, source_person_id,
                condition, technical_status, last_repair_date, repair_history,
                purchase_price, purchase_date, purchase_document,
                sale_price, warranty_type, warranty_days, warranty_description,
                quantity, location, status, accessories, description, photos_path,
                entry_date
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            
            # تنظیم پارامترها
            params = (
                data.get('device_type_id'),
                data.get('brand_id'),
                data.get('model', 'بدون مدل'),
                serial_number,
                data.get('production_year', 1400),
                'تامین کننده',  # source_type
                data.get('supplier_id') or data.get('source_person_id'),
                data.get('condition', 'خوب'),
                data.get('technical_status', ''),
                data.get('last_repair_date'),
                data.get('repair_history', ''),
                float(data.get('purchase_price', 0)),
                data.get('purchase_date'),
                data.get('purchase_document', ''),
                float(data.get('sale_price', 0)),
                data.get('warranty_type', 'گارانتی فروشگاه'),
                data.get('warranty_days', 90),
                data.get('warranty_description', ''),
                data.get('quantity', 1),
                data.get('location', 'انبار عمومی'),
                data.get('status', 'موجود'),
                data.get('accessories', ''),
                data.get('description', ''),
                data.get('photos_path', ''),
                data.get('entry_date')
            )
            
            print(f"   🔧 پارامترهای کوئری آماده شدند")
            
            # اجرای کوئری اصلی
            success = self.db.execute_query(query, params)
            
            if not success:
                print(f"   ❌ خطا در اجرای کوئری اصلی")
                return (False, None)
            
            # دریافت ID دستگاه
            get_id_query = """
            SELECT id FROM UsedAppliancesWarehouse 
            WHERE serial_number = ? 
            ORDER BY id DESC LIMIT 1
            """
            
            result = self.db.fetch_one(get_id_query, (serial_number,))
            
            if result and 'id' in result:
                item_id = result['id']
                print(f"   🎯 دستگاه با شناسه {item_id} در دیتابیس ثبت شد")
                
                # ثبت تراکنش انبار
                try:
                    from PySide6.QtCore import QDateTime
                    transaction_date = QDateTime.currentDateTime().toString("yyyy-MM-dd HH:mm:ss")
                    
                    transaction_query = """
                    INSERT INTO InventoryTransactions (
                        transaction_type, warehouse_type, item_id, quantity, unit_price,
                        total_price, transaction_date, related_document, description, employee
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """
                    
                    quantity = data.get('quantity', 1)
                    purchase_price = float(data.get('purchase_price', 0))
                    total_price = quantity * purchase_price
                    
                    transaction_params = (
                        'خرید',
                        'لوازم دست دوم',
                        item_id,
                        quantity,
                        purchase_price,
                        total_price,
                        transaction_date,
                        data.get('purchase_document', '') or 'بدون شماره سند',
                        f"خرید لوازم دست دوم - {data.get('model', 'دستگاه')} از تامین کننده",
                        data.get('employee', 'سیستم')
                    )
                    
                    transaction_success = self.db.execute_query(transaction_query, transaction_params)
                    
                    if transaction_success:
                        print(f"   ✅ تراکنش انبار ثبت شد")
                    else:
                        print(f"   ⚠️ خطا در ثبت تراکنش انبار (اما دستگاه ذخیره شد)")
                    
                except Exception as trans_error:
                    print(f"   ⚠️ خطا در ثبت تراکنش انبار: {trans_error}")
                
                self.data_changed.emit("UsedAppliancesWarehouse")
                return (True, item_id)
            else:
                return (False, None)
                
        except Exception as e:
            print(f"   ❌ خطا: {e}")
            import traceback
            traceback.print_exc()
            return (False, None)


    def get_used_appliances_by_source(self, source_type=None):
        """دریافت لوازم دست دوم بر اساس منبع"""
        if source_type:
            query = """
            SELECT 
                uaw.*,
                dc.name as device_type_name,
                b.name as brand_name,
                p.full_name as source_name,
                r.reception_number
            FROM UsedAppliancesWarehouse uaw
            LEFT JOIN DeviceCategories_name dc ON uaw.device_type_id = dc.id
            LEFT JOIN Brands b ON uaw.brand_id = b.id
            LEFT JOIN Persons p ON uaw.source_person_id = p.id
            LEFT JOIN Receptions r ON uaw.original_reception_id = r.id
            WHERE uaw.source_type = ? AND uaw.status = 'موجود'
            ORDER BY uaw.entry_date DESC
            """
            return self.fetch_all(query, (source_type,))
        else:
            query = """
            SELECT 
                uaw.*,
                dc.name as device_type_name,
                b.name as brand_name,
                p.full_name as source_name,
                r.reception_number
            FROM UsedAppliancesWarehouse uaw
            LEFT JOIN DeviceCategories_name dc ON uaw.device_type_id = dc.id
            LEFT JOIN Brands b ON uaw.brand_id = b.id
            LEFT JOIN Persons p ON uaw.source_person_id = p.id
            LEFT JOIN Receptions r ON uaw.original_reception_id = r.id
            WHERE uaw.status = 'موجود'
            ORDER BY uaw.entry_date DESC
            """
            return self.fetch_all(query)
    
    def update_warehouse_item(self, warehouse_type, item_id, data):
        """بروزرسانی آیتم در انبار با ثبت تراکنش"""
        table_map = {
            'قطعات نو': 'NewPartsWarehouse',
            'قطعات دست دوم': 'UsedPartsWarehouse',
            'لوازم نو': 'NewAppliancesWarehouse',
            'لوازم دست دوم': 'UsedAppliancesWarehouse'
        }
        
        table_name = table_map.get(warehouse_type)
        if not table_name:
            return False
        
        try:
            # دریافت اطلاعات قدیمی برای مقایسه و ثبت تراکنش
            old_item = self.get_warehouse_item_info(warehouse_type, item_id)
            
            # ایجاد بخش SET به صورت دینامیک
            set_parts = []
            params = []
            
            for key, value in data.items():
                if key != 'id' and value is not None:
                    set_parts.append(f"{key} = ?")
                    params.append(value)
            
            if not set_parts:
                return False
            
            params.append(item_id)
            set_clause = ", ".join(set_parts)
            query = f"UPDATE {table_name} SET {set_clause}, updated_at = CURRENT_TIMESTAMP WHERE id = ?"
            
            print(f"🔧 در حال بروزرسانی آیتم {item_id} در انبار {warehouse_type}...")
            
            success = self.execute_query(query, params)
            
            if success and old_item:
                # ثبت تراکنش برای تغییرات
                self._log_update_transaction(warehouse_type, item_id, old_item, data)
                
            if success:
                self.data_changed.emit(table_name)
                print(f"✅ آیتم {item_id} با موفقیت بروزرسانی شد.")
                return True
            return False
            
        except Exception as e:
            print(f"❌ خطا در به‌روزرسانی اطلاعات انبار: {e}")
            return False

    def _log_update_transaction(self, warehouse_type, item_id, old_item, new_data):
        """ثبت تراکنش برای تغییرات در ویرایش"""
        try:
            # فقط اگر تغییر مهمی وجود دارد تراکنش ثبت کن
            changes = []
            
            # بررسی تغییر قیمت خرید
            old_price = old_item.get('purchase_price', 0)
            new_price = new_data.get('purchase_price', old_price)
            if old_price != new_price:
                changes.append(f"قیمت خرید: {old_price:,} → {new_price:,}")
            
            # بررسی تغییر تعداد
            old_qty = old_item.get('quantity', 0)
            new_qty = new_data.get('quantity', old_qty)
            if old_qty != new_qty:
                changes.append(f"تعداد: {old_qty} → {new_qty}")
            
            # بررسی تغییر وضعیت
            old_status = old_item.get('status', '')
            new_status = new_data.get('status', old_status)
            if old_status != new_status:
                changes.append(f"وضعیت: {old_status} → {new_status}")
            
            if changes:
                from PySide6.QtCore import QDateTime
                transaction_date = QDateTime.currentDateTime().toString("yyyy-MM-dd HH:mm:ss")
                
                query = """
                INSERT INTO InventoryTransactions (
                    transaction_type, warehouse_type, item_id, quantity, unit_price,
                    total_price, transaction_date, description, employee
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """
                
                # برای ویرایش، از نوع "تعدیل" استفاده می‌کنیم
                params = (
                    'تعدیل',
                    warehouse_type,
                    item_id,
                    new_qty - old_qty,  # تغییر در تعداد
                    new_price,
                    (new_qty - old_qty) * new_price,  # ارزش تغییر
                    transaction_date,
                    f"ویرایش {warehouse_type} - تغییرات: {'، '.join(changes)}",
                    'سیستم'
                )
                
                self.execute_query(query, params)
                print(f"📝 تراکنش ویرایش برای آیتم {item_id} ثبت شد")
                
        except Exception as e:
            print(f"⚠️ خطا در ثبت تراکنش ویرایش: {e}")


    def delete_warehouse_item(self, warehouse_type, item_id):
        """حذف آیتم از انبار"""
        table_map = {
            'قطعات نو': 'NewPartsWarehouse',
            'قطعات دست دوم': 'UsedPartsWarehouse',
            'لوازم نو': 'NewAppliancesWarehouse',
            'لوازم دست دوم': 'UsedAppliancesWarehouse'
        }
        
        table_name = table_map.get(warehouse_type)
        if not table_name:
            return False
        
        query = f"UPDATE {table_name} SET status = 'حذف شده' WHERE id = ?"
        
        if self.execute_query(query, (item_id,)):
            self.data_changed.emit(table_name)
            return True
        return False
    
    def get_low_stock_items(self, warehouse_type, threshold=5):
        """دریافت آیتم‌های با موجودی کم"""
        if warehouse_type == 'قطعات نو':
            query = """
            SELECT 
                npw.*,
                p.part_code,
                p.part_name,
                p.category,
                p.unit,
                p.min_stock
            FROM NewPartsWarehouse npw
            LEFT JOIN Parts p ON npw.part_id = p.id
            WHERE npw.status = 'موجود' AND npw.quantity <= ?
            ORDER BY npw.quantity
            """
            return self.fetch_all(query, (threshold,))
        elif warehouse_type == 'لوازم نو':
            query = """
            SELECT 
                naw.*,
                dc.name as device_type_name,
                b.name as brand_name
            FROM NewAppliancesWarehouse naw
            LEFT JOIN DeviceCategories_name dc ON naw.device_type_id = dc.id
            LEFT JOIN Brands b ON naw.brand_id = b.id
            WHERE naw.status = 'موجود' AND naw.quantity <= ?
            ORDER BY naw.quantity
            """
            return self.fetch_all(query, (threshold,))
        
        return []
    
    def get_inventory_transactions(self, warehouse_type=None, start_date=None, end_date=None):
        """دریافت تراکنش‌های انبار"""
        query = """
        SELECT 
            it.*,
            CASE 
                WHEN it.warehouse_type = 'قطعات نو' THEN np.part_id
                WHEN it.warehouse_type = 'لوازم نو' THEN naw.id
                ELSE NULL
            END as related_item_id
        FROM InventoryTransactions it
        LEFT JOIN NewPartsWarehouse np ON it.item_id = np.id AND it.warehouse_type = 'قطعات نو'
        LEFT JOIN NewAppliancesWarehouse naw ON it.item_id = naw.id AND it.warehouse_type = 'لوازم نو'
        WHERE 1=1
        """
        
        params = []
        
        if warehouse_type:
            query += " AND it.warehouse_type = ?"
            params.append(warehouse_type)
        
        if start_date:
            query += " AND DATE(it.transaction_date) >= ?"
            params.append(start_date)
        
        if end_date:
            query += " AND DATE(it.transaction_date) <= ?"
            params.append(end_date)
        
        query += " ORDER BY it.transaction_date DESC"
        
        return self.fetch_all(query, params)

    def update_stock_info(self, warehouse_type, warehouse_id, data):
        """به‌روزرسانی اطلاعات موجودی در انبار"""
        table_map = {
            'قطعات نو': 'NewPartsWarehouse',
            'قطعات دست دوم': 'UsedPartsWarehouse',
            'لوازم نو': 'NewAppliancesWarehouse',
            'لوازم دست دوم': 'UsedAppliancesWarehouse'
        }
        
        table_name = table_map.get(warehouse_type)
        if not table_name:
            return False
        
        try:
            # ایجاد بخش SET به صورت دینامیک
            set_parts = []
            params = []
            
            for key, value in data.items():
                if key != 'id' and value is not None:
                    set_parts.append(f"{key} = ?")
                    params.append(value)
            
            if not set_parts:
                return False
            
            params.append(warehouse_id)
            set_clause = ", ".join(set_parts)
            query = f"UPDATE {table_name} SET {set_clause}, updated_at = CURRENT_TIMESTAMP WHERE id = ?"
            
            success = self.execute_query(query, params)
            if success:
                self.data_changed.emit(table_name)
            
            return success
            
        except Exception as e:
            print(f"خطا در به‌روزرسانی اطلاعات انبار: {e}")
            return False        
    


    def soft_delete_warehouse_item(self, warehouse_type, item_id, reason="حذف دستی"):
        """حذف نرم (تغییر وضعیت به 'اسقاط' یا 'ناموجود')"""
        try:
            print(f"🔄 در حال حذف نرم آیتم {item_id} از {warehouse_type}...")
            
            table_map = {
                'قطعات نو': 'NewPartsWarehouse',
                'قطعات دست دوم': 'UsedPartsWarehouse',
                'لوازم نو': 'NewAppliancesWarehouse',
                'لوازم دست دوم': 'UsedAppliancesWarehouse'
            }
            
            table_name = table_map.get(warehouse_type)
            if not table_name:
                return False
            
            # دریافت اطلاعات قبل از حذف
            item_info = self.get_warehouse_item_info(warehouse_type, item_id)
            if not item_info:
                return False
            
            # ذخیره وضعیت اصلی برای بازیابی
            original_status = item_info.get('status', 'موجود')
            
            # انتخاب وضعیت مناسب بر اساس نوع انبار
            if warehouse_type == 'قطعات دست دوم':
                # برای قطعات دست دوم از 'اسقاط' استفاده می‌کنیم
                new_status = 'اسقاط'
            elif warehouse_type == 'قطعات نو':
                # برای قطعات نو از 'ناموجود' استفاده می‌کنیم
                new_status = 'ناموجود'
            elif warehouse_type == 'لوازم دست دوم':
                # برای لوازم دست دوم از 'اسقاط' استفاده می‌کنیم
                new_status = 'اسقاط'
            elif warehouse_type == 'لوازم نو':
                # برای لوازم نو از 'ناموجود' استفاده می‌کنیم
                new_status = 'ناموجود'
            else:
                new_status = 'اسقاط'  # پیش‌فرض
            
            print(f"   📝 تغییر وضعیت از '{original_status}' به '{new_status}'")
            
            # تغییر وضعیت
            query = f"UPDATE {table_name} SET status = ? WHERE id = ?"
            success = self.execute_query(query, (new_status, item_id))
            
            if success:
                # ثبت تراکنش حذف نرم
                delete_data = {
                    'item_id': item_id,
                    'quantity': item_info.get('quantity', 0),
                    'unit_price': item_info.get('purchase_price', 0),
                    'item_name': item_info.get('part_name', item_info.get('model', 'آیتم')),
                    'reason': f"حذف نرم - {reason}",
                    'original_status': original_status,
                    'new_status': new_status
                }
                
                # ثبت در تاریخچه حذف‌ها
                self._record_soft_delete_transaction(warehouse_type, delete_data)
                
                # ثبت در لاگ تراکنش‌ها
                self._log_soft_deletion_transaction(warehouse_type, delete_data)
                
                self.data_changed.emit(table_name)
                print(f"✅ حذف نرم آیتم {item_id} با موفقیت انجام شد (وضعیت: {new_status})")
                return True
            return False
            
        except Exception as e:
            print(f"خطا در حذف نرم: {e}")
            import traceback
            traceback.print_exc()
            return False

    def _record_soft_delete_transaction(self, warehouse_type, data):
        """ثبت تراکنش حذف نرم در جدول مخصوص"""
        try:
            query = """
            INSERT INTO InventorySoftDeletions (
                warehouse_type, item_id, quantity, unit_price, total_price,
                deletion_date, deletion_reason, original_status, new_status,
                description, deleted_by
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            
            from PySide6.QtCore import QDateTime
            deletion_date = QDateTime.currentDateTime().toString("yyyy-MM-dd HH:mm:ss")
            
            total_price = data['quantity'] * data['unit_price']
            
            params = (
                warehouse_type,
                data['item_id'],
                data['quantity'],
                data['unit_price'],
                total_price,
                deletion_date,
                data.get('reason', 'حذف دستی'),
                data.get('original_status', 'موجود'),
                data.get('new_status', 'اسقاط'),
                data.get('description', ''),
                data.get('employee', 'سیستم')
            )
            
            return self.execute_query(query, params)
            
        except Exception as e:
            print(f"خطا در ثبت تراکنش حذف نرم: {e}")
            return False

    def _log_soft_deletion_transaction(self, warehouse_type, data):
        """ثبت لاگ حذف نرم در جدول تراکنش‌های اصلی"""
        try:
            query = """
            INSERT INTO InventoryTransactions (
                transaction_type, warehouse_type, item_id, quantity, unit_price,
                total_price, transaction_date, related_document, description, employee
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            
            from PySide6.QtCore import QDateTime
            transaction_date = QDateTime.currentDateTime().toString("yyyy-MM-dd HH:mm:ss")
            
            params = (
                'حذف نرم',  # نوع تراکنش
                warehouse_type,
                data['item_id'],
                data['quantity'],
                data['unit_price'],
                data['quantity'] * data['unit_price'],
                transaction_date,
                'SOFT_DELETE',
                f"حذف نرم {warehouse_type} - {data.get('item_name', 'آیتم')} (از {data.get('original_status', '')} به {data.get('new_status', '')}) - دلیل: {data.get('reason', 'نامشخص')}",
                'سیستم'
            )
            
            return self.execute_query(query, params)
            
        except Exception as e:
            print(f"خطا در ثبت لاگ حذف نرم: {e}")
            return False

    def restore_soft_deleted_item(self, warehouse_type, deletion_id):
        """بازیابی آیتم حذف نرم شده"""
        try:
            # دریافت اطلاعات حذف نرم
            query = """
            SELECT * FROM InventorySoftDeletions 
            WHERE id = ? AND warehouse_type = ?
            """
            deletion_record = self.fetch_one(query, (deletion_id, warehouse_type))
            
            if not deletion_record:
                return False
            
            item_id = deletion_record['item_id']
            original_status = deletion_record['original_status']
            
            # برگرداندن به وضعیت اصلی
            table_map = {
                'قطعات نو': 'NewPartsWarehouse',
                'قطعات دست دوم': 'UsedPartsWarehouse',
                'لوازم نو': 'NewAppliancesWarehouse',
                'لوازم دست دوم': 'UsedAppliancesWarehouse'
            }
            
            table_name = table_map.get(warehouse_type)
            if not table_name:
                return False
            
            restore_query = f"UPDATE {table_name} SET status = ? WHERE id = ?"
            success = self.execute_query(restore_query, (original_status, item_id))
            
            if success:
                # ثبت تراکنش بازیابی
                self._log_restoration_transaction(warehouse_type, deletion_record)
                
                # حذف از جدول حذف‌های نرم
                delete_query = "DELETE FROM InventorySoftDeletions WHERE id = ?"
                self.execute_query(delete_query, (deletion_id,))
                
                self.data_changed.emit(table_name)
                return True
            return False
            
        except Exception as e:
            print(f"خطا در بازیابی آیتم: {e}")
            return False

    def _log_restoration_transaction(self, warehouse_type, deletion_record):
        """ثبت تراکنش بازیابی"""
        try:
            query = """
            INSERT INTO InventoryTransactions (
                transaction_type, warehouse_type, item_id, quantity, unit_price,
                total_price, transaction_date, related_document, description, employee
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            
            from PySide6.QtCore import QDateTime
            transaction_date = QDateTime.currentDateTime().toString("yyyy-MM-dd HH:mm:ss")
            
            params = (
                'بازیابی',
                warehouse_type,
                deletion_record['item_id'],
                deletion_record['quantity'],
                deletion_record['unit_price'],
                deletion_record['total_price'],
                transaction_date,
                'RESTORATION',
                f"بازیابی {warehouse_type} - آیتم #{deletion_record['item_id']} (وضعیت: {deletion_record['original_status']})",
                'سیستم'
            )
            
            return self.execute_query(query, params)
            
        except Exception as e:
            print(f"خطا در ثبت تراکنش بازیابی: {e}")
            return False


    def get_inventory_transactions(self, warehouse_type=None, start_date=None, end_date=None):
        """دریافت تراکنش‌های انبار - نسخه بهبود یافته شامل حذف‌ها"""
        try:
            print(f"🔍 دریافت تراکنش‌های انبار...")
            print(f"   نوع انبار: {warehouse_type}")
            print(f"   از تاریخ: {start_date}")
            print(f"   تا تاریخ: {end_date}")
            
            # دریافت از جدول اصلی تراکنش‌ها
            query_main = """
            SELECT 
                'main' as source,
                it.id,
                it.transaction_type,
                it.warehouse_type,
                it.item_id,
                it.quantity,
                it.unit_price,
                it.total_price,
                it.transaction_date,
                it.related_document,
                it.description,
                it.employee,
                it.created_at
            FROM InventoryTransactions it
            WHERE 1=1
            """
            
            # دریافت از جدول حذف‌ها
            query_delete = """
            SELECT 
                'delete' as source,
                idt.id,
                'حذف' as transaction_type,
                idt.warehouse_type,
                idt.item_id,
                idt.quantity,
                idt.unit_price,
                idt.total_price,
                idt.deletion_date as transaction_date,
                'حذف دستی' as related_document,
                CASE 
                    WHEN idt.description IS NOT NULL THEN 'حذف - ' || idt.description
                    ELSE 'حذف - ' || idt.deletion_reason
                END as description,
                idt.deleted_by as employee,
                idt.created_at
            FROM InventoryDeleteTransactions idt
            WHERE 1=1
            """
            
            # دریافت از جدول حذف‌های نرم
            query_soft_delete = """
            SELECT 
                'soft_delete' as source,
                isd.id,
                'حذف نرم' as transaction_type,
                isd.warehouse_type,
                isd.item_id,
                isd.quantity,
                isd.unit_price,
                isd.total_price,
                isd.deletion_date as transaction_date,
                'حذف نرم' as related_document,
                CASE 
                    WHEN isd.description IS NOT NULL THEN 'حذف نرم - ' || isd.description
                    ELSE 'حذف نرم - ' || isd.deletion_reason || ' (از ' || isd.original_status || ' به ' || isd.new_status || ')'
                END as description,
                isd.deleted_by as employee,
                isd.created_at
            FROM InventorySoftDeletions isd
            WHERE 1=1
            """
            
            # ساخت شرط‌های WHERE
            conditions_main = []
            conditions_delete = []
            conditions_soft = []
            params_main = []
            params_delete = []
            params_soft = []
            
            if warehouse_type:
                conditions_main.append("it.warehouse_type = ?")
                conditions_delete.append("idt.warehouse_type = ?")
                conditions_soft.append("isd.warehouse_type = ?")
                params_main.append(warehouse_type)
                params_delete.append(warehouse_type)
                params_soft.append(warehouse_type)
            
            if start_date:
                conditions_main.append("DATE(it.transaction_date) >= ?")
                conditions_delete.append("DATE(idt.deletion_date) >= ?")
                conditions_soft.append("DATE(isd.deletion_date) >= ?")
                params_main.append(start_date)
                params_delete.append(start_date)
                params_soft.append(start_date)
            
            if end_date:
                conditions_main.append("DATE(it.transaction_date) <= ?")
                conditions_delete.append("DATE(idt.deletion_date) <= ?")
                conditions_soft.append("DATE(isd.deletion_date) <= ?")
                params_main.append(end_date)
                params_delete.append(end_date)
                params_soft.append(end_date)
            
            # اضافه کردن شرط‌ها به کوئری‌ها
            if conditions_main:
                query_main += " AND " + " AND ".join(conditions_main)
            
            if conditions_delete:
                query_delete += " AND " + " AND ".join(conditions_delete)
            
            if conditions_soft:
                query_soft_delete += " AND " + " AND ".join(conditions_soft)
            
            # UNION همه کوئری‌ها
            final_query = f"""
            {query_main}
            UNION ALL
            {query_delete}
            UNION ALL
            {query_soft_delete}
            ORDER BY transaction_date DESC
            """
            
            # اجرای کوئری
            all_params = params_main + params_delete + params_soft
            
            print(f"   کوئری نهایی: {final_query[:200]}...")
            print(f"   پارامترها: {all_params}")
            
            results = self.fetch_all(final_query, all_params)
            print(f"   ✅ {len(results)} تراکنش (شامل حذف‌ها) یافت شد")
            
            # تبدیل تاریخ‌ها به شمسی برای نمایش بهتر
            for result in results:
                try:
                    # تبدیل تاریخ میلادی به شمسی
                    trans_date = result.get('transaction_date', '')
                    if trans_date:
                        # اگر تاریخ شمسی است (دارای /) نیازی به تبدیل نیست
                        if '/' not in str(trans_date):
                            # فرض می‌کنیم میلادی است
                            import re
                            numbers = re.findall(r'\d+', str(trans_date))
                            if len(numbers) >= 3:
                                year, month, day = map(int, numbers[:3])
                                if year > 1500:  # میلادی است
                                    import datetime
                                    from datetime import date as datetime_date
                                    gdate = datetime_date(year, month, day)
                                    jdate = jdatetime.date.fromgregorian(date=gdate)
                                    result['transaction_date_shamsi'] = jdate.strftime("%Y/%m/%d")
                                else:
                                    result['transaction_date_shamsi'] = f"{year}/{month:02d}/{day:02d}"
                except Exception as e:
                    print(f"⚠️ خطا در تبدیل تاریخ: {e}")
                    result['transaction_date_shamsi'] = str(trans_date)
            
            return results
            
        except Exception as e:
            print(f"❌ خطا در دریافت تراکنش‌ها: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def get_all_transactions_grouped(self):
        """دریافت تمام تراکنش‌ها گروه‌بندی شده بر اساس نوع"""
        try:
            query = """
            SELECT 
                transaction_type,
                COUNT(*) as count,
                SUM(total_price) as total_amount,
                SUM(quantity) as total_quantity
            FROM (
                SELECT transaction_type, total_price, quantity FROM InventoryTransactions
                UNION ALL
                SELECT 'حذف' as transaction_type, total_price, quantity FROM InventoryDeleteTransactions
                UNION ALL
                SELECT 'حذف نرم' as transaction_type, total_price, quantity FROM InventorySoftDeletions
            ) as all_transactions
            GROUP BY transaction_type
            ORDER BY total_amount DESC
            """
            
            return self.fetch_all(query)
            
        except Exception as e:
            print(f"❌ خطا در دریافت آمار تراکنش‌ها: {e}")
            return []



    def delete_warehouse_item_with_transaction(self, warehouse_type, item_id, reason="حذف دستی"):
        """حذف آیتم از انبار با ثبت تراکنش حذف"""
        try:
            print(f"🗑️ در حال حذف آیتم {item_id} از انبار {warehouse_type}...")
            
            # ابتدا اطلاعات آیتم را دریافت می‌کنیم
            item_info = self.get_warehouse_item_info(warehouse_type, item_id)
            if not item_info:
                print(f"⚠️ آیتم {item_id} در انبار {warehouse_type} یافت نشد")
                return False
            
            # نام جدول بر اساس نوع انبار
            table_map = {
                'قطعات نو': 'NewPartsWarehouse',
                'قطعات دست دوم': 'UsedPartsWarehouse',
                'لوازم نو': 'NewAppliancesWarehouse',
                'لوازم دست دوم': 'UsedAppliancesWarehouse'
            }
            
            table_name = table_map.get(warehouse_type)
            if not table_name:
                print(f"⚠️ نوع انبار نامعتبر: {warehouse_type}")
                return False
            
            # ثبت تراکنش حذف
            transaction_data = {
                'item_id': item_id,
                'quantity': item_info.get('quantity', 0),
                'unit_price': item_info.get('purchase_price', 0),
                'total_price': item_info.get('quantity', 0) * item_info.get('purchase_price', 0),
                'description': f"حذف {warehouse_type} - {item_info.get('part_name', item_info.get('model', 'آیتم'))}",
                'reason': reason,
                'employee': 'سیستم'
            }
            
            # 🔴 اطمینان از وجود جدول قبل از ثبت تراکنش
            self.ensure_inventory_tables_exist()
            
            if not self._record_delete_transaction(warehouse_type, transaction_data):
                print(f"⚠️ خطا در ثبت تراکنش حذف برای آیتم {item_id}")
                # همچنان ادامه می‌دهیم و حذف را انجام می‌دهیم
                print(f"   ادامه حذف بدون ثبت تراکنش...")
            
            # حذف فیزیکی از جدول اصلی
            delete_query = f"DELETE FROM {table_name} WHERE id = ?"
            
            print(f"   🔧 اجرای کوئری حذف: {delete_query} برای آیتم {item_id}")
            
            success = self.execute_query(delete_query, (item_id,))
            
            if success:
                print(f"   ✅ آیتم {item_id} از انبار {warehouse_type} حذف شد")
                
                # ثبت لاگ حذف در جدول تراکنش‌های اصلی (InventoryTransactions)
                delete_transaction_data = {
                    'item_id': item_id,
                    'item_name': item_info.get('part_name', item_info.get('model', 'آیتم')),
                    'quantity': item_info.get('quantity', 0),
                    'unit_price': item_info.get('purchase_price', 0),
                    'reason': reason
                }
                
                self._log_deletion_transaction(warehouse_type, delete_transaction_data)
                
                # ارسال سیگنال
                self.data_changed.emit(table_name)
                self.data_changed.emit("InventoryDeleteTransactions")
                
                return True
            else:
                print(f"   ❌ خطا در حذف آیتم {item_id}")
                return False
                
        except Exception as e:
            print(f"❌ خطا در حذف آیتم: {e}")
            import traceback
            traceback.print_exc()
            return False

    def get_warehouse_item_info(self, warehouse_type, item_id):
        """دریافت اطلاعات کامل یک آیتم انبار"""
        try:
            if warehouse_type == 'قطعات دست دوم':
                query = """
                SELECT 
                    upw.*,
                    p.part_code,
                    p.part_name,
                    p.category,
                    p.brand,
                    p.unit
                FROM UsedPartsWarehouse upw
                LEFT JOIN Parts p ON upw.part_id = p.id
                WHERE upw.id = ?
                """
                return self.fetch_one(query, (item_id,))
            elif warehouse_type == 'قطعات نو':
                query = """
                SELECT 
                    npw.*,
                    p.part_code,
                    p.part_name,
                    p.category,
                    p.brand,
                    p.unit
                FROM NewPartsWarehouse npw
                LEFT JOIN Parts p ON npw.part_id = p.id
                WHERE npw.id = ?
                """
                return self.fetch_one(query, (item_id,))
            elif warehouse_type == 'لوازم دست دوم':
                query = """
                SELECT 
                    uaw.*,
                    dc.name as device_type_name,
                    b.name as brand_name,
                    p.full_name as source_name,
                    r.reception_number
                FROM UsedAppliancesWarehouse uaw
                LEFT JOIN DeviceCategories_name dc ON uaw.device_type_id = dc.id
                LEFT JOIN Brands b ON uaw.brand_id = b.id
                LEFT JOIN Persons p ON uaw.source_person_id = p.id
                LEFT JOIN Receptions r ON uaw.original_reception_id = r.id
                WHERE uaw.id = ?
                """
                return self.fetch_one(query, (item_id,))
            elif warehouse_type == 'لوازم نو':
                query = """
                SELECT 
                    naw.*,
                    dc.name as device_type_name,
                    b.name as brand_name,
                    p.full_name as supplier_name
                FROM NewAppliancesWarehouse naw
                LEFT JOIN DeviceCategories_name dc ON naw.device_type_id = dc.id
                LEFT JOIN Brands b ON naw.brand_id = b.id
                LEFT JOIN Persons p ON naw.supplier_id = p.id
                WHERE naw.id = ?
                """
                return self.fetch_one(query, (item_id,))
        except Exception as e:
            print(f"خطا در دریافت اطلاعات آیتم: {e}")
            return None

    def _record_delete_transaction(self, warehouse_type, data):
        """ثبت تراکنش حذف در جدول InventoryDeleteTransactions - نسخه مقاوم در برابر خطا"""
        try:
            # تاریخ و زمان فعلی به میلادی
            from PySide6.QtCore import QDateTime
            deletion_date = QDateTime.currentDateTime().toString("yyyy-MM-dd HH:mm:ss")
            
            query = """
            INSERT INTO InventoryDeleteTransactions (
                warehouse_type, item_id, quantity, unit_price, total_price,
                deletion_date, deletion_reason, description, deleted_by
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            
            params = (
                warehouse_type,
                data['item_id'],
                data['quantity'],
                data['unit_price'],
                data['total_price'],
                deletion_date,
                data.get('reason', 'حذف دستی'),
                data.get('description', ''),
                data.get('employee', 'سیستم')
            )
            
            print(f"📝 ثبت تراکنش حذف در InventoryDeleteTransactions...")
            print(f"   پارامترها: {params}")
            
            result = self.execute_query(query, params)
            if result:
                print(f"✅ تراکنش حذف ثبت شد.")
            else:
                print(f"⚠️ خطا در ثبت تراکنش حذف.")
            
            return result
            
        except Exception as e:
            print(f"❌ خطا در ثبت تراکنش حذف: {e}")
            import traceback
            traceback.print_exc()
            return False

   
    def _log_deletion_transaction(self, warehouse_type, data):
        """ثبت لاگ حذف در جدول تراکنش‌های اصلی"""
        try:
            query = """
            INSERT INTO InventoryTransactions (
                transaction_type, warehouse_type, item_id, quantity, unit_price,
                total_price, transaction_date, related_document, description, employee
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            
            from PySide6.QtCore import QDateTime
            transaction_date = QDateTime.currentDateTime().toString("yyyy-MM-dd HH:mm:ss")
            
            params = (
                'حذف',  # نوع تراکنش
                warehouse_type,
                data['item_id'],
                data['quantity'],
                data['unit_price'],
                data['quantity'] * data['unit_price'],
                transaction_date,
                'DELETION',  # سند مرتبط
                f"حذف {warehouse_type} - {data['item_name']} - دلیل: {data.get('reason', 'نامشخص')}",
                'سیستم'
            )
            
            return self.execute_query(query, params)
            
        except Exception as e:
            print(f"خطا در ثبت لاگ حذف: {e}")
            return False
    
    def get_deletion_transactions(self, start_date=None, end_date=None, warehouse_type=None):
        """دریافت تاریخچه حذف‌ها"""
        query = """
        SELECT * FROM InventoryDeleteTransactions 
        WHERE 1=1
        """
        
        params = []
        
        if start_date:
            query += " AND DATE(deletion_date) >= ?"
            params.append(start_date)
        
        if end_date:
            query += " AND DATE(deletion_date) <= ?"
            params.append(end_date)
        
        if warehouse_type:
            query += " AND warehouse_type = ?"
            params.append(warehouse_type)
        
        query += " ORDER BY deletion_date DESC"
        
        return self.fetch_all(query, params)
    
    def delete_warehouse_item(self, warehouse_type, item_id, soft_delete=True, reason="حذف دستی"):
        """حذف آیتم از انبار (با قابلیت حذف نرم یا سخت)"""
        if soft_delete:
            return self.soft_delete_warehouse_item(warehouse_type, item_id, reason)
        else:
            return self.delete_warehouse_item_with_transaction(warehouse_type, item_id, reason)
      
    def restore_deleted_item(self, warehouse_type, deletion_id):
        """بازیابی آیتم حذف شده"""
        try:
            # دریافت اطلاعات حذف
            query = """
            SELECT * FROM InventoryDeleteTransactions 
            WHERE id = ? AND warehouse_type = ?
            """
            deletion_record = self.fetch_one(query, (deletion_id, warehouse_type))
            
            if not deletion_record:
                return False
            
            item_id = deletion_record['item_id']
            
            # بر اساس نوع انبار، وضعیت را به موجود تغییر می‌دهیم
            table_map = {
                'قطعات نو': 'NewPartsWarehouse',
                'قطعات دست دوم': 'UsedPartsWarehouse',
                'لوازم نو': 'NewAppliancesWarehouse',
                'لوازم دست دوم': 'UsedAppliancesWarehouse'
            }
            
            table_name = table_map.get(warehouse_type)
            if not table_name:
                return False
            
            restore_query = f"UPDATE {table_name} SET status = 'موجود' WHERE id = ?"
            success = self.execute_query(restore_query, (item_id,))
            
            if success:
                # ثبت تراکنش بازیابی
                restore_transaction_query = """
                INSERT INTO InventoryTransactions (
                    transaction_type, warehouse_type, item_id, quantity, unit_price,
                    total_price, transaction_date, related_document, description, employee
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """
                
                from PySide6.QtCore import QDateTime
                transaction_date = QDateTime.currentDateTime().toString("yyyy-MM-dd HH:mm:ss")
                
                params = (
                    'بازیابی',
                    warehouse_type,
                    item_id,
                    deletion_record['quantity'],
                    deletion_record['unit_price'],
                    deletion_record['total_price'],
                    transaction_date,
                    'RESTORATION',
                    f"بازیابی {warehouse_type} - آیتم #{item_id}",
                    'سیستم'
                )
                
                self.execute_query(restore_transaction_query, params)
                
                self.data_changed.emit(table_name)
                return True
            return False
            
        except Exception as e:
            print(f"خطا در بازیابی آیتم: {e}")
            return False

    def get_item_name(self, warehouse_type, item_id):
        """دریافت نام آیتم بر اساس نوع انبار و شناسه"""
        try:
            if warehouse_type == 'قطعات نو':
                query = """
                SELECT p.part_name 
                FROM NewPartsWarehouse npw
                LEFT JOIN Parts p ON npw.part_id = p.id
                WHERE npw.id = ?
                """
                result = self.fetch_one(query, (item_id,))
                return result['part_name'] if result else f"قطعه #{item_id}"
            
            elif warehouse_type == 'لوازم نو':
                query = """
                SELECT naw.model 
                FROM NewAppliancesWarehouse naw
                WHERE naw.id = ?
                """
                result = self.fetch_one(query, (item_id,))
                return result['model'] if result else f"لوازم #{item_id}"
            
            elif warehouse_type == 'قطعات دست دوم':
                query = """
                SELECT p.part_name 
                FROM UsedPartsWarehouse upw
                LEFT JOIN Parts p ON upw.part_id = p.id
                WHERE upw.id = ?
                """
                result = self.fetch_one(query, (item_id,))
                return result['part_name'] if result else f"قطعه دست دوم #{item_id}"
            
            elif warehouse_type == 'لوازم دست دوم':
                query = """
                SELECT uaw.model 
                FROM UsedAppliancesWarehouse uaw
                WHERE uaw.id = ?
                """
                result = self.fetch_one(query, (item_id,))
                return result['model'] if result else f"لوازم دست دوم #{item_id}"
            
            else:
                return f"آیتم #{item_id}"
                
        except Exception as e:
            print(f"خطا در دریافت نام آیتم ({warehouse_type}, {item_id}): {e}")
            return f"خطا #{item_id}"


class Invoice(BaseModel):
    """مدل مدیریت فاکتورها"""
    
    def __init__(self, db_manager):
        super().__init__(db_manager)
        self.table_name = "Invoices"
    
    def generate_invoice_number(self):
        """تولید شماره فاکتور خودکار"""
        year = QDate.currentDate().year()
        month = QDate.currentDate().month()
        
        query = f"""
        SELECT COUNT(*) as count FROM {self.table_name} 
        WHERE strftime('%Y', invoice_date) = ? AND strftime('%m', invoice_date) = ?
        """
        
        result = self.fetch_one(query, (str(year), f"{month:02d}"))
        count = result['count'] + 1 if result else 1
        
        return f"INV-{year}{month:02d}{count:04d}"
    
    def create_invoice(self, data, items):
        """ایجاد فاکتور جدید"""
        invoice_number = self.generate_invoice_number()
        
        # محاسبه جمع‌های فاکتور
        subtotal = sum(item['total_price'] for item in items)
        discount = data.get('discount', 0)
        tax = data.get('tax', 0)
        total = subtotal - discount + tax
        
        query = f"""
        INSERT INTO {self.table_name} (
            invoice_number, invoice_type, customer_id, reception_id, invoice_date,
            due_date, subtotal, discount, tax, total, paid_amount, remaining_amount,
            payment_status, payment_method, description, outsourced_to, outsourced_cost
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        
        params = (
            invoice_number,
            data.get('invoice_type', 'خدمات'),
            data.get('customer_id'),
            data.get('reception_id'),
            data.get('invoice_date', QDate.currentDate().toString('yyyy-MM-dd')),
            data.get('due_date'),
            subtotal,
            discount,
            tax,
            total,
            data.get('paid_amount', 0),
            total - data.get('paid_amount', 0),
            data.get('payment_status', 'نقدی'),
            data.get('payment_method', ''),
            data.get('description', ''),
            data.get('outsourced_to'),
            data.get('outsourced_cost', 0)
        )
        
        if self.execute_query(query, params):
            # دریافت invoice_id
            query = "SELECT last_insert_rowid() as id"
            result = self.fetch_one(query)
            invoice_id = result['id'] if result else None
            
            # افزودن اقلام فاکتور
            if invoice_id and self._add_invoice_items(invoice_id, items):
                self.data_changed.emit(self.table_name)
                
                # محاسبه سهم شرکا
                if data.get('calculate_partner_shares', True):
                    self._calculate_partner_shares(invoice_id, data.get('invoice_type'))
                
                return invoice_number
        return None
    
    def _add_invoice_items(self, invoice_id, items):
        """افزودن اقلام فاکتور"""
        for item in items:
            query = """
            INSERT INTO InvoiceItems (
                invoice_id, item_type, item_id, item_name, quantity,
                unit_price, total_price, description, partner_percentage
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            
            params = (
                invoice_id,
                item.get('item_type', 'قطعه'),
                item.get('item_id'),
                item.get('item_name', ''),
                item.get('quantity', 1),
                item.get('unit_price', 0),
                item.get('total_price', 0),
                item.get('description', ''),
                item.get('partner_percentage', 0)
            )
            
            if not self.execute_query(query, params):
                return False
        return True
    
    def _calculate_partner_shares(self, invoice_id, invoice_type):
        """محاسبه سهم شرکا از فاکتور"""
        # دریافت اطلاعات شرکا فعال
        query = """
        SELECT p.*, ps.profit_percentage 
        FROM Partners p
        JOIN Persons per ON p.person_id = per.id
        WHERE p.active = 1
        """
        
        partners = self.fetch_all(query)
        if not partners:
            return
        
        # دریافت مبلغ کل فاکتور
        query = "SELECT total FROM Invoices WHERE id = ?"
        invoice = self.fetch_one(query, (invoice_id,))
        if not invoice:
            return
        
        total_amount = invoice['total']
        
        # محاسبه سهم هر شریک (در این مثال به صورت مساوی)
        share_percentage = 100.0 / len(partners)
        share_amount = total_amount * (share_percentage / 100)
        
        # ثبت سهم شرکا
        for partner in partners:
            query = """
            INSERT INTO PartnerShares (
                partner_id, transaction_type, transaction_id,
                share_percentage, share_amount, description
            ) VALUES (?, ?, ?, ?, ?, ?)
            """
            
            params = (
                partner['id'],
                invoice_type,
                invoice_id,
                share_percentage,
                share_amount,
                f"سهم از فاکتور {invoice_id}"
            )
            
            self.execute_query(query, params)

AccountingManager = AccountManager  # این ساده‌تر است
class AccountManager(BaseModel):
    """مدیریت حساب‌های بانکی و نقدی - نسخه کامل و اصلاح شده"""
    
    def __init__(self, db_manager):
        super().__init__(db_manager)
        self.table_name = "Accounts"
    
    def add_account(self, data):
        """افزودن حساب جدید - نسخه اصلاح شده"""
        try:
            print(f"➕ در حال افزودن حساب جدید...")
            print(f"   داده‌ها: {data}")
            
            query = """
            INSERT INTO Accounts (
                account_number, account_name, account_type, bank_name,
                initial_balance, current_balance, owner_name, description, is_active
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            
            # تبدیل موجودی به ریال (در دیتابیس ریال ذخیره می‌شود)
            initial_balance_rial = float(data.get('initial_balance', 0)) * 10
            
            params = (
                data.get('account_number', ''),
                data.get('account_name', ''),
                data.get('account_type', 'جاری'),
                data.get('bank_name', ''),
                initial_balance_rial,
                initial_balance_rial,  # current_balance = initial_balance
                data.get('owner_name', ''),
                data.get('description', ''),
                1  # is_active = True
            )
            
            print(f"   پارامترهای کوئری: {params}")
            
            # استفاده مستقیم از execute_query
            success = self.db.execute_query(query, params)
            
            if success:
                print(f"✅ حساب با موفقیت ثبت شد")
                self.data_changed.emit("Accounts")
                return True, "حساب با موفقیت ایجاد شد"
            else:
                print(f"❌ خطا در ثبت حساب")
                return False, "خطا در ثبت حساب"
                
        except Exception as e:
            print(f"❌ خطا در افزودن حساب: {e}")
            import traceback
            traceback.print_exc()
            return False, f"خطا: {str(e)}"
    
    def update_account(self, account_id, data):
        """ویرایش حساب موجود"""
        try:
            print(f"✏️ در حال ویرایش حساب {account_id}...")
            
            query = """
            UPDATE Accounts SET
                account_number = ?,
                account_name = ?,
                account_type = ?,
                bank_name = ?,
                owner_name = ?,
                description = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """
            
            params = (
                data.get('account_number', ''),
                data.get('account_name', ''),
                data.get('account_type', 'جاری'),
                data.get('bank_name', ''),
                data.get('owner_name', ''),
                data.get('description', ''),
                account_id
            )
            
            print(f"   پارامترهای کوئری: {params}")
            
            success = self.db.execute_query(query, params)
            
            if success:
                print(f"✅ حساب {account_id} با موفقیت ویرایش شد")
                self.data_changed.emit("Accounts")
                return True, "حساب با موفقیت ویرایش شد"
            return False, "خطا در ویرایش حساب"
            
        except Exception as e:
            print(f"❌ خطا در ویرایش حساب: {e}")
            return False, f"خطا: {str(e)}"
    
    def get_account_by_id(self, account_id):
        """دریافت حساب با شناسه"""
        query = "SELECT * FROM Accounts WHERE id = ?"
        account = self.fetch_one(query, (account_id,))
        
        if account:
            # تبدیل موجودی به تومان برای نمایش
            account['current_balance_toman'] = account['current_balance'] / 10
            account['initial_balance_toman'] = account['initial_balance'] / 10
        
        return account
    
    def get_all_accounts(self, active_only=True):
        """دریافت تمام حساب‌ها"""
        if active_only:
            query = "SELECT * FROM Accounts WHERE is_active = 1 ORDER BY account_type, account_name"
        else:
            query = "SELECT * FROM Accounts ORDER BY account_type, account_name"
        
        accounts = self.fetch_all(query)
        
        # تبدیل موجودی‌ها به تومان برای نمایش
        for account in accounts:
            account['current_balance_toman'] = account['current_balance'] / 10
            account['initial_balance_toman'] = account['initial_balance'] / 10
        
        return accounts
    
    def delete_account(self, account_id):
        """حذف حساب (غیرفعال کردن)"""
        query = "UPDATE Accounts SET is_active = 0 WHERE id = ?"
        success = self.execute_query(query, (account_id,))
        
        if success:
            self.data_changed.emit("Accounts")
            return True, "حساب غیرفعال شد"
        return False, "خطا در غیرفعال کردن حساب"
    
    def get_financial_summary(self):
        """خلاصه مالی"""
        # دریافت اطلاعات از حساب‌ها
        accounts = AccountManager(self.db)
        total_balance = accounts.get_total_balance()
        
        # دریافت اطلاعات چک‌ها
        checks = CheckManager(self.db)
        check_stats = checks.get_check_statistics()
        
        # دریافت اطلاعات فاکتورها
        invoices = Invoice(self.db)
        
        return {
            'total_balance': total_balance,
            'check_stats': check_stats,
            # اطلاعات دیگر...
        }

    def get_total_balance(self):
        """محاسبه موجودی کل تمام حساب‌ها"""
        query = """
        SELECT SUM(current_balance) as total_balance
        FROM Accounts 
        WHERE is_active = 1
        """
        
        result = self.fetch_one(query)
        total_balance = result.get('total_balance', 0) if result else 0
        
        return {
            'total_rial': total_balance,
            'total_toman': total_balance / 10
        }
    
    def get_accounts_summary(self):
        """خلاصه وضعیت حساب‌ها"""
        query = """
        SELECT 
            account_type,
            COUNT(*) as count,
            SUM(current_balance) as total_balance
        FROM Accounts 
        WHERE is_active = 1
        GROUP BY account_type
        ORDER BY total_balance DESC
        """
        
        summary = self.fetch_all(query)
        
        # تبدیل به تومان
        for item in summary:
            item['total_balance_toman'] = item['total_balance'] / 10
        
        return summary
    
    def get_account_transactions(self, account_id, start_date=None, end_date=None):
        """دریافت تراکنش‌های یک حساب"""
        query = """
        SELECT 
            at.*,
            a1.account_name as from_account_name,
            a2.account_name as to_account_name,
            CASE 
                WHEN at.from_account_id = ? THEN 'برداشت'
                WHEN at.to_account_id = ? THEN 'واریز'
                ELSE 'نامشخص'
            END as transaction_direction
        FROM AccountingTransactions at
        LEFT JOIN Accounts a1 ON at.from_account_id = a1.id
        LEFT JOIN Accounts a2 ON at.to_account_id = a2.id
        WHERE (at.from_account_id = ? OR at.to_account_id = ?)
        """
        
        params = [account_id, account_id, account_id, account_id]
        
        if start_date:
            query += " AND DATE(at.transaction_date) >= ?"
            params.append(start_date)
        
        if end_date:
            query += " AND DATE(at.transaction_date) <= ?"
            params.append(end_date)
        
        query += " ORDER BY at.transaction_date DESC"
        
        transactions = self.fetch_all(query, params)
        
        # تبدیل تاریخ‌ها به شمسی و مبلغ به تومان
        for transaction in transactions:
            transaction['transaction_date_shamsi'] = self.db.gregorian_to_jalali(
                transaction['transaction_date']
            )
            transaction['amount_toman'] = transaction['amount'] / 10
        
        return transactions
    
    def add_transaction(self, data):
        """افزودن تراکنش حسابداری"""
        try:
            print(f"💰 در حال ثبت تراکنش...")
            
            query = """
            INSERT INTO AccountingTransactions (
                transaction_date, transaction_type, from_account_id, to_account_id,
                amount, description, employee
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """
            
            params = (
                data.get('transaction_date'),
                data.get('transaction_type'),
                data.get('from_account_id'),
                data.get('to_account_id'),
                data.get('amount', 0),
                data.get('description', ''),
                data.get('employee', 'سیستم')
            )
            
            success = self.db.execute_query(query, params)
            
            if success:
                # بروزرسانی موجودی حساب‌ها
                self._update_account_balances(
                    data.get('from_account_id'),
                    data.get('to_account_id'),
                    data.get('amount', 0),
                    data.get('transaction_type')
                )
                
                print(f"✅ تراکنش با موفقیت ثبت شد")
                self.data_changed.emit("AccountingTransactions")
                return True, "تراکنش با موفقیت ثبت شد"
            else:
                print(f"❌ خطا در ثبت تراکنش")
                return False, "خطا در ثبت تراکنش"
                
        except Exception as e:
            print(f"❌ خطا در افزودن تراکنش: {e}")
            return False, f"خطا: {str(e)}"
    
    def _update_account_balances(self, from_account_id, to_account_id, amount, transaction_type):
        """بروزرسانی موجودی حساب‌ها"""
        if transaction_type == 'انتقال' and from_account_id and to_account_id:
            # کسر از حساب مبدا
            query = "UPDATE Accounts SET current_balance = current_balance - ? WHERE id = ?"
            self.execute_query(query, (amount, from_account_id))
            
            # افزودن به حساب مقصد
            query = "UPDATE Accounts SET current_balance = current_balance + ? WHERE id = ?"
            self.execute_query(query, (amount, to_account_id))
        elif transaction_type == 'دریافت' and to_account_id:
            # افزودن به حساب
            query = "UPDATE Accounts SET current_balance = current_balance + ? WHERE id = ?"
            self.execute_query(query, (amount, to_account_id))
        elif transaction_type == 'پرداخت' and from_account_id:
            # کسر از حساب
            query = "UPDATE Accounts SET current_balance = current_balance - ? WHERE id = ?"
            self.execute_query(query, (amount, from_account_id))

class CheckManager(BaseModel):
    """مدل مدیریت چک‌ها"""
    
    def __init__(self, db_manager):
        super().__init__(db_manager)
        self.table_name = "Checks"
    
    def add_check(self, data):
        """افزودن چک جدید"""
        query = f"""
        INSERT INTO {self.table_name} (
            check_number, bank_name, branch, account_number, amount,
            issue_date, due_date, drawer, payee, status, check_type,
            related_invoice, description
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        
        params = (
            data.get('check_number'),
            data.get('bank_name'),
            data.get('branch', ''),
            data.get('account_number', ''),
            data.get('amount', 0),
            data.get('issue_date'),
            data.get('due_date'),
            data.get('drawer'),
            data.get('payee'),
            data.get('status', 'وصول نشده'),
            data.get('check_type', 'دریافتی'),
            data.get('related_invoice'),
            data.get('description', '')
        )
        
        if self.execute_query(query, params):
            self.data_changed.emit(self.table_name)
            return True
        return False

# در کلاس CheckManager در models.py، متد update_check_status را اصلاح کنید:

    def update_check_status(self, check_id, status):
        """بروزرسانی وضعیت چک - نسخه اصلاح شده"""
        try:
            # اعتبارسنجی وضعیت
            valid_statuses = ['وصول نشده', 'وصول شده', 'برگشتی', 'پاس شده', 'پاس نشده', 'بلوکه شده']
            if status not in valid_statuses:
                return False, "وضعیت نامعتبر"
            
            # دریافت اطلاعات چک قبل از تغییر
            old_check = self.get_check_by_id(check_id)
            if not old_check:
                return False, "چک مورد نظر یافت نشد"
            
            # کوئری بدون ستون‌های اضافی
            query = f"""
            UPDATE {self.table_name} 
            SET status = ?, updated_at = CURRENT_TIMESTAMP 
            WHERE id = ?
            """
            
            params = (status, check_id)
            
            success = self.execute_query(query, params)
            
            if success:
                self.data_changed.emit(self.table_name)
                return True, f"وضعیت چک به '{status}' تغییر کرد"
            return False, "خطا در بروزرسانی وضعیت"
                
        except Exception as e:
            print(f"⚠️ خطا در تغییر وضعیت چک: {e}")
            return False, f"خطای سیستم: {str(e)}"

    # همچنین متد _log_status_change را غیرفعال یا اصلاح کنید:
    def _log_status_change(self, check_id, old_status, new_status):
        """ثبت تاریخچه تغییر وضعیت - غیرفعال موقت"""
        try:
            # برای جلوگیری از خطا، فعلاً این متد را خالی می‌گذاریم
            pass
        except:
            pass

    def get_check_by_id(self, check_id):
        """دریافت چک با شناسه - نسخه ایمن"""
        query = f"SELECT * FROM {self.table_name} WHERE id = ?"
        return self.fetch_one(query, (check_id,))    
   
    def get_checks_due_soon(self, days=7):
        """دریافت چک‌های در سررسید نزدیک"""
        query = f"""
        SELECT * FROM {self.table_name} 
        WHERE status IN ('وصول نشده', 'پاس نشده')
        AND date(due_date) <= date('now', '+{days} days')
        AND date(due_date) >= date('now')
        ORDER BY due_date
        """
        return self.fetch_all(query)  

    def get_due_checks(self, days=7):
        """دریافت چک‌های در سررسید نزدیک"""
        query = f"""
        SELECT * FROM {self.table_name} 
        WHERE status IN ('وصول نشده', 'پاس نشده')
        AND date(due_date) <= date('now', '+{days} days')
        AND date(due_date) >= date('now')
        ORDER BY due_date
        """
        return self.fetch_all(query)
    
    def get_all_checks(self, check_type=None, status=None):
        """دریافت تمام چک‌ها - نسخه اصلاح شده"""
        query = f"""
        SELECT c.*,
               CASE 
                   WHEN p.first_name IS NOT NULL AND p.last_name IS NOT NULL THEN p.first_name || ' ' || p.last_name
                   WHEN p.first_name IS NOT NULL THEN p.first_name
                   WHEN p.last_name IS NOT NULL THEN p.last_name
                   WHEN p.mobile IS NOT NULL THEN p.mobile
                   ELSE 'شخص #' || c.drawer
               END as customer_name
        FROM {self.table_name} c
        LEFT JOIN Persons p ON c.drawer = p.id OR c.payee = p.id
        WHERE 1=1
        """
        
        params = []
        
        if check_type:
            query += " AND c.check_type = ?"
            params.append(check_type)
        
        if status:
            query += " AND c.status = ?"
            params.append(status)
        
        query += " ORDER BY c.due_date"
        return self.fetch_all(query, params)
    
class ReportManager(BaseModel):
    """مدل مدیریت گزارش‌ها"""
    
    def __init__(self, db_manager):
        super().__init__(db_manager)
    
    def get_daily_report(self, report_date=None):
        """گزارش روزانه"""
        if not report_date:
            report_date = QDate.currentDate().toString('yyyy-MM-dd')
        
        # گزارش پذیرش‌ها
        query = """
        SELECT COUNT(*) as total_receptions,
               SUM(CASE WHEN status = 'تعمیر شده' THEN 1 ELSE 0 END) as repaired,
               SUM(CASE WHEN status = 'تحویل داده شده' THEN 1 ELSE 0 END) as delivered,
               SUM(estimated_cost) as total_estimated
        FROM Receptions
        WHERE reception_date = ?
        """
        
        reception_report = self.fetch_one(query, (report_date,))
        
        # گزارش مالی
        query = """
        SELECT 
            SUM(CASE WHEN transaction_type = 'دریافت' THEN amount ELSE 0 END) as total_income,
            SUM(CASE WHEN transaction_type = 'پرداخت' THEN amount ELSE 0 END) as total_expense,
            COUNT(*) as total_transactions
        FROM AccountingTransactions
        WHERE date(transaction_date) = ?
        """
        
        financial_report = self.fetch_one(query, (report_date,))
        
        return {
            'date': report_date,
            'receptions': reception_report or {},
            'financial': financial_report or {}
        }
    
    def get_monthly_report(self, year=None, month=None):
        """گزارش ماهانه"""
        if not year:
            year = QDate.currentDate().year()
        if not month:
            month = QDate.currentDate().month()
        
        # گزارش پذیرش ماهانه
        query = """
        SELECT 
            COUNT(*) as total_receptions,
            SUM(CASE WHEN status = 'تعمیر شده' THEN 1 ELSE 0 END) as repaired,
            SUM(CASE WHEN status = 'تحویل داده شده' THEN 1 ELSE 0 END) as delivered,
            AVG(estimated_cost) as avg_estimated_cost
        FROM Receptions
        WHERE strftime('%Y', reception_date) = ? AND strftime('%m', reception_date) = ?
        """
        
        reception_report = self.fetch_one(query, (str(year), f"{month:02d}"))
        
        # گزارش فروش ماهانه
        query = """
        SELECT 
            COUNT(*) as total_invoices,
            SUM(total) as total_sales,
            SUM(paid_amount) as total_paid,
            AVG(total) as avg_invoice_amount
        FROM Invoices
        WHERE strftime('%Y', invoice_date) = ? AND strftime('%m', invoice_date) = ?
        AND invoice_type IN ('فروش', 'خدمات')
        """
        
        sales_report = self.fetch_one(query, (str(year), f"{month:02d}"))
        
        return {
            'year': year,
            'month': month,
            'receptions': reception_report or {},
            'sales': sales_report or {}
        }
    
    def get_partner_profit_report(self, start_date=None, end_date=None):
        """گزارش سود شرکا"""
        if not start_date:
            start_date = QDate.currentDate().addMonths(-1).toString('yyyy-MM-dd')
        if not end_date:
            end_date = QDate.currentDate().toString('yyyy-MM-dd')
        
        query = """
        SELECT 
            p.id,
            per.first_name || ' ' || per.last_name as partner_name,
            SUM(ps.share_amount) as total_profit,
            COUNT(ps.id) as total_transactions
        FROM PartnerShares ps
        JOIN Partners p ON ps.partner_id = p.id
        JOIN Persons per ON p.person_id = per.id
        WHERE date(ps.calculation_date) BETWEEN ? AND ?
        GROUP BY p.id, partner_name
        ORDER BY total_profit DESC
        """
        
        return self.fetch_all(query, (start_date, end_date))

    def get_active_partners(self):
        """دریافت شرکای فعال - با رفع خطای partner_name"""
        try:
            query = """
            SELECT 
                p.id,
                CASE 
                    WHEN per.first_name IS NOT NULL AND per.last_name IS NOT NULL THEN per.first_name || ' ' || per.last_name
                    WHEN per.first_name IS NOT NULL THEN per.first_name
                    WHEN per.last_name IS NOT NULL THEN per.last_name
                    WHEN per.mobile IS NOT NULL THEN per.mobile
                    ELSE 'شریک #' || p.id
                END as partner_name,
                p.partnership_start,
                p.profit_percentage
            FROM Partners p
            LEFT JOIN Persons per ON p.person_id = per.id
            WHERE p.active = 1
            ORDER BY partner_name
            """
            return self.fetch_all(query)
        except Exception as e:
            print(f"⚠️ خطا در دریافت شرکا: {e}")
            return []

class SettingsManager(BaseModel):
    """مدل مدیریت تنظیمات"""
    
    def __init__(self, db_manager):
        super().__init__(db_manager)
        self.table_name = "Settings"
    
    def get_settings(self):
        """دریافت تنظیمات"""
        query = f"SELECT * FROM {self.table_name} WHERE id = 1"
        return self.fetch_one(query)
    
    def update_settings(self, data):
        """بروزرسانی تنظیمات"""
        query = f"""
        UPDATE {self.table_name} SET
            app_name = ?,
            date_format = ?,
            font_name = ?,
            font_size = ?,
            bg_color = ?,
            text_color = ?,
            logo_path = ?,
            company_name = ?,
            company_address = ?,
            company_phone = ?,
            company_email = ?,
            tax_percentage = ?
        WHERE id = 1
        """
        
        params = (
            data.get('app_name', 'سیستم مدیریت تعمیرگاه لوازم خانگی'),
            data.get('date_format', 'yyyy/MM/dd'),
            data.get('font_name', 'B Nazanin'),
            data.get('font_size', 10),
            data.get('bg_color', '#FFFFFF'),
            data.get('text_color', '#000000'),
            data.get('logo_path', ''),
            data.get('company_name', ''),
            data.get('company_address', ''),
            data.get('company_phone', ''),
            data.get('company_email', ''),
            data.get('tax_percentage', 9)
        )
        
        if self.execute_query(query, params):
            self.data_changed.emit(self.table_name)
            return True
        return False

class UserManager(BaseModel):
    """مدل مدیریت کاربران"""
    
    def __init__(self, db_manager):
        super().__init__(db_manager)
        self.table_name = "Users"
    
    def authenticate(self, username, password):
        """احراز هویت کاربر"""
        query = f"""
        SELECT u.*, p.first_name || ' ' || p.last_name as full_name
        FROM {self.table_name} u
        LEFT JOIN Persons p ON u.person_id = p.id
        WHERE u.username = ? AND u.password = ? AND u.is_active = 1
        """
        
        user = self.fetch_one(query, (username, password))
        if user:
            # بروزرسانی زمان آخرین ورود
            update_query = f"""
            UPDATE {self.table_name} 
            SET last_login = CURRENT_TIMESTAMP 
            WHERE id = ?
            """
            self.execute_query(update_query, (user['id'],))
            
        return user
    
    def add_user(self, data):
        """افزودن کاربر جدید"""
        query = f"""
        INSERT INTO {self.table_name} (
            username, password, person_id, role, is_active
        ) VALUES (?, ?, ?, ?, ?)
        """
        
        params = (
            data.get('username'),
            data.get('password'),
            data.get('person_id'),
            data.get('role', 'اپراتور'),
            data.get('is_active', 1)
        )
        
        if self.execute_query(query, params):
            self.data_changed.emit(self.table_name)
            return True
        return False

class LookupValue(BaseModel):
    """مدل مدیریت مقادیر ثابت (انواع دستگاه، برندها، ...)"""
    def __init__(self, db_manager):
        super().__init__(db_manager)
        self.table_name = "LookupValues"
    
    def get_by_category(self, category, active_only=True):
        """دریافت تمام مقادیر یک دسته"""
        if active_only:
            query = f"SELECT * FROM {self.table_name} WHERE category = ? AND is_active = 1 ORDER BY display_order, value"
        else:
            query = f"SELECT * FROM {self.table_name} WHERE category = ? ORDER BY display_order, value"
        return self.fetch_all(query, (category,))
    
    def add_value(self, category, value, order=0):
        """افزودن مقدار جدید به یک دسته"""
        query = f"""
        INSERT INTO {self.table_name} (category, value, display_order) 
        VALUES (?, ?, ?)
        """
        return self.execute_query(query, (category, value, order))

class DeviceCategoryManager:
    def __init__(self, db):
        self.db = db
    
    def get_all_devices(self):
        """دریافت تمام دستگاه‌ها"""
        return self.db.fetch_all("SELECT * FROM DeviceCategories_name ORDER BY name")
    
    def get_all(self):
        """دریافت تمام دستگاه‌ها (نام دیگر برای سازگاری)"""
        return self.get_all_devices()

    def add_device(self, name, description=""):
        """افزودن دستگاه جدید"""
        query = "INSERT INTO DeviceCategories_name (name, description) VALUES (?, ?)"
        return self.db.execute_query(query, (name, description))

class BrandManager:
    def __init__(self, db):
        self.db = db
    
    def get_all_brands(self):
        """دریافت تمام برندها"""
        return self.db.fetch_all("SELECT * FROM Brands ORDER BY name")
    

    def get_all(self):
        """دریافت تمام برندها (نام دیگر برای سازگاری)"""
        return self.get_all_brands()
    

    def add_brand(self, name):
        """افزودن برند جدید"""
        query = """INSERT INTO Brands (name) 
                   VALUES (?)"""
        return self.db.execute_query(query, (name))

class ServiceFee(BaseModel):
    """مدل مدیریت اجرت‌های استاندارد"""
    def __init__(self, db_manager):
        super().__init__(db_manager)
        self.table_name = "ServiceFees"
    
    def get_all_services(self, active_only=True):
        """دریافت تمام خدمات (با امکان فیلتر فعال/غیرفعال)"""
        if active_only:
            query = f"SELECT * FROM {self.table_name} WHERE is_active = 1 ORDER BY category, service_name"
        else:
            query = f"SELECT * FROM {self.table_name} ORDER BY category, service_name"
        return self.fetch_all(query)
    
    def get_active_services(self):
        """دریافت تمام خدمات فعال"""
        return self.get_all_services(active_only=True)
    
    def get_by_category(self, category):
        """دریافت خدمات یک دسته خاص"""
        query = f"SELECT * FROM {self.table_name} WHERE category = ? AND is_active = 1 ORDER BY service_name"
        return self.fetch_all(query, (category,))
    
    def search_services(self, keyword):
        """جستجوی خدمات بر اساس نام یا کد"""
        query = f"SELECT * FROM {self.table_name} WHERE (service_name LIKE ? OR service_code LIKE ?) AND is_active = 1 ORDER BY service_name"
        return self.fetch_all(query, (f"%{keyword}%", f"%{keyword}%"))
    
    def add_service(self, data):
        """افزودن خدمت جدید"""
        query = f"""
        INSERT INTO {self.table_name} 
        (service_code, service_name, category, default_fee, estimated_hours, difficulty_level, description, is_active)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """
        params = (
            data.get('service_code', ''),
            data.get('service_name', ''),
            data.get('category', 'عمومی'),
            data.get('default_fee', 0),
            data.get('estimated_hours', 1.0),
            data.get('difficulty_level', 1),
            data.get('description', ''),
            data.get('is_active', 1)
        )
        return self.execute_query(query, params)
    
    def update_service(self, service_id, data):
        """ویرایش خدمت موجود"""
        query = f"""
        UPDATE {self.table_name} SET
            service_name = ?,
            category = ?,
            default_fee = ?,
            estimated_hours = ?,
            difficulty_level = ?,
            description = ?,
            is_active = ?
        WHERE id = ?
        """
        params = (
            data.get('service_name', ''),
            data.get('category', 'عمومی'),
            data.get('default_fee', 0),
            data.get('estimated_hours', 1.0),
            data.get('difficulty_level', 1),
            data.get('description', ''),
            data.get('is_active', 1),
            service_id
        )
        return self.execute_query(query, params)
    
    def delete_service(self, service_id):
        """حذف خدمت"""
        query = f"DELETE FROM {self.table_name} WHERE id = ?"
        return self.execute_query(query, (service_id,))
    
    def get_service_by_code(self, service_code):
        """دریافت خدمت با کد"""
        query = f"SELECT * FROM {self.table_name} WHERE service_code = ?"
        return self.fetch_one(query, (service_code,))

class DeviceCategoryName(BaseModel):
    """مدل مدیریت دسته‌بندی‌های دستگاه‌ها"""
    def __init__(self, db_manager):
        super().__init__(db_manager)
        self.table_name = "DeviceCategories_name"
    
    def get_all(self):
        """دریافت تمام دسته‌بندی‌ها"""
        query = f"SELECT * FROM {self.table_name} ORDER BY name"
        return self.fetch_all(query)
    
    def get_by_id(self, category_id):
        """دریافت دسته‌بندی با شناسه"""
        query = f"SELECT * FROM {self.table_name} WHERE id = ?"
        return self.fetch_one(query, (category_id,))
    
    def add(self, name, description=""):
        """افزودن دسته‌بندی جدید"""
        query = f"INSERT INTO {self.table_name} (name, description) VALUES (?, ?)"
        return self.execute_query(query, (name, description))
    
    def update(self, category_id, name, description=""):
        """ویرایش دسته‌بندی"""
        query = f"UPDATE {self.table_name} SET name = ?, description = ? WHERE id = ?"
        return self.execute_query(query, (name, description, category_id))
    
    def delete(self, category_id):
        """حذف دسته‌بندی"""
        query = f"DELETE FROM {self.table_name} WHERE id = ?"
        return self.execute_query(query, (category_id,))

class DeviceWithCategory(BaseModel):
    """مدل مدیریت دستگاه‌ها با دسته‌بندی و برند"""
    def __init__(self, db_manager):
        super().__init__(db_manager)
        self.table_name = "Devices"
    
    def get_all_with_details(self):
        """دریافت تمام دستگاه‌ها با اطلاعات دسته‌بندی و برند"""
        query = """
        SELECT 
            d.id,
            d.model,
            d.serial_number,
            d.production_year,
            d.description,
            dc.name as device_type_name,
            dc.id as device_type_id,
            b.name as brand_name,
            b.id as brand_id
        FROM Devices d
        LEFT JOIN DeviceCategories_name dc ON d.device_type_id = dc.id
        LEFT JOIN Brands b ON d.brand_id = b.id
        ORDER BY dc.name, b.name, d.model
        """
        return self.fetch_all(query)
    
    def add_device(self, device_type_id, brand_id, model, serial_number=None, production_year=None, description=""):
        """افزودن دستگاه جدید"""
        query = """
        INSERT INTO Devices (device_type_id, brand_id, model, serial_number, production_year, description)
        VALUES (?, ?, ?, ?, ?, ?)
        """
        return self.execute_query(query, (device_type_id, brand_id, model, serial_number, production_year, description))

# کلاس اصلی برای مدیریت تمام مدل‌ها
# در انتهای فایل models.py، کلاس DataManager را اینگونه اصلاح کنید:

# models.py - بخش‌های اصلاح شده

# در انتهای فایل models.py، کلاس DataManager را اینگونه اصلاح کنید:

# در انتهای کلاس DataManager در models.py، تغییرات زیر را اعمال کنید:

class DataManager(QObject):
    """مدیریت متمرکز تمام مدل‌های داده - نسخه سریع"""
    
    def __init__(self, db_path="data/repair_shop.db"):  
        super().__init__()
        self.db = DatabaseManager(db_path)
        self.db.initialize_database()
        
        # 🔴 فقط مهاجرت‌های ضروری را اجرا کن
        self.run_quick_migrations()

        # ایجاد نمونه‌های مدل
        self.person = Person(self.db)
        self.device = Device(self.db)
        self.reception = Reception(self.db)
        self.part = Part(self.db)
        self.warehouse = WarehouseManager(self.db)
        self.invoice = Invoice(self.db)
        self.accounting = AccountManager(self.db)
        self.check_manager = CheckManager(self.db)
        self.report = ReportManager(self.db)
        self.settings = SettingsManager(self.db)
        self.user = UserManager(self.db)
        self.lookup = LookupValue(self.db)
        self.device_category = DeviceCategoryManager(self.db)  
        self.brand = BrandManager(self.db)  
        self.repair = Repair(self.db)
        self.service_fee = ServiceFee(self.db)
        self.device_category_name = DeviceCategoryName(self.db)  
        self.device_with_category = DeviceWithCategory(self.db)
        
        # ایجاد AccountManager
        self.account_manager = AccountManager(self.db)
        self.calculator = FinancialCalculator(self)
        
        # ایجاد TransactionManager
        try:
            from modules.accounting import TransactionManager
            self.transaction_manager = TransactionManager(self)
        except ImportError as e:
            print(f"⚠️ خطا در بارگذاری TransactionManager: {e}")
            self.transaction_manager = None

        # ایجاد InvoiceManager
        try:
            # از ماژول invoice_manager که در کد اولیه وجود دارد استفاده می‌کنیم
            from modules.accounting.invoice_manager import InvoiceManager
            self.invoice_manager = InvoiceManager(self)
        except ImportError as e:
            print(f"⚠️ خطا در بارگذاری InvoiceManager: {e}")
            # اگر ماژول invoice_manager جداگانه موجود نیست، از خود کلاس Invoice استفاده می‌کنیم
            self.invoice_manager = self.invoice

        # اتصال سیگنال‌ها
        self._connect_signals()
        
        print("✅ DataManager با موفقیت ایجاد شد")
    
    def _connect_signals(self):
        """اتصال سیگنال‌های تغییر داده"""
        models = [
            self.person, self.device, self.reception, self.part,
            self.invoice, self.check_manager, self.settings, self.user,
            self.device_category_name, self.device_with_category,
            self.account_manager, self.repair, self.service_fee,
            self.transaction_manager, self.invoice_manager
        ]
        
        for model in models:
            if model and hasattr(model, 'data_changed'):
                model.data_changed.connect(self._on_data_changed)
    
    def _on_data_changed(self, table_name):
        """هندلر تغییر داده"""
        print(f"📊 داده‌های جدول {table_name} تغییر کرد")
    
    def run_quick_migrations(self):
        """اجرای مهاجرت‌های سریع"""
        print("🔧 اجرای مهاجرت‌های سریع دیتابیس...")
        
        # فقط چند مهاجرت ضروری
        try:
            # بررسی و اضافه کردن ستون‌های گمشده
            self.db.connect()
            
            # 1. Checks table - اضافه کردن ستون check_date اگر وجود ندارد
            self.db.cursor.execute("PRAGMA table_info(Checks)")
            check_columns = [col[1] for col in self.db.cursor.fetchall()]
            
            if 'check_date' not in check_columns:
                print("➕ افزودن check_date به Checks")
                self.db.cursor.execute("ALTER TABLE Checks ADD COLUMN check_date DATE")
                # مقداردهی اولیه با due_date
                self.db.cursor.execute("UPDATE Checks SET check_date = due_date WHERE check_date IS NULL")
            
            # 2. Invoices table - بررسی ستون invoice_date
            self.db.cursor.execute("PRAGMA table_info(Invoices)")
            invoice_columns = [col[1] for col in self.db.cursor.fetchall()]
            if 'invoice_date' not in invoice_columns:
                print("➕ افزودن invoice_date به Invoices")
                self.db.cursor.execute("ALTER TABLE Invoices ADD COLUMN invoice_date DATE")
            
            self.db.connection.commit()
            print("✅ مهاجرت‌های سریع انجام شد")
            
        except Exception as e:
            print(f"⚠️ خطا در مهاجرت‌های سریع: {e}")
        finally:
            if self.db.connection:
                self.db.connection.close()

# تست مدل‌ها
if __name__ == "__main__":
    print("تست مدل‌های داده...")
    
    # ایجاد مدیر داده
    data_manager = DataManager()
    
    # تست تنظیمات
    settings = data_manager.settings.get_settings()
    print(f"تنظیمات برنامه: {settings['app_name']}")
    
    # تست کاربران
    user = data_manager.user.authenticate('admin', 'admin123')
    if user:
        print(f"ورود موفق: {user.get('full_name', user['username'])}")
    else:
        print("ورود ناموفق")
    
    # تست دریافت اشخاص
    persons = data_manager.person.get_all_persons()
    print(f"تعداد اشخاص در دیتابیس: {len(persons)}")

    print("تست مدل‌ها با موفقیت انجام شد!")