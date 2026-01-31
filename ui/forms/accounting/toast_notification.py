# ui/forms/accounting/toast_notification.py

"""
سیستم اعلان‌های شناور (Toast Notifications)
"""

from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout, QHBoxLayout, QPushButton
from PySide6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, QPoint
from PySide6.QtGui import QFont, QPainter, QColor, QLinearGradient, QBrush


class ToastNotification(QWidget):
    """اعلان شناور در گوشه صفحه"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Tool | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_ShowWithoutActivating)
        
        self.init_ui()
        self.hide()
    
    def init_ui(self):
        """ایجاد رابط کاربری Toast"""
        self.setFixedSize(350, 90)
        
        # ویجت اصلی
        main_widget = QWidget()
        main_widget.setStyleSheet("""
            QWidget {
                background-color: rgba(44, 62, 80, 0.95);
                border-radius: 10px;
                border: 2px solid #3498db;
            }
        """)
        
        layout = QVBoxLayout(main_widget)
        layout.setContentsMargins(15, 10, 15, 10)
        layout.setSpacing(5)
        
        # عنوان
        self.title_label = QLabel()
        self.title_label.setStyleSheet("""
            QLabel {
                color: #ffffff;
                font-weight: bold;
                font-size: 13pt;
            }
        """)
        
        # پیام
        self.message_label = QLabel()
        self.message_label.setStyleSheet("""
            QLabel {
                color: #ecf0f1;
                font-size: 11pt;
            }
        """)
        self.message_label.setWordWrap(True)
        
        layout.addWidget(self.title_label)
        layout.addWidget(self.message_label)
        
        # لایه نهایی
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(main_widget)
        
        # ایجاد انیمیشن
        self.opacity_effect = QPropertyAnimation(self, b"windowOpacity")
        self.opacity_effect.setDuration(300)
        
        self.pos_animation = QPropertyAnimation(self, b"pos")
        self.pos_animation.setDuration(300)
        self.pos_animation.setEasingCurve(QEasingCurve.OutCubic)
    
    def show_toast(self, title, message, duration=3000, toast_type="info"):
        """نمایش Toast"""
        self.title_label.setText(title)
        self.message_label.setText(message)
        
        # تغییر رنگ بر اساس نوع
        colors = {
            "success": "#27ae60",
            "error": "#e74c3c",
            "warning": "#f39c12",
            "info": "#3498db"
        }
        
        color = colors.get(toast_type, "#3498db")
        self.findChild(QWidget).setStyleSheet(f"""
            QWidget {{
                background-color: rgba(44, 62, 80, 0.95);
                border-radius: 10px;
                border: 2px solid {color};
            }}
        """)
        
        # موقعیت‌دهی در گوشه پایین راست
        self.set_position()
        
        # انیمیشن نمایش
        self.opacity_effect.setStartValue(0)
        self.opacity_effect.setEndValue(1)
        self.opacity_effect.start()
        
        self.show()
        self.raise_()
        
        # مخفی کردن خودکار
        QTimer.singleShot(duration, self.hide_toast)
    
    def set_position(self):
        """تنظیم موقعیت Toast"""
        if self.parent_window:
            parent_geometry = self.parent_window.geometry()
            x = parent_geometry.x() + parent_geometry.width() - self.width() - 20
            y = parent_geometry.y() + parent_geometry.height() - self.height() - 20
            self.move(x, y)
        else:
            # اگر parent نداریم، در گوشه پایین راست صفحه اصلی
            from PySide6.QtWidgets import QApplication
            screen = QApplication.primaryScreen().geometry()
            x = screen.width() - self.width() - 20
            y = screen.height() - self.height() - 20
            self.move(x, y)
    
    def hide_toast(self):
        """مخفی کردن Toast با انیمیشن"""
        self.opacity_effect.setStartValue(1)
        self.opacity_effect.setEndValue(0)
        self.opacity_effect.finished.connect(self.hide)
        self.opacity_effect.start()


class ToastManager:
    """مدیریت اعلان‌های شناور"""
    
    def __init__(self, parent_window):
        self.parent_window = parent_window
        self.toasts = []
        self.max_toasts = 3  # حداکثر تعداد Toastهای همزمان
        
    def show_toast(self, title, message, duration=3000, toast_type="info"):
        """نمایش یک Toast جدید"""
        # حذف Toastهای قدیمی اگر بیش از حد مجاز باشد
        if len(self.toasts) >= self.max_toasts:
            old_toast = self.toasts.pop(0)
            old_toast.hide()
            old_toast.deleteLater()
        
        toast = ToastNotification(self.parent_window)
        toast.show_toast(title, message, duration, toast_type)
        self.toasts.append(toast)
        
        # موقعیت‌دهی عمودی برای Toastهای متعدد
        self.reposition_toasts()
        
        # حذف از لیست پس از مخفی شدن
        QTimer.singleShot(duration + 300, lambda: self.remove_toast(toast))
    
    def reposition_toasts(self):
        """تنظیم مجدد موقعیت Toastها"""
        if not self.toasts:
            return
        
        for i, toast in enumerate(self.toasts):
            if self.parent_window:
                parent_geometry = self.parent_window.geometry()
                x = parent_geometry.x() + parent_geometry.width() - toast.width() - 20
                y = parent_geometry.y() + parent_geometry.height() - ((i + 1) * (toast.height() + 10)) - 20
                toast.move(x, y)
    
    def remove_toast(self, toast):
        """حذف Toast از لیست"""
        if toast in self.toasts:
            self.toasts.remove(toast)
            toast.deleteLater()
            self.reposition_toasts()
    
    def show_success(self, message, title="✅ موفقیت"):
        """نمایش پیام موفقیت"""
        self.show_toast(title, message, 3000, "success")
    
    def show_error(self, message, title="❌ خطا"):
        """نمایش پیام خطا"""
        self.show_toast(title, message, 5000, "error")
    
    def show_info(self, message, title="ℹ️ اطلاعات"):
        """نمایش پیام اطلاعات"""
        self.show_toast(title, message, 3000, "info")
    
    def show_warning(self, message, title="⚠️ هشدار"):
        """نمایش پیام هشدار"""
        self.show_toast(title, message, 4000, "warning")
    
    def clear_all(self):
        """پاک کردن تمام Toastها"""
        for toast in self.toasts:
            toast.hide()
            toast.deleteLater()
        self.toasts.clear()


class NotificationBanner(QWidget):
    """بنر اطلاع‌رسانی در بالای صفحه"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        if parent:
            parent.installEventFilter(self)
        
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TransparentForMouseEvents)
        
        self.init_ui()
        self.hide()
    
    def init_ui(self):
        """ایجاد رابط کاربری بنر"""
        self.setFixedHeight(50)
        
        container = QWidget()
        container.setStyleSheet("""
            QWidget {
                background-color: rgba(41, 128, 185, 0.95);
                border-radius: 0px;
                border-bottom: 2px solid #2980b9;
            }
        """)
        
        layout = QHBoxLayout(container)
        layout.setContentsMargins(20, 5, 20, 5)
        
        self.message_label = QLabel()
        self.message_label.setStyleSheet("""
            QLabel {
                color: white;
                font-weight: bold;
                font-size: 12pt;
                padding: 5px;
            }
        """)
        
        layout.addWidget(self.message_label)
        layout.addStretch()
        
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(container)
    
    def show_notification(self, message, duration=3000, banner_type="info"):
        """نمایش بنر اطلاع‌رسانی"""
        self.message_label.setText(message)
        
        # تغییر رنگ بر اساس نوع
        colors = {
            "success": "#27ae60",
            "error": "#e74c3c",
            "warning": "#f39c12",
            "info": "#3498db"
        }
        
        color = colors.get(banner_type, "#3498db")
        self.findChild(QWidget).setStyleSheet(f"""
            QWidget {{
                background-color: rgba({self.hex_to_rgb(color)}, 0.95);
                border-radius: 0px;
                border-bottom: 2px solid {color};
            }}
        """)
        
        # تنظیم موقعیت در بالای پنجره والد
        if self.parent():
            parent_rect = self.parent().rect()
            self.setFixedWidth(parent_rect.width())
            self.move(0, 0)
        
        self.show()
        
        # مخفی کردن خودکار
        QTimer.singleShot(duration, self.hide_notification)
    
    def hex_to_rgb(self, hex_color):
        """تبدیل رنگ HEX به RGB"""
        hex_color = hex_color.lstrip('#')
        if len(hex_color) == 6:
            r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
            return f"{r}, {g}, {b}"
        return "41, 128, 185"
    
    def hide_notification(self):
        """مخفی کردن بنر"""
        self.hide()