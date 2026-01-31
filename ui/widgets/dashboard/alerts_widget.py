# ui/widgets/dashboard/alerts_widget.py
"""
ویجت هشدارها و اعلان‌های داشبورد
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QFrame, QPushButton, QScrollArea,
    QSizePolicy
)
from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtGui import QFont, QColor, QPainter, QBrush, QLinearGradient


class AlertItem(QFrame):
    """آیتم هشدار"""
    
    clicked = Signal(dict)  # سیگنال کلیک روی هشدار
    
    def __init__(self, alert_data, parent=None):
        super().__init__(parent)
        self.alert_data = alert_data
        self.setup_ui()
        self.apply_style()
    
    def setup_ui(self):
        self.setCursor(Qt.PointingHandCursor)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(6)
        
        # هدر هشدار
        header_layout = QHBoxLayout()
        
        # آیکون نوع هشدار
        type_icon = self.get_type_icon()
        icon_label = QLabel(type_icon)
        icon_label.setStyleSheet("font-size: 16px;")
        
        # عنوان هشدار
        title_label = QLabel(self.alert_data.get('title', 'هشدار'))
        title_label.setStyleSheet("""
            font-weight: bold;
            font-size: 13px;
        """)
        
        # زمان
        time_label = QLabel(self.format_time())
        time_label.setStyleSheet("""
            font-size: 10px;
            color: #aaa;
        """)
        
        header_layout.addWidget(icon_label)
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        header_layout.addWidget(time_label)
        
        layout.addLayout(header_layout)
        
        # پیام هشدار
        message_label = QLabel(self.alert_data.get('message', ''))
        message_label.setStyleSheet("font-size: 12px; color: #ddd;")
        message_label.setWordWrap(True)
        layout.addWidget(message_label)
        
        # جزئیات (اختیاری)
        details = self.alert_data.get('details', '')
        if details:
            details_label = QLabel(details)
            details_label.setStyleSheet("""
                font-size: 11px;
                color: #999;
                font-style: italic;
                padding-top: 5px;
            """)
            details_label.setWordWrap(True)
            layout.addWidget(details_label)
        
        # دکمه عمل
        action = self.alert_data.get('action', '')
        if action:
            action_layout = QHBoxLayout()
            action_layout.addStretch()
            
            action_btn = QPushButton(self.get_action_text(action))
            action_btn.setStyleSheet("""
                QPushButton {
                    background-color: rgba(52, 152, 219, 0.3);
                    color: #3498db;
                    border: 1px solid #3498db;
                    border-radius: 4px;
                    padding: 4px 12px;
                    font-size: 11px;
                    min-width: 80px;
                }
                QPushButton:hover {
                    background-color: rgba(52, 152, 219, 0.5);
                }
            """)
            action_btn.clicked.connect(lambda: self.on_action_clicked(action))
            
            action_layout.addWidget(action_btn)
            layout.addLayout(action_layout)
    
    def get_type_icon(self):
        """دریافت آیکون بر اساس نوع هشدار"""
        alert_type = self.alert_data.get('type', 'info')
        
        icons = {
            'urgent': '🔴',
            'warning': '🟡',
            'info': '🔵'
        }
        
        return icons.get(alert_type, '⚪')
    
    def format_time(self):
        """فرمت‌دهی زمان"""
        import datetime
        
        timestamp = self.alert_data.get('timestamp', '')
        if not timestamp:
            return 'همین حالا'
        
        try:
            if isinstance(timestamp, str):
                alert_time = datetime.datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            else:
                alert_time = timestamp
            
            now = datetime.datetime.now()
            diff = now - alert_time
            
            if diff.days > 0:
                return f"{diff.days} روز پیش"
            elif diff.seconds > 3600:
                hours = diff.seconds // 3600
                return f"{hours} ساعت پیش"
            elif diff.seconds > 60:
                minutes = diff.seconds // 60
                return f"{minutes} دقیقه پیش"
            else:
                return "همین حالا"
                
        except:
            return 'همین حالا'
    
    def get_action_text(self, action):
        """دریافت متن دکمه عمل"""
        actions = {
            'receptions': 'مشاهده پذیرش',
            'inventory': 'مشاهده انبار',
            'checks': 'مشاهده چک‌ها',
            'customers': 'مشاهده مشتری',
            'repairs': 'مشاهده تعمیرات'
        }
        
        return actions.get(action, 'مشاهده')
    
    def apply_style(self):
        """اعمال استایل بر اساس نوع هشدار"""
        alert_type = self.alert_data.get('type', 'info')
        
        colors = {
            'urgent': {
                'bg': 'rgba(231, 76, 60, 0.15)',
                'border': 'rgba(231, 76, 60, 0.5)',
                'hover': 'rgba(231, 76, 60, 0.25)'
            },
            'warning': {
                'bg': 'rgba(243, 156, 18, 0.15)',
                'border': 'rgba(243, 156, 18, 0.5)',
                'hover': 'rgba(243, 156, 18, 0.25)'
            },
            'info': {
                'bg': 'rgba(52, 152, 219, 0.15)',
                'border': 'rgba(52, 152, 219, 0.5)',
                'hover': 'rgba(52, 152, 219, 0.25)'
            }
        }
        
        color_info = colors.get(alert_type, colors['info'])
        
        self.setStyleSheet(f"""
            AlertItem {{
                background-color: {color_info['bg']};
                border: 1px solid {color_info['border']};
                border-radius: 8px;
                margin: 2px;
            }}
            AlertItem:hover {{
                background-color: {color_info['hover']};
                border: 1px solid {color_info['border'].replace('0.5', '0.8')};
            }}
        """)
    
    def on_action_clicked(self, action):
        """کلیک روی دکمه عمل"""
        self.clicked.emit({
            'type': 'alert_action',
            'action': action,
            'alert_data': self.alert_data
        })
    
    def mousePressEvent(self, event):
        """کلیک روی هشدار"""
        if event.button() == Qt.LeftButton:
            self.clicked.emit({
                'type': 'alert_click',
                'alert_data': self.alert_data
            })
    
    def paintEvent(self, event):
        """رسم گرادیانت و جلوه‌های بصری"""
        super().paintEvent(event)
        
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # گرادیانت زیبا
        rect = self.rect()
        gradient = QLinearGradient(rect.topLeft(), rect.bottomRight())
        
        alert_type = self.alert_data.get('type', 'info')
        if alert_type == 'urgent':
            gradient.setColorAt(0, QColor(231, 76, 60, 30))
            gradient.setColorAt(1, QColor(192, 57, 43, 10))
        elif alert_type == 'warning':
            gradient.setColorAt(0, QColor(243, 156, 18, 30))
            gradient.setColorAt(1, QColor(230, 126, 34, 10))
        else:
            gradient.setColorAt(0, QColor(52, 152, 219, 30))
            gradient.setColorAt(1, QColor(41, 128, 185, 10))
        
        painter.fillRect(rect, QBrush(gradient))


class AlertsWidget(QWidget):
    """ویجت هشدارهای داشبورد"""
    
    alert_action_triggered = Signal(dict)  # سیگنال عمل روی هشدار
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.dashboard_manager = None
        self.alert_items = []
        self.setup_ui()
        
        # تایمر برای بروزرسانی زمان‌ها
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_alert_times)
        self.update_timer.start(60000)  # هر دقیقه
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # هدر هشدارها
        header_layout = QHBoxLayout()
        
        # عنوان
        title_label = QLabel("⚠️ هشدارها و اعلان‌ها")
        title_label.setStyleSheet("""
            font-size: 16px;
            font-weight: bold;
            color: #f39c12;
            padding-bottom: 5px;
        """)
        
        # شمارنده هشدارها
        self.counter_label = QLabel("(0)")
        self.counter_label.setStyleSheet("""
            font-size: 14px;
            font-weight: bold;
            color: #e74c3c;
            background-color: rgba(231, 76, 60, 0.2);
            border-radius: 12px;
            padding: 2px 10px;
            margin-left: 10px;
        """)
        
        header_layout.addWidget(title_label)
        header_layout.addWidget(self.counter_label)
        header_layout.addStretch()
        
        # دکمه‌های فیلتر
        filter_layout = QHBoxLayout()
        
        self.all_btn = self.create_filter_button("همه", "all", True)
        self.urgent_btn = self.create_filter_button("فوری", "urgent")
        self.warning_btn = self.create_filter_button("هشدار", "warning")
        self.info_btn = self.create_filter_button("اطلاع", "info")
        
        filter_layout.addWidget(self.all_btn)
        filter_layout.addWidget(self.urgent_btn)
        filter_layout.addWidget(self.warning_btn)
        filter_layout.addWidget(self.info_btn)
        filter_layout.addStretch()
        
        header_layout.addLayout(filter_layout)
        
        layout.addLayout(header_layout)
        
        # ناحیه اسکرول برای هشدارها
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QScrollBar:vertical {
                background-color: #2c2c2c;
                width: 10px;
                border-radius: 5px;
            }
            QScrollBar::handle:vertical {
                background-color: #444;
                border-radius: 5px;
                min-height: 30px;
            }
        """)
        
        # ویجت حاوی هشدارها
        self.alerts_container = QWidget()
        self.alerts_layout = QVBoxLayout(self.alerts_container)
        self.alerts_layout.setSpacing(8)
        self.alerts_layout.setContentsMargins(5, 5, 5, 5)
        self.alerts_layout.addStretch()
        
        scroll_area.setWidget(self.alerts_container)
        layout.addWidget(scroll_area)
        
        # پیام خالی
        self.empty_message = QLabel("هیچ هشدار فعالی وجود ندارد. ✅")
        self.empty_message.setStyleSheet("""
            font-size: 14px;
            color: #666;
            font-style: italic;
            padding: 30px;
            text-align: center;
        """)
        self.empty_message.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.empty_message)
        self.empty_message.hide()
        
        # متغیرهای فیلتر
        self.current_filter = "all"
        self.filter_buttons = {
            "all": self.all_btn,
            "urgent": self.urgent_btn,
            "warning": self.warning_btn,
            "info": self.info_btn
        }
    
    def create_filter_button(self, text, filter_type, active=False):
        """ایجاد دکمه فیلتر"""
        btn = QPushButton(text)
        btn.setCheckable(True)
        btn.setChecked(active)
        
        if active:
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #3498db;
                    color: white;
                    border: none;
                    border-radius: 5px;
                    padding: 6px 15px;
                    font-size: 11px;
                    min-width: 60px;
                }
            """)
        else:
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #2c2c2c;
                    color: #bbb;
                    border: 1px solid #444;
                    border-radius: 5px;
                    padding: 6px 15px;
                    font-size: 11px;
                    min-width: 60px;
                }
                QPushButton:hover {
                    background-color: #3c3c3c;
                }
            """)
        
        btn.clicked.connect(lambda: self.set_filter(filter_type))
        return btn
    
    def set_filter(self, filter_type):
        """تنظیم فیلتر هشدارها"""
        self.current_filter = filter_type
        
        # بروزرسانی ظاهر دکمه‌ها
        for btn_type, btn in self.filter_buttons.items():
            btn.setChecked(btn_type == filter_type)
            
            if btn_type == filter_type:
                btn.setStyleSheet("""
                    QPushButton {
                        background-color: #3498db;
                        color: white;
                        border: none;
                        border-radius: 5px;
                        padding: 6px 15px;
                        font-size: 11px;
                        min-width: 60px;
                    }
                """)
            else:
                btn.setStyleSheet("""
                    QPushButton {
                        background-color: #2c2c2c;
                        color: #bbb;
                        border: 1px solid #444;
                        border-radius: 5px;
                        padding: 6px 15px;
                        font-size: 11px;
                        min-width: 60px;
                    }
                    QPushButton:hover {
                        background-color: #3c3c3c;
                    }
                """)
        
        # اعمال فیلتر
        self.apply_filter()
    
    def apply_filter(self):
        """اعمال فیلتر روی هشدارها"""
        for alert_item in self.alert_items:
            if self.current_filter == "all":
                alert_item.show()
            else:
                alert_type = alert_item.alert_data.get('type', '')
                alert_item.setVisible(alert_type == self.current_filter)
    
    def set_dashboard_manager(self, dashboard_manager):
        """تنظیم مدیر داشبورد"""
        self.dashboard_manager = dashboard_manager
    
    def update_alerts(self, alerts_data):
        """بروزرسانی هشدارها"""
        if not alerts_data:
            return
        
        # پاک کردن هشدارهای قبلی
        self.clear_alerts()
        
        # شمارنده‌های انواع هشدار
        alert_counts = {
            'urgent': 0,
            'warning': 0,
            'info': 0,
            'total': 0
        }
        
        # جمع‌آوری همه هشدارها
        all_alerts = []
        
        for alert_type in ['urgent', 'warning', 'info']:
            alerts = alerts_data.get(alert_type, [])
            for alert in alerts:
                alert['type'] = alert_type
                all_alerts.append(alert)
                alert_counts[alert_type] += 1
                alert_counts['total'] += 1
        
        # مرتب‌سازی: ابتدا فوری، سپس هشدار، سپس اطلاع
        all_alerts.sort(key=lambda x: {
            'urgent': 1,
            'warning': 2,
            'info': 3
        }.get(x.get('type', 'info'), 4))
        
        # ایجاد آیتم‌های هشدار
        for alert in all_alerts:
            alert_item = AlertItem(alert)
            alert_item.clicked.connect(self.on_alert_clicked)
            
            self.alert_items.append(alert_item)
            self.alerts_layout.insertWidget(self.alerts_layout.count() - 1, alert_item)
        
        # بروزرسانی شمارنده
        self.update_counter(alert_counts)
        
        # اعمال فیلتر فعلی
        self.apply_filter()
        
        # نمایش پیام خالی اگر هیچ هشداری نیست
        if alert_counts['total'] == 0:
            self.empty_message.show()
        else:
            self.empty_message.hide()
    
    def update_counter(self, counts):
        """بروزرسانی شمارنده هشدارها"""
        total = counts['total']
        urgent = counts['urgent']
        
        if urgent > 0:
            counter_text = f"({total} - {urgent} فوری)"
            self.counter_label.setStyleSheet("""
                font-size: 14px;
                font-weight: bold;
                color: #e74c3c;
                background-color: rgba(231, 76, 60, 0.3);
                border-radius: 12px;
                padding: 2px 10px;
                margin-left: 10px;
            """)
        elif total > 0:
            counter_text = f"({total})"
            self.counter_label.setStyleSheet("""
                font-size: 14px;
                font-weight: bold;
                color: #f39c12;
                background-color: rgba(243, 156, 18, 0.2);
                border-radius: 12px;
                padding: 2px 10px;
                margin-left: 10px;
            """)
        else:
            counter_text = "(0)"
            self.counter_label.setStyleSheet("""
                font-size: 14px;
                font-weight: bold;
                color: #27ae60;
                background-color: rgba(39, 174, 96, 0.2);
                border-radius: 12px;
                padding: 2px 10px;
                margin-left: 10px;
            """)
        
        self.counter_label.setText(counter_text)
    
    def clear_alerts(self):
        """پاک کردن تمام هشدارها"""
        for alert_item in self.alert_items:
            alert_item.deleteLater()
        
        self.alert_items = []
    
    def update_alert_times(self):
        """بروزرسانی زمان هشدارها"""
        for alert_item in self.alert_items:
            # این باعث به‌روزرسانی زمان‌ها می‌شود
            # در واقعیت باید متد update_time در AlertItem داشته باشیم
            pass
    
    def on_alert_clicked(self, data):
        """کلیک روی هشدار"""
        self.alert_action_triggered.emit(data)
    
    def refresh_alerts(self):
        """بروزرسانی هشدارها"""
        if self.dashboard_manager:
            alerts_data = self.dashboard_manager.get_alerts()
            self.update_alerts(alerts_data)


