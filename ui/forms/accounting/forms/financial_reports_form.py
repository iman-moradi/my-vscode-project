# ui/forms/accounting/forms/financial_reports_form.py
"""
فرم گزارش‌های مالی - کامل و یکپارچه
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QComboBox, QFrame, QTableWidget, QTableWidgetItem, QHeaderView,
    QTabWidget, QTextEdit, QMessageBox, QDateEdit, QGroupBox,
    QFormLayout, QSpinBox, QCheckBox, QSplitter, QProgressBar,
    QFileDialog, QTreeWidget, QTreeWidgetItem, QStyledItemDelegate,
    QStyleOptionViewItem, QApplication
)
from PySide6.QtCore import Qt, Signal, QTimer, QDate, QDateTime
from PySide6.QtGui import QFont, QColor, QBrush, QIcon
import jdatetime
from datetime import datetime, timedelta
import json
import os
import traceback

try:
    from modules.accounting.report_generator import ReportGenerator
    REPORT_GENERATOR_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ خطا در بارگذاری ReportGenerator: {e}")
    REPORT_GENERATOR_AVAILABLE = False


try:
    from utils.jalali_date_widget import JalaliDateInput
    JALALI_DATE_INPUT_AVAILABLE = True
except ImportError:
    print("⚠️ ویجت تاریخ شمسی در دسترس نیست")
    JALALI_DATE_INPUT_AVAILABLE = False


class FinancialReportsForm(QWidget):
    """فرم گزارش‌های مالی کامل"""
    
    data_changed = Signal()
    
    def __init__(self, data_manager):
        super().__init__()
        self.data_manager = data_manager
        
        # فقط در صورت موجود بودن ReportGenerator آن را ایجاد کن
        if REPORT_GENERATOR_AVAILABLE:
            self.report_generator = ReportGenerator(data_manager)
        else:
            self.report_generator = None
            
        self.current_report = None
        
        # راست‌چین کردن کامل
        self.setLayoutDirection(Qt.RightToLeft)
        
        # تنظیم استایل
        self.setup_styles()
        
        # ایجاد رابط کاربری
        self.init_ui()
        
        # بارگذاری داده‌های اولیه
        self.load_initial_data()
        
        print("✅ فرم گزارش‌های مالی ایجاد شد")
    
    def setup_styles(self):
        """تنظیم استایل فرم"""
        self.setStyleSheet("""
            /* استایل کلی فرم */
            QWidget {
                background-color: #111111;
                color: #ffffff;
                font-family: 'B Nazanin';
            }
            
            /* گروه‌بندی */
            QGroupBox {
                font-size: 12pt;
                font-weight: bold;
                border: 2px solid #3498db;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
                color: #3498db;
            }
            
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top center;
                padding: 0 10px;
                background-color: #111111;
            }
            
            /* دکمه‌ها */
            QPushButton {
                background-color: #2c3e50;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 10px 15px;
                font-size: 11pt;
                font-weight: bold;
            }
            
            QPushButton:hover {
                background-color: #34495e;
            }
            
            QPushButton:pressed {
                background-color: #2980b9;
            }
            
            QPushButton[style_type="primary"] {
                background-color: #27ae60;
            }
            
            QPushButton[style_type="primary"]:hover {
                background-color: #219653;
            }
            
            QPushButton[style_type="danger"] {
                background-color: #e74c3c;
            }
            
            QPushButton[style_type="danger"]:hover {
                background-color: #c0392b;
            }
            
            QPushButton[style_type="info"] {
                background-color: #3498db;
            }
            
            QPushButton[style_type="info"]:hover {
                background-color: #2980b9;
            }
            
            /* کامبوباکس */
            QComboBox {
                background-color: #222222;
                color: white;
                border: 2px solid #333333;
                border-radius: 5px;
                padding: 8px;
                font-size: 11pt;
                min-height: 40px;
            }
            
            QComboBox:hover {
                border-color: #3498db;
            }
            
            QComboBox::drop-down {
                border: none;
            }
            
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid white;
                margin-right: 10px;
            }
            
            QComboBox QAbstractItemView {
                background-color: #222222;
                color: white;
                selection-background-color: #3498db;
                border: 1px solid #333;
            }
            
            /* جداول */
            QTableWidget {
                background-color: #111111;
                alternate-background-color: #0a0a0a;
                selection-background-color: #3498db;
                selection-color: white;
                gridline-color: #333;
                border: 1px solid #333;
                font-size: 11pt;
            }
            
            QTableWidget::item {
                padding: 8px;
                color: white;
                border-bottom: 1px solid #333;
            }
            
            QHeaderView::section {
                background-color: #2c3e50;
                color: white;
                padding: 12px;
                border: none;
                font-weight: bold;
                font-size: 11pt;
                text-align: center;
            }
            
            /* تب‌ها */
            QTabWidget::pane {
                border: 1px solid #333;
                background-color: #111111;
            }
            
            QTabBar::tab {
                background-color: #2c2c2c;
                color: #bbb;
                padding: 10px 20px;
                margin-left: 2px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                font-size: 11pt;
            }
            
            QTabBar::tab:selected {
                background-color: #3498db;
                color: white;
                font-weight: bold;
            }
            
            QTabBar::tab:hover:!selected {
                background-color: #3c3c3c;
            }
            
            /* تکست‌ادی */
            QTextEdit {
                background-color: #222222;
                color: white;
                border: 1px solid #333;
                border-radius: 5px;
                padding: 10px;
                font-family: 'Courier New';
                font-size: 10pt;
            }
            
            /* تریدی ویجت */
            QTreeWidget {
                background-color: #111111;
                color: white;
                border: 1px solid #333;
                alternate-background-color: #0a0a0a;
            }
            
            QTreeWidget::item {
                padding: 8px;
                border-bottom: 1px solid #333;
            }
            
            QTreeWidget::item:selected {
                background-color: #3498db;
                color: white;
            }
            
            /* پروگرسبار */
            QProgressBar {
                border: 1px solid #333;
                border-radius: 5px;
                text-align: center;
                color: white;
                font-weight: bold;
            }
            
            QProgressBar::chunk {
                background-color: #27ae60;
                border-radius: 5px;
            }
        """)
    
    def init_ui(self):
        """ایجاد رابط کاربری"""
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(15, 15, 15, 15)
        
        # ==================== بخش 1: هدر و کنترل‌ها ====================
        header_frame = QFrame()
        header_layout = QVBoxLayout(header_frame)
        
        # عنوان
        title_label = QLabel("📊 سیستم گزارش‌گیری مالی پیشرفته")
        title_label.setStyleSheet("""
            QLabel {
                font-size: 18pt;
                font-weight: bold;
                color: #3498db;
                padding: 10px;
                border-bottom: 2px solid #3498db;
            }
        """)
        header_layout.addWidget(title_label)
        
        # کنترل‌های گزارش‌گیری
        controls_group = QGroupBox("🎯 تنظیمات گزارش")
        controls_layout = QVBoxLayout()
        
        # ردیف 1: انتخاب نوع گزارش
        type_layout = QHBoxLayout()
        type_layout.addWidget(QLabel("نوع گزارش:"))
        
        self.report_type_combo = QComboBox()
        self.report_type_combo.addItems([
            "📅 گزارش روزانه",
            "📈 گزارش ماهانه", 
            "💰 صورت سود و زیان",
            "💵 صورت جریان وجوه نقد",
            "🏦 ترازنامه",
            "🤝 گزارش سود شرکا",
            "📊 گزارش ROI شرکا"
        ])
        self.report_type_combo.currentIndexChanged.connect(self.on_report_type_changed)
        type_layout.addWidget(self.report_type_combo)
        
        type_layout.addStretch()
        controls_layout.addLayout(type_layout)
        
        # ردیف 2: پارامترهای تاریخ
        self.date_params_widget = QWidget()
        self.date_params_layout = QHBoxLayout(self.date_params_widget)
        
        # ویجت‌های تاریخ شمسی
        if JALALI_DATE_INPUT_AVAILABLE:
            self.start_date_input = JalaliDateInput(mode='edit', theme='dark')
            self.end_date_input = JalaliDateInput(mode='edit', theme='dark')
        else:
            # جایگزین ساده
            self.start_date_input = QDateEdit()
            self.end_date_input = QDateEdit()
            self.start_date_input.setCalendarPopup(True)
            self.end_date_input.setCalendarPopup(True)
        
        self.date_params_layout.addWidget(QLabel("تاریخ شروع:"))
        self.date_params_layout.addWidget(self.start_date_input)
        self.date_params_layout.addWidget(QLabel("تاریخ پایان:"))
        self.date_params_layout.addWidget(self.end_date_input)
        
        # دکمه تاریخ‌های پیش‌فرض
        date_buttons_layout = QHBoxLayout()
        
        btn_today = QPushButton("امروز")
        btn_today.setProperty("style_type", "info")
        btn_today.clicked.connect(self.set_today_dates)
        
        btn_yesterday = QPushButton("دیروز")
        btn_yesterday.setProperty("style_type", "info")
        btn_yesterday.clicked.connect(self.set_yesterday_dates)
        
        btn_this_month = QPushButton("این ماه")
        btn_this_month.setProperty("style_type", "info")
        btn_this_month.clicked.connect(self.set_this_month_dates)
        
        btn_last_month = QPushButton("ماه قبل")
        btn_last_month.setProperty("style_type", "info")
        btn_last_month.clicked.connect(self.set_last_month_dates)
        
        date_buttons_layout.addWidget(btn_today)
        date_buttons_layout.addWidget(btn_yesterday)
        date_buttons_layout.addWidget(btn_this_month)
        date_buttons_layout.addWidget(btn_last_month)
        
        self.date_params_layout.addLayout(date_buttons_layout)
        controls_layout.addWidget(self.date_params_widget)
        
        # ردیف 3: پارامترهای خاص گزارش
        self.specific_params_widget = QWidget()
        self.specific_params_layout = QHBoxLayout(self.specific_params_widget)
        
        # برای گزارش ROI شرکا
        self.partner_label = QLabel("شریک:")
        self.partner_combo = QComboBox()
        self.partner_combo.addItem("همه شرکا", None)
        
        self.specific_params_layout.addWidget(self.partner_label)
        self.specific_params_layout.addWidget(self.partner_combo)
        self.specific_params_layout.addStretch()
        
        controls_layout.addWidget(self.specific_params_widget)
        
        # ردیف 4: دکمه‌های عملیات
        action_layout = QHBoxLayout()
        
        self.btn_generate = QPushButton("🔄 تولید گزارش")
        self.btn_generate.setProperty("style_type", "primary")
        self.btn_generate.clicked.connect(self.generate_report)
        self.btn_generate.setMinimumHeight(45)
        
        self.btn_export_json = QPushButton("💾 ذخیره JSON")
        self.btn_export_json.setProperty("style_type", "info")
        self.btn_export_json.clicked.connect(self.export_json)
        self.btn_export_json.setEnabled(False)
        
        self.btn_export_pdf = QPushButton("📄 ذخیره PDF")
        self.btn_export_pdf.setProperty("style_type", "info")
        self.btn_export_pdf.clicked.connect(self.export_pdf)
        self.btn_export_pdf.setEnabled(False)
        
        self.btn_refresh = QPushButton("🔄 بروزرسانی")
        self.btn_refresh.setProperty("style_type", "info")
        self.btn_refresh.clicked.connect(self.refresh_form_data)
        
        self.btn_clear = QPushButton("🗑️ پاک کردن")
        self.btn_clear.setProperty("style_type", "danger")
        self.btn_clear.clicked.connect(self.clear_report)
        
        action_layout.addWidget(self.btn_generate)
        action_layout.addWidget(self.btn_export_json)
        action_layout.addWidget(self.btn_export_pdf)
        action_layout.addWidget(self.btn_refresh)
        action_layout.addWidget(self.btn_clear)
        
        controls_layout.addLayout(action_layout)
        
        # پروگرسبار
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        controls_layout.addWidget(self.progress_bar)
        
        controls_group.setLayout(controls_layout)
        header_layout.addWidget(controls_group)
        
        main_layout.addWidget(header_frame)
        
        # ==================== بخش 2: نمایش گزارش ====================
        display_splitter = QSplitter(Qt.Vertical)
        
        # تب‌های مختلف نمایش
        self.display_tabs = QTabWidget()
        
        # تب 1: نمایش جدولی
        self.table_tab = QWidget()
        table_layout = QVBoxLayout(self.table_tab)
        
        self.result_table = QTableWidget()
        self.result_table.setColumnCount(0)
        self.result_table.horizontalHeader().setStretchLastSection(True)
        self.result_table.setAlternatingRowColors(True)
        self.result_table.setSortingEnabled(True)
        
        table_layout.addWidget(self.result_table)
        self.display_tabs.addTab(self.table_tab, "📊 نمایش جدولی")
        
        # تب 2: نمایش درختی (برای گزارش‌های سلسله‌مراتبی)
        self.tree_tab = QWidget()
        tree_layout = QVBoxLayout(self.tree_tab)
        
        self.result_tree = QTreeWidget()
        self.result_tree.setHeaderLabels(['شرح', 'مقدار', 'واحد'])
        tree_layout.addWidget(self.result_tree)
        self.display_tabs.addTab(self.tree_tab, "🌳 نمایش درختی")
        
        # تب 3: نمایش JSON
        self.json_tab = QWidget()
        json_layout = QVBoxLayout(self.json_tab)
        
        self.json_view = QTextEdit()
        self.json_view.setReadOnly(True)
        json_layout.addWidget(self.json_view)
        self.display_tabs.addTab(self.json_tab, "📝 نمایش JSON")
        
        # تب 4: تحلیل و نمودار
        self.analysis_tab = QWidget()
        analysis_layout = QVBoxLayout(self.analysis_tab)
        
        self.analysis_view = QTextEdit()
        self.analysis_view.setReadOnly(True)
        self.analysis_view.setStyleSheet("""
            QTextEdit {
                font-family: 'B Nazanin';
                font-size: 11pt;
                line-height: 1.5;
            }
        """)
        
        analysis_layout.addWidget(QLabel("📈 تحلیل گزارش:"))
        analysis_layout.addWidget(self.analysis_view)
        self.display_tabs.addTab(self.analysis_tab, "📈 تحلیل و نمودار")
        
        display_splitter.addWidget(self.display_tabs)
        
        # تب 5: خلاصه گزارش
        self.summary_widget = QWidget()
        summary_layout = QVBoxLayout(self.summary_widget)
        
        self.summary_text = QTextEdit()
        self.summary_text.setMaximumHeight(150)
        self.summary_text.setReadOnly(True)
        self.summary_text.setStyleSheet("""
            QTextEdit {
                background-color: #1a252f;
                border: 2px solid #3498db;
                border-radius: 8px;
                font-size: 11pt;
                font-weight: bold;
                color: #ffffff;
            }
        """)
        
        summary_layout.addWidget(QLabel("📋 خلاصه گزارش:"))
        summary_layout.addWidget(self.summary_text)
        
        display_splitter.addWidget(self.summary_widget)
        display_splitter.setSizes([500, 150])
        
        main_layout.addWidget(display_splitter, 1)
        
        # ==================== بخش 3: وضعیت سیستم ====================
        status_frame = QFrame()
        status_layout = QHBoxLayout(status_frame)
        
        self.status_label = QLabel("✅ آماده برای تولید گزارش")
        self.status_label.setStyleSheet("""
            QLabel {
                color: #27ae60;
                font-size: 10pt;
                padding: 5px;
                border: 1px solid #27ae60;
                border-radius: 5px;
                background-color: rgba(39, 174, 96, 0.1);
            }
        """)
        
        self.report_info_label = QLabel("")
        self.report_info_label.setStyleSheet("color: #bbb; font-size: 9pt;")
        
        status_layout.addWidget(self.status_label)
        status_layout.addStretch()
        status_layout.addWidget(self.report_info_label)
        
        main_layout.addWidget(status_frame)
        
        # مخفی کردن ویجت‌های غیرضروری
        self.hide_unnecessary_widgets()
    
    def load_initial_data(self):
        """بارگذاری داده‌های اولیه"""
        try:
            # تنظیم تاریخ‌های پیش‌فرض
            self.set_today_dates()
            
            # بارگذاری لیست شرکا
            self.load_partners()
            
            # مخفی کردن ویجت‌های غیرفعال
            self.on_report_type_changed(0)
            
            print("✅ داده‌های اولیه بارگذاری شد")
            
        except Exception as e:
            print(f"⚠️ خطا در بارگذاری داده‌های اولیه: {e}")
    
    def load_partners(self):
        """بارگذاری لیست شرکا"""
        try:
            query = """
            SELECT 
                p.id,
                per.first_name || ' ' || per.last_name as name
            FROM Partners p
            JOIN Persons per ON p.person_id = per.id
            WHERE p.active = 1
            ORDER BY per.last_name
            """
            
            partners = self.data_manager.db.fetch_all(query)
            
            for partner in partners:
                self.partner_combo.addItem(partner['name'], partner['id'])
                
        except Exception as e:
            print(f"⚠️ خطا در بارگذاری شرکا: {e}")
    
    def hide_unnecessary_widgets(self):
        """مخفی کردن ویجت‌های غیرضروری"""
        self.specific_params_widget.hide()
    
    def on_report_type_changed(self, index):
        """هنگام تغییر نوع گزارش"""
        report_type = self.report_type_combo.currentText()
        
        # نمایش/مخفی کردن ویجت‌های مربوطه
        if "ROI" in report_type or "سود شرکا" in report_type:
            self.specific_params_widget.show()
        else:
            self.specific_params_widget.hide()
        
        # تنظیم برچسب‌های تاریخ
        if "روزانه" in report_type:
            if JALALI_DATE_INPUT_AVAILABLE:
                today = self.data_manager.db.get_current_jalali_date()
                self.start_date_input.set_date_string(today)
                self.end_date_input.set_date_string(today)
        elif "ماهانه" in report_type:
            self.set_this_month_dates()
        elif "ترازنامه" in report_type:
            if JALALI_DATE_INPUT_AVAILABLE:
                today = self.data_manager.db.get_current_jalali_date()
                self.start_date_input.set_date_string(today)
                self.end_date_input.set_date_string(today)
        
        self.status_label.setText(f"📊 گزارش {report_type} انتخاب شد")
    
    # ==================== متدهای تنظیم تاریخ ====================
    
    def set_today_dates(self):
        """تنظیم تاریخ امروز"""
        try:
            today = self.data_manager.db.get_current_jalali_date()
            if JALALI_DATE_INPUT_AVAILABLE:
                self.start_date_input.set_date_string(today)
                self.end_date_input.set_date_string(today)
            else:
                # برای QDateEdit
                gregorian_date = self.data_manager.db.jalali_to_gregorian(today)
                qdate = QDate.fromString(gregorian_date, "yyyy-MM-dd")
                self.start_date_input.setDate(qdate)
                self.end_date_input.setDate(qdate)
        except Exception as e:
            print(f"⚠️ خطا در تنظیم تاریخ امروز: {e}")
            # استفاده از تاریخ جاری
            if JALALI_DATE_INPUT_AVAILABLE:
                self.start_date_input.set_date_string(jdatetime.datetime.now().strftime("%Y/%m/%d"))
                self.end_date_input.set_date_string(jdatetime.datetime.now().strftime("%Y/%m/%d"))
    
    def set_yesterday_dates(self):
        """تنظیم تاریخ دیروز"""
        try:
            today = jdatetime.datetime.now()
            yesterday = today - timedelta(days=1)
            date_str = yesterday.strftime("%Y/%m/%d")
            
            if JALALI_DATE_INPUT_AVAILABLE:
                self.start_date_input.set_date_string(date_str)
                self.end_date_input.set_date_string(date_str)
            else:
                gregorian_date = self.data_manager.db.jalali_to_gregorian(date_str)
                qdate = QDate.fromString(gregorian_date, "yyyy-MM-dd")
                self.start_date_input.setDate(qdate)
                self.end_date_input.setDate(qdate)
        except Exception as e:
            print(f"⚠️ خطا در تنظیم تاریخ دیروز: {e}")
    
    def set_this_month_dates(self):
        """تنظیم تاریخ‌های این ماه"""
        try:
            today = jdatetime.datetime.now()
            first_day = jdatetime.date(today.year, today.month, 1)
            last_day = jdatetime.date(today.year, today.month, today.day)
            
            start_str = first_day.strftime("%Y/%m/%d")
            end_str = last_day.strftime("%Y/%m/%d")
            
            if JALALI_DATE_INPUT_AVAILABLE:
                self.start_date_input.set_date_string(start_str)
                self.end_date_input.set_date_string(end_str)
            else:
                start_gregorian = self.data_manager.db.jalali_to_gregorian(start_str)
                end_gregorian = self.data_manager.db.jalali_to_gregorian(end_str)
                
                start_qdate = QDate.fromString(start_gregorian, "yyyy-MM-dd")
                end_qdate = QDate.fromString(end_gregorian, "yyyy-MM-dd")
                
                self.start_date_input.setDate(start_qdate)
                self.end_date_input.setDate(end_qdate)
        except Exception as e:
            print(f"⚠️ خطا در تنظیم تاریخ این ماه: {e}")
    
    def set_last_month_dates(self):
        """تنظیم تاریخ‌های ماه قبل"""
        try:
            today = jdatetime.datetime.now()
            if today.month == 1:
                last_month = jdatetime.date(today.year - 1, 12, 1)
            else:
                last_month = jdatetime.date(today.year, today.month - 1, 1)
            
            last_day = jdatetime.date(last_month.year, last_month.month, 
                                     jdatetime.jalali.month_length(last_month.year, last_month.month))
            
            start_str = last_month.strftime("%Y/%m/%d")
            end_str = last_day.strftime("%Y/%m/%d")
            
            if JALALI_DATE_INPUT_AVAILABLE:
                self.start_date_input.set_date_string(start_str)
                self.end_date_input.set_date_string(end_str)
            else:
                start_gregorian = self.data_manager.db.jalali_to_gregorian(start_str)
                end_gregorian = self.data_manager.db.jalali_to_gregorian(end_str)
                
                start_qdate = QDate.fromString(start_gregorian, "yyyy-MM-dd")
                end_qdate = QDate.fromString(end_gregorian, "yyyy-MM-dd")
                
                self.start_date_input.setDate(start_qdate)
                self.end_date_input.setDate(end_qdate)
        except Exception as e:
            print(f"⚠️ خطا در تنظیم تاریخ ماه قبل: {e}")
    
    # ==================== متدهای اصلی ====================
    
    def generate_report(self):
        """تولید گزارش"""
        if not REPORT_GENERATOR_AVAILABLE or self.report_generator is None:
            QMessageBox.warning(self, "خطا", "ماژول تولید گزارش در دسترس نیست!")
            return
        
        try:
            # نمایش پروگرسبار
            self.progress_bar.setVisible(True)
            self.progress_bar.setValue(10)
            self.status_label.setText("🔄 در حال تولید گزارش...")
            QApplication.processEvents()
            
            # دریافت پارامترها
            report_type = self.report_type_combo.currentText()
            
            # دریافت تاریخ‌ها
            if JALALI_DATE_INPUT_AVAILABLE:
                start_date = self.start_date_input.get_date()
                end_date = self.end_date_input.get_date()
            else:
                # برای QDateEdit
                start_qdate = self.start_date_input.date()
                end_qdate = self.end_date_input.date()
                # تبدیل به رشته شمسی
                start_gregorian = start_qdate.toString("yyyy-MM-dd")
                end_gregorian = end_qdate.toString("yyyy-MM-dd")
                
                # تبدیل به شمسی
                start_date = self.data_manager.db.gregorian_to_jalali(start_gregorian)
                end_date = self.data_manager.db.gregorian_to_jalali(end_gregorian)
            
            if not start_date or not end_date:
                QMessageBox.warning(self, "خطا", "لطفاً تاریخ‌ها را وارد کنید!")
                return
            
            self.progress_bar.setValue(30)
            
            # تولید گزارش بر اساس نوع
            report_data = None
            
            if "روزانه" in report_type:
                report_data = self.report_generator.generate_daily_report(start_date)
                
            elif "ماهانه" in report_type:
                # استخراج سال و ماه از تاریخ
                parts = start_date.split('/')
                if len(parts) >= 2:
                    year = int(parts[0])
                    month = int(parts[1])
                    report_data = self.report_generator.generate_monthly_report(year, month)
                
            elif "سود و زیان" in report_type:
                report_data = self.report_generator.generate_profit_loss_statement(start_date, end_date)
                
            elif "جریان وجوه نقد" in report_type:
                report_data = self.report_generator.generate_cash_flow_statement(start_date, end_date)
                
            elif "ترازنامه" in report_type:
                report_data = self.report_generator.generate_balance_sheet(start_date)
                
            elif "سود شرکا" in report_type:
                report_data = self.report_generator.generate_partner_profit_report(start_date, end_date)
                
            elif "ROI" in report_type:
                partner_id = self.partner_combo.currentData()
                report_data = self.report_generator.generate_partner_roi_report(partner_id)
            
            self.progress_bar.setValue(70)
            
            if report_data and 'error' not in report_data:
                self.current_report = report_data
                self.display_report(report_data)
                self.update_summary(report_data)
                
                # فعال کردن دکمه‌های خروجی
                self.btn_export_json.setEnabled(True)
                self.btn_export_pdf.setEnabled(True)
                
                self.status_label.setText(f"✅ گزارش با موفقیت تولید شد")
                self.report_info_label.setText(
                    f"تاریخ تولید: {self.data_manager.db.get_current_jalali_datetime()}"
                )
            else:
                error_msg = report_data.get('error', 'خطا در تولید گزارش!') if report_data else 'خطا در تولید گزارش!'
                QMessageBox.warning(self, "خطا", error_msg)
                self.status_label.setText("❌ خطا در تولید گزارش")
            
            self.progress_bar.setValue(100)
            QTimer.singleShot(1000, lambda: self.progress_bar.setVisible(False))
            
        except Exception as e:
            self.progress_bar.setVisible(False)
            QMessageBox.critical(self, "خطا", f"خطا در تولید گزارش:\n{str(e)}")
            print(f"❌ خطا در تولید گزارش: {e}")
            traceback.print_exc()
            self.status_label.setText("❌ خطا در تولید گزارش")
    
    def display_report(self, report_data):
        """نمایش گزارش در فرمت‌های مختلف"""
        try:
            # 1. نمایش در جدول
            self.display_in_table(report_data)
            
            # 2. نمایش درختی
            self.display_in_tree(report_data)
            
            # 3. نمایش JSON
            self.display_as_json(report_data)
            
            # 4. تحلیل گزارش
            self.display_analysis(report_data)
            
        except Exception as e:
            print(f"⚠️ خطا در نمایش گزارش: {e}")
    
    def display_in_table(self, report_data):
        """نمایش گزارش در جدول"""
        try:
            self.result_table.clear()
            
            # شناسایی ساختار داده
            if isinstance(report_data, dict):
                # اگر داده‌های اصلی در کلیدهای خاصی باشند
                main_data = None
                
                # جستجوی کلیدهای حاوی داده‌های جدولی
                table_keys = ['transactions_summary', 'invoices_summary', 'checks_summary',
                            'monthly_financial_summary', 'monthly_invoices', 'monthly_checks',
                            'revenues', 'expenses', 'cash_flows', 'assets', 'liabilities', 'equity',
                            'profit_summary']
                
                for key in table_keys:
                    if key in report_data:
                        main_data = report_data[key]
                        break
                
                if main_data and isinstance(main_data, list) and len(main_data) > 0:
                    # تنظیم ستون‌ها
                    columns = list(main_data[0].keys())
                    self.result_table.setColumnCount(len(columns))
                    self.result_table.setHorizontalHeaderLabels(columns)
                    
                    # پر کردن داده‌ها
                    self.result_table.setRowCount(len(main_data))
                    
                    for row_idx, row_data in enumerate(main_data):
                        for col_idx, col_name in enumerate(columns):
                            value = row_data.get(col_name, '')
                            
                            # قالب‌بندی اعداد
                            if isinstance(value, (int, float)):
                                if 'amount' in col_name.lower() or 'price' in col_name.lower() or 'balance' in col_name.lower():
                                    value_str = f"{value:,.0f}"
                                elif 'percentage' in col_name.lower() or 'ratio' in col_name.lower():
                                    value_str = f"{value:.2f}%"
                                else:
                                    value_str = str(value)
                            else:
                                value_str = str(value)
                            
                            item = QTableWidgetItem(value_str)
                            item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                            
                            # رنگ‌بندی بر اساس مقادیر
                            if isinstance(value, (int, float)):
                                if value < 0:
                                    item.setForeground(QBrush(QColor("#e74c3c")))
                                elif value > 0:
                                    item.setForeground(QBrush(QColor("#27ae60")))
                            
                            self.result_table.setItem(row_idx, col_idx, item)
                    
                    # تنظیم اندازه ستون‌ها
                    self.result_table.resizeColumnsToContents()
                    
                else:
                    # نمایش داده‌های دیکشنری ساده
                    keys = list(report_data.keys())
                    values = list(report_data.values())
                    
                    self.result_table.setColumnCount(2)
                    self.result_table.setHorizontalHeaderLabels(['کلید', 'مقدار'])
                    self.result_table.setRowCount(len(keys))
                    
                    for i, (key, value) in enumerate(report_data.items()):
                        key_item = QTableWidgetItem(str(key))
                        value_item = QTableWidgetItem(str(value))
                        
                        key_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                        value_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                        
                        self.result_table.setItem(i, 0, key_item)
                        self.result_table.setItem(i, 1, value_item)
            
        except Exception as e:
            print(f"⚠️ خطا در نمایش جدولی: {e}")
            self.result_table.setRowCount(1)
            self.result_table.setColumnCount(1)
            self.result_table.setItem(0, 0, QTableWidgetItem(f"خطا: {str(e)}"))
    
    def display_in_tree(self, report_data):
        """نمایش گزارش در قالب درختی"""
        try:
            self.result_tree.clear()
            
            def add_to_tree(parent, data, level=0):
                if isinstance(data, dict):
                    for key, value in data.items():
                        if isinstance(value, (dict, list)):
                            child = QTreeWidgetItem(parent, [str(key), "", ""])
                            add_to_tree(child, value, level + 1)
                        else:
                            value_str = str(value)
                            if isinstance(value, (int, float)):
                                if 'amount' in key.lower() or 'price' in key.lower():
                                    value_str = f"{value:,.0f} ریال"
                                elif 'percentage' in key.lower():
                                    value_str = f"{value:.2f}%"
                            
                            QTreeWidgetItem(parent, [str(key), value_str, self.get_unit_for_key(key)])
                
                elif isinstance(data, list):
                    for i, item in enumerate(data):
                        child = QTreeWidgetItem(parent, [f"آیتم {i+1}", "", ""])
                        add_to_tree(child, item, level + 1)
            
            root = QTreeWidgetItem(self.result_tree, ['گزارش', '', ''])
            add_to_tree(root, report_data)
            
            self.result_tree.expandAll()
            
        except Exception as e:
            print(f"⚠️ خطا در نمایش درختی: {e}")
    
    def get_unit_for_key(self, key):
        """تعیین واحد برای کلید"""
        key_lower = key.lower()
        
        if any(term in key_lower for term in ['amount', 'price', 'cost', 'balance', 'total']):
            return 'ریال'
        elif any(term in key_lower for term in ['percentage', 'ratio', 'margin']):
            return '%'
        elif any(term in key_lower for term in ['count', 'number']):
            return 'عدد'
        elif 'date' in key_lower:
            return 'تاریخ'
        else:
            return ''
    
    def display_as_json(self, report_data):
        """نمایش گزارش به صورت JSON"""
        try:
            formatted_json = json.dumps(report_data, ensure_ascii=False, indent=2)
            self.json_view.setPlainText(formatted_json)
        except Exception as e:
            self.json_view.setPlainText(f"خطا در نمایش JSON: {str(e)}")
    
    def display_analysis(self, report_data):
        """نمایش تحلیل گزارش"""
        try:
            analysis_text = ""
            
            # اطلاعات پایه
            if 'report_type' in report_data:
                analysis_text += f"📊 نوع گزارش: {report_data['report_type']}\n"
            
            if 'period' in report_data:
                analysis_text += f"📅 دوره زمانی: {report_data['period']}\n"
            
            if 'generated_at' in report_data:
                analysis_text += f"⏰ زمان تولید: {report_data['generated_at']}\n"
            
            analysis_text += "\n" + "="*50 + "\n\n"
            
            # تحلیل مالی
            if 'summary' in report_data:
                summary = report_data['summary']
                analysis_text += "💰 خلاصه مالی:\n"
                
                for key, value in summary.items():
                    if isinstance(value, (int, float)):
                        if 'amount' in key or 'price' in key or 'total' in key or 'balance' in key:
                            value_str = f"{value:,.0f} ریال"
                        elif 'percentage' in key or 'ratio' in key or 'margin' in key:
                            value_str = f"{value:.2f}%"
                        else:
                            value_str = f"{value:,.0f}"
                    else:
                        value_str = str(value)
                    
                    key_fa = self.translate_key(key)
                    analysis_text += f"  • {key_fa}: {value_str}\n"
            
            # تحلیل پیشرفته
            if 'advanced_analysis' in report_data:
                analysis = report_data['advanced_analysis']
                analysis_text += "\n📈 تحلیل پیشرفته:\n"
                
                for key, value in analysis.items():
                    if isinstance(value, (int, float)):
                        if 'percentage' in key or 'ratio' in key:
                            value_str = f"{value:.2f}%"
                        else:
                            value_str = f"{value:,.0f} ریال"
                    else:
                        value_str = str(value)
                    
                    key_fa = self.translate_key(key)
                    analysis_text += f"  • {key_fa}: {value_str}\n"
            
            # توصیه‌ها
            if 'recommendations' in report_data:
                recommendations = report_data['recommendations']
                if isinstance(recommendations, list) and len(recommendations) > 0:
                    analysis_text += "\n💡 توصیه‌ها:\n"
                    for i, rec in enumerate(recommendations, 1):
                        analysis_text += f"  {i}. {rec}\n"
            
            self.analysis_view.setPlainText(analysis_text)
            
        except Exception as e:
            print(f"⚠️ خطا در نمایش تحلیل: {e}")
            self.analysis_view.setPlainText(f"خطا در نمایش تحلیل: {str(e)}")
    
    def translate_key(self, key):
        """ترجمه کلیدهای انگلیسی به فارسی"""
        translations = {
            'total_income': 'کل درآمد',
            'total_expense': 'کل هزینه',
            'net_cash_flow': 'جریان نقدی خالص',
            'net_profit': 'سود خالص',
            'gross_profit': 'سود ناخالص',
            'profit_margin': 'حاشیه سود',
            'total_revenue': 'کل درآمد',
            'total_assets': 'کل دارایی‌ها',
            'total_liabilities': 'کل بدهی‌ها',
            'total_equity': 'کل سرمایه',
            'current_ratio': 'نسبت جاری',
            'debt_to_equity': 'نسبت بدهی به سرمایه',
            'roi_percentage': 'بازده سرمایه',
            'average_roi': 'میانگین بازده سرمایه',
            'expense_ratio': 'نسبت هزینه',
            'cash_flow_adequacy_ratio': 'نسبت کفایت جریان نقدی'
        }
        
        return translations.get(key, key)
    
    def update_summary(self, report_data):
        """بروزرسانی خلاصه گزارش"""
        try:
            summary_text = ""
            
            # استخراج اطلاعات کلیدی
            if 'report_type' in report_data:
                summary_text += f"<b>نوع:</b> {report_data['report_type']}<br>"
            
            if 'period' in report_data:
                summary_text += f"<b>دوره:</b> {report_data['period']}<br>"
            
            # جمع‌بندی مالی
            if 'summary' in report_data:
                summary = report_data['summary']
                
                financial_items = ['total_income', 'total_expense', 'net_profit', 
                                 'total_revenue', 'total_assets', 'total_liabilities']
                
                for item in financial_items:
                    if item in summary:
                        value = summary[item]
                        if isinstance(value, (int, float)):
                            value_str = f"{value:,.0f} ریال"
                        else:
                            value_str = str(value)
                        
                        item_fa = self.translate_key(item)
                        color = "#27ae60" if value > 0 else "#e74c3c" if value < 0 else "#3498db"
                        summary_text += f"<b><font color='{color}'>{item_fa}:</font></b> {value_str}<br>"
            
            # وضعیت کلی
            if 'net_profit' in report_data.get('summary', {}):
                net_profit = report_data['summary']['net_profit']
                if net_profit > 0:
                    status = "<font color='#27ae60'>✅ سودده</font>"
                elif net_profit < 0:
                    status = "<font color='#e74c3c'>❌ زیان‌ده</font>"
                else:
                    status = "<font color='#3498db'>⚖️ متوازن</font>"
                
                summary_text += f"<b>وضعیت:</b> {status}"
            
            self.summary_text.setHtml(summary_text)
            
        except Exception as e:
            print(f"⚠️ خطا در بروزرسانی خلاصه: {e}")
    
    def export_json(self):
        """خروجی گرفتن به فرمت JSON"""
        if not self.current_report:
            QMessageBox.warning(self, "خطا", "ابتدا گزارشی تولید کنید!")
            return
        
        try:
            # دریافت مسیر ذخیره
            default_filename = f"گزارش_مالی_{jdatetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                "ذخیره گزارش JSON",
                default_filename,
                "JSON Files (*.json);;All Files (*)"
            )
            
            if file_path:
                if self.report_generator:
                    success = self.report_generator.export_to_json(self.current_report, file_path)
                    if success:
                        QMessageBox.information(self, "موفقیت", f"گزارش با موفقیت در\n{file_path}\nذخیره شد.")
                    else:
                        QMessageBox.warning(self, "خطا", "خطا در ذخیره فایل JSON!")
                else:
                    QMessageBox.warning(self, "خطا", "ماژول تولید گزارش در دسترس نیست!")
        
        except Exception as e:
            QMessageBox.critical(self, "خطا", f"خطا در ذخیره JSON:\n{str(e)}")
    
    def export_pdf(self):
        """خروجی گرفتن به فرمت PDF"""
        if not self.current_report:
            QMessageBox.warning(self, "خطا", "ابتدا گزارشی تولید کنید!")
            return
        
        try:
            # دریافت مسیر ذخیره
            default_filename = f"گزارش_مالی_{jdatetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                "ذخیره گزارش PDF",
                default_filename,
                "PDF Files (*.pdf);;All Files (*)"
            )
            
            if file_path:
                if self.report_generator:
                    success = self.report_generator.export_to_pdf(self.current_report, file_path)
                    if success:
                        QMessageBox.information(self, "موفقیت", f"گزارش با موفقیت در\n{file_path}\nذخیره شد.")
                    else:
                        QMessageBox.warning(self, "خطا", "خطا در ذخیره فایل PDF!")
                else:
                    QMessageBox.warning(self, "خطا", "ماژول تولید گزارش در دسترس نیست!")
        
        except Exception as e:
            QMessageBox.critical(self, "خطا", f"خطا در ذخیره PDF:\n{str(e)}")
    
    def clear_report(self):
        """پاک کردن گزارش فعلی"""
        self.current_report = None
        
        # پاک کردن نمایش‌ها
        self.result_table.clear()
        self.result_table.setRowCount(0)
        self.result_table.setColumnCount(0)
        
        self.result_tree.clear()
        self.json_view.clear()
        self.analysis_view.clear()
        self.summary_text.clear()
        
        # غیرفعال کردن دکمه‌های خروجی
        self.btn_export_json.setEnabled(False)
        self.btn_export_pdf.setEnabled(False)
        
        self.status_label.setText("✅ آماده برای تولید گزارش")
        self.report_info_label.clear()
    
    def refresh_form_data(self):
        """بروزرسانی داده‌های فرم (با نام جدید برای جلوگیری از بازگشت)"""
        try:
            # بروزرسانی لیست شرکا
            self.partner_combo.clear()
            self.partner_combo.addItem("همه شرکا", None)
            self.load_partners()
            
            # بروزرسانی تاریخ‌ها
            self.set_today_dates()
            
            self.status_label.setText("✅ داده‌ها بروزرسانی شدند")
            
            QMessageBox.information(self, "بروزرسانی", "داده‌ها با موفقیت بروزرسانی شدند.")
            
        except Exception as e:
            QMessageBox.warning(self, "خطا", f"خطا در بروزرسانی:\n{str(e)}")
    
    # ==================== متدهای عمومی ====================
    
    def refresh_data(self):
        """بروزرسانی فرم (برای استفاده از بیرون) - نام قبلی نگه داشته شده برای سازگاری"""
        self.refresh_form_data()
    
    def showEvent(self, event):
        """هنگام نمایش فرم"""
        super().showEvent(event)
        # فقط یک بار هنگام نمایش فرم داده‌ها را بارگذاری کن
        # از QTimer استفاده می‌کنیم تا بعد از نمایش کامل فرم، داده‌ها بارگذاری شوند
        QTimer.singleShot(100, self.refresh_form_data)