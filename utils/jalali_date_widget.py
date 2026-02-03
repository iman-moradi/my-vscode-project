# jalali_date_widget.py - ویجت کامل تاریخ شمسی
# هماهنگ با ماژول و دیتابیس 
# D:\app shervin shop\shervinshop4\utils\jalali_date_widget.py

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, 
                               QPushButton, QLabel, QDialog, QGridLayout, 
                               QCalendarWidget, QComboBox, QSpinBox,
                               QApplication, QStyle, QDateEdit)
from PySide6.QtCore import Qt, QDate, Signal, QLocale, QDateTime
from PySide6.QtGui import QFont, QPalette, QColor, QIcon
import jdatetime
import locale
from datetime import datetime
from database import DatabaseManager

class JalaliCalendarDialog(QDialog):
    """دیالوگ تقویم شمسی"""
    
    date_selected = Signal(str)  # سیگنال انتخاب تاریخ با فرمت YYYY/MM/DD
    
    def __init__(self, parent=None, current_date=None):
        super().__init__(parent)
        self.db = DatabaseManager()  # اتصال به دیتابیس
        self.setWindowTitle("انتخاب تاریخ شمسی")
        self.setWindowIcon(QIcon.fromTheme("calendar"))
        self.setFixedSize(400, 350)
        
        # تنظیم استایل
        self.setStyleSheet("""
            QDialog {
                background-color: #f5f5f5;
                font-family: 'B Nazanin';
                font-size: 12pt;
            }
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-family: 'B Nazanin';
                font-size: 11pt;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton#cancelBtn {
                background-color: #f44336;
            }
            QPushButton#cancelBtn:hover {
                background-color: #d32f2f;
            }
            QLabel {
                color: #333;
                font-weight: bold;
            }
            QComboBox, QSpinBox {
                padding: 6px;
                border: 1px solid #ddd;
                border-radius: 4px;
                background-color: white;
                font-family: 'B Nazanin';
                font-size: 11pt;
            }
        """)
        
        self.init_ui(current_date)
    
    def init_ui(self, current_date):
        layout = QVBoxLayout(self)
        
        # نوار کنترل سال و ماه
        control_layout = QHBoxLayout()
        
        # سال
        year_label = QLabel("سال:")
        self.year_combo = QComboBox()
        current_jalali = jdatetime.datetime.now()
        
        # پر کردن سال‌ها (از 1300 تا 1450)
        for year in range(1300, 1451):
            self.year_combo.addItem(f"{year}", year)
        
        # ماه
        month_label = QLabel("ماه:")
        self.month_combo = QComboBox()
        months = [
            ("فروردین", 1), ("اردیبهشت", 2), ("خرداد", 3),
            ("تیر", 4), ("مرداد", 5), ("شهریور", 6),
            ("مهر", 7), ("آبان", 8), ("آذر", 9),
            ("دی", 10), ("بهمن", 11), ("اسفند", 12)
        ]
        
        for month_name, month_num in months:
            self.year_combo.setItemData(month_num - 1, month_name, Qt.DisplayRole)
        
        for month_name, month_num in months:
            self.month_combo.addItem(month_name, month_num)
        
        # تنظیم تاریخ فعلی اگر داده شده
        if current_date:
            try:
                if isinstance(current_date, str):
                    # تبدیل رشته تاریخ به شیء جلالی
                    if '/' in current_date:
                        parts = current_date.split('/')
                        if len(parts) >= 3:
                            year = int(parts[0])
                            month = int(parts[1])
                            day = int(parts[2])
                            current_jalali = jdatetime.date(year, month, day)
                elif isinstance(current_date, jdatetime.date):
                    current_jalali = current_date
            except:
                current_jalali = jdatetime.datetime.now()
        else:
            current_jalali = jdatetime.datetime.now()
        
        # تنظیم مقادیر پیش‌فرض
        self.year_combo.setCurrentText(str(current_jalali.year))
        self.month_combo.setCurrentIndex(current_jalali.month - 1)
        
        control_layout.addWidget(year_label)
        control_layout.addWidget(self.year_combo)
        control_layout.addWidget(month_label)
        control_layout.addWidget(self.month_combo)
        control_layout.addStretch()
        
        layout.addLayout(control_layout)
        
        # تقویم
        self.calendar_widget = QWidget()
        self.calendar_layout = QGridLayout(self.calendar_widget)
        self.calendar_layout.setSpacing(2)
        self.calendar_layout.setContentsMargins(5, 5, 5, 5)
        
        # اضافه کردن روزهای هفته
        week_days = ["ش", "ی", "د", "س", "چ", "پ", "ج"]
        for i, day in enumerate(week_days):
            day_label = QLabel(day)
            day_label.setAlignment(Qt.AlignCenter)
            day_label.setStyleSheet("""
                QLabel {
                    background-color: #2196F3;
                    color: white;
                    font-weight: bold;
                    padding: 5px;
                    border-radius: 3px;
                }
            """)
            self.calendar_layout.addWidget(day_label, 0, i)
        
        layout.addWidget(self.calendar_widget)
        
        # دکمه‌های امروز و انتخاب
        button_layout = QHBoxLayout()
        
        today_btn = QPushButton("امروز")
        today_btn.clicked.connect(self.set_today)
        button_layout.addWidget(today_btn)
        
        button_layout.addStretch()
        
        cancel_btn = QPushButton("انصراف")
        cancel_btn.setObjectName("cancelBtn")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        select_btn = QPushButton("انتخاب تاریخ")
        select_btn.clicked.connect(self.select_date)
        button_layout.addWidget(select_btn)
        
        layout.addLayout(button_layout)
        
        # روزهای تقویم را پر کن
        self.update_calendar()
        
        # اتصال سیگنال‌های تغییر
        self.year_combo.currentIndexChanged.connect(self.update_calendar)
        self.month_combo.currentIndexChanged.connect(self.update_calendar)
    
    def update_calendar(self):
        """به‌روزرسانی تقویم بر اساس سال و ماه انتخاب شده"""
        # حذف دکمه‌های قبلی
        for i in reversed(range(self.calendar_layout.count())):
            widget = self.calendar_layout.itemAt(i).widget()
            if widget and isinstance(widget, QPushButton):
                widget.deleteLater()
        
        # دریافت سال و ماه انتخاب شده
        year = self.year_combo.currentData()
        month = self.month_combo.currentData()
        
        # تعیین اولین روز ماه
        first_day = jdatetime.date(year, month, 1)
        start_weekday = (first_day.weekday() + 2) % 7  # تطبیق با تقویم شمسی
        
        # تعداد روزهای ماه
        try:
            next_month = jdatetime.date(year, month, 1) + jdatetime.timedelta(days=35)
            next_month = next_month.replace(day=1)
            days_in_month = (next_month - jdatetime.timedelta(days=1)).day
        except:
            days_in_month = 30 if month <= 6 else 29
        
        # اضافه کردن روزهای ماه
        row, col = 1, start_weekday
        current_jalali = jdatetime.datetime.now()
        
        for day in range(1, days_in_month + 1):
            date_btn = QPushButton(str(day))
            date_btn.setFixedSize(40, 40)
            
            # بررسی اگر تاریخ امروز است
            if (year == current_jalali.year and 
                month == current_jalali.month and 
                day == current_jalali.day):
                date_btn.setStyleSheet("""
                    QPushButton {
                        background-color: #4CAF50;
                        color: white;
                        font-weight: bold;
                        border-radius: 20px;
                    }
                    QPushButton:hover {
                        background-color: #45a049;
                    }
                """)
            else:
                date_btn.setStyleSheet("""
                    QPushButton {
                        background-color: white;
                        border: 1px solid #ddd;
                        border-radius: 4px;
                    }
                    QPushButton:hover {
                        background-color: #e3f2fd;
                        border-color: #2196F3;
                    }
                """)
            
            # ذخیره تاریخ در دیتای دکمه
            date_btn.setProperty("jalali_date", f"{year}/{month:02d}/{day:02d}")
            date_btn.clicked.connect(self.on_date_clicked)
            
            self.calendar_layout.addWidget(date_btn, row, col)
            
            col += 1
            if col > 6:
                col = 0
                row += 1
    
    def on_date_clicked(self):
        """وقتی روی روزی کلیک شد"""
        sender = self.sender()
        if sender:
            jalali_date = sender.property("jalali_date")
            self.selected_date = jalali_date
            
            # هایلایت کردن دکمه انتخاب شده
            for i in range(self.calendar_layout.count()):
                widget = self.calendar_layout.itemAt(i).widget()
                if widget and isinstance(widget, QPushButton):
                    if widget.property("jalali_date") == jalali_date:
                        widget.setStyleSheet("""
                            QPushButton {
                                background-color: #2196F3;
                                color: white;
                                font-weight: bold;
                                border-radius: 4px;
                            }
                        """)
                    else:
                        # ریست استایل به حالت عادی
                        year, month, day = map(int, jalali_date.split('/'))
                        current_jalali = jdatetime.datetime.now()
                        if (year == current_jalali.year and 
                            month == current_jalali.month and 
                            int(widget.text()) == current_jalali.day):
                            widget.setStyleSheet("""
                                QPushButton {
                                    background-color: #4CAF50;
                                    color: white;
                                    font-weight: bold;
                                    border-radius: 20px;
                                }
                            """)
                        else:
                            widget.setStyleSheet("""
                                QPushButton {
                                    background-color: white;
                                    border: 1px solid #ddd;
                                    border-radius: 4px;
                                }
                            """)
    
    def set_today(self):
        """تنظیم تاریخ امروز"""
        today = jdatetime.datetime.now()
        self.year_combo.setCurrentText(str(today.year))
        self.month_combo.setCurrentIndex(today.month - 1)
        
        # پیدا کردن دکمه امروز و کلیک روی آن
        for i in range(self.calendar_layout.count()):
            widget = self.calendar_layout.itemAt(i).widget()
            if widget and isinstance(widget, QPushButton):
                if widget.text() == str(today.day):
                    self.on_date_clicked()
                    widget.click()
                    break
    
    def select_date(self):
        """انتخاب تاریخ"""
        if hasattr(self, 'selected_date'):
            self.date_selected.emit(self.selected_date)
            self.accept()
        else:
            # اگر تاریخی انتخاب نشده، تاریخ امروز را انتخاب کن
            today = jdatetime.datetime.now().strftime("%Y/%m/%d")
            self.date_selected.emit(today)
            self.accept()
    
    def get_selected_date(self):
        """دریافت تاریخ انتخاب شده"""
        if hasattr(self, 'selected_date'):
            return self.selected_date
        return jdatetime.datetime.now().strftime("%Y/%m/%d")

