# ui/widgets/dashboard/stats_cards_widget.py
"""
ویجت کارت‌های آماری داشبورد
"""

from PySide6.QtWidgets import (
    QWidget, QGridLayout, QVBoxLayout, QHBoxLayout,
    QLabel, QFrame, QPushButton
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont, QColor, QLinearGradient, QBrush
import math


class StatsCard(QFrame):
    """کارت آماری تک"""
    
    def __init__(self, title, value, icon="📊", color="#3498db", description="", parent=None):
        super().__init__(parent)
        self.title = title
        self.value = value
        self.icon = icon
        self.color = color
        self.description = description
        
        self.setup_ui()
        self.apply_style()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)
        
        # هدر کارت
        header_layout = QHBoxLayout()
        
        # آیکون
        icon_label = QLabel(self.icon)
        icon_label.setStyleSheet(f"font-size: 24px; color: {self.color};")
        
        # عنوان
        title_label = QLabel(self.title)
        title_label.setStyleSheet("""
            font-size: 13px;
            font-weight: bold;
            color: #bbb;
        """)
        
        header_layout.addWidget(icon_label)
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        
        layout.addLayout(header_layout)
        
        # مقدار
        self.value_label = QLabel(str(self.value))
        self.value_label.setStyleSheet(f"""
            font-size: 28px;
            font-weight: bold;
            color: {self.color};
            margin-top: 5px;
        """)
        self.value_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.value_label)
        
        # توضیحات (اختیاری)
        if self.description:
            desc_label = QLabel(self.description)
            desc_label.setStyleSheet("""
                font-size: 11px;
                color: #999;
                font-style: italic;
            """)
            desc_label.setAlignment(Qt.AlignCenter)
            layout.addWidget(desc_label)
    
    def apply_style(self):
        """اعمال استایل زیبا با گرادیانت"""
        gradient = QLinearGradient(0, 0, self.width(), 0)
        gradient.setColorAt(0, QColor(30, 30, 30))  # تیره
        gradient.setColorAt(1, QColor(40, 40, 40))  # کمی روشن‌تر
        
        border_color = QColor(self.color)
        border_color.setAlpha(100)  # شفافیت
        
        self.setStyleSheet(f"""
            StatsCard {{
                background-color: #1e1e1e;
                border-radius: 12px;
                border: 2px solid rgba({border_color.red()}, {border_color.green()}, {border_color.blue()}, 100);
                min-width: 180px;
                min-height: 120px;
            }}
            StatsCard:hover {{
                border: 2px solid {self.color};
                background-color: #252525;
            }}
        """)
    
    def update_value(self, new_value, new_description=""):
        """بروزرسانی مقدار کارت"""
        self.value = new_value
        self.value_label.setText(str(new_value))
        
        if new_description:
            self.description = new_description
            # اگر توضیحات داریم، آن را هم بروزرسانی می‌کنیم


class AnimatedStatsCard(StatsCard):
    """کارت آماری با انیمیشن"""
    
    def __init__(self, title, value, icon="📊", color="#3498db", description="", parent=None):
        super().__init__(title, value, icon, color, description, parent)
        self.animation_timer = QTimer()
        self.animation_timer.timeout.connect(self.animate_value)
        self.target_value = value
        self.current_value = 0
        self.animation_speed = 5
    
    def animate_to_value(self, target_value):
        """انیمیشن به مقدار هدف"""
        self.target_value = target_value
        
        if isinstance(target_value, (int, float)):
            self.animation_timer.start(20)  # هر 20ms
    
    def animate_value(self):
        """انیمیشن مقدار"""
        diff = self.target_value - self.current_value
        
        if abs(diff) < 1:
            self.current_value = self.target_value
            self.animation_timer.stop()
        else:
            self.current_value += diff / self.animation_speed
        
        # نمایش مقدار (با فرمت مناسب)
        if isinstance(self.target_value, (int, float)):
            display_value = math.ceil(self.current_value)
            if self.target_value >= 1000:
                display_text = f"{display_value:,}"
            else:
                display_text = str(display_value)
        else:
            display_text = str(self.target_value)
        
        self.value_label.setText(display_text)


