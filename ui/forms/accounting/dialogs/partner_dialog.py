# ui/forms/accounting/dialogs/partner_dialog.py
"""
دیالوگ افزودن/ویرایش شریک
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QFormLayout, QMessageBox, QComboBox,
    QTextEdit, QGroupBox, QGridLayout
)
from PySide6.QtCore import Qt, Signal
import jdatetime

# ایمپورت ویجت تاریخ شمسی
try:
    from ui.forms.accounting.widgets.jalali_date_input import JalaliDateInputAccounting
except ImportError:
    print("⚠️ ویجت تاریخ شمسی یافت نشد")


class PartnerDialog(QDialog):
    """دیالوگ مدیریت شریک"""
    
    partner_saved = Signal()
    
    def __init__(self, data_manager, partner_id=None, parent=None):
        super().__init__(parent)
        self.data_manager = data_manager
        self.partner_id = partner_id
        self.partner_manager = None
        
        try:
            from modules.accounting.partner_manager import PartnerManager
            self.partner_manager = PartnerManager(data_manager)
        except ImportError as e:
            print(f"⚠️ خطا در بارگذاری PartnerManager: {e}")
        
        self.setWindowTitle("➕ افزودن شریک جدید" if not partner_id else "✏️ ویرایش شریک")
        self.setMinimumWidth(600)
        
        # 🔴 راست‌چین
        self.setLayoutDirection(Qt.RightToLeft)
        
        self.setup_styles()
        self.init_ui()
        self.load_partner_data()
        
    def setup_styles(self):
        """تنظیم استایل"""
        self.setStyleSheet("""
            QDialog {
                background-color: #111111;
                color: #ffffff;
                font-family: 'B Nazanin';
            }
            
            QLabel {
                color: #ffffff;
                font-size: 11pt;
            }
            
            QLineEdit, QComboBox, QTextEdit {
                background-color: #222222;
                border: 1px solid #333333;
                color: white;
                border-radius: 4px;
                padding: 8px;
                font-size: 11pt;
                font-family: 'B Nazanin';
            }
            
            QLineEdit:focus, QComboBox:focus, QTextEdit:focus {
                border-color: #27ae60;
            }
            
            QPushButton {
                background-color: #2c3e50;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-size: 11pt;
                font-weight: bold;
                font-family: 'B Nazanin';
            }
            
            QPushButton:hover {
                background-color: #34495e;
            }
            
            QPushButton#save_button {
                background-color: #27ae60;
            }
            
            QPushButton#save_button:hover {
                background-color: #219653;
            }
            
            QPushButton#cancel_button {
                background-color: #e74c3c;
            }
            
            QPushButton#cancel_button:hover {
                background-color: #c0392b;
            }
            
            QGroupBox {
                border: 2px solid #3498db;
                border-radius: 5px;
                margin-top: 10px;
                font-weight: bold;
                color: #3498db;
                background-color: #1a1a1a;
            }
            
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top right;
                padding: 0 10px 0 10px;
            }
        """)
    
    def init_ui(self):
        """راه‌اندازی رابط کاربری"""
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # گروه‌باکس اطلاعات پایه
        basic_group = QGroupBox("📋 اطلاعات پایه")
        basic_layout = QFormLayout()
        
        self.person_combo = QComboBox()
        self.load_persons()
        basic_layout.addRow("👤 شخص:", self.person_combo)
        
        self.start_date_input = JalaliDateInputAccounting()
        basic_layout.addRow("📅 تاریخ شروع:", self.start_date_input)
        
        self.end_date_input = JalaliDateInputAccounting()
        basic_layout.addRow("📅 تاریخ پایان (اختیاری):", self.end_date_input)
        
        basic_group.setLayout(basic_layout)
        layout.addWidget(basic_group)
        
        # گروه‌باکس اطلاعات مالی
        financial_group = QGroupBox("💰 اطلاعات مالی")
        financial_layout = QGridLayout()
        
        financial_layout.addWidget(QLabel("سرمایه (تومان):"), 0, 0)
        self.capital_input = QLineEdit()
        self.capital_input.setPlaceholderText("مبلغ سرمایه به تومان")
        financial_layout.addWidget(self.capital_input, 0, 1)
        
        financial_layout.addWidget(QLabel("درصد سود:"), 0, 2)
        self.percentage_input = QLineEdit()
        self.percentage_input.setPlaceholderText("درصد")
        financial_layout.addWidget(self.percentage_input, 0, 3)
        
        self.active_combo = QComboBox()
        self.active_combo.addItems(["فعال", "غیرفعال"])
        financial_layout.addWidget(QLabel("وضعیت:"), 1, 0)
        financial_layout.addWidget(self.active_combo, 1, 1)
        
        financial_group.setLayout(financial_layout)
        layout.addWidget(financial_group)
        
        # توضیحات
        layout.addWidget(QLabel("توضیحات:"))
        self.description_input = QTextEdit()
        self.description_input.setMaximumHeight(100)
        layout.addWidget(self.description_input)
        
        # دکمه‌ها
        btn_layout = QHBoxLayout()
        
        self.btn_save = QPushButton("💾 ذخیره")
        self.btn_save.setObjectName("save_button")
        self.btn_save.clicked.connect(self.save_partner)
        
        self.btn_cancel = QPushButton("❌ انصراف")
        self.btn_cancel.setObjectName("cancel_button")
        self.btn_cancel.clicked.connect(self.reject)
        
        btn_layout.addStretch()
        btn_layout.addWidget(self.btn_save)
        btn_layout.addWidget(self.btn_cancel)
        
        layout.addLayout(btn_layout)

    # در partner_dialog.py، تابع load_persons را اصلاح کنید:

    def load_persons(self):
        """بارگذاری لیست اشخاص"""
        try:
            # روش صحیح: استفاده از data_manager.person
            persons = self.data_manager.person.get_all_persons()  # 🔴 تغییر این خط
            
            self.person_combo.clear()
            for person in persons:
                display_name = f"{person.get('first_name', '')} {person.get('last_name', '')} - {person.get('mobile', '')}"
                self.person_combo.addItem(display_name, person.get('id'))
                
            print(f"✅ {len(persons)} شخص برای انتخاب بارگذاری شد")
            
        except Exception as e:
            print(f"⚠️ خطا در بارگذاری اشخاص: {e}")
            # اضافه کردن یک آیتم خالی
            self.person_combo.addItem("-- انتخاب کنید --", None)

    def load_partner_data(self):
        """بارگذاری داده‌های شریک برای ویرایش"""
        if not self.partner_id:
            # تنظیم تاریخ امروز برای شریک جدید
            self.start_date_input.set_today()
            return
        
        try:
            if not self.partner_manager:
                QMessageBox.warning(self, "خطا", "مدیریت شرکا در دسترس نیست")
                self.reject()
                return
            
            partner = self.partner_manager.get_partner_by_id(self.partner_id)
            if not partner:
                QMessageBox.warning(self, "خطا", "شریک یافت نشد")
                self.reject()
                return
            
            # بارگذاری داده‌ها در فیلدها
            # انتخاب شخص
            for i in range(self.person_combo.count()):
                if self.person_combo.itemData(i) == partner.get('person_id'):
                    self.person_combo.setCurrentIndex(i)
                    break
            
            # تاریخ‌ها
            if partner.get('partnership_start_shamsi'):
                self.start_date_input.set_date(partner.get('partnership_start_shamsi'))
            
            if partner.get('partnership_end_shamsi'):
                self.end_date_input.set_date(partner.get('partnership_end_shamsi'))
            
            # اطلاعات مالی
            self.capital_input.setText(str(partner.get('capital_toman', 0)))
            self.percentage_input.setText(str(partner.get('profit_percentage', 0)))
            
            # وضعیت
            self.active_combo.setCurrentIndex(0 if partner.get('active') else 1)
            
            # توضیحات
            self.description_input.setText(partner.get('description', ''))
            
        except Exception as e:
            QMessageBox.warning(self, "خطا", f"خطا در بارگذاری داده‌ها:\n{str(e)}")
    
 

    def save_partner(self):
        """ذخیره شریک"""
        try:
            # اعتبارسنجی
            person_id = self.person_combo.currentData()
            if not person_id:
                QMessageBox.warning(self, "خطا", "لطفاً یک شخص را انتخاب کنید")
                return
            
            capital_text = self.capital_input.text().strip()
            if not capital_text:
                capital = 0
            else:
                try:
                    capital = float(capital_text) * 10  # 🔴 تبدیل تومان به ریال (ضرب در 10)
                except:
                    QMessageBox.warning(self, "خطا", "سرمایه باید عددی باشد")
                    return
            
            percentage_text = self.percentage_input.text().strip()
            if not percentage_text:
                percentage = 0
            else:
                try:
                    percentage = float(percentage_text)
                except:
                    QMessageBox.warning(self, "خطا", "درصد سود باید عددی باشد")
                    return
            
            # 🔴 تبدیل تاریخ‌های شمسی به میلادی برای ذخیره در دیتابیس
            start_date_shamsi = self.start_date_input.get_date()
            start_date_miladi = self.data_manager.db.jalali_to_gregorian(start_date_shamsi) if start_date_shamsi else None
            
            end_date_shamsi = self.end_date_input.get_date()
            end_date_miladi = self.data_manager.db.jalali_to_gregorian(end_date_shamsi) if end_date_shamsi else None
            
            # آماده‌سازی داده‌ها
            partner_data = {
                'person_id': person_id,
                'partnership_start': start_date_miladi,  # 🔴 تاریخ میلادی
                'partnership_end': end_date_miladi,      # 🔴 تاریخ میلادی
                'capital': capital,  # 🔴 در دیتابیس به ریال ذخیره می‌شود
                'profit_percentage': percentage,
                'active': 1 if self.active_combo.currentText() == "فعال" else 0,
                'description': self.description_input.toPlainText().strip()
            }
            
            if not self.partner_manager:
                QMessageBox.warning(self, "خطا", "مدیریت شرکا در دسترس نیست")
                return
            
            # ذخیره یا ویرایش
            if not self.partner_id:
                success, message = self.partner_manager.create_partner(partner_data)
            else:
                success, message = self.partner_manager.update_partner(self.partner_id, partner_data)
            
            if success:
                self.partner_saved.emit()
                QMessageBox.information(self, "موفق", message)
                self.accept()
            else:
                QMessageBox.warning(self, "خطا", message)
                
        except Exception as e:
            QMessageBox.critical(self, "خطا", f"خطا در ذخیره شریک:\n{str(e)}")


