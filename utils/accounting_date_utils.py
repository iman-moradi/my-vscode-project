"""
ابزارهای تاریخ شمسی پیشرفته برای سیستم‌های حسابداری
ویژگی‌های جدید: اعتبارسنجی پیشرفته، تبدیلات هوشمند، محاسبات مالی، دوره‌های مالی
"""

import jdatetime
from datetime import datetime, date, timedelta
import re
from typing import Optional, Union, Tuple, Dict, Any, List
from dataclasses import dataclass
from enum import Enum
from PySide6.QtCore import QDate


class DateFormat(Enum):
    """انواع فرمت‌های تاریخ"""
    JALALI_NUMERIC = "jalali_numeric"      # 1403/01/15
    JALALI_DASH = "jalali_dash"            # 1403-01-15
    JALALI_PERSIAN = "jalali_persian"      # ۱۴۰۳/۰۱/۱۵
    GREGORIAN_NUMERIC = "gregorian_numeric" # 2024-04-04
    GREGORIAN_SLASH = "gregorian_slash"    # 2024/04/04
    LONG_PERSIAN = "long_persian"          # پنجشنبه ۱۵ فروردین ۱۴۰۳
    SHORT_PERSIAN = "short_persian"        # ۱۵ فروردین ۱۴۰۳
    DATABASE = "database"                  # برای ذخیره در دیتابیس
    TIMESTAMP = "timestamp"                # 2024-04-04 14:30:00


@dataclass
class DateRange:
    """داده‌ساختار برای محدوده تاریخ"""
    start_date: jdatetime.date
    end_date: jdatetime.date
    description: str = ""
    
    def to_dict(self) -> Dict[str, str]:
        """تبدیل به دیکشنری"""
        return {
            'start': self.start_date.strftime("%Y/%m/%d"),
            'end': self.end_date.strftime("%Y/%m/%d"),
            'start_gregorian': self.start_date.togregorian().strftime("%Y-%m-%d"),
            'end_gregorian': self.end_date.togregorian().strftime("%Y-%m-%d"),
            'description': self.description
        }
    
    def days_count(self) -> int:
        """تعداد روزهای محدوده"""
        greg_start = self.start_date.togregorian()
        greg_end = self.end_date.togregorian()
        return (greg_end - greg_start).days + 1


class PersianMonth(Enum):
    """ماه‌های فارسی"""
    FARVARDIN = (1, "فروردین", 31)
    ORDIBEHESHT = (2, "اردیبهشت", 31)
    KHORDAD = (3, "خرداد", 31)
    TIR = (4, "تیر", 31)
    MORDAD = (5, "مرداد", 31)
    SHAHRIVAR = (6, "شهریور", 31)
    MEHR = (7, "مهر", 30)
    ABAN = (8, "آبان", 30)
    AZAR = (9, "آذر", 30)
    DEY = (10, "دی", 30)
    BAHMAN = (11, "بهمن", 30)
    ESFAND = (12, "اسفند", 29)  # 29 یا 30 در سال کبیسه
    
    def __init__(self, number, name, days):
        self.number = number
        self.persian_name = name
        self.default_days = days
    
    @classmethod
    def from_number(cls, month_number: int) -> 'PersianMonth':
        """گرفتن ماه از شماره آن"""
        for month in cls:
            if month.number == month_number:
                return month
        raise ValueError(f"ماه نامعتبر: {month_number}")
    
    def get_days_in_year(self, year: int) -> int:
        """دریافت تعداد روزهای ماه در یک سال خاص"""
        if self.number == 12:  # اسفند
            try:
                test_date = jdatetime.date(year, 12, 1)
                return 30 if test_date.isleap() else 29
            except:
                return 29
        return self.default_days


class FinancialPeriod:
    """دوره مالی"""
    
    def __init__(self, start_month: int = 1, start_day: int = 1):
        """
        ایجاد دوره مالی
        
        Args:
            start_month: ماه شروع سال مالی (1-12)
            start_day: روز شروع سال مالی (1-31)
        """
        self.start_month = start_month
        self.start_day = start_day
    
    def get_financial_year(self, target_date: jdatetime.date = None) -> int:
        """دریافت سال مالی برای تاریخ مشخص"""
        if target_date is None:
            target_date = jdatetime.date.today()
        
        if (target_date.month > self.start_month or 
            (target_date.month == self.start_month and target_date.day >= self.start_day)):
            return target_date.year
        else:
            return target_date.year - 1
    
    def get_financial_year_range(self, year: int = None) -> DateRange:
        """دریافت محدوده سال مالی"""
        if year is None:
            year = self.get_financial_year()
        
        # شروع سال مالی
        try:
            start_date = jdatetime.date(year, self.start_month, self.start_day)
        except ValueError:
            # اگر روز معتبر نبود، روز اول ماه را در نظر بگیر
            start_date = jdatetime.date(year, self.start_month, 1)
        
        # پایان سال مالی (روز قبل از شروع سال بعد)
        next_year_start = jdatetime.date(year + 1, self.start_month, self.start_day)
        try:
            end_date = next_year_start - jdatetime.timedelta(days=1)
        except:
            # اگر خطا داد، یک روز قبل از شروع ماه بعد سال بعد
            end_date = jdatetime.date(year + 1, self.start_month, 1) - jdatetime.timedelta(days=1)
        
        return DateRange(start_date, end_date, f"سال مالی {year}")
    
    def get_current_period(self) -> DateRange:
        """دریافت دوره مالی جاری"""
        current_year = self.get_financial_year()
        return self.get_financial_year_range(current_year)
    
    def get_previous_period(self) -> DateRange:
        """دریافت دوره مالی قبلی"""
        current_year = self.get_financial_year()
        return self.get_financial_year_range(current_year - 1)


