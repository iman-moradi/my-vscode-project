"""
ویجت نمایش سطح موجودی (پیشرفت بار)
"""
from PySide6.QtWidgets import QWidget, QVBoxLayout, QProgressBar, QLabel, QHBoxLayout
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor

class StockLevelWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(5, 5, 5, 5)
        
        # هدر
        self.header_label = QLabel("سطح موجودی")
        self.header_label.setAlignment(Qt.AlignCenter)
        self.header_label.setStyleSheet("font-weight: bold; font-size: 11pt; color: #3498db;")
        
        # نوار پیشرفت
        self.progress_bar = QProgressBar()
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setFormat("%v/%m (%p%)")
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid #333333;
                border-radius: 5px;
                text-align: center;
                height: 25px;
                font-size: 10pt;
            }
            QProgressBar::chunk {
                background-color: #27ae60;
                border-radius: 3px;
            }
        """)
        
        # اطلاعات عددی
        info_layout = QHBoxLayout()
        self.current_label = QLabel("0")
        self.current_label.setStyleSheet("color: #27ae60; font-weight: bold;")
        self.separator_label = QLabel("/")
        self.separator_label.setStyleSheet("color: #cccccc;")
        self.max_label = QLabel("0")
        self.max_label.setStyleSheet("color: #e74c3c; font-weight: bold;")
        self.unit_label = QLabel("عدد")
        self.unit_label.setStyleSheet("color: #95a5a6;")
        
        info_layout.addWidget(self.current_label)
        info_layout.addWidget(self.separator_label)
        info_layout.addWidget(self.max_label)
        info_layout.addWidget(self.unit_label)
        info_layout.addStretch()
        
        layout.addWidget(self.header_label)
        layout.addWidget(self.progress_bar)
        layout.addLayout(info_layout)
        
        self.setLayout(layout)
    
    def set_stock_level(self, current, max_stock, unit="عدد"):
        """تنظیم سطح موجودی"""
        self.progress_bar.setMaximum(max_stock)
        self.progress_bar.setValue(current)
        
        self.current_label.setText(str(current))
        self.max_label.setText(str(max_stock))
        self.unit_label.setText(unit)
        
        # تغییر رنگ بر اساس سطح موجودی
        percentage = (current / max_stock) * 100 if max_stock > 0 else 0
        
        if percentage >= 70:
            color = "#27ae60"  # سبز
        elif percentage >= 30:
            color = "#f39c12"  # نارنجی
        else:
            color = "#e74c3c"  # قرمز
            
        self.progress_bar.setStyleSheet(f"""
            QProgressBar {{
                border: 2px solid #333333;
                border-radius: 5px;
                text-align: center;
                height: 25px;
                font-size: 10pt;
            }}
            QProgressBar::chunk {{
                background-color: {color};
                border-radius: 3px;
            }}
        """)