"""
ویجت نمایش وضعیت چک با آیکون‌های رنگی
"""

from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QPainter, QBrush, QPen


class CheckStatusWidget(QWidget):
    """ویجت نمایش وضعیت چک با دایره رنگی"""
    
    def __init__(self, status, parent=None):
        super().__init__(parent)
        self.status = status
        self.setup_ui()
    
    def setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(5, 2, 5, 2)
        layout.setSpacing(8)
        
        # دایره رنگی
        self.color_label = QLabel()
        self.color_label.setFixedSize(12, 12)
        self.color_label.setStyleSheet(f"""
            QLabel {{
                background-color: {self.get_status_color()};
                border-radius: 6px;
                border: 1px solid #333;
            }}
        """)
        
        # متن وضعیت
        self.text_label = QLabel(self.get_status_text())
        self.text_label.setStyleSheet("color: white; font-size: 9pt;")
        
        layout.addWidget(self.color_label)
        layout.addWidget(self.text_label)
        layout.addStretch()
    
    def get_status_color(self):
        """رنگ بر اساس وضعیت"""
        colors = {
            'وصول شده': '#27ae60',  # سبز
            'وصول نشده': '#f39c12',  # نارنجی
            'برگشتی': '#e74c3c',  # قرمز
            'پاس شده': '#3498db',  # آبی
            'پاس نشده': '#9b59b6',  # بنفش
            'بلوکه شده': '#7f8c8d',  # خاکستری
        }
        return colors.get(self.status, '#95a5a6')
    
    def get_status_text(self):
        """متن وضعیت با آیکون"""
        texts = {
            'وصول شده': '✅ وصول شده',
            'وصول نشده': '⏳ وصول نشده',
            'برگشتی': '❌ برگشتی',
            'پاس شده': '✅ پاس شده',
            'پاس نشده': '⏳ پاس نشده',
            'بلوکه شده': '🔒 بلوکه شده'
        }
        return texts.get(self.status, self.status)
    
    def set_status(self, status):
        """تغییر وضعیت"""
        self.status = status
        self.color_label.setStyleSheet(f"""
            QLabel {{
                background-color: {self.get_status_color()};
                border-radius: 6px;
                border: 1px solid #333;
            }}
        """)
        self.text_label.setText(self.get_status_text())


class CheckStatusIndicator(QWidget):
    """شاخص وضعیت چک برای استفاده در جدول"""
    
    def __init__(self, status, parent=None):
        super().__init__(parent)
        self.status = status
        self.setMinimumSize(80, 25)
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # رنگ پس‌زمینه
        color = QColor(self.get_status_color())
        painter.setBrush(QBrush(color))
        painter.setPen(QPen(QColor('#333'), 1))
        
        # رسم مستطیل گرد
        rect = self.rect().adjusted(1, 1, -1, -1)
        painter.drawRoundedRect(rect, 5, 5)
        
        # متن
        painter.setPen(QPen(QColor('white')))
        painter.drawText(rect, Qt.AlignCenter, self.get_status_short())
    
    def get_status_color(self):
        """رنگ بر اساس وضعیت"""
        colors = {
            'وصول شده': '#27ae60',
            'وصول نشده': '#f39c12',
            'برگشتی': '#e74c3c',
            'پاس شده': '#3498db',
            'پاس نشده': '#9b59b6',
            'بلوکه شده': '#7f8c8d',
        }
        return colors.get(self.status, '#95a5a6')
    
    def get_status_short(self):
        """متن کوتاه وضعیت"""
        texts = {
            'وصول شده': 'وصول',
            'وصول نشده': 'وصول نشده',
            'برگشتی': 'برگشتی',
            'پاس شده': 'پاس',
            'پاس نشده': 'پاس نشده',
            'بلوکه شده': 'بلوکه'
        }
        return texts.get(self.status, self.status[:10])