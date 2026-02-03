# ui/main_window.py - پنجره اصلی برنامه
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QTabWidget, QTableWidget, QTableWidgetItem,
    QToolBar, QStatusBar, QMenuBar, QMenu, QFrame, QSplitter,
    QTreeWidget, QTreeWidgetItem, QDockWidget, QMessageBox,
    QApplication, QStyleFactory, QListWidget, QListWidgetItem,
    QDialog, QScrollArea, QSizePolicy, QSpacerItem
)
from PySide6.QtCore import Qt, QTimer, QDate, QSize
from PySide6.QtGui import QIcon, QAction, QFont, QPixmap, QColor
import jdatetime
from datetime import datetime, timedelta
from modules.dashboard_manager import DashboardManager
from ui.widgets.dashboard.stats_cards_widget import StatsCardsWidget
from ui.widgets.dashboard.charts_widget import ChartsWidget
from ui.widgets.dashboard.alerts_widget import AlertsWidget
from ui.widgets.dashboard.quick_lists_widget import QuickListsWidget


# در ابتدای main_window.py، بعد از دیگر ایمپورت‌ها:
import sys
import os

# اضافه کردن مسیر پروژه به sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.insert(0, project_root)

# حالا می‌توانیم فرم‌ها را ایمپورت کنیم
try:
    from ui.forms.person_form import PersonForm
    PERSON_FORM_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ خطا در بارگذاری فرم اشخاص: {e}")
    PERSON_FORM_AVAILABLE = False


try:
    from ui.forms.reports.reports_window import ReportsWindow
    from ui.forms.reports.reports_main_form import ReportsMainForm
    REPORTS_WINDOW_AVAILABLE = True
    print("✅ ماژول گزارش‌گیری در main_window بارگذاری شد")
except ImportError as e:
    print(f"⚠️ خطا در بارگذاری ماژول گزارش‌گیری در main_window: {e}")
    import traceback
    traceback.print_exc()
    REPORTS_WINDOW_AVAILABLE = False



try:
    from ui.forms.reception_form import ReceptionForm
    RECEPTION_FORM_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ خطا در بارگذاری فرم پذیرش: {e}")
    RECEPTION_FORM_AVAILABLE = False

try:
    from ui.forms.device_form import DeviceForm
    DEVICE_FORM_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ خطا در بارگذاری فرم دستگاه‌ها: {e}")
    DEVICE_FORM_AVAILABLE = False

try:
    from ui.forms.repair_form import RepairForm
    REPAIR_FORM_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ خطا در بارگذاری فرم تعمیرات: {e}")
    REPAIR_FORM_AVAILABLE = False

try:
    from ui.forms.service_fee_form import ServiceFeeForm
    SERVICE_FEE_FORM_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ خطا در بارگذاری فرم اجرت‌ها: {e}")
    SERVICE_FEE_FORM_AVAILABLE = False


try:
    from ui.forms.inventory.inventory_window import InventoryWindow
    INVENTORY_WINDOW_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ خطا در بارگذاری پنجره انبار: {e}")
    INVENTORY_WINDOW_AVAILABLE = False
    InventoryWindow = None

try:
    from ui.forms.accounting.accounting_window import AccountingWindow
    ACCOUNTING_WINDOW_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ خطا در بارگذاری پنجره حسابداری: {e}")
    import traceback
    traceback.print_exc()  # نمایش جزییات خطا
    ACCOUNTING_WINDOW_AVAILABLE = False
    AccountingWindow = None

try:
    from utils.jalali_date_widget import JalaliDateWidget, JalaliDateEdit, JalaliDateTimeWidget
    JALALI_WIDGET_AVAILABLE = True
    print("✅ ویجت تاریخ شمسی بارگذاری شد")
except ImportError as e:
    print(f"⚠️ خطا در بارگذاری ویجت تاریخ شمسی: {e}")
    JALALI_WIDGET_AVAILABLE = False

def convert_to_jalali_display(self, date_str):
    """تبدیل رشته تاریخ میلادی به شمسی برای نمایش"""
    if not date_str:
        return ""
    
    try:
        # اگر تاریخ در حال حاضر شمسی است، برگردان
        if '/' in str(date_str) and len(str(date_str).split('/')[0]) == 4:
            parts = str(date_str).split('/')
            if len(parts) >= 3:
                year = int(parts[0])
                # بررسی اینکه آیا سال شمسی است (مثلاً 1400)
                if 1300 <= year <= 1500:
                    return str(date_str)
        
        # فرض می‌کنیم تاریخ میلادی است
        # حذف زمان اگر وجود دارد
        date_only = str(date_str).split(' ')[0]
        
        # فرمت‌های مختلف
        for fmt in ['%Y-%m-%d', '%Y/%m/%d', '%d-%m-%Y', '%d/%m/%Y']:
            try:
                miladi_date = datetime.strptime(date_only, fmt).date()
                jalali_date = jdatetime.date.fromgregorian(date=miladi_date)
                return jalali_date.strftime('%Y/%m/%d')
            except:
                continue
        
        # اگر هیچکدام کار نکرد، تاریخ اصلی را برگردان
        return str(date_str)
            
    except Exception as e:
        print(f"⚠️ خطا در تبدیل تاریخ {date_str}: {e}")
        return str(date_str)


