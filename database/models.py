# models.py
from PySide6.QtCore import QObject, Signal, QDate, QDateTime
from datetime import datetime, date
from .database import DatabaseManager
import sqlite3


import json

class BaseModel(QObject):
    data_changed = Signal(str)
    
    def __init__(self, db_manager):
        super().__init__()
        self.db = db_manager
        self.table_name = self.__class__.__name__.lower()
        
    def execute_query(self, query, params=()):
        try:
            self.db.connect()
            self.db.cursor.execute(query, params)
            self.db.connection.commit()
            return True
        except Exception as e:
            print(f"خطا در اجرای کوئری: {str(e)}")
            return False
        finally:
            if self.db.connection:
                self.db.connection.close()
    
    def fetch_all(self, query, params=()):
        try:
            self.db.connect()
            self.db.cursor.execute(query, params)
            rows = self.db.cursor.fetchall()
            
            # تبدیل ردیف‌ها به دیکشنری
            result = []
            for row in rows:
                if hasattr(row, 'keys') and callable(row.keys):
                    # اگر row از نوع sqlite3.Row باشد
                    result.append(dict(row))
                else:
                    # اگر tuple باشد
                    column_names = [description[0] for description in self.db.cursor.description]
                    row_dict = {}
                    for i, column in enumerate(column_names):
                        row_dict[column] = row[i]
                    result.append(row_dict)
            return result
        except Exception as e:
            print(f"خطا در دریافت داده: {str(e)}")
            return []
        finally:
            if self.db.connection:
                self.db.connection.close()
    
    def fetch_one(self, query, params=()):
        try:
            self.db.connect()
            self.db.cursor.execute(query, params)
            row = self.db.cursor.fetchone()
            
            if row:
                if hasattr(row, 'keys') and callable(row.keys):
                    # اگر row از نوع sqlite3.Row باشد
                    return dict(row)
                else:
                    # اگر tuple باشد
                    column_names = [description[0] for description in self.db.cursor.description]
                    row_dict = {}
                    for i, column in enumerate(column_names):
                        row_dict[column] = row[i]
                    return row_dict
            return None
        except Exception as e:
            print(f"خطا در دریافت داده: {str(e)}")
            return None
        finally:
            if self.db.connection:
                self.db.connection.close()
    
    def fetch_one(self, query, params=()):
        try:
            self.db.connect()
            self.db.cursor.execute(query, params)
            row = self.db.cursor.fetchone()
            
            if row:
                # دریافت نام ستون‌ها
                column_names = [description[0] for description in self.db.cursor.description]
                # تبدیل ردیف به دیکشنری
                row_dict = {}
                for i, column in enumerate(column_names):
                    row_dict[column] = row[i]
                return row_dict
            return None
            
        except sqlite3.Error as e:
            print(f"خطای SQLite در fetch_one: {e}")
            return None
        except Exception as e:
            print(f"خطای عمومی در fetch_one: {e}")
            return None
        finally:
            if self.db.connection:
                self.db.connection.close()


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
        """افزودن تعمیر جدید"""
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
        
        if self.execute_query(query, params):
            self.data_changed.emit(self.table_name)
            return True
        return False
    
    def update_repair(self, repair_id, data):
        """ویرایش تعمیر"""
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
        
        return self.execute_query(query, params)

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
        """دریافت قطعات با موجودی کم"""
        query = """
        SELECT p.*, 
               COALESCE(np.quantity, 0) as new_quantity,
               COALESCE(up.quantity, 0) as used_quantity
        FROM Parts p
        LEFT JOIN (
            SELECT part_id, SUM(quantity) as quantity 
            FROM NewPartsWarehouse 
            WHERE status = 'موجود' 
            GROUP BY part_id
        ) np ON p.id = np.part_id
        LEFT JOIN (
            SELECT part_id, SUM(quantity) as quantity 
            FROM UsedPartsWarehouse 
            WHERE status = 'موجود' 
            GROUP BY part_id
        ) up ON p.id = up.part_id
        WHERE (COALESCE(np.quantity, 0) + COALESCE(up.quantity, 0)) < p.min_stock
        """
        return self.fetch_all(query)

