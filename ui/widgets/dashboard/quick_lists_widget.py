# ui/widgets/dashboard/quick_lists_widget.py
"""
ویجت لیست‌های سریع برای دسترسی آسان
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QFrame, QPushButton, QTableWidget,
    QTableWidgetItem, QHeaderView, QAbstractItemView,
    QScrollArea
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QColor, QBrush


class QuickListWidget(QFrame):
    """ویجت لیست سریع"""
    
    item_clicked = Signal(dict)  # سیگنال کلیک روی آیتم
    
    def __init__(self, title, icon="📋", color="#3498db", parent=None):
        super().__init__(parent)
        self.title = title
        self.icon = icon
        self.color = color
        self.items = []
        self.setup_ui()
        self.apply_style()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)
        
        # هدر لیست
        header_layout = QHBoxLayout()
        
        # آیکون و عنوان
        icon_label = QLabel(self.icon)
        icon_label.setStyleSheet(f"font-size: 20px; color: {self.color};")
        
        title_label = QLabel(self.title)
        title_label.setStyleSheet("""
            font-size: 14px;
            font-weight: bold;
            color: white;
        """)
        
        header_layout.addWidget(icon_label)
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        
        layout.addLayout(header_layout)
        
        # جدول آیتم‌ها
        self.table = QTableWidget()
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(['آیتم', 'وضعیت'])
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setAlternatingRowColors(True)
        self.table.setShowGrid(False)
        
        # استایل جدول
        self.table.setStyleSheet("""
            QTableWidget {
                background-color: #1a1a1a;
                alternate-background-color: #222;
                border: none;
                border-radius: 5px;
                font-size: 11px;
            }
            QTableWidget::item {
                padding: 8px;
                color: #ddd;
                border-bottom: 1px solid #333;
            }
            QTableWidget::item:selected {
                background-color: #2c3e50;
                color: white;
            }
            QHeaderView::section {
                background-color: #2c3e50;
                color: white;
                padding: 8px;
                border: none;
                font-weight: bold;
                font-size: 11px;
            }
        """)
        
        # تنظیم اندازه ستون‌ها
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        
        self.table.cellClicked.connect(self.on_item_clicked)
        
        layout.addWidget(self.table)
        
        # دکمه مشاهده بیشتر
        self.more_btn = QPushButton("مشاهده بیشتر →")
        self.more_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: rgba({int(self.color[1:3], 16)}, {int(self.color[3:5], 16)}, {int(self.color[5:7], 16)}, 0.2);
                color: {self.color};
                border: 1px solid {self.color};
                border-radius: 5px;
                padding: 8px;
                font-size: 11px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: rgba({int(self.color[1:3], 16)}, {int(self.color[3:5], 16)}, {int(self.color[5:7], 16)}, 0.4);
            }}
        """)
        self.more_btn.clicked.connect(self.on_more_clicked)
        
        layout.addWidget(self.more_btn)
    
    def apply_style(self):
        """اعمال استایل"""
        self.setStyleSheet(f"""
            QuickListWidget {{
                background-color: #1e1e1e;
                border-radius: 10px;
                border: 2px solid {self.color};
            }}
        """)
    
    def set_items(self, items, columns=None):
        """تنظیم آیتم‌های لیست"""
        self.items = items
        
        if not items:
            self.table.setRowCount(0)
            return
        
        if columns:
            self.table.setColumnCount(len(columns))
            self.table.setHorizontalHeaderLabels(columns)
        
        self.table.setRowCount(len(items))
        
        for row, item in enumerate(items):
            if isinstance(item, dict):
                # اگر آیتم دیکشنری است
                for col, key in enumerate(item.keys()):
                    value = item[key]
                    table_item = QTableWidgetItem(str(value))
                    
                    # رنگ‌آمیزی بر اساس نوع داده
                    if key == 'status' or key == 'وضعیت':
                        self.colorize_status(table_item, str(value))
                    elif key == 'amount' or key == 'مبلغ':
                        table_item.setText(f"{value:,} تومان")
                        table_item.setForeground(QBrush(QColor('#2ecc71')))
                    
                    self.table.setItem(row, col, table_item)
            else:
                # اگر آیتم ساده است
                table_item = QTableWidgetItem(str(item))
                self.table.setItem(row, 0, table_item)
    
    def colorize_status(self, item, status):
        """رنگ‌آمیزی وضعیت"""
        colors = {
            'فوری': '#e74c3c',
            'خیلی فوری': '#c0392b',
            'عادی': '#3498db',
            'در انتظار': '#f39c12',
            'در حال تعمیر': '#3498db',
            'تعمیر شده': '#27ae60',
            'تحویل داده شده': '#9b59b6',
            'وصول نشده': '#e74c3c',
            'وصول شده': '#27ae60',
            'پاس شده': '#2ecc71',
            'موجود': '#27ae60',
            'ناموجود': '#e74c3c'
        }
        
        color = colors.get(status, '#cccccc')
        item.setForeground(QBrush(QColor(color)))
    
    def on_item_clicked(self, row, column):
        """کلیک روی آیتم"""
        if row < len(self.items):
            item = self.items[row]
            self.item_clicked.emit({
                'type': 'list_item',
                'list_type': self.title,
                'item': item,
                'row': row
            })
    
    def on_more_clicked(self):
        """کلیک روی دکمه مشاهده بیشتر"""
        self.item_clicked.emit({
            'type': 'view_more',
            'list_type': self.title
        })