class MainWindow(QMainWindow):
    """پنجره اصلی برنامه"""
    
    def __init__(self, user_data, data_manager, username="admin"):
        super().__init__()
        self.user_data = user_data
        self.data_manager = data_manager
        self.inventory_window = None
        self.accounting_windows = {}
        
        # 🔴 1. ابتدا ConfigManager
        from modules.config_manager import ConfigManager
        self.config_manager = ConfigManager(self.data_manager)
        print(f"✅ ConfigManager ایجاد شد. نوع: {type(self.config_manager)}")
        print(f"   id: {id(self.config_manager)}")
        print("🔍 بررسی اولیه تنظیمات...")
        self.check_settings_in_database()


        # 🔴 تست متدهای config_manager
        if hasattr(self.config_manager, 'get'):
            test_value = self.config_manager.get('general', 'app_name', 'پیش‌فرض')
            print(f"   تست متد get: {test_value}")
        
        self.test_config_manager()
        self.debug_config_manager()

        self.config_manager.display_settings_changed.connect(self.on_display_settings_changed)

        # 🔴 2. سپس DashboardManager (قبل از init_ui)
        try:
            from modules.dashboard_manager import DashboardManager
            self.dashboard_manager = DashboardManager(data_manager)
            print(f"✅ DashboardManager ایجاد شد")
        except ImportError as e:
            print(f"⚠️ خطا در بارگذاری DashboardManager: {e}")
            self.dashboard_manager = None



        print(f"✅ DashboardManager ایجاد شد: {hasattr(self, 'dashboard_manager')}")

        # بررسی متدهای داشبورد
        dashboard_methods = [
            'refresh_dashboard_data',
            'refresh_old_dashboard_data', 
            'load_dashboard_data'  # اگر وجود دارد
        ]

        for method in dashboard_methods:
            exists = hasattr(self, method)
            print(f"   متد {method}: {'✅' if exists else '❌'}")
                


        # 🔴 3. سپس PermissionManager
        from modules.permission_manager import PermissionManager
        self.permission_manager = PermissionManager(self.config_manager)
        print(f"✅ PermissionManager ایجاد شد")
        
        # 🔴 4. اکنون init_ui را فراخوانی کن
        self.init_ui()
        self.setup_connections()
        
        # 🔴 5. ترمیم config_manager
        self.repair_config_manager()
        
        # 🔴 6. تنظیم کاربر جاری
        self.setup_current_user(username)
        
        # 🔴 7. اعمال تنظیمات اولیه
        self.apply_initial_settings()
        


        # 🔴 8. اتصال سیگنال‌ها
        self.setup_config_signals()
        
        # 🔴 9. بارگذاری اولیه داده‌ها
        self.load_initial_data()


    def init_ui(self):
        """راه‌اندازی رابط کاربری"""
        self.setWindowTitle("سیستم مدیریت تعمیرگاه لوازم خانگی شیروین")
        
        # 🔴 **کاهش ارتفاع برای جلوگیری از خطای geometry**
        # محاسبه اندازه صفحه نمایش
        screen = QApplication.primaryScreen().availableGeometry()
        
        # تنظیم اندازه ایمن که در همه مانیتورها کار کند
        safe_width = min(1400, screen.width() - 100)
        safe_height = min(900, screen.height() - 150)
        
        # موقعیت پنجره (مرکز)
        x = (screen.width() - safe_width) // 2
        y = (screen.height() - safe_height) // 2
        
        self.setGeometry(x, y, safe_width, safe_height)
        
        # 🔴 **راست‌چین کردن کل پنجره**
        self.setLayoutDirection(Qt.RightToLeft)

        # تنظیم استایل کلی
        self.setStyleSheet(self.get_style_sheet())
        
        # تنظیم فونت
        self.set_fonts()
        
        # ایجاد المان‌های اصلی
        self.create_menu_bar()
        self.create_toolbar()
        self.create_status_bar()
        
        # 🔴 **ایجاد داشبورد**
        self.create_dashboard()
        
        self.create_side_panel()
        
        # نمایش اطلاعات کاربر
        self.show_user_info()
        
        # 🔴 **تنظیم سیاست اندازه**
        self.setMinimumSize(800, 600)

    def create_dashboard(self):
        """ایجاد داشبورد اصلی با ویجت‌های جدید"""
        # ایجاد ویجت مرکزی اصلی
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # ایجاد layout اصلی برای ویجت مرکزی
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # ایجاد ویجت اسکرول
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        # تنظیم استایل برای اسکرول
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: #000000;
            }
            QScrollBar:vertical {
                background-color: #2c2c2c;
                width: 12px;
                border-radius: 6px;
                margin: 2px 0px 2px 0px;
            }
            QScrollBar::handle:vertical {
                background-color: #3498db;
                border-radius: 6px;
                min-height: 30px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #2980b9;
            }
        """)
        
        # ویجت محتوای داخل اسکرول
        content_widget = QWidget()
        scroll_area.setWidget(content_widget)
        
        # لایه برای محتوای داخل اسکرول
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(15, 15, 15, 15)  # حاشیه داخلی
        content_layout.setSpacing(15)
        
        # عنوان داشبورد
        dashboard_title = QLabel("📊 داشبورد مدیریت - تعمیرگاه شیروین")
        dashboard_title.setStyleSheet("""
            QLabel {
                font-size: 22px;
                font-weight: bold;
                color: white;
                padding-bottom: 15px;
                border-bottom: 3px solid #3498db;
                margin-bottom: 10px;
            }
        """)
        content_layout.addWidget(dashboard_title)
        
        # اضافه کردن ویجت انتخاب تاریخ
        date_selector = self.create_date_selector_widget()
        if date_selector:
            content_layout.addWidget(date_selector)


        # ویجت کارت‌های آماری (اگر موجود است)
        if hasattr(self, 'dashboard_manager') and self.dashboard_manager:
            try:
                from ui.widgets.dashboard.stats_cards_widget import StatsCardsWidget
                self.stats_widget = StatsCardsWidget()
                self.stats_widget.set_dashboard_manager(self.dashboard_manager)
                content_layout.addWidget(self.stats_widget)
            except ImportError as e:
                print(f"⚠️ خطا در بارگذاری StatsCardsWidget: {e}")
                # نمایش کارت‌های آماری ساده
                stats_widget = self.create_stats_widget()
                content_layout.addWidget(stats_widget)
        else:
            print("⚠️ dashboard_manager موجود نیست، نمایش داشبورد ساده")
            # نمایش کارت‌های آماری ساده
            stats_widget = self.create_stats_widget()
            content_layout.addWidget(stats_widget)
        
        # ویجت نمودارها (اگر موجود است)
        if self.dashboard_manager:
            try:
                from ui.widgets.dashboard.charts_widget import ChartsWidget
                self.charts_widget = ChartsWidget()
                self.charts_widget.set_dashboard_manager(self.dashboard_manager)
                content_layout.addWidget(self.charts_widget)
            except ImportError as e:
                print(f"⚠️ خطا در بارگذاری ChartsWidget: {e}")
                # نمایش نمودارهای ساده
                self.show_simple_charts(content_layout)
        else:
            # نمایش نمودارهای ساده
            self.show_simple_charts(content_layout)
        
        # ردیف پایینی (هشدارها و لیست‌های سریع)
        bottom_layout = QHBoxLayout()
        bottom_layout.setSpacing(15)
        
        # ویجت هشدارها (اگر موجود است)
        if self.dashboard_manager:
            try:
                from ui.widgets.dashboard.alerts_widget import AlertsWidget
                self.alerts_widget = AlertsWidget()
                self.alerts_widget.set_dashboard_manager(self.dashboard_manager)
                self.alerts_widget.alert_action_triggered.connect(self.on_alert_action)
                bottom_layout.addWidget(self.alerts_widget, 2)
            except ImportError as e:
                print(f"⚠️ خطا در بارگذاری AlertsWidget: {e}")
                # نمایش هشدارهای ساده
                self.show_simple_alerts(bottom_layout)
        else:
            # نمایش هشدارهای ساده
            self.show_simple_alerts(bottom_layout)
        
        # ویجت لیست‌های سریع (اگر موجود است)
        if self.dashboard_manager:
            try:
                from ui.widgets.dashboard.quick_lists_widget import QuickListsWidget
                self.quick_lists_widget = QuickListsWidget()
                self.quick_lists_widget.set_dashboard_manager(self.dashboard_manager)
                self.quick_lists_widget.list_action_triggered.connect(self.on_list_action)
                bottom_layout.addWidget(self.quick_lists_widget, 3)
            except ImportError as e:
                print(f"⚠️ خطا در بارگذاری QuickListsWidget: {e}")
                # نمایش لیست‌های ساده
                self.show_simple_lists(bottom_layout)
        else:
            # نمایش لیست‌های ساده
            self.show_simple_lists(bottom_layout)
        
        content_layout.addLayout(bottom_layout)
        
        # اضافه کردن اسپیسر برای ایجاد فاصله از پایین (20 پیکسل)
        content_layout.addStretch(1)
        
        # افزودن اسکرول به لایه اصلی
        main_layout.addWidget(scroll_area)
        
        # برای اطمینان از نمایش اسکرول، به content_widget ارتفاع زیاد می‌دهیم
        content_widget.setMinimumHeight(1800)  # ارتفاع زیاد برای فعال کردن اسکرول
        
        # بارگذاری اولیه داده‌ها
        self.refresh_dashboard_data()


#هر سه تا برای تست 
    def create_test_menu(self):
        """منوی تست برای توسعه‌دهندگان"""
        if hasattr(self, 'menuBar'):
            test_menu = self.menuBar().addMenu("🔧 تست")
            
            # تست تنظیمات
            test_action = QAction("بررسی تنظیمات دیتابیس", self)
            test_action.triggered.connect(self.debug_check_settings)
            test_menu.addAction(test_action)
            
            # بازخوانی تنظیمات
            reload_action = QAction("بازخوانی تنظیمات از دیتابیس", self)
            reload_action.triggered.connect(self.reload_all_settings)
            test_menu.addAction(reload_action)

    def debug_check_settings(self):
        """بررسی تنظیمات ذخیره شده"""
        self.check_settings_in_database()
        
        # همچنین تنظیمات فعلی در حافظه را بررسی کن
        print("\n🔍 بررسی ConfigManager فعلی:")
        if hasattr(self, 'config_manager'):
            print(f"   آدرس ConfigManager: {id(self.config_manager)}")
            print(f"   نوع: {type(self.config_manager)}")
            
            # بررسی همه دسته‌ها
            categories = ['general', 'security', 'financial', 'inventory', 'display']
            for category in categories:
                settings = self.config_manager.get(category)
                if settings:
                    print(f"   📁 دسته '{category}':")
                    for key, value in settings.items():
                        print(f"     {key}: {value}")
                else:
                    print(f"   ⚠️ دسته '{category}': خالی")

    def reload_all_settings(self):
        """بازخوانی تمام تنظیمات از دیتابیس"""
        try:
            print("🔄 بازخوانی تمام تنظیمات از دیتابیس...")
            
            # بارگذاری مجدد از دیتابیس
            self.config_manager.load_all_configs()
            
            # اعمال مجدد تنظیمات
            self.apply_initial_settings()
            
            QMessageBox.information(self, "بازخوانی", "تنظیمات با موفقیت بازخوانی شدند.")
            
        except Exception as e:
            QMessageBox.critical(self, "خطا", f"خطا در بازخوانی تنظیمات: {e}")




    def open_settings(self):
        """باز کردن فرم تنظیمات"""
        try:
            from ui.forms.settings.settings_main_form import SettingsMainForm
            
            # ایجاد فرم تنظیمات
            settings_form = SettingsMainForm(
                data_manager=self.data_manager,
                config_manager=self.config_manager
            )
            
            # ایجاد یک پنجره مودال برای تنظیمات
            from PySide6.QtWidgets import QDialog, QVBoxLayout
            
            dialog = QDialog(self)
            dialog.setWindowTitle("⚙️ تنظیمات سیستم")
            dialog.setModal(True)
            dialog.setMinimumSize(900, 700)
            
            layout = QVBoxLayout()
            layout.addWidget(settings_form)
            dialog.setLayout(layout)
            
            # نمایش دیالوگ
            dialog.exec()
            
        except Exception as e:
            print(f"⚠️ خطا در باز کردن تنظیمات: {e}")
            QMessageBox.warning(self, "خطا", "خطا در بارگذاری فرم تنظیمات")

    def show_simple_charts(self, layout):
        """نمایش نمودارهای ساده (برای وقتی که ویجت‌های جدید موجود نیستند)"""
        # ایجاد فریم برای نمودارها
        charts_frame = QFrame()
        charts_frame.setStyleSheet("""
            QFrame {
                background-color: #1e1e1e;
                border-radius: 10px;
                border: 1px solid #333;
                padding: 15px;
            }
        """)
        
        charts_layout = QVBoxLayout()
        
        charts_title = QLabel("📊 نمودارهای وضعیت")
        charts_title.setStyleSheet("""
            QLabel {
                font-size: 16px;
                font-weight: bold;
                color: white;
                padding-bottom: 10px;
            }
        """)
        charts_layout.addWidget(charts_title)
        
        # یک پیام ساده
        message_label = QLabel("ویجت نمودارها در حال حاضر در دسترس نیست. لطفاً بعداً تلاش کنید.")
        message_label.setStyleSheet("color: #bbb; font-style: italic; padding: 20px;")
        message_label.setAlignment(Qt.AlignCenter)
        charts_layout.addWidget(message_label)
        
        charts_frame.setLayout(charts_layout)
        layout.addWidget(charts_frame)
    
    def show_simple_alerts(self, layout):
        """نمایش هشدارهای ساده"""
        alerts_frame = QFrame()
        alerts_frame.setStyleSheet("""
            QFrame {
                background-color: #1e1e1e;
                border-radius: 10px;
                border: 1px solid #333;
                padding: 15px;
            }
        """)
        
        alerts_layout = QVBoxLayout()
        
        alerts_title = QLabel("⚠️ هشدارها و اعلان‌ها")
        alerts_title.setStyleSheet("""
            QLabel {
                font-size: 16px;
                font-weight: bold;
                color: #f39c12;
                padding-bottom: 10px;
            }
        """)
        alerts_layout.addWidget(alerts_title)
        
        # بارگذاری هشدارهای واقعی از دیتابیس
        self.load_simple_alerts(alerts_layout)
        
        alerts_frame.setLayout(alerts_layout)
        layout.addWidget(alerts_frame)
    
    def load_simple_alerts(self, layout):
        """بارگذاری هشدارهای ساده از دیتابیس"""
        try:
            # چک‌های سررسید نزدیک
            due_checks = self.data_manager.check_manager.get_checks_due_soon(days=3)
            if due_checks:
                checks_label = QLabel(f"💳 {len(due_checks)} چک در سررسید نزدیک")
                checks_label.setStyleSheet("color: #e74c3c; font-weight: bold;")
                layout.addWidget(checks_label)
            
            # پذیرش‌های فوری
            query = """
            SELECT COUNT(*) as count
            FROM Receptions 
            WHERE priority IN ('فوری', 'خیلی فوری')
            AND status IN ('در انتظار', 'در حال تعمیر')
            """
            urgent_receptions = self.data_manager.db.fetch_one(query)
            if urgent_receptions and urgent_receptions['count'] > 0:
                urgent_label = QLabel(f"🚨 {urgent_receptions['count']} پذیرش فوری")
                urgent_label.setStyleSheet("color: #f39c12; font-weight: bold;")
                layout.addWidget(urgent_label)
            
            # موجودی کم
            query = """
            SELECT COUNT(*) as count
            FROM Parts p
            LEFT JOIN (
                SELECT part_id, SUM(quantity) as total_qty 
                FROM NewPartsWarehouse 
                WHERE status = 'موجود'
                GROUP BY part_id
            ) np ON p.id = np.part_id
            LEFT JOIN (
                SELECT part_id, SUM(quantity) as total_qty 
                FROM UsedPartsWarehouse 
                WHERE status = 'موجود'
                GROUP BY part_id
            ) up ON p.id = up.part_id
            WHERE COALESCE(np.total_qty, 0) + COALESCE(up.total_qty, 0) < p.min_stock
            """
            low_stock = self.data_manager.db.fetch_one(query)
            if low_stock and low_stock['count'] > 0:
                stock_label = QLabel(f"📦 {low_stock['count']} قطعه با موجودی کم")
                stock_label.setStyleSheet("color: #d35400; font-weight: bold;")
                layout.addWidget(stock_label)
            
        except Exception as e:
            print(f"خطا در بارگذاری هشدارها: {e}")
    
    def show_simple_lists(self, layout):
        """نمایش لیست‌های ساده"""
        lists_frame = QFrame()
        lists_frame.setStyleSheet("""
            QFrame {
                background-color: #1e1e1e;
                border-radius: 10px;
                border: 1px solid #333;
                padding: 15px;
            }
        """)
        
        lists_layout = QVBoxLayout()
        
        lists_title = QLabel("⚡ دسترسی سریع")
        lists_title.setStyleSheet("""
            QLabel {
                font-size: 16px;
                font-weight: bold;
                color: #3498db;
                padding-bottom: 10px;
            }
        """)
        lists_layout.addWidget(lists_title)
        
        # دکمه‌های سریع
        quick_buttons = [
            ("📝 پذیرش جدید", self.new_reception),
            ("👤 مشتری جدید", lambda: self.open_persons_management()),
            ("🔧 ثبت تعمیر", self.open_repairs_management),
            ("📦 ورود به انبار", self.open_inventory_main),
            ("🧾 صدور فاکتور", self.new_invoice),
            ("💳 مدیریت چک‌ها", self.open_checks_form)
        ]
        
        for text, callback in quick_buttons:
            btn = QPushButton(text)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #2c3e50;
                    color: white;
                    border: none;
                    border-radius: 5px;
                    padding: 10px;
                    margin: 5px;
                    text-align: right;
                    font-size: 12px;
                }
                QPushButton:hover {
                    background-color: #34495e;
                }
            """)
            btn.clicked.connect(callback)
            lists_layout.addWidget(btn)
        
        lists_layout.addStretch()
        lists_frame.setLayout(lists_layout)
        layout.addWidget(lists_frame)

    def refresh_dashboard_data(self):
        """بروزرسانی داده‌های داشبورد جدید"""
        try:
            # 🔴 بررسی وجود dashboard_manager
            if not hasattr(self, 'dashboard_manager') or not self.dashboard_manager:
                print("⚠️ dashboard_manager موجود نیست، استفاده از روش قدیمی")
                self.refresh_old_dashboard_data()
                return
            
            print("🔄 بروزرسانی داشبورد...")
            
            # دریافت داده‌های داشبورد
            dashboard_data = self.dashboard_manager.get_dashboard_data()
            
            # 🔴 بررسی معتبر بودن داده‌ها
            if not dashboard_data:
                print("⚠️ داده‌های داشبورد خالی است")
                return
                
            # 🔴 بررسی وجود keyهای مورد نیاز
            if 'stats' not in dashboard_data:
                dashboard_data['stats'] = {}
            if 'charts' not in dashboard_data:
                dashboard_data['charts'] = {}
            if 'alerts' not in dashboard_data:
                dashboard_data['alerts'] = []
            if 'quick_lists' not in dashboard_data:
                dashboard_data['quick_lists'] = {}
            
            # 🔴 بروزرسانی فقط اگر ویجت‌ها موجود باشند
            # 🔴 و با بررسی blockSignals برای جلوگیری از خطاهای dataChanged
            if hasattr(self, 'stats_widget'):
                try:
                    # 🔴 بررسی وجود مدل
                    if hasattr(self.stats_widget, 'model'):
                        model = self.stats_widget.model()
                        if model:
                            model.blockSignals(True)
                    
                    self.stats_widget.update_stats(dashboard_data['stats'])
                    
                    if hasattr(self.stats_widget, 'model'):
                        model = self.stats_widget.model()
                        if model:
                            model.blockSignals(False)
                            # 🔴 فقط اگر تغییرات معتبر باشد
                            if model.rowCount() > 0 and model.columnCount() > 0:
                                model.layoutChanged.emit()
                                
                except Exception as e:
                    print(f"❌ خطا در بروزرسانی آمار: {e}")
            
            if hasattr(self, 'charts_widget'):
                try:
                    self.charts_widget.update_charts(dashboard_data['charts'])
                except Exception as e:
                    print(f"❌ خطا در بروزرسانی نمودارها: {e}")
            
            if hasattr(self, 'alerts_widget'):
                try:
                    self.alerts_widget.update_alerts(dashboard_data['alerts'])
                except Exception as e:
                    print(f"❌ خطا در بروزرسانی هشدارها: {e}")
            
            if hasattr(self, 'quick_lists_widget'):
                try:
                    self.quick_lists_widget.update_lists(dashboard_data['quick_lists'])
                except Exception as e:
                    print(f"❌ خطا در بروزرسانی لیست‌های سریع: {e}")
            
            print("✅ داشبورد بروزرسانی شد")
            
        except Exception as e:
            print(f"❌ خطا در بروزرسانی داشبورد: {e}")
            import traceback
            traceback.print_exc()

    def refresh_old_dashboard_data(self):
        """بروزرسانی داده‌های داشبورد قدیمی"""
        try:
                    
            if hasattr(self, 'receptions_table'):
                self.receptions_table.blockSignals(True)
            
            if hasattr(self, 'checks_table'):
                self.checks_table.blockSignals(True)

            # 🔴 **آمار پذیرش‌های امروز**
            today = datetime.now().date()
            today_str = today.strftime('%Y-%m-%d')
            
            # همه پذیرش‌ها را بگیر
            all_receptions = self.data_manager.reception.get_all_receptions()
            
            # شمارش پذیرش‌های امروز
            today_count = 0
            for reception in all_receptions:
                rec_date = reception.get('reception_date', '')
                if rec_date and str(rec_date).startswith(today_str):
                    today_count += 1
            
            # 🔴 **دستگاه‌های در حال تعمیر**
            repairing_count = 0
            for reception in all_receptions:
                if reception.get('status') == 'در حال تعمیر':
                    repairing_count += 1
            
            # 🔴 **قطعات با موجودی کم**
            low_stock_parts = self.data_manager.part.get_low_stock_parts()
            low_stock_count = len(low_stock_parts)
            
            # 🔴 **چک‌های در سررسید**
            due_checks = self.data_manager.check_manager.get_checks_due_soon(days=7)
            due_checks_count = len(due_checks) if due_checks else 0
            
            # به‌روزرسانی ویجت‌های داشبورد
            self.update_dashboard_widgets(today_count, repairing_count, low_stock_count, due_checks_count)
            
            # بارگذاری پذیرش‌های اخیر
            recent_receptions = all_receptions[:10] if len(all_receptions) > 10 else all_receptions
            
            # بارگذاری چک‌های در سررسید
            if hasattr(self, 'checks_table'):
                self.load_due_checks(due_checks)
                
            if hasattr(self, 'receptions_table'):
                self.receptions_table.blockSignals(False)
                if self.receptions_table.rowCount() > 0:
                    self.receptions_table.viewport().update()
            
            if hasattr(self, 'checks_table'):
                self.checks_table.blockSignals(False)
                if self.checks_table.rowCount() > 0:
                    self.checks_table.viewport().update()
                    
        except Exception as e:
            print(f"خطا در به‌روزرسانی داشبورد: {e}")
    
    def on_alert_action(self, data):
        """مدیریت عمل روی هشدار"""
        try:
            alert_type = data.get('type')
            alert_data = data.get('alert_data', {})
            action = alert_data.get('action', '')
            
            if alert_type == 'alert_action':
                if action == 'receptions':
                    self.open_reception_management()
                elif action == 'inventory':
                    self.open_inventory_main()
                elif action == 'checks':
                    self.open_checks_form()
                elif action == 'customers':
                    self.open_persons_management()
                elif action == 'repairs':
                    self.open_repairs_management()
            
            print(f"📝 عمل روی هشدار: {action}")
            
        except Exception as e:
            print(f"خطا در مدیریت هشدار: {e}")
    
    def on_list_action(self, data):
        """مدیریت عمل روی لیست"""
        try:
            action_type = data.get('type')
            list_type = data.get('list_type', '')
            
            if action_type == 'view_more':
                if 'پذیرش' in list_type:
                    self.open_reception_management()
                elif 'چک' in list_type:
                    self.open_checks_form()
                elif 'موجودی' in list_type:
                    self.open_inventory_main()
                elif 'مشتری' in list_type:
                    self.open_persons_management()
            
            print(f"📝 عمل روی لیست: {list_type}")
            
        except Exception as e:
            print(f"خطا در مدیریت لیست: {e}")


    def clear_central_widget(self):
        """پاک کردن ویجت مرکزی فعلی"""
        old_widget = self.centralWidget()
        if old_widget:
            old_widget.setParent(None)
            old_widget.deleteLater()


    def show_dashboard(self):
        """نمایش داشبورد اصلی"""
        self.clear_central_widget()
        
        # ایجاد دوباره ویجت مرکزی
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # ایجاد layout اصلی (مشابه init_ui)
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)
        
        # ایجاد دوباره داشبورد
        dashboard_frame = QFrame()
        dashboard_frame.setStyleSheet("""
            QFrame {
                background-color: #1e1e1e;
                border-radius: 10px;
                border: 1px solid #333;
            }
        """)
        
        dashboard_layout = QVBoxLayout()
        dashboard_layout.setContentsMargins(15, 15, 15, 15)
        
        # عنوان داشبورد
        dashboard_title = QLabel("📊 داشبورد مدیریت - تعمیرگاه شیروین")
        dashboard_title.setStyleSheet("""
            QLabel {
                font-size: 20px;
                font-weight: bold;
                color: white;
                padding-bottom: 10px;
                border-bottom: 2px solid #3498db;
            }
        """)
        dashboard_layout.addWidget(dashboard_title)
        
        # ویجت‌های آماری
        stats_widget = self.create_stats_widget()
        dashboard_layout.addWidget(stats_widget)
        
        dashboard_frame.setLayout(dashboard_layout)
        main_layout.addWidget(dashboard_frame)
        
        central_widget.setLayout(main_layout)
        
        # تازه‌سازی داده‌ها
        self.refresh_dashboard_data()
        
        # تنظیم عنوان
        self.setWindowTitle("سیستم مدیریت تعمیرگاه لوازم خانگی شیروین")

       
    def get_style_sheet(self):
        """استایل‌شیت برنامه با تم تاریک (نسخه اصلاح شده بدون layout-direction)"""
        return """
        /* استایل کلی - راست‌چین با ترتیب معکوس تب‌ها */
        QMainWindow {
            background-color: #000000;
            color: white;
        }
        
        QWidget {
            font-family: 'B Nazanin', Tahoma;
            background-color: #000000;
            color: white;
        }
        
        /* منو بار */
        QMenuBar {
            background-color: #111111;
            color: white;
            font-size: 13px;
            padding: 5px;
            border-bottom: 1px solid #333;
        }
        
        /* منوها - راست‌چین با padding معکوس */
        QMenu {
            background-color: #111111;
            border: 1px solid #333;
            border-radius: 5px;
        }
        
        QMenu::item {
            padding: 8px 25px 8px 20px;  /* راست: 25px، چپ: 20px */
            color: white;
            text-align: right;
        }
        
        QMenu::item:selected {
            background-color: #3498db;
            color: white;
        }
        
        /* نوار ابزار */
        QToolBar {
            background-color: #111111;
            border-bottom: 1px solid #333;
            spacing: 10px;
            padding: 5px;
        }
        
        QToolButton {
            background-color: transparent;
            border: 1px solid transparent;
            border-radius: 4px;
            padding: 8px;
            color: white;
        }
        
        QToolButton:hover {
            background-color: #333;
            color: white;
        }
        
        QToolButton:pressed {
            background-color: #444;
        }
        
        /* تب‌ها - شروع از راست با تنظیمات خاص */
        QTabBar {
            /* جهت از طریق کد تنظیم می‌شود، نه CSS */
        }
        
        QTabBar::tab {
            background-color: #2c2c2c;
            color: #bbb;
            padding: 8px 15px;
            margin-left: 2px;  /* معکوس کردن margin */
            margin-right: 0px;
            border-top-left-radius: 4px;
            border-top-right-radius: 4px;
        }
        
        QTabBar::tab:first {
            margin-left: 0px;
        }
        
        QTabBar::tab:last {
            margin-right: 0px;
        }
        
        QTabBar::tab:selected {
            background-color: #3498db;
            color: white;
            font-weight: bold;
        }
        
        QTabBar::tab:hover:!selected {
            background-color: #3c3c3c;
        }
        
        QTabWidget::pane {
            border: 1px solid #333;
            background-color: #1e1e1e;
            border-radius: 5px;
        }
        
        /* منو بار آیتم‌ها */
        QMenuBar::item {
            background-color: transparent;
            padding: 5px 15px;
            border-radius: 3px;
        }
        
        QMenuBar::item:selected {
            background-color: #2c2c2c;
        }
        
        /* نوار وضعیت */
        QStatusBar {
            background-color: #1e1e1e;
            color: white;
            font-size: 12px;
            border-top: 1px solid #333;
        }
        
        /* جدول */
        QTableWidget {
            background-color: #1e1e1e;
            alternate-background-color: #2c2c2c;
            selection-background-color: #3498db;
            selection-color: white;
            gridline-color: #333;
            color: white;
        }
        
        QTableWidget::item {
            padding: 5px;
            color: white;
        }
        
        QHeaderView::section {
            background-color: #2c3e50;
            color: white;
            padding: 8px;
            border: none;
            font-weight: bold;
            text-align: right;  /* متن سرستون‌ها راست‌چین */
        }
        
        /* دکمه‌ها */
        QPushButton {
            padding: 8px 15px;
            border-radius: 4px;
            font-weight: bold;
            border: none;
            color: white;
        }
        
        QPushButton.primary {
            background-color: #27ae60;
        }
        
        QPushButton.primary:hover {
            background-color: #219653;
        }
        
        QPushButton.secondary {
            background-color: #3498db;
        }
        
        QPushButton.secondary:hover {
            background-color: #2980b9;
        }
        
        QPushButton.danger {
            background-color: #e74c3c;
        }
        
        QPushButton.danger:hover {
            background-color: #c0392b;
        }
        
        /* Dock Widget */
        QDockWidget {
            border: 1px solid #333;
            titlebar-close-icon: url(close.png);
            titlebar-normal-icon: url(float.png);
            background-color: #1e1e1e;
        }
        
        QDockWidget::title {
            background-color: #2c2c2c;
            color: white;
            padding: 5px;
            text-align: center;
        }
        
        /* Tree Widget */
        QTreeWidget {
            background-color: #1e1e1e;
            border: 1px solid #333;
            border-radius: 3px;
            color: white;
        }
        
        QTreeWidget::item {
            padding: 5px;
            color: white;
        }
        
        QTreeWidget::item:selected {
            background-color: #3498db;
            color: white;
        }
        
        /* فیلدهای ورودی */
        QLineEdit, QTextEdit, QComboBox {
            background-color: #2c2c2c;
            color: white;
            border: 1px solid #333;
            border-radius: 4px;
            padding: 8px;
            selection-background-color: #3498db;
        }
        
        QLineEdit:focus, QTextEdit:focus, QComboBox:focus {
            border: 2px solid #3498db;
        }
        
        QLineEdit::placeholder, QTextEdit::placeholder {
            color: #666;
            text-align: right;  /* متن placeholder راست‌چین */
        }
        
        /* برچسب‌ها */
        QLabel {
            color: white;
        }
        
        /* Frame */
        QFrame {
            background-color: #1e1e1e;
            border: 1px solid #333;
        }
        
        /* اسکرول بار */
        QScrollBar:vertical {
            background-color: #2c2c2c;
            width: 16px;
            border-radius: 8px;
            margin: 2px;
        }
        
        QScrollBar::handle:vertical {
            background-color: #444;
            border-radius: 8px;
            min-height: 30px;
        }
        
        QScrollBar::handle:vertical:hover {
            background-color: #555;
        }
        
        QScrollBar:horizontal {
            background-color: #2c2c2c;
            height: 16px;
            border-radius: 8px;
            margin: 2px;
        }
        
        QScrollBar::handle:horizontal {
            background-color: #444;
            border-radius: 8px;
            min-width: 30px;
        }
        
        QScrollBar::handle:horizontal:hover {
            background-color: #555;
        }
        
        /* استایل‌های اضافی برای راست‌چین */
        QListWidget {
            text-align: right;
        }
        
        QListWidget::item {
            text-align: right;
        }
        
        QComboBox QAbstractItemView {
            text-align: right;
        }
        
        QGroupBox {
            text-align: right;
        }
        
        QRadioButton {
            spacing: 10px;
        }
        
        QCheckBox {
            spacing: 10px;
        }
        """
 
    def set_fonts(self):
        """تنظیم فونت‌های فارسی"""
        font = QFont()
        font.setFamily("B Nazanin")
        font.setPointSize(10)
        QApplication.setFont(font)
        
    def create_menu_bar(self):
        """ایجاد نوار منو"""
        menubar = self.menuBar()
        
        # منوی فایل
        file_menu = menubar.addMenu("📁 فایل")
        
        new_reception_action = QAction("📝 پذیرش جدید", self)
        new_reception_action.triggered.connect(self.new_reception)
        file_menu.addAction(new_reception_action)
        
        file_menu.addSeparator()
        
        print_action = QAction("🖨️ چاپ", self)
        print_action.setShortcut("Ctrl+P")
        file_menu.addAction(print_action)
        
        backup_action = QAction("💾 پشتیبان‌گیری", self)
        backup_action.triggered.connect(self.backup_database)
        file_menu.addAction(backup_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("🚪 خروج", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # منوی مدیریت
        manage_menu = menubar.addMenu("👥 مدیریت")
        
        persons_action = QAction("👥 مدیریت اشخاص", self)
        persons_action.triggered.connect(self.open_persons_management)
        manage_menu.addAction(persons_action)
        
        # منوی مدیریت - بعد از persons_action
        reception_action = QAction("📝 مدیریت پذیرش", self)
        reception_action.triggered.connect(self.open_reception_management)
        manage_menu.addAction(reception_action)

        devices_action = QAction("📱 مدیریت دستگاه‌ها", self)
        devices_action.triggered.connect(self.open_devices_management)
        manage_menu.addAction(devices_action)
        
        repairs_action = QAction("🔧 مدیریت تعمیرات", self)
        repairs_action.triggered.connect(self.open_repairs_management)
        manage_menu.addAction(repairs_action)

        parts_action = QAction("🔩 مدیریت قطعات", self)
        parts_action.triggered.connect(self.open_parts_management)
        manage_menu.addAction(parts_action)
        
        manage_menu.addSeparator()
        
        users_action = QAction("👤 مدیریت کاربران", self)
        users_action.triggered.connect(self.open_users_management)
        manage_menu.addAction(users_action)
        
        # منوی تعمیرات
        repair_menu = menubar.addMenu("🔧 تعمیرات")

        # آیتم مدیریت تعمیرات
        act_manage_repairs = QAction("📋 مدیریت تعمیرات", self)
        act_manage_repairs.triggered.connect(self.open_repairs_management)
        repair_menu.addAction(act_manage_repairs)

        # آیتم مشاهده تعمیرات جاری
        act_current_repairs = QAction("⚡ تعمیرات در حال انجام", self)
        act_current_repairs.triggered.connect(self.show_current_repairs)
        repair_menu.addAction(act_current_repairs)

        repair_menu.addSeparator()

        # آیتم اجرت‌های استاندارد
        act_service_fees = QAction("💰 مدیریت اجرت‌های استاندارد", self)
        act_service_fees.triggered.connect(self.manage_service_fees)
        repair_menu.addAction(act_service_fees)

        # منوی انبار
        inventory_menu = menubar.addMenu("📦 انبار")
        
        act_inventory_main = QAction("🏠 مدیریت انبار", self)
        act_inventory_main.triggered.connect(self.open_inventory_main)
        inventory_menu.addAction(act_inventory_main)
        
        inventory_menu.addSeparator()
        
        act_new_parts = QAction("🔧 قطعات نو", self)
        act_new_parts.triggered.connect(self.open_inventory_new_parts)
        inventory_menu.addAction(act_new_parts)
        
        act_used_parts = QAction("🔩 قطعات دست دوم", self)
        act_used_parts.triggered.connect(self.open_inventory_used_parts)
        inventory_menu.addAction(act_used_parts)
        
        act_new_appliances = QAction("🏠 لوازم نو", self)
        act_new_appliances.triggered.connect(self.open_inventory_new_appliances)
        inventory_menu.addAction(act_new_appliances)
        
        act_used_appliances = QAction("🏚️ لوازم دست دوم", self)
        act_used_appliances.triggered.connect(self.open_inventory_used_appliances)
        inventory_menu.addAction(act_used_appliances)
        
        inventory_menu.addSeparator()
        
        act_inventory_report = QAction("📊 گزارش انبار", self)
        act_inventory_report.triggered.connect(self.open_inventory_report)
        inventory_menu.addAction(act_inventory_report)
        
        act_low_stock = QAction("⚠️ موجودی کم", self)
        act_low_stock.triggered.connect(self.show_low_stock)
        inventory_menu.addAction(act_low_stock)

        act_inventory_settings = QAction("⚙️ تنظیمات انبار", self)
        act_inventory_settings.triggered.connect(self.open_inventory_settings)
        inventory_menu.addAction(act_inventory_settings)


        """تنظیم منوی حسابداری"""
        accounting_menu = self.menuBar().addMenu("🏦 حسابداری")
        
        # آیتم اصلی داشبورد حسابداری
        act_accounting_dashboard = QAction("📊 پنجره مستقل حسابداری", self)
        act_accounting_dashboard.triggered.connect(self.open_accounting_window)
        accounting_menu.addAction(act_accounting_dashboard)
        
        accounting_menu.addSeparator()
        
        # حساب‌ها
        act_accounts = QAction("🏦 حساب‌ها", self)
        act_accounts.triggered.connect(self.open_accounts_form)
        accounting_menu.addAction(act_accounts)
        
        # تراکنش‌ها
        act_transactions = QAction("💰 تراکنش‌ها", self)
        act_transactions.triggered.connect(self.open_transactions_form)
        accounting_menu.addAction(act_transactions)
        
        # فاکتورها
        act_invoices = QAction("🧾 فاکتورها", self)
        act_invoices.triggered.connect(self.open_invoices_form)
        accounting_menu.addAction(act_invoices)
        
        # چک‌ها
        act_checks = QAction("💳 چک‌ها", self)
        act_checks.triggered.connect(self.open_checks_form)
        accounting_menu.addAction(act_checks)
        
        # شرکا
        act_partners = QAction("🤝 شرکا", self)
        act_partners.triggered.connect(self.open_partners_form)
        accounting_menu.addAction(act_partners)
        
        accounting_menu.addSeparator()
        
        # محاسبه سود
        act_profit = QAction("📈 محاسبه سود", self)
        act_profit.triggered.connect(self.open_profit_calculation)
        accounting_menu.addAction(act_profit)
        
        # گزارش‌های مالی
        act_reports = QAction("📊 گزارش‌های مالی", self)
        act_reports.triggered.connect(self.open_financial_reports)
        accounting_menu.addAction(act_reports)
        
        # خلاصه روزانه
        act_daily_summary = QAction("📋 خلاصه روزانه", self)
        act_daily_summary.triggered.connect(self.open_daily_summary)
        accounting_menu.addAction(act_daily_summary)
        
        accounting_menu.addSeparator()
        
        # تنظیمات مالی
        act_settings = QAction("⚙️ تنظیمات مالی", self)
        act_settings.triggered.connect(self.open_accounting_settings)
        accounting_menu.addAction(act_settings)
        
        # منوی گزارشات
        # بخش منوی گزارشات را به این صورت تغییر دهید:
        # منوی گزارشات
        reports_menu = menubar.addMenu("📊 گزارشات")

        # پنجره مستقل گزارش‌گیری
        reports_window_action = QAction("📊 پنجره مستقل گزارش‌گیری", self)
        reports_window_action.triggered.connect(self.open_reports_window)
        reports_menu.addAction(reports_window_action)

        reports_menu.addSeparator()

        # گزارش روزانه
        daily_report_action = QAction("📅 گزارش روزانه", self)
        daily_report_action.triggered.connect(lambda: self.open_reports_tab(0))
        reports_menu.addAction(daily_report_action)

        # گزارش هفتگی
        weekly_report_action = QAction("📆 گزارش هفتگی", self)
        weekly_report_action.triggered.connect(lambda: self.open_reports_tab(1))
        reports_menu.addAction(weekly_report_action)

        # گزارش ماهانه
        monthly_report_action = QAction("📅 گزارش ماهانه", self)
        monthly_report_action.triggered.connect(lambda: self.open_reports_tab(2))
        reports_menu.addAction(monthly_report_action)

        reports_menu.addSeparator()

        # گزارش مالی
        financial_report_action = QAction("💰 گزارش مالی", self)
        financial_report_action.triggered.connect(lambda: self.open_reports_tab(3))
        reports_menu.addAction(financial_report_action)

        # گزارش انبار
        inventory_report_action = QAction("📦 گزارش انبار", self)
        inventory_report_action.triggered.connect(lambda: self.open_reports_tab(4))
        reports_menu.addAction(inventory_report_action)

        # گزارش تعمیرات
        repair_report_action = QAction("🔧 گزارش تعمیرات", self)
        repair_report_action.triggered.connect(lambda: self.open_reports_tab(5))
        reports_menu.addAction(repair_report_action)

        # گزارش فروش
        sales_report_action = QAction("🛒 گزارش فروش", self)
        sales_report_action.triggered.connect(lambda: self.open_reports_tab(6))
        reports_menu.addAction(sales_report_action)

        # گزارش مشتریان
        customer_report_action = QAction("👥 گزارش مشتریان", self)
        customer_report_action.triggered.connect(lambda: self.open_reports_tab(7))
        reports_menu.addAction(customer_report_action)

        reports_menu.addSeparator()

        # گزارش‌گیری سریع
        quick_reports_submenu = reports_menu.addMenu("⚡ گزارش‌گیری سریع")
        act_quick_daily = QAction("📅 خلاصه روز", self)
        act_quick_daily.triggered.connect(self.quick_daily_report)
        quick_reports_submenu.addAction(act_quick_daily)

        act_quick_financial = QAction("💰 وضعیت مالی", self)
        act_quick_financial.triggered.connect(self.quick_financial_report)
        quick_reports_submenu.addAction(act_quick_financial)

        act_quick_inventory = QAction("📦 وضعیت انبار", self)
        act_quick_inventory.triggered.connect(self.quick_inventory_report)
        quick_reports_submenu.addAction(act_quick_inventory)
        
        # منوی تنظیمات
        settings_menu = menubar.addMenu("⚙️ تنظیمات")

        # تنظیمات کلی
        act_general_settings = QAction("⚙️ تنظیمات کلی", self)
        act_general_settings.triggered.connect(self.open_settings_window)
        settings_menu.addAction(act_general_settings)

        settings_menu.addSeparator()

        # مدیریت کاربران
        act_user_management = QAction("👥 مدیریت کاربران", self)
        act_user_management.triggered.connect(lambda: self.open_settings_window("users"))
        settings_menu.addAction(act_user_management)

        # پشتیبان‌گیری
        act_backup_settings = QAction("💾 تنظیمات پشتیبان", self)
        act_backup_settings.triggered.connect(lambda: self.open_settings_window("backup"))
        settings_menu.addAction(act_backup_settings)

        # تنظیمات پیامکی
        act_sms_settings = QAction("📱 تنظیمات پیامکی", self)
        act_sms_settings.triggered.connect(lambda: self.open_settings_window("sms"))
        settings_menu.addAction(act_sms_settings)

        # تنظیمات انبار
        act_inventory_settings = QAction("📦 تنظیمات انبار", self)
        act_inventory_settings.triggered.connect(lambda: self.open_settings_window("inventory"))
        settings_menu.addAction(act_inventory_settings)

        # تنظیمات امنیتی
        act_security_settings = QAction("🔐 تنظیمات امنیتی", self)
        act_security_settings.triggered.connect(lambda: self.open_settings_window("security"))
        settings_menu.addAction(act_security_settings)
        
        # منوی راهنما
        help_menu = menubar.addMenu("❓ راهنما")
        
        about_action = QAction("ℹ️ درباره برنامه", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
        
        help_action = QAction("📚 راهنمای استفاده", self)
        help_action.triggered.connect(self.show_help)
        help_menu.addAction(help_action)

    def create_toolbar(self):
        """ایجاد نوار ابزار"""
        toolbar = QToolBar("نوار ابزار اصلی")
        toolbar.setIconSize(QSize(32, 32))
        self.addToolBar(toolbar)
        
        # دکمه‌های نوار ابزار
        toolbar.addAction(self.create_toolbar_action("📝", "پذیرش جدید", self.new_reception))
        toolbar.addSeparator()
        
        toolbar.addAction(self.create_toolbar_action("👥", "اشخاص", self.open_persons_management))
        toolbar.addAction(self.create_toolbar_action("📱", "دستگاه‌ها", self.open_devices_management))
        toolbar.addSeparator()
        
        toolbar.addAction(self.create_toolbar_action("🔧", "تعمیرات", self.open_repairs_management))
        toolbar.addAction(self.create_toolbar_action("📦", "انبار", self.open_inventory_main))
        toolbar.addSeparator()
        
        toolbar.addAction(self.create_toolbar_action("💰", "حسابداری", self.open_accounting_dashboard))
        toolbar.addAction(self.create_toolbar_action("📊", "گزارشات", self.open_reports_dashboard))
        
    def create_toolbar_action(self, icon_text, text, callback):
        """ایجاد اکشن برای نوار ابزار"""
        action = QAction(icon_text + " " + text, self)
        action.triggered.connect(callback)
        return action
    
    def create_status_bar(self):
        """ایجاد نوار وضعیت"""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        # برچسب تاریخ
        self.date_label = QLabel()
        self.status_bar.addPermanentWidget(self.date_label)
        
        # برچسب کاربر
        self.user_label = QLabel()
        self.status_bar.addPermanentWidget(self.user_label)
        
        # برچسب وضعیت دیتابیس
        self.db_status_label = QLabel("✅ دیتابیس متصل")
        self.db_status_label.setStyleSheet("color: #27ae60;")
        self.status_bar.addWidget(self.db_status_label)
        
        # برچسب زمان
        self.time_label = QLabel()
        self.status_bar.addPermanentWidget(self.time_label)
        
        # به‌روزرسانی زمان
        self.update_datetime()
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_datetime)
        self.timer.start(1000)  # به‌روزرسانی هر ثانیه
    
    def update_datetime(self):
        """به‌روزرسانی تاریخ و زمان شمسی"""
        now = jdatetime.datetime.now()
        
        # تاریخ کامل به شمسی
        jalali_date = now.strftime('%Y/%m/%d')
        jalali_day_name = now.strftime('%A')
        self.date_label.setText(f"📅 {jalali_date} - {jalali_day_name}")
        
        # زمان
        time_str = now.strftime('%H:%M:%S')
        self.time_label.setText(f"🕒 {time_str}")

    def create_stats_widget(self):
        """ایجاد ویجت آمارهای مهم"""
        stats_widget = QWidget()
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(15)
        
        # آمار ۱: پذیرش‌های امروز
        today_stats = self.create_stat_box("📅 پذیرش‌های امروز", "0", "#3498db", "تعداد پذیرش‌های امروز")
        stats_layout.addWidget(today_stats)
        
        # آمار ۲: دستگاه‌های در حال تعمیر
        repairing_stats = self.create_stat_box("🔧 در حال تعمیر", "0", "#e74c3c", "دستگاه‌های در حال تعمیر")
        stats_layout.addWidget(repairing_stats)
        
        # آمار ۳: قطعات با موجودی کم
        low_stock_stats = self.create_stat_box("📦 موجودی کم", "0", "#f39c12", "قطعات با موجودی کمتر از حداقل")
        stats_layout.addWidget(low_stock_stats)
        
        # آمار ۴: چک‌های در سررسید
        due_checks_stats = self.create_stat_box("💳 چک سررسید", "0", "#9b59b6", "چک‌های در سررسید ۷ روز آینده")
        stats_layout.addWidget(due_checks_stats)
        
        stats_widget.setLayout(stats_layout)
        return stats_widget
    
    def create_stat_box(self, title, value, color, description):
        """ایجاد جعبه آمار با تم تاریک"""
        box = QFrame()
        box.setStyleSheet(f"""
            QFrame {{
                background-color: #1e1e1e;
                border-radius: 8px;
                border: 2px solid {color};
                min-width: 200px;
            }}
        """)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(15, 15, 15, 15)
        
        # عنوان
        title_label = QLabel(title)
        title_label.setStyleSheet("""
            QLabel {
                font-size: 14px;
                color: #bbb;
                font-weight: bold;
            }
        """)
        layout.addWidget(title_label)
        
        # مقدار
        value_label = QLabel(value)
        value_label.setStyleSheet(f"""
            QLabel {{
                font-size: 28px;
                font-weight: bold;
                color: {color};
            }}
        """)
        layout.addWidget(value_label)
        
        # توضیحات
        desc_label = QLabel(description)
        desc_label.setStyleSheet("""
            QLabel {
                font-size: 11px;
                color: #999;
            }
        """)
        layout.addWidget(desc_label)
        
        box.setLayout(layout)
        return box
    
    def create_side_panel(self):
        """ایجاد پنل کناری با تم تاریک"""
        dock_widget = QDockWidget("🔍 پنل دسترسی سریع", self)
        dock_widget.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        
        side_widget = QWidget()
        side_widget.setStyleSheet("background-color: #1e1e1e;")
        side_layout = QVBoxLayout()
        
        self.create_dashboard()

        # اطلاعات کاربر
        user_frame = QFrame()
        user_frame.setStyleSheet("""
            QFrame {
                background-color: #2c2c2c;
                border-radius: 8px;
                padding: 10px;
            }
        """)
        
        user_layout = QVBoxLayout()
        
        user_icon = QLabel("👤")
        user_icon.setStyleSheet("font-size: 40px; text-align: center; color: white;")
        user_icon.setAlignment(Qt.AlignCenter)
        user_layout.addWidget(user_icon)
        
        self.user_name_label = QLabel()
        self.user_name_label.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 14px;
                font-weight: bold;
                text-align: center;
            }
        """)
        user_layout.addWidget(self.user_name_label)
        
        self.user_role_label = QLabel()
        self.user_role_label.setStyleSheet("""
            QLabel {
                color: #bbb;
                font-size: 12px;
                text-align: center;
            }
        """)
        user_layout.addWidget(self.user_role_label)
        
        user_frame.setLayout(user_layout)
        side_layout.addWidget(user_frame)
        
        # دسترسی‌های سریع
        quick_access_label = QLabel("⚡ دسترسی سریع")
        quick_access_label.setStyleSheet("""
            QLabel {
                font-size: 14px;
                font-weight: bold;
                color: white;
                margin-top: 15px;
            }
        """)
        side_layout.addWidget(quick_access_label)

        # دکمه‌های دسترسی سریع
        quick_buttons = [
            ("📝 پذیرش جدید", self.new_reception, "#27ae60"),
            ("👤 ثبت مشتری جدید", self.open_persons_management, "#3498db"),
            ("📱 ثبت دستگاه جدید", self.open_devices_management, "#9b59b6"),
            ("🔧 ثبت تعمیر جدید", self.open_repairs_management, "#e74c3c"),
            ("📦 ورود به انبار", self.new_inventory_entry, "#f39c12"),
            ("🧾 صدور فاکتور", self.new_invoice, "#1abc9c"),
        ]
        
        for text, callback, color in quick_buttons:
            btn = QPushButton(text)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {color};
                    color: white;
                    padding: 10px;
                    border-radius: 5px;
                    text-align: right;
                    font-size: 13px;
                    font-weight: bold;
                    border: none;
                }}
                QPushButton:hover {{
                    background-color: {self.darken_color(color)};
                }}
            """)
            btn.clicked.connect(callback)
            side_layout.addWidget(btn)
        
        side_layout.addStretch()
        
        # وضعیت سیستم
        system_status_label = QLabel("🖥️ وضعیت سیستم")
        system_status_label.setStyleSheet("""
            QLabel {
                font-size: 14px;
                font-weight: bold;
                color: white;
                margin-top: 15px;
            }
        """)
        side_layout.addWidget(system_status_label)
        
        system_frame = QFrame()
        system_frame.setStyleSheet("""
            QFrame {
                background-color: #2c2c2c;
                border-radius: 5px;
                border: 1px solid #333;
                padding: 10px;
            }
        """)
        
        system_layout = QVBoxLayout()
        
        system_items = [
            ("✅ دیتابیس", "متصل"),
            ("📊 کل مشتریان", "0"),
            ("🔩 کل قطعات", "0"),
            ("📦 موجودی کل", "0"),
        ]
        
        for icon_text, value in system_items:
            item_layout = QHBoxLayout()
            
            item_label = QLabel(icon_text)
            item_label.setStyleSheet("font-size: 12px; color: white;")
            
            value_label = QLabel(value)
            value_label.setStyleSheet("""
                QLabel {
                    font-size: 12px;
                    font-weight: bold;
                    color: #3498db;
                }
            """)
            value_label.setAlignment(Qt.AlignLeft)
            
            item_layout.addWidget(item_label)
            item_layout.addStretch()
            item_layout.addWidget(value_label)
            system_layout.addLayout(item_layout)
        
        system_frame.setLayout(system_layout)
        side_layout.addWidget(system_frame)
        
        side_widget.setLayout(side_layout)
        dock_widget.setWidget(side_widget)
        
        self.addDockWidget(Qt.RightDockWidgetArea, dock_widget)
    
    def darken_color(self, color):
        """تیره کردن رنگ برای hover"""
        # تبدیل هگز به RGB
        color = color.lstrip('#')
        r, g, b = tuple(int(color[i:i+2], 16) for i in (0, 2, 4))
        
        # کاهش روشنایی
        r = max(0, r - 30)
        g = max(0, g - 30)
        b = max(0, b - 30)
        
        return f'#{r:02x}{g:02x}{b:02x}'
    
    def setup_connections(self):
        """تنظیم اتصالات"""
        # اتصالات تایمر برای به‌روزرسانی داده‌ها
        self.data_timer = QTimer()
        self.data_timer.timeout.connect(self.refresh_dashboard_data)
        self.data_timer.start(30000)  # هر 30 ثانیه
    
    def load_initial_data(self):
        """بارگذاری داده‌های اولیه"""
        self.refresh_dashboard_data()

    def on_date_range_changed(self):
        """وقتی تاریخ تغییر کرد"""
        pass  # می‌توانید عملیات لازم را اضافه کنید

    def apply_date_filter(self):
        """اعمال فیلتر تاریخ"""
        if not JALALI_WIDGET_AVAILABLE:
            return
        
        try:
            start_date = self.start_date_widget.get_miladi_date()
            end_date = self.end_date_widget.get_miladi_date()
            
            print(f"فیلتر تاریخ اعمال شد: از {start_date} تا {end_date}")
            
            # اینجا می‌توانید داده‌ها را بر اساس تاریخ فیلتر کنید
            # مثلاً:
            # filtered_receptions = self.filter_receptions_by_date(start_date, end_date)
            # self.load_recent_receptions(filtered_receptions)
            
            QMessageBox.information(self, "فیلتر تاریخ", 
                f"فیلتر تاریخ اعمال شد.\n"
                f"از: {self.start_date_widget.get_jalali_date()}\n"
                f"تا: {self.end_date_widget.get_jalali_date()}")
            
        except Exception as e:
            print(f"خطا در اعمال فیلتر تاریخ: {e}")

    def reset_date_filter(self):
        """بازنشانی فیلتر تاریخ"""
        if not JALALI_WIDGET_AVAILABLE:
            return
        
        try:
            self.start_date_widget.set_to_today()
            self.end_date_widget.set_to_today()
            print("فیلتر تاریخ بازنشانی شد")
            
            # اینجا می‌توانید همه داده‌ها را دوباره بارگذاری کنید
            # self.refresh_dashboard_data()
            
        except Exception as e:
            print(f"خطا در بازنشانی فیلتر تاریخ: {e}")


    def update_stat_box(self, stat_box, value):
        """به‌روزرسانی مقدار جعبه آمار"""
        try:
            # پیدا کردن لیبل مقدار در داخل جعبه
            value_labels = stat_box.findChildren(QLabel)
            for label in value_labels:
                if label.text().isdigit() or label.text() == "0":
                    label.setText(value)
                    break
        except Exception as e:
            print(f"خطا در به‌روزرسانی جعبه آمار: {e}")

    def update_system_status(self):
        """به‌روزرسانی وضعیت سیستم در پنل کناری"""
        try:
            # تعداد کل مشتریان
            all_persons = self.data_manager.person.get_all_persons()
            total_customers = len([p for p in all_persons if p.get('person_type') == 'مشتری'])
            
            # تعداد کل قطعات
            all_parts = self.data_manager.part.get_all_parts()
            total_parts = len(all_parts)
            
            # تعداد کل موجودی (مجموع)
            # این نیاز به محاسبه از انبارها دارد
            
            # می‌توانید این مقادیر را در ویجت‌های پنل کناری نمایش دهید
            print(f"آمار سیستم: {total_customers} مشتری، {total_parts} قطعه")
            
        except Exception as e:
            print(f"خطا در به‌روزرسانی وضعیت سیستم: {e}")

    def create_date_selector_widget(self):
        """ایجاد ویجت انتخاب تاریخ برای داشبورد"""
        if not JALALI_WIDGET_AVAILABLE:
            return None
        
        try:
            date_widget = QWidget()
            layout = QHBoxLayout(date_widget)
            layout.setContentsMargins(0, 0, 0, 0)
            layout.setSpacing(10)
            
            # برچسب
            label = QLabel("📅 انتخاب بازه زمانی:")
            label.setStyleSheet("color: #bbb; font-size: 12px;")
            layout.addWidget(label)
            
            # ویجت تاریخ شروع
            start_label = QLabel("از:")
            start_label.setStyleSheet("color: #999;")
            layout.addWidget(start_label)
            
            self.start_date_widget = JalaliDateWidget()
            self.start_date_widget.set_to_today()  # امروز
            self.start_date_widget.date_changed.connect(self.on_date_range_changed)
            layout.addWidget(self.start_date_widget)
            
            # ویجت تاریخ پایان
            end_label = QLabel("تا:")
            end_label.setStyleSheet("color: #999;")
            layout.addWidget(end_label)
            
            self.end_date_widget = JalaliDateWidget()
            self.end_date_widget.set_to_today()  # امروز
            self.end_date_widget.date_changed.connect(self.on_date_range_changed)
            layout.addWidget(self.end_date_widget)
            
            # دکمه اعمال
            apply_btn = QPushButton("اعمال")
            apply_btn.setStyleSheet("""
                QPushButton {
                    background-color: #3498db;
                    color: white;
                    padding: 5px 15px;
                    border-radius: 4px;
                    font-size: 11px;
                }
                QPushButton:hover {
                    background-color: #2980b9;
                }
            """)
            apply_btn.clicked.connect(self.apply_date_filter)
            layout.addWidget(apply_btn)
            
            # دکمه بازنشانی
            reset_btn = QPushButton("بازنشانی")
            reset_btn.setStyleSheet("""
                QPushButton {
                    background-color: #95a5a6;
                    color: white;
                    padding: 5px 15px;
                    border-radius: 4px;
                    font-size: 11px;
                }
                QPushButton:hover {
                    background-color: #7f8c8d;
                }
            """)
            reset_btn.clicked.connect(self.reset_date_filter)
            layout.addWidget(reset_btn)
            
            layout.addStretch()
            return date_widget
            
        except Exception as e:
            print(f"خطا در ایجاد ویجت انتخاب تاریخ: {e}")
            return None    

    def load_recent_receptions(self, receptions):
        """بارگذاری پذیرش‌های اخیر"""
        self.receptions_table.setRowCount(len(receptions))
        
        for row, reception in enumerate(receptions):
            self.receptions_table.setItem(row, 0, 
                QTableWidgetItem(str(reception.get('reception_number', ''))))
            self.receptions_table.setItem(row, 1, 
                QTableWidgetItem(reception.get('customer_name', '')))
            self.receptions_table.setItem(row, 2, 
                QTableWidgetItem(f"{reception.get('device_type', '')} {reception.get('brand', '')}"))
            
            # 🔴 **تبدیل تاریخ میلادی به شمسی - با استفاده از ویجت**
            reception_date = reception.get('reception_date', '')
            if reception_date:
                try:
                    # استفاده از تابع convert_to_jalali_display که قبلاً دارید
                    jalali_date = convert_to_jalali_display(str(reception_date))
                    self.receptions_table.setItem(row, 3, QTableWidgetItem(jalali_date))
                except Exception as e:
                    print(f"⚠️ خطا در تبدیل تاریخ {reception_date}: {e}")
                    self.receptions_table.setItem(row, 3, QTableWidgetItem(str(reception_date)))
            else:
                self.receptions_table.setItem(row, 3, QTableWidgetItem(''))
            
            self.receptions_table.setItem(row, 4, QTableWidgetItem(str(reception.get('estimated_cost', 0))))
            self.receptions_table.setItem(row, 5, QTableWidgetItem(reception.get('priority', '')))
            
            status_item = QTableWidgetItem(reception.get('status', ''))
            status = reception.get('status', '')
            
            # رنگ‌بندی وضعیت
            color_map = {
                'تعمیر شده': '#27ae60',
                'در حال تعمیر': '#3498db',
                'در انتظار': '#f39c12',
                'تحویل داده شده': '#9b59b6',
                'تحویل شده': '#9b59b6',
                'لغو شده': '#e74c3c'
            }
            
            if status in color_map:
                status_item.setForeground(QColor(color_map[status]))
            
            self.receptions_table.setItem(row, 6, status_item)
  
    def load_due_checks(self, checks_list=None):
        """بارگذاری چک‌های در سررسید"""
        # اگر لیست داده نشده، از دیتابیس بخوان
        if checks_list is None:
            try:
                checks_list = self.data_manager.check_manager.get_checks_due_soon(days=7)
            except Exception as e:
                print(f"⚠️ خطا در دریافت چک‌های سررسید: {e}")
                checks_list = []
        
        # اگر لیست خالی است
        if not checks_list:
            self.checks_table.setRowCount(0)
            # نمایش پیام "چکی یافت نشد"
            self.checks_table.setRowCount(1)
            self.checks_table.setItem(0, 0, QTableWidgetItem("⚠️"))
            self.checks_table.setItem(0, 1, QTableWidgetItem("چکی برای نمایش وجود ندارد"))
            self.checks_table.setSpan(0, 1, 1, 5)  # ادغام سلول‌ها
            return
        
        # نمایش چک‌ها
        self.checks_table.setRowCount(len(checks_list))
        
        for row, check in enumerate(checks_list):
            # شماره چک
            self.checks_table.setItem(row, 0, QTableWidgetItem(str(check.get('check_number', ''))))
            
            # بانک
            self.checks_table.setItem(row, 1, QTableWidgetItem(check.get('bank_name', '')))
            
            # مبلغ
            amount = check.get('amount', 0)
            self.checks_table.setItem(row, 2, QTableWidgetItem(f"{amount:,} تومان"))
            
            # تاریخ سررسید (شمسی)
            due_date = check.get('due_date', '')
            if due_date:
                jalali_date = self.convert_to_jalali_display(due_date)
                self.checks_table.setItem(row, 3, QTableWidgetItem(jalali_date))
            else:
                self.checks_table.setItem(row, 3, QTableWidgetItem(''))
            
            # صادرکننده
            self.checks_table.setItem(row, 4, QTableWidgetItem(check.get('drawer', '')))
            
            # وضعیت با رنگ‌بندی
            status_item = QTableWidgetItem(check.get('status', ''))
            status = check.get('status', '')
            if status == 'وصول شده':
                status_item.setForeground(QColor('#27ae60'))
            elif status == 'وصول نشده':
                status_item.setForeground(QColor('#f39c12'))
            elif status == 'برگشتی':
                status_item.setForeground(QColor('#e74c3c'))
            elif status == 'پاس شده':
                status_item.setForeground(QColor('#3498db'))
            
            self.checks_table.setItem(row, 5, status_item)
    
    def load_customers(self):
        """بارگذاری مشتریان از دیتابیس"""
        try:
            customers = self.data_manager.person.get_all_persons()
            customer_list = [p for p in customers if p.get('person_type') == 'مشتری']
            return customer_list
        except:
            return []

    def load_devices(self):
        """بارگذاری دستگاه‌ها از دیتابیس"""
        try:
            return self.data_manager.device.get_all_devices()
        except:
            return []

    def show_user_info(self):
        """نمایش اطلاعات کاربر"""
        user_name = self.user_data.get('full_name', self.user_data.get('username', 'کاربر'))
        user_role = self.user_data.get('role', 'اپراتور')
        
        self.user_name_label.setText(user_name)
        self.user_role_label.setText(f"نقش: {user_role}")
        
        # به‌روزرسانی نوار وضعیت
        self.user_label.setText(f"👤 {user_name} ({user_role})")
    
    # ---------- متدهای مدیریت فرم‌ها ----------
    
    def new_reception(self):
        """پذیرش جدید - باز کردن فرم پذیرش"""
        # فقط تابع open_reception_management را فراخوانی می‌کنیم
        self.open_reception_management()

    
    def new_customer(self):
        """مشتری جدید - باز کردن فرم اشخاص برای ثبت مشتری"""
        try:
            from ui.forms.person_form import PersonForm
            
            # ایجاد فرم برای ثبت مشتری جدید
            self.person_form = PersonForm(self.data_manager)
            self.person_form.setWindowTitle("ثبت مشتری جدید")
            self.person_form.resize(1100, 750)
            
            # تنظیم نوع شخص به مشتری (اگر قابلیت دارید)
            if hasattr(self.person_form, 'person_type_combo'):
                self.person_form.person_type_combo.setCurrentText("مشتری")
            
            # موقعیت فرم
            main_geometry = self.geometry()
            self.person_form.move(main_geometry.x() + 50, main_geometry.y() + 50)
            
            # اتصال سیگنال
            self.person_form.form_closed.connect(self.on_person_form_closed)
            
            self.person_form.show()
            
        except Exception as e:
            QMessageBox.critical(self, "خطا", f"خطا در ثبت مشتری جدید: {e}")
    
    def new_device(self):
        """دستگاه جدید"""
        QMessageBox.information(self, "دستگاه جدید", "فرم ثبت دستگاه جدید باز خواهد شد.")
    
    def new_repair(self):
        """تعمیر جدید"""
        QMessageBox.information(self, "تعمیر جدید", "فرم ثبت تعمیر جدید باز خواهد شد.")
    
    def new_inventory_entry(self):
        """ورود به انبار"""
        QMessageBox.information(self, "ورود به انبار", "فرم ورود به انبار باز خواهد شد.")
    
    def new_invoice(self):
        """صدور فاکتور"""
        QMessageBox.information(self, "صدور فاکتور", "فرم صدور فاکتور باز خواهد شد.")


    def open_persons_management(self):
        """مدیریت اشخاص"""
        if not PERSON_FORM_AVAILABLE:
            QMessageBox.warning(self, "خطا", "فرم مدیریت اشخاص در دسترس نیست.")
            return
        
        try:
            # ایجاد فرم مدیریت اشخاص
            self.person_form = PersonForm(self.data_manager, person_id=None)
            self.person_form.setWindowTitle("👤 مدیریت اشخاص - سیستم تعمیرگاه")
            self.person_form.setMinimumSize(1000, 700)
            
            # موقعیت فرم نسبت به پنجره اصلی
            main_geometry = self.geometry()
            self.person_form.move(
                main_geometry.x() + 50,
                main_geometry.y() + 50
            )
            
            # اتصال سیگنال‌ها
            self.person_form.form_closed.connect(self.on_person_form_closed)
            self.person_form.person_saved.connect(self.on_person_saved)
            
            # نمایش فرم
            self.person_form.show()
            
        except Exception as e:
            QMessageBox.critical(
                self, 
                "خطا", 
                f"خطا در باز کردن فرم مدیریت اشخاص:\n\n{str(e)}"
            )

    def on_person_form_closed(self):
        """هنگام بسته شدن فرم اشخاص"""
        print("فرم مدیریت اشخاص بسته شد")
        # تازه‌سازی داده‌ها
        self.refresh_dashboard_data()

    def on_person_saved(self, person_data):
        """هنگام ذخیره شخص"""
        print(f"شخص ذخیره شد: {person_data}")
        # می‌توانید اعلان یا عملیات دیگری انجام دهید
    


    def open_devices_management(self):
        """باز کردن فرم مدیریت دستگاه‌ها"""
        if not DEVICE_FORM_AVAILABLE:
            QMessageBox.warning(self, "خطا", "فرم مدیریت دستگاه‌ها در دسترس نیست.")
            return
        
        try:
            self.device_form = DeviceForm(self.data_manager)
            self.device_form.setWindowTitle("📱 مدیریت دستگاه‌ها - سیستم تعمیرگاه")
            self.device_form.setMinimumSize(1000, 700)
            
            main_geometry = self.geometry()
            self.device_form.move(main_geometry.x() + 50, main_geometry.y() + 50)
            
            self.device_form.form_closed.connect(self.on_device_form_closed)
            self.device_form.device_saved.connect(self.on_device_saved)
            
            self.device_form.show()
            
        except Exception as e:
            QMessageBox.critical(self, "خطا", f"خطا در باز کردن فرم دستگاه‌ها:\n\n{str(e)}")
    
    def on_device_form_closed(self):
        """هنگام بسته شدن فرم دستگاه‌ها"""
        print("فرم دستگاه‌ها بسته شد")
        self.refresh_dashboard_data()

    def on_device_saved(self, device_data):
        """هنگام ذخیره دستگاه"""
        print(f"دستگاه ذخیره شد: {device_data.get('brand', '')} {device_data.get('model', '')}")
        QMessageBox.information(self, "ذخیره موفق", "دستگاه با موفقیت ذخیره شد.")


    def open_inventory_management(self):
        """باز کردن فرم مدیریت انبار (فرم اصلی با ۴ تب)"""
        try:
            # import داخل تابع برای جلوگیری از import circular
            from ui.forms.inventory.inventory_main_form import InventoryMainForm
            
            # ایجاد فرم مدیریت انبار
            self.inventory_form = InventoryMainForm(self.data_manager)
            self.inventory_form.setWindowTitle("مدیریت انبار")
            self.inventory_form.show()
            
            # مرکزیت فرم نسبت به پنجره اصلی
            self.center_window(self.inventory_form)
            
        except Exception as e:
            print(f"خطا در باز کردن فرم مدیریت انبار: {e}")
            QMessageBox.critical(self, "خطا", f"خطا در باز کردن فرم مدیریت انبار:\n{str(e)}")

    def open_parts_management(self):
        """مدیریت قطعات"""
        QMessageBox.information(self, "مدیریت قطعات", "مدیریت قطعات باز خواهد شد.")
    

    def open_reception_management(self):
        """باز کردن فرم مدیریت پذیرش"""
        if not RECEPTION_FORM_AVAILABLE:
            QMessageBox.warning(self, "خطا", "فرم مدیریت پذیرش در دسترس نیست.")
            return
        
        try:
            # ایجاد فرم مدیریت پذیرش
            self.reception_form = ReceptionForm(self.data_manager)
            self.reception_form.setWindowTitle("📝 مدیریت پذیرش - سیستم تعمیرگاه")
            self.reception_form.setMinimumSize(1200, 700)
            
            # موقعیت فرم نسبت به پنجره اصلی
            main_geometry = self.geometry()
            self.reception_form.move(
                main_geometry.x() + 50,
                main_geometry.y() + 50
            )
            
            # اتصال سیگنال‌ها
            self.reception_form.form_closed.connect(self.on_reception_form_closed)
            self.reception_form.reception_saved.connect(self.on_reception_saved)
            
            # نمایش فرم
            self.reception_form.show()
            
        except Exception as e:
            QMessageBox.critical(
                self, 
                "خطا", 
                f"خطا در باز کردن فرم پذیرش:\n\n{str(e)}"
            )

    def on_reception_form_closed(self):
        """هنگام بسته شدن فرم پذیرش"""
        print("فرم پذیرش بسته شد")
        # تازه‌سازی داشبورد
        self.refresh_dashboard_data()
    
    def on_reception_saved(self, reception_data):
        """هنگام ذخیره پذیرش"""
        reception_number = reception_data.get('reception_number', 'نامشخص')
        print(f"✅ پذیرش ذخیره شد: {reception_number}")
        
        # نمایش پیام موفقیت
        QMessageBox.information(
            self, 
            "ذخیره موفق", 
            f"پذیرش شماره {reception_number} با موفقیت ذخیره شد."
        )
        
        # تازه‌سازی داشبورد
        self.refresh_dashboard_data()   


    def open_users_management(self):
        """مدیریت کاربران"""
        QMessageBox.information(self, "مدیریت کاربران", "مدیریت کاربران باز خواهد شد.")
    

    def show_current_repairs(self):
        """نمایش تعمیرات در حال انجام"""
        try:
            # دریافت تعمیرات در حال انجام
            query = """
            SELECT r.*, 
                   rc.reception_number, rc.reception_date,
                   p.first_name || ' ' || p.last_name as customer_name,
                   d.device_type, d.brand, d.model
            FROM Repairs r
            JOIN Receptions rc ON r.reception_id = rc.id
            JOIN Persons p ON rc.customer_id = p.id
            JOIN Devices d ON rc.device_id = d.id
            WHERE r.status IN ('شروع شده', 'در حال انجام')
            ORDER BY r.start_time DESC
            """
            
            current_repairs = self.data_manager.db.fetch_all(query)
            
            if not current_repairs:
                QMessageBox.information(self, "تعمیرات جاری", 
                    "⏳ در حال حاضر هیچ تعمیر در حال انجامی وجود ندارد.")
                return
            
            # ایجاد ویجت لیست
            dialog = QDialog(self)
            dialog.setWindowTitle("⚡ تعمیرات در حال انجام")
            dialog.resize(800, 600)
            
            layout = QVBoxLayout()
            
            # جدول تعمیرات
            table = QTableWidget()
            table.setColumnCount(7)
            table.setHorizontalHeaderLabels([
                "شماره پذیرش", "مشتری", "دستگاه", "شروع تعمیر", 
                "تعمیرکار", "وضعیت", "عملیات"
            ])
            
            table.setRowCount(len(current_repairs))
            
            for row, repair in enumerate(current_repairs):
                table.setItem(row, 0, QTableWidgetItem(str(repair['reception_number'])))
                table.setItem(row, 1, QTableWidgetItem(repair['customer_name']))
                table.setItem(row, 2, QTableWidgetItem(f"{repair['device_type']} {repair['brand']}"))
                
                # تاریخ شروع
                start_time = repair.get('start_time', '')
                if start_time:
                    table.setItem(row, 3, QTableWidgetItem(str(start_time)))
                else:
                    table.setItem(row, 3, QTableWidgetItem("ثبت نشده"))
                
                # تعمیرکار
                if repair.get('technician_id'):
                    technician = self.data_manager.person.get_person_by_id(repair['technician_id'])
                    if technician:
                        tech_name = technician.get('full_name', 'نامشخص')
                        table.setItem(row, 4, QTableWidgetItem(tech_name))
                    else:
                        table.setItem(row, 4, QTableWidgetItem("نامشخص"))
                else:
                    table.setItem(row, 4, QTableWidgetItem("تعیین نشده"))
                
                # وضعیت
                status_item = QTableWidgetItem(repair['status'])
                if repair['status'] == 'در حال انجام':
                    status_item.setForeground(QColor('#f39c12'))
                elif repair['status'] == 'شروع شده':
                    status_item.setForeground(QColor('#3498db'))
                table.setItem(row, 5, status_item)
                
                # دکمه مشاهده جزئیات
                btn_details = QPushButton("📋 جزئیات")
                btn_details.clicked.connect(lambda checked, r=repair['id']: self.open_repair_details(r))
                table.setCellWidget(row, 6, btn_details)
            
            table.resizeColumnsToContents()
            layout.addWidget(table)
            
            # دکمه‌های پایین
            btn_close = QPushButton("بستن")
            btn_close.clicked.connect(dialog.accept)
            
            btn_layout = QHBoxLayout()
            btn_layout.addStretch()
            btn_layout.addWidget(btn_close)
            layout.addLayout(btn_layout)
            
            dialog.setLayout(layout)
            dialog.exec()
            
        except Exception as e:
            QMessageBox.warning(self, "خطا", f"خطا در نمایش تعمیرات جاری: {e}")
    
    def open_repair_details(self, repair_id):
        """باز کردن جزئیات یک تعمیر خاص"""
        self.open_repairs_management(repair_id)
    
    def manage_service_fees(self):
        """مدیریت اجرت‌های استاندارد"""
        if not SERVICE_FEE_FORM_AVAILABLE:
            QMessageBox.warning(self, "خطا", "فرم مدیریت اجرت‌ها در دسترس نیست.")
            return
        
        try:
            from ui.forms.service_fee_form import ServiceFeeForm
            self.service_fee_form = ServiceFeeForm(self.data_manager)
            self.service_fee_form.setWindowTitle("💰 مدیریت اجرت‌های استاندارد")
            self.service_fee_form.setMinimumSize(800, 600)
            
            main_geometry = self.geometry()
            self.service_fee_form.move(main_geometry.x() + 100, main_geometry.y() + 100)
            
            self.service_fee_form.show()
            
        except Exception as e:
            QMessageBox.critical(self, "خطا", f"خطا در باز کردن فرم اجرت‌ها: {e}")
    
    def on_repair_form_closed(self):
        """هنگام بسته شدن فرم تعمیرات"""
        print("فرم تعمیرات بسته شد")
        self.refresh_dashboard_data()


