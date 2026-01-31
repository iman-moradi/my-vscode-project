# ui/forms/inventory/widgets/inventory_date_input.py
"""
ویجت ورود تاریخ شمسی مخصوص انبار - نسخه بهبود یافته
"""

from PySide6.QtWidgets import QWidget, QHBoxLayout, QPushButton, QLineEdit, QToolButton, QMenu, QApplication
from PySide6.QtCore import Qt, Signal, QDate, QTimer
from PySide6.QtGui import QFont, QIcon, QAction
import jdatetime
from datetime import datetime
import locale

class InventoryDateInput(QWidget):
    """ویجت ورود تاریخ شمسی با استایل مدرن"""
    
    date_changed = Signal(jdatetime.date)
    
    def __init__(self, parent=None, with_today_button=True, with_calendar=True):
        super().__init__(parent)
        self.with_today_button = with_today_button
        self.with_calendar = with_calendar
        self.setup_ui()
        self.setup_connections()
    
    def setup_ui(self):
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(3)
        
        # فیلد ورود تاریخ
        self.date_input = QLineEdit()
        self.date_input.setFixedWidth(100)
        self.date_input.setAlignment(Qt.AlignCenter)
        self.date_input.setStyleSheet("""
            QLineEdit {
                background-color: #f8f9fa;
                border: 2px solid #dee2e6;
                border-radius: 6px;
                padding: 6px;
                font-family: 'B Nazanin';
                font-size: 12px;
                color: #495057;
            }
            QLineEdit:focus {
                border: 2px solid #4dabf7;
                background-color: #ffffff;
            }
        """)
        
        layout.addWidget(self.date_input)
        
        # دکمه تقویم
        if self.with_calendar:
            self.calendar_btn = QToolButton()
            self.calendar_btn.setText("📅")
            self.calendar_btn.setFixedSize(30, 30)
            self.calendar_btn.setStyleSheet("""
                QToolButton {
                    background-color: #4dabf7;
                    border: none;
                    border-radius: 6px;
                    color: white;
                    font-size: 14px;
                }
                QToolButton:hover {
                    background-color: #339af0;
                }
                QToolButton:pressed {
                    background-color: #1c7ed6;
                }
            """)
            layout.addWidget(self.calendar_btn)
        
        # دکمه امروز
        if self.with_today_button:
            self.today_btn = QToolButton()
            self.today_btn.setText("امروز")
            self.today_btn.setFixedSize(60, 30)
            self.today_btn.setStyleSheet("""
                QToolButton {
                    background-color: #51cf66;
                    border: none;
                    border-radius: 6px;
                    color: white;
                    font-family: 'B Nazanin';
                    font-size: 11px;
                    padding: 0px 5px;
                }
                QToolButton:hover {
                    background-color: #40c057;
                }
                QToolButton:pressed {
                    background-color: #2f9e44;
                }
            """)
            layout.addWidget(self.today_btn)
        
        # دکمه پاک کردن
        self.clear_btn = QToolButton()
        self.clear_btn.setText("✕")
        self.clear_btn.setFixedSize(30, 30)
        self.clear_btn.setStyleSheet("""
            QToolButton {
                background-color: #ff6b6b;
                border: none;
                border-radius: 6px;
                color: white;
                font-size: 12px;
            }
            QToolButton:hover {
                background-color: #fa5252;
            }
            QToolButton:pressed {
                background-color: #e03131;
            }
        """)
        layout.addWidget(self.clear_btn)
        
        self.setLayout(layout)
        
        # تنظیم تاریخ امروز به صورت پیش‌فرض
        self.set_date_to_today()
    
    def setup_connections(self):
        if hasattr(self, 'today_btn'):
            self.today_btn.clicked.connect(self.set_date_to_today)
        
        if hasattr(self, 'calendar_btn'):
            self.calendar_btn.clicked.connect(self.show_calendar_menu)
        
        self.clear_btn.clicked.connect(self.clear)
        self.date_input.textChanged.connect(self.on_text_changed)
    
    def show_calendar_menu(self):
        """نمایش منوی تقویم سریع"""
        menu = QMenu(self)
        
        # روزهای خاص
        today_action = QAction("📅 امروز", self)
        today_action.triggered.connect(self.set_date_to_today)
        menu.addAction(today_action)
        
        menu.addSeparator()
        
        # 7 روز گذشته
        for i in range(1, 8):
            date = jdatetime.date.today() - jdatetime.timedelta(days=i)
            action = QAction(f"📅 {date.strftime('%Y/%m/%d')}", self)
            action.triggered.connect(lambda checked, d=date: self.set_date(d))
            menu.addAction(action)
        
        menu.addSeparator()
        
        # 7 روز آینده
        for i in range(1, 8):
            date = jdatetime.date.today() + jdatetime.timedelta(days=i)
            action = QAction(f"📅 {date.strftime('%Y/%m/%d')}", self)
            action.triggered.connect(lambda checked, d=date: self.set_date(d))
            menu.addAction(action)
        
        menu.exec(self.calendar_btn.mapToGlobal(self.calendar_btn.rect().bottomLeft()))
    
    def set_date(self, date):
        """تنظیم تاریخ"""
        if isinstance(date, jdatetime.date):
            self.current_date = date
            self.date_input.setText(date.strftime("%Y/%m/%d"))
            self.date_changed.emit(date)
        elif isinstance(date, str):
            try:
                if '/' in date:
                    year, month, day = map(int, date.split('/'))
                    self.current_date = jdatetime.date(year, month, day)
                elif '-' in date:
                    year, month, day = map(int, date.split('-'))
                    self.current_date = jdatetime.date(year, month, day)
                self.date_input.setText(self.current_date.strftime("%Y/%m/%d"))
                self.date_changed.emit(self.current_date)
            except:
                self.set_date_to_today()
    
    def set_date_to_today(self):
        """تنظیم تاریخ به امروز"""
        today = jdatetime.date.today()
        self.set_date(today)
        return today
    
    def get_date(self):
        """دریافت تاریخ"""
        text = self.date_input.text().strip()
        if not text:
            return jdatetime.date.today()
        
        try:
            if '/' in text:
                year, month, day = map(int, text.split('/'))
                return jdatetime.date(year, month, day)
            elif '-' in text:
                year, month, day = map(int, text.split('-'))
                return jdatetime.date(year, month, day)
        except:
            return jdatetime.date.today()
    
    def get_date_string(self, format_str="%Y-%m-%d"):
        """دریافت تاریخ به صورت رشته"""
        date_obj = self.get_date()
        return date_obj.strftime(format_str)
    
    def get_gregorian_date(self):
        """دریافت تاریخ میلادی"""
        jdate = self.get_date()
        gdate = jdate.togregorian()
        return gdate
    
    def get_gregorian_string(self, format_str="%Y-%m-%d"):
        """دریافت تاریخ میلادی به صورت رشته"""
        gdate = self.get_gregorian_date()
        return gdate.strftime(format_str)
    
    def text(self):
        """دریافت متن"""
        return self.date_input.text()
    
    def clear(self):
        """پاک کردن تاریخ"""
        self.date_input.clear()
        self.set_date_to_today()
    
    def on_text_changed(self, text):
        """وقتی متن تغییر کرد"""
        if len(text) == 10 and ('/' in text or '-' in text):
            try:
                if '/' in text:
                    year, month, day = map(int, text.split('/'))
                    date_obj = jdatetime.date(year, month, day)
                elif '-' in text:
                    year, month, day = map(int, text.split('-'))
                    date_obj = jdatetime.date(year, month, day)
                
                self.current_date = date_obj
                self.date_changed.emit(date_obj)
            except:
                pass
    
    def set_placeholder(self, text):
        """تنظیم متن راهنما"""
        self.date_input.setPlaceholderText(text)
    
    def set_readonly(self, readonly=True):
        """تنظیم حالت فقط خواندنی"""
        self.date_input.setReadOnly(readonly)
        if readonly:
            self.date_input.setStyleSheet("""
                QLineEdit {
                    background-color: #e9ecef;
                    border: 1px solid #ced4da;
                    border-radius: 6px;
                    padding: 6px;
                    font-family: 'B Nazanin';
                    font-size: 12px;
                    color: #6c757d;
                }
            """)