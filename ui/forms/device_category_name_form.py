# ui/forms/device_category_name_form.py - نسخه اصلاح شده
from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *

class DeviceCategoryNameForm(QDialog):
    """فرم ساده برای ایجاد/ویرایش دسته‌بندی دستگاه‌ها"""
    
    def __init__(self, data_manager, parent=None, category_id=None):
        super().__init__(parent)
        self.data_manager = data_manager
        self.category_id = category_id
        
        self.setWindowTitle("➕ دسته‌بندی جدید" if not category_id else "✏️ ویرایش دسته‌بندی")
        self.setMinimumSize(400, 200)
        
        self.setup_ui()
        self.setup_style()
        
        if category_id:
            self.load_category_data()
            
    def setup_ui(self):
        """ایجاد رابط کاربری ساده"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # عنوان
        title_label = QLabel("📱 فرم مدیریت دسته‌بندی‌ها")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("font-size: 14pt; font-weight: bold; color: #4fc3f7;")
        layout.addWidget(title_label)
        
        # فیلد نام
        lbl_name = QLabel("نام دسته‌بندی:")
        self.txt_name = QLineEdit()
        self.txt_name.setPlaceholderText("مثال: سشوار، یخچال، ماشین لباسشویی")
        
        layout.addWidget(lbl_name)
        layout.addWidget(self.txt_name)
        layout.addStretch()
        
        # دکمه‌ها
        button_layout = QHBoxLayout()
        
        self.btn_save = QPushButton("💾 ذخیره" if not self.category_id else "💾 بروزرسانی")
        self.btn_save.setStyleSheet("""
            QPushButton {
                background-color: #1976d2;
                color: white;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
        """)
        self.btn_save.clicked.connect(self.on_save)
        
        self.btn_cancel = QPushButton("❌ انصراف")
        self.btn_cancel.setStyleSheet("""
            QPushButton {
                background-color: #d32f2f;
                color: white;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
        """)
        self.btn_cancel.clicked.connect(self.reject)
        
        button_layout.addStretch()
        button_layout.addWidget(self.btn_save)
        button_layout.addWidget(self.btn_cancel)
        
        layout.addLayout(button_layout)
        
        # راست‌چین
        self.setLayoutDirection(Qt.RightToLeft)
        
    def setup_style(self):
        """تنظیم استایل ساده"""
        self.setStyleSheet("""
            QDialog {
                background-color: #000000;
                color: #ffffff;
                font-family: 'B Nazanin';
                font-size: 11pt;
            }
            
            QLabel {
                color: #ffffff;
                background-color: transparent;
                padding: 5px;
            }
            
            QLineEdit {
                background-color: #1a1a1a;
                border: 1px solid #424242;
                border-radius: 4px;
                padding: 8px;
                color: #ffffff;
            }
            
            QLineEdit:focus {
                border: 1px solid #4a9eff;
            }
            
            QLineEdit::placeholder {
                color: #b0b0b0;
            }
            
            QPushButton {
                background-color: #2d2d2d;
                color: #ffffff;
                border: 1px solid #444;
                border-radius: 4px;
                padding: 8px 15px;
                min-width: 80px;
            }
            
            QPushButton:hover {
                background-color: #3d3d3d;
                border-color: #555;
            }
            
            QPushButton:pressed {
                background-color: #1d1d1d;
            }
        """)
        
    def load_category_data(self):
        """بارگذاری اطلاعات دسته‌بندی"""
        try:
            if self.category_id:
                query = "SELECT name FROM DeviceCategories_name WHERE id = ?"
                result = self.data_manager.db.fetch_one(query, (self.category_id,))
                if result and 'name' in result:
                    self.txt_name.setText(result['name'])
                    
        except Exception as e:
            print(f"خطا در بارگذاری اطلاعات دسته‌بندی: {e}")
            
    def on_save(self):
        """ذخیره دسته‌بندی - با بررسی تکراری بودن"""
        try:
            name = self.txt_name.text().strip()
            if not name:
                QMessageBox.warning(self, "خطا", "نام دسته‌بندی الزامی است")
                return
            
            # بررسی تکراری بودن نام (بدون در نظر گرفتن فاصله و حروف)
            normalized_name = name.strip().replace(' ', '')
            
            if self.category_id:
                # حالت ویرایش
                # ابتدا نام فعلی را بگیر
                query_current = "SELECT name FROM DeviceCategories_name WHERE id = ?"
                current_result = self.data_manager.db.fetch_one(query_current, (self.category_id,))
                
                if current_result:
                    current_name = current_result['name']
                    normalized_current = current_name.strip().replace(' ', '')
                    
                    if normalized_name == normalized_current:
                        # نام تغییر نکرده
                        query = "UPDATE DeviceCategories_name SET name = ? WHERE id = ?"
                        params = (name, self.category_id)
                    else:
                        # نام تغییر کرده، بررسی تکراری
                        query_check = """
                        SELECT COUNT(*) as count FROM DeviceCategories_name 
                        WHERE REPLACE(name, ' ', '') = ? AND id != ?
                        """
                        check_result = self.data_manager.db.fetch_one(query_check, (normalized_name, self.category_id))
                        
                        if check_result and check_result['count'] > 0:
                            QMessageBox.warning(self, "خطا", 
                                "این نام (یا نام مشابه) قبلاً ثبت شده است")
                            return
                        
                        query = "UPDATE DeviceCategories_name SET name = ? WHERE id = ?"
                        params = (name, self.category_id)
                    
                    message = "✅ دسته‌بندی ویرایش شد"
                else:
                    QMessageBox.critical(self, "خطا", "دسته‌بندی پیدا نشد")
                    return
            else:
                # حالت افزودن جدید
                query_check = """
                SELECT COUNT(*) as count FROM DeviceCategories_name 
                WHERE REPLACE(name, ' ', '') = ?
                """
                check_result = self.data_manager.db.fetch_one(query_check, (normalized_name,))
                
                if check_result and check_result['count'] > 0:
                    QMessageBox.warning(self, "خطا", 
                        "این نام (یا نام مشابه) قبلاً ثبت شده است")
                    return
                
                query = "INSERT INTO DeviceCategories_name (name) VALUES (?)"
                params = (name,)
                message = "✅ دسته‌بندی جدید اضافه شد"
            
            success = self.data_manager.db.execute_query(query, params)
            
            if success:
                QMessageBox.information(self, "موفقیت", message)
                self.accept()
            else:
                QMessageBox.critical(self, "خطا", "❌ خطا در ذخیره‌سازی")
                
        except Exception as e:
            print(f"خطا در ذخیره دسته‌بندی: {e}")
            QMessageBox.critical(self, "خطا", f"❌ خطا: {str(e)}")