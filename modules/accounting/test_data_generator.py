# modules/accounting/test_data_generator.py
"""
اسکریپت ایجاد داده‌های آزمایشی برای تست گزارش‌های مالی
"""

import jdatetime
from datetime import datetime, timedelta
import random
from typing import Dict, List


class TestDataGenerator:
    """کلاس تولید داده‌های آزمایشی"""
    
    def __init__(self, data_manager):
        """
        مقداردهی اولیه
        
        Args:
            data_manager: شیء مدیریت داده‌ها
        """
        self.data_manager = data_manager
    
    def generate_test_data(self, days_back: int = 90):
        """
        تولید داده‌های آزمایشی برای 90 روز گذشته
        
        Args:
            days_back: تعداد روزهای گذشته برای تولید داده
        """
        print("🚀 شروع تولید داده‌های آزمایشی...")
        
        try:
            # 1. ایجاد حساب‌های آزمایشی
            self._create_test_accounts()
            
            # 2. ایجاد اشخاص آزمایشی
            self._create_test_persons()
            
            # 3. ایجاد شرکای آزمایشی
            self._create_test_partners()
            
            # 4. ایجاد تراکنش‌های آزمایشی
            self._create_test_transactions(days_back)
            
            # 5. ایجاد فاکتورهای آزمایشی
            self._create_test_invoices(days_back)
            
            # 6. ایجاد چک‌های آزمایشی
            self._create_test_checks(days_back)
            
            # 7. ایجاد موجودی آزمایشی
            self._create_test_inventory()
            
            # 8. ایجاد سهام شرکا
            self._create_test_partner_shares(days_back)
            
            print("✅ داده‌های آزمایشی با موفقیت ایجاد شدند!")
            return True
            
        except Exception as e:
            print(f"❌ خطا در تولید داده‌های آزمایشی: {e}")
            return False
    
    def _create_test_accounts(self):
        """ایجاد حساب‌های بانکی آزمایشی"""
        accounts = [
            {
                'account_name': 'صندوق فروشگاه',
                'account_type': 'نقدی',
                'account_number': 'CASH001',
                'bank_name': 'صندوق',
                'current_balance': 50000000,
                'opening_balance': 50000000,
                'description': 'صندوق اصلی فروشگاه'
            },
            {
                'account_name': 'حساب جاری ملی',
                'account_type': 'جاری',
                'account_number': '6037991234567890',
                'bank_name': 'ملی',
                'current_balance': 150000000,
                'opening_balance': 150000000,
                'description': 'حساب اصلی شرکت'
            },
            {
                'account_name': 'حساب پس‌انداز',
                'account_type': 'پس‌انداز',
                'account_number': '6274121234567890',
                'bank_name': 'صادرات',
                'current_balance': 80000000,
                'opening_balance': 80000000,
                'description': 'حساب پس‌انداز شرکت'
            },
            {
                'account_name': 'کارت اعتباری',
                'account_type': 'اعتباری',
                'account_number': '6395991234567890',
                'bank_name': 'ملت',
                'current_balance': -20000000,
                'opening_balance': 0,
                'description': 'کارت اعتباری خرید قطعات'
            }
        ]
        
        for account in accounts:
            self.data_manager.add_account(
                account_name=account['account_name'],
                account_type=account['account_type'],
                account_number=account['account_number'],
                bank_name=account['bank_name'],
                current_balance=account['current_balance'],
                opening_balance=account['opening_balance'],
                description=account['description']
            )
        
        print(f"✅ {len(accounts)} حساب بانکی ایجاد شد")
    
    def _create_test_persons(self):
        """ایجاد اشخاص آزمایشی (مشتریان، تامین‌کنندگان)"""
        persons = [
            # مشتریان
            {
                'first_name': 'احمد',
                'last_name': 'محمدی',
                'national_code': '1234567890',
                'phone_number': '09121234567',
                'email': 'ahmad@gmail.com',
                'address': 'تهران، خیابان ولیعصر',
                'person_type': 'مشتری',
                'is_customer': 1,
                'is_supplier': 0
            },
            {
                'first_name': 'فاطمه',
                'last_name': 'کریمی',
                'national_code': '2345678901',
                'phone_number': '09129876543',
                'email': 'fatemeh@gmail.com',
                'address': 'مشهد، بلوار وکیل‌آباد',
                'person_type': 'مشتری',
                'is_customer': 1,
                'is_supplier': 0
            },
            {
                'first_name': 'رضا',
                'last_name': 'حسینی',
                'national_code': '3456789012',
                'phone_number': '09131234567',
                'email': 'reza@gmail.com',
                'address': 'اصفهان، خیابان چهارباغ',
                'person_type': 'مشتری',
                'is_customer': 1,
                'is_supplier': 0
            },
            
            # تامین‌کنندگان
            {
                'first_name': 'شرکت',
                'last_name': 'تامین قطعات البرز',
                'national_code': '4567890123',
                'phone_number': '02112345678',
                'email': 'info@alborzparts.com',
                'address': 'تهران، شهرک صنعتی عباس‌آباد',
                'person_type': 'تامین کننده',
                'is_customer': 0,
                'is_supplier': 1
            },
            {
                'first_name': 'شرکت',
                'last_name': 'لوازم یدکی تهران',
                'national_code': '5678901234',
                'phone_number': '02187654321',
                'email': 'info@tehranparts.com',
                'address': 'تهران، خیابان جمهوری',
                'person_type': 'تامین کننده',
                'is_customer': 0,
                'is_supplier': 1
            }
        ]
        
        for person in persons:
            self.data_manager.add_person(
                first_name=person['first_name'],
                last_name=person['last_name'],
                national_code=person['national_code'],
                phone_number=person['phone_number'],
                email=person['email'],
                address=person['address'],
                person_type=person['person_type'],
                is_customer=person['is_customer'],
                is_supplier=person['is_supplier']
            )
        
        print(f"✅ {len(persons)} شخص ایجاد شد")
    
    def _create_test_partners(self):
        """ایجاد شرکای آزمایشی"""
        partners = [
            {
                'person_id': 1,  # احمد محمدی
                'capital': 200000000,
                'profit_percentage': 40,
                'start_date': '1403/01/01',
                'active': 1,
                'notes': 'شریک اصلی'
            },
            {
                'person_id': 2,  # فاطمه کریمی
                'capital': 150000000,
                'profit_percentage': 30,
                'start_date': '1403/01/01',
                'active': 1,
                'notes': 'شریک دوم'
            },
            {
                'person_id': 3,  # رضا حسینی
                'capital': 100000000,
                'profit_percentage': 20,
                'start_date': '1403/01/01',
                'active': 1,
                'notes': 'شریک سوم'
            }
        ]
        
        for partner in partners:
            self.data_manager.add_partner(
                person_id=partner['person_id'],
                capital=partner['capital'],
                profit_percentage=partner['profit_percentage'],
                start_date=partner['start_date'],
                active=partner['active'],
                notes=partner['notes']
            )
        
        print(f"✅ {len(partners)} شریک ایجاد شد")
    
    def _create_test_transactions(self, days_back: int):
        """ایجاد تراکنش‌های آزمایشی"""
        transaction_types = ['دریافت', 'پرداخت', 'درآمد', 'هزینه']
        descriptions = [
            'فروش موبایل', 'فروش لپ‌تاپ', 'دریافت از مشتری', 'فروش قطعات',
            'خرید قطعات', 'پرداخت اجاره', 'هزینه برق', 'حقوق پرسنل',
            'هزینه اینترنت', 'خرید لوازم اداری'
        ]
        
        # تراکنش‌های درآمدی
        for i in range(days_back * 3):  # 3 تراکنش در روز
            days_ago = random.randint(0, days_back)
            transaction_date = (jdatetime.datetime.now() - 
                              jdatetime.timedelta(days=days_ago))
            
            amount = random.randint(500000, 5000000)
            transaction_type = random.choice(['دریافت', 'درآمد'])
            description = random.choice(['فروش موبایل', 'فروش لپ‌تاپ', 'فروش قطعات'])
            
            gregorian_date = self._jalali_to_gregorian(
                transaction_date.strftime("%Y/%m/%d")
            )
            
            self.data_manager.add_transaction(
                transaction_date=gregorian_date,
                amount=amount,
                transaction_type=transaction_type,
                account_id=random.randint(1, 3),
                description=description,
                reference_number=f"TRX-{transaction_date.strftime('%Y%m%d')}-{i:03d}",
                created_by='سیستم'
            )
        
        # تراکنش‌های هزینه
        for i in range(days_back * 2):  # 2 تراکنش در روز
            days_ago = random.randint(0, days_back)
            transaction_date = (jdatetime.datetime.now() - 
                              jdatetime.timedelta(days=days_ago))
            
            amount = random.randint(100000, 3000000)
            transaction_type = random.choice(['پرداخت', 'هزینه'])
            description = random.choice(['خرید قطعات', 'پرداخت اجاره', 'هزینه برق', 'حقوق پرسنل'])
            
            gregorian_date = self._jalali_to_gregorian(
                transaction_date.strftime("%Y/%m/%d")
            )
            
            self.data_manager.add_transaction(
                transaction_date=gregorian_date,
                amount=amount,
                transaction_type=transaction_type,
                account_id=random.randint(1, 4),
                description=description,
                reference_number=f"EXP-{transaction_date.strftime('%Y%m%d')}-{i:03d}",
                created_by='سیستم'
            )
        
        print(f"✅ {days_back * 5} تراکنش آزمایشی ایجاد شد")
    
    def _create_test_invoices(self, days_back: int):
        """ایجاد فاکتورهای آزمایشی"""
        # دریافت شناسه مشتریان
        customers = self.data_manager.db.fetch_all(
            "SELECT id FROM Persons WHERE is_customer = 1"
        )
        
        invoice_types = ['فروش', 'خدمات', 'قطعات']
        payment_methods = ['نقدی', 'چک', 'کارت']
        
        for i in range(days_back * 2):  # 2 فاکتور در روز
            days_ago = random.randint(0, days_back)
            invoice_date = (jdatetime.datetime.now() - 
                          jdatetime.timedelta(days=days_ago))
            
            customer_id = random.choice(customers)['id']
            invoice_type = random.choice(invoice_types)
            payment_method = random.choice(payment_methods)
            total = random.randint(1000000, 10000000)
            paid_amount = total if payment_method == 'نقدی' else total * random.uniform(0.3, 0.8)
            
            gregorian_date = self._jalali_to_gregorian(
                invoice_date.strftime("%Y/%m/%d")
            )
            
            # افزودن فاکتور
            self.data_manager.add_invoice(
                invoice_number=f"INV-{invoice_date.strftime('%Y%m%d')}-{i:03d}",
                invoice_date=gregorian_date,
                customer_id=customer_id,
                invoice_type=invoice_type,
                total=total,
                paid_amount=paid_amount,
                remaining_amount=total - paid_amount,
                payment_method=payment_method,
                payment_status='نقدی' if paid_amount == total else 'قسطی',
                due_date=self._jalali_to_gregorian(
                    (invoice_date + jdatetime.timedelta(days=30)).strftime("%Y/%m/%d")
                ) if paid_amount < total else None,
                notes='فاکتور آزمایشی'
            )
        
        print(f"✅ {days_back * 2} فاکتور آزمایشی ایجاد شد")
    
    def _create_test_checks(self, days_back: int):
        """ایجاد چک‌های آزمایشی"""
        check_types = ['دریافتی', 'پرداختی']
        banks = ['ملی', 'ملت', 'صادرات', 'تجارت', 'سامان']
        statuses = ['در جریان', 'وصول شده', 'پاس شده', 'برگشتی']
        
        for i in range(days_back):  # 1 چک در روز
            days_ago = random.randint(0, days_back)
            issue_date = (jdatetime.datetime.now() - 
                         jdatetime.timedelta(days=days_ago))
            due_date = issue_date + jdatetime.timedelta(days=random.randint(30, 90))
            
            check_type = random.choice(check_types)
            amount = random.randint(1000000, 5000000)
            status = random.choice(statuses)
            
            issue_gregorian = self._jalali_to_gregorian(
                issue_date.strftime("%Y/%m/%d")
            )
            due_gregorian = self._jalali_to_gregorian(
                due_date.strftime("%Y/%m/%d")
            )
            
            self.data_manager.add_check(
                check_number=f"{random.randint(100000, 999999)}",
                amount=amount,
                issue_date=issue_gregorian,
                due_date=due_gregorian,
                check_type=check_type,
                bank_name=random.choice(banks),
                account_id=random.randint(1, 3) if check_type == 'دریافتی' else random.randint(1, 4),
                status=status,
                description='چک آزمایشی',
                payer_receiver='احمد محمدی' if check_type == 'دریافتی' else 'شرکت البرز',
                is_post_dated=1 if due_date > jdatetime.datetime.now() else 0
            )
        
        print(f"✅ {days_back} چک آزمایشی ایجاد شد")
    
    def _create_test_inventory(self):
        """ایجاد موجودی آزمایشی"""
        inventory_items = [
            {
                'item_name': 'باتری موبایل سامسونگ',
                'item_code': 'BAT-SAM-001',
                'category': 'قطعات موبایل',
                'unit': 'عدد',
                'quantity': 50,
                'unit_cost': 150000,
                'min_quantity': 10,
                'supplier_id': 4  # شرکت تامین قطعات البرز
            },
            {
                'item_name': 'نمایشگر آیفون 13',
                'item_code': 'SCR-IP13-001',
                'category': 'قطعات موبایل',
                'unit': 'عدد',
                'quantity': 25,
                'unit_cost': 800000,
                'min_quantity': 5,
                'supplier_id': 4
            },
            {
                'item_name': 'کیس گیمینگ',
                'item_code': 'CASE-GAM-001',
                'category': 'لوازم جانبی',
                'unit': 'عدد',
                'quantity': 100,
                'unit_cost': 250000,
                'min_quantity': 20,
                'supplier_id': 5  # شرکت لوازم یدکی تهران
            },
            {
                'item_name': 'شارژر سریع',
                'item_code': 'CHG-FST-001',
                'category': 'لوازم جانبی',
                'unit': 'عدد',
                'quantity': 75,
                'unit_cost': 180000,
                'min_quantity': 15,
                'supplier_id': 5
            }
        ]
        
        for item in inventory_items:
            self.data_manager.add_inventory_item(
                item_name=item['item_name'],
                item_code=item['item_code'],
                category=item['category'],
                unit=item['unit'],
                quantity=item['quantity'],
                unit_cost=item['unit_cost'],
                min_quantity=item['min_quantity'],
                supplier_id=item['supplier_id'],
                description='آیتم آزمایشی'
            )
        
        print(f"✅ {len(inventory_items)} آیتم موجودی ایجاد شد")
    
    def _create_test_partner_shares(self, days_back: int):
        """ایجاد سود شرکا"""
        partners = self.data_manager.db.fetch_all(
            "SELECT id, profit_percentage FROM Partners WHERE active = 1"
        )
        
        # محاسبه سود کل ماهانه (فرضی)
        monthly_profits = []
        for month in range(1, 13):
            total_profit = random.randint(20000000, 50000000)
            monthly_profits.append({
                'month': month,
                'total_profit': total_profit
            })
        
        for month_data in monthly_profits:
            month = month_data['month']
            total_profit = month_data['total_profit']
            
            calculation_date = jdatetime.date(1403, month, 15)  # روز 15 هر ماه
            gregorian_date = self._jalali_to_gregorian(
                calculation_date.strftime("%Y/%m/%d")
            )
            
            for partner in partners:
                partner_id = partner['id']
                percentage = partner['profit_percentage']
                share_amount = (total_profit * percentage) / 100
                
                self.data_manager.db.execute("""
                    INSERT INTO PartnerShares (
                        partner_id, 
                        calculation_date, 
                        share_amount,
                        period_start_date,
                        period_end_date,
                        created_at
                    ) VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    partner_id,
                    gregorian_date,
                    share_amount,
                    self._jalali_to_gregorian(jdatetime.date(1403, month, 1).strftime("%Y/%m/%d")),
                    self._jalali_to_gregorian(jdatetime.date(1403, month, 29 if month == 12 else 30).strftime("%Y/%m/%d")),
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                ))
        
        print(f"✅ سود 12 ماهه برای شرکا ایجاد شد")
    
    def _jalali_to_gregorian(self, jalali_date: str) -> str:
        """
        تبدیل تاریخ شمسی به میلادی
        """
        try:
            year, month, day = map(int, jalali_date.split('/'))
            gregorian_date = jdatetime.JalaliToGregorian(year, month, day)
            return f"{gregorian_date.gyear}-{gregorian_date.gmonth:02d}-{gregorian_date.gday:02d}"
        except:
            # اگر تبدیل نشد، تاریخ امروز برگردان
            return datetime.now().strftime("%Y-%m-%d")
    
    def clear_test_data(self):
        """
        پاک کردن تمام داده‌های آزمایشی
        """
        try:
            tables = [
                'PartnerShares',
                'InventoryItems',
                'Checks',
                'InvoiceItems',
                'Invoices',
                'AccountingTransactions',
                'Partners',
                'Persons',
                'Accounts'
            ]
            
            for table in tables:
                self.data_manager.db.execute(f"DELETE FROM {table}")
                print(f"🧹 داده‌های جدول {table} پاک شد")
            
            print("✅ تمام داده‌های آزمایشی پاک شدند")
            return True
            
        except Exception as e:
            print(f"❌ خطا در پاک کردن داده‌های آزمایشی: {e}")
            return False