"""
ویجت نمایش موجودی حساب‌ها
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QColor


class AccountBalanceWidget(QWidget):
    """ویجت نمایش موجودی یک حساب"""
    
    def __init__(self, data_manager, account_id=None):
        super().__init__()
        self.data_manager = data_manager
        self.account_id = account_id
        
        self.setup_ui()
        
        if account_id:
            self.load_account_data()
        
        # تایمر برای به‌روزرسانی خودکار
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_balance)
        self.timer.start(30000)  # هر 30 ثانیه
    
    def setup_ui(self):
        """ایجاد رابط کاربری ویجت"""
        self.setStyleSheet("""
            QWidget {
                background-color: #111111;
                border-radius: 8px;
                border: 2px solid #333;
            }
        """)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)
        
        # عنوان
        self.title_label = QLabel("موجودی حساب")
        self.title_label.setStyleSheet("""
            QLabel {
                color: #bbb;
                font-size: 12pt;
                font-weight: bold;
            }
        """)
        self.title_label.setAlignment(Qt.AlignRight)
        layout.addWidget(self.title_label)
        
        # موجودی
        self.balance_label = QLabel("در حال بارگذاری...")
        self.balance_label.setStyleSheet("""
            QLabel {
                color: #ffffff;
                font-size: 20pt;
                font-weight: bold;
            }
        """)
        self.balance_label.setAlignment(Qt.AlignRight)
        layout.addWidget(self.balance_label)
        
        # نام حساب
        self.account_name_label = QLabel("")
        self.account_name_label.setStyleSheet("""
            QLabel {
                color: #3498db;
                font-size: 10pt;
            }
        """)
        self.account_name_label.setAlignment(Qt.AlignRight)
        layout.addWidget(self.account_name_label)
        
        # شماره حساب
        self.account_number_label = QLabel("")
        self.account_number_label.setStyleSheet("""
            QLabel {
                color: #95a5a6;
                font-size: 9pt;
            }
        """)
        self.account_number_label.setAlignment(Qt.AlignRight)
        layout.addWidget(self.account_number_label)
        
        self.setLayout(layout)
    
    def load_account_data(self):
        """بارگذاری اطلاعات حساب"""
        if not self.account_id:
            return
        
        try:
            query = """
            SELECT 
                account_name,
                account_number,
                current_balance,
                account_type,
                bank_name
            FROM Accounts 
            WHERE id = ? AND is_active = 1
            """
            
            account = self.data_manager.db.fetch_one(query, (self.account_id,))
            
            if account:
                # به‌روزرسانی برچسب‌ها
                self.title_label.setText(f"موجودی {account.get('account_type', 'حساب')}")
                self.account_name_label.setText(account.get('account_name', ''))
                self.account_number_label.setText(account.get('account_number', ''))
                
                # محاسبه و نمایش موجودی
                self.update_balance()
        
        except Exception as e:
            print(f"⚠️ خطا در بارگذاری اطلاعات حساب: {e}")
    
    def update_balance(self):
        """به‌روزرسانی موجودی"""
        if not self.account_id:
            return
        
        try:
            query = "SELECT current_balance FROM Accounts WHERE id = ?"
            result = self.data_manager.db.fetch_one(query, (self.account_id,))
            
            if result and result.get('current_balance') is not None:
                balance = float(result['current_balance']) / 10  # تبدیل به تومان
                
                # نمایش موجودی
                self.balance_label.setText(f"{balance:,.0f} تومان")
                
                # رنگ‌بندی بر اساس مقدار
                if balance > 0:
                    self.balance_label.setStyleSheet("""
                        QLabel {
                            color: #27ae60;
                            font-size: 20pt;
                            font-weight: bold;
                        }
                    """)
                elif balance < 0:
                    self.balance_label.setStyleSheet("""
                        QLabel {
                            color: #e74c3c;
                            font-size: 20pt;
                            font-weight: bold;
                        }
                    """)
                else:
                    self.balance_label.setStyleSheet("""
                        QLabel {
                            color: #f39c12;
                            font-size: 20pt;
                            font-weight: bold;
                        }
                    """)
            else:
                self.balance_label.setText("اطلاعات موجود نیست")
                self.balance_label.setStyleSheet("""
                    QLabel {
                        color: #95a5a6;
                        font-size: 16pt;
                        font-weight: bold;
                    }
                """)
        
        except Exception as e:
            print(f"⚠️ خطا در به‌روزرسانی موجودی: {e}")
            self.balance_label.setText("خطا در محاسبه")
            self.balance_label.setStyleSheet("""
                QLabel {
                    color: #e74c3c;
                    font-size: 16pt;
                    font-weight: bold;
                }
            """)