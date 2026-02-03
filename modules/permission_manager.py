# modules/permission_manager.py
from PySide6.QtWidgets import QMessageBox
from functools import wraps

class PermissionManager:
    """مدیریت دسترسی‌ها و مجوزهای کاربران"""
    
    def __init__(self, config_manager):
        self.config_manager = config_manager
        self.current_user = None
        self.current_role = None
    
    def set_current_user(self, user_id, username, role):
        """تنظیم کاربر جاری"""
        self.current_user = {
            'id': user_id,
            'username': username,
            'role': role
        }
        self.current_role = role
    
    def has_permission(self, permission):
        """بررسی آیا کاربر مجوز دارد"""
        if not self.current_role:
            return False
        
        return self.config_manager.check_permission(self.current_role, permission)
    
    def get_all_permissions(self):
        """دریافت تمام مجوزهای کاربر جاری"""
        if not self.current_role:
            return []
        
        return self.config_manager.get_user_permissions(self.current_role)
    
    def check_and_show(self, permission, widget=None):
        """
        بررسی مجوز و نمایش پیام در صورت عدم دسترسی
        بازگشت: True اگر مجوز دارد، False اگر ندارد
        """
        if self.has_permission(permission):
            return True
        
        if widget:
            QMessageBox.warning(
                widget,
                "دسترسی محدود",
                f"شما مجوز '{permission}' را ندارید.\n"
                f"نقش شما: {self.current_role}\n"
                "برای دسترسی بیشتر با مدیر سیستم تماس بگیرید."
            )
        
        return False
    
    def require_permission(self, permission):
        """دکوراتور برای بررسی مجوز قبل از اجرای تابع"""
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                # یافتن ویجت والد (اولین آرگومان معمولاً self است)
                widget = args[0] if args else None
                
                if not self.check_and_show(permission, widget):
                    return None
                
                return func(*args, **kwargs)
            return wrapper
        return decorator
    
    def log_operation(self, operation_name):
        """دکوراتور برای ثبت لاگ عملیات"""
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                try:
                    result = func(*args, **kwargs)
                    
                    # ثبت لاگ
                    if self.current_user:
                        self.config_manager.log_security_event(
                            self.current_user['id'],
                            operation_name,
                            f"تابع: {func.__name__}"
                        )
                    
                    return result
                    
                except Exception as e:
                    # ثبت لاگ خطا
                    if self.current_user:
                        self.config_manager.log_security_event(
                            self.current_user['id'],
                            f"خطا در {operation_name}",
                            f"خطا: {str(e)}"
                        )
                    raise e
            return wrapper
        return decorator