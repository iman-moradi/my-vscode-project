# daily_summary_form.py - نسخه اصلاح شده

"""
فرم خلاصه روزانه - نسخه اصلاح شده با تاریخ شمسی
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QGroupBox,
    QFrame, QMessageBox, QSpacerItem, QSizePolicy
)
from PySide6.QtCore import Qt, Signal, QTimer
from PySide6.QtGui import QFont, QColor
import jdatetime
from datetime import datetime as dt
import locale

# وارد کردن ویجت تاریخ شمسی
from ui.forms.accounting.widgets.jalali_date_input import JalaliDateInputAccounting


class DailySummaryForm(QWidget):
    """فرم خلاصه روزانه حسابداری با تاریخ شمسی - نسخه اصلاح شده"""
    
    # سیگنال‌های جدید
    refresh_requested = Signal(str)  # تاریخ شمسی برای بارگذاری مجدد
    summary_loaded = Signal(dict)    # اطلاعات خلاصه بارگذاری شده
    
    def __init__(self, data_manager=None):
        super().__init__()
        self.data_manager = data_manager
        self.summary_data = {}
        self.current_jalali_date = jdatetime.date.today()
        
        # تنظیمات اولیه
        try:
            locale.setlocale(locale.LC_ALL, 'fa_IR.UTF-8')
        except:
            pass
        
        # 🔴 **راست‌چین کردن کامل**
        self.setLayoutDirection(Qt.RightToLeft)
        
        self.setup_ui()
        self.setup_styles()
        
        # بارگذاری اولیه
        QTimer.singleShot(100, self.load_today_summary)
    
    def setup_ui(self):
        """ایجاد رابط کاربری - نسخه ساده‌تر"""
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # 🔴 **هدر فرم**
        header_layout = QHBoxLayout()
        
        # عنوان
        title_label = QLabel("📊 خلاصه روزانه حسابداری")
        title_label.setObjectName("title_label")
        
        # ویجت تاریخ شمسی
        date_group = QGroupBox("تاریخ:")
        date_layout = QHBoxLayout()
        
        self.date_widget = JalaliDateInputAccounting(
            mode='edit',
            date_format='persian',
            theme='dark',
            show_today_button=True,
            show_calendar_button=True
        )
        self.date_widget.set_date_string(
            self.current_jalali_date.strftime("%Y/%m/%d")
        )
        self.date_widget.date_changed.connect(self.on_date_changed)
        
        date_layout.addWidget(self.date_widget)
        date_group.setLayout(date_layout)
        
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        header_layout.addWidget(date_group)
        
        layout.addLayout(header_layout)
        
        # 🔴 **آمار کلیدی**
        stats_frame = QFrame()
        stats_frame.setObjectName("stats_frame")
        stats_layout = QHBoxLayout(stats_frame)
        stats_layout.setSpacing(10)
        
        self.stats_cards = {}
        
        # آمار ساده‌تر - فقط مواردی که در دیتابیس وجود دارند
        stats_config = [
            ("💰 مجموع دریافتی", "0", "#27ae60", "total_income"),
            ("💸 مجموع پرداختی", "0", "#e74c3c", "total_expense"),
            ("📈 مانده روز", "0", "#3498db", "daily_balance"),
            ("🧾 تعداد تراکنش", "0", "#9b59b6", "transaction_count")
        ]
        
        for title, value, color, key in stats_config:
            card = self.create_stat_card(title, value, color)
            stats_layout.addWidget(card)
            self.stats_cards[key] = card
        
        layout.addWidget(stats_frame)
        
        # 🔴 **خلاصه دریافتی‌ها**
        income_group = QGroupBox("💰 دریافتی‌های امروز")
        income_layout = QVBoxLayout()
        
        self.income_table = QTableWidget()
        self.income_table.setColumnCount(5)  # کاهش ستون‌ها
        self.income_table.setHorizontalHeaderLabels([
            "ردیف",
            "زمان",
            "حساب",
            "مبلغ (ریال)",
            "توضیحات"
        ])
        self.income_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.income_table.setAlternatingRowColors(True)
        
        income_layout.addWidget(self.income_table)
        income_group.setLayout(income_layout)
        
        # 🔴 **خلاصه پرداختی‌ها**
        expense_group = QGroupBox("💸 پرداختی‌های امروز")
        expense_layout = QVBoxLayout()
        
        self.expense_table = QTableWidget()
        self.expense_table.setColumnCount(5)  # کاهش ستون‌ها
        self.expense_table.setHorizontalHeaderLabels([
            "ردیف",
            "زمان",
            "حساب",
            "مبلغ (ریال)",
            "توضیحات"
        ])
        self.expense_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.expense_table.setAlternatingRowColors(True)
        
        expense_layout.addWidget(self.expense_table)
        expense_group.setLayout(expense_layout)
        
        # تیغه برای نمایش همزمان دو جدول
        split_layout = QHBoxLayout()
        split_layout.addWidget(income_group)
        split_layout.addWidget(expense_group)
        
        layout.addLayout(split_layout)
        
        # 🔴 **اطلاعات روز**
        day_info_frame = QFrame()
        day_info_frame.setObjectName("day_info_frame")
        day_info_layout = QVBoxLayout(day_info_frame)
        
        self.day_info_label = QLabel("در حال بارگذاری...")
        self.day_info_label.setWordWrap(True)
        self.day_info_label.setStyleSheet("""
            QLabel {
                font-size: 11pt;
                padding: 10px;
                border-radius: 6px;
                background-color: #2c3e50;
                color: white;
            }
        """)
        
        day_info_layout.addWidget(self.day_info_label)
        
        layout.addWidget(day_info_frame)
        
        # 🔴 **دکمه‌های عملیاتی**
        button_layout = QHBoxLayout()
        
        self.refresh_button = QPushButton("🔄 بروزرسانی")
        self.refresh_button.clicked.connect(self.refresh_data)
        
        self.print_button = QPushButton("🖨️ چاپ گزارش")
        self.print_button.clicked.connect(self.print_summary)
        
        button_layout.addWidget(self.refresh_button)
        button_layout.addWidget(self.print_button)
        button_layout.addStretch()
        
        layout.addLayout(button_layout)
        
        # 🔴 **نوار وضعیت**
        status_bar = QFrame()
        status_bar.setObjectName("status_bar")
        status_layout = QHBoxLayout(status_bar)
        
        self.status_label = QLabel("آماده")
        self.status_label.setObjectName("status_label")
        
        self.last_update_label = QLabel("آخرین بروزرسانی: -")
        self.last_update_label.setObjectName("last_update_label")
        
        status_layout.addWidget(self.status_label)
        status_layout.addStretch()
        status_layout.addWidget(self.last_update_label)
        
        layout.addWidget(status_bar)
        
        self.setLayout(layout)
        
        # تنظیم اندازه‌های نسبی
        self.setMinimumSize(1200, 800)
    
    def setup_styles(self):
        """تنظیم استایل"""
        self.setStyleSheet("""
            QWidget {
                background-color: #000000;
                color: #ffffff;
                font-family: 'B Nazanin';
            }
            
            #title_label {
                font-size: 18pt;
                font-weight: bold;
                color: #2ecc71;
                padding: 5px;
            }
            
            #stats_frame {
                background-color: #111111;
                border: 1px solid #333;
                border-radius: 8px;
                padding: 15px;
            }
            
            .stat_card {
                background-color: #222222;
                border: 2px solid #444;
                border-radius: 6px;
                padding: 15px;
                min-width: 200px;
            }
            
            .stat_card_title {
                color: #bbb;
                font-size: 11pt;
                font-weight: bold;
            }
            
            .stat_card_value {
                color: white;
                font-size: 16pt;
                font-weight: bold;
            }
            
            QGroupBox {
                font-weight: bold;
                border: 1px solid #444;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
                font-size: 11pt;
            }
            
            QGroupBox::title {
                subcontrol-origin: margin;
                right: 10px;
                padding: 0 10px 0 10px;
                color: #3498db;
            }
            
            QTableWidget {
                background-color: #111111;
                alternate-background-color: #0a0a0a;
                gridline-color: #333;
                color: white;
                font-size: 10pt;
                border: none;
            }
            
            QTableWidget::item {
                padding: 8px;
                border-bottom: 1px solid #222;
            }
            
            QTableWidget::item:selected {
                background-color: #27ae60;
                color: white;
            }
            
            QHeaderView::section {
                background-color: #2c3e50;
                color: white;
                padding: 10px;
                font-weight: bold;
                text-align: center;
                border: none;
                font-size: 10pt;
            }
            
            QPushButton {
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
                min-width: 120px;
                font-size: 10pt;
                border: 1px solid #444;
            }
            
            QPushButton:hover {
                border-color: #27ae60;
                background-color: #222;
            }
            
            QPushButton:pressed {
                background-color: #27ae60;
            }
            
            #day_info_frame {
                background-color: #111111;
                border: 1px solid #333;
                border-radius: 8px;
                padding: 15px;
            }
            
            #status_bar {
                background-color: #111111;
                border-top: 1px solid #333;
                padding: 8px;
            }
            
            #status_label {
                color: #27ae60;
                font-weight: bold;
            }
            
            #last_update_label {
                color: #999;
                font-size: 9pt;
            }
        """)
    
    def create_stat_card(self, title: str, value: str, color: str) -> QFrame:
        """ایجاد کارت آمار"""
        card = QFrame()
        card.setObjectName("stat_card")
        card.setStyleSheet(f"border-color: {color};")
        
        layout = QVBoxLayout(card)
        layout.setSpacing(5)
        
        # عنوان
        title_label = QLabel(title)
        title_label.setObjectName("stat_card_title")
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        # مقدار
        value_label = QLabel(value)
        value_label.setObjectName("stat_card_value")
        value_label.setAlignment(Qt.AlignCenter)
        value_label.setStyleSheet(f"color: {color};")
        layout.addWidget(value_label)
        
        # ذخیره رفرنس
        card.value_label = value_label
        
        return card
    
    def load_today_summary(self):
        """بارگذاری خلاصه امروز"""
        today_jalali = jdatetime.date.today()
        self.date_widget.set_date_string(today_jalali.strftime("%Y/%m/%d"))
        self.load_summary_for_date(today_jalali)
    
    def on_date_changed(self, date_str: str):
        """هنگام تغییر تاریخ در ویجت"""
        try:
            if date_str:  # فقط اگر تاریخ وارد شده باشد
                jalali_date = jdatetime.datetime.strptime(date_str, "%Y/%m/%d").date()
                self.load_summary_for_date(jalali_date)
        except ValueError:
            print(f"⚠️ تاریخ نامعتبر: {date_str}")
            # در صورت خطا، تاریخ امروز را تنظیم کن
            self.load_today_summary()
    
    def load_summary_for_date(self, jalali_date: jdatetime.date):
        """بارگذاری خلاصه برای تاریخ مشخص شمسی"""
        try:
            self.current_jalali_date = jalali_date
            
            # تبدیل به میلادی برای کوئری دیتابیس
            gregorian_date = jalali_date.togregorian()
            date_str = gregorian_date.strftime("%Y-%m-%d")
            
            # به‌روزرسانی وضعیت
            self.status_label.setText("در حال بارگذاری...")
            
            if self.data_manager:
                # 🔴 **بارگذاری آمار کلیدی**
                self.load_summary_stats(date_str)
                
                # 🔴 **بارگذاری جزئیات دریافتی‌ها**
                self.load_income_details(date_str)
                
                # 🔴 **بارگذاری جزئیات پرداختی‌ها**
                self.load_expense_details(date_str)
                
                # 🔴 **بارگذاری اطلاعات روز**
                self.load_day_info(jalali_date)
            
            # به‌روزرسانی برچسب آخرین بروزرسانی
            current_time = dt.now().strftime("%H:%M:%S")
            persian_time = self.english_to_persian_numbers(current_time)
            self.last_update_label.setText(f"آخرین بروزرسانی: {persian_time}")
            
            self.status_label.setText("آماده")
            
            # ارسال سیگنال
            if hasattr(self, 'summary_loaded'):
                self.summary_loaded.emit(self.summary_data)
            
        except Exception as e:
            print(f"⚠️ خطا در بارگذاری خلاصه: {e}")
            self.status_label.setText(f"خطا: {str(e)[:50]}")
            QMessageBox.warning(self, "خطا", f"خطا در بارگذاری داده‌ها:\n{str(e)[:100]}")
    
    def load_summary_stats(self, date_str: str):
        """بارگذاری آمار کلیدی - نسخه اصلاح شده"""
        try:
            # مجموع دریافتی‌ها
            income_query = """
            SELECT SUM(amount) as total 
            FROM AccountingTransactions 
            WHERE transaction_type = 'دریافت' 
            AND DATE(transaction_date) = ?
            """
            income_result = self.data_manager.db.fetch_one(income_query, (date_str,))
            income_total = income_result.get('total', 0) if income_result else 0
            
            # مجموع پرداختی‌ها
            expense_query = """
            SELECT SUM(amount) as total 
            FROM AccountingTransactions 
            WHERE transaction_type = 'پرداخت' 
            AND DATE(transaction_date) = ?
            """
            expense_result = self.data_manager.db.fetch_one(expense_query, (date_str,))
            expense_total = expense_result.get('total', 0) if expense_result else 0
            
            # تعداد تراکنش‌ها
            count_query = """
            SELECT COUNT(*) as count 
            FROM AccountingTransactions 
            WHERE DATE(transaction_date) = ?
            """
            count_result = self.data_manager.db.fetch_one(count_query, (date_str,))
            transaction_count = count_result.get('count', 0) if count_result else 0
            
            # محاسبه مانده روز
            daily_balance = income_total - expense_total
            
            # ذخیره داده‌ها
            self.summary_data = {
                'total_income': income_total,
                'total_expense': expense_total,
                'daily_balance': daily_balance,
                'transaction_count': transaction_count,
                'date': self.current_jalali_date
            }
            
            # به‌روزرسانی کارت‌ها
            if 'total_income' in self.stats_cards:
                self.stats_cards['total_income'].value_label.setText(
                    f"{self.format_currency(income_total)}"
                )
            
            if 'total_expense' in self.stats_cards:
                self.stats_cards['total_expense'].value_label.setText(
                    f"{self.format_currency(expense_total)}"
                )
            
            if 'daily_balance' in self.stats_cards:
                balance_color = "#27ae60" if daily_balance >= 0 else "#e74c3c"
                self.stats_cards['daily_balance'].value_label.setStyleSheet(
                    f"color: {balance_color};"
                )
                self.stats_cards['daily_balance'].value_label.setText(
                    f"{self.format_currency(daily_balance)}"
                )
            
            if 'transaction_count' in self.stats_cards:
                persian_count = self.english_to_persian_numbers(str(transaction_count))
                self.stats_cards['transaction_count'].value_label.setText(
                    f"{persian_count} تراکنش"
                )
                
        except Exception as e:
            print(f"⚠️ خطا در بارگذاری آمار: {e}")
    
    def load_income_details(self, date_str: str):
        """بارگذاری جزئیات دریافتی‌ها - نسخه اصلاح شده"""
        try:
            # کوئری ساده‌تر بدون ستون‌های ناموجود
            income_details_query = """
            SELECT 
                ROW_NUMBER() OVER (ORDER BY t.created_at) as row_num,
                TIME(t.created_at) as time,
                COALESCE(a.account_name, 'حساب نقدی') as account_name,
                t.amount,
                t.description
            FROM AccountingTransactions t
            LEFT JOIN Accounts a ON t.from_account_id = a.id
            WHERE t.transaction_type = 'دریافت' 
            AND DATE(t.transaction_date) = ?
            ORDER BY t.created_at DESC
            """
            income_details = self.data_manager.db.fetch_all(income_details_query, (date_str,))
            
            self.income_table.setRowCount(len(income_details))
            
            for row, trans in enumerate(income_details):
                # ردیف
                row_num = trans.get('row_num', row + 1)
                row_item = QTableWidgetItem(self.english_to_persian_numbers(str(row_num)))
                row_item.setTextAlignment(Qt.AlignCenter)
                self.income_table.setItem(row, 0, row_item)
                
                # زمان
                time_val = trans.get('time', '')
                if time_val:
                    time_str = str(time_val)[:8]  # فقط ساعت:دقیقه:ثانیه
                    time_item = QTableWidgetItem(time_str)
                else:
                    time_item = QTableWidgetItem("-")
                time_item.setTextAlignment(Qt.AlignCenter)
                self.income_table.setItem(row, 1, time_item)
                
                # حساب
                account_name = trans.get('account_name', 'نامشخص')
                account_item = QTableWidgetItem(account_name)
                self.income_table.setItem(row, 2, account_item)
                
                # مبلغ
                amount = trans.get('amount', 0)
                amount_text = self.format_currency(amount)
                amount_item = QTableWidgetItem(amount_text)
                amount_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                amount_item.setForeground(QColor("#27ae60"))
                self.income_table.setItem(row, 3, amount_item)
                
                # توضیحات
                description = trans.get('description', '')
                description_item = QTableWidgetItem(description)
                self.income_table.setItem(row, 4, description_item)
            
        except Exception as e:
            print(f"⚠️ خطا در بارگذاری دریافتی‌ها: {e}")
            self.income_table.setRowCount(0)
    
    def load_expense_details(self, date_str: str):
        """بارگذاری جزئیات پرداختی‌ها - نسخه اصلاح شده"""
        try:
            expense_details_query = """
            SELECT 
                ROW_NUMBER() OVER (ORDER BY t.created_at) as row_num,
                TIME(t.created_at) as time,
                COALESCE(a.account_name, 'حساب نقدی') as account_name,
                t.amount,
                t.description
            FROM AccountingTransactions t
            LEFT JOIN Accounts a ON t.from_account_id = a.id
            WHERE t.transaction_type = 'پرداخت' 
            AND DATE(t.transaction_date) = ?
            ORDER BY t.created_at DESC
            """
            expense_details = self.data_manager.db.fetch_all(expense_details_query, (date_str,))
            
            self.expense_table.setRowCount(len(expense_details))
            
            for row, trans in enumerate(expense_details):
                # ردیف
                row_num = trans.get('row_num', row + 1)
                row_item = QTableWidgetItem(self.english_to_persian_numbers(str(row_num)))
                row_item.setTextAlignment(Qt.AlignCenter)
                self.expense_table.setItem(row, 0, row_item)
                
                # زمان
                time_val = trans.get('time', '')
                if time_val:
                    time_str = str(time_val)[:8]
                    time_item = QTableWidgetItem(time_str)
                else:
                    time_item = QTableWidgetItem("-")
                time_item.setTextAlignment(Qt.AlignCenter)
                self.expense_table.setItem(row, 1, time_item)
                
                # حساب
                account_name = trans.get('account_name', 'نامشخص')
                account_item = QTableWidgetItem(account_name)
                self.expense_table.setItem(row, 2, account_item)
                
                # مبلغ
                amount = trans.get('amount', 0)
                amount_text = self.format_currency(amount)
                amount_item = QTableWidgetItem(amount_text)
                amount_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                amount_item.setForeground(QColor("#e74c3c"))
                self.expense_table.setItem(row, 3, amount_item)
                
                # توضیحات
                description = trans.get('description', '')
                description_item = QTableWidgetItem(description)
                self.expense_table.setItem(row, 4, description_item)
            
        except Exception as e:
            print(f"⚠️ خطا در بارگذاری پرداختی‌ها: {e}")
            self.expense_table.setRowCount(0)
    
    def load_day_info(self, jalali_date: jdatetime.date):
        """بارگذاری اطلاعات روز - نسخه اصلاح شده"""
        try:
            weekday_names = ["شنبه", "یکشنبه", "دوشنبه", "سه‌شنبه", "چهارشنبه", "پنجشنبه", "جمعه"]
            month_names = [
                "فروردین", "اردیبهشت", "خرداد", "تیر", "مرداد", "شهریور",
                "مهر", "آبان", "آذر", "دی", "بهمن", "اسفند"
            ]
            
            weekday = weekday_names[jalali_date.weekday()]
            month_name = month_names[jalali_date.month - 1]
            day_name = self.english_to_persian_numbers(str(jalali_date.day))
            
            # محاسبه روز سال شمسی
            day_of_year = self._get_jalali_day_of_year(jalali_date)
            
            day_info_text = f"""
            <div style='color: #3498db; font-size: 12pt;'>
                📅 {weekday}، {day_name} {month_name} {self.english_to_persian_numbers(str(jalali_date.year))}
            </div>
            <div style='color: #ddd; margin-top: 10px; font-size: 10pt;'>
                معادل میلادی: {jalali_date.togregorian().strftime("%Y/%m/%d")}<br>
                روز {self.english_to_persian_numbers(str(day_of_year))} از سال شمسی
            </div>
            """
            
            self.day_info_label.setText(day_info_text)
            
        except Exception as e:
            print(f"⚠️ خطا در بارگذاری اطلاعات روز: {e}")
            self.day_info_label.setText("خطا در بارگذاری اطلاعات روز")
    
    def _get_jalali_day_of_year(self, jalali_date: jdatetime.date) -> int:
        """محاسبه روز سال برای تاریخ شمسی"""
        try:
            day_of_year = 0
            for month in range(1, jalali_date.month):
                if month <= 6:
                    day_of_year += 31
                elif month <= 11:
                    day_of_year += 30
                else:  # اسفند
                    day_of_year += 29 if jalali_date.isleap() else 28
            
            day_of_year += jalali_date.day
            return day_of_year
        except:
            return 0
    
    def refresh_data(self):
        """بروزرسانی داده‌ها"""
        date_str = self.date_widget.get_date()
        if date_str:
            try:
                jalali_date = jdatetime.datetime.strptime(date_str, "%Y/%m/%d").date()
                self.load_summary_for_date(jalali_date)
                if hasattr(self, 'refresh_requested'):
                    self.refresh_requested.emit(date_str)
            except ValueError:
                self.load_today_summary()
    
    def print_summary(self):
        """چاپ گزارش"""
        try:
            date_str = self.date_widget.get_date()
            if not date_str:
                date_str = jdatetime.date.today().strftime("%Y/%m/%d")
            
            # ایجاد گزارش چاپ
            report_text = self.generate_print_report()
            
            QMessageBox.information(
                self,
                "چاپ گزارش",
                f"📄 گزارش تاریخ {date_str} آماده چاپ است.\n\n"
                f"تعداد دریافتی: {self.income_table.rowCount()}\n"
                f"تعداد پرداختی: {self.expense_table.rowCount()}\n"
                f"دریافتی کل: {self.format_currency(self.summary_data.get('total_income', 0))}\n"
                f"پرداختی کل: {self.format_currency(self.summary_data.get('total_expense', 0))}"
            )
            
        except Exception as e:
            QMessageBox.warning(self, "خطا در چاپ", f"خطا در آماده‌سازی گزارش: {str(e)}")
    
    # ------------------ متدهای کمکی ------------------
    
    @staticmethod
    def english_to_persian_numbers(text: str) -> str:
        """تبدیل اعداد انگلیسی به فارسی"""
        persian_nums = {
            '0': '۰', '1': '۱', '2': '۲', '3': '۳', '4': '۴',
            '5': '۵', '6': '۶', '7': '۷', '8': '۸', '9': '۹',
            '.': '.', ',': '،'
        }
        
        result = []
        for char in str(text):
            result.append(persian_nums.get(char, char))
        
        return ''.join(result)
    
    def format_currency(self, amount: float) -> str:
        """فرمت‌دهی مبلغ به صورت ریال"""
        try:
            # تبدیل به عدد صحیح
            amount_int = int(amount)
            
            # فرمت با جداکننده هزارگان
            formatted = f"{amount_int:,}"
            
            # تبدیل اعداد به فارسی
            persian_formatted = self.english_to_persian_numbers(formatted)
            
            return f"{persian_formatted} ریال"
        except:
            return "۰ ریال"
    
    def generate_print_report(self) -> str:
        """ایجاد متن گزارش برای چاپ"""
        date_str = self.date_widget.get_date()
        jalali_date = self.current_jalali_date
        
        report_lines = []
        report_lines.append("=" * 60)
        report_lines.append(f"گزارش خلاصه روزانه حسابداری")
        report_lines.append(f"تاریخ: {date_str}")
        report_lines.append(f"تاریخ میلادی: {jalali_date.togregorian().strftime('%Y/%m/%d')}")
        report_lines.append("=" * 60)
        report_lines.append("")
        
        # آمار کلیدی
        report_lines.append("📊 آمار کلیدی:")
        report_lines.append(f"  مجموع دریافتی: {self.format_currency(self.summary_data.get('total_income', 0))}")
        report_lines.append(f"  مجموع پرداختی: {self.format_currency(self.summary_data.get('total_expense', 0))}")
        report_lines.append(f"  مانده روز: {self.format_currency(self.summary_data.get('daily_balance', 0))}")
        report_lines.append(f"  تعداد تراکنش: {self.summary_data.get('transaction_count', 0)}")
        report_lines.append("")
        
        # خلاصه دریافتی‌ها
        report_lines.append("💰 دریافتی‌ها:")
        report_lines.append("-" * 40)
        
        for row in range(self.income_table.rowCount()):
            time_item = self.income_table.item(row, 1)
            account_item = self.income_table.item(row, 2)
            amount_item = self.income_table.item(row, 3)
            
            if all([time_item, account_item, amount_item]):
                report_lines.append(
                    f"  {time_item.text()} | {account_item.text()} | {amount_item.text()}"
                )
        
        report_lines.append("")
        
        # خلاصه پرداختی‌ها
        report_lines.append("💸 پرداختی‌ها:")
        report_lines.append("-" * 40)
        
        for row in range(self.expense_table.rowCount()):
            time_item = self.expense_table.item(row, 1)
            account_item = self.expense_table.item(row, 2)
            amount_item = self.expense_table.item(row, 3)
            
            if all([time_item, account_item, amount_item]):
                report_lines.append(
                    f"  {time_item.text()} | {account_item.text()} | {amount_item.text()}"
                )
        
        report_lines.append("")
        report_lines.append("=" * 60)
        report_lines.append(f"تاریخ ایجاد گزارش: {dt.now().strftime('%Y/%m/%d %H:%M:%S')}")
        
        return "\n".join(report_lines)
    
    def set_data_manager(self, data_manager):
        """تنظیم مدیریت داده‌ها"""
        self.data_manager = data_manager
        self.refresh_data()
    
    def get_current_date(self) -> str:
        """دریافت تاریخ جاری"""
        return self.date_widget.get_date()
    
    def get_summary_data(self) -> dict:
        """دریافت داده‌های خلاصه"""
        return self.summary_data.copy()


class DailySummaryDialog(QWidget):
    """دیالوگ خلاصه روزانه (برای پنجره اصلی) - نسخه اصلاح شده"""
    
    def __init__(self, data_manager, parent=None):
        super().__init__(parent)
        self.data_manager = data_manager
        
        self.setup_ui()
        self.setup_styles()
        
        # بارگذاری اولیه
        QTimer.singleShot(100, self.load_summary)
    
    def setup_ui(self):
        """ایجاد رابط کاربری"""
        self.setWindowTitle("📋 خلاصه روزانه حسابداری")
        self.setMinimumSize(1200, 800)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # استفاده از فرم خلاصه روزانه
        self.summary_form = DailySummaryForm(self.data_manager)
        layout.addWidget(self.summary_form)
        
        # دکمه بستن
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.close_button = QPushButton("❌ بستن")
        self.close_button.clicked.connect(self.close)
        self.close_button.setFixedWidth(150)
        
        button_layout.addWidget(self.close_button)
        layout.addLayout(button_layout)
    
    def setup_styles(self):
        """تنظیم استایل دیالوگ"""
        self.setStyleSheet("""
            QWidget {
                background-color: #000000;
                color: #ffffff;
                font-family: 'B Nazanin';
            }
            
            QPushButton {
                padding: 12px 25px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 11pt;
                background-color: #2c3e50;
                color: white;
                border: 1px solid #34495e;
            }
            
            QPushButton:hover {
                background-color: #34495e;
                border-color: #27ae60;
            }
            
            QPushButton:pressed {
                background-color: #27ae60;
            }
        """)
    
    def load_summary(self):
        """بارگذاری خلاصه"""
        self.summary_form.load_today_summary()


# تست فرم
if __name__ == "__main__":
    import sys
    from PySide6.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    
    # تنظیم فونت فارسی
    font = QFont("B Nazanin", 11)
    app.setFont(font)
    
    # ایجاد فرم تست
    form = DailySummaryForm()
    form.setWindowTitle("تست فرم خلاصه روزانه با تاریخ شمسی")
    form.resize(1200, 800)
    form.show()
    
    sys.exit(app.exec())