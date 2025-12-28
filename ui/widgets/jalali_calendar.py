# ui/widgets/jalali_calendar.py
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                               QLabel, QGridLayout, QTableWidget, QTableWidgetItem,
                               QHeaderView, QDialog)
from PySide6.QtCore import (
    Signal,  # اضافه کردن Signal
    Slot,
    QObject,
    QDate,
    Qt,
    QSize,
    QPoint,
    QRect
)
from PySide6.QtGui import QFont
import jdatetime

class JalaliCalendarWidget(QWidget):
    """ویجت تقویم شمسی"""
    
    date_selected = Signal(jdatetime.date)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_date = jdatetime.date.today()
        self.selected_date = self.current_date
        self.init_ui()
        
    # در کلاس JalaliCalendarWidget، متد init_ui را به این صورت اصلاح کنید:
    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(5)
        
        # هدر تقویم
        header_layout = QHBoxLayout()
        
        self.prev_year_btn = QPushButton("⏪")
        self.prev_year_btn.setFixedSize(40, 30)
        self.prev_year_btn.clicked.connect(self.prev_year)
        self.prev_year_btn.setStyleSheet("""
            QPushButton {
                background-color: #2c3e50;
                color: white;
                border: 1px solid #34495e;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #34495e;
            }
        """)
        
        self.prev_month_btn = QPushButton("◀️")
        self.prev_month_btn.setFixedSize(40, 30)
        self.prev_month_btn.clicked.connect(self.prev_month)
        self.prev_month_btn.setStyleSheet("""
            QPushButton {
                background-color: #2c3e50;
                color: white;
                border: 1px solid #34495e;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #34495e;
            }
        """)
        
        self.date_label = QLabel()
        self.date_label.setAlignment(Qt.AlignCenter)
        self.date_label.setStyleSheet("""
            font-weight: bold; 
            font-size: 14px; 
            color: white;
            background-color: #2c3e50;
            padding: 5px;
            border-radius: 4px;
        """)
        
        self.next_month_btn = QPushButton("▶️")
        self.next_month_btn.setFixedSize(40, 30)
        self.next_month_btn.clicked.connect(self.next_month)
        self.next_month_btn.setStyleSheet("""
            QPushButton {
                background-color: #2c3e50;
                color: white;
                border: 1px solid #34495e;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #34495e;
            }
        """)
        
        self.next_year_btn = QPushButton("⏩")
        self.next_year_btn.setFixedSize(40, 30)
        self.next_year_btn.clicked.connect(self.next_year)
        self.next_year_btn.setStyleSheet("""
            QPushButton {
                background-color: #2c3e50;
                color: white;
                border: 1px solid #34495e;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #34495e;
            }
        """)
        
        header_layout.addWidget(self.prev_year_btn)
        header_layout.addWidget(self.prev_month_btn)
        header_layout.addWidget(self.date_label, 1)
        header_layout.addWidget(self.next_month_btn)
        header_layout.addWidget(self.next_year_btn)
        
        layout.addLayout(header_layout)
        
        # نام روزهای هفته
        days_layout = QGridLayout()
        days_layout.setSpacing(2)
        
        days = ['ش', 'ی', 'د', 'س', 'چ', 'پ', 'ج']
        for i, day in enumerate(days):
            label = QLabel(day)
            label.setAlignment(Qt.AlignCenter)
            label.setStyleSheet("""
                font-weight: bold; 
                color: white;
                background-color: #34495e;
                padding: 5px;
                border-radius: 3px;
            """)
            days_layout.addWidget(label, 0, i)
        
        # جدول روزها
        self.days_table = QTableWidget(6, 7)
        self.days_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.days_table.setSelectionMode(QTableWidget.SingleSelection)
        self.days_table.horizontalHeader().setVisible(False)
        self.days_table.verticalHeader().setVisible(False)
        self.days_table.setShowGrid(True)
        self.days_table.setStyleSheet("""
            QTableWidget {
                border: 1px solid #34495e;
                background-color: #2c3e50;
                gridline-color: #34495e;
            }
            QTableWidget::item {
                padding: 8px;
                text-align: center;
                color: white;
                border: none;
            }
            QTableWidget::item:hover {
                background-color: #34495e;
            }
            QTableWidget::item:selected {
                background-color: #3498db;
                color: white;
            }
        """)
        
        self.days_table.cellClicked.connect(self.on_day_selected)
        
        layout.addLayout(days_layout)
        layout.addWidget(self.days_table)
        
        # دکمه امروز
        self.today_btn = QPushButton("امروز")
        self.today_btn.clicked.connect(self.go_to_today)
        self.today_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2ecc71;
            }
        """)
        
        layout.addWidget(self.today_btn)
        
        # استایل کلی ویجت
        self.setStyleSheet("""
            JalaliCalendarWidget {
                background-color: #1a252f;
                border: 1px solid #34495e;
                border-radius: 8px;
                padding: 10px;
            }
        """)
        
        self.setLayout(layout)
        self.update_calendar()

        
    def update_calendar(self):
        """به‌روزرسانی تقویم"""
        # به‌روزرسانی عنوان
        month_names = [
            'فروردین', 'اردیبهشت', 'خرداد', 'تیر', 'مرداد', 'شهریور',
            'مهر', 'آبان', 'آذر', 'دی', 'بهمن', 'اسفند'
        ]
        month_name = month_names[self.current_date.month - 1]
        self.date_label.setText(f"{month_name} {self.current_date.year}")
        
        # پاک کردن جدول
        for i in range(6):
            for j in range(7):
                self.days_table.setItem(i, j, None)
        
        # محاسبه روز اول ماه
        first_day = jdatetime.date(self.current_date.year, self.current_date.month, 1)
        start_weekday = first_day.weekday()  # شنبه=0، جمعه=6
        
        # تعداد روزهای ماه
        if self.current_date.month <= 6:
            days_in_month = 31
        elif self.current_date.month <= 11:
            days_in_month = 30
        else:  # اسفند
            if jdatetime.jalali.isleap(self.current_date.year):
                days_in_month = 30
            else:
                days_in_month = 29
        
        # پر کردن روزها
        day = 1
        for week in range(6):
            for weekday in range(7):
                if week == 0 and weekday < start_weekday:
                    continue
                if day > days_in_month:
                    break
                
                item = QTableWidgetItem(str(day))
                item.setTextAlignment(Qt.AlignCenter)
                
                # اگر روز انتخاب شده است
                if (self.current_date.year == self.selected_date.year and
                    self.current_date.month == self.selected_date.month and
                    day == self.selected_date.day):
                    item.setBackground(Qt.blue)
                    item.setForeground(Qt.white)
                
                # اگر روز امروز است
                today = jdatetime.date.today()
                if (self.current_date.year == today.year and
                    self.current_date.month == today.month and
                    day == today.day):
                    item.setBackground(Qt.green)
                    item.setForeground(Qt.black)
                
                self.days_table.setItem(week, weekday, item)
                day += 1
        
        # تنظیم سایز ستون‌ها
        self.days_table.resizeRowsToContents()
        self.days_table.resizeColumnsToContents()
        
    def on_day_selected(self, row, col):
        """وقتی روزی انتخاب شد"""
        item = self.days_table.item(row, col)
        if item and item.text():
            day = int(item.text())
            self.selected_date = jdatetime.date(
                self.current_date.year,
                self.current_date.month,
                day
            )
            self.date_selected.emit(self.selected_date)
            self.update_calendar()
            
    def prev_month(self):
        """ماه قبل"""
        if self.current_date.month == 1:
            self.current_date = jdatetime.date(self.current_date.year - 1, 12, 1)
        else:
            self.current_date = jdatetime.date(
                self.current_date.year,
                self.current_date.month - 1,
                1
            )
        self.update_calendar()
        
    def next_month(self):
        """ماه بعد"""
        if self.current_date.month == 12:
            self.current_date = jdatetime.date(self.current_date.year + 1, 1, 1)
        else:
            self.current_date = jdatetime.date(
                self.current_date.year,
                self.current_date.month + 1,
                1
            )
        self.update_calendar()
        
    def prev_year(self):
        """سال قبل"""
        self.current_date = jdatetime.date(self.current_date.year - 1, self.current_date.month, 1)
        self.update_calendar()
        
    def next_year(self):
        """سال بعد"""
        self.current_date = jdatetime.date(self.current_date.year + 1, self.current_date.month, 1)
        self.update_calendar()
        
    def go_to_today(self):
        """برو به امروز"""
        self.current_date = jdatetime.date.today()
        self.selected_date = self.current_date
        self.update_calendar()
        self.date_selected.emit(self.selected_date)
        
    def get_selected_date(self):
        """دریافت تاریخ انتخاب شده"""
        return self.selected_date
        
    def set_selected_date(self, date):
        """تنظیم تاریخ انتخاب شده"""
        if isinstance(date, jdatetime.date):
            self.selected_date = date
            self.current_date = jdatetime.date(date.year, date.month, 1)
            self.update_calendar()

class JalaliCalendarDialog(QDialog):
    """دیالوگ تقویم شمسی"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("تقویم شمسی")
        self.setModal(True)
        self.setFixedSize(400, 450)
        
        layout = QVBoxLayout()
        
        # ویجت تقویم
        self.calendar = JalaliCalendarWidget()
        layout.addWidget(self.calendar)
        
        # دکمه‌ها
        buttons_layout = QHBoxLayout()
        
        self.ok_btn = QPushButton("تأیید")
        self.ok_btn.clicked.connect(self.accept)
        
        self.cancel_btn = QPushButton("انصراف")
        self.cancel_btn.clicked.connect(self.reject)
        
        buttons_layout.addWidget(self.ok_btn)
        buttons_layout.addWidget(self.cancel_btn)
        layout.addLayout(buttons_layout)
        
        self.setLayout(layout)
        
    def get_selected_date(self):
        """دریافت تاریخ انتخابی"""
        return self.calendar.get_selected_date()
        
    def set_selected_date(self, date):
        """تنظیم تاریخ"""
        self.calendar.set_selected_date(date)