#کلا مربوط به ستینگ و تب ها

    def setup_current_user(self, username):
        """تنظیم کاربر جاری و دسترسی‌ها"""
        try:
            # دریافت اطلاعات کاربر از دیتابیس
            query = """
            SELECT u.id, u.username, u.role, p.first_name, p.last_name
            FROM Users u
            LEFT JOIN Persons p ON u.person_id = p.id
            WHERE u.username = ? AND u.is_active = 1
            """
            
            user_data = self.data_manager.db.fetch_one(query, (username,))
            
            if user_data:
                self.current_user = user_data
                self.current_username = username
                self.current_user_role = user_data.get('role', 'اپراتور')
                self.current_user_id = user_data.get('id', 1)
                
                # تنظیم PermissionManager
                self.permission_manager.set_current_user(
                    self.current_user_id,
                    username,
                    self.current_user_role
                )
                
                print(f"👤 کاربر وارد شده: {username}")
                print(f"   نقش: {self.current_user_role}")
                print(f"   دسترسی‌ها: {self.permission_manager.get_all_permissions()}")
                
            else:
                # حالت پیش‌فرض برای توسعه
                self.current_user_role = 'مدیر'
                self.current_user_id = 1
                self.permission_manager.set_current_user(1, username, 'مدیر')
                
        except Exception as e:
            print(f"⚠️ خطا در تنظیم کاربر: {e}")
            self.current_user_role = 'مدیر'
            self.permission_manager.set_current_user(1, username, 'مدیر')

    def repair_config_manager(self):
        """ترمیم config_manager در صورت خرابی"""
        try:
            from modules.config_manager import ConfigManager
            
            print(f"🔍 بررسی config_manager: نوع فعلی = {type(self.config_manager)}")
            
            # 🔴 ابتدا import کن تا از circular import جلوگیری شود
            from ui.main_window import MainWindow
            
            # 🔴 بررسی وجود config_manager
            if not hasattr(self, 'config_manager') or self.config_manager is None:
                print("🔧 ایجاد config_manager جدید")
                self.config_manager = ConfigManager(self.data_manager)
                return True
            
            # 🔴 بررسی نوع - با احتیاط
            current_type = type(self.config_manager).__name__
            print(f"   نوع فعلی: {current_type}")
            
            # اگر config_manager خود MainWindow است
            if current_type == 'MainWindow' or self.config_manager is self:
                print("⚠️ config_manager به اشتباه به MainWindow اشاره می‌کند. در حال ترمیم...")
                self.config_manager = ConfigManager(self.data_manager)
                print(f"✅ config_manager ترمیم شد. نوع جدید: {type(self.config_manager)}")
                return True
            
            # 🔴 بررسی وجود متدهای ضروری
            required_methods = ['get', 'set', 'apply_display_settings']
            for method in required_methods:
                if not hasattr(self.config_manager, method):
                    print(f"⚠️ config_manager متد {method} ندارد. در حال ترمیم...")
                    self.config_manager = ConfigManager(self.data_manager)
                    return True
            
            print(f"✅ config_manager سالم است: {type(self.config_manager)}")
            return False
            
        except Exception as e:
            print(f"⚠️ خطا در ترمیم config_manager: {e}")
            # در صورت خطا، ایجاد جدید
            from modules.config_manager import ConfigManager
            self.config_manager = ConfigManager(self.data_manager)
            return True

    def apply_initial_settings(self):
        """اعمال تنظیمات اولیه روی پنجره اصلی"""
        try:
            # 🔴 بررسی مجدد config_manager قبل از استفاده
            self.repair_config_manager()
            
            # 🔴 بررسی وجود متد get
            if not hasattr(self.config_manager, 'get'):
                print("❌ config_manager متد get ندارد. در حال ترمیم...")
                from modules.config_manager import ConfigManager
                self.config_manager = ConfigManager(self.data_manager)
            
            # اعمال تم
            theme = self.config_manager.get('general', 'theme', 'dark')
            print(f"🎨 اعمال تم: {theme}")
            
            # 🔴 ابتدا استایل تاریک را اعمال کن
            self.setStyleSheet(self.get_style_sheet())
            
            # 🔴 سپس تنظیمات نمایش را اعمال کن (اگر خواستید)
            # try:
            #     if hasattr(self.config_manager, 'apply_display_settings'):
            #         self.config_manager.apply_display_settings(self)
            # except Exception as e:
            #     print(f"⚠️ خطا در اعمال تنظیمات نمایش: {e}")
            
            # به‌روزرسانی عنوان پنجره
            app_name = self.config_manager.get('general', 'app_name', 'سیستم مدیریت تعمیرگاه')
            self.setWindowTitle(f"{app_name} - {self.current_username}")
            
            print("✅ تنظیمات اولیه اعمال شد")
            
        except Exception as e:
            print(f"⚠️ خطا در اعمال تنظیمات اولیه: {e}")
            import traceback
            traceback.print_exc()

    def setup_config_signals(self):
        """اتصال سیگنال‌های ConfigManager"""
        self.config_manager.config_updated.connect(self.on_config_updated)
    
    def on_config_updated(self, key_path, changes):
        """وقتی تنظیمات تغییر کرد"""
        print(f"⚙️ تنظیمات به‌روزرسانی شد: {key_path}")
        
        # اعمال تغییرات بر اساس نوع تنظیمات
        if key_path.startswith('general.'):
            self.apply_general_changes(key_path, changes)
        elif key_path.startswith('display.'):
            self.apply_display_changes(key_path, changes)
        elif key_path.startswith('security.'):
            self.apply_security_changes(key_path, changes)
    
    def apply_general_changes(self, key_path, changes):
        """اعمال تغییرات تنظیمات عمومی"""
        if 'app_name' in key_path:
            new_name = changes['new']
            self.setWindowTitle(f"{new_name} - {self.current_username}")
        
        elif 'theme' in key_path:
            self.apply_theme(changes['new'])
    
    def apply_display_changes(self, key_path, changes):
        """اعمال تغییرات تنظیمات نمایش"""
        self.config_manager.apply_display_settings(self)

    def apply_security_changes(self, key_path, changes):
        """اعمال تغییرات تنظیمات امنیتی"""
        # 🔴 ترمیم قبل از استفاده
        self.repair_config_manager()
        
        if 'role_permissions' in key_path:
            # 🔴 دریافت ایمن تنظیمات امنیتی
            try:
                security_config = self.config_manager.get('security')
                if security_config is None:
                    security_config = {}
                
                role_permissions = security_config.get('role_permissions', {})
                print(f"🔒 به‌روزرسانی دسترسی‌های نقش: {list(role_permissions.keys())}")
                
                # به‌روزرسانی منوها
                self.update_menu_permissions()
                
            except Exception as e:
                print(f"⚠️ خطا در اعمال تغییرات امنیتی: {e}")   

    def apply_theme(self, theme_name):
        """اعمال تم"""
        # این تابع از قبل وجود دارد، فقط مطمئن شوید کار می‌کند
        print(f"🎨 اعمال تم: {theme_name}")
    
    def update_menu_permissions(self):
        """به‌روزرسانی منوها بر اساس دسترسی کاربر"""
        # این تابع منوها را بر اساس نقش کاربر به‌روز می‌کند
        pass

    def _get_config_manager(self):
        """دریافت ایمن config_manager"""
        if not hasattr(self, '_config_manager'):
            from modules.config_manager import ConfigManager
            self._config_manager = ConfigManager(self.data_manager)
        return self._config_manager

    def _set_config_manager(self, value):
        """تنظیم ایمن config_manager"""
        self._config_manager = value

    config_manager = property(_get_config_manager, _set_config_manager)

    def test_config_manager(self):
        """تست سریع config_manager"""
        try:
            print("\n🧪 تست ConfigManager:")
            
            # تست 1: بررسی وجود
            if not hasattr(self, 'config_manager'):
                print("❌ config_manager وجود ندارد")
                return False
            
            # تست 2: بررسی نوع
            from modules.config_manager import ConfigManager
            if not isinstance(self.config_manager, ConfigManager):
                print(f"❌ نوع نادرست: {type(self.config_manager)}")
                return False
            
            # تست 3: تست متد get
            value = self.config_manager.get('general', 'app_name', 'پیش‌فرض')
            print(f"✅ تست get: {value}")
            
            # تست 4: تست متد set
            success = self.config_manager.set('test', 'key', 'value', save_to_db=False)
            print(f"✅ تست set: {'موفق' if success else 'ناموفق'}")
            
            return True
            
        except Exception as e:
            print(f"❌ خطا در تست: {e}")
            import traceback
            traceback.print_exc()
            return False

    def set_current_tab(self, tab_index):
        """تغییر تب فعلی (برای استفاده از بیرون)"""
        if hasattr(self, 'tab_widget'):
            self.tab_widget.setCurrentIndex(tab_index)

    def check_settings_in_database(self):
        """بررسی تنظیمات ذخیره شده در دیتابیس"""
        try:
            # ۱. بررسی تنظیمات عمومی
            query = "SELECT * FROM Settings WHERE id = 1"
            settings = self.data_manager.db.fetch_one(query)
            print("📊 تنظیمات در جدول Settings:")
            if settings:
                for key, value in settings.items():
                    print(f"   {key}: {value}")
            else:
                print("   ⚠️ هیچ تنظیماتی یافت نشد!")
            
            # ۲. بررسی تنظیمات امنیتی
            query = "SELECT * FROM SecuritySettings WHERE id = 1"
            security_settings = self.data_manager.db.fetch_one(query)
            print("🔐 تنظیمات امنیتی:")
            if security_settings:
                for key, value in security_settings.items():
                    print(f"   {key}: {value}")
            
            # ۳. بررسی cache ConfigManager
            print("💾 تنظیمات در ConfigManager Cache:")
            for category, configs in self.config_manager.config_cache.items():
                print(f"   دسته '{category}':")
                for key, value in configs.items():
                    print(f"     {key}: {value}")
                    
        except Exception as e:
            print(f"⚠️ خطا در بررسی تنظیمات: {e}")

    def apply_display_settings(self):
        """اعمال تنظیمات نمایش به صورت پویا"""
        try:
            if not self.config_manager:
                return
            
            # دریافت تنظیمات از config_manager
            font_family = self.config_manager.get('display', 'font_family', 'B Nazanin')
            font_size = self.config_manager.get('display', 'font_size', 11)
            text_color = self.config_manager.get('display', 'text_color', '#FFFFFF')
            bg_color = self.config_manager.get('display', 'bg_color', '#000000')
            
            # تولید استایل پویا
            style = f"""
            /* استایل کلی - راست‌چین */
            QMainWindow {{
                background-color: {bg_color};
                color: {text_color};
            }}
            
            QWidget {{
                font-family: '{font_family}';
                font-size: {font_size}pt;
                background-color: {bg_color};
                color: {text_color};
            }}
            
            /* سایر استایل‌ها ... */
            QMenuBar {{
                background-color: #111111;
                color: {text_color};
                font-size: 13px;
                padding: 5px;
                border-bottom: 1px solid #333;
            }}
            
            QMenu {{
                background-color: #111111;
                border: 1px solid #333;
                border-radius: 5px;
                color: {text_color};
            }}
            
            QMenu::item {{
                padding: 8px 25px 8px 20px;
                color: {text_color};
                text-align: right;
            }}
            
            QMenu::item:selected {{
                background-color: #3498db;
                color: white;
            }}
            
            QPushButton {{
                padding: 8px 15px;
                border-radius: 4px;
                font-weight: bold;
                border: none;
                color: {text_color};
                background-color: #2c3e50;
            }}
            
            QPushButton:hover {{
                background-color: #34495e;
            }}
            
            QLineEdit, QComboBox, QSpinBox, QTextEdit {{
                background-color: #222222;
                color: {text_color};
                border: 1px solid #444444;
                border-radius: 4px;
                padding: 8px;
            }}
            
            QTableWidget {{
                background-color: #111111;
                alternate-background-color: #2c2c2c;
                color: {text_color};
                gridline-color: #333;
            }}
            
            QHeaderView::section {{
                background-color: #2c3e50;
                color: {text_color};
                padding: 8px;
                border: none;
                font-weight: bold;
            }}
            
            QTabBar::tab {{
                background-color: #2c2c2c;
                color: #bbb;
                padding: 8px 15px;
                margin-left: 2px;
                margin-right: 0px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }}
            
            QTabBar::tab:selected {{
                background-color: #3498db;
                color: white;
                font-weight: bold;
            }}
            
            QStatusBar {{
                background-color: #1e1e1e;
                color: {text_color};
                font-size: 12px;
                border-top: 1px solid #333;
            }}
            
            QLabel {{
                color: {text_color};
            }}
            
            QGroupBox {{
                color: #3498db;
                border: 2px solid #3498db;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
                font-weight: bold;
                font-size: 12pt;
            }}
            
            QGroupBox::title {{
                subcontrol-origin: margin;
                padding: 0 10px;
            }}
            """
            
            # اعمال استایل
            self.setStyleSheet(style)
            
            # اعمال بر روی تمام ویجت‌های فرزند
            for widget in self.findChildren(QWidget):
                widget.setStyleSheet("")
            
            print(f"✅ تنظیمات نمایش اعمال شد: {font_family} {font_size}pt")
            
        except Exception as e:
            print(f"⚠️ خطا در اعمال تنظیمات نمایش: {e}")
            # در صورت خطا، استایل تاریک پیش‌فرض را اعمال کن
            self.setStyleSheet(self.get_style_sheet())

    def on_display_settings_changed(self, display_settings):
        """وقتی تنظیمات نمایش تغییر کرد"""
        print("🎨 تنظیمات نمایش تغییر کرد، در حال اعمال...")
        self.apply_display_settings()




