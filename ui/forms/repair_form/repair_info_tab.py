# ui/forms/repair_form/repair_info_tab.py
from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *
import jdatetime
from ui.widgets.jalali_date_input import JalaliDateInput

# ui/forms/repair_form/repair_info_tab.py
class RepairInfoTab(QWidget):
    reception_changed = Signal(int)
    outsource_cost_changed = Signal()
    reception_selected = Signal(int)

    def __init__(self, data_manager, parent=None):
        super().__init__(parent)
        self.data_manager = data_manager
        self.reception_id = None
        
        self.setup_ui()
        self.load_technicians()
        self.load_outsource_persons()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(15, 15, 15, 15)
        
        # --- بخش جستجوی پذیرش ---
        group_search = self.create_search_group()
        layout.addWidget(group_search)
        
        # --- بخش اطلاعات تعمیر و پذیرش ---
        info_widget = QWidget()
        info_layout = QHBoxLayout(info_widget)
        info_layout.setSpacing(15)
        
        # ستون سمت چپ: اطلاعات تعمیر
        group_info = self.create_info_group()
        info_layout.addWidget(group_info)
        
        # ستون سمت راست: اطلاعات پذیرش و توضیحات
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setSpacing(15)
        
        group_reception = self.create_reception_group()
        group_desc = self.create_description_group()
        
        right_layout.addWidget(group_reception)
        right_layout.addWidget(group_desc, 1)  # ضریب کشش 1 برای توضیحات
        
        info_layout.addWidget(right_widget, 1)  # ضریب کشش 1
        
        layout.addWidget(info_widget, 1)  # ضریب کشش 1
        
        self.setLayout(layout)
    
    def create_search_group(self):
        """ایجاد گروه جستجوی پذیرش"""
        group = QGroupBox("🔍 جستجوی پذیرش")
        group.setMinimumHeight(250)
        
        layout = QVBoxLayout()
        layout.setSpacing(10)
        
        # ردیف جستجو
        search_row = QHBoxLayout()
        lbl_mobile = QLabel("شماره موبایل مشتری:")
        lbl_mobile.setStyleSheet("font-weight: bold;")
        search_row.addWidget(lbl_mobile)
        
        self.txt_mobile = QLineEdit()
        self.txt_mobile.setPlaceholderText("09xxxxxxxxx")
        self.txt_mobile.setMinimumWidth(200)
        self.txt_mobile.textChanged.connect(self.search_by_mobile)
        search_row.addWidget(self.txt_mobile)
        
        self.btn_clear_search = QPushButton("🗑️ پاک کردن")
        self.btn_clear_search.setStyleSheet("""
            QPushButton {
                background-color: #6c757d;
                color: white;
                border-radius: 4px;
                padding: 8px 15px;
            }
            QPushButton:hover {
                background-color: #5a6268;
            }
        """)
        self.btn_clear_search.clicked.connect(self.clear_search)
        search_row.addWidget(self.btn_clear_search)
        layout.addLayout(search_row)
        
        # لیست پذیرش‌ها
        self.lbl_search_results = QLabel("پذیرش‌های یافت شده: ۰ مورد")
        self.lbl_search_results.setStyleSheet("color: #4dabf7; font-weight: bold;")
        layout.addWidget(self.lbl_search_results)
        
        self.list_receptions = QListWidget()
        self.list_receptions.setMinimumHeight(180)
        self.list_receptions.setMaximumHeight(250)
        self.list_receptions.itemClicked.connect(self.on_reception_selected)
        layout.addWidget(self.list_receptions)
        
        group.setLayout(layout)
        return group
    
    def create_info_group(self):
        """ایجاد گروه اطلاعات تعمیر"""
        group = QGroupBox("📋 اطلاعات تعمیر")
        group.setMinimumWidth(400)
        
        layout = QVBoxLayout()
        layout.setSpacing(10)
        
        # ردیف‌ها به صورت عمودی
        row_layout = QHBoxLayout()
        lbl_date = QLabel("تاریخ تعمیر:")
        lbl_date.setStyleSheet("font-weight: bold; min-width: 100px;")
        row_layout.addWidget(lbl_date)
        self.txt_repair_date = JalaliDateInput()
        self.txt_repair_date.set_date(jdatetime.datetime.now())
        row_layout.addWidget(self.txt_repair_date, 1)
        layout.addLayout(row_layout)

        
        # ردیف ۲: تعمیرکار
        lbl_technician = QLabel("تعمیرکار:")
        layout = QGridLayout()
        lbl_technician.setStyleSheet("font-weight: bold;")
        layout.addWidget(lbl_technician, 1, 0)
        
        self.cmb_technician = QComboBox()
        self.cmb_technician.setMinimumWidth(250)
        self.load_technicians()
        layout.addWidget(self.cmb_technician, 1, 1)
        
        # ردیف ۳: نوع تعمیر
        lbl_repair_type = QLabel("نوع تعمیر:")
        lbl_repair_type.setStyleSheet("font-weight: bold;")
        layout.addWidget(lbl_repair_type, 2, 0)
        
        self.cmb_repair_type = QComboBox()
        self.cmb_repair_type.addItems(["داخلی", "بیرون سپاری"])
        self.cmb_repair_type.setCurrentText("داخلی")
        self.cmb_repair_type.currentTextChanged.connect(self.on_repair_type_changed)
        layout.addWidget(self.cmb_repair_type, 2, 1)
        
        # ردیف ۴: بیرون سپاری به
        self.lbl_outsource_to = QLabel("بیرون سپاری به:")
        self.lbl_outsource_to.setStyleSheet("font-weight: bold;")
        self.cmb_outsource_to = QComboBox()
        self.cmb_outsource_to.setVisible(False)
        self.cmb_outsource_to.setMinimumWidth(250)
        layout.addWidget(self.lbl_outsource_to, 3, 0)
        layout.addWidget(self.cmb_outsource_to, 3, 1)
        
        # ردیف ۵: هزینه بیرون سپاری
        self.lbl_outsource_cost = QLabel("هزینه بیرون سپاری (تومان):")
        self.lbl_outsource_cost.setStyleSheet("font-weight: bold;")
        self.spn_outsource_cost = QDoubleSpinBox()
        self.spn_outsource_cost.setRange(0, 100000000)
        self.spn_outsource_cost.setValue(0)
        self.spn_outsource_cost.setVisible(False)
        self.spn_outsource_cost.setSuffix(" تومان")
        self.spn_outsource_cost.setMinimumWidth(250)
        self.spn_outsource_cost.valueChanged.connect(lambda: self.outsource_cost_changed.emit())
        layout.addWidget(self.lbl_outsource_cost, 4, 0)
        layout.addWidget(self.spn_outsource_cost, 4, 1)
        
        # بارگذاری لیست افراد برای بیرون سپاری
        self.load_outsource_persons()
        
        group.setLayout(layout)
        return group
    
    def create_reception_group(self):
        """ایجاد گروه اطلاعات پذیرش"""
        group = QGroupBox("📄 اطلاعات پذیرش انتخاب شده")
        group.setMinimumHeight(200)
        
        layout = QVBoxLayout()
        
        self.lbl_reception_info = QLabel("⏳ هیچ پذیرشی انتخاب نشده است.")
        self.lbl_reception_info.setWordWrap(True)
        self.lbl_reception_info.setStyleSheet("""
            QLabel {
                color: #95a5a6;
                font-style: italic;
                padding: 15px;
                background-color: #2d2d2d;
                border-radius: 5px;
                border: 1px solid #444444;
                font-size: 11pt;
                min-height: 150px;
            }
        """)
        layout.addWidget(self.lbl_reception_info)
        
        group.setLayout(layout)
        return group
    
    def create_description_group(self):
        """ایجاد گروه توضیحات"""
        group = QGroupBox("📝 توضیحات تعمیر")
        group.setMinimumHeight(200)
        
        layout = QVBoxLayout()
        
        self.txt_description = QTextEdit()
        self.txt_description.setPlaceholderText("شرح دقیق عملیات تعمیر، مشکلات شناسایی شده، تست‌های انجام شده و ...")
        self.txt_description.setMinimumHeight(150)
        layout.addWidget(self.txt_description)
        
        group.setLayout(layout)
        return group
    
    # ... بقیه متدها (search_by_mobile, clear_search, on_reception_selected, etc.) بدون تغییر ...
    
    def search_by_mobile(self, mobile):
        """جستجوی پذیرش بر اساس موبایل مشتری"""
        mobile = mobile.strip()
        if len(mobile) < 3:
            self.list_receptions.clear()
            self.lbl_search_results.setText("پذیرش‌های یافت شده: ۰ مورد")
            return
        
        try:
            # استفاده از مدل Receptions
            all_receptions = self.data_manager.reception.get_all_receptions()
            
            results = []
            for reception in all_receptions:
                # دریافت اطلاعات مشتری
                customer_id = reception.get('customer_id')
                if customer_id:
                    customer = self.data_manager.person.get_person_by_id(customer_id)
                    if customer and mobile in customer.get('mobile', ''):
                        # دریافت اطلاعات دستگاه
                        device_id = reception.get('device_id')
                        device = self.data_manager.device.get_device_by_id(device_id) if device_id else None
                        
                        results.append({
                            'id': reception['id'],
                            'reception_number': reception.get('reception_number', ''),
                            'reception_date': reception.get('reception_date', ''),
                            'status': reception.get('status', ''),
                            'customer_name': f"{customer.get('first_name', '')} {customer.get('last_name', '')}",
                            'mobile': customer.get('mobile', ''),
                            'device_type': device.get('device_type', '') if device else '',
                            'brand': device.get('brand', '') if device else '',
                            'model': device.get('model', '') if device else '',
                            'serial_number': device.get('serial_number', '') if device else '',
                            'problem_description': reception.get('problem_description', '')
                        })
            
            self.list_receptions.clear()
            for row in results:
                # تبدیل تاریخ شمسی
                reception_date = row['reception_date']
                if reception_date:
                    try:
                        year, month, day = map(int, str(reception_date).split('-'))
                        jalali_date = jdatetime.date.fromgregorian(year=year, month=month, day=day)
                        reception_date_str = jalali_date.strftime("%Y/%m/%د")
                    except:
                        reception_date_str = str(reception_date)
                else:
                    reception_date_str = "تاریخ نامشخص"
                
                item_text = (
                    f"📋 پذیرش #{row['reception_number']} - {reception_date_str}\n"
                    f"👤 مشتری: {row['customer_name']} - 📱 {row['mobile']}\n"
                    f"📱 دستگاه: {row['device_type']} {row['brand']} {row['model']}\n"
                    f"🔢 سریال: {row['serial_number'] or 'نامشخص'} - 🏷️ وضعیت: {row['status']}"
                )
                
                item = QListWidgetItem(item_text)
                item.setData(Qt.UserRole, row['id'])
                self.list_receptions.addItem(item)
            
            self.lbl_search_results.setText(f"پذیرش‌های یافت شده: {len(results)} مورد")
            
        except Exception as e:
            print(f"خطا در جستجوی پذیرش: {e}")
            self.lbl_search_results.setText(f"خطا در جستجو: {str(e)[:50]}")
    
    def clear_search(self):
        """پاک کردن جستجو"""
        self.txt_mobile.clear()
        self.list_receptions.clear()
        self.lbl_reception_info.setText("⏳ هیچ پذیرشی انتخاب نشده است.")
        self.lbl_search_results.setText("پذیرش‌های یافت شده: ۰ مورد")
        self.reception_id = None
        self.reception_selected.emit(0)
    
    def on_reception_selected(self, item):
        """وقتی یک پذیرش از لیست انتخاب شد"""
        self.reception_id = item.data(Qt.UserRole)
        
        try:
            # دریافت اطلاعات کامل پذیرش
            reception = self.data_manager.reception.get_reception_by_id(self.reception_id)
            if reception:
                # تبدیل تاریخ پذیرش به شمسی
                reception_date = reception.get('reception_date', '')
                reception_date_str = "تاریخ نامشخص"
                if reception_date:
                    try:
                        year, month, day = map(int, str(reception_date).split('-'))
                        jalali_date = jdatetime.date.fromgregorian(year=year, month=month, day=day)
                        reception_date_str = jalali_date.strftime("%Y/%m/%د")
                    except:
                        reception_date_str = str(reception_date)
                
                info_text = (
                    f"✅ پذیرش #{reception.get('reception_number', '')} انتخاب شد\n\n"
                    f"📅 تاریخ پذیرش: {reception_date_str}\n"
                    f"👤 مشتری: {reception.get('customer_name', 'نامشخص')}\n"
                    f"📱 تلفن: {reception.get('mobile', 'ندارد')}\n"
                    f"📱 دستگاه: {reception.get('device_type', '')} {reception.get('brand', '')} {reception.get('model', '')}\n"
                    f"🔢 سریال: {reception.get('serial_number', 'نامشخص')}\n"
                    f"📝 شرح خرابی: {reception.get('problem_description', 'ندارد')[:100]}..."
                )
                
                self.lbl_reception_info.setText(info_text)
                
                # ارسال سیگنال به فرم اصلی
                self.reception_selected.emit(self.reception_id)
                self.reception_changed.emit(self.reception_id)
                
        except Exception as e:
            print(f"خطا در دریافت اطلاعات پذیرش: {e}")
    
    def load_technicians(self):
        """بارگذاری لیست تعمیرکاران"""
        self.cmb_technician.clear()
        self.cmb_technician.addItem("انتخاب تعمیرکار", 0)
        
        try:
            # دریافت تمام اشخاص
            all_persons = self.data_manager.person.get_all_persons()
            
            # فیلتر کردن تعمیرکاران
            for person in all_persons:
                person_type = person.get('person_type', '')
                is_active = person.get('is_active', 1)
                
                # تعمیرکاران می‌توانند: تعمیرکار بیرونی یا کارمند باشند
                if is_active and person_type in ['تعمیرکار بیرونی', 'کارمند']:
                    full_name = f"{person.get('first_name', '')} {person.get('last_name', '')}"
                    self.cmb_technician.addItem(full_name, person['id'])
                    
        except Exception as e:
            print(f"خطا در بارگذاری تعمیرکاران: {e}")
    
    def load_outsource_persons(self):
        """بارگذاری لیست افراد برای بیرون سپاری"""
        self.cmb_outsource_to.clear()
        self.cmb_outsource_to.addItem("انتخاب شخص", 0)
        
        try:
            all_persons = self.data_manager.person.get_all_persons()
            
            for person in all_persons:
                person_type = person.get('person_type', '')
                is_active = person.get('is_active', 1)
                
                if is_active and person_type in ['تامین کننده', 'تعمیرکار بیرونی']:
                    full_name = f"{person.get('first_name', '')} {person.get('last_name', '')}"
                    self.cmb_outsource_to.addItem(full_name, person['id'])
                    
        except Exception as e:
            print(f"خطا در بارگذاری لیست بیرون‌سپاری: {e}")
    
    def on_repair_type_changed(self, repair_type):
        """وقتی نوع تعمیر تغییر کرد"""
        is_outsourced = (repair_type == "بیرون سپاری")
        
        # نمایش/مخفی کردن فیلدهای مربوط به بیرون سپاری
        self.lbl_outsource_to.setVisible(is_outsourced)
        self.cmb_outsource_to.setVisible(is_outsourced)
        self.lbl_outsource_cost.setVisible(is_outsourced)
        self.spn_outsource_cost.setVisible(is_outsourced)
        
        # ارسال سیگنال تغییر هزینه
        self.outsource_cost_changed.emit()
    
    def get_data(self):
        """دریافت داده‌های فرم"""
        data = {
            'reception_id': self.reception_id,
            'repair_date': self.txt_repair_date.get_gregorian_date() or jdatetime.datetime.now().togregorian().strftime("%Y-%m-%d"),
            'technician_id': self.cmb_technician.currentData() or None,
            'repair_type': self.cmb_repair_type.currentText(),
            'outsourced_to': self.cmb_outsource_to.currentData() if self.cmb_repair_type.currentText() == "بیرون سپاری" else None,
            'outsourced_cost': self.spn_outsource_cost.value() * 10 if self.cmb_repair_type.currentText() == "بیرون سپاری" else 0,  # تبدیل به ریال
            'labor_cost': 0,  # در تب خدمات محاسبه می‌شود
            'total_cost': 0,   # بعداً محاسبه می‌شود
            'repair_description': self.txt_description.toPlainText().strip(),
            'used_parts': '',  # در تب قطعات پر می‌شود
            'status': 'شروع شده'
        }
        
        return data
    
    def set_data(self, repair_data):
        """بارگذاری داده‌ها در فرم (برای ویرایش)"""
        try:
            # تاریخ تعمیر
            if repair_data.get('repair_date'):
                self.txt_repair_date.set_gregorian_date(repair_data['repair_date'])
            
            # تعمیرکار
            if repair_data.get('technician_id'):
                for i in range(self.cmb_technician.count()):
                    if self.cmb_technician.itemData(i) == repair_data['technician_id']:
                        self.cmb_technician.setCurrentIndex(i)
                        break
            
            # نوع تعمیر
            repair_type = repair_data.get('repair_type', 'داخلی')
            self.cmb_repair_type.setCurrentText(repair_type)
            
            # بیرون سپاری
            if repair_data.get('outsourced_to') and repair_type == 'بیرون سپاری':
                for i in range(self.cmb_outsource_to.count()):
                    if self.cmb_outsource_to.itemData(i) == repair_data['outsourced_to']:
                        self.cmb_outsource_to.setCurrentIndex(i)
                        break
            
            # هزینه بیرون سپاری (تبدیل به تومان)
            if repair_data.get('outsourced_cost'):
                self.spn_outsource_cost.setValue(float(repair_data['outsourced_cost']) / 10)
            
            # توضیحات
            if repair_data.get('repair_description'):
                self.txt_description.setPlainText(repair_data['repair_description'])
            
            print("✅ داده‌های تعمیر در تب اطلاعات بارگذاری شدند")
            
        except Exception as e:
            print(f"❌ خطا در بارگذاری داده‌های فرم اطلاعات: {e}")
    
    def get_outsource_cost(self):
        """دریافت هزینه بیرون‌سپاری (ریال)"""
        if self.cmb_repair_type.currentText() == "بیرون سپاری":
            return self.spn_outsource_cost.value() * 10  # تبدیل به ریال
        return 0