class WarehouseManager(BaseModel):
    """مدل مدیریت انبارهای مختلف"""
    
    def __init__(self, db_manager):
        super().__init__(db_manager)
        
    def add_to_warehouse(self, warehouse_type, data):
        """افزودن به انبار (نو یا دست دوم)"""
        table_map = {
            'قطعات نو': 'NewPartsWarehouse',
            'قطعات دست دوم': 'UsedPartsWarehouse',
            'لوازم نو': 'NewAppliancesWarehouse',
            'لوازم دست دوم': 'UsedAppliancesWarehouse'
        }
        
        table_name = table_map.get(warehouse_type)
        if not table_name:
            return False
        
        if warehouse_type in ['قطعات نو', 'قطعات دست دوم']:
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
                data.get('purchase_date', QDate.currentDate().toString('yyyy-MM-dd')),
                data.get('batch_number', ''),
                data.get('location', ''),
                data.get('expiration_date'),
                data.get('status', 'موجود')
            )
        else:  # لوازم خانگی
            query = f"""
            INSERT INTO {table_name} (
                device_id, quantity, purchase_price, sale_price, supplier_id,
                purchase_date, warranty_months, location, status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            
            params = (
                data.get('device_id'),
                data.get('quantity', 0),
                data.get('purchase_price', 0),
                data.get('sale_price', 0),
                data.get('supplier_id'),
                data.get('purchase_date', QDate.currentDate().toString('yyyy-MM-dd')),
                data.get('warranty_months', 12),
                data.get('location', ''),
                data.get('status', 'موجود')
            )
        
        if self.execute_query(query, params):
            self.data_changed.emit(table_name)
            # ثبت تراکنش انبار
            self._add_inventory_transaction(warehouse_type, 'خرید', data)
            return True
        return False
    
    def _add_inventory_transaction(self, warehouse_type, transaction_type, data):
        """ثبت تراکنش انبار"""
        query = """
        INSERT INTO InventoryTransactions (
            transaction_type, warehouse_type, item_id, quantity, unit_price,
            total_price, transaction_date, related_document, description, employee
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        
        # محاسبه قیمت کل
        quantity = data.get('quantity', 0)
        unit_price = data.get('purchase_price', 0)
        total_price = quantity * unit_price
        
        params = (
            transaction_type,
            warehouse_type,
            data.get('part_id') or data.get('device_id'),
            quantity,
            unit_price,
            total_price,
            QDateTime.currentDateTime().toString('yyyy-MM-dd HH:mm:ss'),
            data.get('batch_number', ''),
            f"{transaction_type} {warehouse_type}",
            'سیستم'
        )
        
        self.execute_query(query, params)
    
    def get_warehouse_stock(self, warehouse_type, item_id=None):
        """دریافت موجودی انبار"""
        table_map = {
            'قطعات نو': 'NewPartsWarehouse',
            'قطعات دست دوم': 'UsedPartsWarehouse',
            'لوازم نو': 'NewAppliancesWarehouse',
            'لوازم دست دوم': 'UsedAppliancesWarehouse'
        }
        
        table_name = table_map.get(warehouse_type)
        if not table_name:
            return []
        
        if item_id:
            query = f"""
            SELECT * FROM {table_name} 
            WHERE {'part_id' if 'Parts' in table_name else 'device_id'} = ? 
            AND status = 'موجود'
            ORDER BY purchase_date
            """
            return self.fetch_all(query, (item_id,))
        else:
            query = f"""
            SELECT * FROM {table_name} 
            WHERE status = 'موجود'
            ORDER BY purchase_date
            """
            return self.fetch_all(query)

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

class AccountingManager(BaseModel):
    """مدل مدیریت حسابداری"""
    
    def __init__(self, db_manager):
        super().__init__(db_manager)
    
    def add_account(self, data):
        """افزودن حساب جدید"""
        query = """
        INSERT INTO Accounts (
            account_number, account_name, account_type, bank_name,
            initial_balance, current_balance, owner_name, description
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """
        
        params = (
            data.get('account_number'),
            data.get('account_name'),
            data.get('account_type', 'جاری'),
            data.get('bank_name', ''),
            data.get('initial_balance', 0),
            data.get('initial_balance', 0),  # current_balance = initial_balance
            data.get('owner_name', ''),
            data.get('description', '')
        )
        
        if self.execute_query(query, params):
            self.data_changed.emit("Accounts")
            return True
        return False
    
    def add_transaction(self, data):
        """افزودن تراکنش حسابداری"""
        query = """
        INSERT INTO AccountingTransactions (
            transaction_date, transaction_type, from_account_id, to_account_id,
            amount, description, reference_id, reference_type, employee
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        
        params = (
            data.get('transaction_date', QDateTime.currentDateTime().toString('yyyy-MM-dd HH:mm:ss')),
            data.get('transaction_type'),
            data.get('from_account_id'),
            data.get('to_account_id'),
            data.get('amount', 0),
            data.get('description', ''),
            data.get('reference_id'),
            data.get('reference_type'),
            data.get('employee', 'سیستم')
        )
        
        if self.execute_query(query, params):
            # بروزرسانی موجودی حساب‌ها
            self._update_account_balances(
                data.get('from_account_id'),
                data.get('to_account_id'),
                data.get('amount', 0),
                data.get('transaction_type')
            )
            
            self.data_changed.emit("AccountingTransactions")
            return True
        return False
    
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
    
    def update_check_status(self, check_id, status):
        """بروزرسانی وضعیت چک"""
        query = f"""
        UPDATE {self.table_name} 
        SET status = ?, updated_at = CURRENT_TIMESTAMP 
        WHERE id = ?
        """
        
        if self.execute_query(query, (status, check_id)):
            self.data_changed.emit(self.table_name)
            return True
        return False
    
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
    
    
# کلاس اصلی برای مدیریت تمام مدل‌ها
# در انتهای فایل models.py، کلاس DataManager را اینگونه اصلاح کنید:

class DataManager(QObject):
    """مدیریت متمرکز تمام مدل‌های داده"""
    
    def __init__(self, db_path="data/repair_shop.db"):  # 🔴 تغییر: اضافه کردن پارامتر db_path
        super().__init__()
        self.db = DatabaseManager(db_path)  # 🔴 استفاده از مسیر داده شده
        self.db.initialize_database()
        
        # ایجاد نمونه‌های مدل
        self.person = Person(self.db)
        self.device = Device(self.db)
        self.reception = Reception(self.db)
        self.part = Part(self.db)
        self.warehouse = WarehouseManager(self.db)
        self.invoice = Invoice(self.db)
        self.accounting = AccountingManager(self.db)
        self.check_manager = CheckManager(self.db)
        self.report = ReportManager(self.db)
        self.settings = SettingsManager(self.db)
        self.user = UserManager(self.db)
        self.lookup = LookupValue(self.db)
        self.repair = Repair(self.db)
        self.service_fee = ServiceFee(self.db)

        
        # اتصال سیگنال‌ها
        self._connect_signals()
    
    def _connect_signals(self):
        """اتصال سیگنال‌های تغییر داده"""
        models = [
            self.person, self.device, self.reception, self.part,
            self.invoice, self.check_manager, self.settings, self.user
        ]
        
        for model in models:
            model.data_changed.connect(self._on_data_changed)
    
    def _on_data_changed(self, table_name):
        """هنگام تغییر داده"""
        print(f"داده‌های جدول {table_name} تغییر کرد")
        # می‌توانید این سیگنال را به UI منتقل کنید

    def get_lookup_list(self, category):
        """دریافت لیست ساده از مقادیر یک دسته (برای پر کردن ComboBox)"""
        items = self.lookup.get_by_category(category)
        # تبدیل لیست دیکشنری به لیست رشته
        return [item['value'] for item in items] if items else []

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