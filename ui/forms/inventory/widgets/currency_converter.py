# ui/forms/inventory/widgets/currency_converter.py
"""
ویجت تبدیل ارز تومان/ریال
"""

from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QLabel, QLineEdit, 
    QComboBox, QPushButton
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont

class CurrencyConverter(QWidget):
    """ویجت تبدیل تومان به ریال و بالعکس"""
    
    value_changed = Signal(float)  # مقدار به تومان
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
    
    def setup_ui(self):
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)
        
        # فیلد ورود مقدار
        self.value_input = QLineEdit()
        self.value_input.setPlaceholderText("مبلغ")
        self.value_input.setMaximumWidth(150)
        self.value_input.setAlignment(Qt.AlignCenter)
        self.value_input.textChanged.connect(self.on_value_changed)
        
        # انتخاب واحد
        self.unit_combo = QComboBox()
        self.unit_combo.addItems(["تومان", "ریال"])
        self.unit_combo.setMaximumWidth(100)
        self.unit_combo.currentTextChanged.connect(self.on_unit_changed)
        
        # برچسب تبدیل
        self.conversion_label = QLabel("0 تومان")
        self.conversion_label.setStyleSheet("color: #1e90ff; font-weight: bold;")
        
        layout.addWidget(self.conversion_label)
        layout.addStretch()
        layout.addWidget(self.unit_combo)
        layout.addWidget(self.value_input)
        
        self.setLayout(layout)
    
    def on_value_changed(self, text):
        """هنگام تغییر مقدار"""
        try:
            value = float(text) if text else 0.0
            self.update_conversion(value)
        except:
            self.conversion_label.setText("0 تومان")
    
    def on_unit_changed(self, unit):
        """هنگام تغییر واحد"""
        self.on_value_changed(self.value_input.text())
    
    def update_conversion(self, value):
        """به‌روزرسانی نمایش تبدیل"""
        unit = self.unit_combo.currentText()
        
        if unit == "تومان":
            rial_value = value * 10
            self.conversion_label.setText(f"{rial_value:,.0f} ریال")
            self.value_changed.emit(value)
        else:  # ریال
            toman_value = value / 10
            self.conversion_label.setText(f"{toman_value:,.0f} تومان")
            self.value_changed.emit(toman_value)
    
    def set_value(self, value_in_toman):
        """تنظیم مقدار (بر حسب تومان)"""
        try:
            value = float(value_in_toman)
            if self.unit_combo.currentText() == "تومان":
                self.value_input.setText(str(value))
            else:
                self.value_input.setText(str(value * 10))
        except:
            self.value_input.setText("0")
    
    def get_value_toman(self):
        """دریافت مقدار به تومان"""
        try:
            value = float(self.value_input.text() or 0)
            if self.unit_combo.currentText() == "تومان":
                return value
            else:
                return value / 10
        except:
            return 0.0
    
    def get_value_rial(self):
        """دریافت مقدار به ریال"""
        return self.get_value_toman() * 10