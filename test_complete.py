"""
فایل تست برای فرم مدیریت تعمیرات
"""

import sys
import os
from PySide6.QtWidgets import QApplication

# اضافه کردن مسیر پروژه
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
sys.path.insert(0, project_root)

from database.database import DatabaseManager
from database.models import DataManager


def test_repair_form():
    """تابع تست فرم مدیریت تعمیرات"""
    
    app = QApplication(sys.argv)
    
    print("🔧 در حال راه‌اندازی تست فرم مدیریت تعمیرات...")
    
    try:
        # ایجاد دیتابیس تست
        db_manager = DatabaseManager(":memory:")
        print("📁 ایجاد دیتابیس در حافظه...")
        
        if db_manager.initialize_database():
            print("✅ دیتابیس با موفقیت ایجاد شد")
        else:
            print("❌ خطا در ایجاد دیتابیس")
            return
        
        # ایجاد مدیر داده
        data_manager = DataManager()
        data_manager.db = db_manager
        
        print("📊 در حال ایجاد داده‌های نمونه...")
        
        # ۱. اضافه کردن مشتری
        customer_data = {
            'person_type': 'مشتری',
            'first_name': 'علی',
            'last_name': 'محمدی',
            'mobile': '09121234567',
            'address': 'تهران، میدان انقلاب'
        }
        
        if data_manager.person.add_person(customer_data):
            print("   ✅ مشتری نمونه اضافه شد")
        
        # ۲. اضافه کردن دستگاه
        device_data = {
            'device_type': 'یخچال',
            'brand': 'ال جی',
            'model': 'مدل 2023',
            'serial_number': 'SN123456'
        }
        
        # نیاز به اضافه کردن توابع add_device در مدل Device داریم
        # برای تست، مستقیماً در دیتابیس درج می‌کنیم
        data_manager.device.execute_query(
            "INSERT INTO Devices (device_type, brand, model, serial_number) VALUES (?, ?, ?, ?)",
            (device_data['device_type'], device_data['brand'], device_data['model'], device_data['serial_number'])
        )
        
        print("   ✅ دستگاه نمونه اضافه شد")
        
        # ۳. اضافه کردن پذیرش
        reception_data = {
            'customer_id': 1,
            'device_id': 1,
            'problem_description': 'یخچال کار نمی‌کند',
            'status': 'در انتظار'
        }
        
        reception_number = data_manager.reception.add_reception(reception_data)
        if reception_number:
            print(f"   ✅ پذیرش نمونه اضافه شد (شماره: {reception_number})")
        
        # ۴. اضافه کردن اجرت‌های نمونه
        sample_services = [
            ('SRV-0001', 'عیب‌یابی اولیه', 'عمومی', 50000, 0.5, 1, 'بررسی اولیه دستگاه', 1),
            ('SRV-0002', 'تعویض کمپرسور', 'یخچال', 350000, 3.0, 4, 'تعویض کمپرسور یخچال', 1),
            ('SRV-0003', 'شارژ گاز', 'کولر گازی', 250000, 2.0, 3, 'شارژ گاز کولر', 1),
        ]
        
        for service in sample_services:
            data_manager.service_fee.execute_query(
                "INSERT INTO ServiceFees (service_code, service_name, category, default_fee, estimated_hours, difficulty_level, description, is_active) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                service
            )
        
        print("   ✅ اجرت‌های نمونه اضافه شدند")
        
        # ۵. ایجاد و نمایش فرم
        print("🎯 ایجاد فرم مدیریت تعمیرات...")
        
        from ui.forms.repair_form import RepairForm
        form = RepairForm(data_manager, reception_id=1)
        form.show()
        
        print("""
✅ تست با موفقیت راه‌اندازی شد!

📝 دستورالعمل تست:
1. بررسی کنید که پذیرش در ComboBox نمایش داده شود
2. روی تب "هزینه‌ها" کلیک کنید
3. در کمبوباکس دسته‌بندی، عبارت "یخچال" را تایپ کنید
4. بررسی کنید که جستجوی زنده کار کند
5. یک دسته‌بندی انتخاب کنید
6. بررسی کنید که اجرت‌های آن دسته در کمبوباکس اجرت نمایش داده شوند
7. یک اجرت انتخاب کنید و بررسی کنید که قیمت به صورت خودکار پر شود
8. دکمه "افزودن به لیست" را بزنید
9. بررسی کنید که اجرت به جدول اضافه شود
10. دکمه "محاسبه کل هزینه‌ها" را تست کنید
11. دکمه "مدیریت اجرت‌ها" را تست کنید
        """)
        
        sys.exit(app.exec())
        
    except Exception as e:
        print(f"❌ خطا در اجرای تست: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_repair_form()