# ui/forms/repair_form/repair_form.py
from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *
import jdatetime
from database.models import DataManager

# ایمپورت تب‌های جداگانه
try:
    from .repair_info_tab import RepairInfoTab
    from .repair_services_tab import RepairServicesTab
    from .repair_parts_tab import RepairPartsTab
except ImportError:
    import sys
    import os
    current_dir = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, current_dir)
    from repair_info_tab import RepairInfoTab
    from repair_services_tab import RepairServicesTab
    from repair_parts_tab import RepairPartsTab


class RepairForm(QWidget):
    def __init__(self, data_manager: DataManager, repair_id=None, parent=None):
        super().__init__(parent)
        self.data_manager = data_manager
        self.repair_id = repair_id
        self.reception_id = None
        self.current_reception = None
        
        # داده‌های موقت
        self.services_list = []  # لیست خدمات اضافه شده
        self.parts_list = []     # لیست قطعات اضافه شده
        
        # تب‌ها
        self.info_tab = None
        self.services_tab = None
        self.parts_tab = None
        
        self.setup_ui()
        if repair_id:
            self.load_repair_data()
    
    def setup_ui(self):
        self.setWindowTitle("🛠️ فرم مدیریت تعمیرات")
        self.setMinimumSize(1400, 800)  # ارتفاع بیشتر
        self.setMaximumSize(1800, 1200)  # حداکثر اندازه بزرگتر
        self.setWindowIcon(QIcon("assets/icons/repair.png"))
        
        # تم تاریک
        self.setStyleSheet("""
            QWidget {
                background-color: #000000;
                color: #FFFFFF;
                font-family: 'B Nazanin';
                font-size: 11pt;
                font-weight: 500;
            }
            QLabel {
                color: #FFFFFF;
                font-size: 11pt;
            }
            QGroupBox {
                background-color: #1a1a1a;
                border: 2px solid #333333;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 15px;
                font-weight: bold;
                font-size: 12pt;
                color: #FFFFFF;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 10px 0 10px;
                color: #4dabf7;
            }
            QTabWidget::pane {
                border: 2px solid #333333;
                background-color: #1a1a1a;
                border-radius: 5px;
            }
            QTabBar::tab {
                background-color: #2d2d2d;
                color: #cccccc;
                padding: 12px 25px;
                margin-right: 3px;
                border-top-left-radius: 5px;
                border-top-right-radius: 5px;
                font-size: 11pt;
                min-width: 150px;
            }
            QTabBar::tab:selected {
                background-color: #0056b3;
                color: #ffffff;
                font-weight: bold;
                border-bottom: 3px solid #4dabf7;
            }
            QTabBar::tab:hover {
                background-color: #3d3d3d;
            }
            QPushButton {
                background-color: #0056b3;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 20px;
                font-weight: bold;
                font-size: 11pt;
                min-width: 120px;
                margin: 5px;
            }
            QPushButton:hover {
                background-color: #0069d9;
                border: 1px solid #4dabf7;
            }
            QPushButton:pressed {
                background-color: #004085;
            }
            QPushButton#btn_save {
                background-color: #28a745;
                font-size: 12pt;
                padding: 12px 25px;
            }
            QPushButton#btn_save:hover {
                background-color: #218838;
            }
            QPushButton#btn_cancel {
                background-color: #dc3545;
            }
            QPushButton#btn_cancel:hover {
                background-color: #c82333;
            }
            QLineEdit, QTextEdit, QComboBox, QSpinBox, QDoubleSpinBox {
                background-color: #2d2d2d;
                color: #ffffff;
                border: 1px solid #555555;
                border-radius: 4px;
                padding: 8px;
                font-size: 11pt;
                selection-background-color: #0056b3;
            }
            QLineEdit:focus, QTextEdit:focus, QComboBox:focus, QSpinBox:focus, QDoubleSpinBox:focus {
                border: 2px solid #4dabf7;
                background-color: #3d3d3d;
            }
            QListWidget {
                background-color: #2d2d2d;
                color: #ffffff;
                border: 1px solid #555555;
                border-radius: 4px;
                alternate-background-color: #3d3d3d;
            }
            QListWidget::item {
                padding: 8px;
                border-bottom: 1px solid #444444;
            }
            QListWidget::item:selected {
                background-color: #0056b3;
                color: white;
            }
            QTableWidget {
                background-color: #1a1a1a;
                color: #ffffff;
                border: 1px solid #333333;
                border-radius: 4px;
                gridline-color: #444444;
                selection-background-color: #0056b3;
                selection-color: white;
            }
            QTableWidget::item {
                padding: 8px;
            }
            QTableWidget::item:selected {
                background-color: #0056b3;
            }
            QHeaderView::section {
                background-color: #2d2d2d;
                color: #ffffff;
                padding: 10px;
                border: 1px solid #333333;
                font-weight: bold;
                font-size: 11pt;
            }
            QScrollBar:vertical {
                background-color: #2d2d2d;
                width: 15px;
                border-radius: 7px;
            }
            QScrollBar::handle:vertical {
                background-color: #555555;
                border-radius: 7px;
                min-height: 30px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #666666;
            }
            QScrollBar:horizontal {
                background-color: #2d2d2d;
                height: 15px;
                border-radius: 7px;
            }
            QScrollBar::handle:horizontal {
                background-color: #555555;
                border-radius: 7px;
                min-width: 30px;
            }
            QScrollBar::handle:horizontal:hover {
                background-color: #666666;
            }
            QScrollArea {
                background-color: transparent;
                border: none;
            }
        """)
        
        # ایجاد اسکرول کلی برای کل فرم
        self.main_scroll = QScrollArea()
        self.main_scroll.setWidgetResizable(True)
        self.main_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.main_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.main_scroll.setFrameShape(QFrame.NoFrame)
        
        # ویجت محتوا برای اسکرول اصلی
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setSpacing(20)
        self.content_layout.setContentsMargins(20, 20, 20, 20)
        
        # ایجاد تب‌ها
        self.create_tabs()
        
        # پنل وضعیت
        self.create_status_panel()
        
        # پنل جمع‌بندی هزینه‌ها
        self.create_summary_panel()
        
        # دکمه‌های عملیات
        self.create_action_buttons()
        
        # تنظیم ترتیب نمایش
        self.content_layout.addWidget(self.status_panel)
        self.content_layout.addWidget(self.tab_widget)
        self.content_layout.addWidget(self.summary_panel)
        self.content_layout.addStretch(1)  # فضای خالی برای فشرده نشدن
        
        # تنظیم ویجت محتوا در اسکرول اصلی
        self.main_scroll.setWidget(self.content_widget)
        
        # لایه اصلی
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        main_layout.addWidget(self.main_scroll)
        main_layout.addLayout(self.btn_layout)  # دکمه‌ها پایین فرم
        
        self.setLayout(main_layout)
    
    def create_tabs(self):
        """ایجاد تب‌های فرم"""
        self.tab_widget = QTabWidget()
        self.tab_widget.setDocumentMode(True)
        
        # ایجاد تب‌های جداگانه
        self.info_tab = RepairInfoTab(self.data_manager, self)
        self.services_tab = RepairServicesTab(self.data_manager, self)
        self.parts_tab = RepairPartsTab(self.data_manager, self)
        
        # اتصال سیگنال‌ها
        self.info_tab.reception_selected.connect(self.on_reception_selected_from_tab)
        self.info_tab.reception_changed.connect(self.on_reception_changed)
        self.services_tab.services_changed.connect(self.calculate_totals)
        self.parts_tab.parts_changed.connect(self.calculate_totals)
        self.info_tab.outsource_cost_changed.connect(self.calculate_totals)
        
        self.tab_widget.addTab(self.info_tab, "📋 اطلاعات اصلی")
        self.tab_widget.addTab(self.services_tab, "🔧 خدمات و اجرت‌ها")
        self.tab_widget.addTab(self.parts_tab, "⚙️ قطعات مصرفی")
        
        # تنظیم حداقل ارتفاع برای تب‌ها
        self.tab_widget.setMinimumHeight(500)
    
    def create_status_panel(self):
        """ایجاد پنل وضعیت"""
        self.status_panel = QWidget()
        status_layout = QHBoxLayout(self.status_panel)
        self.lbl_status = QLabel("📝 در حال ثبت تعمیر جدید")
        self.lbl_status.setStyleSheet("""
            QLabel {
                font-size: 13pt;
                font-weight: bold;
                color: #4dabf7;
                padding: 15px;
                background-color: #1a1a1a;
                border-radius: 8px;
                border: 2px solid #333333;
                min-height: 30px;
            }
        """)
        self.lbl_status.setAlignment(Qt.AlignRight)
        status_layout.addWidget(self.lbl_status)
    
    def create_summary_panel(self):
        """ایجاد پنل جمع‌بندی هزینه‌ها"""
        self.summary_panel = QGroupBox("💰 جمع‌بندی هزینه‌ها (تومان)")
        self.summary_panel.setStyleSheet("""
            QGroupBox {
                background-color: #0d1117;
                border: 3px solid #2d81e0;
                font-size: 12pt;
                min-height: 200px;
            }
            QGroupBox::title {
                color: #2d81e0;
                font-weight: bold;
                font-size: 13pt;
            }
        """)
        
        layout = QGridLayout(self.summary_panel)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 25, 20, 20)
        
        # استایل برای برچسب‌ها
        label_style = "font-size: 11pt; font-weight: bold; padding: 5px;"
        value_style = "font-size: 12pt; font-weight: bold; padding: 10px; border-radius: 5px;"
        
        # هزینه اجرت‌ها
        lbl_services = QLabel("جمع هزینه اجرت‌ها:")
        lbl_services.setStyleSheet(label_style)
        layout.addWidget(lbl_services, 0, 0)
        
        self.lbl_services_total = QLabel("۰ تومان")
        self.lbl_services_total.setStyleSheet(f"{value_style} color: #27AE60; background-color: #1a1f2c;")
        self.lbl_services_total.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.lbl_services_total, 0, 1)
        
        # هزینه قطعات
        lbl_parts = QLabel("جمع هزینه قطعات:")
        lbl_parts.setStyleSheet(label_style)
        layout.addWidget(lbl_parts, 1, 0)
        
        self.lbl_parts_total = QLabel("۰ تومان")
        self.lbl_parts_total.setStyleSheet(f"{value_style} color: #E74C3C; background-color: #1a1f2c;")
        self.lbl_parts_total.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.lbl_parts_total, 1, 1)
        
        # هزینه بیرون‌سپاری
        lbl_outsource = QLabel("هزینه بیرون‌سپاری:")
        lbl_outsource.setStyleSheet(label_style)
        layout.addWidget(lbl_outsource, 2, 0)
        
        self.lbl_outsource_total = QLabel("۰ تومان")
        self.lbl_outsource_total.setStyleSheet(f"{value_style} color: #F39C12; background-color: #1a1f2c;")
        self.lbl_outsource_total.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.lbl_outsource_total, 2, 1)
        
        # خط جداکننده
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        line.setStyleSheet("background-color: #2d81e0; height: 2px;")
        layout.addWidget(line, 3, 0, 1, 2)
        
        # جمع کل
        lbl_grand = QLabel("💎 جمع کل تعمیر:")
        lbl_grand.setStyleSheet("font-size: 14pt; font-weight: bold; color: #9B59B6; padding: 10px;")
        layout.addWidget(lbl_grand, 4, 0)
        
        self.lbl_grand_total = QLabel("۰ تومان")
        self.lbl_grand_total.setStyleSheet("""
            font-size: 16pt; 
            font-weight: bold; 
            color: #9B59B6;
            background-color: #2d1f3c;
            padding: 15px;
            border-radius: 8px;
            border: 2px solid #9B59B6;
        """)
        self.lbl_grand_total.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.lbl_grand_total, 4, 1)
    
    def create_action_buttons(self):
        """ایجاد دکمه‌های عملیات"""
        self.btn_layout = QHBoxLayout()
        self.btn_layout.setSpacing(20)
        self.btn_layout.setContentsMargins(20, 10, 20, 20)
        
        self.btn_save = QPushButton("💾 ذخیره تعمیر")
        self.btn_save.setObjectName("btn_save")
        self.btn_save.setIcon(QIcon.fromTheme("document-save"))
        self.btn_save.clicked.connect(self.save_repair)
        self.btn_save.setMinimumHeight(50)
        
        self.btn_print = QPushButton("🖨️ چاپ برگه تعمیر")
        self.btn_print.setIcon(QIcon.fromTheme("document-print"))
        self.btn_print.clicked.connect(self.print_repair)
        self.btn_print.setMinimumHeight(50)
        
        self.btn_cancel = QPushButton("❌ انصراف")
        self.btn_cancel.setObjectName("btn_cancel")
        self.btn_cancel.setIcon(QIcon.fromTheme("dialog-cancel"))
        self.btn_cancel.clicked.connect(self.close)
        self.btn_cancel.setMinimumHeight(50)
        
        self.btn_layout.addStretch()
        self.btn_layout.addWidget(self.btn_save)
        self.btn_layout.addWidget(self.btn_print)
        self.btn_layout.addWidget(self.btn_cancel)
        self.btn_layout.addStretch()
    
    def on_reception_changed(self, reception_id):
        """وقتی پذیرش تغییر کرد"""
        self.reception_id = reception_id
        if reception_id:
            reception = self.data_manager.reception.get_reception_by_id(reception_id)
            if reception:
                customer_name = reception.get('customer_name', 'نامشخص')
                device_info = f"{reception.get('device_type', '')} {reception.get('brand', '')}"
                self.lbl_status.setText(f"📝 تعمیر برای پذیرش #{reception_id} - مشتری: {customer_name} - دستگاه: {device_info}")
    
    def calculate_totals(self):
        """محاسبه جمع کل هزینه‌ها به تومان"""
        try:
            services_total = self.services_tab.get_total() / 10  # تبدیل به تومان
            parts_total = self.parts_tab.get_total() / 10        # تبدیل به تومان
            outsource_total = self.info_tab.get_outsource_cost() / 10  # تبدیل به تومان
            
            # به روزرسانی نمایش
            self.lbl_services_total.setText(f"{services_total:,.0f} تومان")
            self.lbl_parts_total.setText(f"{parts_total:,.0f} تومان")
            self.lbl_outsource_total.setText(f"{outsource_total:,.0f} تومان")
            
            grand_total = services_total + parts_total + outsource_total
            self.lbl_grand_total.setText(f"{grand_total:,.0f} تومان")
            
            return grand_total * 10  # بازگشت به ریال برای ذخیره در دیتابیس
        except Exception as e:
            print(f"خطا در محاسبه جمع: {e}")
            return 0
    
    # ... بقیه متدها (save_repair, load_repair_data, etc.) ...   
    def save_repair(self):
        """ذخیره اطلاعات تعمیر در دیتابیس"""
        try:
            # اعتبارسنجی اولیه
            if not self.reception_id:
                QMessageBox.warning(self, "خطا", "لطفاً ابتدا یک پذیرش انتخاب کنید.")
                return
            
            # جمع آوری داده‌ها از تب‌ها
            repair_data = self.info_tab.get_data()
            
            # محاسبه هزینه کل
            total_cost = self.calculate_totals()  # این در ریال است
            repair_data['total_cost'] = total_cost
            
            print(f"💾 ذخیره تعمیر - reception_id: {self.reception_id}, repair_id: {self.repair_id}")
            
            # اگر repair_id داریم، آپدیت کنیم، اگر نه جدید بسازیم
            if self.repair_id:
                # حالت ویرایش تعمیر موجود
                success = self.data_manager.repair.update_repair(self.repair_id, repair_data)
                action = "ویرایش"
                message = f"تعمیر #{self.repair_id} با موفقیت به‌روزرسانی شد"
            else:
                # حالت ایجاد تعمیر جدید
                repair_id = self.data_manager.repair.add_repair(repair_data)
                if repair_id:
                    self.repair_id = repair_id
                    success = True
                    action = "ثبت"
                    message = f"تعمیر جدید با کد #{repair_id} ثبت شد"
                else:
                    success = False
            
            if success:
                # ذخیره خدمات
                if self.repair_id:
                    self.save_repair_services()
                
                # ذخیره قطعات
                self.save_repair_parts()
                
                # بروزرسانی وضعیت پذیرش به "در حال تعمیر"
                self.data_manager.reception.update_status(self.reception_id, "در حال تعمیر")
                
                QMessageBox.information(self, "موفقیت", 
                    f"{message}\n\n💰 هزینه کل: {total_cost/10:,.0f} تومان")
                
                # بستن فرم پس از ذخیره موفق
                self.close()
            else:
                QMessageBox.critical(self, "خطا", "خطا در ذخیره‌سازی تعمیر.")
                
        except Exception as e:
            QMessageBox.critical(self, "خطا", f"خطا در ذخیره‌سازی:\n{str(e)}")
            import traceback
            traceback.print_exc()
    
    def save_repair_services(self):
        """ذخیره خدمات تعمیر"""
        try:
            services = self.services_tab.get_services_data()
            # حذف خدمات قبلی
            self.data_manager.repair.delete_repair_services(self.repair_id)
            
            # اضافه کردن خدمات جدید
            for service in services:
                self.data_manager.repair.add_repair_service(
                    repair_id=self.repair_id,
                    service_id=service['service_id'],
                    quantity=service['quantity'],
                    unit_price=service['unit_price'],
                    description=service.get('description', '')
                )
            print(f"✅ خدمات تعمیر ذخیره شد: {len(services)} مورد")
        except Exception as e:
            print(f"❌ خطا در ذخیره خدمات: {e}")
    
    def save_repair_parts(self):
        """ذخیره قطعات مصرفی و کاهش موجودی انبار"""
        try:
            parts = self.parts_tab.get_parts_data()
            
            if not parts:
                print("⚠️ هیچ قطعه‌ای برای ذخیره وجود ندارد")
                return
            
            # حذف قطعات قبلی
            self.data_manager.repair.delete_repair_parts(self.repair_id)
            
            # اضافه کردن قطعات جدید
            saved_count = 0
            for part in parts:
                success = self.data_manager.repair.add_repair_part(
                    repair_id=self.repair_id,
                    part_id=part['part_id'],
                    quantity=part['quantity'],
                    unit_price=part['unit_price'],
                    warehouse_type=part['warehouse_type'],
                    description=f"{part['part_name']} - {part.get('brand', '')}"
                )
                if success:
                    saved_count += 1
                    
                    # کاهش موجودی انبار
                    self.update_inventory(
                        part['part_id'], 
                        part['warehouse_type'], 
                        -part['quantity']
                    )
            
            print(f"✅ {saved_count} قطعه با موفقیت ذخیره شد")
            
        except Exception as e:
            print(f"❌ خطا در ذخیره قطعات: {e}")
            import traceback
            traceback.print_exc()

    def update_inventory(self, part_id, warehouse_type, quantity_change):
        """بروزرسانی موجودی انبار"""
        try:
            if warehouse_type == "قطعات نو":
                table_name = "NewPartsWarehouse"
            else:
                table_name = "UsedPartsWarehouse"
            
            query = f"""
            UPDATE {table_name} 
            SET quantity = quantity + ?, updated_at = CURRENT_TIMESTAMP
            WHERE part_id = ? AND status = 'موجود'
            """
            
            success = self.data_manager.db.execute_query(query, (quantity_change, part_id))
            if success:
                print(f"✅ موجودی انبار {warehouse_type} برای قطعه {part_id} به‌روز شد")
            else:
                print(f"⚠️ خطا در به‌روزرسانی موجودی انبار")
                
        except Exception as e:
            print(f"❌ خطا در به‌روزرسانی انبار: {e}")
    
    def load_repair_data(self):
        """بارگذاری داده‌های یک تعمیر موجود"""
        try:
            repair = self.data_manager.db.fetch_one(
                "SELECT * FROM Repairs WHERE id = ?", 
                (self.repair_id,)
            )
            
            if repair:
                # بارگذاری اطلاعات اصلی
                self.info_tab.set_data(repair)
                
                # بارگذاری خدمات
                services = self.data_manager.repair.get_repair_services(self.repair_id)
                if services:
                    self.services_tab.set_services(services)
                
                # بارگذاری قطعات
                parts = self.data_manager.repair.get_repair_parts(self.repair_id)
                if parts:
                    self.parts_tab.set_parts(parts)
                
                # بروزرسانی وضعیت
                self.reception_id = repair['reception_id']
                self.lbl_status.setText(f"✏️ در حال ویرایش تعمیر #{self.repair_id}")
                
                # محاسبه مجدد جمع‌ها
                self.calculate_totals()
                
        except Exception as e:
            QMessageBox.warning(self, "خطا", f"خطا در بارگذاری اطلاعات تعمیر:\n{str(e)}")
            import traceback
            traceback.print_exc()
    
    def load_existing_repair(self):
        """بارگذاری تعمیرات موجود برای پذیرش انتخاب شده"""
        if not self.reception_id:
            return
        
        try:
            existing_repair = self.data_manager.repair.fetch_one(
                "SELECT * FROM Repairs WHERE reception_id = ? ORDER BY id DESC LIMIT 1", 
                (self.reception_id,)
            )
            
            if existing_repair:
                self.repair_id = existing_repair['id']
                self.lbl_status.setText(f"✏️ در حال ویرایش تعمیر #{self.repair_id}")
                
                # بارگذاری اطلاعات تعمیر در فرم
                self.load_repair_data()
                
                print(f"✅ تعمیر موجود بارگذاری شد: ID={self.repair_id}")
            else:
                self.repair_id = None
                self.lbl_status.setText("📝 در حال ثبت تعمیر جدید")
                
        except Exception as e:
            print(f"❌ خطا در بارگذاری تعمیر موجود: {e}")

    def on_reception_selected_from_tab(self, reception_id):
        """وقتی از تب اطلاعات یک پذیرش انتخاب شد"""
        print(f"📥 پذیرش انتخاب شد: {reception_id}")
        self.reception_id = reception_id
        self.load_existing_repair()

    def print_repair(self):
        """چاپ برگه تعمیر"""
        if not self.repair_id:
            QMessageBox.warning(self, "هشدار", "ابتدا تعمیر را ذخیره کنید.")
            return
        
        QMessageBox.information(self, "چاپ", "امکان چاپ به زودی اضافه خواهد شد.")