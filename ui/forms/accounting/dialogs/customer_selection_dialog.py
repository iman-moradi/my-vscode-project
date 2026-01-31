"""
دیالوگ انتخاب مشتری برای فاکتور
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QLineEdit,
    QMessageBox, QAbstractItemView, QGroupBox, QRadioButton,
    QButtonGroup, QDialogButtonBox
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QBrush, QColor


class CustomerSelectionDialog(QDialog):
    """دیالوگ انتخاب مشتری از لیست مشتریان"""
    
    customer_selected = Signal(dict)  # ارسال اطلاعات مشتری انتخاب شده
    
    def __init__(self, data_manager, parent=None):
        super().__init__(parent)
        self.data_manager = data_manager
        self.selected_customer = None
        
        # تنظیمات پنجره
        self.setWindowTitle("انتخاب مشتری")
        self.setMinimumSize(800, 600)
        self.setLayoutDirection(Qt.RightToLeft)
        
        # استایل
        self.setStyleSheet("""
            QDialog {
                background-color: #000000;
                color: #ffffff;
                font-family: 'B Nazanin';
            }
            QTableWidget {
                background-color: #111111;
                alternate-background-color: #0a0a0a;
                gridline-color: #333;
                color: #ffffff;
            }
            QHeaderView::section {
                background-color: #2c3e50;
                color: white;
                padding: 8px;
                border: none;
            }
            QLineEdit {
                background-color: #222222;
                border: 1px solid #333;
                color: white;
                padding: 8px;
                border-radius: 4px;
            }
            QPushButton {
                background-color: #2c3e50;
                color: white;
                padding: 8px 15px;
                border-radius: 4px;
                border: none;
            }
            QPushButton:hover {
                background-color: #34495e;
            }
        """)
        
        self.init_ui()
        self.load_customers()
    
    def init_ui(self):
        """ایجاد رابط کاربری"""
        layout = QVBoxLayout(self)
        
        # نوار جستجو
        search_layout = QHBoxLayout()
        search_label = QLabel("جستجو:")
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("نام، نام خانوادگی، موبایل، کد ملی...")
        self.search_input.textChanged.connect(self.filter_customers)
        
        search_btn = QPushButton("🔍 جستجو")
        search_btn.clicked.connect(self.search_customers)
        
        search_layout.addWidget(search_label)
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(search_btn)
        
        layout.addLayout(search_layout)
        
        # جدول مشتریان
        self.customers_table = QTableWidget()
        self.customers_table.setColumnCount(6)
        self.customers_table.setHorizontalHeaderLabels([
            "کد مشتری",
            "نام و نام خانوادگی",
            "موبایل",
            "تلفن",
            "آدرس",
            "تاریخ ثبت"
        ])
        
        self.customers_table.setAlternatingRowColors(True)
        self.customers_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.customers_table.setSelectionMode(QTableWidget.SingleSelection)
        self.customers_table.setEditTriggers(QTableWidget.NoEditTriggers)
        
        header = self.customers_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
        
        layout.addWidget(self.customers_table)
        
        # دکمه‌ها
        button_layout = QHBoxLayout()
        
        select_btn = QPushButton("✅ انتخاب مشتری")
        select_btn.setStyleSheet("background-color: #27ae60;")
        select_btn.clicked.connect(self.select_customer)
        
        cancel_btn = QPushButton("❌ انصراف")
        cancel_btn.setStyleSheet("background-color: #e74c3c;")
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
                id, 
                first_name, 
                last_name, 
                mobile, 
                phone, 
                address, 
                registration_date
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
            # کد مشتری
            self.customers_table.setItem(row_idx, 0,
                QTableWidgetItem(str(customer.get('id', ''))))
            
            # نام و نام خانوادگی
            full_name = f"{customer.get('first_name', '')} {customer.get('last_name', '')}"
            self.customers_table.setItem(row_idx, 1,
                QTableWidgetItem(full_name.strip()))
            
            # موبایل
            self.customers_table.setItem(row_idx, 2,
                QTableWidgetItem(customer.get('mobile', '')))
            
            # تلفن
            self.customers_table.setItem(row_idx, 3,
                QTableWidgetItem(customer.get('phone', '')))
            
            # آدرس
            address = customer.get('address', '')
            if len(address) > 50:
                address = address[:47] + "..."
            self.customers_table.setItem(row_idx, 4,
                QTableWidgetItem(address))
            
            # تاریخ ثبت
            reg_date = customer.get('registration_date', '')
            if reg_date:
                # تبدیل به تاریخ شمسی
                jalali_date = self.data_manager.db.gregorian_to_jalali(reg_date)
                self.customers_table.setItem(row_idx, 5,
                    QTableWidgetItem(jalali_date))
            else:
                self.customers_table.setItem(row_idx, 5,
                    QTableWidgetItem("--"))
    
    def filter_customers(self):
        """فیلتر کردن مشتریان بر اساس متن جستجو"""
        search_text = self.search_input.text().strip().lower()
        
        for row in range(self.customers_table.rowCount()):
            show_row = False
            
            # بررسی تمام ستون‌ها برای تطابق
            for col in range(self.customers_table.columnCount()):
                item = self.customers_table.item(row, col)
                if item and search_text in item.text().lower():
                    show_row = True
                    break
            
            self.customers_table.setRowHidden(row, not show_row)
    
    def search_customers(self):
        """جستجوی پیشرفته مشتریان"""
        search_text = self.search_input.text().strip()
        if not search_text:
            self.load_customers()
            return
        
        try:
            query = """
            SELECT 
                id, 
                first_name, 
                last_name, 
                mobile, 
                phone, 
                address, 
                registration_date
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
        """انتخاب مشتری از جدول"""
        selected_row = self.customers_table.currentRow()
        if selected_row < 0:
            QMessageBox.warning(self, "خطا", "لطفاً یک مشتری را انتخاب کنید.")
            return
        
        try:
            # دریافت کد مشتری
            customer_id_item = self.customers_table.item(selected_row, 0)
            if not customer_id_item:
                return
            
            customer_id = int(customer_id_item.text())
            
            # دریافت اطلاعات کامل مشتری
            query = """
            SELECT * FROM Persons WHERE id = ?
            """
            customer = self.data_manager.db.fetch_one(query, (customer_id,))
            
            if customer:
                self.selected_customer = customer
                self.customer_selected.emit(customer)
                self.accept()
            else:
                QMessageBox.warning(self, "خطا", "مشتری یافت نشد.")
                
        except Exception as e:
            QMessageBox.critical(self, "خطا", f"خطا در انتخاب مشتری:\n{str(e)}")
    
    def get_selected_customer(self):
        """دریافت مشتری انتخاب شده"""
        return self.selected_customer