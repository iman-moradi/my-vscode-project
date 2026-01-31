# test_dashboard.py
"""
تست کامل داشبورد مدیریتی
"""

import sys
import os
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QLabel
from PySide6.QtCore import Qt

# اضافه کردن مسیر پروژه
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# ایمپورت ماژول‌ها
try:
    from database import DatabaseManager
    from database.models import DataManager
    from modules.dashboard_manager import DashboardManager
    from ui.widgets.dashboard import (
        StatsCardsWidget, ChartsWidget, 
        AlertsWidget, QuickListsWidget
    )
    
    print("✅ تمام ماژول‌ها با موفقیت بارگذاری شدند")
    
except ImportError as e:
    print(f"❌ خطا در بارگذاری ماژول‌ها: {e}")
    sys.exit(1)


class TestDashboardWindow(QMainWindow):
    """پنجره تست داشبورد"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("تست داشبورد مدیریتی - شیروین")
        self.setGeometry(100, 50, 1400, 800)
        
        # استایل تاریک
        self.setStyleSheet("""
            QMainWindow {
                background-color: #0a0a0a;
            }
            QLabel {
                color: white;
            }
        """)
        
        # ایجاد مدیر داده
        print("🔄 ایجاد DataManager...")
        self.data_manager = DataManager()
        
        # ایجاد مدیر داشبورد
        print("🔄 ایجاد DashboardManager...")
        self.dashboard_manager = DashboardManager(self.data_manager)
        
        # ایجاد رابط کاربری
        self.setup_ui()
        
        # بارگذاری داده‌ها
        self.load_data()
    
    def setup_ui(self):
        """راه‌اندازی رابط کاربری"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # عنوان
        title_label = QLabel("🧪 تست داشبورد مدیریتی")
        title_label.setStyleSheet("""
            font-size: 24px;
            font-weight: bold;
            color: #3498db;
            padding: 10px;
            border-bottom: 2px solid #3498db;
        """)
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        # ویجت کارت‌های آماری
        print("📊 ایجاد ویجت کارت‌های آماری...")
        self.stats_widget = StatsCardsWidget()
        self.stats_widget.set_dashboard_manager(self.dashboard_manager)
        layout.addWidget(self.stats_widget)
        
        # ویجت نمودارها
        print("📈 ایجاد ویجت نمودارها...")
        self.charts_widget = ChartsWidget()
        self.charts_widget.set_dashboard_manager(self.dashboard_manager)
        layout.addWidget(self.charts_widget)
        
        # ویجت هشدارها
        print("⚠️ ایجاد ویجت هشدارها...")
        self.alerts_widget = AlertsWidget()
        self.alerts_widget.set_dashboard_manager(self.dashboard_manager)
        layout.addWidget(self.alerts_widget)
        
        # ویجت لیست‌های سریع
        print("⚡ ایجاد ویجت لیست‌های سریع...")
        self.quick_lists_widget = QuickListsWidget()
        self.quick_lists_widget.set_dashboard_manager(self.dashboard_manager)
        layout.addWidget(self.quick_lists_widget)
        
        central_widget.setLayout(layout)
    
    def load_data(self):
        """بارگذاری داده‌های تست"""
        print("🔄 بارگذاری داده‌های تست...")
        
        # دریافت داده‌های داشبورد
        dashboard_data = self.dashboard_manager.get_dashboard_data(force_refresh=True)
        
        # بروزرسانی ویجت‌ها
        if dashboard_data:
            print(f"📊 دریافت {len(dashboard_data)} بخش داده")
            
            if 'stats' in dashboard_data:
                stats = dashboard_data['stats']
                print(f"📈 آمار: {len(stats)} مورد")
                self.stats_widget.update_stats(stats)
            
            if 'charts' in dashboard_data:
                charts = dashboard_data['charts']
                print(f"📊 نمودارها: {len(charts)} نوع")
                self.charts_widget.update_charts(charts)
            
            if 'alerts' in dashboard_data:
                alerts = dashboard_data['alerts']
                total_alerts = (
                    len(alerts.get('urgent', [])) + 
                    len(alerts.get('warning', [])) + 
                    len(alerts.get('info', []))
                )
                print(f"⚠️ هشدارها: {total_alerts} مورد")
                self.alerts_widget.update_alerts(alerts)
            
            if 'quick_lists' in dashboard_data:
                lists = dashboard_data['quick_lists']
                print(f"📋 لیست‌ها: {len(lists)} مورد")
                self.quick_lists_widget.update_lists(lists)
        
        print("✅ بارگذاری داده‌ها تکمیل شد")


if __name__ == "__main__":
    print("🚀 شروع تست داشبورد مدیریتی...")
    print("=" * 50)
    
    app = QApplication(sys.argv)
    
    # تنظیم فونت فارسی
    font = app.font()
    font.setFamily("B Nazanin")
    font.setPointSize(10)
    app.setFont(font)
    
    window = TestDashboardWindow()
    window.show()
    
    print("✅ پنجره تست نمایش داده شد")
    print("=" * 50)
    
    sys.exit(app.exec())