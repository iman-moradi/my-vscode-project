# ui/widgets/repair_widget.py
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                               QPushButton, QTableWidget, QTableWidgetItem,
                               QHeaderView, QMessageBox, QLineEdit)
from PySide6.QtCore import Qt, Signal

class RepairWidget(QWidget):
    """ویجت نمایش لیست تعمیرات"""
    
    repair_selected = Signal(int)  # شناسه تعمیر انتخاب شده
    
    def __init__(self, data_manager):
        super().__init__()
        self.data_manager = data_manager
        self.init_ui()
        self.refresh_data()
    
    def init_ui(self):
        """راه‌اندازی رابط کاربری"""
        layout = QVBoxLayout()
        
        # نوار جستجو
        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel("جستجو:"))
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("شماره پذیرش، مشتری، تعمیرکار...")
        self.search_input.textChanged.connect(self.refresh_data)
        search_layout.addWidget(self.search_input)
        
        btn_refresh = QPushButton("🔄 تازه‌سازی")
        btn_refresh.clicked.connect(self.refresh_data)
        search_layout.addWidget(btn_refresh)
        
        layout.addLayout(search_layout)
        
        # جدول تعمیرات
        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels([
            "ردیف", "شماره پذیرش", "مشتری", "دستگاه", "تعمیرکار", 
            "تاریخ تعمیر", "هزینه کل", "وضعیت"
        ])
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setAlternatingRowColors(True)
        self.table.doubleClicked.connect(self.on_row_double_clicked)
        
        # تنظیم عرض ستون‌ها
        self.table.setColumnWidth(0, 60)
        self.table.setColumnWidth(1, 120)
        self.table.setColumnWidth(2, 150)
        self.table.setColumnWidth(3, 150)
        self.table.setColumnWidth(4, 120)
        self.table.setColumnWidth(5, 100)
        self.table.setColumnWidth(6, 120)
        
        layout.addWidget(self.table)
        
        self.setLayout(layout)
    
    def refresh_data(self, search_text=""):
        """تازه‌سازی داده‌های جدول"""
        try:
            # در آینده با کوئری مناسب جایگزین شود
            # فعلاً یک پیام نمایش می‌دهیم
            self.table.setRowCount(1)
            self.table.setItem(0, 0, QTableWidgetItem("1"))
            self.table.setItem(0, 1, QTableWidgetItem("نمونه"))
            self.table.setItem(0, 2, QTableWidgetItem("در حال توسعه..."))
            
        except Exception as e:
            print(f"خطا در بارگذاری تعمیرات: {e}")
    
    def on_row_double_clicked(self, index):
        """هنگام دابل کلیک روی ردیف"""
        row = index.row()
        # در آینده پیاده‌سازی شود
        pass