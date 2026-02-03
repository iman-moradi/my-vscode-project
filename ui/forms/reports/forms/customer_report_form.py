# ui/forms/reports/forms/customer_report_form.py
"""
فرم گزارش مشتریان
"""

from PySide6.QtWidgets import *
from PySide6.QtCore import Qt, Signal, QDate, QTimer
from PySide6.QtGui import QFont, QColor, QPainter
from utils.jalali_date_widget import get_current_jalali, gregorian_to_jalali
from PySide6.QtCharts import QChart, QChartView, QPieSeries, QBarSeries, QBarSet, QLineSeries
from PySide6.QtCharts import QValueAxis, QBarCategoryAxis


class CustomerReportForm(QWidget):
    """فرم گزارش مشتریان"""
    
    report_updated = Signal(dict)
    
    def __init__(self, data_manager):
        super().__init__()
        self.data_manager = data_manager
        self.customer_data = {}
        
        self.setup_ui()
        self.load_customer_data()
    
    def setup_ui(self):
        """تنظیم رابط کاربری"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)
        
        # نوار ابزار
        self.create_toolbar(main_layout)
        
        # فیلترها
        self.create_filters(main_layout)
        
        # ویجت تب‌ها
        self.create_tab_widget(main_layout)
        
        # نوار وضعیت
        self.create_status_bar(main_layout)
    
    def create_toolbar(self, parent_layout):
        """ایجاد نوار ابزار"""
        toolbar_frame = QFrame()
        toolbar_frame.setStyleSheet("""
            QFrame {
                background-color: #1a1a2e;
                border-radius: 6px;
                padding: 8px;
            }
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 8px 15px;
                border-radius: 4px;
                font-weight: bold;
                font-family: 'B Nazanin';
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        
        layout = QHBoxLayout(toolbar_frame)
        
        # دکمه‌ها
        btn_refresh = QPushButton("🔄 بروزرسانی")
        btn_refresh.clicked.connect(self.load_customer_data)
        
        btn_export = QPushButton("📊 خروجی Excel")
        btn_export.clicked.connect(self.export_to_excel)
        
        layout.addWidget(btn_refresh)
        layout.addWidget(btn_export)
        layout.addStretch()
        
        parent_layout.addWidget(toolbar_frame)
    
    def create_filters(self, parent_layout):
        """ایجاد فیلترها"""
        filter_frame = QFrame()
        filter_frame.setStyleSheet("""
            QFrame {
                background-color: #2c3e50;
                border-radius: 6px;
                padding: 10px;
            }
            QLabel {
                color: #ecf0f1;
                font-weight: bold;
            }
            QComboBox, QDateEdit {
                background-color: #34495e;
                color: white;
                border: 1px solid #4a6278;
                border-radius: 4px;
                padding: 5px;
                font-family: 'B Nazanin';
            }
        """)
        
        layout = QGridLayout(filter_frame)
        
        # دوره زمانی
        layout.addWidget(QLabel("دوره زمانی:"), 0, 0)
        self.period_combo = QComboBox()
        self.period_combo.addItems([
            "امروز",
            "دیروز",
            "هفته جاری",
            "ماه جاری",
            "۳ ماه اخیر",
            "۶ ماه اخیر",
            "سال جاری",
            "بازه دلخواه"
        ])
        self.period_combo.currentIndexChanged.connect(self.on_period_changed)
        layout.addWidget(self.period_combo, 0, 1)
        
        # تاریخ شروع
        layout.addWidget(QLabel("از تاریخ:"), 0, 2)
        self.start_date_edit = QDateEdit()
        self.start_date_edit.setCalendarPopup(True)
        self.start_date_edit.setDate(QDate.currentDate().addDays(-30))
        self.start_date_edit.setDisplayFormat("yyyy-MM-dd")
        layout.addWidget(self.start_date_edit, 0, 3)
        
        # تاریخ پایان
        layout.addWidget(QLabel("تا تاریخ:"), 0, 4)
        self.end_date_edit = QDateEdit()
        self.end_date_edit.setCalendarPopup(True)
        self.end_date_edit.setDate(QDate.currentDate())
        self.end_date_edit.setDisplayFormat("yyyy-MM-dd")
        layout.addWidget(self.end_date_edit, 0, 5)
        
        # نوع مشتری
        layout.addWidget(QLabel("نوع مشتری:"), 1, 0)
        self.type_combo = QComboBox()
        self.type_combo.addItems([
            "همه",
            "مشتری عادی",
            "مشتری وفادار",
            "مشتری VIP",
            "مشتری جدید",
            "مشتری غیرفعال"
        ])
        layout.addWidget(self.type_combo, 1, 1)
        
        # حداقل خرید
        layout.addWidget(QLabel("حداقل خرید:"), 1, 2)
        self.min_purchase_spin = QSpinBox()
        self.min_purchase_spin.setRange(0, 1000000000)
        self.min_purchase_spin.setValue(0)
        self.min_purchase_spin.setSuffix(" تومان")
        layout.addWidget(self.min_purchase_spin, 1, 3)
        
        # دکمه اعمال فیلتر
        btn_apply = QPushButton("✅ اعمال فیلتر")
        btn_apply.clicked.connect(self.apply_filters)
        layout.addWidget(btn_apply, 1, 4)
        
        # دکمه بازنشانی
        btn_reset = QPushButton("🔄 بازنشانی")
        btn_reset.clicked.connect(self.reset_filters)
        layout.addWidget(btn_reset, 1, 5)
        
        parent_layout.addWidget(filter_frame)
    
    def create_tab_widget(self, parent_layout):
        """ایجاد ویجت تب‌ها"""
        self.tab_widget = QTabWidget()
        
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
                background-color: #9b59b6;
                color: white;
            }
            QTabBar::tab:hover:!selected {
                background-color: #34495e;
            }
        """)
        
        # ایجاد تب‌ها
        self.create_overview_tab()
        self.create_behavior_tab()
        self.create_segmentation_tab()
        self.create_history_tab()
        
        parent_layout.addWidget(self.tab_widget, 1)
    
    def create_overview_tab(self):
        """ایجاد تب نمای کلی"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # هدر
        header_label = QLabel("📊 نمای کلی مشتریان")
        header_label.setStyleSheet("""
            QLabel {
                color: #9b59b6;
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
        
        # کارت‌های آمار
        self.create_stats_cards(layout)
        
        # نمودار رشد مشتریان
        self.create_customer_growth_chart(layout)
        
        # جدول آخرین مشتریان
        self.create_recent_customers_table(layout)
        
        self.tab_widget.addTab(tab, "📊 نمای کلی")
    
    def create_stats_cards(self, parent_layout):
        """ایجاد کارت‌های آمار"""
        cards_frame = QFrame()
        cards_layout = QGridLayout(cards_frame)
        cards_layout.setSpacing(15)
        
        # کارت‌های مختلف
        stats = [
            ("👥 کل مشتریان", "۰", "#3498db"),
            ("💰 مشتریان فعال", "۰", "#2ecc71"),
            ("⭐ مشتریان VIP", "۰", "#f1c40f"),
            ("📅 مشتریان جدید", "۰", "#e74c3c"),
            ("📊 میانگین خرید", "۰ تومان", "#9b59b6"),
            ("🏆 بیشترین خرید", "۰ تومان", "#1abc9c"),
            ("📈 نرخ بازگشت", "۰٪", "#27ae60"),
            ("📉 مشتریان غیرفعال", "۰", "#7f8c8d")
        ]
        
        for i, (title, value, color) in enumerate(stats):
            row = i // 4
            col = i % 4
            card = self.create_stat_card(title, value, color)
            cards_layout.addWidget(card, row, col)
        
        parent_layout.addWidget(cards_frame)
    
    def create_stat_card(self, title, value, color):
        """ایجاد یک کارت آمار"""
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
                font-size: 11pt;
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
                font-size: 14pt;
                font-weight: bold;
                text-align: center;
                padding: 8px 0;
            }
        """)
        layout.addWidget(value_label)
        
        return card
    
    def create_customer_growth_chart(self, parent_layout):
        """ایجاد نمودار رشد مشتریان"""
        group = QGroupBox("📈 نمودار رشد مشتریان")
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
        
        # نمودار
        self.growth_chart_view = QChartView()
        self.growth_chart_view.setRenderHint(QPainter.Antialiasing)
        self.growth_chart_view.setMinimumHeight(250)
        
        layout.addWidget(self.growth_chart_view)
        parent_layout.addWidget(group)
    
    def create_recent_customers_table(self, parent_layout):
        """ایجاد جدول آخرین مشتریان"""
        group = QGroupBox("🆕 آخرین مشتریان ثبت شده")
        group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #2ecc71;
                border-radius: 8px;
                margin-top: 15px;
                padding-top: 15px;
                color: #2ecc71;
                font-size: 12pt;
            }
        """)
        
        layout = QVBoxLayout(group)
        
        # جدول
        self.recent_customers_table = QTableWidget(10, 5)
        
        # تنظیمات
        for i in range(10):
            self.recent_customers_table.setRowHeight(i, 35)
        
        self.recent_customers_table.setStyleSheet("""
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
        
        # هدرها
        headers = ["نام مشتری", "موبایل", "تاریخ ثبت", "تعداد خرید", "مجموع خرید"]
        self.recent_customers_table.setHorizontalHeaderLabels(headers)
        
        # تنظیم ستون‌ها
        header = self.recent_customers_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        
        layout.addWidget(self.recent_customers_table)
        parent_layout.addWidget(group)
    
    def create_behavior_tab(self):
        """ایجاد تب تحلیل رفتاری"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # محتوای تب تحلیل رفتاری
        label = QLabel("📈 تحلیل رفتاری مشتریان - به زودی...")
        label.setAlignment(Qt.AlignCenter)
        label.setStyleSheet("""
            QLabel {
                color: #7f8c8d;
                font-size: 18pt;
                padding: 50px;
            }
        """)
        
        layout.addWidget(label)
        self.tab_widget.addTab(tab, "📈 رفتارشناسی")
    
    def create_segmentation_tab(self):
        """ایجاد تب تقسیم‌بندی"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # محتوای تب تقسیم‌بندی
        label = QLabel("🎯 تقسیم‌بندی مشتریان - به زودی...")
        label.setAlignment(Qt.AlignCenter)
        label.setStyleSheet("""
            QLabel {
                color: #7f8c8d;
                font-size: 18pt;
                padding: 50px;
            }
        """)
        
        layout.addWidget(label)
        self.tab_widget.addTab(tab, "🎯 تقسیم‌بندی")
    
    def create_history_tab(self):
        """ایجاد تب تاریخچه"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # محتوای تب تاریخچه
        label = QLabel("📋 تاریخچه تعاملات - به زودی...")
        label.setAlignment(Qt.AlignCenter)
        label.setStyleSheet("""
            QLabel {
                color: #7f8c8d;
                font-size: 18pt;
                padding: 50px;
            }
        """)
        
        layout.addWidget(label)
        self.tab_widget.addTab(tab, "📋 تاریخچه")
    
    def create_status_bar(self, parent_layout):
        """ایجاد نوار وضعیت"""
        status_frame = QFrame()
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
        
        layout = QHBoxLayout(status_frame)
        
        self.status_label = QLabel("✅ سیستم گزارش مشتریان آماده است")
        self.customers_count_label = QLabel("تعداد مشتریان: ۰")
        self.last_update_label = QLabel("آخرین بروزرسانی: --:--")
        
        layout.addWidget(self.status_label, 5)
        layout.addWidget(self.customers_count_label, 3)
        layout.addWidget(self.last_update_label, 3)
        
        parent_layout.addWidget(status_frame)
    
    def load_customer_data(self):
        """بارگذاری داده‌های مشتریان"""
        try:
            self.status_label.setText("📊 در حال دریافت داده‌های مشتریان...")
            
            # دریافت تاریخ‌ها
            start_date = self.start_date_edit.date().toString("yyyy-MM-dd")
            end_date = self.end_date_edit.date().toString("yyyy-MM-dd")
            
            # دریافت داده‌ها از دیتابیس
            self.load_customers_from_database(start_date, end_date)
            
            # به‌روزرسانی UI
            self.update_overview_tab()
            
            self.status_label.setText("✅ داده‌های مشتریان بارگذاری شد")
            self.last_update_label.setText(f"آخرین بروزرسانی: {get_current_jalali()}")
            
        except Exception as e:
            self.status_label.setText(f"❌ خطا در بارگذاری داده‌ها: {str(e)}")
            print(f"خطا در load_customer_data: {e}")
            self.load_sample_customer_data()
    
    def load_customers_from_database(self, start_date, end_date):
        """بارگذاری مشتریان از دیتابیس"""
        try:
            # دریافت کل مشتریان
            query = """
            SELECT 
                p.id,
                p.first_name,
                p.last_name,
                p.mobile,
                p.registration_date,
                COUNT(DISTINCT i.id) as invoice_count,
                SUM(i.total) as total_purchases,
                MAX(i.invoice_date) as last_purchase_date
            FROM Persons p
            LEFT JOIN Invoices i ON p.id = i.customer_id
            WHERE p.person_type = 'مشتری'
            AND (i.invoice_date IS NULL OR DATE(i.invoice_date) BETWEEN ? AND ?)
            GROUP BY p.id
            ORDER BY total_purchases DESC
            """
            
            customers = self.data_manager.db.fetch_all(query, (start_date, end_date))
            
            # پردازش داده‌ها
            self.customer_data = {
                'total_customers': len(customers),
                'active_customers': sum(1 for c in customers if c.get('invoice_count', 0) > 0),
                'vip_customers': sum(1 for c in customers if c.get('total_purchases', 0) > 10000000),
                'new_customers': sum(1 for c in customers if c.get('registration_date', '') >= start_date),
                'avg_purchase': sum(c.get('total_purchases', 0) for c in customers) / len(customers) if customers else 0,
                'max_purchase': max((c.get('total_purchases', 0) for c in customers), default=0),
                'recent_customers': customers[:10] if customers else []
            }
            
            print(f"📊 تعداد مشتریان بارگذاری شده: {self.customer_data['total_customers']}")
            
        except Exception as e:
            print(f"❌ خطا در بارگذاری مشتریان از دیتابیس: {e}")
            raise
    
    def load_sample_customer_data(self):
        """بارگذاری داده‌های نمونه"""
        self.customer_data = {
            'total_customers': 150,
            'active_customers': 120,
            'vip_customers': 25,
            'new_customers': 15,
            'avg_purchase': 850000,
            'max_purchase': 5200000,
            'recent_customers': [
                {
                    'first_name': 'رضا',
                    'last_name': 'محمدی',
                    'mobile': '09121234567',
                    'registration_date': '1402/10/15',
                    'invoice_count': 8,
                    'total_purchases': 2500000
                },
                {
                    'first_name': 'سارا',
                    'last_name': 'احمدی',
                    'mobile': '09351234567',
                    'registration_date': '1402/10/10',
                    'invoice_count': 5,
                    'total_purchases': 1800000
                }
            ]
        }
    
    def update_overview_tab(self):
        """به‌روزرسانی تب نمای کلی"""
        # به‌روزرسانی کارت‌ها
        # این بخش نیاز به اتصال به ویجت‌های واقعی دارد
        
        # به‌روزرسانی جدول مشتریان
        self.update_recent_customers_table()
    
    def update_recent_customers_table(self):
        """به‌روزرسانی جدول آخرین مشتریان"""
        recent_customers = self.customer_data.get('recent_customers', [])
        
        row_count = min(len(recent_customers), 10)
        self.recent_customers_table.setRowCount(row_count)
        
        for row, customer in enumerate(recent_customers[:10]):
            # نام کامل
            full_name = f"{customer.get('first_name', '')} {customer.get('last_name', '')}".strip()
            
            # موبایل
            mobile = customer.get('mobile', '')
            
            # تاریخ ثبت (تبدیل به شمسی)
            reg_date = customer.get('registration_date', '')
            if reg_date:
                reg_date_shamsi = gregorian_to_jalali(reg_date)
            else:
                reg_date_shamsi = ''
            
            # تعداد خرید
            invoice_count = customer.get('invoice_count', 0)
            
            # مجموع خرید (تبدیل به تومان)
            total_purchases = customer.get('total_purchases', 0) / 10
            total_formatted = f"{total_purchases:,.0f} تومان"
            
            # قرار دادن در جدول
            items = [
                full_name,
                mobile,
                reg_date_shamsi,
                str(invoice_count),
                total_formatted
            ]
            
            for col, text in enumerate(items):
                item = QTableWidgetItem(str(text))
                item.setTextAlignment(Qt.AlignCenter)
                
                # رنگ‌بندی بر اساس مبلغ خرید
                if col == 4 and total_purchases > 1000000:
                    item.setForeground(QColor("#f1c40f"))  # طلایی برای خریدهای بالا
                
                self.recent_customers_table.setItem(row, col, item)
        
        # پنهان کردن ردیف‌های خالی
        for row in range(row_count, 10):
            self.recent_customers_table.hideRow(row)
    
    def on_period_changed(self, index):
        """تغییر دوره زمانی"""
        pass
    
    def apply_filters(self):
        """اعمال فیلترها"""
        self.status_label.setText("🔄 در حال اعمال فیلترها...")
        QTimer.singleShot(100, self.load_customer_data)
    
    def reset_filters(self):
        """بازنشانی فیلترها"""
        self.period_combo.setCurrentIndex(0)
        self.start_date_edit.setDate(QDate.currentDate().addDays(-30))
        self.end_date_edit.setDate(QDate.currentDate())
        self.type_combo.setCurrentIndex(0)
        self.min_purchase_spin.setValue(0)
        self.apply_filters()
    
    def export_to_excel(self):
        """صدور گزارش به Excel"""
        try:
            from ui.forms.reports.utils.exporters import ExcelExporter
            
            exporter = ExcelExporter(self.data_manager)
            
            start_date = self.start_date_edit.date().toString("yyyy-MM-dd")
            end_date = self.end_date_edit.date().toString("yyyy-MM-dd")
            
            # در اینجا باید داده‌های مشتریان را برای export آماده کنیم
            customer_data = self.prepare_customer_data_for_export()
            
            success, message = exporter.export_customer_report(
                customer_data, start_date, end_date
            )
            
            if success:
                QMessageBox.information(self, "✅ موفق", message)
            else:
                QMessageBox.warning(self, "⚠️ خطا", message)
                
        except Exception as e:
            QMessageBox.critical(self, "❌ خطا", f"خطا در صدور خروجی:\n{str(e)}")
    
    def prepare_customer_data_for_export(self):
        """آماده‌سازی داده‌های مشتریان برای خروجی"""
        return self.customer_data