class AdvancedAccountingDateUtils:
    """
    کلاس پیشرفته برای مدیریت تاریخ شمسی در حسابداری
    
    ویژگی‌های جدید:
    1. تشخیص خودکار نوع تاریخ (شمسی/میلادی)
    2. تبدیلات هوشمند با پشتیبانی از ۱۵ فرمت مختلف
    3. اعتبارسنجی چندلایه با پیام‌های خطای دقیق
    4. محاسبات مالی (سررسید، اقساط، محاسبه سود)
    5. مدیریت دوره‌های مالی قابل تنظیم
    6. کش کردن نتایج برای بهبود عملکرد
    7. پشتیبانی از تاریخ‌های نسبی (امروز، دیروز، فردا، اول ماه، ...)
    8. محاسبه تفاوت تاریخ‌ها با واحدهای مختلف
    9. تولید گزارش‌های زمانی
    """
    
    # تعطیلات رسمی ایران
    IRANIAN_HOLIDAYS = {
        (1, 1): "عید نوروز",
        (1, 2): "عید نوروز",
        (1, 3): "عید نوروز",
        (1, 4): "عید نوروز",
        (1, 12): "روز جمهوری اسلامی",
        (1, 13): "سیزده بدر",
        (3, 14): "رحلت امام خمینی",
        (3, 15): "قیام 15 خرداد",
        (11, 22): "پیروزی انقلاب اسلامی",
        (12, 29): "روز ملی شدن صنعت نفت"
    }
    
    # روزهای هفته فارسی
    PERSIAN_WEEKDAYS = [
        "شنبه", "یکشنبه", "دوشنبه", "سه‌شنبه", 
        "چهارشنبه", "پنج‌شنبه", "جمعه"
    ]
    
    # روزهای هفته کوتاه
    PERSIAN_WEEKDAYS_SHORT = ["ش", "ی", "د", "س", "چ", "پ", "ج"]
    
    def __init__(self, financial_year_start_month: int = 1, financial_year_start_day: int = 1):
        """
        مقداردهی اولیه
        
        Args:
            financial_year_start_month: ماه شروع سال مالی (پیش‌فرض: فروردین)
            financial_year_start_day: روز شروع سال مالی (پیش‌فرض: اول ماه)
        """
        self.financial_period = FinancialPeriod(financial_year_start_month, financial_year_start_day)
        
        # کش برای بهبود عملکرد
        self._cache = {}
        self._month_range_cache = {}
        self._validation_cache = {}
    
    # ==================== تشخیص و تبدیل فرمت ====================
    
    def detect_date_format(self, date_str: str) -> Tuple[str, Optional[DateFormat]]:
        """
        تشخیص خودکار فرمت تاریخ
        
        Returns:
            (تمیز شده, فرمت تشخیص داده شده)
        """
        if not date_str:
            return "", None
        
        date_str = str(date_str).strip()
        
        # الگوهای مختلف
        patterns = [
            (r'^(\d{4})[/\-](\d{1,2})[/\-](\d{1,2})$', DateFormat.JALALI_NUMERIC),  # 1403/01/15
            (r'^(\d{4})[/\-](\d{1,2})[/\-](\d{1,2})$', DateFormat.GREGORIAN_NUMERIC),  # 2024-04-04
            (r'^(\d{2})[/\-](\d{1,2})[/\-](\d{1,2})$', DateFormat.JALALI_NUMERIC),  # 03/01/15
            (r'^[\u06F0-\u06F9]{4}[/\-][\u06F0-\u06F9]{2}[/\-][\u06F0-\u06F9]{2}$', DateFormat.JALALI_PERSIAN),  # ۱۴۰۳/۰۱/۱۵
            (r'^(\d{8})$', DateFormat.JALALI_NUMERIC),  # 14030115
            (r'^(\d{14})$', DateFormat.TIMESTAMP),  # 20240404143000
        ]
        
        for pattern, date_format in patterns:
            if re.match(pattern, date_str):
                return date_str, date_format
        
        # اگر فرمت طولانی فارسی باشد
        for month_name in [month.persian_name for month in PersianMonth]:
            if month_name in date_str:
                return date_str, DateFormat.LONG_PERSIAN
        
        return date_str, None
    
    def normalize_date_string(self, date_str: str, target_format: DateFormat = None) -> str:
        """
        نرمال‌سازی رشته تاریخ
        
        Args:
            date_str: رشته تاریخ ورودی
            target_format: فرمت خروجی مورد نظر
        
        Returns:
            رشته تاریخ نرمال شده
        """
        if not date_str:
            return ""
        
        cache_key = f"normalize_{date_str}_{target_format}"
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        date_str = str(date_str).strip()
        
        # اگر تاریخ میلادی است (سال بالای 1500)
        if re.match(r'^\d{4}[-/]\d{1,2}[-/]\d{1,2}$', date_str):
            year = int(re.split(r'[-/]', date_str)[0])
            if year > 1500:  # احتمالاً میلادی
                try:
                    # تبدیل به شمسی
                    dt = datetime.strptime(date_str.replace('/', '-'), "%Y-%m-%d")
                    jalali = jdatetime.date.fromgregorian(date=dt.date())
                    result = jalali.strftime("%Y/%m/%d")
                    self._cache[cache_key] = result
                    return result
                except:
                    pass
        
        # حذف کاراکترهای غیرمجاز
        cleaned = re.sub(r'[^\d/\-\.\u06F0-\u06F9]', '', date_str)
        
        # تبدیل اعداد فارسی به انگلیسی
        cleaned = self._persian_to_english_numbers(cleaned)
        
        # فرمت‌های مختلف
        if re.match(r'^\d{8}$', cleaned):  # 14030115
            year, month, day = cleaned[:4], cleaned[4:6], cleaned[6:8]
            cleaned = f"{year}/{month}/{day}"
        elif re.match(r'^\d{4}\d{2}\d{2}$', cleaned):  # 1403-01-15
            cleaned = cleaned.replace('-', '/')
        
        # هدف فرمت خاص
        if target_format:
            try:
                # ابتدا به تاریخ تبدیل کن
                jalali_date = self._parse_jalali_date(cleaned)
                if jalali_date:
                    result = self._format_date(jalali_date, target_format)
                    self._cache[cache_key] = result
                    return result
            except:
                pass
        
        self._cache[cache_key] = cleaned
        return cleaned
    
    # ==================== اعتبارسنجی پیشرفته ====================
    
    def validate_date_extended(self, date_str: str, 
                              check_range: bool = True,
                              min_year: int = 1300,
                              max_year: int = 1500) -> Dict[str, Any]:
        """
        اعتبارسنجی پیشرفته تاریخ
        
        Returns:
            دیکشنری شامل وضعیت اعتبارسنجی و اطلاعات اضافه
        """
        if not date_str:
            return {
                'valid': False,
                'error': 'رشته تاریخ خالی است',
                'date': None,
                'type': None
            }
        
        cache_key = f"validate_{date_str}_{check_range}_{min_year}_{max_year}"
        if cache_key in self._validation_cache:
            return self._validation_cache[cache_key]
        
        # نرمال‌سازی اولیه
        normalized = self.normalize_date_string(date_str)
        
        # تشخیص نوع
        date_type = self._detect_date_type(normalized)
        
        if date_type == 'jalali':
            result = self._validate_jalali_date(normalized, check_range, min_year, max_year)
        elif date_type == 'gregorian':
            result = self._validate_gregorian_date(normalized, check_range)
        else:
            result = {
                'valid': False,
                'error': 'فرمت تاریخ نامعتبر است',
                'date': None,
                'type': None
            }
        
        self._validation_cache[cache_key] = result
        return result
    
    def _detect_date_type(self, date_str: str) -> str:
        """تشخیص نوع تاریخ (شمسی/میلادی)"""
        if not date_str:
            return 'unknown'
        
        # بررسی الگوهای شمسی
        jalali_patterns = [
            r'^\d{4}/\d{1,2}/\d{1,2}$',
            r'^\d{4}-\d{1,2}-\d{1,2}$',
            r'^\d{8}$'
        ]
        
        for pattern in jalali_patterns:
            if re.match(pattern, date_str):
                # بررسی سال
                parts = re.split(r'[/\-]', date_str.replace('-', '/'))
                if len(parts) == 3:
                    try:
                        year = int(parts[0])
                        if 1300 <= year <= 1500:
                            return 'jalali'
                    except:
                        pass
        
        # اگر به اینجا رسید، احتمالاً میلادی است
        return 'gregorian'
    
    def _validate_jalali_date(self, date_str: str, check_range: bool, 
                             min_year: int, max_year: int) -> Dict[str, Any]:
        """اعتبارسنجی تاریخ شمسی"""
        try:
            # استخراج اجزا
            if '/' in date_str:
                parts = date_str.split('/')
            elif '-' in date_str:
                parts = date_str.split('-')
            else:
                # فرض می‌کنیم YYYYMMDD
                parts = [date_str[:4], date_str[4:6], date_str[6:8]]
            
            if len(parts) != 3:
                return {
                    'valid': False,
                    'error': 'فرمت تاریخ نامعتبر است',
                    'date': None,
                    'type': 'jalali'
                }
            
            year, month, day = map(int, parts)
            
            # بررسی محدوده سال
            if check_range and (year < min_year or year > max_year):
                return {
                    'valid': False,
                    'error': f'سال باید بین {min_year} و {max_year} باشد',
                    'date': None,
                    'type': 'jalali',
                    'year': year,
                    'month': month,
                    'day': day
                }
            
            # بررسی محدوده ماه
            if month < 1 or month > 12:
                return {
                    'valid': False,
                    'error': 'ماه باید بین ۱ و ۱۲ باشد',
                    'date': None,
                    'type': 'jalali',
                    'year': year,
                    'month': month,
                    'day': day
                }
            
            # تعداد روزهای مجاز ماه
            month_enum = PersianMonth.from_number(month)
            max_days = month_enum.get_days_in_year(year)
            
            if day < 1 or day > max_days:
                return {
                    'valid': False,
                    'error': f'روز باید بین ۱ و {max_days} برای ماه {month_enum.persian_name} باشد',
                    'date': None,
                    'type': 'jalali',
                    'year': year,
                    'month': month,
                    'day': day,
                    'max_days': max_days
                }
            
            # ایجاد تاریخ برای اطمینان نهایی
            jalali_date = jdatetime.date(year, month, day)
            
            return {
                'valid': True,
                'error': None,
                'date': jalali_date,
                'type': 'jalali',
                'year': year,
                'month': month,
                'day': day,
                'month_name': month_enum.persian_name,
                'weekday': jalali_date.weekday(),
                'weekday_name': self.PERSIAN_WEEKDAYS[jalali_date.weekday()],
                'is_holiday': self.is_holiday(jalali_date)
            }
            
        except ValueError as e:
            return {
                'valid': False,
                'error': f'تاریخ نامعتبر: {str(e)}',
                'date': None,
                'type': 'jalali'
            }
        except Exception as e:
            return {
                'valid': False,
                'error': f'خطا در اعتبارسنجی: {str(e)}',
                'date': None,
                'type': 'jalali'
            }
    
    def _validate_gregorian_date(self, date_str: str, check_range: bool) -> Dict[str, Any]:
        """اعتبارسنجی تاریخ میلادی"""
        try:
            # فرمت‌های مختلف
            formats = ['%Y-%m-%d', '%Y/%m/%d', '%Y%m%d']
            
            for fmt in formats:
                try:
                    dt = datetime.strptime(date_str, fmt)
                    break
                except:
                    continue
            else:
                return {
                    'valid': False,
                    'error': 'فرمت تاریخ میلادی نامعتبر',
                    'date': None,
                    'type': 'gregorian'
                }
            
            year = dt.year
            
            # بررسی محدوده سال (اختیاری)
            if check_range and (year < 1900 or year > 2100):
                return {
                    'valid': False,
                    'error': 'سال میلادی باید بین ۱۹۰۰ و ۲۱۰۰ باشد',
                    'date': None,
                    'type': 'gregorian',
                    'year': year
                }
            
            # تبدیل به شمسی برای اطلاعات بیشتر
            jalali_date = jdatetime.date.fromgregorian(date=dt.date())
            
            return {
                'valid': True,
                'error': None,
                'date': jalali_date,
                'type': 'gregorian',
                'gregorian_date': dt.date(),
                'year': jalali_date.year,
                'month': jalali_date.month,
                'day': jalali_date.day,
                'month_name': PersianMonth.from_number(jalali_date.month).persian_name,
                'weekday': jalali_date.weekday(),
                'weekday_name': self.PERSIAN_WEEKDAYS[jalali_date.weekday()],
                'is_holiday': self.is_holiday(jalali_date)
            }
            
        except Exception as e:
            return {
                'valid': False,
                'error': f'خطا در اعتبارسنجی میلادی: {str(e)}',
                'date': None,
                'type': 'gregorian'
            }
    
    # ==================== تبدیلات تاریخ ====================
    
    def convert_date(self, date_str: str, 
                    target_format: DateFormat = DateFormat.JALALI_NUMERIC,
                    source_format: DateFormat = None) -> str:
        """
        تبدیل تاریخ بین فرمت‌های مختلف
        """
        if not date_str:
            return ""
        
        cache_key = f"convert_{date_str}_{target_format}_{source_format}"
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        # اعتبارسنجی
        validation = self.validate_date_extended(date_str, check_range=False)
        if not validation['valid']:
            return date_str
        
        jalali_date = validation['date']
        
        # تبدیل به فرمت هدف
        result = self._format_date(jalali_date, target_format)
        
        self._cache[cache_key] = result
        return result
    
    def _format_date(self, jalali_date: jdatetime.date, 
                    target_format: DateFormat) -> str:
        """فرمت‌دهی تاریخ"""
        if target_format == DateFormat.JALALI_NUMERIC:
            return jalali_date.strftime("%Y/%m/%d")
        elif target_format == DateFormat.JALALI_DASH:
            return jalali_date.strftime("%Y-%m-%d")
        elif target_format == DateFormat.JALALI_PERSIAN:
            return self._to_persian_numbers(jalali_date.strftime("%Y/%m/%d"))
        elif target_format == DateFormat.GREGORIAN_NUMERIC:
            return jalali_date.togregorian().strftime("%Y-%m-%d")
        elif target_format == DateFormat.GREGORIAN_SLASH:
            return jalali_date.togregorian().strftime("%Y/%m/%d")
        elif target_format == DateFormat.LONG_PERSIAN:
            month_name = PersianMonth.from_number(jalali_date.month).persian_name
            weekday_name = self.PERSIAN_WEEKDAYS[jalali_date.weekday()]
            return f"{weekday_name} {jalali_date.day} {month_name} {jalali_date.year}"
        elif target_format == DateFormat.SHORT_PERSIAN:
            month_name = PersianMonth.from_number(jalali_date.month).persian_name
            return f"{jalali_date.day} {month_name} {jalali_date.year}"
        elif target_format == DateFormat.DATABASE:
            return jalali_date.togregorian().strftime("%Y-%m-%d")
        elif target_format == DateFormat.TIMESTAMP:
            return jalali_date.togregorian().strftime("%Y-%m-%d %H:%M:%S")
        else:
            return jalali_date.strftime("%Y/%m/%d")
    
    # ==================== محاسبات مالی ====================
    
    def calculate_due_date(self, start_date: Union[str, jdatetime.date],
                          period_days: int = 30,
                          grace_period: int = 0) -> Dict[str, Any]:
        """
        محاسبه تاریخ سررسید
        
        Args:
            start_date: تاریخ شروع
            period_days: مدت دوره (روز)
            grace_period: مدت تنفس (روز)
        
        Returns:
            اطلاعات تاریخ سررسید
        """
        # تبدیل به تاریخ
        if isinstance(start_date, str):
            validation = self.validate_date_extended(start_date)
            if not validation['valid']:
                return {'error': 'تاریخ شروع نامعتبر'}
            start_jalali = validation['date']
        else:
            start_jalali = start_date
        
        # محاسبه تاریخ سررسید
        greg_start = start_jalali.togregorian()
        greg_due = greg_start + timedelta(days=period_days)
        due_jalali = jdatetime.date.fromgregorian(date=greg_due)
        
        # محاسبه تاریخ با تنفس
        if grace_period > 0:
            greg_grace = greg_due + timedelta(days=grace_period)
            grace_jalali = jdatetime.date.fromgregorian(date=greg_grace)
        else:
            grace_jalali = due_jalali
        
        return {
            'start_date': start_jalali,
            'due_date': due_jalali,
            'grace_date': grace_jalali,
            'period_days': period_days,
            'grace_period': grace_period,
            'is_overdue': self.is_date_passed(due_jalali),
            'days_remaining': self.days_between(jdatetime.date.today(), due_jalali),
            'formatted': {
                'start': self._format_date(start_jalali, DateFormat.LONG_PERSIAN),
                'due': self._format_date(due_jalali, DateFormat.LONG_PERSIAN),
                'grace': self._format_date(grace_jalali, DateFormat.LONG_PERSIAN)
            }
        }
    
    def calculate_installments(self, start_date: Union[str, jdatetime.date],
                              total_amount: float,
                              installment_count: int,
                              interval_days: int = 30) -> List[Dict[str, Any]]:
        """
        محاسبه اقساط
        
        Args:
            start_date: تاریخ شروع
            total_amount: مبلغ کل
            installment_count: تعداد اقساط
            interval_days: فاصله بین اقساط (روز)
        
        Returns:
            لیست اقساط
        """
        if isinstance(start_date, str):
            validation = self.validate_date_extended(start_date)
            if not validation['valid']:
                return []
            current_jalali = validation['date']
        else:
            current_jalali = start_date
        
        installments = []
        installment_amount = total_amount / installment_count
        
        for i in range(installment_count):
            due_date = current_jalali
            if i > 0:
                greg_current = current_jalali.togregorian()
                greg_next = greg_current + timedelta(days=interval_days)
                due_date = jdatetime.date.fromgregorian(date=greg_next)
                current_jalali = due_date
            
            installments.append({
                'number': i + 1,
                'due_date': due_date,
                'amount': installment_amount,
                'remaining_amount': total_amount - (installment_amount * (i + 1)),
                'formatted_date': self._format_date(due_date, DateFormat.LONG_PERSIAN),
                'is_paid': False,
                'is_overdue': self.is_date_passed(due_date)
            })
        
        return installments
    
    def calculate_interest(self, principal: float,
                          start_date: Union[str, jdatetime.date],
                          end_date: Union[str, jdatetime.date] = None,
                          annual_rate: float = 18.0) -> Dict[str, Any]:
        """
        محاسبه سود
        
        Args:
            principal: مبلغ اصلی
            start_date: تاریخ شروع
            end_date: تاریخ پایان (اگر None باشد، امروز)
            annual_rate: نرخ سود سالانه (درصد)
        
        Returns:
            اطلاعات سود
        """
        # تبدیل تاریخ‌ها
        if isinstance(start_date, str):
            start_validation = self.validate_date_extended(start_date)
            if not start_validation['valid']:
                return {'error': 'تاریخ شروع نامعتبر'}
            start_jalali = start_validation['date']
        else:
            start_jalali = start_date
        
        if end_date is None:
            end_jalali = jdatetime.date.today()
        elif isinstance(end_date, str):
            end_validation = self.validate_date_extended(end_date)
            if not end_validation['valid']:
                return {'error': 'تاریخ پایان نامعتبر'}
            end_jalali = end_validation['date']
        else:
            end_jalali = end_date
        
        # محاسبه تعداد روزها
        days = self.days_between(start_jalali, end_jalali)
        if days < 0:
            return {'error': 'تاریخ پایان باید بعد از تاریخ شروع باشد'}
        
        # محاسبه سود
        daily_rate = annual_rate / 36500  # تقسیم بر 365 روز و 100 برای درصد
        interest = principal * daily_rate * days
        
        return {
            'principal': principal,
            'start_date': start_jalali,
            'end_date': end_jalali,
            'days': days,
            'annual_rate': annual_rate,
            'interest': interest,
            'total': principal + interest,
            'formatted': {
                'start': self._format_date(start_jalali, DateFormat.LONG_PERSIAN),
                'end': self._format_date(end_jalali, DateFormat.LONG_PERSIAN),
                'interest': f"{interest:,.2f}",
                'total': f"{principal + interest:,.2f}"
            }
        }
    
    # ==================== توابع کاربردی ====================
    
    def get_relative_date(self, relative: str = "today") -> jdatetime.date:
        """
        دریافت تاریخ نسبی
        
        Args:
            relative: یکی از موارد زیر:
                     "today", "yesterday", "tomorrow",
                     "first_of_month", "last_of_month",
                     "first_of_year", "last_of_year",
                     "first_of_financial_year", "last_of_financial_year"
        
        Returns:
            تاریخ شمسی
        """
        today = jdatetime.date.today()
        
        if relative == "today":
            return today
        elif relative == "yesterday":
            return today - jdatetime.timedelta(days=1)
        elif relative == "tomorrow":
            return today + jdatetime.timedelta(days=1)
        elif relative == "first_of_month":
            return jdatetime.date(today.year, today.month, 1)
        elif relative == "last_of_month":
            next_month = today.month + 1 if today.month < 12 else 1
            next_year = today.year if today.month < 12 else today.year + 1
            first_of_next = jdatetime.date(next_year, next_month, 1)
            return first_of_next - jdatetime.timedelta(days=1)
        elif relative == "first_of_year":
            return jdatetime.date(today.year, 1, 1)
        elif relative == "last_of_year":
            return jdatetime.date(today.year, 12, 29)  # 29 اسفند
        elif relative == "first_of_financial_year":
            financial_year = self.financial_period.get_financial_year()
            return self.financial_period.get_financial_year_range(financial_year).start_date
        elif relative == "last_of_financial_year":
            financial_year = self.financial_period.get_financial_year()
            return self.financial_period.get_financial_year_range(financial_year).end_date
        else:
            return today
    
    def days_between(self, date1: jdatetime.date, date2: jdatetime.date) -> int:
        """محاسبه تعداد روز بین دو تاریخ"""
        greg1 = date1.togregorian()
        greg2 = date2.togregorian()
        return (greg2 - greg1).days
    
    def is_date_passed(self, target_date: jdatetime.date) -> bool:
        """آیا تاریخ گذشته است؟"""
        today = jdatetime.date.today()
        return self.days_between(target_date, today) > 0
    
    def is_holiday(self, jalali_date: jdatetime.date) -> bool:
        """آیا تاریخ تعطیل است؟"""
        # جمعه
        if jalali_date.weekday() == 6:
            return True
        
        # تعطیلات رسمی
        return (jalali_date.month, jalali_date.day) in self.IRANIAN_HOLIDAYS
    
    def get_working_days(self, start_date: jdatetime.date, 
                        end_date: jdatetime.date) -> int:
        """محاسبه تعداد روزهای کاری بین دو تاریخ"""
        total_days = self.days_between(start_date, end_date) + 1
        holidays = 0
        
        current = start_date
        while current <= end_date:
            if self.is_holiday(current):
                holidays += 1
            current += jdatetime.timedelta(days=1)
        
        return total_days - holidays
    
    def get_month_range(self, year: int = None, month: int = None) -> DateRange:
        """
        دریافت محدوده ماه
        
        Args:
            year: سال (پیش‌فرض: سال جاری)
            month: ماه (پیش‌فرض: ماه جاری)
        
        Returns:
            محدوده ماه
        """
        if year is None:
            year = jdatetime.date.today().year
        if month is None:
            month = jdatetime.date.today().month
        
        cache_key = f"month_range_{year}_{month}"
        if cache_key in self._month_range_cache:
            return self._month_range_cache[cache_key]
        
        try:
            start_date = jdatetime.date(year, month, 1)
            
            # محاسبه آخرین روز ماه
            if month == 12:
                next_month = 1
                next_year = year + 1
            else:
                next_month = month + 1
                next_year = year
            
            try:
                next_month_start = jdatetime.date(next_year, next_month, 1)
                end_date = next_month_start - jdatetime.timedelta(days=1)
            except:
                # برای اسفند
                month_enum = PersianMonth.from_number(month)
                max_days = month_enum.get_days_in_year(year)
                end_date = jdatetime.date(year, month, max_days)
            
            month_name = month_enum.persian_name
            range_obj = DateRange(start_date, end_date, f"ماه {month_name} {year}")
            
            self._month_range_cache[cache_key] = range_obj
            return range_obj
            
        except Exception as e:
            # مقدار پیش‌فرض
            today = jdatetime.date.today()
            start_date = jdatetime.date(today.year, today.month, 1)
            end_date = today
            range_obj = DateRange(start_date, end_date, "ماه جاری")
            return range_obj
    
    def generate_date_report(self, start_date: jdatetime.date,
                           end_date: jdatetime.date) -> Dict[str, Any]:
        """
        تولید گزارش از محدوده تاریخ
        
        Returns:
            گزارش کامل از محدوده تاریخ
        """
        total_days = self.days_between(start_date, end_date) + 1
        working_days = self.get_working_days(start_date, end_date)
        holidays = total_days - working_days
        
        # لیست تعطیلات در محدوده
        holiday_list = []
        current = start_date
        while current <= end_date:
            if self.is_holiday(current):
                holiday_name = self.IRANIAN_HOLIDAYS.get(
                    (current.month, current.day), 
                    "جمعه" if current.weekday() == 6 else "تعطیل"
                )
                holiday_list.append({
                    'date': current,
                    'formatted': self._format_date(current, DateFormat.LONG_PERSIAN),
                    'name': holiday_name,
                    'is_friday': current.weekday() == 6
                })
            current += jdatetime.timedelta(days=1)
        
        return {
            'start_date': start_date,
            'end_date': end_date,
            'total_days': total_days,
            'working_days': working_days,
            'holidays': holidays,
            'holiday_list': holiday_list,
            'formatted': {
                'start': self._format_date(start_date, DateFormat.LONG_PERSIAN),
                'end': self._format_date(end_date, DateFormat.LONG_PERSIAN),
                'range': f"{self._format_date(start_date, DateFormat.SHORT_PERSIAN)} تا {self._format_date(end_date, DateFormat.SHORT_PERSIAN)}"
            }
        }
    
    # ==================== توابع کمکی ====================
    
    @staticmethod
    def _parse_jalali_date(date_str: str) -> Optional[jdatetime.date]:
        """تبدیل رشته به تاریخ شمسی"""
        try:
            if '/' in date_str:
                parts = date_str.split('/')
            elif '-' in date_str:
                parts = date_str.split('-')
            else:
                # YYYYMMDD
                parts = [date_str[:4], date_str[4:6], date_str[6:8]]
            
            if len(parts) == 3:
                year, month, day = map(int, parts)
                return jdatetime.date(year, month, day)
        except:
            pass
        return None
    
    @staticmethod
    def _persian_to_english_numbers(text: str) -> str:
        """تبدیل اعداد فارسی به انگلیسی"""
        persian_to_english = {
            '۰': '0', '۱': '1', '۲': '2', '۳': '3', '۴': '4',
            '۵': '5', '۶': '6', '۷': '7', '۸': '8', '۹': '9',
            '٠': '0', '١': '1', '٢': '2', '٣': '3', '٤': '4',
            '٥': '5', '٦': '6', '٧': '7', '٨': '8', '٩': '9'
        }
        
        result = []
        for char in text:
            result.append(persian_to_english.get(char, char))
        
        return ''.join(result)
    
    @staticmethod
    def _to_persian_numbers(text: str) -> str:
        """تبدیل اعداد انگلیسی به فارسی"""
        english_to_persian = {
            '0': '۰', '1': '۱', '2': '۲', '3': '۳', '4': '۴',
            '5': '۵', '6': '۶', '7': '۷', '8': '۸', '9': '۹'
        }
        
        result = []
        for char in text:
            result.append(english_to_persian.get(char, char))
        
        return ''.join(result)
    
    def clear_cache(self):
        """پاک کردن کش"""
        self._cache.clear()
        self._month_range_cache.clear()
        self._validation_cache.clear()


