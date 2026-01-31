"""
فرم گزارش‌گیری انبار
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QComboBox, QTableWidget, QTableWidgetItem,
    QGroupBox, QFormLayout, QDateEdit, QCheckBox,
    QTabWidget, QFrame, QTextEdit, QProgressBar,
    QFileDialog, QMessageBox
)
from PySide6.QtCore import Qt, QDate, QTimer
from PySide6.QtGui import QColor, QFont
from PySide6.QtCharts import QChart, QChartView, QBarSeries, QBarSet, QBarCategoryAxis, QValueAxis
import jdatetime
from datetime import datetime, timedelta
import json

from ui.widgets.jalali_date_input import JalaliDateInput

from .base_inventory_form import BaseInventoryForm

class InventoryReportForm(BaseInventoryForm):
    """فرم گزارش‌گیری انبار"""
    
    def __init__(self, parent=None):
        super().__init__("گزارش‌گیری انبار", parent)
        self.setup_ui()
        self.load_initial_data()

    def format_date(self, date_str):
        """فرمت کردن تاریخ (تبدیل میلادی به شمسی)"""
        try:
            if not date_str:
                return ""
            
            # اگر تاریخ شمسی است
            if isinstance(date_str, str) and ('/' in date_str or '-' in date_str):
                # بررسی اگر تاریخ شمسی است
                try:
                    parts = date_str.replace('-', '/').split('/')
                    if len(parts) == 3:
                        year, month, day = map(int, parts)
                        # اگر تاریخ شمسی است (سال بین 1300 تا 1500)
                        if 1300 <= year <= 1500:
                            jalali_date = jdatetime.date(year, month, day)
                            return f"{jalali_date.year:04d}/{jalali_date.month:02d}/{jalali_date.day:02d}"
                except:
                    pass
            
            # تبدیل میلادی به شمسی
            if isinstance(date_str, str):
                # فرمت‌های مختلف تاریخ میلادی
                for fmt in ["%Y-%m-%d", "%Y/%m/%d", "%Y-%m-%d %H:%M:%S", "%Y/%m/%d %H:%M:%S"]:
                    try:
                        date_obj = datetime.strptime(date_str, fmt)
                        jalali_date = jdatetime.date.fromgregorian(date=date_obj.date())
                        return f"{jalali_date.year:04d}/{jalali_date.month:02d}/{jalali_date.day:02d}"
                    except:
                        continue
            
            return str(date_str)
        except:
            return date_str      

    def setup_ui(self):
        # هدر
        header_label = QLabel("📊 گزارش‌گیری انبار")
        header_label.setStyleSheet("""
            font-size: 18px;
            font-weight: bold;
            color: #1e90ff;
            padding: 10px;
            text-align: center;
        """)
        self.main_layout.addWidget(header_label)
        
        # تب‌ها
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabPosition(QTabWidget.North)
        
        self.create_summary_tab()
        self.create_stock_report_tab()
        self.create_transaction_report_tab()
        self.create_valuation_tab()
        
        self.main_layout.addWidget(self.tab_widget)
        
        # دکمه‌های عملیات
        self.create_action_buttons()
    
    def create_summary_tab(self):
        """تب خلاصه وضعیت"""
        tab = QWidget()
        layout = QVBoxLayout()
        
        # فیلترها
        filter_group = QGroupBox("🔍 فیلتر گزارش")
        filter_layout = QFormLayout()
        
        date_layout = QHBoxLayout()

        # تاریخ شمسی
        self.report_from_date = JalaliDateInput()
        self.report_to_date = JalaliDateInput()

        # تنظیم تاریخ پیش‌فرض (30 روز قبل تا امروز)
        import jdatetime
        today_jalali = jdatetime.date.today()
        thirty_days_ago = today_jalali - jdatetime.timedelta(days=30)

        self.report_from_date.set_date(thirty_days_ago)
        self.report_to_date.set_date(today_jalali)

        # تنظیم ارتفاع یکسان
        self.report_from_date.setFixedHeight(35)
        self.report_to_date.setFixedHeight(35)

        # تغییر ترتیب نمایش
        date_layout.addWidget(QLabel("تا تاریخ:"))
        date_layout.addWidget(self.report_to_date)
        date_layout.addWidget(QLabel("از تاریخ:"))
        date_layout.addWidget(self.report_from_date)
        date_layout.addStretch()
        
        filter_layout.addRow(date_layout)
        
        # دکمه تولید گزارش
        btn_layout = QHBoxLayout()
        generate_btn = QPushButton("📈 تولید گزارش خلاصه")
        generate_btn.clicked.connect(self.generate_summary_report)
        generate_btn.setStyleSheet("background-color: #3498db; color: white; padding: 10px 20px;")
        
        btn_layout.addWidget(generate_btn)
        btn_layout.addStretch()
        
        filter_layout.addRow(btn_layout)
        filter_group.setLayout(filter_layout)
        layout.addWidget(filter_group)
        
        # کارت‌های آمار
        self.summary_cards_layout = QHBoxLayout()
        layout.addLayout(self.summary_cards_layout)
        
        # جداول خلاصه
        tables_layout = QHBoxLayout()
        tables_layout.setSpacing(15)

        # جدول 1: موجودی کم
        low_stock_group = QGroupBox("⚠️ موجودی‌های کم")
        low_stock_group.setStyleSheet("""
            QGroupBox {
                border: 2px solid #f39c12;
                border-radius: 8px;
                font-weight: bold;
                padding: 10px;
                margin-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
        low_stock_layout = QVBoxLayout()
        
        self.low_stock_table = QTableWidget()
        self.low_stock_table.setColumnCount(4)
        self.low_stock_table.setHorizontalHeaderLabels(["آیتم", "موجودی", "حداقل", "تفاضل"])
        self.low_stock_table.setMaximumHeight(200)
        
        low_stock_layout.addWidget(self.low_stock_table)
        low_stock_group.setLayout(low_stock_layout)
        self.low_stock_table.setMinimumHeight(250)
        self.low_stock_table.setMaximumHeight(400)

        # جدول 2: تراکنش‌های اخیر
        recent_trans_group = QGroupBox("🔄 تراکنش‌های اخیر")
        recent_trans_group.setStyleSheet("""
            QGroupBox {
                border: 2px solid #3498db;
                border-radius: 8px;
                font-weight: bold;
                padding: 10px;
                margin-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
        recent_trans_layout = QVBoxLayout()
        
        self.recent_trans_table = QTableWidget()
        self.recent_trans_table.setColumnCount(6)
        self.recent_trans_table.setHorizontalHeaderLabels(["تاریخ", "نوع تراکنش", "نام آیتم/قطعه", "تعداد", "قیمت واحد", "توضیحات"])
        self.recent_trans_table.setMaximumHeight(200)
        self.recent_trans_table.setMinimumHeight(250)
        self.recent_trans_table.setMaximumHeight(400)

        recent_trans_layout.addWidget(self.recent_trans_table)
        recent_trans_group.setLayout(recent_trans_layout)
        
        tables_layout.addWidget(low_stock_group)
        tables_layout.addWidget(recent_trans_group)
        layout.addLayout(tables_layout)
        
        tab.setLayout(layout)
        self.tab_widget.addTab(tab, "📊 خلاصه")
    
    def create_stock_report_tab(self):
        """تب گزارش موجودی"""
        tab = QWidget()
        layout = QVBoxLayout()
        
        # فیلترها
        filter_group = QGroupBox("🔍 فیلتر موجودی")
        filter_layout = QFormLayout()
        
        # نوع انبار
        self.stock_warehouse_type = QComboBox()
        self.stock_warehouse_type.addItems(["همه انبارها", "قطعات نو", "قطعات دست دوم", "لوازم نو", "لوازم دست دوم"])
        self.stock_warehouse_type.setFixedHeight(35)

        # وضعیت
        self.stock_status = QComboBox()
        self.stock_status.addItems(["همه وضعیت‌ها", "موجود", "ناموجود", "موجودی کم"])
        self.stock_status.setFixedHeight(35)

        # دکمه‌ها
        btn_layout = QHBoxLayout()
        generate_stock_btn = QPushButton("📋 تولید گزارش موجودی")
        generate_stock_btn.clicked.connect(self.generate_stock_report)
        generate_stock_btn.setStyleSheet("background-color: #27ae60; color: white; padding: 10px 20px;")
        
        export_stock_btn = QPushButton("💾 خروجی Excel")
        export_stock_btn.clicked.connect(self.export_stock_report)
        export_stock_btn.setStyleSheet("background-color: #9b59b6; color: white; padding: 10px 20px;")
        
        btn_layout.addWidget(generate_stock_btn)
        btn_layout.addWidget(export_stock_btn)
        btn_layout.addStretch()
        
        filter_layout.addRow("وضعیت:", self.stock_status)
        filter_layout.addRow("نوع انبار:", self.stock_warehouse_type)
        filter_layout.addRow(btn_layout)
        
        filter_group.setLayout(filter_layout)
        layout.addWidget(filter_group)
        
        # جدول گزارش
        self.stock_report_table = QTableWidget()
        self.stock_report_table.setColumnCount(8)
        self.stock_report_table.setMinimumHeight(400)
        self.stock_report_table.setMaximumHeight(600)
        self.stock_report_table.setHorizontalHeaderLabels([
            "ردیف", "کد/مدل", "نام آیتم", "نوع", "موجودی", 
            "قیمت خرید", "قیمت فروش", "ارزش کل"
        ])
        
        layout.addWidget(self.stock_report_table)
        
        # آمار پایین جدول
        stats_layout = QHBoxLayout()
        
        self.total_items_label = QLabel("تعداد کل آیتم‌ها: 0")
        self.total_items_label.setStyleSheet("color: #3498db; font-weight: bold;")
        
        self.total_value_label = QLabel("ارزش کل انبار: 0 تومان")
        self.total_value_label.setStyleSheet("color: #27ae60; font-weight: bold;")
        
        stats_layout.addWidget(self.total_value_label)
        stats_layout.addWidget(self.total_items_label)
        stats_layout.addStretch()
        
        layout.addLayout(stats_layout)
        
        tab.setLayout(layout)
        self.tab_widget.addTab(tab, "📦 موجودی")
    
    def create_transaction_report_tab(self):
        """تب گزارش تراکنش‌ها"""
        tab = QWidget()
        layout = QVBoxLayout()
        
        # فیلترها
        filter_group = QGroupBox("🔍 فیلتر تراکنش‌ها")
        filter_layout = QFormLayout()
        
        # ردیف اول
        row1_layout = QHBoxLayout()
        
        self.trans_warehouse_type = QComboBox()
        self.trans_warehouse_type.addItems(["همه انبارها", "قطعات نو", "قطعات دست دوم", "لوازم نو", "لوازم دست دوم"])
        self.trans_warehouse_type.setFixedHeight(35)

        self.trans_type = QComboBox()
        self.trans_type.addItems(["همه انواع", "خرید", "فروش", "استفاده در تعمیر", "تعدیل"])
        self.trans_type.setFixedHeight(35)

        row1_layout.addWidget(QLabel("نوع تراکنش:"))
        row1_layout.addWidget(self.trans_type)
        row1_layout.addWidget(QLabel("نوع انبار:"))
        row1_layout.addWidget(self.trans_warehouse_type)
        
        filter_layout.addRow(row1_layout)
        
        # ردیف دوم: بازه تاریخ
        row2_layout = QHBoxLayout()

        # تاریخ شمسی
        self.trans_from_date = JalaliDateInput()
        self.trans_to_date = JalaliDateInput()

        # تنظیم تاریخ پیش‌فرض
        today_jalali = jdatetime.date.today()
        thirty_days_ago = today_jalali - jdatetime.timedelta(days=30)

        self.trans_from_date.set_date(thirty_days_ago)
        self.trans_to_date.set_date(today_jalali)

        # تنظیم ارتفاع یکسان
        self.trans_from_date.setFixedHeight(35)
        self.trans_to_date.setFixedHeight(35)

        row2_layout.addWidget(QLabel("تا تاریخ:"))
        row2_layout.addWidget(self.trans_to_date)
        row2_layout.addWidget(QLabel("از تاریخ:"))
        row2_layout.addWidget(self.trans_from_date)
        row2_layout.addStretch()
        
        filter_layout.addRow(row2_layout)
        
        # دکمه‌ها
        btn_layout = QHBoxLayout()
        generate_trans_btn = QPushButton("📊 تولید گزارش تراکنش")
        generate_trans_btn.clicked.connect(self.generate_transaction_report)
        generate_trans_btn.setStyleSheet("background-color: #3498db; color: white; padding: 10px 20px;")
        
        export_trans_btn = QPushButton("💾 خروجی Excel")
        export_trans_btn.clicked.connect(self.export_transaction_report)
        export_trans_btn.setStyleSheet("background-color: #9b59b6; color: white; padding: 10px 20px;")
        
        btn_layout.addWidget(generate_trans_btn)
        btn_layout.addWidget(export_trans_btn)
        btn_layout.addStretch()
        
        filter_layout.addRow(btn_layout)
        filter_group.setLayout(filter_layout)
        layout.addWidget(filter_group)
        
        # جدول گزارش
        self.transaction_report_table = QTableWidget()
        self.transaction_report_table.setColumnCount(8)
        self.transaction_report_table.setMinimumHeight(400)
        self.transaction_report_table.setMaximumHeight(600)
        self.transaction_report_table.setHorizontalHeaderLabels([
            "تاریخ", "نوع تراکنش", "نوع انبار", "آیتم", 
            "تعداد", "قیمت واحد", "قیمت کل", "توضیحات"
        ])
        
        layout.addWidget(self.transaction_report_table)
        
        # آمار پایین جدول
        trans_stats_layout = QHBoxLayout()
        
        self.total_trans_label = QLabel("تعداد تراکنش‌ها: 0")
        self.total_trans_label.setStyleSheet("color: #3498db; font-weight: bold;")
        
        self.total_amount_label = QLabel("جمع مبالغ: 0 تومان")
        self.total_amount_label.setStyleSheet("color: #27ae60; font-weight: bold;")
        
        trans_stats_layout.addWidget(self.total_amount_label)
        trans_stats_layout.addWidget(self.total_trans_label)
        trans_stats_layout.addStretch()
        
        layout.addLayout(trans_stats_layout)
        
        tab.setLayout(layout)
        self.tab_widget.addTab(tab, "🔄 تراکنش‌ها")
    
    def create_valuation_tab(self):
        """تب ارزش‌گذاری انبار"""
        tab = QWidget()
        layout = QVBoxLayout()
        
        # اطلاعات ارزش انبار
        valuation_group = QGroupBox("💰 ارزش‌گذاری انبار")
        valuation_group.setStyleSheet("""
            QGroupBox {
                border: 2px solid #f1c40f;
                border-radius: 8px;
                font-weight: bold;
            }
        """)
        valuation_layout = QVBoxLayout()
        
        # کارت‌های ارزش
        value_cards_layout = QHBoxLayout()
        
        # ارزش بر اساس قیمت خرید
        purchase_card = self.create_value_card("ارزش خرید", "#3498db", "0 تومان")
        
        # ارزش بر اساس قیمت فروش
        sale_card = self.create_value_card("ارزش فروش", "#27ae60", "0 تومان")
        
        # سود بالقوه
        profit_card = self.create_value_card("سود بالقوه", "#9b59b6", "0 تومان")
        
        # درصد سود
        profit_percent_card = self.create_value_card("درصد سود", "#f39c12", "0%")
        
        value_cards_layout.addWidget(purchase_card)
        value_cards_layout.addWidget(sale_card)
        value_cards_layout.addWidget(profit_card)
        value_cards_layout.addWidget(profit_percent_card)
        
        valuation_layout.addLayout(value_cards_layout)
        
        # جدول ارزش‌گذاری
        self.valuation_table = QTableWidget()
        self.valuation_table.setColumnCount(6)
        self.valuation_table.setMinimumHeight(300)
        self.valuation_table.setHorizontalHeaderLabels([
            "نوع انبار", "تعداد آیتم", "ارزش خرید", "ارزش فروش", 
            "سود بالقوه", "درصد سود"
        ])
        
        valuation_layout.addWidget(self.valuation_table)
        valuation_group.setLayout(valuation_layout)
        layout.addWidget(valuation_group)
        
        # دکمه محاسبه
        btn_layout = QHBoxLayout()
        calculate_btn = QPushButton("🧮 محاسبه ارزش انبار")
        calculate_btn.clicked.connect(self.calculate_inventory_value)
        calculate_btn.setStyleSheet("background-color: #f39c12; color: white; padding: 10px 20px;")
        
        btn_layout.addWidget(calculate_btn)
        btn_layout.addStretch()
        
        layout.addLayout(btn_layout)
        
        tab.setLayout(layout)
        self.tab_widget.addTab(tab, "💰 ارزش")

    def setup_table_style(self, table, row_height=35, header_height=40):
        """تنظیم استایل و ارتفاع جدول"""
        # تنظیم ارتفاع ردیف‌ها
        for row in range(table.rowCount()):
            table.setRowHeight(row, row_height)
        
        # تنظیم ارتفاع هدر
        table.verticalHeader().setDefaultSectionSize(row_height)
        table.horizontalHeader().setMinimumHeight(header_height)
        table.horizontalHeader().setStretchLastSection(True)
        
        # فونت مناسب
        font = QFont()
        font.setPointSize(10)
        table.setFont(font)

    def create_value_card(self, title, color, value):
        """ایجاد کارت نمایش ارزش"""
        card = QFrame()
        card.setFrameShape(QFrame.StyledPanel)
        card.setStyleSheet(f"""
            QFrame {{
                background-color: {color}20;
                border: 2px solid {color};
                border-radius: 10px;
                padding: 15px;
                margin: 5px;
            }}
        """)
        
        layout = QVBoxLayout()
        
        title_label = QLabel(title)
        title_label.setStyleSheet(f"""
            QLabel {{
                color: {color};
                font-size: 11pt;
                font-weight: bold;
            }}
        """)
        title_label.setAlignment(Qt.AlignCenter)
        
        value_label = QLabel(value)
        value_label.setStyleSheet("""
            QLabel {
                color: #ffffff;
                font-size: 14pt;
                font-weight: bold;
                padding: 10px 0;
            }
        """)
        value_label.setAlignment(Qt.AlignCenter)
        
        layout.addWidget(title_label)
        layout.addWidget(value_label)
        
        card.setLayout(layout)
        return card
    
    def create_action_buttons(self):
        """ایجاد دکمه‌های عملیات پایین فرم"""
        button_layout = QHBoxLayout()
        
        print_btn = QPushButton("🖨️ چاپ گزارش")
        print_btn.clicked.connect(self.print_report)
        print_btn.setStyleSheet("background-color: #3498db; color: white; padding: 10px 20px;")
        
        save_btn = QPushButton("💾 ذخیره گزارش")
        save_btn.clicked.connect(self.save_report)
        save_btn.setStyleSheet("background-color: #27ae60; color: white; padding: 10px 20px;")
        
        refresh_btn = QPushButton("🔄 تازه‌سازی")
        refresh_btn.clicked.connect(self.load_initial_data)
        refresh_btn.setStyleSheet("background-color: #f39c12; color: white; padding: 10px 20px;")
        
        button_layout.addWidget(print_btn)
        button_layout.addWidget(save_btn)
        button_layout.addWidget(refresh_btn)
        button_layout.addStretch()
        
        self.main_layout.addLayout(button_layout)
    
    def load_initial_data(self):
        """بارگذاری داده‌های اولیه"""
        self.generate_summary_report()
        self.generate_stock_report()
    
    def generate_summary_report(self):
        """تولید گزارش خلاصه"""
        try:
            if not self.data_manager or not hasattr(self.data_manager, 'warehouse'):
                self.show_error("اتصال به دیتابیس برقرار نیست!")
                return
            
            # پاک کردن کارت‌های قبلی
            for i in reversed(range(self.summary_cards_layout.count())):
                widget = self.summary_cards_layout.itemAt(i).widget()
                if widget:
                    widget.deleteLater()
            
            # ایجاد کارت‌های جدید
            summary_stats = [
                ("📦 کل آیتم‌ها", "#3498db", "0"),
                ("💰 ارزش کل", "#27ae60", "0 تومان"),
                ("⚠️ کمبود", "#f39c12", "0"),
                ("🔄 تراکنش‌ها", "#9b59b6", "0")
            ]
            
            for title, color, value in summary_stats:
                card = self.create_value_card(title, color, value)
                self.summary_cards_layout.addWidget(card)
            
            # بارگذاری موجودی‌های کم
            low_stock_items = self.get_low_stock_items()
            self.display_low_stock_items(low_stock_items)
            
            # بارگذاری تراکنش‌های اخیر
            recent_transactions = self.get_recent_transactions()
            self.display_recent_transactions(recent_transactions)
            
            self.show_success("گزارش خلاصه با موفقیت تولید شد.")
            
        except Exception as e:
            print(f"❌ خطا در تولید گزارش خلاصه: {e}")
            self.show_error(f"خطا در تولید گزارش: {str(e)}")
    
    def get_low_stock_items(self):
        """دریافت آیتم‌های با موجودی کم"""
        low_stock_items = []
        
        try:
            # بررسی تمام انواع انبار
            warehouse_types = ['قطعات نو', 'قطعات دست دوم', 'لوازم نو', 'لوازم دست دوم']
            
            for w_type in warehouse_types:
                items = self.data_manager.warehouse.get_warehouse_stock(w_type, show_all=True)
                for item in items:
                    quantity = item.get('quantity', 0)
                    min_stock = item.get('min_stock', 5)
                    
                    if quantity <= min_stock:
                        item['warehouse_type'] = w_type
                        low_stock_items.append(item)
            
        except Exception as e:
            print(f"خطا در دریافت موجودی‌های کم: {e}")
        
        return low_stock_items[:10]  # فقط 10 مورد اول
    
    def display_low_stock_items(self, items):
        """نمایش آیتم‌های با موجودی کم"""
        self.low_stock_table.setRowCount(len(items))
        
        for row, item in enumerate(items):
            # نام آیتم
            name = item.get('part_name') or item.get('model') or item.get('device_type_name', 'نامشخص')
            self.low_stock_table.setItem(row, 0, QTableWidgetItem(name))
            
            # موجودی
            self.low_stock_table.setItem(row, 1, QTableWidgetItem(str(item.get('quantity', 0))))
            
            # حداقل
            self.low_stock_table.setItem(row, 2, QTableWidgetItem(str(item.get('min_stock', 5))))
            
            # تفاضل
            diff = max(0, item.get('min_stock', 5) - item.get('quantity', 0))
            self.low_stock_table.setItem(row, 3, QTableWidgetItem(str(diff)))
            
            # رنگ‌آمیزی
            if item.get('quantity', 0) == 0:
                for col in range(4):
                    cell = self.low_stock_table.item(row, col)
                    if cell:
                        cell.setBackground(QColor('#ffcccc'))
        
        # تنظیم ارتفاع ردیف‌ها
        for row in range(self.low_stock_table.rowCount()):
            self.low_stock_table.setRowHeight(row, 35)
        
        # تنظیم اندازه ستون‌ها
        self.low_stock_table.setColumnWidth(0, 180)  # آیتم
        self.low_stock_table.setColumnWidth(1, 80)   # موجودی
        self.low_stock_table.setColumnWidth(2, 80)   # حداقل
        self.low_stock_table.setColumnWidth(3, 80)   # تفاضل

    def get_recent_transactions(self):
        """دریافت تراکنش‌های اخیر"""
        try:
            # تاریخ 7 روز گذشته شمسی
            today_jalali = jdatetime.date.today()
            seven_days_ago_jalali = today_jalali - jdatetime.timedelta(days=7)
            
            # تبدیل به میلادی برای دیتابیس
            seven_days_ago_gregorian = seven_days_ago_jalali.togregorian()
            
            transactions = self.data_manager.warehouse.get_inventory_transactions(
                start_date=seven_days_ago_gregorian.strftime('%Y-%m-%d')
            )
            
            # پردازش و بهبود اطلاعات تراکنش‌ها
            enhanced_transactions = []
            for trans in transactions[:10]:  # فقط 10 مورد اول
                # کپی از تراکنش
                enhanced_trans = trans.copy()
                
                # استخراج نام آیتم از توضیحات
                description = trans.get('description', '')
                if description and '-' in description:
                    parts = description.split('-')
                    if len(parts) >= 2:
                        item_name = parts[-1].strip()
                        enhanced_trans['item_name'] = item_name
                    else:
                        enhanced_trans['item_name'] = description
                elif description:
                    enhanced_trans['item_name'] = description
                else:
                    enhanced_trans['item_name'] = f"آیتم #{trans.get('item_id', '?')}"
                
                enhanced_transactions.append(enhanced_trans)
            
            # دیباگ: نمایش داده‌های پردازش شده
            print("\n" + "="*60)
            print("تراکنش‌های پردازش شده:")
            for i, trans in enumerate(enhanced_transactions):
                print(f"{i+1}. نوع: {trans.get('transaction_type')} | "
                    f"آیتم: {trans.get('item_name')} | "
                    f"توضیحات: {trans.get('description')}")
            print("="*60 + "\n")
            
            return enhanced_transactions
            
        except Exception as e:
            print(f"خطا در دریافت تراکنش‌ها: {e}")
            return []

    def display_recent_transactions(self, transactions):
        """نمایش تراکنش‌های اخیر"""
        self.recent_trans_table.setRowCount(len(transactions))
        
        for row, trans in enumerate(transactions):
            # تاریخ
            date_str = self.format_date(str(trans.get('transaction_date', '')))
            self.recent_trans_table.setItem(row, 0, QTableWidgetItem(date_str))
            
            # نوع تراکنش
            trans_type = trans.get('transaction_type', 'نامشخص')
            trans_item = QTableWidgetItem(trans_type)
            
            # رنگ‌آمیزی نوع تراکنش
            if trans_type == 'خرید':
                trans_item.setBackground(QColor('#27ae60'))
                trans_item.setForeground(QColor('white'))
            elif trans_type == 'فروش':
                trans_item.setBackground(QColor('#3498db'))
                trans_item.setForeground(QColor('white'))
            elif trans_type == 'استفاده در تعمیر':
                trans_item.setBackground(QColor('#f39c12'))
                trans_item.setForeground(QColor('white'))
            elif trans_type == 'تعدیل':
                trans_item.setBackground(QColor('#9b59b6'))
                trans_item.setForeground(QColor('white'))
            
            self.recent_trans_table.setItem(row, 1, trans_item)
            
            # نام آیتم - با الگوریتم بهبود یافته
            item_name = trans.get('item_name', '')
            
            # اگر item_name خالی است یا "نامشخص" است، از توضیحات استخراج کن
            if not item_name or item_name == 'نامشخص':
                description = trans.get('description', '')
                if description:
                    # استخراج نام آیتم از توضیحات
                    if '-' in description:
                        parts = description.split('-')
                        if len(parts) >= 2:
                            extracted_name = parts[-1].strip()
                            # بررسی کن که آیا یک مدل/کد معتبر است
                            if extracted_name and any(c.isdigit() for c in extracted_name):
                                item_name = extracted_name
                            else:
                                item_name = description
                        else:
                            item_name = description
                    else:
                        item_name = description
            
            # اگر هنوز خالی است
            if not item_name:
                item_name = f"آیتم #{trans.get('item_id', row+1)}"
            
            # حذف کلمات اضافی از ابتدای نام
            prefixes = ['خرید ', 'فروش ', 'استفاده ', 'تعدیل ']
            for prefix in prefixes:
                if item_name.startswith(prefix):
                    item_name = item_name[len(prefix):].strip()
            
            self.recent_trans_table.setItem(row, 2, QTableWidgetItem(item_name))
            
            # تعداد
            quantity = trans.get('quantity', 0)
            qty_item = QTableWidgetItem(str(quantity))
            qty_item.setTextAlignment(Qt.AlignCenter)
            self.recent_trans_table.setItem(row, 3, qty_item)
            
            # قیمت واحد
            unit_price = trans.get('unit_price', 0)
            price_item = QTableWidgetItem(self.format_currency(unit_price))
            self.recent_trans_table.setItem(row, 4, price_item)
            
            # توضیحات کامل (بدون پردازش)
            description = trans.get('description', '')
            self.recent_trans_table.setItem(row, 5, QTableWidgetItem(description))
        
        # تنظیم ارتفاع ردیف‌ها و عرض ستون‌ها
        for row in range(self.recent_trans_table.rowCount()):
            self.recent_trans_table.setRowHeight(row, 35)
        
        # تنظیم اندازه ستون‌ها
        self.recent_trans_table.setColumnWidth(0, 100)  # تاریخ
        self.recent_trans_table.setColumnWidth(1, 100)  # نوع تراکنش
        self.recent_trans_table.setColumnWidth(2, 180)  # نام آیتم
        self.recent_trans_table.setColumnWidth(3, 70)   # تعداد
        self.recent_trans_table.setColumnWidth(4, 100)  # قیمت واحد
        self.recent_trans_table.setColumnWidth(5, 200)  # توضیحات (عرض بیشتر)


    def get_item_name_from_transaction(self, transaction):
        """دریافت نام آیتم از تراکنش"""
        try:
            # اول از همه، check کن ببین خود transaction نام آیتم را دارد
            if transaction.get('item_name'):
                return transaction['item_name']
            
            # بررسی توضیحات - این قسمت جدید است
            description = transaction.get('description', '')
            if description:
                # اگر توضیحات شامل خط تیره (-) است، احتمالاً فرمت "نوع تراکنش - نام آیتم" است
                if '-' in description:
                    # تقسیم بر اساس خط تیره
                    parts = description.split('-')
                    if len(parts) >= 2:
                        # قسمت دوم را به عنوان نام آیتم در نظر بگیر
                        item_name = parts[-1].strip()
                        # بررسی کن که آیا این یک کد/مدل معتبر است
                        if item_name and len(item_name) > 1 and item_name != "نامشخص":
                            return item_name
                
                # اگر توضیحات کوتاه است و شبیه نام آیتم است (مثل "WF-8000")
                if len(description) < 50 and not any(word in description for word in 
                                                ['خرید', 'فروش', 'استفاده', 'تعدیل', 'انبار', 'قطعات', 'لوازم']):
                    # اگر شامل اعداد و حروف است (مثل مدل)
                    if any(c.isdigit() for c in description) and any(c.isalpha() for c in description):
                        return description
            
            # اگر از طریق توضیحات موفق نبودیم، سعی کن از دیتابیس نام آیتم را بگیر
            item_id = transaction.get('item_id')
            warehouse_type = transaction.get('warehouse_type', 'قطعات نو')
            
            if item_id:
                # ابتدا در cache جستجو کن
                if not hasattr(self, '_item_cache'):
                    self._item_cache = {}
                
                cache_key = f"{warehouse_type}_{item_id}"
                if cache_key in self._item_cache:
                    return self._item_cache[cache_key]
                
                # در غیر این صورت از دیتابیس بخوان
                try:
                    # این بستگی به ساختار دیتابیس شما دارد
                    # با توجه به مشکل "خرید لوازم دست دوم - WF-8000" می‌توانیم از توضیحات استفاده کنیم
                    if description and '-' in description:
                        parts = description.split('-')
                        if len(parts) >= 2:
                            item_name = parts[-1].strip()
                            self._item_cache[cache_key] = item_name
                            return item_name
                    
                    # یا از متدهای موجود استفاده کن
                    if hasattr(self.data_manager.warehouse, 'get_item_details'):
                        item_details = self.data_manager.warehouse.get_item_details(item_id, warehouse_type)
                        if item_details:
                            name = item_details.get('name') or item_details.get('model') or item_details.get('part_name')
                            if name:
                                self._item_cache[cache_key] = name
                                return name
                            
                except Exception as e:
                    print(f"خطا در جستجوی آیتم: {e}")
            
            # اگر همه روش‌ها شکست خورد، از توضیحات استفاده کن (حتی اگر کامل باشد)
            if description:
                # سعی کن قسمت مفید توضیحات را استخراج کن
                # حذف کلمات کلی مانند "خرید"، "فروش" و غیره
                words_to_remove = ['خرید', 'فروش', 'استفاده در تعمیر', 'تعدیل', 'انبار', 'موجودی', 'تاریخ']
                cleaned_desc = description
                for word in words_to_remove:
                    cleaned_desc = cleaned_desc.replace(word, '').strip()
                
                # حذف فاصله‌های اضافه و خط تیره‌های ابتدایی/انتهایی
                cleaned_desc = cleaned_desc.strip(' -')
                
                if cleaned_desc:
                    return cleaned_desc
            
            # روش آخر
            transaction_type = transaction.get('transaction_type', '')
            warehouse = transaction.get('warehouse_type', 'انبار')
            return f"{transaction_type} {warehouse}"
            
        except Exception as e:
            print(f"خطا در get_item_name_from_transaction: {e}")
            return "نامشخص"  

    def extract_item_name_from_description(self, description):
        """استخراج نام آیتم از توضیحات"""
        if not description:
            return ""
        
        # الگوهای مختلف برای استخراج نام آیتم
        patterns = [
            # الگو: "خرید/فروش [نوع انبار] - [نام آیتم]"
            r'(خرید|فروش|استفاده|تعدیل)\s+[\w\s]+\s*-\s*([\w\-]+)',
            # الگو: "خرید [نام آیتم] از انبار"
            r'خرید\s+([\w\-]+)\s+از',
            # الگو: "فروش [نام آیتم] به مشتری"
            r'فروش\s+([\w\-]+)\s+به',
            # الگو: فقط مدل/کد (مثل WF-8000, ABC-123)
            r'([A-Z]{2,}-\d{3,})',
            r'([A-Z]{2,}\d{3,})',
        ]
        
        # ابتدا ساده‌ترین حالت: اگر - وجود دارد
        if '-' in description:
            parts = description.split('-')
            if len(parts) >= 2:
                last_part = parts[-1].strip()
                # بررسی کن که آیا این قسمت معتبر است
                if last_part and len(last_part) > 1:
                    # بررسی الگوهای مدل
                    import re
                    model_pattern = r'^[A-Z]{2,}[-_]?\d{3,}$'
                    if re.match(model_pattern, last_part):
                        return last_part
                    
                    # یا اگر شامل اعداد و حروف است
                    if any(c.isdigit() for c in last_part) and any(c.isalpha() for c in last_part):
                        return last_part
        
        # اگر شامل اعداد و حروف است و کوتاه است
        if len(description) < 30:
            if any(c.isdigit() for c in description) and any(c.isalpha() for c in description):
                return description
        
        return ""

    def generate_stock_report(self):
        """تولید گزارش موجودی"""
        try:
            warehouse_type = self.stock_warehouse_type.currentText()
            status_filter = self.stock_status.currentText()
            
            all_items = []
            total_value = 0
            total_items = 0
            
            if warehouse_type == "همه انبارها":
                # جمع‌آوری از همه انبارها
                warehouse_types = ['قطعات نو', 'قطعات دست دوم', 'لوازم نو', 'لوازم دست دوم']
                for w_type in warehouse_types:
                    items = self.data_manager.warehouse.get_warehouse_stock(w_type, show_all=True)
                    for item in items:
                        item['warehouse_type'] = w_type
                        all_items.append(item)
            else:
                # فقط یک نوع انبار
                items = self.data_manager.warehouse.get_warehouse_stock(warehouse_type, show_all=True)
                for item in items:
                    item['warehouse_type'] = warehouse_type
                    all_items.append(item)
            
            # اعمال فیلتر وضعیت
            filtered_items = []
            for item in all_items:
                if status_filter == "همه وضعیت‌ها":
                    filtered_items.append(item)
                elif status_filter == "موجود" and item.get('status') == 'موجود':
                    filtered_items.append(item)
                elif status_filter == "ناموجود" and item.get('status') == 'ناموجود':
                    filtered_items.append(item)
                elif status_filter == "موجودی کم":
                    quantity = item.get('quantity', 0)
                    min_stock = item.get('min_stock', 5)
                    if quantity <= min_stock:
                        filtered_items.append(item)
            
            # نمایش در جدول
            self.display_stock_report(filtered_items)
            
            # محاسبه آمار
            total_items = len(filtered_items)
            total_value = sum(
                item.get('purchase_price', 0) * item.get('quantity', 0) 
                for item in filtered_items
            )
            
            self.total_items_label.setText(f"تعداد کل آیتم‌ها: {total_items}")
            self.total_value_label.setText(f"ارزش کل انبار: {self.format_currency(total_value)}")
            
            self.show_success(f"گزارش موجودی با {total_items} آیتم تولید شد.")
            
        except Exception as e:
            print(f"❌ خطا در تولید گزارش موجودی: {e}")
            self.show_error(f"خطا در تولید گزارش موجودی: {str(e)}")
    
    def display_stock_report(self, items):
        """نمایش گزارش موجودی"""
        self.stock_report_table.setRowCount(len(items))
        
        for row, item in enumerate(items):
            # ردیف
            self.stock_report_table.setItem(row, 0, QTableWidgetItem(str(row + 1)))
            
            # کد/مدل
            code = item.get('part_code') or item.get('model') or f"ID-{item.get('id', row+1)}"
            self.stock_report_table.setItem(row, 1, QTableWidgetItem(code))
            
            # نام آیتم
            name = item.get('part_name') or item.get('model') or item.get('device_type_name', 'نامشخص')
            self.stock_report_table.setItem(row, 2, QTableWidgetItem(name))
            
            # نوع انبار
            self.stock_report_table.setItem(row, 3, QTableWidgetItem(item.get('warehouse_type', '')))
            
            # موجودی
            quantity = item.get('quantity', 0)
            qty_item = QTableWidgetItem(str(quantity))
            qty_item.setTextAlignment(Qt.AlignCenter)
            self.stock_report_table.setItem(row, 4, qty_item)
            
            # قیمت خرید
            purchase_price = item.get('purchase_price', 0)
            purchase_item = QTableWidgetItem(self.format_currency(purchase_price))
            self.stock_report_table.setItem(row, 5, purchase_item)
            
            # قیمت فروش
            sale_price = item.get('sale_price', 0)
            sale_item = QTableWidgetItem(self.format_currency(sale_price))
            self.stock_report_table.setItem(row, 6, sale_item)
            
            # ارزش کل
            total_value = purchase_price * quantity
            total_item = QTableWidgetItem(self.format_currency(total_value))
            self.stock_report_table.setItem(row, 7, total_item)
            
            # رنگ‌آمیزی
            if quantity == 0:
                for col in range(8):
                    cell = self.stock_report_table.item(row, col)
                    if cell:
                        cell.setBackground(QColor('#ffcccc'))
            elif quantity <= item.get('min_stock', 5):
                for col in range(8):
                    cell = self.stock_report_table.item(row, col)
                    if cell:
                        cell.setBackground(QColor('#ffe6cc'))

    def gregorian_to_jalali(self, date_obj):
        """تبدیل تاریخ میلادی به شمسی"""
        if not date_obj:
            return ""
        
        try:
            if isinstance(date_obj, str):
                # تلاش برای تبدیل رشته به تاریخ
                for fmt in ["%Y-%m-%d", "%Y/%m/%d", "%Y-%m-%d %H:%M:%S"]:
                    try:
                        date_obj = datetime.strptime(date_obj.split('T')[0], fmt)
                        break
                    except:
                        continue
            
            if isinstance(date_obj, datetime):
                jalali_date = jdatetime.date.fromgregorian(date=date_obj.date())
                return jalali_date
            elif isinstance(date_obj, QDate):
                date_str = date_obj.toString("yyyy-MM-dd")
                date_obj = datetime.strptime(date_str, "%Y-%m-%d")
                jalali_date = jdatetime.date.fromgregorian(date=date_obj.date())
                return jalali_date
            else:
                return jdatetime.date.today()
        except:
            return jdatetime.date.today() 

    def generate_transaction_report(self):
        """تولید گزارش تراکنش‌ها"""
        try:
            warehouse_type = None
            if self.trans_warehouse_type.currentText() != "همه انبارها":
                warehouse_type = self.trans_warehouse_type.currentText()
            
            # تاریخ‌های شمسی
            from_date_jalali = self.trans_from_date.get_date()
            to_date_jalali = self.trans_to_date.get_date()
            
            # تبدیل تاریخ شمسی به میلادی برای دیتابیس
            from_date_gregorian = from_date_jalali.togregorian()
            to_date_gregorian = to_date_jalali.togregorian()
            
            from_date = from_date_gregorian.strftime("%Y-%m-%d")
            to_date = to_date_gregorian.strftime("%Y-%m-%d")
            
            # دریافت تراکنش‌ها
            transactions = self.data_manager.warehouse.get_inventory_transactions(
                warehouse_type=warehouse_type,
                start_date=from_date,
                end_date=to_date
            )
            
            # فیلتر نوع تراکنش
            trans_type = self.trans_type.currentText()
            if trans_type != "همه انواع":
                transactions = [t for t in transactions if t.get('transaction_type') == trans_type]
            
            # نمایش در جدول
            self.display_transaction_report(transactions)
            
            # محاسبه آمار
            total_trans = len(transactions)
            total_amount = sum(t.get('total_price', 0) for t in transactions)
            
            self.total_trans_label.setText(f"تعداد تراکنش‌ها: {total_trans}")
            self.total_amount_label.setText(f"جمع مبالغ: {self.format_currency(total_amount)}")
            
            # نمایش تاریخ انتخاب شده در پیام
            from_date_str = from_date_jalali.strftime("%Y/%m/%d")
            to_date_str = to_date_jalali.strftime("%Y/%m/%d")
            self.show_success(f"گزارش تراکنش از {from_date_str} تا {to_date_str} با {total_trans} رکورد تولید شد.")
            
        except Exception as e:
            print(f"❌ خطا در تولید گزارش تراکنش: {e}")
            self.show_error(f"خطا در تولید گزارش تراکنش: {str(e)}")
    
    def display_transaction_report(self, transactions):
        """نمایش گزارش تراکنش‌ها"""
        self.transaction_report_table.setRowCount(len(transactions))
        
        for row, trans in enumerate(transactions):
            # تاریخ
            date_str = self.format_date(str(trans.get('transaction_date', '')))
            self.transaction_report_table.setItem(row, 0, QTableWidgetItem(date_str))
            
            # نوع تراکنش
            trans_type = trans.get('transaction_type', '')
            trans_item = QTableWidgetItem(trans_type)
            
            # رنگ‌آمیزی نوع تراکنش
            if trans_type == 'خرید':
                trans_item.setBackground(QColor('#27ae60'))
                trans_item.setForeground(QColor('white'))
            elif trans_type == 'فروش':
                trans_item.setBackground(QColor('#3498db'))
                trans_item.setForeground(QColor('white'))
            
            self.transaction_report_table.setItem(row, 1, trans_item)
            
            # نوع انبار
            self.transaction_report_table.setItem(row, 2, QTableWidgetItem(trans.get('warehouse_type', '')))
            
            # آیتم
            self.transaction_report_table.setItem(row, 3, QTableWidgetItem(f"آیتم #{trans.get('item_id', row+1)}"))
            
            # تعداد
            self.transaction_report_table.setItem(row, 4, QTableWidgetItem(str(trans.get('quantity', 0))))
            
            # قیمت واحد
            unit_price = trans.get('unit_price', 0)
            self.transaction_report_table.setItem(row, 5, QTableWidgetItem(self.format_currency(unit_price)))
            
            # قیمت کل
            total_price = trans.get('total_price', 0)
            self.transaction_report_table.setItem(row, 6, QTableWidgetItem(self.format_currency(total_price)))
            
            # توضیحات
            self.transaction_report_table.setItem(row, 7, QTableWidgetItem(trans.get('description', '')))
    
    def calculate_inventory_value(self):
        """محاسبه ارزش انبار"""
        try:
            # جمع‌آوری از همه انبارها
            warehouse_types = ['قطعات نو', 'قطعات دست دوم', 'لوازم نو', 'لوازم دست دوم']
            
            valuation_data = []
            total_purchase_value = 0
            total_sale_value = 0
            
            for w_type in warehouse_types:
                items = self.data_manager.warehouse.get_warehouse_stock(w_type, show_all=True)
                
                warehouse_purchase_value = 0
                warehouse_sale_value = 0
                item_count = 0
                
                for item in items:
                    quantity = item.get('quantity', 0)
                    purchase_price = item.get('purchase_price', 0)
                    sale_price = item.get('sale_price', 0)
                    
                    warehouse_purchase_value += quantity * purchase_price
                    warehouse_sale_value += quantity * sale_price
                    item_count += 1 if quantity > 0 else 0
                
                total_purchase_value += warehouse_purchase_value
                total_sale_value += warehouse_sale_value
                
                profit = warehouse_sale_value - warehouse_purchase_value
                profit_percent = (profit / warehouse_purchase_value * 100) if warehouse_purchase_value > 0 else 0
                
                valuation_data.append({
                    'warehouse_type': w_type,
                    'item_count': item_count,
                    'purchase_value': warehouse_purchase_value,
                    'sale_value': warehouse_sale_value,
                    'profit': profit,
                    'profit_percent': profit_percent
                })
            
            # نمایش در جدول
            self.display_valuation_table(valuation_data)
            
            # محاسبه کلی
            total_profit = total_sale_value - total_purchase_value
            total_profit_percent = (total_profit / total_purchase_value * 100) if total_purchase_value > 0 else 0
            
            # به‌روزرسانی کارت‌ها
            self.update_value_cards(total_purchase_value, total_sale_value, total_profit, total_profit_percent)
            
            self.show_success("ارزش‌گذاری انبار با موفقیت محاسبه شد.")
            
        except Exception as e:
            print(f"❌ خطا در محاسبه ارزش انبار: {e}")
            self.show_error(f"خطا در محاسبه ارزش انبار: {str(e)}")
    
    def display_valuation_table(self, data):
        """نمایش جدول ارزش‌گذاری"""
        self.valuation_table.setRowCount(len(data))
        
        for row, item in enumerate(data):
            # نوع انبار
            self.valuation_table.setItem(row, 0, QTableWidgetItem(item['warehouse_type']))
            
            # تعداد آیتم
            self.valuation_table.setItem(row, 1, QTableWidgetItem(str(item['item_count'])))
            
            # ارزش خرید
            self.valuation_table.setItem(row, 2, QTableWidgetItem(self.format_currency(item['purchase_value'])))
            
            # ارزش فروش
            self.valuation_table.setItem(row, 3, QTableWidgetItem(self.format_currency(item['sale_value'])))
            
            # سود بالقوه
            profit_item = QTableWidgetItem(self.format_currency(item['profit']))
            if item['profit'] > 0:
                profit_item.setForeground(QColor('#27ae60'))
            elif item['profit'] < 0:
                profit_item.setForeground(QColor('#e74c3c'))
            self.valuation_table.setItem(row, 4, profit_item)
            
            # درصد سود
            percent_item = QTableWidgetItem(f"{item['profit_percent']:.1f}%")
            if item['profit_percent'] > 0:
                percent_item.setForeground(QColor('#27ae60'))
            elif item['profit_percent'] < 0:
                percent_item.setForeground(QColor('#e74c3c'))
            self.valuation_table.setItem(row, 5, percent_item)
    
    def update_value_cards(self, purchase_value, sale_value, profit, profit_percent):
        """به‌روزرسانی کارت‌های ارزش"""
        # پیدا کردن کارت‌ها و به‌روزرسانی
        for i in range(self.summary_cards_layout.count()):
            card = self.summary_cards_layout.itemAt(i).widget()
            if card and card.layout():
                title_label = card.layout().itemAt(0).widget()
                if title_label:
                    title = title_label.text()
                    value_label = card.layout().itemAt(1).widget()
                    
                    if title == "💰 ارزش خرید":
                        value_label.setText(self.format_currency(purchase_value))
                    elif title == "💰 ارزش فروش":
                        value_label.setText(self.format_currency(sale_value))
                    elif title == "💰 سود بالقوه":
                        value_label.setText(self.format_currency(profit))
                    elif title == "💰 درصد سود":
                        value_label.setText(f"{profit_percent:.1f}%")
    
    def export_stock_report(self):
        """خروجی گزارش موجودی به Excel"""
        self.export_table_to_excel(self.stock_report_table, "گزارش_موجودی_انبار")
    
    def export_transaction_report(self):
        """خروجی گزارش تراکنش به Excel"""
        self.export_table_to_excel(self.transaction_report_table, "گزارش_تراکنش_انبار")
    
    def export_table_to_excel(self, table, filename):
        """خروجی جدول به فایل Excel"""
        try:
            import pandas as pd
            from datetime import datetime
            
            # جمع‌آوری داده‌ها از جدول
            data = []
            headers = []
            
            # خواندن هدرها
            for col in range(table.columnCount()):
                headers.append(table.horizontalHeaderItem(col).text())
            
            # خواندن داده‌ها
            for row in range(table.rowCount()):
                row_data = []
                for col in range(table.columnCount()):
                    item = table.item(row, col)
                    row_data.append(item.text() if item else "")
                data.append(row_data)
            
            # ایجاد DataFrame
            df = pd.DataFrame(data, columns=headers)
            
            # ذخیره فایل
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filepath = f"{filename}_{timestamp}.xlsx"
            
            df.to_excel(filepath, index=False, engine='openpyxl')
            
            self.show_success(f"✅ فایل با موفقیت ذخیره شد:\n{filepath}")
            
        except ImportError:
            self.show_warning("⚠️ برای خروجی Excel نیاز به نصب کتابخانه pandas و openpyxl دارید.")
        except Exception as e:
            print(f"❌ خطا در خروجی Excel: {e}")
            self.show_error(f"خطا در خروجی Excel: {str(e)}")
    
    def print_report(self):
        """چاپ گزارش"""
        self.show_success("ویژگی چاپ در حال توسعه است.")
    
    def save_report(self):
        """ذخیره گزارش"""
        self.show_success("گزارش ذخیره شد (ویژگی در حال توسعه).")