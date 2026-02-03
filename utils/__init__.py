try:
    from helpers import format_currency, to_rial, to_toman
except ImportError:
    # توابع جایگزین در صورت عدم وجود فایل helpers
    def format_currency(amount, currency="تومان"):
        return f"{amount:,} {currency}" if isinstance(amount, (int, float)) else f"{amount} {currency}"
    
    def to_rial(amount_toman):
        return amount_toman * 10 if isinstance(amount_toman, (int, float)) else 0
    
    def to_toman(amount_rial):
        return amount_rial / 10 if isinstance(amount_rial, (int, float)) else 0

# تغییر این خط: اضافه کردن نقطه قبل از jalali_date_widget برای import نسبی
try:
    from .jalali_date_widget import JalaliCalendarDialog, JalaliDateWidget, JalaliDateEdit, JalaliDateTimeWidget, JalaliDateDelegate
except ImportError:
    # اگر فایل وجود ندارد، کلاس‌های جایگزین تعریف می‌کنیم
    class JalaliDateWidget:
        pass
    class JalaliDateEdit:
        pass
    class JalaliDateTimeWidget:
        pass
    class JalaliCalendarDialog:
        pass
    class JalaliDateDelegate:
        pass

__all__ = [
    'format_currency', 
    'to_rial',
    'to_toman',
    'JalaliCalendarDialog',
    'JalaliDateWidget',
    'JalaliDateEdit',
    'JalaliDateTimeWidget',
    'JalaliDateDelegate'
    ]