# ui/forms/brand_name_form.py
from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *

class BrandNameForm(QDialog):
    """فرم ساده برای ایجاد/ویرایش برندها"""
    
    def __init__(self, data_manager, parent=None, brand_id=None):
        super().__init__(parent)
        self.data_manager = data_manager
        self.brand_id = brand_id
        
        self.setWindowTitle("➕ برند جدید" if not brand_id else "✏️ ویرایش برند")
        self.setMinimumSize(400, 200)
        
        self.setup_ui()
        self.setup_style()
        
        if brand_id:
            self.load_brand_data()
    
    def setup_ui(self):
        """ایجاد رابط کاربری"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # عنوان
        title_label = QLabel("🏷️ فرم مدیریت برندها")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("font-size: 14pt; font-weight: bold; color: #ff9800;")
        layout.addWidget(title_label)
        
        # فیلد نام
        lbl_name = QLabel("نام برند:")
        self.txt_name = QLineEdit()
        self.txt_name.setPlaceholderText("مثال: Samsung, LG, Sony")
        
        layout.addWidget(lbl_name)
        layout.addWidget(self.txt_name)
        layout.addStretch()
        
        # دکمه‌ها
        button_layout = QHBoxLayout()
        
        self.btn_save = QPushButton("💾 ذخیره" if not self.brand_id else "💾 بروزرسانی")
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
                border: 1px solid #ff9800;
            }
        """)
    
    def load_brand_data(self):
        """بارگذاری اطلاعات برند"""
        try:
            if self.brand_id:
                query = "SELECT name FROM Brands WHERE id = ?"
                result = self.data_manager.db.fetch_one(query, (self.brand_id,))
                if result and 'name' in result:
                    self.txt_name.setText(result['name'])
        except Exception as e:
            print(f"خطا در بارگذاری اطلاعات برند: {e}")
    
    def on_save(self):
        """ذخیره برند"""
        try:
            name = self.txt_name.text().strip()
            if not name:
                QMessageBox.warning(self, "خطا", "نام برند الزامی است")
                return
            
            # بررسی تکراری بودن
            normalized_name = name.strip().replace(' ', '')
            
            if self.brand_id:
                # حالت ویرایش
                query_check = """
                SELECT COUNT(*) as count FROM Brands 
                WHERE REPLACE(name, ' ', '') = ? AND id != ?
                """
                check_result = self.data_manager.db.fetch_one(query_check, (normalized_name, self.brand_id))
                
                if check_result and check_result['count'] > 0:
                    QMessageBox.warning(self, "خطا", "این نام (یا نام مشابه) قبلاً ثبت شده است")
                    return
                
                query = "UPDATE Brands SET name = ? WHERE id = ?"
                params = (name, self.brand_id)
                message = "✅ برند ویرایش شد"
            else:
                # حالت افزودن جدید
                query_check = """
                SELECT COUNT(*) as count FROM Brands 
                WHERE REPLACE(name, ' ', '') = ?
                """
                check_result = self.data_manager.db.fetch_one(query_check, (normalized_name,))
                
                if check_result and check_result['count'] > 0:
                    QMessageBox.warning(self, "خطا", "این نام (یا نام مشابه) قبلاً ثبت شده است")
                    return
                
                query = "INSERT INTO Brands (name) VALUES (?)"
                params = (name,)
                message = "✅ برند جدید اضافه شد"
            
            success = self.data_manager.db.execute_query(query, params)
            
            if success:
                QMessageBox.information(self, "موفقیت", message)
                self.accept()
            else:
                QMessageBox.critical(self, "خطا", "❌ خطا در ذخیره‌سازی")
        
        except Exception as e:
            print(f"خطا در ذخیره برند: {e}")
            QMessageBox.critical(self, "خطا", f"❌ خطا: {str(e)}")