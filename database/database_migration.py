# database_migration.py
"""
مهاجرت پایگاه داده برای رفع خطاهای موجود
"""

class DatabaseMigration:
    def __init__(self, db_manager):
        self.db = db_manager
    
    def run_migrations(self):
        """اجرای تمام مهاجرت‌های لازم"""
        print("🔄 شروع مهاجرت پایگاه داده...")
        
        migrations = [
            self.migrate_partners_table,
            self.migrate_checks_table,
            self.migrate_invoices_table,
            self.migrate_persons_table
        ]
        
        for migration in migrations:
            try:
                if migration():
                    print(f"✅ {migration.__name__} با موفقیت اجرا شد")
                else:
                    print(f"⚠️ {migration.__name__} اجرا نشد")
            except Exception as e:
                print(f"❌ خطا در {migration.__name__}: {e}")
        
        print("🎯 مهاجرت‌ها تکمیل شد")
    
    def migrate_partners_table(self):
        """مهاجرت جدول شرکا"""
        try:
            # بررسی وجود ستون‌های لازم
            self.db.connect()
            self.db.cursor.execute("PRAGMA table_info(Partners)")
            columns = [col[1] for col in self.db.cursor.fetchall()]
            
            if 'active' not in columns:
                print("🔧 افزودن ستون active به جدول Partners")
                self.db.cursor.execute("ALTER TABLE Partners ADD COLUMN active BOOLEAN DEFAULT 1")
                self.db.connection.commit()
                return True
            
            return False
        except Exception as e:
            print(f"⚠️ خطا در مهاجرت جدول شرکا: {e}")
            return False
        finally:
            if self.db.connection:
                self.db.connection.close()
    
    def migrate_checks_table(self):
        """مهاجرت جدول چک‌ها"""
        try:
            self.db.connect()
            self.db.cursor.execute("PRAGMA table_info(Checks)")
            columns = [col[1] for col in self.db.cursor.fetchall()]
            
            # بررسی وجود ستون issue_date
            if 'issue_date' not in columns:
                print("🔧 افزودن ستون issue_date به جدول Checks")
                self.db.cursor.execute("ALTER TABLE Checks ADD COLUMN issue_date DATE")
                self.db.connection.commit()
                
                # پر کردن مقادیر پیش‌فرض
                self.db.cursor.execute("UPDATE Checks SET issue_date = due_date WHERE issue_date IS NULL")
                self.db.connection.commit()
                return True
            
            return False
        except Exception as e:
            print(f"⚠️ خطا در مهاجرت جدول چک‌ها: {e}")
            return False
        finally:
            if self.db.connection:
                self.db.connection.close()
    
    def migrate_invoices_table(self):
        """مهاجرت جدول فاکتورها"""
        try:
            self.db.connect()
            self.db.cursor.execute("PRAGMA table_info(Invoices)")
            columns = [col[1] for col in self.db.cursor.fetchall()]
            
            # بررسی وجود ستون invoice_date
            if 'invoice_date' not in columns:
                print("🔧 افزودن ستون invoice_date به جدول Invoices")
                self.db.cursor.execute("ALTER TABLE Invoices ADD COLUMN invoice_date DATE DEFAULT CURRENT_DATE")
                self.db.connection.commit()
                
                # پر کردن مقادیر پیش‌فرض
                self.db.cursor.execute("UPDATE Invoices SET invoice_date = created_at WHERE invoice_date IS NULL")
                self.db.connection.commit()
                return True
            
            return False
        except Exception as e:
            print(f"⚠️ خطا در مهاجرت جدول فاکتورها: {e}")
            return False
        finally:
            if self.db.connection:
                self.db.connection.close()
    
    def migrate_persons_table(self):
        """مهاجرت جدول اشخاص"""
        try:
            self.db.connect()
            self.db.cursor.execute("PRAGMA table_info(Persons)")
            columns = [col[1] for col in self.db.cursor.fetchall()]
            
            # بررسی وجود ستون first_name و last_name
            if 'first_name' not in columns:
                print("🔧 افزودن ستون first_name به جدول Persons")
                self.db.cursor.execute("ALTER TABLE Persons ADD COLUMN first_name TEXT")
                self.db.connection.commit()
            
            if 'last_name' not in columns:
                print("🔧 افزودن ستون last_name به جدول Persons")
                self.db.cursor.execute("ALTER TABLE Persons ADD COLUMN last_name TEXT")
                self.db.connection.commit()
                
                # بررسی وجود ستون‌های قدیمی name و family
                self.db.cursor.execute("PRAGMA table_info(Persons)")
                columns = [col[1] for col in self.db.cursor.fetchall()]
                
                if 'name' in columns and 'family' in columns:
                    # انتقال داده‌ها از ستون‌های قدیمی به جدید
                    self.db.cursor.execute("""
                        UPDATE Persons 
                        SET first_name = COALESCE(name, 'نامشخص'),
                            last_name = COALESCE(family, 'نامشخص')
                        WHERE first_name IS NULL OR last_name IS NULL
                    """)
                    self.db.connection.commit()
                else:
                    # پر کردن مقادیر پیش‌فرض
                    self.db.cursor.execute("""
                        UPDATE Persons 
                        SET first_name = COALESCE(first_name, 'نام'),
                            last_name = COALESCE(last_name, 'خانوادگی')
                        WHERE first_name IS NULL OR last_name IS NULL
                    """)
                    self.db.connection.commit()
                return True
            
            return False
        except Exception as e:
            print(f"⚠️ خطا در مهاجرت جدول اشخاص: {e}")
            return False
        finally:
            if self.db.connection:
                self.db.connection.close()