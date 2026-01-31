"""
فرم مدیریت فاکتورها - بازنویسی شده با InvoiceManager و تاریخ شمسی
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QFrame,
    QLineEdit, QComboBox, QDateEdit, QDoubleSpinBox,
    QTextEdit, QGroupBox, QGridLayout, QMessageBox,
    QTabWidget, QScrollArea, QSplitter, QToolButton,
    QInputDialog, QProgressDialog, QDialog, QSpinBox
)
from PySide6.QtCore import Qt, Signal, QDate, QDateTime, QTimer
from PySide6.QtGui import QFont, QColor, QBrush
import jdatetime
from datetime import datetime
import json

# ایمپورت ویجت تاریخ شمسی
try:
    from ui.widgets.jalali_date_widget import JalaliDateWidget as JalaliDatePicker
    JALALI_DATE_AVAILABLE = True
except ImportError:
    print("⚠️ JalaliDateWidget یافت نشد. از ورودی متنی استفاده می‌شود.")
    JALALI_DATE_AVAILABLE = False


class InvoiceForm(QWidget):
    """فرم مدیریت فاکتورها - بازنویسی شده با InvoiceManager"""
    
    invoice_created = Signal(int)
    invoice_updated = Signal(int)
    data_changed = Signal()
    
    def __init__(self, data_manager):
        super().__init__()
        self.data_manager = data_manager
        self.invoice_manager = self.data_manager.invoice_manager
        self.current_invoice_id = None
        self.invoice_items = []
        
        self.setLayoutDirection(Qt.RightToLeft)
        self.setup_styles()
        self.init_ui()
        self.setup_connections()
        self.load_initial_data()
        
        print("✅ فرم فاکتورنویسی ایجاد شد")
    
    def setup_styles(self):
        """تنظیم استایل فرم"""
        self.setStyleSheet("""
            QWidget {
                background-color: #000000;
                color: #ffffff;
                font-family: 'B Nazanin';
                font-size: 11pt;
            }
            
            QGroupBox {
                background-color: #111111;
                border: 2px solid #333;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 15px;
                font-weight: bold;
                color: #2ecc71;
            }
            
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top right;
                right: 10px;
                padding: 0 10px 0 10px;
            }
            
            QTableWidget {
                background-color: #111111;
                alternate-background-color: #0a0a0a;
                gridline-color: #333;
                color: #ffffff;
                border: 1px solid #333;
                border-radius: 5px;
            }
            
            QTableWidget::item {
                padding: 5px;
            }
            
            QTableWidget::item:selected {
                background-color: #2ecc71;
                color: #000000;
            }
            
            QHeaderView::section {
                background-color: #2c3e50;
                color: white;
                padding: 8px;
                border: none;
                font-weight: bold;
            }
            
            QPushButton {
                padding: 8px 15px;
                border-radius: 5px;
                font-weight: bold;
                border: none;
                color: white;
            }
            
            QPushButton#btn_create {
                background-color: #27ae60;
                font-size: 12pt;
            }
            
            QPushButton#btn_create:hover {
                background-color: #219653;
            }
        """)
    
    def init_ui(self):
        """ایجاد رابط کاربری"""
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        
        container = QWidget()
        container.setLayoutDirection(Qt.RightToLeft)
        main_layout = QVBoxLayout(container)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        header_layout = self.create_header()
        main_layout.addLayout(header_layout)
        
        splitter = QSplitter(Qt.Horizontal)
        
        self.invoice_list_widget = self.create_invoice_list_panel()
        splitter.addWidget(self.invoice_list_widget)
        
        self.invoice_detail_widget = self.create_invoice_detail_panel()
        splitter.addWidget(self.invoice_detail_widget)
        
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 2)
        
        main_layout.addWidget(splitter)
        
        footer_layout = self.create_footer_panel()
        main_layout.addLayout(footer_layout)
        
        scroll.setWidget(container)
        
        final_layout = QVBoxLayout(self)
        final_layout.setContentsMargins(0, 0, 0, 0)
        final_layout.addWidget(scroll)
    
    def create_header(self):
        """ایجاد هدر فرم"""
        header_layout = QHBoxLayout()
        
        title_label = QLabel("🧾 مدیریت فاکتورها")
        title_label.setStyleSheet("font-size: 18pt; font-weight: bold; color: #2ecc71;")
        
        search_layout = QHBoxLayout()
        search_label = QLabel("جستجو:")
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("شماره فاکتور، مشتری، پذیرش...")
        self.search_input.setMinimumWidth(300)
        
        search_btn = QPushButton("🔍 جستجو")
        search_btn.clicked.connect(self.search_invoices)
        
        search_layout.addWidget(search_label)
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(search_btn)
        
        button_layout = QHBoxLayout()
        
        new_btn = QPushButton("➕ فاکتور جدید")
        new_btn.setObjectName("btn_create")
        new_btn.clicked.connect(self.create_new_invoice)
        
        refresh_btn = QPushButton("🔄 بروزرسانی")
        refresh_btn.clicked.connect(self.refresh_data)
        
        button_layout.addWidget(new_btn)
        button_layout.addWidget(refresh_btn)
        
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        header_layout.addLayout(search_layout)
        header_layout.addSpacing(20)
        header_layout.addLayout(button_layout)
        
        return header_layout
    
    def create_invoice_list_panel(self):
        """ایجاد پنل لیست فاکتورها"""
        panel = QFrame()
        panel.setFrameStyle(QFrame.StyledPanel | QFrame.Raised)
        layout = QVBoxLayout(panel)
        
        list_title = QLabel("📋 لیست فاکتورها")
        list_title.setStyleSheet("font-size: 14pt; font-weight: bold; color: #3498db;")
        layout.addWidget(list_title)
        
        filter_layout = QHBoxLayout()
        
        status_label = QLabel("وضعیت:")
        self.status_filter = QComboBox()
        self.status_filter.addItems(["همه", "پرداخت شده", "نقدی", "نسیه", "چک", "کارت"])
        self.status_filter.currentIndexChanged.connect(self.filter_invoices)
        
        date_label = QLabel("از تاریخ:")
        self.date_from_filter = self.create_jalali_date_widget()
        
        to_label = QLabel("تا تاریخ:")
        self.date_to_filter = self.create_jalali_date_widget()
        
        filter_layout.addWidget(status_label)
        filter_layout.addWidget(self.status_filter)
        filter_layout.addStretch()
        filter_layout.addWidget(date_label)
        filter_layout.addWidget(self.date_from_filter)
        filter_layout.addWidget(to_label)
        filter_layout.addWidget(self.date_to_filter)
        
        layout.addLayout(filter_layout)
        
        self.invoice_table = QTableWidget()
        self.invoice_table.setColumnCount(7)
        self.invoice_table.setHorizontalHeaderLabels([
            "شماره فاکتور", "مشتری", "تاریخ", "مبلغ کل", 
            "پرداخت شده", "مانده", "وضعیت"
        ])
        
        header = self.invoice_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
        self.invoice_table.setAlternatingRowColors(True)
        self.invoice_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.invoice_table.setSelectionMode(QTableWidget.SingleSelection)
        self.invoice_table.setEditTriggers(QTableWidget.NoEditTriggers)
        
        self.invoice_table.cellClicked.connect(self.on_invoice_selected)
        
        layout.addWidget(self.invoice_table)
        
        stats_layout = QHBoxLayout()
        
        self.total_invoices_label = QLabel("تعداد فاکتورها: 0")
        self.total_amount_label = QLabel("جمع مبالغ: 0 تومان")
        self.total_paid_label = QLabel("جمع پرداختی: 0 تومان")
        
        stats_layout.addWidget(self.total_invoices_label)
        stats_layout.addWidget(self.total_amount_label)
        stats_layout.addWidget(self.total_paid_label)
        stats_layout.addStretch()
        
        layout.addLayout(stats_layout)
        
        return panel
    
    def create_jalali_date_widget(self):
        """ایجاد ویجت تاریخ شمسی"""
        if JALALI_DATE_AVAILABLE:
            widget = JalaliDatePicker()
            widget.set_date(jdatetime.date.today())
            return widget
        else:
            widget = QLineEdit()
            widget.setText(jdatetime.date.today().strftime("%Y/%m/%d"))
            widget.setReadOnly(True)
            widget.setStyleSheet("""
                QLineEdit {
                    background-color: #222222;
                    border: 1px solid #333;
                    color: white;
                    border-radius: 4px;
                    padding: 6px;
                }
            """)
            return widget
    
    def create_invoice_detail_panel(self):
        """ایجاد پنل جزئیات فاکتور"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        self.detail_tabs = QTabWidget()
        
        info_tab = self.create_info_tab()
        self.detail_tabs.addTab(info_tab, "📋 اطلاعات فاکتور")
        
        items_tab = self.create_items_tab()
        self.detail_tabs.addTab(items_tab, "🛒 اقلام فاکتور")
        
        payments_tab = self.create_payments_tab()
        self.detail_tabs.addTab(payments_tab, "💳 پرداخت‌ها")
        
        layout.addWidget(self.detail_tabs)
        
        return panel
    
    def create_info_tab(self):
        """ایجاد تب اطلاعات فاکتور"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(15)
        
        basic_group = QGroupBox("اطلاعات پایه فاکتور")
        basic_layout = QGridLayout(basic_group)
        
        basic_layout.addWidget(QLabel("شماره فاکتور:"), 0, 0)
        self.invoice_number = QLabel("--")
        basic_layout.addWidget(self.invoice_number, 0, 1)
        
        basic_layout.addWidget(QLabel("تاریخ فاکتور:"), 0, 2)
        self.invoice_date = self.create_jalali_date_widget()
        basic_layout.addWidget(self.invoice_date, 0, 3)
        
        basic_layout.addWidget(QLabel("نوع فاکتور:"), 1, 0)
        self.invoice_type = QComboBox()
        self.invoice_type.addItems(["خدمات", "فروش", "بیرون سپاری", "خرید", "مرجوعی"])
        basic_layout.addWidget(self.invoice_type, 1, 1)
        
        basic_layout.addWidget(QLabel("وضعیت پرداخت:"), 1, 2)
        self.payment_status = QComboBox()
        self.payment_status.addItems(["نقدی", "نسیه", "چک", "کارت"])
        basic_layout.addWidget(self.payment_status, 1, 3)
        
        layout.addWidget(basic_group)
        
        relation_group = QGroupBox("اطلاعات مرتبط")
        relation_layout = QGridLayout(relation_group)
        
        relation_layout.addWidget(QLabel("مشتری:"), 0, 0)
        self.customer_combo = QComboBox()
        relation_layout.addWidget(self.customer_combo, 0, 1)
        
        btn_select_customer = QPushButton("انتخاب مشتری")
        btn_select_customer.clicked.connect(self.select_customer)
        relation_layout.addWidget(btn_select_customer, 0, 2)
        
        relation_layout.addWidget(QLabel("پذیرش:"), 1, 0)
        self.reception_combo = QComboBox()
        relation_layout.addWidget(self.reception_combo, 1, 1)
        
        btn_select_reception = QPushButton("انتخاب پذیرش")
        btn_select_reception.clicked.connect(self.select_reception)
        relation_layout.addWidget(btn_select_reception, 1, 2)
        
        relation_layout.addWidget(QLabel("توضیحات:"), 2, 0)
        self.description_input = QTextEdit()
        self.description_input.setMaximumHeight(80)
        relation_layout.addWidget(self.description_input, 2, 1, 1, 2)
        
        layout.addWidget(relation_group)
        
        amount_group = QGroupBox("مقادیر مالی")
        amount_layout = QGridLayout(amount_group)
        
        amount_layout.addWidget(QLabel("جمع کل:"), 0, 0)
        self.subtotal_label = QLabel("0 تومان")
        self.subtotal_label.setStyleSheet("font-size: 14pt; color: #f39c12;")
        amount_layout.addWidget(self.subtotal_label, 0, 1)
        
        amount_layout.addWidget(QLabel("تخفیف (%):"), 1, 0)
        self.discount_spin = QDoubleSpinBox()
        self.discount_spin.setRange(0, 100)
        self.discount_spin.setValue(0)
        self.discount_spin.setSuffix(" %")
        amount_layout.addWidget(self.discount_spin, 1, 1)
        
        self.discount_amount = QLabel("0 تومان")
        amount_layout.addWidget(self.discount_amount, 1, 2)
        
        amount_layout.addWidget(QLabel("مالیات (%):"), 2, 0)
        self.tax_spin = QDoubleSpinBox()
        self.tax_spin.setRange(0, 100)
        self.tax_spin.setValue(9)
        self.tax_spin.setSuffix(" %")
        amount_layout.addWidget(self.tax_spin, 2, 1)
        
        self.tax_amount = QLabel("0 تومان")
        amount_layout.addWidget(self.tax_amount, 2, 2)
        
        amount_layout.addWidget(QLabel("مبلغ نهایی:"), 3, 0)
        self.total_label = QLabel("0 تومان")
        self.total_label.setStyleSheet("font-size: 16pt; font-weight: bold; color: #2ecc71;")
        amount_layout.addWidget(self.total_label, 3, 1)
        
        layout.addWidget(amount_group)
        
        button_layout = QHBoxLayout()
        
        self.save_btn = QPushButton("💾 ذخیره فاکتور")
        self.save_btn.setObjectName("btn_create")
        self.save_btn.clicked.connect(self.save_invoice)
        
        self.cancel_btn = QPushButton("❌ انصراف")
        self.cancel_btn.clicked.connect(self.cancel_edit)
        
        button_layout.addStretch()
        button_layout.addWidget(self.save_btn)
        button_layout.addWidget(self.cancel_btn)
        
        layout.addLayout(button_layout)
        layout.addStretch()
        
        return tab
    
    def create_items_tab(self):
        """ایجاد تب اقلام فاکتور"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        item_buttons_layout = QHBoxLayout()
        
        btn_add_service = QPushButton("➕ افزودن خدمت")
        btn_add_service.setObjectName("btn_add_item")
        btn_add_service.clicked.connect(self.add_service_item)
        
        btn_add_part = QPushButton("🔩 افزودن قطعه")
        btn_add_part.setObjectName("btn_add_item")
        btn_add_part.clicked.connect(self.add_part_item)
        
        btn_remove_item = QPushButton("🗑️ حذف آیتم انتخاب شده")
        btn_remove_item.setObjectName("btn_delete")
        btn_remove_item.clicked.connect(self.remove_selected_item)
        
        item_buttons_layout.addWidget(btn_add_service)
        item_buttons_layout.addWidget(btn_add_part)
        item_buttons_layout.addStretch()
        item_buttons_layout.addWidget(btn_remove_item)
        
        layout.addLayout(item_buttons_layout)
        
        self.items_table = QTableWidget()
        self.items_table.setColumnCount(8)
        self.items_table.setHorizontalHeaderLabels([
            "ردیف", "نوع", "نام آیتم", "تعداد", 
            "قیمت واحد", "تخفیف", "مالیات", "جمع"
        ])
        
        header = self.items_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
        self.items_table.setAlternatingRowColors(True)
        self.items_table.setSelectionBehavior(QTableWidget.SelectRows)
        
        layout.addWidget(self.items_table)
        
        items_summary_layout = QHBoxLayout()
        
        self.items_count_label = QLabel("تعداد اقلام: 0")
        self.items_total_label = QLabel("جمع کل اقلام: 0 تومان")
        
        items_summary_layout.addWidget(self.items_count_label)
        items_summary_layout.addWidget(self.items_total_label)
        items_summary_layout.addStretch()
        
        layout.addLayout(items_summary_layout)
        
        return tab
    
    def create_payments_tab(self):
        """ایجاد تب پرداخت‌ها"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        payment_info_layout = QGridLayout()
        
        payment_info_layout.addWidget(QLabel("مبلغ قابل پرداخت:"), 0, 0)
        self.payable_amount = QLabel("0 تومان")
        self.payable_amount.setStyleSheet("font-size: 14pt; color: #f39c12;")
        payment_info_layout.addWidget(self.payable_amount, 0, 1)
        
        payment_info_layout.addWidget(QLabel("پرداخت شده:"), 1, 0)
        self.paid_amount = QLabel("0 تومان")
        payment_info_layout.addWidget(self.paid_amount, 1, 1)
        
        payment_info_layout.addWidget(QLabel("مانده:"), 2, 0)
        self.remaining_amount = QLabel("0 تومان")
        self.remaining_amount.setStyleSheet("font-size: 14pt; font-weight: bold; color: #e74c3c;")
        payment_info_layout.addWidget(self.remaining_amount, 2, 1)
        
        layout.addLayout(payment_info_layout)
        
        payment_buttons_layout = QHBoxLayout()
        
        btn_cash_payment = QPushButton("💵 پرداخت نقدی")
        btn_cash_payment.setObjectName("btn_payment")
        btn_cash_payment.clicked.connect(lambda: self.record_payment('نقدی'))
        
        btn_card_payment = QPushButton("💳 پرداخت کارت")
        btn_card_payment.setObjectName("btn_payment")
        btn_card_payment.clicked.connect(lambda: self.record_payment('کارت'))
        
        btn_check_payment = QPushButton("📄 پرداخت چک")
        btn_check_payment.setObjectName("btn_payment")
        btn_check_payment.clicked.connect(lambda: self.record_payment('چک'))
        
        payment_buttons_layout.addWidget(btn_cash_payment)
        payment_buttons_layout.addWidget(btn_card_payment)
        payment_buttons_layout.addWidget(btn_check_payment)
        payment_buttons_layout.addStretch()
        
        layout.addLayout(payment_buttons_layout)
        
        self.payments_table = QTableWidget()
        self.payments_table.setColumnCount(5)
        self.payments_table.setHorizontalHeaderLabels([
            "تاریخ", "نوع پرداخت", "مبلغ", "توضیحات", "وضعیت"
        ])
        
        header = self.payments_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
        
        layout.addWidget(self.payments_table)
        
        return tab
    
    def create_footer_panel(self):
        """ایجاد پنل فوتر"""
        footer_layout = QHBoxLayout()
        
        summary_frame = QFrame()
        summary_frame.setStyleSheet("""
            QFrame {
                background-color: #1e1e1e;
                border: 2px solid #2ecc71;
                border-radius: 10px;
                padding: 15px;
            }
        """)
        
        summary_layout = QGridLayout(summary_frame)
        
        summary_layout.addWidget(QLabel("💰 خلاصه مالی فاکتور:"), 0, 0, 1, 2)
        
        summary_items = [
            ("جمع کل اقلام:", "subtotal_summary"),
            ("تخفیف:", "discount_summary"),
            ("مالیات:", "tax_summary"),
            ("مبلغ قابل پرداخت:", "payable_summary"),
            ("پرداخت شده:", "paid_summary"),
            ("مانده حساب:", "balance_summary")
        ]
        
        for i, (label_text, obj_name) in enumerate(summary_items):
            summary_layout.addWidget(QLabel(label_text), i+1, 0)
            label = QLabel("0 تومان")
            label.setObjectName(obj_name)
            if "مانده" in label_text or "پرداخت" in label_text:
                label.setStyleSheet("font-weight: bold; color: #f39c12;")
            summary_layout.addWidget(label, i+1, 1)
        
        footer_layout.addWidget(summary_frame)
        
        final_buttons_layout = QVBoxLayout()
        
        btn_print = QPushButton("🖨️ چاپ فاکتور")
        btn_print.setObjectName("btn_print")
        btn_print.clicked.connect(self.print_invoice)
        
        btn_export = QPushButton("📤 خروجی PDF")
        btn_export.clicked.connect(self.export_invoice)
        
        final_buttons_layout.addWidget(btn_print)
        final_buttons_layout.addWidget(btn_export)
        final_buttons_layout.addStretch()
        
        footer_layout.addLayout(final_buttons_layout)
        
        return footer_layout
    
    def setup_connections(self):
        """اتصال سیگنال‌ها"""
        self.discount_spin.valueChanged.connect(self.calculate_totals)
        self.tax_spin.valueChanged.connect(self.calculate_totals)
        self.payment_status.currentTextChanged.connect(self.on_payment_status_changed)
        
        if hasattr(self.invoice_date, 'date_changed'):
            self.invoice_date.date_changed.connect(self.on_date_changed)
    
    def on_date_changed(self, date):
        """هنگام تغییر تاریخ"""
        print(f"📅 تاریخ فاکتور تغییر کرد به: {date}")
    
    def load_initial_data(self):
        """بارگذاری داده‌های اولیه"""
        self.load_customers()
        self.load_receptions()
        self.load_invoice_list()
        self.set_new_invoice_mode()
        
        print("✅ داده‌های اولیه فاکتور بارگذاری شد")
    
    def load_customers(self):
        """بارگذاری لیست مشتریان"""
        try:
            self.customer_combo.clear()
            
            query = """
            SELECT id, first_name || ' ' || last_name as full_name, mobile
            FROM Persons 
            WHERE person_type = 'مشتری'
            ORDER BY last_name, first_name
            """
            
            customers = self.data_manager.db.fetch_all(query)
            
            self.customer_combo.addItem("-- انتخاب مشتری --", None)
            
            for customer in customers:
                display_text = f"{customer['full_name']} - {customer['mobile']}"
                self.customer_combo.addItem(display_text, customer['id'])
                
        except Exception as e:
            print(f"⚠️ خطا در بارگذاری مشتریان: {e}")
    
    def load_receptions(self):
        """بارگذاری لیست پذیرش‌ها"""
        try:
            self.reception_combo.clear()
            
            query = """
            SELECT r.id, r.reception_number, 
                   p.first_name || ' ' || p.last_name as customer_name,
                   d.device_type, d.brand
            FROM Receptions r
            JOIN Persons p ON r.customer_id = p.id
            JOIN Devices d ON r.device_id = d.id
            WHERE r.status IN ('تعمیر شده', 'تحویل داده شده')
            ORDER BY r.reception_date DESC
            """
            
            receptions = self.data_manager.db.fetch_all(query)
            
            self.reception_combo.addItem("-- انتخاب پذیرش --", None)
            
            for reception in receptions:
                display_text = f"{reception['reception_number']} - {reception['customer_name']} - {reception['device_type']}"
                self.reception_combo.addItem(display_text, reception['id'])
                
        except Exception as e:
            print(f"⚠️ خطا در بارگذاری پذیرش‌ها: {e}")
    
    def load_invoice_list(self):
        """بارگذاری لیست فاکتورها با استفاده از InvoiceManager"""
        try:
            self.invoice_table.setRowCount(0)
            
            # استفاده از InvoiceManager برای دریافت فاکتورها
            invoices = self.invoice_manager.get_all_invoices()
            
            total_count = len(invoices)
            total_amount = 0
            total_paid = 0
            
            for row_idx, invoice in enumerate(invoices):
                self.invoice_table.insertRow(row_idx)
                
                self.invoice_table.setItem(row_idx, 0, 
                    QTableWidgetItem(invoice.get('invoice_number', '')))
                
                self.invoice_table.setItem(row_idx, 1,
                    QTableWidgetItem(invoice.get('customer_name', '--')))
                
                self.invoice_table.setItem(row_idx, 2,
                    QTableWidgetItem(invoice.get('invoice_date_shamsi', '--')))
                
                total = invoice.get('total', 0)
                total_toman = total / 10
                total_amount += total
                self.invoice_table.setItem(row_idx, 3,
                    QTableWidgetItem(f"{total_toman:,.0f} تومان"))
                
                paid = invoice.get('paid_amount', 0)
                paid_toman = paid / 10
                total_paid += paid
                self.invoice_table.setItem(row_idx, 4,
                    QTableWidgetItem(f"{paid_toman:,.0f} تومان"))
                
                remaining = invoice.get('remaining_amount', 0)
                remaining_toman = remaining / 10
                
                remaining_item = QTableWidgetItem(f"{remaining_toman:,.0f} تومان")
                if remaining > 0:
                    remaining_item.setForeground(QBrush(QColor("#e74c3c")))
                else:
                    remaining_item.setForeground(QBrush(QColor("#27ae60")))
                self.invoice_table.setItem(row_idx, 5, remaining_item)
                
                status = invoice.get('payment_status', '')
                status_item = QTableWidgetItem(status)
                
                if status == 'پرداخت شده':
                    status_item.setForeground(QBrush(QColor("#27ae60")))
                elif status == 'نسیه':
                    status_item.setForeground(QBrush(QColor("#e74c3c")))
                elif status == 'چک':
                    status_item.setForeground(QBrush(QColor("#f39c12")))
                elif status == 'کارت':
                    status_item.setForeground(QBrush(QColor("#3498db")))
                    
                self.invoice_table.setItem(row_idx, 6, status_item)
            
            self.total_invoices_label.setText(f"تعداد فاکتورها: {total_count}")
            self.total_amount_label.setText(f"جمع مبالغ: {total_amount/10:,.0f} تومان")
            self.total_paid_label.setText(f"جمع پرداختی: {total_paid/10:,.0f} تومان")
            
            print(f"✅ {total_count} فاکتور بارگذاری شد")
            
        except Exception as e:
            print(f"⚠️ خطا در بارگذاری لیست فاکتورها: {e}")
            QMessageBox.warning(self, "خطا", f"خطا در بارگذاری فاکتورها:\n{str(e)}")
    
    def set_new_invoice_mode(self):
        """تنظیم حالت ایجاد فاکتور جدید"""
        self.current_invoice_id = None
        self.invoice_items = []
        
        self.invoice_number.setText("-- (خودکار تولید می‌شود)")
        self.description_input.clear()
        self.discount_spin.setValue(0)
        self.tax_spin.setValue(9)
        
        try:
            today_jalali = jdatetime.datetime.now().date()
            self.set_widget_date(self.invoice_date, today_jalali)
            
            date_30_days_ago = today_jalali - jdatetime.timedelta(days=30)
            self.set_widget_date(self.date_from_filter, date_30_days_ago)
            self.set_widget_date(self.date_to_filter, today_jalali)
            
            self.customer_combo.setCurrentIndex(0)
            self.reception_combo.setCurrentIndex(0)
            self.invoice_type.setCurrentIndex(0)
            self.payment_status.setCurrentIndex(0)
            
        except Exception as e:
            print(f"⚠️ خطا در تنظیم تاریخ شمسی: {e}")
        
        self.clear_items_table()
        self.clear_payments_table()
        self.calculate_totals()
        
        print("📄 حالت فاکتور جدید تنظیم شد")
    
    def set_widget_date(self, widget, jalali_date):
        """تنظیم تاریخ در ویجت"""
        if hasattr(widget, 'set_date'):
            widget.set_date(jalali_date)
        elif isinstance(widget, QLineEdit):
            widget.setText(jalali_date.strftime("%Y/%m/%d"))
    
    def get_widget_date(self, widget):
        """دریافت تاریخ از ویجت"""
        if hasattr(widget, 'get_date'):
            return widget.get_date()
        elif isinstance(widget, QLineEdit):
            try:
                return jdatetime.datetime.strptime(widget.text(), "%Y/%m/%d").date()
            except:
                return jdatetime.date.today()
        return jdatetime.date.today()
    
    def clear_items_table(self):
        """پاک کردن جدول اقلام"""
        self.items_table.setRowCount(0)
        self.items_count_label.setText("تعداد اقلام: 0")
        self.items_total_label.setText("جمع کل اقلام: 0 تومان")
    
    def clear_payments_table(self):
        """پاک کردن جدول پرداخت‌ها"""
        self.payments_table.setRowCount(0)
    
    def search_invoices(self):
        """جستجو در فاکتورها"""
        search_text = self.search_input.text().strip()
        if not search_text:
            self.load_invoice_list()
            return
        
        try:
            self.invoice_table.setRowCount(0)
            
            query = """
            SELECT i.*, 
                   p.first_name || ' ' || p.last_name as customer_name,
                   (i.total - i.paid_amount) as remaining
            FROM Invoices i
            LEFT JOIN Persons p ON i.customer_id = p.id
            WHERE i.invoice_number LIKE ? 
               OR p.first_name LIKE ? 
               OR p.last_name LIKE ? 
               OR p.mobile LIKE ?
            ORDER BY i.invoice_date DESC
            """
            
            search_term = f"%{search_text}%"
            invoices = self.data_manager.db.fetch_all(query, 
                (search_term, search_term, search_term, search_term))
            
            # نمایش نتایج
            for row_idx, invoice in enumerate(invoices):
                self.invoice_table.insertRow(row_idx)
                
                # پر کردن جدول (مشابه load_invoice_list)
                # ...
            
            QMessageBox.information(self, "جستجو", 
                f"تعداد {len(invoices)} فاکتور یافت شد.")
                
        except Exception as e:
            QMessageBox.warning(self, "خطای جستجو", f"خطا در جستجو:\n{str(e)}")
    
    def filter_invoices(self):
        """فیلتر کردن فاکتورها"""
        status = self.status_filter.currentText()
        date_from = self.get_widget_date(self.date_from_filter)
        date_to = self.get_widget_date(self.date_to_filter)
        
        if status == "همه":
            status = None
        
        invoices = self.invoice_manager.get_all_invoices(
            status=status,
            start_date=date_from.strftime("%Y/%m/%d"),
            end_date=date_to.strftime("%Y/%m/%d")
        )
        
        self.display_invoices_in_table(invoices)
    
    def display_invoices_in_table(self, invoices):
        """نمایش فاکتورها در جدول"""
        self.invoice_table.setRowCount(0)
        
        for row_idx, invoice in enumerate(invoices):
            self.invoice_table.insertRow(row_idx)
            
            # پر کردن جدول (مشابه load_invoice_list)
            # ...
    
    def on_invoice_selected(self, row, column):
        """هنگام انتخاب فاکتور از لیست"""
        try:
            invoice_number = self.invoice_table.item(row, 0).text()
            
            # استفاده از InvoiceManager برای دریافت اطلاعات فاکتور
            query = """
            SELECT id FROM Invoices WHERE invoice_number = ?
            """
            result = self.data_manager.db.fetch_one(query, (invoice_number,))
            
            if not result:
                QMessageBox.warning(self, "خطا", "فاکتور یافت نشد!")
                return
            
            invoice_id = result['id']
            self.current_invoice_id = invoice_id
            
            invoice = self.invoice_manager.get_invoice_by_id(invoice_id)
            
            if invoice:
                self.load_invoice_details(invoice)
                self.load_invoice_items()
                self.load_invoice_payments()
                
                print(f"📄 فاکتور {invoice_number} انتخاب شد")
            
        except Exception as e:
            print(f"⚠️ خطا در انتخاب فاکتور: {e}")
    
    def load_invoice_details(self, invoice):
        """بارگذاری جزئیات فاکتور"""
        try:
            self.invoice_number.setText(invoice.get('invoice_number', '--'))
            
            # تنظیم تاریخ فاکتور
            invoice_date_str = invoice.get('invoice_date_shamsi', '')
            if invoice_date_str:
                try:
                    year, month, day = map(int, invoice_date_str.split('/'))
                    jalali_date = jdatetime.date(year, month, day)
                    self.set_widget_date(self.invoice_date, jalali_date)
                except:
                    today = jdatetime.date.today()
                    self.set_widget_date(self.invoice_date, today)
            
            invoice_type = invoice.get('invoice_type', 'خدمات')
            index = self.invoice_type.findText(invoice_type)
            if index >= 0:
                self.invoice_type.setCurrentIndex(index)
            
            payment_status = invoice.get('payment_status', 'نقدی')
            index = self.payment_status.findText(payment_status)
            if index >= 0:
                self.payment_status.setCurrentIndex(index)
            
            customer_id = invoice.get('customer_id')
            if customer_id:
                for i in range(self.customer_combo.count()):
                    if self.customer_combo.itemData(i) == customer_id:
                        self.customer_combo.setCurrentIndex(i)
                        break
            
            reception_id = invoice.get('reception_id')
            if reception_id:
                for i in range(self.reception_combo.count()):
                    if self.reception_combo.itemData(i) == reception_id:
                        self.reception_combo.setCurrentIndex(i)
                        break
            
            self.description_input.setPlainText(invoice.get('description', ''))
            
            subtotal = invoice.get('subtotal', 0)
            discount = invoice.get('discount', 0)
            tax = invoice.get('tax', 0)
            total = invoice.get('total', 0)
            paid = invoice.get('paid_amount', 0)
            remaining = invoice.get('remaining_amount', 0)
            
            discount_percent = (discount / subtotal * 100) if subtotal > 0 else 0
            tax_percent = (tax / subtotal * 100) if subtotal > 0 else 9
            
            self.discount_spin.setValue(discount_percent)
            self.tax_spin.setValue(tax_percent)
            
            self.update_amount_labels(subtotal, discount, tax, total, paid, remaining)
            
            print(f"✅ جزئیات فاکتور بارگذاری شد")
            
        except Exception as e:
            print(f"⚠️ خطا در بارگذاری جزئیات فاکتور: {e}")
    
    def load_invoice_items(self):
        """بارگذاری اقلام فاکتور"""
        try:
            if not self.current_invoice_id:
                return
            
            self.clear_items_table()
            self.invoice_items = []
            
            items = self.invoice_manager.get_invoice_items(self.current_invoice_id)
            
            for row_idx, item in enumerate(items):
                self.items_table.insertRow(row_idx)
                
                self.items_table.setItem(row_idx, 0,
                    QTableWidgetItem(str(row_idx + 1)))
                
                self.items_table.setItem(row_idx, 1,
                    QTableWidgetItem(item.get('item_type', '')))
                
                self.items_table.setItem(row_idx, 2,
                    QTableWidgetItem(item.get('display_name', '')))
                
                self.items_table.setItem(row_idx, 3,
                    QTableWidgetItem(str(item.get('quantity', 1))))
                
                unit_price = item.get('unit_price_toman', 0)
                self.items_table.setItem(row_idx, 4,
                    QTableWidgetItem(f"{unit_price:,.0f} تومان"))
                
                self.items_table.setItem(row_idx, 5,
                    QTableWidgetItem("0%"))
                
                self.items_table.setItem(row_idx, 6,
                    QTableWidgetItem("9%"))
                
                total_price = item.get('total_price_toman', 0)
                self.items_table.setItem(row_idx, 7,
                    QTableWidgetItem(f"{total_price:,.0f} تومان"))
                
                self.invoice_items.append({
                    'item_type': item.get('item_type', ''),
                    'item_id': item.get('item_id'),
                    'item_name': item.get('item_name', ''),
                    'quantity': item.get('quantity', 1),
                    'unit_price': item.get('unit_price', 0),
                    'total_price': item.get('total_price', 0),
                    'description': item.get('description', '')
                })
            
            self.items_count_label.setText(f"تعداد اقلام: {len(items)}")
            self.calculate_totals()
            
            print(f"✅ {len(items)} قلم بارگذاری شد")
            
        except Exception as e:
            print(f"⚠️ خطا در بارگذاری اقلام فاکتور: {e}")
    
    def load_invoice_payments(self):
        """بارگذاری پرداخت‌های فاکتور"""
        try:
            if not self.current_invoice_id:
                return
            
            self.clear_payments_table()
            
            query = """
            SELECT at.*, a.account_name
            FROM AccountingTransactions at
            LEFT JOIN Accounts a ON at.to_account_id = a.id
            WHERE at.reference_type = 'فاکتور' 
              AND at.reference_id = ?
              AND at.transaction_type IN ('دریافت', 'انتقال')
            ORDER BY at.transaction_date DESC
            """
            
            payments = self.data_manager.db.fetch_all(query, (self.current_invoice_id,))
            
            total_paid = 0
            
            for row_idx, payment in enumerate(payments):
                self.payments_table.insertRow(row_idx)
                
                trans_date = payment.get('transaction_date', '')
                if trans_date:
                    jalali_date = self.data_manager.db.gregorian_to_jalali(trans_date)
                else:
                    jalali_date = '--'
                self.payments_table.setItem(row_idx, 0,
                    QTableWidgetItem(jalali_date))
                
                trans_type = payment.get('transaction_type', '')
                account_name = payment.get('account_name', '')
                payment_type = f"{trans_type} - {account_name}" if account_name else trans_type
                self.payments_table.setItem(row_idx, 1,
                    QTableWidgetItem(payment_type))
                
                amount = payment.get('amount', 0)
                amount_toman = amount / 10
                total_paid += amount
                self.payments_table.setItem(row_idx, 2,
                    QTableWidgetItem(f"{amount_toman:,.0f} تومان"))
                
                description = payment.get('description', '')
                self.payments_table.setItem(row_idx, 3,
                    QTableWidgetItem(description))
                
                status = "تأیید شده"
                self.payments_table.setItem(row_idx, 4,
                    QTableWidgetItem(status))
            
            self.update_payment_amounts(total_paid)
            
            print(f"✅ {len(payments)} پرداخت بارگذاری شد")
            
        except Exception as e:
            print(f"⚠️ خطا در بارگذاری پرداخت‌ها: {e}")
    
    def select_customer(self):
        """انتخاب مشتری"""
        dialog = CustomerSelectionDialog(self.data_manager, self)
        if dialog.exec():
            selected_customer = dialog.get_selected_customer()
            if selected_customer:
                customer_id = selected_customer['id']
                for i in range(self.customer_combo.count()):
                    if self.customer_combo.itemData(i) == customer_id:
                        self.customer_combo.setCurrentIndex(i)
                        self.load_customer_receptions(customer_id)
                        break
    
    def select_reception(self):
        """انتخاب پذیرش"""
        dialog = ReceptionSelectionDialog(self.data_manager, self)
        if dialog.exec():
            selected_reception = dialog.get_selected_reception()
            if selected_reception:
                reception_id = selected_reception['id']
                for i in range(self.reception_combo.count()):
                    if self.reception_combo.itemData(i) == reception_id:
                        self.reception_combo.setCurrentIndex(i)
                        self.load_reception_items(reception_id)
                        break
    
    def load_customer_receptions(self, customer_id):
        """بارگذاری پذیرش‌های یک مشتری"""
        try:
            self.reception_combo.clear()
            
            query = """
            SELECT r.id, r.reception_number, r.reception_date,
                   d.device_type, d.brand, d.model,
                   r.status
            FROM Receptions r
            JOIN Devices d ON r.device_id = d.id
            WHERE r.customer_id = ?
            ORDER BY r.reception_date DESC
            """
            
            receptions = self.data_manager.db.fetch_all(query, (customer_id,))
            
            self.reception_combo.addItem("-- انتخاب پذیرش --", None)
            
            for reception in receptions:
                reception_date = reception.get('reception_date', '')
                if reception_date:
                    jalali_date = self.data_manager.db.gregorian_to_jalali(reception_date)
                else:
                    jalali_date = '--'
                
                display_text = f"{reception['reception_number']} - {reception['device_type']} - {jalali_date}"
                self.reception_combo.addItem(display_text, reception['id'])
                
        except Exception as e:
            print(f"⚠️ خطا در بارگذاری پذیرش‌های مشتری: {e}")
    
    def load_reception_items(self, reception_id):
        """بارگذاری اقلام پذیرش"""
        try:
            self.clear_items_table()
            self.invoice_items = []
            
            query = """
            SELECT r.*, 
                p.first_name || ' ' || p.last_name as customer_name,
                d.device_type, d.brand, d.model
            FROM Receptions r
            JOIN Persons p ON r.customer_id = p.id
            JOIN Devices d ON r.device_id = d.id
            WHERE r.id = ?
            """
            
            reception = self.data_manager.db.fetch_one(query, (reception_id,))
            if not reception:
                QMessageBox.warning(self, "خطا", "پذیرش انتخاب شده یافت نشد!")
                return
            
            description = f"پذیرش شماره {reception['reception_number']} - "
            description += f"{reception['device_type']} {reception['brand']}"
            self.description_input.setPlainText(description)
            
            row_idx = 0
            total_items_amount = 0
            
            # بارگذاری خدمات
            query = """
            SELECT rs.*, sf.service_name, sf.category
            FROM Repair_Services rs
            JOIN ServiceFees sf ON rs.service_id = sf.id
            WHERE rs.repair_id IN (
                SELECT id FROM Repairs WHERE reception_id = ?
            )
            """
            
            services = self.data_manager.db.fetch_all(query, (reception_id,))
            
            for service in services:
                self.add_item_to_table(row_idx, service, 'خدمات')
                
                self.invoice_items.append({
                    'item_type': 'خدمات',
                    'item_id': service['service_id'],
                    'item_name': service.get('service_name', 'خدمات تعمیر'),
                    'quantity': service.get('quantity', 1),
                    'unit_price': service.get('unit_price', 0),
                    'total_price': service.get('total_price', 0),
                    'description': service.get('description', '')
                })
                
                total_items_amount += service.get('total_price', 0)
                row_idx += 1
            
            # بارگذاری قطعات
            query = """
            SELECT rp.*, p.part_name, p.part_code
            FROM Repair_Parts rp
            LEFT JOIN Parts p ON rp.part_id = p.id
            WHERE rp.repair_id IN (
                SELECT id FROM Repairs WHERE reception_id = ?
            )
            """
            
            parts = self.data_manager.db.fetch_all(query, (reception_id,))
            
            for part in parts:
                item_type = "قطعات نو" if part.get('warehouse_type') == 'قطعات نو' else "قطعات دست دوم"
                self.add_item_to_table(row_idx, part, item_type)
                
                part_name = part.get('part_name', 'قطعه')
                part_code = part.get('part_code', '')
                display_name = f"{part_name} ({part_code})" if part_code else part_name
                
                self.invoice_items.append({
                    'item_type': item_type,
                    'item_id': part['part_id'],
                    'item_name': display_name,
                    'quantity': part.get('quantity', 1),
                    'unit_price': part.get('unit_price', 0),
                    'total_price': part.get('total_price', 0),
                    'description': part.get('description', '')
                })
                
                total_items_amount += part.get('total_price', 0)
                row_idx += 1
            
            # هزینه اجرت
            query = """
            SELECT labor_cost, repair_description
            FROM Repairs 
            WHERE reception_id = ?
            """
            
            repairs = self.data_manager.db.fetch_all(query, (reception_id,))
            total_labor_cost = sum(repair.get('labor_cost', 0) for repair in repairs)
            
            if total_labor_cost > 0:
                labor_item = {
                    'item_name': 'هزینه اجرت تعمیر',
                    'unit_price': total_labor_cost,
                    'total_price': total_labor_cost,
                    'quantity': 1
                }
                
                self.add_item_to_table(row_idx, labor_item, 'اجرت')
                
                self.invoice_items.append({
                    'item_type': 'اجرت',
                    'item_id': None,
                    'item_name': 'هزینه اجرت تعمیر',
                    'quantity': 1,
                    'unit_price': total_labor_cost,
                    'total_price': total_labor_cost,
                    'description': 'هزینه اجرت تعمیرکار'
                })
                
                total_items_amount += total_labor_cost
                row_idx += 1
            
            self.items_count_label.setText(f"تعداد اقلام: {row_idx}")
            self.items_total_label.setText(f"جمع کل اقلام: {total_items_amount/10:,.0f} تومان")
            self.calculate_totals()
            
            print(f"✅ {row_idx} قلم از پذیرش بارگذاری شد.")
            
        except Exception as e:
            print(f"⚠️ خطا در بارگذاری اقلام پذیرش: {e}")
            QMessageBox.warning(self, "خطا", f"خطا در بارگذاری پذیرش:\n{str(e)}")
    
    def add_item_to_table(self, row_idx, item, item_type):
        """افزودن آیتم به جدول"""
        self.items_table.insertRow(row_idx)
        
        self.items_table.setItem(row_idx, 0,
            QTableWidgetItem(str(row_idx + 1)))
        
        self.items_table.setItem(row_idx, 1,
            QTableWidgetItem(item_type))
        
        item_name = item.get('item_name', item.get('service_name', item.get('part_name', 'آیتم')))
        self.items_table.setItem(row_idx, 2,
            QTableWidgetItem(item_name))
        
        quantity = item.get('quantity', 1)
        self.items_table.setItem(row_idx, 3,
            QTableWidgetItem(str(quantity)))
        
        unit_price = item.get('unit_price', 0)
        unit_toman = unit_price / 10
        self.items_table.setItem(row_idx, 4,
            QTableWidgetItem(f"{unit_toman:,.0f} تومان"))
        
        self.items_table.setItem(row_idx, 5,
            QTableWidgetItem("0%"))
        
        self.items_table.setItem(row_idx, 6,
            QTableWidgetItem("9%"))
        
        total_price = item.get('total_price', unit_price * quantity)
        total_toman = total_price / 10
        self.items_table.setItem(row_idx, 7,
            QTableWidgetItem(f"{total_toman:,.0f} تومان"))
    
    def add_service_item(self):
        """افزودن خدمت"""
        try:
            services = self.data_manager.service_fee.get_active_services()
            if not services:
                QMessageBox.information(self, "خدمات", "هیچ خدمتی تعریف نشده است.")
                return
            
            service_names = [f"{s['service_name']} ({s['default_fee']/10:,.0f} تومان)" for s in services]
            
            service_text, ok = QInputDialog.getItem(
                self, "انتخاب خدمت", 
                "خدمت مورد نظر را انتخاب کنید:", 
                service_names, 0, False
            )
            
            if not ok or not service_text:
                return
            
            selected_index = service_names.index(service_text)
            selected_service = services[selected_index]
            
            quantity, ok = QInputDialog.getDouble(
                self, "تعداد خدمت",
                f"تعداد خدمت '{selected_service['service_name']}' را وارد کنید:",
                1.0, 0.1, 100.0, 1
            )
            
            if not ok:
                return
            
            unit_price = selected_service['default_fee']
            total_price = unit_price * quantity
            
            row_idx = self.items_table.rowCount()
            self.add_item_to_table(row_idx, {
                'item_name': selected_service['service_name'],
                'unit_price': unit_price,
                'total_price': total_price,
                'quantity': quantity
            }, 'خدمات')
            
            self.invoice_items.append({
                'item_type': 'خدمات',
                'item_id': selected_service['id'],
                'item_name': selected_service['service_name'],
                'quantity': quantity,
                'unit_price': unit_price,
                'total_price': total_price,
                'description': selected_service.get('description', '')
            })
            
            self.items_count_label.setText(f"تعداد اقلام: {row_idx + 1}")
            self.calculate_totals()
            
            print(f"✅ خدمت '{selected_service['service_name']}' اضافه شد")
            
        except Exception as e:
            print(f"⚠️ خطا در افزودن خدمت: {e}")
            QMessageBox.warning(self, "خطا", f"خطا در افزودن خدمت:\n{str(e)}")
    
    def add_part_item(self):
        """افزودن قطعه"""
        QMessageBox.information(self, "افزودن قطعه", 
            "این بخش به زودی اضافه خواهد شد.")
    
    def remove_selected_item(self):
        """حذف آیتم انتخاب شده"""
        selected_row = self.items_table.currentRow()
        if selected_row < 0:
            QMessageBox.warning(self, "خطا", "لطفاً یک آیتم را انتخاب کنید.")
            return
        
        reply = QMessageBox.question(
            self, "تأیید حذف",
            "آیا مطمئن هستید که می‌خواهید این آیتم را حذف کنید؟",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.items_table.removeRow(selected_row)
            
            if selected_row < len(self.invoice_items):
                self.invoice_items.pop(selected_row)
            
            for row in range(self.items_table.rowCount()):
                self.items_table.setItem(row, 0,
                    QTableWidgetItem(str(row + 1)))
            
            self.items_count_label.setText(f"تعداد اقلام: {self.items_table.rowCount()}")
            self.calculate_totals()
            
            print("🗑️ آیتم حذف شد")
    
    def calculate_totals(self):
        """محاسبه مجموع‌های مالی"""
        try:
            items_total = sum(item.get('total_price', 0) for item in self.invoice_items)
            
            discount_percent = self.discount_spin.value()
            discount_amount = items_total * (discount_percent / 100)
            
            taxable_amount = items_total - discount_amount
            tax_percent = self.tax_spin.value()
            tax_amount = taxable_amount * (tax_percent / 100)
            
            total_amount = items_total - discount_amount + tax_amount
            
            self.update_amount_labels(
                items_total, discount_amount, tax_amount, 
                total_amount, 0, total_amount
            )
            
            table_total = 0
            for row in range(self.items_table.rowCount()):
                total_cell = self.items_table.item(row, 7)
                if total_cell:
                    text = total_cell.text().replace("تومان", "").replace(",", "").strip()
                    try:
                        table_total += float(text) * 10
                    except:
                        pass
            
            self.items_total_label.setText(f"جمع کل اقلام: {table_total/10:,.0f} تومان")
            
        except Exception as e:
            print(f"⚠️ خطا در محاسبه جمع‌ها: {e}")
    
    def update_amount_labels(self, subtotal, discount, tax, total, paid, remaining):
        """به‌روزرسانی برچسب‌های مبالغ"""
        subtotal_toman = subtotal / 10
        discount_toman = discount / 10
        tax_toman = tax / 10
        total_toman = total / 10
        paid_toman = paid / 10
        remaining_toman = remaining / 10
        
        self.subtotal_label.setText(f"{subtotal_toman:,.0f} تومان")
        self.discount_amount.setText(f"{discount_toman:,.0f} تومان")
        self.tax_amount.setText(f"{tax_toman:,.0f} تومان")
        self.total_label.setText(f"{total_toman:,.0f} تومان")
        
        self.payable_amount.setText(f"{total_toman:,.0f} تومان")
        self.paid_amount.setText(f"{paid_toman:,.0f} تومان")
        self.remaining_amount.setText(f"{remaining_toman:,.0f} تومان")
        
        summary_widgets = {
            'subtotal_summary': subtotal_toman,
            'discount_summary': discount_toman,
            'tax_summary': tax_toman,
            'payable_summary': total_toman,
            'paid_summary': paid_toman,
            'balance_summary': remaining_toman
        }
        
        for obj_name, amount in summary_widgets.items():
            widget = self.findChild(QLabel, obj_name)
            if widget:
                widget.setText(f"{amount:,.0f} تومان")
    
    def update_payment_amounts(self, total_paid):
        """به‌روزرسانی مبالغ پرداختی"""
        total_paid_toman = total_paid / 10
        
        total_label_text = self.total_label.text()
        total_amount = 0
        try:
            total_text = total_label_text.replace("تومان", "").replace(",", "").strip()
            total_amount = float(total_text) * 10
        except:
            total_amount = sum(item.get('total_price', 0) for item in self.invoice_items)
        
        remaining = total_amount - total_paid
        
        self.paid_amount.setText(f"{total_paid_toman:,.0f} تومان")
        self.remaining_amount.setText(f"{remaining/10:,.0f} تومان")
        
        paid_summary = self.findChild(QLabel, 'paid_summary')
        balance_summary = self.findChild(QLabel, 'balance_summary')
        
        if paid_summary:
            paid_summary.setText(f"{total_paid_toman:,.0f} تومان")
        if balance_summary:
            balance_summary.setText(f"{remaining/10:,.0f} تومان")
    
    def on_payment_status_changed(self, status):
        """هنگام تغییر وضعیت پرداخت"""
        print(f"🔄 وضعیت پرداخت تغییر کرد به: {status}")
    
    def record_payment(self, payment_type):
        """ثبت پرداخت"""
        if not self.current_invoice_id:
            QMessageBox.warning(self, "خطا", "لطفاً ابتدا یک فاکتور انتخاب کنید.")
            return
        
        try:
            from ui.forms.accounting.dialogs.payment_dialog import PaymentDialog
            dialog = PaymentDialog(self.data_manager, self.current_invoice_id, self)
            if dialog.exec():
                self.load_invoice_payments()
                self.calculate_totals()
                QMessageBox.information(self, "پرداخت", "✅ پرداخت با موفقیت ثبت شد.")
                
        except ImportError:
            QMessageBox.information(self, "ثبت پرداخت", 
                "فرم ثبت پرداخت به زودی اضافه خواهد شد.")
    
    def save_invoice(self):
        """ذخیره فاکتور"""
        try:
            if not self.validate_invoice_data():
                return
            
            invoice_data = self.get_invoice_data()
            
            if self.current_invoice_id:
                # بروزرسانی فاکتور موجود
                success, message = self.update_existing_invoice(invoice_data)
                if success:
                    QMessageBox.information(self, "ذخیره", message)
                    self.invoice_updated.emit(self.current_invoice_id)
                else:
                    QMessageBox.warning(self, "خطا", message)
            else:
                # ایجاد فاکتور جدید
                success, message = self.invoice_manager.create_invoice(invoice_data, self.invoice_items)
                if success:
                    QMessageBox.information(self, "ذخیره", message)
                    self.invoice_created.emit(self.current_invoice_id)
                else:
                    QMessageBox.warning(self, "خطا", message)
            
            self.load_invoice_list()
            self.data_changed.emit()
            
        except Exception as e:
            print(f"❌ خطا در ذخیره فاکتور: {e}")
            QMessageBox.critical(self, "خطا", 
                f"خطا در ذخیره فاکتور:\n\n{str(e)}")
    
    def validate_invoice_data(self):
        """اعتبارسنجی داده‌های فاکتور"""
        customer_id = self.customer_combo.currentData()
        if not customer_id:
            QMessageBox.warning(self, "اعتبارسنجی", "لطفاً یک مشتری انتخاب کنید.")
            return False
        
        if len(self.invoice_items) == 0:
            reply = QMessageBox.question(
                self, "فاقد اقلام",
                "فاکتور شما هیچ قلمی ندارد. آیا مطمئن هستید که می‌خواهید ادامه دهید؟",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            if reply == QMessageBox.No:
                return False
        
        return True
    
    def get_invoice_data(self):
        """دریافت داده‌های فرم فاکتور"""
        try:
            # دریافت تاریخ از ویجت شمسی
            invoice_date = self.get_widget_date(self.invoice_date)
            invoice_date_str = invoice_date.strftime("%Y/%m/%d")
            
            items_total = sum(item.get('total_price', 0) for item in self.invoice_items)
            discount_percent = self.discount_spin.value()
            discount_amount = items_total * (discount_percent / 100)
            tax_percent = self.tax_spin.value()
            tax_amount = (items_total - discount_amount) * (tax_percent / 100)
            total_amount = items_total - discount_amount + tax_amount
            
            return {
                'invoice_date': invoice_date_str,
                'invoice_type': self.invoice_type.currentText(),
                'customer_id': self.customer_combo.currentData(),
                'reception_id': self.reception_combo.currentData(),
                'payment_method': self.payment_status.currentText(),
                'payment_status': self.payment_status.currentText(),
                'subtotal': items_total,
                'discount': discount_amount,
                'tax': tax_amount,
                'total': total_amount,
                'paid_amount': 0,
                'remaining_amount': total_amount,
                'description': self.description_input.toPlainText().strip(),
                'tax_rate': tax_percent
            }
            
        except Exception as e:
            print(f"❌ خطا در دریافت داده‌های فاکتور: {e}")
            return None
    
    def update_existing_invoice(self, invoice_data):
        """بروزرسانی فاکتور موجود"""
        try:
            query = """
            UPDATE Invoices SET
                invoice_date = ?,
                invoice_type = ?,
                customer_id = ?,
                reception_id = ?,
                payment_method = ?,
                payment_status = ?,
                subtotal = ?,
                discount = ?,
                tax = ?,
                total = ?,
                remaining_amount = ?,
                description = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """
            
            params = (
                self.data_manager.db.jalali_to_gregorian(invoice_data['invoice_date']),
                invoice_data['invoice_type'],
                invoice_data['customer_id'],
                invoice_data['reception_id'],
                invoice_data['payment_method'],
                invoice_data['payment_status'],
                invoice_data['subtotal'],
                invoice_data['discount'],
                invoice_data['tax'],
                invoice_data['total'],
                invoice_data['remaining_amount'],
                invoice_data['description'],
                self.current_invoice_id
            )
            
            success = self.data_manager.db.execute_query(query, params)
            if not success:
                return False, "خطا در بروزرسانی فاکتور"
            
            # حذف اقلام قبلی
            delete_query = "DELETE FROM InvoiceItems WHERE invoice_id = ?"
            self.data_manager.db.execute_query(delete_query, (self.current_invoice_id,))
            
            # افزودن اقلام جدید
            for item in self.invoice_items:
                self.invoice_manager.add_invoice_item(self.current_invoice_id, item)
            
            return True, "✅ فاکتور با موفقیت بروزرسانی شد"
            
        except Exception as e:
            return False, f"خطا: {str(e)}"
    
    def cancel_edit(self):
        """لغو ویرایش"""
        reply = QMessageBox.question(
            self, "انصراف از ویرایش",
            "آیا مطمئن هستید که می‌خواهید تغییرات را لغو کنید؟\n\n"
            "تغییرات ذخیره نشده از بین خواهند رفت.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            if self.current_invoice_id:
                invoice = self.invoice_manager.get_invoice_by_id(self.current_invoice_id)
                self.load_invoice_details(invoice)
                self.load_invoice_items()
            else:
                self.set_new_invoice_mode()
    
    def create_new_invoice(self):
        """ایجاد فاکتور جدید"""
        self.set_new_invoice_mode()
        self.detail_tabs.setCurrentIndex(0)
        print("📄 فاکتور جدید آماده است")
    
    def refresh_data(self):
        """بروزرسانی داده‌ها"""
        self.load_customers()
        self.load_receptions()
        self.load_invoice_list()
        self.calculate_totals()
        
        QMessageBox.information(self, "بروزرسانی", 
            "✅ داده‌های فاکتور بروزرسانی شدند.")
    
    def print_invoice(self):
        """چاپ فاکتور"""
        if not self.current_invoice_id:
            QMessageBox.warning(self, "چاپ", "لطفاً ابتدا یک فاکتور انتخاب کنید.")
            return
        
        QMessageBox.information(self, "چاپ فاکتور", 
            "این قابلیت به زودی اضافه خواهد شد.")
    
    def export_invoice(self):
        """خروجی PDF فاکتور"""
        if not self.current_invoice_id:
            QMessageBox.warning(self, "خروجی", "لطفاً ابتدا یک فاکتور انتخاب کنید.")
            return
        
        QMessageBox.information(self, "خروجی PDF", 
            "این قابلیت به زودی اضافه خواهد شد.")


class CustomerSelectionDialog(QDialog):
    """دیالوگ انتخاب مشتری"""
    
    def __init__(self, data_manager, parent=None):
        super().__init__(parent)
        self.data_manager = data_manager
        self.selected_customer = None
        
        self.setWindowTitle("انتخاب مشتری")
        self.setMinimumSize(800, 600)
        self.setLayoutDirection(Qt.RightToLeft)
        
        self.init_ui()
        self.load_customers()
    
    def init_ui(self):
        """ایجاد رابط کاربری"""
        layout = QVBoxLayout(self)
        
        search_layout = QHBoxLayout()
        search_label = QLabel("جستجو:")
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("نام، نام خانوادگی، موبایل...")
        self.search_input.textChanged.connect(self.filter_customers)
        
        search_btn = QPushButton("🔍 جستجو")
        search_btn.clicked.connect(self.search_customers)
        
        search_layout.addWidget(search_label)
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(search_btn)
        
        layout.addLayout(search_layout)
        
        self.customers_table = QTableWidget()
        self.customers_table.setColumnCount(6)
        self.customers_table.setHorizontalHeaderLabels([
            "کد مشتری", "نام و نام خانوادگی", "موبایل", 
            "تلفن", "آدرس", "تاریخ ثبت"
        ])
        
        self.customers_table.setAlternatingRowColors(True)
        self.customers_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.customers_table.setSelectionMode(QTableWidget.SingleSelection)
        self.customers_table.setEditTriggers(QTableWidget.NoEditTriggers)
        
        header = self.customers_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
        
        layout.addWidget(self.customers_table)
        
        button_layout = QHBoxLayout()
        
        select_btn = QPushButton("✅ انتخاب مشتری")
        select_btn.clicked.connect(self.select_customer)
        
        cancel_btn = QPushButton("❌ انصراف")
        cancel_btn.clicked.connect(self.reject)
        
        button_layout.addWidget(select_btn)
        button_layout.addStretch()
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
    
    def load_customers(self):
        """بارگذاری لیست مشتریان"""
        try:
            query = """
            SELECT 
                id, first_name, last_name, mobile, phone, 
                address, registration_date
            FROM Persons 
            WHERE person_type = 'مشتری'
            ORDER BY last_name, first_name
            """
            
            customers = self.data_manager.db.fetch_all(query)
            self.display_customers(customers)
            
        except Exception as e:
            QMessageBox.critical(self, "خطا", f"خطا در بارگذاری مشتریان:\n{str(e)}")
    
    def display_customers(self, customers):
        """نمایش مشتریان در جدول"""
        self.customers_table.setRowCount(len(customers))
        
        for row_idx, customer in enumerate(customers):
            self.customers_table.setItem(row_idx, 0,
                QTableWidgetItem(str(customer.get('id', ''))))
            
            full_name = f"{customer.get('first_name', '')} {customer.get('last_name', '')}"
            self.customers_table.setItem(row_idx, 1,
                QTableWidgetItem(full_name.strip()))
            
            self.customers_table.setItem(row_idx, 2,
                QTableWidgetItem(customer.get('mobile', '')))
            
            self.customers_table.setItem(row_idx, 3,
                QTableWidgetItem(customer.get('phone', '')))
            
            address = customer.get('address', '')
            if len(address) > 50:
                address = address[:47] + "..."
            self.customers_table.setItem(row_idx, 4,
                QTableWidgetItem(address))
            
            reg_date = customer.get('registration_date', '')
            if reg_date:
                jalali_date = self.data_manager.db.gregorian_to_jalali(reg_date)
                self.customers_table.setItem(row_idx, 5,
                    QTableWidgetItem(jalali_date))
            else:
                self.customers_table.setItem(row_idx, 5,
                    QTableWidgetItem("--"))
    
    def filter_customers(self):
        """فیلتر کردن مشتریان"""
        search_text = self.search_input.text().strip().lower()
        
        for row in range(self.customers_table.rowCount()):
            show_row = False
            
            for col in range(self.customers_table.columnCount()):
                item = self.customers_table.item(row, col)
                if item and search_text in item.text().lower():
                    show_row = True
                    break
            
            self.customers_table.setRowHidden(row, not show_row)
    
    def search_customers(self):
        """جستجوی مشتریان"""
        search_text = self.search_input.text().strip()
        if not search_text:
            self.load_customers()
            return
        
        try:
            query = """
            SELECT 
                id, first_name, last_name, mobile, phone, 
                address, registration_date
            FROM Persons 
            WHERE person_type = 'مشتری'
                AND (first_name LIKE ? OR last_name LIKE ? 
                     OR mobile LIKE ? OR phone LIKE ? 
                     OR address LIKE ? OR national_id LIKE ?)
            ORDER BY last_name, first_name
            """
            
            search_term = f"%{search_text}%"
            customers = self.data_manager.db.fetch_all(query, 
                (search_term, search_term, search_term, 
                 search_term, search_term, search_term))
            
            self.display_customers(customers)
            
            if len(customers) == 0:
                QMessageBox.information(self, "جستجو", 
                    "هیچ مشتری با مشخصات وارد شده یافت نشد.")
                
        except Exception as e:
            QMessageBox.critical(self, "خطا", f"خطا در جستجو:\n{str(e)}")
    
    def select_customer(self):
        """انتخاب مشتری"""
        selected_row = self.customers_table.currentRow()
        if selected_row < 0:
            QMessageBox.warning(self, "خطا", "لطفاً یک مشتری را انتخاب کنید.")
            return
        
        try:
            customer_id_item = self.customers_table.item(selected_row, 0)
            if not customer_id_item:
                return
            
            customer_id = int(customer_id_item.text())
            
            query = "SELECT * FROM Persons WHERE id = ?"
            customer = self.data_manager.db.fetch_one(query, (customer_id,))
            
            if customer:
                self.selected_customer = customer
                self.accept()
            else:
                QMessageBox.warning(self, "خطا", "مشتری یافت نشد.")
                
        except Exception as e:
            QMessageBox.critical(self, "خطا", f"خطا در انتخاب مشتری:\n{str(e)}")
    
    def get_selected_customer(self):
        """دریافت مشتری انتخاب شده"""
        return self.selected_customer


class ReceptionSelectionDialog(QDialog):
    """دیالوگ انتخاب پذیرش"""
    
    def __init__(self, data_manager, parent=None):
        super().__init__(parent)
        self.data_manager = data_manager
        self.selected_reception = None
        
        self.setWindowTitle("انتخاب پذیرش")
        self.setMinimumSize(1000, 700)
        self.setLayoutDirection(Qt.RightToLeft)
        
        self.init_ui()
        self.load_receptions()
    
    def init_ui(self):
        """ایجاد رابط کاربری"""
        layout = QVBoxLayout(self)
        
        filter_layout = QHBoxLayout()
        
        status_label = QLabel("وضعیت:")
        self.status_combo = QComboBox()
        self.status_combo.addItems([
            "همه", "در انتظار", "تعمیر شده", 
            "تحویل داده شده", "لغو شده"
        ])
        self.status_combo.currentIndexChanged.connect(self.filter_receptions)
        
        date_label = QLabel("از تاریخ:")
        self.date_from = QLineEdit(jdatetime.date.today().strftime("%Y/%m/%d"))
        self.date_from.setReadOnly(True)
        
        to_label = QLabel("تا تاریخ:")
        self.date_to = QLineEdit(jdatetime.date.today().strftime("%Y/%m/%d"))
        self.date_to.setReadOnly(True)
        
        filter_btn = QPushButton("🔍 فیلتر")
        filter_btn.clicked.connect(self.filter_receptions)
        
        filter_layout.addWidget(status_label)
        filter_layout.addWidget(self.status_combo)
        filter_layout.addStretch()
        filter_layout.addWidget(date_label)
        filter_layout.addWidget(self.date_from)
        filter_layout.addWidget(to_label)
        filter_layout.addWidget(self.date_to)
        filter_layout.addWidget(filter_btn)
        
        layout.addLayout(filter_layout)
        
        search_layout = QHBoxLayout()
        search_label = QLabel("جستجو:")
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("شماره پذیرش، نام مشتری، دستگاه...")
        self.search_input.textChanged.connect(self.search_receptions)
        
        search_btn = QPushButton("جستجو")
        search_btn.clicked.connect(self.search_receptions)
        
        search_layout.addWidget(search_label)
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(search_btn)
        
        layout.addLayout(search_layout)
        
        self.receptions_table = QTableWidget()
        self.receptions_table.setColumnCount(8)
        self.receptions_table.setHorizontalHeaderLabels([
            "شماره پذیرش", "مشتری", "دستگاه", "مدل", 
            "تاریخ پذیرش", "وضعیت", "هزینه برآوردی", "توضیحات مشکل"
        ])
        
        self.receptions_table.setAlternatingRowColors(True)
        self.receptions_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.receptions_table.setSelectionMode(QTableWidget.SingleSelection)
        self.receptions_table.setEditTriggers(QTableWidget.NoEditTriggers)
        
        header = self.receptions_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
        
        layout.addWidget(self.receptions_table)
        
        button_layout = QHBoxLayout()
        
        select_btn = QPushButton("✅ انتخاب پذیرش")
        select_btn.clicked.connect(self.select_reception)
        
        cancel_btn = QPushButton("❌ انصراف")
        cancel_btn.clicked.connect(self.reject)
        
        button_layout.addWidget(select_btn)
        button_layout.addStretch()
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
    
    def load_receptions(self):
        """بارگذاری لیست پذیرش‌ها"""
        try:
            query = """
            SELECT 
                r.id,
                r.reception_number,
                r.reception_date,
                r.status,
                r.estimated_cost,
                r.problem_description,
                p.first_name || ' ' || p.last_name as customer_name,
                d.device_type,
                d.brand,
                d.model
            FROM Receptions r
            JOIN Persons p ON r.customer_id = p.id
            JOIN Devices d ON r.device_id = d.id
            WHERE r.status IN ('تعمیر شده', 'تحویل داده شده')
            ORDER BY r.reception_date DESC
            LIMIT 100
            """
            
            receptions = self.data_manager.db.fetch_all(query)
            self.display_receptions(receptions)
            
        except Exception as e:
            QMessageBox.critical(self, "خطا", f"خطا در بارگذاری پذیرش‌ها:\n{str(e)}")
    
    def display_receptions(self, receptions):
        """نمایش پذیرش‌ها در جدول"""
        self.receptions_table.setRowCount(len(receptions))
        
        for row_idx, reception in enumerate(receptions):
            self.receptions_table.setItem(row_idx, 0,
                QTableWidgetItem(reception.get('reception_number', '')))
            
            self.receptions_table.setItem(row_idx, 1,
                QTableWidgetItem(reception.get('customer_name', '--')))
            
            device_text = f"{reception.get('device_type', '')} - {reception.get('brand', '')}"
            self.receptions_table.setItem(row_idx, 2,
                QTableWidgetItem(device_text))
            
            self.receptions_table.setItem(row_idx, 3,
                QTableWidgetItem(reception.get('model', '--')))
            
            reception_date = reception.get('reception_date', '')
            if reception_date:
                jalali_date = self.data_manager.db.gregorian_to_jalali(reception_date)
                self.receptions_table.setItem(row_idx, 4,
                    QTableWidgetItem(jalali_date))
            else:
                self.receptions_table.setItem(row_idx, 4,
                    QTableWidgetItem("--"))
            
            status = reception.get('status', '')
            status_item = QTableWidgetItem(status)
            
            if status == 'تعمیر شده':
                status_item.setForeground(QBrush(QColor("#27ae60")))
            elif status == 'تحویل داده شده':
                status_item.setForeground(QBrush(QColor("#3498db")))
            elif status == 'در انتظار':
                status_item.setForeground(QBrush(QColor("#f39c12")))
            elif status == 'لغو شده':
                status_item.setForeground(QBrush(QColor("#e74c3c")))
                
            self.receptions_table.setItem(row_idx, 5, status_item)
            
            estimated_cost = reception.get('estimated_cost', 0)
            estimated_toman = estimated_cost / 10
            self.receptions_table.setItem(row_idx, 6,
                QTableWidgetItem(f"{estimated_toman:,.0f} تومان"))
            
            problem_desc = reception.get('problem_description', '')
            if len(problem_desc) > 50:
                problem_desc = problem_desc[:47] + "..."
            self.receptions_table.setItem(row_idx, 7,
                QTableWidgetItem(problem_desc))
    
    def filter_receptions(self):
        """فیلتر کردن پذیرش‌ها"""
        status = self.status_combo.currentText()
        date_from = self.date_from.text()
        date_to = self.date_to.text()
        
        try:
            if status == "همه":
                query = """
                SELECT 
                    r.id,
                    r.reception_number,
                    r.reception_date,
                    r.status,
                    r.estimated_cost,
                    r.problem_description,
                    p.first_name || ' ' || p.last_name as customer_name,
                    d.device_type,
                    d.brand,
                    d.model
                FROM Receptions r
                JOIN Persons p ON r.customer_id = p.id
                JOIN Devices d ON r.device_id = d.id
                WHERE DATE(r.reception_date) BETWEEN ? AND ?
                ORDER BY r.reception_date DESC
                """
                params = (
                    self.data_manager.db.jalali_to_gregorian(date_from),
                    self.data_manager.db.jalali_to_gregorian(date_to)
                )
            else:
                query = """
                SELECT 
                    r.id,
                    r.reception_number,
                    r.reception_date,
                    r.status,
                    r.estimated_cost,
                    r.problem_description,
                    p.first_name || ' ' || p.last_name as customer_name,
                    d.device_type,
                    d.brand,
                    d.model
                FROM Receptions r
                JOIN Persons p ON r.customer_id = p.id
                JOIN Devices d ON r.device_id = d.id
                WHERE r.status = ? AND DATE(r.reception_date) BETWEEN ? AND ?
                ORDER BY r.reception_date DESC
                """
                params = (
                    status,
                    self.data_manager.db.jalali_to_gregorian(date_from),
                    self.data_manager.db.jalali_to_gregorian(date_to)
                )
            
            receptions = self.data_manager.db.fetch_all(query, params)
            self.display_receptions(receptions)
            
        except Exception as e:
            print(f"⚠️ خطا در فیلتر پذیرش‌ها: {e}")
            QMessageBox.warning(self, "خطا", f"خطا در فیلتر پذیرش‌ها:\n{str(e)}")
    
    def search_receptions(self):
        """جستجوی پذیرش‌ها"""
        search_text = self.search_input.text().strip()
        if not search_text:
            self.load_receptions()
            return
        
        try:
            query = """
            SELECT 
                r.id,
                r.reception_number,
                r.reception_date,
                r.status,
                r.estimated_cost,
                r.problem_description,
                p.first_name || ' ' || p.last_name as customer_name,
                d.device_type,
                d.brand,
                d.model
            FROM Receptions r
            JOIN Persons p ON r.customer_id = p.id
            JOIN Devices d ON r.device_id = d.id
            WHERE r.reception_number LIKE ? 
               OR p.first_name LIKE ? 
               OR p.last_name LIKE ? 
               OR d.device_type LIKE ? 
               OR d.brand LIKE ? 
               OR d.model LIKE ?
            ORDER BY r.reception_date DESC
            """
            
            search_term = f"%{search_text}%"
            params = (search_term, search_term, search_term, 
                     search_term, search_term, search_term)
            
            receptions = self.data_manager.db.fetch_all(query, params)
            self.display_receptions(receptions)
            
            if len(receptions) == 0:
                QMessageBox.information(self, "جستجو", 
                    "هیچ پذیرش با مشخصات وارد شده یافت نشد.")
                
        except Exception as e:
            QMessageBox.critical(self, "خطا", f"خطا در جستجو:\n{str(e)}")
    
    def select_reception(self):
        """انتخاب پذیرش"""
        selected_row = self.receptions_table.currentRow()
        if selected_row < 0:
            QMessageBox.warning(self, "خطا", "لطفاً یک پذیرش را انتخاب کنید.")
            return
        
        try:
            reception_number_item = self.receptions_table.item(selected_row, 0)
            if not reception_number_item:
                return
            
            reception_number = reception_number_item.text()
            
            query = """
            SELECT 
                r.*,
                p.first_name || ' ' || p.last_name as customer_name,
                p.mobile,
                p.phone,
                p.address,
                d.device_type,
                d.brand,
                d.model,
                d.serial_number
            FROM Receptions r
            JOIN Persons p ON r.customer_id = p.id
            JOIN Devices d ON r.device_id = d.id
            WHERE r.reception_number = ?
            """
            
            reception = self.data_manager.db.fetch_one(query, (reception_number,))
            
            if reception:
                self.selected_reception = reception
                self.accept()
            else:
                QMessageBox.warning(self, "خطا", "پذیرش یافت نشد.")
                
        except Exception as e:
            QMessageBox.critical(self, "خطا", f"خطا در انتخاب پذیرش:\n{str(e)}")
    
    def get_selected_reception(self):
        """دریافت پذیرش انتخاب شده"""
        return self.selected_reception


class PaymentDialog(QDialog):
    """دیالوگ ثبت پرداخت"""
    
    def __init__(self, data_manager, invoice_id, parent=None):
        super().__init__(parent)
        self.data_manager = data_manager
        self.invoice_id = invoice_id
        self.invoice_manager = self.data_manager.invoice_manager
        
        self.setWindowTitle("ثبت پرداخت فاکتور")
        self.setMinimumSize(600, 500)
        self.setLayoutDirection(Qt.RightToLeft)
        
        self.init_ui()
        self.load_invoice_info()
    
    def init_ui(self):
        """ایجاد رابط کاربری"""
        layout = QVBoxLayout(self)
        
        info_group = QGroupBox("اطلاعات فاکتور")
        info_layout = QVBoxLayout(info_group)
        
        self.invoice_info_label = QLabel("در حال بارگذاری...")
        info_layout.addWidget(self.invoice_info_label)
        
        layout.addWidget(info_group)
        
        amount_group = QGroupBox("مبلغ پرداختی")
        amount_layout = QVBoxLayout(amount_group)
        
        amount_info_layout = QHBoxLayout()
        payable_label = QLabel("مبلغ قابل پرداخت:")
        self.payable_amount = QLabel("0 تومان")
        
        amount_info_layout.addWidget(payable_label)
        amount_info_layout.addWidget(self.payable_amount)
        amount_info_layout.addStretch()
        
        amount_layout.addLayout(amount_info_layout)
        
        payment_layout = QHBoxLayout()
        payment_label = QLabel("مبلغ پرداختی:")
        self.payment_spin = QDoubleSpinBox()
        self.payment_spin.setRange(0, 1000000000)
        self.payment_spin.setValue(0)
        self.payment_spin.setSuffix(" تومان")
        self.payment_spin.setSingleStep(10000)
        self.payment_spin.valueChanged.connect(self.calculate_remaining)
        
        payment_layout.addWidget(payment_label)
        payment_layout.addWidget(self.payment_spin)
        payment_layout.addStretch()
        
        amount_layout.addLayout(payment_layout)
        
        remaining_layout = QHBoxLayout()
        remaining_label = QLabel("مانده حساب:")
        self.remaining_amount = QLabel("0 تومان")
        
        remaining_layout.addWidget(remaining_label)
        remaining_layout.addWidget(self.remaining_amount)
        remaining_layout.addStretch()
        
        amount_layout.addLayout(remaining_layout)
        
        layout.addWidget(amount_group)
        
        method_group = QGroupBox("روش پرداخت")
        method_layout = QVBoxLayout(method_group)
        
        self.payment_method_combo = QComboBox()
        self.payment_method_combo.addItems(["نقدی", "کارت", "چک", "انتقال بانکی"])
        
        method_layout.addWidget(self.payment_method_combo)
        
        layout.addWidget(method_group)
        
        desc_group = QGroupBox("توضیحات")
        desc_layout = QVBoxLayout(desc_group)
        
        self.description_input = QTextEdit()
        self.description_input.setMaximumHeight(80)
        self.description_input.setPlaceholderText("توضیحات پرداخت...")
        
        desc_layout.addWidget(self.description_input)
        
        layout.addWidget(desc_group)
        
        button_layout = QHBoxLayout()
        
        self.record_btn = QPushButton("💾 ثبت پرداخت")
        self.record_btn.clicked.connect(self.record_payment)
        
        cancel_btn = QPushButton("❌ انصراف")
        cancel_btn.clicked.connect(self.reject)
        
        button_layout.addWidget(self.record_btn)
        button_layout.addStretch()
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
    
    def load_invoice_info(self):
        """بارگذاری اطلاعات فاکتور"""
        try:
            invoice = self.invoice_manager.get_invoice_by_id(self.invoice_id)
            
            if invoice:
                total_toman = invoice.get('total_toman', 0)
                paid_toman = invoice.get('paid_amount_toman', 0)
                remaining_toman = invoice.get('remaining_amount_toman', 0)
                
                self.invoice_info_label.setText(
                    f"فاکتور شماره: {invoice.get('invoice_number', '--')} | "
                    f"مبلغ کل: {total_toman:,.0f} تومان | "
                    f"پرداخت شده: {paid_toman:,.0f} تومان"
                )
                
                self.payable_amount.setText(f"{remaining_toman:,.0f} تومان")
                self.payment_spin.setValue(remaining_toman)
                self.payment_spin.setMaximum(remaining_toman)
                
                self.calculate_remaining()
                
        except Exception as e:
            print(f"⚠️ خطا در بارگذاری اطلاعات فاکتور: {e}")
    
    def calculate_remaining(self):
        """محاسبه مانده"""
        try:
            payable_text = self.payable_amount.text()
            payable = float(payable_text.replace("تومان", "").replace(",", "").strip())
            
            payment_amount = self.payment_spin.value()
            remaining = payable - payment_amount
            
            self.remaining_amount.setText(f"{remaining:,.0f} تومان")
            
            if remaining < 0:
                self.record_btn.setEnabled(False)
            else:
                self.record_btn.setEnabled(True)
                
        except:
            self.remaining_amount.setText("0 تومان")
    
    def record_payment(self):
        """ثبت پرداخت"""
        try:
            payment_amount = self.payment_spin.value()
            if payment_amount <= 0:
                QMessageBox.warning(self, "خطا", "مبلغ پرداختی باید بزرگتر از صفر باشد.")
                return
            
            method = self.payment_method_combo.currentText()
            
            reply = QMessageBox.question(
                self, "تأیید پرداخت",
                f"آیا از ثبت پرداخت به مبلغ {payment_amount:,.0f} تومان مطمئن هستید؟",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply != QMessageBox.Yes:
                return
            
            payment_data = {
                'amount': payment_amount,
                'payment_method': method,
                'description': self.description_input.toPlainText().strip()
            }
            
            success, message = self.invoice_manager.update_invoice_payment(
                self.invoice_id, payment_data
            )
            
            if success:
                QMessageBox.information(self, "ثبت پرداخت", message)
                self.accept()
            else:
                QMessageBox.critical(self, "خطا", message)
                
        except Exception as e:
            QMessageBox.critical(self, "خطا", f"خطا در ثبت پرداخت:\n{str(e)}")