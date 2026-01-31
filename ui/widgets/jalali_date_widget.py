"""
ویجت تاریخ شمسی حرفه‌ای با کلیک روی فیلد
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLineEdit, 
    QDialog, QGridLayout, QLabel,
    QComboBox, QPushButton, QFrame
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QMouseEvent
import jdatetime
from datetime import datetime


class JalaliDateWidget(QWidget):
    """ویجت انتخاب تاریخ شمسی - کلیک روی فیلد برای باز کردن تقویم"""
    
    date_changed = Signal(jdatetime.date)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_date = jdatetime.date.today()
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # فیلد نمایش تاریخ - با کلیک برای باز کردن تقویم
        self.date_input = QLineEdit()
        self.date_input.setReadOnly(True)
        self.date_input.setCursor(Qt.PointingHandCursor)  # نشانگر دست
        self.date_input.setStyleSheet("""
            QLineEdit {
                background-color: #222222;
                border: 1px solid #333;
                color: white;
                border-radius: 4px;
                padding: 10px;
                font-family: 'B Nazanin';
                font-size: 13pt;
                min-height: 45px;
                text-align: center;
                selection-background-color: #2ecc71;
            }
            QLineEdit:hover {
                border: 2px solid #2ecc71;
                background-color: #1a1a1a;
            }
            QLineEdit:focus {
                border: 2px solid #3498db;
            }
        """)
        
        # اضافه کردن آیکون تقویم در سمت چپ
        self.date_input.setTextMargins(10, 0, 10, 0)
        
        # اتصال کلیک به باز کردن تقویم
        self.date_input.mousePressEvent = self.open_calendar
        
        layout.addWidget(self.date_input)
        self.setLayout(layout)
        self.update_display()
    
    def update_display(self):
        """به‌روزرسانی نمایش تاریخ - با فرمت YYYY/MM/DD"""
        # نمایش به صورت: 1404/11/03
        date_str = f"{self.current_date.year:04d}/{self.current_date.month:02d}/{self.current_date.day:02d}"
        self.date_input.setText(date_str)
    
    def open_calendar(self, event):
        """باز کردن تقویم حرفه‌ای با کلیک روی فیلد"""
        dialog = ProfessionalJalaliCalendar(self.current_date, self)
        
        if dialog.exec():
            selected_date = dialog.get_selected_date()
            self.set_date(selected_date)
    
    def set_date(self, jalali_date):
        """تنظیم تاریخ شمسی"""
        if isinstance(jalali_date, jdatetime.datetime):
            jalali_date = jalali_date.date()
        
        self.current_date = jalali_date
        self.update_display()
        self.date_changed.emit(self.current_date)
    
    def get_date(self):
        """دریافت تاریخ شمسی"""
        return self.current_date
    
    def get_date_string(self, format_str="%Y/%m/%d"):
        """دریافت تاریخ به صورت رشته"""
        return self.current_date.strftime(format_str)


class ProfessionalJalaliCalendar(QDialog):
    """تقویم شمسی حرفه‌ای"""
    
    def __init__(self, initial_date, parent=None):
        super().__init__(parent)
        self.selected_date = initial_date
        self.setup_ui()
        
    def setup_ui(self):
        self.setWindowTitle("تقویم شمسی")
        self.setModal(True)
        self.setFixedSize(450, 500)
        
        # استایل حرفه‌ای
        self.setStyleSheet("""
            QDialog {
                background-color: #0a0a0a;
                color: white;
                font-family: 'B Nazanin';
            }
            QLabel {
                color: white;
            }
            QComboBox {
                background-color: #1a1a1a;
                color: white;
                border: 1px solid #333;
                border-radius: 4px;
                padding: 6px;
                min-height: 30px;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox::down-arrow {
                image: url(data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIyNCIgaGVpZ2h0PSIyNCIgdmlld0JveD0iMCAwIDI0IDI0IiBmaWxsPSJ3aGl0ZSI+PHBhdGggZD0iTTcgMTBsNSA1IDUtNXoiLz48L3N2Zz4=);
                width: 16px;
                height: 16px;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(15, 15, 15, 15)
        
        # هدر تقویم با پس‌زمینه زیبا
        header_frame = QFrame()
        header_frame.setStyleSheet("""
            QFrame {
                background-color: #1a252f;
                border-radius: 8px;
                padding: 10px;
            }
        """)
        
        header_layout = QGridLayout(header_frame)
        header_layout.setSpacing(10)
        
        # سال
        year_label = QLabel("سال:")
        year_label.setStyleSheet("font-weight: bold; color: #3498db;")
        self.year_combo = QComboBox()
        self.year_combo.setStyleSheet("""
            QComboBox {
                background-color: #2c3e50;
                color: white;
                border: 2px solid #3498db;
                border-radius: 6px;
                padding: 8px;
                font-size: 12pt;
                font-weight: bold;
            }
        """)
        
        # ماه
        month_label = QLabel("ماه:")
        month_label.setStyleSheet("font-weight: bold; color: #3498db;")
        self.month_combo = QComboBox()
        self.month_combo.setStyleSheet("""
            QComboBox {
                background-color: #2c3e50;
                color: white;
                border: 2px solid #3498db;
                border-radius: 6px;
                padding: 8px;
                font-size: 12pt;
                font-weight: bold;
            }
        """)
        
        # پر کردن سال‌ها
        current_year = jdatetime.date.today().year
        for year in range(current_year - 5, current_year + 6):
            self.year_combo.addItem(str(year), year)
        
        # پر کردن ماه‌ها
        month_names = [
            'فروردین', 'اردیبهشت', 'خرداد', 'تیر', 'مرداد', 'شهریور',
            'مهر', 'آبان', 'آذر', 'دی', 'بهمن', 'اسفند'
        ]
        for i, name in enumerate(month_names, 1):
            self.month_combo.addItem(name, i)
        
        header_layout.addWidget(year_label, 0, 0)
        header_layout.addWidget(self.year_combo, 0, 1)
        header_layout.addWidget(month_label, 0, 2)
        header_layout.addWidget(self.month_combo, 0, 3)
        
        layout.addWidget(header_frame)
        
        # نمایش تاریخ انتخاب شده
        self.selected_date_label = QLabel()
        self.selected_date_label.setAlignment(Qt.AlignCenter)
        self.selected_date_label.setStyleSheet("""
            QLabel {
                font-weight: bold;
                color: #2ecc71;
                font-size: 14pt;
                padding: 10px;
                background-color: #1a252f;
                border-radius: 8px;
                border: 2px solid #2ecc71;
            }
        """)
        layout.addWidget(self.selected_date_label)
        
        # شبکه روزهای هفته
        self.calendar_grid = QGridLayout()
        self.calendar_grid.setSpacing(3)
        self.calendar_grid.setContentsMargins(5, 5, 5, 5)
        
        # نام روزهای هفته
        days_of_week = ['ش', 'ی', 'د', 'س', 'چ', 'پ', 'ج']
        for i, day in enumerate(days_of_week):
            day_label = QLabel(day)
            day_label.setAlignment(Qt.AlignCenter)
            day_label.setFixedHeight(35)
            day_label.setStyleSheet("""
                QLabel {
                    font-weight: bold;
                    color: #3498db;
                    background-color: #1a252f;
                    border-radius: 5px;
                    padding: 5px;
                    font-size: 11pt;
                }
            """)
            self.calendar_grid.addWidget(day_label, 0, i)
        
        layout.addLayout(self.calendar_grid)
        
        # دکمه‌های پایین
        button_layout = QGridLayout()
        
        # دکمه امروز
        today_btn = QPushButton("📅 امروز")
        today_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border-radius: 6px;
                padding: 12px;
                font-weight: bold;
                font-size: 11pt;
                border: none;
            }
            QPushButton:hover {
                background-color: #2ecc71;
            }
        """)
        today_btn.clicked.connect(self.set_today)
        
        # دکمه تأیید
        confirm_btn = QPushButton("✅ تأیید")
        confirm_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border-radius: 6px;
                padding: 12px;
                font-weight: bold;
                font-size: 11pt;
                border: none;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        confirm_btn.clicked.connect(self.accept)
        
        # دکمه انصراف
        cancel_btn = QPushButton("❌ انصراف")
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border-radius: 6px;
                padding: 12px;
                font-weight: bold;
                font-size: 11pt;
                border: none;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        cancel_btn.clicked.connect(self.reject)
        
        button_layout.addWidget(today_btn, 0, 0)
        button_layout.addWidget(confirm_btn, 0, 1)
        button_layout.addWidget(cancel_btn, 0, 2)
        
        layout.addLayout(button_layout)
        
        # اتصال سیگنال‌ها
        self.year_combo.currentIndexChanged.connect(self.update_calendar)
        self.month_combo.currentIndexChanged.connect(self.update_calendar)
        
        # تنظیم مقادیر اولیه
        self.year_combo.setCurrentText(str(self.selected_date.year))
        self.month_combo.setCurrentIndex(self.selected_date.month - 1)
        
        self.update_calendar()
    
    def update_calendar(self):
        """به‌روزرسانی تقویم - نسخه اصلاح شده"""
        # پاک کردن سلول‌های قبلی
        for i in reversed(range(self.calendar_grid.count())):
            widget = self.calendar_grid.itemAt(i).widget()
            if widget and i >= 7:  # بعد از نام روزها
                widget.deleteLater()
        
        # دریافت سال و ماه انتخاب شده
        # 🔴 اصلاح شده: استفاده از currentData به جای currentText برای دریافت عدد ماه
        year = int(self.year_combo.currentText())
        month = self.month_combo.currentData()  # این عدد ماه (1 تا 12) را برمی‌گرداند
        
        # اگر به هر دلیلی داده‌ای نبود (احتیاط)
        if month is None:
            month = 1

        # محاسبه روز اول ماه
        try:
            first_day = jdatetime.date(year, month, 1)
            start_weekday = first_day.weekday()  # 0=شنبه, 6=جمعه
        except:
            return
        
        # تعداد روزهای ماه
        if month <= 6:
            days_in_month = 31
        elif month <= 11:
            days_in_month = 30
        else:
            if jdatetime.jalali.isleap(year):
                days_in_month = 30
            else:
                days_in_month = 29
        
        # پر کردن تقویم
        day = 1
        row = 1
        
        while day <= days_in_month:
            for col in range(7):
                if day == 1 and col < start_weekday:
                    continue
                
                if day > days_in_month:
                    break
                
                # ایجاد دکمه روز
                day_btn = QPushButton(str(day))
                day_btn.setFixedSize(45, 45)
                
                # تعیین استایل بر اساس وضعیت روز
                today = jdatetime.date.today()
                is_today = (year == today.year and month == today.month and day == today.day)
                is_selected = (year == self.selected_date.year and 
                              month == self.selected_date.month and 
                              day == self.selected_date.day)
                
                if is_today and is_selected:
                    style = """
                        QPushButton {
                            background-color: #f39c12;
                            color: white;
                            font-weight: bold;
                            border-radius: 8px;
                            border: 3px solid #e74c3c;
                        }
                        QPushButton:hover {
                            background-color: #e67e22;
                        }
                    """
                elif is_today:
                    style = """
                        QPushButton {
                            background-color: #27ae60;
                            color: white;
                            font-weight: bold;
                            border-radius: 8px;
                        }
                        QPushButton:hover {
                            background-color: #2ecc71;
                        }
                    """
                elif is_selected:
                    style = """
                        QPushButton {
                            background-color: #3498db;
                            color: white;
                            font-weight: bold;
                            border-radius: 8px;
                            border: 2px solid #2ecc71;
                        }
                        QPushButton:hover {
                            background-color: #2980b9;
                        }
                    """
                else:
                    style = """
                        QPushButton {
                            background-color: #2c3e50;
                            color: white;
                            border-radius: 8px;
                        }
                        QPushButton:hover {
                            background-color: #34495e;
                            border: 2px solid #3498db;
                        }
                    """
                
                day_btn.setStyleSheet(style)
                day_btn.clicked.connect(lambda checked, d=day: self.select_day(d))
                
                self.calendar_grid.addWidget(day_btn, row, col)
                day += 1
            
            row += 1
        
        # به‌روزرسانی نمایش تاریخ انتخاب شده
        self.update_selected_label()

    def update_selected_label(self):
        """به‌روزرسانی نمایش تاریخ انتخاب شده"""
        date_str = f"{self.selected_date.year:04d}/{self.selected_date.month:02d}/{self.selected_date.day:02d}"
        self.selected_date_label.setText(f"📅 تاریخ انتخاب شده: {date_str}")
    
    def select_day(self, day):
        """انتخاب روز - نسخه اصلاح شده"""
        # دریافت سال و ماه انتخاب شده
        year = int(self.year_combo.currentText())
        
        # 🔴 اصلاح شده: استفاده از currentData به جای currentText
        month = self.month_combo.currentData()
        
        # اگر به هر دلیلی داده‌ای نبود (احتیاط)
        if month is None:
            month = 1
            
        self.selected_date = jdatetime.date(year, month, day)
        self.update_calendar()
    
    def set_today(self):
        """تنظیم تاریخ امروز"""
        today = jdatetime.date.today()
        self.selected_date = today
        self.year_combo.setCurrentText(str(today.year))
        self.month_combo.setCurrentIndex(today.month - 1)
        self.update_calendar()
    
    def get_selected_date(self):
        """دریافت تاریخ انتخاب شده"""
        return self.selected_date


# کلاس‌های مستعار برای سازگاری
JalaliDatePicker = JalaliDateWidget
JalaliDateInput = JalaliDateWidget