# smart_search_dialog.py - نسخه اصلاح شده
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QTableWidget, QTableWidgetItem, QRadioButton,
    QWidget, QGridLayout, QGroupBox, QFrame, QMessageBox,
    QHeaderView, QComboBox, QScrollArea, QAbstractItemView 
)
from PySide6.QtCore import Qt, Signal, QRegularExpression, QTimer
from PySide6.QtGui import QRegularExpressionValidator, QColor
import jdatetime

class SmartSearchDialog(QDialog):
    """
    دیالوگ جستجوی هوشمند با قابلیت نمایش تاریخ پذیرش و شماره پذیرش
    """
    
    reception_selected = Signal(dict)  # اطلاعات پذیرش انتخاب شده
    
    def __init__(self, data_manager):
        super().__init__()
        self.data_manager = data_manager
        self.selected_reception = None
        
        # تایمر برای جستجوی زنده
        self.search_timer = QTimer()
        self.search_timer.setSingleShot(True)
        self.search_timer.timeout.connect(self.perform_search)
        
        self.init_ui()
    
    def init_ui(self):
        """راه‌اندازی رابط کاربری"""
        self.setWindowTitle("🔍 جستجوی پذیرش‌ها - سیستم تعمیرگاه شیروین")
        self.setMinimumSize(1200, 700)
        self.setStyleSheet(self.get_style_sheet())
        
        # لایه اصلی
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(10)
        
        # ===== بخش فیلترها =====
        filter_frame = QFrame()
        filter_frame.setStyleSheet("""
            QFrame {
                background-color: #2c3e50;
                border-radius: 8px;
                padding: 15px;
            }
        """)
        
        filter_layout = QGridLayout()
        
        # موبایل مشتری
        filter_layout.addWidget(QLabel("📱 موبایل مشتری:"), 0, 0)
        self.filter_mobile = QLineEdit()
        self.filter_mobile.setPlaceholderText("09xxxxxxxxx - جستجو در موبایل مشتریان")
        self.filter_mobile.setValidator(
            QRegularExpressionValidator(QRegularExpression(r'[0-9]*'))
        )
        self.filter_mobile.textChanged.connect(self.on_filter_changed)
        filter_layout.addWidget(self.filter_mobile, 0, 1, 1, 2)
        
        # نام مشتری
        filter_layout.addWidget(QLabel("👤 نام مشتری:"), 1, 0)
        self.filter_name = QLineEdit()
        self.filter_name.setPlaceholderText("نام یا نام خانوادگی مشتری")
        self.filter_name.textChanged.connect(self.on_filter_changed)
        filter_layout.addWidget(self.filter_name, 1, 1, 1, 2)
        
        # شماره پذیرش
        filter_layout.addWidget(QLabel("🔢 شماره پذیرش:"), 2, 0)
        self.filter_reception_no = QLineEdit()
        self.filter_reception_no.setPlaceholderText("شماره پذیرش")
        self.filter_reception_no.textChanged.connect(self.on_filter_changed)
        filter_layout.addWidget(self.filter_reception_no, 2, 1)
        
        # وضعیت
        filter_layout.addWidget(QLabel("📊 وضعیت:"), 2, 2)
        self.filter_status = QComboBox()
        self.filter_status.addItems(["همه", "در انتظار", "در حال تعمیر", "تعمیر شده", "تحویل داده شده"])
        self.filter_status.currentIndexChanged.connect(self.on_filter_changed)
        filter_layout.addWidget(self.filter_status, 2, 3)
        
        # دکمه‌های فیلتر
        btn_clear = QPushButton("🗑️ پاک کردن فیلترها")
        btn_clear.setStyleSheet(self.get_button_style("#e74c3c"))
        btn_clear.clicked.connect(self.clear_filters)
        filter_layout.addWidget(btn_clear, 3, 0, 1, 2)
        
        btn_search = QPushButton("🔍 جستجوی دستی")
        btn_search.setStyleSheet(self.get_button_style("#3498db"))
        btn_search.clicked.connect(self.perform_search)
        filter_layout.addWidget(btn_search, 3, 2, 1, 2)
        
        filter_frame.setLayout(filter_layout)
        main_layout.addWidget(filter_frame)
        
        # ===== بخش نتایج =====
        result_frame = QFrame()
        result_layout = QVBoxLayout()
        
        # وضعیت جستجو
        self.status_label = QLabel("آماده برای جستجو...")
        self.status_label.setStyleSheet("""
            QLabel {
                color: #f39c12;
                font-weight: bold;
                padding: 5px;
                background-color: #34495e;
                border-radius: 4px;
            }
        """)
        result_layout.addWidget(self.status_label)
        
        # جدول نتایج
        self.results_table = QTableWidget()
        self.results_table.setColumnCount(9)
        self.results_table.setHorizontalHeaderLabels([
            "انتخاب", "شماره پذیرش", "مشتری", "موبایل", "دستگاه", 
            "نوع", "تاریخ پذیرش", "هزینه تخمینی", "وضعیت"
        ])
        self.results_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.results_table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.results_table.cellClicked.connect(self.on_row_clicked)
        
        # تنظیمات جدول
        header = self.results_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Fixed)    # انتخاب
        header.setSectionResizeMode(1, QHeaderView.Fixed)    # شماره پذیرش
        header.setSectionResizeMode(2, QHeaderView.Stretch)  # مشتری
        header.setSectionResizeMode(3, QHeaderView.Fixed)    # موبایل
        header.setSectionResizeMode(4, QHeaderView.Stretch)  # دستگاه
        header.setSectionResizeMode(5, QHeaderView.Fixed)    # نوع
        header.setSectionResizeMode(6, QHeaderView.Fixed)    # تاریخ
        header.setSectionResizeMode(7, QHeaderView.Fixed)    # هزینه
        header.setSectionResizeMode(8, QHeaderView.Fixed)    # وضعیت
        
        self.results_table.setColumnWidth(0, 60)
        self.results_table.setColumnWidth(1, 120)
        self.results_table.setColumnWidth(3, 110)
        self.results_table.setColumnWidth(5, 100)
        self.results_table.setColumnWidth(6, 100)
        self.results_table.setColumnWidth(7, 110)
        self.results_table.setColumnWidth(8, 110)
        
        # ارتفاع سطرها
        self.results_table.verticalHeader().setDefaultSectionSize(40)
        
        result_layout.addWidget(self.results_table)
        result_frame.setLayout(result_layout)
        main_layout.addWidget(result_frame, stretch=1)
        
        # ===== بخش اطلاعات انتخاب شده =====
        selected_frame = QFrame()
        selected_frame.setStyleSheet("""
            QFrame {
                background-color: #27ae60;
                border-radius: 8px;
                padding: 10px;
            }
        """)
        
        selected_layout = QGridLayout()
        
        self.selected_info = QLabel("⚠️ هیچ پذیرشی انتخاب نشده است")
        self.selected_info.setStyleSheet("""
            QLabel {
                color: white;
                font-weight: bold;
                font-size: 13px;
            }
        """)
        self.selected_info.setWordWrap(True)
        selected_layout.addWidget(self.selected_info, 0, 0, 1, 3)
        
        selected_frame.setLayout(selected_layout)
        main_layout.addWidget(selected_frame)
        
        # ===== دکمه‌های پایین =====
        button_layout = QHBoxLayout()
        
        self.btn_select = QPushButton("✅ انتخاب پذیرش")
        self.btn_select.setEnabled(False)
        self.btn_select.clicked.connect(self.accept_selection)
        self.btn_select.setStyleSheet(self.get_button_style("#27ae60"))
        self.btn_select.setMinimumHeight(45)
        
        self.btn_new = QPushButton("🆕 پذیرش جدید")
        self.btn_new.clicked.connect(self.new_reception)
        self.btn_new.setStyleSheet(self.get_button_style("#3498db"))
        self.btn_new.setMinimumHeight(45)
        
        self.btn_cancel = QPushButton("❌ انصراف")
        self.btn_cancel.clicked.connect(self.reject)
        self.btn_cancel.setStyleSheet(self.get_button_style("#e74c3c"))
        self.btn_cancel.setMinimumHeight(45)
        
        button_layout.addWidget(self.btn_select)
        button_layout.addWidget(self.btn_new)
        button_layout.addStretch()
        button_layout.addWidget(self.btn_cancel)
        
        main_layout.addLayout(button_layout)
        self.setLayout(main_layout)
    
    def on_filter_changed(self):
        """هنگام تغییر فیلترها"""
        self.search_timer.stop()
        self.search_timer.start(500)  # 500ms delay
    
    def perform_search(self):
        """انجام جستجو بر اساس فیلترها"""
        try:
            # دریافت فیلترها
            mobile = self.filter_mobile.text().strip()
            name = self.filter_name.text().strip()
            reception_no = self.filter_reception_no.text().strip()
            status_filter = self.filter_status.currentText()
            
            # دریافت همه پذیرش‌ها از دیتابیس
            all_receptions = self.data_manager.reception.get_all_receptions()
            
            # فیلتر کردن نتایج
            filtered_receptions = []
            for reception in all_receptions:
                # فیلتر موبایل
                if mobile:
                    # پیدا کردن مشتری و بررسی موبایل
                    customer_id = reception.get('customer_id')
                    if customer_id:
                        customer = self.data_manager.person.get_person_by_id(customer_id)
                        if customer and mobile not in str(customer.get('mobile', '')):
                            continue
                    else:
                        continue
                
                # فیلتر نام
                if name:
                    customer_name = reception.get('customer_name', '').lower()
                    if name.lower() not in customer_name:
                        continue
                
                # فیلتر شماره پذیرش
                if reception_no:
                    reception_number = str(reception.get('reception_number', '')).lower()
                    if reception_no.lower() not in reception_number:
                        continue
                
                # فیلتر وضعیت
                if status_filter != "همه":
                    status = reception.get('status', '')
                    if status != status_filter:
                        continue
                
                filtered_receptions.append(reception)
            
            # نمایش نتایج
            self.display_results(filtered_receptions)
            
            # به‌روزرسانی وضعیت
            count = len(filtered_receptions)
            self.status_label.setText(f"✅ {count} پذیرش یافت شد" if count > 0 else "❌ نتیجه‌ای یافت نشد")
            
        except Exception as e:
            self.status_label.setText(f"❌ خطا در جستجو: {str(e)}")
            print(f"خطا در جستجو: {e}")
    
    def display_results(self, receptions):
        """نمایش پذیرش‌ها در جدول"""
        self.results_table.setRowCount(len(receptions))
        
        for row, reception in enumerate(receptions):
            # ستون انتخاب (رادیو باتن)
            radio = QRadioButton()
            radio.setProperty('reception_id', reception.get('id'))
            radio.toggled.connect(
                lambda checked, r=reception: self.on_reception_selected(r) if checked else None
            )
            
            cell_widget = QWidget()
            layout = QHBoxLayout(cell_widget)
            layout.addWidget(radio)
            layout.setAlignment(Qt.AlignCenter)
            layout.setContentsMargins(0, 0, 0, 0)
            self.results_table.setCellWidget(row, 0, cell_widget)
            
            # شماره پذیرش
            self.results_table.setItem(row, 1, 
                QTableWidgetItem(str(reception.get('reception_number', ''))))
            
            # مشتری
            self.results_table.setItem(row, 2, 
                QTableWidgetItem(reception.get('customer_name', '')))
            
            # موبایل مشتری
            mobile = self.get_customer_mobile(reception.get('customer_id'))
            self.results_table.setItem(row, 3, QTableWidgetItem(mobile))
            
            # دستگاه
            device_text = f"{reception.get('brand', '')} {reception.get('model', '')}"
            self.results_table.setItem(row, 4, QTableWidgetItem(device_text))
            
            # نوع دستگاه
            self.results_table.setItem(row, 5, 
                QTableWidgetItem(reception.get('device_type', '')))
            
            # تاریخ پذیرش (تبدیل به شمسی)
            reception_date = reception.get('reception_date', '')
            jalali_date = self.convert_to_jalali(reception_date)
            self.results_table.setItem(row, 6, QTableWidgetItem(jalali_date))
            
            # هزینه تخمینی
            cost = reception.get('estimated_cost', 0)
            cost_text = f"{cost:,} تومان" if cost else "تعیین نشده"
            self.results_table.setItem(row, 7, QTableWidgetItem(cost_text))
            
            # وضعیت با رنگ‌بندی
            status_item = QTableWidgetItem(reception.get('status', ''))
            status = reception.get('status', '')
            
            # رنگ‌بندی وضعیت
            if status == 'تعمیر شده':
                status_item.setForeground(QColor('#27ae60'))
            elif status == 'در حال تعمیر':
                status_item.setForeground(QColor('#3498db'))
            elif status == 'در انتظار':
                status_item.setForeground(QColor('#f39c12'))
            elif status == 'تحویل داده شده':
                status_item.setForeground(QColor('#9b59b6'))
            
            self.results_table.setItem(row, 8, status_item)
    
    def get_customer_mobile(self, customer_id):
        """دریافت موبایل مشتری"""
        if not customer_id:
            return ""
        
        try:
            customer = self.data_manager.person.get_person_by_id(customer_id)
            return customer.get('mobile', '') if customer else ""
        except:
            return ""
    
    def convert_to_jalali(self, date_str):
        """تبدیل تاریخ میلادی به شمسی"""
        if not date_str:
            return ""
        
        try:
            # جدا کردن قسمت تاریخ از رشته
            if ' ' in str(date_str):
                date_str = str(date_str).split(' ')[0]
            
            # جدا کردن سال، ماه، روز
            parts = str(date_str).replace('-', '/').split('/')
            if len(parts) >= 3:
                year, month, day = map(int, parts[:3])
                
                # تبدیل میلادی به شمسی
                jalali_date = jdatetime.date.fromgregorian(year=year, month=month, day=day)
                return jalali_date.strftime('%Y/%m/%d')
        except:
            pass
        
        return str(date_str)
    
    def on_reception_selected(self, reception):
        """هنگام انتخاب یک پذیرش"""
        self.selected_reception = reception
        
        # نمایش اطلاعات انتخاب شده
        customer_name = reception.get('customer_name', '')
        device_text = f"{reception.get('device_type', '')} - {reception.get('brand', '')} {reception.get('model', '')}"
        reception_date = self.convert_to_jalali(reception.get('reception_date', ''))
        
        info_text = f"""
        ✅ پذیرش انتخاب شده:
        📋 شماره: {reception.get('reception_number', '')}
        👤 مشتری: {customer_name}
        📱 دستگاه: {device_text}
        📅 تاریخ: {reception_date}
        📊 وضعیت: {reception.get('status', '')}
        """
        
        self.selected_info.setText(info_text)
        self.btn_select.setEnabled(True)
    
    def on_row_clicked(self, row, column):
        """هنگام کلیک روی سطر جدول"""
        if column != 0:  # اگر روی ستون رادیو کلیک نکرده
            radio_widget = self.results_table.cellWidget(row, 0)
            if radio_widget:
                radio = radio_widget.findChild(QRadioButton)
                if radio:
                    radio.setChecked(True)
    
    def accept_selection(self):
        """تأیید انتخاب"""
        if self.selected_reception:
            # جمع‌آوری اطلاعات کامل
            result = self.collect_complete_data()
            self.reception_selected.emit(result)
            self.accept()
    
    def collect_complete_data(self):
        """جمع‌آوری اطلاعات کامل برای فرم تعمیر"""
        if not self.selected_reception:
            return None
        
        try:
            # دریافت اطلاعات مشتری
            customer_id = self.selected_reception.get('customer_id')
            customer = None
            if customer_id:
                customer = self.data_manager.person.get_person_by_id(customer_id)
            
            # دریافت اطلاعات دستگاه
            device_id = self.selected_reception.get('device_id')
            device = None
            if device_id:
                device = self.data_manager.device.get_device_by_id(device_id)
            
            # ساخت دیکشنری اطلاعات
            data = {
                'reception_id': self.selected_reception.get('id'),
                'reception_number': self.selected_reception.get('reception_number', ''),
                'customer_id': customer_id,
                'customer_name': f"{customer.get('first_name', '')} {customer.get('last_name', '')}" if customer else '',
                'customer_mobile': customer.get('mobile', '') if customer else '',
                'customer_address': customer.get('address', '') if customer else '',
                'device_id': device_id,
                'device_type': device.get('device_type', '') if device else self.selected_reception.get('device_type', ''),
                'device_brand': device.get('brand', '') if device else self.selected_reception.get('brand', ''),
                'device_model': device.get('model', '') if device else self.selected_reception.get('model', ''),
                'device_serial': device.get('serial_number', '') if device else '',
                'reception_date': self.selected_reception.get('reception_date'),
                'problem_description': self.selected_reception.get('problem_description', ''),
                'estimated_cost': self.selected_reception.get('estimated_cost', 0),
                'status': self.selected_reception.get('status', ''),
            }
            
            print(f"📤 ارسال داده‌ها به فرم تعمیرات: reception_id={data['reception_id']}")
            return data
            
        except Exception as e:
            print(f"❌ خطا در جمع‌آوری اطلاعات: {e}")
            return None
        
    def clear_filters(self):
        """پاک کردن فیلترها"""
        self.filter_mobile.clear()
        self.filter_name.clear()
        self.filter_reception_no.clear()
        self.filter_status.setCurrentIndex(0)
        self.perform_search()
    
    def new_reception(self):
        """پذیرش جدید"""
        QMessageBox.information(self, "پذیرش جدید", 
            "برای ثبت پذیرش جدید، از منوی اصلی استفاده کنید.\nاین دیالوگ فقط برای جستجوی پذیرش‌های موجود است.")
    
    def get_button_style(self, color):
        """استایل دکمه"""
        return f"""
        QPushButton {{
            background-color: {color};
            color: white;
            padding: 8px 15px;
            border-radius: 5px;
            font-weight: bold;
            border: none;
            min-width: 120px;
        }}
        QPushButton:hover {{ background-color: {self.darken_color(color)}; }}
        QPushButton:disabled {{ background-color: #7f8c8d; color: #bdc3c7; }}
        """
    
    def darken_color(self, color, amount=30):
        """تیره کردن رنگ"""
        color = color.lstrip('#')
        r, g, b = tuple(int(color[i:i+2], 16) for i in (0, 2, 4))
        r, g, b = max(0, r-amount), max(0, g-amount), max(0, b-amount)
        return f'#{r:02x}{g:02x}{b:02x}'
    
    def get_style_sheet(self):
        """استایل کلی"""
        return """
        QDialog {
            background-color: #1e1e1e;
            font-family: 'B Nazanin', Tahoma;
            color: white;
        }
        QTableWidget {
            background-color: #2c2c2c;
            alternate-background-color: #3c3c3c;
            gridline-color: #444;
            font-size: 12px;
        }
        QTableWidget::item {
            padding: 6px 4px;
        }
        QHeaderView::section {
            background-color: #2c3e50;
            color: white;
            padding: 10px;
            border: none;
            font-weight: bold;
            font-size: 11px;
        }
        QLineEdit, QComboBox {
            background-color: #2c2c2c;
            color: white;
            border: 1px solid #444;
            border-radius: 4px;
            padding: 8px;
            min-height: 35px;
        }
        QLineEdit:focus, QComboBox:focus {
            border: 2px solid #3498db;
        }
        QRadioButton::indicator {
            width: 20px;
            height: 20px;
            border-radius: 10px;
            border: 2px solid #7f8c8d;
        }
        QRadioButton::indicator:checked {
            background-color: #27ae60;
            border: 2px solid #27ae60;
        }
        """