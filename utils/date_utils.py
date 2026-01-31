"""
ابزارهای تاریخ شمسی
"""

import jdatetime
from datetime import datetime
import locale


def get_current_jalali():
    """دریافت تاریخ شمسی فعلی به صورت رشته"""
    now = jdatetime.datetime.now()
    return now.strftime("%Y/%m/%d")


def get_current_jalali_datetime():
    """دریافت تاریخ و زمان شمسی فعلی"""
    return jdatetime.datetime.now()


def get_current_jalali_date():
    """دریافت تاریخ شمسی فعلی (همنام با تابع قبلی)"""
    return get_current_jalali()


def gregorian_to_jalali(gregorian_date):
    """تبدیل تاریخ میلادی به شمسی"""
    if isinstance(gregorian_date, datetime):
        try:
            return jdatetime.datetime.fromgregorian(
                year=gregorian_date.year,
                month=gregorian_date.month,
                day=gregorian_date.day
            )
        except:
            return jdatetime.date.fromgregorian(date=gregorian_date.date())
    elif isinstance(gregorian_date, str):
        # فرض بر این که فرمت yyyy-mm-dd است
        try:
            # حذف بخش زمانی اگر وجود دارد
            gregorian_date = gregorian_date.split(' ')[0]
            year, month, day = map(int, gregorian_date.split('-'))
            return jdatetime.date.fromgregorian(year=year, month=month, day=day)
        except:
            try:
                # فرمت yyyy/mm/dd
                year, month, day = map(int, gregorian_date.split('/'))
                return jdatetime.date.fromgregorian(year=year, month=month, day=day)
            except:
                return jdatetime.date.today()
    return None


def jalali_to_gregorian(jalali_date):
    """تبدیل تاریخ شمسی به میلادی"""
    if isinstance(jalali_date, jdatetime.datetime):
        return jalali_date.togregorian()
    elif isinstance(jalali_date, jdatetime.date):
        return jalali_date.togregorian()
    elif isinstance(jalali_date, str):
        try:
            # فرمت yyyy/mm/dd
            year, month, day = map(int, jalali_date.split('/'))
            jalali = jdatetime.date(year, month, day)
            return jalali.togregorian()
        except:
            try:
                # فرمت yyyy-mm-dd
                year, month, day = map(int, jalali_date.split('-'))
                jalali = jdatetime.date(year, month, day)
                return jalali.togregorian()
            except:
                return datetime.now().date()
    return None


def format_jalali_date(jalali_date, format_str="%Y/%m/%d"):
    """فرمت‌دهی تاریخ شمسی"""
    if isinstance(jalali_date, jdatetime.datetime):
        return jalali_date.strftime(format_str)
    elif isinstance(jalali_date, jdatetime.date):
        return jalali_date.strftime(format_str)
    elif isinstance(jalali_date, str):
        try:
            # تبدیل رشته به تاریخ شمسی
            date_str = jalali_date.replace('-', '/')
            parts = date_str.split('/')
            if len(parts) == 3:
                year, month, day = map(int, parts)
                date_obj = jdatetime.date(year, month, day)
                return date_obj.strftime(format_str)
        except:
            return jalali_date
    return ""


def get_persian_weekday(jalali_date):
    """دریافت نام روز هفته فارسی"""
    # تنظیم locale برای فارسی
    try:
        locale.setlocale(locale.LC_ALL, 'fa_IR.UTF-8')
    except:
        pass
    
    weekdays = {
        0: "شنبه",
        1: "یکشنبه",
        2: "دوشنبه",
        3: "سه‌شنبه",
        4: "چهارشنبه",
        5: "پنجشنبه",
        6: "جمعه"
    }
    
    if isinstance(jalali_date, jdatetime.datetime):
        weekday_num = jalali_date.weekday()
    elif isinstance(jalali_date, jdatetime.date):
        weekday_num = jalali_date.weekday()
    else:
        return ""
    
    return weekdays.get(weekday_num, "")


def get_persian_month_name(month_number):
    """دریافت نام ماه فارسی"""
    months = {
        1: "فروردین",
        2: "اردیبهشت",
        3: "خرداد",
        4: "تیر",
        5: "مرداد",
        6: "شهریور",
        7: "مهر",
        8: "آبان",
        9: "آذر",
        10: "دی",
        11: "بهمن",
        12: "اسفند"
    }
    return months.get(month_number, "")


def get_current_persian_weekday():
    """دریافت نام روز هفته فعلی به فارسی"""
    return get_persian_weekday(jdatetime.datetime.now())


def get_current_persian_month_name():
    """دریافت نام ماه فعلی به فارسی"""
    return get_persian_month_name(jdatetime.datetime.now().month)


def convert_to_jalali_display(date_str):
    """تبدیل رشته تاریخ میلادی به شمسی برای نمایش (همنام با تابع main_window)"""
    if not date_str:
        return ""
    
    try:
        # فرمت‌های مختلف تاریخ
        date_formats = ['%Y-%m-%d', '%Y/%m/%d', '%d-%m-%Y', '%d/%m/%Y']
        
        miladi_date = None
        for fmt in date_formats:
            try:
                miladi_date = datetime.strptime(str(date_str).split(' ')[0], fmt).date()
                break
            except:
                continue
        
        if miladi_date:
            jalali_date = jdatetime.date.fromgregorian(date=miladi_date)
            return jalali_date.strftime('%Y/%m/%d')
        else:
            return str(date_str)  # اگر تبدیل نشد، تاریخ اصلی را برگردان
            
    except Exception as e:
        print(f"⚠️ خطا در تبدیل تاریخ {date_str}: {e}")
        return str(date_str)


# توابع کمکی برای ویجت JalaliDateInput
def get_jalali_today():
    """دریافت تاریخ امروز شمسی برای ویجت"""
    return jdatetime.date.today()


def string_to_jalali(date_str):
    """تبدیل رشته به تاریخ شمسی"""
    try:
        date_str = date_str.replace('-', '/').strip()
        parts = date_str.split('/')
        if len(parts) == 3:
            year = int(parts[0])
            month = int(parts[1])
            day = int(parts[2])
            if 1300 <= year <= 1500 and 1 <= month <= 12 and 1 <= day <= 31:
                return jdatetime.date(year, month, day)
    except:
        pass
    return jdatetime.date.today()


def jalali_to_string(jalali_date, separator='/'):
    """تبدیل تاریخ شمسی به رشته"""
    if isinstance(jalali_date, jdatetime.date):
        return f"{jalali_date.year}{separator}{jalali_date.month:02d}{separator}{jalali_date.day:02d}"
    return ""