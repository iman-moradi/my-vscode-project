# -*- coding: utf-8 -*-
"""
پنجره مستقل سیستم گزارش‌گیری
Design: تم تاریک، راست‌چین، فونت فارسی
"""

import sys
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QToolBar, QStatusBar,
    QTabWidget, QMenuBar, QScrollArea, QFrame,
    QMessageBox  # اضافه شد
)
from PySide6.QtCore import Qt, QSize, Signal
from PySide6.QtGui import QIcon, QFont, QPalette, QColor, QAction

from ui.forms.reports.reports_main_form import ReportsMainForm


class ReportsWindow(QMainWindow):
    """پنجره مستقل برای سیستم گزارش‌گیری"""
    
    window_closed = Signal()
    
    def __init__(self, data_manager, parent=None):
        super().__init__(parent)
        self.data_manager = data_manager
        self.parent_window = parent
        
        # تنظیمات اولیه پنجره
        self.setWindowTitle("📊 سیستم گزارش‌گیری شیروین")
        self.setGeometry(100, 100, 1200, 800)  # x, y, width, height
        
        # تم تاریک
        self.set_dark_theme()
        
        # تنظیم فونت فارسی
        self.set_font()
        
        # ایجاد رابط کاربری
        self.init_ui()
        
        # اتصال سیگنال‌ها
        self.setup_connections()
    
    def set_dark_theme(self):
        """تنظیم تم تاریک برای پنجره"""
        palette = self.palette()
        
        # رنگ‌های تم تاریک
        palette.setColor(QPalette.Window, QColor(0, 0, 0))  # زمینه سیاه
        palette.setColor(QPalette.WindowText, QColor(255, 255, 255))  # متن سفید
        palette.setColor(QPalette.Base, QColor(30, 30, 30))  # زمینه ویجت‌ها
        palette.setColor(QPalette.AlternateBase, QColor(45, 45, 45))
        palette.setColor(QPalette.ToolTipBase, QColor(0, 0, 0))
        palette.setColor(QPalette.ToolTipText, QColor(255, 255, 255))
        palette.setColor(QPalette.Text, QColor(255, 255, 255))
        palette.setColor(QPalette.Button, QColor(50, 50, 50))
        palette.setColor(QPalette.ButtonText, QColor(255, 255, 255))
        palette.setColor(QPalette.BrightText, QColor(255, 0, 0))
        palette.setColor(QPalette.Link, QColor(42, 130, 218))
        palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
        palette.setColor(QPalette.HighlightedText, QColor(255, 255, 255))
        
        self.setPalette(palette)
    
    def set_font(self):
        """تنظیم فونت فارسی برای پنجره"""
        try:
            font = QFont("B Nazanin", 11)
            font.setStyleStrategy(QFont.PreferAntialias)
            self.setFont(font)
        except:
            # اگر فونت پیدا نشد، از فونت پیش‌فرض سیستم استفاده کن
            font = QFont()
            font.setPointSize(11)
            self.setFont(font)
    
    def init_ui(self):
        """ایجاد رابط کاربری پنجره"""
        # ایجاد منو بار
        self.create_menu_bar()
        
        # ایجاد نوار ابزار
        self.create_tool_bar()
        
        # ایجاد ویجت مرکزی
        self.create_central_widget()
        
        # ایجاد نوار وضعیت
        self.create_status_bar()
    
    def create_menu_bar(self):
        """ایجاد منو بار گزارش‌گیری"""
        menubar = self.menuBar()
        
        # منوی فایل
        file_menu = menubar.addMenu("📁 فایل")
        
        # آیتم‌های منوی فایل
        act_new_report = QAction("📄 گزارش جدید", self)
        act_new_report.setShortcut("Ctrl+N")
        
        act_open_report = QAction("📂 باز کردن گزارش", self)
        act_open_report.setShortcut("Ctrl+O")
        
        act_save_report = QAction("💾 ذخیره گزارش", self)
        act_save_report.setShortcut("Ctrl+S")
        
        act_export_pdf = QAction("📄 خروجی PDF", self)
        act_export_excel = QAction("📊 خروجی Excel", self)
        
        act_print = QAction("🖨️ چاپ", self)
        act_print.setShortcut("Ctrl+P")
        
        act_exit = QAction("🚪 خروج", self)
        act_exit.setShortcut("Ctrl+Q")
        act_exit.triggered.connect(self.close)
        
        file_menu.addAction(act_new_report)
        file_menu.addAction(act_open_report)
        file_menu.addAction(act_save_report)
        file_menu.addSeparator()
        file_menu.addAction(act_export_pdf)
        file_menu.addAction(act_export_excel)
        file_menu.addSeparator()
        file_menu.addAction(act_print)
        file_menu.addSeparator()
        file_menu.addAction(act_exit)
        
        # منوی مشاهده
        view_menu = menubar.addMenu("👁️ مشاهده")
        
        act_refresh = QAction("🔄 بروزرسانی", self)
        act_refresh.setShortcut("F5")
        
        act_fullscreen = QAction("🖥️ حالت تمام صفحه", self)
        act_fullscreen.setShortcut("F11")
        
        view_menu.addAction(act_refresh)
        view_menu.addAction(act_fullscreen)
        
        # منوی گزارش‌ها
        reports_menu = menubar.addMenu("📊 گزارش‌ها")
        
        act_daily_report = QAction("📅 گزارش روزانه", self)
        act_weekly_report = QAction("📆 گزارش هفتگی", self)
        act_monthly_report = QAction("📅 گزارش ماهانه", self)
        act_financial_report = QAction("💰 گزارش مالی", self)
        act_inventory_report = QAction("📦 گزارش انبار", self)
        act_repair_report = QAction("🔧 گزارش تعمیرات", self)
        act_sales_report = QAction("🛒 گزارش فروش", self)
        act_customer_report = QAction("👥 گزارش مشتریان", self)
        
        reports_menu.addAction(act_daily_report)
        reports_menu.addAction(act_weekly_report)
        reports_menu.addAction(act_monthly_report)
        reports_menu.addSeparator()
        reports_menu.addAction(act_financial_report)
        reports_menu.addAction(act_inventory_report)
        reports_menu.addAction(act_repair_report)
        reports_menu.addAction(act_sales_report)
        reports_menu.addAction(act_customer_report)
        
        # منوی ابزارها
        tools_menu = menubar.addMenu("⚙️ ابزارها")
        
        act_chart_tools = QAction("📈 ابزارهای نمودار", self)
        act_filter_tools = QAction("🔍 ابزارهای فیلتر", self)
        act_export_tools = QAction("📤 ابزارهای خروجی", self)
        
        tools_menu.addAction(act_chart_tools)
        tools_menu.addAction(act_filter_tools)
        tools_menu.addAction(act_export_tools)
        
        # منوی کمک
        help_menu = menubar.addMenu("❓ راهنما")
        
        act_help = QAction("📘 راهنمای گزارش‌گیری", self)
        act_about = QAction("ℹ️ درباره سیستم گزارش‌گیری", self)
        
        help_menu.addAction(act_help)
        help_menu.addAction(act_about)
    
    def create_tool_bar(self):
        """ایجاد نوار ابزار گزارش‌گیری"""
        toolbar = QToolBar("نوار ابزار گزارش‌گیری")
        toolbar.setIconSize(QSize(24, 24))
        self.addToolBar(toolbar)
        
        # دکمه‌های نوار ابزار
        btn_new = QPushButton("📄 جدید")
        btn_new.setToolTip("گزارش جدید")
        
        btn_open = QPushButton("📂 بازکردن")
        btn_open.setToolTip("باز کردن گزارش ذخیره شده")
        
        btn_save = QPushButton("💾 ذخیره")
        btn_save.setToolTip("ذخیره گزارش")
        
        toolbar.addWidget(btn_new)
        toolbar.addWidget(btn_open)
        toolbar.addWidget(btn_save)
        toolbar.addSeparator()
        
        btn_print = QPushButton("🖨️ چاپ")
        btn_print.setToolTip("چاپ گزارش")
        
        btn_pdf = QPushButton("📄 PDF")
        btn_pdf.setToolTip("خروجی PDF")
        
        btn_excel = QPushButton("📊 Excel")
        btn_excel.setToolTip("خروجی Excel")
        
        toolbar.addWidget(btn_print)
        toolbar.addWidget(btn_pdf)
        toolbar.addWidget(btn_excel)
        toolbar.addSeparator()
        
        btn_refresh = QPushButton("🔄 بروزرسانی")
        btn_refresh.setToolTip("بروزرسانی داده‌ها")
        
        btn_chart = QPushButton("📈 نمودار")
        btn_chart.setToolTip("ایجاد نمودار جدید")
        
        btn_filter = QPushButton("🔍 فیلتر")
        btn_filter.setToolTip("اعمال فیلتر")
        
        toolbar.addWidget(btn_refresh)
        toolbar.addWidget(btn_chart)
        toolbar.addWidget(btn_filter)
    
    def create_central_widget(self):
        """ایجاد ویجت مرکزی پنجره"""
        # ایجاد اسکرول اریا برای پشتیبانی از صفحه‌های بزرگ
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        # ایجاد ویجت اصلی داخل اسکرول
        main_widget = QWidget()
        main_layout = QVBoxLayout(main_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)
        
        # هدر گزارش‌گیری
        header_frame = self.create_header()
        main_layout.addWidget(header_frame)
        
        # فرم اصلی گزارش‌ها
        self.reports_form = ReportsMainForm(self.data_manager)
        main_layout.addWidget(self.reports_form, 1)  # stretch factor = 1
        
        # فوتر
        footer_frame = self.create_footer()
        main_layout.addWidget(footer_frame)
        
        scroll_area.setWidget(main_widget)
        self.setCentralWidget(scroll_area)
    
    def create_header(self):
        """ایجاد هدر گزارش‌گیری"""
        frame = QFrame()
        frame.setFrameStyle(QFrame.StyledPanel | QFrame.Raised)
        frame.setStyleSheet("""
            QFrame {
                background-color: #2c3e50;
                border-radius: 8px;
                padding: 15px;
            }
            QLabel {
                color: #ffffff;
                font-size: 16pt;
                font-weight: bold;
            }
        """)
        
        layout = QHBoxLayout(frame)
        
        # عنوان
        title_label = QLabel("📊 سیستم گزارش‌گیری جامع شیروین")
        title_label.setAlignment(Qt.AlignCenter)
        
        # تاریخ شمسی (جاگذاری)
        date_label = QLabel("تاریخ: در حال بارگذاری...")
        date_label.setAlignment(Qt.AlignCenter)
        
        layout.addWidget(title_label, 7)  # 70% فضا
        layout.addWidget(date_label, 3)   # 30% فضا
        
        return frame
    
    def create_footer(self):
        """ایجاد فوتر گزارش‌گیری"""
        frame = QFrame()
        frame.setFrameStyle(QFrame.StyledPanel | QFrame.Sunken)
        frame.setStyleSheet("""
            QFrame {
                background-color: #34495e;
                border-radius: 5px;
                padding: 10px;
            }
            QLabel {
                color: #bdc3c7;
                font-size: 10pt;
            }
        """)
        
        layout = QHBoxLayout(frame)
        
        # اطلاعات نسخه
        version_label = QLabel("نسخه: ۱.۰.۰")
        
        # وضعیت سیستم
        status_label = QLabel("وضعیت: آماده")
        
        # راهنمای کلیدهای میانبر
        shortcuts_label = QLabel("میانبرها: F5=بروزرسانی | Ctrl+P=چاپ | Ctrl+S=ذخیره")
        
        layout.addWidget(version_label, 2)
        layout.addWidget(status_label, 3)
        layout.addWidget(shortcuts_label, 5)
        
        return frame
    
    def create_status_bar(self):
        """ایجاد نوار وضعیت"""
        status_bar = QStatusBar()
        self.setStatusBar(status_bar)
        
        # آیتم‌های نوار وضعیت
        status_bar.showMessage("سیستم گزارش‌گیری آماده است", 5000)
        
        # نمایش تاریخ شمسی در نوار وضعیت
        self.date_status_label = QLabel("")
        status_bar.addPermanentWidget(self.date_status_label)
        
        # نمایش تعداد گزارش‌ها
        self.reports_count_label = QLabel("گزارش‌ها: ۰")
        status_bar.addPermanentWidget(self.reports_count_label)
    
    def setup_connections(self):
        """اتصال سیگنال‌ها و اسلات‌ها"""
        # اتصال رویداد بسته شدن پنجره
        pass
    
    def closeEvent(self, event):
        """رویداد بسته شدن پنجره"""
        self.window_closed.emit()
        super().closeEvent(event)
    
    def refresh_data(self):
        """بروزرسانی داده‌های گزارش"""
        # TODO: پیاده‌سازی بروزرسانی داده‌ها
        self.statusBar().showMessage("داده‌ها بروزرسانی شدند", 3000)
    
    def export_to_pdf(self):
        """صدور خروجی PDF"""
        # TODO: پیاده‌سازی خروجی PDF
        QMessageBox.information(self, "خروجی PDF", "این قابلیت به زودی اضافه خواهد شد")
    
    def export_to_excel(self):
        """صدور خروجی Excel"""
        # TODO: پیاده‌سازی خروجی Excel
        QMessageBox.information(self, "خروجی Excel", "این قابلیت به زودی اضافه خواهد شد")
    
    def show_daily_report(self):
        """نمایش گزارش روزانه"""
        # TODO: پیاده‌سازی نمایش گزارش روزانه
        self.reports_form.show_tab(0)  # تب اول (گزارش روزانه)
    
    def show_financial_report(self):
        """نمایش گزارش مالی"""
        # TODO: پیاده‌سازی نمایش گزارش مالی
        self.reports_form.show_tab(3)  # تب چهارم (گزارش مالی)


if __name__ == "__main__":
    # تست مستقل پنجره گزارش‌گیری
    from PySide6.QtWidgets import QApplication
    import sys
    
    app = QApplication(sys.argv)
    
    # DataManager ساختگی برای تست
    class MockDataManager:
        def get_data(self, *args):
            return []
    
    window = ReportsWindow(MockDataManager())
    window.show()
    
    sys.exit(app.exec())