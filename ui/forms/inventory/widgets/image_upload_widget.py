# ui/forms/inventory/widgets/image_upload_widget.py
"""
ویجت آپلود عکس برای دستگاه‌ها
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QScrollArea, QFrame, QGridLayout
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPixmap, QIcon
import os

class ImageUploadWidget(QWidget):
    """ویجت آپلود و نمایش عکس‌ها"""
    
    images_uploaded = Signal(dict)  # signal با مسیر عکس‌ها
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.image_paths = {}
        self.setup_ui()
    
    def setup_ui(self):
        """تنظیم رابط کاربری"""
        layout = QVBoxLayout()
        
        # هدر
        header_layout = QHBoxLayout()
        
        title_label = QLabel("🖼️ عکس‌ها و مدارک دستگاه")
        title_label.setStyleSheet("font-weight: bold; color: #ffffff;")
        
        btn_upload = QPushButton("📤 آپلود عکس")
        btn_upload.clicked.connect(self.upload_image)
        
        btn_clear = QPushButton("🗑️ پاک کردن همه")
        btn_clear.clicked.connect(self.clear_images)
        
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        header_layout.addWidget(btn_clear)
        header_layout.addWidget(btn_upload)
        
        layout.addLayout(header_layout)
        
        # ScrollArea برای نمایش عکس‌ها
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setMinimumHeight(200)
        
        self.scroll_content = QWidget()
        self.images_layout = QGridLayout(self.scroll_content)
        self.images_layout.setSpacing(10)
        
        self.scroll_area.setWidget(self.scroll_content)
        layout.addWidget(self.scroll_area)
        
        # برچسب راهنما
        help_label = QLabel("📎 می‌توانید عکس‌های دستگاه، مدارک خرید، گارانتی و ... را آپلود کنید.")
        help_label.setStyleSheet("color: #aaaaaa; font-size: 9pt;")
        layout.addWidget(help_label)
        
        self.setLayout(layout)
    
    def upload_image(self):
        """آپلود عکس"""
        from PySide6.QtWidgets import QFileDialog
        
        file_paths, _ = QFileDialog.getOpenFileNames(
            self,
            "انتخاب عکس‌ها",
            "",
            "Images (*.png *.jpg *.jpeg *.bmp *.gif);;All Files (*)"
        )
        
        if file_paths:
            for file_path in file_paths:
                self.add_image(file_path)
            
            self.images_uploaded.emit(self.image_paths)
    
    def add_image(self, file_path):
        """افزودن عکس به ویجت"""
        try:
            # ایجاد نام منحصر به فرد
            file_name = os.path.basename(file_path)
            if file_name in self.image_paths:
                base_name, ext = os.path.splitext(file_name)
                counter = 1
                while f"{base_name}_{counter}{ext}" in self.image_paths:
                    counter += 1
                file_name = f"{base_name}_{counter}{ext}"
            
            # ذخیره مسیر
            self.image_paths[file_name] = file_path
            
            # ایجاد کارت عکس
            self.create_image_card(file_name, file_path)
            
        except Exception as e:
            print(f"خطا در افزودن عکس: {e}")
    
    def create_image_card(self, file_name, file_path):
        """ایجاد کارت نمایش عکس"""
        # ایجاد ویجت کارت
        card = QFrame()
        card.setFrameShape(QFrame.StyledPanel)
        card.setStyleSheet("""
            QFrame {
                background-color: #1a1a1a;
                border: 2px solid #333333;
                border-radius: 8px;
                padding: 10px;
            }
        """)
        
        card_layout = QVBoxLayout()
        
        # نمایش تصویر کوچک
        image_label = QLabel()
        pixmap = QPixmap(file_path)
        
        # تغییر اندازه تصویر
        if not pixmap.isNull():
            scaled_pixmap = pixmap.scaled(
                150, 100, 
                Qt.KeepAspectRatio, 
                Qt.SmoothTransformation
            )
            image_label.setPixmap(scaled_pixmap)
            image_label.setAlignment(Qt.AlignCenter)
        
        card_layout.addWidget(image_label)
        
        # نام فایل
        name_label = QLabel(file_name[:20] + "..." if len(file_name) > 20 else file_name)
        name_label.setStyleSheet("color: #ffffff; font-size: 9pt;")
        name_label.setAlignment(Qt.AlignCenter)
        card_layout.addWidget(name_label)
        
        # دکمه حذف
        btn_delete = QPushButton("حذف")
        btn_delete.setMaximumWidth(80)
        btn_delete.clicked.connect(lambda: self.remove_image(file_name))
        
        card_layout.addWidget(btn_delete, 0, Qt.AlignCenter)
        
        card.setLayout(card_layout)
        
        # افزودن به layout
        row = len(self.image_paths) - 1
        col = row % 3  # 3 ستون
        self.images_layout.addWidget(card, row // 3, col)
    
    def remove_image(self, file_name):
        """حذف عکس"""
        if file_name in self.image_paths:
            del self.image_paths[file_name]
            self.refresh_images()
    
    def clear_images(self):
        """پاک کردن تمام عکس‌ها"""
        if self.image_paths:
            self.image_paths.clear()
            self.refresh_images()
    
    def refresh_images(self):
        """به‌روزرسانی نمایش عکس‌ها"""
        # حذف ویجت‌های قدیمی
        for i in reversed(range(self.images_layout.count())):
            widget = self.images_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()
        
        # افزودن مجدد عکس‌ها
        for i, (file_name, file_path) in enumerate(self.image_paths.items()):
            self.create_image_card(file_name, file_path)
    
    def get_images(self):
        """دریافت عکس‌ها"""
        return self.image_paths
    
    def clear(self):
        """پاک کردن ویجت"""
        self.clear_images()