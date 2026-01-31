# ui/forms/inventory/base_inventory_form.py
"""
کلاس پایه برای تمام فرم‌های انبار
تم مشکی کامل - متن سفید - راست‌چین
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QLineEdit, QComboBox, QTableWidget,
    QTableWidgetItem, QHeaderView, QMessageBox,
    QGroupBox, QFormLayout, QSpinBox, QDoubleSpinBox,
    QDateEdit, QTextEdit, QCheckBox, QTabWidget,
    QScrollArea, QFrame, QSizePolicy,QGridLayout
)
from PySide6.QtCore import Qt, Signal, QDate, QTimer
from PySide6.QtGui import QFont, QColor, QPalette
import jdatetime
from datetime import datetime

class BaseInventoryForm(QWidget):
    """فرم پایه انبار با تم مشکی کامل و راست‌چین"""
    
    data_saved = Signal()
    data_changed = Signal()
    
    def __init__(self, title="انبار", parent=None):
        # بررسی اینکه parent واقعاً یک ویجت Qt باشد
        if parent is not None and not isinstance(parent, QWidget):
            # اگر parent داده‌منیجر است، None بگذار
            if hasattr(parent, 'data_manager'):
                # parent اصلی را None می‌گذاریم
                super().__init__(None)
                self.data_manager = parent.data_manager if hasattr(parent, 'data_manager') else None
            else:
                super().__init__(None)
                self.data_manager = None
        else:
            # parent معتبر است
            super().__init__(parent)
            self.data_manager = parent.data_manager if parent and hasattr(parent, 'data_manager') else None
        
        self.title = title
        self.data_manager = parent.data_manager if parent and hasattr(parent, 'data_manager') else None
            
        # ایجاد layout اصلی با اسکرول
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QFrame.NoFrame)
        
        self.scroll_content = QWidget()
        self.main_layout = QVBoxLayout(self.scroll_content)
        self.main_layout.setContentsMargins(15, 15, 15, 15)
        self.main_layout.setSpacing(10)
        
        self.scroll_area.setWidget(self.scroll_content)
        
        # Layout اصلی برای ویجت
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.scroll_area)
        
        self.apply_black_theme()
        self.set_rtl_layout()
        #self.setup_ui()

    def format_date(self, date_str):
        """فرمت کردن تاریخ (تبدیل میلادی به شمسی)"""
        try:
            if not date_str:
                return ""
            
            # اگر تاریخ شمسی است
            if isinstance(date_str, str) and ('/' in date_str or '-' in date_str):
                # بررسی اگر تاریخ شمسی است
                try:
                    parts = date_str.replace('-', '/').split('/')
                    if len(parts) == 3:
                        year, month, day = map(int, parts)
                        # اگر تاریخ شمسی است (سال بین 1300 تا 1500)
                        if 1300 <= year <= 1500:
                            jalali_date = jdatetime.date(year, month, day)
                            return f"{jalali_date.year:04d}/{jalali_date.month:02d}/{jalali_date.day:02d}"
                except:
                    pass
            
            # تبدیل میلادی به شمسی
            if isinstance(date_str, str):
                # فرمت‌های مختلف تاریخ میلادی
                for fmt in ["%Y-%m-%d", "%Y/%m/%d", "%Y-%m-%d %H:%M:%S", "%Y/%m/%d %H:%M:%S"]:
                    try:
                        date_obj = datetime.strptime(date_str, fmt)
                        jalali_date = jdatetime.date.fromgregorian(date=date_obj.date())
                        return f"{jalali_date.year:04d}/{jalali_date.month:02d}/{jalali_date.day:02d}"
                    except:
                        continue
            
            return str(date_str)
        except:
            return date_str
        
    def create_stat_card(self, title, icon, color, value):
        """ایجاد کارت آمار"""
        card = QFrame()
        card.setFrameShape(QFrame.StyledPanel)
        card.setStyleSheet(f"""
            QFrame {{
                background-color: #{color}20;
                border: 2px solid #{color};
                border-radius: 10px;
                padding: 15px;
            }}
        """)
        
        layout = QVBoxLayout()
        
        # هدر کارت
        header_layout = QHBoxLayout()
        icon_label = QLabel(icon)
        icon_label.setStyleSheet(f"font-size: 24px; color: #{color};")
        
        title_label = QLabel(title)
        title_label.setStyleSheet(f"""
            QLabel {{
                color: #{color};
                font-size: 12pt;
                font-weight: bold;
            }}
        """)
        
        header_layout.addWidget(icon_label)
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        
        layout.addLayout(header_layout)
        
        # مقدار
        value_label = QLabel(value)
        value_label.setStyleSheet("""
            QLabel {
                color: #ffffff;
                font-size: 14pt;
                font-weight: bold;
                padding: 10px 0;
            }
        """)
        value_label.setAlignment(Qt.AlignCenter)
        
        layout.addWidget(value_label)
        
        # ذخیره reference برای به‌روزرسانی
        setattr(card, 'value_label', value_label)
        setattr(card, 'title', title)
        
        card.setLayout(layout)
        return card


    def setup_ui(self):
        """تنظیم رابط کاربری پایه"""
        print(f"🎯 setup_ui فراخوانی شد برای: {self.__class__.__name__}")
        pass
    
    def apply_black_theme(self):
        """اعمال تم مشکی کامل"""
        # استایل اصلی
        self.setStyleSheet("""
            QWidget {
                background-color: #000000;
                color: #ffffff;
                font-family: 'B Nazanin', 'Segoe UI', Tahoma;
                font-size: 10pt;
                selection-background-color: #1e90ff;
                selection-color: white;
            }
            
            /* لیبل‌ها */
            QLabel {
                color: #ffffff;
                font-size: 10pt;
            }
            
            /* فیلدهای ورودی */
            QLineEdit, QTextEdit, QComboBox, QSpinBox, QDoubleSpinBox {
                background-color: #1a1a1a;
                border: 2px solid #333333;
                border-radius: 6px;
                padding: 8px;
                color: #ffffff;
                min-height: 25px;
            }
            
            QLineEdit:focus, QTextEdit:focus, QComboBox:focus, 
            QSpinBox:focus, QDoubleSpinBox:focus {
                border: 2px solid #1e90ff;
                background-color: #262626;
            }
            
            QLineEdit:hover, QTextEdit:hover, QComboBox:hover, 
            QSpinBox:hover, QDoubleSpinBox:hover {
                border: 2px solid #555555;
            }
            
            QComboBox::drop-down {
                border: none;
                width: 30px;
            }
            
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid #ffffff;
            }
            
            QComboBox QAbstractItemView {
                background-color: #1a1a1a;
                color: #ffffff;
                border: 2px solid #333333;
                selection-background-color: #1e90ff;
            }
            
            /* دکمه‌ها */
            QPushButton {
                background-color: #0066cc;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 20px;
                font-weight: bold;
                font-size: 10pt;
                min-height: 35px;
            }
            
            QPushButton:hover {
                background-color: #0077dd;
                border: 1px solid #1e90ff;
            }
            
            QPushButton:pressed {
                background-color: #0055aa;
            }
            
            QPushButton:disabled {
                background-color: #555555;
                color: #aaaaaa;
            }
            
            /* دکمه‌های عملیات خاص */
            QPushButton[style*="primary"] {
                background-color: #27ae60;
            }
            
            QPushButton[style*="warning"] {
                background-color: #f39c12;
            }
            
            QPushButton[style*="danger"] {
                background-color: #e74c3c;
            }
            
            QPushButton[style*="info"] {
                background-color: #3498db;
            }
            
            /* جدول‌ها */
            QTableWidget {
                background-color: #111111;
                alternate-background-color: #0a0a0a;
                gridline-color: #333333;
                border: 2px solid #333333;
                border-radius: 6px;
                selection-background-color: #1e90ff;
                selection-color: white;
            }
            
            QTableWidget::item {
                padding: 8px;
                border-bottom: 1px solid #222222;
            }
            
            QTableWidget::item:selected {
                background-color: #1e90ff;
                color: white;
            }
            
            QHeaderView::section {
                background-color: #0066cc;
                color: white;
                padding: 12px;
                border: none;
                font-weight: bold;
                font-size: 10pt;
            }
            
            QHeaderView::section:hover {
                background-color: #0077dd;
            }
            
            /* GroupBox */
            QGroupBox {
                border: 2px solid #333333;
                border-radius: 8px;
                margin-top: 15px;
                padding-top: 15px;
                font-weight: bold;
                font-size: 11pt;
                color: #1e90ff;
                background-color: rgba(30, 30, 30, 0.5);
            }
            
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top center;
                padding: 0 15px;
                color: #1e90ff;
            }
            
            /* TabWidget */
            QTabWidget::pane {
                border: 2px solid #333333;
                background-color: #111111;
                border-radius: 8px;
                margin-top: 5px;
            }
            
            QTabBar::tab {
                background-color: #333333;
                color: #cccccc;
                padding: 12px 25px;
                margin-right: 3px;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                font-size: 10pt;
                min-width: 150px;
            }
            
            QTabBar::tab:selected {
                background-color: #0066cc;
                color: white;
                font-weight: bold;
            }
            
            QTabBar::tab:hover {
                background-color: #555555;
            }
            
            /* ScrollArea */
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            
            QScrollBar:vertical {
                border: none;
                background-color: #1a1a1a;
                width: 12px;
                margin: 0;
            }
            
            QScrollBar::handle:vertical {
                background-color: #555555;
                border-radius: 6px;
                min-height: 30px;
            }
            
            QScrollBar::handle:vertical:hover {
                background-color: #777777;
            }
            
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                border: none;
                background: none;
                height: 0;
            }
            
            /* DateEdit */
            QDateEdit::drop-down {
                border: none;
                width: 30px;
            }
            
            QDateEdit::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid #ffffff;
            }
            
            /* TextEdit */
            QTextEdit {
                background-color: #1a1a1a;
                border: 2px solid #333333;
                border-radius: 6px;
                color: #ffffff;
                padding: 8px;
            }
            
            /* Separator */
            QFrame[frameShape="4"] {
                background-color: #333333;
                min-height: 2px;
                max-height: 2px;
            }
        """)
        
        # تنظیم پالت
        palette = self.palette()
        palette.setColor(QPalette.Window, QColor("#000000"))
        palette.setColor(QPalette.WindowText, QColor("#ffffff"))
        palette.setColor(QPalette.Base, QColor("#1a1a1a"))
        palette.setColor(QPalette.AlternateBase, QColor("#111111"))
        palette.setColor(QPalette.Text, QColor("#ffffff"))
        palette.setColor(QPalette.Button, QColor("#0066cc"))
        palette.setColor(QPalette.ButtonText, QColor("#ffffff"))
        palette.setColor(QPalette.Highlight, QColor("#1e90ff"))
        palette.setColor(QPalette.HighlightedText, QColor("#ffffff"))
        palette.setColor(QPalette.PlaceholderText, QColor("#777777"))
        self.setPalette(palette)
    
    def create_collapsible_summary(self, title="خلاصه انبار"):
        """ایجاد یک پنل خلاصه انبار کشویی"""
        # ایجاد گروه با دکمه باز/بسته
        group = QGroupBox(title)
        group.setCheckable(True)  # این امکان را می‌دهد که groupbox قابل انتخاب باشد
        group.setChecked(False)  # به صورت پیش‌فرض بسته است
        
        # استایل مخصوص برای groupbox کشویی
        group.setStyleSheet("""
            QGroupBox::indicator {
                width: 15px;
                height: 15px;
            }
            QGroupBox::indicator:checked {
                image: url(:/icons/down_arrow.png);
            }
            QGroupBox::indicator:unchecked {
                image: url(:/icons/right_arrow.png);
            }
        """)
        
        # Layout برای محتوا
        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(15, 25, 15, 15)  # حاشیه بیشتر برای عنوان
        
        # ایجاد شبکه برای نمایش آمار
        grid = QGridLayout()
        grid.setHorizontalSpacing(20)
        grid.setVerticalSpacing(10)
        
        # اضافه کردن به layout اصلی
        content_layout.addLayout(grid)
        group.setLayout(content_layout)
        
        # ذخیره reference برای به‌روزرسانی
        setattr(group, 'grid_layout', grid)
        setattr(group, 'stats_items', {})
        
        # مخفی کردن محتوا هنگام بسته شدن
        def toggle_content(checked):
            for i in range(1, content_layout.count()):
                item = content_layout.itemAt(i)
                if item:
                    widget = item.widget()
                    if widget:
                        widget.setVisible(checked)
                    elif item.layout():
                        for j in range(item.layout().count()):
                            sub_widget = item.layout().itemAt(j).widget()
                            if sub_widget:
                                sub_widget.setVisible(checked)
        
        group.toggled.connect(toggle_content)
        
        # در ابتدا محتوا را مخفی می‌کنیم
        for i in range(1, content_layout.count()):
            item = content_layout.itemAt(i)
            if item:
                widget = item.widget()
                if widget:
                    widget.setVisible(False)
        
        return group

    def update_summary_stats(self, summary_group, stats_data):
        """به‌روزرسانی آمار در پنل خلاصه"""
        if not hasattr(summary_group, 'grid_layout'):
            return
        
        grid = summary_group.grid_layout
        
        # پاک کردن آمار قبلی
        for i in reversed(range(grid.count())):
            widget = grid.itemAt(i).widget()
            if widget:
                widget.deleteLater()
        
        if not hasattr(summary_group, 'stats_items'):
            summary_group.stats_items = {}
        
        # ایجاد آمار جدید
        row = 0
        col = 0
        max_columns = 3  # حداکثر 3 ستون
        
        for stat_name, stat_value in stats_data.items():
            # ایجاد کارت آمار
            stat_card = self.create_summary_card(stat_name, stat_value)
            
            # اضافه کردن به شبکه
            grid.addWidget(stat_card, row, col)
            
            # حرکت به ستون بعدی
            col += 1
            if col >= max_columns:
                col = 0
                row += 1
        
        # اضافه کردن stretch به ردیف آخر
        grid.setRowStretch(row + 1, 1)

    def create_summary_card(self, title, value):
        """ایجاد کارت کوچک برای نمایش آمار"""
        card = QFrame()
        card.setFrameShape(QFrame.StyledPanel)
        card.setMinimumHeight(80)
        card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        
        card.setStyleSheet("""
            QFrame {
                background-color: #1a1a1a;
                border: 2px solid #333333;
                border-radius: 8px;
                padding: 10px;
            }
            QFrame:hover {
                border: 2px solid #1e90ff;
                background-color: #222222;
            }
        """)
        
        layout = QVBoxLayout()
        layout.setSpacing(5)
        
        # عنوان
        title_label = QLabel(title)
        title_label.setStyleSheet("""
            QLabel {
                color: #cccccc;
                font-size: 9pt;
                font-weight: bold;
            }
        """)
        title_label.setAlignment(Qt.AlignCenter)
        
        # مقدار
        value_label = QLabel(value)
        value_label.setStyleSheet("""
            QLabel {
                color: #ffffff;
                font-size: 12pt;
                font-weight: bold;
            }
        """)
        value_label.setAlignment(Qt.AlignCenter)
        
        layout.addWidget(title_label)
        layout.addWidget(value_label)
        
        card.setLayout(layout)
        
        return card

    def set_rtl_layout(self):
        """تنظیم چیدمان راست‌چین"""
        self.setLayoutDirection(Qt.RightToLeft)
        
        # تنظیم فونت فارسی
        font = QFont("B Nazanin", 10)
        font.setBold(False)
        self.setFont(font)
    
    def create_form_group(self, title="اطلاعات"):
        """ایجاد گروه فرم"""
        group = QGroupBox(title)
        form_layout = QFormLayout()
        form_layout.setLabelAlignment(Qt.AlignRight)
        form_layout.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)
        form_layout.setVerticalSpacing(12)
        form_layout.setHorizontalSpacing(20)
        group.setLayout(form_layout)
        return group, form_layout
    
    def create_table(self, headers, row_count=0):
        """ایجاد جدول با هدرهای داده شده"""
        table = QTableWidget(row_count, len(headers))
        table.setHorizontalHeaderLabels(headers)
        
        # تنظیمات جدول
        table.setAlternatingRowColors(True)
        table.setSelectionBehavior(QTableWidget.SelectRows)
        table.setSelectionMode(QTableWidget.SingleSelection)
        table.setEditTriggers(QTableWidget.NoEditTriggers)
        
        # تنظیم هدر
        header = table.horizontalHeader()
        header.setStretchLastSection(True)
        header.setDefaultAlignment(Qt.AlignRight | Qt.AlignVCenter)
        
        # تنظیم حداقل ارتفاع ردیف
        table.verticalHeader().setDefaultSectionSize(40)
        
        return table
    
    def format_currency(self, value):
        """قالب‌بندی ارز به صورت تومان"""
        try:
            value = float(value)
            if value == 0:
                return "۰ تومان"
            
            formatted = f"{value:,.0f}".replace(',', '،')
            return f"{formatted} تومان"
        except:
            return "۰ تومان"
    
    def to_rial(self, toman_value):
        """تبدیل تومان به ریال"""
        try:
            return float(toman_value) * 10
        except:
            return 0
    
    def to_toman(self, rial_value):
        """تبدیل ریال به تومان"""
        try:
            return float(rial_value) / 10
        except:
            return 0
    
    def format_date(self, date_str):
        """قالب‌بندی تاریخ شمسی"""
        if not date_str:
            return ""
        
        try:
            # اگر تاریخ میلادی است، به شمسی تبدیل کن
            if '-' in date_str and len(date_str.split('-')) == 3:
                year, month, day = map(int, date_str.split('-'))
                jalali_date = jdatetime.date.fromgregorian(year=year, month=month, day=day)
                return jalali_date.strftime("%Y/%m/%d")
            
            # اگر تاریخ شمسی است
            if '/' in date_str:
                parts = date_str.replace('-', '/').split('/')
                if len(parts) == 3:
                    year, month, day = map(int, parts)
                    jalali_date = jdatetime.date(year, month, day)
                    return jalali_date.strftime("%Y/%m/%d")
                    
        except Exception as e:
            print(f"خطا در تبدیل تاریخ: {e}")
        
        return date_str
    
    def setup_live_search(self, search_widget, callback, delay=300):
        """تنظیم جستجوی زنده برای ویجت"""
        self.search_timer = QTimer()
        self.search_timer.setSingleShot(True)
        
        def on_text_changed():
            self.search_timer.stop()
            self.search_timer.start(delay)
        
        def on_timeout():
            callback()
        
        if isinstance(search_widget, QLineEdit):
            search_widget.textChanged.connect(on_text_changed)
        elif isinstance(search_widget, QComboBox):
            search_widget.currentTextChanged.connect(on_text_changed)
        
        self.search_timer.timeout.connect(on_timeout)
    
    def show_message(self, title, message, icon=QMessageBox.Information):
        """نمایش پیام"""
        msg = QMessageBox(self)
        msg.setWindowTitle(title)
        msg.setText(message)
        msg.setIcon(icon)
        
        # اعمال استایل مشکی روی MessageBox
        msg.setStyleSheet("""
            QMessageBox {
                background-color: #000000;
                color: #ffffff;
            }
            QLabel {
                color: #ffffff;
                min-width: 400px;
                min-height: 100px;
            }
            QPushButton {
                background-color: #0066cc;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #0077dd;
            }
        """)
        
        return msg.exec()
    
    def show_error(self, message):
        """نمایش خطا"""
        return self.show_message("خطا", message, QMessageBox.Critical)
    
    def show_success(self, message):
        """نمایش موفقیت"""
        return self.show_message("موفقیت", message, QMessageBox.Information)
    
    def show_warning(self, message):
        """نمایش هشدار"""
        return self.show_message("هشدار", message, QMessageBox.Warning)
    
    def confirm_action(self, title, message):
        """درخواست تایید از کاربر"""
        reply = QMessageBox.question(
            self, title, message,
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        return reply == QMessageBox.Yes
    
    def clear_form(self):
        """پاک کردن فرم"""
        pass
    
    def load_data(self):
        """بارگذاری داده‌ها"""
        pass
    
    def save_data(self):
        """ذخیره داده‌ها"""
        pass