class JalaliDateWidget(QWidget):
    """ویجت ورود تاریخ شمسی"""
    
    date_changed = Signal(str)  # تاریخ میلادی
    jalali_date_changed = Signal(str)  # تاریخ شمسی
    
    def __init__(self, parent=None, show_time=False):
        super().__init__(parent)
        self.db = DatabaseManager()
        self.show_time = show_time
        self.current_miladi = None
        self.current_jalali = None
        
        self.init_ui()
        
        # تاریخ امروز را تنظیم کن
        self.set_to_today()
    
    def init_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)
        
        # فیلد نمایش تاریخ
        self.date_edit = QLineEdit()
        self.date_edit.setReadOnly(True)
        self.date_edit.setPlaceholderText("تاریخ شمسی")
        self.date_edit.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                border: 1px solid #ddd;
                border-radius: 4px;
                font-family: 'B Nazanin';
                font-size: 11pt;
                background-color: white;
            }
            QLineEdit:focus {
                border-color: #2196F3;
            }
        """)
        
        # دکمه باز کردن تقویم
        self.calendar_btn = QPushButton()
        self.calendar_btn.setIcon(QApplication.style().standardIcon(QStyle.SP_FileDialogDetailedView))
        self.calendar_btn.setToolTip("باز کردن تقویم")
        self.calendar_btn.setFixedSize(40, 40)
        self.calendar_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                border: none;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
            QPushButton:pressed {
                background-color: #0D47A1;
            }
        """)
        
        # دکمه امروز
        self.today_btn = QPushButton("امروز")
        self.today_btn.setToolTip("تنظیم تاریخ امروز")
        self.today_btn.setFixedSize(60, 40)
        self.today_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 4px;
                font-family: 'B Nazanin';
                font-size: 10pt;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        
        layout.addWidget(self.date_edit)
        layout.addWidget(self.calendar_btn)
        layout.addWidget(self.today_btn)
        
        # اتصال سیگنال‌ها
        self.calendar_btn.clicked.connect(self.open_calendar)
        self.today_btn.clicked.connect(self.set_to_today)
        
        # اگر نمایش زمان نیاز است
        if self.show_time:
            time_layout = QHBoxLayout()
            
            self.hour_spin = QSpinBox()
            self.hour_spin.setRange(0, 23)
            self.hour_spin.setSuffix(" ساعت")
            self.hour_spin.setValue(datetime.now().hour)
            
            self.minute_spin = QSpinBox()
            self.minute_spin.setRange(0, 59)
            self.minute_spin.setSuffix(" دقیقه")
            self.minute_spin.setValue(datetime.now().minute)
            
            time_layout.addWidget(QLabel("زمان:"))
            time_layout.addWidget(self.hour_spin)
            time_layout.addWidget(self.minute_spin)
            
            main_layout = QVBoxLayout()
            main_layout.addLayout(layout)
            main_layout.addLayout(time_layout)
            
            self.setLayout(main_layout)
            
            # اتصال سیگنال‌های تغییر زمان
            self.hour_spin.valueChanged.connect(self.emit_time_changed)
            self.minute_spin.valueChanged.connect(self.emit_time_changed)
    
    def open_calendar(self):
        """باز کردن دیالوگ تقویم"""
        current_date = self.current_jalali if self.current_jalali else None
        calendar_dialog = JalaliCalendarDialog(self, current_date)
        
        calendar_dialog.date_selected.connect(self.on_date_selected)
        calendar_dialog.exec()
    
    def on_date_selected(self, jalali_date_str):
        """وقتی تاریخ از تقویم انتخاب شد"""
        self.set_jalali_date(jalali_date_str)
    
    def set_jalali_date(self, jalali_date_str):
        """تنظیم تاریخ شمسی"""
        try:
            # تبدیل تاریخ شمسی به میلادی
            miladi_date_str = self.db.jalali_to_gregorian(jalali_date_str)
            
            # ذخیره تاریخ‌ها
            self.current_jalali = jalali_date_str
            self.current_miladi = miladi_date_str
            
            # نمایش تاریخ شمسی
            self.date_edit.setText(jalali_date_str)
            
            # ارسال سیگنال‌ها
            self.date_changed.emit(miladi_date_str)
            self.jalali_date_changed.emit(jalali_date_str)
            
        except Exception as e:
            print(f"خطا در تنظیم تاریخ شمسی: {e}")
    
    def set_miladi_date(self, miladi_date_str):
        """تنظیم تاریخ میلادی"""
        try:
            # تبدیل تاریخ میلادی به شمسی
            jalali_date_str = self.db.gregorian_to_jalali(miladi_date_str)
            
            # ذخیره تاریخ‌ها
            self.current_miladi = miladi_date_str
            self.current_jalali = jalali_date_str
            
            # نمایش تاریخ شمسی
            self.date_edit.setText(jalali_date_str)
            
            # ارسال سیگنال‌ها
            self.date_changed.emit(miladi_date_str)
            self.jalali_date_changed.emit(jalali_date_str)
            
        except Exception as e:
            print(f"خطا در تنظیم تاریخ میلادی: {e}")
    
    def set_to_today(self):
        """تنظیم تاریخ امروز"""
        today_jalali = jdatetime.datetime.now().strftime("%Y/%m/%d")
        self.set_jalali_date(today_jalali)

    def set_date_string(self, jalali_date_str):
        """تنظیم تاریخ از رشته شمسی (سازگاری با کدهای موجود)"""
        self.set_jalali_date(jalali_date_str)

    def date_string(self):
        """دریافت تاریخ به صورت رشته شمسی (سازگاری با کدهای موجود)"""
        return self.get_jalali_date()

    def get_date_string(self):
        """دریافت تاریخ به صورت رشته شمسی"""
        return self.get_jalali_date()

    def get_miladi_date(self):
        """دریافت تاریخ میلادی"""
        return self.current_miladi
    
    def get_jalali_date(self):
        """دریافت تاریخ شمسی"""
        return self.current_jalali
    
    def get_date_time(self):
        """دریافت تاریخ و زمان کامل"""
        if not self.show_time:
            return self.current_miladi
        
        # اگر زمان هم نمایش داده می‌شود
        time_str = f"{self.hour_spin.value():02d}:{self.minute_spin.value():02d}:00"
        
        if self.current_miladi:
            # اضافه کردن زمان به تاریخ
            return f"{self.current_miladi} {time_str}"
        
        return None
    
    def set_date_time(self, datetime_str):
        """تنظیم تاریخ و زمان کامل"""
        if not datetime_str:
            return
        
        try:
            # جدا کردن تاریخ و زمان
            if ' ' in datetime_str:
                date_part, time_part = datetime_str.split(' ', 1)
                # تنظیم تاریخ
                self.set_miladi_date(date_part)
                
                # تنظیم زمان
                if self.show_time and ':' in time_part:
                    time_parts = time_part.split(':')
                    if len(time_parts) >= 2:
                        self.hour_spin.setValue(int(time_parts[0]))
                        self.minute_spin.setValue(int(time_parts[1]))
            else:
                # فقط تاریخ
                self.set_miladi_date(datetime_str)
                
        except Exception as e:
            print(f"خطا در تنظیم تاریخ و زمان: {e}")
    
    def set_date(self, date):
        """متد سازگاری - تنظیم تاریخ از انواع مختلف"""
        if isinstance(date, QDate):
            if date.isValid():
                date_str = f"{date.year()}-{date.month():02d}-{date.day():02d}"
                self.set_miladi_date(date_str)
        elif isinstance(date, str) and date:
            # بررسی فرمت
            if '/' in date and date.count('/') == 2:
                # احتمالاً تاریخ شمسی است
                self.set_jalali_date(date)
            elif '-' in date and date.count('-') == 2:
                # احتمالاً تاریخ میلادی است
                self.set_miladi_date(date)
        elif isinstance(date, datetime):
            date_str = date.strftime("%Y-%m-%d")
            self.set_miladi_date(date_str)
        elif isinstance(date, jdatetime.datetime) or isinstance(date, jdatetime.date):
            date_str = date.strftime("%Y/%m/%d")
            self.set_jalali_date(date_str)

    def clear(self):
        """پاک کردن تاریخ"""
        self.date_edit.clear()
        self.current_miladi = None
        self.current_jalali = None
        
        if self.show_time:
            self.hour_spin.setValue(0)
            self.minute_spin.setValue(0)
    
    def is_valid(self):
        """بررسی معتبر بودن تاریخ"""
        return self.current_miladi is not None and self.current_jalali is not None
    
    def emit_time_changed(self):
        """ارسال سیگنال تغییر زمان"""
        if self.current_miladi:
            self.date_changed.emit(self.get_date_time())

    def set_display_format(self, format_str):
        """تنظیم فرمت نمایش تاریخ"""
        self.display_format = format_str
        
    def format_date(self, jalali_date_str=None):
        """فرمت‌دهی تاریخ بر اساس فرمت تنظیم شده"""
        if not hasattr(self, 'display_format'):
            return jalali_date_str or self.get_jalali_date()
        
        if jalali_date_str is None:
            jalali_date_str = self.get_jalali_date()
        
        if not jalali_date_str:
            return ""
        
        try:
            # تبدیل رشته به تاریخ جلالی
            year, month, day = map(int, jalali_date_str.split('/'))
            jalali_date = jdatetime.date(year, month, day)
            
            # فرمت‌دهی بر اساس display_format
            if self.display_format == 'yyyy/MM/dd':
                return f"{jalali_date.year:04d}/{jalali_date.month:02d}/{jalali_date.day:02d}"
            elif self.display_format == 'yy/MM/dd':
                return f"{jalali_date.year % 100:02d}/{jalali_date.month:02d}/{jalali_date.day:02d}"
            elif self.display_format == 'dd/MM/yyyy':
                return f"{jalali_date.day:02d}/{jalali_date.month:02d}/{jalali_date.year:04d}"
            else:
                # فرمت پیش‌فرض
                return jalali_date_str
        except:
            return jalali_date_str



