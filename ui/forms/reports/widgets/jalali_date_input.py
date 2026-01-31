#ui\forms\reports\widgets\jalali_date_input.py

"""
ویجت ورود تاریخ شمسی پیشرفته 
"""

from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QLineEdit, QPushButton,
    QDialog, QVBoxLayout, QLabel, QGridLayout,
    QComboBox, QFrame, QApplication, QCalendarWidget
)
from PySide6.QtCore import Qt, Signal, QEvent, QDate
from PySide6.QtGui import QFont, QMouseEvent
import jdatetime
import re
import sys
import os
from datetime import datetime
from typing import Optional, Union
from datetime import date


class JalaliDateInput(QWidget):
    """
    ویجت ورود تاریخ شمسی پیشرفته برای فرم‌های حسابداری
    
    ویژگی‌های جدید:
    1. دو حالت: edit (ویرایش مستقیم) و display (فقط نمایش با کلیک)
    2. پشتیبانی از ۸ فرمت مختلف تاریخ
    3. اعتبارسنجی پیشرفته با نمایش خطا
    4. محدوده تاریخ قابل تنظیم (min_date, max_date)
    5. تبدیل خودکار به میلادی برای دیتابیس
    6. کلیدهای میانبر (Ctrl+T برای امروز، Ctrl+C برای تقویم)
    7. پشتیبانی از تم تاریک/روشن
    8. نمایش تعطیلات رسمی در تقویم
    9. قابلیت نمایش اعداد فارسی
    """
    
    # سیگنال‌های پیشرفته
    date_changed = Signal(str)  # رشته تاریخ
    date_object_changed = Signal(object)  # شیء jdatetime.date
    validation_changed = Signal(bool)  # وضعیت اعتبارسنجی
    
    # فرمت‌های پشتیبانی شده
    FORMATS = {
        'numeric': '%Y/%m/%d',      # 1403/01/15
        'numeric_dash': '%Y-%m-%d', # 1403-01-15
        'numeric_no_sep': '%Y%m%d', # 14030115
        'long': '%Y %B %d',         # 1403 فروردین 15
        'short': '%y/%m/%d',        # 03/01/15
        'full': '%A %d %B %Y',      # شنبه 15 فروردین 1403
        'database': '%Y-%m-%d',     # برای ذخیره در دیتابیس (میلادی)
        'persian': '%Y/%m/%d',      # ۱۴۰۳/۰۱/۱۵ (اعداد فارسی)
    }
    
    def __init__(self, 
                 parent=None,
                 mode: str = 'edit',  # 'edit' یا 'display'
                 date_format: str = 'numeric',
                 min_date: Optional[jdatetime.date] = None,
                 max_date: Optional[jdatetime.date] = None,
                 show_today_button: bool = True,
                 show_calendar_button: bool = True,
                 theme: str = 'dark'):
        """
        مقداردهی اولیه ویجت
        
        Args:
            parent: والد ویجت
            mode: حالت ویجت ('edit' یا 'display')
            date_format: فرمت تاریخ (از FORMATS)
            min_date: حداقل تاریخ مجاز
            max_date: حداکثر تاریخ مجاز
            show_today_button: نمایش دکمه امروز
            show_calendar_button: نمایش دکمه تقویم
            theme: تم ('dark' یا 'light')
        """
        super().__init__(parent)
        
        # متغیرهای داخلی
        self._current_date = jdatetime.date.today()
        self._mode = mode
        self._date_format = date_format
        self._min_date = min_date
        self._max_date = max_date
        self._theme = theme
        self._is_valid = True
        self._show_today_button = show_today_button
        self._show_calendar_button = show_calendar_button
        
        # تنظیمات اولیه
        self._init_styles()
        self.init_ui()
        self._connect_signals()
        
        # تنظیم تاریخ امروز به صورت پیش‌فرض
        self.set_today()
    
    def _init_styles(self):
        """تعریف استایل‌ها بر اساس تم"""
        if self._theme == 'dark':
            self.STYLES = {
                'line_edit': """
                    QLineEdit {
                        background-color: #222222;
                        border: 2px solid #333333;
                        border-radius: 4px;
                        padding: 8px;
                        color: white;
                        font-family: 'B Nazanin';
                        font-size: 11pt;
                        selection-background-color: #27ae60;
                    }
                    QLineEdit:focus {
                        border-color: #27ae60;
                        background-color: #1a1a1a;
                    }
                    QLineEdit:disabled {
                        background-color: #1a1a1a;
                        color: #666;
                    }
                    QLineEdit[valid="false"] {
                        border-color: #e74c3c;
                        color: #e74c3c;
                    }
                """,
                'button': """
                    QPushButton {
                        background-color: #2c3e50;
                        color: white;
                        border: none;
                        border-radius: 4px;
                        font-family: 'B Nazanin';
                        font-size: 10pt;
                    }
                    QPushButton:hover {
                        background-color: #34495e;
                    }
                    QPushButton:pressed {
                        background-color: #27ae60;
                    }
                    QPushButton:disabled {
                        background-color: #1a1a1a;
                        color: #666;
                    }
                """,
                'today_button': """
                    QPushButton {
                        background-color: #27ae60;
                        color: white;
                        font-weight: bold;
                    }
                    QPushButton:hover {
                        background-color: #219653;
                    }
                """,
                'calendar_button': """
                    QPushButton {
                        background-color: #3498db;
                    }
                    QPushButton:hover {
                        background-color: #2980b9;
                    }
                """
            }
        else:  # light theme
            self.STYLES = {
                'line_edit': """
                    QLineEdit {
                        background-color: #ffffff;
                        border: 2px solid #d1d1d1;
                        border-radius: 4px;
                        padding: 8px;
                        color: #000000;
                        font-family: 'B Nazanin';
                        font-size: 11pt;
                        selection-background-color: #27ae60;
                    }
                    QLineEdit:focus {
                        border-color: #27ae60;
                        background-color: #f8f8f8;
                    }
                    QLineEdit:disabled {
                        background-color: #f0f0f0;
                        color: #999;
                    }
                    QLineEdit[valid="false"] {
                        border-color: #e74c3c;
                        color: #e74c3c;
                    }
                """,
                'button': """
                    QPushButton {
                        background-color: #ecf0f1;
                        color: #2c3e50;
                        border: 1px solid #bdc3c7;
                        border-radius: 4px;
                        font-family: 'B Nazanin';
                        font-size: 10pt;
                    }
                    QPushButton:hover {
                        background-color: #d5dbdb;
                        border-color: #27ae60;
                    }
                    QPushButton:pressed {
                        background-color: #27ae60;
                        color: white;
                    }
                    QPushButton:disabled {
                        background-color: #f8f8f8;
                        color: #ccc;
                    }
                """,
                'today_button': """
                    QPushButton {
                        background-color: #27ae60;
                        color: white;
                        font-weight: bold;
                    }
                    QPushButton:hover {
                        background-color: #219653;
                    }
                """,
                'calendar_button': """
                    QPushButton {
                        background-color: #3498db;
                        color: white;
                    }
                    QPushButton:hover {
                        background-color: #2980b9;
                    }
                """
            }
    
    def init_ui(self):
        """راه‌اندازی رابط کاربری"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)
        
        # فیلد ورود/نمایش تاریخ
        self.date_input = QLineEdit()
        self.date_input.setPlaceholderText("1404/10/06")
        self.date_input.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.date_input.setFixedWidth(130)
        self.date_input.setProperty("valid", "true")
        self.date_input.setStyleSheet(self.STYLES['line_edit'])
        
        if self._mode == 'display':
            self.date_input.setReadOnly(True)
            self.date_input.setCursor(Qt.CursorShape.PointingHandCursor)
            self.date_input.mousePressEvent = self._open_calendar_on_click
        else:
            self.date_input.setToolTip("تاریخ شمسی را وارد کنید یا از تقویم انتخاب نمایید")
        
        layout.addWidget(self.date_input)
        
        # دکمه تقویم (اگر فعال باشد)
        if self._show_calendar_button:
            self.calendar_btn = QPushButton("📅")
            self.calendar_btn.setFixedWidth(40)
            self.calendar_btn.setToolTip("انتخاب از تقویم (Ctrl+C)")
            self.calendar_btn.clicked.connect(self.show_calendar)
            self.calendar_btn.setStyleSheet(self.STYLES['button'] + self.STYLES['calendar_button'])
            layout.addWidget(self.calendar_btn)
        
        # دکمه امروز (اگر فعال باشد)
        if self._show_today_button:
            self.today_btn = QPushButton("امروز")
            self.today_btn.setFixedWidth(60)
            self.today_btn.setToolTip("تنظیم تاریخ امروز (Ctrl+T)")
            self.today_btn.clicked.connect(self.set_today)
            self.today_btn.setStyleSheet(self.STYLES['button'] + self.STYLES['today_button'])
            layout.addWidget(self.today_btn)
        
        # برچسب نمایش خطا
        self.error_label = QLabel()
        self.error_label.setVisible(False)
        self.error_label.setStyleSheet("""
            QLabel {
                color: #e74c3c;
                font-size: 9pt;
                font-family: 'B Nazanin';
                padding: 2px 4px;
            }
        """)
        layout.addWidget(self.error_label)
        
        # تنظیم فیلتر رویداد برای کلیدهای میانبر
        self.date_input.installEventFilter(self)
    
    def _connect_signals(self):
        """اتصال سیگنال‌ها"""
        self.date_input.textChanged.connect(self.on_text_changed)
        self.date_input.returnPressed.connect(self._validate_and_emit)
    
    def eventFilter(self, obj, event):
        """فیلتر رویداد برای کلیدهای میانبر"""
        if obj == self.date_input and event.type() == QEvent.Type.KeyPress:
            key_event = event
            # Ctrl+T برای تاریخ امروز
            if (key_event.modifiers() == Qt.KeyboardModifier.ControlModifier and 
                key_event.key() == Qt.Key.Key_T):
                self.set_today()
                return True
            # Ctrl+C برای باز کردن تقویم
            elif (key_event.modifiers() == Qt.KeyboardModifier.ControlModifier and 
                  key_event.key() == Qt.Key.Key_C):
                self.show_calendar()
                return True
            # Escape برای پاک کردن
            elif key_event.key() == Qt.Key.Key_Escape:
                self.clear()
                return True
        
        return super().eventFilter(obj, event)
    
    def _open_calendar_on_click(self, event):
        """باز کردن تقویم با کلیک روی فیلد (در حالت display)"""
        self.show_calendar()
    
    def set_today(self):
        """تنظیم تاریخ امروز شمسی"""
        today = jdatetime.date.today()
        self._set_date_internal(today)
    
    def show_calendar(self):
        """نمایش تقویم شمسی پیشرفته"""
        dialog = AdvancedJalaliCalendarDialog(
            initial_date=self._current_date,
            min_date=self._min_date,
            max_date=self._max_date,
            theme=self._theme,
            parent=self
        )
        
        if dialog.exec():
            selected_date = dialog.get_selected_date()
            if selected_date:
                self._set_date_internal(selected_date)
    
    def on_text_changed(self, text):
        """اعتبارسنجی و فرمت کردن تاریخ وارد شده"""
        text = text.strip()
        if not text:
            return
        
        # حذف کاراکترهای غیرعددی به جز اسلش و خط تیره
        cleaned = re.sub(r'[^\d/\-\.]', '', text)
        
        # محدود کردن طول
        if len(cleaned) > 10:
            cleaned = cleaned[:10]
        
        # فرمت کردن به صورت خودکار
        if '/' not in cleaned and '-' not in cleaned and len(cleaned) >= 8:
            # اگر کاربر 14041006 وارد کرده، به 1404/10/06 تبدیل کن
            year = cleaned[:4]
            month = cleaned[4:6] if len(cleaned) >= 6 else ''
            day = cleaned[6:8] if len(cleaned) >= 8 else ''
            
            if self._date_format == 'numeric_dash':
                cleaned = f"{year}-{month}-{day}"
            else:  # numeric (default)
                cleaned = f"{year}/{month}/{day}"
        
        if self.date_input.text() != cleaned:
            self.date_input.setText(cleaned)
            self.date_input.setCursorPosition(len(cleaned))
        
        # اعتبارسنجی
        self._validate_and_emit()
    
    def _validate_and_emit(self):
        """اعتبارسنجی تاریخ و ارسال سیگنال"""
        date_str = self.date_input.text().strip()
        
        if not date_str:
            self._is_valid = True
            self.date_input.setProperty("valid", "true")
            self.date_input.style().polish(self.date_input)
            self.error_label.clear()
            self.error_label.setVisible(False)
            self.validation_changed.emit(True)
            return
        
        # تبدیل رشته به تاریخ
        jalali_date = self._parse_date_string(date_str)
        
        if jalali_date is None:
            self._is_valid = False
            self.date_input.setProperty("valid", "false")
            self.date_input.style().polish(self.date_input)
            self.error_label.setText("⚠ تاریخ نامعتبر است")
            self.error_label.setVisible(True)
            self.validation_changed.emit(False)
            return
        
        # بررسی محدوده تاریخ
        if not self._check_date_range(jalali_date):
            self._is_valid = False
            self.date_input.setProperty("valid", "false")
            self.date_input.style().polish(self.date_input)
            
            if self._min_date and self._max_date:
                msg = f"⚠ تاریخ باید بین {self._min_date} و {self._max_date} باشد"
            elif self._min_date:
                msg = f"⚠ تاریخ باید از {self._min_date} به بعد باشد"
            elif self._max_date:
                msg = f"⚠ تاریخ باید تا {self._max_date} باشد"
            else:
                msg = "⚠ تاریخ خارج از محدوده مجاز است"
            
            self.error_label.setText(msg)
            self.error_label.setVisible(True)
            self.validation_changed.emit(False)
            return
        
        # تاریخ معتبر است
        self._is_valid = True
        self._current_date = jalali_date
        self.date_input.setProperty("valid", "true")
        self.date_input.style().polish(self.date_input)
        self.error_label.clear()
        self.error_label.setVisible(False)
        
        # ارسال سیگنال‌ها
        date_str_formatted = self._format_date(jalali_date)
        self.date_changed.emit(date_str_formatted)
        self.date_object_changed.emit(jalali_date)
        self.validation_changed.emit(True)
    
    def _parse_date_string(self, date_str: str) -> Optional[jdatetime.date]:
        """تبدیل رشته به تاریخ شمسی"""
        if not date_str:
            return None
        
        try:
            # تشخیص فرمت و تبدیل
            formats_to_try = [
                '%Y/%m/%d', '%Y-%m-%d', '%Y%m%d',
                '%y/%m/%d', '%y-%m-%d', '%y%m%d'
            ]
            
            for fmt in formats_to_try:
                try:
                    # حذف فاصله‌های اضافی
                    cleaned = date_str.strip().replace(' ', '')
                    return jdatetime.datetime.strptime(cleaned, fmt).date()
                except ValueError:
                    continue
            
            return None
            
        except Exception:
            return None
    
    def _check_date_range(self, date: jdatetime.date) -> bool:
        """بررسی محدوده تاریخ"""
        if self._min_date and date < self._min_date:
            return False
        if self._max_date and date > self._max_date:
            return False
        return True
    
    def _format_date(self, date: jdatetime.date) -> str:
        """فرمت‌دهی تاریخ"""
        if self._date_format == 'persian':
            return self._to_persian_numbers(date.strftime('%Y/%m/%d'))
        elif self._date_format in self.FORMATS:
            return date.strftime(self.FORMATS[self._date_format])
        else:
            return date.strftime('%Y/%m/%d')
    
    def _set_date_internal(self, date_obj: Union[jdatetime.date, datetime, str]):
        """تنظیم داخلی تاریخ"""
        # تبدیل به تاریخ شمسی
        jalali_date = None
        
        if isinstance(date_obj, jdatetime.date):
            jalali_date = date_obj
        elif isinstance(date_obj, jdatetime.datetime):
            jalali_date = date_obj.date()
        elif isinstance(date_obj, datetime):
            jalali_date = jdatetime.date.fromgregorian(date=date_obj.date())
        elif isinstance(date_obj, str):
            jalali_date = self._parse_date_string(date_obj)
        
        if jalali_date is None:
            jalali_date = jdatetime.date.today()
        
        # بررسی محدوده
        if not self._check_date_range(jalali_date):
            print(f"⚠ تاریخ {jalali_date} خارج از محدوده مجاز است")
            jalali_date = jdatetime.date.today()
        
        # تنظیم تاریخ
        self._current_date = jalali_date
        date_str = self._format_date(jalali_date)
        self.date_input.setText(date_str)
        
        # اعتبارسنجی و ارسال سیگنال
        self._validate_and_emit()
    
    # ------------------ متدهای عمومی (API اصلی) ------------------
    
    # در کلاس JalaliDateInput، متد get_date را اصلاح کنید:
    def get_date(self) -> Optional[str]:
        """
        دریافت تاریخ شمسی وارد شده به صورت رشته
        برمی‌گرداند: رشته تاریخ یا None اگر نامعتبر باشد
        """
        if not self._is_valid:
            return None
        
        # اگر فیلد خالی است
        if not self.date_input.text().strip():
            return None
        
        return self._format_date(self._current_date)
    
    def get_date_object(self) -> Optional[jdatetime.date]:
        """
        دریافت تاریخ شمسی به صورت شیء
        برمی‌گرداند: jdatetime.date یا None اگر نامعتبر باشد
        """
        return self._current_date if self._is_valid else None
    
    def get_date_for_database(self) -> Optional[str]:
        """
        دریافت تاریخ برای ذخیره در دیتابیس (به میلادی تبدیل می‌کند)
        برمی‌گرداند: رشته تاریخ میلادی یا None اگر نامعتبر باشد
        """
        if not self._is_valid or self._current_date is None:
            return None
        
        try:
            gregorian_obj = self._current_date.togregorian()
            return gregorian_obj.strftime("%Y-%m-%d")
        except:
            return None
    
    def set_date(self, date_str):
        """تنظیم تاریخ از رشته"""
        if date_str:
            # اگر تاریخ میلادی است، به شمسی تبدیل کن
            if re.match(r'^\d{4}-\d{2}-\d{2}$', str(date_str)):
                try:
                    year, month, day = map(int, date_str.split('-'))
                    from datetime import date as datetime_date
                    gdate = datetime_date(year, month, day)
                    jdate = jdatetime.date.fromgregorian(date=gdate)
                    date_str = jdate.strftime("%Y/%m/%d")
                except:
                    pass
            
            self._set_date_internal(date_str)
    
    def clear(self):
        """پاک کردن فیلد تاریخ"""
        self.date_input.clear()
        self._is_valid = True
        self.date_input.setProperty("valid", "true")
        self.date_input.style().polish(self.date_input)
        self.error_label.clear()
        self.error_label.setVisible(False)
        self.validation_changed.emit(True)
    
    def set_date_string(self, date_string, format_str="%Y/%m/%d"):
        """
        تنظیم تاریخ از روی رشته با فرمت مشخص
        
        Args:
            date_string: رشته تاریخ شمسی مانند '1404/11/06'
            format_str: فرمت رشته ورودی
        """
        try:
            if not date_string:
                return
            
            # تبدیل رشته به تاریخ شمسی
            jalali_date = jdatetime.datetime.strptime(date_string, format_str).date()
            self._set_date_internal(jalali_date)
        except ValueError as e:
            print(f"⚠️ خطا در تبدیل رشته تاریخ: {e}")
            # در صورت خطا، تاریخ امروز را تنظیم کن
            self.set_today()
    
    def is_valid(self) -> bool:
        """بررسی آیا تاریخ وارد شده معتبر است"""
        return self._is_valid
    
    def set_min_date(self, min_date: Optional[jdatetime.date]):
        """تنظیم حداقل تاریخ مجاز"""
        self._min_date = min_date
        self._validate_and_emit()
    
    def set_max_date(self, max_date: Optional[jdatetime.date]):
        """تنظیم حداکثر تاریخ مجاز"""
        self._max_date = max_date
        self._validate_and_emit()
    
    def set_date_format(self, format_name: str):
        """تنظیم فرمت نمایش تاریخ"""
        if format_name in self.FORMATS:
            self._date_format = format_name
            self._set_date_internal(self._current_date)
    
    def set_mode(self, mode: str):
        """تغییر حالت ویجت (edit/display)"""
        self._mode = mode
        if mode == 'display':
            self.date_input.setReadOnly(True)
            self.date_input.setCursor(Qt.CursorShape.PointingHandCursor)
            self.date_input.mousePressEvent = self._open_calendar_on_click
        else:
            self.date_input.setReadOnly(False)
            self.date_input.mousePressEvent = None
            self.date_input.setCursor(Qt.CursorShape.IBeamCursor)
    
    def set_theme(self, theme: str):
        """تغییر تم (dark/light)"""
        self._theme = theme
        self._init_styles()
        self.date_input.setStyleSheet(self.STYLES['line_edit'])
        
        if hasattr(self, 'today_btn'):
            self.today_btn.setStyleSheet(self.STYLES['button'] + self.STYLES['today_button'])
        if hasattr(self, 'calendar_btn'):
            self.calendar_btn.setStyleSheet(self.STYLES['button'] + self.STYLES['calendar_button'])
    
    # ------------------ متدهای کمکی ------------------
    
    @staticmethod
    def _to_persian_numbers(text: str) -> str:
        """تبدیل اعداد انگلیسی به فارسی"""
        persian_nums = {
            '0': '۰', '1': '۱', '2': '۲', '3': '۳', '4': '۴',
            '5': '۵', '6': '۶', '7': '۷', '8': '۸', '9': '۹',
            '/': '/', '-': '-', '.': '.'
        }
        
        result = []
        for char in text:
            result.append(persian_nums.get(char, char))
        
        return ''.join(result)


class AdvancedJalaliCalendarDialog(QDialog):
    """
    دیالوگ تقویم شمسی پیشرفته
    
    ویژگی‌ها:
    - نمایش ماه‌های قبل و بعد
    - انتخاب سریع سال و ماه
    - برجسته‌سازی روزهای خاص
    - محدوده تاریخ قابل تنظیم
    - نمایش تعطیلات رسمی ایران
    """
    
    # تعطیلات رسمی ایران (شمسی)
    HOLIDAYS = {
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
    
    # روزهای هفته
    WEEKDAYS = ["ش", "ی", "د", "س", "چ", "پ", "ج"]
    WEEKDAYS_FULL = ["شنبه", "یکشنبه", "دوشنبه", "سه‌شنبه", "چهارشنبه", "پنجشنبه", "جمعه"]
    
    # نام ماه‌ها
    MONTH_NAMES = [
        "فروردین", "اردیبهشت", "خرداد",
        "تیر", "مرداد", "شهریور",
        "مهر", "آبان", "آذر",
        "دی", "بهمن", "اسفند"
    ]
    
    def __init__(self, 
                 initial_date: jdatetime.date = None,
                 min_date: jdatetime.date = None,
                 max_date: jdatetime.date = None,
                 theme: str = 'dark',
                 parent=None):
        """
        مقداردهی اولیه تقویم
        """
        super().__init__(parent)
        
        self._current_date = initial_date or jdatetime.date.today()
        self._min_date = min_date
        self._max_date = max_date
        self._theme = theme
        self._selected_date = self._current_date
        
        self._init_styles()
        self._setup_ui()
        self._update_calendar()
        
        self.setWindowTitle("تقویم شمسی")
        self.setFixedSize(450, 500)
    
    def _init_styles(self):
        """تعریف استایل‌ها"""
        if self._theme == 'dark':
            self.STYLES = {
                'dialog': """
                    QDialog {
                        background-color: #111111;
                        border: 2px solid #2c3e50;
                        border-radius: 10px;
                    }
                """,
                'header': """
                    QFrame {
                        background-color: #1a252f;
                        border-radius: 8px;
                        padding: 10px;
                    }
                """,
                'day_button': """
                    QPushButton {
                        background-color: #2d2d30;
                        border: 1px solid #3d3d3d;
                        border-radius: 4px;
                        color: #ffffff;
                        font-size: 13px;
                        min-width: 40px;
                        min-height: 40px;
                        font-family: 'B Nazanin';
                    }
                    QPushButton:hover {
                        background-color: #323233;
                        border-color: #27ae60;
                    }
                    QPushButton:pressed {
                        background-color: #27ae60;
                    }
                """,
                'today_button': """
                    QPushButton {
                        background-color: #27ae60;
                        font-weight: bold;
                    }
                """,
                'selected_button': """
                    QPushButton {
                        background-color: #3498db;
                        font-weight: bold;
                        border: 2px solid #27ae60;
                    }
                """,
                'holiday_button': """
                    QPushButton {
                        color: #ff6b6b;
                        font-weight: bold;
                    }
                """,
                'disabled_button': """
                    QPushButton {
                        background-color: #1a1a1a;
                        color: #666;
                        border-color: #2d2d2d;
                    }
                    QPushButton:hover {
                        background-color: #1a1a1a;
                        border-color: #2d2d2d;
                    }
                """
            }
        else:  # light theme
            self.STYLES = {
                'dialog': """
                    QDialog {
                        background-color: #f8f9fa;
                        border: 2px solid #dee2e6;
                        border-radius: 10px;
                    }
                """,
                'header': """
                    QFrame {
                        background-color: #e9ecef;
                        border-radius: 8px;
                        padding: 10px;
                    }
                """,
                'day_button': """
                    QPushButton {
                        background-color: #ffffff;
                        border: 1px solid #dee2e6;
                        border-radius: 4px;
                        color: #212529;
                        font-size: 13px;
                        min-width: 40px;
                        min-height: 40px;
                        font-family: 'B Nazanin';
                    }
                    QPushButton:hover {
                        background-color: #f8f9fa;
                        border-color: #27ae60;
                    }
                    QPushButton:pressed {
                        background-color: #27ae60;
                        color: white;
                    }
                """,
                'today_button': """
                    QPushButton {
                        background-color: #27ae60;
                        color: white;
                        font-weight: bold;
                    }
                """,
                'selected_button': """
                    QPushButton {
                        background-color: #3498db;
                        color: white;
                        font-weight: bold;
                        border: 2px solid #27ae60;
                    }
                """,
                'holiday_button': """
                    QPushButton {
                        color: #e74c3c;
                        font-weight: bold;
                    }
                """,
                'disabled_button': """
                    QPushButton {
                        background-color: #f8f9fa;
                        color: #adb5bd;
                        border-color: #e9ecef;
                    }
                    QPushButton:hover {
                        background-color: #f8f9fa;
                        border-color: #e9ecef;
                    }
                """
            }
    
    def _setup_ui(self):
        """راه‌اندازی رابط کاربری تقویم"""
        self.setStyleSheet(self.STYLES['dialog'])
        
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(15, 15, 15, 15)
        
        # هدر - ناوبری
        header_frame = QFrame()
        header_frame.setStyleSheet(self.STYLES['header'])
        header_layout = QHBoxLayout(header_frame)
        
        # دکمه ماه قبل
        prev_month_btn = QPushButton("◀")
        prev_month_btn.clicked.connect(self._prev_month)
        prev_month_btn.setFixedSize(40, 40)
        prev_month_btn.setStyleSheet(self.STYLES['day_button'])
        
        # دکمه ماه بعد
        next_month_btn = QPushButton("▶")
        next_month_btn.clicked.connect(self._next_month)
        next_month_btn.setFixedSize(40, 40)
        next_month_btn.setStyleSheet(self.STYLES['day_button'])
        
        # کامبوباکس سال
        self.year_combo = QComboBox()
        current_year = self._current_date.year
        for year in range(current_year - 10, current_year + 11):
            self.year_combo.addItem(str(year), year)
        self.year_combo.setCurrentText(str(current_year))
        self.year_combo.currentIndexChanged.connect(self._on_date_component_changed)
        
        # کامبوباکس ماه
        self.month_combo = QComboBox()
        for i, month_name in enumerate(self.MONTH_NAMES, 1):
            self.month_combo.addItem(month_name, i)
        self.month_combo.setCurrentIndex(self._current_date.month - 1)
        self.month_combo.currentIndexChanged.connect(self._on_date_component_changed)
        
        # برچسب تاریخ انتخاب شده
        self.selected_label = QLabel()
        self.selected_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.selected_label.setStyleSheet("""
            QLabel {
                font-size: 14px;
                font-weight: bold;
                padding: 10px;
                border-radius: 6px;
                background-color: #2c3e50;
                color: white;
                font-family: 'B Nazanin';
            }
        """)
        
        # افزودن ویجت‌ها به هدر
        header_layout.addWidget(prev_month_btn)
        header_layout.addWidget(self.year_combo)
        header_layout.addWidget(self.month_combo)
        header_layout.addWidget(next_month_btn)
        
        layout.addWidget(header_frame)
        layout.addWidget(self.selected_label)
        
        # شبکه روزهای هفته
        weekdays_layout = QGridLayout()
        weekdays_layout.setSpacing(3)
        
        for i, day in enumerate(self.WEEKDAYS):
            label = QLabel(day)
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            label.setStyleSheet("""
                QLabel {
                    font-weight: bold;
                    font-size: 12px;
                    padding: 5px;
                    color: #3498db;
                    font-family: 'B Nazanin';
                }
            """)
            weekdays_layout.addWidget(label, 0, i)
        
        # شبکه روزهای ماه
        self.calendar_grid = QGridLayout()
        self.calendar_grid.setSpacing(3)
        
        layout.addLayout(weekdays_layout)
        layout.addLayout(self.calendar_grid)
        
        # پانل پایین - دکمه‌ها
        button_layout = QHBoxLayout()
        
        # دکمه امروز
        today_btn = QPushButton("📅 امروز")
        today_btn.clicked.connect(self._set_today)
        today_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                font-weight: bold;
                padding: 10px 20px;
                border-radius: 6px;
                font-family: 'B Nazanin';
            }
            QPushButton:hover {
                background-color: #219653;
            }
        """)
        
        # دکمه تأیید
        confirm_btn = QPushButton("✅ تأیید")
        confirm_btn.clicked.connect(self.accept)
        confirm_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                font-weight: bold;
                padding: 10px 20px;
                border-radius: 6px;
                font-family: 'B Nazanin';
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        
        # دکمه انصراف
        cancel_btn = QPushButton("❌ انصراف")
        cancel_btn.clicked.connect(self.reject)
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                font-weight: bold;
                padding: 10px 20px;
                border-radius: 6px;
                font-family: 'B Nazanin';
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        
        button_layout.addWidget(today_btn)
        button_layout.addStretch()
        button_layout.addWidget(confirm_btn)
        button_layout.addWidget(cancel_btn)
        
        layout.addStretch()
        layout.addLayout(button_layout)
        
        # بروزرسانی نمایش
        self._update_selected_label()
    
    def _update_calendar(self):
        """بروزرسانی نمایش تقویم"""
        # پاک کردن روزهای قبلی
        for i in reversed(range(self.calendar_grid.count())):
            widget = self.calendar_grid.itemAt(i).widget()
            if widget:
                widget.deleteLater()
        
        # دریافت سال و ماه انتخاب شده
        year = int(self.year_combo.currentText())
        month = self.month_combo.currentData()
        
        if month is None:
            month = 1
        
        # محاسبه روز اول ماه
        try:
            first_day = jdatetime.date(year, month, 1)
            start_weekday = first_day.weekday()  # 0=شنبه, 6=جمعه
            
            # تعداد روزهای ماه
            if month <= 6:
                days_in_month = 31
            elif month <= 11:
                days_in_month = 30
            else:  # اسفند
                days_in_month = 29 if jdatetime.jalali.isleap(year) else 28
        except:
            return
        
        # پر کردن تقویم
        day = 1
        row = 0
        
        while day <= days_in_month:
            for col in range(7):
                if day == 1 and col < start_weekday:
                    # خانه‌های خالی قبل از روز اول
                    empty_label = QLabel()
                    empty_label.setFixedSize(40, 40)
                    self.calendar_grid.addWidget(empty_label, row, col)
                    continue
                
                if day > days_in_month:
                    break
                
                # ایجاد دکمه روز
                day_btn = QPushButton(str(day))
                day_btn.setFixedSize(40, 40)
                
                # تعیین وضعیت روز
                current_date = jdatetime.date(year, month, day)
                is_today = (current_date == jdatetime.date.today())
                is_selected = (current_date == self._selected_date)
                is_holiday = (current_date.weekday() == 6)  # جمعه
                is_official_holiday = (month, day) in self.HOLIDAYS
                
                # اعمال استایل‌ها
                style = self.STYLES['day_button']
                
                if is_today:
                    style += self.STYLES['today_button']
                if is_selected:
                    style += self.STYLES['selected_button']
                if is_holiday or is_official_holiday:
                    style += self.STYLES['holiday_button']
                
                # بررسی محدوده تاریخ
                if self._min_date and current_date < self._min_date:
                    style += self.STYLES['disabled_button']
                    day_btn.setEnabled(False)
                elif self._max_date and current_date > self._max_date:
                    style += self.STYLES['disabled_button']
                    day_btn.setEnabled(False)
                else:
                    day_btn.clicked.connect(lambda checked, d=day: self._select_day(d))
                
                day_btn.setStyleSheet(style)
                
                # نمایش تعطیلات رسمی
                if is_official_holiday:
                    day_btn.setToolTip(self.HOLIDAYS[(month, day)])
                
                self.calendar_grid.addWidget(day_btn, row, col)
                day += 1
            
            row += 1
        
        self._update_selected_label()
    
    def _update_selected_label(self):
        """بروزرسانی نمایش تاریخ انتخاب شده"""
        date_str = f"{self._selected_date.year}/{self._selected_date.month:02d}/{self._selected_date.day:02d}"
        
        weekday = self.WEEKDAYS_FULL[self._selected_date.weekday()]
        month_name = self.MONTH_NAMES[self._selected_date.month - 1]
        
        display_text = f"📅 {weekday}، {self._selected_date.day} {month_name} {self._selected_date.year}"
        self.selected_label.setText(display_text)
    
    def _select_day(self, day):
        """انتخاب روز"""
        year = int(self.year_combo.currentText())
        month = self.month_combo.currentData()
        
        if month is None:
            month = 1
            
        self._selected_date = jdatetime.date(year, month, day)
        self._update_calendar()
    
    def _prev_month(self):
        """ماه قبل"""
        current_month = self.month_combo.currentData()
        current_year = int(self.year_combo.currentText())
        
        if current_month == 1:
            new_month = 12
            new_year = current_year - 1
        else:
            new_month = current_month - 1
            new_year = current_year
        
        self.year_combo.setCurrentText(str(new_year))
        self.month_combo.setCurrentIndex(new_month - 1)
    
    def _next_month(self):
        """ماه بعد"""
        current_month = self.month_combo.currentData()
        current_year = int(self.year_combo.currentText())
        
        if current_month == 12:
            new_month = 1
            new_year = current_year + 1
        else:
            new_month = current_month + 1
            new_year = current_year
        
        self.year_combo.setCurrentText(str(new_year))
        self.month_combo.setCurrentIndex(new_month - 1)
    
    def _set_today(self):
        """تنظیم تاریخ امروز"""
        today = jdatetime.date.today()
        self._selected_date = today
        self.year_combo.setCurrentText(str(today.year))
        self.month_combo.setCurrentIndex(today.month - 1)
        self._update_calendar()
    
    def _on_date_component_changed(self):
        """واکنش به تغییر سال یا ماه"""
        self._update_calendar()
    
    def get_selected_date(self) -> jdatetime.date:
        """دریافت تاریخ انتخاب شده"""
        return self._selected_date


