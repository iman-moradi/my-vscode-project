# ui/forms/brand_manager_form.py
from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *
import sys
import os
import jdatetime
from datetime import datetime

# اضافه کردن مسیر پروژه به sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "../../../"))
if project_root not in sys.path:
    sys.path.append(project_root)

from .brand_name_form import BrandNameForm

class BrandManagerForm(QDialog):
    """فرم مدیریت کامل برندها"""
    
    def __init__(self, data_manager, parent=None):
        super().__init__(parent)
        self.data_manager = data_manager
        self.brands = []
        
        self.setWindowTitle("🏷️ مدیریت برندها")
        self.setMinimumSize(800, 600)
        
        self.setup_ui()
        self.load_brands()
        
        # راست‌چین کامل
        self.setLayoutDirection(Qt.RightToLeft)
    
    def setup_ui(self):
        """ایجاد رابط کاربری"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(10)
        
        # نوار ابزار
        toolbar_layout = QHBoxLayout()
        
        # جستجو
        self.txt_search = QLineEdit()
        self.txt_search.setPlaceholderText("جستجوی برند...")
        self.txt_search.textChanged.connect(self.search_brands)
        toolbar_layout.addWidget(QLabel("جستجو:"))
        toolbar_layout.addWidget(self.txt_search)
        
        toolbar_layout.addStretch()
        
        # دکمه‌های عملیاتی
        self.btn_add = QPushButton("➕ افزودن جدید")
        self.btn_add.clicked.connect(self.add_brand)
        toolbar_layout.addWidget(self.btn_add)
        
        self.btn_edit = QPushButton("✏️ ویرایش")
        self.btn_edit.clicked.connect(self.edit_brand)
        toolbar_layout.addWidget(self.btn_edit)
        
        self.btn_delete = QPushButton("🗑️ حذف")
        self.btn_delete.clicked.connect(self.delete_brand)
        toolbar_layout.addWidget(self.btn_delete)
        
        self.btn_refresh = QPushButton("🔄 بروزرسانی")
        self.btn_refresh.clicked.connect(self.load_brands)
        toolbar_layout.addWidget(self.btn_refresh)
        
        main_layout.addLayout(toolbar_layout)
        
        # جدول برندها
        self.table = QTableWidget()
        headers = ["ردیف", "شناسه", "نام برند", "تاریخ ایجاد"]
        self.table.setColumnCount(len(headers))
        self.table.setHorizontalHeaderLabels(headers)
        
        # تنظیمات جدول
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.verticalHeader().setVisible(False)
        
        # تنظیم عرض ستون‌ها
        self.table.setColumnWidth(0, 50)   # ردیف
        self.table.setColumnWidth(1, 70)   # شناسه
        self.table.setColumnWidth(2, 300)  # نام
        
        main_layout.addWidget(self.table)
        
        # آمار
        stats_layout = QHBoxLayout()
        self.lbl_stats = QLabel("تعداد: 0")
        stats_layout.addWidget(self.lbl_stats)
        stats_layout.addStretch()
        main_layout.addLayout(stats_layout)
        
        # دکمه‌های پایین
        btn_layout = QHBoxLayout()
        self.btn_close = QPushButton("❌ بستن")
        self.btn_close.clicked.connect(self.reject)
        btn_layout.addStretch()
        btn_layout.addWidget(self.btn_close)
        
        main_layout.addLayout(btn_layout)
    
    def convert_to_jalali(self, gregorian_date_str):
        """تبدیل تاریخ میلادی به شمسی"""
        if not gregorian_date_str:
            return ""
        
        try:
            if isinstance(gregorian_date_str, str):
                if ' ' in gregorian_date_str:
                    gregorian_date_str = gregorian_date_str.split(' ')[0]
                
                if '-' in gregorian_date_str:
                    parts = gregorian_date_str.split('-')
                elif '/' in gregorian_date_str:
                    parts = gregorian_date_str.split('/')
                else:
                    return gregorian_date_str
                
                if len(parts) >= 3:
                    year, month, day = map(int, parts[:3])
                    gregorian_date = datetime(year, month, day).date()
                else:
                    return gregorian_date_str
            else:
                gregorian_date = gregorian_date_str
            
            jalali_date = jdatetime.date.fromgregorian(date=gregorian_date)
            return jalali_date.strftime("%Y/%m/%d")
            
        except Exception as e:
            print(f"خطا در تبدیل تاریخ: {e}")
            return str(gregorian_date_str)
    
    def load_brands(self):
        """بارگذاری برندها"""
        try:
            query = "SELECT * FROM Brands ORDER BY name"
            self.brands = self.data_manager.db.fetch_all(query)
            self.update_table()
            
        except Exception as e:
            print(f"خطا در بارگذاری برندها: {e}")
            QMessageBox.critical(self, "خطا", f"خطا در بارگذاری برندها: {str(e)}")
    
    def update_table(self):
        """به‌روزرسانی جدول"""
        self.table.setRowCount(len(self.brands))
        
        for i, brand in enumerate(self.brands):
            # ردیف
            item = QTableWidgetItem(str(i + 1))
            item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(i, 0, item)
            
            # شناسه
            item = QTableWidgetItem(str(brand.get('id', '')))
            item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(i, 1, item)
            
            # نام
            item = QTableWidgetItem(brand.get('name', ''))
            item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.table.setItem(i, 2, item)
            
            # تاریخ ایجاد
            created = brand.get('created_at', '')
            if created:
                jalali_date = self.convert_to_jalali(created)
                item = QTableWidgetItem(jalali_date)
            else:
                item = QTableWidgetItem('---')
            
            item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(i, 3, item)
        
        self.lbl_stats.setText(f"تعداد برندها: {len(self.brands)}")
    
    def search_brands(self, text):
        """جستجوی برندها"""
        if not text.strip():
            self.update_table()
            return
        
        filtered = []
        search_text = text.strip().lower()
        
        for brand in self.brands:
            name = brand.get('name', '').lower()
            if search_text in name:
                filtered.append(brand)
        
        # نمایش نتایج فیلتر شده
        self.table.setRowCount(len(filtered))
        for i, brand in enumerate(filtered):
            item = QTableWidgetItem(str(i + 1))
            item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(i, 0, item)
            
            item = QTableWidgetItem(str(brand.get('id', '')))
            item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(i, 1, item)
            
            item = QTableWidgetItem(brand.get('name', ''))
            item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.table.setItem(i, 2, item)
            
            self.lbl_stats.setText(f"تعداد نتایج: {len(filtered)}")
    
    def get_selected_brand_id(self):
        """دریافت شناسه برند انتخاب شده"""
        selected_row = self.table.currentRow()
        if selected_row >= 0 and selected_row < len(self.brands):
            return self.brands[selected_row].get('id')
        return None
    
    def add_brand(self):
        """افزودن برند جدید"""
        dialog = BrandNameForm(self.data_manager, self)
        if dialog.exec():
            self.load_brands()
    
    def edit_brand(self):
        """ویرایش برند انتخاب شده"""
        brand_id = self.get_selected_brand_id()
        if not brand_id:
            QMessageBox.warning(self, "هشدار", "لطفاً یک برند را انتخاب کنید")
            return
        
        dialog = BrandNameForm(self.data_manager, self, brand_id)
        if dialog.exec():
            self.load_brands()
    
    def delete_brand(self):
        """حذف برند انتخاب شده"""
        brand_id = self.get_selected_brand_id()
        if not brand_id:
            QMessageBox.warning(self, "هشدار", "لطفاً یک برند را انتخاب کنید")
            return
        
        # دریافت نام برند برای نمایش
        brand_name = ""
        for brand in self.brands:
            if brand.get('id') == brand_id:
                brand_name = brand.get('name', '')
                break
        
        # تایید حذف
        reply = QMessageBox.question(
            self, "تایید حذف",
            f"آیا از حذف برند '{brand_name}' مطمئن هستید؟\nاین عمل قابل بازگشت نیست.",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                query = "DELETE FROM Brands WHERE id = ?"
                if self.data_manager.db.execute_query(query, (brand_id,)):
                    QMessageBox.information(self, "موفقیت", "برند با موفقیت حذف شد")
                    self.load_brands()
                else:
                    QMessageBox.critical(self, "خطا", "خطا در حذف برند")
            
            except Exception as e:
                QMessageBox.critical(self, "خطا", f"خطا در حذف: {str(e)}")