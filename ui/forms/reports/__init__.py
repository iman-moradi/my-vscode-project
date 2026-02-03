"""
ماژول گزارش‌گیری - اکسپورت کلاس‌های اصلی
"""

from .reports_window import ReportsWindow
from .reports_main_form import ReportsMainForm

# فرم‌های گزارش
from .forms.financial_report_form import FinancialReportForm
from .forms.inventory_report_form import InventoryReportForm
from .forms.repair_report_form import RepairReportForm
from .forms.sales_report_form import SalesReportForm
from .forms.customer_report_form import CustomerReportForm
from .forms.weekly_report_form import WeeklyReportForm
from .forms.monthly_report_form import MonthlyReportForm

# ابزارهای کمکی
try:
    from .utils.exporters import ExcelExporter
except ImportError:
    ExcelExporter = None
    print("⚠️ ExcelExporter در دسترس نیست")

try:
    from .utils.printers import ReportPrinter
except ImportError:
    ReportPrinter = None
    print("⚠️ ReportPrinter در دسترس نیست")

try:
    from .utils.report_generators import ReportGenerator
except ImportError:
    ReportGenerator = None
    print("⚠️ ReportGenerator در دسترس نیست")

try:
    from .utils.optimizations import ReportDataLoader, ReportCache, PerformanceMonitor
except ImportError:
    ReportDataLoader = None
    ReportCache = None
    PerformanceMonitor = None
    print("⚠️ ابزارهای بهینه‌سازی در دسترس نیستند")

try:
    from .utils.help_system import ReportHelpSystem
except ImportError:
    ReportHelpSystem = None
    print("⚠️ ReportHelpSystem در دسترس نیست")


__all__ = [
    # کلاس‌های اصلی
    'ReportsWindow',
    'ReportsMainForm',
    
    # فرم‌های گزارش
    'FinancialReportForm',
    'InventoryReportForm',
    'RepairReportForm',
    'SalesReportForm',
    'CustomerReportForm',
    'WeeklyReportForm',
    'MonthlyReportForm',
    
    # ابزارها
    'ExcelExporter',
    'ReportPrinter',
    'ReportGenerator',
    'ReportDataLoader',
    'ReportCache',
    'PerformanceMonitor',
    'ReportHelpSystem',
    

]