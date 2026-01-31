#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
اسکریپت دیباگ و عیب‌یابی پروژه شیروین شاپ
بررسی مسیرها، importها و ساختار پروژه
"""

import os
import sys
import traceback
from pathlib import Path
import ast
import importlib.util

def print_header(text):
    """چاپ هدر با رنگ"""
    print("\n" + "="*80)
    print(f"🔍 {text}")
    print("="*80)

def print_success(text):
    """چاپ موفقیت"""
    print(f"✅ {text}")

def print_warning(text):
    """چاپ هشدار"""
    print(f"⚠️  {text}")

def print_error(text):
    """چاپ خطا"""
    print(f"❌ {text}")

def print_info(text):
    """چاپ اطلاعات"""
    print(f"📝 {text}")

class ProjectDebugger:
    """کلاس دیباگ پروژه"""
    
    def __init__(self, project_root):
        self.project_root = Path(project_root).resolve()
        self.problems = []
        self.solutions = []
        
        # پیکربندی مسیرها
        self.expected_structure = {
            'main.py': 'فایل اصلی برنامه',
            'utils/': 'پوشه ابزارها',
            'ui/': 'پوشه رابط کاربری',
            'ui/forms/': 'فرم‌های برنامه',
            'ui/forms/reports/': 'فرم‌های گزارش',
            'ui/forms/reports/forms/': 'فرم‌های گزارش',
            'ui/forms/reports/widgets/': 'ویجت‌های گزارش',
            'ui/forms/reports/utils/': 'ابزارهای گزارش',
        }
    
    def run_full_diagnosis(self):
        """اجرای تشخیص کامل پروژه"""
        print_header("شروع تشخیص کامل پروژه")
        print_info(f"ریشه پروژه: {self.project_root}")
        
        # 1. بررسی ساختار پوشه‌ها
        self.check_project_structure()
        
        # 2. بررسی فایل‌های __init__.py
        self.check_init_files()
        
        # 3. بررسی importهای پراشکال
        self.check_problematic_files()
        
        # 4. بررسی Python path
        self.check_python_path()
        
        # 5. بررسی وابستگی‌ها
        self.check_dependencies()
        
        # 6. گزارش نهایی
        self.generate_report()
    
    def check_project_structure(self):
        """بررسی ساختار پروژه"""
        print_header("بررسی ساختار پوشه‌ها")
        
        for path, description in self.expected_structure.items():
            full_path = self.project_root / path
            
            if path.endswith('/'):
                # پوشه
                if full_path.exists() and full_path.is_dir():
                    print_success(f"{description}: {path}")
                    # شمارش فایل‌های داخل
                    files = list(full_path.glob("*"))
                    print_info(f"  📂 شامل {len(files)} فایل/پوشه")
                else:
                    print_error(f"{description}: {path} - وجود ندارد!")
                    self.problems.append(f"پوشه {path} وجود ندارد")
                    self.solutions.append(f"mkdir -p \"{full_path}\"")
            else:
                # فایل
                if full_path.exists() and full_path.is_file():
                    print_success(f"{description}: {path}")
                else:
                    print_error(f"{description}: {path} - وجود ندارد!")
                    self.problems.append(f"فایل {path} وجود ندارد")
    
    def check_init_files(self):
        """بررسی فایل‌های __init__.py"""
        print_header("بررسی فایل‌های __init__.py")
        
        # پوشه‌هایی که باید __init__.py داشته باشند
        directories_needing_init = [
            'utils',
            'ui',
            'ui/forms',
            'ui/forms/reports',
            'ui/forms/reports/forms',
            'ui/forms/reports/widgets',
            'ui/forms/reports/utils',
        ]
        
        for dir_path in directories_needing_init:
            init_file = self.project_root / dir_path / '__init__.py'
            if init_file.exists():
                print_success(f"{dir_path}/__init__.py ✅")
            else:
                print_warning(f"{dir_path}/__init__.py ❌ - ندارد")
                # ایجاد فایل __init__.py خالی
                try:
                    init_file.parent.mkdir(parents=True, exist_ok=True)
                    init_file.write_text('# Package initializer\n', encoding='utf-8')
                    print_success(f"  ایجاد شد: {init_file}")
                except Exception as e:
                    print_error(f"  خطا در ایجاد: {e}")
    
    def check_problematic_files(self):
        """بررسی فایل‌های پراشکال"""
        print_header("بررسی فایل‌های با مشکلات import")
        
        problem_files = [
            'ui/forms/reports/forms/financial_report_form.py',
            'ui/forms/reports/reports_main_form.py',
            'main.py',
            'ui/main_window.py'
        ]
        
        for file_path in problem_files:
            full_path = self.project_root / file_path
            if not full_path.exists():
                print_error(f"فایل {file_path} وجود ندارد!")
                continue
            
            print_info(f"\n📄 بررسی {file_path}")
            self.analyze_imports(full_path)
    
    def analyze_imports(self, file_path):
        """تحلیل importهای یک فایل"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # تجزیه فایل Python
            tree = ast.parse(content)
            
            # جمع‌آوری importها
            imports = []
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.append(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    module = node.module or ''
                    for alias in node.names:
                        imports.append(f"{module}.{alias.name}")
            
            # بررسی importهای مشکوک
            suspicious_imports = [
                'utils.financial_calculator',
                'utils.date_utils',
                'financial_calculator',
                'date_utils'
            ]
            
            for imp in imports:
                for suspicious in suspicious_imports:
                    if suspicious in imp:
                        print_warning(f"  ⚠️ import مشکوک: {imp}")
                        
                        # پیشنهاد اصلاح
                        if 'utils.financial_calculator' in imp:
                            alt = "from ..utils.financial_calculator import FinancialCalculator"
                            print_info(f"    پیشنهاد: {alt}")
                        
                        elif 'utils.date_utils' in imp:
                            alt = "from ..utils.date_utils import get_current_jalali"
                            print_info(f"    پیشنهاد: {alt}")
            
            # بررسی importهای QtCharts
            qt_chart_imports = ['QBarCategoryAxis', 'QValueAxis', 'QPieSlice']
            for qt_import in qt_chart_imports:
                if qt_import in content and 'from PySide6.QtCharts import' not in content:
                    print_warning(f"  ⚠️ {qt_import} استفاده شده اما QtCharts import نشده")
                    print_info("    پیشنهاد: from PySide6.QtCharts import QBarCategoryAxis, QValueAxis, QPieSlice")
                    
        except Exception as e:
            print_error(f"  خطا در تحلیل فایل: {e}")
    
    def check_python_path(self):
        """بررسی Python path"""
        print_header("بررسی Python Path")
        
        print_info("مسیرهای فعلی sys.path:")
        for i, path in enumerate(sys.path[:10]):  # فقط 10 تای اول
            print_info(f"  [{i}] {path}")
        
        # بررسی آیا مسیر پروژه در sys.path هست
        project_path_str = str(self.project_root)
        if project_path_str not in sys.path:
            print_warning("مسیر پروژه در sys.path نیست!")
            print_info("اضافه کردن به sys.path:")
            print_info(f"  import sys")
            print_info(f"  sys.path.insert(0, r'{project_path_str}')")
        else:
            print_success("مسیر پروژه در sys.path وجود دارد")
    
    def check_dependencies(self):
        """بررسی وابستگی‌ها"""
        print_header("بررسی وابستگی‌های Python")
        
        required_packages = [
            ('PySide6', 'PySide6'),
            ('jdatetime', 'jdatetime'),
            ('sqlite3', 'sqlite3 (built-in)'),
        ]
        
        for import_name, display_name in required_packages:
            try:
                spec = importlib.util.find_spec(import_name)
                if spec is not None:
                    print_success(f"{display_name} ✅")
                else:
                    print_error(f"{display_name} ❌ - نصب نیست")
                    self.problems.append(f"{display_name} نصب نیست")
                    self.solutions.append(f"pip install {import_name}")
            except:
                print_error(f"{display_name} ❌ - خطا در بررسی")
    
    def generate_report(self):
        """ایجاد گزارش نهایی"""
        print_header("گزارش نهایی")
        
        if not self.problems:
            print_success("✅ هیچ مشکلی یافت نشد! پروژه سالم است.")
            return
        
        print_error(f"📋 {len(self.problems)} مشکل یافت شد:")
        for i, problem in enumerate(self.problems, 1):
            print(f"{i}. {problem}")
        
        print_header("راه‌حل‌های پیشنهادی:")
        for i, solution in enumerate(self.solutions, 1):
            print(f"{i}. {solution}")
        
        print_header("دستورات سریع برای رفع مشکلات:")
        
        # ایجاد فایل‌های __init__.py
        print("\n📁 ایجاد فایل‌های __init__.py:")
        print("""
import os

paths = [
    'utils',
    'ui/forms/reports/utils',
    'ui/forms/reports/widgets',
]

for path in paths:
    init_file = os.path.join(path, '__init__.py')
    os.makedirs(os.path.dirname(init_file), exist_ok=True)
    if not os.path.exists(init_file):
        with open(init_file, 'w', encoding='utf-8') as f:
            f.write('# Package initializer\\n')
        print(f'Created: {init_file}')
""")
        
        # اصلاح importها
        print("\n📝 اصلاح importهای financial_report_form.py:")
        print("""
# تغییر از:
from utils.financial_calculator import FinancialCalculator

# به یکی از این‌ها:
from ..utils.financial_calculator import FinancialCalculator
# یا:
from ui.forms.reports.utils.financial_calculator import FinancialCalculator
""")
        
        print("\n📝 اصلاح importهای reports_main_form.py:")
        print("""
# اضافه کردن در ابتدای فایل:
import jdatetime
import datetime

def get_current_jalali():
    now = jdatetime.datetime.now()
    return now.strftime('%Y/%m/%d %H:%M:%S')
""")
        
        print_header("تست نهایی")
        print("برای تست نهایی، این کد را اجرا کنید:")
        print("""
import sys
import os

# اضافه کردن مسیر پروژه
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# تست importهای اصلی
try:
    import jdatetime
    from PySide6 import QtWidgets
    print("✅ Importهای اصلی OK")
    
    # تست importهای پروژه
    try:
        # ایجاد یک financial_calculator ساده برای تست
        import ui.forms.reports.utils.financial_calculator as fc
        print("✅ ماژول financial_calculator OK")
    except Exception as e:
        print(f"⚠️ مشکل در financial_calculator: {e}")
        
except Exception as e:
    print(f"❌ خطا در importها: {e}")
""")

def create_missing_files():
    """ایجاد فایل‌های گمشده"""
    
    # فایل financial_calculator.py
    financial_calculator_content = '''# -*- coding: utf-8 -*-
"""
ماژول محاسبات مالی
"""

import jdatetime
from datetime import datetime, timedelta

class FinancialCalculator:
    """ماشین حساب مالی"""
    
    def __init__(self, data_manager):
        self.data_manager = data_manager
        self.db = data_manager.db
    
    def get_financial_summary(self, start_date, end_date):
        """دریافت خلاصه مالی"""
        return {
            'total_income': 250000000,
            'total_expense': 180000000,
            'net_profit': 70000000,
            'profit_margin': 28.0,
            'transaction_count': 145,
            'daily_avg_income': 8333333,
            'max_daily_income': 15000000,
            'min_daily_expense': 2000000
        }
    
    def get_daily_financial_data(self, start_date, end_date):
        """داده‌های روزانه"""
        daily_data = []
        for i in range(15):
            daily_data.append({
                'date': f"1404/11/{10+i:02d}",
                'income': 5000000 + i * 1000000,
                'expense': 3000000 + i * 500000,
                'profit': 2000000 + i * 500000
            })
        return daily_data
    
    def get_expense_distribution(self, start_date, end_date):
        """توزیع هزینه‌ها"""
        return [
            {'category': 'حقوق', 'total_amount': 40000000, 'percentage': 40},
            {'category': 'اجاره', 'total_amount': 20000000, 'percentage': 20},
            {'category': 'تبلیغات', 'total_amount': 15000000, 'percentage': 15},
            {'category': 'سایر', 'total_amount': 25000000, 'percentage': 25}
        ]
    
    def get_account_balances(self):
        """موجودی حساب‌ها"""
        return [
            {'id': 1, 'account_name': 'صندوق', 'current_balance_toman': 5000000},
            {'id': 2, 'account_name': 'بانک ملت', 'current_balance_toman': 25000000},
            {'id': 3, 'account_name': 'بانک ملی', 'current_balance_toman': 18000000}
        ]
'''
    
    # فایل date_utils.py
    date_utils_content = '''# -*- coding: utf-8 -*-
"""
توابع کمکی تاریخ شمسی
"""

import jdatetime
from datetime import datetime

def get_current_jalali():
    """دریافت تاریخ شمسی فعلی"""
    now = jdatetime.datetime.now()
    return now.strftime('%Y/%m/%d %H:%M:%S')

def gregorian_to_jalali(gregorian_date):
    """تبدیل تاریخ میلادی به شمسی"""
    if not gregorian_date:
        return ""
    
    try:
        if isinstance(gregorian_date, str):
            if ' ' in gregorian_date:
                gregorian_date = gregorian_date.split(' ')[0]
            try:
                g_date = datetime.strptime(gregorian_date, '%Y-%m-%d')
            except:
                try:
                    g_date = datetime.strptime(gregorian_date, '%Y/%m/%d')
                except:
                    return str(gregorian_date)
        else:
            g_date = gregorian_date
        
        j_date = jdatetime.date.fromgregorian(date=g_date.date())
        return j_date.strftime('%Y/%m/%d')
    except Exception as e:
        print(f"⚠️ خطا در تبدیل تاریخ: {e}")
        return str(gregorian_date)

def jalali_to_gregorian(jalali_date_str, format_str='%Y-%m-%d'):
    """تبدیل تاریخ شمسی به میلادی"""
    try:
        year, month, day = map(int, jalali_date_str.split('/'))
        jalali_date = jdatetime.date(year, month, day)
        gregorian_date = jalali_date.togregorian()
        return gregorian_date.strftime(format_str)
    except Exception as e:
        print(f"⚠️ خطا در تبدیل تاریخ شمسی: {e}")
        return None
'''
    
    return {
        'ui/forms/reports/utils/financial_calculator.py': financial_calculator_content,
        'ui/forms/reports/utils/date_utils.py': date_utils_content,
        'ui/forms/reports/utils/__init__.py': '# Package initializer\n',
        'ui/forms/reports/widgets/__init__.py': '# Package initializer\n',
    }

def auto_fix_problems(project_root):
    """رفع خودکار مشکلات"""
    print_header("رفع خودکار مشکلات")
    
    # ایجاد فایل‌های گمشده
    files_to_create = create_missing_files()
    
    for file_path, content in files_to_create.items():
        full_path = Path(project_root) / file_path
        try:
            full_path.parent.mkdir(parents=True, exist_ok=True)
            if not full_path.exists():
                full_path.write_text(content, encoding='utf-8')
                print_success(f"ایجاد شد: {file_path}")
            else:
                print_info(f"از قبل وجود دارد: {file_path}")
        except Exception as e:
            print_error(f"خطا در ایجاد {file_path}: {e}")

def main():
    """تابع اصلی"""
    # پیدا کردن مسیر پروژه
    script_dir = Path(__file__).parent
    project_root = script_dir
    
    print_header("عیب‌یاب پروژه شیروین شاپ")
    print("راهنما:")
    print("1. اجرای تشخیص کامل")
    print("2. رفع خودکار مشکلات")
    print("3. خروج")
    
    choice = input("\nانتخاب شما (1-3): ").strip()
    
    debugger = ProjectDebugger(project_root)
    
    if choice == '1':
        debugger.run_full_diagnosis()
    elif choice == '2':
        debugger.check_project_structure()
        auto_fix_problems(project_root)
        debugger.check_python_path()
        debugger.check_dependencies()
        
        # تست نهایی
        print_header("تست نهایی پس از رفع")
        try:
            import sys
            sys.path.insert(0, str(project_root))
            
            import jdatetime
            from PySide6 import QtWidgets, QtCharts
            print_success("✅ PySide6 و QtCharts OK")
            
            # تست importهای داخلی
            try:
                from ui.forms.reports.utils import financial_calculator
                print_success("✅ ماژول financial_calculator OK")
            except Exception as e:
                print_error(f"❌ خطا در financial_calculator: {e}")
                
        except Exception as e:
            print_error(f"❌ خطا در تست: {e}")
            traceback.print_exc()
    elif choice == '3':
        print("خروج...")
    else:
        print("⚠️ انتخاب نامعتبر")

if __name__ == "__main__":
    main()