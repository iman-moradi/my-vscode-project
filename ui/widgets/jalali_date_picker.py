# ui/widgets/jalali_date_picker.py
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, 
    QPushButton, QDialog, QGridLayout, QLabel,
    QComboBox, QApplication
)
from PySide6.QtCore import Qt, Signal, QDate
from PySide6.QtGui import QFont, QIcon
import jdatetime
from datetime import datetime


class JalaliDatePicker(QWidget):
    """ویجت انتخاب تاریخ شمسی با تقویم شمسی واقعی"""
    
    date_changed = Signal(jdatetime.date)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_date = jdatetime.date.today()
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)
        
        # بخش نمایش تاریخ
        self.date_line = QLineEdit()
        self.date_line.setReadOnly(True)
        self.date_line.setStyleSheet("""
            QLineEdit {
                background-color: #222222;
                border: 1px solid #333;
                color: white;
                border-radius: 4px;
                padding: 8px;
                font-family: 'B Nazanin';
                font-size: 12pt;
            }
        """)
        
        layout.addWidget(self.date_line)
        
        # دکمه باز کردن تقویم
        self.calendar_btn = QPushButton("📅 باز کردن تقویم شمسی")
        self.calendar_btn.setStyleSheet("""
            QPushButton {
                background-color: #2c3e50;
                color: white;
                border: 1px solid #34495e;
                border-radius: 4px;
                padding: 6px;
                font-family: 'B Nazanin';
            }
            QPushButton:hover {
                background-color: #3498db;
            }
        """)
        self.calendar_btn.clicked.connect(self.show_calendar_dialog)
        
        layout.addWidget(self.calendar_btn)
        
        # بخش انتخاب سریع تاریخ
        quick_select_layout = QHBoxLayout()
        
        today_btn = QPushButton("امروز")
        today_btn.clicked.connect(lambda: self.set_date(jdatetime.date.today()))
        today_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                padding: 5px;
                border-radius: 3px;
            }
        """)
        
        yesterday_btn = QPushButton("دیروز")
        yesterday_btn.clicked.connect(lambda: self.set_date(jdatetime.date.today() - jdatetime.timedelta(days=1)))
        yesterday_btn.setStyleSheet("""
            QPushButton {
                background-color: #f39c12;
                color: white;
                padding: 5px;
                border-radius: 3px;
            }
        """)
        
        quick_select_layout.addWidget(today_btn)
        quick_select_layout.addWidget(yesterday_btn)
        quick_select_layout.addStretch()
        
        layout.addLayout(quick_select_layout)
        
        self.setLayout(layout)
        self.update_display()
    
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
    
    def update_display(self):
        """به‌روزرسانی نمایش تاریخ"""
        month_names = [
            'فروردین', 'اردیبهشت', 'خرداد', 'تیر', 'مرداد', 'شهریور',
            'مهر', 'آبان', 'آذر', 'دی', 'بهمن', 'اسفند'
        ]
        
        day_name = self.get_day_name(self.current_date.weekday())
        month_name = month_names[self.current_date.month - 1]
        
        date_str = f"{day_name}، {self.current_date.day} {month_name} {self.current_date.year}"
        self.date_line.setText(date_str)
    
    def get_day_name(self, weekday):
        """دریافت نام روز هفته"""
        days = ['شنبه', 'یکشنبه', 'دوشنبه', 'سه‌شنبه', 'چهارشنبه', 'پنجشنبه', 'جمعه']
        return days[weekday]
    
    def show_calendar_dialog(self):
        """نمایش دیالوگ تقویم شمسی"""
        dialog = JalaliCalendarDialog(self)
        dialog.set_selected_date(self.current_date)
        
        if dialog.exec():
            selected_date = dialog.get_selected_date()
            self.set_date(selected_date)


class JalaliCalendarDialog(QDialog):
    """دیالوگ تقویم شمسی"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("تقویم شمسی")
        self.setModal(True)
        self.setMinimumSize(400, 400)
        self.setStyleSheet("""
            QDialog {
                background-color: #000000;
                color: white;
                font-family: 'B Nazanin';
            }
        """)
        
        self.current_date = jdatetime.date.today()
        self.selected_date = self.current_date
        
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # هدر تقویم
        header_layout = QHBoxLayout()
        
        self.year_combo = QComboBox()
        self.year_combo.setStyleSheet("""
            QComboBox {
                background-color: #222222;
                color: white;
                padding: 5px;
                border-radius: 4px;
            }
        """)
        
        self.month_combo = QComboBox()
        self.month_combo.setStyleSheet("""
            QComboBox {
                background-color: #222222;
                color: white;
                padding: 5px;
                border-radius: 4px;
            }
        """)
        
        # پر کردن سال‌ها
        current_year = self.current_date.year
        for year in range(current_year - 10, current_year + 11):
            self.year_combo.addItem(str(year), year)
        
        # پر کردن ماه‌ها
        month_names = [
            'فروردین', 'اردیبهشت', 'خرداد', 'تیر', 'مرداد', 'شهریور',
            'مهر', 'آبان', 'آذر', 'دی', 'بهمن', 'اسفند'
        ]
        for i, name in enumerate(month_names, 1):
            self.month_combo.addItem(name, i)
        
        header_layout.addWidget(QLabel("سال:"))
        header_layout.addWidget(self.year_combo)
        header_layout.addWidget(QLabel("ماه:"))
        header_layout.addWidget(self.month_combo)
        
        layout.addLayout(header_layout)
        
        # تقویم
        self.calendar_grid = QGridLayout()
        self.calendar_grid.setSpacing(2)
        
        # نام روزهای هفته
        days = ['ش', 'ی', 'د', 'س', 'چ', 'پ', 'ج']
        for i, day in enumerate(days):
            day_label = QLabel(day)
            day_label.setAlignment(Qt.AlignCenter)
            day_label.setStyleSheet("""
                QLabel {
                    font-weight: bold;
                    color: #3498db;
                    padding: 5px;
                    background-color: #1a252f;
                    border-radius: 3px;
                }
            """)
            self.calendar_grid.addWidget(day_label, 0, i)
        
        layout.addLayout(self.calendar_grid)
        
        # دکمه‌ها
        button_layout = QHBoxLayout()
        
        select_btn = QPushButton("انتخاب")
        select_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                padding: 8px 20px;
                border-radius: 4px;
            }
        """)
        select_btn.clicked.connect(self.accept)
        
        cancel_btn = QPushButton("انصراف")
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                padding: 8px 20px;
                border-radius: 4px;
            }
        """)
        cancel_btn.clicked.connect(self.reject)
        
        button_layout.addStretch()
        button_layout.addWidget(select_btn)
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
        
        # اتصال سیگنال‌ها
        self.year_combo.currentIndexChanged.connect(self.update_calendar)
        self.month_combo.currentIndexChanged.connect(self.update_calendar)
        
        # تنظیم مقادیر اولیه
        self.year_combo.setCurrentIndex(10)  # سال جاری
        self.month_combo.setCurrentIndex(self.current_date.month - 1)
        
        self.update_calendar()
    
    def update_calendar(self):
        """به‌روزرسانی تقویم"""
        # پاک کردن سلول‌های قبلی
        for i in reversed(range(self.calendar_grid.count())):
            widget = self.calendar_grid.itemAt(i).widget()
            if widget and i >= 7:  # بعد از نام روزها
                widget.deleteLater()
        
        # دریافت سال و ماه انتخاب شده
        year = self.year_combo.currentData()
        month = self.month_combo.currentData()
        
        # محاسبه روز اول ماه
        first_day = jdatetime.date(year, month, 1)
        start_weekday = first_day.weekday()  # 0=شنبه, 6=جمعه
        
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
                day_btn.setFixedSize(40, 40)
                
                # بررسی اگر امروز است
                today = jdatetime.date.today()
                if year == today.year and month == today.month and day == today.day:
                    day_btn.setStyleSheet("""
                        QPushButton {
                            background-color: #27ae60;
                            color: white;
                            font-weight: bold;
                            border-radius: 5px;
                        }
                        QPushButton:hover {
                            background-color: #2ecc71;
                        }
                    """)
                # بررسی اگر تاریخ انتخاب شده است
                elif (year == self.selected_date.year and 
                      month == self.selected_date.month and 
                      day == self.selected_date.day):
                    day_btn.setStyleSheet("""
                        QPushButton {
                            background-color: #3498db;
                            color: white;
                            font-weight: bold;
                            border-radius: 5px;
                        }
                        QPushButton:hover {
                            background-color: #2980b9;
                        }
                    """)
                else:
                    day_btn.setStyleSheet("""
                        QPushButton {
                            background-color: #2c3e50;
                            color: white;
                            border-radius: 5px;
                        }
                        QPushButton:hover {
                            background-color: #34495e;
                        }
                    """)
                
                # اتصال کلیک
                day_btn.clicked.connect(lambda checked, d=day: self.select_day(d))
                
                self.calendar_grid.addWidget(day_btn, row, col)
                day += 1
            
            row += 1
    
    def select_day(self, day):
        """انتخاب روز"""
        year = self.year_combo.currentData()
        month = self.month_combo.currentData()
        self.selected_date = jdatetime.date(year, month, day)
        self.update_calendar()
    
    def set_selected_date(self, date):
        """تنظیم تاریخ انتخاب شده"""
        self.selected_date = date
        self.year_combo.setCurrentText(str(date.year))
        self.month_combo.setCurrentIndex(date.month - 1)
        self.update_calendar()
    
    def get_selected_date(self):
        """دریافت تاریخ انتخاب شده"""
        return self.selected_date