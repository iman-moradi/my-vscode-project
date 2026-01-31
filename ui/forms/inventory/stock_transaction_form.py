# ui/forms/inventory/forms/stock_transaction_form.py
"""
فرم مشاهده و مدیریت تراکنش‌های انبار - نسخه اصلاح شده با تاریخ شمسی
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QLineEdit, QComboBox, QTableWidget,
    QTableWidgetItem, QHeaderView, QGroupBox,
    QFormLayout, QCheckBox, QMessageBox, QSpinBox, QFrame, QDialog
)
from PySide6.QtCore import Qt, QDate, QDateTime, Signal
from PySide6.QtGui import QColor, QFont, QIcon

from .base_inventory_form import BaseInventoryForm
from .widgets.inventory_date_input import InventoryDateInput
from .widgets.inventory_table import InventoryTable
import jdatetime
import locale

# تنظیم لوکال فارسی
try:
    locale.setlocale(locale.LC_ALL, 'fa_IR.UTF-8')
except:
    pass


class AdvancedSearchDialog(QDialog):
    """دیالوگ جستجوی پیشرفته"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
    
    def setup_ui(self):
        self.setWindowTitle("جستجوی پیشرفته تراکنش‌ها")
        self.setFixedSize(500, 400)
        
        layout = QVBoxLayout()
        
        # عنوان
        title = QLabel("🔎 جستجوی پیشرفته تراکنش‌ها")
        title.setStyleSheet("font-size: 16px; font-weight: bold; color: #2c3e50;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # فرم جستجو
        form_layout = QFormLayout()
        
        # بازه مبلغ
        amount_layout = QHBoxLayout()
        self.min_amount = QLineEdit()
        self.min_amount.setPlaceholderText("حداقل مبلغ")
        self.max_amount = QLineEdit()
        self.max_amount.setPlaceholderText("حداکثر مبلغ")
        amount_layout.addWidget(self.min_amount)
        amount_layout.addWidget(QLabel("تا"))
        amount_layout.addWidget(self.max_amount)
        
        form_layout.addRow("بازه مبلغ (تومان):", amount_layout)
        
        # بازه تعداد
        qty_layout = QHBoxLayout()
        self.min_qty = QSpinBox()
        self.min_qty.setMinimum(0)
        self.min_qty.setMaximum(10000)
        self.max_qty = QSpinBox()
        self.max_qty.setMinimum(0)
        self.max_qty.setMaximum(10000)
        self.max_qty.setValue(1000)
        qty_layout.addWidget(self.min_qty)
        qty_layout.addWidget(QLabel("تا"))
        qty_layout.addWidget(self.max_qty)
        
        form_layout.addRow("بازه تعداد:", qty_layout)
        
        # کاربر خاص
        self.specific_user = QLineEdit()
        self.specific_user.setPlaceholderText("نام کاربری یا نام کامل")
        form_layout.addRow("کاربر ثبت کننده:", self.specific_user)
        
        # شامل توضیحات
        self.include_description = QCheckBox("جستجو در توضیحات")
        self.include_description.setChecked(True)
        form_layout.addRow("", self.include_description)
        
        # فقط تراکنش‌های امروز
        self.today_only = QCheckBox("فقط تراکنش‌های امروز")
        form_layout.addRow("", self.today_only)
        
        layout.addLayout(form_layout)
        layout.addStretch()
        
        # دکمه‌ها
        btn_layout = QHBoxLayout()
        
        btn_search = QPushButton("🔍 انجام جستجو")
        btn_search.clicked.connect(self.accept)
        btn_search.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
        """)
        
        btn_cancel = QPushButton("لغو")
        btn_cancel.clicked.connect(self.reject)
        btn_cancel.setStyleSheet("""
            QPushButton {
                background-color: #95a5a6;
                color: white;
                padding: 8px 16px;
                border-radius: 4px;
            }
        """)
        
        btn_layout.addWidget(btn_search)
        btn_layout.addWidget(btn_cancel)
        
        layout.addLayout(btn_layout)
        self.setLayout(layout)
    
    def get_search_criteria(self):
        """دریافت معیارهای جستجو"""
        return {
            'min_amount': self.min_amount.text(),
            'max_amount': self.max_amount.text(),
            'min_qty': self.min_qty.value(),
            'max_qty': self.max_qty.value(),
            'specific_user': self.specific_user.text(),
            'include_description': self.include_description.isChecked(),
            'today_only': self.today_only.isChecked()
        }


class StockTransactionForm(BaseInventoryForm):
    """فرم تراکنش‌های انبار - نسخه بهبود یافته"""
    
    def __init__(self, parent=None):
        super().__init__("تراکنش‌های انبار", parent)
        self.setup_ui()
        self.load_data()
        
    def setup_ui(self):
        # هدر
        header_frame = QFrame()
        header_frame.setStyleSheet("""
            QFrame {
                background-color: #2c3e50;
                border-radius: 8px;
                padding: 10px;
            }
        """)
        header_layout = QHBoxLayout(header_frame)
        
        header_label = QLabel("📊 مدیریت تراکنش‌های انبار")
        header_label.setStyleSheet("""
            QLabel {
                font-size: 20px;
                font-weight: bold;
                color: white;
                font-family: 'B Nazanin';
            }
        """)
        header_label.setFont(QFont("B Nazanin", 14, QFont.Bold))
        
        header_layout.addWidget(header_label)
        header_layout.addStretch()
        
        # آمار سریع
        stats_label = QLabel("📈 آمار: در حال بارگذاری...")
        stats_label.setStyleSheet("color: #ecf0f1; font-size: 12px;")
        header_layout.addWidget(stats_label)
        self.stats_label = stats_label
        
        self.main_layout.addWidget(header_frame)
        
        # فیلترها
        self.create_filter_section()
        
        # جدول تراکنش‌ها
        self.create_transaction_table()
        
        # دکمه‌ها
        self.create_action_buttons()
    
    def create_filter_section(self):
        """ایجاد بخش فیلترها با تاریخ شمسی"""
        filter_group = QGroupBox("🔍 فیلتر پیشرفته تراکنش‌ها")
        filter_group.setStyleSheet("""
            QGroupBox {
                border: 2px solid #3498db;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 20px;
                font-weight: bold;
                font-family: 'B Nazanin';
                font-size: 12px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                right: 10px;
                padding: 0 10px 0 10px;
                color: #3498db;
            }
        """)
        filter_layout = QFormLayout()
        filter_layout.setLabelAlignment(Qt.AlignRight)
        filter_layout.setSpacing(10)
        
        # ردیف 1: نوع انبار و نوع تراکنش
        row1_layout = QHBoxLayout()
        row1_layout.setSpacing(15)
        
        # نوع انبار
        warehouse_label = QLabel("نوع انبار:")
        warehouse_label.setFixedWidth(80)
        self.warehouse_type = QComboBox()
        self.warehouse_type.setFixedWidth(180)
        self.warehouse_type.addItems(["همه انبارها", "قطعات نو", "قطعات دست دوم", "لوازم نو", "لوازم دست دوم"])
        self.warehouse_type.setStyleSheet("""
            QComboBox {
                padding: 6px;
                border: 1px solid #bdc3c7;
                border-radius: 4px;
                font-family: 'B Nazanin';
                font-size: 11px;
            }
        """)
        
        # نوع تراکنش
        trans_label = QLabel("نوع تراکنش:")
        trans_label.setFixedWidth(80)
        self.transaction_type = QComboBox()
        self.transaction_type.setFixedWidth(180)
        self.transaction_type.addItems([
            "همه انواع", "خرید", "فروش", "استفاده در تعمیر", 
            "برگشت", "تعدیل", "ضایعات", "انتقال", "حذف", "بازیابی"
        ])
        self.transaction_type.setStyleSheet("""
            QComboBox {
                padding: 6px;
                border: 1px solid #bdc3c7;
                border-radius: 4px;
                font-family: 'B Nazanin';
                font-size: 11px;
            }
        """)
        
        row1_layout.addWidget(warehouse_label)
        row1_layout.addWidget(self.warehouse_type)
        row1_layout.addWidget(trans_label)
        row1_layout.addWidget(self.transaction_type)
        row1_layout.addStretch()
        
        filter_layout.addRow(row1_layout)
        
        # ردیف 2: بازه تاریخ شمسی
        row2_layout = QHBoxLayout()
        row2_layout.setSpacing(15)
        
        # از تاریخ
        from_label = QLabel("از تاریخ:")
        from_label.setFixedWidth(60)
        self.from_date = InventoryDateInput(with_today_button=False, with_calendar=True)
        self.from_date.setFixedWidth(200)  # افزایش عرض

        # تا تاریخ
        to_label = QLabel("تا تاریخ:")
        to_label.setFixedWidth(60)
        self.to_date = InventoryDateInput(with_today_button=False, with_calendar=True)
        self.to_date.setFixedWidth(200)  # افزایش عرض

        row2_layout.addWidget(from_label)
        row2_layout.addWidget(self.from_date)
        row2_layout.addWidget(to_label)
        row2_layout.addWidget(self.to_date)
        row2_layout.addStretch()

        filter_layout.addRow(row2_layout)
        
        # ردیف 3: جستجو و تعداد ردیف‌ها
        row3_layout = QHBoxLayout()
        row3_layout.setSpacing(15)
        
        # جستجو
        search_label = QLabel("جستجو:")
        search_label.setFixedWidth(50)
        self.search_input = QLineEdit()
        self.search_input.setFixedWidth(250)
        self.search_input.setPlaceholderText("جستجو در کد، نام، توضیحات، کاربر...")
        self.search_input.setStyleSheet("""
            QLineEdit {
                padding: 6px;
                border: 1px solid #bdc3c7;
                border-radius: 4px;
                font-family: 'B Nazanin';
                font-size: 11px;
            }
        """)
        
        # محدودیت تعداد ردیف‌ها
        limit_label = QLabel("تعداد نمایش:")
        limit_label.setFixedWidth(70)
        self.limit_spin = QSpinBox()
        self.limit_spin.setFixedWidth(80)
        self.limit_spin.setRange(10, 1000)
        self.limit_spin.setValue(100)
        self.limit_spin.setSuffix(" ردیف")
        
        row3_layout.addWidget(search_label)
        row3_layout.addWidget(self.search_input)
        row3_layout.addWidget(limit_label)
        row3_layout.addWidget(self.limit_spin)
        row3_layout.addStretch()
        
        filter_layout.addRow(row3_layout)
        
        # ردیف 4: دکمه‌های فیلتر
        row4_layout = QHBoxLayout()
        row4_layout.setSpacing(10)
        
        filter_btn = QPushButton("🔍 اعمال فیلتر")
        filter_btn.setFixedWidth(120)
        filter_btn.clicked.connect(self.apply_filters)
        filter_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                padding: 8px;
                border-radius: 4px;
                font-family: 'B Nazanin';
                font-size: 11px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        
        clear_btn = QPushButton("🗑️ پاک کردن فیلترها")
        clear_btn.setFixedWidth(130)
        clear_btn.clicked.connect(self.clear_filters)
        clear_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                padding: 8px;
                border-radius: 4px;
                font-family: 'B Nazanin';
                font-size: 11px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        
        export_btn = QPushButton("📋 خروجی فوری")
        export_btn.setFixedWidth(120)
        export_btn.clicked.connect(self.quick_export)
        export_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                padding: 8px;
                border-radius: 4px;
                font-family: 'B Nazanin';
                font-size: 11px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #219653;
            }
        """)
        
        row4_layout.addWidget(filter_btn)
        row4_layout.addWidget(clear_btn)
        row4_layout.addWidget(export_btn)
        row4_layout.addStretch()
        
        filter_layout.addRow(row4_layout)
        
        filter_group.setLayout(filter_layout)
        self.main_layout.addWidget(filter_group)
        
        # تنظیم تاریخ پیش‌فرض (30 روز گذشته تا امروز)
        today = jdatetime.date.today()
        self.from_date.set_date(today - jdatetime.timedelta(days=30))
        self.to_date.set_date(today)
    
    def create_transaction_table(self):
        """ایجاد جدول تراکنش‌ها با ستون‌های بهینه"""
        group = QGroupBox("📋 لیست تراکنش‌ها")
        group.setStyleSheet("""
            QGroupBox {
                border: 2px solid #9b59b6;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 20px;
                font-weight: bold;
                font-family: 'B Nazanin';
                font-size: 12px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                right: 10px;
                padding: 0 10px 0 10px;
                color: #9b59b6;
            }
        """)
        layout = QVBoxLayout()
        
        # نوار وضعیت جدول
        table_header = QHBoxLayout()
        
        self.table_info = QLabel("در حال بارگذاری...")
        self.table_info.setStyleSheet("color: #7f8c8d; font-size: 11px;")
        table_header.addWidget(self.table_info)
        table_header.addStretch()
        
        # دکمه‌های کنترل جدول
        btn_refresh = QPushButton("🔄")
        btn_refresh.setFixedSize(30, 30)
        btn_refresh.setToolTip("تازه‌سازی جدول")
        btn_refresh.clicked.connect(self.load_data)
        btn_refresh.setStyleSheet("""
            QPushButton {
                background-color: #f39c12;
                color: white;
                border-radius: 4px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #e67e22;
            }
        """)
        
        btn_export = QPushButton("📊")
        btn_export.setFixedSize(30, 30)
        btn_export.setToolTip("خروجی Excel")
        btn_export.clicked.connect(self.export_to_excel)
        btn_export.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border-radius: 4px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #219653;
            }
        """)
        
        table_header.addWidget(btn_refresh)
        table_header.addWidget(btn_export)
        
        layout.addLayout(table_header)
        
        # ایجاد جدول
        self.table = QTableWidget()
        self.table.setMinimumHeight(400)
        self.table.setAlternatingRowColors(True)
        self.table.setStyleSheet("""
            QTableWidget {
                font-family: 'B Nazanin';
                font-size: 11px;
                gridline-color: #ecf0f1;
                selection-background-color: #3498db;
                selection-color: white;
            }
            QTableWidget::item {
                padding: 4px;
            }
            QHeaderView::section {
                background-color: #34495e;
                color: white;
                padding: 6px;
                border: none;
                font-weight: bold;
                font-family: 'B Nazanin';
                font-size: 11px;
            }
            QTableWidget::item:selected {
                background-color: #2980b9;
            }
        """)
        
        # تنظیم 12 ستون برای نمایش اطلاعات کامل
        self.table.setColumnCount(12)
        self.table.setHorizontalHeaderLabels([
            "ردیف",
            "شناسه",
            "تاریخ تراکنش",
            "نوع تراکنش",
            "نوع انبار", 
            "کد آیتم",
            "نام آیتم",
            "تعداد",
            "قیمت واحد (تومان)",
            "قیمت کل (تومان)",
            "توضیحات",
            "کاربر ثبت کننده"
        ])
        
        # تنظیم عرض ستون‌ها به صورت دقیق
        column_widths = [60, 80, 120, 120, 120, 100, 150, 80, 120, 120, 200, 120]
        for i, width in enumerate(column_widths):
            self.table.setColumnWidth(i, width)
        
        # تنظیم هدر قابل تغییر اندازه
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(10, QHeaderView.Stretch)  # ستون توضیحات کشیده شود
        header.setStretchLastSection(True)
        
        layout.addWidget(self.table)
        group.setLayout(layout)
        self.main_layout.addWidget(group)
    
    def create_action_buttons(self):
        """ایجاد دکمه‌های عملیات اصلی"""
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)
        
        # دکمه گزارش خلاصه
        btn_summary = QPushButton("📈 گزارش خلاصه ماهانه")
        btn_summary.clicked.connect(self.show_monthly_summary)
        btn_summary.setStyleSheet("""
            QPushButton {
                background-color: #8e44ad;
                color: white;
                padding: 10px 20px;
                border-radius: 6px;
                font-family: 'B Nazanin';
                font-size: 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #7d3c98;
            }
        """)
        
        # دکمه چاپ
        btn_print = QPushButton("🖨️ چاپ گزارش انتخابی")
        btn_print.clicked.connect(self.print_selected)
        btn_print.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                padding: 10px 20px;
                border-radius: 6px;
                font-family: 'B Nazanin';
                font-size: 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        
        # دکمه جستجوی پیشرفته
        btn_adv_search = QPushButton("🔎 جستجوی پیشرفته")
        btn_adv_search.clicked.connect(self.show_advanced_search)
        btn_adv_search.setStyleSheet("""
            QPushButton {
                background-color: #f39c12;
                color: white;
                padding: 10px 20px;
                border-radius: 6px;
                font-family: 'B Nazanin';
                font-size: 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #e67e22;
            }
        """)
        
        btn_layout.addWidget(btn_summary)
        btn_layout.addWidget(btn_print)
        btn_layout.addWidget(btn_adv_search)
        btn_layout.addStretch()
        
        self.main_layout.addLayout(btn_layout)
    
    def load_data(self):
        """بارگذاری تراکنش‌ها از دیتابیس"""
        print("🔄 در حال بارگذاری تراکنش‌های انبار از دیتابیس...")
        
        try:
            if self.data_manager and hasattr(self.data_manager, 'warehouse'):
                # دریافت پارامترهای فیلتر
                limit = self.limit_spin.value()
                
                # بارگذاری از دیتابیس
                transactions = self.data_manager.warehouse.get_inventory_transactions()
                
                if transactions:
                    print(f"✅ {len(transactions)} تراکنش از دیتابیس بارگذاری شد")
                    
                    # محدود کردن تعداد ردیف‌ها
                    if limit < len(transactions):
                        transactions = transactions[:limit]
                        self.table_info.setText(f"نمایش {limit} تراکنش از {len(transactions)} تراکنش (برای مشاهده بیشتر از فیلترها استفاده کنید)")
                    else:
                        self.table_info.setText(f"نمایش {len(transactions)} تراکنش")
                    
                    self.display_transactions(transactions)
                    self.update_stats(transactions)
                else:
                    print("⚠️ دیتابیس تراکنش‌ها خالی است")
                    self.table.setRowCount(0)
                    self.table_info.setText("هیچ تراکنشی یافت نشد")
                    self.show_info("هیچ تراکنشی در دیتابیس وجود ندارد.")
            else:
                print("❌ data_manager یا warehouse موجود نیست")
                self.show_error("اتصال به دیتابیس برقرار نیست!")
                
        except Exception as e:
            print(f"❌ خطا در بارگذاری تراکنش‌ها: {e}")
            import traceback
            traceback.print_exc()
            self.show_error(f"خطا در بارگذاری تراکنش‌ها: {str(e)}")
    
    def display_transactions(self, transactions):
        """نمایش تراکنش‌ها در جدول با فرمت صحیح"""
        self.table.setRowCount(len(transactions))
        
        # کش برای ذخیره نام آیتم‌ها (برای جلوگیری از کوئری‌های تکراری)
        item_name_cache = {}
        
        for row, trans in enumerate(transactions):
            # ستون 0: ردیف
            item = QTableWidgetItem(str(row + 1))
            item.setTextAlignment(Qt.AlignCenter)
            item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
            self.table.setItem(row, 0, item)
            
            # ستون 1: شناسه تراکنش + منبع
            trans_id = str(trans.get('id', ''))
            source = trans.get('source', '')
            source_symbol = {
                'main': '📝',
                'delete': '🗑️',
                'soft_delete': '📄'
            }.get(source, '')
            
            item = QTableWidgetItem(f"{source_symbol}{trans_id}")
            item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row, 1, item)
            
            # ستون 2: تاریخ تراکنش (شمسی)
            trans_date = trans.get('transaction_date_shamsi', trans.get('transaction_date', ''))
            
            # اگر تاریخ میلادی است، به شمسی تبدیل کن
            if trans_date and '/' not in str(trans_date):
                try:
                    import re
                    numbers = re.findall(r'\d+', str(trans_date))
                    if len(numbers) >= 3:
                        year, month, day = map(int, numbers[:3])
                        if year > 1500:  # میلادی است
                            import datetime
                            from datetime import date as datetime_date
                            gdate = datetime_date(year, month, day)
                            jdate = jdatetime.date.fromgregorian(date=gdate)
                            trans_date = jdate.strftime("%Y/%m/%d")
                except:
                    pass
            
            item = QTableWidgetItem(str(trans_date))
            item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row, 2, item)
            
            # ستون 3: نوع تراکنش
            trans_type = trans.get('transaction_type', '')
            item = QTableWidgetItem(trans_type)
            item.setTextAlignment(Qt.AlignCenter)
            
            # رنگ‌آمیزی بر اساس نوع تراکنش
            color_map = {
                'خرید': QColor('#27ae60'),
                'فروش': QColor('#3498db'),
                'استفاده در تعمیر': QColor('#9b59b6'),
                'برگشت': QColor('#f39c12'),
                'تعدیل': QColor('#e67e22'),
                'ضایعات': QColor('#e74c3c'),
                'انتقال': QColor('#1abc9c'),
                'حذف': QColor('#c0392b'),
                'حذف نرم': QColor('#d35400'),
                'بازیابی': QColor('#16a085')
            }
            
            if trans_type in color_map:
                item.setBackground(color_map[trans_type])
                item.setForeground(QColor('white'))
            
            self.table.setItem(row, 3, item)
            
            # ستون 4: نوع انبار
            warehouse_type = trans.get('warehouse_type', '')
            item = QTableWidgetItem(warehouse_type)
            item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row, 4, item)
            
            # ستون 5: کد آیتم
            item_id = str(trans.get('item_id', ''))
            item_widget = QTableWidgetItem(item_id)
            item_widget.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row, 5, item_widget)
            
            # ستون 6: نام آیتم
            item_name = "در حال بارگیری..."
            warehouse_type_val = trans.get('warehouse_type', '')
            item_id_val = trans.get('item_id', 0)

            # کلید کش
            cache_key = f"{warehouse_type_val}_{item_id_val}"

            if cache_key in item_name_cache:
                item_name = item_name_cache[cache_key]
            else:
                try:
                    # استفاده از تابع جدید
                    item_name = self.data_manager.warehouse.get_item_name(warehouse_type_val, item_id_val)
                    # ذخیره در کش
                    item_name_cache[cache_key] = item_name
                except Exception as e:
                    print(f"خطا در دریافت نام آیتم: {e}")
                    item_name = f"آیتم #{item_id_val}"

            item = QTableWidgetItem(item_name)
            self.table.setItem(row, 6, item)
                        
            # ستون 7: تعداد
            quantity = trans.get('quantity', 0)
            item = QTableWidgetItem(self.format_number(quantity))
            item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row, 7, item)
            
            # ستون 8: قیمت واحد
            unit_price = trans.get('unit_price', 0)
            item = QTableWidgetItem(self.format_currency(unit_price))
            item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.table.setItem(row, 8, item)
            
            # ستون 9: قیمت کل
            total_price = trans.get('total_price', 0)
            item = QTableWidgetItem(self.format_currency(total_price))
            item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            
            # رنگ‌آمیزی قیمت کل بر اساس نوع تراکنش
            if trans_type in ['فروش', 'بازیابی']:
                item.setForeground(QColor('#27ae60'))
            elif trans_type in ['خرید', 'حذف', 'حذف نرم', 'ضایعات']:
                item.setForeground(QColor('#e74c3c'))
            elif trans_type in ['انتقال', 'تعدیل']:
                item.setForeground(QColor('#f39c12'))
            
            self.table.setItem(row, 9, item)
            
            # ستون 10: توضیحات
            description = trans.get('description', '')
            item = QTableWidgetItem(description)
            self.table.setItem(row, 10, item)
            
            # ستون 11: کاربر ثبت کننده
            employee = trans.get('employee', 'سیستم')
            item = QTableWidgetItem(employee)
            item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row, 11, item)
        
        # تنظیم ارتفاع ردیف‌ها
        self.table.resizeRowsToContents()

    def update_stats(self, transactions):
        """به‌روزرسانی آمار تراکنش‌ها - نسخه بهبود یافته"""
        if not transactions:
            self.stats_label.setText("📊 آمار: هیچ تراکنشی یافت نشد")
            return
        
        total_count = len(transactions)
        total_amount = sum(t.get('total_price', 0) for t in transactions)
        
        # شمارش بر اساس نوع تراکنش با جزئیات بیشتر
        type_counts = {}
        type_amounts = {}
        
        for t in transactions:
            trans_type = t.get('transaction_type', 'نامشخص')
            amount = t.get('total_price', 0)
            
            type_counts[trans_type] = type_counts.get(trans_type, 0) + 1
            type_amounts[trans_type] = type_amounts.get(trans_type, 0) + amount
        
        # ایجاد متن آمار
        stats_text = f"📊 آمار: {total_count} تراکنش | جمع مبالغ: {self.format_currency(total_amount)}"
        
        # اضافه کردن انواع پرتکرار
        common_types = sorted(type_counts.items(), key=lambda x: x[1], reverse=True)[:3]
        if common_types:
            type_text = " | پرتکرار: "
            for trans_type, count in common_types:
                amount = type_amounts.get(trans_type, 0)
                type_text += f"{trans_type}: {count} ({self.format_currency(amount)})، "
            type_text = type_text.rstrip("، ")
            stats_text += type_text
        
        # شمارش تعداد حذف‌ها
        delete_count = type_counts.get('حذف', 0) + type_counts.get('حذف نرم', 0)
        if delete_count > 0:
            stats_text += f" | حذف‌ها: {delete_count}"
        
        self.stats_label.setText(stats_text)
    
    def apply_filters(self):
        """اعمال فیلترهای پیشرفته"""
        print("🔍 اعمال فیلترهای پیشرفته...")
        
        try:
            if self.data_manager and hasattr(self.data_manager, 'warehouse'):
                # دریافت پارامترهای فیلتر
                warehouse_type = None
                if self.warehouse_type.currentText() != "همه انبارها":
                    warehouse_type = self.warehouse_type.currentText()
                
                # تبدیل تاریخ‌های شمسی به میلادی برای کوئری
                from_date_shamsi = self.from_date.get_date()
                to_date_shamsi = self.to_date.get_date()
                
                from_date_miladi = from_date_shamsi.togregorian().strftime("%Y-%m-%d")
                to_date_miladi = to_date_shamsi.togregorian().strftime("%Y-%m-%d")
                
                # دریافت تراکنش‌ها با فیلتر تاریخ
                transactions = self.data_manager.warehouse.get_inventory_transactions(
                    warehouse_type=warehouse_type,
                    start_date=from_date_miladi,
                    end_date=to_date_miladi
                )
                
                # فیلتر بر اساس نوع تراکنش
                trans_type_filter = self.transaction_type.currentText()
                if trans_type_filter != "همه انواع":
                    transactions = [t for t in transactions if t.get('transaction_type') == trans_type_filter]
                
                # فیلتر بر اساس جستجوی متن
                search_text = self.search_input.text().strip()
                if search_text:
                    search_text_lower = search_text.lower()
                    transactions = [t for t in transactions if 
                                   search_text_lower in str(t.get('description', '')).lower() or
                                   search_text_lower in str(t.get('employee', '')).lower() or
                                   search_text_lower in str(t.get('item_id', '')).lower()]
                
                # محدود کردن تعداد
                limit = self.limit_spin.value()
                if limit < len(transactions):
                    transactions = transactions[:limit]
                    self.table_info.setText(f"نمایش {limit} تراکنش از {len(transactions)} تراکنش یافت شده")
                else:
                    self.table_info.setText(f"نمایش {len(transactions)} تراکنش")
                
                print(f"✅ {len(transactions)} تراکنش پس از فیلتر یافت شد")
                self.display_transactions(transactions)
                self.update_stats(transactions)
                
            else:
                self.show_error("اتصال به دیتابیس برقرار نیست!")
                
        except Exception as e:
            print(f"❌ خطا در اعمال فیلتر: {e}")
            self.show_error(f"خطا در اعمال فیلتر: {str(e)}")
    
    def clear_filters(self):
        """پاک کردن تمام فیلترها"""
        self.warehouse_type.setCurrentIndex(0)
        self.transaction_type.setCurrentIndex(0)
        
        # تنظیم تاریخ پیش‌فرض
        today = jdatetime.date.today()
        self.from_date.set_date(today - jdatetime.timedelta(days=30))
        self.to_date.set_date(today)
        
        self.search_input.clear()
        self.limit_spin.setValue(100)
        
        self.load_data()
        self.show_info("فیلترها با موفقیت پاک شدند.")
    
    def quick_export(self):
        """خروجی سریع به فایل متنی"""
        try:
            row_count = self.table.rowCount()
            if row_count == 0:
                self.show_warning("هیچ تراکنشی برای خروجی وجود ندارد.")
                return
            
            # ساخت گزارش
            import os
            from datetime import datetime
            
            reports_dir = "reports"
            if not os.path.exists(reports_dir):
                os.makedirs(reports_dir)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"تراکنش_انبار_{timestamp}.txt"
            filepath = os.path.join(reports_dir, filename)
            
            # جمع‌آوری داده‌ها
            report_lines = []
            report_lines.append("=" * 80)
            report_lines.append("گزارش تراکنش‌های انبار - تولید شده توسط سیستم مدیریت انبار")
            report_lines.append(f"تاریخ تولید: {jdatetime.datetime.now().strftime('%Y/%m/%d ساعت %H:%M')}")
            report_lines.append(f"تعداد تراکنش‌ها: {row_count}")
            report_lines.append("=" * 80)
            report_lines.append("")
            
            # جمع کل مبالغ
            total_amount = 0
            for row in range(row_count):
                try:
                    amount_text = self.table.item(row, 9).text().replace('تومان', '').replace(',', '').strip()
                    amount = float(amount_text) if amount_text else 0
                    total_amount += amount
                except:
                    pass
            
            report_lines.append(f"💰 جمع کل مبالغ: {self.format_currency(total_amount)}")
            report_lines.append("")
            
            # سرستون‌ها
            headers = []
            for col in range(self.table.columnCount()):
                headers.append(self.table.horizontalHeaderItem(col).text())
            
            report_lines.append(" | ".join(headers))
            report_lines.append("-" * 80)
            
            # داده‌های هر ردیف
            for row in range(row_count):
                row_data = []
                for col in range(self.table.columnCount()):
                    item = self.table.item(row, col)
                    if item:
                        row_data.append(item.text())
                    else:
                        row_data.append("")
                report_lines.append(" | ".join(row_data))
            
            report_lines.append("")
            report_lines.append("=" * 80)
            report_lines.append("پایان گزارش")
            
            # ذخیره فایل
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write('\n'.join(report_lines))
            
            self.show_success(f"✅ گزارش با موفقیت ذخیره شد:\n{filepath}")
            
        except Exception as e:
            print(f"❌ خطا در تولید گزارش سریع: {e}")
            self.show_error(f"خطا در تولید گزارش: {str(e)}")
    
    def export_to_excel(self):
        """خروجی به Excel"""
        try:
            row_count = self.table.rowCount()
            if row_count == 0:
                self.show_warning("هیچ تراکنشی برای خروجی وجود ندارد.")
                return
            
            self.show_info("در حال آماده‌سازی خروجی Excel...")
            # این بخش نیاز به کتابخانه pandas یا openpyxl دارد
            # فعلاً از خروجی متنی استفاده می‌کنیم
            self.quick_export()
            
        except Exception as e:
            print(f"❌ خطا در خروجی Excel: {e}")
            self.show_error("برای خروجی Excel نیاز به نصب کتابخانه pandas است. از خروجی متنی استفاده کنید.")
    
    def print_selected(self):
        """چاپ تراکنش‌های انتخابی"""
        try:
            selected_rows = self.table.selectedItems()
            if not selected_rows:
                self.show_warning("لطفاً یک یا چند تراکنش را برای چاپ انتخاب کنید.")
                return
            
            # جمع‌آوری ردیف‌های انتخابی
            unique_rows = set()
            for item in selected_rows:
                unique_rows.add(item.row())
            
            row_count = len(unique_rows)
            self.show_info(f"آماده‌سازی {row_count} تراکنش انتخابی برای چاپ...")
            
            # ایجاد گزارش انتخابی
            import os
            from datetime import datetime
            
            reports_dir = "reports"
            if not os.path.exists(reports_dir):
                os.makedirs(reports_dir)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"تراکنش_انتخابی_{timestamp}.txt"
            filepath = os.path.join(reports_dir, filename)
            
            # ساخت گزارش
            report_lines = []
            report_lines.append("=" * 80)
            report_lines.append("گزارش تراکنش‌های انتخابی انبار")
            report_lines.append(f"تاریخ تولید: {jdatetime.datetime.now().strftime('%Y/%m/%d ساعت %H:%M')}")
            report_lines.append(f"تعداد تراکنش‌های انتخابی: {row_count}")
            report_lines.append("=" * 80)
            report_lines.append("")
            
            # جمع کل مبالغ انتخابی
            total_amount = 0
            for row in sorted(unique_rows):
                try:
                    amount_text = self.table.item(row, 9).text().replace('تومان', '').replace(',', '').strip()
                    amount = float(amount_text) if amount_text else 0
                    total_amount += amount
                except:
                    pass
            
            report_lines.append(f"💰 جمع کل مبالغ انتخابی: {self.format_currency(total_amount)}")
            report_lines.append("")
            
            # سرستون‌ها
            headers = []
            for col in range(self.table.columnCount()):
                headers.append(self.table.horizontalHeaderItem(col).text())
            
            report_lines.append(" | ".join(headers))
            report_lines.append("-" * 80)
            
            # داده‌های ردیف‌های انتخابی
            for row in sorted(unique_rows):
                row_data = []
                for col in range(self.table.columnCount()):
                    item = self.table.item(row, col)
                    if item:
                        row_data.append(item.text())
                    else:
                        row_data.append("")
                report_lines.append(" | ".join(row_data))
            
            report_lines.append("")
            report_lines.append("=" * 80)
            report_lines.append("پایان گزارش")
            
            # ذخیره فایل
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write('\n'.join(report_lines))
            
            self.show_success(f"✅ گزارش انتخابی با موفقیت ذخیره شد:\n{filepath}")
            
        except Exception as e:
            print(f"❌ خطا در چاپ انتخابی: {e}")
            self.show_error(f"خطا در چاپ انتخابی: {str(e)}")
    
    def show_monthly_summary(self):
        """نمایش گزارش خلاصه ماهانه"""
        try:
            # محاسبه آمار ماه جاری
            today = jdatetime.date.today()
            current_month = today.month
            current_year = today.year
            
            # این بخش نیاز به کوئری خاص برای آمار ماهانه دارد
            # فعلاً یک پیام ساده نمایش می‌دهیم
            self.show_info(f"گزارش ماهانه برای {current_year}/{current_month}\nاین قابلیت در حال توسعه است.")
            
        except Exception as e:
            print(f"❌ خطا در گزارش ماهانه: {e}")
            self.show_error("خطا در تولید گزارش ماهانه")
    
    def show_advanced_search(self):
        """نمایش فرم جستجوی پیشرفته"""
        dialog = AdvancedSearchDialog(self)
        if dialog.exec():
            search_criteria = dialog.get_search_criteria()
            self.apply_advanced_search(search_criteria)
    
    def apply_advanced_search(self, criteria):
        """اعمال جستجوی پیشرفته"""
        print(f"🔍 اعمال جستجوی پیشرفته: {criteria}")
        self.show_info("جستجوی پیشرفته اعمال شد.\nاین قابلیت در حال توسعه است.")
    
    def format_number(self, number):
        """قالب‌بندی اعداد با جداکننده هزارگان"""
        try:
            return f"{int(number):,}"
        except:
            return str(number)
    
    def format_currency(self, amount):
        """قالب‌بندی مبالغ پولی"""
        try:
            return f"{float(amount):,.0f} تومان"
        except:
            return "۰ تومان"