#انتهای توابع تنظیمات

    def open_new_parts_inventory(self):
        """انبار قطعات نو"""
        QMessageBox.information(self, "انبار قطعات نو", "انبار قطعات نو باز خواهد شد.")
    
    def open_used_parts_inventory(self):
        """انبار قطعات دست دوم"""
        QMessageBox.information(self, "انبار قطعات دست دوم", "انبار قطعات دست دوم باز خواهد شد.")
    
    def open_new_appliances_inventory(self):
        """انبار لوازم نو"""
        QMessageBox.information(self, "انبار لوازم نو", "انبار لوازم نو باز خواهد شد.")
    
    def open_used_appliances_inventory(self):
        """انبار لوازم دست دوم"""
        QMessageBox.information(self, "انبار لوازم دست دوم", "انبار لوازم دست دوم باز خواهد شد.")
    
    def open_invoices_management(self):
        """مدیریت فاکتورها"""
        QMessageBox.information(self, "مدیریت فاکتورها", "مدیریت فاکتورها باز خواهد شد.")
    
    def open_accounts_management(self):
        """مدیریت حساب‌ها"""
        QMessageBox.information(self, "مدیریت حساب‌ها", "مدیریت حساب‌ها باز خواهد شد.")
    
    def open_checks_management(self):
        """مدیریت چک‌ها"""
        QMessageBox.information(self, "مدیریت چک‌ها", "مدیریت چک‌ها باز خواهد شد.")
    
    def open_partners_management(self):
        """مدیریت شرکا"""
        QMessageBox.information(self, "مدیریت شرکا", "مدیریت شرکا باز خواهد شد.")
      
    def open_repairs_management(self):
        """باز کردن فرم تعمیرات"""
        try:
            # ایمپورت Lazy برای جلوگیری از circular import
            try:
                from ui.forms.repair_form import RepairForm
            except ImportError as import_error:
                print(f"❌ خطای ایمپورت در open_repair_form: {import_error}")
                
                # تلاش برای ایمپورت با مسیر کامل
                import sys
                import os
                
                # افزودن مسیر پروژه به sys.path
                project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                if project_root not in sys.path:
                    sys.path.insert(0, project_root)
                
                # دوباره تلاش کن
                from ui.forms.repair_form import RepairForm
                print("✅ ایمپورت موفق بعد از تنظیم sys.path")
            
            # ایجاد فرم
            self.repair_form = RepairForm(self.data_manager)
            
            # تنظیمات پنجره
            self.repair_form.setWindowModality(Qt.ApplicationModal)
            self.repair_form.show()
            self.repair_form.raise_()
            
            print("✅ فرم تعمیرات با موفقیت باز شد")
            
        except Exception as e:
            QMessageBox.critical(
                self, 
                "خطا در باز کردن فرم تعمیرات",
                f"خطا: {str(e)}\n\n"
                f"لطفاً:\n"
                f"۱. فایل repair_form.py را بررسی کنید\n"
                f"۲. ساختار پوشه‌ها را بررسی کنید\n"
                f"۳. خطاهای کنسول را ببینید"
            )
            print(f"❌ خطای کامل در open_repair_form:")
            import traceback
            traceback.print_exc()



    def open_inventory_main(self):
        """باز کردن پنجره مستقل مدیریت انبار"""
        if not INVENTORY_WINDOW_AVAILABLE or InventoryWindow is None:
            QMessageBox.warning(self, "خطا", "پنجره انبار در دسترس نیست.")
            return
        
        try:
            # اگر پنجره قبلاً باز است، آن را فعال کن
            if hasattr(self, 'inventory_window') and self.inventory_window and self.inventory_window.isVisible():
                self.inventory_window.raise_()
                self.inventory_window.activateWindow()
                return
            
            # ایجاد پنجره جدید انبار
            self.inventory_window = InventoryWindow(self.data_manager, self)
            
            # موقعیت پنجره
            main_geometry = self.geometry()
            self.inventory_window.move(
                main_geometry.x() + 100,
                main_geometry.y() + 100
            )
            
            # نمایش پنجره
            self.inventory_window.show()
            
            print("✅ پنجره انبار با موفقیت باز شد")
            
        except Exception as e:
            QMessageBox.critical(
                self, 
                "خطا", 
                f"خطا در باز کردن پنجره انبار:\n\n{str(e)}"
            )
            import traceback
            traceback.print_exc()


    def open_inventory_tab(self, tab_index):
        """باز کردن تب خاصی از انبار در پنجره مستقل"""
        if not INVENTORY_WINDOW_AVAILABLE:
            QMessageBox.warning(self, "خطا", "پنجره انبار در دسترس نیست.")
            return
        
        try:
            # اگر پنجره باز نیست، ابتدا آن را باز کن
            if not self.inventory_window or not self.inventory_window.isVisible():
                self.open_inventory_main()
                # کمی تأخیر برای بارگذاری فرم
                from PySide6.QtCore import QTimer
                QTimer.singleShot(300, lambda: self.switch_inventory_tab(tab_index))
            else:
                self.switch_inventory_tab(tab_index)
                
        except Exception as e:
            QMessageBox.critical(self, "خطا", f"خطا در تغییر تب انبار: {e}")

    def switch_inventory_tab(self, tab_index):
        """تغییر تب در پنجره انبار"""
        if (self.inventory_window and 
            self.inventory_window.isVisible() and 
            hasattr(self.inventory_window.inventory_form, 'tab_widget')):
            
            self.inventory_window.inventory_form.tab_widget.setCurrentIndex(tab_index)
            self.inventory_window.raise_()
            self.inventory_window.activateWindow()

    def open_inventory_new_parts(self):
        """باز کردن پنجره انبار و نمایش تب قطعات نو"""
        self.open_inventory_tab(0)

    def open_inventory_used_parts(self):
        """باز کردن پنجره انبار و نمایش تب قطعات دست دوم"""
        self.open_inventory_tab(1)

    def open_inventory_new_appliances(self):
        """باز کردن پنجره انبار و نمایش تب لوازم نو"""
        self.open_inventory_tab(2)

    def open_inventory_used_appliances(self):
        """باز کردن پنجره انبار و نمایش تب لوازم دست دوم"""
        self.open_inventory_tab(3)

    def open_inventory_report(self):
        """باز کردن فرم گزارش انبار"""
        try:
            from ui.forms.inventory import InventoryReportForm
            self.report_form = InventoryReportForm(self.data_manager, self)
            self.report_form.show()
        except Exception as e:
            print(f"خطا در باز کردن فرم گزارش: {e}")

    def open_inventory_settings(self):
        """باز کردن فرم تنظیمات انبار"""
        try:
            # import داخل تابع برای جلوگیری از import circular
            from ui.forms.inventory.inventory_settings_form import InventorySettingsForm
            
            # ایجاد فرم تنظیمات انبار
            self.inventory_settings_form = InventorySettingsForm(self.data_manager)
            self.inventory_settings_form.setWindowTitle("تنظیمات انبار")
            self.inventory_settings_form.show()
            
            # مرکزیت فرم نسبت به پنجره اصلی
            self.center_window(self.inventory_settings_form)
            
        except Exception as e:
            print(f"خطا در باز کردن فرم تنظیمات انبار: {e}")
            QMessageBox.critical(self, "خطا", f"خطا در باز کردن فرم تنظیمات انبار:\n{str(e)}")


    def show_message(self, message):
        """نمایش یک پیام ساده"""
        from PySide6.QtWidgets import QMessageBox
        QMessageBox.information(self, "پیام", message)

    # اضافه کردن توابع باز کردن حسابداری
    def open_accounting_dashboard(self):
        """باز کردن داشبورد حسابداری"""
        from ui.forms.accounting.accounting_dashboard import AccountingDashboard
        self.show_form_in_central(AccountingDashboard(self.data_manager), "داشبورد حسابداری")

    def show_form_in_central(self, widget, title):
        """نمایش یک ویجت در قسمت مرکزی پنجره اصلی"""
        try:
            # حذف ویجت قبلی از central widget
            old_widget = self.centralWidget()
            if old_widget:
                old_widget.deleteLater()
            
            # تنظیم ویجت جدید
            widget.setParent(self)
            self.setCentralWidget(widget)
            
            # به روزرسانی عنوان پنجره
            self.setWindowTitle(f"{title} - سیستم مدیریت تعمیرگاه شیروین")
            
            # نمایش ویجت
            widget.show()
            
        except Exception as e:
            print(f"❌ خطا در نمایش فرم: {e}")
            # نمایش پیام خطا
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.critical(self, "خطا", f"خطا در نمایش فرم:\n{str(e)}")


    # ---------- متدهای حسابداری ----------
    
    def open_accounts_form(self):
        """باز کردن تب حساب‌ها در حسابداری"""
        self.open_accounting_window_tab(0)
    
    def open_transactions_form(self):
        """باز کردن تب تراکنش‌ها در حسابداری"""
        self.open_accounting_window_tab(1)
    
    def open_invoices_form(self):
        """باز کردن تب فاکتورها در حسابداری"""
        self.open_accounting_window_tab(2)
    
    def open_checks_form(self):
        """باز کردن تب چک‌ها در حسابداری"""
        self.open_accounting_window_tab(3)
    
    def open_partners_form(self):
        """باز کردن تب شرکا در حسابداری"""
        self.open_accounting_window_tab(4)
    
    def open_profit_calculation(self):
        """باز کردن تب محاسبه سود در حسابداری"""
        self.open_accounting_window_tab(5)
    
    def open_financial_reports(self):
        """باز کردن تب گزارش‌های مالی در حسابداری"""
        self.open_accounting_window_tab(6)
    
    def open_daily_summary(self):
        """باز کردن تب خلاصه روزانه در حسابداری"""
        self.open_accounting_window_tab(7)
    
    def open_accounting_settings(self):
        """باز کردن تنظیمات حسابداری"""
        QMessageBox.information(self, "تنظیمات حسابداری", 
            "تنظیمات حسابداری به زودی اضافه خواهد شد.")
    
    def open_accounting_window_tab(self, tab_index):
        """باز کردن پنجره حسابداری و رفتن به تب مشخص"""
        # ابتدا پنجره حسابداری را باز کن
        self.open_accounting_window()
        
        # کمی تاخیر برای بارگذاری کامل پنجره
        from PySide6.QtCore import QTimer
        QTimer.singleShot(300, lambda: self._switch_accounting_tab(tab_index))
    
    def _switch_accounting_tab(self, tab_index):
        """تغییر تب در پنجره حسابداری (فراخوانی داخلی)"""
        if (hasattr(self, 'accounting_window') and 
            self.accounting_window and 
            self.accounting_window.isVisible()):
            
            # فعال کردن پنجره
            self.accounting_window.raise_()
            self.accounting_window.activateWindow()
            
            # تغییر تب اگر امکان دارد
            if hasattr(self.accounting_window, 'accounting_form'):
                self.accounting_window.accounting_form.set_current_tab(tab_index)
    
    def open_accounting_window(self):
        """باز کردن پنجره مستقل حسابداری"""
        try:
            # ایمپورت درون تابع برای جلوگیری از مشکلات import
            try:
                from ui.forms.accounting.accounting_window import AccountingWindow
            except ImportError as e:
                print(f"⚠️ خطای ایمپورت حسابداری: {e}")
                QMessageBox.warning(self, "خطا", 
                    f"خطا در بارگذاری ماژول حسابداری:\n\n{str(e)}")
                return
            
            # اگر پنجره قبلاً باز است، آن را فعال کن
            if hasattr(self, 'accounting_window') and self.accounting_window:
                try:
                    if self.accounting_window.isVisible():
                        self.accounting_window.raise_()
                        self.accounting_window.activateWindow()
                        return
                    else:
                        # پنجره وجود دارد اما بسته شده، دوباره ایجاد کن
                        self.accounting_window = None
                except:
                    self.accounting_window = None
            
            # ایجاد پنجره جدید حسابداری
            self.accounting_window = AccountingWindow(self.data_manager, self)
            
            # موقعیت پنجره
            main_geometry = self.geometry()
            self.accounting_window.move(
                main_geometry.x() + 100,
                main_geometry.y() + 100
            )
            
            # نمایش پنجره
            self.accounting_window.show()
            
            print("✅ پنجره حسابداری با موفقیت باز شد")
            
        except Exception as e:
            QMessageBox.critical(
                self, 
                "خطا", 
                f"خطا در باز کردن پنجره حسابداری:\n\n{str(e)}"
            )
            import traceback
            traceback.print_exc()




    def show_low_stock(self):
        """نمایش اقلام با موجودی کم"""
        try:
            from ui.forms.inventory.dialogs import LowStockDialog
            self.low_stock_dialog = LowStockDialog(self.data_manager, self)
            self.low_stock_dialog.exec()
        except Exception as e:
            print(f"خطا در نمایش موجودی کم: {e}")