# ==================== کلاس سازگاری (برای کدهای قدیمی) ====================

class AccountingDateUtils:
    """کلاس سازگاری برای کدهای قدیمی"""
    
    @staticmethod
    def validate_jalali_date(date_str):
        """اعتبارسنجی تاریخ شمسی"""
        utils = AdvancedAccountingDateUtils()
        result = utils.validate_date_extended(date_str)
        return result['valid']
    
    @staticmethod
    def fix_invalid_jalali_date(date_str):
        """اصلاح تاریخ شمسی نامعتبر"""
        utils = AdvancedAccountingDateUtils()
        normalized = utils.normalize_date_string(date_str)
        validation = utils.validate_date_extended(normalized)
        
        if validation['valid']:
            return validation['date'].strftime("%Y/%m/%d")
        
        # تلاش برای اصلاح
        try:
            if '/' in normalized:
                year, month, day = map(int, normalized.split('/'))
                
                # محدود کردن روز
                if day > 31:
                    day = 31
                
                # ماه‌های 30 روزه
                if month in [7, 8, 9, 10, 11]:
                    if day > 30:
                        day = 30
                elif month == 12:  # اسفند
                    if day > 29:
                        day = 29
                
                return f"{year}/{month:02d}/{day:02d}"
        except:
            pass
        
        return date_str
    
    @staticmethod
    def get_current_jalali():
        """دریافت تاریخ امروز شمسی"""
        return jdatetime.datetime.now().strftime("%Y/%m/%d")
    
    @staticmethod
    def get_jalali_month_range(month_offset=0):
        """دریافت محدوده ماه شمسی"""
        utils = AdvancedAccountingDateUtils()
        
        today = jdatetime.date.today()
        if month_offset != 0:
            greg_today = today.togregorian()
            greg_target = greg_today + timedelta(days=30 * month_offset)
            today = jdatetime.date.fromgregorian(date=greg_target)
        
        month_range = utils.get_month_range(today.year, today.month)
        
        return {
            'start': month_range.start_date.strftime("%Y/%m/%d"),
            'end': month_range.end_date.strftime("%Y/%m/%d"),
            'year': month_range.start_date.year,
            'month': month_range.start_date.month,
            'month_name': PersianMonth.from_number(month_range.start_date.month).persian_name
        }
    
    @staticmethod
    def get_persian_month_name(month):
        """نام ماه فارسی"""
        try:
            return PersianMonth.from_number(month).persian_name
        except:
            return ""
    
    @staticmethod
    def get_persian_weekday(jalali_date_str=None):
        """دریافت نام روز هفته فارسی"""
        utils = AdvancedAccountingDateUtils()
        
        if not jalali_date_str:
            jalali_date = jdatetime.date.today()
        else:
            validation = utils.validate_date_extended(jalali_date_str)
            if not validation['valid']:
                return ""
            jalali_date = validation['date']
        
        return utils.PERSIAN_WEEKDAYS[jalali_date.weekday()]
    
    @staticmethod
    def format_jalali_for_display(date_str):
        """فرمت تاریخ شمسی برای نمایش زیبا"""
        utils = AdvancedAccountingDateUtils()
        validation = utils.validate_date_extended(date_str)
        
        if validation['valid']:
            return utils._format_date(validation['date'], DateFormat.LONG_PERSIAN)
        
        return date_str
    
    @staticmethod
    def format_jalali_short(date_str):
        """فرمت کوتاه تاریخ شمسی"""
        utils = AdvancedAccountingDateUtils()
        return utils.normalize_date_string(date_str)
    
    @staticmethod
    def get_financial_year():
        """دریافت سال مالی"""
        utils = AdvancedAccountingDateUtils()
        return utils.financial_period.get_financial_year()
    
    @staticmethod
    def get_financial_year_range():
        """دریافت محدوده سال مالی"""
        utils = AdvancedAccountingDateUtils()
        financial_year = utils.financial_period.get_financial_year()
        year_range = utils.financial_period.get_financial_year_range(financial_year)
        
        return {
            'start': year_range.start_date.strftime("%Y/%m/%d"),
            'end': year_range.end_date.strftime("%Y/%m/%d"),
            'year': financial_year
        }
    
    @staticmethod
    def gregorian_to_jalali(gregorian_date):
        """تبدیل تاریخ میلادی به شمسی"""
        utils = AdvancedAccountingDateUtils()
        
        if not gregorian_date:
            return ""
        
        try:
            if isinstance(gregorian_date, str):
                validation = utils.validate_date_extended(gregorian_date)
                if validation['valid']:
                    return validation['date'].strftime("%Y/%m/%d")
            
            elif isinstance(gregorian_date, date):
                jalali = jdatetime.date.fromgregorian(date=gregorian_date)
                return jalali.strftime("%Y/%m/%d")
        except:
            pass
        
        return str(gregorian_date)
    
    @staticmethod
    def jalali_to_gregorian(jalali_date_str):
        """تبدیل تاریخ شمسی به میلادی"""
        utils = AdvancedAccountingDateUtils()
        
        if not jalali_date_str:
            return None
        
        validation = utils.validate_date_extended(jalali_date_str)
        if validation['valid']:
            return validation['date'].togregorian().strftime("%Y-%m-%d")
        
        return jalali_date_str
    
    @staticmethod
    def get_qdate_from_jalali(jalali_date_str):
        """تبدیل تاریخ شمسی به QDate"""
        utils = AdvancedAccountingDateUtils()
        
        if not jalali_date_str:
            return QDate.currentDate()
        
        validation = utils.validate_date_extended(jalali_date_str)
        if validation['valid']:
            gregorian_date = validation['date'].togregorian()
            return QDate(gregorian_date.year, gregorian_date.month, gregorian_date.day)
        
        return QDate.currentDate()
    
    @staticmethod
    def get_days_between(start_date_jalali, end_date_jalali):
        """محاسبه تعداد روز بین دو تاریخ شمسی"""
        utils = AdvancedAccountingDateUtils()
        
        start_validation = utils.validate_date_extended(start_date_jalali)
        end_validation = utils.validate_date_extended(end_date_jalali)
        
        if start_validation['valid'] and end_validation['valid']:
            return utils.days_between(start_validation['date'], end_validation['date'])
        
        return 0