class StatsCardsWidget(QWidget):
    """ویجت مجموعه کارت‌های آماری"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.dashboard_manager = None
        self.stats_cards = {}
        self.setup_ui()
    
    def setup_ui(self):
        layout = QGridLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(15)
        layout.setHorizontalSpacing(15)
        layout.setVerticalSpacing(15)
        
        # 4 ستون برای دسکتاپ
        self.columns = 4
        
        # ایجاد کارت‌های خالی اولیه
        self.create_initial_cards()
    
    def create_initial_cards(self):
        """ایجاد کارت‌های اولیه"""
        # پاک کردن کارت‌های قبلی
        for i in reversed(range(self.layout().count())):
            widget = self.layout().itemAt(i).widget()
            if widget:
                widget.deleteLater()
        
        # تعریف کارت‌های مختلف
        card_definitions = [
            {
                'key': 'today_receptions',
                'title': '📅 پذیرش امروز',
                'icon': '📅',
                'color': '#3498db',
                'description': 'تعداد پذیرش‌های امروز',
                'format': 'number'
            },
            {
                'key': 'repairing_devices',
                'title': '🔧 در حال تعمیر',
                'icon': '🔧',
                'color': '#f39c12',
                'description': 'دستگاه‌های در حال تعمیر',
                'format': 'number'
            },
            {
                'key': 'completed_today',
                'title': '✅ تکمیل شده',
                'icon': '✅',
                'color': '#27ae60',
                'description': 'تعمیرات تکمیل شده امروز',
                'format': 'number'
            },
            {
                'key': 'today_income',
                'title': '💰 درآمد امروز',
                'icon': '💰',
                'color': '#2ecc71',
                'description': 'درآمد نقدی امروز',
                'format': 'currency'
            },
            {
                'key': 'profit_today',
                'title': '📈 سود امروز',
                'icon': '📈',
                'color': '#9b59b6',
                'description': 'سود خالص امروز',
                'format': 'currency'
            },
            {
                'key': 'new_customers',
                'title': '👥 مشتریان جدید',
                'icon': '👥',
                'color': '#1abc9c',
                'description': 'مشتریان ثبت‌نام کرده امروز',
                'format': 'number'
            },
            {
                'key': 'low_stock_items',
                'title': '⚠️ موجودی کم',
                'icon': '⚠️',
                'color': '#e74c3c',
                'description': 'قطعات با موجودی زیر حداقل',
                'format': 'number'
            },
            {
                'key': 'due_checks',
                'title': '💳 چک سررسید',
                'icon': '💳',
                'color': '#d35400',
                'description': 'چک‌های در سررسید ۳ روز آینده',
                'format': 'count_amount'
            }
        ]
        
        # ایجاد کارت‌ها
        self.stats_cards = {}
        for i, card_def in enumerate(card_definitions):
            row = i // self.columns
            col = i % self.columns
            
            card = AnimatedStatsCard(
                title=card_def['title'],
                value=0,
                icon=card_def['icon'],
                color=card_def['color'],
                description=card_def['description']
            )
            
            self.stats_cards[card_def['key']] = {
                'widget': card,
                'format': card_def['format']
            }
            
            self.layout().addWidget(card, row, col)
    
    def set_dashboard_manager(self, dashboard_manager):
        """تنظیم مدیر داشبورد"""
        self.dashboard_manager = dashboard_manager
    
    def update_stats(self, stats_data):
        """بروزرسانی آمار کارت‌ها"""
        if not stats_data:
            return
        
        for key, card_info in self.stats_cards.items():
            widget = card_info['widget']
            format_type = card_info['format']
            
            if key in stats_data:
                value = stats_data[key]
                
                if format_type == 'currency':
                    # فرمت ارز: 1,000,000 تومان
                    if isinstance(value, (int, float)):
                        display_value = f"{value:,.0f} تومان"
                        widget.animate_to_value(value)
                elif format_type == 'count_amount':
                    # برای داده‌های ترکیبی مانند چک‌ها
                    if isinstance(value, dict):
                        count = value.get('count', 0)
                        amount = value.get('amount', 0)
                        display_value = f"{count} چک\n{amount:,.0f} تومان"
                        widget.animate_to_value(count)
                    else:
                        widget.animate_to_value(value)
                else:
                    # فرمت عدد ساده
                    if isinstance(value, (int, float)):
                        widget.animate_to_value(value)
                    else:
                        widget.update_value(str(value))
            else:
                # مقدار پیش‌فرض
                widget.update_value("--")
    
    def clear_cards(self):
        """پاک کردن مقادیر کارت‌ها"""
        for card_info in self.stats_cards.values():
            card_info['widget'].update_value("--")
    
    def resizeEvent(self, event):
        """تغییر سایز ویجت - تنظیم تعداد ستون‌ها بر اساس عرض"""
        width = self.width()
        
        # تنظیم تعداد ستون‌ها بر اساس عرض
        if width < 600:
            new_columns = 2
        elif width < 900:
            new_columns = 3
        else:
            new_columns = 4
        
        if new_columns != self.columns:
            self.columns = new_columns
            # بازسازی کارت‌ها با ستون‌های جدید
            self.rebuild_layout()
        
        super().resizeEvent(event)
    
    def rebuild_layout(self):
        """بازسازی layout با ستون‌های جدید"""
        # ذخیره کارت‌ها
        cards = list(self.stats_cards.values())
        
        # پاک کردن layout فعلی
        layout = self.layout()
        for i in reversed(range(layout.count())):
            layout.itemAt(i).widget().setParent(None)
        
        # اضافه کردن کارت‌ها به layout جدید
        for i, card_info in enumerate(cards):
            row = i // self.columns
            col = i % self.columns
            layout.addWidget(card_info['widget'], row, col)


if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication
    import sys
    
    app = QApplication(sys.argv)
    
    widget = StatsCardsWidget()
    widget.setFixedSize(800, 400)
    widget.show()
    
    # تست با داده‌های نمونه
    test_stats = {
        'today_receptions': 15,
        'repairing_devices': 8,
        'completed_today': 12,
        'today_income': 2500000,
        'profit_today': 1200000,
        'new_customers': 5,
        'low_stock_items': 3,
        'due_checks': {'count': 2, 'amount': 500000}
    }
    
    widget.update_stats(test_stats)
    
    sys.exit(app.exec())