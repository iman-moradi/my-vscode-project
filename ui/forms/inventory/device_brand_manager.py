# ui/forms/inventory/device_brand_manager.py
from PySide6.QtWidgets import QInputDialog, QMessageBox
from database.database import DatabaseManager

class DeviceBrandManager:
    """مدیریت نوع دستگاه‌ها و برندها"""
    
    def __init__(self, db):
        self.db = db
    
    def load_device_types(self, combobox, add_empty=True):
        """بارگذاری انواع دستگاه‌ها در کامبوباکس"""
        try:
            combobox.clear()
            if add_empty:
                combobox.addItem("انتخاب کنید", None)
            
            query = "SELECT id, name FROM DeviceCategories_name ORDER BY name"
            device_types = self.db.fetch_all(query)
            
            for dt in device_types:
                combobox.addItem(dt['name'], dt['id'])
                
        except Exception as e:
            print(f"خطا در بارگذاری انواع دستگاه‌ها: {e}")
    
    def load_brands(self, combobox, add_empty=True):
        """بارگذاری برندها در کامبوباکس"""
        try:
            combobox.clear()
            if add_empty:
                combobox.addItem("انتخاب کنید", None)
            
            query = "SELECT id, name FROM Brands ORDER BY name"
            brands = self.db.fetch_all(query)
            
            for brand in brands:
                combobox.addItem(brand['name'], brand['id'])
                
        except Exception as e:
            print(f"خطا در بارگذاری برندها: {e}")
    
    def add_device_type(self, parent):
        """افزودن نوع دستگاه جدید"""
        name, ok = QInputDialog.getText(
            parent, "افزودن نوع دستگاه جدید",
            "نام نوع دستگاه را وارد کنید:"
        )
        
        if ok and name.strip():
            try:
                query = "INSERT OR IGNORE INTO DeviceCategories_name (name) VALUES (?)"
                if self.db.execute_query(query, (name.strip(),)):
                    return True
            except Exception as e:
                QMessageBox.warning(parent, "خطا", f"خطا در افزودن نوع دستگاه: {str(e)}")
        
        return False
    
    def add_brand(self, parent):
        """افزودن برند جدید"""
        name, ok = QInputDialog.getText(
            parent, "افزودن برند جدید",
            "نام برند را وارد کنید:"
        )
        
        if ok and name.strip():
            try:
                query = "INSERT OR IGNORE INTO Brands (name) VALUES (?)"
                if self.db.execute_query(query, (name.strip(),)):
                    return True
            except Exception as e:
                QMessageBox.warning(parent, "خطا", f"خطا در افزودن برند: {str(e)}")
        
        return False