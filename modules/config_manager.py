# modules/config_manager.py
import json
import os
from PySide6.QtCore import QObject, Signal, QTimer, Qt
from datetime import datetime

class ConfigManager(QObject):
    """
    مدیر متمرکز تمام تنظیمات سیستم
    Singleton Pattern - فقط یک نمونه در کل برنامه
    """
    _instance = None
    config_updated = Signal(str, dict)  # سیگنال به‌روزرسانی تنظیمات
    user_permission_changed = Signal(str, list)  # سیگنال تغییر دسترسی کاربر
    display_settings_changed = Signal(dict)


    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self, data_manager):
        if not hasattr(self, 'initialized'):
            super().__init__()
            self.data_manager = data_manager
            self.config_cache = {}  # کش تنظیمات در حافظه
            self.user_permissions = {}  # دسترسی‌های کاربران
            self.initialized = True
            
            # بارگذاری اولیه
            self.load_all_configs()
            self.setup_auto_save()
    
    def load_all_configs(self):
        """بارگذاری تمام تنظیمات از دیتابیس"""
        print("⚙️ در حال بارگذاری تنظیمات سیستم...")
        
        # ۱. تنظیمات عمومی
        self.load_general_config()
        
        # ۲. تنظیمات امنیتی
        self.load_security_config()
        
        # ۳. تنظیمات مالی
        self.load_financial_config()
        
        # ۴. تنظیمات انبار
        self.load_inventory_config()
        
        # ۵. تنظیمات نمایش
        self.load_display_config()
        
        print("✅ تنظیمات سیستم بارگذاری شد")
    
    def load_general_config(self):
        """بارگذاری تنظیمات عمومی"""
        try:
            query = "SELECT * FROM Settings WHERE id = 1"
            result = self.data_manager.db.fetch_one(query)
            
            if result:
                self.config_cache['general'] = {
                    'app_name': result.get('app_name', 'سیستم مدیریت تعمیرگاه'),
                    'company_name': result.get('company_name', ''),
                    'company_address': result.get('company_address', ''),
                    'company_phone': result.get('company_phone', ''),
                    'company_email': result.get('company_email', ''),
                    'logo_path': result.get('logo_path', ''),
                    'date_format': result.get('date_format', 'شمسی'),
                    'language': result.get('language', 'فارسی'),
                    'theme': result.get('theme', 'dark'),
                    'auto_backup': bool(result.get('auto_backup', 1)),
                    'backup_path': result.get('backup_path', 'data/backup/')
                }
            else:
                self.set_default_general_config()
                
        except Exception as e:
            print(f"⚠️ خطا در بارگذاری تنظیمات عمومی: {e}")
            self.set_default_general_config()
    
    def load_security_config(self):
        """بارگذاری تنظیمات امنیتی"""
        try:
            query = "SELECT * FROM SecuritySettings WHERE id = 1"
            result = self.data_manager.db.fetch_one(query)
            
            if result:
                self.config_cache['security'] = {
                    'max_login_attempts': result.get('max_login_attempts', 3),
                    'session_timeout': result.get('session_timeout_minutes', 30),
                    'password_min_length': result.get('min_password_length', 8),
                    'password_require_upper': bool(result.get('require_uppercase', 1)),
                    'password_require_lower': bool(result.get('require_lowercase', 1)),
                    'password_require_number': bool(result.get('require_numbers', 1)),
                    'password_require_special': bool(result.get('require_special', 0)),
                    'auto_logout': bool(result.get('auto_logout', 1)),
                    'inactivity_timeout': result.get('inactivity_minutes', 10),
                    'audit_log': bool(result.get('audit_log', 1)),
                    
                    # نقش‌های کاربری و دسترسی‌ها
                    'role_permissions': {
                        'مدیر': ['all'],
                        'حسابدار': ['view_accounting', 'edit_accounting', 'view_reports'],
                        'انباردار': ['view_inventory', 'edit_inventory', 'view_reports'],
                        'اپراتور': ['view_receptions', 'edit_receptions', 'view_customers'],
                        'مشاهده‌گر': ['view_dashboard', 'view_reports']
                    }
                }
            else:
                self.set_default_security_config()
                
        except Exception as e:
            print(f"⚠️ خطا در بارگذاری تنظیمات امنیتی: {e}")
            self.set_default_security_config()

    def load_financial_config(self):
        """بارگذاری تنظیمات مالی - نسخه اصلاح شده"""
        try:
            # تلاش برای بارگذاری از دیتابیس
            query1 = "SELECT tax_percentage FROM Settings WHERE id = 1"
            result1 = self.data_manager.db.fetch_one(query1)
            
            settings = {
                'tax_rate': 9.0,
                'currency': 'تومان',
                'default_discount': 0.0,
                'max_credit_amount': 10000000,
                'check_warning_days': 3
            }
            
            if result1:
                settings['tax_rate'] = float(result1.get('tax_percentage', 9.0))
            
            # بررسی وجود جدول FinancialSettings
            try:
                query2 = "SELECT * FROM FinancialSettings WHERE id = 1"
                result2 = self.data_manager.db.fetch_one(query2)
                if result2:
                    settings.update({
                        'default_discount': float(result2.get('default_discount', 0.0)),
                        'max_credit_amount': float(result2.get('max_credit_amount', 10000000)),
                        'check_warning_days': result2.get('check_warning_days', 3)
                    })
            except:
                pass  # اگر جدول وجود نداشت، مشکلی نیست
            
            self.config_cache['financial'] = settings
            
        except Exception as e:
            print(f"⚠️ خطا در بارگذاری تنظیمات مالی: {e}")
            self.set_default_financial_config()
    
    def load_inventory_config(self):
        """بارگذاری تنظیمات انبار"""
        try:
            self.config_cache['inventory'] = {
                'min_stock_default': 5,
                'max_stock_default': 100,
                'low_stock_warning': 10,
                'auto_reorder': False,
                'reorder_threshold': 15,
                'default_warehouse': 'اصلی'
            }
            
            # در آینده می‌توان از جدول InventorySettings بارگذاری کرد
                
        except Exception as e:
            print(f"⚠️ خطا در بارگذاری تنظیمات انبار: {e}")
            self.set_default_inventory_config()
    
    def load_display_config(self):
        """بارگذاری تنظیمات نمایش"""
        try:
            query = """
            SELECT font_name, font_size, text_color, bg_color 
            FROM Settings WHERE id = 1
            """
            result = self.data_manager.db.fetch_one(query)
            
            if result:
                self.config_cache['display'] = {
                    'font_family': result.get('font_name', 'B Nazanin'),
                    'font_size': result.get('font_size', 11),
                    'text_color': result.get('text_color', '#ffffff'),
                    'bg_color': result.get('bg_color', '#000000'),
                    'rtl': True,
                    'number_format': 'fa'  # فارسی یا انگلیسی
                }
            else:
                self.set_default_display_config()
                
        except Exception as e:
            print(f"⚠️ خطا در بارگذاری تنظیمات نمایش: {e}")
            self.set_default_display_config()
    
    def set_default_general_config(self):
        """تنظیمات پیش‌فرض عمومی"""
        self.config_cache['general'] = {
            'app_name': 'سیستم مدیریت تعمیرگاه شروین',
            'company_name': 'تعمیرگاه لوازم خانگی شروین',
            'company_address': '',
            'company_phone': '',
            'company_email': '',
            'logo_path': '',
            'date_format': 'شمسی',
            'language': 'فارسی',
            'theme': 'dark',
            'auto_backup': True,
            'backup_path': 'data/backup/'
        }
    
    def set_default_security_config(self):
        """تنظیمات پیش‌فرض امنیتی"""
        self.config_cache['security'] = {
            'max_login_attempts': 3,
            'session_timeout': 30,
            'password_min_length': 8,
            'password_require_upper': True,
            'password_require_lower': True,
            'password_require_number': True,
            'password_require_special': False,
            'auto_logout': True,
            'inactivity_timeout': 10,
            'audit_log': True,
            'role_permissions': {
                'مدیر': ['all'],
                'حسابدار': ['view_accounting', 'edit_accounting', 'view_reports'],
                'انباردار': ['view_inventory', 'edit_inventory', 'view_reports'],
                'اپراتور': ['view_receptions', 'edit_receptions', 'view_customers'],
                'مشاهده‌گر': ['view_dashboard', 'view_reports']
            }
        }
    
    def set_default_financial_config(self):
        """تنظیمات پیش‌فرض مالی"""
        self.config_cache['financial'] = {
            'tax_rate': 9.0,
            'currency': 'تومان',
            'default_discount': 0.0,
            'max_credit_amount': 10000000,
            'check_warning_days': 3
        }
    
    def set_default_inventory_config(self):
        """تنظیمات پیش‌فرض انبار"""
        self.config_cache['inventory'] = {
            'min_stock_default': 5,
            'max_stock_default': 100,
            'low_stock_warning': 10,
            'auto_reorder': False,
            'reorder_threshold': 15,
            'default_warehouse': 'اصلی'
        }
    
    def set_default_display_config(self):
        """تنظیمات پیش‌فرض نمایش"""
        self.config_cache['display'] = {
            'font_family': 'B Nazanin',
            'font_size': 11,
            'text_color': '#ffffff',
            'bg_color': '#000000',
            'rtl': True,
            'number_format': 'fa'
        }

    def get(self, category, key=None, default=None):
        """
        دریافت مقدار تنظیمات - نسخه نهایی اصلاح شده
        """
        try:
            # دیباگ: چاپ ورودی‌ها برای ردیابی
            key_type_str = type(key).__name__ if key is not None else 'None'
            print(f"🔍 دیباگ get: category='{category}', type={type(category).__name__}, key={key}, type(key)={key_type_str}")
            
            # اگر category دیکشنری است (اشتباه رایج)
            if isinstance(category, dict):
                print("⚠️ هشدار: category یک دیکشنری است!")
                return default
            
            # اگر category رشته نیست
            if not isinstance(category, str):
                print("⚠️ هشدار: category باید رشته باشد")
                return default
            
            # اگر key یک دیکشنری است، احتمالاً می‌خواهند default را ارسال کنند
            if isinstance(key, dict):
                print(f"⚠️ هشدار: key یک دیکشنری است! احتمالاً می‌خواهید: get('{category}', default={key})")
                # در این حالت، key را نادیده می‌گیریم و از default استفاده می‌کنیم
                return self.get(category, None, key)
            
            # بررسی وجود دسته
            if category not in self.config_cache:
                return default
            
            # اگر key مشخص نشده، کل دسته را برگردان
            if key is None:
                result = self.config_cache.get(category)
                return result if result is not None else default
            
            # اطمینان از اینکه key رشته است
            if not isinstance(key, str):
                try:
                    key = str(key)
                except:
                    return default
            
            # دریافت مقدار خاص
            category_dict = self.config_cache.get(category, {})
            if not isinstance(category_dict, dict):
                return default
            
            return category_dict.get(key, default)
            
        except Exception as e:
            print(f"⚠️ خطا در دریافت تنظیمات: {e}")
            return default

    def set(self, category, key, value, save_to_db=True):
        """تنظیم مقدار"""
        try:
            if category not in self.config_cache:
                self.config_cache[category] = {}
            
            old_value = self.config_cache[category].get(key)
            self.config_cache[category][key] = value
            
            # ارسال سیگنال
            self.config_updated.emit(f"{category}.{key}", {
                'old': old_value,
                'new': value,
                'category': category,
                'key': key
            })
            
            # اگر تنظیمات نمایش تغییر کرد، سیگنال ویژه ارسال کن
            if category == 'display':
                self.display_settings_changed.emit(self.config_cache['display'])
            
            # ذخیره در دیتابیس
            if save_to_db:
                self.save_to_database(category, {key: value})
            
            return True
            
        except Exception as e:
            print(f"⚠️ خطا در تنظیم مقدار: {e}")
            return False

    def save_to_database(self, category, data):
        """ذخیره تنظیمات در دیتابیس"""
        try:
            if category == 'general':
                # به‌روزرسانی جدول Settings
                set_clause = ", ".join([f"{k} = ?" for k in data.keys()])
                values = list(data.values())
                values.append(1)  # برای WHERE id = 1
                
                query = f"UPDATE Settings SET {set_clause} WHERE id = ?"
                return self.data_manager.db.execute_query(query, values)
            
            elif category == 'security':
                # به‌روزرسانی جدول SecuritySettings
                set_clause = ", ".join([f"{k} = ?" for k in data.keys()])
                values = list(data.values())
                values.append(1)
                
                query = f"UPDATE SecuritySettings SET {set_clause} WHERE id = ?"
                return self.data_manager.db.execute_query(query, values)
            
            # TODO: سایر جداول
            
            return True
            
        except Exception as e:
            print(f"⚠️ خطا در ذخیره تنظیمات در دیتابیس: {e}")
            return False
    
    def setup_auto_save(self):
        """تنظیم ذخیره خودکار هر ۵ دقیقه - فقط اگر در محیط GUI هستیم"""
        try:
            # بررسی اینکه آیا QApplication اجرا شده یا نه
            from PySide6.QtWidgets import QApplication
            app = QApplication.instance()
            
            if app:
                self.auto_save_timer = QTimer()
                self.auto_save_timer.timeout.connect(self.auto_save_configs)
                self.auto_save_timer.start(300000)  # 5 دقیقه
                print("⏰ تایمر ذخیره خودکار فعال شد")
            else:
                print("⚠️ تایمر ذخیره خودکار غیرفعال (بدون QApplication)")
                
        except Exception as e:
            print(f"⚠️ خطا در تنظیم تایمر ذخیره خودکار: {e}")
    
    def auto_save_configs(self):
        """ذخیره خودکار تنظیمات"""
        try:
            for category, configs in self.config_cache.items():
                self.save_to_database(category, configs)
            print("💾 تنظیمات به صورت خودکار ذخیره شد")
        except Exception as e:
            print(f"⚠️ خطا در ذخیره خودکار: {e}")
    
    def check_permission(self, user_role, permission):
        """بررسی دسترسی کاربر"""
        try:
            role_perms = self.get('security', 'role_permissions', {})
            
            if user_role not in role_perms:
                return False
            
            user_permissions = role_perms[user_role]
            
            # اگر 'all' دارد، همه مجوزها را بده
            if 'all' in user_permissions:
                return True
            
            return permission in user_permissions
            
        except Exception as e:
            print(f"⚠️ خطا در بررسی دسترسی: {e}")
            return False
    
    def get_user_permissions(self, user_role):
        """دریافت تمام مجوزهای یک نقش"""
        try:
            role_perms = self.get('security', 'role_permissions', {})
            return role_perms.get(user_role, [])
        except:
            return []


    def validate_password(self, password):
        """اعتبارسنجی رمز عبور بر اساس تنظیمات"""
        try:
            security_config = self.get('security', {})
            
            # بررسی طول
            if len(password) < security_config.get('password_min_length', 8):
                return False, f"رمز عبور باید حداقل {security_config['password_min_length']} کاراکتر باشد"
            
            # بررسی حروف بزرگ
            if security_config.get('password_require_upper', True):
                if not any(c.isupper() for c in password):
                    return False, "رمز عبور باید حداقل یک حرف بزرگ داشته باشد"
            
            # بررسی حروف کوچک
            if security_config.get('password_require_lower', True):
                if not any(c.islower() for c in password):
                    return False, "رمز عبور باید حداقل یک حرف کوچک داشته باشد"
            
            # بررسی اعداد
            if security_config.get('password_require_number', True):
                if not any(c.isdigit() for c in password):
                    return False, "رمز عبور باید حداقل یک عدد داشته باشد"
            
            # بررسی کاراکترهای خاص
            if security_config.get('password_require_special', False):
                special_chars = "!@#$%^&*()_+-=[]{}|;:,.<>?"
                if not any(c in special_chars for c in password):
                    return False, "رمز عبور باید حداقل یک کاراکتر خاص داشته باشد"
            
            return True, "رمز عبور معتبر است"
            
        except Exception as e:
            print(f"⚠️ خطا در اعتبارسنجی رمز عبور: {e}")
            return False, "خطا در اعتبارسنجی رمز عبور"
    
    def log_security_event(self, user_id, action, details=""):
        """ثبت رویداد امنیتی"""
        try:
            if not self.get('security', 'audit_log', True):
                return
            
            query = """
            INSERT INTO Logs (user_id, action, details, ip_address, created_at)
            VALUES (?, ?, ?, ?, ?)
            """
            
            # در حالت واقعی، IP کاربر را دریافت کنید
            ip_address = "127.0.0.1"
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            return self.data_manager.db.execute_query(
                query, (user_id, action, details, ip_address, timestamp)
            )
            
        except Exception as e:
            print(f"⚠️ خطا در ثبت رویداد امنیتی: {e}")
            return False
    
    def apply_display_settings(self, widget):
        """اعمال تنظیمات نمایش روی یک ویجت - نسخه اصلاح شده"""
        try:
            # دریافت ایمن تنظیمات نمایش
            display_config = self.get('display')
            
            # اگر None برگرداند، از پیش‌فرض استفاده کن
            if display_config is None:
                display_config = {}
            
            # استخراج مقادیر با پیش‌فرض
            font_family = display_config.get('font_family', 'B Nazanin')
            font_size = display_config.get('font_size', 11)
            text_color = display_config.get('text_color', '#ffffff')
            bg_color = display_config.get('bg_color', '#000000')
            rtl = display_config.get('rtl', True)
            
            style = f"""
            QWidget {{
                font-family: '{font_family}';
                font-size: {font_size}pt;
                color: {text_color};
                background-color: {bg_color};
            }}
            """
            
            if widget:
                widget.setStyleSheet(style)
                
                # راست‌چین
                if rtl:
                    widget.setLayoutDirection(Qt.RightToLeft)
                
            return True
                
        except Exception as e:
            print(f"⚠️ خطا در اعمال تنظیمات نمایش: {e}")
            return False
    