# در کلاس MainWindow، بعد از متد open_accounting_window (حدود خط 1000-1050) اضافه کنید:

    def open_reports_window(self):
        """باز کردن پنجره مستقل گزارش‌گیری"""
        if not REPORTS_WINDOW_AVAILABLE:
            QMessageBox.warning(self, "خطا", 
                "پنجره گزارش‌گیری در دسترس نیست.\n"
                "لطفا مطمئن شوید فایل‌های گزارش‌گیری وجود دارند.")
            return
        
        # اگر پنجره از قبل باز است، آن را جلو بیاور
        if hasattr(self, 'reports_window') and self.reports_window is not None:
            self.reports_window.raise_()
            self.reports_window.activateWindow()
            return
        
        try:
            # ایجاد پنجره جدید
            self.reports_window = ReportsWindow(self.data_manager, self)
            self.reports_window.window_closed.connect(self.on_reports_window_closed)
            self.reports_window.show()
            print("✅ پنجره گزارش‌گیری باز شد")
        except Exception as e:
            QMessageBox.critical(self, "خطا", 
                f"خطا در باز کردن پنجره گزارش‌گیری:\n{str(e)}")
            print(f"❌ خطا در ایجاد پنجره گزارش‌گیری: {e}")

    def on_reports_window_closed(self):
        """رویداد بسته شدن پنجره گزارش‌گیری"""
        self.reports_window = None
        print("✅ پنجره گزارش‌گیری بسته شد")
        
    def open_reports_tab(self, tab_index):
        """باز کردن پنجره گزارش‌گیری با تب مشخص شده"""
        self.open_reports_window()  # اول پنجره را باز کن
        
        # صبر کن تا پنجره بارگذاری شود، سپس تب مورد نظر را انتخاب کن
        if hasattr(self, 'reports_window') and self.reports_window is not None:
            # استفاده از تایمر برای اطمینان از بارگذاری کامل
            from PySide6.QtCore import QTimer
            QTimer.singleShot(200, lambda: self.reports_window.reports_form.show_tab(tab_index))
            
    def quick_daily_report(self):
        """گزارش سریع خلاصه روز"""
        try:
            # ایجاد یک دیالوگ ساده
            from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton
            from PySide6.QtCore import Qt
            
            dialog = QDialog(self)
            dialog.setWindowTitle("📅 گزارش روزانه - سریع")
            dialog.resize(500, 300)
            
            layout = QVBoxLayout(dialog)
            
            title = QLabel("📊 خلاصه فعالیت‌های امروز")
            title.setAlignment(Qt.AlignCenter)
            title.setStyleSheet("font-size: 16pt; font-weight: bold; color: #3498db;")
            layout.addWidget(title)
            
            # آمار ساده
            stats = """
            📅 تاریخ: امروز
            
            📋 آمار سریع:
            • پذیرش جدید: ۱۵
            • تعمیرات تکمیل شده: ۱۰
            • فاکتورهای صادر شده: ۸
            • دریافتی نقدی: ۲,۵۰۰,۰۰۰ تومان
            • مشتریان جدید: ۵
            • قطعات مصرف شده: ۲۳
            
            ⚠️ هشدارها:
            • ۲ دستگاه در انتظار تعمیر
            • موجودی کم: کمپرسور یخچال
            
            ✅ پیشنهاد:
            • موجودی کمپرسور را تکمیل کنید
            """
            
            stats_label = QLabel(stats)
            stats_label.setStyleSheet("font-size: 11pt; padding: 15px;")
            layout.addWidget(stats_label)
            
            btn_close = QPushButton("بستن")
            btn_close.clicked.connect(dialog.close)
            layout.addWidget(btn_close)
            
            dialog.exec()
            
        except Exception as e:
            QMessageBox.information(self, "گزارش روزانه", 
                "📅 گزارش روزانه\n\n"
                "برای گزارش کامل از پنجره مستقل گزارش‌گیری استفاده کنید.")

    def quick_financial_report(self):
        """گزارش سریع وضعیت مالی"""
        QMessageBox.information(self, "گزارش مالی", 
            "💰 گزارش مالی\n\n"
            "این قابلیت به زودی تکمیل خواهد شد.\n"
            "برای گزارش کامل از پنجره مستقل گزارش‌گیری استفاده کنید.")
        
    def quick_inventory_report(self):
        """گزارش سریع وضعیت انبار"""
        QMessageBox.information(self, "گزارش انبار", 
            "📦 گزارش انبار\n\n"
            "این قابلیت به زودی تکمیل خواهد شد.\n"
            "برای گزارش کامل از پنجره مستقل گزارش‌گیری استفاده کنید.")

    def show_inventory_report(self):
        """نمایش گزارش انبار"""
        try:
            from ui.forms.reports.forms.inventory_report_form import InventoryReportForm
            
            # ایجاد ویجت گزارش انبار
            inventory_widget = QWidget()
            layout = QVBoxLayout(inventory_widget)
            
            # افزودن گزارش انبار
            inventory_form = InventoryReportForm(self.data_manager)
            layout.addWidget(inventory_form)
            
            # نمایش در تب جدید
            self.add_tab(inventory_widget, "📦 گزارش انبار")
            
        except Exception as e:
            print(f"❌ خطا در نمایش گزارش انبار: {e}")
            QMessageBox.warning(self, "خطا", f"خطا در بارگذاری گزارش انبار: {str(e)}")




    def open_financial_dashboard(self):
        """داشبورد مالی"""
        QMessageBox.information(self, "داشبورد مالی", "داشبورد مالی باز خواهد شد.")
    
    def open_reports_dashboard(self):
        """داشبورد گزارشات"""
        QMessageBox.information(self, "داشبورد گزارشات", "داشبورد گزارشات باز خواهد شد.")
    
    def open_daily_report(self):
        """گزارش روزانه"""
        QMessageBox.information(self, "گزارش روزانه", "گزارش روزانه باز خواهد شد.")
    
    def open_monthly_report(self):
        """گزارش ماهانه"""
        QMessageBox.information(self, "گزارش ماهانه", "گزارش ماهانه باز خواهد شد.")
    
    def open_financial_report(self):
        """گزارش مالی"""
        QMessageBox.information(self, "گزارش مالی", "گزارش مالی باز خواهد شد.")
    
    def open_settings_window(self, initial_tab="general"):
        """باز کردن پنجره تنظیمات"""
        try:
            from ui.forms.settings.settings_window import SettingsWindow
            
            if not hasattr(self, 'settings_window') or self.settings_window is None:
                # 🔴 ارسال config_manager به جای self
                self.settings_window = SettingsWindow(
                    self.data_manager, 
                    self.config_manager,  # ✅ این مهم است
                    self  # parent
                )
            
            self.settings_window.show()
            self.settings_window.raise_()
            self.settings_window.activateWindow()
            
            # انتخاب تب اولیه
            if initial_tab == "users":
                self.settings_window.main_form.tab_widget.setCurrentIndex(2)  # تب کاربران
            elif initial_tab == "backup":
                self.settings_window.main_form.tab_widget.setCurrentIndex(3)  # تب پشتیبان
            elif initial_tab == "sms":
                self.settings_window.main_form.tab_widget.setCurrentIndex(4)  # تب پیامک
            elif initial_tab == "inventory":
                self.settings_window.main_form.tab_widget.setCurrentIndex(5)  # تب انبار
            elif initial_tab == "security":
                self.settings_window.main_form.tab_widget.setCurrentIndex(6)  # تب امنیت
            else:
                self.settings_window.main_form.tab_widget.setCurrentIndex(0)  # تب عمومی
                
        except ImportError as e:
            QMessageBox.critical(self, "خطا", f"پنجره تنظیمات در دسترس نیست:\n{str(e)}")
        except Exception as e:
            QMessageBox.critical(self, "خطا", f"خطا در باز کردن پنجره تنظیمات:\n{str(e)}")

    def debug_config_manager(self):
        """دیباگ وضعیت config_manager"""
        print(f"\n🔍 دیباگ config_manager:")
        print(f"   موجود است: {hasattr(self, 'config_manager')}")
        if hasattr(self, 'config_manager'):
            print(f"   نوع: {type(self.config_manager)}")
            print(f"   id: {id(self.config_manager)}")
            
            # بررسی متدهای اصلی
            methods = ['get', 'set', 'apply_display_settings']
            for method in methods:
                has_method = hasattr(self.config_manager, method)
                print(f"   متد {method}: {'✅' if has_method else '❌'}")
        
        return self.config_manager


    # در main_window.py
    def setup_sms_module(self):
        """راه‌اندازی ماژول پیامکی"""
        try:
            from modules.sms_manager import SMSManager
            from services.sms_service import SMSService
            
            # ایجاد مدیر پیامک
            api_key = self.get_setting('sms_api_key', '')  # از تنظیمات بخوان
            self.sms_manager = SMSManager(self.data_manager, api_key=api_key)
            
            # ایجاد سرویس خودکار
            self.sms_service = SMSService(self.sms_manager, self.data_manager)
            
            # شروع سرویس
            if self.get_setting('auto_sms_enabled', False):
                self.sms_service.start()
                
        except ImportError as e:
            print(f"خطا در بارگذاری ماژول پیامکی: {e}")
            self.sms_manager = None
            self.sms_service = None

    def open_sms_composer(self):
        """باز کردن فرم ارسال پیامک"""
        if not self.sms_manager:
            QMessageBox.warning(self, "خطا", "ماژول پیامکی راه‌اندازی نشده است.")
            return
        
        try:
            from ui.forms.sms.sms_composer import SMSComposerForm
            self.sms_composer = SMSComposerForm(self.sms_manager, self)
            self.sms_composer.show()
        except Exception as e:
            QMessageBox.critical(self, "خطا", f"خطا در باز کردن فرم پیامک: {str(e)}")

    def open_inventory_report(self):
        """گزارش انبار"""
        QMessageBox.information(self, "گزارش انبار", "گزارش انبار باز خواهد شد.")
    
    def open_app_settings(self):
        """تنظیمات برنامه"""
        QMessageBox.information(self, "تنظیمات برنامه", "تنظیمات برنامه باز خواهد شد.")
    
    def open_sms_settings(self):
        """تنظیمات پیامکی"""
        QMessageBox.information(self, "تنظیمات پیامکی", "تنظیمات پیامکی باز خواهد شد.")
    
    def backup_database(self):
        """پشتیبان‌گیری از دیتابیس"""
        try:
            backup_path = self.data_manager.db.backup_database()
            if backup_path:
                QMessageBox.information(self, "پشتیبان‌گیری", 
                    f"پشتیبان‌گیری با موفقیت انجام شد.\nمسیر: {backup_path}")
            else:
                QMessageBox.warning(self, "خطا", "خطا در پشتیبان‌گیری")
        except Exception as e:
            QMessageBox.critical(self, "خطا", f"خطا در پشتیبان‌گیری: {str(e)}")
    
    def show_about(self):
        """نمایش اطلاعات برنامه"""
        about_text = """
        <h2>سیستم مدیریت تعمیرگاه لوازم خانگی شیروین</h2>
        <p><b>ورژن:</b> ۱.۰.۰</p>
        <p><b>تاریخ انتشار:</b> ۱۴۰۴/۱۰/۰۵</p>
        <p><b>توسعه‌دهنده:</b> تیم فنی تعمیرگاه شیروین</p>
        <p><b>امکانات:</b></p>
        <ul>
            <li>مدیریت کامل پذیرش و تعمیرات</li>
            <li>مدیریت ۴ نوع انبار</li>
            <li>سیستم حسابداری پیشرفته</li>
            <li>مدیریت شرکا و محاسبه سود</li>
            <li>گزارش‌گیری حرفه‌ای</li>
            <li>پشتیبانی از تاریخ شمسی</li>
        </ul>
        <p>© ۱۴۰۴ - کلیه حقوق محفوظ است.</p>
        """
        
        QMessageBox.about(self, "درباره برنامه", about_text)
    
    def show_help(self):
        """نمایش راهنمای برنامه"""
        help_text = """
        <h2>راهنمای استفاده از برنامه</h2>
        
        <h3>منوهای اصلی:</h3>
        <ul>
            <li><b>فایل:</b> عملیات سیستمی مانند پشتیبان‌گیری و خروج</li>
            <li><b>مدیریت:</b> مدیریت اشخاص، دستگاه‌ها، قطعات و کاربران</li>
            <li><b>انبار:</b> مدیریت ۴ نوع انبار مختلف</li>
            <li><b>مالی:</b> فاکتورها، حساب‌ها، چک‌ها و شرکا</li>
            <li><b>گزارشات:</b> انواع گزارش‌های تحلیلی</li>
            <li><b>تنظیمات:</b> تنظیمات برنامه و پیامکی</li>
        </ul>
        
        <h3>داشبورد:</h3>
        <p>اطلاعات مهم و آماری را در لحظه نمایش می‌دهد.</p>
        
        <h3>پنل کناری:</h3>
        <p>دسترسی سریع به عملکردهای پرکاربرد.</p>
        
        <h3>برای شروع:</h3>
        <ol>
            <li>از منوی مدیریت، ابتدا مشتریان و دستگاه‌ها را ثبت کنید</li>
            <li>از پنل کناری "پذیرش جدید" را انتخاب کنید</li>
            <li>عملیات تعمیر را ثبت و پیگیری کنید</li>
            <li>در پایان، فاکتور صادر کنید</li>
        </ol>
        """
        
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("راهنمای برنامه")
        msg_box.setText(help_text)
        msg_box.exec()
    
    def closeEvent(self, event):
        """مدیریت بسته شدن پنجره"""
        reply = QMessageBox.question(
            self, "خروج از برنامه",
            "آیا مطمئن هستید که می‌خواهید خارج شوید؟",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # ذخیره تنظیمات و انجام عملیات پایانی
            self.timer.stop()
            self.data_timer.stop()
            event.accept()
        else:
            event.ignore()



    def showEvent(self, event):
        """رویداد نمایش پنجره"""
        super().showEvent(event)
        
        # کمی تأخیر و سپس بررسی اسکرول
        QTimer.singleShot(500, self.ensure_scroll_visible)

    def ensure_scroll_visible(self):
        """اطمینان از نمایش اسکرول"""
        try:
            # پیدا کردن ویجت اسکرول
            scroll_area = self.findChild(QScrollArea)
            if scroll_area:
                # فعال کردن اسکرول
                scroll_area.verticalScrollBar().setValue(10)
                scroll_area.verticalScrollBar().setValue(0)
                print("✅ اسکرول فعال شد")
        except:
            pass




