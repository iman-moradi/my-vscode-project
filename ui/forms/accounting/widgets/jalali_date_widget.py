"""
ویجت تاریخ شمسی حرفه‌ای - نسخه بهینه شده برای PySide6
پشتیبانی از: PySide6 - jdatetime
"""

import os
import sys
from datetime import datetime
import re
import jdatetime
from typing import Optional, Union, Tuple, Dict, Any

# import های PySide6
from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *

# تنظیم Signal و Slot برای PySide6
Signal = Signal
Slot = Slot


class JalaliDateWidget(QWidget):
    """
    ویجت تاریخ شمسی حرفه‌ای با پشتیبانی کامل
    
    ویژگی‌ها:
    - دو حالت: فقط نمایش یا ورود مستقیم
    - پشتیبانی از ۸ فرمت مختلف تاریخ
    - اعتبارسنجی خودکار
    - محدوده تاریخ قابل تنظیم
    - تبدیل خودکار به میلادی برای دیتابیس
    - پشتیبانی از تم تاریک/روشن
    - کلیدهای میانبر (Ctrl+T برای امروز، Ctrl+C برای تقویم)
    """
    
    # سیگنال‌ها
    date_changed = Signal(object)  # تاریخ شمسی (jdatetime.date)
    date_string_changed = Signal(str)  # رشته تاریخ
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
                 show_buttons: bool = True,
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
            show_buttons: نمایش دکمه‌ها
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
        self._show_buttons = show_buttons
        self._show_today_button = show_today_button
        self._show_calendar_button = show_calendar_button
        
        # تنظیمات اولیه
        self._init_styles()
        self._setup_ui()
        self._connect_signals()
        
        # تنظیم تاریخ امروز
        self.set_date(self._current_date)
    
    def _init_styles(self):
        """تعریف استایل‌ها بر اساس تم"""
        if self._theme == 'dark':
            self.STYLES = {
                'widget': """
                    QWidget {
                        background-color: transparent;
                    }
                """,
                'line_edit': """
                    QLineEdit {
                        background-color: #2d2d2d;
                        border: 2px solid #3d3d3d;
                        border-radius: 6px;
                        padding: 8px 12px;
                        color: #ffffff;
                        font-family: 'B Nazanin', 'Segoe UI';
                        font-size: 13px;
                        selection-background-color: #0078d7;
                    }
                    QLineEdit:focus {
                        border-color: #0078d7;
                        background-color: #1e1e1e;
                    }
                    QLineEdit:disabled {
                        background-color: #1a1a1a;
                        color: #666;
                    }
                    QLineEdit[valid="false"] {
                        border-color: #d13438;
                        color: #d13438;
                    }
                """,
                'button': """
                    QPushButton {
                        background-color: #323233;
                        border: 1px solid #3d3d3d;
                        border-radius: 4px;
                        padding: 6px 12px;
                        color: #ffffff;
                        font-family: 'Segoe UI';
                        font-size: 12px;
                        min-height: 24px;
                    }
                    QPushButton:hover {
                        background-color: #424245;
                        border-color: #0078d7;
                    }
                    QPushButton:pressed {
                        background-color: #0078d7;
                    }
                    QPushButton:disabled {
                        background-color: #1a1a1a;
                        color: #666;
                    }
                """,
                'today_button': """
                    QPushButton {
                        background-color: #0c6c0c;
                        color: white;
                        font-weight: bold;
                    }
                    QPushButton:hover {
                        background-color: #0e7c0e;
                    }
                """,
                'calendar_button': """
                    QPushButton {
                        background-color: #004578;
                    }
                    QPushButton:hover {
                        background-color: #005a9e;
                    }
                """
            }
        else:  # light theme
            self.STYLES = {
                'widget': """
                    QWidget {
                        background-color: transparent;
                    }
                """,
                'line_edit': """
                    QLineEdit {
                        background-color: #ffffff;
                        border: 2px solid #d1d1d1;
                        border-radius: 6px;
                        padding: 8px 12px;
                        color: #000000;
                        font-family: 'B Nazanin', 'Segoe UI';
                        font-size: 13px;
                        selection-background-color: #0078d7;
                    }
                    QLineEdit:focus {
                        border-color: #0078d7;
                        background-color: #f8f8f8;
                    }
                    QLineEdit:disabled {
                        background-color: #f0f0f0;
                        color: #999;
                    }
                    QLineEdit[valid="false"] {
                        border-color: #d13438;
                        color: #d13438;
                    }
                """,
                'button': """
                    QPushButton {
                        background-color: #f0f0f0;
                        border: 1px solid #d1d1d1;
                        border-radius: 4px;
                        padding: 6px 12px;
                        color: #000000;
                        font-family: 'Segoe UI';
                        font-size: 12px;
                        min-height: 24px;
                    }
                    QPushButton:hover {
                        background-color: #e5e5e5;
                        border-color: #0078d7;
                    }
                    QPushButton:pressed {
                        background-color: #0078d7;
                        color: white;
                    }
                    QPushButton:disabled {
                        background-color: #f8f8f8;
                        color: #ccc;
                    }
                """,
                'today_button': """
                    QPushButton {
                        background-color: #0c6c0c;
                        color: white;
                        font-weight: bold;
                    }
                    QPushButton:hover {
                        background-color: #0e7c0e;
                    }
                """,
                'calendar_button': """
                    QPushButton {
                        background-color: #004578;
                        color: white;
                    }
                    QPushButton:hover {
                        background-color: #005a9e;
                    }
                """
            }
    
    def _setup_ui(self):
        """راه‌اندازی رابط کاربری"""
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        
        # لایه اصلی
        self.main_layout = QHBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(6)
        
        # فیلد ورود/نمایش تاریخ
        self.date_input = QLineEdit()
        self.date_input.setProperty("valid", "true")
        self.date_input.setStyleSheet(self.STYLES['line_edit'])
        
        if self._mode == 'display':
            self.date_input.setReadOnly(True)
            self.date_input.setCursor(Qt.CursorShape.PointingHandCursor)
            self.date_input.mousePressEvent = self._open_calendar
        else:
            self.date_input.setPlaceholderText("مثال: 1403/01/15")
            self.date_input.setToolTip("تاریخ شمسی را وارد کنید یا از تقویم انتخاب نمایید")
        
        self.main_layout.addWidget(self.date_input, 1)
        
        # دکمه‌ها (اگر فعال باشند)
        if self._show_buttons:
            # دکمه امروز
            if self._show_today_button:
                self.today_btn = QPushButton("امروز")
                self.today_btn.setStyleSheet(self.STYLES['button'] + self.STYLES['today_button'])
                self.today_btn.setToolTip("Ctrl+T: تنظیم تاریخ امروز")
                self.today_btn.setCursor(Qt.CursorShape.PointingHandCursor)
                self.main_layout.addWidget(self.today_btn)
            
            # دکمه تقویم
            if self._show_calendar_button:
                self.calendar_btn = QPushButton("📅")
                self.calendar_btn.setStyleSheet(self.STYLES['button'] + self.STYLES['calendar_button'])
                self.calendar_btn.setToolTip("Ctrl+C: باز کردن تقویم")
                self.calendar_btn.setCursor(Qt.CursorShape.PointingHandCursor)
                self.main_layout.addWidget(self.calendar_btn)
        
        # نمایش وضعیت اعتبارسنجی
        self.validation_label = QLabel()
        self.validation_label.setVisible(False)
        self.validation_label.setStyleSheet("""
            QLabel {
                color: #d13438;
                font-size: 11px;
                padding: 2px 4px;
            }
        """)
        self.main_layout.addWidget(self.validation_label)
    
    def _connect_signals(self):
        """اتصال سیگنال‌ها"""
        # اتصال تغییرات متن
        self.date_input.textChanged.connect(self._on_text_changed)
        self.date_input.returnPressed.connect(self._validate_date)
        
        # اتصال دکمه‌ها
        if hasattr(self, 'today_btn'):
            self.today_btn.clicked.connect(self.set_to_today)
        if hasattr(self, 'calendar_btn'):
            self.calendar_btn.clicked.connect(self._open_calendar)
        
        # تنظیم فیلتر رویداد برای کلیدهای میانبر
        self.date_input.installEventFilter(self)
    
    def eventFilter(self, obj, event):
        """فیلتر رویداد برای کلیدهای میانبر"""
        if obj == self.date_input and event.type() == QEvent.Type.KeyPress:
            key_event = event
            # Ctrl+T برای تاریخ امروز
            if key_event.modifiers() == Qt.KeyboardModifier.ControlModifier and key_event.key() == Qt.Key.Key_T:
                self.set_to_today()
                return True
            # Ctrl+C برای باز کردن تقویم
            elif key_event.modifiers() == Qt.KeyboardModifier.ControlModifier and key_event.key() == Qt.Key.Key_C:
                self._open_calendar()
                return True
            # Escape برای پاک کردن
            elif key_event.key() == Qt.Key.Key_Escape:
                self.clear()
                return True
        
        return super().eventFilter(obj, event)
    
    def _on_text_changed(self, text):
        """واکنش به تغییر متن"""
        # فرمت خودکار هنگام تایپ
        if self._mode == 'edit' and text:
            formatted = self._auto_format(text)
            if formatted != text:
                self.date_input.setText(formatted)
                self.date_input.setCursorPosition(len(formatted))
        
        # اعتبارسنجی اولیه
        self._validate_date()
    
    def _auto_format(self, text: str) -> str:
        """فرمت خودکار متن ورودی"""
        # حذف کاراکترهای غیر مجاز
        cleaned = re.sub(r'[^\d/\-\.]', '', text)
        
        # اگر فقط اعداد وارد شده، فرمت کن
        if re.match(r'^\d+$', cleaned):
            digits = cleaned
            
            if len(digits) >= 8:
                year = digits[:4]
                month = digits[4:6] if len(digits) >= 6 else ''
                day = digits[6:8] if len(digits) >= 8 else ''
                
                # فرمت بر اساس تنظیمات
                if self._date_format == 'numeric_dash':
                    return f"{year}-{month}-{day}"
                elif self._date_format == 'numeric_no_sep':
                    return f"{year}{month}{day}"
                else:  # numeric (default)
                    return f"{year}/{month}/{day}"
        
        return cleaned[:10]  # محدود کردن طول
    
    def _validate_date(self):
        """اعتبارسنجی تاریخ وارد شده"""
        date_str = self.date_input.text().strip()
        
        if not date_str:
            self._is_valid = True
            self.date_input.setProperty("valid", "true")
            self.date_input.style().polish(self.date_input)
            self.validation_label.clear()
            self.validation_label.setVisible(False)
            self.validation_changed.emit(True)
            return True
        
        # تبدیل رشته به تاریخ
        jalali_date = self._parse_date_string(date_str)
        
        if jalali_date is None:
            self._is_valid = False
            self.date_input.setProperty("valid", "false")
            self.date_input.style().polish(self.date_input)
            self.validation_label.setText("⚠ تاریخ نامعتبر است")
            self.validation_label.setVisible(True)
            self.validation_changed.emit(False)
            return False
        
        # بررسی محدوده تاریخ
        is_in_range = self._check_date_range(jalali_date)
        
        if not is_in_range:
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
            
            self.validation_label.setText(msg)
            self.validation_label.setVisible(True)
            self.validation_changed.emit(False)
            return False
        
        # تاریخ معتبر است
        self._is_valid = True
        self._current_date = jalali_date
        self.date_input.setProperty("valid", "true")
        self.date_input.style().polish(self.date_input)
        self.validation_label.clear()
        self.validation_label.setVisible(False)
        
        # ارسال سیگنال‌ها
        self.date_changed.emit(jalali_date)
        self.date_string_changed.emit(self.get_date_string())
        self.validation_changed.emit(True)
        
        return True
    
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
            
            # اگر هیچکدام کار نکرد
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
    
    def _open_calendar(self, event=None):
        """باز کردن دیالوگ تقویم"""
        dialog = AdvancedJalaliCalendar(
            initial_date=self._current_date,
            min_date=self._min_date,
            max_date=self._max_date,
            theme=self._theme,
            parent=self
        )
        
        if dialog.exec():
            selected_date = dialog.get_selected_date()
            if selected_date:
                self.set_date(selected_date)
    
    # ------------------ متدهای عمومی ------------------
    
    def set_to_today(self):
        """تنظیم تاریخ امروز"""
        today = jdatetime.date.today()
        self.set_date(today)
    
    def set_date(self, date_obj: Union[jdatetime.date, datetime, str, None]):
        """
        تنظیم تاریخ از انواع مختلف
        
        Args:
            date_obj: می‌تواند یکی از موارد زیر باشد:
                     - jdatetime.date: تاریخ شمسی
                     - datetime: تاریخ میلادی
                     - str: رشته تاریخ
                     - None: پاک کردن
        """
        if date_obj is None:
            self.clear()
            return
        
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
        
        # اعتبارسنجی
        self._validate_date()
    
    def clear(self):
        """پاک کردن فیلد"""
        self.date_input.clear()
        self._is_valid = True
        self.date_input.setProperty("valid", "true")
        self.date_input.style().polish(self.date_input)
        self.validation_label.clear()
        self.validation_label.setVisible(False)
    
    def get_date(self) -> Optional[jdatetime.date]:
        """دریافت تاریخ شمسی (اگر معتبر باشد)"""
        return self._current_date if self._is_valid else None
    
    def get_date_string(self, format_name: Optional[str] = None) -> str:
        """دریافت تاریخ به صورت رشته"""
        if not self._is_valid or self._current_date is None:
            return ""
        
        fmt = format_name or self._date_format
        
        if fmt == 'persian':
            return self._to_persian_numbers(
                self._current_date.strftime(self.FORMATS['numeric'])
            )
        elif fmt == 'database':
            gregorian = self._current_date.togregorian()
            return gregorian.strftime('%Y-%m-%d')
        elif fmt in self.FORMATS:
            return self._current_date.strftime(self.FORMATS[fmt])
        else:
            return self._current_date.strftime(self.FORMATS['numeric'])
    
    def get_gregorian_date(self) -> Optional[datetime.date]:
        """دریافت تاریخ میلادی برای ذخیره در دیتابیس"""
        if not self._is_valid or self._current_date is None:
            return None
        return self._current_date.togregorian()
    
    def is_valid(self) -> bool:
        """آیا تاریخ معتبر است؟"""
        return self._is_valid
    
    def set_min_date(self, min_date: Optional[jdatetime.date]):
        """تنظیم حداقل تاریخ مجاز"""
        self._min_date = min_date
        self._validate_date()
    
    def set_max_date(self, max_date: Optional[jdatetime.date]):
        """تنظیم حداکثر تاریخ مجاز"""
        self._max_date = max_date
        self._validate_date()
    
    def set_date_format(self, format_name: str):
        """تنظیم فرمت نمایش تاریخ"""
        if format_name in self.FORMATS:
            self._date_format = format_name
            self.set_date(self._current_date)
    
    def set_mode(self, mode: str):
        """تغییر حالت ویجت (edit/display)"""
        self._mode = mode
        if mode == 'display':
            self.date_input.setReadOnly(True)
            self.date_input.setCursor(Qt.CursorShape.PointingHandCursor)
            self.date_input.mousePressEvent = self._open_calendar
        else:
            self.date_input.setReadOnly(False)
            self.date_input.mousePressEvent = None
    
    def set_theme(self, theme: str):
        """تغییر تم"""
        self._theme = theme
        self._init_styles()
        self.date_input.setStyleSheet(self.STYLES['line_edit'])
        
        if hasattr(self, 'today_btn'):
            self.today_btn.setStyleSheet(self.STYLES['button'] + self.STYLES['today_button'])
        if hasattr(self, 'calendar_btn'):
            self.calendar_btn.setStyleSheet(self.STYLES['button'] + self.STYLES['calendar_button'])
    
    # ------------------ متدهای کمکی ------------------
    
    def _format_date(self, date: jdatetime.date) -> str:
        """فرمت‌دهی تاریخ"""
        if self._date_format == 'persian':
            return self._to_persian_numbers(date.strftime(self.FORMATS['numeric']))
        elif self._date_format in self.FORMATS:
            return date.strftime(self.FORMATS[self._date_format])
        else:
            return date.strftime(self.FORMATS['numeric'])
    
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
    
    @staticmethod
    def _from_persian_numbers(text: str) -> str:
        """تبدیل اعداد فارسی به انگلیسی"""
        english_nums = {
            '۰': '0', '۱': '1', '۲': '2', '۳': '3', '۴': '4',
            '۵': '5', '۶': '6', '۷': '7', '۸': '8', '۹': '9',
            '/': '/', '-': '-', '.': '.'
        }
        
        result = []
        for char in text:
            result.append(english_nums.get(char, char))
        
        return ''.join(result)


