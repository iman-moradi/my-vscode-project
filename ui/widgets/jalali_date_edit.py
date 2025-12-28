from PySide6.QtWidgets import QDateEdit
from PySide6.QtCore import QDate
import jdatetime

class JalaliDateEdit(QDateEdit):
    """ویجت تاریخ شمسی"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setCalendarPopup(True)
        self.setDisplayFormat("yyyy/MM/dd")
        self.set_date_to_today()
        
    def set_date_to_today(self):
        """تنظیم تاریخ به امروز شمسی"""
        # تاریخ امروز شمسی
        today_jalali = jdatetime.date.today()
        
        # تبدیل به میلادی برای QDateEdit
        try:
            today_gregorian = today_jalali.togregorian()
            qdate = QDate(today_gregorian.year, today_gregorian.month, today_gregorian.day)
            self.setDate(qdate)
            return True
        except Exception as e:
            print(f"خطا در تنظیم تاریخ امروز: {e}")
            # در صورت خطا، تاریخ میلادی امروز
            self.setDate(QDate.currentDate())
            return False
            
    def get_jalali_date(self):
        """دریافت تاریخ شمسی"""
        try:
            qdate = self.date()
            gregorian_date = qdate.toPython()
            # تبدیل به تاریخ شمسی
            jalali_date = jdatetime.date.fromgregorian(date=gregorian_date)
            return jalali_date
        except Exception as e:
            print(f"خطا در دریافت تاریخ شمسی: {e}")
            return jdatetime.date.today()
            
    def set_jalali_date(self, jalali_date):
        """تنظیم تاریخ شمسی"""
        try:
            if isinstance(jalali_date, jdatetime.date):
                # تبدیل به میلادی
                gregorian_date = jalali_date.togregorian()
                qdate = QDate(gregorian_date.year, gregorian_date.month, gregorian_date.day)
                self.setDate(qdate)
                return True
            elif isinstance(jalali_date, str) and jalali_date.strip():
                # اگر رشته است
                # حذف کاراکترهای غیرعددی
                clean_date = ''.join(c for c in jalali_date if c.isdigit() or c in ['/', '-'])
                try:
                    if len(clean_date) == 8:
                        # فرض: 14031225
                        year = int(clean_date[0:4])
                        month = int(clean_date[4:6])
                        day = int(clean_date[6:8])
                        jalali_date_obj = jdatetime.date(year, month, day)
                    elif '/' in clean_date:
                        parts = clean_date.split('/')
                        if len(parts) == 3:
                            year = int(parts[0])
                            month = int(parts[1])
                            day = int(parts[2])
                            jalali_date_obj = jdatetime.date(year, month, day)
                    else:
                        return False
                    
                    return self.set_jalali_date(jalali_date_obj)
                except:
                    return False
        except Exception as e:
            print(f"خطا در تنظیم تاریخ شمسی: {e}")
        
        return False
                
    def get_jalali_date_string(self, format_str="%Y-%m-%d"):
        """دریافت تاریخ شمسی به صورت رشته"""
        jalali_date = self.get_jalali_date()
        if jalali_date:
            try:
                return jalali_date.strftime(format_str)
            except:
                # فرمت ساده
                return f"{jalali_date.year:04d}/{jalali_date.month:02d}/{jalali_date.day:02d}"
        return ""
    
    def text(self):
        """متن تاریخ به صورت شمسی"""
        return self.get_jalali_date_string("%Y/%m/%d")