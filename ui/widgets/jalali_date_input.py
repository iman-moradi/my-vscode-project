# ui/widgets/jalali_date_input.py
from PySide6.QtWidgets import QLineEdit, QHBoxLayout, QPushButton, QWidget
from PySide6.QtCore import Qt, Signal
import jdatetime
from datetime import datetime  # 🔴 اضافه کردن datetime

from .jalali_calendar import JalaliCalendarDialog

class JalaliDateInput(QWidget):
   
    
    date_changed = Signal(jdatetime.date)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)
        
        # فیلد ورود تاریخ
        self.date_input = QLineEdit()
        self.date_input.setPlaceholderText("1403/01/01")
        self.date_input.setMaximumWidth(120)
        self.date_input.setAlignment(Qt.AlignCenter)
        self.date_input.setStyleSheet("""
            QLineEdit {
                padding: 5px;
                border: 1px solid #34495e;
                border-radius: 4px;
                background-color: #2c3e50;
                color: white;
                selection-background-color: #3498db;
                selection-color: white;
            }
            QLineEdit:focus {
                border: 2px solid #3498db;
            }
            QLineEdit::placeholder {
                color: #95a5a6;
            }
        """)
        
        # دکمه تقویم
        self.calendar_button = QPushButton("📅")
        self.calendar_button.setFixedSize(35, 35)
        self.calendar_button.setToolTip("انتخاب از تقویم شمسی")
        self.calendar_button.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border-radius: 4px;
                font-size: 16px;
                border: none;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #21618c;
            }
        """)
        self.calendar_button.clicked.connect(self.open_calendar)
        
        layout.addWidget(self.date_input)
        layout.addWidget(self.calendar_button)
        
        self.setLayout(layout)
        
        # تنظیم تاریخ امروز به صورت پیش‌فرض
        self.set_date_to_today()
    
    def open_calendar(self):
        """باز کردن دیالوگ تقویم شمسی"""
        dialog = JalaliCalendarDialog(self)
        
        # تنظیم تاریخ فعلی در تقویم
        current_date = self.get_date()
        dialog.set_selected_date(current_date)
        
        if dialog.exec():
            selected_date = dialog.get_selected_date()
            self.set_date(selected_date)
            self.date_changed.emit(selected_date)
    
    def set_date_to_today(self):
        """تنظیم تاریخ به امروز شمسی"""
        today_jalali = jdatetime.date.today()
        self.set_date(today_jalali)
        return today_jalali
    
    def set_date(self, jalali_date):
        """تنظیم تاریخ شمسی"""
        if isinstance(jalali_date, jdatetime.date):
            self.date_input.setText(f"{jalali_date.year:04d}/{jalali_date.month:02d}/{jalali_date.day:02d}")
            self.date_changed.emit(jalali_date)
        elif isinstance(jalali_date, str):
            self.date_input.setText(jalali_date)
            # سعی کن رشته را به تاریخ تبدیل کنی
            try:
                parts = jalali_date.replace('-', '/').split('/')
                if len(parts) == 3:
                    year, month, day = map(int, parts)
                    jalali_date_obj = jdatetime.date(year, month, day)
                    self.date_changed.emit(jalali_date_obj)
            except:
                pass
        return True
    
    def get_date(self):
        """دریافت تاریخ شمسی"""
        text = self.date_input.text().strip()
        if text:
            # تبدیل رشته به تاریخ شمسی
            parts = text.replace('-', '/').split('/')
            if len(parts) == 3:
                try:
                    year = int(parts[0])
                    month = int(parts[1])
                    day = int(parts[2])
                    # اعتبارسنجی تاریخ
                    if 1300 <= year <= 1500 and 1 <= month <= 12 and 1 <= day <= 31:
                        return jdatetime.date(year, month, day)
                except:
                    pass
        # در صورت خطا، تاریخ امروز
        return jdatetime.date.today()
    
    def get_date_string(self, format_str="%Y-%m-%d"):
        """دریافت تاریخ شمسی به صورت رشته"""
        jalali_date = self.get_date()
        try:
            return jalali_date.strftime(format_str)
        except:
            return f"{jalali_date.year:04d}-{jalali_date.month:02d}-{jalali_date.day:02d}"
    
    def text(self):
        """متن تاریخ"""
        return self.date_input.text()
    
    # 🔴 اضافه کردن متد clear
    def clear(self):
        """پاک کردن تاریخ"""
        self.date_input.clear()
        # اختیاری: سیگنال بفرستید که تاریخ پاک شد
        # self.date_changed.emit(None)  # اگر سیگنال None را قبول کند
        return True
    
    # 🔴 اضافه کردن متد set_gregorian_date (برای فرم دستگاه‌ها)
    def set_gregorian_date(self, gregorian_date_str):
        """تنظیم تاریخ از روی تاریخ میلادی"""
        if not gregorian_date_str:
            self.clear()
            return False
            
        try:
            # تبدیل رشته به تاریخ میلادی
            if isinstance(gregorian_date_str, str):
                # حذف زمان اگر وجود دارد
                gregorian_date_str = gregorian_date_str.split(' ')[0]
                # جدا کردن تاریخ
                if '-' in gregorian_date_str:
                    parts = gregorian_date_str.split('-')
                elif '/' in gregorian_date_str:
                    parts = gregorian_date_str.split('/')
                else:
                    self.clear()
                    return False
                    
                if len(parts) >= 3:
                    year, month, day = map(int, parts[:3])
                    # ایجاد تاریخ میلادی
                    gregorian_date = datetime(year, month, day).date()
                else:
                    self.clear()
                    return False
            else:
                # احتمالاً شیء date است
                import datetime as dt
                gregorian_date = gregorian_date_str
            
            # تبدیل به شمسی
            jalali_date = jdatetime.date.fromgregorian(date=gregorian_date)
            self.set_date(jalali_date)
            return True
            
        except Exception as e:
            print(f"خطا در تبدیل تاریخ میلادی '{gregorian_date_str}': {e}")
            self.clear()
            return False
    
    # 🔴 اضافه کردن متد get_gregorian_date
    def get_gregorian_date(self):
        """دریافت تاریخ میلادی"""
        jalali_date = self.get_date()
        if jalali_date:
            try:
                gregorian_date = jalali_date.togregorian()
                return gregorian_date.strftime("%Y-%m-%d")
            except:
                return None
        return None
    
    # 🔴 اضافه کردن متد is_valid (اختیاری)
    def is_valid(self):
        """بررسی معتبر بودن تاریخ"""
        text = self.date_input.text().strip()
        if not text:
            return False
        try:
            parts = text.replace('-', '/').split('/')
            if len(parts) == 3:
                year, month, day = map(int, parts)
                # اعتبارسنجی تاریخ
                if 1300 <= year <= 1500 and 1 <= month <= 12 and 1 <= day <= 31:
                    # تلاش برای ایجاد تاریخ
                    jdatetime.date(year, month, day)
                    return True
        except:
            pass
        return False