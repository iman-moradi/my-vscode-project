"""
فرم اصلی حسابداری با تب‌های مختلف و هدر متحرک
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTabWidget, QLabel,
    QPushButton, QFrame, QScrollArea, QMessageBox, QSizePolicy,
    QSplitter
)
from PySide6.QtCore import Qt, QTimer, Signal, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QFont

# ایمپورت فرم‌های تب‌ها با استفاده از مسیر کامل
import sys
import os

# اضافه کردن مسیر پروژه
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

try:
    from ui.forms.accounting.forms.accounts_form import AccountsForm
    from ui.forms.accounting.forms.transactions_form import TransactionsForm
    from ui.forms.accounting.forms.invoice_form import InvoiceForm
    print("✅ فرم‌های حسابداری با موفقیت بارگذاری شدند")
except ImportError as e:
    print(f"⚠️ خطا در بارگذاری فرم‌های حسابداری: {e}")
    # کلاس‌های placeholder
    class AccountsForm(QWidget):
        def __init__(self, data_manager):
            super().__init__()
            label = QLabel("فرم حساب‌ها - خطا در بارگذاری")
            label.setAlignment(Qt.AlignCenter)
            layout = QVBoxLayout(self)
            layout.addWidget(label)
    class TransactionsForm(QWidget):
        def __init__(self, data_manager):
            super().__init__()
            label = QLabel("فرم تراکنش‌ها - خطا در بارگذاری")
            label.setAlignment(Qt.AlignCenter)
            layout = QVBoxLayout(self)
            layout.addWidget(label)
    class InvoiceForm(QWidget):
        def __init__(self, data_manager):
            super().__init__()
            label = QLabel("فرم فاکتورها - خطا در بارگذاری")
            label.setAlignment(Qt.AlignCenter)
            layout = QVBoxLayout(self)
            layout.addWidget(label)


class AccountingMainForm(QWidget):
    """فرم اصلی حسابداری با تب‌های مختلف و هدر متحرک"""
    
    data_changed = Signal()  # وقتی داده‌ها تغییر می‌کنند
    
    def __init__(self, data_manager):
        super().__init__()
        self.data_manager = data_manager
        
        # 🔴 **راست‌چین کردن کامل**
        self.setLayoutDirection(Qt.RightToLeft)
        
        # تنظیم استایل
        self.setup_styles()
        
        # ایجاد رابط کاربری
        self.init_ui()
        
        # بارگذاری فرم‌های تب
        self.load_tab_forms()
        
        # اتصال سیگنال‌ها
        self.setup_connections()
        
        # تایمر برای به‌روزرسانی آمار
        self.stats_timer = QTimer()
        self.stats_timer.timeout.connect(self.update_quick_stats)
        self.stats_timer.start(60000)  # هر دقیقه
        
        # بارگذاری اولیه آمار
        self.update_quick_stats()
        
        print("✅ فرم اصلی حسابداری با هدر متحرک ایجاد شد")
    
    def setup_styles(self):
        """تنظیم استایل فرم"""
        self.setStyleSheet("""
            /* استایل کلی */
            QWidget {
                background-color: #000000;
                color: #ffffff;
                font-family: 'B Nazanin';
            }
            
            /* هدر فرم */
            #header_widget {
                background-color: #1e1e1e;
                border: 2px solid #2ecc71;
                border-radius: 10px;
                padding: 15px;
            }
            
            /* کارت آمار سریع */
            .stat_card {
                background-color: #111111;
                border: 1px solid #333;
                border-radius: 8px;
                padding: 15px;
            }
            
            .stat_card_title {
                color: #bbb;
                font-size: 12px;
                font-weight: bold;
            }
            
            .stat_card_value {
                color: #ffffff;
                font-size: 18px;
                font-weight: bold;
            }
            
            /* تب‌ها با ارتفاع بیشتر */
            QTabWidget {
                background-color: #111111;
                border: 1px solid #333;
                border-radius: 5px;
                min-height: 1000px;  /* ارتفاع بیشتر برای کانتینر تب‌ها */
            }
            
            QTabWidget::pane {
                border: 1px solid #333;
                background-color: #111111;
                border-radius: 5px;
                min-height: 900px;  /* ارتفاع بیشتر برای پنل تب‌ها */
            }
            
            QTabBar::tab {
                background-color: #2c2c2c;
                color: #bbb;
                padding: 10px 20px;
                margin-left: 2px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                font-size: 11pt;
                min-height: 40px;  /* ارتفاع بیشتر برای تب‌ها */
            }
            
            QTabBar::tab:selected {
                background-color: #2ecc71;
                color: white;
                font-weight: bold;
            }
            
            QTabBar::tab:hover:!selected {
                background-color: #3c3c3c;
            }
            
            /* جداول داخل تب‌ها با اسکرول */
            QTableWidget {
                background-color: #111111;
                alternate-background-color: #0a0a0a;
                selection-background-color: #2ecc71;
                selection-color: white;
                gridline-color: #333;
                color: white;
                border: none;
                font-size: 13pt;  /* 🔴 افزایش سایز فونت کلی جدول */
                min-height: 700px;  /* 🔴 افزایش ارتفاع جدول */
            }
            
            QTableWidget::item {
                padding: 12px;  /* 🔴 افزایش padding */
                color: white;
                font-size: 12pt;  /* 🔴 افزایش سایز فونت آیتم‌ها */
                min-height: 45px;  /* 🔴 افزایش ارتفاع ردیف‌ها */
            }
            
            QHeaderView::section {
                background-color: #2c3e50;
                color: white;
                padding: 15px;  /* 🔴 افزایش padding */
                border: none;
                font-weight: bold;
                text-align: right;
                font-size: 13pt;  /* 🔴 افزایش سایز فونت هدر */
                min-height: 60px;  /* 🔴 افزایش ارتفاع هدر */
            }
                
            /* اسکرول‌بار برای جداول */
            QScrollBar:vertical {
                background-color: #111111;
                width: 14px;
                border-radius: 7px;
            }
            
            QScrollBar::handle:vertical {
                background-color: #2ecc71;
                border-radius: 7px;
                min-height: 30px;
            }
            
            QScrollBar::handle:vertical:hover {
                background-color: #27ae60;
            }
            
            QScrollBar:horizontal {
                background-color: #111111;
                height: 14px;
                border-radius: 7px;
            }
            
            QScrollBar::handle:horizontal {
                background-color: #2ecc71;
                border-radius: 7px;
                min-width: 30px;
            }
            
            QScrollBar::handle:horizontal:hover {
                background-color: #27ae60;
            }
        """)
    
    def init_ui(self):
        """ایجاد رابط کاربری با اسکرول عمودی برای کل فرم"""
        # لیوت اصلی
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(10)
        
        # 🔴 **هدر (آمار سریع)**
        self.header_widget = self.create_header_widget()
        self.header_widget.setObjectName("header_widget")
        main_layout.addWidget(self.header_widget)
        
        # 🔴 **تب‌های اصلی با ارتفاع بیشتر**
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabPosition(QTabWidget.North)
        self.tab_widget.setDocumentMode(True)
        self.tab_widget.setMinimumHeight(600)  # ارتفاع بیشتر برای کانتینر تب‌ها
        
        main_layout.addWidget(self.tab_widget)
        
        # تنظیم سیاست اندازه‌گیری
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
    
    def create_header_widget(self):
        """ایجاد ویجت هدر"""
        header_widget = QWidget()
        header_widget.setMinimumHeight(200)  # ارتفاع مناسب برای هدر
        
        layout = QVBoxLayout(header_widget)
        layout.setSpacing(15)
        layout.setContentsMargins(15, 15, 15, 15)
        
        # 🔴 **عنوان و تاریخ**
        title_layout = QHBoxLayout()
        
        title_label = QLabel("🏦 سیستم حسابداری پیشرفته")
        title_label.setStyleSheet("""
            QLabel {
                font-size: 20pt;
                font-weight: bold;
                color: #2ecc71;
            }
        """)
        
        # تاریخ شمسی امروز
        try:
            from utils.jalali_date_widget import get_current_jalali
            today_date = get_current_jalali()
        except:
            import jdatetime
            today_date = jdatetime.datetime.now().strftime("%Y/%m/%d")
        
        date_label = QLabel(f"📅 تاریخ امروز: {today_date}")
        date_label.setStyleSheet("""
            QLabel {
                font-size: 12pt;
                color: #bbb;
                font-weight: bold;
            }
        """)
        
        title_layout.addWidget(title_label)
        title_layout.addStretch()
        title_layout.addWidget(date_label)
        
        layout.addLayout(title_layout)
        
        # 🔴 **آمار سریع**
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(15)
        
        self.stat_cards = {}
        
        # ۴ کارت آماری
        stats_config = [
            ("💰 موجودی کل", "0", "#27ae60", "total_balance"),
            ("📈 درآمد امروز", "0", "#3498db", "today_income"),
            ("📉 هزینه امروز", "0", "#e74c3c", "today_expense"),
            ("🧾 فاکتور امروز", "0", "#9b59b6", "today_invoices")
        ]
        
        for title, default_value, color, key in stats_config:
            card = self.create_stat_card(title, default_value, color)
            stats_layout.addWidget(card)
            self.stat_cards[key] = card
        
        layout.addLayout(stats_layout)
        
        # 🔴 **دکمه‌های عملیاتی سریع**
        quick_buttons_layout = QHBoxLayout()
        quick_buttons_layout.setSpacing(10)
        
        quick_buttons = [
            ("➕ ثبت تراکنش", self.add_transaction, "#27ae60"),
            ("🏦 اضافه کردن حساب", self.add_account, "#3498db"),
            ("🧾 صدور فاکتور", self.create_invoice, "#9b59b6"),
            ("💳 ثبت چک", self.add_check, "#e74c3c"),
            ("🤝 اضافه کردن شریک", self.add_partner, "#f39c12")
        ]
        
        for text, callback, color in quick_buttons:
            btn = QPushButton(text)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {color};
                    color: white;
                    border: none;
                    padding: 10px 15px;
                    border-radius: 5px;
                    font-size: 11pt;
                    font-weight: bold;
                }}
                QPushButton:hover {{
                    background-color: {self.darken_color(color)};
                }}
            """)
            btn.clicked.connect(callback)
            btn.setMinimumHeight(40)
            quick_buttons_layout.addWidget(btn)
        
        quick_buttons_layout.addStretch()
        layout.addLayout(quick_buttons_layout)
        
        return header_widget
    
    def create_stat_card(self, title, value, color):
        """ایجاد یک کارت آمار"""
        card = QFrame()
        card.setObjectName("stat_card")
        card.setFixedHeight(90)
        
        layout = QVBoxLayout(card)
        layout.setSpacing(8)
        layout.setContentsMargins(15, 15, 15, 15)
        
        # عنوان
        title_label = QLabel(title)
        title_label.setObjectName("stat_card_title")
        title_label.setAlignment(Qt.AlignRight)
        layout.addWidget(title_label)
        
        # مقدار
        value_label = QLabel(value)
        value_label.setObjectName("stat_card_value")
        value_label.setAlignment(Qt.AlignRight)
        
        # اعمال استایل دینامیک
        value_label.setStyleSheet(f"color: {color}; font-size: 18pt; font-weight: bold;")
        
        layout.addWidget(value_label)
        layout.addStretch()
        
        # ذخیره رفرنس
        card.value_label = value_label
        
        return card
    
    def darken_color(self, color):
        """تیره کردن رنگ برای hover"""
        color = color.lstrip('#')
        r, g, b = tuple(int(color[i:i+2], 16) for i in (0, 2, 4))
        r = max(0, r - 30)
        g = max(0, g - 30)
        b = max(0, b - 30)
        return f'#{r:02x}{g:02x}{b:02x}'
    
    def hide_header(self):
        """مخفی کردن هدر"""
        self.header_widget.hide()
    
    def show_header(self):
        """نمایش هدر"""
        self.header_widget.show()
    
    def load_tab_forms(self):
        """بارگذاری فرم‌های تب‌های مختلف"""
        
        # 🔴 **تب ۱: حساب‌ها**
        try:
            self.accounts_tab = AccountsForm(self.data_manager)
            self.tab_widget.addTab(self.accounts_tab, "🏦 حساب‌ها")
            
            # اتصال سیگنال تغییر داده
            if hasattr(self.accounts_tab, 'data_changed'):
                self.accounts_tab.data_changed.connect(self.on_data_changed)
                
            print("✅ تب حساب‌ها بارگذاری شد")
            
        except Exception as e:
            print(f"⚠️ خطا در بارگذاری تب حساب‌ها: {e}")
            error_widget = QLabel(f"خطا در بارگذاری حساب‌ها:\n{str(e)}")
            error_widget.setAlignment(Qt.AlignCenter)
            self.tab_widget.addTab(error_widget, "🏦 حساب‌ها")
        
        # 🔴 **تب ۲: تراکنش‌ها**
        try:
            self.transactions_tab = TransactionsForm(self.data_manager)
            self.tab_widget.addTab(self.transactions_tab, "💰 تراکنش‌ها")
            
            # اتصال سیگنال تغییر داده
            if hasattr(self.transactions_tab, 'data_changed'):
                self.transactions_tab.data_changed.connect(self.on_data_changed)
                
            print("✅ تب تراکنش‌ها بارگذاری شد")
            
        except Exception as e:
            print(f"⚠️ خطا در بارگذاری تب تراکنش‌ها: {e}")
            error_widget = QLabel(f"خطا در بارگذاری تراکنش‌ها:\n{str(e)}")
            error_widget.setAlignment(Qt.AlignCenter)
            self.tab_widget.addTab(error_widget, "💰 تراکنش‌ها")
        
        # 🔴 **تب ۳: فاکتورها**
        try:
            self.invoice_tab = InvoiceForm(self.data_manager)
            self.tab_widget.addTab(self.invoice_tab, "🧾 فاکتورها")
            
            # اتصال سیگنال تغییر داده
            if hasattr(self.invoice_tab, 'data_changed'):
                self.invoice_tab.data_changed.connect(self.on_data_changed)
                
            print("✅ تب فاکتورها بارگذاری شد")
            
        except Exception as e:
            print(f"⚠️ خطا در بارگذاری تب فاکتورها: {e}")
            error_widget = QLabel(f"خطا در بارگذاری فاکتورها:\n{str(e)}")
            error_widget.setAlignment(Qt.AlignCenter)
            error_widget.setStyleSheet("""
                QLabel {
                    font-size: 11pt;
                    color: #e74c3c;
                    background-color: #111111;
                    padding: 20px;
                    border: 2px solid #e74c3c;
                    border-radius: 10px;
                }
            """)
            error_widget.setWordWrap(True)
            self.tab_widget.addTab(error_widget, "🧾 فاکتورها")
        

        # 🔴 **تب ۴: چک‌ها**
        try:
            from ui.forms.accounting.forms.checks_form import ChecksForm
            self.checks_tab = ChecksForm(self.data_manager)
            self.tab_widget.addTab(self.checks_tab, "💳 چک‌ها")
            
            # اتصال سیگنال تغییر داده
            if hasattr(self.checks_tab, 'data_changed'):
                self.checks_tab.data_changed.connect(self.on_data_changed)
                
            print("✅ تب چک‌ها بارگذاری شد")
            
        except ImportError as e:
            print(f"⚠️ خطا در بارگذاری تب چک‌ها: {e}")
            error_widget = QLabel(f"خطا در بارگذاری چک‌ها:\n{str(e)}")
            error_widget.setAlignment(Qt.AlignCenter)
            error_widget.setStyleSheet("""
                QLabel {
                    font-size: 11pt;
                    color: #e74c3c;
                    background-color: #111111;
                    padding: 20px;
                    border: 2px solid #e74c3c;
                    border-radius: 10px;
                }
            """)
            error_widget.setWordWrap(True)
            self.tab_widget.addTab(error_widget, "💳 چک‌ها")
        except Exception as e:
            print(f"⚠️ خطای دیگر در بارگذاری تب چک‌ها: {e}")
            import traceback
            traceback.print_exc()
            error_widget = QLabel(f"خطا:\n{str(e)[:100]}")
            error_widget.setAlignment(Qt.AlignCenter)
            self.tab_widget.addTab(error_widget, "💳 چک‌ها")
        
            # 🔴 **تب 5: شرکا (جدید)**
        try:
            from ui.forms.accounting.forms.partners_form import PartnersForm
            self.partners_tab = PartnersForm(self.data_manager)
            self.tab_widget.addTab(self.partners_tab, "🤝 شرکا")
            
            if hasattr(self.partners_tab, 'data_changed'):
                self.partners_tab.data_changed.connect(self.on_data_changed)
                
            print("✅ تب شرکا بارگذاری شد")
            
        except ImportError as e:
            print(f"⚠️ خطا در بارگذاری تب شرکا: {e}")
            error_widget = QLabel(f"خطا در بارگذاری شرکا:\n{str(e)}")
            error_widget.setAlignment(Qt.AlignCenter)
            self.tab_widget.addTab(error_widget, "🤝 شرکا")
        
        # 🔴 **تب 6: محاسبه سود**

        try:
            from ui.forms.accounting.forms.profit_calculation_form import ProfitCalculationForm
            self.profit_calc_tab = ProfitCalculationForm(self.data_manager)
            self.tab_widget.addTab(self.profit_calc_tab, "📈 محاسبه سود")
            
            # اتصال سیگنال تغییر داده
            if hasattr(self.profit_calc_tab, 'data_changed'):
                self.profit_calc_tab.data_changed.connect(self.on_data_changed)
            
            print("✅ تب محاسبه سود بارگذاری شد")
            
        except ImportError as e:
            print(f"⚠️ خطا در بارگذاری تب محاسبه سود: {e}")
            import traceback
            traceback.print_exc()
            error_widget = QLabel(f"خطا در بارگذاری محاسبه سود:\n{str(e)[:100]}")
            error_widget.setAlignment(Qt.AlignCenter)
            error_widget.setStyleSheet("""
                QLabel {
                    font-size: 11pt;
                    color: #e74c3c;
                    background-color: #111111;
                    padding: 20px;
                    border: 2px solid #e74c3c;
                    border-radius: 10px;
                }
            """)
            error_widget.setWordWrap(True)
            self.tab_widget.addTab(error_widget, "📈 محاسبه سود")
        
    # 🔴 **تب ۷: گزارش‌ها** (تب ۷ است نه ۶)
        try:
            from ui.forms.accounting.forms.financial_reports_form import FinancialReportsForm
            self.reports_tab = FinancialReportsForm(self.data_manager)
            self.tab_widget.addTab(self.reports_tab, "📊 گزارش‌ها")
            
            # اتصال سیگنال تغییر داده
            if hasattr(self.reports_tab, 'data_changed'):
                self.reports_tab.data_changed.connect(self.on_data_changed)
                
            print("✅ تب گزارش‌ها بارگذاری شد")
            
        except ImportError as e:
            print(f"⚠️ خطا در بارگذاری تب گزارش‌ها: {e}")
            import traceback
            traceback.print_exc()
            error_widget = QLabel(f"خطا در بارگذاری گزارش‌ها:\n{str(e)[:200]}")
            error_widget.setAlignment(Qt.AlignCenter)
            error_widget.setStyleSheet("""
                QLabel {
                    font-size: 11pt;
                    color: #e74c3c;
                    background-color: #111111;
                    padding: 20px;
                    border: 2px solid #e74c3c;
                    border-radius: 10px;
                }
            """)
            error_widget.setWordWrap(True)
            self.tab_widget.addTab(error_widget, "📊 گزارش‌ها")
        except Exception as e:
            print(f"⚠️ خطای دیگر در بارگذاری تب گزارش‌ها: {e}")
            traceback.print_exc()
            error_widget = QLabel(f"خطا:\n{str(e)[:100]}")
            error_widget.setAlignment(Qt.AlignCenter)
            self.tab_widget.addTab(error_widget, "📊 گزارش‌ها")
        
        # 🔴 **تب ۸: خلاصه روز**
        try:
            from ui.forms.accounting.forms.daily_summary_form import DailySummaryForm
            self.summary_tab = DailySummaryForm(self.data_manager)
            self.tab_widget.addTab(self.summary_tab, "📋 خلاصه روز")
            print("✅ تب خلاصه روز بارگذاری شد")
        except ImportError as e:
            print(f"⚠️ خطا در بارگذاری تب خلاصه روز: {e}")
            summary_placeholder = QLabel("📋 خلاصه روزانه\n\nبه زودی اضافه خواهد شد...")
            summary_placeholder.setAlignment(Qt.AlignCenter)
            summary_placeholder.setStyleSheet("font-size: 14pt; color: #bbb;")
            self.tab_widget.addTab(summary_placeholder, "📋 خلاصه روز")
    
    def setup_connections(self):
        """اتصال سیگنال‌ها"""
        # وقتی تب تغییر می‌کند، داده‌های آن تب را بروزرسانی کن
        self.tab_widget.currentChanged.connect(self.on_tab_changed)
    
    def on_tab_changed(self, index):
        """هنگام تغییر تب"""
        tab_name = self.tab_widget.tabText(index)
        print(f"📌 تغییر به تب: {tab_name}")
        
        # بروزرسانی فرم فعال
        self.refresh_current_tab()
    
    def refresh_current_tab(self):
        """بروزرسانی تب فعلی"""
        current_index = self.tab_widget.currentIndex()
        current_widget = self.tab_widget.widget(current_index)
        
        if hasattr(current_widget, 'refresh_data'):
            current_widget.refresh_data()
    
    def refresh_all_tabs(self):
        """بروزرسانی تمام تب‌ها"""
        print("🔄 بروزرسانی تمام تب‌های حسابداری...")
        
        for i in range(self.tab_widget.count()):
            tab_widget = self.tab_widget.widget(i)
            if hasattr(tab_widget, 'refresh_data'):
                try:
                    tab_widget.refresh_data()
                except Exception as e:
                    print(f"⚠️ خطا در بروزرسانی تب {i}: {e}")
        
        # بروزرسانی آمار سریع
        self.update_quick_stats()
        
        print("✅ تمام تب‌ها بروزرسانی شدند")
    
    def update_quick_stats(self):
        """بروزرسانی آمار سریع در هدر"""
        try:
            # 🔴 **موجودی کل حساب‌ها**
            query_total = """
            SELECT SUM(current_balance) as total 
            FROM Accounts 
            WHERE is_active = 1
            """
            result_total = self.data_manager.db.fetch_one(query_total)
            
            # حل مشکل None
            if result_total and result_total.get('total') is not None:
                total_balance = result_total.get('total', 0)
            else:
                total_balance = 0
                
            total_toman = total_balance / 10 if total_balance else 0
            
            if 'total_balance' in self.stat_cards:
                self.stat_cards['total_balance'].value_label.setText(f"{total_toman:,.0f} تومان")
                if total_toman >= 0:
                    self.stat_cards['total_balance'].value_label.setStyleSheet(
                        "color: #27ae60; font-size: 18pt; font-weight: bold;"
                    )
                else:
                    self.stat_cards['total_balance'].value_label.setStyleSheet(
                        "color: #e74c3c; font-size: 18pt; font-weight: bold;"
                    )
            
            # 🔴 **درآمد امروز (فقط دریافت‌ها)**
            today = self.data_manager.db.get_current_jalali_date()
            today_gregorian = self.data_manager.db.jalali_to_gregorian(today)
            
            query_income = """
            SELECT SUM(amount) as total 
            FROM AccountingTransactions 
            WHERE transaction_type = 'دریافت' 
            AND DATE(transaction_date) = ?
            """
            result_income = self.data_manager.db.fetch_one(query_income, (today_gregorian,))
            
            # حل مشکل None
            if result_income and result_income.get('total') is not None:
                today_income = result_income.get('total', 0)
            else:
                today_income = 0
                
            today_income_toman = today_income / 10 if today_income else 0
            
            if 'today_income' in self.stat_cards:
                self.stat_cards['today_income'].value_label.setText(f"{today_income_toman:,.0f} تومان")
            
            # 🔴 **هزینه امروز (فقط پرداخت‌ها)**
            query_expense = """
            SELECT SUM(amount) as total 
            FROM AccountingTransactions 
            WHERE transaction_type = 'پرداخت' 
            AND DATE(transaction_date) = ?
            """
            result_expense = self.data_manager.db.fetch_one(query_expense, (today_gregorian,))
            
            # حل مشکل None
            if result_expense and result_expense.get('total') is not None:
                today_expense = result_expense.get('total', 0)
            else:
                today_expense = 0
                
            today_expense_toman = today_expense / 10 if today_expense else 0
            
            if 'today_expense' in self.stat_cards:
                self.stat_cards['today_expense'].value_label.setText(f"{today_expense_toman:,.0f} تومان")
            
            # 🔴 **تعداد فاکتورهای امروز - CORRECTED: استفاده از invoice_date به جای creation_date**
            query_invoices = """
            SELECT COUNT(*) as count 
            FROM Invoices 
            WHERE DATE(invoice_date) = ?
            """
            result_invoices = self.data_manager.db.fetch_one(query_invoices, (today_gregorian,))

            # حل مشکل None
            if result_invoices and result_invoices.get('count') is not None:
                today_invoices = result_invoices.get('count', 0)
            else:
                today_invoices = 0
            
            if 'today_invoices' in self.stat_cards:
                self.stat_cards['today_invoices'].value_label.setText(f"{today_invoices} عدد")
            
            # 🔴 **تعداد چک‌های امروز - اضافه کردن برای رفع خطای مشابه**
            query_checks = """
            SELECT COUNT(*) as count 
            FROM Checks 
            WHERE DATE(issue_date) = ?
            """
            result_checks = self.data_manager.db.fetch_one(query_checks, (today_gregorian,))
            
            # حل مشکل None
            if result_checks and result_checks.get('count') is not None:
                today_checks = result_checks.get('count', 0)
            else:
                today_checks = 0
            
            if 'today_checks' in self.stat_cards:
                self.stat_cards['today_checks'].value_label.setText(f"{today_checks} عدد")
                
        except Exception as e:
            print(f"⚠️ خطا در بروزرسانی آمار سریع: {e}")
            import traceback
            traceback.print_exc()

    def on_data_changed(self):
        """هنگام تغییر داده‌ها در هر تب"""
        self.data_changed.emit()
        self.update_quick_stats()
    
    def set_current_tab(self, tab_index):
        """تنظیم تب فعلی"""
        if 0 <= tab_index < self.tab_widget.count():
            self.tab_widget.setCurrentIndex(tab_index)
    
    # ---------- متدهای دکمه‌های سریع ----------
    
    def add_transaction(self):
        """ثبت تراکنش جدید"""
        try:
            from ui.forms.accounting.dialogs.transaction_dialog import TransactionDialog
            dialog = TransactionDialog(self.data_manager, parent=self)
            if dialog.exec():
                self.on_data_changed()
                # بروزرسانی تب تراکنش‌ها
                if hasattr(self, 'transactions_tab'):
                    self.transactions_tab.refresh_data()
        except ImportError:
            QMessageBox.information(self, "ثبت تراکنش", 
                "فرم ثبت تراکنش به زودی اضافه خواهد شد.")
    
    def add_account(self):
        """افزودن حساب جدید"""
        try:
            from ui.forms.accounting.dialogs.account_dialog import AccountDialog
            dialog = AccountDialog(self.data_manager, parent=self)
            if dialog.exec():
                self.on_data_changed()
                # بروزرسانی تب حساب‌ها
                if hasattr(self, 'accounts_tab'):
                    self.accounts_tab.refresh_data()
        except ImportError:
            QMessageBox.information(self, "افزودن حساب", 
                "فرم افزودن حساب به زودی اضافه خواهد شد.")
    
    def create_invoice(self):
        """صدور فاکتور جدید"""
        try:
            # رفتن به تب فاکتورها (تب سوم، اندیس 2)
            self.tab_widget.setCurrentIndex(2)
            
            # ایجاد فاکتور جدید در فرم فاکتورها
            if hasattr(self, 'invoice_tab'):
                try:
                    self.invoice_tab.create_new_invoice()
                    QMessageBox.information(self, "فاکتور جدید", 
                        "✅ فرم فاکتور جدید آماده است.")
                except Exception as e:
                    QMessageBox.warning(self, "خطا", 
                        f"خطا در ایجاد فاکتور جدید:\n{str(e)}")
            else:
                QMessageBox.information(self, "صدور فاکتور", 
                    "فرم فاکتورها آماده نیست.")
        except Exception as e:
            print(f"⚠️ خطا در باز کردن فرم فاکتور: {e}")
            QMessageBox.warning(self, "خطا", 
                "خطا در باز کردن فرم فاکتورها.")
    
    def add_check(self):
        """ثبت چک جدید"""
        QMessageBox.information(self, "ثبت چک", 
            "فرم ثبت چک به زودی اضافه خواهد شد.")
    
    def add_partner(self):
        """افزودن شریک جدید"""
        QMessageBox.information(self, "افزودن شریک", 
            "فرم افزودن شریک به زودی اضافه خواهد شد.")