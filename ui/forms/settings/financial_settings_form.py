# financial_settings_form.py

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QFormLayout,
                               QLabel, QLineEdit, QSpinBox, 
                               QDoubleSpinBox, QComboBox, QCheckBox,
                               QGroupBox, QHBoxLayout, QPushButton)
from PySide6.QtCore import Qt

class FinancialSettingsForm(QWidget):
    """فرم تنظیمات مالی"""
    
    def __init__(self, data_manager):
        super().__init__()
        self.data_manager = data_manager
        self.init_ui()
        self.apply_styles()
    
    def init_ui(self):
        """ایجاد رابط کاربری"""
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # گروه مالیات
        tax_group = QGroupBox("💰 تنظیمات مالیاتی")
        tax_layout = QFormLayout()
        
        # نرخ مالیات بر ارزش افزوده
        self.spn_tax_percentage = QDoubleSpinBox()
        self.spn_tax_percentage.setRange(0, 100)
        self.spn_tax_percentage.setValue(9.0)
        self.spn_tax_percentage.setSuffix(" %")
        self.spn_tax_percentage.setDecimals(2)
        
        # فعال بودن مالیات
        self.chk_tax_enabled = QCheckBox("فعال کردن محاسبه مالیات")
        self.chk_tax_enabled.setChecked(True)
        
        # شماره اقتصادی
        self.txt_economic_code = QLineEdit()
        self.txt_economic_code.setPlaceholderText("کد اقتصادی شرکت")
        
        # شماره ثبت
        self.txt_registration_number = QLineEdit()
        self.txt_registration_number.setPlaceholderText("شماره ثبت شرکت")
        
        tax_layout.addRow("نرخ مالیات ارزش افزوده:", self.spn_tax_percentage)
        tax_layout.addRow("", self.chk_tax_enabled)
        tax_layout.addRow("کد اقتصادی:", self.txt_economic_code)
        tax_layout.addRow("شماره ثبت:", self.txt_registration_number)
        
        tax_group.setLayout(tax_layout)
        main_layout.addWidget(tax_group)
        
        # گروه تخفیف
        discount_group = QGroupBox("🎁 تنظیمات تخفیف")
        discount_layout = QFormLayout()
        
        # حداکثر تخفیف مجاز
        self.spn_max_discount = QDoubleSpinBox()
        self.spn_max_discount.setRange(0, 100)
        self.spn_max_discount.setValue(20.0)
        self.spn_max_discount.setSuffix(" %")
        
        # اعمال تخفیف روی خدمات
        self.chk_discount_on_services = QCheckBox("اجازه تخفیف روی خدمات")
        self.chk_discount_on_services.setChecked(True)
        
        # اعمال تخفیف روی قطعات
        self.chk_discount_on_parts = QCheckBox("اجازه تخفیف روی قطعات")
        self.chk_discount_on_parts.setChecked(True)
        
        # اعمال تخفیف روی دستگاه‌ها
        self.chk_discount_on_devices = QCheckBox("اجازه تخفیف روی دستگاه‌ها")
        self.chk_discount_on_devices.setChecked(False)
        
        discount_layout.addRow("حداکثر تخفیف مجاز:", self.spn_max_discount)
        discount_layout.addRow("", self.chk_discount_on_services)
        discount_layout.addRow("", self.chk_discount_on_parts)
        discount_layout.addRow("", self.chk_discount_on_devices)
        
        discount_group.setLayout(discount_layout)
        main_layout.addWidget(discount_group)
        
        # گروه سود شرکا
        profit_group = QGroupBox("🤝 تنظیمات سود شرکا")
        profit_layout = QFormLayout()
        
        # روش محاسبه سود
        self.cmb_profit_method = QComboBox()
        self.cmb_profit_method.addItems([
            "درصدی از کل فروش",
            "درصدی از سود خالص",
            "ثابت برای هر تراکنش",
            "ترکیبی (خدمات و قطعات جدا)"
        ])
        
        # توزیع خودکار سود
        self.chk_auto_profit_distribution = QCheckBox("توزیع خودکار سود پس از هر تراکنش")
        self.chk_auto_profit_distribution.setChecked(True)
        
        # تاریخ پرداخت سود
        self.cmb_profit_payment_date = QComboBox()
        self.cmb_profit_payment_date.addItems([
            "پایان هر روز",
            "پایان هر هفته",
            "پایان هر ماه",
            "پایان هر فصل",
            "پایان هر سال"
        ])
        
        # حداقل سود برای پرداخت
        self.spn_min_profit_payment = QDoubleSpinBox()
        self.spn_min_profit_payment.setRange(0, 100000000)
        self.spn_min_profit_payment.setValue(100000)
        self.spn_min_profit_payment.setSuffix(" تومان")
        self.spn_min_profit_payment.setDecimals(0)
        
        profit_layout.addRow("روش محاسبه سود:", self.cmb_profit_method)
        profit_layout.addRow("", self.chk_auto_profit_distribution)
        profit_layout.addRow("تاریخ پرداخت سود:", self.cmb_profit_payment_date)
        profit_layout.addRow("حداقل سود برای پرداخت:", self.spn_min_profit_payment)
        
        profit_group.setLayout(profit_layout)
        main_layout.addWidget(profit_group)
        
        # گروه روش‌های پرداخت
        payment_group = QGroupBox("💳 روش‌های پرداخت")
        payment_layout = QFormLayout()
        
        # فعال‌سازی روش‌های پرداخت
        self.chk_cash_payment = QCheckBox("پرداخت نقدی")
        self.chk_cash_payment.setChecked(True)
        
        self.chk_cheque_payment = QCheckBox("پرداخت با چک")
        self.chk_cheque_payment.setChecked(True)
        
        self.chk_card_payment = QCheckBox("پرداخت با کارت")
        self.chk_card_payment.setChecked(True)
        
        self.chk_online_payment = QCheckBox("پرداخت آنلاین")
        self.chk_online_payment.setChecked(False)
        
        self.chk_credit_payment = QCheckBox("پرداخت نسیه")
        self.chk_credit_payment.setChecked(True)
        
        # کارمزد کارتخوان
        self.spn_card_fee = QDoubleSpinBox()
        self.spn_card_fee.setRange(0, 10)
        self.spn_card_fee.setValue(1.5)
        self.spn_card_fee.setSuffix(" %")
        
        # حداکثر مبلغ نسیه
        self.spn_max_credit = QDoubleSpinBox()
        self.spn_max_credit.setRange(0, 100000000)
        self.spn_max_credit.setValue(5000000)
        self.spn_max_credit.setSuffix(" تومان")
        self.spn_max_credit.setDecimals(0)
        
        payment_layout.addRow("", self.chk_cash_payment)
        payment_layout.addRow("", self.chk_cheque_payment)
        payment_layout.addRow("", self.chk_card_payment)
        payment_layout.addRow("", self.chk_online_payment)
        payment_layout.addRow("", self.chk_credit_payment)
        payment_layout.addRow("کارمزد کارتخوان:", self.spn_card_fee)
        payment_layout.addRow("حداکثر مبلغ نسیه:", self.spn_max_credit)
        
        payment_group.setLayout(payment_layout)
        main_layout.addWidget(payment_group)
        
        # گروه گزارش مالی
        report_group = QGroupBox("📊 تنظیمات گزارش مالی")
        report_layout = QFormLayout()
        
        # دوره گزارش‌گیری
        self.cmb_report_period = QComboBox()
        self.cmb_report_period.addItems([
            "روزانه",
            "هفتگی",
            "ماهانه",
            "فصلی",
            "سالانه"
        ])
        
        # ارسال خودکار گزارش
        self.chk_auto_report = QCheckBox("ارسال خودکار گزارش به ایمیل")
        self.chk_auto_report.setChecked(False)
        
        # ایمیل دریافت گزارش
        self.txt_report_email = QLineEdit()
        self.txt_report_email.setPlaceholderText("ایمیل دریافت گزارش")
        
        # فرمت گزارش
        self.cmb_report_format = QComboBox()
        self.cmb_report_format.addItems(["PDF", "Excel", "هر دو"])
        
        report_layout.addRow("دوره گزارش‌گیری:", self.cmb_report_period)
        report_layout.addRow("", self.chk_auto_report)
        report_layout.addRow("ایمیل دریافت گزارش:", self.txt_report_email)
        report_layout.addRow("فرمت گزارش:", self.cmb_report_format)
        
        report_group.setLayout(report_layout)
        main_layout.addWidget(report_group)
        
        # فضای خالی در پایین
        main_layout.addStretch()
        
        self.setLayout(main_layout)
    
    def apply_styles(self):
        """اعمال استایل"""
        self.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 12pt;
                color: #2ecc71;
                border: 2px solid #2ecc71;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                padding: 0 10px;
            }
            QLineEdit, QComboBox, QDoubleSpinBox {
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
        """)
    
    def load_settings(self, settings_data):
        """بارگذاری تنظیمات"""
        try:
            # مالیات
            self.spn_tax_percentage.setValue(settings_data.get('tax_percentage', 9.0))
            self.chk_tax_enabled.setChecked(settings_data.get('tax_enabled', True))
            self.txt_economic_code.setText(settings_data.get('economic_code', ''))
            self.txt_registration_number.setText(settings_data.get('registration_number', ''))
            
            # تخفیف
            self.spn_max_discount.setValue(settings_data.get('max_discount', 20.0))
            self.chk_discount_on_services.setChecked(settings_data.get('discount_on_services', True))
            self.chk_discount_on_parts.setChecked(settings_data.get('discount_on_parts', True))
            self.chk_discount_on_devices.setChecked(settings_data.get('discount_on_devices', False))
            
            # سود شرکا
            profit_method = settings_data.get('profit_method', 'درصدی از کل فروش')
            profit_index = self.cmb_profit_method.findText(profit_method)
            if profit_index >= 0:
                self.cmb_profit_method.setCurrentIndex(profit_index)
            
            self.chk_auto_profit_distribution.setChecked(settings_data.get('auto_profit_distribution', True))
            
            payment_date = settings_data.get('profit_payment_date', 'پایان هر ماه')
            payment_index = self.cmb_profit_payment_date.findText(payment_date)
            if payment_index >= 0:
                self.cmb_profit_payment_date.setCurrentIndex(payment_index)
            
            self.spn_min_profit_payment.setValue(settings_data.get('min_profit_payment', 100000))
            
            # روش‌های پرداخت
            self.chk_cash_payment.setChecked(settings_data.get('cash_payment', True))
            self.chk_cheque_payment.setChecked(settings_data.get('cheque_payment', True))
            self.chk_card_payment.setChecked(settings_data.get('card_payment', True))
            self.chk_online_payment.setChecked(settings_data.get('online_payment', False))
            self.chk_credit_payment.setChecked(settings_data.get('credit_payment', True))
            self.spn_card_fee.setValue(settings_data.get('card_fee', 1.5))
            self.spn_max_credit.setValue(settings_data.get('max_credit', 5000000))
            
            # گزارش مالی
            report_period = settings_data.get('report_period', 'ماهانه')
            period_index = self.cmb_report_period.findText(report_period)
            if period_index >= 0:
                self.cmb_report_period.setCurrentIndex(period_index)
            
            self.chk_auto_report.setChecked(settings_data.get('auto_report', False))
            self.txt_report_email.setText(settings_data.get('report_email', ''))
            
            report_format = settings_data.get('report_format', 'PDF')
            format_index = self.cmb_report_format.findText(report_format)
            if format_index >= 0:
                self.cmb_report_format.setCurrentIndex(format_index)
                
        except Exception as e:
            print(f"خطا در بارگذاری تنظیمات مالی: {e}")
    
    def get_settings(self):
        """جمع‌آوری تنظیمات"""
        settings = {
            # مالیات
            'tax_percentage': self.spn_tax_percentage.value(),
            'tax_enabled': self.chk_tax_enabled.isChecked(),
            'economic_code': self.txt_economic_code.text().strip(),
            'registration_number': self.txt_registration_number.text().strip(),
            
            # تخفیف
            'max_discount': self.spn_max_discount.value(),
            'discount_on_services': self.chk_discount_on_services.isChecked(),
            'discount_on_parts': self.chk_discount_on_parts.isChecked(),
            'discount_on_devices': self.chk_discount_on_devices.isChecked(),
            
            # سود شرکا
            'profit_method': self.cmb_profit_method.currentText(),
            'auto_profit_distribution': self.chk_auto_profit_distribution.isChecked(),
            'profit_payment_date': self.cmb_profit_payment_date.currentText(),
            'min_profit_payment': self.spn_min_profit_payment.value(),
            
            # روش‌های پرداخت
            'cash_payment': self.chk_cash_payment.isChecked(),
            'cheque_payment': self.chk_cheque_payment.isChecked(),
            'card_payment': self.chk_card_payment.isChecked(),
            'online_payment': self.chk_online_payment.isChecked(),
            'credit_payment': self.chk_credit_payment.isChecked(),
            'card_fee': self.spn_card_fee.value(),
            'max_credit': self.spn_max_credit.value(),
            
            # گزارش مالی
            'report_period': self.cmb_report_period.currentText(),
            'auto_report': self.chk_auto_report.isChecked(),
            'report_email': self.txt_report_email.text().strip(),
            'report_format': self.cmb_report_format.currentText(),
        }
        
        return settings