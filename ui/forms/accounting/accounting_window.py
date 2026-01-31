"""
پنجره مستقل سیستم حسابداری (مانند پنجره انبار)
"""

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QTabWidget, QStatusBar, QToolBar, QFrame,
    QScrollArea, QMessageBox, QSplitter
)
from PySide6.QtCore import Qt, QTimer, QSize, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QAction, QIcon, QFont
import jdatetime
from datetime import datetime
from utils.date_utils import get_current_jalali

# ایمپورت فرم اصلی حسابداری
from .accounting_main_form import AccountingMainForm


class AccountingWindow(QMainWindow):
    """پنجره مستقل سیستم حسابداری"""
    
    def __init__(self, data_manager, parent=None):
        super().__init__(parent)
        self.data_manager = data_manager
        self.parent_window = parent
        
        # تنظیمات پنجره
        self.setWindowTitle("🏦 سیستم حسابداری - تعمیرگاه شیروین")
        self.setGeometry(100, 100, 1400, 900)
        
        # 🔴 **راست‌چین کردن کامل**
        self.setLayoutDirection(Qt.RightToLeft)
        
        # تنظیم استایل تم تاریک
        self.setStyleSheet(self.get_dark_style())
        
        # تنظیم فونت فارسی
        self.set_fonts()
        
        # ایجاد رابط کاربری
        self.init_ui()
        
        # اتصال سیگنال‌ها
        self.setup_connections()
        
        # بارگذاری داده‌های اولیه
        self.load_initial_data()
        
        print("✅ پنجره حسابداری ایجاد شد")
    
    def get_dark_style(self):
        """استایل تم تاریک برای حسابداری"""
        return """
        /* استایل کلی - زمینه سیاه، متن سفید */
        QMainWindow {
            background-color: #000000;
            color: #ffffff;
        }
        
        QWidget {
            font-family: 'B Nazanin', Tahoma;
            background-color: #000000;
            color: #ffffff;
        }
        
        /* نوار منو */
        QMenuBar {
            background-color: #111111;
            color: white;
            font-size: 13px;
            padding: 5px;
            border-bottom: 1px solid #333;
        }
        
        QMenuBar::item {
            background-color: transparent;
            padding: 5px 15px;
            border-radius: 3px;
        }
        
        QMenuBar::item:selected {
            background-color: #2c2c2c;
        }
        
        /* منوها */
        QMenu {
            background-color: #111111;
            border: 1px solid #333;
            border-radius: 5px;
        }
        
        QMenu::item {
            padding: 8px 25px 8px 20px;
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
        
        /* تب‌ها */
        QTabWidget::pane {
            border: 1px solid #333;
            background-color: #1e1e1e;
            border-radius: 5px;
        }
        
        QTabBar::tab {
            background-color: #2c2c2c;
            color: #bbb;
            padding: 8px 15px;
            margin-left: 2px;
            border-top-left-radius: 4px;
            border-top-right-radius: 4px;
            font-size: 11pt;
        }
        
        QTabBar::tab:selected {
            background-color: #2ecc71;
            color: white;
            font-weight: bold;
        }
        
        QTabBar::tab:hover:!selected {
            background-color: #3c3c3c;
        }
        
        /* نوار وضعیت */
        QStatusBar {
            background-color: #1e1e1e;
            color: white;
            font-size: 12px;
            border-top: 1px solid #333;
        }
        
        /* جدول‌ها */
        QTableWidget {
            background-color: #111111;
            alternate-background-color: #0a0a0a;
            selection-background-color: #2ecc71;
            selection-color: white;
            gridline-color: #333;
            color: white;
            border: 1px solid #333;
        }
        
        QTableWidget::item {
            padding: 8px;
            color: white;
        }
        
        QHeaderView::section {
            background-color: #2c3e50;
            color: white;
            padding: 10px;
            border: none;
            font-weight: bold;
            text-align: right;
        }
        
        /* دکمه‌ها */
        QPushButton {
            padding: 8px 15px;
            border-radius: 4px;
            font-weight: bold;
            border: none;
            color: white;
            text-align: right;
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
        
        /* فیلدهای ورودی */
        QLineEdit, QTextEdit, QComboBox, QSpinBox, QDoubleSpinBox {
            background-color: #2c2c2c;
            color: white;
            border: 1px solid #333;
            border-radius: 4px;
            padding: 8px;
            selection-background-color: #3498db;
            text-align: right;
        }
        
        QLineEdit:focus, QTextEdit:focus, QComboBox:focus {
            border: 2px solid #3498db;
        }
        
        QLineEdit::placeholder, QTextEdit::placeholder {
            color: #666;
            text-align: right;
        }
        
        /* برچسب‌ها */
        QLabel {
            color: white;
            text-align: right;
        }
        
        /* Frame */
        QFrame {
            background-color: #1e1e1e;
            border: 1px solid #333;
        }
        
        /* اسکرول بار */
        QScrollArea {
            border: none;
            background-color: #000000;
        }
        
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
        
        /* لیست‌ها */
        QListWidget {
            background-color: #1e1e1e;
            color: white;
            border: 1px solid #333;
            text-align: right;
        }
        
        QListWidget::item {
            padding: 8px;
            text-align: right;
        }
        
        QListWidget::item:selected {
            background-color: #2ecc71;
            color: white;
        }
        
        /* دکمه مخفی/نمایش هدر */
        #toggle_header_btn {
            background-color: #3498db;
            color: white;
            border: none;
            padding: 5px 10px;
            border-radius: 3px;
            font-size: 10pt;
            font-weight: bold;
            min-width: 100px;
        }
        
        #toggle_header_btn:hover {
            background-color: #2980b9;
        }
        """
    
    def set_fonts(self):
        """تنظیم فونت‌های فارسی"""
        font = QFont()
        font.setFamily("B Nazanin")
        font.setPointSize(10)
        self.setFont(font)
    
    def init_ui(self):
        """ایجاد رابط کاربری پنجره با اسکرول عمودی"""
        # ویجت مرکزی اصلی
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # لیوت اصلی
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # ایجاد اسکرول‌اریا برای کل پنجره
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: #000000;
            }
            QScrollBar:vertical {
                background-color: #2c2c2c;
                width: 16px;
                border-radius: 8px;
            }
            QScrollBar::handle:vertical {
                background-color: #444;
                border-radius: 8px;
                min-height: 30px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #555;
            }
        """)
        
        # ویجت محتوای اسکرول
        scroll_content = QWidget()
        scroll_content.setLayoutDirection(Qt.RightToLeft)
        
        # لیوت محتوای اسکرول
        self.scroll_layout = QVBoxLayout(scroll_content)
        self.scroll_layout.setContentsMargins(10, 10, 10, 10)
        self.scroll_layout.setSpacing(10)
        
        # ایجاد دکمه مخفی/نمایش هدر (بالای فرم)
        self.toggle_header_btn = QPushButton("⬆️ مخفی کردن هدر")
        self.toggle_header_btn.setObjectName("toggle_header_btn")
        self.toggle_header_btn.clicked.connect(self.toggle_header_visibility)
        self.scroll_layout.addWidget(self.toggle_header_btn, 0, Qt.AlignCenter)
        
        # ایجاد فرم اصلی درون اسکرول
        self.accounting_form = AccountingMainForm(self.data_manager)
        self.scroll_layout.addWidget(self.accounting_form)
        
        # تنظیم محتوای اسکرول
        self.scroll_area.setWidget(scroll_content)
        main_layout.addWidget(self.scroll_area)
        
        # ایجاد منو بار
        self.create_menu_bar()
        
        # ایجاد نوار ابزار
        self.create_toolbar()
        
        # ایجاد نوار وضعیت
        self.create_status_bar()
        
        # وضعیت اولیه: هدر نمایش داده شود
        self.header_visible = True
        
        print("✅ رابط کاربری پنجره حسابداری با اسکرول ایجاد شد")
    
    def toggle_header_visibility(self):
        """مخفی یا نمایش هدر فرم"""
        self.header_visible = not self.header_visible
        
        if self.header_visible:
            self.toggle_header_btn.setText("⬆️ مخفی کردن هدر")
            # نمایش هدر
            if hasattr(self.accounting_form, 'show_header'):
                self.accounting_form.show_header()
        else:
            self.toggle_header_btn.setText("⬇️ نمایش هدر")
            # مخفی کردن هدر
            if hasattr(self.accounting_form, 'hide_header'):
                self.accounting_form.hide_header()
        
        # به‌روزرسانی اسکرول
        QTimer.singleShot(100, self.update_scroll_area)
    
    def update_scroll_area(self):
        """به‌روزرسانی اسکرول‌اریا"""
        self.scroll_area.verticalScrollBar().setValue(0)
    
    def create_menu_bar(self):
        """ایجاد نوار منوی حسابداری"""
        menubar = self.menuBar()
        
        # منوی فایل
        file_menu = menubar.addMenu("📁 فایل")
        
        new_action = QAction("📄 سند جدید", self)
        new_action.setShortcut("Ctrl+N")
        file_menu.addAction(new_action)
        
        save_action = QAction("💾 ذخیره", self)
        save_action.setShortcut("Ctrl+S")
        file_menu.addAction(save_action)
        
        file_menu.addSeparator()
        
        print_action = QAction("🖨️ چاپ", self)
        print_action.setShortcut("Ctrl+P")
        file_menu.addAction(print_action)
        
        export_action = QAction("📤 خروجی اکسل", self)
        export_action.setShortcut("Ctrl+E")
        file_menu.addAction(export_action)
        
        file_menu.addSeparator()
        
        close_action = QAction("❌ بستن پنجره", self)
        close_action.setShortcut("Ctrl+W")
        close_action.triggered.connect(self.close)
        file_menu.addAction(close_action)
        
        # منوی گزارشات
        reports_menu = menubar.addMenu("📊 گزارشات")
        
        daily_report_action = QAction("📅 گزارش روزانه", self)
        daily_report_action.triggered.connect(self.show_daily_report)
        reports_menu.addAction(daily_report_action)
        
        monthly_report_action = QAction("📈 گزارش ماهانه", self)
        monthly_report_action.triggered.connect(self.show_monthly_report)
        reports_menu.addAction(monthly_report_action)
        
        profit_report_action = QAction("💰 گزارش سود و زیان", self)
        profit_report_action.triggered.connect(self.show_profit_report)
        reports_menu.addAction(profit_report_action)
        
        cashflow_report_action = QAction("💸 گزارش گردش نقدی", self)
        cashflow_report_action.triggered.connect(self.show_cashflow_report)
        reports_menu.addAction(cashflow_report_action)
        
        reports_menu.addSeparator()
        
        custom_report_action = QAction("🎛️ گزارش سفارشی", self)
        custom_report_action.triggered.connect(self.show_custom_report)
        reports_menu.addAction(custom_report_action)
        
        # منوی تنظیمات
        settings_menu = menubar.addMenu("⚙️ تنظیمات")
        
        accounts_action = QAction("🏦 تنظیمات حساب‌ها", self)
        accounts_action.triggered.connect(self.open_accounts_settings)
        settings_menu.addAction(accounts_action)
        
        taxes_action = QAction("🧾 تنظیمات مالیات", self)
        taxes_action.triggered.connect(self.open_taxes_settings)
        settings_menu.addAction(taxes_action)
        
        partners_action = QAction("🤝 تنظیمات شرکا", self)
        partners_action.triggered.connect(self.open_partners_settings)
        settings_menu.addAction(partners_action)
        
        settings_menu.addSeparator()
        
        backup_action = QAction("💾 پشتیبان‌گیری مالی", self)
        backup_action.triggered.connect(self.backup_financial_data)
        settings_menu.addAction(backup_action)
        
        # منوی راهنما
        help_menu = menubar.addMenu("❓ راهنما")
        
        accounting_help_action = QAction("📚 راهنمای حسابداری", self)
        accounting_help_action.triggered.connect(self.show_accounting_help)
        help_menu.addAction(accounting_help_action)
        
        about_action = QAction("ℹ️ درباره سیستم حسابداری", self)
        about_action.triggered.connect(self.show_about_accounting)
        help_menu.addAction(about_action)
    
    def create_toolbar(self):
        """ایجاد نوار ابزار حسابداری"""
        toolbar = QToolBar("نوار ابزار حسابداری")
        toolbar.setIconSize(QSize(32, 32))
        toolbar.setMovable(False)
        self.addToolBar(toolbar)
        
        # دکمه‌های نوار ابزار
        actions = [
            ("🏦", "حساب‌ها", self.show_accounts, "#27ae60"),
            ("💰", "تراکنش‌ها", self.show_transactions, "#3498db"),
            ("🧾", "فاکتور", self.create_invoice, "#9b59b6"),
            ("💳", "چک‌ها", self.show_checks, "#e74c3c"),
            ("🤝", "شرکا", self.show_partners, "#f39c12"),
            ("📊", "داشبورد", self.show_dashboard, "#1abc9c"),
            ("📋", "خلاصه روز", self.show_daily_summary, "#34495e"),
        ]
        
        for icon, text, callback, color in actions:
            btn = QPushButton(f"{icon} {text}")
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {color};
                    color: white;
                    border: none;
                    padding: 10px 15px;
                    border-radius: 5px;
                    font-size: 12pt;
                    font-weight: bold;
                    min-width: 140px;
                    text-align: center;
                }}
                QPushButton:hover {{
                    background-color: {self.darken_color(color)};
                }}
            """)
            btn.clicked.connect(callback)
            toolbar.addWidget(btn)
            toolbar.addSeparator()
        
        toolbar.addWidget(QLabel("   "))  # فاصله
        
        # دکمه‌های سمت چپ
        refresh_btn = QPushButton("🔄 بروزرسانی")
        refresh_btn.clicked.connect(self.refresh_data)
        refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: #7f8c8d;
                color: white;
                border: none;
                padding: 10px 15px;
                border-radius: 5px;
                font-size: 11pt;
            }
            QPushButton:hover {
                background-color: #95a5a6;
            }
        """)
        toolbar.addWidget(refresh_btn)
    
    def darken_color(self, color):
        """تیره کردن رنگ برای حالت hover"""
        color = color.lstrip('#')
        r, g, b = tuple(int(color[i:i+2], 16) for i in (0, 2, 4))
        r = max(0, r - 30)
        g = max(0, g - 30)
        b = max(0, b - 30)
        return f'#{r:02x}{g:02x}{b:02x}'
    
    def create_status_bar(self):
        """ایجاد نوار وضعیت"""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        # برچسب تاریخ شمسی
        self.date_label = QLabel()
        self.status_bar.addPermanentWidget(self.date_label)
        
        # برچسب وضعیت مالی
        self.financial_status_label = QLabel("💰 وضعیت مالی: عادی")
        self.financial_status_label.setStyleSheet("color: #27ae60;")
        self.status_bar.addWidget(self.financial_status_label)
        
        # برچسب موجودی کل
        self.total_balance_label = QLabel("🏦 موجودی کل: در حال محاسبه...")
        self.status_bar.addWidget(self.total_balance_label)
        
        # برچسب زمان
        self.time_label = QLabel()
        self.status_bar.addPermanentWidget(self.time_label)
        
        # تایمر برای به‌روزرسانی زمان
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_status_bar)
        self.timer.start(1000)  # هر ثانیه
    
    def update_status_bar(self):
        """به‌روزرسانی نوار وضعیت"""
        # تاریخ و زمان شمسی
        try:
            from utils.date_utils import get_current_jalali, get_persian_weekday
            now = jdatetime.datetime.now()
            jalali_date = now.strftime('%Y/%m/%d')
            weekday = get_persian_weekday(now)
            self.date_label.setText(f"📅 {jalali_date} - {weekday}")
            self.time_label.setText(f"🕒 {now.strftime('%H:%M:%S')}")
        except:
            now = jdatetime.datetime.now()
            self.date_label.setText(f"📅 {now.strftime('%Y/%m/%d')}")
            self.time_label.setText(f"🕒 {now.strftime('%H:%M:%S')}")
        
        # به‌روزرسانی موجودی کل (هر 30 ثانیه)
        if not hasattr(self, 'last_balance_update') or (datetime.now() - self.last_balance_update).seconds > 30:
            self.update_total_balance()
            self.last_balance_update = datetime.now()
    
    def update_total_balance(self):
        """به‌روزرسانی موجودی کل حساب‌ها"""
        try:
            query = """
            SELECT SUM(current_balance) as total_balance 
            FROM Accounts 
            WHERE is_active = 1
            """
            result = self.data_manager.db.fetch_one(query)
            
            if result and result.get('total_balance'):
                total_balance = result['total_balance']
                total_balance_toman = total_balance / 10  # تبدیل به تومان
                
                # تعیین وضعیت مالی
                if total_balance_toman > 0:
                    status_text = "مثبت"
                    status_color = "#27ae60"
                elif total_balance_toman < 0:
                    status_text = "منفی"
                    status_color = "#e74c3c"
                else:
                    status_text = "صفر"
                    status_color = "#f39c12"
                
                # به‌روزرسانی برچسب‌ها
                self.financial_status_label.setText(f"💰 وضعیت مالی: {status_text}")
                self.financial_status_label.setStyleSheet(f"color: {status_color};")
                
                self.total_balance_label.setText(f"🏦 موجودی کل: {total_balance_toman:,.0f} تومان")
            else:
                self.total_balance_label.setText("🏦 موجودی کل: ۰ تومان")
                
        except Exception as e:
            print(f"⚠️ خطا در محاسبه موجودی کل: {e}")
            self.total_balance_label.setText("🏦 موجودی کل: خطا در محاسبه")
    
    def load_initial_data(self):
        """بارگذاری داده‌های اولیه"""
        self.update_total_balance()
        print("✅ داده‌های اولیه حسابداری بارگذاری شد")
    
    def setup_connections(self):
        """اتصال سیگنال‌ها"""
        # اتصال فرم اصلی به پنجره
        if hasattr(self.accounting_form, 'data_changed'):
            self.accounting_form.data_changed.connect(self.on_data_changed)
    
    def on_data_changed(self):
        """هنگام تغییر داده‌ها در فرم"""
        self.update_total_balance()
        print("📊 داده‌های حسابداری تغییر کرد")
    
    # ---------- متدهای منوها ----------
    
    def show_daily_report(self):
        """نمایش گزارش روزانه"""
        try:
            from .reports.daily_report import DailyReportDialog
            dialog = DailyReportDialog(self.data_manager, self)
            dialog.exec()
        except ImportError:
            QMessageBox.information(self, "گزارش روزانه", "این بخش به زودی اضافه خواهد شد.")
    
    def show_monthly_report(self):
        """نمایش گزارش ماهانه"""
        QMessageBox.information(self, "گزارش ماهانه", "این بخش به زودی اضافه خواهد شد.")
    
    def show_profit_report(self):
        """نمایش گزارش سود و زیان"""
        QMessageBox.information(self, "گزارش سود و زیان", "این بخش به زودی اضافه خواهد شد.")
    
    def show_cashflow_report(self):
        """نمایش گزارش گردش نقدی"""
        QMessageBox.information(self, "گزارش گردش نقدی", "این بخش به زونی اضافه خواهد شد.")
    
    def show_custom_report(self):
        """نمایش گزارش سفارشی"""
        QMessageBox.information(self, "گزارش سفارشی", "این بخش به زونی اضافه خواهد شد.")
    
    def open_accounts_settings(self):
        """تنظیمات حساب‌ها"""
        QMessageBox.information(self, "تنظیمات حساب‌ها", "این بخش به زونی اضافه خواهد شد.")
    
    def open_taxes_settings(self):
        """تنظیمات مالیات"""
        QMessageBox.information(self, "تنظیمات مالیات", "این بخش به زونی اضافه خواهد شد.")
    
    def open_partners_settings(self):
        """تنظیمات شرکا"""
        QMessageBox.information(self, "تنظیمات شرکا", "این بخش به زونی اضافه خواهد شد.")
    
    def backup_financial_data(self):
        """پشتیبان‌گیری از داده‌های مالی"""
        try:
            backup_path = self.data_manager.db.backup_database(
                backup_name=f"financial_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
            )
            if backup_path:
                QMessageBox.information(
                    self, 
                    "پشتیبان‌گیری موفق",
                    f"✅ پشتیبان‌گیری از داده‌های مالی با موفقیت انجام شد.\n\nمسیر: {backup_path}"
                )
            else:
                QMessageBox.warning(self, "خطا", "❌ خطا در پشتیبان‌گیری")
        except Exception as e:
            QMessageBox.critical(self, "خطا", f"❌ خطا در پشتیبان‌گیری:\n\n{str(e)}")
    
    def show_accounting_help(self):
        """نمایش راهنمای حسابداری"""
        help_text = """
        <h2>📚 راهنمای سیستم حسابداری</h2>
        
        <h3>🏦 بخش‌های اصلی:</h3>
        <ul>
            <li><b>حساب‌ها:</b> مدیریت حساب‌های بانکی و نقدی</li>
            <li><b>تراکنش‌ها:</b> ثبت دریافت، پرداخت و انتقال وجه</li>
            <li><b>فاکتورها:</b> صدور فاکتور برای خدمات و قطعات</li>
            <li><b>چک‌ها:</b> مدیریت چک‌های دریافتی و پرداختی</li>
            <li><b>شرکا:</b> مدیریت شرکا و محاسبه سود</li>
            <li><b>گزارشات:</b> انواع گزارش‌های مالی</li>
        </ul>
        
        <h3>🔧 نحوه شروع:</h3>
        <ol>
            <li>ابتدا حساب‌های بانکی و صندوق‌ها را ثبت کنید</li>
            <li>تراکنش‌های مالی را روزانه ثبت کنید</li>
            <li>از پذیرش‌های تکمیل شده، فاکتور صادر کنید</li>
            <li>چک‌ها را با تاریخ سررسید ثبت کنید</li>
            <li>اطلاعات شرکا و درصد سهم آنها را تنظیم کنید</li>
        </ol>
        
        <h3>⚠️ نکات مهم:</h3>
        <ul>
            <li>تمام مبالغ به ریال ذخیره می‌شوند</li>
            <li>نمایش مبالغ به تومان است (هر تومان = ۱۰ ریال)</li>
            <li>تاریخ‌ها به صورت شمسی نمایش داده می‌شوند</li>
            <li>پشتیبان‌گیری منظم از داده‌های مالی ضروری است</li>
        </ul>
        
        <p><b>📞 پشتیبانی:</b> در صورت نیاز به راهنمایی بیشتر با مدیر سیستم تماس بگیرید.</p>
        """
        
        QMessageBox.information(self, "راهنمای حسابداری", help_text)
    
    def show_about_accounting(self):
        """درباره سیستم حسابداری"""
        about_text = """
        <h2>🏦 سیستم حسابداری تعمیرگاه شیروین</h2>
        
        <p><b>🔢 نسخه:</b> ۱.۰.۰ (حسابداری پایه)</p>
        <p><b>📅 تاریخ انتشار:</b> ۱۴۰۴/۱۰/۰۶</p>
        <p><b>👨‍💻 توسعه‌دهنده:</b> تیم فنی شیروین</p>
        
        <h3>🎯 قابلیت‌های اصلی:</h3>
        <ul>
            <li>مدیریت چندحساب بانکی و نقدی</li>
            <li>ثبت کامل تراکنش‌های مالی</li>
            <li>فاکتورنویسی پیشرفته</li>
            <li>مدیریت چک با هشدار سررسید</li>
            <li>محاسبه خودکار سود شرکا</li>
            <li>گزارش‌گیری حرفه‌ای مالی</li>
            <li>پشتیبانی کامل از تاریخ شمسی</li>
            <li>رابط کاربری فارسی و راست‌چین</li>
        </ul>
        
        <h3>📊 خروجی‌ها:</h3>
        <ul>
            <li>گزارش سود و زیان</li>
            <li>تراز آزمایشی</li>
            <li>گردش حساب‌ها</li>
            <li>خلاصه مالی روزانه</li>
            <li>خروجی اکسل</li>
        </ul>
        
        <p>© ۱۴۰۴ - تمامی حقوق برای تعمیرگاه شیروین محفوظ است.</p>
        """
        
        QMessageBox.about(self, "درباره سیستم حسابداری", about_text)
    
    # ---------- متدهای نوار ابزار ----------
    
    def show_accounts(self):
        """نمایش تب حساب‌ها"""
        if hasattr(self.accounting_form, 'set_current_tab'):
            self.accounting_form.set_current_tab(0)  # تب حساب‌ها
    
    def show_transactions(self):
        """نمایش تب تراکنش‌ها"""
        if hasattr(self.accounting_form, 'set_current_tab'):
            self.accounting_form.set_current_tab(1)  # تب تراکنش‌ها
    
    def create_invoice(self):
        """ایجاد فاکتور جدید"""
        QMessageBox.information(self, "فاکتور جدید", "این بخش به زونی اضافه خواهد شد.")
    
    def show_checks(self):
        """نمایش تب چک‌ها"""
        if hasattr(self.accounting_form, 'set_current_tab'):
            self.accounting_form.set_current_tab(3)  # تب چک‌ها
    
    def show_partners(self):
        """نمایش تب شرکا"""
        if hasattr(self.accounting_form, 'set_current_tab'):
            self.accounting_form.set_current_tab(4)  # تب شرکا
    
    def show_dashboard(self):
        """نمایش داشبورد مالی"""
        if hasattr(self.accounting_form, 'set_current_tab'):
            # اگر داشبورد تب آخر است
            last_tab = self.accounting_form.tab_widget.count() - 1
            self.accounting_form.set_current_tab(last_tab)
    
    def show_daily_summary(self):
        """نمایش خلاصه روز"""
        try:
            from .forms.daily_summary_form import DailySummaryDialog
            dialog = DailySummaryDialog(self.data_manager, self)
            dialog.exec()
        except ImportError:
            QMessageBox.information(self, "خلاصه روز", "این بخش به زونی اضافه خواهد شد.")
    
    def refresh_data(self):
        """بروزرسانی داده‌ها"""
        self.update_total_balance()
        
        # بروزرسانی فرم اصلی
        if hasattr(self.accounting_form, 'refresh_all_tabs'):
            self.accounting_form.refresh_all_tabs()
        
        QMessageBox.information(self, "بروزرسانی", "✅ داده‌های حسابداری بروزرسانی شد.")
    
    def closeEvent(self, event):
        """مدیریت بسته شدن پنجره"""
        reply = QMessageBox.question(
            self, "بستن پنجره حسابداری",
            "آیا مطمئن هستید که می‌خواهید پنجره حسابداری را ببندید؟\n\n"
            "تغییرات ذخیره نشده از بین خواهند رفت.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # توقف تایمرها
            if hasattr(self, 'timer'):
                self.timer.stop()
            
            # اطلاع به پنجره اصلی
            if self.parent_window and hasattr(self.parent_window, 'accounting_window_closed'):
                self.parent_window.accounting_window_closed()
            
            event.accept()
        else:
            event.ignore()