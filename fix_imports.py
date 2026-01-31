#!/usr/bin/env python3
import os
import sys

# 1. خالی کردن فایل __init__.py مشکل‌دار
init_path = r"ui\forms\reports\utils\__init__.py"
if os.path.exists(init_path):
    with open(init_path, 'w', encoding='utf-8') as f:
        f.write('# Package initializer\n')
    print(f"✅ فایل {init_path} خالی شد")

# 2. اضافه کردن import مستقیم در reports_main_form.py
main_form_path = r"ui\forms\reports\reports_main_form.py"
if os.path.exists(main_form_path):
    with open(main_form_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # پیدا کردن خط import و اصلاح آن
    lines = content.split('\n')
    for i, line in enumerate(lines):
        if 'from ui.forms.reports.utils.financial_calculator import FinancialCalculator' in line:
            # جایگزین با import مستقیم
            lines[i] = '# ' + line + '\n' + 'from ui.forms.reports.utils.financial_calculator import FinancialCalculator'
            break
    
    with open(main_form_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    
    print(f"✅ فایل {main_form_path} اصلاح شد")

# 3. تست
print("\n🧪 تست...")
sys.path.insert(0, os.getcwd())

try:
    import jdatetime
    print("✅ jdatetime OK")
    
    # تست مستقیم
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "financial_calculator", 
        r"ui\forms\reports\utils\financial_calculator.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    print("✅ financial_calculator.py قابل import است")
    
except Exception as e:
    print(f"❌ خطا: {e}")

print("\n✅ انجام شد! برنامه را دوباره اجرا کنید.")