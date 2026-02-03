# helpers.py - فایل کمکی موقت
def format_currency(amount, currency="تومان"):
    """قالب‌بندی مبلغ به صورت زیبا"""
    try:
        amount = float(amount)
        return f"{amount:,.0f} {currency}"
    except:
        return f"{amount} {currency}"

def to_rial(amount_toman):
    """تبدیل تومان به ریال"""
    try:
        return float(amount_toman) * 10
    except:
        return 0

def to_toman(amount_rial):
    """تبدیل ریال به تومان"""
    try:
        return float(amount_rial) / 10
    except:
        return 0

# توابع اضافی برای جلوگیری از خطاهای بعدی
def get_current_date():
    """دریافت تاریخ جاری"""
    from datetime import datetime
    return datetime.now().strftime("%Y-%m-%d")

def validate_phone(phone):
    """اعتبارسنجی شماره تلفن"""
    if phone and len(str(phone)) >= 10:
        return True
    return False