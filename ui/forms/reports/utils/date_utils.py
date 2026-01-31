"""
توابع کمکی تاریخ شمسی - نسخه ایمن
"""

import jdatetime
from datetime import datetime
import re

def get_current_jalali():
    """دریافت تاریخ شمسی فعلی"""
    try:
        now = jdatetime.datetime.now()
        return now.strftime('%Y/%m/%d %H:%M:%S')
    except:
        return "1403/01/01 00:00:00"

def gregorian_to_jalali(gregorian_date, format_str='%Y/%m/%d'):
    """تبدیل تاریخ میلادی به شمسی - نسخه ایمن"""
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
                    # اگر تبدیل نشد، خود رشته را برگردان
                    return str(gregorian_date)
        else:
            # اگر از قبل شیء datetime است
            g_date = gregorian_date
        
        # تبدیل به تاریخ شمسی
        j_date = jdatetime.date.fromgregorian(date=g_date.date())
        return j_date.strftime(format_str)
    except Exception as e:
        print(f"⚠️ خطا در تبدیل تاریخ {gregorian_date}: {e}")
        return str(gregorian_date)

def jalali_to_gregorian(jalali_date_str):
    """تبدیل تاریخ شمسی به میلادی - نسخه اصلاح شده"""
    if not jalali_date_str:
        return None
    
    try:
        # پاکسازی رشته
        date_str = str(jalali_date_str).strip()
        
        # اگر فرمت yyyy/mm/dd است
        if '/' in date_str:
            parts = date_str.split('/')
            if len(parts) == 3:
                year = int(parts[0])
                month = int(parts[1])
                day = int(parts[2])
            else:
                return None
        # اگر فرمت yyyy-mm-dd است
        elif '-' in date_str:
            parts = date_str.split('-')
            if len(parts) == 3:
                year = int(parts[0])
                month = int(parts[1])
                day = int(parts[2])
            else:
                return None
        else:
            return None
        
        # ایجاد تاریخ شمسی
        jalali_date = jdatetime.date(year, month, day)
        
        # تبدیل به میلادی
        gregorian_date = jalali_date.togregorian()
        
        return gregorian_date.strftime("%Y-%m-%d")
        
    except Exception as e:
        print(f"⚠️ خطا در تبدیل تاریخ شمسی {jalali_date_str}: {e}")
        return None

def format_jalali_date(jalali_date, format_str='%Y/%m/%d'):
    """فرمت تاریخ شمسی - نسخه ایمن"""
    if not jalali_date:
        return ""
    
    try:
        if isinstance(jalali_date, str):
            # اگر رشته است، به تاریخ تبدیل کن
            if '/' in jalali_date:
                year, month, day = map(int, jalali_date.split('/'))
                jalali_date = jdatetime.date(year, month, day)
            else:
                return str(jalali_date)
        
        if isinstance(jalali_date, jdatetime.date):
            return jalali_date.strftime(format_str)
        
        return str(jalali_date)
    except Exception:
        return str(jalali_date)

def validate_jalali_date(date_str):
    """اعتبارسنجی تاریخ شمسی"""
    if not date_str:
        return False
    
    try:
        if '/' in date_str:
            parts = date_str.split('/')
            if len(parts) != 3:
                return False
            
            year, month, day = map(int, parts)
            # بررسی محدوده معقول
            if year < 1300 or year > 1500:
                return False
            if month < 1 or month > 12:
                return False
            if day < 1 or day > 31:
                return False
            
            # ایجاد تاریخ برای بررسی معتبر بودن
            jdatetime.date(year, month, day)
            return True
        return False
    except:
        return False