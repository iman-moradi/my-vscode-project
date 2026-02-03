# modules/settings_integration.py
from PySide6.QtWidgets import QMessageBox

class SettingsIntegrator:
    """کلاس یکپارچه‌کننده تنظیمات در تمام بخش‌های سیستم"""
    
    def __init__(self, config_manager):
        self.config_manager = config_manager
        self.registered_forms = {}
    
    def register_form(self, form_name, form_instance):
        """ثبت یک فرم برای دریافت به‌روزرسانی‌های تنظیمات"""
        self.registered_forms[form_name] = form_instance
        
        # اتصال سیگنال
        self.config_manager.config_updated.connect(
            lambda key, changes: self.update_form(form_name, key, changes)
        )
    
    def update_form(self, form_name, key_path, changes):
        """به‌روزرسانی یک فرم خاص"""
        if form_name in self.registered_forms:
            form = self.registered_forms[form_name]
            
            if hasattr(form, 'on_config_updated'):
                form.on_config_updated(key_path, changes)
    
    def apply_security_to_form(self, form, user_role):
        """اعمال تنظیمات امنیتی روی یک فرم"""
        try:
            # دریافت مجوزهای لازم برای این فرم
            required_permissions = self.get_required_permissions(form)
            
            # بررسی و اعمال محدودیت‌ها
            for widget_name, permission in required_permissions.items():
                if hasattr(form, widget_name):
                    widget = getattr(form, widget_name)
                    
                    # بررسی دسترسی
                    if not self.config_manager.check_permission(user_role, permission):
                        widget.setEnabled(False)
                        if hasattr(widget, 'setToolTip'):
                            widget.setToolTip("شما دسترسی لازم را ندارید")
            
            return True
            
        except Exception as e:
            print(f"⚠️ خطا در اعمال امنیت روی فرم: {e}")
            return False
    
    def get_required_permissions(self, form):
        """دریافت مجوزهای مورد نیاز برای یک فرم"""
        # این می‌تواند از یک فایل پیکربندی یا دیتابیس بارگذاری شود
        form_permissions = {
            'PersonForm': {
                'btn_save': 'edit_persons',
                'btn_delete': 'delete_persons',
                'btn_new': 'edit_persons',
                'tab_financial': 'view_financial_info'
            },
            'InventoryForm': {
                'btn_add': 'edit_inventory',
                'btn_delete': 'delete_inventory',
                'btn_edit': 'edit_inventory'
            }
            # ... سایر فرم‌ها
        }
        
        form_class_name = form.__class__.__name__
        return form_permissions.get(form_class_name, {})
    
    def validate_transaction(self, user_role, transaction_type, amount):
        """اعتبارسنجی تراکنش بر اساس تنظیمات"""
        try:
            # دریافت محدودیت‌های مالی
            max_amounts = {
                'payment': self.config_manager.get('financial', 'max_payment_amount', 50000000),
                'receipt': self.config_manager.get('financial', 'max_receipt_amount', 100000000),
                'transfer': self.config_manager.get('financial', 'max_transfer_amount', 200000000)
            }
            
            max_allowed = max_amounts.get(transaction_type, 10000000)
            
            if amount > max_allowed:
                return False, f"مبلغ نمی‌تواند بیشتر از {max_allowed:,} تومان باشد"
            
            # بررسی محدودیت‌های نقش
            if user_role == 'اپراتور' and amount > 5000000:
                return False, "اپراتورها نمی‌توانند تراکنش‌های بالای ۵ میلیون تومان انجام دهند"
            
            return True, "تراکنش معتبر است"
            
        except Exception as e:
            print(f"⚠️ خطا در اعتبارسنجی تراکنش: {e}")
            return False, "خطا در اعتبارسنجی"