"""
دیالوگ انتخاب پذیرش برای فاکتور
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QLineEdit,
    QMessageBox, QComboBox, QDateEdit, QGroupBox, QWidget,
    QRadioButton, QButtonGroup, QDialogButtonBox, QSpinBox
)
from PySide6.QtCore import Qt, Signal, QDate
from PySide6.QtGui import QBrush, QColor
import jdatetime


# ایمپورت ویجت تاریخ شمسی جدید (کلیک روی فیلد)
try:
    from utils.jalali_date_widget import JalaliDateWidget as JalaliDatePicker
    JALALI_DATE_AVAILABLE = True
    print("✅ ویجت تاریخ شمسی (کلیک روی فیلد) در دیالوگ بارگذاری شد")
except ImportError as e:
    print(f"⚠️ خطا در بارگذاری ویجت تاریخ شمسی در دیالوگ: {e}")
    JALALI_DATE_AVAILABLE = False
    # کلاس جایگزین ساده
    class JalaliDatePicker(QWidget):
        def __init__(self, parent=None):
            super().__init__(parent)
            self.current_date = jdatetime.date.today()
            layout = QVBoxLayout(self)
            self.date_display = QLineEdit(str(self.current_date))
            layout.addWidget(self.date_display)
        def set_date(self, date): self.current_date = date
        def get_date(self): return self.current_date



class ReceptionSelectionDialog(QDialog):
    """دیالوگ انتخاب پذیرش از لیست پذیرش‌ها"""
    
    reception_selected = Signal(dict)  # ارسال اطلاعات پذیرش انتخاب شده
    
    def __init__(self, data_manager, parent=None):
        super().__init__(parent)
        self.data_manager = data_manager
        self.selected_reception = None
        
        # تنظیمات پنجره
        self.setWindowTitle("انتخاب پذیرش")
        self.setMinimumSize(1000, 700)
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
            QLineEdit, QComboBox {
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
        self.load_receptions()
    
    def init_ui(self):
        """ایجاد رابط کاربری"""
        layout = QVBoxLayout(self)
        
        # فیلترها
        filter_group = QGroupBox("فیلتر پذیرش‌ها")
        filter_layout = QVBoxLayout(filter_group)
        
        # فیلتر وضعیت
        status_layout = QHBoxLayout()
        status_label = QLabel("وضعیت:")
        self.status_combo = QComboBox()
        self.status_combo.addItems([
            "همه",
            "در انتظار",
            "تعمیر شده",
            "تحویل داده شده",
            "لغو شده"
        ])
        self.status_combo.currentIndexChanged.connect(self.filter_receptions)
        
        status_layout.addWidget(status_label)
        status_layout.addWidget(self.status_combo)
        status_layout.addStretch()
        
        # فیلتر تاریخ - استفاده از ویجت تاریخ شمسی یکپارچه
        date_layout = QHBoxLayout()
        date_label = QLabel("از تاریخ:")
        
        # استفاده از ویجت تاریخ شمسی
        self.date_from = JalaliDatePicker()
        self.date_to = JalaliDatePicker()
        
        # تنظیم تاریخ پیش‌فرض (30 روز گذشته تا امروز)
        today_jalali = jdatetime.date.today()
        date_30_days_ago = today_jalali - jdatetime.timedelta(days=30)
        
        self.date_from.set_date(date_30_days_ago)
        self.date_to.set_date(today_jalali)
        
        to_label = QLabel("تا تاریخ:")
        
        filter_btn = QPushButton("🔍 فیلتر")
        filter_btn.clicked.connect(self.filter_receptions)
        
        date_layout.addWidget(date_label)
        date_layout.addWidget(self.date_from)
        date_layout.addWidget(to_label)
        date_layout.addWidget(self.date_to)
        date_layout.addWidget(filter_btn)
        
        filter_layout.addLayout(status_layout)
        filter_layout.addLayout(date_layout)
        layout.addWidget(filter_group)
            
        # جستجوی متن
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
        
        # جدول پذیرش‌ها
        self.receptions_table = QTableWidget()
        self.receptions_table.setColumnCount(8)
        self.receptions_table.setHorizontalHeaderLabels([
            "شماره پذیرش",
            "مشتری",
            "دستگاه",
            "مدل",
            "تاریخ پذیرش",
            "وضعیت",
            "هزینه برآوردی",
            "توضیحات مشکل"
        ])
        
        self.receptions_table.setAlternatingRowColors(True)
        self.receptions_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.receptions_table.setSelectionMode(QTableWidget.SingleSelection)
        self.receptions_table.setEditTriggers(QTableWidget.NoEditTriggers)
        
        header = self.receptions_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
        
        layout.addWidget(self.receptions_table)
        
        # دکمه‌ها
        button_layout = QHBoxLayout()
        
        select_btn = QPushButton("✅ انتخاب پذیرش")
        select_btn.setStyleSheet("background-color: #27ae60;")
        select_btn.clicked.connect(self.select_reception)
        
        cancel_btn = QPushButton("❌ انصراف")
        cancel_btn.setStyleSheet("background-color: #e74c3c;")
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
            # شماره پذیرش
            self.receptions_table.setItem(row_idx, 0,
                QTableWidgetItem(reception.get('reception_number', '')))
            
            # مشتری
            self.receptions_table.setItem(row_idx, 1,
                QTableWidgetItem(reception.get('customer_name', '--')))
            
            # دستگاه
            device_type = reception.get('device_type', '')
            brand = reception.get('brand', '')
            device_text = f"{device_type} - {brand}"
            self.receptions_table.setItem(row_idx, 2,
                QTableWidgetItem(device_text))
            
            # مدل
            self.receptions_table.setItem(row_idx, 3,
                QTableWidgetItem(reception.get('model', '--')))
            
            # تاریخ پذیرش
            reception_date = reception.get('reception_date', '')
            if reception_date:
                jalali_date = self.data_manager.db.gregorian_to_jalali(reception_date)
                self.receptions_table.setItem(row_idx, 4,
                    QTableWidgetItem(jalali_date))
            else:
                self.receptions_table.setItem(row_idx, 4,
                    QTableWidgetItem("--"))
            
            # وضعیت
            status = reception.get('status', '')
            status_item = QTableWidgetItem(status)
            
            # رنگ‌بندی وضعیت
            if status == 'تعمیر شده':
                status_item.setForeground(QBrush(QColor("#27ae60")))
            elif status == 'تحویل داده شده':
                status_item.setForeground(QBrush(QColor("#3498db")))
            elif status == 'در انتظار':
                status_item.setForeground(QBrush(QColor("#f39c12")))
            elif status == 'لغو شده':
                status_item.setForeground(QBrush(QColor("#e74c3c")))
                
            self.receptions_table.setItem(row_idx, 5, status_item)
            
            # هزینه برآوردی
            estimated_cost = reception.get('estimated_cost', 0)
            estimated_toman = estimated_cost / 10
            self.receptions_table.setItem(row_idx, 6,
                QTableWidgetItem(f"{estimated_toman:,.0f} تومان"))
            
            # توضیحات مشکل
            problem_desc = reception.get('problem_description', '')
            if len(problem_desc) > 50:
                problem_desc = problem_desc[:47] + "..."
            self.receptions_table.setItem(row_idx, 7,
                QTableWidgetItem(problem_desc))
    
    def filter_receptions(self):
        """فیلتر کردن پذیرش‌ها - نسخه اصلاح شده با تاریخ شمسی"""
        try:
            status = self.status_combo.currentText()
            
            # دریافت تاریخ‌های شمسی از ویجت
            date_from_jalali = self.date_from.get_date()
            date_to_jalali = self.date_to.get_date()
                        
            # تبدیل به رشته
            date_from_str = date_from_jalali.strftime("%Y/%m/%d")
            date_to_str = date_to_jalali.strftime("%Y/%m/%d")
                        
            # تبدیل تاریخ‌های شمسی به میلادی برای کوئری
            date_from_greg = self.data_manager.db.jalali_to_gregorian(date_from_str)
            date_to_greg = self.data_manager.db.jalali_to_gregorian(date_to_str)
            
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
                params = (date_from_greg, date_to_greg)
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
                params = (status, date_from_greg, date_to_greg)
            
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
        """انتخاب پذیرش از جدول"""
        selected_row = self.receptions_table.currentRow()
        if selected_row < 0:
            QMessageBox.warning(self, "خطا", "لطفاً یک پذیرش را انتخاب کنید.")
            return
        
        try:
            # دریافت شماره پذیرش
            reception_number_item = self.receptions_table.item(selected_row, 0)
            if not reception_number_item:
                return
            
            reception_number = reception_number_item.text()
            
            # دریافت اطلاعات کامل پذیرش
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
                self.reception_selected.emit(reception)
                self.accept()
            else:
                QMessageBox.warning(self, "خطا", "پذیرش یافت نشد.")
                
        except Exception as e:
            QMessageBox.critical(self, "خطا", f"خطا در انتخاب پذیرش:\n{str(e)}")
    
    def get_selected_reception(self):
        """دریافت پذیرش انتخاب شده"""
        return self.selected_reception
    
class SimpleDateDialog(QDialog):
    """دیالوگ ساده انتخاب تاریخ"""
    
    def __init__(self, current_date, parent=None):
        super().__init__(parent)
        self.setWindowTitle("انتخاب تاریخ")
        self.setModal(True)
        self.setMinimumSize(300, 200)
        
        self.selected_date = current_date
        
        layout = QVBoxLayout(self)
        
        # فیلدهای سال، ماه، روز
        year_layout = QHBoxLayout()
        year_layout.addWidget(QLabel("سال:"))
        self.year_spin = QSpinBox()
        self.year_spin.setRange(1300, 1500)
        self.year_spin.setValue(current_date.year)
        year_layout.addWidget(self.year_spin)
        
        month_layout = QHBoxLayout()
        month_layout.addWidget(QLabel("ماه:"))
        self.month_spin = QSpinBox()
        self.month_spin.setRange(1, 12)
        self.month_spin.setValue(current_date.month)
        month_layout.addWidget(self.month_spin)
        
        day_layout = QHBoxLayout()
        day_layout.addWidget(QLabel("روز:"))
        self.day_spin = QSpinBox()
        self.day_spin.setRange(1, 31)
        self.day_spin.setValue(current_date.day)
        day_layout.addWidget(self.day_spin)
        
        layout.addLayout(year_layout)
        layout.addLayout(month_layout)
        layout.addLayout(day_layout)
        
        # نمایش تاریخ انتخاب شده
        self.preview_label = QLabel()
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.preview_label.setStyleSheet("""
            QLabel {
                font-weight: bold;
                color: #2ecc71;
                padding: 10px;
                font-size: 12pt;
            }
        """)
        layout.addWidget(self.preview_label)
        
        # دکمه‌ها
        button_layout = QHBoxLayout()
        btn_today = QPushButton("امروز")
        btn_today.clicked.connect(self.set_today)
        btn_ok = QPushButton("تأیید")
        btn_ok.clicked.connect(self.accept)
        btn_cancel = QPushButton("انصراف")
        btn_cancel.clicked.connect(self.reject)
        
        button_layout.addWidget(btn_today)
        button_layout.addStretch()
        button_layout.addWidget(btn_ok)
        button_layout.addWidget(btn_cancel)
        
        layout.addLayout(button_layout)
        
        # اتصال سیگنال‌ها
        self.year_spin.valueChanged.connect(self.update_preview)
        self.month_spin.valueChanged.connect(self.update_preview)
        self.day_spin.valueChanged.connect(self.update_preview)
        
        self.update_preview()
    
    def update_preview(self):
        """به‌روزرسانی پیش‌نمایش تاریخ"""
        year = self.year_spin.value()
        month = self.month_spin.value()
        day = self.day_spin.value()
        
        try:
            self.selected_date = jdatetime.date(year, month, day)
            date_str = f"{year:04d}/{month:02d}/{day:02d}"
            self.preview_label.setText(f"تاریخ انتخاب شده: {date_str}")
        except:
            self.preview_label.setText("تاریخ نامعتبر!")
    
    def set_today(self):
        """تنظیم تاریخ امروز"""
        today = jdatetime.date.today()
        self.year_spin.setValue(today.year)
        self.month_spin.setValue(today.month)
        self.day_spin.setValue(today.day)
    
    def get_selected_date(self):
        """دریافت تاریخ انتخاب شده"""
        return self.selected_date