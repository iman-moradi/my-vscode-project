"""
ویجت ورود تاریخ شمسی
"""

from PySide6.QtWidgets import QDateEdit, QCalendarWidget
from PySide6.QtCore import QDate, Qt, Signal
from PySide6.QtGui import QPalette, QColor
import jdatetime


class JalaliDateInput(QDateEdit):
    """ویجت ورود تاریخ شمسی با تقویم فارسی"""
    
    date_changed = Signal(jdatetime.date)  # سیگنال تغییر تاریخ
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # تنظیمات اولیه
        self.setCalendarPopup(True)
        self.setDisplayFormat("yyyy/MM/dd")
        
        # تنظیم تاریخ پیش‌فرض به امروز شمسی
        today = jdatetime.datetime.now()
        self.set_date(today)
        
        # استایل
        self.setStyleSheet("""
            QDateEdit {
                background-color: #222222;
                border: 1px solid #333;
                color: white;
                border-radius: 4px;
                padding: 6px;
                selection-background-color: #2ecc71;
            }
            QDateEdit:hover {
                border: 1px solid #2ecc71;
            }
            QDateEdit::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 25px;
                border-left-width: 1px;
                border-left-color: #333;
                border-left-style: solid;
                border-top-right-radius: 4px;
                border-bottom-right-radius: 4px;
            }
            QDateEdit::down-arrow {
                image: url(data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIyNCIgaGVpZ2h0PSIyNCIgdmlld0JveD0iMCAwIDI0IDI0IiBmaWxsPSJ3aGl0ZSI+PHBhdGggZD0iTTcgMTBsNSA1IDUtNXoiLz48L3N2Zz4=);
            }
        """)
        
        # اتصال سیگنال تغییر تاریخ
        self.dateChanged.connect(self._on_date_changed)
    
    def set_date(self, jalali_date):
        """تنظیم تاریخ شمسی"""
        if isinstance(jalali_date, jdatetime.datetime):
            jalali_date = jalali_date.date()
        
        # تبدیل به میلادی برای QDateEdit
        gregorian_date = jalali_date.togregorian()
        qdate = QDate(gregorian_date.year, gregorian_date.month, gregorian_date.day)
        self.setDate(qdate)
    
    def get_date(self):
        """دریافت تاریخ شمسی"""
        qdate = self.date()
        gregorian_date = jdatetime.date.fromgregorian(
            year=qdate.year(), 
            month=qdate.month(), 
            day=qdate.day()
        )
        return gregorian_date
    
    def get_date_string(self, format_str="%Y/%m/%d"):
        """دریافت تاریخ به صورت رشته"""
        jalali_date = self.get_date()
        return jalali_date.strftime(format_str)
    
    def _on_date_changed(self, date):
        """هنگام تغییر تاریخ"""
        gregorian_date = jdatetime.date.fromgregorian(
            year=date.year(), 
            month=date.month(), 
            day=date.day()
        )
        self.date_changed.emit(gregorian_date)
    
    def set_display_format(self, format_str):
        """تنظیم فرمت نمایش تاریخ (برای سازگاری)"""
        # QDateEdit از فرمت میلادی استفاده می‌کند
        # برای نمایش شمسی باید فرمت را به میلادی تبدیل کنیم
        # در اینجا فقط متد را برای جلوگیری از خطا تعریف می‌کنیم
        super().setDisplayFormat("yyyy/MM/dd")
    
    # متدهای سازگاری
    def setDisplayFormat(self, format_str):
        """متد سازگاری با کد موجود"""
        self.set_display_format(format_str)
    
    def set_jalali_date(self, year, month, day):
        """تنظیم تاریخ شمسی مستقیم"""
        jalali_date = jdatetime.date(year, month, day)
        self.set_date(jalali_date)

    def set_date_string(self, date_string, format_str="%Y/%m/%d"):
        """
        تنظیم تاریخ از روی رشته.
        date_string: رشته تاریخ شمسی مانند '1404/11/06'
        format_str: فرمت رشته ورودی
        """
        try:
            if not date_string:
                return
            
            # تبدیل رشته به تاریخ شمسی
            jalali_date = jdatetime.datetime.strptime(date_string, format_str).date()
            self.set_date(jalali_date)
        except ValueError as e:
            print(f"⚠️ خطا در تبدیل رشته تاریخ: {e}")
            # در صورت خطا، تاریخ امروز را تنظیم کن
            self.set_date(jdatetime.date.today())    


# کلاس کمکی برای تبدیل تاریخ
class JalaliDateConverter:
    """تبدیل کننده تاریخ شمسی به میلادی و بالعکس"""
    
    @staticmethod
    def to_jalali(gregorian_date):
        """تبدیل میلادی به شمسی"""
        if isinstance(gregorian_date, QDate):
            return jdatetime.date.fromgregorian(
                year=gregorian_date.year(),
                month=gregorian_date.month(),
                day=gregorian_date.day()
            )
        elif isinstance(gregorian_date, str):
            # فرض می‌کنیم رشته تاریخ میلادی است
            from datetime import datetime
            dt = datetime.strptime(gregorian_date, "%Y-%m-%d")
            return jdatetime.date.fromgregorian(date=dt.date())
        return None
    
    @staticmethod
    def to_gregorian(jalali_date):
        """تبدیل شمسی به میلادی"""
        if isinstance(jalali_date, jdatetime.date):
            return jalali_date.togregorian()
        elif isinstance(jalali_date, str):
            # فرض می‌کنیم رشته تاریخ شمسی است
            year, month, day = map(int, jalali_date.split('/'))
            jalali = jdatetime.date(year, month, day)
            return jalali.togregorian()
        return None