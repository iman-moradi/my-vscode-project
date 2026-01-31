"""
دیالوگ تعدیل موجودی (افزایش/کاهش)
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QComboBox, QSpinBox, QLineEdit,
    QFormLayout, QGroupBox, QRadioButton, QButtonGroup,
    QTextEdit, QMessageBox
)
from PySide6.QtCore import Qt, Signal, QDate
from PySide6.QtGui import QColor, QFont
import jdatetime

class StockAdjustmentDialog(QDialog):
    """دیالوگ تعدیل موجودی"""
    
    adjustment_completed = Signal(dict)  # سیگنال اتمام تعدیل
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("تعدیل موجودی")
        self.setMinimumWidth(500)
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # اطلاعات آیتم
        info_group = QGroupBox("📦 اطلاعات آیتم")
        info_group.setStyleSheet("""
            QGroupBox {
                color: #3498db;
                font-weight: bold;
                border: 2px solid #3498db;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 15px;
            }
        """)
        info_layout = QFormLayout()
        
        self.item_label = QLabel()
        self.item_label.setStyleSheet("font-weight: bold; color: #3498db; font-size: 12pt;")
        info_layout.addRow("آیتم:", self.item_label)
        
        self.current_location_label = QLabel()
        info_layout.addRow("محل فعلی:", self.current_location_label)
        
        self.current_stock_label = QLabel()
        info_layout.addRow("موجودی فعلی:", self.current_stock_label)
        
        info_group.setLayout(info_layout)
        layout.addWidget(info_group)
        
        # تنظیمات تعدیل
        adjustment_group = QGroupBox("📊 تنظیمات تعدیل")
        adjustment_group.setStyleSheet("""
            QGroupBox {
                color: #f39c12;
                font-weight: bold;
                border: 2px solid #f39c12;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 15px;
            }
        """)
        adjustment_layout = QFormLayout()
        
        # نوع تعدیل (افزایش/کاهش)
        type_layout = QHBoxLayout()
        self.adjustment_type_group = QButtonGroup()
        
        self.increase_radio = QRadioButton("➕ افزایش موجودی")
        self.increase_radio.setChecked(True)
        self.decrease_radio = QRadioButton("➖ کاهش موجودی")
        
        self.adjustment_type_group.addButton(self.increase_radio, 1)
        self.adjustment_type_group.addButton(self.decrease_radio, 2)
        
        type_layout.addWidget(self.decrease_radio)
        type_layout.addWidget(self.increase_radio)
        type_layout.addStretch()
        
        adjustment_layout.addRow("نوع تعدیل:", type_layout)
        
        # مقدار تعدیل
        self.quantity_spin = QSpinBox()
        self.quantity_spin.setRange(1, 9999)
        self.quantity_spin.setValue(1)
        adjustment_layout.addRow("تعداد:", self.quantity_spin)
        
        # قیمت واحد (در صورت افزایش)
        self.unit_price_layout = QHBoxLayout()
        self.unit_price_label = QLabel("قیمت واحد:")
        self.unit_price_input = QLineEdit()
        self.unit_price_input.setPlaceholderText("قیمت خرید هر واحد")
        self.unit_price_input.setMaximumWidth(150)
        self.unit_price_layout.addWidget(self.unit_price_input)
        self.unit_price_layout.addWidget(self.unit_price_label)
        self.unit_price_layout.addStretch()
        
        adjustment_layout.addRow(self.unit_price_layout)
        
        # دلیل تعدیل
        self.reason_combo = QComboBox()
        self.reason_combo.addItems([
            "تصحیح خطا",
            "موجودی فیزیکی",
            "خرید جدید",
            "فروش",
            "ضایعات",
            "سایر"
        ])
        adjustment_layout.addRow("دلیل تعدیل:", self.reason_combo)
        
        # توضیحات اضافی
        self.description_input = QTextEdit()
        self.description_input.setMaximumHeight(80)
        self.description_input.setPlaceholderText("توضیحات بیشتر (اختیاری)")
        adjustment_layout.addRow("توضیحات:", self.description_input)
        
        adjustment_group.setLayout(adjustment_layout)
        layout.addWidget(adjustment_group)
        
        # اطلاعات پس از تعدیل
        self.result_group = QGroupBox("📈 پس از تعدیل")
        self.result_group.setStyleSheet("""
            QGroupBox {
                color: #27ae60;
                font-weight: bold;
                border: 2px solid #27ae60;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 15px;
            }
        """)
        result_layout = QFormLayout()
        
        self.new_stock_label = QLabel("0 عدد")
        self.new_stock_label.setStyleSheet("font-weight: bold; color: #27ae60; font-size: 11pt;")
        result_layout.addRow("موجودی جدید:", self.new_stock_label)
        
        self.result_group.setLayout(result_layout)
        layout.addWidget(self.result_group)
        
        # اتصال سیگنال‌ها برای محاسبه آنی
        self.quantity_spin.valueChanged.connect(self.calculate_new_stock)
        self.increase_radio.toggled.connect(self.calculate_new_stock)
        self.decrease_radio.toggled.connect(self.calculate_new_stock)
        
        # دکمه‌ها
        button_layout = QHBoxLayout()
        
        self.adjust_btn = QPushButton("✅ تایید تعدیل")
        self.adjust_btn.clicked.connect(self.accept)
        self.adjust_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 12px 24px;
                font-weight: bold;
                font-size: 11pt;
            }
            QPushButton:hover {
                background-color: #219653;
            }
        """)
        
        self.cancel_btn = QPushButton("❌ لغو")
        self.cancel_btn.clicked.connect(self.reject)
        self.cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 12px 24px;
                font-weight: bold;
                font-size: 11pt;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        
        button_layout.addWidget(self.adjust_btn)
        button_layout.addWidget(self.cancel_btn)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
        
        # محاسبه اولیه
        self.calculate_new_stock()
    
    def set_item_info(self, item_data):
        """تنظیم اطلاعات آیتم"""
        item_name = item_data.get('part_name') or item_data.get('model') or item_data.get('item_name', 'نامشخص')
        self.item_label.setText(f"{item_name}")
        self.current_location_label.setText(item_data.get('location', 'نامشخص'))
        
        current_stock = item_data.get('quantity', 0)
        self.current_stock_label.setText(f"{current_stock} عدد")
        
        # ذخیره اطلاعات برای محاسبات
        self.current_stock = current_stock
        self.item_data = item_data
        
        # تنظیم حداکثر مقدار کاهش
        if self.decrease_radio.isChecked():
            self.quantity_spin.setMaximum(current_stock)
        
        self.calculate_new_stock()
    
    def calculate_new_stock(self):
        """محاسبه موجودی جدید"""
        try:
            adjustment = self.quantity_spin.value()
            current = self.current_stock
            
            if self.increase_radio.isChecked():
                new_stock = current + adjustment
                self.new_stock_label.setText(f"{new_stock} عدد (+{adjustment})")
                self.new_stock_label.setStyleSheet("font-weight: bold; color: #27ae60; font-size: 11pt;")
                
                # فعال کردن قیمت واحد برای افزایش
                self.unit_price_label.setVisible(True)
                self.unit_price_input.setVisible(True)
            else:
                new_stock = current - adjustment
                self.new_stock_label.setText(f"{new_stock} عدد (-{adjustment})")
                self.new_stock_label.setStyleSheet("font-weight: bold; color: #e74c3c; font-size: 11pt;")
                
                # غیرفعال کردن قیمت واحد برای کاهش
                self.unit_price_label.setVisible(False)
                self.unit_price_input.setVisible(False)
            
        except:
            self.new_stock_label.setText("خطا در محاسبه")
    
    def get_adjustment_data(self):
        """دریافت داده‌های تعدیل"""
        adjustment_type = "افزایش" if self.increase_radio.isChecked() else "کاهش"
        
        data = {
            'adjustment_type': adjustment_type,
            'quantity': self.quantity_spin.value(),
            'current_stock': self.current_stock,
            'new_stock': self.current_stock + (self.quantity_spin.value() if adjustment_type == "افزایش" else -self.quantity_spin.value()),
            'reason': self.reason_combo.currentText(),
            'description': self.description_input.toPlainText(),
            'item_data': self.item_data
        }
        
        # اضافه کردن قیمت واحد در صورت افزایش
        if adjustment_type == "افزایش":
            try:
                data['unit_price'] = float(self.unit_price_input.text()) if self.unit_price_input.text() else 0
            except:
                data['unit_price'] = 0
        
        return data
    
    def accept(self):
        """تایید تعدیل"""
        # اعتبارسنجی
        if self.decrease_radio.isChecked():
            if self.quantity_spin.value() > self.current_stock:
                QMessageBox.warning(self, "خطا", "مقدار کاهش نمی‌تواند بیشتر از موجودی فعلی باشد.")
                return
        
        if self.increase_radio.isChecked():
            if self.unit_price_input.text() and not self.unit_price_input.text().isdigit():
                QMessageBox.warning(self, "خطا", "قیمت واحد باید عددی باشد.")
                return
        
        super().accept()