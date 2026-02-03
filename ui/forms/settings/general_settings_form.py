# ui/forms/general_settings_form.py - فرم ساده برای شروع
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QFormLayout, 
                               QLineEdit, QComboBox, QSpinBox, QCheckBox)

class GeneralSettingsForm(QWidget):
    """فرم تنظیمات عمومی"""
    
    def __init__(self, data_manager, config_manager=None):
        super().__init__()
        self.data_manager = data_manager
        self.config_manager = config_manager
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        form_layout = QFormLayout()
        
        # نام برنامه
        self.txt_app_name = QLineEdit()
        form_layout.addRow("نام برنامه:", self.txt_app_name)
        
        # نام شرکت
        self.txt_company_name = QLineEdit()
        form_layout.addRow("نام شرکت:", self.txt_company_name)
        
        # تلفن
        self.txt_phone = QLineEdit()
        form_layout.addRow("تلفن:", self.txt_phone)
        
        # ایمیل
        self.txt_email = QLineEdit()
        form_layout.addRow("ایمیل:", self.txt_email)
        
        # فرمت تاریخ
        self.cmb_date_format = QComboBox()
        self.cmb_date_format.addItems(["شمسی", "میلادی"])
        form_layout.addRow("فرمت تاریخ:", self.cmb_date_format)
        
        # زبان
        self.cmb_language = QComboBox()
        self.cmb_language.addItems(["فارسی", "انگلیسی"])
        form_layout.addRow("زبان:", self.cmb_language)
        
        layout.addLayout(form_layout)
        layout.addStretch()
        self.setLayout(layout)
    
    def load_settings(self):
        """بارگذاری تنظیمات"""
        if self.config_manager:
            general = self.config_manager.get('general', {})
            self.txt_app_name.setText(general.get('app_name', ''))
            self.txt_company_name.setText(general.get('company_name', ''))
            self.txt_phone.setText(general.get('company_phone', ''))
            self.txt_email.setText(general.get('company_email', ''))
            self.cmb_date_format.setCurrentText(general.get('date_format', 'شمسی'))
            self.cmb_language.setCurrentText(general.get('language', 'فارسی'))
    
    def get_settings(self):
        """دریافت تنظیمات از فرم"""
        return {
            'app_name': self.txt_app_name.text(),
            'company_name': self.txt_company_name.text(),
            'company_phone': self.txt_phone.text(),
            'company_email': self.txt_email.text(),
            'date_format': self.cmb_date_format.currentText(),
            'language': self.cmb_language.currentText()
        }