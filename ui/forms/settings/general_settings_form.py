# general_settings_form.py

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, 
                               QGridLayout, QLabel, QLineEdit, 
                               QComboBox, QSpinBox, QCheckBox,
                               QGroupBox, QFormLayout, QTextEdit,
                               QPushButton, QFileDialog)
from PySide6.QtCore import Qt
import os

class GeneralSettingsForm(QWidget):
    """فرم تنظیمات عمومی"""
    
    def __init__(self, data_manager):
        super().__init__()
        self.data_manager = data_manager
        self.init_ui()
        self.apply_styles()
    
    def init_ui(self):
        """ایجاد رابط کاربری"""
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # گروه اطلاعات شرکت
        company_group = QGroupBox("🏢 اطلاعات شرکت")
        company_layout = QFormLayout()
        
        self.txt_company_name = QLineEdit()
        self.txt_company_name.setPlaceholderText("نام شرکت/تعمیرگاه")
        
        self.txt_company_address = QTextEdit()
        self.txt_company_address.setMaximumHeight(100)
        self.txt_company_address.setPlaceholderText("آدرس کامل")
        
        self.txt_company_phone = QLineEdit()
        self.txt_company_phone.setPlaceholderText("تلفن شرکت")
        
        self.txt_company_email = QLineEdit()
        self.txt_company_email.setPlaceholderText("ایمیل شرکت")
        
        self.txt_company_website = QLineEdit()
        self.txt_company_website.setPlaceholderText("وب‌سایت")
        
        # انتخاب لوگو
        logo_layout = QHBoxLayout()
        self.txt_logo_path = QLineEdit()
        self.txt_logo_path.setPlaceholderText("مسیر فایل لوگو")
        self.btn_browse_logo = QPushButton("انتخاب لوگو")
        self.btn_browse_logo.clicked.connect(self.browse_logo)
        logo_layout.addWidget(self.txt_logo_path)
        logo_layout.addWidget(self.btn_browse_logo)
        
        company_layout.addRow("نام شرکت:", self.txt_company_name)
        company_layout.addRow("آدرس:", self.txt_company_address)
        company_layout.addRow("تلفن:", self.txt_company_phone)
        company_layout.addRow("ایمیل:", self.txt_company_email)
        company_layout.addRow("وب‌سایت:", self.txt_company_website)
        company_layout.addRow("لوگو:", logo_layout)
        
        company_group.setLayout(company_layout)
        main_layout.addWidget(company_group)
        
        # گروه تنظیمات نمایش
        display_group = QGroupBox("🎨 تنظیمات نمایش")
        display_layout = QFormLayout()
        
        # انتخاب تم
        self.cmb_theme = QComboBox()
        self.cmb_theme.addItems(["تاریک", "روشن", "آبی تیره", "سبز تیره"])
        
        # انتخاب فونت
        self.cmb_font = QComboBox()
        self.cmb_font.addItems(["B Nazanin", "B Mitra", "B Titr", "Tahoma", "Arial"])
        
        # اندازه فونت
        self.spn_font_size = QSpinBox()
        self.spn_font_size.setRange(8, 20)
        self.spn_font_size.setValue(11)
        
        # راست‌چین
        self.chk_rtl = QCheckBox("فعال کردن راست‌چین")
        self.chk_rtl.setChecked(True)
        
        # نمایش تصویر
        self.chk_show_images = QCheckBox("نمایش تصاویر در فرم‌ها")
        self.chk_show_images.setChecked(True)
        
        display_layout.addRow("تم برنامه:", self.cmb_theme)
        display_layout.addRow("فونت:", self.cmb_font)
        display_layout.addRow("اندازه فونت:", self.spn_font_size)
        display_layout.addRow("", self.chk_rtl)
        display_layout.addRow("", self.chk_show_images)
        
        display_group.setLayout(display_layout)
        main_layout.addWidget(display_group)
        
        # گروه تنظیمات فرمت
        format_group = QGroupBox("📝 تنظیمات فرمت")
        format_layout = QFormLayout()
        
        # فرمت تاریخ
        self.cmb_date_format = QComboBox()
        self.cmb_date_format.addItems([
            "شمسی (۱۴۰۳/۰۱/۰۱)",
            "شمسی (۱۴۰۳-۰۱-۰۱)",
            "میلادی (2024-01-01)",
            "میلادی (01/01/2024)"
        ])
        
        # فرمت زمان
        self.cmb_time_format = QComboBox()
        self.cmb_time_format.addItems(["24 ساعته", "12 ساعته"])
        
        # فرمت ارز
        self.cmb_currency_format = QComboBox()
        self.cmb_currency_format.addItems([
            "تومان (۱,۰۰۰,۰۰۰)",
            "تومان (۱۰۰۰۰۰۰)",
            "ریال (۱۰,۰۰۰,۰۰۰)",
            "ریال (۱۰۰۰۰۰۰۰)"
        ])
        
        # جداکننده ارقام
        self.cmb_thousand_separator = QComboBox()
        self.cmb_thousand_separator.addItems(["ویرگول (۱,۰۰۰)", "نقطه (۱.۰۰۰)", "فاصله (۱ ۰۰۰)"])
        
        # تعداد اعشار
        self.spn_decimal_places = QSpinBox()
        self.spn_decimal_places.setRange(0, 4)
        self.spn_decimal_places.setValue(0)
        
        format_layout.addRow("فرمت تاریخ:", self.cmb_date_format)
        format_layout.addRow("فرمت زمان:", self.cmb_time_format)
        format_layout.addRow("فرمت ارز:", self.cmb_currency_format)
        format_layout.addRow("جداکننده هزارگان:", self.cmb_thousand_separator)
        format_layout.addRow("تعداد اعشار:", self.spn_decimal_places)
        
        format_group.setLayout(format_layout)
        main_layout.addWidget(format_group)
        
        # گروه تنظیمات چاپ
        print_group = QGroupBox("🖨️ تنظیمات چاپ")
        print_layout = QFormLayout()
        
        self.txt_printer_name = QLineEdit()
        self.txt_printer_name.setPlaceholderText("نام پیش‌فرض چاپگر")
        
        self.spn_print_copies = QSpinBox()
        self.spn_print_copies.setRange(1, 10)
        self.spn_print_copies.setValue(1)
        
        self.chk_print_header = QCheckBox("چاپ سربرگ در فاکتور")
        self.chk_print_header.setChecked(True)
        
        self.chk_print_footer = QCheckBox("چاپ پاورقی در فاکتور")
        self.chk_print_footer.setChecked(True)
        
        self.chk_auto_print = QCheckBox("چاپ خودکار پس از صدور فاکتور")
        self.chk_auto_print.setChecked(False)
        
        print_layout.addRow("چاپگر پیش‌فرض:", self.txt_printer_name)
        print_layout.addRow("تعداد کپی:", self.spn_print_copies)
        print_layout.addRow("", self.chk_print_header)
        print_layout.addRow("", self.chk_print_footer)
        print_layout.addRow("", self.chk_auto_print)
        
        print_group.setLayout(print_layout)
        main_layout.addWidget(print_group)
        
        # فضای خالی در پایین
        main_layout.addStretch()
        
        self.setLayout(main_layout)
    
    def apply_styles(self):
        """اعمال استایل"""
        self.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 12pt;
                color: #3498db;
                border: 2px solid #3498db;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                padding: 0 10px;
            }
            QLineEdit, QTextEdit, QComboBox, QSpinBox {
                background-color: #222222;
                color: #ffffff;
                border: 1px solid #444444;
                border-radius: 3px;
                padding: 5px;
                min-height: 25px;
            }
            QCheckBox {
                color: #ffffff;
            }
            QPushButton {
                background-color: #2c3e50;
                color: white;
                border: none;
                padding: 5px 15px;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #34495e;
            }
        """)
    
    def browse_logo(self):
        """انتخاب فایل لوگو"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "انتخاب لوگو",
            "",
            "Image Files (*.png *.jpg *.jpeg *.bmp *.ico)"
        )
        
        if file_path:
            self.txt_logo_path.setText(file_path)
    
    def load_settings(self, settings_data):
        """بارگذاری تنظیمات"""
        try:
            # اطلاعات شرکت
            self.txt_company_name.setText(settings_data.get('company_name', ''))
            self.txt_company_address.setPlainText(settings_data.get('company_address', ''))
            self.txt_company_phone.setText(settings_data.get('company_phone', ''))
            self.txt_company_email.setText(settings_data.get('company_email', ''))
            self.txt_company_website.setText(settings_data.get('company_website', ''))
            self.txt_logo_path.setText(settings_data.get('logo_path', ''))
            
            # تنظیمات نمایش
            theme = settings_data.get('theme', 'تاریک')
            theme_index = self.cmb_theme.findText(theme)
            if theme_index >= 0:
                self.cmb_theme.setCurrentIndex(theme_index)
            
            font = settings_data.get('font_family', 'B Nazanin')
            font_index = self.cmb_font.findText(font)
            if font_index >= 0:
                self.cmb_font.setCurrentIndex(font_index)
            
            self.spn_font_size.setValue(settings_data.get('font_size', 11))
            self.chk_rtl.setChecked(settings_data.get('rtl_enabled', True))
            self.chk_show_images.setChecked(settings_data.get('show_images', True))
            
            # تنظیمات فرمت
            date_format = settings_data.get('date_format', 'شمسی (۱۴۰۳/۰۱/۰۱)')
            date_index = self.cmb_date_format.findText(date_format)
            if date_index >= 0:
                self.cmb_date_format.setCurrentIndex(date_index)
            
            time_format = settings_data.get('time_format', '24 ساعته')
            time_index = self.cmb_time_format.findText(time_format)
            if time_index >= 0:
                self.cmb_time_format.setCurrentIndex(time_index)
            
            currency_format = settings_data.get('currency_format', 'تومان (۱,۰۰۰,۰۰۰)')
            currency_index = self.cmb_currency_format.findText(currency_format)
            if currency_index >= 0:
                self.cmb_currency_format.setCurrentIndex(currency_index)
            
            separator = settings_data.get('thousand_separator', 'ویرگول (۱,۰۰۰)')
            separator_index = self.cmb_thousand_separator.findText(separator)
            if separator_index >= 0:
                self.cmb_thousand_separator.setCurrentIndex(separator_index)
            
            self.spn_decimal_places.setValue(settings_data.get('decimal_places', 0))
            
            # تنظیمات چاپ
            self.txt_printer_name.setText(settings_data.get('printer_name', ''))
            self.spn_print_copies.setValue(settings_data.get('print_copies', 1))
            self.chk_print_header.setChecked(settings_data.get('print_header', True))
            self.chk_print_footer.setChecked(settings_data.get('print_footer', True))
            self.chk_auto_print.setChecked(settings_data.get('auto_print', False))
            
        except Exception as e:
            print(f"خطا در بارگذاری تنظیمات عمومی: {e}")
    
    def get_settings(self):
        """جمع‌آوری تنظیمات"""
        settings = {
            # اطلاعات شرکت
            'company_name': self.txt_company_name.text().strip(),
            'company_address': self.txt_company_address.toPlainText().strip(),
            'company_phone': self.txt_company_phone.text().strip(),
            'company_email': self.txt_company_email.text().strip(),
            'company_website': self.txt_company_website.text().strip(),
            'logo_path': self.txt_logo_path.text().strip(),
            
            # تنظیمات نمایش
            'theme': self.cmb_theme.currentText(),
            'font_family': self.cmb_font.currentText(),
            'font_size': self.spn_font_size.value(),
            'rtl_enabled': self.chk_rtl.isChecked(),
            'show_images': self.chk_show_images.isChecked(),
            
            # تنظیمات فرمت
            'date_format': self.cmb_date_format.currentText(),
            'time_format': self.cmb_time_format.currentText(),
            'currency_format': self.cmb_currency_format.currentText(),
            'thousand_separator': self.cmb_thousand_separator.currentText(),
            'decimal_places': self.spn_decimal_places.value(),
            
            # تنظیمات چاپ
            'printer_name': self.txt_printer_name.text().strip(),
            'print_copies': self.spn_print_copies.value(),
            'print_header': self.chk_print_header.isChecked(),
            'print_footer': self.chk_print_footer.isChecked(),
            'auto_print': self.chk_auto_print.isChecked(),
        }
        
        return settings