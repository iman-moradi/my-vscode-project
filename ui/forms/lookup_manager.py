from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                               QPushButton, QLineEdit, QComboBox, QListWidget, 
                               QMessageBox, QInputDialog)
from PySide6.QtCore import Qt, Signal

class LookupManagerForm(QWidget):
    form_closed = Signal()
    
    def __init__(self, data_manager):
        super().__init__()
        self.data_manager = data_manager
        self.setWindowTitle("مدیریت لیست‌های ثابت")
        self.setMinimumSize(500, 400)
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # انتخاب دسته
        cat_layout = QHBoxLayout()
        cat_layout.addWidget(QLabel("دسته‌بندی:"))
        self.category_combo = QComboBox()
        self.category_combo.addItems(['device_type', 'device_brand'])
        self.category_combo.currentTextChanged.connect(self.load_values)
        cat_layout.addWidget(self.category_combo)
        layout.addLayout(cat_layout)
        
        # لیست مقادیر موجود
        self.values_list = QListWidget()
        layout.addWidget(QLabel("مقادیر موجود:"))
        layout.addWidget(self.values_list)
        
        # افزودن مقدار جدید
        add_layout = QHBoxLayout()
        self.new_value_input = QLineEdit()
        self.new_value_input.setPlaceholderText("مقدار جدید (مثل: 'تلویزیون')...")
        add_layout.addWidget(self.new_value_input)
        btn_add = QPushButton("➕ افزودن")
        btn_add.clicked.connect(self.add_new_value)
        add_layout.addWidget(btn_add)
        layout.addLayout(add_layout)
        
        # دکمه‌های پایانی
        btn_close = QPushButton("بستن")
        btn_close.clicked.connect(self.close)
        layout.addWidget(btn_close)
        
        self.setLayout(layout)
        self.load_values()
    
    def load_values(self):
        category = self.category_combo.currentText()
        values = self.data_manager.get_lookup_list(category)
        self.values_list.clear()
        self.values_list.addItems(values)
    
    def add_new_value(self):
        category = self.category_combo.currentText()
        new_value = self.new_value_input.text().strip()
        
        if not new_value:
            QMessageBox.warning(self, "خطا", "لطفاً مقداری وارد کنید.")
            return
        
        # بررسی عدم تکرار
        existing = self.data_manager.get_lookup_list(category)
        if new_value in existing:
            QMessageBox.warning(self, "تکراری", "این مقدار از قبل وجود دارد.")
            return
        
        # ذخیره در دیتابیس
        success = self.data_manager.lookup.add_value(category, new_value)
        if success:
            QMessageBox.information(self, "موفق", "مقدار جدید اضافه شد.")
            self.new_value_input.clear()
            self.load_values()
        else:
            QMessageBox.critical(self, "خطا", "خطا در ذخیره مقدار جدید.")

# میتوانید منوی این فرم را به main_window.py اضافه کنید.