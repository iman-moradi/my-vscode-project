# ui/forms/reports/utils/date_utils.py
"""
توابع کمکی تاریخ شمسی برای ماژول گزارش‌گیری
"""

import jdatetime
from datetime import datetime

def get_current_jalali():
    """دریافت تاریخ شمسی فعلی"""
    now = jdatetime.datetime.now()
    return now.strftime('%Y/%m/%d %H:%M:%S')

def gregorian_to_jalali(gregorian_date):
    """تبدیل تاریخ میلادی به شمسی"""
    if not gregorian_date:
        return ""
    
    try:
        if isinstance(gregorian_date, str):
            # حذف زمان اگر وجود دارد
            if ' ' in gregorian_date:
                gregorian_date = gregorian_date.split(' ')[0]
            
            # تبدیل رشته به تاریخ میلادی
            try:
                g_date = datetime.strptime(gregorian_date, '%Y-%m-%d')
            except:
                try:
                    g_date = datetime.strptime(gregorian_date, '%Y/%m/%d')
                except:
                    return str(gregorian_date)
        else:
            # اگر از قبل شیء datetime است
            g_date = gregorian_date
        
        # تبدیل به تاریخ شمسی
        j_date = jdatetime.date.fromgregorian(date=g_date.date())
        return j_date.strftime('%Y/%m/%d')
    except Exception as e:
        print(f"⚠️ خطا در تبدیل تاریخ {gregorian_date}: {e}")
        return str(gregorian_date)

def jalali_to_gregorian(jalali_date_str, format_str='%Y-%m-%d'):
    """تبدیل تاریخ شمسی به میلادی"""
    try:
        year, month, day = map(int, jalali_date_str.split('/'))
        jalali_date = jdatetime.date(year, month, day)
        gregorian_date = jalali_date.togregorian()
        return gregorian_date.strftime(format_str)
    except Exception as e:
        print(f"⚠️ خطا در تبدیل تاریخ شمسی {jalali_date_str}: {e}")
        return None

def format_jalali_date(jalali_date, format_str='%Y/%m/%d'):
    """فرمت تاریخ شمسی"""
    if isinstance(jalali_date, str):
        try:
            year, month, day = map(int, jalali_date.split('/'))
            jalali_date = jdatetime.date(year, month, day)
        except:
            return jalali_date
    
    if isinstance(jalali_date, jdatetime.date):
        return jalali_date.strftime(format_str)
    
    return str(jalali_date)