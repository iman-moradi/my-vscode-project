"""
جدول سفارشی برای نمایش آیتم‌های انبار
"""

from PySide6.QtWidgets import QTableWidget, QTableWidgetItem, QHeaderView, QMenu, QAbstractItemView
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor, QAction, QFont

class InventoryTable(QTableWidget):
    """جدول سفارشی انبار با قابلیت‌های اضافه"""
    
    item_double_clicked = Signal(dict)  # سیگنال دابل کلیک
    context_menu_requested = Signal(int, dict)  # سیگنال منوی راست کلیک
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_data = []
        self.setup_table()
        
    def setup_table(self):
        """تنظیمات اولیه جدول"""
        self.setAlternatingRowColors(True)
        self.setSelectionBehavior(QTableWidget.SelectRows)
        self.setSelectionMode(QTableWidget.SingleSelection)
        self.setEditTriggers(QTableWidget.NoEditTriggers)
        
        # تنظیم هدر
        header = self.horizontalHeader()
        header.setStretchLastSection(True)
        header.setDefaultAlignment(Qt.AlignRight | Qt.AlignVCenter)
        header.setSectionResizeMode(QHeaderView.Interactive)
        
        # تنظیم حداقل ارتفاع ردیف
        self.verticalHeader().setDefaultSectionSize(40)
        self.verticalHeader().setVisible(False)
        
        # فعال کردن منوی زمینه
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)
        
        # اتصال دابل کلیک
        self.itemDoubleClicked.connect(self.on_item_double_clicked)
    
    def load_data(self, data, columns):
        """بارگذاری داده‌ها در جدول"""
        self.current_data = data
        self.setColumnCount(len(columns))
        self.setHorizontalHeaderLabels(columns)
        self.setRowCount(len(data))
        
        for row, item in enumerate(data):
            for col, column_name in enumerate(columns):
                value = str(item.get(column_name, ''))
                table_item = QTableWidgetItem(value)
                
                # تنظیم تراز
                if column_name in ['ردیف', 'تعداد', 'سال تولید', 'قیمت']:
                    table_item.setTextAlignment(Qt.AlignCenter)
                else:
                    table_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                
                # رنگ‌آمیزی بر اساس وضعیت
                self.colorize_item(table_item, item, column_name)
                
                self.setItem(row, col, table_item)
        
        # تنظیم عرض ستون‌ها
        self.resize_columns()
    
    def colorize_item(self, item, row_data, column_name):
        """رنگ‌آمیزی سلول بر اساس داده‌ها"""
        if column_name == 'وضعیت':
            status = row_data.get('status', '')
            if status == 'موجود':
                item.setBackground(QColor('#27ae60'))
                item.setForeground(QColor('white'))
            elif status == 'موجودی کم':
                item.setBackground(QColor('#f39c12'))
                item.setForeground(QColor('white'))
            elif status == 'ناموجود':
                item.setBackground(QColor('#e74c3c'))
                item.setForeground(QColor('white'))
            elif status == 'رزرو شده':
                item.setBackground(QColor('#3498db'))
                item.setForeground(QColor('white'))
                
        elif column_name == 'تعداد':
            quantity = row_data.get('quantity', 0)
            min_stock = row_data.get('min_stock', 5)
            
            if quantity == 0:
                item.setBackground(QColor('#e74c3c'))
                item.setForeground(QColor('white'))
            elif quantity <= min_stock:
                item.setBackground(QColor('#f39c12'))
                item.setForeground(QColor('white'))
    
    def resize_columns(self):
        """تنظیم خودکار عرض ستون‌ها"""
        header = self.horizontalHeader()
        for i in range(self.columnCount()):
            header.setSectionResizeMode(i, QHeaderView.ResizeToContents)
            current_width = header.sectionSize(i)
            header.resizeSection(i, min(current_width, 250))
    
    def show_context_menu(self, position):
        """نمایش منوی راست کلیک"""
        row = self.rowAt(position.y())
        if row >= 0 and row < len(self.current_data):
            menu = QMenu()
            
            edit_action = QAction('✏️ ویرایش', self)
            delete_action = QAction('🗑️ حذف', self)
            view_action = QAction('👁️ مشاهده جزئیات', self)
            transfer_action = QAction('🔄 انتقال موجودی', self)
            
            menu.addAction(edit_action)
            menu.addAction(view_action)
            menu.addSeparator()
            menu.addAction(transfer_action)
            menu.addSeparator()
            menu.addAction(delete_action)
            
            # اجرای اکشن انتخاب شده
            action = menu.exec_(self.mapToGlobal(position))
            
            if action == edit_action:
                self.context_menu_requested.emit(row, {'action': 'edit'})
            elif action == delete_action:
                self.context_menu_requested.emit(row, {'action': 'delete'})
            elif action == view_action:
                self.context_menu_requested.emit(row, {'action': 'view'})
            elif action == transfer_action:
                self.context_menu_requested.emit(row, {'action': 'transfer'})
    
    def on_item_double_clicked(self, item):
        """هنگام دابل کلیک روی آیتم"""
        row = item.row()
        if row < len(self.current_data):
            self.item_double_clicked.emit(self.current_data[row])
    
    def get_selected_row_data(self):
        """دریافت داده‌های ردیف انتخاب شده"""
        selected_rows = self.selectionModel().selectedRows()
        if selected_rows:
            row = selected_rows[0].row()
            if row < len(self.current_data):
                return self.current_data[row]
        return None