class AdvancedJalaliCalendar(QDialog):
    """
    تقویم شمسی پیشرفته با قابلیت‌های کامل
    
    ویژگی‌ها:
    - نمایش ماه‌های قبل و بعد
    - انتخاب سریع سال و ماه
    - برجسته‌سازی روزهای خاص
    - محدوده تاریخ قابل تنظیم
    - پشتیبانی از تم تاریک/روشن
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
        
        Args:
            initial_date: تاریخ اولیه
            min_date: حداقل تاریخ قابل انتخاب
            max_date: حداکثر تاریخ قابل انتخاب
            theme: تم ('dark' یا 'light')
            parent: والد دیالوگ
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
        self.setFixedSize(500, 550)
    
    def _init_styles(self):
        """تعریف استایل‌ها"""
        if self._theme == 'dark':
            self.STYLES = {
                'dialog': """
                    QDialog {
                        background-color: #1e1e1e;
                        color: #ffffff;
                    }
                """,
                'header': """
                    QFrame {
                        background-color: #252526;
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
                    }
                    QPushButton:hover {
                        background-color: #323233;
                        border-color: #0078d7;
                    }
                    QPushButton:pressed {
                        background-color: #0078d7;
                    }
                """,
                'today_button': """
                    QPushButton {
                        background-color: #0c6c0c;
                        font-weight: bold;
                    }
                """,
                'selected_button': """
                    QPushButton {
                        background-color: #0078d7;
                        font-weight: bold;
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
                        background-color: #ffffff;
                        color: #000000;
                    }
                """,
                'header': """
                    QFrame {
                        background-color: #f0f0f0;
                        border-radius: 8px;
                        padding: 10px;
                    }
                """,
                'day_button': """
                    QPushButton {
                        background-color: #f8f8f8;
                        border: 1px solid #e0e0e0;
                        border-radius: 4px;
                        color: #000000;
                        font-size: 13px;
                        min-width: 40px;
                        min-height: 40px;
                    }
                    QPushButton:hover {
                        background-color: #f0f0f0;
                        border-color: #0078d7;
                    }
                    QPushButton:pressed {
                        background-color: #0078d7;
                        color: white;
                    }
                """,
                'today_button': """
                    QPushButton {
                        background-color: #0c6c0c;
                        color: white;
                        font-weight: bold;
                    }
                """,
                'selected_button': """
                    QPushButton {
                        background-color: #0078d7;
                        color: white;
                        font-weight: bold;
                    }
                """,
                'holiday_button': """
                    QPushButton {
                        color: #d13438;
                        font-weight: bold;
                    }
                """,
                'disabled_button': """
                    QPushButton {
                        background-color: #f0f0f0;
                        color: #ccc;
                        border-color: #e0e0e0;
                    }
                    QPushButton:hover {
                        background-color: #f0f0f0;
                        border-color: #e0e0e0;
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
        
        # دکمه ماه بعد
        next_month_btn = QPushButton("▶")
        next_month_btn.clicked.connect(self._next_month)
        next_month_btn.setFixedSize(40, 40)
        
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
                padding: 8px;
                border-radius: 6px;
                background-color: #252526;
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
                    color: #0078d7;
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
                background-color: #0c6c0c;
                color: white;
                font-weight: bold;
                padding: 10px 20px;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #0e7c0e;
            }
        """)
        
        # دکمه تأیید
        confirm_btn = QPushButton("✅ تأیید")
        confirm_btn.clicked.connect(self.accept)
        confirm_btn.setStyleSheet("""
            QPushButton {
                background-color: #0078d7;
                color: white;
                font-weight: bold;
                padding: 10px 20px;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #005a9e;
            }
        """)
        
        # دکمه انصراف
        cancel_btn = QPushButton("❌ انصراف")
        cancel_btn.clicked.connect(self.reject)
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #d13438;
                color: white;
                font-weight: bold;
                padding: 10px 20px;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #c23934;
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
    
    def _on_date_component_changed(self):
        """واکنش به تغییر سال یا ماه"""
        self._update_calendar()
    
    def get_selected_date(self) -> jdatetime.date:
        """دریافت تاریخ انتخاب شده"""
        return self._selected_date


# ------------------ توابع کمکی برای سازگاری ------------------

def create_jalali_date_widget(mode='edit', **kwargs):
    """
    تابع کمکی برای ایجاد ویجت تاریخ شمسی
    
    Args:
        mode: 'edit' یا 'display'
        **kwargs: سایر پارامترهای JalaliDateWidget
    
    Returns:
        JalaliDateWidget
    """
    return JalaliDateWidget(mode=mode, **kwargs)


def get_jalali_date_from_widget(widget):
    """
    دریافت تاریخ از ویجت
    
    Args:
        widget: JalaliDateWidget
    
    Returns:
        تاریخ شمسی یا None
    """
    if isinstance(widget, JalaliDateWidget):
        return widget.get_date()
    return None


def set_jalali_date_to_widget(widget, date_obj):
    """
    تنظیم تاریخ روی ویجت
    
    Args:
        widget: JalaliDateWidget
        date_obj: تاریخ (شمسی، میلادی یا رشته)
    """
    if isinstance(widget, JalaliDateWidget):
        widget.set_date(date_obj)


# ------------------ تست ------------------

if __name__ == "__main__":
    import sys
    
    app = QApplication(sys.argv)
    
    # تنظیم فونت فارسی
    font = QFont("B Nazanin", 11)
    app.setFont(font)
    
    # ایجاد ویندوز تست
    window = QWidget()
    window.setWindowTitle("تست ویجت تاریخ شمسی پیشرفته")
    window.setGeometry(100, 100, 600, 400)
    
    layout = QVBoxLayout(window)
    
    # ویجت ۱: حالت ویرایش
    label1 = QLabel("حالت ویرایش (Edit Mode):")
    widget1 = JalaliDateWidget(mode='edit', theme='dark')
    widget1.set_date(jdatetime.date.today())
    
    # ویجت ۲: حالت نمایش
    label2 = QLabel("حالت نمایش (Display Mode):")
    widget2 = JalaliDateWidget(mode='display', theme='dark', 
                               show_today_button=False)
    widget2.set_date(jdatetime.date.today())
    
    # ویجت ۳: با فرمت متفاوت
    label3 = QLabel("فرمت فارسی:")
    widget3 = JalaliDateWidget(mode='edit', date_format='persian', theme='light')
    widget3.set_date(jdatetime.date.today())
    
    # دکمه برای نمایش اطلاعات
    info_btn = QPushButton("نمایش اطلاعات ویجت‌ها")
    
    def show_info():
        print("\n" + "="*50)
        print("اطلاعات ویجت‌ها:")
        
        for i, (name, widget) in enumerate([("ویجت ۱", widget1), 
                                           ("ویجت ۲", widget2), 
                                           ("ویجت ۳", widget3)], 1):
            date_obj = widget.get_date()
            date_str = widget.get_date_string()
            is_valid = widget.is_valid()
            
            print(f"\n{name}:")
            print(f"  تاریخ شمسی: {date_obj}")
            print(f"  رشته تاریخ: {date_str}")
            print(f"  معتبر است: {is_valid}")
            
            if date_obj:
                gregorian = date_obj.togregorian()
                print(f"  تاریخ میلادی (برای دیتابیس): {gregorian}")
    
    info_btn.clicked.connect(show_info)
    
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