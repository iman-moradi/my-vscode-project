
def format_currency(value, unit="تومان"):
    """قالب‌بندی ارز به صورت خوانا"""
    try:
        value = float(value)
        # جدا کردن سه رقم سه رقم
        formatted = f"{value:,.0f}".replace(",", "٬")
        return f"{formatted} {unit}"
    except:
        return f"0 {unit}"

def to_rial(toman_value):
    """تبدیل تومان به ریال"""
    try:
        return float(toman_value) * 10
    except:
        return 0

def to_toman(rial_value):
    """تبدیل ریال به تومان"""
    try:
        return float(rial_value) / 10
    except:
        return 0