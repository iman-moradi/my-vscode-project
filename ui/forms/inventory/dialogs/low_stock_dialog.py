"""
دیالوگ نمایش آیتم‌های با موجودی کم
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QTableWidget, QTableWidgetItem,
    QGroupBox, QHeaderView, QCheckBox, QMessageBox, QWidget
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor, QFont

class LowStockDialog(QDialog):
    """دیالوگ هشدار موجودی کم"""
    
    order_created = Signal(list)  # سیگنال ایجاد سفارش
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("هشدار موجودی کم")
        self.setMinimumSize(800, 500)
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # هدر
        header_label = QLabel("⚠️ هشدار موجودی کم")
        header_label.setStyleSheet("""
            QLabel {
                color: #e74c3c;
                font-size: 16pt;
                font-weight: bold;
                padding: 10px;
                text-align: center;
            }
        """)
        layout.addWidget(header_label)
        
        # توضیح
        explanation_label = QLabel("موارد زیر به حداقل موجودی رسیده یا از آن کمتر هستند. لطفاً برای سفارش اقدام کنید.")
        explanation_label.setStyleSheet("color: #f39c12; font-size: 11pt; padding: 5px;")
        explanation_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(explanation_label)
        
        # جدول آیتم‌های کمبود
        table_group = QGroupBox("📋 لیست آیتم‌های با موجودی کم")
        table_group.setStyleSheet("""
            QGroupBox {
                border: 2px solid #f39c12;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 15px;
                font-weight: bold;
            }
        """)
        table_layout = QVBoxLayout()
        
        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels([
            "انتخاب",
            "ردیف",
            "کد/مدل",
            "نام آیتم",
            "موجودی فعلی",
            "حداقل",
            "تفاضل",
            "وضعیت"
        ])
        
        # تنظیمات جدول
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        
        header = self.table.horizontalHeader()
        header.setStretchLastSection(True)
        header.setDefaultAlignment(Qt.AlignRight | Qt.AlignVCenter)
        
        # تنظیم عرض ستون‌ها
        self.table.setColumnWidth(0, 60)
        self.table.setColumnWidth(1, 60)
        self.table.setColumnWidth(2, 120)
        self.table.setColumnWidth(3, 200)
        self.table.setColumnWidth(4, 100)
        self.table.setColumnWidth(5, 80)
        self.table.setColumnWidth(6, 80)
        
        table_layout.addWidget(self.table)
        table_group.setLayout(table_layout)
        layout.addWidget(table_group)
        
        # دکمه انتخاب/عدم انتخاب همه
        selection_layout = QHBoxLayout()
        
        self.select_all_checkbox = QCheckBox("انتخاب همه")
        self.select_all_checkbox.stateChanged.connect(self.toggle_select_all)
        
        selection_layout.addWidget(self.select_all_checkbox)
        selection_layout.addStretch()
        
        layout.addLayout(selection_layout)
        
        # آمار
        stats_group = QGroupBox("📊 آمار کمبود")
        stats_group.setStyleSheet("""
            QGroupBox {
                border: 2px solid #3498db;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 15px;
                font-weight: bold;
            }
        """)
        stats_layout = QVBoxLayout()
        
        stats_row1 = QHBoxLayout()
        self.total_items_label = QLabel("تعداد کل آیتم‌ها: 0")
        self.total_items_label.setStyleSheet("color: #3498db; font-weight: bold;")
        
        self.critical_items_label = QLabel("آیتم‌های بحرانی: 0")
        self.critical_items_label.setStyleSheet("color: #e74c3c; font-weight: bold;")
        
        stats_row1.addWidget(self.critical_items_label)
        stats_row1.addWidget(self.total_items_label)
        stats_row1.addStretch()
        
        stats_row2 = QHBoxLayout()
        self.needed_total_label = QLabel("کل تعداد مورد نیاز: 0")
        self.needed_total_label.setStyleSheet("color: #27ae60; font-weight: bold;")
        
        stats_row2.addWidget(self.needed_total_label)
        stats_row2.addStretch()
        
        stats_layout.addLayout(stats_row1)
        stats_layout.addLayout(stats_row2)
        stats_group.setLayout(stats_layout)
        layout.addWidget(stats_group)
        
        # دکمه‌ها
        button_layout = QHBoxLayout()
        
        self.order_btn = QPushButton("📦 ایجاد سفارش برای موارد انتخاب شده")
        self.order_btn.clicked.connect(self.create_order)
        self.order_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 12px 24px;
                font-weight: bold;
                font-size: 11pt;
            }
            QPushButton:hover {
                background-color: #219653;
            }
        """)
        
        self.ignore_btn = QPushButton("👁️ فقط مشاهده")
        self.ignore_btn.clicked.connect(self.ignore_warning)
        self.ignore_btn.setStyleSheet("""
            QPushButton {
                background-color: #95a5a6;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 12px 24px;
                font-weight: bold;
                font-size: 11pt;
            }
            QPushButton:hover {
                background-color: #7f8c8d;
            }
        """)
        
        button_layout.addWidget(self.order_btn)
        button_layout.addWidget(self.ignore_btn)
        button_layout.addStretch()
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
        
        # ذخیره داده‌ها
        self.low_stock_items = []
        self.selected_items = []
    
    def load_low_stock_items(self, items):
        """بارگذاری آیتم‌های با موجودی کم"""
        self.low_stock_items = items
        self.table.setRowCount(len(items))
        
        total_items = len(items)
        critical_items = 0
        total_needed = 0
        
        for row, item in enumerate(items):
            # ستون انتخاب
            checkbox = QCheckBox()
            checkbox_widget = QWidget()
            checkbox_layout = QHBoxLayout()
            checkbox_layout.addWidget(checkbox)
            checkbox_layout.setAlignment(Qt.AlignCenter)
            checkbox_layout.setContentsMargins(0, 0, 0, 0)
            checkbox_widget.setLayout(checkbox_layout)
            self.table.setCellWidget(row, 0, checkbox_widget)
            
            # ردیف
            self.table.setItem(row, 1, QTableWidgetItem(str(row + 1)))
            self.table.item(row, 1).setTextAlignment(Qt.AlignCenter)
            
            # کد/مدل
            code = item.get('part_code') or item.get('model') or f"ID-{item.get('id', row+1)}"
            self.table.setItem(row, 2, QTableWidgetItem(code))
            
            # نام آیتم
            name = item.get('part_name') or item.get('model') or item.get('device_type_name', 'نامشخص')
            self.table.setItem(row, 3, QTableWidgetItem(name))
            
            # موجودی فعلی
            current_qty = item.get('quantity', 0)
            current_item = QTableWidgetItem(str(current_qty))
            current_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row, 4, current_item)
            
            # حداقل موجودی
            min_stock = item.get('min_stock', 5)
            min_item = QTableWidgetItem(str(min_stock))
            min_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row, 5, min_item)
            
            # تفاضل مورد نیاز
            needed = max(0, min_stock - current_qty)
            needed_item = QTableWidgetItem(str(needed))
            needed_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row, 6, needed_item)
            
            # وضعیت
            if current_qty == 0:
                status = "⛔ تمام شده"
                status_color = "#e74c3c"
                critical_items += 1
            elif current_qty <= min_stock * 0.3:
                status = "🔥 بحرانی"
                status_color = "#e74c3c"
                critical_items += 1
            elif current_qty <= min_stock * 0.7:
                status = "⚠️ کمبود"
                status_color = "#f39c12"
            else:
                status = "📉 نزدیک به حداقل"
                status_color = "#f1c40f"
            
            status_item = QTableWidgetItem(status)
            status_item.setTextAlignment(Qt.AlignCenter)
            status_item.setForeground(QColor(status_color))
            self.table.setItem(row, 7, status_item)
            
            # رنگ‌آمیزی ردیف
            if current_qty == 0:
                for col in range(8):
                    cell = self.table.item(row, col)
                    if cell:
                        cell.setBackground(QColor('#ffcccc'))
            elif current_qty <= min_stock * 0.3:
                for col in range(8):
                    cell = self.table.item(row, col)
                    if cell:
                        cell.setBackground(QColor('#ffe6cc'))
            
            total_needed += needed
        
        # به‌روزرسانی آمار
        self.total_items_label.setText(f"تعداد کل آیتم‌ها: {total_items}")
        self.critical_items_label.setText(f"آیتم‌های بحرانی: {critical_items}")
        self.needed_total_label.setText(f"کل تعداد مورد نیاز: {total_needed}")
        
        # انتخاب خودکار موارد بحرانی
        self.auto_select_critical()
    
    def auto_select_critical(self):
        """انتخاب خودکار موارد بحرانی"""
        for row, item in enumerate(self.low_stock_items):
            current_qty = item.get('quantity', 0)
            min_stock = item.get('min_stock', 5)
            
            if current_qty == 0 or current_qty <= min_stock * 0.3:
                checkbox_widget = self.table.cellWidget(row, 0)
                checkbox = checkbox_widget.layout().itemAt(0).widget()
                checkbox.setChecked(True)
    
    def toggle_select_all(self, state):
        """انتخاب یا عدم انتخاب همه موارد"""
        for row in range(self.table.rowCount()):
            checkbox_widget = self.table.cellWidget(row, 0)
            if checkbox_widget:
                checkbox = checkbox_widget.layout().itemAt(0).widget()
                checkbox.setChecked(state == Qt.Checked)
    
    def get_selected_items(self):
        """دریافت آیتم‌های انتخاب شده"""
        selected = []
        for row in range(self.table.rowCount()):
            checkbox_widget = self.table.cellWidget(row, 0)
            if checkbox_widget:
                checkbox = checkbox_widget.layout().itemAt(0).widget()
                if checkbox.isChecked() and row < len(self.low_stock_items):
                    item = self.low_stock_items[row].copy()
                    
                    # محاسبه تعداد مورد نیاز
                    current_qty = item.get('quantity', 0)
                    min_stock = item.get('min_stock', 5)
                    item['needed_quantity'] = max(0, min_stock - current_qty)
                    
                    selected.append(item)
        
        return selected
    
    def create_order(self):
        """ایجاد سفارش برای موارد انتخاب شده"""
        selected_items = self.get_selected_items()
        
        if not selected_items:
            QMessageBox.warning(self, "خطا", "لطفاً حداقل یک آیتم را انتخاب کنید.")
            return
        
        # نمایش خلاصه سفارش
        total_items = len(selected_items)
        total_quantity = sum(item['needed_quantity'] for item in selected_items)
        
        reply = QMessageBox.question(
            self,
            "تایید سفارش",
            f"آیا از ایجاد سفارش برای {total_items} آیتم به میزان {total_quantity} عدد اطمینان دارید؟",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.Yes
        )
        
        if reply == QMessageBox.Yes:
            self.order_created.emit(selected_items)
            self.accept()
    
    def ignore_warning(self):
        """نادیده گرفتن هشدار"""
        self.reject()