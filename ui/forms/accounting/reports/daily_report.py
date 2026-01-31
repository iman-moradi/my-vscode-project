"""
گزارش روزانه حسابداری
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QDateEdit,
    QGroupBox, QFormLayout, QTextEdit, QMessageBox
)
from PySide6.QtCore import Qt, QDate
from PySide6.QtGui import QFont


class DailyReportDialog(QDialog):
    """دیالوگ گزارش روزانه"""
    
    def __init__(self, data_manager, parent=None):
        super().__init__(parent)
        self.data_manager = data_manager
        
        # 🔴 **راست‌چین کردن کامل**
        self.setLayoutDirection(Qt.RightToLeft)
        
        self.setup_ui()
        self.setup_styles()
        self.load_today_report()
    
    def setup_ui(self):
        """ایجاد رابط کاربری"""
        self.setWindowTitle("📅 گزارش روزانه حسابداری")
        self.setMinimumSize(1000, 700)
        
        layout = QVBoxLayout()
        
        # 🔴 **هدر گزارش**
        header_layout = QHBoxLayout()
        
        # انتخاب تاریخ
        date_group = QGroupBox("انتخاب تاریخ:")
        date_form = QFormLayout()
        
        self.date_input = QDateEdit()
        self.date_input.setCalendarPopup(True)
        self.date_input.setDate(QDate.currentDate())
        self.date_input.setDisplayFormat("yyyy/MM/dd")
        self.date_input.dateChanged.connect(self.on_date_changed)
        
        date_form.addRow("تاریخ گزارش:", self.date_input)
        date_group.setLayout(date_form)
        
        header_layout.addWidget(date_group)
        header_layout.addStretch()
        
        # دکمه‌های عملیاتی
        self.print_button = QPushButton("🖨️ چاپ گزارش")
        self.print_button.clicked.connect(self.print_report)
        
        self.export_button = QPushButton("📤 خروجی اکسل")
        self.export_button.clicked.connect(self.export_report)
        
        self.close_button = QPushButton("❌ بستن")
        self.close_button.clicked.connect(self.reject)
        
        header_layout.addWidget(self.print_button)
        header_layout.addWidget(self.export_button)
        header_layout.addWidget(self.close_button)
        
        layout.addLayout(header_layout)
        
        # 🔴 **آمار خلاصه**
        summary_group = QGroupBox("📊 خلاصه مالی روز")
        summary_layout = QHBoxLayout()
        
        self.summary_labels = {}
        
        summary_items = [
            ("💰 دریافتی‌ها", "0 ریال", "#27ae60"),
            ("💸 پرداختی‌ها", "0 ریال", "#e74c3c"),
            ("🔄 انتقالات", "0 ریال", "#3498db"),
            ("🏦 موجودی کل", "0 ریال", "#f39c12")
        ]
        
        for title, value, color in summary_items:
            summary_card = QLabel(f"<h3>{title}</h3><p style='font-size: 16pt; color: {color};'>{value}</p>")
            summary_card.setAlignment(Qt.AlignCenter)
            summary_card.setStyleSheet(f"""
                border: 2px solid {color};
                border-radius: 8px;
                padding: 10px;
                background-color: #111111;
            """)
            summary_layout.addWidget(summary_card)
            self.summary_labels[title] = summary_card
        
        summary_group.setLayout(summary_layout)
        layout.addWidget(summary_group)
        
        # 🔴 **جدول تراکنش‌های روز**
        self.transactions_table = QTableWidget()
        self.transactions_table.setColumnCount(7)
        self.transactions_table.setHorizontalHeaderLabels([
            "ردیف",
            "زمان",
            "نوع",
            "حساب",
            "مبلغ (ریال)",
            "دسته‌بندی",
            "توضیحات"
        ])
        
        # تنظیمات جدول
        self.transactions_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.transactions_table.setAlternatingRowColors(True)
        
        layout.addWidget(QLabel("📋 تراکنش‌های روز:"))
        layout.addWidget(self.transactions_table)
        
        # 🔴 **یادداشت روز**
        notes_group = QGroupBox("📝 یادداشت‌های روز")
        notes_layout = QVBoxLayout()
        
        self.notes_input = QTextEdit()
        self.notes_input.setPlaceholderText("یادداشت‌ها و توضیحات روزانه...")
        self.notes_input.setMaximumHeight(100)
        
        self.save_notes_button = QPushButton("💾 ذخیره یادداشت")
        self.save_notes_button.clicked.connect(self.save_notes)
        
        notes_layout.addWidget(self.notes_input)
        notes_layout.addWidget(self.save_notes_button)
        notes_group.setLayout(notes_layout)
        
        layout.addWidget(notes_group)
        
        self.setLayout(layout)
    
    def setup_styles(self):
        """تنظیم استایل"""
        self.setStyleSheet("""
            QDialog {
                background-color: #000000;
                color: #ffffff;
                font-family: 'B Nazanin';
            }
            
            QGroupBox {
                font-weight: bold;
                border: 1px solid #444;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
            
            QTableWidget {
                background-color: #111111;
                alternate-background-color: #0a0a0a;
                gridline-color: #333;
                color: white;
                font-size: 11pt;
            }
            
            QHeaderView::section {
                background-color: #2c3e50;
                color: white;
                padding: 10px;
                font-weight: bold;
                text-align: center;
            }
            
            QPushButton {
                padding: 8px 15px;
                border-radius: 5px;
                font-weight: bold;
                min-width: 120px;
            }
        """)
    
    def load_today_report(self):
        """بارگذاری گزارش روز جاری"""
        self.load_report_for_date(QDate.currentDate())
    
    def on_date_changed(self, date):
        """هنگام تغییر تاریخ"""
        self.load_report_for_date(date)
    
    def load_report_for_date(self, date):
        """بارگذاری گزارش برای تاریخ مشخص"""
        try:
            date_str = date.toString("yyyy-MM-dd")
            
            # 🔴 **بارگذاری آمار خلاصه**
            # دریافتی‌ها
            income_query = """
            SELECT SUM(amount) as total 
            FROM AccountingTransactions 
            WHERE transaction_type = 'دریافت' 
            AND DATE(transaction_date) = ?
            """
            income_result = self.data_manager.db.fetch_one(income_query, (date_str,))
            income_total = income_result.get('total', 0) if income_result else 0
            
            # پرداختی‌ها
            expense_query = """
            SELECT SUM(amount) as total 
            FROM AccountingTransactions 
            WHERE transaction_type = 'پرداخت' 
            AND DATE(transaction_date) = ?
            """
            expense_result = self.data_manager.db.fetch_one(expense_query, (date_str,))
            expense_total = expense_result.get('total', 0) if expense_result else 0
            
            # انتقالات
            transfer_query = """
            SELECT SUM(amount) as total 
            FROM AccountingTransactions 
            WHERE transaction_type = 'انتقال' 
            AND DATE(transaction_date) = ?
            """
            transfer_result = self.data_manager.db.fetch_one(transfer_query, (date_str,))
            transfer_total = transfer_result.get('total', 0) if transfer_result else 0
            
            # موجودی کل حساب‌ها
            balance_query = """
            SELECT SUM(current_balance) as total 
            FROM Accounts 
            WHERE is_active = 1
            """
            balance_result = self.data_manager.db.fetch_one(balance_query)
            balance_total = balance_result.get('total', 0) if balance_result else 0
            
            # به‌روزرسانی آمار
            if "💰 دریافتی‌ها" in self.summary_labels:
                self.summary_labels["💰 دریافتی‌ها"].setText(
                    f"<h3>💰 دریافتی‌ها</h3><p style='font-size: 16pt; color: #27ae60;'>{income_total:,.0f} ریال</p>"
                )
            
            if "💸 پرداختی‌ها" in self.summary_labels:
                self.summary_labels["💸 پرداختی‌ها"].setText(
                    f"<h3>💸 پرداختی‌ها</h3><p style='font-size: 16pt; color: #e74c3c;'>{expense_total:,.0f} ریال</p>"
                )
            
            if "🔄 انتقالات" in self.summary_labels:
                self.summary_labels["🔄 انتقالات"].setText(
                    f"<h3>🔄 انتقالات</h3><p style='font-size: 16pt; color: #3498db;'>{transfer_total:,.0f} ریال</p>"
                )
            
            if "🏦 موجودی کل" in self.summary_labels:
                self.summary_labels["🏦 موجودی کل"].setText(
                    f"<h3>🏦 موجودی کل</h3><p style='font-size: 16pt; color: #f39c12;'>{balance_total:,.0f} ریال</p>"
                )
            
            # 🔴 **بارگذاری تراکنش‌های روز**
            transactions_query = """
            SELECT 
                t.transaction_id,
                t.transaction_type,
                t.amount,
                t.description,
                t.category,
                t.transaction_date,
                t.created_at,
                a1.account_name as from_account,
                a2.account_name as to_account
            FROM AccountingTransactions t
            LEFT JOIN Accounts a1 ON t.from_account_id = a1.account_id
            LEFT JOIN Accounts a2 ON t.to_account_id = a2.account_id
            WHERE DATE(t.transaction_date) = ?
            ORDER BY t.created_at DESC
            """
            transactions = self.data_manager.db.fetch_all(transactions_query, (date_str,))
            
            # تنظیم جدول
            self.transactions_table.setRowCount(len(transactions))
            
            for row, trans in enumerate(transactions):
                # ردیف
                self.transactions_table.setItem(row, 0, QTableWidgetItem(str(row + 1)))
                
                # زمان
                created_at = trans.get('created_at', '')
                if ' ' in created_at:
                    time_part = created_at.split(' ')[1]
                    self.transactions_table.setItem(row, 1, QTableWidgetItem(time_part[:8]))
                
                # نوع تراکنش
                trans_type = trans.get('transaction_type', '')
                type_item = QTableWidgetItem(trans_type)
                
                # رنگ‌بندی بر اساس نوع
                if trans_type == "دریافت":
                    type_item.setForeground(Qt.green)
                elif trans_type == "پرداخت":
                    type_item.setForeground(Qt.red)
                elif trans_type == "انتقال":
                    type_item.setForeground(Qt.blue)
                
                self.transactions_table.setItem(row, 2, type_item)
                
                # حساب
                account_text = trans.get('from_account', '')
                if trans_type == "انتقال":
                    to_account = trans.get('to_account', '')
                    account_text = f"{account_text} → {to_account}"
                
                self.transactions_table.setItem(row, 3, QTableWidgetItem(account_text))
                
                # مبلغ
                amount = trans.get('amount', 0)
                amount_item = QTableWidgetItem(f"{amount:,.0f}")
                amount_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                
                if trans_type == "دریافت":
                    amount_item.setForeground(Qt.green)
                elif trans_type == "پرداخت":
                    amount_item.setForeground(Qt.red)
                
                self.transactions_table.setItem(row, 4, amount_item)
                
                # دسته‌بندی
                self.transactions_table.setItem(row, 5, QTableWidgetItem(trans.get('category', '')))
                
                # توضیحات
                self.transactions_table.setItem(row, 6, QTableWidgetItem(trans.get('description', '')))
            
            # 🔴 **بارگذاری یادداشت‌های روز**
            notes_query = """
            SELECT notes FROM DailyNotes 
            WHERE note_date = ?
            """
            notes_result = self.data_manager.db.fetch_one(notes_query, (date_str,))
            
            if notes_result and notes_result.get('notes'):
                self.notes_input.setPlainText(notes_result['notes'])
            else:
                self.notes_input.clear()
            
        except Exception as e:
            print(f"⚠️ خطا در بارگذاری گزارش روزانه: {e}")
    
    def save_notes(self):
        """ذخیره یادداشت‌های روز"""
        try:
            date_str = self.date_input.date().toString("yyyy-MM-dd")
            notes = self.notes_input.toPlainText().strip()
            
            # بررسی وجود یادداشت قبلی
            check_query = "SELECT COUNT(*) as count FROM DailyNotes WHERE note_date = ?"
            check_result = self.data_manager.db.fetch_one(check_query, (date_str,))
            
            if check_result and check_result.get('count', 0) > 0:
                # به‌روزرسانی
                update_query = """
                UPDATE DailyNotes 
                SET notes = ?, updated_at = datetime('now')
                WHERE note_date = ?
                """
                self.data_manager.db.execute(update_query, (notes, date_str))
            else:
                # درج جدید
                insert_query = """
                INSERT INTO DailyNotes (note_date, notes, created_at)
                VALUES (?, ?, datetime('now'))
                """
                self.data_manager.db.execute(insert_query, (date_str, notes))
            
            QMessageBox.information(self, "موفق", "✅ یادداشت‌های روز با موفقیت ذخیره شد.")
            
        except Exception as e:
            QMessageBox.critical(self, "خطا", f"❌ خطا در ذخیره یادداشت:\n\n{str(e)}")
    
    def print_report(self):
        """چاپ گزارش"""
        QMessageBox.information(self, "چاپ", "🖨️ این قابلیت به زودی اضافه خواهد شد.")
    
    def export_report(self):
        """خروجی اکسل"""
        QMessageBox.information(self, "خروجی اکسل", "📤 این قابلیت به زودی اضافه خواهد شد.")