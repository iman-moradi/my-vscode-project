# ui/forms/device_category_manager_form.py - نسخه اصلاح شده
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

from .device_category_name_form import DeviceCategoryNameForm
from database.database import DatabaseManager
from database.models import DataManager

class DeviceCategoryManagerForm(QDialog):
    """فرم مدیریت کامل دسته‌بندی دستگاه‌ها"""
    
    def __init__(self, data_manager, parent=None):
        super().__init__(parent)
        self.data_manager = data_manager
        self.categories = []
        
        self.setWindowTitle("📱 مدیریت دسته‌بندی دستگاه‌ها")
        self.setMinimumSize(800, 600)
        
        self.setup_ui()
        self.load_categories()
        
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
        self.txt_search.setPlaceholderText("جستجوی دسته‌بندی...")
        self.txt_search.textChanged.connect(self.search_categories)
        toolbar_layout.addWidget(QLabel("جستجو:"))
        toolbar_layout.addWidget(self.txt_search)
        
        toolbar_layout.addStretch()
        
        # دکمه‌های عملیاتی
        self.btn_add = QPushButton("➕ افزودن جدید")
        self.btn_add.clicked.connect(self.add_category)
        toolbar_layout.addWidget(self.btn_add)
        
        self.btn_edit = QPushButton("✏️ ویرایش")
        self.btn_edit.clicked.connect(self.edit_category)
        toolbar_layout.addWidget(self.btn_edit)
        
        self.btn_delete = QPushButton("🗑️ حذف")
        self.btn_delete.clicked.connect(self.delete_category)
        toolbar_layout.addWidget(self.btn_delete)
        
        self.btn_refresh = QPushButton("🔄 بروزرسانی")
        self.btn_refresh.clicked.connect(self.load_categories)
        toolbar_layout.addWidget(self.btn_refresh)
        
        main_layout.addLayout(toolbar_layout)
        
        # جدول دسته‌بندی‌ها
        self.table = QTableWidget()
        headers = ["ردیف", "شناسه", "نام دسته‌بندی", "تاریخ ایجاد"]
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
        
        # استایل
        self.setStyleSheet("""
            QDialog {
                background-color: #000000;
                color: #ffffff;
                font-family: 'B Nazanin';
                font-size: 11pt;
            }
            
            QLabel {
                color: #ffffff;
                background-color: transparent;
                padding: 3px;
            }
            
            QLineEdit {
                background-color: #1a1a1a;
                border: 1px solid #424242;
                border-radius: 4px;
                padding: 8px;
                color: #ffffff;
                min-height: 30px;
            }
            
            QPushButton {
                background-color: #2d2d2d;
                color: #ffffff;
                border: 1px solid #444;
                border-radius: 4px;
                padding: 8px 15px;
                min-width: 80px;
            }
            
            QPushButton:hover {
                background-color: #3d3d3d;
            }
            
            QTableWidget {
                background-color: #0a0a0a;
                color: #ffffff;
                gridline-color: #333;
                border: 1px solid #333;
                selection-background-color: #2a5caa;
                selection-color: #ffffff;
            }
            
            QTableWidget::item {
                padding: 5px;
                color: #ffffff;
            }
            
            QHeaderView::section {
                background-color: #1a1a1a;
                color: #ffffff;
                padding: 8px;
                border: 1px solid #333;
                font-weight: bold;
            }
        """)
    
    def convert_to_jalali(self, gregorian_date_str):
        """تبدیل تاریخ میلادی به شمسی - شبیه JalaliDateInput"""
        if not gregorian_date_str:
            return ""
        
        try:
            # اگر رشته تاریخ میلادی است
            if isinstance(gregorian_date_str, str):
                # حذف زمان اگر وجود دارد (مثلا: '2024-01-30 20:33:20')
                if ' ' in gregorian_date_str:
                    gregorian_date_str = gregorian_date_str.split(' ')[0]
                
                # جدا کردن تاریخ
                if '-' in gregorian_date_str:
                    parts = gregorian_date_str.split('-')
                elif '/' in gregorian_date_str:
                    parts = gregorian_date_str.split('/')
                else:
                    return gregorian_date_str
                
                if len(parts) >= 3:
                    year, month, day = map(int, parts[:3])
                    # ایجاد تاریخ میلادی
                    gregorian_date = datetime(year, month, day).date()
                else:
                    return gregorian_date_str
            else:
                # احتمالاً شیء date است
                gregorian_date = gregorian_date_str
            
            # تبدیل به شمسی
            jalali_date = jdatetime.date.fromgregorian(date=gregorian_date)
            return jalali_date.strftime("%Y/%m/%d")
            
        except Exception as e:
            print(f"خطا در تبدیل تاریخ '{gregorian_date_str}': {e}")
            return str(gregorian_date_str)
    
    def load_categories(self):
        """بارگذاری دسته‌بندی‌ها"""
        try:
            self.categories = self.data_manager.device_category_name.get_all()
            self.update_table()
            
        except Exception as e:
            QMessageBox.critical(self, "خطا", f"خطا در بارگذاری دسته‌بندی‌ها: {str(e)}")
    
    def update_table(self):
        """به‌روزرسانی جدول"""
        self.table.setRowCount(len(self.categories))
        
        for i, category in enumerate(self.categories):
            # ردیف
            item = QTableWidgetItem(str(i + 1))
            item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(i, 0, item)
            
            # شناسه
            item = QTableWidgetItem(str(category.get('id', '')))
            item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(i, 1, item)
            
            # نام
            item = QTableWidgetItem(category.get('name', ''))
            item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.table.setItem(i, 2, item)
            
            # تاریخ ایجاد - تبدیل به شمسی
            created = category.get('created_at', '')
            if created:
                jalali_date = self.convert_to_jalali(created)
                item = QTableWidgetItem(jalali_date)
            else:
                item = QTableWidgetItem('---')
            
            item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(i, 3, item)
        
        self.lbl_stats.setText(f"تعداد دسته‌بندی‌ها: {len(self.categories)}")
    
    def search_categories(self, text):
        """جستجوی دسته‌بندی‌ها"""
        if not text.strip():
            self.update_table()
            return
        
        filtered = []
        search_text = text.strip().lower()
        
        for category in self.categories:
            name = category.get('name', '').lower()
            if search_text in name:
                filtered.append(category)
        
        # نمایش نتایج فیلتر شده
        self.table.setRowCount(len(filtered))
        for i, category in enumerate(filtered):
            item = QTableWidgetItem(str(i + 1))
            item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(i, 0, item)
            
            item = QTableWidgetItem(str(category.get('id', '')))
            item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(i, 1, item)
            
            item = QTableWidgetItem(category.get('name', ''))
            item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.table.setItem(i, 2, item)
            
            self.lbl_stats.setText(f"تعداد نتایج: {len(filtered)}")
    
    def get_selected_category_id(self):
        """دریافت شناسه دسته‌بندی انتخاب شده"""
        selected_row = self.table.currentRow()
        if selected_row >= 0 and selected_row < len(self.categories):
            return self.categories[selected_row].get('id')
        return None
    
    def add_category(self):
        """افزودن دسته‌بندی جدید"""
        dialog = DeviceCategoryNameForm(self.data_manager, self)
        if dialog.exec():
            self.load_categories()
    
    def edit_category(self):
        """ویرایش دسته‌بندی انتخاب شده"""
        category_id = self.get_selected_category_id()
        if not category_id:
            QMessageBox.warning(self, "هشدار", "لطفاً یک دسته‌بندی را انتخاب کنید")
            return
        
        dialog = DeviceCategoryNameForm(self.data_manager, self, category_id)
        if dialog.exec():
            self.load_categories()
    
    def delete_category(self):
        """حذف دسته‌بندی انتخاب شده"""
        category_id = self.get_selected_category_id()
        if not category_id:
            QMessageBox.warning(self, "هشدار", "لطفاً یک دسته‌بندی را انتخاب کنید")
            return
        
        # دریافت نام دسته‌بندی برای نمایش
        category_name = ""
        for cat in self.categories:
            if cat.get('id') == category_id:
                category_name = cat.get('name', '')
                break
        
        # تایید حذف
        reply = QMessageBox.question(
            self, "تایید حذف",
            f"آیا از حذف دسته‌بندی '{category_name}' مطمئن هستید؟\nاین عمل قابل بازگشت نیست.",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                query = "DELETE FROM DeviceCategories_name WHERE id = ?"
                if self.data_manager.db.execute_query(query, (category_id,)):
                    QMessageBox.information(self, "موفقیت", "دسته‌بندی با موفقیت حذف شد")
                    self.load_categories()
                else:
                    QMessageBox.critical(self, "خطا", "خطا در حذف دسته‌بندی")
            
            except Exception as e:
                QMessageBox.critical(self, "خطا", f"خطا در حذف: {str(e)}")