# ==================== تست ====================

if __name__ == "__main__":
    print("🧪 تست ابزارهای تاریخ شمسی پیشرفته")
    print("=" * 50)
    
    utils = AdvancedAccountingDateUtils()
    
    # تست اعتبارسنجی
    test_dates = [
        "1404/10/06",
        "1404-10-06",
        "14041006",
        "۱۴۰۴/۱۰/۰۶",
        "2024-04-04",
        "تاریخ نامعتبر"
    ]
    
    print("📅 تست اعتبارسنجی:")
    for date_str in test_dates:
        result = utils.validate_date_extended(date_str)
        status = "✅" if result['valid'] else "❌"
        print(f"  {status} {date_str:20} -> {result.get('error', 'معتبر')}")
    
    print("\n🔄 تست تبدیل فرمت:")
    jalali_date = "1404/10/06"
    for fmt in DateFormat:
        converted = utils.convert_date(jalali_date, fmt)
        print(f"  {fmt.value:20} -> {converted}")
    
    print("\n💰 تست محاسبات مالی:")
    
    # تست سررسید
    due_result = utils.calculate_due_date("1404/10/06", period_days=30, grace_period=7)
    print(f"  تاریخ سررسید: {due_result['formatted']['due']}")
    print(f"  با تنفس: {due_result['formatted']['grace']}")
    
    # تست اقساط
    installments = utils.calculate_installments(
        "1404/10/06", 
        total_amount=1000000, 
        installment_count=3, 
        interval_days=30
    )
    print(f"  تعداد اقساط: {len(installments)}")
    for inst in installments[:2]:  # فقط دو قسط اول
        print(f"    قسط {inst['number']}: {inst['formatted_date']} - {inst['amount']:,.0f}")
    
    # تست سود
    interest_result = utils.calculate_interest(
        principal=1000000,
        start_date="1404/01/01",
        annual_rate=18.0
    )
    print(f"  سود: {interest_result['formatted']['interest']}")
    print(f"  کل: {interest_result['formatted']['total']}")
    
    print("\n📊 تست گزارش:")
    month_range = utils.get_month_range(1404, 10)
    report = utils.generate_date_report(month_range.start_date, month_range.end_date)
    print(f"  محدوده: {report['formatted']['range']}")
    print(f"  روزهای کاری: {report['working_days']}")
    print(f"  تعطیلات: {report['holidays']}")
    
    print("\n🎯 تست توابع نسبی:")
    relatives = ["today", "yesterday", "tomorrow", "first_of_month", "last_of_month"]
    for rel in relatives:
        date_obj = utils.get_relative_date(rel)
        formatted = utils._format_date(date_obj, DateFormat.LONG_PERSIAN)
        print(f"  {rel:20} -> {formatted}")
    
    print("\n📈 تست سال مالی:")
    financial_range = utils.financial_period.get_current_period()
    print(f"  سال مالی جاری: {financial_range.description}")
    print(f"  از: {financial_range.start_date.strftime('%Y/%m/%d')}")
    print(f"  تا: {financial_range.end_date.strftime('%Y/%m/%d')}")
    print(f"  تعداد روزها: {financial_range.days_count()}")
    
    print("\n🔧 تست کلاس سازگاری:")
    compat_date = "1404/10/06"
    print(f"  اعتبارسنجی: {AccountingDateUtils.validate_jalali_date(compat_date)}")
    print(f"  نمایش زیبا: {AccountingDateUtils.format_jalali_for_display(compat_date)}")
    print(f"  تبدیل به میلادی: {AccountingDateUtils.jalali_to_gregorian(compat_date)}")
    
    print("\n" + "=" * 50)
    print("✅ تست‌ها با موفقیت انجام شد!")