class JalaliDateEdit(QLineEdit):
    """ورودی تاریخ شمسی ساده (مانند QDateEdit اما برای تاریخ شمسی)"""
    
    date_changed = Signal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.db = DatabaseManager()
        self.calendar_dialog = None
        
        self.setPlaceholderText("1403/01/01")
        self.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                border: 1px solid #ddd;
                border-radius: 4px;
                font-family: 'B Nazanin';
                font-size: 11pt;
            }
            QLineEdit:focus {
                border-color: #2196F3;
            }
        """)
        
        # اعتبارسنجی ورودی
        self.textChanged.connect(self.validate_date)
    
    def validate_date(self, text):
        """اعتبارسنجی فرمت تاریخ شمسی"""
        if not text:
            return
        
        # بررسی فرمت YYYY/MM/DD
        if '/' in text:
            parts = text.split('/')
            if len(parts) == 3:
                try:
                    year, month, day = map(int, parts)
                    
                    # بررسی محدوده‌های منطقی
                    if 1300 <= year <= 1500 and 1 <= month <= 12 and 1 <= day <= 31:
                        # سعی در ایجاد تاریخ جلالی برای اعتبارسنجی
                        jdatetime.date(year, month, day)
                        
                        # تبدیل به میلادی و ارسال سیگنال
                        miladi_date = self.db.jalali_to_gregorian(text)
                        self.date_changed.emit(miladi_date)
                        
                        self.setStyleSheet("""
                            QLineEdit {
                                padding: 8px;
                                border: 2px solid #4CAF50;
                                border-radius: 4px;
                                font-family: 'B Nazanin';
                                font-size: 11pt;
                            }
                        """)
                        return
                except:
                    pass
        
        # اگر تاریخ نامعتبر است
        self.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                border: 2px solid #f44336;
                border-radius: 4px;
                font-family: 'B Nazanin';
                font-size: 11pt;
            }
        """)
    
    def set_jalali_date(self, jalali_date):
        """تنظیم تاریخ شمسی"""
        self.setText(jalali_date)
    
    def set_miladi_date(self, miladi_date):
        """تنظیم تاریخ میلادی"""
        jalali_date = self.db.gregorian_to_jalali(miladi_date)
        self.setText(jalali_date)
    
    def get_miladi_date(self):
        """دریافت تاریخ میلادی"""
        jalali_text = self.text()
        if jalali_text:
            return self.db.jalali_to_gregorian(jalali_text)
        return None
    
    def get_jalali_date(self):
        """دریافت تاریخ شمسی"""
        return self.text()
    
    def mouseDoubleClickEvent(self, event):
        """با دابل کلیک تقویم باز شود"""
        self.open_calendar()
        super().mouseDoubleClickEvent(event)
    
    def open_calendar(self):
        """باز کردن تقویم"""
        if not self.calendar_dialog:
            self.calendar_dialog = JalaliCalendarDialog(self, self.text())
            self.calendar_dialog.date_selected.connect(self.on_date_selected)
        
        self.calendar_dialog.show()
    
    def on_date_selected(self, jalali_date):
        """وقتی تاریخ از تقویم انتخاب شد"""
        self.set_jalali_date(jalali_date)
        self.calendar_dialog.hide()

