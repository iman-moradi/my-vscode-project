# ui/forms/reports/utils/help_system.py
"""
سیستم راهنمای کاربری برای ماژول گزارش‌گیری
"""

from PySide6.QtWidgets import *
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QDesktopServices
from PySide6.QtCore import QUrl


class ReportHelpSystem:
    """سیستم راهنمای گزارش‌گیری"""
    
    @staticmethod
    def show_quick_start_guide():
        """نمایش راهنمای شروع سریع"""
        dialog = QDialog()
        dialog.setWindowTitle("🚀 راهنمای شروع سریع گزارش‌گیری")
        dialog.setMinimumSize(700, 500)
        
        layout = QVBoxLayout(dialog)
        
        # تب‌ها
        tab_widget = QTabWidget()
        
        # تب مقدمه
        intro_tab = QWidget()
        intro_layout = QVBoxLayout(intro_tab)
        
        intro_text = """
        <h2>🎯 معرفی ماژول گزارش‌گیری</h2>
        
        <p>ماژول گزارش‌گیری یک سیستم جامع برای تحلیل و گزارش‌گیری از داده‌های تعمیرگاه است. این ماژول شامل:</p>
        
        <ul>
            <li><b>📊 ۹ نوع گزارش تخصصی</b> (داشبورد، مالی، فروش، انبار، تعمیرات، مشتریان و ...)</li>
            <li><b>📈 نمودارهای تعاملی</b> با قابلیت زوم و فیلتر</li>
            <li><b>📤 خروجی‌های مختلف</b> (Excel, PDF, چاپ)</li>
            <li><b>🔍 فیلترهای پیشرفته</b> بر اساس تاریخ، دسته، وضعیت و ...</li>
            <li><b>⚡ بهینه‌سازی عملکرد</b> با سیستم کش و لودر موازی</li>
        </ul>
        
        <h3>📋 نحوه استفاده:</h3>
        <ol>
            <li>از تب‌های بالای پنجره، نوع گزارش مورد نظر را انتخاب کنید</li>
            <li>فیلترهای مورد نیاز را تنظیم کنید</li>
            <li>دکمه "بروزرسانی" را بزنید یا منتظر لود خودکار بمانید</li>
            <li>برای خروجی، از دکمه‌های خروجی Excel/PDF استفاده کنید</li>
            <li>برای تنظیمات بیشتر، به منوی تنظیمات مراجعه کنید</li>
        </ol>
        """
        
        intro_label = QLabel(intro_text)
        intro_label.setWordWrap(True)
        intro_label.setTextFormat(Qt.RichText)
        intro_layout.addWidget(intro_label)
        
        tab_widget.addTab(intro_tab, "🎯 مقدمه")
        
        # تب گزارش‌ها
        reports_tab = QWidget()
        reports_layout = QVBoxLayout(reports_tab)
        
        reports_text = """
        <h2>📊 انواع گزارش‌ها</h2>
        
        <table border="1" cellpadding="8" style="border-collapse: collapse; width: 100%;">
            <tr style="background-color: #2c3e50; color: white;">
                <th>گزارش</th>
                <th>توضیحات</th>
                <th>کاربرد</th>
            </tr>
            <tr>
                <td><b>📊 داشبورد</b></td>
                <td>نمای کلی از وضعیت تعمیرگاه</td>
                <td>مدیریت سریع و تصمیم‌گیری</td>
            </tr>
            <tr>
                <td><b>📅 روزانه</b></td>
                <td>فعالیت‌های روز جاری</td>
                <td>پیگیری کارهای روزانه</td>
            </tr>
            <tr>
                <td><b>💰 مالی</b></td>
                <td>درآمد، هزینه، سود، حساب‌ها</td>
                <td>مدیریت مالی و حسابداری</td>
            </tr>
            <tr>
                <td><b>🛒 فروش</b></td>
                <td>آمار فروش، محصولات پرفروش، مشتریان برتر</td>
                <td>تحلیل بازار و فروش</td>
            </tr>
            <tr>
                <td><b>📦 انبار</b></td>
                <td>موجودی ۴ انبار، هشدارهای موجودی کم</td>
                <td>مدیریت انبار و موجودی</td>
            </tr>
            <tr>
                <td><b>🔧 تعمیرات</b></td>
                <td>آمار تعمیرات، تحلیل تعمیرکاران، علل خرابی</td>
                <td>بهبود کیفیت خدمات</td>
            </tr>
            <tr>
                <td><b>👥 مشتریان</b></td>
                <td>تحلیل مشتریان، وفاداری، RFM</td>
                <td>مدیریت ارتباط با مشتریان</td>
            </tr>
        </table>
        
        <h3>🎯 نکات مهم:</h3>
        <ul>
            <li>گزارش <b>داشبورد</b> برای نگاه سریع به وضعیت کلی مناسب است</li>
            <li>گزارش <b>مالی</b> برای تحلیل دقیق درآمد و هزینه استفاده می‌شود</li>
            <li>گزارش <b>انبار</b> هشدارهای موجودی کم را به صورت خودکار نمایش می‌دهد</li>
            <li>گزارش <b>مشتریان</b> به شناسایی مشتریان وفادار کمک می‌کند</li>
        </ul>
        """
        
        reports_label = QLabel(reports_text)
        reports_label.setWordWrap(True)
        reports_label.setTextFormat(Qt.RichText)
        reports_layout.addWidget(reports_label)
        
        tab_widget.addTab(reports_tab, "📊 گزارش‌ها")
        
        # تب خروجی‌ها
        export_tab = QWidget()
        export_layout = QVBoxLayout(export_tab)
        
        export_text = """
        <h2>📤 سیستم خروجی‌گیری</h2>
        
        <h3>📊 خروجی Excel:</h3>
        <ul>
            <li><b>قالب حرفه‌ای:</b> با فرمت‌بندی و رنگ‌بندی</li>
            <li><b>چندین برگه:</b> هر گزارش در برگه جداگانه</li>
            <li><b>پشتیبانی از نمودار:</b> در صورت فعال بودن تنظیمات</li>
            <li><b>فشرده‌سازی:</b> حجم فایل بهینه می‌شود</li>
        </ul>
        
        <h3>📄 خروجی PDF:</h3>
        <ul>
            <li><b>کیفیت بالا:</b> مناسب برای چاپ و ارسال</li>
            <li><b>سربرگ اختصاصی:</b> شامل لوگو و اطلاعات شرکت</li>
            <li><b>رمزگذاری:</b> در صورت نیاز امنیتی</li>
            <li><b>پشتیبانی از راست‌چین:</b> کاملاً فارسی</li>
        </ul>
        
               <h3>🖨️ چاپ مستقیم:</h3>
        <ul>
            <li><b>پیش‌نمایش چاپ:</b> قبل از چاپ مشاهده کنید</li>
            <li><b>تنظیمات حاشیه:</b> قابل تنظیم بر اساس میلیمتر</li>
            <li><b>چاپ سیاه و سفید:</b> برای صرفه‌جویی در جوهر</li>
            <li><b>چندین کپی:</b> امکان چاپ چندین نسخه</li>
        </ul>
        
        <h3>🎯 نکات خروجی:</h3>
        <ul>
            <li>فایل‌های Excel در مسیر پیش‌فرض یا انتخابی ذخیره می‌شوند</li>
            <li>فایل‌های PDF با کیفیت بالا برای چاپ حرفه‌ای مناسب هستند</li>
            <li>می‌توانید قبل از چاپ، پیش‌نمایش را مشاهده کنید</li>
            <li>از منوی "تنظیمات" می‌توانید فرمت خروجی‌ها را تغییر دهید</li>
        </ul>
        """
        
        export_label = QLabel(export_text)
        export_label.setWordWrap(True)
        export_label.setTextFormat(Qt.RichText)
        export_layout.addWidget(export_label)
        
        tab_widget.addTab(export_tab, "📤 خروجی‌ها")
        
        # تب تنظیمات
        settings_tab = QWidget()
        settings_layout = QVBoxLayout(settings_tab)
        
        settings_text = """
        <h2>⚙️ تنظیمات پیشرفته</h2>
        
        <h3>💾 سیستم کش:</h3>
        <ul>
            <li><b>فعال‌سازی کش:</b> افزایش سرعت لود گزارش‌های تکراری</li>
            <li><b>اندازه کش:</b> تعداد گزارش‌های ذخیره شده در حافظه</li>
            <li><b>زمان انقضا:</b> مدت اعتبار گزارش‌های کش شده</li>
            <li><b>پاک کردن کش:</b> در صورت مشاهده داده‌های قدیمی</li>
        </ul>
        
        <h3>📈 تنظیمات نمایش:</h3>
        <ul>
            <li><b>فونت گزارش‌ها:</b> انتخاب فونت فارسی مناسب</li>
            <li><b>تم رنگی:</b> تاریک، روشن یا خودکار</li>
            <li><b>نمایش تومان:</b> تبدیل خودکار ریال به تومان</li>
            <li><b>تعداد ردیف جداول:</b> محدودیت نمایش در هر صفحه</li>
        </ul>
        
        <h3>🔄 بروزرسانی خودکار:</h3>
        <ul>
            <li><b>فاصله بروزرسانی:</b> از ۱ تا ۶۰ دقیقه قابل تنظیم است</li>
            <li><b>حالت بلادرنگ:</b> در صورت نیاز به داده‌های لحظه‌ای</li>
            <li><b>مصرف منابع:</b> در حالت خودکار بهینه‌سازی شده است</li>
        </ul>
        
        <h3>🎯 نکات تنظیمات:</h3>
        <ul>
            <li>تغییرات تنظیمات بلافاصله اعمال می‌شوند</li>
            <li>می‌توانید به تنظیمات پیش‌فرض بازگردید</li>
            <li>تنظیمات در حافظه سیستم ذخیره می‌شوند</li>
            <li>برای عملکرد بهتر، کش را فعال نگه دارید</li>
        </ul>
        """
        
        settings_label = QLabel(settings_text)
        settings_label.setWordWrap(True)
        settings_label.setTextFormat(Qt.RichText)
        settings_layout.addWidget(settings_label)
        
        tab_widget.addTab(settings_tab, "⚙️ تنظیمات")
        
        # تب عیب‌یابی
        troubleshooting_tab = QWidget()
        troubleshooting_layout = QVBoxLayout(troubleshooting_tab)
        
        troubleshooting_text = """
        <h2>🔧 راهنمای عیب‌یابی</h2>
        
        <h3>❌ مشکلات رایج و راه‌حل‌ها:</h3>
        
        <table border="1" cellpadding="8" style="border-collapse: collapse; width: 100%;">
            <tr style="background-color: #2c3e50; color: white;">
                <th>مشکل</th>
                <th>علت احتمالی</th>
                <th>راه‌حل</th>
            </tr>
            <tr>
                <td>گزارش لود نمی‌شود</td>
                <td>اتصال به دیتابیس قطع شده</td>
                <td>اتصال اینترنت/دیتابیس را بررسی کنید</td>
            </tr>
            <tr>
                <td>داده‌ها قدیمی هستند</td>
                <td>کش فعال است و داده‌های جدید لود نشده</td>
                <td>کش را پاک کنید یا بروزرسانی دستی انجام دهید</td>
            </tr>
            <tr>
                <td>خروجی Excel ایجاد نمی‌شود</td>
                <td>کتابخانه pandas نصب نیست</td>
                <td>دستور pip install pandas را اجرا کنید</td>
            </tr>
            <tr>
                <td>چاپ درست عمل نمی‌کند</td>
                <td>درایور چاپگر یا تنظیمات چاپ</td>
                <td>چاپگر را تست کنید و تنظیمات را بررسی نمایید</td>
            </tr>
            <tr>
                <td>سیستم کند است</td>
                <td>داده‌های زیاد یا کش پر</td>
                <td>فیلترها را محدود کنید و کش را پاک کنید</td>
            </tr>
        </table>
        
        <h3>📞 پشتیبانی:</h3>
        <ul>
            <li><b>مستندات آنلاین:</b> از منوی Help → Documentation</li>
            <li><b>گزارش خطا:</b> خطاها را در بخش Issue Tracking ثبت کنید</li>
            <li><b>آپدیت سیستم:</b> آخرین نسخه را از سایت دریافت کنید</li>
            <li><b>تماس با پشتیبانی:</b> support@repairshop.com</li>
        </ul>
        """
        
        troubleshooting_label = QLabel(troubleshooting_text)
        troubleshooting_label.setWordWrap(True)
        troubleshooting_label.setTextFormat(Qt.RichText)
        troubleshooting_layout.addWidget(troubleshooting_label)
        
        tab_widget.addTab(troubleshooting_tab, "🔧 عیب‌یابی")
        
        layout.addWidget(tab_widget)
        
        # دکمه‌های پایین
        button_layout = QHBoxLayout()
        
        btn_close = QPushButton("✅ بستن راهنما")
        btn_close.clicked.connect(dialog.accept)
        
        btn_docs = QPushButton("📚 بازکردن مستندات کامل")
        btn_docs.clicked.connect(lambda: QDesktopServices.openUrl(QUrl("https://docs.repairshop.com/reports")))
        
        button_layout.addWidget(btn_docs)
        button_layout.addStretch()
        button_layout.addWidget(btn_close)
        
        layout.addLayout(button_layout)
        
        dialog.exec()
    
    @staticmethod
    def show_tooltip(widget, text):
        """نمایش راهنمای ابزار برای ویجت"""
        widget.setToolTip(text)
        widget.setToolTipDuration(5000)  # 5 ثانیه
    
    @staticmethod
    def create_context_menu(parent):
        """ایجاد منوی راست کلیک برای راهنما"""
        menu = QMenu(parent)
        
        action_help = menu.addAction("❓ راهنمای این بخش")
        action_help.setIcon(parent.style().standardIcon(QStyle.SP_MessageBoxInformation))
        
        menu.addSeparator()
        
        action_settings = menu.addAction("⚙️ تنظیمات گزارش‌گیری")
        action_quick_start = menu.addAction("🚀 راهنمای شروع سریع")
        
        return menu