# در ui/forms/accounting/widgets/jalali_date_input.py

class JalaliCalendarDialog(QDialog):
    """دیالوگ تقویم شمسی - نسخه کامل"""
    def __init__(self, parent=None, initial_date=None):
        super().__init__(parent)
        self.setWindowTitle("📅 تقویم شمسی")
        self.setMinimumSize(400, 400)
        
        # کد کامل دیالوگ تقویم
        layout = QVBoxLayout()
        
        # ایجاد ویجت تقویم شمسی
        self.calendar = QCalendarWidget()
        self.calendar.setGridVisible(True)
        
        # تنظیم تاریخ اولیه
        if initial_date:
            # تبدیل تاریخ شمسی به QDate
            try:
                if isinstance(initial_date, str):
                    # فرض بر اینکه تاریخ شمسی است: 1404/11/07
                    parts = initial_date.split('/')
                    if len(parts) == 3:
                        year, month, day = map(int, parts)
                        # تبدیل شمسی به میلادی
                        jalali_date = jdatetime.date(year, month, day)
                        gregorian_date = jalali_date.togregorian()
                        qdate = QDate(gregorian_date.year, gregorian_date.month, gregorian_date.day)
                        self.calendar.setSelectedDate(qdate)
            except:
                pass
        
        layout.addWidget(self.calendar)
        
        # دکمه‌ها
        btn_layout = QHBoxLayout()
        self.btn_ok = QPushButton("تأیید")
        self.btn_cancel = QPushButton("انصراف")
        
        self.btn_ok.clicked.connect(self.accept)
        self.btn_cancel.clicked.connect(self.reject)
        
        btn_layout.addWidget(self.btn_ok)
        btn_layout.addWidget(self.btn_cancel)
        
        layout.addLayout(btn_layout)
        self.setLayout(layout)
    
    def get_date(self):
        """دریافت تاریخ انتخاب شده به صورت شمسی"""
        selected_date = self.calendar.selectedDate()
        # تبدیل میلادی به شمسی
        gregorian_date = date(selected_date.year(), selected_date.month(), selected_date.day())
        jalali_date = jdatetime.date.fromgregorian(date=gregorian_date)
        return jalali_date.strftime("%Y/%m/%d")

    # ------------------ توابع کمکی برای سازگاری ------------------

    def create_jalali_date_widget(mode='edit', **kwargs):
        """
        تابع کمکی برای ایجاد ویجت تاریخ شمسی
        
        Args:
            mode: 'edit' یا 'display'
            **kwargs: سایر پارامترهای JalaliDateInput
        
        Returns:
            JalaliDateInput
        """
        return JalaliDateInput(mode=mode, **kwargs)


