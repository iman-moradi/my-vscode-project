# ui/forms/reports/forms/inventory_report_form.py
"""
فرم گزارش انبار کامل
شامل: خلاصه انبارها، هشدارهای موجودی کم، حرکات انبار
"""

import datetime
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QPushButton, QFrame, QScrollArea,
    QTableWidget, QTableWidgetItem, QHeaderView,
    QComboBox, QLineEdit, QDateEdit, QGroupBox,
    QFormLayout, QSpinBox, QCheckBox, QTextEdit,
    QProgressBar, QTabWidget, QSplitter, QSizePolicy
)
from PySide6.QtCore import Qt, Signal, QDate, QTimer
from PySide6.QtGui import QFont, QColor, QAction, QPainter, QBrush
from PySide6.QtCharts import QChart, QChartView, QBarSeries, QBarSet, QPieSeries, QPieSlice

from utils.jalali_date_widget import get_current_jalali, gregorian_to_jalali, jalali_to_gregorian
from ui.forms.reports.utils.inventory_calculator import InventoryCalculator


class InventoryReportForm(QWidget):
    """فرم گزارش انبار کامل"""
    
    report_updated = Signal(dict)  # سیگنال بروزرسانی گزارش
    
    def __init__(self, data_manager):
        super().__init__()
        self.data_manager = data_manager
        self.inventory_calculator = InventoryCalculator(data_manager)
        self.inventory_data = {}
        
        # تنظیمات اولیه
        self.init_ui()
        
        # بارگذاری اولیه داده‌ها
        QTimer.singleShot(100, self.load_inventory_data)
    
    def init_ui(self):
        """ایجاد رابط کاربری فرم"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)
        
        # نوار ابزار فیلترها
        self.create_filter_toolbar(main_layout)
        
        # ایجاد ویجت تب‌ها برای بخش‌های مختلف
        self.create_tab_widget(main_layout)
        
        # نوار وضعیت
        self.create_status_bar(main_layout)
    
    def create_filter_toolbar(self, parent_layout):
        """ایجاد نوار ابزار فیلترهای گزارش انبار"""
        filter_frame = QFrame()
        filter_frame.setFrameStyle(QFrame.StyledPanel | QFrame.Raised)
        filter_frame.setStyleSheet("""
            QFrame {
                background-color: #1a1a2e;
                border-radius: 6px;
                padding: 10px;
            }
            QLabel {
                color: #ffffff;
                font-weight: bold;
            }
            QComboBox, QLineEdit, QDateEdit {
                background-color: #2c3e50;
                color: white;
                border: 1px solid #34495e;
                border-radius: 4px;
                padding: 5px;
                min-height: 30px;
            }
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 8px 15px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        
        filter_layout = QGridLayout(filter_frame)
        
        # انتخاب انبار
        filter_layout.addWidget(QLabel("🏪 انبار:"), 0, 0)
        self.warehouse_combo = QComboBox()
        self.warehouse_combo.addItems([
            "همه انبارها",
            "قطعات نو",
            "قطعات دست دوم",
            "لوازم نو",
            "لوازم دست دوم"
        ])
        self.warehouse_combo.currentIndexChanged.connect(self.on_warehouse_changed)
        filter_layout.addWidget(self.warehouse_combo, 0, 1)
        
        # تاریخ شروع
        filter_layout.addWidget(QLabel("از تاریخ:"), 0, 2)
        self.start_date_edit = QDateEdit()
        self.start_date_edit.setCalendarPopup(True)
        self.start_date_edit.setDate(QDate.currentDate().addDays(-30))
        filter_layout.addWidget(self.start_date_edit, 0, 3)
        
        # تاریخ پایان
        filter_layout.addWidget(QLabel("تا تاریخ:"), 0, 4)
        self.end_date_edit = QDateEdit()
        self.end_date_edit.setCalendarPopup(True)
        self.end_date_edit.setDate(QDate.currentDate())
        filter_layout.addWidget(self.end_date_edit, 0, 5)
        
        # دکمه اعمال فیلتر
        self.btn_apply_filter = QPushButton("✅ اعمال فیلتر")
        self.btn_apply_filter.clicked.connect(self.apply_filters)
        filter_layout.addWidget(self.btn_apply_filter, 0, 6)
        
        # دکمه بازنشانی
        self.btn_reset = QPushButton("🔄 بازنشانی")
        self.btn_reset.clicked.connect(self.reset_filters)
        filter_layout.addWidget(self.btn_reset, 0, 7)
        
        parent_layout.addWidget(filter_frame)
    
    def create_tab_widget(self, parent_layout):
        """ایجاد ویجت تب‌های مختلف"""
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabPosition(QTabWidget.North)
        
        # استایل تب‌ها
        self.tab_widget.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #444;
                background-color: #111;
                border-radius: 5px;
            }
            QTabBar::tab {
                background-color: #2c3e50;
                color: white;
                padding: 10px 20px;
                margin-right: 2px;
                border-top-left-radius: 5px;
                border-top-right-radius: 5px;
                font-weight: bold;
            }
            QTabBar::tab:selected {
                background-color: #3498db;
                color: white;
            }
            QTabBar::tab:hover:!selected {
                background-color: #34495e;
            }
        """)
        
        # ایجاد تب‌های مختلف
        self.create_summary_tab()
        self.create_movements_tab()
        self.create_alerts_tab()
        self.create_details_tab()
        
        parent_layout.addWidget(self.tab_widget, 1)
    
    def create_summary_tab(self):
        """ایجاد تب خلاصه انبارها"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # هدر تب
        header_label = QLabel("🏪 خلاصه وضعیت انبارها")
        header_label.setStyleSheet("""
            QLabel {
                color: #3498db;
                font-size: 16pt;
                font-weight: bold;
                padding: 10px;
                background-color: #1a1a2e;
                border-radius: 8px;
                text-align: center;
            }
        """)
        header_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(header_label)
        
        # کارت‌های خلاصه انبارها
        self.create_warehouse_cards(layout)
        
        # نمودار توزیع موجودی
        self.create_inventory_chart(layout)
        
        # کارت‌های آمار کلی
        self.create_overall_stats(layout)
        
        self.tab_widget.addTab(tab, "📊 خلاصه")
    
    def create_warehouse_cards(self, parent_layout):
        """ایجاد کارت‌های خلاصه برای هر انبار"""
        cards_frame = QFrame()
        cards_layout = QGridLayout(cards_frame)
        cards_layout.setSpacing(15)
        
        # کارت قطعات نو
        self.new_parts_card = self.create_warehouse_card(
            "📦 قطعات نو", 
            "۰ عدد", 
            "۰ تومان", 
            "#3498db"
        )
        cards_layout.addWidget(self.new_parts_card, 0, 0)
        
        # کارت قطعات دست دوم
        self.used_parts_card = self.create_warehouse_card(
            "🔧 قطعات دست دوم", 
            "۰ عدد", 
            "۰ تومان", 
            "#2ecc71"
        )
        cards_layout.addWidget(self.used_parts_card, 0, 1)
        
        # کارت لوازم نو
        self.new_appliances_card = self.create_warehouse_card(
            "🏠 لوازم نو", 
            "۰ عدد", 
            "۰ تومان", 
            "#e74c3c"
        )
        cards_layout.addWidget(self.new_appliances_card, 1, 0)
        
        # کارت لوازم دست دوم
        self.used_appliances_card = self.create_warehouse_card(
            "🔄 لوازم دست دوم", 
            "۰ عدد", 
            "۰ تومان", 
            "#f39c12"
        )
        cards_layout.addWidget(self.used_appliances_card, 1, 1)
        
        parent_layout.addWidget(cards_frame)
    
    def create_warehouse_card(self, title, item_count, total_value, color):
        """ایجاد یک کارت انبار"""
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background-color: {color}20;
                border: 2px solid {color};
                border-radius: 10px;
                padding: 15px;
            }}
        """)
        
        layout = QVBoxLayout(card)
        
        # عنوان
        title_label = QLabel(title)
        title_label.setStyleSheet(f"""
            QLabel {{
                color: {color};
                font-size: 12pt;
                font-weight: bold;
                text-align: center;
            }}
        """)
        layout.addWidget(title_label)
        
        # تعداد آیتم‌ها
        count_label = QLabel(f"📊 تعداد: {item_count}")
        count_label.setStyleSheet("""
            QLabel {
                color: #ffffff;
                font-size: 11pt;
                text-align: center;
                padding: 5px 0;
            }
        """)
        layout.addWidget(count_label)
        
        # ارزش کل
        value_label = QLabel(f"💰 ارزش: {total_value}")
        value_label.setStyleSheet("""
            QLabel {
                color: #ffffff;
                font-size: 11pt;
                text-align: center;
                padding: 5px 0;
            }
        """)
        layout.addWidget(value_label)
        
        # نوار پیشرفت موجودی
        self.create_inventory_progress_bar(layout, color)
        
        return card
    
    def create_inventory_progress_bar(self, parent_layout, color):
        """ایجاد نوار پیشرفت برای نمایش سطح موجودی"""
        progress_frame = QFrame()
        progress_layout = QVBoxLayout(progress_frame)
        
        # برچسب درصد
        percent_label = QLabel("سطح موجودی: ۰٪")
        percent_label.setStyleSheet(f"""
            QLabel {{
                color: {color};
                font-size: 9pt;
                text-align: center;
            }}
        """)
        progress_layout.addWidget(percent_label)
        
        # نوار پیشرفت
        progress_bar = QProgressBar()
        progress_bar.setRange(0, 100)
        progress_bar.setValue(0)
        progress_bar.setTextVisible(False)
        progress_bar.setStyleSheet(f"""
            QProgressBar {{
                border: 1px solid {color};
                border-radius: 5px;
                background-color: #2c3e50;
                height: 10px;
            }}
            QProgressBar::chunk {{
                background-color: {color};
                border-radius: 4px;
            }}
        """)
        progress_layout.addWidget(progress_bar)
        
        parent_layout.addWidget(progress_frame)
    
    def create_inventory_chart(self, parent_layout):
        """ایجاد نمودار توزیع موجودی"""
        group = QGroupBox("📈 توزیع موجودی بین انبارها")
        group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #3498db;
                border-radius: 8px;
                margin-top: 15px;
                padding-top: 15px;
                color: #3498db;
                font-size: 12pt;
            }
        """)
        
        layout = QVBoxLayout(group)
        
        # نمودار دایره‌ای
        self.inventory_chart_view = QChartView()
        self.inventory_chart_view.setRenderHint(QPainter.Antialiasing)
        self.inventory_chart_view.setMinimumHeight(300)
        self.inventory_chart_view.setStyleSheet("""
            QChartView {
                background-color: #111111;
                border-radius: 8px;
                border: 1px solid #444;
            }
        """)
        
        layout.addWidget(self.inventory_chart_view)
        parent_layout.addWidget(group)
    
    def create_overall_stats(self, parent_layout):
        """ایجاد کارت‌های آمار کلی"""
        stats_frame = QFrame()
        stats_layout = QGridLayout(stats_frame)
        stats_layout.setSpacing(10)
        
        # کل آیتم‌ها
        self.total_items_card = self.create_stat_card(
            "📦 کل آیتم‌ها",
            "۰ عدد",
            "#9b59b6"
        )
        stats_layout.addWidget(self.total_items_card, 0, 0)
        
        # کل ارزش
        self.total_value_card = self.create_stat_card(
            "💰 کل ارزش",
            "۰ تومان",
            "#2ecc71"
        )
        stats_layout.addWidget(self.total_value_card, 0, 1)
        
        # نرخ موجودی
        self.availability_card = self.create_stat_card(
            "📊 نرخ موجودی",
            "۰٪",
            "#3498db"
        )
        stats_layout.addWidget(self.availability_card, 0, 2)
        
        # هشدارهای موجودی کم
        self.alerts_card = self.create_stat_card(
            "⚠️ هشدارها",
            "۰ مورد",
            "#e74c3c"
        )
        stats_layout.addWidget(self.alerts_card, 0, 3)
        
        parent_layout.addWidget(stats_frame)
    
    def create_stat_card(self, title, value, color):
        """ایجاد کارت آمار"""
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background-color: {color}15;
                border: 1px solid {color};
                border-radius: 8px;
                padding: 10px;
            }}
        """)
        
        layout = QVBoxLayout(card)
        
        # عنوان
        title_label = QLabel(title)
        title_label.setStyleSheet(f"""
            QLabel {{
                color: {color};
                font-size: 10pt;
                font-weight: bold;
                text-align: center;
            }}
        """)
        layout.addWidget(title_label)
        
        # مقدار
        value_label = QLabel(value)
        value_label.setStyleSheet("""
            QLabel {
                color: #ffffff;
                font-size: 12pt;
                font-weight: bold;
                text-align: center;
                padding: 5px 0;
            }
        """)
        layout.addWidget(value_label)
        
        return card
    
    def create_movements_tab(self):
        """ایجاد تب حرکات انبار"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # هدر تب
        header_label = QLabel("📋 حرکات انبار")
        header_label.setStyleSheet("""
            QLabel {
                color: #2ecc71;
                font-size: 16pt;
                font-weight: bold;
                padding: 10px;
                background-color: #1a1a2e;
                border-radius: 8px;
                text-align: center;
            }
        """)
        header_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(header_label)
        
        # ایجاد جدول حرکات
        self.create_movements_table(layout)
        
        self.tab_widget.addTab(tab, "📋 حرکات")
    
    def create_movements_table(self, parent_layout):
        """ایجاد جدول حرکات انبار"""
        group = QGroupBox("📊 تاریخچه حرکات انبار")
        group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #2ecc71;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 15px;
                color: #2ecc71;
                font-size: 12pt;
            }
        """)
        
        layout = QVBoxLayout(group)
        
        # ایجاد جدول
        self.movements_table = QTableWidget(20, 7)
        
        # تنظیم ارتفاع ردیف‌ها
        for i in range(20):
            self.movements_table.setRowHeight(i, 35)
        
        self.movements_table.setStyleSheet("""
            QTableWidget {
                background-color: #111111;
                alternate-background-color: #0a0a0a;
                gridline-color: #333333;
                color: #ffffff;
                font-size: 10pt;
                font-family: 'B Nazanin';
            }
            QTableWidget::item {
                padding: 8px;
            }
            QTableWidget::item:selected {
                background-color: #3498db;
                color: white;
            }
            QHeaderView::section {
                background-color: #2c3e50;
                color: white;
                padding: 10px;
                border: none;
                font-weight: bold;
                font-size: 11pt;
                font-family: 'B Nazanin';
            }
        """)
        
        # تنظیم هدرهای جدول
        headers = ["تاریخ", "نوع انبار", "نوع حرکت", "آیتم", "تعداد", "مبلغ کل", "شرح"]
        self.movements_table.setHorizontalHeaderLabels(headers)
        
        # تنظیمات ستون‌ها
        header = self.movements_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # تاریخ
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)  # نوع انبار
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)  # نوع حرکت
        header.setSectionResizeMode(3, QHeaderView.Stretch)           # آیتم
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)  # تعداد
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)  # مبلغ کل
        header.setSectionResizeMode(6, QHeaderView.ResizeToContents)  # شرح
        
        layout.addWidget(self.movements_table)
        parent_layout.addWidget(group)
    
    def create_alerts_tab(self):
        """ایجاد تب هشدارهای موجودی کم"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # هدر تب
        header_label = QLabel("⚠️ هشدارهای موجودی کم")
        header_label.setStyleSheet("""
            QLabel {
                color: #e74c3c;
                font-size: 16pt;
                font-weight: bold;
                padding: 10px;
                background-color: #1a1a2e;
                border-radius: 8px;
                text-align: center;
            }
        """)
        header_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(header_label)
        
        # ایجاد جدول هشدارها
        self.create_alerts_table(layout)
        
        self.tab_widget.addTab(tab, "⚠️ هشدارها")
    
    def create_alerts_table(self, parent_layout):
        """ایجاد جدول هشدارهای موجودی کم"""
        group = QGroupBox("📊 آیتم‌های با موجودی کم یا صفر")
        group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #e74c3c;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 15px;
                color: #e74c3c;
                font-size: 12pt;
            }
        """)
        
        layout = QVBoxLayout(group)
        
        # ایجاد جدول
        self.alerts_table = QTableWidget(15, 6)
        
        # تنظیم ارتفاع ردیف‌ها
        for i in range(15):
            self.alerts_table.setRowHeight(i, 40)
        
        self.alerts_table.setStyleSheet("""
            QTableWidget {
                background-color: #111111;
                alternate-background-color: #0a0a0a;
                gridline-color: #333333;
                color: #ffffff;
                font-size: 10pt;
                font-family: 'B Nazanin';
            }
            QTableWidget::item {
                padding: 10px;
            }
            QTableWidget::item:selected {
                background-color: #e74c3c;
                color: white;
            }
            QHeaderView::section {
                background-color: #2c3e50;
                color: white;
                padding: 12px;
                border: none;
                font-weight: bold;
                font-size: 11pt;
                font-family: 'B Nazanin';
            }
        """)
        
        # تنظیم هدرهای جدول
        headers = ["انبار", "نام آیتم", "کد", "موجودی فعلی", "حداقل موجودی", "محل"]
        self.alerts_table.setHorizontalHeaderLabels(headers)
        
        # تنظیمات ستون‌ها
        header = self.alerts_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # انبار
        header.setSectionResizeMode(1, QHeaderView.Stretch)           # نام آیتم
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)  # کد
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)  # موجودی فعلی
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)  # حداقل موجودی
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)  # محل
        
        layout.addWidget(self.alerts_table)
        parent_layout.addWidget(group)
    
    def create_details_tab(self):
        """ایجاد تب جزئیات انبارها"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # هدر تب
        header_label = QLabel("📋 جزئیات هر انبار")
        header_label.setStyleSheet("""
            QLabel {
                color: #f39c12;
                font-size: 16pt;
                font-weight: bold;
                padding: 10px;
                background-color: #1a1a2e;
                border-radius: 8px;
                text-align: center;
            }
        """)
        header_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(header_label)
        
        # انتخاب انبار برای جزئیات
        self.create_warehouse_selection(layout)
        
        # جدول جزئیات
        self.create_details_table(layout)
        
        self.tab_widget.addTab(tab, "📋 جزئیات")
    
    def create_warehouse_selection(self, parent_layout):
        """ایجاد انتخاب‌گر انبار برای نمایش جزئیات"""
        selection_frame = QFrame()
        selection_layout = QHBoxLayout(selection_frame)
        
        selection_layout.addWidget(QLabel("انتخاب انبار برای نمایش جزئیات:"))
        
        self.details_warehouse_combo = QComboBox()
        self.details_warehouse_combo.addItems([
            "قطعات نو",
            "قطعات دست دوم",
            "لوازم نو",
            "لوازم دست دوم"
        ])
        self.details_warehouse_combo.currentIndexChanged.connect(self.load_warehouse_details)
        selection_layout.addWidget(self.details_warehouse_combo)
        
        # دکمه بازنشانی
        btn_refresh = QPushButton("🔄 بروزرسانی")
        btn_refresh.clicked.connect(self.load_warehouse_details)
        selection_layout.addWidget(btn_refresh)
        
        selection_layout.addStretch()
        parent_layout.addWidget(selection_frame)
    
    def create_details_table(self, parent_layout):
        """ایجاد جدول جزئیات انبار"""
        group = QGroupBox("📊 لیست آیتم‌های موجود در انبار")
        group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #f39c12;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 15px;
                color: #f39c12;
                font-size: 12pt;
            }
        """)
        
        layout = QVBoxLayout(group)
        
        # ایجاد جدول
        self.details_table = QTableWidget(20, 8)
        
        # تنظیم ارتفاع ردیف‌ها
        for i in range(20):
            self.details_table.setRowHeight(i, 40)
        
        self.details_table.setStyleSheet("""
            QTableWidget {
                background-color: #111111;
                alternate-background-color: #0a0a0a;
                gridline-color: #333333;
                color: #ffffff;
                font-size: 10pt;
                font-family: 'B Nazanin';
            }
            QTableWidget::item {
                padding: 10px;
            }
            QTableWidget::item:selected {
                background-color: #f39c12;
                color: white;
            }
            QHeaderView::section {
                background-color: #2c3e50;
                color: white;
                padding: 12px;
                border: none;
                font-weight: bold;
                font-size: 11pt;
                font-family: 'B Nazanin';
            }
        """)
        
        # تنظیم هدرهای جدول (عمومی - بر اساس انبار تغییر می‌کنند)
        headers = ["کد", "نام", "دسته", "برند", "موجودی", "قیمت خرید", "قیمت فروش", "محل"]
        self.details_table.setHorizontalHeaderLabels(headers)
        
        # تنظیمات ستون‌ها
        header = self.details_table.horizontalHeader()
        for i in range(8):
            header.setSectionResizeMode(i, QHeaderView.ResizeToContents)
        
        layout.addWidget(self.details_table)
        parent_layout.addWidget(group)
    
    def create_status_bar(self, parent_layout):
        """ایجاد نوار وضعیت پایین فرم"""
        status_frame = QFrame()
        status_frame.setFrameStyle(QFrame.StyledPanel | QFrame.Sunken)
        status_frame.setStyleSheet("""
            QFrame {
                background-color: #2c3e50;
                border-radius: 3px;
                padding: 5px;
            }
            QLabel {
                color: #ecf0f1;
                font-size: 9pt;
            }
        """)
        
        status_layout = QHBoxLayout(status_frame)
        
        # وضعیت سیستم
        self.status_label = QLabel("✅ در حال بارگذاری داده‌های انبار...")
        
        # تعداد آیتم‌ها
        self.items_count_label = QLabel("تعداد کل آیتم‌ها: ۰")
        
        # آخرین بروزرسانی
        self.last_update_label = QLabel("آخرین بروزرسانی: --:--")
        
        status_layout.addWidget(self.status_label, 5)
        status_layout.addWidget(self.items_count_label, 3)
        status_layout.addWidget(self.last_update_label, 3)
        
        parent_layout.addWidget(status_frame)
    
    def on_warehouse_changed(self, index):
        """رویداد تغییر انبار"""
        # غیرفعال کردن انتخاب تاریخ برای "همه انبارها"
        is_all_warehouses = (index == 0)
        self.start_date_edit.setEnabled(not is_all_warehouses)
        self.end_date_edit.setEnabled(not is_all_warehouses)
    
    def apply_filters(self):
        """اعمال فیلترهای انتخاب شده"""
        self.status_label.setText("🔄 در حال اعمال فیلترها...")
        QTimer.singleShot(100, self.load_inventory_data)
    
    def reset_filters(self):
        """بازنشانی فیلترها"""
        self.warehouse_combo.setCurrentIndex(0)  # همه انبارها
        self.start_date_edit.setDate(QDate.currentDate().addDays(-30))
        self.end_date_edit.setDate(QDate.currentDate())
        self.apply_filters()
    
    def load_inventory_data(self):
        """بارگذاری داده‌های انبار"""
        try:
            self.status_label.setText("📊 در حال دریافت داده‌های انبار از دیتابیس...")
            
            # ۱. دریافت خلاصه انبارها
            self.inventory_data = self.inventory_calculator.get_inventory_summary()
            
            # ۲. دریافت حرکات انبار
            start_date = self.start_date_edit.date().toString("yyyy-MM-dd")
            end_date = self.end_date_edit.date().toString("yyyy-MM-dd")
            self.movements_list = self.inventory_calculator.get_inventory_movements(start_date, end_date)
            
            # ۳. دریافت هشدارها
            self.alerts_list = self.inventory_calculator.get_low_stock_alerts()
            
            # ۴. به‌روزرسانی UI
            self.update_warehouse_summary()
            self.update_movements_table()
            self.update_alerts_table()
            self.update_inventory_chart()
            
            # ۵. بارگذاری جزئیات انبار پیش‌فرض
            self.load_warehouse_details()
            
            self.status_label.setText("✅ داده‌های انبار با موفقیت بارگذاری شدند")
            self.items_count_label.setText(f"تعداد کل آیتم‌ها: {self.inventory_data.get('total_items', 0)}")
            self.last_update_label.setText(f"آخرین بروزرسانی: {get_current_jalali()}")
            
            # ارسال سیگنال بروزرسانی
            self.report_updated.emit(self.inventory_data)
            
        except Exception as e:
            self.status_label.setText(f"❌ خطا در بارگذاری داده‌ها: {str(e)}")
            print(f"خطا در load_inventory_data: {e}")
            # در صورت خطا، از داده‌های نمونه استفاده کن
            self.load_sample_inventory_data()
    
    def load_sample_inventory_data(self):
        """بارگذاری داده‌های نمونه انبار (در صورت خطا)"""
        self.inventory_data = {
            'warehouses': {
                'قطعات نو': {
                    'total_items': 45,
                    'available_items': 38,
                    'total_value': 12500000,
                    'available_value': 10500000,
                    'availability_rate': 84.4
                },
                'قطعات دست دوم': {
                    'total_items': 28,
                    'available_items': 22,
                    'total_value': 8500000,
                    'available_value': 6800000,
                    'availability_rate': 78.6
                },
                'لوازم نو': {
                    'total_items': 12,
                    'available_items': 9,
                    'total_value': 45000000,
                    'available_value': 38000000,
                    'availability_rate': 75.0
                },
                'لوازم دست دوم': {
                    'total_items': 18,
                    'available_items': 15,
                    'total_value': 32000000,
                    'available_value': 28000000,
                    'availability_rate': 83.3
                }
            },
            'total_items': 103,
            'total_value': 98000000,
            'low_stock_alerts': [
                {'type': 'قطعات نو', 'item_name': 'کمپرسور یخچال', 'current_stock': 2, 'min_stock': 5, 'severity': 'high'},
                {'type': 'قطعات نو', 'item_name': 'برد مایکروویو', 'current_stock': 3, 'min_stock': 5, 'severity': 'medium'},
                {'type': 'لوازم نو', 'item_name': 'جاروبرقی', 'current_stock': 1, 'min_stock': 3, 'severity': 'high'}
            ]
        }
    
    def update_warehouse_summary(self):
        """به‌روزرسانی خلاصه انبارها"""
        warehouses = self.inventory_data.get('warehouses', {})
        
        # به‌روزرسانی کارت‌های انبار
        for warehouse_type, stats in warehouses.items():
            if warehouse_type == 'قطعات نو':
                self.update_warehouse_card(
                    self.new_parts_card,
                    f"{stats.get('available_items', 0)} از {stats.get('total_items', 0)} عدد",
                    f"{self.format_currency(stats.get('available_value', 0) / 10)} تومان",
                    stats.get('availability_rate', 0)
                )
            elif warehouse_type == 'قطعات دست دوم':
                self.update_warehouse_card(
                    self.used_parts_card,
                    f"{stats.get('available_items', 0)} از {stats.get('total_items', 0)} عدد",
                    f"{self.format_currency(stats.get('available_value', 0) / 10)} تومان",
                    stats.get('availability_rate', 0)
                )
            elif warehouse_type == 'لوازم نو':
                self.update_warehouse_card(
                    self.new_appliances_card,
                    f"{stats.get('available_items', 0)} از {stats.get('total_items', 0)} عدد",
                    f"{self.format_currency(stats.get('available_value', 0) / 10)} تومان",
                    stats.get('availability_rate', 0)
                )
            elif warehouse_type == 'لوازم دست دوم':
                self.update_warehouse_card(
                    self.used_appliances_card,
                    f"{stats.get('available_items', 0)} از {stats.get('total_items', 0)} عدد",
                    f"{self.format_currency(stats.get('available_value', 0) / 10)} تومان",
                    stats.get('availability_rate', 0)
                )
        
        # به‌روزرسانی کارت‌های آمار کلی
        self.update_stat_card(self.total_items_card, f"{self.inventory_data.get('total_items', 0)} عدد")
        self.update_stat_card(self.total_value_card, f"{self.format_currency(self.inventory_data.get('total_value', 0) / 10)} تومان")
        
        # محاسبه میانگین نرخ موجودی
        total_rate = 0
        count = 0
        for stats in warehouses.values():
            total_rate += stats.get('availability_rate', 0)
            count += 1
        
        avg_rate = total_rate / count if count > 0 else 0
        self.update_stat_card(self.availability_card, f"{avg_rate:.1f}٪")
        
        # تعداد هشدارها
        alert_count = len(self.inventory_data.get('low_stock_alerts', []))
        self.update_stat_card(self.alerts_card, f"{alert_count} مورد")
    
    def update_warehouse_card(self, card, item_count, total_value, availability_rate):
        """به‌روزرسانی متن یک کارت انبار"""
        # کارت شامل یک QVBoxLayout است
        layout = card.layout()
        if layout and layout.count() >= 3:
            # بروزرسانی تعداد
            count_label = layout.itemAt(1).widget()  # موقعیت دوم = تعداد
            if count_label:
                count_label.setText(f"📊 تعداد: {item_count}")
            
            # بروزرسانی ارزش
            value_label = layout.itemAt(2).widget()  # موقعیت سوم = ارزش
            if value_label:
                value_label.setText(f"💰 ارزش: {total_value}")
            
            # بروزرسانی نوار پیشرفت
            if layout.count() >= 4:
                progress_frame = layout.itemAt(3).widget()
                if progress_frame:
                    progress_layout = progress_frame.layout()
                    if progress_layout and progress_layout.count() >= 2:
                        # بروزرسانی درصد
                        percent_label = progress_layout.itemAt(0).widget()
                        if percent_label:
                            percent_label.setText(f"سطح موجودی: {availability_rate:.1f}٪")
                        
                        # بروزرسانی نوار پیشرفت
                        progress_bar = progress_layout.itemAt(1).widget()
                        if progress_bar:
                            progress_bar.setValue(int(availability_rate))
    
    def update_stat_card(self, card, new_value):
        """به‌روزرسانی کارت آمار"""
        layout = card.layout()
        if layout and layout.count() >= 2:
            value_label = layout.itemAt(1).widget()  # موقعیت دوم = مقدار
            if value_label:
                value_label.setText(new_value)
    
    def update_movements_table(self):
        """به‌روزرسانی جدول حرکات انبار"""
        if not hasattr(self, 'movements_list') or not self.movements_list:
            print("⚠️ لیست حرکات انبار خالی است")
            return
        
        row_count = len(self.movements_list)
        self.movements_table.setRowCount(row_count)
        
        for row, movement in enumerate(self.movements_list):
            # تاریخ
            date_shamsi = movement.get('transaction_date_shamsi', '')
            
            # نوع انبار
            warehouse_type = movement.get('warehouse_type', '')
            
            # نوع حرکت
            transaction_type = movement.get('transaction_type', '')
            
            # نام آیتم
            item_name = movement.get('item_name', '')[:30] + "..." if len(movement.get('item_name', '')) > 30 else movement.get('item_name', '')
            
            # تعداد
            quantity = movement.get('quantity', 0)
            
            # مبلغ کل (تبدیل از ریال به تومان)
            total_price = movement.get('total_price', 0) / 10
            total_formatted = f"{self.format_currency(total_price)} تومان"
            
            # شرح
            description = movement.get('description', '')[:40] + "..." if len(movement.get('description', '')) > 40 else movement.get('description', '')
            
            # قرار دادن در جدول
            items = [
                date_shamsi,
                warehouse_type,
                transaction_type,
                item_name,
                str(quantity),
                total_formatted,
                description
            ]
            
            for col, text in enumerate(items):
                item = QTableWidgetItem(str(text))
                item.setTextAlignment(Qt.AlignCenter)
                
                # رنگ‌بندی نوع حرکت
                if col == 2:  # ستون نوع حرکت
                    if transaction_type in ['خرید', 'دریافت']:
                        item.setForeground(QColor("#2ecc71"))
                        item.setToolTip("ورود به انبار")
                    elif transaction_type in ['فروش', 'استفاده در تعمیر']:
                        item.setForeground(QColor("#e74c3c"))
                        item.setToolTip("خروج از انبار")
                    elif transaction_type in ['تعدیل', 'برگشت']:
                        item.setForeground(QColor("#f39c12"))
                        item.setToolTip("تعدیل موجودی")
                    else:
                        item.setForeground(QColor("#3498db"))
                
                # رنگ‌بندی نوع انبار
                elif col == 1:  # ستون نوع انبار
                    if warehouse_type == 'قطعات نو':
                        item.setForeground(QColor("#3498db"))
                    elif warehouse_type == 'قطعات دست دوم':
                        item.setForeground(QColor("#2ecc71"))
                    elif warehouse_type == 'لوازم نو':
                        item.setForeground(QColor("#e74c3c"))
                    elif warehouse_type == 'لوازم دست دوم':
                        item.setForeground(QColor("#f39c12"))
                
                self.movements_table.setItem(row, col, item)
        
        # پنهان کردن ردیف‌های خالی
        for row in range(row_count, 20):
            self.movements_table.hideRow(row)
        
        print(f"✅ جدول حرکات با {row_count} ردیف بروزرسانی شد")
    
    def update_alerts_table(self):
        """به‌روزرسانی جدول هشدارها"""
        alerts = self.inventory_data.get('low_stock_alerts', [])
        
        row_count = len(alerts)
        self.alerts_table.setRowCount(row_count)
        
        for row, alert in enumerate(alerts):
            # انبار
            alert_type = alert.get('type', '')
            
            # نام آیتم
            item_name = alert.get('item_name', '')
            
            # کد (ساختی)
            item_code = f"ALT-{row + 1:03d}"
            
            # موجودی فعلی
            current_stock = alert.get('current_stock', 0)
            
            # حداقل موجودی
            min_stock = alert.get('min_stock', 0)
            
            # محل
            location = alert.get('location', 'نامشخص')
            
            # قرار دادن در جدول
            items = [
                alert_type,
                item_name,
                item_code,
                str(current_stock),
                str(min_stock),
                location
            ]
            
            for col, text in enumerate(items):
                item = QTableWidgetItem(str(text))
                item.setTextAlignment(Qt.AlignCenter)
                
                # رنگ‌بندی بر اساس شدت هشدار
                if col == 3:  # ستون موجودی فعلی
                    severity = alert.get('severity', 'medium')
                    if severity == 'high' or current_stock == 0:
                        item.setForeground(QColor("#e74c3c"))
                        item.setToolTip("موجودی بحرانی - نیاز به سفارش فوری")
                    elif severity == 'medium':
                        item.setForeground(QColor("#f39c12"))
                        item.setToolTip("موجودی کم - نیاز به سفارش")
                    else:
                        item.setForeground(QColor("#2ecc71"))
                
                self.alerts_table.setItem(row, col, item)
        
        # پنهان کردن ردیف‌های خالی
        for row in range(row_count, 15):
            self.alerts_table.hideRow(row)
    
    def load_warehouse_details(self):
        """بارگذاری جزئیات انبار انتخاب شده"""
        try:
            # دریافت انبار انتخاب شده
            warehouse_type = self.details_warehouse_combo.currentText()
            
            # دریافت جزئیات از دیتابیس
            details = self.inventory_calculator.get_warehouse_details(warehouse_type)
            
            # به‌روزرسانی جدول
            self.update_details_table(details, warehouse_type)
            
        except Exception as e:
            print(f"❌ خطا در بارگذاری جزئیات انبار: {e}")
    
    def update_details_table(self, details, warehouse_type):
        """به‌روزرسانی جدول جزئیات"""
        if not details:
            print(f"⚠️ جزئیات انبار {warehouse_type} خالی است")
            return
        
        row_count = len(details)
        self.details_table.setRowCount(row_count)
        
        for row, item in enumerate(details):
            # بر اساس نوع انبار، ستون‌ها متفاوت هستند
            if warehouse_type == 'قطعات نو' or warehouse_type == 'قطعات دست دوم':
                # کد قطعه
                part_code = item.get('part_code', '')
                
                # نام قطعه
                part_name = item.get('part_name', '')
                
                # دسته
                category = item.get('category', '')
                
                # برند
                brand = item.get('brand', '')
                
                # موجودی
                quantity = item.get('quantity', 0)
                
                # قیمت خرید (تبدیل از ریال به تومان)
                purchase_price = item.get('purchase_price', 0) / 10
                purchase_formatted = f"{self.format_currency(purchase_price)} تومان"
                
                # قیمت فروش (تبدیل از ریال به تومان)
                sale_price = item.get('sale_price', 0) / 10
                sale_formatted = f"{self.format_currency(sale_price)} تومان"
                
                # محل
                location = item.get('location', '')
                
                items = [
                    part_code,
                    part_name,
                    category,
                    brand,
                    str(quantity),
                    purchase_formatted,
                    sale_formatted,
                    location
                ]
                
            elif warehouse_type == 'لوازم نو' or warehouse_type == 'لوازم دست دوم':
                # کد (سریال یا مدل)
                serial_number = item.get('serial_number', '') or item.get('model', '')
                
                # مدل
                model = item.get('model', '')
                
                # نوع دستگاه
                device_type = item.get('device_type_name', '')
                
                # برند
                brand = item.get('brand_name', '')
                
                # موجودی
                quantity = item.get('quantity', 0)
                
                # قیمت خرید (تبدیل از ریال به تومان)
                purchase_price = item.get('purchase_price', 0) / 10
                purchase_formatted = f"{self.format_currency(purchase_price)} تومان"
                
                # قیمت فروش (تبدیل از ریال به تومان)
                sale_price = item.get('sale_price', 0) / 10
                sale_formatted = f"{self.format_currency(sale_price)} تومان"
                
                # محل
                location = item.get('location', '')
                
                items = [
                    serial_number,
                    model,
                    device_type,
                    brand,
                    str(quantity),
                    purchase_formatted,
                    sale_formatted,
                    location
                ]
            
            for col, text in enumerate(items):
                item_widget = QTableWidgetItem(str(text))
                item_widget.setTextAlignment(Qt.AlignCenter)
                
                # رنگ‌بندی موجودی
                if col == 4:  # ستون موجودی
                    if quantity <= 0:
                        item_widget.setForeground(QColor("#e74c3c"))
                    elif quantity <= 5:
                        item_widget.setForeground(QColor("#f39c12"))
                    else:
                        item_widget.setForeground(QColor("#2ecc71"))
                
                self.details_table.setItem(row, col, item_widget)
        
        # پنهان کردن ردیف‌های خالی
        for row in range(row_count, 20):
            self.details_table.hideRow(row)
    
    def update_inventory_chart(self):
        """به‌روزرسانی نمودار توزیع موجودی"""
        try:
            warehouses = self.inventory_data.get('warehouses', {})
            
            chart = QChart()
            chart.setTitle("📊 توزیع موجودی بین انبارها")
            chart.setTitleFont(QFont("B Nazanin", 12, QFont.Bold))
            chart.setAnimationOptions(QChart.SeriesAnimations)
            
            # سری دایره‌ای
            pie_series = QPieSeries()
            pie_series.setPieSize(0.7)
            
            # رنگ‌های مختلف برای انبارها
            colors = {
                'قطعات نو': QColor("#3498db"),
                'قطعات دست دوم': QColor("#2ecc71"),
                'لوازم نو': QColor("#e74c3c"),
                'لوازم دست دوم': QColor("#f39c12")
            }
            
            # اضافه کردن بخش‌ها
            total_value = self.inventory_data.get('total_value', 0)
            
            for warehouse_type, stats in warehouses.items():
                value = stats.get('available_value', 0)
                percentage = (value / total_value * 100) if total_value > 0 else 0
                
                if value > 0:
                    slice = pie_series.append(
                        f"{warehouse_type}\n{self.format_currency(value / 10)} تومان ({percentage:.1f}%)", 
                        value
                    )
                    slice.setColor(colors.get(warehouse_type, QColor("#95a5a6")))
                    
                    # نمایش مقدار روی برش
                    slice.setLabelVisible(True)
                    slice.setLabelPosition(QPieSlice.LabelInsideNormal)
                    slice.setLabelBrush(QColor("#FFFFFF"))
            
            chart.addSeries(pie_series)
            chart.legend().setVisible(True)
            chart.legend().setAlignment(Qt.AlignRight)
            
            self.inventory_chart_view.setChart(chart)
            
        except Exception as e:
            print(f"⚠️ خطا در ایجاد نمودار توزیع موجودی: {e}")
    
    def format_currency(self, amount):
        """فرمت کردن مبلغ به صورت جداکننده هزارگان"""
        return f"{amount:,.0f}".replace(",", "٬")