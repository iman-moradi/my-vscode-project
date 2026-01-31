# ui/main_window.py - پنجره اصلی برنامه
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QTabWidget, QTableWidget, QTableWidgetItem,
    QToolBar, QStatusBar, QMenuBar, QMenu, QFrame, QSplitter,
    QTreeWidget, QTreeWidgetItem, QDockWidget, QMessageBox,
    QApplication, QStyleFactory, QListWidget, QListWidgetItem,QDialog
)
from PySide6.QtCore import Qt, QTimer, QDate, QSize
from PySide6.QtGui import QIcon, QAction, QFont, QPixmap, QColor
import jdatetime
from datetime import datetime, timedelta


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

    

def convert_to_jalali_display(date_str):
    """تبدیل رشته تاریخ میلادی به شمسی برای نمایش"""
    if not date_str:
        return ""
    
    try:
        # فرمت‌های مختلف تاریخ
        date_formats = ['%Y-%m-%d', '%Y/%m/%d', '%d-%m-%Y', '%d/%m/%Y']
        
        miladi_date = None
        for fmt in date_formats:
            try:
                miladi_date = datetime.strptime(date_str, fmt).date()
                break
            except:
                continue
        
        if miladi_date:
            jalali_date = jdatetime.date.fromgregorian(date=miladi_date)
            return jalali_date.strftime('%Y/%m/%d')
        else:
            return date_str  # اگر تبدیل نشد، تاریخ اصلی را برگردان
            
    except Exception as e:
        print(f"⚠️ خطا در تبدیل تاریخ {date_str}: {e}")
        return date_str