# ------------------ تست ویجت ------------------

if __name__ == "__main__":
    import sys
    
    app = QApplication(sys.argv)
    
    # تنظیم فونت فارسی
    font = QFont("B Nazanin", 11)
    app.setFont(font)
    
    # ایجاد ویندوز تست
    window = QWidget()
    window.setWindowTitle("تست ویجت تاریخ شمسی پیشرفته - ماژول حسابداری")
    window.setGeometry(100, 100, 600, 400)
    
    layout = QVBoxLayout(window)
    
    # ویجت ۱: حالت ویرایش با دکمه‌ها
    label1 = QLabel("حالت ویرایش (Edit Mode) با دکمه‌ها:")
    widget1 = JalaliDateInput(mode='edit', theme='dark')
    
    # ویجت ۲: حالت نمایش (کلیک روی فیلد)
    label2 = QLabel("حالت نمایش (Display Mode) - کلیک روی فیلد:")
    widget2 = JalaliDateInput(mode='display', theme='dark', 
                                        show_today_button=False, 
                                        show_calendar_button=False)
    
    # ویجت ۳: با فرمت فارسی و تم روشن
    label3 = QLabel("فرمت فارسی با تم روشن:")
    widget3 = JalaliDateInput(mode='edit', date_format='persian', theme='light')
    
    # دکمه برای نمایش اطلاعات
    info_btn = QPushButton("نمایش اطلاعات ویجت‌ها")
    
    def show_info():
        print("\n" + "="*50)
        print("اطلاعات ویجت‌ها:")
        
        for i, (name, widget) in enumerate([("ویجت ۱", widget1), 
                                           ("ویجت ۲", widget2), 
                                           ("ویجت ۳", widget3)], 1):
            date_str = widget.get_date()
            date_obj = widget.get_date_object()
            db_date = widget.get_date_for_database()
            is_valid = widget.is_valid()
            
            print(f"\n{name}:")
            print(f"  رشته تاریخ: {date_str}")
            print(f"  شیء تاریخ: {date_obj}")
            print(f"  تاریخ دیتابیس: {db_date}")
            print(f"  معتبر است: {is_valid}")
    
    info_btn.clicked.connect(show_info)
    
    # اتصال سیگنال‌ها برای نمایش تغییرات
    def on_date_changed(date_str):
        print(f"تاریخ تغییر کرد: {date_str}")
    
    def on_validation_changed(is_valid):
        print(f"اعتبارسنجی تغییر کرد: {is_valid}")
    
    widget1.date_changed.connect(on_date_changed)
    widget1.validation_changed.connect(on_validation_changed)
    
    # افزودن به layout
    layout.addWidget(label1)
    layout.addWidget(widget1)
    layout.addWidget(label2)
    layout.addWidget(widget2)
    layout.addWidget(label3)
    layout.addWidget(widget3)
    layout.addWidget(info_btn)
    layout.addStretch()
    
    window.show()
    sys.exit(app.exec())