if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication
    import sys
    import datetime
    
    app = QApplication(sys.argv)
    
    widget = AlertsWidget()
    widget.setFixedSize(500, 600)
    widget.show()
    
    # تست با داده‌های نمونه
    test_alerts = {
        'urgent': [
            {
                'title': 'چک سررسید فردا',
                'message': 'چک شماره 12345 بانک ملی مبلغ 5,000,000 تومان',
                'details': 'صادرکننده: شرکت مثال',
                'action': 'checks',
                'timestamp': datetime.datetime.now().isoformat()
            },
            {
                'title': 'پذیرش فوری',
                'message': 'پذیرش شماره 1001 - یخچال ال جی',
                'details': 'مشتری: علی محمدی',
                'action': 'receptions',
                'timestamp': datetime.datetime.now().isoformat()
            }
        ],
        'warning': [
            {
                'title': 'موجودی کم',
                'message': 'کمپرسور یخچال (کد: CP-100)',
                'details': 'موجودی: 2 - حداقل: 5',
                'action': 'inventory',
                'timestamp': datetime.datetime.now().isoformat()
            }
        ],
        'info': [
            {
                'title': 'تماس با مشتری',
                'message': 'رضا کریمی - دستگاه تعمیر شده',
                'details': 'شماره: 09123456789 - ماشین لباسشویی',
                'action': 'customers',
                'timestamp': datetime.datetime.now().isoformat()
            }
        ]
    }
    
    widget.update_alerts(test_alerts)
    
    sys.exit(app.exec())