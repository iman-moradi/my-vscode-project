# debug_reports.py
import sys
import os

print("🔍 دیباگ ماژول گزارش‌گیری")
print("=" * 50)

# مسیر فعلی
print(f"مسیر جاری: {os.getcwd()}")

# بررسی ساختار پوشه
reports_path = "ui/forms/reports"
print(f"\nبررسی مسیر: {reports_path}")
print(f"آیا مسیر وجود دارد؟ {os.path.exists(reports_path)}")

if os.path.exists(reports_path):
    print("\nفایل‌های داخل پوشه:")
    for file in os.listdir(reports_path):
        print(f"  - {file}")
    
    # بررسی فایل‌های خاص
    required_files = ["__init__.py", "reports_window.py", "reports_main_form.py"]
    print("\nبررسی فایل‌های ضروری:")
    for file in required_files:
        file_path = os.path.join(reports_path, file)
        exists = os.path.exists(file_path)
        print(f"  - {file}: {'✅ موجود' if exists else '❌ ناموجود'}")
        
        if exists:
            print(f"    اندازه فایل: {os.path.getsize(file_path)} بایت")
    
    # سعی در ایمپورت
    print("\nتلاش برای ایمپورت...")
    try:
        # اضافه کردن مسیر به sys.path
        sys.path.insert(0, os.getcwd())
        
        from ui.forms.reports.reports_window import ReportsWindow
        print("✅ ایمپورت ReportsWindow موفقیت‌آمیز بود!")
        
        from ui.forms.reports.reports_main_form import ReportsMainForm
        print("✅ ایمپورت ReportsMainForm موفقیت‌آمیز بود!")
        
    except ImportError as e:
        print(f"❌ خطای ایمپورت: {e}")
        import traceback
        traceback.print_exc()
        
else:
    print("❌ پوشه گزارش‌گیری وجود ندارد!")

print("\n" + "=" * 50)
print("پایان دیباگ")