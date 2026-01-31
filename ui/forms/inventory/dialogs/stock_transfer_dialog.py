"""
دیالوگ انتقال موجودی بین انبارها
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QComboBox, QSpinBox, QLineEdit,
    QFormLayout, QGroupBox, QMessageBox
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor

class StockTransferDialog(QDialog):
    """دیالوگ انتقال موجودی"""
    
    transfer_completed = Signal(dict)  # سیگنال اتمام انتقال
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("انتقال موجودی")
        self.setMinimumWidth(500)
        self.setStyleSheet("""
            QDialog {
                background-color: #1a1a1a;
            }
            QLabel {
                color: #ffffff;
            }
            QLineEdit, QSpinBox, QComboBox {
                background-color: #2a2a2a;
                color: #ffffff;
                border: 1px solid #444;
                border-radius: 4px;
                padding: 5px;
            }
        """)
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
        
        # تنظیمات انتقال
        transfer_group = QGroupBox("🔄 تنظیمات انتقال")
        transfer_group.setStyleSheet("""
            QGroupBox {
                color: #27ae60;
                font-weight: bold;
                border: 2px solid #27ae60;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 15px;
            }
        """)
        transfer_layout = QFormLayout()
        
        self.quantity_spin = QSpinBox()
        self.quantity_spin.setRange(1, 9999)
        self.quantity_spin.setValue(1)
        
        self.from_combo = QComboBox()
        self.to_combo = QComboBox()
        
        self.reason_input = QLineEdit()
        self.reason_input.setPlaceholderText("دلیل انتقال (اختیاری)")
        
        transfer_layout.addRow("تعداد:", self.quantity_spin)
        transfer_layout.addRow("از:", self.from_combo)
        transfer_layout.addRow("به:", self.to_combo)
        transfer_layout.addRow("دلیل:", self.reason_input)
        
        transfer_group.setLayout(transfer_layout)
        layout.addWidget(transfer_group)
        
        # دکمه‌ها
        button_layout = QHBoxLayout()
        
        self.transfer_btn = QPushButton("🔄 انتقال")
        self.transfer_btn.clicked.connect(self.accept)
        self.transfer_btn.setStyleSheet("""
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
        
        button_layout.addWidget(self.transfer_btn)
        button_layout.addWidget(self.cancel_btn)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
    
    def set_item_info(self, item_data):
        """تنظیم اطلاعات آیتم"""
        item_name = item_data.get('part_name') or item_data.get('model') or item_data.get('item_name', 'نامشخص')
        self.item_label.setText(f"{item_name}")
        self.current_location_label.setText(item_data.get('location', 'نامشخص'))
        self.current_stock_label.setText(f"{item_data.get('quantity', 0)} عدد")
        
        # تنظیم حداکثر مقدار انتقال
        max_quantity = item_data.get('quantity', 0)
        self.quantity_spin.setRange(1, max_quantity)
        
        # پر کردن لیست مکان‌ها
        locations = ['انبار اصلی', 'انبار سرد', 'انبار گرم', 'قفسه A', 'قفسه B', 'نمایشگاه']
        self.from_combo.clear()
        self.to_combo.clear()
        
        current_loc = item_data.get('location', '')
        if current_loc:
            self.from_combo.addItem(current_loc)
            
        for loc in locations:
            if loc != current_loc:
                self.from_combo.addItem(loc)
                self.to_combo.addItem(loc)
    
    def get_transfer_data(self):
        """دریافت داده‌های انتقال"""
        return {
            'quantity': self.quantity_spin.value(),
            'from_location': self.from_combo.currentText(),
            'to_location': self.to_combo.currentText(),
            'reason': self.reason_input.text()
        }