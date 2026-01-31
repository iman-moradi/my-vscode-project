"""
فرم مدیریت حساب‌های بانکی و نقدی
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QLineEdit, QComboBox, QLabel, QMessageBox, QHeaderView,
    QScrollArea, QFrame, QGroupBox, QFormLayout, QSplitter, QToolBar
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor, QFont, QIcon
import jdatetime
from datetime import datetime

class AccountsForm(QWidget):
    """فرم مدیریت حساب‌ها"""
    
    # سیگنال‌ها
    data_changed = Signal()
    account_selected = Signal(int)
    
    def __init__(self, data_manager):
        super().__init__()
        self.data_manager = data_manager
        self.selected_account_id = None
        
        # 🔴 **راست‌چین کردن کامل**
        self.setLayoutDirection(Qt.RightToLeft)
        
        # تنظیم استایل
        self.setup_styles()
        
        # ایجاد رابط کاربری
        self.init_ui()
        
        # بارگذاری داده‌ها
        self.load_accounts()
        
        print("✅ فرم حساب‌ها ایجاد شد")
    
    def setup_styles(self):
        """تنظیم استایل فرم"""
        self.setStyleSheet("""
            /* استایل کلی فرم */
            QWidget {
                background-color: #000000;
                color: #ffffff;
                font-family: 'B Nazanin';
            }
            
            /* گروه‌بندی */
            QGroupBox {
                font-weight: bold;
                border: 2px solid #3498db;
                border-radius: 8px;
                margin-top: 20px;
                padding-top: 10px;
                background-color: #111111;
            }
            
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top right;
                right: 10px;
                padding: 0 10px;
                color: #3498db;
                font-size: 12pt;
            }
            
            /* جدول حساب‌ها */
            #accounts_table {
                background-color: #111111;
                alternate-background-color: #0a0a0a;
                gridline-color: #333;
            }
            
            #accounts_table::item {
                padding: 8px;
                border-bottom: 1px solid #222;
            }
            
            #accounts_table::item:selected {
                background-color: #2ecc71;
                color: white;
            }
            
            /* دکمه‌ها */
            .primary_button {
                background-color: #27ae60;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-size: 11pt;
                font-weight: bold;
                min-width: 120px;
            }
            
            .primary_button:hover {
                background-color: #219653;
            }
            
            .secondary_button {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-size: 11pt;
                font-weight: bold;
                min-width: 120px;
            }
            
            .secondary_button:hover {
                background-color: #2980b9;
            }
            
            .danger_button {
                background-color: #e74c3c;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-size: 11pt;
                font-weight: bold;
                min-width: 120px;
            }
            
            .danger_button:hover {
                background-color: #c0392b;
            }
            
            /* فیلدهای جستجو */
            QLineEdit, QComboBox {
                background-color: #222222;
                border: 1px solid #333;
                border-radius: 4px;
                padding: 8px;
                color: white;
                min-height: 35px;
                font-size: 11pt;
            }
            
            QLineEdit:focus, QComboBox:focus {
                border: 2px solid #3498db;
            }
            
            QLineEdit::placeholder {
                color: #666;
            }
            
            /* برچسب‌ها */
            QLabel {
                color: #ffffff;
                font-size: 11pt;
            }
            
            .section_title {
                font-size: 14pt;
                font-weight: bold;
                color: #2ecc71;
                padding: 10px 0;
                border-bottom: 2px solid #2ecc71;
            }
            
            /* نوار ابزار */
            QToolBar {
                background-color: #111111;
                border-bottom: 1px solid #333;
                spacing: 10px;
                padding: 5px;
            }
        """)
    
    def init_ui(self):
        """ایجاد رابط کاربری"""
        # لیوت اصلی با اسکرول
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: #000000;
            }
        """)
        
        container = QWidget()
        container.setLayoutDirection(Qt.RightToLeft)
        main_layout = QVBoxLayout(container)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # 🔴 **عنوان بخش**
        title_label = QLabel("🏦 مدیریت حساب‌های بانکی و نقدی")
        title_label.setProperty("class", "section_title")
        title_label.setAlignment(Qt.AlignRight)
        main_layout.addWidget(title_label)
        
        # 🔴 **نوار ابزار عملیات**
        toolbar = QToolBar()
        toolbar.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        
        toolbar_actions = [
            ("➕", "حساب جدید", self.add_account, "#27ae60"),
            ("✏️", "ویرایش حساب", self.edit_account, "#3498db"),
            ("🗑️", "حذف حساب", self.delete_account, "#e74c3c"),
            ("🔄", "انتقال وجه", self.transfer_funds, "#9b59b6"),
            ("📊", "جزئیات حساب", self.show_account_details, "#f39c12"),
            ("🖨️", "چاپ لیست", self.print_accounts_list, "#1abc9c")
        ]
        
        for icon, text, callback, color in toolbar_actions:
            btn = QPushButton(f"{icon} {text}")
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {color};
                    color: white;
                    border: none;
                    padding: 8px 15px;
                    border-radius: 4px;
                    font-size: 10pt;
                    font-weight: bold;
                    min-width: 130px;
                }}
                QPushButton:hover {{
                    background-color: {self.darken_color(color)};
                }}
                QPushButton:disabled {{
                    background-color: #666;
                    color: #999;
                }}
            """)
            btn.clicked.connect(callback)
            toolbar.addWidget(btn)
        
        main_layout.addWidget(toolbar)
        
        # 🔴 **بخش جستجو و فیلتر**
        search_group = QGroupBox("🔍 جستجو و فیلتر")
        search_layout = QHBoxLayout()
        
        # فیلد جستجو
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("جستجو بر اساس نام حساب، شماره حساب، بانک...")
        
        # فیلتر نوع حساب
        self.account_type_filter = QComboBox()
        self.account_type_filter.addItems([
            "همه انواع حساب",
            "جاری",
            "پس‌انداز", 
            "صندوق",
            "بانکی",
            "نقدی"
        ])
        
        # فیلتر وضعیت
        self.status_filter = QComboBox()
        self.status_filter.addItems([
            "همه وضعیت‌ها",
            "✅ فعال",
            "❌ غیرفعال"
        ])
        
        # دکمه‌های فیلتر
        btn_search = QPushButton("🔍 اعمال فیلتر")
        btn_search.setProperty("class", "primary_button")
        btn_search.clicked.connect(self.filter_accounts)
        
        btn_clear = QPushButton("🗑️ پاک کردن")
        btn_clear.setProperty("class", "danger_button")
        btn_clear.clicked.connect(self.clear_filters)
        
        search_layout.addWidget(QLabel("نوع حساب:"))
        search_layout.addWidget(self.account_type_filter)
        search_layout.addWidget(QLabel("وضعیت:"))
        search_layout.addWidget(self.status_filter)
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(btn_search)
        search_layout.addWidget(btn_clear)
        
        search_group.setLayout(search_layout)
        main_layout.addWidget(search_group)
        
        # 🔴 **جدول حساب‌ها**
        table_group = QGroupBox("📋 لیست حساب‌ها")
        table_layout = QVBoxLayout()
        
        self.accounts_table = QTableWidget()
        self.accounts_table.setObjectName("accounts_table")
        self.accounts_table.setColumnCount(9)
        self.accounts_table.setHorizontalHeaderLabels([
            "ردیف",
            "شماره حساب",
            "نام حساب",
            "نوع حساب", 
            "بانک / صندوق",
            "موجودی فعلی",
            "تاریخ ایجاد",
            "آخرین بروزرسانی",
            "وضعیت"
        ])
        
        # تنظیمات جدول
        self.accounts_table.setAlternatingRowColors(True)
        self.accounts_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.accounts_table.setSelectionMode(QTableWidget.SingleSelection)
        self.accounts_table.horizontalHeader().setStretchLastSection(True)
        
        # تنظیم عرض ستون‌ها
        header = self.accounts_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Fixed)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(6, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(7, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(8, QHeaderView.ResizeToContents)
        
        self.accounts_table.setColumnWidth(0, 60)   # ردیف
        self.accounts_table.setColumnWidth(1, 150)  # شماره حساب
        self.accounts_table.setColumnWidth(3, 100)  # نوع حساب
        self.accounts_table.setColumnWidth(4, 150)  # بانک
        self.accounts_table.setColumnWidth(5, 150)  # موجودی
        self.accounts_table.setColumnWidth(6, 120)  # تاریخ ایجاد
        self.accounts_table.setColumnWidth(7, 120)  # آخرین بروزرسانی
        self.accounts_table.setColumnWidth(8, 100)  # وضعیت
        
        table_layout.addWidget(self.accounts_table)
        
        # 🔴 **آمار پایین جدول**
        stats_layout = QHBoxLayout()
        
        self.stats_label = QLabel("تعداد حساب‌ها: ۰ | موجودی کل: ۰ تومان")
        self.stats_label.setStyleSheet("""
            QLabel {
                color: #3498db;
                font-size: 11pt;
                font-weight: bold;
                padding: 8px;
                background-color: #111;
                border-radius: 5px;
                border: 1px solid #333;
            }
        """)
        
        btn_refresh = QPushButton("🔄 بروزرسانی")
        btn_refresh.setProperty("class", "secondary_button")
        btn_refresh.clicked.connect(self.load_accounts)
        
        stats_layout.addWidget(self.stats_label)
        stats_layout.addStretch()
        stats_layout.addWidget(btn_refresh)
        
        table_layout.addLayout(stats_layout)
        table_group.setLayout(table_layout)
        main_layout.addWidget(table_group)
        
        # 🔴 **اطلاعات حساب انتخاب شده**
        selection_group = QGroupBox("ℹ️ اطلاعات حساب انتخاب شده")
        selection_layout = QVBoxLayout()
        
        self.selection_info_label = QLabel("⚠️ هیچ حسابی انتخاب نشده است")
        self.selection_info_label.setStyleSheet("""
            QLabel {
                color: #f39c12;
                font-size: 11pt;
                padding: 12px;
                background-color: #222;
                border-radius: 6px;
                border: 1px solid #444;
            }
        """)
        self.selection_info_label.setAlignment(Qt.AlignRight)
        
        # دکمه‌های عملیات روی حساب انتخاب شده
        selection_buttons_layout = QHBoxLayout()
        
        btn_view_transactions = QPushButton("💰 مشاهده تراکنش‌ها")
        btn_view_transactions.setProperty("class", "secondary_button")
        btn_view_transactions.clicked.connect(self.view_account_transactions)
        
        btn_deposit = QPushButton("📥 واریز")
        btn_deposit.setProperty("class", "primary_button")
        btn_deposit.clicked.connect(self.deposit_to_account)
        
        btn_withdraw = QPushButton("📤 برداشت")
        btn_withdraw.setProperty("class", "danger_button")
        btn_withdraw.clicked.connect(self.withdraw_from_account)
        
        btn_edit_balance = QPushButton("🧮 تعدیل موجودی")
        btn_edit_balance.setProperty("class", "secondary_button")
        btn_edit_balance.clicked.connect(self.adjust_account_balance)
        
        selection_buttons_layout.addWidget(btn_view_transactions)
        selection_buttons_layout.addWidget(btn_deposit)
        selection_buttons_layout.addWidget(btn_withdraw)
        selection_buttons_layout.addWidget(btn_edit_balance)
        selection_buttons_layout.addStretch()
        
        selection_layout.addWidget(self.selection_info_label)
        selection_layout.addLayout(selection_buttons_layout)
        selection_group.setLayout(selection_layout)
        main_layout.addWidget(selection_group)
        
        scroll.setWidget(container)
        
        # لیوت نهایی
        final_layout = QVBoxLayout(self)
        final_layout.setContentsMargins(0, 0, 0, 0)
        final_layout.addWidget(scroll)
        
        # اتصال سیگنال انتخاب ردیف
        self.accounts_table.itemSelectionChanged.connect(self.on_account_selected)
    
    def darken_color(self, color):
        """تیره کردن رنگ برای hover"""
        color = color.lstrip('#')
        r, g, b = tuple(int(color[i:i+2], 16) for i in (0, 2, 4))
        r = max(0, r - 30)
        g = max(0, g - 30)
        b = max(0, b - 30)
        return f'#{r:02x}{g:02x}{b:02x}'

    def convert_to_jalali(self, gregorian_date):
        """تبدیل تاریخ میلادی به شمسی"""
        try:
            if not gregorian_date:
                return ""
            
            # اگر None باشد
            if gregorian_date is None:
                return ""
            
            # اگر رشته است
            if isinstance(gregorian_date, str):
                # حذف بخش زمانی اگر وجود دارد
                date_str = str(gregorian_date).strip()
                if ' ' in date_str:
                    date_str = date_str.split(' ')[0]
                
                # حذف T اگر وجود دارد (فرمت ISO)
                if 'T' in date_str:
                    date_str = date_str.split('T')[0]
                
                # تبدیل به تاریخ میلادی
                try:
                    # فرمت YYYY-MM-DD
                    miladi_date = datetime.strptime(date_str, '%Y-%m-%d').date()
                except:
                    try:
                        # فرمت YYYY/MM/DD
                        miladi_date = datetime.strptime(date_str, '%Y/%m/%d').date()
                    except:
                        # اگر تبدیل نشد، تاریخ اصلی را برگردان
                        return date_str
            
            # اگر datetime.datetime است
            elif isinstance(gregorian_date, datetime):
                miladi_date = gregorian_date.date()
            
            # اگر datetime.date است
            elif hasattr(gregorian_date, 'year'):
                miladi_date = gregorian_date
            
            else:
                return str(gregorian_date)
            
            # تبدیل به شمسی
            jalali_date = jdatetime.date.fromgregorian(date=miladi_date)
            return jalali_date.strftime('%Y/%m/%d')
            
        except Exception as e:
            print(f"⚠️ خطا در تبدیل تاریخ {gregorian_date}: {e}")
            return str(gregorian_date) 

    def load_accounts(self, filters=None):
        """بارگذاری حساب‌ها از دیتابیس"""
        try:
            # ساخت کوئری
            query = """
            SELECT 
                a.id,
                a.account_number,
                a.account_name,
                a.account_type,
                a.bank_name,
                a.current_balance,
                a.initial_balance,
                a.owner_name,
                a.description,
                a.is_active,
                a.created_at,
                a.updated_at,
                COUNT(at.id) as transaction_count
            FROM Accounts a
            LEFT JOIN AccountingTransactions at ON (
                at.from_account_id = a.id OR at.to_account_id = a.id
            )
            WHERE 1=1
            """
            
            params = []
            
            # اعمال فیلترها
            if filters:
                # فیلتر جستجو
                if filters.get('search'):
                    query += " AND (a.account_name LIKE ? OR a.account_number LIKE ? OR a.bank_name LIKE ?)"
                    search_term = f"%{filters['search']}%"
                    params.extend([search_term, search_term, search_term])
                
                # فیلتر نوع حساب
                if filters.get('type') and filters['type'] != "همه انواع حساب":
                    query += " AND a.account_type = ?"
                    params.append(filters['type'])
                
                # فیلتر وضعیت
                if filters.get('status'):
                    if filters['status'] == "✅ فعال":
                        query += " AND a.is_active = 1"
                    elif filters['status'] == "❌ غیرفعال":
                        query += " AND a.is_active = 0"
            
            query += " GROUP BY a.id ORDER BY a.account_type, a.account_name"
            
            # اجرای کوئری
            accounts = self.data_manager.db.fetch_all(query, params)
            
            # پاک کردن جدول
            self.accounts_table.setRowCount(0)
            
            # محاسبه مجموع موجودی
            total_balance = 0
            active_accounts = 0
            
            # پر کردن جدول
            for row, account in enumerate(accounts):
                self.accounts_table.insertRow(row)
                
                # شماره ردیف
                self.accounts_table.setItem(row, 0, 
                    QTableWidgetItem(str(row + 1)))
                
                # شماره حساب
                self.accounts_table.setItem(row, 1, 
                    QTableWidgetItem(account.get('account_number', '')))
                
                # نام حساب
                self.accounts_table.setItem(row, 2, 
                    QTableWidgetItem(account.get('account_name', '')))
                
                # نوع حساب
                self.accounts_table.setItem(row, 3, 
                    QTableWidgetItem(account.get('account_type', '')))
                
                # بانک / صندوق
                bank_name = account.get('bank_name', '')
                if not bank_name and account.get('account_type') in ['صندوق', 'نقدی']:
                    bank_name = "صندوق فروشگاه"
                self.accounts_table.setItem(row, 4, 
                    QTableWidgetItem(bank_name))
                
                # موجودی فعلی (تومان)
                balance = float(account.get('current_balance', 0)) / 10
                balance_item = QTableWidgetItem(f"{balance:,.0f} تومان")
                
                # رنگ‌بندی بر اساس موجودی
                if balance > 0:
                    balance_item.setForeground(QColor('#27ae60'))  # سبز
                elif balance < 0:
                    balance_item.setForeground(QColor('#e74c3c'))  # قرمز
                else:
                    balance_item.setForeground(QColor('#f39c12'))  # نارنجی
                
                self.accounts_table.setItem(row, 5, balance_item)
                total_balance += balance
                
                # تاریخ ایجاد (شمسی)
                created_date = account.get('created_at', '')
                if created_date:
                    try:
                        jalali_date = self.data_manager.db.gregorian_to_jalali(created_date)
                        self.accounts_table.setItem(row, 6, 
                            QTableWidgetItem(jalali_date))
                    except Exception as e:
                        print(f"⚠️ خطا در تبدیل تاریخ ایجاد {created_date}: {e}")
                        # نمایش تاریخ اصلی در صورت خطا
                        self.accounts_table.setItem(row, 6, 
                            QTableWidgetItem(str(created_date)))
                else:
                    self.accounts_table.setItem(row, 6, QTableWidgetItem(""))
                
                # آخرین بروزرسانی
                updated_date = account.get('updated_at', '')
                if updated_date:
                    try:
                        jalali_updated = self.data_manager.db.gregorian_to_jalali(updated_date)
                        self.accounts_table.setItem(row, 7, 
                            QTableWidgetItem(jalali_updated))
                    except Exception as e:
                        print(f"⚠️ خطا در تبدیل تاریخ بروزرسانی {updated_date}: {e}")
                        self.accounts_table.setItem(row, 7, 
                            QTableWidgetItem(str(updated_date)))
                else:
                    self.accounts_table.setItem(row, 7, QTableWidgetItem(""))
                
                # وضعیت
                is_active = account.get('is_active', 1)
                status_text = "✅ فعال" if is_active else "❌ غیرفعال"
                status_item = QTableWidgetItem(status_text)
                status_item.setForeground(QColor('#27ae60' if is_active else '#e74c3c'))
                self.accounts_table.setItem(row, 8, status_item)
                
                if is_active:
                    active_accounts += 1
                
                # ذخیره شناسه حساب در تمام ستون‌های ردیف
                for col in range(self.accounts_table.columnCount()):
                    item = self.accounts_table.item(row, col)
                    if item:
                        item.setData(Qt.UserRole, account.get('id'))
            
            # به‌روزرسانی آمار
            self.stats_label.setText(
                f"تعداد حساب‌ها: {len(accounts)} ({active_accounts} فعال) | "
                f"موجودی کل: {total_balance:,.0f} تومان"
            )
            
            print(f"✅ {len(accounts)} حساب بارگذاری شد")
            
        except Exception as e:
            print(f"❌ خطا در بارگذاری حساب‌ها: {e}")
            QMessageBox.critical(self, "خطا", f"خطا در بارگذاری حساب‌ها:\n\n{str(e)}")
    
    def filter_accounts(self):
        """اعمال فیلترها بر روی حساب‌ها"""
        filters = {
            'search': self.search_input.text().strip(),
            'type': self.account_type_filter.currentText(),
            'status': self.status_filter.currentText()
        }
        self.load_accounts(filters)
    
    def clear_filters(self):
        """پاک کردن فیلترها"""
        self.search_input.clear()
        self.account_type_filter.setCurrentIndex(0)
        self.status_filter.setCurrentIndex(0)
        self.load_accounts()
    
    def on_account_selected(self):
        """هنگام انتخاب حساب از جدول"""
        selected_items = self.accounts_table.selectedItems()
        if selected_items:
            first_item = selected_items[0]
            self.selected_account_id = first_item.data(Qt.UserRole)
            
            # دریافت اطلاعات حساب
            query = "SELECT * FROM Accounts WHERE id = ?"
            account = self.data_manager.db.fetch_one(query, (self.selected_account_id,))
            
            if account:
                balance = float(account.get('current_balance', 0)) / 10
                owner = account.get('owner_name', 'تعیین نشده')
                
                info_text = (
                    f"🏦 حساب: {account.get('account_name')}\n"
                    f"🔢 شماره: {account.get('account_number')}\n"
                    f"💰 موجودی: {balance:,.0f} تومان\n"
                    f"👤 صاحب حساب: {owner}\n"
                    f"🏛️ بانک: {account.get('bank_name', 'صندوق فروشگاه')}"
                )
                
                self.selection_info_label.setText(info_text)
                self.selection_info_label.setStyleSheet("""
                    QLabel {
                        color: #2ecc71;
                        font-size: 11pt;
                        padding: 12px;
                        background-color: #222;
                        border-radius: 6px;
                        border: 1px solid #2ecc71;
                    }
                """)
    
    # ---------- متدهای عملیاتی ----------
    
    def add_account(self):
        """افزودن حساب جدید"""
        try:
            from ..dialogs.account_dialog import AccountDialog
            dialog = AccountDialog(self.data_manager, parent=self)
            if dialog.exec():
                self.load_accounts()
                self.data_changed.emit()
        except ImportError:
            QMessageBox.information(self, "افزودن حساب", 
                "فرم افزودن حساب به زودی اضافه خواهد شد.")
    
    def edit_account(self):
        """ویرایش حساب انتخاب شده"""
        if not self.selected_account_id:
            QMessageBox.warning(self, "هشدار", "⚠️ لطفاً ابتدا یک حساب را انتخاب کنید.")
            return
        
        try:
            from ..dialogs.account_dialog import AccountDialog
            dialog = AccountDialog(self.data_manager, 
                                 account_id=self.selected_account_id, 
                                 parent=self)
            if dialog.exec():
                self.load_accounts()
                self.data_changed.emit()
        except ImportError:
            QMessageBox.information(self, "ویرایش حساب", 
                "فرم ویرایش حساب به زودی اضافه خواهد شد.")
    
    def delete_account(self):
        """حذف (غیرفعال کردن) حساب"""
        if not self.selected_account_id:
            QMessageBox.warning(self, "هشدار", "⚠️ لطفاً ابتدا یک حساب را انتخاب کنید.")
            return
        
        reply = QMessageBox.question(
            self, "تأیید حذف",
            "آیا از غیرفعال کردن این حساب اطمینان دارید؟\n\n"
            "⚠️ توجه: حساب‌های غیرفعال در لیست اصلی نمایش داده نمی‌شوند.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                query = "UPDATE Accounts SET is_active = 0 WHERE id = ?"
                success = self.data_manager.db.execute_query(query, (self.selected_account_id,))
                
                if success:
                    QMessageBox.information(self, "موفق", "✅ حساب با موفقیت غیرفعال شد.")
                    self.load_accounts()
                    self.data_changed.emit()
                    self.selected_account_id = None
                    self.selection_info_label.setText("⚠️ هیچ حسابی انتخاب نشده است")
                else:
                    QMessageBox.critical(self, "خطا", "❌ خطا در غیرفعال کردن حساب.")
            except Exception as e:
                QMessageBox.critical(self, "خطا", f"❌ خطا در غیرفعال کردن حساب:\n\n{str(e)}")
    
    def transfer_funds(self):
        """انتقال وجه بین حساب‌ها"""
        try:
            from ..dialogs.transfer_dialog import TransferDialog
            dialog = TransferDialog(self.data_manager, parent=self)
            if dialog.exec():
                self.load_accounts()
                self.data_changed.emit()
        except ImportError:
            QMessageBox.information(self, "انتقال وجه", 
                "فرم انتقال وجه به زودی اضافه خواهد شد.")
    
    def show_account_details(self):
        """نمایش جزئیات حساب"""
        if not self.selected_account_id:
            QMessageBox.warning(self, "هشدار", "⚠️ لطفاً ابتدا یک حساب را انتخاب کنید.")
            return
        
        try:
            from ..dialogs.account_details_dialog import AccountDetailsDialog
            dialog = AccountDetailsDialog(self.data_manager, 
                                        self.selected_account_id, 
                                        parent=self)
            dialog.exec()
        except ImportError:
            QMessageBox.information(self, "جزئیات حساب", 
                "فرم جزئیات حساب به زودی اضافه خواهد شد.")
    
    def print_accounts_list(self):
        """چاپ لیست حساب‌ها"""
        QMessageBox.information(self, "چاپ لیست", 
            "✅ لیست حساب‌ها آماده چاپ است.\n\nاین قابلیت به زودی فعال خواهد شد.")
    
    def view_account_transactions(self):
        """مشاهده تراکنش‌های حساب انتخاب شده"""
        if not self.selected_account_id:
            QMessageBox.warning(self, "هشدار", "⚠️ لطفاً ابتدا یک حساب را انتخاب کنید.")
            return
        
        QMessageBox.information(self, "تراکنش‌ها", 
            "📋 نمایش تراکنش‌های حساب.\n\nاین قابلیت به زودی فعال خواهد شد.")
    
    def deposit_to_account(self):
        """واریز به حساب انتخاب شده"""
        if not self.selected_account_id:
            QMessageBox.warning(self, "هشدار", "⚠️ لطفاً ابتدا یک حساب را انتخاب کنید.")
            return
        
        QMessageBox.information(self, "واریز", 
            "📥 واریز به حساب.\n\nاین قابلیت به زودی فعال خواهد شد.")
    
    def withdraw_from_account(self):
        """برداشت از حساب انتخاب شده"""
        if not self.selected_account_id:
            QMessageBox.warning(self, "هشدار", "⚠️ لطفاً ابتدا یک حساب را انتخاب کنید.")
            return
        
        QMessageBox.information(self, "برداشت", 
            "📤 برداشت از حساب.\n\nاین قابلیت به زودی فعال خواهد شد.")
    
    def adjust_account_balance(self):
        """تعدیل موجودی حساب"""
        if not self.selected_account_id:
            QMessageBox.warning(self, "هشدار", "⚠️ لطفاً ابتدا یک حساب را انتخاب کنید.")
            return
        
        QMessageBox.information(self, "تعدیل موجودی", 
            "🧮 تعدیل موجودی حساب.\n\nاین قابلیت به زودی فعال خواهد شد.")
    
    def refresh_data(self):
        """بروزرسانی داده‌های فرم"""
        print("🔄 بروزرسانی فرم حساب‌ها...")
        self.load_accounts()
        self.data_changed.emit()


# تست مستقل
if __name__ == "__main__":
    import sys
    from PySide6.QtWidgets import QApplication
    from database.database import DatabaseManager
    
    app = QApplication(sys.argv)
    
    # ایجاد مدیر داده
    db_manager = DatabaseManager("data/repair_shop.db")
    
    # ایجاد فرم حساب‌ها
    form = AccountsForm(db_manager)
    form.setWindowTitle("فرم مدیریت حساب‌ها")
    form.resize(1000, 700)
    form.show()
    
    sys.exit(app.exec())