class QuickListsWidget(QWidget):
    """ویجت لیست‌های سریع داشبورد"""
    
    list_action_triggered = Signal(dict)  # سیگنال عمل روی لیست
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.dashboard_manager = None
        self.lists = {}
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(15)
        
        # عنوان
        title_label = QLabel("⚡ دسترسی سریع")
        title_label.setStyleSheet("""
            font-size: 16px;
            font-weight: bold;
            color: #3498db;
            padding-bottom: 10px;
            border-bottom: 2px solid #3498db;
        """)
        layout.addWidget(title_label)
        
        # Grid برای لیست‌ها
        self.grid_layout = QGridLayout()
        self.grid_layout.setSpacing(15)
        self.grid_layout.setHorizontalSpacing(15)
        self.grid_layout.setVerticalSpacing(15)
        
        layout.addLayout(self.grid_layout)
        
        # ایجاد لیست‌های اولیه
        self.create_lists()
    
    def create_lists(self):
        """ایجاد لیست‌های اولیه"""
        list_definitions = [
            {
                'key': 'urgent_receptions',
                'title': 'پذیرش‌های فوری',
                'icon': '🚨',
                'color': '#e74c3c',
                'columns': ['شماره پذیرش', 'مشتری', 'اولویت', 'وضعیت']
            },
            {
                'key': 'due_checks',
                'title': 'چک‌های سررسید',
                'icon': '💳',
                'color': '#f39c12',
                'columns': ['شماره چک', 'بانک', 'مبلغ', 'سررسید']
            },
            {
                'key': 'low_stock',
                'title': 'موجودی‌های کم',
                'icon': '⚠️',
                'color': '#d35400',
                'columns': ['کد قطعه', 'نام قطعه', 'موجودی', 'حداقل']
            },
            {
                'key': 'waiting_customers',
                'title': 'مشتریان منتظر',
                'icon': '👥',
                'color': '#3498db',
                'columns': ['نام مشتری', 'تلفن', 'تعداد', 'آخرین پذیرش']
            }
        ]
        
        self.lists = {}
        
        for i, list_def in enumerate(list_definitions):
            row = i // 2
            col = i % 2
            
            list_widget = QuickListWidget(
                title=list_def['title'],
                icon=list_def['icon'],
                color=list_def['color']
            )
            
            list_widget.item_clicked.connect(self.on_list_item_clicked)
            
            self.lists[list_def['key']] = {
                'widget': list_widget,
                'columns': list_def['columns'],
                'type': list_def['key']
            }
            
            self.grid_layout.addWidget(list_widget, row, col)
    
    def set_dashboard_manager(self, dashboard_manager):
        """تنظیم مدیر داشبورد"""
        self.dashboard_manager = dashboard_manager
    
    def update_lists(self, lists_data):
        """بروزرسانی لیست‌ها"""
        if not lists_data:
            return
        
        for list_key, list_info in self.lists.items():
            if list_key in lists_data:
                items = lists_data[list_key]
                list_info['widget'].set_items(items, list_info['columns'])
            else:
                list_info['widget'].set_items([])
    
    def on_list_item_clicked(self, data):
        """کلیک روی آیتم لیست"""
        self.list_action_triggered.emit(data)
    
    def refresh_lists(self):
        """بروزرسانی لیست‌ها"""
        if self.dashboard_manager:
            lists_data = self.dashboard_manager.get_quick_lists()
            self.update_lists(lists_data)
    
    def clear_lists(self):
        """پاک کردن لیست‌ها"""
        for list_info in self.lists.values():
            list_info['widget'].set_items([])


if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication
    import sys
    
    app = QApplication(sys.argv)
    
    widget = QuickListsWidget()
    widget.setFixedSize(900, 600)
    widget.show()
    
    # تست با داده‌های نمونه
    test_lists = {
        'urgent_receptions': [
            {
                'شماره پذیرش': '1001',
                'مشتری': 'علی محمدی',
                'اولویت': 'خیلی فوری',
                'وضعیت': 'در انتظار'
            },
            {
                'شماره پذیرش': '1002',
                'مشتری': 'رضا کریمی',
                'اولویت': 'فوری',
                'وضعیت': 'در حال تعمیر'
            },
            {
                'شماره پذیرش': '1003',
                'مشتری': 'سارا احمدی',
                'اولویت': 'فوری',
                'وضعیت': 'در انتظار'
            }
        ],
        'due_checks': [
            {
                'شماره چک': '12345',
                'بانک': 'ملی',
                'مبلغ': 5000000,
                'سررسید': '1404/11/05'
            },
            {
                'شماره چک': '12346',
                'بانک': 'صادرات',
                'مبلغ': 3000000,
                'سررسید': '1404/11/06'
            }
        ],
        'low_stock': [
            {
                'کد قطعه': 'CP-100',
                'نام قطعه': 'کمپرسور یخچال',
                'موجودی': 2,
                'حداقل': 5
            },
            {
                'کد قطعه': 'FAN-50',
                'نام قطعه': 'فن پنکه',
                'موجودی': 3,
                'حداقل': 10
            }
        ],
        'waiting_customers': [
            {
                'نام مشتری': 'محمد حسینی',
                'تلفن': '09123456789',
                'تعداد': 2,
                'آخرین پذیرش': '1404/11/01'
            }
        ]
    }
    
    widget.update_lists(test_lists)
    
    sys.exit(app.exec())