# ui/login_window.py - فرم ورود به سیستم
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QLineEdit, QPushButton, QMessageBox, QFrame, 
    QSpacerItem, QSizePolicy
)
from PySide6.QtCore import Qt, Signal, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QFont, QPixmap, QIcon, QPalette, QColor
import jdatetime

class LoginWindow(QWidget):
    """فرم ورود به سیستم"""
    login_successful = Signal(dict)  # سیگنال موفقیت‌آمیز بودن ورود
    
    def __init__(self, data_manager):
        super().__init__()
        self.data_manager = data_manager
        self.init_ui()
        self.setup_animations()
        
    def init_ui(self):
        """راه‌اندازی رابط کاربری"""
        self.setWindowTitle("ورود به سیستم - مدیریت تعمیرگاه شیروین")
        self.setFixedSize(450, 550)
        
        # تنظیم استایل کلی
        self.setStyleSheet("""
            QWidget {
                background-color: #f5f7fa;
                font-family: 'B Nazanin', Tahoma;
            }
        """)
        
        # لایه اصلی
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # هدر با گرادیان
        header = QFrame()
        header.setFixedHeight(180)
        header.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #2c3e50, stop:1 #3498db);
                border-top-left-radius: 10px;
                border-top-right-radius: 10px;
            }
        """)
        
        header_layout = QVBoxLayout()
        header_layout.setContentsMargins(20, 20, 20, 20)
        
        # لوگو و عنوان
        logo_layout = QHBoxLayout()
        
        # آیکون برنامه
        icon_label = QLabel()
        icon_label.setFixedSize(60, 60)
        icon_label.setStyleSheet("""
            QLabel {
                background-color: white;
                border-radius: 30px;
                font-size: 24px;
                font-weight: bold;
                color: #3498db;
            }
        """)
        icon_label.setText("⚙️")
        icon_label.setAlignment(Qt.AlignCenter)
        
        # عنوان برنامه
        title_layout = QVBoxLayout()
        app_title = QLabel("سیستم مدیریت تعمیرگاه")
        app_title.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 24px;
                font-weight: bold;
            }
        """)
        app_title.setAlignment(Qt.AlignRight)
        
        app_subtitle = QLabel("لوازم خانگی شیروین")
        app_subtitle.setStyleSheet("""
            QLabel {
                color: #ecf0f1;
                font-size: 16px;
            }
        """)
        app_subtitle.setAlignment(Qt.AlignRight)
        
        title_layout.addWidget(app_title)
        title_layout.addWidget(app_subtitle)
        
        logo_layout.addLayout(title_layout)
        logo_layout.addWidget(icon_label)
        
        # تاریخ شمسی
        today = jdatetime.datetime.now()
        date_label = QLabel(today.strftime("%A %d %B %Y"))
        date_label.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 14px;
                padding-top: 10px;
            }
        """)
        date_label.setAlignment(Qt.AlignCenter)
        
        header_layout.addLayout(logo_layout)
        header_layout.addWidget(date_label)
        header.setLayout(header_layout)
        
        main_layout.addWidget(header)
        
        # فرم ورود
        form_container = QFrame()
        form_container.setStyleSheet("""
            QFrame {
                background-color: white;
                border-bottom-left-radius: 10px;
                border-bottom-right-radius: 10px;
            }
        """)
        
        form_layout = QVBoxLayout()
        form_layout.setContentsMargins(40, 30, 40, 30)
        form_layout.setSpacing(20)
        
        # عنوان فرم
        form_title = QLabel("ورود به پنل مدیریت")
        form_title.setStyleSheet("""
            QLabel {
                color: #2c3e50;
                font-size: 20px;
                font-weight: bold;
                padding-bottom: 10px;
            }
        """)
        form_title.setAlignment(Qt.AlignCenter)
        form_layout.addWidget(form_title)
        
        # فیلد نام کاربری
        username_group = QVBoxLayout()
        username_group.setSpacing(8)
        
        username_label = QLabel("نام کاربری:")
        username_label.setStyleSheet("""
            QLabel {
                color: #34495e;
                font-size: 14px;
                font-weight: bold;
            }
        """)
        
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("نام کاربری خود را وارد کنید")
        self.username_input.setMinimumHeight(45)
        self.username_input.setStyleSheet("""
            QLineEdit {
                padding: 12px 15px;
                border: 2px solid #dfe6e9;
                border-radius: 8px;
                font-size: 14px;
                color: #2d3436;
                background-color: #f8f9fa;
            }
            QLineEdit:focus {
                border: 2px solid #3498db;
                background-color: white;
            }
            QLineEdit:hover {
                border: 2px solid #b2bec3;
            }
        """)
        
        username_group.addWidget(username_label)
        username_group.addWidget(self.username_input)
        form_layout.addLayout(username_group)
        
        # فیلد رمز عبور
        password_group = QVBoxLayout()
        password_group.setSpacing(8)
        
        password_label = QLabel("رمز عبور:")
        password_label.setStyleSheet("""
            QLabel {
                color: #34495e;
                font-size: 14px;
                font-weight: bold;
            }
        """)
        
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("رمز عبور خود را وارد کنید")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setMinimumHeight(45)
        self.password_input.setStyleSheet("""
            QLineEdit {
                padding: 12px 15px;
                border: 2px solid #dfe6e9;
                border-radius: 8px;
                font-size: 14px;
                color: #2d3436;
                background-color: #f8f9fa;
            }
            QLineEdit:focus {
                border: 2px solid #3498db;
                background-color: white;
            }
            QLineEdit:hover {
                border: 2px solid #b2bec3;
            }
        """)
        
        password_group.addWidget(password_label)
        password_group.addWidget(self.password_input)
        form_layout.addLayout(password_group)
        
        # دکمه ورود
        self.login_button = QPushButton("ورود به سیستم")
        self.login_button.setMinimumHeight(50)
        self.login_button.setCursor(Qt.PointingHandCursor)
        self.login_button.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #27ae60, stop:1 #2ecc71);
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 16px;
                font-weight: bold;
                padding: 12px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #219653, stop:1 #27ae60);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #1e8449, stop:1 #219653);
                padding: 13px 11px 11px 13px;
            }
            QPushButton:disabled {
                background: #95a5a6;
                color: #7f8c8d;
            }
        """)
        self.login_button.clicked.connect(self.authenticate)
        form_layout.addWidget(self.login_button)
        
        # فاصله
        form_layout.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Expanding))
        
        # اطلاعات پیش‌فرض
        info_frame = QFrame()
        info_frame.setStyleSheet("""
            QFrame {
                background-color: #f8f9fa;
                border-radius: 8px;
                border: 1px solid #dfe6e9;
            }
        """)
        
        info_layout = QVBoxLayout()
        info_layout.setContentsMargins(15, 15, 15, 15)
        
        info_title = QLabel("💡 اطلاعات ورود پیش‌فرض")
        info_title.setStyleSheet("""
            QLabel {
                color: #2c3e50;
                font-size: 14px;
                font-weight: bold;
            }
        """)
        
        info_text = QLabel("نام کاربری: <b>admin</b><br>رمز عبور: <b>admin123</b>")
        info_text.setStyleSheet("""
            QLabel {
                color: #7f8c8d;
                font-size: 13px;
            }
        """)
        
        info_layout.addWidget(info_title)
        info_layout.addWidget(info_text)
        info_frame.setLayout(info_layout)
        
        form_layout.addWidget(info_frame)
        
        # کپی‌رایت
        copyright_label = QLabel("© ۱۴۰۴ - توسعه داده شده توسط تیم فنی تعمیرگاه شیروین")
        copyright_label.setStyleSheet("""
            QLabel {
                color: #95a5a6;
                font-size: 11px;
                padding-top: 15px;
            }
        """)
        copyright_label.setAlignment(Qt.AlignCenter)
        form_layout.addWidget(copyright_label)
        
        form_container.setLayout(form_layout)
        main_layout.addWidget(form_container)
        
        self.setLayout(main_layout)
        
        # تنظیم فونت
        self.set_fonts()
        
        # پیش‌پر کردن فیلدها برای تست
        self.username_input.setText("admin")
        self.password_input.setText("admin123")
        
        # تنظیم فوکوس
        self.username_input.setFocus()
        
    def set_fonts(self):
        """تنظیم فونت‌های فارسی"""
        font = QFont()
        font.setFamily("B Nazanin")
        font.setPointSize(10)
        self.setFont(font)
        
        # فونت مخصوص دکمه‌ها
        button_font = QFont()
        button_font.setFamily("B Nazanin")
        button_font.setPointSize(11)
        button_font.setBold(True)
        self.login_button.setFont(button_font)
        
    def setup_animations(self):
        """تنظیم انیمیشن‌ها"""
        self.shake_animation = QPropertyAnimation(self)
        self.shake_animation.setTargetObject(self)
        self.shake_animation.setPropertyName(b"pos")
        self.shake_animation.setEasingCurve(QEasingCurve.InOutSine)
        self.shake_animation.setDuration(300)
        
    def shake_window(self):
        """انیمیشن لرزش پنجره برای خطا"""
        original_pos = self.pos()
        
        self.shake_animation.setStartValue(original_pos)
        self.shake_animation.setKeyValueAt(0.2, original_pos + self.mapToParent(self.rect().topRight() * 0.05))
        self.shake_animation.setKeyValueAt(0.4, original_pos - self.mapToParent(self.rect().topRight() * 0.05))
        self.shake_animation.setKeyValueAt(0.6, original_pos + self.mapToParent(self.rect().topRight() * 0.03))
        self.shake_animation.setKeyValueAt(0.8, original_pos - self.mapToParent(self.rect().topRight() * 0.03))
        self.shake_animation.setEndValue(original_pos)
        
        self.shake_animation.start()
        
    def authenticate(self):
        """احراز هویت کاربر"""
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()
        
        # اعتبارسنجی اولیه
        if not username or not password:
            self.show_error("خطا", "لطفاً نام کاربری و رمز عبور را وارد کنید")
            self.shake_window()
            return
        
        # غیرفعال کردن دکمه هنگام پردازش
        self.login_button.setEnabled(False)
        self.login_button.setText("در حال بررسی...")
        
        # شبیه‌سازی تأخیر برای تجربه کاربری بهتر
        from PySide6.QtCore import QTimer
        QTimer.singleShot(500, lambda: self.perform_authentication(username, password))
        
    def perform_authentication(self, username, password):
        """انجام عملیات احراز هویت"""
        try:
            # احراز هویت از طریق DataManager
            user = self.data_manager.user.authenticate(username, password)
            
            if user:
                # موفقیت‌آمیز
                self.show_success("خوش آمدید", 
                    f"کاربر گرامی {user.get('full_name', user['username'])}، به سیستم مدیریت تعمیرگاه خوش آمدید.")
                
                # ارسال سیگنال موفقیت
                self.login_successful.emit(user)
            else:
                # ناموفق
                self.show_error("خطای ورود", 
                    "نام کاربری یا رمز عبور اشتباه است.\nلطفاً مجدداً تلاش کنید.")
                self.shake_window()
                self.password_input.clear()
                self.password_input.setFocus()
                
        except Exception as e:
            # خطای سیستمی
            self.show_error("خطای سیستم", 
                f"خطا در اتصال به پایگاه داده:\n{str(e)}")
            print(f"خطای احراز هویت: {e}")
            
        finally:
            # فعال‌سازی مجدد دکمه
            self.login_button.setEnabled(True)
            self.login_button.setText("ورود به سیستم")
            
    def show_error(self, title, message):
        """نمایش پیام خطا"""
        msg_box = QMessageBox(self)
        msg_box.setIcon(QMessageBox.Critical)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.setStandardButtons(QMessageBox.Ok)
        msg_box.setStyleSheet("""
            QMessageBox {
                background-color: white;
                font-family: 'B Nazanin', Tahoma;
            }
            QLabel {
                color: #2c3e50;
                font-size: 13px;
            }
            QPushButton {
                background-color: #e74c3c;
                color: white;
                padding: 8px 20px;
                border-radius: 5px;
                font-weight: bold;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        msg_box.exec()
        
    def show_success(self, title, message):
        """نمایش پیام موفقیت"""
        msg_box = QMessageBox(self)
        msg_box.setIcon(QMessageBox.Information)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.setStandardButtons(QMessageBox.Ok)
        msg_box.setStyleSheet("""
            QMessageBox {
                background-color: white;
                font-family: 'B Nazanin', Tahoma;
            }
            QLabel {
                color: #2c3e50;
                font-size: 13px;
            }
            QPushButton {
                background-color: #27ae60;
                color: white;
                padding: 8px 20px;
                border-radius: 5px;
                font-weight: bold;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #219653;
            }
        """)
        msg_box.exec()
        
    def keyPressEvent(self, event):
        """مدیریت کلیدهای کیبورد"""
        if event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
            self.authenticate()
        elif event.key() == Qt.Key_Escape:
            self.close()
        else:
            super().keyPressEvent(event)