class JalaliDateTimeWidget(QWidget):
    """ویجت کامل تاریخ و زمان شمسی"""
    
    datetime_changed = Signal(str)  # تاریخ و زمان میلادی
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.db = DatabaseManager()
        
        self.init_ui()
        self.set_to_now()
    
    def init_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)
        
        # ویجت تاریخ
        self.date_widget = JalaliDateWidget(show_time=False)
        
        # اسپین‌بکس‌های زمان
        time_layout = QHBoxLayout()
        
        self.hour_spin = QSpinBox()
        self.hour_spin.setRange(0, 23)
        self.hour_spin.setPrefix("ساعت: ")
        self.hour_spin.setSuffix("  ")
        self.hour_spin.setFixedWidth(100)
        
        self.minute_spin = QSpinBox()
        self.minute_spin.setRange(0, 59)
        self.minute_spin.setPrefix("دقیقه: ")
        self.minute_spin.setSuffix("  ")
        self.minute_spin.setFixedWidth(100)
        
        self.second_spin = QSpinBox()
        self.second_spin.setRange(0, 59)
        self.second_spin.setPrefix("ثانیه: ")
        self.second_spin.setFixedWidth(100)
        
        time_layout.addWidget(self.hour_spin)
        time_layout.addWidget(self.minute_spin)
        time_layout.addWidget(self.second_spin)
        time_layout.addStretch()
        
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.date_widget)
        main_layout.addLayout(time_layout)
        
        self.setLayout(main_layout)
        
        # اتصال سیگنال‌ها
        self.date_widget.date_changed.connect(self.on_date_changed)
        self.hour_spin.valueChanged.connect(self.on_time_changed)
        self.minute_spin.valueChanged.connect(self.on_time_changed)
        self.second_spin.valueChanged.connect(self.on_time_changed)
    
    def on_date_changed(self, date_str):
        """وقتی تاریخ تغییر کرد"""
        self.emit_datetime_changed()
    
    def on_time_changed(self):
        """وقتی زمان تغییر کرد"""
        self.emit_datetime_changed()
    
    def emit_datetime_changed(self):
        """ارسال سیگنال تغییر تاریخ و زمان"""
        date_str = self.date_widget.get_miladi_date()
        if date_str:
            time_str = f"{self.hour_spin.value():02d}:{self.minute_spin.value():02d}:{self.second_spin.value():02d}"
            datetime_str = f"{date_str} {time_str}"
            self.datetime_changed.emit(datetime_str)
    
    def set_to_now(self):
        """تنظیم به زمان فعلی"""
        now = datetime.now()
        jalali_now = jdatetime.datetime.fromgregorian(datetime=now)
        
        # تنظیم تاریخ
        self.date_widget.set_jalali_date(jalali_now.strftime("%Y/%m/%d"))
        
        # تنظیم زمان
        self.hour_spin.setValue(now.hour)
        self.minute_spin.setValue(now.minute)
        self.second_spin.setValue(now.second)
    
    def set_datetime(self, datetime_str):
        """تنظیم تاریخ و زمان"""
        if not datetime_str:
            return
        
        try:
            # جدا کردن تاریخ و زمان
            if ' ' in datetime_str:
                date_part, time_part = datetime_str.split(' ', 1)
                
                # تنظیم تاریخ
                self.date_widget.set_miladi_date(date_part)
                
                # تنظیم زمان
                if ':' in time_part:
                    time_parts = time_part.split(':')
                    if len(time_parts) >= 1:
                        self.hour_spin.setValue(int(time_parts[0]))
                    if len(time_parts) >= 2:
                        self.minute_spin.setValue(int(time_parts[1]))
                    if len(time_parts) >= 3:
                        self.second_spin.setValue(int(time_parts[2]))
            else:
                # فقط تاریخ
                self.date_widget.set_miladi_date(datetime_str)
                
        except Exception as e:
            print(f"خطا در تنظیم تاریخ و زمان: {e}")
    
    def get_datetime(self):
        """دریافت تاریخ و زمان"""
        date_str = self.date_widget.get_miladi_date()
        if date_str:
            time_str = f"{self.hour_spin.value():02d}:{self.minute_spin.value():02d}:{self.second_spin.value():02d}"
            return f"{date_str} {time_str}"
        return None
    
    def get_jalali_datetime(self):
        """دریافت تاریخ و زمان شمسی"""
        jalali_date = self.date_widget.get_jalali_date()
        if jalali_date:
            time_str = f"{self.hour_spin.value():02d}:{self.minute_spin.value():02d}:{self.second_spin.value():02d}"
            return f"{jalali_date} {time_str}"
        return None

