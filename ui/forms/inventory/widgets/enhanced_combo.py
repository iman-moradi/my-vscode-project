# ui/forms/inventory/widgets/enhanced_combo.py
"""
کامبوباکس‌های پیشرفته با جستجوی زنده - نسخه نهایی با استفاده از data_manager فرم
"""

from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QComboBox, QPushButton, 
    QLineEdit
)
from PySide6.QtCore import Qt, Signal, QTimer

class EnhancedComboBox(QWidget):
    """کامبوباکس پیشرفته با جستجوی زنده"""
    
    value_changed = Signal(int)  # signal با ID آیتم
    
    def __init__(self, combo_type, parent=None):
        """
        combo_type: 'category', 'brand', 'supplier'
        """
        super().__init__(parent)
        self.combo_type = combo_type
        self.items = []
        self.setup_ui()
        
        # بارگذاری با تاخیر تا مطمئن شویم فرم کامل ساخته شده
        QTimer.singleShot(100, self.load_items)
    
    def setup_ui(self):
        """تنظیم رابط کاربری"""
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)
        
        # کامبوباکس اصلی
        self.combo = QComboBox()
        self.combo.setMinimumWidth(250)
        self.combo.setMaximumWidth(300)
        self.combo.currentIndexChanged.connect(self.on_index_changed)
        
        # فیلد جستجوی سریع
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("جستجو...")
        self.search_edit.setVisible(False)
        self.search_edit.textChanged.connect(self.on_search)
        
        layout.addWidget(self.combo)
        layout.addWidget(self.search_edit)
        
        self.setLayout(layout)
        
        # تایمر برای جستجوی زنده
        self.search_timer = QTimer()
        self.search_timer.setSingleShot(True)
        self.search_timer.timeout.connect(self.perform_search)
    
    def get_data_manager(self):
        """دریافت DataManager از فرم والد"""
        try:
            # حرکت به سمت بالا در سلسله مراتب والدین تا فرم را پیدا کنیم
            parent = self.parent()
            while parent:
                if hasattr(parent, 'data_manager') and parent.data_manager:
                    return parent.data_manager
                parent = parent.parent()
            return None
        except:
            return None
    
    def load_items(self):
        """بارگذاری آیتم‌ها از دیتابیس"""
        print(f"🔄 در حال بارگذاری {self.combo_type} از دیتابیس...")
        
        try:
            self.items = []
            self.combo.clear()
            
            data_manager = self.get_data_manager()
            if not data_manager:
                print(f"❌ DataManager برای {self.combo_type} یافت نشد")
                self.load_sample_items()
                return
            
            # بارگذاری بر اساس نوع
            if self.combo_type == 'category':
                self.load_categories(data_manager)
            elif self.combo_type == 'brand':
                self.load_brands(data_manager)
            elif self.combo_type == 'supplier':
                self.load_suppliers(data_manager)
            
            # اگر هیچ آیتمی بارگذاری نشد
            if self.combo.count() == 0:
                self.load_sample_items()
                
        except Exception as e:
            print(f"❌ خطا در بارگذاری {self.combo_type}: {str(e)}")
            self.load_sample_items()
    
    def load_categories(self, data_manager):
        """بارگذاری دسته‌بندی‌ها"""
        if hasattr(data_manager, 'device_category_name'):
            items = data_manager.device_category_name.get_all()
            if items:
                self.items = items
                self.combo.addItem("-- انتخاب دسته‌بندی --", 0)
                for item in items:
                    self.combo.addItem(item.get('name', ''), item.get('id', 0))
                print(f"✅ {len(items)} دسته‌بندی بارگذاری شد")
    
    def load_brands(self, data_manager):
        """بارگذاری برندها"""
        if hasattr(data_manager, 'brand'):
            items = data_manager.brand.get_all_brands()
            if items:
                self.items = items
                self.combo.addItem("-- انتخاب برند --", 0)
                for item in items:
                    self.combo.addItem(item.get('name', ''), item.get('id', 0))
                print(f"✅ {len(items)} برند بارگذاری شد")
    
    def load_suppliers(self, data_manager):
        """بارگذاری تامین‌کنندگان"""
        if hasattr(data_manager, 'person'):
            items = data_manager.person.get_by_type('تامین کننده')
            if items:
                self.items = items
                self.combo.addItem("-- انتخاب تامین‌کننده --", 0)
                for item in items:
                    name = self.format_supplier_name(item)
                    self.combo.addItem(name, item.get('id', 0))
                print(f"✅ {len(items)} تامین‌کننده بارگذاری شد")
    
    def load_sample_items(self):
        """بارگذاری آیتم‌های نمونه"""
        if self.combo_type == 'category':
            sample_items = [
                {'id': 1, 'name': 'یخچال'},
                {'id': 2, 'name': 'مایکروویو'},
                {'id': 3, 'name': 'جاروبرقی'}
            ]
            self.combo.addItem("-- انتخاب دسته‌بندی --", 0)
            for item in sample_items:
                self.combo.addItem(item['name'], item['id'])
            print("📋 دسته‌بندی‌های نمونه بارگذاری شد")
        elif self.combo_type == 'brand':
            sample_items = [
                {'id': 1, 'name': 'سامسونگ'},
                {'id': 2, 'name': 'ال جی'},
                {'id': 3, 'name': 'پاناسونیک'}
            ]
            self.combo.addItem("-- انتخاب برند --", 0)
            for item in sample_items:
                self.combo.addItem(item['name'], item['id'])
            print("📋 برندهای نمونه بارگذاری شد")
        elif self.combo_type == 'supplier':
            sample_items = [
                {'id': 1, 'first_name': 'رضا', 'last_name': 'احمدی', 'mobile': '09121234567'},
                {'id': 2, 'first_name': 'محمد', 'last_name': 'کریمی', 'mobile': '09129876543'},
                {'id': 3, 'first_name': 'علی', 'last_name': 'محمدی', 'mobile': '09131112233'}
            ]
            self.combo.addItem("-- انتخاب تامین‌کننده --", 0)
            for item in sample_items:
                name = self.format_supplier_name(item)
                self.combo.addItem(name, item['id'])
            print("📋 تامین‌کنندگان نمونه بارگذاری شد")
    
    def format_supplier_name(self, supplier):
        """قالب‌بندی نام تامین‌کننده"""
        name_parts = []
        if supplier.get('first_name'):
            name_parts.append(supplier.get('first_name'))
        if supplier.get('last_name'):
            name_parts.append(supplier.get('last_name'))
        
        name = ' '.join(name_parts)
        
        if supplier.get('mobile'):
            if name:
                name = f"{name} ({supplier.get('mobile')})"
            else:
                name = f"تامین‌کننده ({supplier.get('mobile')})"
        
        return name.strip() if name.strip() else "نامشخص"
    
    # بقیه متدها بدون تغییر...
    def on_index_changed(self, index):
        """هنگام تغییر انتخاب"""
        if index > 0:
            item_id = self.combo.currentData()
            if item_id:
                self.value_changed.emit(item_id)
    
    def on_search(self, text):
        """جستجوی زنده"""
        if text:
            self.search_edit.setVisible(True)
            self.combo.setVisible(False)
            self.search_timer.stop()
            self.search_timer.start(300)
        else:
            self.search_edit.setVisible(False)
            self.combo.setVisible(True)
            QTimer.singleShot(100, self.load_items)
    
    def perform_search(self):
        """انجام جستجو"""
        search_text = self.search_edit.text().strip().lower()
        if not search_text:
            return
        
        filtered = []
        
        if self.combo_type == 'supplier':
            for item in self.items:
                name = self.format_supplier_name(item).lower()
                if search_text in name:
                    filtered.append(item)
                    continue
                mobile = item.get('mobile', '').lower()
                if search_text in mobile:
                    filtered.append(item)
        else:
            for item in self.items:
                name = item.get('name', '').lower()
                if search_text in name:
                    filtered.append(item)
        
        self.combo.blockSignals(True)
        self.combo.clear()
        
        if filtered:
            self.combo.addItem(f"-- نتایج جستجو ({len(filtered)} مورد) --", 0)
            for item in filtered:
                if self.combo_type == 'supplier':
                    name = self.format_supplier_name(item)
                else:
                    name = item.get('name', '')
                item_id = item.get('id', 0)
                self.combo.addItem(name, item_id)
        else:
            self.combo.addItem(f"-- موردی یافت نشد --", 0)
        
        self.combo.setVisible(True)
        self.search_edit.setVisible(False)
        self.combo.blockSignals(False)
    
    def set_value(self, item_id):
        """تنظیم مقدار انتخابی"""
        if not isinstance(item_id, int):
            try:
                item_id = int(item_id)
            except:
                item_id = 0
        
        for i in range(self.combo.count()):
            if self.combo.itemData(i) == item_id:
                self.combo.setCurrentIndex(i)
                return
        
        if self.combo.count() > 0:
            self.combo.setCurrentIndex(0)
    
    def get_value(self):
        """دریافت مقدار انتخابی"""
        index = self.combo.currentIndex()
        if index > 0:
            return self.combo.currentData()
        return 0
    
    def get_text(self):
        """دریافت متن انتخابی"""
        return self.combo.currentText() if self.combo.currentIndex() > 0 else ""

    def set_text(self, text):
        """تنظیم متن انتخاب شده در کامبوباکس - نسخه بهینه"""
        if not text or text == "":
            self.combo.setCurrentIndex(0)
            return
        
        # ابتدا سعی می‌کنیم دقیقاً تطبیق دهیم
        index = self.combo.findText(text, Qt.MatchFixedString)
        if index >= 0:
            self.combo.setCurrentIndex(index)
            return
        
        # اگر دقیقاً پیدا نشد، سعی می‌کنیم بخشی از متن را جستجو کنیم
        for i in range(self.combo.count()):
            item_text = self.combo.itemText(i)
            if text in item_text:
                self.combo.setCurrentIndex(i)
                return
        
        # اگر باز هم پیدا نشد، سعی می‌کنیم با بخشی از نام تطبیق دهیم
        # (مخصوصاً برای تامین‌کنندگان که فرمت "نام (موبایل)" دارند)
        for i in range(self.combo.count()):
            item_text = self.combo.itemText(i)
            # اگر text بخشی از item_text است یا برعکس
            if text in item_text or item_text in text:
                self.combo.setCurrentIndex(i)
                return
        
        # اگر هیچ‌کدام جواب نداد، متن را به صورت مستقیم تنظیم می‌کنیم
        self.combo.setEditText(text)

    def clear(self):
        """پاک کردن انتخاب"""
        self.combo.setCurrentIndex(0)
    
    def refresh(self):
        """بارگذاری مجدد آیتم‌ها"""
        self.load_items()


    # بخشی از کلاس EnhancedComboBox در widgets/enhanced_combo.py
    # به متد load_items اضافه کنید:

    def load_items(self):
        """بارگذاری آیتم‌ها از دیتابیس"""
        print(f"🔄 در حال بارگذاری {self.combo_type} از دیتابیس...")
        
        try:
            self.items = []
            self.combo.clear()
            
            data_manager = self.get_data_manager()
            if not data_manager:
                print(f"❌ DataManager برای {self.combo_type} یافت نشد")
                self.load_sample_items()
                return
            
            # بارگذاری بر اساس نوع
            if self.combo_type == 'category':
                self.load_categories(data_manager)
            elif self.combo_type == 'brand':
                self.load_brands(data_manager)
            elif self.combo_type == 'supplier':
                self.load_suppliers(data_manager)
            elif self.combo_type == 'customer':
                self.load_customers(data_manager)
            elif self.combo_type == 'reception':
                self.load_receptions(data_manager)
            
            # اگر هیچ آیتمی بارگذاری نشد
            if self.combo.count() == 0:
                self.load_sample_items()
                
        except Exception as e:
            print(f"❌ خطا در بارگذاری {self.combo_type}: {str(e)}")
            self.load_sample_items()

    def load_customers(self, data_manager):
        """بارگذاری مشتریان"""
        if hasattr(data_manager, 'person'):
            items = data_manager.person.get_by_type('مشتری')
            if items:
                self.items = items
                self.combo.addItem("-- انتخاب مشتری --", 0)
                for item in items:
                    name = self.format_person_name(item)
                    self.combo.addItem(name, item.get('id', 0))
                print(f"✅ {len(items)} مشتری بارگذاری شد")

    def load_receptions(self, data_manager):
        """بارگذاری پذیرش‌ها"""
        if hasattr(data_manager, 'reception'):
            items = data_manager.reception.get_all_receptions()
            if items:
                self.items = items
                self.combo.addItem("-- انتخاب پذیرش --", 0)
                for item in items:
                    text = f"{item.get('reception_number', '')} - {item.get('customer_name', '')}"
                    self.combo.addItem(text, item.get('id', 0))
                print(f"✅ {len(items)} پذیرش بارگذاری شد")

    def format_person_name(self, person):
        """قالب‌بندی نام شخص"""
        name_parts = []
        if person.get('first_name'):
            name_parts.append(person.get('first_name'))
        if person.get('last_name'):
            name_parts.append(person.get('last_name'))
        
        name = ' '.join(name_parts)
        
        if person.get('mobile'):
            if name:
                name = f"{name} ({person.get('mobile')})"
            else:
                name = f"مشتری ({person.get('mobile')})"
        
        return name.strip() if name.strip() else "نامشخص"       