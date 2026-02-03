# ui/forms/inventory/inventory_main_form.py
"""
فرم اصلی مدیریت انبارها - نسخه اصلاح شده
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTabWidget,
    QLabel, QPushButton, QGridLayout, QGroupBox,
    QMessageBox, QFrame, QScrollArea, QSizePolicy
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont
from PySide6.QtCore import QSize

from .base_inventory_form import BaseInventoryForm
from typing import Optional, Dict, Any


class InventoryMainForm(BaseInventoryForm):
    """فرم اصلی انبار با 4 تب و خلاصه کشویی"""
    
    def __init__(self, parent=None, config_manager=None, permission_manager=None):
        # حل مشکل parent
        if parent is not None and not isinstance(parent, QWidget):
            super().__init__("مدیریت انبارها", None)
            if hasattr(parent, 'data_manager'):
                self.data_manager = parent.data_manager
            else:
                self.data_manager = None
        else:
            super().__init__("مدیریت انبارها", parent)
            self.data_manager = parent.data_manager if parent and hasattr(parent, 'data_manager') else None
        
        # ذخیره parent برای استفاده بعدی
        self.window_parent = parent
        
        # تعریف متغیرهای فرم‌های تب‌ها
        self.new_parts_form = None
        self.used_parts_form = None
        self.new_appliances_form = None
        self.used_appliances_form = None
        
        # دیکشنری برای ذخیره فرم‌ها
        self.tab_forms: Dict[str, Any] = {}
        
        # دیکشنری برای ذخیره کارت‌های خلاصه
        self.summary_cards: Dict[str, QFrame] = {}
        
        # ایجاد ویجت تب‌ها
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabPosition(QTabWidget.North)
        
        # فراخوانی توابع setup
        self.create_navigation_bar()
        self.create_collapsible_summary()
        self.setup_tab_forms()
        
        # اضافه کردن تب‌ها به فرم
        self.main_layout.addWidget(self.tab_widget)
        
        # بارگذاری داده‌ها
        self.load_summary_data()
        
        self.config_manager = config_manager
        self.permission_manager = permission_manager
        
        # بارگذاری تنظیمات انبار
        self.load_inventory_config()
        
        # اعمال محدودیت‌ها
        self.setup_inventory_restrictions()


        print("✅ فرم اصلی انبار با موفقیت ایجاد شد")

    def load_inventory_config(self):
        """بارگذاری تنظیمات انبار"""
        if self.config_manager:
            self.inventory_config = self.config_manager.get('inventory', {})
            
            # تنظیم مقادیر پیش‌فرض
            self.default_min_stock = self.inventory_config.get('min_stock_default', 5)
            self.default_max_stock = self.inventory_config.get('max_stock_default', 100)
            self.low_stock_warning = self.inventory_config.get('low_stock_warning', 10)
    
    def setup_inventory_restrictions(self):
        """تنظیم محدودیت‌های انبار"""
        if not self.permission_manager:
            return
        
        # بررسی دسترسی به انواع انبار
        warehouses = {
            'قطعات نو': 'edit_new_parts',
            'قطعات دست دوم': 'edit_used_parts',
            'لوازم نو': 'edit_new_appliances',
            'لوازم دست دوم': 'edit_used_appliances'
        }
        
        for warehouse_name, permission in warehouses.items():
            if not self.permission_manager.has_permission(permission):
                # غیرفعال کردن تب یا دکمه مربوطه
                pass
    
    def validate_stock_quantity(self, quantity, warehouse_type):
        """اعتبارسنجی تعداد بر اساس تنظیمات"""
        if quantity < 0:
            return False, "تعداد نمی‌تواند منفی باشد"
        
        if quantity > self.default_max_stock:
            return False, f"تعداد نمی‌تواند بیشتر از {self.default_max_stock} باشد"
        
        return True, ""

    def create_navigation_bar(self):
        """ایجاد نوار ناوبری برای بازگشت به داشبورد"""
        nav_frame = QFrame()
        nav_frame.setStyleSheet("""
            QFrame {
                background-color: #1a1a1a;
                border-bottom: 2px solid #333333;
                padding: 10px;
            }
        """)
        
        nav_layout = QHBoxLayout()
        nav_layout.setContentsMargins(5, 5, 5, 5)
        
        # دکمه بازگشت
        btn_back = QPushButton("🏠 بازگشت به داشبورد")
        btn_back.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 15px;
                font-size: 11pt;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        
        # بررسی اینکه آیا در پنجره مستقل هستیم
        if self.window_parent and hasattr(self.window_parent, 'close'):
            # اگر در پنجره مستقل هستیم، پنجره را ببند
            btn_back.clicked.connect(self.window_parent.close)
        elif self.parent() and hasattr(self.parent(), 'show_dashboard'):
            # اگر در پنجره اصلی تعبیه شده‌ایم
            btn_back.clicked.connect(self.parent().show_dashboard)
        else:
            btn_back.clicked.connect(self.return_to_dashboard)
        
        nav_layout.addWidget(btn_back)
        nav_layout.addStretch()
        
        # عنوان
        title_label = QLabel("📦 سیستم مدیریت انبار")
        title_label.setStyleSheet("""
            QLabel {
                color: #ffffff;
                font-size: 16pt;
                font-weight: bold;
            }
        """)
        nav_layout.addWidget(title_label)
        nav_layout.addStretch()
        
        # دکمه تازه‌سازی
        btn_refresh = QPushButton("🔄 تازه‌سازی")
        btn_refresh.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 15px;
                font-size: 11pt;
            }
            QPushButton:hover {
                background-color: #219653;
            }
        """)
        btn_refresh.clicked.connect(self.refresh_all_tabs)
        
        nav_layout.addWidget(btn_refresh)
        
        nav_frame.setLayout(nav_layout)
        self.main_layout.insertWidget(0, nav_frame)
    
    def return_to_dashboard(self):
        """بازگشت به داشبورد اصلی"""
        print("📌 بازگشت به داشبورد")
        # اگر پنجره والد وجود دارد و تابع close دارد، آن را ببند
        if self.window_parent and hasattr(self.window_parent, 'close'):
            self.window_parent.close()
    
    def create_collapsible_summary(self):
        """ایجاد پنل خلاصه کشویی ساده"""
        # ایجاد GroupBox با قابلیت باز و بسته شدن
        self.summary_group = QGroupBox("📊 خلاصه انبار (برای مشاهده کلیک کنید)")
        self.summary_group.setCheckable(True)
        self.summary_group.setChecked(False)  # به صورت پیش‌فرض بسته است
        self.summary_group.setStyleSheet("""
            QGroupBox {
                border: 2px solid #3498db;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 15px;
                font-size: 11pt;
                font-weight: bold;
                background-color: rgba(52, 152, 219, 0.1);
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 10px 0 10px;
                color: #3498db;
            }
        """)
        
        # Layout برای محتوای خلاصه
        summary_content = QWidget()
        self.summary_layout = QGridLayout(summary_content)
        self.summary_layout.setContentsMargins(15, 15, 15, 15)
        self.summary_layout.setSpacing(15)
        
        # محتوای اولیه (مقادیر پیش‌فرض)
        summaries = [
            ("قطعات نو", "📦", "#3498db", "0 قلم", "0", "0 تومان"),
            ("قطعات دست دوم", "🔩", "#9b59b6", "0 قلم", "0", "0 تومان"),
            ("لوازم نو", "🆕", "#2ecc71", "0 قلم", "0", "0 تومان"),
            ("لوازم دست دوم", "🔄", "#e74c3c", "0 قلم", "0", "0 تومان"),
        ]
        
        row, col = 0, 0
        for title, icon, color, items, low, value in summaries:
            card = self.create_summary_card(title, icon, color, items, low, value)
            self.summary_cards[title] = card
            self.summary_layout.addWidget(card, row, col)
            col += 1
            if col > 1:  # دو ستون
                col = 0
                row += 1
        
        # Set content widget to summary group
        self.summary_group.setLayout(QVBoxLayout())
        self.summary_group.layout().addWidget(summary_content)
        
        # مخفی کردن محتوا در ابتدا
        summary_content.setVisible(False)
        
        # اتصال signal برای باز و بسته شدن
        self.summary_group.toggled.connect(summary_content.setVisible)
        
        # اضافه کردن به بالای فرم
        self.main_layout.insertWidget(0, self.summary_group)
    
    def create_summary_card(self, title: str, icon: str, color: str, items: str, low: str, value: str) -> QFrame:
        """ایجاد کارت خلاصه کوچک"""
        card = QFrame()
        card.setFrameShape(QFrame.StyledPanel)
        card.setStyleSheet(f"""
            QFrame {{
                background-color: {color}15;
                border: 1px solid {color};
                border-radius: 8px;
                padding: 12px;
            }}
            QFrame:hover {{
                background-color: {color}25;
                border: 1px solid {color}99;
            }}
        """)
        
        layout = QVBoxLayout()
        layout.setSpacing(8)
        
        # هدر کارت
        header_layout = QHBoxLayout()
        icon_label = QLabel(icon)
        icon_label.setStyleSheet(f"font-size: 18pt; color: {color};")
        
        title_label = QLabel(title)
        title_label.setStyleSheet(f"""
            QLabel {{
                color: {color};
                font-size: 11pt;
                font-weight: bold;
            }}
        """)
        
        header_layout.addWidget(icon_label)
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        
        layout.addLayout(header_layout)
        
        # اطلاعات آماری
        # تعداد کل
        items_layout = QHBoxLayout()
        items_label = QLabel("تعداد:")
        items_label.setStyleSheet("color: #cccccc; font-size: 9pt;")
        items_value = QLabel(items)
        items_value.setStyleSheet(f"color: {color}; font-weight: bold; font-size: 10pt;")
        items_value.setObjectName(f"{title}_items")
        items_layout.addWidget(items_label)
        items_layout.addStretch()
        items_layout.addWidget(items_value)
        layout.addLayout(items_layout)
        
        # موجودی کم
        low_layout = QHBoxLayout()
        low_label = QLabel("کمبود:")
        low_label.setStyleSheet("color: #cccccc; font-size: 9pt;")
        low_value = QLabel(low)
        low_value.setStyleSheet("color: #e74c3c; font-weight: bold; font-size: 10pt;")
        low_value.setObjectName(f"{title}_low")
        low_layout.addWidget(low_label)
        low_layout.addStretch()
        low_layout.addWidget(low_value)
        layout.addLayout(low_layout)
        
        # ارزش کل
        value_layout = QHBoxLayout()
        value_label = QLabel("ارزش:")
        value_label.setStyleSheet("color: #cccccc; font-size: 9pt;")
        value_value = QLabel(value)
        value_value.setStyleSheet("color: #f39c12; font-weight: bold; font-size: 10pt;")
        value_value.setObjectName(f"{title}_value")
        value_layout.addWidget(value_label)
        value_layout.addStretch()
        value_layout.addWidget(value_value)
        layout.addLayout(value_layout)
        
        # دکمه مشاهده جزئیات
        btn_detail = QPushButton("مشاهده →")
        btn_detail.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                color: white;
                border: none;
                border-radius: 5px;
                padding: 6px;
                font-size: 9pt;
                margin-top: 5px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {self.darken_color(color)};
            }}
        """)
        
        # اتصال دکمه به تب مربوطه
        btn_detail.clicked.connect(lambda checked, t=title: self.switch_to_tab(t))
        
        layout.addWidget(btn_detail)
        card.setLayout(layout)
        
        return card
    
    def switch_to_tab(self, title: str):
        """سوئیچ به تب مربوطه"""
        tab_map = {
            "قطعات نو": 0,
            "قطعات دست دوم": 1,
            "لوازم نو": 2,
            "لوازم دست دوم": 3
        }
        
        if title in tab_map:
            self.tab_widget.setCurrentIndex(tab_map[title])
    
    def darken_color(self, hex_color: str) -> str:
        """تیره کردن رنگ HEX"""
        try:
            if hex_color.startswith("#"):
                r = int(hex_color[1:3], 16)
                g = int(hex_color[3:5], 16)
                b = int(hex_color[5:7], 16)
                
                r = max(0, r - 40)
                g = max(0, g - 40)
                b = max(0, b - 40)
                
                return f"#{r:02x}{g:02x}{b:02x}"
        except:
            return hex_color
        return hex_color
    

    def setup_tab_forms(self):
        """ایجاد فرم‌های تب‌های مختلف"""
        print("🔄 در حال ایجاد تب‌های انبار...")
        
        # لیست فرم‌ها به همراه کلاس‌های مربوطه
        tab_configs = [
            ("new_parts_form", "📦 قطعات نو", "NewPartsForm"),
            ("used_parts_form", "🔩 قطعات دست دوم", "UsedPartsForm"),
            ("new_appliances_form", "🆕 لوازم نو", "NewAppliancesForm"),
            ("used_appliances_form", "🔄 لوازم دست دوم", "UsedAppliancesForm"),
            ("stock_transaction_form", "📊 تراکنش‌ها", "StockTransactionForm"),
            ("inventory_report_form", "📈 گزارش‌گیری", "InventoryReportForm"),  # جدید
            ("inventory_settings_form", "⚙️ تنظیمات", "InventorySettingsForm")   # جدید
        ]
        
        for form_attr, tab_text, form_class_name in tab_configs:
            try:
                print(f"  📝 ایجاد تب {tab_text}...")
                
                # ایمپورت داینامیک فرم‌ها
                form_instance = self.import_and_create_form(form_class_name, form_attr)
                if form_instance:
                    self.tab_widget.addTab(form_instance, tab_text)
                    print(f"  ✅ تب {tab_text} ایجاد شد")
                else:
                    print(f"  ⚠️ فرم {form_class_name} یافت نشد")
                    self.add_error_tab(tab_text, f"فرم {form_class_name} یافت نشد")
            except Exception as e:
                print(f"  ❌ خطا در بارگذاری فرم {tab_text}: {e}")
                self.add_error_tab(tab_text, str(e))

    def import_and_create_form(self, form_class_name: str, form_attr: str) -> Optional[QWidget]:
        """ایمپورت و ایجاد فرم به صورت داینامیک"""
        try:
            # ایمپورت فرم مورد نظر
            if form_class_name == "NewPartsForm":
                from .new_parts_form import NewPartsForm
                form_class = NewPartsForm
            elif form_class_name == "UsedPartsForm":
                from .used_parts_form import UsedPartsForm
                form_class = UsedPartsForm
            elif form_class_name == "NewAppliancesForm":
                from .new_appliances_form import NewAppliancesForm
                form_class = NewAppliancesForm
            elif form_class_name == "UsedAppliancesForm":
                from .used_appliances_form import UsedAppliancesForm
                form_class = UsedAppliancesForm
            elif form_class_name == "StockTransactionForm":
                from .stock_transaction_form import StockTransactionForm
                form_class = StockTransactionForm
            elif form_class_name == "InventoryReportForm":  # جدید
                from .inventory_report_form import InventoryReportForm
                form_class = InventoryReportForm
            elif form_class_name == "InventorySettingsForm":  # جدید
                from .inventory_settings_form import InventorySettingsForm
                form_class = InventorySettingsForm
            else:
                print(f"  ⚠️ کلاس {form_class_name} شناخته نشد")
                return None
            
            # ایجاد نمونه فرم
            print(f"    ایجاد نمونه از {form_class_name}...")
            form_instance = form_class(self)
            
            # ذخیره در متغیرهای کلاس
            setattr(self, form_attr, form_instance)
            
            # ذخیره در دیکشنری فرم‌ها
            self.tab_forms[form_attr] = form_instance
            
            return form_instance
            
        except ImportError as e:
            print(f"  ⚠️ خطای ایمپورت برای {form_class_name}: {e}")
            return None
        except Exception as e:
            print(f"  ⚠️ خطای ایجاد برای {form_class_name}: {e}")
            return None
 
    
    def add_error_tab(self, tab_text: str, error_message: str):
        """اضافه کردن تب خطا"""
        try:
            error_widget = QWidget()
            error_layout = QVBoxLayout()
            
            error_label = QLabel(f"⚠️ خطا در بارگذاری {tab_text}")
            error_label.setStyleSheet("color: #e74c3c; font-size: 14pt; font-weight: bold; padding: 20px;")
            error_label.setAlignment(Qt.AlignCenter)
            
            detail_label = QLabel(f"خطا: {error_message[:100]}...")
            detail_label.setStyleSheet("color: #cccccc; font-size: 10pt; padding: 10px;")
            detail_label.setAlignment(Qt.AlignCenter)
            detail_label.setWordWrap(True)
            
            retry_btn = QPushButton("🔄 تلاش مجدد")
            retry_btn.setStyleSheet("""
                QPushButton {
                    background-color: #3498db;
                    color: white;
                    border: none;
                    border-radius: 5px;
                    padding: 10px;
                    margin: 10px;
                    font-size: 11pt;
                }
                QPushButton:hover {
                    background-color: #2980b9;
                }
            """)
            retry_btn.clicked.connect(lambda: self.retry_form_load(tab_text))
            
            error_layout.addStretch()
            error_layout.addWidget(error_label)
            error_layout.addWidget(detail_label)
            error_layout.addWidget(retry_btn)
            error_layout.addStretch()
            
            error_widget.setLayout(error_layout)
            self.tab_widget.addTab(error_widget, f"⚠️ {tab_text}")
            
        except Exception as e:
            print(f"❌ خطا در ایجاد تب خطا: {e}")
    
    def retry_form_load(self, tab_text: str):
        """تلاش مجدد برای بارگذاری فرم"""
        print(f"🔄 تلاش مجدد برای بارگذاری {tab_text}")
        
        # پیدا کردن index تب
        for i in range(self.tab_widget.count()):
            if self.tab_widget.tabText(i) == f"⚠️ {tab_text}":
                self.tab_widget.removeTab(i)
                break
        
        # دوباره فرم را بارگذاری کن
        self.setup_tab_forms()
    
    def load_summary_data(self):
        """بارگذاری داده‌های خلاصه انبارها"""
        QTimer.singleShot(500, self.refresh_summary)
    
    def refresh_summary(self):
        """تازه‌سازی خلاصه وضعیت انبارها"""
        try:
            print("📊 تازه‌سازی خلاصه انبار...")
            
            # جمع‌آوری آمار از فرم‌ها
            stats_data = {}
            
            # برای هر تب آمار بگیر
            for i in range(self.tab_widget.count()):
                form = self.tab_widget.widget(i)
                if form and hasattr(form, 'all_data'):
                    try:
                        data = form.all_data
                        
                        # محاسبه آمار
                        total_items = len(data)
                        low_stock = sum(1 for item in data if self.is_low_stock(item))
                        total_value = sum(self.get_item_value(item) for item in data)
                        
                        # نام تب
                        tab_name = self.tab_widget.tabText(i)
                        clean_name = tab_name.replace("📦", "").replace("🔩", "").replace("🆕", "").replace("🔄", "").replace("⚠️", "").strip()
                        
                        stats_data[clean_name] = {
                            "items": total_items,
                            "low": low_stock,
                            "value": total_value
                        }
                        
                        print(f"  📊 آمار {clean_name}: {total_items} قلم، {low_stock} کمبود، {total_value} تومان")
                    except Exception as e:
                        print(f"  ⚠️ خطا در محاسبه آمار تب {i}: {e}")
            
            # به‌روزرسانی کارت‌ها
            self.update_summary_cards(stats_data)
            
        except Exception as e:
            print(f"⚠️ خطا در تازه‌سازی خلاصه: {e}")
    
    def is_low_stock(self, item: Dict) -> bool:
        """بررسی موجودی کم"""
        try:
            quantity = item.get('quantity', 0)
            min_stock = item.get('min_stock', 5)
            return quantity <= min_stock
        except:
            return False
    
    def get_item_value(self, item: Dict) -> float:
        """دریافت ارزش یک آیتم"""
        try:
            quantity = item.get('quantity', 0)
            price = item.get('purchase_price', item.get('sale_price', 0))
            return quantity * price
        except:
            return 0
    
    def update_summary_cards(self, stats_data: Dict[str, Dict]):
        """به‌روزرسانی کارت‌های خلاصه"""
        for title, stats in stats_data.items():
            if title in self.summary_cards:
                card = self.summary_cards[title]
                
                # پیدا کردن labelها و به‌روزرسانی آنها
                for child in card.findChildren(QLabel):
                    obj_name = child.objectName()
                    
                    if obj_name == f"{title}_items":
                        child.setText(f"{stats['items']:,} قلم")
                    elif obj_name == f"{title}_low":
                        child.setText(f"{stats['low']:,}")
                    elif obj_name == f"{title}_value":
                        child.setText(self.format_currency(stats['value']))
    
    def refresh_all_tabs(self):
        """تازه‌سازی تمام تب‌ها"""
        print("🔄 تازه‌سازی تمام تب‌های انبار...")
        
        # لیست فرم‌ها از دیکشنری
        for form_attr, form in self.tab_forms.items():
            if form is not None and hasattr(form, 'load_data'):
                try:
                    tab_name = "نامشخص"
                    for i in range(self.tab_widget.count()):
                        if self.tab_widget.widget(i) == form:
                            tab_name = self.tab_widget.tabText(i)
                            break
                    
                    print(f"  تازه‌سازی {tab_name}...")
                    form.load_data()
                except Exception as e:
                    print(f"  ⚠️ خطا در تازه‌سازی فرم {form_attr}: {e}")
        
        # تازه‌سازی خلاصه
        self.refresh_summary()
        
        # نمایش پیام موفقیت
        self.show_message("تازه‌سازی", "تمامی تب‌های انبار با موفقیت تازه‌سازی شدند.")