# کلاس کمکی برای نمایش تاریخ در جداول
class JalaliDateDelegate:
    """دلیگیت برای نمایش تاریخ شمسی در جدول‌ها"""
    
    @staticmethod
    def display_text(value, role):
        """متن نمایشی برای تاریخ"""
        if role == Qt.DisplayRole and value:
            try:
                db = DatabaseManager()
                return db.gregorian_to_jalali(str(value))
            except:
                return str(value)
        return None


# کلاس برای سازگاری با importهای قدیمی پروژه
# ... (تمام کدهای قبلی فایل)

# کلاس برای سازگاری با importهای قدیمی پروژه
class JalaliDateInput(JalaliDateWidget):
    """ورودی تاریخ شمسی (برای سازگاری با ماژول‌های موجود)"""
    
    def __init__(self, parent=None, mode='edit', theme='dark', 
                 date_format='yyyy/MM/dd', show_calendar_button=True, **kwargs):
        # فراخوانی سازنده والد بدون نمایش زمان
        super().__init__(parent, show_time=False)
        self.mode = mode
        self.theme = theme
        self.date_format = date_format
        self.show_calendar_button = show_calendar_button
        
        # اعمال تم اگر dark است
        if theme == 'dark':
            self.apply_dark_theme()
        else:
            self.apply_light_theme()
        
        # اگر حالت فقط خواندنی است
        if mode == 'readonly':
            self.set_readonly(True)
        
        # اگر دکمه تقویم نباید نمایش داده شود
        if not show_calendar_button:
            self.calendar_btn.hide()
        
        # پردازش پارامترهای اضافی
        if 'show_today_button' in kwargs and not kwargs['show_today_button']:
            self.today_btn.hide()
        
        # سایر تنظیمات
        if 'placeholder_text' in kwargs:
            self.date_edit.setPlaceholderText(kwargs['placeholder_text'])
    
    def apply_dark_theme(self):
        """اعمال تم تاریک"""
        self.setStyleSheet("""
            JalaliDateInput {
                background-color: #2b2b2b;
            }
            QLineEdit {
                padding: 8px;
                border: 1px solid #555;
                border-radius: 4px;
                font-family: 'B Nazanin';
                font-size: 11pt;
                background-color: #3c3c3c;
                color: white;
                selection-background-color: #4CAF50;
            }
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 4px;
                font-family: 'B Nazanin';
                font-size: 10pt;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton#todayBtn {
                background-color: #2196F3;
            }
            QPushButton#todayBtn:hover {
                background-color: #1976D2;
            }
        """)
    
    def apply_light_theme(self):
        """اعمال تم روشن"""
        self.setStyleSheet("""
            JalaliDateInput {
                background-color: white;
            }
            QLineEdit {
                padding: 8px;
                border: 1px solid #ddd;
                border-radius: 4px;
                font-family: 'B Nazanin';
                font-size: 11pt;
                background-color: white;
                color: black;
                selection-background-color: #2196F3;
            }
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                border-radius: 4px;
                font-family: 'B Nazanin';
                font-size: 10pt;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
            QPushButton#todayBtn {
                background-color: #4CAF50;
            }
            QPushButton#todayBtn:hover {
                background-color: #45a049;
            }
        """)
    
    def set_readonly(self, readonly):
        """تنظیم حالت فقط خواندنی"""
        self.date_edit.setReadOnly(readonly)
        self.calendar_btn.setEnabled(not readonly)
        self.today_btn.setEnabled(not readonly)
    
    def get_date(self):
        """متد سازگاری - همان get_miladi_date (برای QDate)"""
        date_str = self.get_miladi_date()
        if date_str:
            try:
                # تبدیل رشته به QDate
                if ' ' in date_str:
                    date_str = date_str.split(' ')[0]
                year, month, day = map(int, date_str.split('-'))
                return QDate(year, month, day)
            except:
                return QDate.currentDate()
        return QDate()

    def set_date_format(self, format_str):
        """تنظیم فرمت تاریخ"""
        self.set_display_format(format_str)

    def set_date(self, date):
        """متد سازگاری - تنظیم تاریخ از QDate یا رشته"""
        if isinstance(date, QDate):
            if date.isValid():
                date_str = f"{date.year()}-{date.month():02d}-{date.day():02d}"
                self.set_miladi_date(date_str)
        elif isinstance(date, str) and date:
            self.set_miladi_date(date)
        elif isinstance(date, datetime):
            date_str = date.strftime("%Y-%m-%d")
            self.set_miladi_date(date_str)
        elif isinstance(date, jdatetime.datetime) or isinstance(date, jdatetime.date):
            date_str = date.strftime("%Y/%m/%d")
            self.set_jalali_date(date_str)
    
    def date(self):
        """متد سازگاری - بازگرداندن QDate"""
        return self.get_date()
    
    def setDisplayFormat(self, format_str):
        """تنظیم فرمت نمایش (برای سازگاری با QDateEdit)"""
        # فرمت شمسی را ذخیره می‌کنیم اما در نمایش فعلی استفاده نمی‌شود
        self.display_format = format_str
    
    def setCalendarPopup(self, enabled):
        """فعال/غیرفعال کردن پاپ‌آپ تقویم (برای سازگاری)"""
        # در کلاس ما همیشه فعال است
        pass
    
    def setMaximumDate(self, date):
        """تنظیم حداکثر تاریخ (برای سازگاری)"""
        # می‌توانید این قابلیت را اضافه کنید
        pass
    
    def setMinimumDate(self, date):
        """تنظیم حداقل تاریخ (برای سازگاری)"""
        # می‌توانید این قابلیت را اضافه کنید
        pass

    def set_date_string(self, jalali_date_str):
        """تنظیم تاریخ از رشته شمسی (سازگاری با کدهای موجود)"""
        self.set_jalali_date(jalali_date_str)

    def date_string(self):
        """دریافت تاریخ به صورت رشته شمسی (سازگاری با کدهای موجود)"""
        return self.get_jalali_date()

    def get_date_string(self):
        """دریافت تاریخ به صورت رشته شمسی"""
        return self.get_jalali_date()


