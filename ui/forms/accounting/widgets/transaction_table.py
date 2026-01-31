# ui/forms/accounting/widgets/transaction_table.py
from PySide6.QtWidgets import QTableWidget, QTableWidgetItem

class TransactionTable(QTableWidget):
    """جدول تراکنش‌های حسابداری"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_table()
    
    def setup_table(self):
        """تنظیمات اولیه جدول"""
        self.setColumnCount(6)
        self.setHorizontalHeaderLabels([
            "تاریخ",
            "نوع",
            "از حساب",
            "به حساب", 
            "مبلغ (تومان)",
            "توضیحات"
        ])
        
        # تنظیمات ظاهری
        self.setAlternatingRowColors(True)
        self.horizontalHeader().setStretchLastSection(True)