# در فایل account_details_dialog.py

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QTableWidget, QTableWidgetItem,
    QPushButton, QMessageBox, QTabWidget, QWidget, QTextEdit, QHeaderView,
    QGroupBox, QFormLayout, QFrame, QDateEdit
)
from PySide6.QtCore import Qt, QDate
from PySide6.QtGui import QColor
import jdatetime
from datetime import datetime, timedelta

class AccountDetailsDialog(QDialog):
    """دیالوگ نمایش جزئیات حساب - نسخه اصلاح شده"""
    
    def __init__(self, data_manager, account_id, parent=None):
        super().__init__(parent)
        self.data_manager = data_manager
        self.account_id = account_id
        
        # 🔴 **راست‌چین کردن کامل**
        self.setLayoutDirection(Qt.RightToLeft)
        
        self.setup_ui()
        self.setup_styles()
        self.load_account_details()
    
    def setup_ui(self):
        """ایجاد رابط کاربری"""
        self.setWindowTitle("ℹ️ جزئیات حساب")
        self.setMinimumSize(900, 700)
        
        layout = QVBoxLayout()
        
        # 🔴 **تب‌ها**
        self.tab_widget = QTabWidget()
        
        # تب 1: اطلاعات اصلی
        info_tab = QWidget()
        info_layout = QVBoxLayout(info_tab)
        self.setup_info_tab(info_layout)
        self.tab_widget.addTab(info_tab, "📋 اطلاعات حساب")
        
        # تب 2: تراکنش‌ها
        transactions_tab = QWidget()
        transactions_layout = QVBoxLayout(transactions_tab)
        self.setup_transactions_tab(transactions_layout)
        self.tab_widget.addTab(transactions_tab, "💰 تراکنش‌ها")
        
        # تب 3: گزارشات
        reports_tab = QWidget()
        reports_layout = QVBoxLayout(reports_tab)
        self.setup_reports_tab(reports_layout)
        self.tab_widget.addTab(reports_tab, "📊 گزارشات")
        
        layout.addWidget(self.tab_widget)
        
        # 🔴 **دکمه‌ها**
        button_layout = QHBoxLayout()
        
        self.print_button = QPushButton("🖨️ چاپ گزارش")
        self.print_button.clicked.connect(self.print_report)
        
        self.close_button = QPushButton("❌ بستن")
        self.close_button.clicked.connect(self.accept)
        
        button_layout.addWidget(self.print_button)
        button_layout.addStretch()
        button_layout.addWidget(self.close_button)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def setup_styles(self):
        """تنظیم استایل"""
        self.setStyleSheet("""
            QDialog {
                background-color: #000000;
                color: #ffffff;
                font-family: 'B Nazanin';
            }
            
            QLabel {
                color: white;
            }
            
            .info_label {
                font-weight: bold;
                color: #3498db;
                min-width: 150px;
            }
            
            .value_label {
                color: #f1c40f;
                font-size: 11pt;
            }
            
            QTableWidget {
                background-color: #111111;
                alternate-background-color: #0a0a0a;
                gridline-color: #333;
                color: white;
            }
            
            QHeaderView::section {
                background-color: #2c3e50;
                color: white;
                padding: 8px;
                font-weight: bold;
            }
            
            QPushButton {
                padding: 8px 15px;
                border-radius: 5px;
                font-weight: bold;
                min-width: 120px;
                background-color: #27ae60;
                color: white;
            }
            
            QPushButton:hover {
                background-color: #219653;
            }
            
            QPushButton#close_button {
                background-color: #e74c3c;
            }
            
            QPushButton#close_button:hover {
                background-color: #c0392b;
            }
        """)
    
    def setup_info_tab(self, layout):
        """تنظیم تب اطلاعات"""
        # اطلاعات اصلی حساب
        info_group = QGroupBox("اطلاعات اصلی حساب")
        info_form = QFormLayout()
        
        self.account_name_label = QLabel()
        self.account_name_label.setProperty("class", "value_label")
        info_form.addRow("نام حساب:", self.account_name_label)
        
        self.account_number_label = QLabel()
        self.account_number_label.setProperty("class", "value_label")
        info_form.addRow("شماره حساب:", self.account_number_label)
        
        self.account_type_label = QLabel()
        self.account_type_label.setProperty("class", "value_label")
        info_form.addRow("نوع حساب:", self.account_type_label)
        
        self.bank_label = QLabel()
        self.bank_label.setProperty("class", "value_label")
        info_form.addRow("بانک/صندوق:", self.bank_label)
        
        self.owner_label = QLabel()
        self.owner_label.setProperty("class", "value_label")
        info_form.addRow("صاحب حساب:", self.owner_label)
        
        self.initial_balance_label = QLabel()
        self.initial_balance_label.setProperty("class", "value_label")
        info_form.addRow("موجودی اولیه:", self.initial_balance_label)
        
        self.current_balance_label = QLabel()
        self.current_balance_label.setProperty("class", "value_label")
        info_form.addRow("موجودی فعلی:", self.current_balance_label)
        
        self.created_date_label = QLabel()
        self.created_date_label.setProperty("class", "value_label")
        info_form.addRow("تاریخ ایجاد:", self.created_date_label)
        
        self.status_label = QLabel()
        self.status_label.setProperty("class", "value_label")
        info_form.addRow("وضعیت:", self.status_label)
        
        info_group.setLayout(info_form)
        layout.addWidget(info_group)
        
        # توضیحات
        desc_group = QGroupBox("توضیحات")
        desc_layout = QVBoxLayout()
        
        self.description_text = QTextEdit()
        self.description_text.setReadOnly(True)
        self.description_text.setMaximumHeight(150)
        desc_layout.addWidget(self.description_text)
        
        desc_group.setLayout(desc_layout)
        layout.addWidget(desc_group)
        
        layout.addStretch()
    
    def setup_transactions_tab(self, layout):
        """تنظیم تب تراکنش‌ها"""
        # فیلترهای زمانی
        filter_group = QGroupBox("فیلتر زمانی")
        filter_layout = QHBoxLayout()
        
        # تاریخ شروع
        filter_layout.addWidget(QLabel("از تاریخ:"))
        self.from_date_input = QDateEdit()
        self.from_date_input.setCalendarPopup(True)
        self.from_date_input.setDate(QDate.currentDate().addDays(-30))
        self.from_date_input.setDisplayFormat("yyyy/MM/dd")
        
        # تاریخ پایان
        filter_layout.addWidget(QLabel("تا تاریخ:"))
        self.to_date_input = QDateEdit()
        self.to_date_input.setCalendarPopup(True)
        self.to_date_input.setDate(QDate.currentDate())
        self.to_date_input.setDisplayFormat("yyyy/MM/dd")
        
        self.filter_button = QPushButton("🔍 اعمال فیلتر")
        self.filter_button.clicked.connect(self.load_transactions)
        
        filter_layout.addWidget(self.from_date_input)
        filter_layout.addWidget(self.to_date_input)
        filter_layout.addWidget(self.filter_button)
        filter_layout.addStretch()
        
        filter_group.setLayout(filter_layout)
        layout.addWidget(filter_group)
        
        # جدول تراکنش‌ها
        self.transactions_table = QTableWidget()
        self.transactions_table.setColumnCount(7)
        self.transactions_table.setHorizontalHeaderLabels([
            "ردیف",
            "تاریخ",
            "نوع تراکنش",
            "طرف حساب",
            "مبلغ (تومان)",
            "شرح",
            "وضعیت"
        ])
        
        # تنظیم عرض ستون‌ها
        self.transactions_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Fixed)
        self.transactions_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.transactions_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.transactions_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)
        self.transactions_table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeToContents)
        self.transactions_table.horizontalHeader().setSectionResizeMode(5, QHeaderView.Stretch)
        self.transactions_table.horizontalHeader().setSectionResizeMode(6, QHeaderView.ResizeToContents)
        
        self.transactions_table.setColumnWidth(0, 60)   # ردیف
        self.transactions_table.setColumnWidth(1, 120)  # تاریخ
        self.transactions_table.setColumnWidth(2, 120)  # نوع تراکنش
        self.transactions_table.setColumnWidth(4, 150)  # مبلغ
        self.transactions_table.setColumnWidth(6, 100)  # وضعیت
        
        self.transactions_table.setAlternatingRowColors(True)
        
        layout.addWidget(self.transactions_table)
        
        # آمار تراکنش‌ها
        stats_frame = QFrame()
        stats_layout = QHBoxLayout(stats_frame)
        
        self.stats_label = QLabel("در حال بارگذاری...")
        stats_layout.addWidget(self.stats_label)
        stats_layout.addStretch()
        
        layout.addWidget(stats_frame)
    
    def setup_reports_tab(self, layout):
        """تنظیم تب گزارشات"""
        # گزارشات خلاصه
        summary_group = QGroupBox("گزارشات خلاصه")
        summary_layout = QVBoxLayout()
        
        reports = [
            ("📊 گردش ماهانه", self.show_monthly_report),
            ("📈 نمودار درآمد و هزینه", self.show_income_expense_chart),
            ("📋 خلاصه سالانه", self.show_yearly_summary),
            ("🧾 صورت حساب", self.show_account_statement)
        ]
        
        for text, callback in reports:
            btn = QPushButton(text)
            btn.clicked.connect(callback)
            summary_layout.addWidget(btn)
        
        summary_group.setLayout(summary_layout)
        layout.addWidget(summary_group)
        
        layout.addStretch()
    
    def load_account_details(self):
        """بارگذاری اطلاعات حساب"""
        try:
            if not self.account_id:
                return
            
            # استفاده از AccountManager
            account = self.data_manager.account_manager.get_account_by_id(self.account_id)
            
            if not account:
                QMessageBox.warning(self, "خطا", "حساب مورد نظر یافت نشد.")
                self.reject()
                return
            
            # پر کردن اطلاعات
            self.account_name_label.setText(account.get('account_name', ''))
            self.account_number_label.setText(account.get('account_number', ''))
            self.account_type_label.setText(account.get('account_type', ''))
            self.bank_label.setText(account.get('bank_name', 'صندوق فروشگاه'))
            self.owner_label.setText(account.get('owner_name', 'تعیین نشده'))
            
            # موجودی‌ها
            initial_balance = account.get('initial_balance_toman', 0)
            current_balance = account.get('current_balance_toman', 0)
            
            self.initial_balance_label.setText(f"{initial_balance:,.0f} تومان")
            self.current_balance_label.setText(f"{current_balance:,.0f} تومان")
            
            # تاریخ ایجاد (شمسی)
            created_date = account.get('created_at', '')
            if created_date:
                try:
                    jalali_date = self.data_manager.db.gregorian_to_jalali(created_date)
                    self.created_date_label.setText(jalali_date)
                except:
                    self.created_date_label.setText(str(created_date))
            else:
                self.created_date_label.setText("ثبت نشده")
            
            # وضعیت
            is_active = account.get('is_active', 1)
            status_text = "✅ فعال" if is_active else "❌ غیرفعال"
            status_color = "#27ae60" if is_active else "#e74c3c"
            
            self.status_label.setText(status_text)
            self.status_label.setStyleSheet(f"color: {status_color}; font-weight: bold;")
            
            # توضیحات
            self.description_text.setText(account.get('description', 'بدون توضیح'))
            
            # بارگذاری تراکنش‌ها
            self.load_transactions()
            
            # به‌روزرسانی عنوان پنجره
            self.setWindowTitle(f"ℹ️ جزئیات حساب - {account.get('account_name', '')}")
            
        except Exception as e:
            QMessageBox.critical(self, "خطا", f"خطا در بارگذاری اطلاعات حساب:\n\n{str(e)}")
    
    def load_transactions(self):
        """بارگذاری تراکنش‌های حساب"""
        try:
            # تبدیل تاریخ‌ها به فرمت میلادی برای کوئری
            from_date = self.from_date_input.date().toString("yyyy-MM-dd")
            to_date = self.to_date_input.date().toString("yyyy-MM-dd")
            
            # استفاده از AccountManager
            transactions = self.data_manager.account_manager.get_account_transactions(
                self.account_id, from_date, to_date
            )
            
            # پاک کردن جدول
            self.transactions_table.setRowCount(0)
            
            # محاسبه آمار
            total_deposits = 0
            total_withdrawals = 0
            
            # پر کردن جدول
            for row, trans in enumerate(transactions):
                self.transactions_table.insertRow(row)
                
                # ردیف
                self.transactions_table.setItem(row, 0, 
                    QTableWidgetItem(str(row + 1)))
                
                # تاریخ (شمسی)
                trans_date = trans.get('transaction_date_shamsi', '')
                self.transactions_table.setItem(row, 1, 
                    QTableWidgetItem(trans_date))
                
                # نوع تراکنش
                trans_type = trans.get('transaction_type', '')
                direction = trans.get('transaction_direction', '')
                type_text = f"{trans_type} ({direction})"
                type_item = QTableWidgetItem(type_text)
                
                # رنگ‌بندی
                if direction == "واریز":
                    type_item.setForeground(QColor('#27ae60'))  # سبز
                    total_deposits += float(trans.get('amount_toman', 0))
                else:
                    type_item.setForeground(QColor('#e74c3c'))  # قرمز
                    total_withdrawals += float(trans.get('amount_toman', 0))
                
                self.transactions_table.setItem(row, 2, type_item)
                
                # طرف حساب
                other_account = trans.get('from_account_name', '') if direction == 'برداشت' else trans.get('to_account_name', '')
                self.transactions_table.setItem(row, 3, 
                    QTableWidgetItem(other_account))
                
                # مبلغ (تومان)
                amount = float(trans.get('amount_toman', 0))
                amount_item = QTableWidgetItem(f"{amount:,.0f}")
                amount_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                
                if direction == "واریز":
                    amount_item.setForeground(QColor('#27ae60'))
                else:
                    amount_item.setForeground(QColor('#e74c3c'))
                
                self.transactions_table.setItem(row, 4, amount_item)
                
                # شرح
                self.transactions_table.setItem(row, 5, 
                    QTableWidgetItem(trans.get('description', '')))
                
                # وضعیت
                status_item = QTableWidgetItem(trans.get('status', 'انجام شده'))
                status_item.setForeground(QColor('#f39c12'))
                self.transactions_table.setItem(row, 6, status_item)
            
            # به‌روزرسانی آمار
            self.stats_label.setText(
                f"تعداد تراکنش‌ها: {len(transactions)} | "
                f"مجموع واریزها: {total_deposits:,.0f} تومان | "
                f"مجموع برداشت‌ها: {total_withdrawals:,.0f} تومان"
            )
            
        except Exception as e:
            print(f"⚠️ خطا در بارگذاری تراکنش‌ها: {e}")
            self.transactions_table.setRowCount(0)
    
    def print_report(self):
        """چاپ گزارش"""
        QMessageBox.information(self, "چاپ گزارش", 
            "🖨️ گزارش حساب آماده چاپ است.\n\nاین قابلیت به زودی فعال خواهد شد.")
    
    def show_monthly_report(self):
        """نمایش گزارش ماهانه"""
        QMessageBox.information(self, "گزارش ماهانه", 
            "📊 گزارش ماهانه حساب.\n\nاین قابلیت به زودی فعال خواهد شد.")
    
    def show_income_expense_chart(self):
        """نمایش نمودار درآمد و هزینه"""
        QMessageBox.information(self, "نمودار", 
            "📈 نمودار درآمد و هزینه حساب.\n\nاین قابلیت به زودی فعال خواهد شد.")
    
    def show_yearly_summary(self):
        """نمایش خلاصه سالانه"""
        QMessageBox.information(self, "خلاصه سالانه", 
            "📋 خلاصه سالانه حساب.\n\nاین قابلیت به زودی فعال خواهد شد.")
    
    def show_account_statement(self):
        """نمایش صورت حساب"""
        QMessageBox.information(self, "صورت حساب", 
            "🧾 صورت حساب حساب.\n\nاین قابلیت به زودی فعال خواهد شد.")