# اضافه کردن کلاس‌های سازگاری بیشتر
class JalaliDateEditCompat(QDateEdit):
    """نسخه سازگار با QDateEdit برای تاریخ شمسی"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        # مخفی کردن ویجت اصلی و استفاده از ویجت شمسی
        self.hide()
        
        # ایجاد ویجت شمسی
        self.jalali_widget = JalaliDateInput(parent)
        
        # اتصال سیگنال‌ها
        self.jalali_widget.date_changed.connect(self._on_date_changed)
        
        # تنظیم تاریخ امروز
        self.setDate(QDate.currentDate())
    
    def _on_date_changed(self, date_str):
        """وقتی تاریخ در ویجت شمسی تغییر کرد"""
        if date_str:
            try:
                # تبدیل رشته به QDate
                if ' ' in date_str:
                    date_str = date_str.split(' ')[0]
                year, month, day = map(int, date_str.split('-'))
                qdate = QDate(year, month, day)
                super().setDate(qdate)
            except:
                pass
    
    def setDate(self, date):
        """تنظیم تاریخ"""
        self.jalali_widget.set_date(date)
    
    def date(self):
        """دریافت تاریخ"""
        return self.jalali_widget.get_date()
    
    def setCalendarPopup(self, enabled):
        """تنظیم پاپ‌آپ تقویم"""
        # همیشه فعال است
        pass
    
    def widget(self):
        """دریافت ویجت شمسی برای قرار دادن در layout"""
        return self.jalali_widget

# تابع کمکی برای ایجاد ویجت تاریخ با تنظیمات مختلف
def create_jalali_date_widget(parent=None, mode='edit', theme='dark', show_time=False):
    """ایجاد ویجت تاریخ شمسی با تنظیمات دلخواه"""
    if mode == 'compat':  # حالت سازگاری کامل با QDateEdit
        widget = JalaliDateEditCompat(parent)
        return widget.widget()
    else:
        widget = JalaliDateInput(parent, mode=mode, theme=theme)
        return widget


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



# تست ویجت
if __name__ == "__main__":
    import sys
    from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QFormLayout
    
    class TestWindow(QMainWindow):
        def __init__(self):
            super().__init__()
            self.setWindowTitle("تست ویجت تاریخ شمسی")
            self.setGeometry(100, 100, 600, 400)
            
            central_widget = QWidget()
            self.setCentralWidget(central_widget)
            
            layout = QVBoxLayout(central_widget)
            
            form_layout = QFormLayout()
            
            # تست ویجت ساده
            self.date_widget1 = JalaliDateWidget()
            form_layout.addRow("تاریخ شمسی ساده:", self.date_widget1)
            
            # تست ویجت با زمان
            self.date_widget2 = JalaliDateWidget(show_time=True)
            form_layout.addRow("تاریخ و زمان شمسی:", self.date_widget2)
            
            # تست ویجت کامل تاریخ و زمان
            self.datetime_widget = JalaliDateTimeWidget()
            form_layout.addRow("تاریخ و زمان کامل:", self.datetime_widget)
            
            # تست ورودی تاریخ
            self.date_edit = JalaliDateEdit()
            form_layout.addRow("ورودی تاریخ:", self.date_edit)
            
            layout.addLayout(form_layout)
            
            # نمایش مقادیر
            self.date_widget1.date_changed.connect(self.on_date_changed)
            self.datetime_widget.datetime_changed.connect(self.on_datetime_changed)
            self.date_edit.date_changed.connect(self.on_date_edit_changed)
        
        def on_date_changed(self, date_str):
            print(f"تاریخ میلادی: {date_str}")
            print(f"تاریخ شمسی: {self.date_widget1.get_jalali_date()}")
        
        def on_datetime_changed(self, datetime_str):
            print(f"تاریخ و زمان میلادی: {datetime_str}")
            print(f"تاریخ و زمان شمسی: {self.datetime_widget.get_jalali_datetime()}")
        
        def on_date_edit_changed(self, date_str):
            print(f"تاریخ از JalaliDateEdit: {date_str}")
    
    app = QApplication(sys.argv)
    
    # تنظیم فونت فارسی
    font = QFont("B Nazanin", 10)
    app.setFont(font)
    
    window = TestWindow()
    window.show()
    
    sys.exit(app.exec())