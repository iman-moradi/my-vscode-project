"""
دیالوگ نمایش جزئیات تراکنش - نسخه شمسی شده با اسکرول
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QMessageBox, QFormLayout, QGroupBox, QFrame, QTextEdit,
    QTableWidget, QTableWidgetItem, QHeaderView, QScrollArea,
    QWidget, QSizePolicy, QSpacerItem
)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QFont, QColor, QIcon
import jdatetime


class TransactionDetailsDialog(QDialog):
    """دیالوگ نمایش جزئیات تراکنش مالی - نسخه شمسی شده با اسکرول"""
    
    def __init__(self, data_manager, transaction_id, parent=None):
        super().__init__(parent)
        self.data_manager = data_manager
        self.transaction_manager = data_manager.transaction_manager
        self.transaction_id = transaction_id
        
        # 🔴 **راست‌چین کردن کامل**
        self.setLayoutDirection(Qt.RightToLeft)
        
        self.setup_ui()
        self.setup_styles()
        self.load_transaction_details()
    
    def setup_ui(self):
        """ایجاد رابط کاربری با اسکرول"""
        self.setWindowTitle("🔍 جزئیات تراکنش")
        self.setMinimumSize(900, 700)  # اندازه بزرگتر برای نمایش بهتر
        
        # 🔴 **لیوت اصلی**
        main_layout = QVBoxLayout()
        
        # 🔴 **عنوان**
        title_label = QLabel("🔍 جزئیات تراکنش مالی")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setFixedHeight(60)
        title_label.setStyleSheet("""
            QLabel {
                font-size: 16pt;
                font-weight: bold;
                color: #3498db;
                padding: 15px;
                background-color: #1a1a1a;
                border-radius: 8px;
                border: 2px solid #3498db;
                margin-bottom: 10px;
            }
        """)
        main_layout.addWidget(title_label)
        
        # 🔴 **ایجاد ویجت محتوا برای اسکرول**
        content_widget = QWidget()
        content_layout = QVBoxLayout()
        content_layout.setSpacing(15)
        content_layout.setContentsMargins(10, 10, 10, 10)
        
        # 🔴 **اطلاعات اصلی**
        main_info_group = QGroupBox("📋 اطلاعات اصلی تراکنش")
        main_info_group.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        main_layout_info = QVBoxLayout()
        
        # فرم اطلاعات
        form_layout = QFormLayout()
        form_layout.setSpacing(10)
        form_layout.setContentsMargins(15, 15, 15, 15)
        
        self.transaction_id_label = QLabel()
        self.transaction_id_label.setStyleSheet("font-weight: bold; color: #3498db; font-size: 12pt;")
        self.transaction_id_label.setMinimumHeight(25)
        
        self.transaction_type_label = QLabel()
        self.transaction_type_label.setMinimumHeight(25)
        
        self.date_label = QLabel()
        self.date_label.setMinimumHeight(25)
        
        self.amount_label = QLabel()
        self.amount_label.setStyleSheet("font-weight: bold; font-size: 14pt;")
        self.amount_label.setMinimumHeight(30)
        
        self.from_account_label = QLabel()
        self.from_account_label.setMinimumHeight(25)
        self.from_account_label.setWordWrap(True)
        
        self.to_account_label = QLabel()
        self.to_account_label.setMinimumHeight(25)
        self.to_account_label.setWordWrap(True)
        
        self.category_label = QLabel()
        self.category_label.setMinimumHeight(25)
        
        self.reference_label = QLabel()
        self.reference_label.setMinimumHeight(25)
        
        self.employee_label = QLabel()
        self.employee_label.setMinimumHeight(25)
        
        self.status_label = QLabel()
        self.status_label.setMinimumHeight(25)
        
        form_layout.addRow("🔢 شماره تراکنش:", self.transaction_id_label)
        form_layout.addRow("📊 نوع تراکنش:", self.transaction_type_label)
        form_layout.addRow("📅 تاریخ تراکنش:", self.date_label)
        form_layout.addRow("💰 مبلغ تراکنش:", self.amount_label)
        form_layout.addRow("🏦 از حساب:", self.from_account_label)
        form_layout.addRow("🏦 به حساب:", self.to_account_label)
        form_layout.addRow("🏷️ دسته‌بندی:", self.category_label)
        form_layout.addRow("🏷️ مرجع:", self.reference_label)
        form_layout.addRow("👤 ثبت کننده:", self.employee_label)
        form_layout.addRow("📊 وضعیت:", self.status_label)
        
        main_layout_info.addLayout(form_layout)
        main_info_group.setLayout(main_layout_info)
        content_layout.addWidget(main_info_group)
        
        # 🔴 **شرح تراکنش**
        description_group = QGroupBox("📝 شرح تراکنش")
        description_group.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        description_layout = QVBoxLayout()
        
        self.description_text = QTextEdit()
        self.description_text.setReadOnly(True)
        self.description_text.setFixedHeight(120)
        self.description_text.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        
        description_layout.addWidget(self.description_text)
        description_group.setLayout(description_layout)
        content_layout.addWidget(description_group)
        
        # 🔴 **تاریخچه تغییرات**
        history_group = QGroupBox("📜 تاریخچه تغییرات")
        history_group.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        history_layout = QVBoxLayout()
        
        self.history_table = QTableWidget()
        self.history_table.setColumnCount(4)
        self.history_table.setHorizontalHeaderLabels([
            "تاریخ",
            "عملیات",
            "کاربر",
            "توضیحات"
        ])
        self.history_table.setFixedHeight(200)
        self.history_table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        
        # تنظیمات جدول
        self.history_table.horizontalHeader().setStretchLastSection(True)
        self.history_table.setAlternatingRowColors(True)
        
        history_layout.addWidget(self.history_table)
        history_group.setLayout(history_layout)
        content_layout.addWidget(history_group)
        
        # 🔴 **اطلاعات سیستم**
        system_info_group = QGroupBox("🖥️ اطلاعات سیستم")
        system_info_group.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        system_layout = QFormLayout()
        
        self.created_at_label = QLabel()
        self.created_at_label.setMinimumHeight(25)
        
        self.updated_at_label = QLabel()
        self.updated_at_label.setMinimumHeight(25)
        
        system_layout.addRow("🕒 تاریخ ایجاد:", self.created_at_label)
        system_layout.addRow("🔄 آخرین بروزرسانی:", self.updated_at_label)
        
        system_info_group.setLayout(system_layout)
        content_layout.addWidget(system_info_group)
        
        # اسپیسر برای فشرده نشدن محتوا
        content_layout.addStretch()
        
        content_widget.setLayout(content_layout)
        
        # 🔴 **ایجاد اسکرول برای محتوا**
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(content_widget)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QScrollBar:vertical {
                border: none;
                background: #1a1a1a;
                width: 12px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background: #3498db;
                min-height: 30px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical:hover {
                background: #2980b9;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                border: none;
                background: none;
                height: 0px;
            }
        """)
        
        main_layout.addWidget(scroll_area)
        
        # 🔴 **دکمه‌های عملیاتی**
        button_layout = QHBoxLayout()
        
        self.print_button = QPushButton("🖨️ چاپ رسید")
        self.print_button.setProperty("class", "info_button")
        self.print_button.clicked.connect(self.print_receipt)
        self.print_button.setFixedHeight(40)
        
        self.reverse_button = QPushButton("↩️ برگشت تراکنش")
        self.reverse_button.setProperty("class", "warning_button")
        self.reverse_button.clicked.connect(self.reverse_transaction)
        self.reverse_button.setFixedHeight(40)
        
        self.edit_button = QPushButton("✏️ ویرایش")
        self.edit_button.setProperty("class", "info_button")
        self.edit_button.clicked.connect(self.edit_transaction)
        self.edit_button.setFixedHeight(40)
        
        self.close_button = QPushButton("❌ بستن")
        self.close_button.setProperty("class", "danger_button")
        self.close_button.clicked.connect(self.accept)
        self.close_button.setFixedHeight(40)
        
        button_layout.addWidget(self.print_button)
        button_layout.addWidget(self.reverse_button)
        button_layout.addWidget(self.edit_button)
        button_layout.addStretch()
        button_layout.addWidget(self.close_button)
        
        main_layout.addLayout(button_layout)
        
        self.setLayout(main_layout)
    
    def setup_styles(self):
        """تنظیم استایل"""
        self.setStyleSheet("""
            QDialog {
                background-color: #0a0a0a;
                color: #ffffff;
                font-family: 'B Nazanin';
                font-size: 11pt;
            }
            
            QGroupBox {
                font-weight: bold;
                border: 2px solid #34495e;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 15px;
                background-color: #1a1a1a;
            }
            
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top right;
                right: 15px;
                padding: 0 15px;
                color: #3498db;
                font-size: 12pt;
            }
            
            QLabel {
                color: #ecf0f1;
                font-size: 11pt;
                min-height: 25px;
                padding: 2px;
            }
            
            QFormLayout QLabel {
                min-width: 150px;
            }
            
            QTextEdit {
                background-color: #2c3e50;
                color: white;
                border: 1px solid #34495e;
                border-radius: 4px;
                font-size: 11pt;
                padding: 8px;
            }
            
            QTableWidget {
                background-color: #2c3e50;
                color: white;
                border: 1px solid #34495e;
                border-radius: 4px;
                alternate-background-color: #34495e;
                font-size: 10pt;
            }
            
            QTableWidget::item {
                padding: 6px;
            }
            
            QHeaderView::section {
                background-color: #34495e;
                color: white;
                padding: 8px;
                border: none;
                font-weight: bold;
                font-size: 10pt;
            }
            
            QPushButton {
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
                font-size: 11pt;
                min-width: 130px;
            }
            
            .info_button {
                background-color: #3498db;
                color: white;
            }
            
            .info_button:hover {
                background-color: #2980b9;
            }
            
            .warning_button {
                background-color: #f39c12;
                color: white;
            }
            
            .warning_button:hover {
                background-color: #d68910;
            }
            
            .danger_button {
                background-color: #e74c3c;
                color: white;
            }
            
            .danger_button:hover {
                background-color: #c0392b;
            }
        """)
    
    def load_transaction_details(self):
        """بارگذاری جزئیات تراکنش با استفاده از TransactionManager"""
        try:
            # استفاده از TransactionManager
            transaction = self.transaction_manager.get_transaction_by_id(self.transaction_id)
            
            if not transaction:
                QMessageBox.warning(self, "خطا", "تراکنش مورد نظر یافت نشد.")
                self.reject()
                return
            
            # پر کردن اطلاعات
            self.transaction_id_label.setText(f"TRX{transaction.get('id', 'نامشخص'):06d}")
            
            # نوع تراکنش با رنگ‌بندی
            trans_type = transaction.get('transaction_type', 'نامشخص')
            self.transaction_type_label.setText(trans_type)
            
            if trans_type == "دریافت":
                self.transaction_type_label.setStyleSheet("color: #27ae60; font-weight: bold; font-size: 11pt;")
                self.setWindowTitle(f"💰 جزئیات دریافت TRX{transaction.get('id', ''):06d}")
            elif trans_type == "پرداخت":
                self.transaction_type_label.setStyleSheet("color: #e74c3c; font-weight: bold; font-size: 11pt;")
                self.setWindowTitle(f"💸 جزئیات پرداخت TRX{transaction.get('id', ''):06d}")
            elif trans_type == "انتقال":
                self.transaction_type_label.setStyleSheet("color: #3498db; font-weight: bold; font-size: 11pt;")
                self.setWindowTitle(f"🔄 جزئیات انتقال TRX{transaction.get('id', ''):06d}")
            else:
                self.transaction_type_label.setStyleSheet("color: #f39c12; font-weight: bold; font-size: 11pt;")
                self.setWindowTitle(f"📊 جزئیات تراکنش TRX{transaction.get('id', ''):06d}")
            
            # تاریخ تراکنش (شمسی)
            trans_date = transaction.get('transaction_date_shamsi', '')
            self.date_label.setText(trans_date)
            
            # مبلغ (تومان)
            amount = transaction.get('amount_toman', 0)
            amount_text = f"{amount:,.0f} تومان"
            self.amount_label.setText(amount_text)
            
            # رنگ‌بندی مبلغ
            if trans_type == "دریافت":
                self.amount_label.setStyleSheet("color: #27ae60; font-weight: bold; font-size: 14pt;")
            elif trans_type == "پرداخت":
                self.amount_label.setStyleSheet("color: #e74c3c; font-weight: bold; font-size: 14pt;")
            else:
                self.amount_label.setStyleSheet("color: #f39c12; font-weight: bold; font-size: 14pt;")
            
            # حساب مبدا
            from_account = transaction.get('from_account_name', '')
            from_account = from_account if from_account else "---"
            self.from_account_label.setText(from_account)
            
            # حساب مقصد
            to_account = transaction.get('to_account_name', '')
            to_account = to_account if to_account else "---"
            self.to_account_label.setText(to_account)
            
            # دسته‌بندی
            category = transaction.get('category', 'عمومی')
            self.category_label.setText(category)
            
            # مرجع
            reference_type = transaction.get('reference_type', '')
            reference_id = transaction.get('reference_id', '')
            reference_text = ""
            
            if reference_type and reference_id:
                reference_text = f"{reference_type} #{reference_id}"
            elif reference_id:
                reference_text = f"#{reference_id}"
            else:
                reference_text = "ندارد"
            
            self.reference_label.setText(reference_text)
            
            # ثبت کننده
            employee = transaction.get('employee', 'سیستم')
            self.employee_label.setText(employee)
            
            # وضعیت
            status = transaction.get('status', 'انجام شده')
            self.status_label.setText(status)
            if status == "انجام شده":
                self.status_label.setStyleSheet("color: #27ae60; font-weight: bold;")
            elif status == "لغو شده":
                self.status_label.setStyleSheet("color: #e74c3c; font-weight: bold;")
            elif status == "در انتظار":
                self.status_label.setStyleSheet("color: #f39c12; font-weight: bold;")
            else:
                self.status_label.setStyleSheet("color: #7f8c8d; font-weight: bold;")
            
            # شرح
            description = transaction.get('description', 'بدون شرح')
            self.description_text.setText(description)
            
            # تاریخ‌های سیستم (شمسی)
            created_at = transaction.get('created_at', '')
            if created_at:
                try:
                    # فرض می‌کنیم تاریخ میلادی است
                    jalali_created = self.data_manager.db.gregorian_to_jalali(created_at)
                    self.created_at_label.setText(jalali_created)
                except:
                    self.created_at_label.setText(str(created_at))
            else:
                self.created_at_label.setText("نامشخص")
            
            updated_at = transaction.get('updated_at', '')
            if updated_at:
                try:
                    jalali_updated = self.data_manager.db.gregorian_to_jalali(updated_at)
                    self.updated_at_label.setText(jalali_updated)
                except:
                    self.updated_at_label.setText(str(updated_at))
            else:
                self.updated_at_label.setText("نامشخص")
            
            # بارگذاری تاریخچه
            self.load_transaction_history()
            
            print(f"✅ جزئیات تراکنش {self.transaction_id} بارگذاری شد")
            
        except Exception as e:
            print(f"❌ خطا در بارگذاری جزئیات تراکنش: {e}")
            QMessageBox.critical(self, "خطا", f"خطا در بارگذاری اطلاعات تراکنش:\n\n{str(e)}")
    
    def load_transaction_history(self):
        """بارگذاری تاریخچه تغییرات تراکنش"""
        try:
            # در این نسخه ساده، تاریخچه را از جدول Logs دریافت می‌کنیم
            query = """
            SELECT 
                l.created_at,
                l.action,
                u.username as user,
                l.details
            FROM Logs l
            LEFT JOIN Users u ON l.user_id = u.id
            WHERE l.table_name = 'AccountingTransactions' 
            AND l.record_id = ?
            ORDER BY l.created_at DESC
            """
            
            history = self.data_manager.db.fetch_all(query, (self.transaction_id,))
            
            self.history_table.setRowCount(0)
            
            for row, record in enumerate(history):
                self.history_table.insertRow(row)
                
                # تاریخ (شمسی)
                created_at = record.get('created_at', '')
                if created_at:
                    try:
                        jalali_date = self.data_manager.db.gregorian_to_jalali(created_at)
                        date_item = QTableWidgetItem(jalali_date)
                    except:
                        date_item = QTableWidgetItem(str(created_at))
                else:
                    date_item = QTableWidgetItem("نامشخص")
                
                date_item.setTextAlignment(Qt.AlignCenter)
                self.history_table.setItem(row, 0, date_item)
                
                # عملیات
                action = record.get('action', '')
                action_item = QTableWidgetItem(action)
                action_item.setTextAlignment(Qt.AlignCenter)
                
                if "ایجاد" in action:
                    action_item.setForeground(QColor('#27ae60'))
                elif "ویرایش" in action:
                    action_item.setForeground(QColor('#3498db'))
                elif "حذف" in action or "لغو" in action:
                    action_item.setForeground(QColor('#e74c3c'))
                else:
                    action_item.setForeground(QColor('#f39c12'))
                
                self.history_table.setItem(row, 1, action_item)
                
                # کاربر
                user = record.get('user', 'سیستم')
                user_item = QTableWidgetItem(user)
                user_item.setTextAlignment(Qt.AlignCenter)
                self.history_table.setItem(row, 2, user_item)
                
                # توضیحات
                details = record.get('details', '')
                details_item = QTableWidgetItem(details[:100] + "..." if len(details) > 100 else details)
                self.history_table.setItem(row, 3, details_item)
            
            # تنظیم اندازه ستون‌ها
            self.history_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
            self.history_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
            self.history_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
            self.history_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)
            
            # تنظیم ارتفاع ردیف‌ها
            for row in range(self.history_table.rowCount()):
                self.history_table.setRowHeight(row, 30)
            
        except Exception as e:
            print(f"⚠️ خطا در بارگذاری تاریخچه: {e}")
            # جدول را خالی می‌کنیم
            self.history_table.setRowCount(0)
    
    def print_receipt(self):
        """چاپ رسید تراکنش"""
        try:
            QMessageBox.information(
                self, "چاپ رسید",
                "🖨️ رسید تراکنش آماده چاپ است.\n\n"
                "ویژگی‌های چاپ:\n"
                "• قالب‌بندی حرفه‌ای\n"
                "• شامل تمام جزئیات\n"
                "• امکان انتخاب پرینتر\n"
                "• ذخیره به صورت PDF\n\n"
                "این قابلیت در نسخه‌های بعدی کامل خواهد شد."
            )
        except Exception as e:
            QMessageBox.critical(self, "خطا", f"خطا در چاپ رسید:\n\n{str(e)}")
    
    def edit_transaction(self):
        """ویرایش تراکنش"""
        try:
            # بستن دیالوگ فعلی
            self.accept()
            
            # باز کردن دیالوگ ویرایش
            from dialogs.transaction_dialog import TransactionDialog
            dialog = TransactionDialog(self.data_manager, 
                                     transaction_id=self.transaction_id,
                                     parent=self.parent())
            dialog.exec()
            
        except ImportError as e:
            QMessageBox.information(self, "ویرایش تراکنش", 
                "فرم ویرایش تراکنش به زودی اضافه خواهد شد.")
    
    def reverse_transaction(self):
        """برگشت تراکنش با استفاده از TransactionManager"""
        # دریافت تایید از کاربر
        reply = QMessageBox.question(
            self, "تأیید برگشت",
            "⚠️ آیا از برگشت این تراکنش اطمینان دارید؟\n\n"
            "این عمل اثرات زیر را دارد:\n"
            "• تراکنش فعلی لغو می‌شود\n"
            "• اثرات تراکنش از حساب‌ها حذف می‌شود\n"
            "• یک تراکنش معکوس ثبت می‌شود\n\n"
            "این عمل قابل بازگشت است.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply != QMessageBox.Yes:
            return
        
        try:
            # استفاده از TransactionManager
            success, message = self.transaction_manager.reverse_transaction(
                self.transaction_id,
                reason="برگشت دستی از پنجره جزئیات"
            )
            
            if success:
                QMessageBox.information(
                    self, "موفق",
                    f"✅ تراکنش با موفقیت برگشت داده شد.\n\n{message}"
                )
                
                # بستن دیالوگ
                self.accept()
            else:
                QMessageBox.critical(self, "خطا", f"❌ {message}")
                
        except Exception as e:
            QMessageBox.critical(self, "خطا", f"❌ خطا در برگشت تراکنش:\n\n{str(e)}")