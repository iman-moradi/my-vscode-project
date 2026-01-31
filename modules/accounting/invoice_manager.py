# modules/accounting/invoice_manager.py

"""
مدیریت فاکتورها و صورتحساب‌ها - نسخه سازگار با سیستم موجود
"""

from PySide6.QtCore import QObject, Signal
import jdatetime
from datetime import datetime

class InvoiceManager(QObject):
    """مدیریت کامل فاکتورها - نسخه ساده‌تر"""
    
    data_changed = Signal(str)
    
    def __init__(self, data_manager):
        super().__init__()
        self.data_manager = data_manager
        self.db = data_manager.db
    
    def generate_invoice_number(self, invoice_type='خدمات'):
        """تولید شماره فاکتور خودکار"""
        today = jdatetime.datetime.now()
        year = today.year
        month = today.month
        
        # شماره‌گذاری بر اساس نوع فاکتور
        prefix = {
            'فروش': 'F',
            'خدمات': 'S', 
            'خرید': 'P',
            'مرجوعی': 'R'
        }.get(invoice_type, 'INV')
        
        # شماره سریال ماهانه
        query = """
        SELECT COUNT(*) as count 
        FROM Invoices 
        WHERE invoice_type = ? 
        AND strftime('%Y', invoice_date) = ? 
        AND strftime('%m', invoice_date) = ?
        """
        
        month_str = f"{month:02d}"
        result = self.db.fetch_one(query, (invoice_type, str(year), month_str))
        count = result['count'] + 1 if result else 1
        
        return f"{prefix}-{year}{month_str}{count:04d}"
    
    def create_invoice(self, invoice_data, items):
        """ایجاد فاکتور جدید"""
        try:
            # اعتبارسنجی
            if not items:
                return False, "فاکتور باید حداقل یک آیتم داشته باشد"
            
            # تولید شماره فاکتور
            invoice_number = self.generate_invoice_number(invoice_data.get('invoice_type', 'خدمات'))
            
            # محاسبات مالی
            subtotal = sum(item.get('total_price', 0) for item in items)
            discount = float(invoice_data.get('discount', 0)) * 10  # تبدیل به ریال
            tax_rate = float(invoice_data.get('tax_rate', 9))  # درصد مالیات
            tax = (subtotal - discount) * (tax_rate / 100)
            total = subtotal - discount + tax
            
            # مبالغ پرداخت شده
            paid_amount = float(invoice_data.get('paid_amount', 0)) * 10
            remaining_amount = total - paid_amount
            
            # وضعیت پرداخت
            if paid_amount >= total:
                payment_status = 'پرداخت شده'
            elif paid_amount > 0:
                payment_status = 'پرداخت جزئی'
            else:
                payment_status = 'پرداخت نشده'
            
            # تبدیل تاریخ‌ها به میلادی برای دیتابیس
            invoice_date_gregorian = self.db.jalali_to_gregorian(invoice_data.get('invoice_date'))
            
            # تاریخ سررسید (اگر داده نشده، 30 روز بعد)
            due_date = invoice_data.get('due_date')
            if not due_date:
                due_date = jdatetime.datetime.strptime(
                    invoice_data.get('invoice_date'), "%Y/%m/%d"
                ) + jdatetime.timedelta(days=30)
                due_date = due_date.strftime("%Y/%m/%d")
            
            due_date_gregorian = self.db.jalali_to_gregorian(due_date)
            
            # ایجاد فاکتور
            query = """
            INSERT INTO Invoices (
                invoice_number, invoice_type, customer_id, reception_id, invoice_date,
                due_date, subtotal, discount, tax, total, paid_amount, remaining_amount,
                payment_status, payment_method, description, outsourced_to, outsourced_cost
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            
            params = (
                invoice_number,
                invoice_data.get('invoice_type', 'خدمات'),
                invoice_data.get('customer_id'),
                invoice_data.get('reception_id'),
                invoice_date_gregorian,
                due_date_gregorian,
                subtotal,
                discount,
                tax,
                total,
                paid_amount,
                remaining_amount,
                payment_status,
                invoice_data.get('payment_method', 'نقدی'),
                invoice_data.get('description', ''),
                invoice_data.get('outsourced_to'),
                float(invoice_data.get('outsourced_cost', 0)) * 10
            )
            
            success = self.db.execute_query(query, params)
            
            if not success:
                return False, "خطا در ایجاد فاکتور"
            
            # دریافت شناسه فاکتور
            invoice_id = self.db.fetch_one("SELECT last_insert_rowid() as id")['id']
            
            # افزودن آیتم‌های فاکتور
            for item in items:
                item_success, item_message = self.add_invoice_item(invoice_id, item)
                if not item_success:
                    return False, f"خطا در افزودن آیتم: {item_message}"
            
            self.data_changed.emit("Invoices")
            return True, f"فاکتور {invoice_number} با موفقیت ایجاد شد"
            
        except Exception as e:
            return False, f"خطا: {str(e)}"
    
    def add_invoice_item(self, invoice_id, item_data):
        """افزودن آیتم به فاکتور"""
        try:
            # محاسبه قیمت کل
            quantity = item_data.get('quantity', 1)
            unit_price = float(item_data.get('unit_price', 0)) * 10  # ریال
            total_price = quantity * unit_price
            
            query = """
            INSERT INTO InvoiceItems (
                invoice_id, item_type, item_id, item_name, quantity,
                unit_price, total_price, description, partner_percentage
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            
            params = (
                invoice_id,
                item_data.get('item_type', 'قطعه'),
                item_data.get('item_id'),
                item_data.get('item_name', ''),
                quantity,
                unit_price,
                total_price,
                item_data.get('description', ''),
                float(item_data.get('partner_percentage', 0))
            )
            
            success = self.db.execute_query(query, params)
            
            return success, "آیتم با موفقیت افزوده شد" if success else "خطا در افزودن آیتم"
            
        except Exception as e:
            return False, f"خطا: {str(e)}"
    
    def get_all_invoices(self, status=None, start_date=None, end_date=None):
        """دریافت تمام فاکتورها"""
        query = """
        SELECT 
            i.*,
            p.first_name || ' ' || p.last_name as customer_name,
            p.mobile as customer_mobile
        FROM Invoices i
        LEFT JOIN Persons p ON i.customer_id = p.id
        WHERE 1=1
        """
        
        params = []
        
        if status:
            query += " AND i.payment_status = ?"
            params.append(status)
        
        if start_date:
            query += " AND DATE(i.invoice_date) >= ?"
            params.append(start_date)
        
        if end_date:
            query += " AND DATE(i.invoice_date) <= ?"
            params.append(end_date)
        
        query += " ORDER BY i.invoice_date DESC"
        
        invoices = self.db.fetch_all(query, params)
        
        # تبدیل تاریخ‌ها و مبالغ
        for invoice in invoices:
            invoice['invoice_date_shamsi'] = self.db.gregorian_to_jalali(invoice['invoice_date'])
            invoice['due_date_shamsi'] = self.db.gregorian_to_jalali(invoice['due_date'])
            
            # تبدیل مبالغ به تومان
            for field in ['subtotal', 'discount', 'tax', 'total', 'paid_amount', 'remaining_amount']:
                invoice[f'{field}_toman'] = invoice[field] / 10 if invoice[field] else 0
        
        return invoices
    
    def get_invoice_by_id(self, invoice_id):
        """دریافت فاکتور با شناسه"""
        query = """
        SELECT 
            i.*,
            p.first_name || ' ' || p.last_name as customer_name,
            p.mobile, p.phone, p.address,
            r.reception_number, r.problem_description
        FROM Invoices i
        LEFT JOIN Persons p ON i.customer_id = p.id
        LEFT JOIN Receptions r ON i.reception_id = r.id
        WHERE i.id = ?
        """
        
        invoice = self.db.fetch_one(query, (invoice_id,))
        
        if invoice:
            invoice['invoice_date_shamsi'] = self.db.gregorian_to_jalali(invoice['invoice_date'])
            invoice['due_date_shamsi'] = self.db.gregorian_to_jalali(invoice['due_date'])
            
            # تبدیل مبالغ به تومان
            for field in ['subtotal', 'discount', 'tax', 'total', 'paid_amount', 'remaining_amount']:
                invoice[f'{field}_toman'] = invoice[field] / 10 if invoice[field] else 0
            
            # دریافت آیتم‌های فاکتور
            invoice['items'] = self.get_invoice_items(invoice_id)
        
        return invoice
    
    def get_invoice_items(self, invoice_id):
        """دریافت آیتم‌های یک فاکتور"""
        query = """
        SELECT 
            ii.*
        FROM InvoiceItems ii
        WHERE ii.invoice_id = ?
        ORDER BY ii.id
        """
        
        items = self.db.fetch_all(query, (invoice_id,))
        
        # تبدیل مبالغ به تومان
        for item in items:
            item['unit_price_toman'] = item['unit_price'] / 10 if item['unit_price'] else 0
            item['total_price_toman'] = item['total_price'] / 10 if item['total_price'] else 0
        
        return items
    
    def update_invoice_payment(self, invoice_id, payment_data):
        """بروزرسانی وضعیت پرداخت فاکتور"""
        try:
            invoice = self.get_invoice_by_id(invoice_id)
            if not invoice:
                return False, "فاکتور یافت نشد"
            
            paid_amount = float(payment_data.get('amount', 0)) * 10
            payment_method = payment_data.get('payment_method', 'نقدی')
            
            # محاسبه مبالغ جدید
            new_paid_amount = invoice['paid_amount'] + paid_amount
            new_remaining_amount = invoice['total'] - new_paid_amount
            
            # تعیین وضعیت پرداخت
            if new_paid_amount >= invoice['total']:
                new_payment_status = 'پرداخت شده'
            elif new_paid_amount > 0:
                new_payment_status = 'پرداخت جزئی'
            else:
                new_payment_status = 'پرداخت نشده'
            
            query = """
            UPDATE Invoices SET
                paid_amount = ?,
                remaining_amount = ?,
                payment_status = ?,
                payment_method = ?
            WHERE id = ?
            """
            
            params = (
                new_paid_amount,
                new_remaining_amount,
                new_payment_status,
                payment_method,
                invoice_id
            )
            
            success = self.db.execute_query(query, params)
            
            if success:
                self.data_changed.emit("Invoices")
                return True, "پرداخت با موفقیت ثبت شد"
            
            return False, "خطا در ثبت پرداخت"
            
        except Exception as e:
            return False, f"خطا: {str(e)}"
    
    def get_unpaid_invoices(self):
        """دریافت فاکتورهای پرداخت نشده"""
        query = """
        SELECT 
            i.*,
            p.first_name || ' ' || p.last_name as customer_name
        FROM Invoices i
        LEFT JOIN Persons p ON i.customer_id = p.id
        WHERE i.remaining_amount > 0
        ORDER BY i.due_date
        """
        
        invoices = self.db.fetch_all(query)
        
        # تبدیل تاریخ‌ها و مبالغ
        for invoice in invoices:
            invoice['invoice_date_shamsi'] = self.db.gregorian_to_jalali(invoice['invoice_date'])
            invoice['due_date_shamsi'] = self.db.gregorian_to_jalali(invoice['due_date'])
            
            # تبدیل مبالغ به تومان
            for field in ['total', 'paid_amount', 'remaining_amount']:
                invoice[f'{field}_toman'] = invoice[field] / 10 if invoice[field] else 0
        
        return invoices