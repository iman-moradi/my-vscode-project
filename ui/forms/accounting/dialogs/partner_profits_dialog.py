# ui/forms/accounting/dialogs/partner_profits_dialog.py
"""
دیالوگ نمایش سودهای یک شریک خاص
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QTableWidget,
    QTableWidgetItem, QPushButton, QMessageBox, QHeaderView,
    QFrame, QGroupBox, QGridLayout, QTextEdit, QComboBox
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont
import jdatetime
from datetime import datetime

# ایمپورت ویجت تاریخ شمسی
try:
    from ui.forms.accounting.widgets.jalali_date_input import JalaliDateInputAccounting
except ImportError:
    print("⚠️ ویجت تاریخ شمسی یافت نشد")


class PartnerProfitsDialog(QDialog):
    """دیالوگ نمایش سودهای یک شریک"""
    
    def __init__(self, data_manager, partner_id, parent=None):
        super().__init__(parent)
        self.data_manager = data_manager
        self.partner_id = partner_id
        
        # 🔴 **راست‌چین کردن کامل**
        self.setLayoutDirection(Qt.RightToLeft)
        
        # تنظیم پنجره
        self.setWindowTitle("💰 سودهای شریک")
        self.setMinimumSize(900, 700)
        
        # تنظیم استایل
        self.setup_styles()
        
        # دریافت اطلاعات شریک
        self.partner_info = self.load_partner_info()
        if not self.partner_info:
            QMessageBox.warning(self, "خطا", "شریک یافت نشد")
            self.reject()
            return
        
        # ایجاد رابط کاربری
        self.init_ui()
        
        # بارگذاری سودها
        self.load_profits()
        
        print(f"✅ دیالوگ سودهای شریک برای {self.partner_info.get('partner_name')} ایجاد شد")
    
    def setup_styles(self):
        """تنظیم استایل دیالوگ"""
        self.setStyleSheet("""
            QDialog {
                background-color: #000000;
                color: #ffffff;
                font-family: 'B Nazanin';
            }
            
            /* استایل هدر */
            .header_frame {
                background-color: #1e1e1e;
                border: 2px solid #2ecc71;
                border-radius: 8px;
                padding: 15px;
            }
            
            /* کارت آمار */
            .stat_card {
                background-color: #111111;
                border: 1px solid #333;
                border-radius: 5px;
                padding: 10px;
            }
            
            /* جدول */
            QTableWidget {
                background-color: #111111;
                alternate-background-color: #0a0a0a;
                selection-background-color: #2ecc71;
                selection-color: white;
                gridline-color: #333;
                color: white;
                border: none;
                font-size: 10pt;
            }
            
            QTableWidget::item {
                padding: 6px;
                color: white;
            }
            
            QHeaderView::section {
                background-color: #2c3e50;
                color: white;
                padding: 8px;
                border: none;
                font-weight: bold;
                text-align: right;
                font-size: 10pt;
            }
            
            /* دکمه‌ها */
            QPushButton {
                background-color: #2c3e50;
                color: white;
                border: none;
                padding: 8px 15px;
                border-radius: 4px;
                font-family: 'B Nazanin';
                font-size: 10pt;
            }
            
            QPushButton:hover {
                background-color: #34495e;
            }
            
            QPushButton:pressed {
                background-color: #27ae60;
            }
            
            QPushButton#close_button {
                background-color: #e74c3c;
            }
            
            QPushButton#close_button:hover {
                background-color: #c0392b;
            }
            
            /* گروه‌باکس */
            QGroupBox {
                border: 2px solid #3498db;
                border-radius: 5px;
                margin-top: 10px;
                font-weight: bold;
                color: #3498db;
                background-color: #111111;
            }
            
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top right;
                padding: 0 10px 0 10px;
            }
        """)
    
    def load_partner_info(self):
        """بارگذاری اطلاعات شریک"""
        try:
            query = """
            SELECT 
                p.*,
                per.first_name || ' ' || per.last_name as partner_name,
                per.mobile, per.national_id,
                (SELECT SUM(share_amount) FROM PartnerShares ps WHERE ps.partner_id = p.id) as total_profit
            FROM Partners p
            JOIN Persons per ON p.person_id = per.id
            WHERE p.id = ?
            """
            
            result = self.data_manager.db.fetch_one(query, (self.partner_id,))
            
            if result:
                # تبدیل تاریخ‌ها و مبالغ
                if result.get('partnership_start'):
                    result['partnership_start_shamsi'] = self.data_manager.db.gregorian_to_jalali(
                        result['partnership_start']
                    )
                
                if result.get('partnership_end'):
                    result['partnership_end_shamsi'] = self.data_manager.db.gregorian_to_jalali(
                        result['partnership_end']
                    )
                
                result['capital_toman'] = result['capital'] / 10 if result['capital'] else 0
                result['total_profit_toman'] = result['total_profit'] / 10 if result['total_profit'] else 0
            
            return result
            
        except Exception as e:
            print(f"⚠️ خطا در بارگذاری اطلاعات شریک: {e}")
            return None
    
    def init_ui(self):
        """راه‌اندازی رابط کاربری"""
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(15, 15, 15, 15)
        
        # 🔴 **هدر - اطلاعات شریک**
        header_frame = self.create_header_frame()
        layout.addWidget(header_frame)
        
        # 🔴 **فیلترها**
        filter_frame = self.create_filter_frame()
        layout.addWidget(filter_frame)
        
        # 🔴 **جدول سودها**
        self.profits_table = QTableWidget()
        self.profits_table.setColumnCount(8)
        self.profits_table.setHorizontalHeaderLabels([
            "ردیف", "تاریخ", "نوع تراکنش", "شماره مرجع", 
            "درصد سهم", "مبلغ سهم (تومان)", "توضیحات", "وضعیت"
        ])
        
        # تنظیمات جدول
        self.profits_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.profits_table.setAlternatingRowColors(True)
        self.profits_table.setSelectionBehavior(QTableWidget.SelectRows)
        
        layout.addWidget(self.profits_table, 1)
        
        # 🔴 **خلاصه مالی**
        summary_frame = self.create_summary_frame()
        layout.addWidget(summary_frame)
        
        # 🔴 **دکمه‌ها**
        button_layout = QHBoxLayout()
        
        btn_close = QPushButton("❌ بستن")
        btn_close.setObjectName("close_button")
        btn_close.clicked.connect(self.reject)
        
        btn_refresh = QPushButton("🔄 بروزرسانی")
        btn_refresh.clicked.connect(self.load_profits)
        
        btn_export = QPushButton("📤 خروجی اکسل")
        btn_export.clicked.connect(self.export_to_excel)
        
        button_layout.addWidget(btn_close)
        button_layout.addStretch()
        button_layout.addWidget(btn_refresh)
        button_layout.addWidget(btn_export)
        
        layout.addLayout(button_layout)
    
    def create_header_frame(self):
        """ایجاد فریم هدر با اطلاعات شریک"""
        frame = QFrame()
        frame.setObjectName("header_frame")
        
        layout = QVBoxLayout(frame)
        layout.setSpacing(10)
        
        # عنوان
        title_label = QLabel(f"💰 سودهای شریک: {self.partner_info.get('partner_name')}")
        title_label.setStyleSheet("""
            QLabel {
                font-size: 16pt;
                font-weight: bold;
                color: #2ecc71;
            }
        """)
        layout.addWidget(title_label)
        
        # اطلاعات شریک
        info_layout = QGridLayout()
        info_layout.setHorizontalSpacing(20)
        info_layout.setVerticalSpacing(8)
        
        info_layout.addWidget(QLabel("📱 موبایل:"), 0, 0)
        info_layout.addWidget(QLabel(self.partner_info.get('mobile', '-')), 0, 1)
        
        info_layout.addWidget(QLabel("📅 تاریخ شروع:"), 0, 2)
        info_layout.addWidget(QLabel(self.partner_info.get('partnership_start_shamsi', '-')), 0, 3)
        
        info_layout.addWidget(QLabel("💼 سرمایه:"), 1, 0)
        info_layout.addWidget(QLabel(f"{self.partner_info.get('capital_toman', 0):,.0f} تومان"), 1, 1)
        
        info_layout.addWidget(QLabel("📈 درصد سود:"), 1, 2)
        info_layout.addWidget(QLabel(f"{self.partner_info.get('profit_percentage', 0):.1f}%"), 1, 3)
        
        info_layout.addWidget(QLabel("💰 سود کل:"), 2, 0)
        profit_label = QLabel(f"{self.partner_info.get('total_profit_toman', 0):,.0f} تومان")
        profit_label.setStyleSheet("color: #2ecc71; font-weight: bold;")
        info_layout.addWidget(profit_label, 2, 1)
        
        info_layout.addWidget(QLabel("🏛️ وضعیت:"), 2, 2)
        status = "فعال" if self.partner_info.get('active') else "غیرفعال"
        status_label = QLabel(status)
        status_label.setStyleSheet("color: #27ae60; font-weight: bold;" if self.partner_info.get('active') else "color: #e74c3c; font-weight: bold;")
        info_layout.addWidget(status_label, 2, 3)
        
        layout.addLayout(info_layout)
        
        return frame
    
    def create_filter_frame(self):
        """ایجاد فریم فیلترها"""
        frame = QFrame()
        
        layout = QHBoxLayout(frame)
        layout.setSpacing(10)
        
        layout.addWidget(QLabel("📅 از تاریخ:"))
        self.start_date_filter = JalaliDateInputAccounting()
        layout.addWidget(self.start_date_filter)
        
        layout.addWidget(QLabel("📅 تا تاریخ:"))
        self.end_date_filter = JalaliDateInputAccounting()
        layout.addWidget(self.end_date_filter)
        
        self.type_filter = QComboBox()
        self.type_filter.addItems(["همه", "فاکتور", "چک", "توزیع سود", "سایر"])
        layout.addWidget(QLabel("📋 نوع:"))
        layout.addWidget(self.type_filter)
        
        btn_filter = QPushButton("🔍 فیلتر")
        btn_filter.clicked.connect(self.apply_filters)
        layout.addWidget(btn_filter)
        
        btn_clear = QPushButton("🗑️ حذف فیلتر")
        btn_clear.clicked.connect(self.clear_filters)
        layout.addWidget(btn_clear)
        
        layout.addStretch()
        
        return frame
    
    def create_summary_frame(self):
        """ایجاد فریم خلاصه مالی"""
        frame = QFrame()
        frame.setObjectName("stat_card")
        
        layout = QHBoxLayout(frame)
        
        self.summary_labels = {}
        
        # 4 کارت خلاصه
        summaries = [
            ("تعداد تراکنش", "0", "#3498db"),
            ("مجموع سود", "0 تومان", "#27ae60"),
            ("میانگین سهم", "0%", "#9b59b6"),
            ("بیشترین سود", "0 تومان", "#f39c12")
        ]
        
        for title, value, color in summaries:
            card = QFrame()
            card.setObjectName("stat_card")
            
            card_layout = QVBoxLayout(card)
            card_layout.setSpacing(5)
            
            title_label = QLabel(title)
            title_label.setAlignment(Qt.AlignCenter)
            title_label.setStyleSheet(f"color: #bbb; font-size: 10pt;")
            
            value_label = QLabel(value)
            value_label.setAlignment(Qt.AlignCenter)
            value_label.setStyleSheet(f"color: {color}; font-size: 12pt; font-weight: bold;")
            
            card_layout.addWidget(title_label)
            card_layout.addWidget(value_label)
            
            layout.addWidget(card)
            self.summary_labels[title] = value_label
        
        return frame
    
    def load_profits(self):
        """بارگذاری سودهای شریک"""
        try:
            # ساختار کوئری پایه
            query = """
            SELECT 
                ps.*,
                CASE 
                    WHEN ps.transaction_type LIKE '%فاکتور%' THEN i.invoice_number
                    WHEN ps.transaction_type LIKE '%چک%' THEN c.check_number
                    ELSE 'سایر'
                END as transaction_ref,
                i.invoice_date,
                CASE 
                    WHEN ps.transaction_type LIKE '%فاکتور%' THEN i.payment_status
                    ELSE 'تکمیل شده'
                END as status
            FROM PartnerShares ps
            LEFT JOIN Invoices i ON ps.transaction_type LIKE '%فاکتور%' AND ps.transaction_id = i.id
            LEFT JOIN Checks c ON ps.transaction_type LIKE '%چک%' AND ps.transaction_id = c.id
            WHERE ps.partner_id = ?
            """
            
            params = [self.partner_id]
            
            # اعمال فیلترهای تاریخ
            start_date = self.start_date_filter.get_date_for_database()
            end_date = self.end_date_filter.get_date_for_database()
            
            if start_date:
                query += " AND DATE(ps.calculation_date) >= ?"
                params.append(start_date)
            
            if end_date:
                query += " AND DATE(ps.calculation_date) <= ?"
                params.append(end_date)
            
            # اعمال فیلتر نوع
            type_filter = self.type_filter.currentText()
            if type_filter != "همه":
                if type_filter == "فاکتور":
                    query += " AND ps.transaction_type LIKE '%فاکتور%'"
                elif type_filter == "چک":
                    query += " AND ps.transaction_type LIKE '%چک%'"
                elif type_filter == "توزیع سود":
                    query += " AND ps.transaction_type = 'توزیع سود'"
                else:
                    query += " AND ps.transaction_type NOT LIKE '%فاکتور%' AND ps.transaction_type NOT LIKE '%چک%'"
            
            query += " ORDER BY ps.calculation_date DESC"
            
            profits = self.data_manager.db.fetch_all(query, params)
            
            # نمایش در جدول
            self.display_profits(profits)
            
            # محاسبه خلاصه
            self.calculate_summary(profits)
            
        except Exception as e:
            print(f"⚠️ خطا در بارگذاری سودها: {e}")
            QMessageBox.warning(self, "خطا", f"خطا در بارگذاری سودها:\n{str(e)}")
    
    def display_profits(self, profits):
        """نمایش سودها در جدول"""
        self.profits_table.setRowCount(len(profits))
        
        total_profit = 0
        total_percentage = 0
        
        for row, profit in enumerate(profits):
            # ردیف
            self.profits_table.setItem(row, 0, QTableWidgetItem(str(row + 1)))
            
            # تاریخ
            date_str = self.data_manager.db.gregorian_to_jalali(profit.get('calculation_date'))
            self.profits_table.setItem(row, 1, QTableWidgetItem(date_str))
            
            # نوع تراکنش
            trans_type = profit.get('transaction_type', 'نامشخص')
            self.profits_table.setItem(row, 2, QTableWidgetItem(trans_type))
            
            # شماره مرجع
            ref = profit.get('transaction_ref', '-')
            self.profits_table.setItem(row, 3, QTableWidgetItem(str(ref)))
            
            # درصد سهم
            percentage = profit.get('share_percentage', 0)
            self.profits_table.setItem(row, 4, QTableWidgetItem(f"{percentage:.1f}%"))
            
            # مبلغ سهم (تبدیل به تومان)
            share_amount = profit.get('share_amount', 0) / 10
            item = QTableWidgetItem(f"{share_amount:,.0f}")
            
            if share_amount > 0:
                item.setForeground(Qt.green)
            elif share_amount < 0:
                item.setForeground(Qt.red)
            
            self.profits_table.setItem(row, 5, item)
            
            # توضیحات
            description = profit.get('description', '')
            self.profits_table.setItem(row, 6, QTableWidgetItem(description[:50] + "..." if len(description) > 50 else description))
            
            # وضعیت
            status = profit.get('status', 'تکمیل شده')
            status_item = QTableWidgetItem(status)
            
            if status == 'پرداخت شده' or status == 'تکمیل شده':
                status_item.setForeground(Qt.green)
            elif status == 'پرداخت نشده':
                status_item.setForeground(Qt.red)
            elif status == 'در انتظار':
                status_item.setForeground(Qt.yellow)
            
            self.profits_table.setItem(row, 7, status_item)
            
            # جمع‌آوری برای خلاصه
            total_profit += share_amount
            total_percentage += percentage
    
    def calculate_summary(self, profits):
        """محاسبه خلاصه مالی"""
        if not profits:
            self.summary_labels['تعداد تراکنش'].setText("0")
            self.summary_labels['مجموع سود'].setText("0 تومان")
            self.summary_labels['میانگین سهم'].setText("0%")
            self.summary_labels['بیشترین سود'].setText("0 تومان")
            return
        
        total_count = len(profits)
        total_profit = sum(p.get('share_amount', 0) / 10 for p in profits)
        avg_percentage = sum(p.get('share_percentage', 0) for p in profits) / total_count
        max_profit = max((p.get('share_amount', 0) / 10 for p in profits), default=0)
        
        self.summary_labels['تعداد تراکنش'].setText(str(total_count))
        self.summary_labels['مجموع سود'].setText(f"{total_profit:,.0f} تومان")
        self.summary_labels['میانگین سهم'].setText(f"{avg_percentage:.1f}%")
        self.summary_labels['بیشترین سود'].setText(f"{max_profit:,.0f} تومان")
    
    def apply_filters(self):
        """اعمال فیلترها"""
        self.load_profits()
    
    def clear_filters(self):
        """حذف فیلترها"""
        self.start_date_filter.clear()
        self.end_date_filter.clear()
        self.type_filter.setCurrentIndex(0)
        self.load_profits()
    
    def export_to_excel(self):
        """خروجی اکسل"""
        try:
            from openpyxl import Workbook
            import os
            
            # ایجاد فایل اکسل
            wb = Workbook()
            ws = wb.active
            ws.title = "سودهای شریک"
            
            # هدرها
            headers = ["ردیف", "تاریخ", "نوع تراکنش", "شماره مرجع", 
                      "درصد سهم", "مبلغ سهم (تومان)", "توضیحات", "وضعیت"]
            ws.append(headers)
            
            # داده‌ها
            for row in range(self.profits_table.rowCount()):
                row_data = []
                for col in range(self.profits_table.columnCount()):
                    item = self.profits_table.item(row, col)
                    row_data.append(item.text() if item else "")
                ws.append(row_data)
            
            # ذخیره فایل
            export_dir = "data/exports"
            os.makedirs(export_dir, exist_ok=True)
            
            filename = f"{export_dir}/partner_profits_{self.partner_id}_{jdatetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            wb.save(filename)
            
            QMessageBox.information(self, "موفق", f"فایل اکسل با موفقیت ذخیره شد:\n{filename}")
            
        except ImportError:
            QMessageBox.warning(self, "خطا", "برای خروجی اکسل، کتابخانه openpyxl را نصب کنید:\npip install openpyxl")
        except Exception as e:
            QMessageBox.warning(self, "خطا", f"خطا در خروجی اکسل:\n{str(e)}")