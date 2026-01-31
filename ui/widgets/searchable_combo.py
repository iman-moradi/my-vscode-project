# ui/widgets/searchable_combo.py - نسخه کامل با پشتیبانی فیلتر

from PySide6.QtWidgets import QComboBox, QLineEdit
from PySide6.QtCore import Qt, Signal
import sys
import os

class SearchableCombo(QComboBox):
    """کامبوباکس قابل جستجو با پشتیبانی از فیلتر"""
    
    item_selected = Signal(str)  # سیگنال هنگام انتخاب آیتم
    
    def __init__(self, data_manager, table_name, display_field, 
                 filter_field=None, filter_value=None, parent=None):
        super().__init__(parent)
        self.data_manager = data_manager
        self.table_name = table_name
        self.display_field = display_field
        self.filter_field = filter_field
        self.filter_value = filter_value
        
        self.setup_ui()
        self.refresh()
    
    def setup_ui(self):
        """تنظیم رابط کاربری"""
        self.setEditable(True)
        self.lineEdit().setPlaceholderText("جستجو...")
        self.lineEdit().textChanged.connect(self.filter_items)
        
        # راست‌چین
        self.setLayoutDirection(Qt.RightToLeft)
        
        # استایل
        self.setStyleSheet("""
            QComboBox {
                background-color: #1a1a1a;
                color: #ffffff;
                border: 1px solid #333;
                border-radius: 4px;
                padding: 8px;
                font-size: 11pt;
                font-family: 'B Nazanin';
                min-height: 35px;
            }
            
            QComboBox QAbstractItemView {
                background-color: #1a1a1a;
                color: #ffffff;
                border: 1px solid #333;
                selection-background-color: #2a5caa;
                font-family: 'B Nazanin';
            }
            
            QLineEdit {
                background-color: transparent;
                color: #ffffff;
                selection-background-color: #2a5caa;
                font-family: 'B Nazanin';
            }
        """)
    
    def refresh(self):
        """بارگذاری مجدد داده‌ها"""
        self.clear()
        
        try:
            # ساخت کوئری بر اساس فیلتر
            if self.filter_field and self.filter_value:
                query = f"""
                SELECT DISTINCT {self.display_field} 
                FROM {self.table_name} 
                WHERE {self.filter_field} = ?
                ORDER BY {self.display_field}
                """
                params = (self.filter_value,)
            else:
                query = f"""
                SELECT DISTINCT {self.display_field} 
                FROM {self.table_name} 
                ORDER BY {self.display_field}
                """
                params = ()
            
            items = self.data_manager.db.fetch_all(query, params)
            
            # اضافه کردن آیتم‌ها
            self.addItem("-- انتخاب کنید --", None)
            
            if items:
                for item in items:
                    value = item.get(self.display_field, '')
                    if value and value != 'None':
                        self.addItem(str(value), value)
            
            # ذخیره تمام آیتم‌ها برای فیلتر کردن
            self.all_items = []
            for i in range(self.count()):
                self.all_items.append(self.itemText(i))
                
        except Exception as e:
            print(f"❌ خطا در بارگذاری {self.table_name}: {e}")
            import traceback
            traceback.print_exc()
            self.addItem("⚠️ خطا در بارگذاری", None)
    
    def filter_items(self, text):
        """فیلتر کردن آیتم‌ها بر اساس متن جستجو"""
        if not hasattr(self, 'all_items'):
            return
        
        self.clear()
        
        if not text.strip():
            # اگر متن خالی است، همه آیتم‌ها را نشان بده
            for item in self.all_items:
                self.addItem(item)
        else:
            # فیلتر بر اساس متن
            search_text = text.strip().lower()
            for item in self.all_items:
                if search_text in item.lower():
                    self.addItem(item)
        
        # نمایش دراپ‌داون
        self.showPopup()
    
    def set_current_text(self, text):
        """تنظیم متن فعلی"""
        if not text:
            return
        
        index = self.findText(text, Qt.MatchFixedString)
        if index >= 0:
            self.setCurrentIndex(index)
    
    def current_text(self):
        """دریافت متن فعلی"""
        return self.currentText()
    
    def get_selected_value(self):
        """دریافت مقدار انتخاب شده"""
        current_text = self.currentText()
        if current_text == "-- انتخاب کنید --":
            return None
        return current_text