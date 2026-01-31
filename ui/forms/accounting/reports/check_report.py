"""
سیستم گزارش‌گیری پیشرفته چک‌ها
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QLabel, QFrame, QGroupBox, QComboBox, QLineEdit,
    QDateEdit, QFormLayout, QHeaderView, QMessageBox, QTabWidget,
    QWidget, QTextEdit, QCheckBox, QSpinBox, QProgressBar, QSplitter,
    QFileDialog, QApplication
)
from PySide6.QtCore import Qt, QDate, Signal, QTimer, QThread, pyqtSignal
from PySide6.QtGui import QFont, QColor, QBrush, QPainter, QPen
from PySide6.QtPrintSupport import QPrinter, QPrintDialog
import jdatetime
from datetime import datetime, timedelta
import json
import os

from ui.widgets.jalali_date_input import JalaliDateInput


class CheckReportWorker(QThread):
    """کارگر برای تولید گزارش در پس‌زمینه"""
    
    report_generated = Signal(list)
    progress_updated = Signal(int)
    
    def __init__(self, db, filters):
        super().__init__()
        self.db = db
        self.filters = filters
    
    def run(self):
        """اجرای تولید گزارش"""
        try:
            self.progress_updated.emit(10)
            
            # ساخت کوئری بر اساس فیلترها
            query = """
            SELECT 
                c.*,
                i.invoice_number,
                p1.first_name || ' ' || p1.last_name as drawer_name,
                p2.first_name || ' ' || p2.last_name as payee_name
            FROM Checks c
            LEFT JOIN Invoices i ON c.related_invoice = i.id
            LEFT JOIN Persons p1 ON c.drawer = p1.id
            LEFT JOIN Persons p2 ON c.payee = p2.id
            WHERE 1=1
            """
            
            params = []
            
            # فیلتر نوع چک
            if self.filters.get('check_type'):
                query += " AND c.check_type = ?"
                params.append(self.filters['check_type'])
            
            # فیلتر وضعیت
            if self.filters.get('status'):
                query += " AND c.status = ?"
                params.append(self.filters['status'])
            
            # فیلتر بانک
            if self.filters.get('bank_name'):
                query += " AND c.bank_name LIKE ?"
                params.append(f"%{self.filters['bank_name']}%")
            
            # فیلتر تاریخ شروع
            if self.filters.get('start_date'):
                start_date_gregorian = self.db.jalali_to_gregorian(self.filters['start_date'])
                query += " AND DATE(c.due_date) >= ?"
                params.append(start_date_gregorian)
            
            # فیلتر تاریخ پایان
            if self.filters.get('end_date'):
                end_date_gregorian = self.db.jalali_to_gregorian(self.filters['end_date'])
                query += " AND DATE(c.due_date) <= ?"
                params.append(end_date_gregorian)
            
            # فیلتر مبلغ
            if self.filters.get('min_amount'):
                min_amount_rial = float(self.filters['min_amount']) * 10
                query += " AND c.amount >= ?"
                params.append(min_amount_rial)
            
            if self.filters.get('max_amount'):
                max_amount_rial = float(self.filters['max_amount']) * 10
                query += " AND c.amount <= ?"
                params.append(max_amount_rial)
            
            # مرتب‌سازی
            order_by = self.filters.get('order_by', 'due_date')
            order_dir = self.filters.get('order_dir', 'ASC')
            query += f" ORDER BY c.{order_by} {order_dir}"
            
            self.progress_updated.emit(30)
            
            # اجرای کوئری
            checks = self.db.fetch_all(query, params)
            
            self.progress_updated.emit(70)
            
            # پردازش داده‌ها
            processed_checks = []
            for check in checks:
                # تبدیل تاریخ‌ها
                check['due_date_shamsi'] = self.db.gregorian_to_jalali(check.get('due_date', ''))
                check['issue_date_shamsi'] = self.db.gregorian_to_jalali(check.get('issue_date', ''))
                
                # تبدیل مبلغ به تومان
                check['amount_toman'] = check.get('amount', 0) / 10
                
                # تعیین وضعیت رنگ
                check['status_color'] = self.get_status_color(check.get('status', ''))
                
                processed_checks.append(check)
            
            self.progress_updated.emit(100)
            self.report_generated.emit(processed_checks)
            
        except Exception as e:
            print(f"❌ خطا در تولید گزارش: {e}")
            import traceback
            traceback.print_exc()
            self.report_generated.emit([])
    
    def get_status_color(self, status):
        """رنگ بر اساس وضعیت"""
        colors = {
            'وصول شده': '#27ae60',
            'وصول نشده': '#f39c12',
            'برگشتی': '#e74c3c',
            'پاس شده': '#3498db',
            'پاس نشده': '#9b59b6',
            'بلوکه شده': '#7f8c8d'
        }
        return colors.get(status, '#95a5a6')


class CheckReportDialog(QDialog):
    """دیالوگ گزارش‌گیری چک‌ها"""
    
    def __init__(self, data_manager, parent=None):
        super().__init__(parent)
        self.data_manager = data_manager
        self.db = data_manager.db
        self.check_manager = data_manager.check_manager
        
        # راست‌چین کردن
        self.setLayoutDirection(Qt.RightToLeft)
        
        self.setWindowTitle("📊 گزارش‌گیری پیشرفته چک‌ها")
        self.setup_ui()
        self.setup_styles()
        
        # تنظیم اندازه
        self.setMinimumSize(900, 700)
        
        print("✅ دیالوگ گزارش‌گیری چک‌ها ایجاد شد")
    
    def setup_styles(self):
        """تنظیم استایل"""
        self.setStyleSheet("""
            QDialog {
                background-color: #000000;
                color: #ffffff;
                font-family: 'B Nazanin';
                font-size: 11pt;
            }
            
            QLabel {
                color: #bbb;
            }
            
            QGroupBox {
                background-color: #111111;
                border: 1px solid #333;
                border-radius: 8px;
                margin-top: 20px;
                padding-top: 10px;
                font-weight: bold;
                color: #2ecc71;
            }
            
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 10px 0 10px;
                background-color: #1a252f;
                border-radius: 4px;
            }
            
            QLineEdit, QComboBox, QSpinBox {
                background-color: #222222;
                border: 1px solid #333;
                color: white;
                border-radius: 4px;
                padding: 6px;
                min-height: 30px;
            }
            
            QPushButton {
                background-color: #2c3e50;
                color: white;
                border: none;
                padding: 8px 15px;
                border-radius: 4px;
                font-weight: bold;
            }
            
            QPushButton:hover {
                background-color: #34495e;
            }
            
            QPushButton#btn_generate {
                background-color: #27ae60;
                font-size: 12pt;
                padding: 10px 20px;
            }
            
            QPushButton#btn_generate:hover {
                background-color: #2ecc71;
            }
            
            QPushButton#btn_export {
                background-color: #3498db;
            }
            
            QPushButton#btn_export:hover {
                background-color: #2980b9;
            }
            
            QPushButton#btn_print {
                background-color: #9b59b6;
            }
            
            QPushButton#btn_print:hover {
                background-color: #8e44ad;
            }
            
            QTableWidget {
                background-color: #111111;
                alternate-background-color: #0a0a0a;
                selection-background-color: #2ecc71;
                selection-color: white;
                gridline-color: #333;
                color: white;
                border: none;
                font-size: 10pt;
            }
            
            QTableWidget::item {
                padding: 8px;
                color: white;
            }
            
            QHeaderView::section {
                background-color: #2c3e50;
                color: white;
                padding: 10px;
                border: none;
                font-weight: bold;
                text-align: center;
                font-size: 10pt;
            }
            
            QTabWidget::pane {
                border: 1px solid #333;
                background-color: #111111;
                border-radius: 5px;
            }
            
            QTabBar::tab {
                background-color: #2c2c2c;
                color: #bbb;
                padding: 10px 20px;
                margin-left: 2px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }
            
            QTabBar::tab:selected {
                background-color: #2ecc71;
                color: white;
                font-weight: bold;
            }
            
            QProgressBar {
                border: 1px solid #333;
                border-radius: 4px;
                background-color: #111111;
                text-align: center;
                color: white;
            }
            
            QProgressBar::chunk {
                background-color: #27ae60;
                border-radius: 4px;
            }
        """)
    
    def setup_ui(self):
        """ایجاد رابط کاربری"""
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # 🔴 **عنوان**
        title_label = QLabel("📊 سیستم گزارش‌گیری پیشرفته چک‌ها")
        title_label.setStyleSheet("""
            QLabel {
                font-size: 16pt;
                font-weight: bold;
                color: #2ecc71;
                padding: 10px;
                background-color: #1a252f;
                border-radius: 8px;
                border: 2px solid #2ecc71;
            }
        """)
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)
        
        # 🔴 **تب‌ها**
        self.tab_widget = QTabWidget()
        
        # تب فیلترها
        filter_tab = self.create_filter_tab()
        self.tab_widget.addTab(filter_tab, "🔍 فیلترها")
        
        # تب گزارش
        report_tab = self.create_report_tab()
        self.tab_widget.addTab(report_tab, "📋 گزارش")
        
        # تب آمار
        stats_tab = self.create_stats_tab()
        self.tab_widget.addTab(stats_tab, "📈 آمار")
        
        main_layout.addWidget(self.tab_widget)
        
        # 🔴 **نوار وضعیت و پیشرفت**
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        main_layout.addWidget(self.progress_bar)
        
        self.status_label = QLabel("آماده برای تولید گزارش...")
        self.status_label.setStyleSheet("color: #bbb; font-size: 10pt;")
        main_layout.addWidget(self.status_label)
        
        # 🔴 **دکمه‌های عملیاتی**
        button_layout = QHBoxLayout()
        
        self.btn_generate = QPushButton("🚀 تولید گزارش")
        self.btn_generate.setObjectName("btn_generate")
        self.btn_generate.clicked.connect(self.generate_report)
        
        self.btn_export = QPushButton("📤 خروجی اکسل")
        self.btn_export.setObjectName("btn_export")
        self.btn_export.clicked.connect(self.export_to_excel)
        self.btn_export.setEnabled(False)
        
        self.btn_print = QPushButton("🖨️ چاپ گزارش")
        self.btn_print.setObjectName("btn_print")
        self.btn_print.clicked.connect(self.print_report)
        self.btn_print.setEnabled(False)
        
        btn_close = QPushButton("❌ بستن")
        btn_close.clicked.connect(self.reject)
        
        button_layout.addWidget(self.btn_generate)
        button_layout.addWidget(self.btn_export)
        button_layout.addWidget(self.btn_print)
        button_layout.addStretch()
        button_layout.addWidget(btn_close)
        
        main_layout.addLayout(button_layout)
    
    def create_filter_tab(self):
        """ایجاد تب فیلترها"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(15)
        
        # گروه فیلترهای اصلی
        main_group = QGroupBox("⚙️ فیلترهای اصلی")
        main_layout = QFormLayout(main_group)
        main_layout.setSpacing(10)
        main_layout.setLabelAlignment(Qt.AlignRight)
        
        # نوع چک
        self.cmb_check_type = QComboBox()
        self.cmb_check_type.addItem("همه", None)
        self.cmb_check_type.addItem("دریافتی", "دریافتی")
        self.cmb_check_type.addItem("پرداختی", "پرداختی")
        main_layout.addRow("نوع چک:", self.cmb_check_type)
        
        # وضعیت چک
        self.cmb_status = QComboBox()
        self.cmb_status.addItem("همه", None)
        self.cmb_status.addItem("وصول نشده", "وصول نشده")
        self.cmb_status.addItem("وصول شده", "وصول شده")
        self.cmb_status.addItem("برگشتی", "برگشتی")
        self.cmb_status.addItem("پاس شده", "پاس شده")
        self.cmb_status.addItem("پاس نشده", "پاس نشده")
        self.cmb_status.addItem("بلوکه شده", "بلوکه شده")
        main_layout.addRow("وضعیت:", self.cmb_status)
        
        # بانک
        self.txt_bank = QLineEdit()
        self.txt_bank.setPlaceholderText("نام بانک (اختیاری)")
        main_layout.addRow("بانک:", self.txt_bank)
        
        layout.addWidget(main_group)
        
        # گروه فیلترهای زمانی
        time_group = QGroupBox("📅 فیلتر زمانی")
        time_layout = QFormLayout(time_group)
        
        # تاریخ شروع
        self.date_start = JalaliDateInput()
        time_layout.addRow("از تاریخ:", self.date_start)
        
        # تاریخ پایان
        self.date_end = JalaliDateInput()
        time_layout.addRow("تا تاریخ:", self.date_end)
        
        # دکمه‌های سریع تاریخ
        quick_date_layout = QHBoxLayout()
        
        btn_today = QPushButton("امروز")
        btn_today.clicked.connect(lambda: self.set_quick_date('today'))
        
        btn_week = QPushButton("هفته جاری")
        btn_week.clicked.connect(lambda: self.set_quick_date('week'))
        
        btn_month = QPushButton("ماه جاری")
        btn_month.clicked.connect(lambda: self.set_quick_date('month'))
        
        btn_year = QPushButton("سال جاری")
        btn_year.clicked.connect(lambda: self.set_quick_date('year'))
        
        quick_date_layout.addWidget(btn_today)
        quick_date_layout.addWidget(btn_week)
        quick_date_layout.addWidget(btn_month)
        quick_date_layout.addWidget(btn_year)
        quick_date_layout.addStretch()
        
        time_layout.addRow("سریع:", quick_date_layout)
        
        layout.addWidget(time_group)
        
        # گروه فیلترهای مبلغی
        amount_group = QGroupBox("💰 فیلتر مبلغی")
        amount_layout = QFormLayout(amount_group)
        
        # مبلغ حداقل
        self.spin_min_amount = QSpinBox()
        self.spin_min_amount.setRange(0, 1000000000)
        self.spin_min_amount.setSuffix(" تومان")
        self.spin_min_amount.setValue(0)
        amount_layout.addRow("حداقل مبلغ:", self.spin_min_amount)
        
        # مبلغ حداکثر
        self.spin_max_amount = QSpinBox()
        self.spin_max_amount.setRange(0, 1000000000)
        self.spin_max_amount.setSuffix(" تومان")
        self.spin_max_amount.setValue(1000000000)
        amount_layout.addRow("حداکثر مبلغ:", self.spin_max_amount)
        
        layout.addWidget(amount_group)
        
        # گروه تنظیمات مرتب‌سازی
        sort_group = QGroupBox("🔢 مرتب‌سازی")
        sort_layout = QFormLayout(sort_group)
        
        # فیلد مرتب‌سازی
        self.cmb_order_by = QComboBox()
        self.cmb_order_by.addItem("تاریخ سررسید", "due_date")
        self.cmb_order_by.addItem("مبلغ", "amount")
        self.cmb_order_by.addItem("تاریخ صدور", "issue_date")
        self.cmb_order_by.addItem("شماره چک", "check_number")
        sort_layout.addRow("مرتب‌سازی بر اساس:", self.cmb_order_by)
        
        # جهت مرتب‌سازی
        self.cmb_order_dir = QComboBox()
        self.cmb_order_dir.addItem("صعودی", "ASC")
        self.cmb_order_dir.addItem("نزولی", "DESC")
        sort_layout.addRow("ترتیب:", self.cmb_order_dir)
        
        layout.addWidget(sort_group)
        
        layout.addStretch()
        
        return tab
    
    def create_report_tab(self):
        """ایجاد تب گزارش"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(10)
        
        # نوار ابزار گزارش
        toolbar_layout = QHBoxLayout()
        
        self.lbl_report_summary = QLabel("هنوز گزارشی تولید نشده است")
        self.lbl_report_summary.setStyleSheet("color: #f39c12; font-weight: bold;")
        
        toolbar_layout.addWidget(self.lbl_report_summary)
        toolbar_layout.addStretch()
        
        layout.addLayout(toolbar_layout)
        
        # جدول گزارش
        self.report_table = QTableWidget()
        self.report_table.setColumnCount(10)
        self.report_table.setHorizontalHeaderLabels([
            "ردیف",
            "شماره چک",
            "نوع",
            "بانک",
            "مبلغ (تومان)",
            "صادرکننده",
            "تاریخ سررسید",
            "وضعیت",
            "توضیحات",
            "شماره فاکتور"
        ])
        
        # تنظیمات جدول
        self.report_table.setAlternatingRowColors(True)
        self.report_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.report_table.setSelectionMode(QTableWidget.SingleSelection)
        self.report_table.setEditTriggers(QTableWidget.NoEditTriggers)
        
        # اندازه ستون‌ها
        header = self.report_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Fixed)  # ردیف
        header.setSectionResizeMode(1, QHeaderView.Fixed)  # شماره چک
        header.setSectionResizeMode(2, QHeaderView.Fixed)  # نوع
        header.setSectionResizeMode(3, QHeaderView.Stretch)  # بانک
        header.setSectionResizeMode(4, QHeaderView.Fixed)  # مبلغ
        header.setSectionResizeMode(5, QHeaderView.Stretch)  # صادرکننده
        header.setSectionResizeMode(6, QHeaderView.Fixed)  # تاریخ سررسید
        header.setSectionResizeMode(7, QHeaderView.Fixed)  # وضعیت
        header.setSectionResizeMode(8, QHeaderView.Stretch)  # توضیحات
        header.setSectionResizeMode(9, QHeaderView.Fixed)  # شماره فاکتور
        
        self.report_table.setColumnWidth(0, 60)
        self.report_table.setColumnWidth(1, 100)
        self.report_table.setColumnWidth(2, 80)
        self.report_table.setColumnWidth(4, 120)
        self.report_table.setColumnWidth(6, 110)
        self.report_table.setColumnWidth(7, 100)
        self.report_table.setColumnWidth(9, 100)
        
        layout.addWidget(self.report_table)
        
        return tab
    
    def create_stats_tab(self):
        """ایجاد تب آمار"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(20)
        
        # کارت‌های آماری
        stats_grid = QHBoxLayout()
        
        self.stat_cards = {}
        
        stats_config = [
            ("📊 تعداد کل", "0", "#3498db", "total_count"),
            ("💰 مجموع مبلغ", "0", "#27ae60", "total_amount"),
            ("📈 میانگین مبلغ", "0", "#f39c12", "avg_amount"),
            ("📉 بیشترین مبلغ", "0", "#e74c3c", "max_amount"),
            ("📊 کمترین مبلغ", "0", "#9b59b6", "min_amount"),
            ("⚠️ تعداد سررسید", "0", "#ff6b6b", "due_count")
        ]
        
        for title, default_value, color, key in stats_config:
            card = self.create_stat_card(title, default_value, color)
            stats_grid.addWidget(card)
            self.stat_cards[key] = card
        
        layout.addLayout(stats_grid)
        
        # نمودارهای آماری (متن جایگزین)
        charts_group = QGroupBox("📈 نمودارهای آماری")
        charts_layout = QVBoxLayout(charts_group)
        
        chart_placeholder = QLabel(
            "📊 نمودارها در نسخه‌های آینده اضافه خواهند شد\n\n"
            "• نمودار توزیع وضعیت چک‌ها\n"
            "• نمودار روند ماهانه\n"
            "• نمودار توزیع بانک‌ها\n"
            "• نمودار مقایسه دریافتی/پرداختی"
        )
        chart_placeholder.setAlignment(Qt.AlignCenter)
        chart_placeholder.setStyleSheet("""
            QLabel {
                color: #bbb;
                font-size: 11pt;
                padding: 20px;
                background-color: #111111;
                border-radius: 10px;
                border: 2px dashed #333;
            }
        """)
        chart_placeholder.setWordWrap(True)
        
        charts_layout.addWidget(chart_placeholder)
        layout.addWidget(charts_group)
        
        layout.addStretch()
        
        return tab
    
    def create_stat_card(self, title, value, color):
        """ایجاد کارت آماری"""
        card = QFrame()
        card.setObjectName("stat_card")
        card.setFixedSize(180, 120)
        
        layout = QVBoxLayout(card)
        layout.setSpacing(5)
        layout.setContentsMargins(15, 15, 15, 15)
        
        # آیکون و عنوان
        title_layout = QHBoxLayout()
        
        title_label = QLabel(title)
        title_label.setStyleSheet(f"""
            QLabel {{
                color: {color};
                font-size: 11pt;
                font-weight: bold;
            }}
        """)
        
        title_layout.addWidget(title_label)
        title_layout.addStretch()
        
        layout.addLayout(title_layout)
        
        # مقدار
        value_label = QLabel(value)
        value_label.setStyleSheet(f"""
            QLabel {{
                color: white;
                font-size: 18pt;
                font-weight: bold;
            }}
        """)
        value_label.setAlignment(Qt.AlignCenter)
        
        layout.addWidget(value_label)
        layout.addStretch()
        
        # ذخیره رفرنس
        card.value_label = value_label
        
        return card
    
    def set_quick_date(self, period):
        """تنظیم سریع تاریخ"""
        today = jdatetime.date.today()
        
        if period == 'today':
            start_date = today
            end_date = today
        elif period == 'week':
            # شروع هفته (شنبه)
            start_date = today - jdatetime.timedelta(days=today.weekday())
            end_date = start_date + jdatetime.timedelta(days=6)
        elif period == 'month':
            start_date = jdatetime.date(today.year, today.month, 1)
            # آخرین روز ماه
            if today.month <= 6:
                end_date = jdatetime.date(today.year, today.month, 31)
            elif today.month <= 11:
                end_date = jdatetime.date(today.year, today.month, 30)
            else:
                if jdatetime.jalali.isleap(today.year):
                    end_date = jdatetime.date(today.year, today.month, 30)
                else:
                    end_date = jdatetime.date(today.year, today.month, 29)
        elif period == 'year':
            start_date = jdatetime.date(today.year, 1, 1)
            end_date = jdatetime.date(today.year, 12, 29 if jdatetime.jalali.isleap(today.year) else 28)
        
        self.date_start.set_date(start_date)
        self.date_end.set_date(end_date)
    
    def generate_report(self):
        """تولید گزارش"""
        try:
            # جمع‌آوری فیلترها
            filters = {
                'check_type': self.cmb_check_type.currentData(),
                'status': self.cmb_status.currentData(),
                'bank_name': self.txt_bank.text().strip(),
                'start_date': self.date_start.get_date_string() if self.date_start.get_date() else None,
                'end_date': self.date_end.get_date_string() if self.date_end.get_date() else None,
                'min_amount': self.spin_min_amount.value(),
                'max_amount': self.spin_max_amount.value(),
                'order_by': self.cmb_order_by.currentData(),
                'order_dir': self.cmb_order_dir.currentData()
            }
            
            # نمایش نوار پیشرفت
            self.progress_bar.setVisible(True)
            self.progress_bar.setValue(0)
            self.status_label.setText("در حال تولید گزارش...")
            self.btn_generate.setEnabled(False)
            
            # ایجاد کارگر برای تولید گزارش در پس‌زمینه
            self.worker = CheckReportWorker(self.db, filters)
            self.worker.report_generated.connect(self.on_report_generated)
            self.worker.progress_updated.connect(self.progress_bar.setValue)
            self.worker.start()
            
        except Exception as e:
            print(f"❌ خطا در تولید گزارش: {e}")
            QMessageBox.warning(self, "خطا", f"خطا در تولید گزارش:\n{str(e)}")
            self.reset_ui_state()
    
    def on_report_generated(self, checks):
        """هنگام تولید گزارش"""
        try:
            self.progress_bar.setVisible(False)
            self.btn_generate.setEnabled(True)
            
            if not checks:
                self.status_label.setText("هیچ چکی با فیلترهای انتخابی یافت نشد.")
                self.lbl_report_summary.setText("هیچ چکی با فیلترهای انتخابی یافت نشد.")
                self.report_table.setRowCount(0)
                self.btn_export.setEnabled(False)
                self.btn_print.setEnabled(False)
                return
            
            # نمایش گزارش در جدول
            self.display_report_in_table(checks)
            
            # به‌روزرسانی آمار
            self.update_statistics(checks)
            
            # فعال کردن دکمه‌ها
            self.btn_export.setEnabled(True)
            self.btn_print.setEnabled(True)
            
            # تغییر به تب گزارش
            self.tab_widget.setCurrentIndex(1)
            
            self.status_label.setText(f"✅ گزارش با موفقیت تولید شد. تعداد: {len(checks)} چک")
            
        except Exception as e:
            print(f"❌ خطا در نمایش گزارش: {e}")
            QMessageBox.warning(self, "خطا", f"خطا در نمایش گزارش:\n{str(e)}")
            self.reset_ui_state()
    
    def display_report_in_table(self, checks):
        """نمایش گزارش در جدول"""
        self.report_table.setRowCount(len(checks))
        
        total_amount = 0
        
        for row, check in enumerate(checks):
            # محاسبات
            amount = check.get('amount_toman', 0)
            total_amount += amount
            
            # ردیف
            item = QTableWidgetItem(str(row + 1))
            item.setTextAlignment(Qt.AlignCenter)
            self.report_table.setItem(row, 0, item)
            
            # شماره چک
            item = QTableWidgetItem(check.get('check_number', ''))
            item.setTextAlignment(Qt.AlignCenter)
            self.report_table.setItem(row, 1, item)
            
            # نوع چک
            check_type = check.get('check_type', '')
            type_text = "💳 دریافتی" if check_type == 'دریافتی' else "💸 پرداختی"
            item = QTableWidgetItem(type_text)
            item.setTextAlignment(Qt.AlignCenter)
            self.report_table.setItem(row, 2, item)
            
            # بانک
            item = QTableWidgetItem(check.get('bank_name', ''))
            item.setTextAlignment(Qt.AlignCenter)
            self.report_table.setItem(row, 3, item)
            
            # مبلغ
            item = QTableWidgetItem(f"{amount:,.0f}")
            item.setTextAlignment(Qt.AlignCenter)
            self.report_table.setItem(row, 4, item)
            
            # صادرکننده
            drawer_name = check.get('drawer_name', check.get('drawer', ''))
            item = QTableWidgetItem(drawer_name)
            item.setTextAlignment(Qt.AlignRight)
            self.report_table.setItem(row, 5, item)
            
            # تاریخ سررسید
            due_date = check.get('due_date_shamsi', '')
            item = QTableWidgetItem(due_date)
            item.setTextAlignment(Qt.AlignCenter)
            
            # رنگ‌آمیزی تاریخ‌های گذشته
            if self.is_date_past(due_date) and check.get('status') in ['وصول نشده', 'پاس نشده']:
                item.setForeground(QBrush(QColor('#ff6b6b')))
            
            self.report_table.setItem(row, 6, item)
            
            # وضعیت
            status = check.get('status', '')
            status_text = self.get_status_display(status)
            item = QTableWidgetItem(status_text)
            item.setTextAlignment(Qt.AlignCenter)
            
            # رنگ پس‌زمینه بر اساس وضعیت
            color = QColor(check.get('status_color', '#2c3e50'))
            item.setBackground(QBrush(color))
            
            self.report_table.setItem(row, 7, item)
            
            # توضیحات
            desc = check.get('description', '')
            if len(desc) > 50:
                desc = desc[:47] + '...'
            item = QTableWidgetItem(desc)
            item.setTextAlignment(Qt.AlignRight)
            self.report_table.setItem(row, 8, item)
            
            # شماره فاکتور
            invoice_num = check.get('invoice_number', '')
            item = QTableWidgetItem(invoice_num if invoice_num else '-')
            item.setTextAlignment(Qt.AlignCenter)
            self.report_table.setItem(row, 9, item)
        
        # خلاصه گزارش
        summary_text = f"""
        📋 خلاصه گزارش:
        • تعداد چک‌ها: {len(checks):,} عدد
        • مجموع مبلغ: {total_amount:,.0f} تومان
        • میانگین مبلغ: {total_amount/len(checks) if checks else 0:,.0f} تومان
        • بازه زمانی: {checks[0].get('due_date_shamsi', '')} تا {checks[-1].get('due_date_shamsi', '')}
        """
        
        self.lbl_report_summary.setText(summary_text.strip())
    
    def is_date_past(self, date_str):
        """بررسی آیا تاریخ گذشته است"""
        try:
            if not date_str:
                return False
            
            parts = date_str.split('/')
            if len(parts) != 3:
                return False
            
            year, month, day = map(int, parts)
            check_date = jdatetime.date(year, month, day)
            today = jdatetime.date.today()
            
            return check_date < today
            
        except:
            return False
    
    def get_status_display(self, status):
        """نمایش وضعیت با آیکون"""
        icons = {
            'وصول شده': '✅',
            'وصول نشده': '⏳',
            'برگشتی': '❌',
            'پاس شده': '✅',
            'پاس نشده': '⏳',
            'بلوکه شده': '🔒'
        }
        return f"{icons.get(status, '📄')} {status}"
    
    def update_statistics(self, checks):
        """به‌روزرسانی آمار"""
        try:
            if not checks:
                return
            
            # محاسبات اولیه
            total_count = len(checks)
            total_amount = sum(check.get('amount_toman', 0) for check in checks)
            avg_amount = total_amount / total_count if total_count > 0 else 0
            
            amounts = [check.get('amount_toman', 0) for check in checks]
            max_amount = max(amounts) if amounts else 0
            min_amount = min(amounts) if amounts else 0
            
            # شمارش چک‌های سررسید گذشته
            due_count = 0
            today = jdatetime.date.today()
            
            for check in checks:
                due_date_str = check.get('due_date_shamsi', '')
                if due_date_str:
                    try:
                        parts = due_date_str.split('/')
                        if len(parts) == 3:
                            year, month, day = map(int, parts)
                            due_date = jdatetime.date(year, month, day)
                            
                            if due_date < today and check.get('status') in ['وصول نشده', 'پاس نشده']:
                                due_count += 1
                    except:
                        pass
            
            # به‌روزرسانی کارت‌ها
            if 'total_count' in self.stat_cards:
                self.stat_cards['total_count'].value_label.setText(f"{total_count:,}")
            
            if 'total_amount' in self.stat_cards:
                self.stat_cards['total_amount'].value_label.setText(f"{total_amount:,.0f}")
            
            if 'avg_amount' in self.stat_cards:
                self.stat_cards['avg_amount'].value_label.setText(f"{avg_amount:,.0f}")
            
            if 'max_amount' in self.stat_cards:
                self.stat_cards['max_amount'].value_label.setText(f"{max_amount:,.0f}")
            
            if 'min_amount' in self.stat_cards:
                self.stat_cards['min_amount'].value_label.setText(f"{min_amount:,.0f}")
            
            if 'due_count' in self.stat_cards:
                self.stat_cards['due_count'].value_label.setText(f"{due_count:,}")
                if due_count > 0:
                    self.stat_cards['due_count'].value_label.setStyleSheet("""
                        QLabel {
                            color: #ff6b6b;
                            font-size: 18pt;
                            font-weight: bold;
                        }
                    """)
            
        except Exception as e:
            print(f"⚠️ خطا در به‌روزرسانی آمار: {e}")
    
    def export_to_excel(self):
        """خروجی اکسل"""
        try:
            # درخواست مسیر ذخیره
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                "ذخیره گزارش اکسل",
                f"گزارش_چک‌ها_{jdatetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                "Excel Files (*.xlsx);;All Files (*)"
            )
            
            if not file_path:
                return
            
            # برای سادگی فعلاً یک فایل CSV ساده ایجاد می‌کنیم
            # در نسخه‌های آینده می‌توان از openpyxl یا xlsxwriter استفاده کرد
            
            # ایجاد فایل CSV
            import csv
            
            # اگر مسیر با .xlsx تمام شده باشد، به .csv تغییر می‌دهیم
            if file_path.endswith('.xlsx'):
                file_path = file_path[:-5] + '.csv'
            
            with open(file_path, 'w', newline='', encoding='utf-8-sig') as csvfile:
                writer = csv.writer(csvfile)
                
                # هدرها
                headers = [
                    'ردیف',
                    'شماره چک',
                    'نوع چک',
                    'بانک',
                    'مبلغ (تومان)',
                    'صادرکننده',
                    'دریافت‌کننده',
                    'تاریخ سررسید',
                    'وضعیت',
                    'توضیحات',
                    'شماره فاکتور'
                ]
                writer.writerow(headers)
                
                # داده‌ها
                for row in range(self.report_table.rowCount()):
                    row_data = []
                    for col in range(self.report_table.columnCount()):
                        item = self.report_table.item(row, col)
                        if item:
                            # حذف آیکون‌ها از وضعیت
                            text = item.text()
                            if col == 7:  # ستون وضعیت
                                text = text.split(' ', 1)[1] if ' ' in text else text
                            row_data.append(text)
                        else:
                            row_data.append('')
                    
                    writer.writerow(row_data)
            
            QMessageBox.information(self, "موفق", f"گزارش با موفقیت در مسیر زیر ذخیره شد:\n{file_path}")
            
        except Exception as e:
            QMessageBox.warning(self, "خطا", f"خطا در خروجی اکسل:\n{str(e)}")
    
    def print_report(self):
        """چاپ گزارش"""
        try:
            # در نسخه ساده، گزارش را در یک دیالوگ نمایش می‌دهیم
            print_dialog = QDialog(self)
            print_dialog.setWindowTitle("🖨️ پیش‌نمایش چاپ")
            print_dialog.setFixedSize(800, 600)
            
            layout = QVBoxLayout(print_dialog)
            
            # متن گزارش برای چاپ
            print_text = QTextEdit()
            print_text.setReadOnly(True)
            
            # ایجاد متن گزارش
            report_content = self.create_print_content()
            print_text.setHtml(report_content)
            
            layout.addWidget(print_text)
            
            # دکمه‌ها
            button_layout = QHBoxLayout()
            
            btn_print = QPushButton("🖨️ چاپ")
            btn_print.clicked.connect(lambda: self.do_print(print_text))
            
            btn_close = QPushButton("بستن")
            btn_close.clicked.connect(print_dialog.accept)
            
            button_layout.addWidget(btn_print)
            button_layout.addWidget(btn_close)
            button_layout.addStretch()
            
            layout.addLayout(button_layout)
            
            print_dialog.exec()
            
        except Exception as e:
            QMessageBox.warning(self, "خطا", f"خطا در چاپ گزارش:\n{str(e)}")
    
    def create_print_content(self):
        """ایجاد محتوای HTML برای چاپ"""
        # تعداد ردیف‌ها
        row_count = self.report_table.rowCount()
        
        if row_count == 0:
            return "<h3>گزارشی برای چاپ وجود ندارد</h3>"
        
        # جمع‌آوری داده‌ها
        data = []
        total_amount = 0
        
        for row in range(row_count):
            row_data = []
            for col in range(self.report_table.columnCount()):
                item = self.report_table.item(row, col)
                row_data.append(item.text() if item else "")
            
            # محاسبه مبلغ کل
            if row_data[4]:  # ستون مبلغ
                try:
                    amount = float(row_data[4].replace(',', ''))
                    total_amount += amount
                except:
                    pass
            
            data.append(row_data)
        
        # ایجاد HTML
        html = f"""
        <html dir="rtl">
        <head>
            <meta charset="UTF-8">
            <style>
                body {{
                    font-family: 'B Nazanin', Tahoma, Arial;
                    font-size: 12pt;
                    line-height: 1.6;
                    color: #333;
                }}
                .header {{
                    text-align: center;
                    margin-bottom: 30px;
                    border-bottom: 3px solid #2ecc71;
                    padding-bottom: 20px;
                }}
                .title {{
                    font-size: 20pt;
                    color: #2ecc71;
                    font-weight: bold;
                }}
                .subtitle {{
                    font-size: 14pt;
                    color: #7f8c8d;
                }}
                .info {{
                    background-color: #f8f9fa;
                    padding: 15px;
                    border-radius: 5px;
                    margin: 20px 0;
                    border-right: 4px solid #3498db;
                }}
                table {{
                    width: 100%;
                    border-collapse: collapse;
                    margin: 20px 0;
                }}
                th {{
                    background-color: #2c3e50;
                    color: white;
                    padding: 12px;
                    text-align: center;
                    border: 1px solid #ddd;
                }}
                td {{
                    padding: 10px;
                    border: 1px solid #ddd;
                    text-align: center;
                }}
                tr:nth-child(even) {{
                    background-color: #f2f2f2;
                }}
                .total {{
                    background-color: #27ae60;
                    color: white;
                    font-weight: bold;
                    font-size: 14pt;
                }}
                .footer {{
                    text-align: center;
                    margin-top: 30px;
                    color: #7f8c8d;
                    font-size: 10pt;
                    border-top: 1px solid #ddd;
                    padding-top: 10px;
                }}
            </style>
        </head>
        <body>
            <div class="header">
                <div class="title">📊 گزارش چک‌ها</div>
                <div class="subtitle">سیستم مدیریت تعمیرگاه شیروین</div>
                <div>تاریخ تولید: {jdatetime.datetime.now().strftime('%Y/%m/%d - %H:%M')}</div>
            </div>
            
            <div class="info">
                <strong>خلاصه گزارش:</strong><br>
                • تعداد چک‌ها: {row_count:,} عدد<br>
                • مجموع مبلغ: {total_amount:,.0f} تومان<br>
                • میانگین مبلغ: {(total_amount/row_count if row_count > 0 else 0):,.0f} تومان
            </div>
            
            <table>
                <thead>
                    <tr>
        """
        
        # هدرهای جدول
        for col in range(self.report_table.columnCount()):
            header = self.report_table.horizontalHeaderItem(col).text()
            html += f"<th>{header}</th>"
        
        html += """
                    </tr>
                </thead>
                <tbody>
        """
        
        # داده‌های جدول
        for row_data in data:
            html += "<tr>"
            for cell in row_data:
                # حذف آیکون‌ها از وضعیت
                if '✅' in cell or '⏳' in cell or '❌' in cell or '🔒' in cell:
                    cell = cell.split(' ', 1)[1] if ' ' in cell else cell
                html += f"<td>{cell}</td>"
            html += "</tr>"
        
        # ردیف جمع کل
        html += f"""
                <tr class="total">
                    <td colspan="4">جمع کل</td>
                    <td>{total_amount:,.0f}</td>
                    <td colspan="5"></td>
                </tr>
                </tbody>
            </table>
            
            <div class="footer">
                تولید شده توسط سیستم مدیریت تعمیرگاه شیروین<br>
                https://github.com/your-repo
            </div>
        </body>
        </html>
        """
        
        return html
    
    def do_print(self, text_edit):
        """اجرای عملیات چاپ"""
        try:
            # چاپ ساده
            printer = QPrinter()
            print_dialog = QPrintDialog(printer, self)
            
            if print_dialog.exec() == QPrintDialog.Accepted:
                text_edit.print_(printer)
                
        except Exception as e:
            # اگر چاپگر در دسترس نبود
            QMessageBox.information(
                self, 
                "چاپ", 
                "برای چاپ حرفه‌ای، از دکمه 'ذخیره به PDF' استفاده کنید و سپس فایل را چاپ کنید."
            )
    
    def reset_ui_state(self):
        """بازنشانی وضعیت UI"""
        self.progress_bar.setVisible(False)
        self.btn_generate.setEnabled(True)
        self.status_label.setText("آماده برای تولید گزارش...")