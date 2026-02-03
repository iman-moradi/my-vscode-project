# ui/forms/inventory/stock_management_form.py
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
    QLineEdit, QPushButton, QMessageBox, QComboBox,
    QFormLayout, QSpinBox, QDoubleSpinBox, QGroupBox,
    QGridLayout, QDateEdit
)
from PySide6.QtCore import Qt, QDate, Signal  # اضافه کردن Signal
from PySide6.QtGui import QFont
import sys
import os

# اضافه کردن مسیر پروژه
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "../../../"))
if project_root not in sys.path:
    sys.path.append(project_root)

from utils.jalali_date_widget import JalaliDateInput


class StockManagementForm(QDialog):
    """فرم مدیریت موجودی و خرید قطعات در انبار نو"""
    
    stock_saved = Signal(dict)
    
    def __init__(self, data_manager, part_id=None, part_info=None, parent=None):
        super().__init__(parent)
        self.data_manager = data_manager
        self.part_id = part_id
        self.part_info = part_info
        
        self.setup_ui()
        
        if part_info:
            self.load_part_info()
        
        # راست‌چین کامل
        self.setLayoutDirection(Qt.RightToLeft)
        
        # تنظیم اندازه
        self.setMinimumWidth(600)
        self.setMinimumHeight(500)
    
    def setup_ui(self):
        """تنظیم رابط کاربری"""
        self.setWindowTitle("مدیریت موجودی قطعه" if self.part_id else "خرید قطعه جدید")
        
        # لایه اصلی
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(15)
        
        # اطلاعات قطعه
        if self.part_info:
            info_group = QGroupBox("📋 اطلاعات قطعه")
            info_group.setLayoutDirection(Qt.RightToLeft)
            info_layout = QFormLayout(info_group)
            info_layout.setLabelAlignment(Qt.AlignRight)
            info_layout.setSpacing(8)
            
            self.lbl_part_code = QLabel("--")
            self.lbl_part_name = QLabel("--")
            self.lbl_category = QLabel("--")
            self.lbl_brand = QLabel("--")
            
            info_layout.addRow("کد قطعه:", self.lbl_part_code)
            info_layout.addRow("نام قطعه:", self.lbl_part_name)
            info_layout.addRow("دسته‌بندی:", self.lbl_category)
            info_layout.addRow("برند:", self.lbl_brand)
            
            layout.addWidget(info_group)
        
        # اطلاعات خرید/موجودی
        stock_group = QGroupBox("📥 اطلاعات خرید و موجودی")
        stock_group.setLayoutDirection(Qt.RightToLeft)
        stock_layout = QFormLayout(stock_group)
        stock_layout.setLabelAlignment(Qt.AlignRight)
        stock_layout.setSpacing(10)
        
        # تامین‌کننده
        self.cmb_supplier = QComboBox()
        self.cmb_supplier.setMinimumHeight(35)
        self.load_suppliers()
        stock_layout.addRow("تامین‌کننده:", self.cmb_supplier)
        
        # تعداد
        self.spn_quantity = QSpinBox()
        self.spn_quantity.setRange(1, 100000)
        self.spn_quantity.setValue(1)
        self.spn_quantity.setMinimumHeight(35)
        self.spn_quantity.setSuffix(" عدد")
        stock_layout.addRow("تعداد:", self.spn_quantity)
        
        # قیمت خرید
        self.spn_purchase_price = QDoubleSpinBox()
        self.spn_purchase_price.setRange(0, 1000000000)
        self.spn_purchase_price.setValue(0)
        self.spn_purchase_price.setMinimumHeight(35)
        self.spn_purchase_price.setDecimals(0)
        self.spn_purchase_price.setSuffix(" ریال")
        stock_layout.addRow("قیمت خرید:", self.spn_purchase_price)
        
        # قیمت فروش
        self.spn_sale_price = QDoubleSpinBox()
        self.spn_sale_price.setRange(0, 1000000000)
        self.spn_sale_price.setValue(0)
        self.spn_sale_price.setMinimumHeight(35)
        self.spn_sale_price.setDecimals(0)
        self.spn_sale_price.setSuffix(" ریال")
        stock_layout.addRow("قیمت فروش:", self.spn_sale_price)
        
        # تاریخ خرید
        self.date_purchase = JalaliDateInput()
        self.date_purchase.set_date_to_today()
        stock_layout.addRow("تاریخ خرید:", self.date_purchase)
        
        # شماره بچ
        self.txt_batch_number = QLineEdit()
        self.txt_batch_number.setPlaceholderText("مثلاً: BATCH-2024-001")
        self.txt_batch_number.setMinimumHeight(35)
        stock_layout.addRow("شماره بچ:", self.txt_batch_number)
        
        # محل انبار
        self.txt_location = QLineEdit()
        self.txt_location.setPlaceholderText("مثلاً: قفسه A-1")
        self.txt_location.setMinimumHeight(35)
        stock_layout.addRow("محل انبار:", self.txt_location)
        
        # تاریخ انقضا
        self.date_expiration = JalaliDateInput()
        stock_layout.addRow("تاریخ انقضا:", self.date_expiration)
        
        layout.addWidget(stock_group)
        
        # دکمه‌ها
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        self.btn_save = QPushButton("💾 ذخیره موجودی")
        self.btn_save.setMinimumHeight(40)
        self.btn_save.setMinimumWidth(120)
        self.btn_save.clicked.connect(self.save_stock)
        btn_layout.addWidget(self.btn_save)
        
        self.btn_cancel = QPushButton("❌ انصراف")
        self.btn_cancel.setMinimumHeight(40)
        self.btn_cancel.setMinimumWidth(120)
        self.btn_cancel.clicked.connect(self.reject)
        btn_layout.addWidget(self.btn_cancel)
        
        layout.addLayout(btn_layout)
        
        # استایل
        self.setup_style()
    
    def setup_style(self):
        """تنظیم استایل فرم"""
        self.setStyleSheet("""
            /* استایل اصلی */
            StockManagementForm {
                background-color: #000000;
            }
            
            /* لیبل‌ها */
            QLabel {
                color: #ffffff;
                background-color: transparent;
                padding: 3px;
                font-size: 11pt;
                font-family: 'B Nazanin';
                text-align: right;
            }
            
            /* کامبوباکس */
            QComboBox {
                background-color: #1a1a1a;
                color: #ffffff;
                border: 1px solid #333;
                border-radius: 4px;
                padding: 8px;
                font-size: 11pt;
                font-family: 'B Nazanin';
                text-align: right;
                min-height: 35px;
            }
            
            /* اسپین‌باکس */
            QSpinBox, QDoubleSpinBox {
                background-color: #1a1a1a;
                color: #ffffff;
                border: 1px solid #333;
                border-radius: 4px;
                padding: 8px;
                font-size: 11pt;
                font-family: 'B Nazanin';
                text-align: right;
                min-height: 35px;
            }
            
            /* فیلدهای متنی */
            QLineEdit {
                background-color: #1a1a1a;
                color: #ffffff;
                border: 1px solid #333;
                border-radius: 4px;
                padding: 8px;
                font-size: 11pt;
                font-family: 'B Nazanin';
                text-align: right;
                min-height: 35px;
            }
            
            /* دکمه‌ها */
            QPushButton {
                background-color: #2d2d2d;
                color: #ffffff;
                border: 1px solid #444;
                border-radius: 4px;
                padding: 10px 20px;
                font-size: 11pt;
                font-family: 'B Nazanin';
                min-width: 100px;
                min-height: 40px;
            }
            
            QPushButton:hover {
                background-color: #3d3d3d;
                border-color: #555;
            }
            
            QPushButton:pressed {
                background-color: #1d1d1d;
            }
            
            /* دکمه ذخیره */
            QPushButton#btn_save {
                background-color: #388e3c;
                font-weight: bold;
            }
            
            QPushButton#btn_save:hover {
                background-color: #43a047;
            }
            
            /* دکمه انصراف */
            QPushButton#btn_cancel {
                background-color: #d32f2f;
                font-weight: bold;
            }
            
            QPushButton#btn_cancel:hover {
                background-color: #e53935;
            }
            
            /* گروه */
            QGroupBox {
                border: 2px solid #333;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 15px;
                font-size: 12pt;
                font-weight: bold;
                color: #4a9eff;
                background-color: #0a0a0a;
            }
            
            QGroupBox::title {
                subcontrol-origin: margin;
                right: 10px;
                padding: 0 10px 0 10px;
                background-color: #0a0a0a;
                color: #4a9eff;
            }
        """)
        
        # ID برای دکمه‌ها
        self.btn_save.setObjectName("btn_save")
        self.btn_cancel.setObjectName("btn_cancel")
    

    def load_suppliers(self):
        """بارگذاری لیست تامین‌کنندگان - نسخه اصلاح شده"""
        try:
            # کوئری ساده‌تر
            query = """
            SELECT 
                id,
                first_name,
                last_name,
                mobile,
                phone
            FROM Persons 
            WHERE person_type = 'تامین کننده'
            ORDER BY first_name, last_name
            """
            
            suppliers = self.data_manager.db.fetch_all(query)
            print(f"📊 تعداد تامین‌کنندگان یافت شده: {len(suppliers)}")
            
            self.cmb_supplier.clear()
            self.cmb_supplier.addItem("-- انتخاب تامین‌کننده --", None)
            
            if suppliers:
                for supplier in suppliers:
                    supplier_id = supplier.get('id')
                    first_name = supplier.get('first_name', '')
                    last_name = supplier.get('last_name', '')
                    mobile = supplier.get('mobile', '')
                    
                    # ایجاد نام نمایشی
                    if first_name and last_name:
                        display_name = f"{first_name} {last_name}"
                    elif first_name:
                        display_name = first_name
                    elif last_name:
                        display_name = last_name
                    elif mobile:
                        display_name = f"تامین‌کننده ({mobile})"
                    else:
                        display_name = f"تامین‌کننده #{supplier_id}"
                    
                    print(f"  ➕ اضافه کردن: {display_name} (ID: {supplier_id})")
                    self.cmb_supplier.addItem(display_name, supplier_id)
            
            else:
                print("⚠️ هیچ تامین‌کننده‌ای یافت نشد")
                self.cmb_supplier.addItem("⚠️ ابتدا تامین‌کننده اضافه کنید", 0)
            
            print(f"✅ تعداد آیتم‌های کامبوباکس: {self.cmb_supplier.count()}")
            
        except Exception as e:
            print(f"❌ خطا در بارگذاری تامین‌کنندگان: {e}")
            import traceback
            traceback.print_exc()
            self.cmb_supplier.clear()
            self.cmb_supplier.addItem("⚠️ خطا در بارگذاری", 0)
        
    def load_part_info(self):
        """بارگذاری اطلاعات قطعه"""
        if self.part_info:
            self.lbl_part_code.setText(self.part_info.get('part_code', '--'))
            self.lbl_part_name.setText(self.part_info.get('part_name', '--'))
            self.lbl_category.setText(self.part_info.get('category', '--'))
            self.lbl_brand.setText(self.part_info.get('brand', '--'))
    
    def validate_form(self):
        """اعتبارسنجی فرم"""
        errors = []
        
        # تامین‌کننده
        if self.cmb_supplier.currentIndex() < 0 or self.cmb_supplier.currentData() == 0:
            errors.append("• انتخاب تامین‌کننده الزامی است")
        
        # تعداد
        if self.spn_quantity.value() <= 0:
            errors.append("• تعداد باید بیشتر از صفر باشد")
        
        # قیمت خرید
        if self.spn_purchase_price.value() <= 0:
            errors.append("• قیمت خرید باید بیشتر از صفر باشد")
        
        # قیمت فروش
        if self.spn_sale_price.value() <= 0:
            errors.append("• قیمت فروش باید بیشتر از صفر باشد")
        
        # بررسی تاریخ خرید
        if not self.date_purchase.is_valid():
            errors.append("• تاریخ خرید نامعتبر است")
        
        return errors
    
    def save_stock(self):
        """ذخیره اطلاعات موجودی"""
        errors = self.validate_form()
        if errors:
            QMessageBox.warning(self, "خطاهای اعتبارسنجی", "\n".join(errors))
            return
        
        try:
            # جمع‌آوری داده‌ها
            stock_data = {
                'part_id': self.part_id,
                'quantity': self.spn_quantity.value(),
                'purchase_price': self.spn_purchase_price.value(),
                'sale_price': self.spn_sale_price.value(),
                'supplier_id': self.cmb_supplier.currentData(),
                'purchase_date': self.date_purchase.get_gregorian_date(),
                'batch_number': self.txt_batch_number.text().strip(),
                'location': self.txt_location.text().strip(),
                'expiration_date': self.date_expiration.get_gregorian_date() if self.date_expiration.is_valid() else None,
                'status': 'موجود'
            }
            
            # اگر اطلاعات قطعه داریم، اضافه کردن به داده‌های ارسالی
            if self.part_info:
                stock_data.update({
                    'part_code': self.part_info.get('part_code', ''),
                    'part_name': self.part_info.get('part_name', '')
                })
            
            # ذخیره در دیتابیس
            success = self.data_manager.warehouse.add_to_warehouse('قطعات نو', stock_data)
            
            if success:
                # ارسال سیگنال
                self.stock_saved.emit(stock_data)
                
                QMessageBox.information(self, "موفقیت", "✅ موجودی با موفقیت ذخیره شد")
                self.accept()
            else:
                QMessageBox.critical(self, "خطا", "❌ خطا در ذخیره‌سازی موجودی")
        
        except Exception as e:
            print(f"خطا در ذخیره موجودی: {e}")
            QMessageBox.critical(self, "خطا", f"❌ خطا در ذخیره‌سازی: {str(e)}")
    
    def get_form_data(self):
        """دریافت داده‌های فرم"""
        return {
            'supplier_id': self.cmb_supplier.currentData(),
            'quantity': self.spn_quantity.value(),
            'purchase_price': self.spn_purchase_price.value(),
            'sale_price': self.spn_sale_price.value(),
            'purchase_date': self.date_purchase.get_gregorian_date(),
            'batch_number': self.txt_batch_number.text().strip(),
            'location': self.txt_location.text().strip(),
            'expiration_date': self.date_expiration.get_gregorian_date() if self.date_expiration.is_valid() else None
        }