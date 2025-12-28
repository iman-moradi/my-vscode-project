# date_utils.py
import jdatetime
from datetime import datetime, date
from PySide6.QtCore import QDate

def gregorian_to_jalali(gregorian_date):
    """تبدیل تاریخ میلادی به شمسی"""
    if isinstance(gregorian_date, QDate):
        gregorian_date = gregorian_date.toPython()
    
    if isinstance(gregorian_date, (date, datetime)):
        try:
            # استفاده از convert برای تبدیل امن
            jalali_date = jdatetime.date.fromgregorian(date=gregorian_date)
            return jalali_date
        except Exception as e:
            print(f"خطا در تبدیل تاریخ: {e}")
            return None
    return None

def jalali_to_gregorian(jalali_date):
    """تبدیل تاریخ شمسی به میلادی"""
    if isinstance(jalali_date, jdatetime.date):
        try:
            gregorian_date = jalali_date.togregorian()
            return gregorian_date
        except Exception as e:
            print(f"خطا در تبدیل تاریخ: {e}")
            return None
    return None

def get_current_jalali_date():
    """دریافت تاریخ شمسی فعلی"""
    return jdatetime.date.today()

def format_jalali_date(jalali_date, format_str="%Y/%m/%d"):
    """فرمت‌دهی تاریخ شمسی"""
    if isinstance(jalali_date, jdatetime.date):
        try:
            return jalali_date.strftime(format_str)
        except:
            try:
                # اگر فرمت استاندارد کار نکرد
                return f"{jalali_date.year:04d}/{jalali_date.month:02d}/{jalali_date.day:02d}"
            except:
                return ""
    return ""

def get_jalali_date_from_string(date_str, format_str="%Y/%m/%d"):
    """تبدیل رشته به تاریخ شمسی"""
    try:
        # حذف کاراکترهای غیرعددی فارسی
        date_str = ''.join(c for c in date_str if c.isdigit() or c in ['/', '-', '.'])
        return jdatetime.datetime.strptime(date_str, format_str).date()
    except Exception as e:
        print(f"خطا در تبدیل رشته به تاریخ: {date_str} - {e}")
        return None

def qdate_to_jalali(qdate):
    """تبدیل QDate به تاریخ شمسی"""
    if isinstance(qdate, QDate):
        gregorian_date = qdate.toPython()
        return gregorian_to_jalali(gregorian_date)
    return None

def jalali_to_qdate(jalali_date):
    """تبدیل تاریخ شمسی به QDate"""
    if isinstance(jalali_date, jdatetime.date):
        gregorian_date = jalali_date.togregorian()
        return QDate(gregorian_date.year, gregorian_date.month, gregorian_date.day)
    return QDate.currentDate()