class MainWindow(QMainWindow):
    """پنجره اصلی برنامه"""
    
    def __init__(self, user_data, data_manager):
        super().__init__()
        self.user_data = user_data
        self.data_manager = data_manager
        self.inventory_window = None
        self.accounting_windows = {}
        self.init_ui()
        self.setup_connections()
        self.load_initial_data()
        
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


    def init_ui(self):
        """راه‌اندازی رابط کاربری"""
        self.setWindowTitle("سیستم مدیریت تعمیرگاه لوازم خانگی شیروین")
        self.setGeometry(100, 50, 1400, 800)
        
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
        self.create_central_widget()
        self.create_side_panel()
        
        # نمایش اطلاعات کاربر
        self.show_user_info()
        
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
        
        app_settings_action = QAction("🎛️ تنظیمات برنامه", self)
        app_settings_action.triggered.connect(self.open_app_settings)
        settings_menu.addAction(app_settings_action)
        
        sms_settings_action = QAction("📱 تنظیمات پیامکی", self)
        sms_settings_action.triggered.connect(self.open_sms_settings)
        settings_menu.addAction(sms_settings_action)
        
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
        """به‌روزرسانی تاریخ و زمان"""
        now = jdatetime.datetime.now()
        self.date_label.setText(f"📅 {now.strftime('%Y/%m/%d - %A')}")
        self.time_label.setText(f"🕒 {now.strftime('%H:%M:%S')}")
    
    def create_central_widget(self):
        """ایجاد ویجت مرکزی با تم تاریک"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)
        
        # داشبورد اصلی
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
        dashboard_title = QLabel("📊 داشبورد مدیریت")
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
        
        # جدول پذیرش‌های اخیر
        recent_receptions_label = QLabel("📋 آخرین پذیرش‌ها")
        recent_receptions_label.setStyleSheet("""
            QLabel {
                font-size: 16px;
                font-weight: bold;
                color: white;
                margin-top: 15px;
            }
        """)
        dashboard_layout.addWidget(recent_receptions_label)
        
        self.receptions_table = QTableWidget()
        self.receptions_table.setColumnCount(7)
        self.receptions_table.setHorizontalHeaderLabels([
            "شماره پذیرش", "مشتری", "دستگاه", "تاریخ", "هزینه تخمینی", 
            "اولویت", "وضعیت"
        ])
        self.receptions_table.horizontalHeader().setStretchLastSection(True)
        dashboard_layout.addWidget(self.receptions_table)
        
        # جدول چک‌های در سررسید
        due_checks_label = QLabel("💳 چک‌های در سررسید (۷ روز آینده)")
        due_checks_label.setStyleSheet("""
            QLabel {
                font-size: 16px;
                font-weight: bold;
                color: white;
                margin-top: 15px;
            }
        """)
        dashboard_layout.addWidget(due_checks_label)
        
        self.checks_table = QTableWidget()
        self.checks_table.setColumnCount(6)
        self.checks_table.setHorizontalHeaderLabels([
            "شماره چک", "بانک", "مبلغ", "تاریخ سررسید", "صادرکننده", "وضعیت"
        ])
        self.checks_table.horizontalHeader().setStretchLastSection(True)
        dashboard_layout.addWidget(self.checks_table)
        
        dashboard_frame.setLayout(dashboard_layout)
        main_layout.addWidget(dashboard_frame)
        
        central_widget.setLayout(main_layout)
    
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
    
    def refresh_dashboard_data(self):
        """به‌روزرسانی داده‌های داشبورد با اطلاعات واقعی"""
        try:
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
            
            # 🔴 **به‌روزرسانی مستقیم ویجت‌های آماری**
            # پیدا کردن و به‌روزرسانی جعبه‌های آمار
            stats_frame = self.findChild(QFrame)  # اولین QFrame
            if stats_frame:
                # پیدا کردن تمام جعبه‌های آماری
                stat_boxes = stats_frame.findChildren(QFrame)
                if stat_boxes and len(stat_boxes) >= 4:
                    # به‌روزرسانی مقادیر
                    self.update_stat_box(stat_boxes[0], str(today_count))
                    self.update_stat_box(stat_boxes[1], str(repairing_count))
                    self.update_stat_box(stat_boxes[2], str(low_stock_count))
                    self.update_stat_box(stat_boxes[3], str(due_checks_count))
            
            # 🔴 **آمار سیستم در پنل کناری**
            self.update_system_status()
            
            # بارگذاری پذیرش‌های اخیر
            recent_receptions = all_receptions[:10] if len(all_receptions) > 10 else all_receptions
            self.load_recent_receptions(recent_receptions)
            
            # بارگذاری چک‌های در سررسید
            self.load_due_checks(due_checks)
            
        except Exception as e:
            print(f"خطا در به‌روزرسانی داشبورد: {e}")

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
            
            # 🔴 **تبدیل تاریخ میلادی به شمسی - نسخه بهبود یافته**
            reception_date = reception.get('reception_date', '')
            if reception_date:
                try:
                    # اگر تاریخ در فرمت رشته است، تبدیل کن
                    date_str = str(reception_date)
                    
                    # حذف زمان اگر وجود دارد
                    if ' ' in date_str:
                        date_str = date_str.split(' ')[0]
                    
                    # جداسازی سال، ماه، روز
                    parts = date_str.replace('-', '/').split('/')
                    if len(parts) == 3:
                        year, month, day = map(int, parts)
                        
                        # تبدیل میلادی به شمسی
                        miladi_date = datetime(year, month, day).date()
                        jalali_date = jdatetime.date.fromgregorian(date=miladi_date)
                        jalali_date_str = jalali_date.strftime('%Y/%m/%d')
                        
                        self.receptions_table.setItem(row, 3, 
                            QTableWidgetItem(jalali_date_str))
                    else:
                        self.receptions_table.setItem(row, 3, 
                            QTableWidgetItem(date_str))
                            
                except Exception as e:
                    print(f"⚠️ خطا در تبدیل تاریخ {reception_date}: {e}")
                    self.receptions_table.setItem(row, 3, 
                        QTableWidgetItem(str(reception_date)))
            else:
                self.receptions_table.setItem(row, 3, QTableWidgetItem(''))
        
            
            self.receptions_table.setItem(row, 4, QTableWidgetItem(str(reception.get('estimated_cost', 0))))
            self.receptions_table.setItem(row, 5, QTableWidgetItem(reception.get('priority', '')))
            
            status_item = QTableWidgetItem(reception.get('status', ''))
            # رنگ‌بندی وضعیت
            status = reception.get('status', '')
            if status == 'تعمیر شده':
                status_item.setForeground(QColor('#27ae60'))
            elif status == 'در حال تعمیر':
                status_item.setForeground(QColor('#3498db'))
            elif status == 'در انتظار':
                status_item.setForeground(QColor('#f39c12'))
            elif status == 'تحویل داده شده':
                status_item.setForeground(QColor('#9b59b6'))
            
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
                jalali_date = convert_to_jalali_display(due_date)
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