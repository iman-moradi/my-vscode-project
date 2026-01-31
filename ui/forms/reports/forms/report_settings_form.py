# ui/forms/reports/forms/report_settings_form.py
"""
فرم تنظیمات گزارش‌گیری
"""

from PySide6.QtWidgets import *
from PySide6.QtCore import Qt, Signal, QSettings
from PySide6.QtGui import QFont, QColor


class ReportSettingsForm(QWidget):
    """فرم تنظیمات گزارش‌گیری"""
    
    settings_changed = Signal(dict)
    
    def __init__(self, data_manager):
        super().__init__()
        self.data_manager = data_manager
        self.settings = QSettings("RepairShop", "Reports")
        
        self.setup_ui()
        self.load_settings()
    
    def setup_ui(self):
        """تنظیم رابط کاربری"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        
        # هدر
        header_label = QLabel("⚙️ تنظیمات گزارش‌گیری")
        header_label.setStyleSheet("""
            QLabel {
                color: #3498db;
                font-size: 18pt;
                font-weight: bold;
                padding: 10px;
                background-color: #1a1a2e;
                border-radius: 8px;
                text-align: center;
            }
        """)
        header_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(header_label)
        
        # ایجاد تب‌های تنظیمات
        tab_widget = QTabWidget()
        tab_widget.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #444;
                background-color: #111;
                border-radius: 5px;
            }
            QTabBar::tab {
                background-color: #2c3e50;
                color: white;
                padding: 10px 20px;
                margin-right: 2px;
                border-top-left-radius: 5px;
                border-top-right-radius: 5px;
                font-weight: bold;
            }
            QTabBar::tab:selected {
                background-color: #3498db;
                color: white;
            }
            QTabBar::tab:hover:!selected {
                background-color: #34495e;
            }
        """)
        
        # تب تنظیمات عمومی
        general_tab = self.create_general_tab()
        tab_widget.addTab(general_tab, "📊 عمومی")
        
        # تب تنظیمات خروجی
        export_tab = self.create_export_tab()
        tab_widget.addTab(export_tab, "📤 خروجی")
        
        # تب تنظیمات چاپ
        print_tab = self.create_print_tab()
        tab_widget.addTab(print_tab, "🖨️ چاپ")
        
        # تب بهینه‌سازی
        performance_tab = self.create_performance_tab()
        tab_widget.addTab(performance_tab, "⚡ عملکرد")
        
        main_layout.addWidget(tab_widget, 1)
        
        # دکمه‌های پایین
        button_layout = QHBoxLayout()
        
        btn_save = QPushButton("💾 ذخیره تنظیمات")
        btn_save.setStyleSheet("""
            QPushButton {
                background-color: #2ecc71;
                color: white;
                border: none;
                padding: 12px 25px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 11pt;
            }
            QPushButton:hover {
                background-color: #27ae60;
            }
        """)
        btn_save.clicked.connect(self.save_settings)
        
        btn_reset = QPushButton("🔄 بازنشانی")
        btn_reset.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                padding: 12px 25px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 11pt;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        btn_reset.clicked.connect(self.reset_to_defaults)
        
        btn_close = QPushButton("❌ بستن")
        btn_close.setStyleSheet("""
            QPushButton {
                background-color: #95a5a6;
                color: white;
                border: none;
                padding: 12px 25px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 11pt;
            }
            QPushButton:hover {
                background-color: #7f8c8d;
            }
        """)
        btn_close.clicked.connect(self.close)
        
        button_layout.addWidget(btn_save)
        button_layout.addWidget(btn_reset)
        button_layout.addStretch()
        button_layout.addWidget(btn_close)
        
        main_layout.addLayout(button_layout)
    
    def create_general_tab(self):
        """ایجاد تب تنظیمات عمومی"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(15)
        
        # گروه تنظیمات نمایش
        display_group = QGroupBox("🎨 تنظیمات نمایش")
        display_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #3498db;
                border-radius: 8px;
                padding-top: 15px;
                color: #3498db;
                font-size: 12pt;
            }
        """)
        
        display_layout = QFormLayout(display_group)
        
        # فونت گزارش‌ها
        self.font_combo = QComboBox()
        self.font_combo.addItems(['B Nazanin', 'Tahoma', 'Arial', 'Times New Roman'])
        display_layout.addRow("فونت گزارش‌ها:", self.font_combo)
        
        # اندازه فونت
        self.font_size_spin = QSpinBox()
        self.font_size_spin.setRange(8, 16)
        self.font_size_spin.setValue(10)
        display_layout.addRow("اندازه فونت:", self.font_size_spin)
        
        # تم رنگی
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(['تاریک', 'روشن', 'خودکار'])
        display_layout.addRow("تم رنگی:", self.theme_combo)
        
        # تاریخ پیش‌فرض
        self.default_period_combo = QComboBox()
        self.default_period_combo.addItems([
            'امروز',
            'دیروز',
            'هفته جاری',
            'ماه جاری',
            '۳ ماه اخیر'
        ])
        display_layout.addRow("دوره پیش‌فرض:", self.default_period_combo)
        
        layout.addWidget(display_group)
        
        # گروه تنظیمات داده
        data_group = QGroupBox("📊 تنظیمات داده")
        data_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #2ecc71;
                border-radius: 8px;
                padding-top: 15px;
                color: #2ecc71;
                font-size: 12pt;
            }
        """)
        
        data_layout = QFormLayout(data_group)
        
        # تعداد ردیف در جداول
        self.table_rows_spin = QSpinBox()
        self.table_rows_spin.setRange(10, 100)
        self.table_rows_spin.setValue(20)
        data_layout.addRow("تعداد ردیف در جداول:", self.table_rows_spin)
        
        # نمایش ارقام به تومان
        self.show_in_toman_check = QCheckBox("نمایش تمام مبالغ به تومان")
        self.show_in_toman_check.setChecked(True)
        data_layout.addRow(self.show_in_toman_check)
        
        # رفرش خودکار
        self.auto_refresh_check = QCheckBox("بروزرسانی خودکار داده‌ها")
        self.auto_refresh_check.setChecked(False)
        data_layout.addRow(self.auto_refresh_check)
        
        # فاصله رفرش خودکار
        self.refresh_interval_spin = QSpinBox()
        self.refresh_interval_spin.setRange(1, 60)
        self.refresh_interval_spin.setValue(5)
        self.refresh_interval_spin.setSuffix(" دقیقه")
        data_layout.addRow("فاصله بروزرسانی:", self.refresh_interval_spin)
        
        layout.addWidget(data_group)
        layout.addStretch()
        
        return tab
    
    def create_export_tab(self):
        """ایجاد تب تنظیمات خروجی"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(15)
        
        # گروه تنظیمات Excel
        excel_group = QGroupBox("📊 تنظیمات خروجی Excel")
        excel_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #27ae60;
                border-radius: 8px;
                padding-top: 15px;
                color: #27ae60;
                font-size: 12pt;
            }
        """)
        
        excel_layout = QFormLayout(excel_group)
        
        # قالب پیش‌فرض Excel
        self.excel_template_combo = QComboBox()
        self.excel_template_combo.addItems(['ساده', 'حرفه‌ای', 'رنگی'])
        excel_layout.addRow("قالب Excel:", self.excel_template_combo)
        
        # شامل نمودارها
        self.include_charts_check = QCheckBox("شامل نمودارها در خروجی Excel")
        self.include_charts_check.setChecked(True)
        excel_layout.addRow(self.include_charts_check)
        
        # فشرده‌سازی
        self.compress_excel_check = QCheckBox("فشرده‌سازی فایل Excel")
        self.compress_excel_check.setChecked(True)
        excel_layout.addRow(self.compress_excel_check)
        
        # مسیر پیش‌فرض ذخیره
        self.default_save_path_edit = QLineEdit()
        self.default_save_path_edit.setPlaceholderText("انتخاب نشده")
        excel_layout.addRow("مسیر ذخیره پیش‌فرض:", self.default_save_path_edit)
        
        btn_browse = QPushButton("انتخاب مسیر")
        btn_browse.clicked.connect(self.browse_save_path)
        excel_layout.addRow("", btn_browse)
        
        layout.addWidget(excel_group)
        
        # گروه تنظیمات PDF
        pdf_group = QGroupBox("📄 تنظیمات خروجی PDF")
        pdf_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #e74c3c;
                border-radius: 8px;
                padding-top: 15px;
                color: #e74c3c;
                font-size: 12pt;
            }
        """)
        
        pdf_layout = QFormLayout(pdf_group)
        
        # کیفیت PDF
        self.pdf_quality_combo = QComboBox()
        self.pdf_quality_combo.addItems(['استاندارد', 'بالا', 'چاپ'])
        pdf_layout.addRow("کیفیت PDF:", self.pdf_quality_combo)
        
        # جهت صفحه
        self.pdf_orientation_combo = QComboBox()
        self.pdf_orientation_combo.addItems(['عمودی', 'افقی'])
        pdf_layout.addRow("جهت صفحه:", self.pdf_orientation_combo)
        
        # شامل هدر و فوتر
        self.include_header_footer_check = QCheckBox("شامل هدر و فوتر در PDF")
        self.include_header_footer_check.setChecked(True)
        pdf_layout.addRow(self.include_header_footer_check)
        
        # رمزگذاری PDF
        self.encrypt_pdf_check = QCheckBox("رمزگذاری فایل‌های PDF")
        self.encrypt_pdf_check.setChecked(False)
        pdf_layout.addRow(self.encrypt_pdf_check)
        
        layout.addWidget(pdf_group)
        layout.addStretch()
        
        return tab
    
    def create_print_tab(self):
        """ایجاد تب تنظیمات چاپ"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(15)
        
        # گروه تنظیمات چاپ
        print_group = QGroupBox("🖨️ تنظیمات چاپ")
        print_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #f39c12;
                border-radius: 8px;
                padding-top: 15px;
                color: #f39c12;
                font-size: 12pt;
            }
        """)
        
        print_layout = QFormLayout(print_group)
        
        # اندازه کاغذ
        self.paper_size_combo = QComboBox()
        self.paper_size_combo.addItems(['A4', 'A5', 'A3', 'Letter'])
        print_layout.addRow("اندازه کاغذ:", self.paper_size_combo)
        
        # حاشیه‌ها
        self.margin_spin = QSpinBox()
        self.margin_spin.setRange(5, 50)
        self.margin_spin.setValue(15)
        self.margin_spin.setSuffix(" mm")
        print_layout.addRow("حاشیه‌ها:", self.margin_spin)
        
        # جهت چاپ
        self.print_orientation_combo = QComboBox()
        self.print_orientation_combo.addItems(['عمودی', 'افقی'])
        print_layout.addRow("جهت چاپ:", self.print_orientation_combo)
        
        # نمایش پیش‌نمایش قبل از چاپ
        self.show_preview_check = QCheckBox("نمایش پیش‌نمایش قبل از چاپ")
        self.show_preview_check.setChecked(True)
        print_layout.addRow(self.show_preview_check)
        
        # چاپ به صورت سیاه و سفید
        self.print_bw_check = QCheckBox("چاپ سیاه و سفید")
        self.print_bw_check.setChecked(False)
        print_layout.addRow(self.print_bw_check)
        
        layout.addWidget(print_group)
        
        # گروه تنظیمات سربرگ
        header_group = QGroupBox("🏢 تنظیمات سربرگ گزارش")
        header_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #9b59b6;
                border-radius: 8px;
                padding-top: 15px;
                color: #9b59b6;
                font-size: 12pt;
            }
        """)
        
        header_layout = QFormLayout(header_group)
        
        # نام شرکت
        self.company_name_edit = QLineEdit()
        self.company_name_edit.setPlaceholderText("نام شرکت/تعمیرگاه")
        header_layout.addRow("نام شرکت:", self.company_name_edit)
        
        # لوگوی شرکت
        self.company_logo_edit = QLineEdit()
        self.company_logo_edit.setPlaceholderText("مسیر فایل لوگو")
        header_layout.addRow("لوگوی شرکت:", self.company_logo_edit)
        
        btn_browse_logo = QPushButton("انتخاب لوگو")
        btn_browse_logo.clicked.connect(self.browse_logo)
        header_layout.addRow("", btn_browse_logo)
        
        # شامل لوگو در گزارش‌ها
        self.include_logo_check = QCheckBox("شامل لوگو در گزارش‌ها")
        self.include_logo_check.setChecked(True)
        header_layout.addRow(self.include_logo_check)
        
        layout.addWidget(header_group)
        layout.addStretch()
        
        return tab
    
    def create_performance_tab(self):
        """ایجاد تب بهینه‌سازی"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(15)
        
        # گروه تنظیمات کش
        cache_group = QGroupBox("💾 تنظیمات کش")
        cache_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #1abc9c;
                border-radius: 8px;
                padding-top: 15px;
                color: #1abc9c;
                font-size: 12pt;
            }
        """)
        
        cache_layout = QFormLayout(cache_group)
        
        # فعال‌سازی کش
        self.enable_cache_check = QCheckBox("فعال‌سازی سیستم کش")
        self.enable_cache_check.setChecked(True)
        cache_layout.addRow(self.enable_cache_check)
        
        # اندازه کش
        self.cache_size_spin = QSpinBox()
        self.cache_size_spin.setRange(1, 50)
        self.cache_size_spin.setValue(10)
        self.cache_size_spin.setSuffix(" گزارش")
        cache_layout.addRow("حداکثر اندازه کش:", self.cache_size_spin)
        
        # زمان انقضای کش
        self.cache_ttl_spin = QSpinBox()
        self.cache_ttl_spin.setRange(1, 60)
        self.cache_ttl_spin.setValue(5)
        self.cache_ttl_spin.setSuffix(" دقیقه")
        cache_layout.addRow("زمان انقضای کش:", self.cache_ttl_spin)
        
        # دکمه پاک کردن کش
        btn_clear_cache = QPushButton("پاک کردن کش")
        btn_clear_cache.clicked.connect(self.clear_cache)
        cache_layout.addRow("", btn_clear_cache)
        
        layout.addWidget(cache_group)
        
        # گروه تنظیمات پرس‌وجو
        query_group = QGroupBox("📋 تنظیمات پرس‌وجو")
        query_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #e67e22;
                border-radius: 8px;
                padding-top: 15px;
                color: #e67e22;
                font-size: 12pt;
            }
        """)
        
        query_layout = QFormLayout(query_group)
        
        # محدودیت تعداد ردیف
        self.query_limit_spin = QSpinBox()
        self.query_limit_spin.setRange(100, 10000)
        self.query_limit_spin.setValue(1000)
        query_layout.addRow("حداکثر ردیف در پرس‌وجو:", self.query_limit_spin)
        
        # تایم‌اوت پرس‌وجو
        self.query_timeout_spin = QSpinBox()
        self.query_timeout_spin.setRange(5, 60)
        self.query_timeout_spin.setValue(30)
        self.query_timeout_spin.setSuffix(" ثانیه")
        query_layout.addRow("تایم‌اوت پرس‌وجو:", self.query_timeout_spin)
        
        # استفاده از ایندکس
        self.use_indexes_check = QCheckBox("استفاده از ایندکس‌های دیتابیس")
        self.use_indexes_check.setChecked(True)
        query_layout.addRow(self.use_indexes_check)
        
        layout.addWidget(query_group)
        
        # گروه اطلاعات عملکرد
        perf_group = QGroupBox("📈 آمار عملکرد")
        perf_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #34495e;
                border-radius: 8px;
                padding-top: 15px;
                color: #34495e;
                font-size: 12pt;
            }
        """)
        
        perf_layout = QVBoxLayout(perf_group)
        
        # نمایش آمار
        self.stats_text = QTextEdit()
        self.stats_text.setReadOnly(True)
        self.stats_text.setMaximumHeight(150)
        self.stats_text.setStyleSheet("""
            QTextEdit {
                background-color: #2c3e50;
                color: #ecf0f1;
                border: 1px solid #4a6278;
                border-radius: 4px;
                padding: 8px;
                font-family: monospace;
            }
        """)
        
        perf_layout.addWidget(self.stats_text)
        
        # دکمه بروزرسانی آمار
        btn_refresh_stats = QPushButton("🔄 بروزرسانی آمار عملکرد")
        btn_refresh_stats.clicked.connect(self.refresh_performance_stats)
        perf_layout.addWidget(btn_refresh_stats)
        
        layout.addWidget(perf_group)
        layout.addStretch()
        
        return tab
    
    def browse_save_path(self):
        """انتخاب مسیر ذخیره"""
        path = QFileDialog.getExistingDirectory(
            self,
            "انتخاب مسیر ذخیره پیش‌فرض",
            self.default_save_path_edit.text()
        )
        
        if path:
            self.default_save_path_edit.setText(path)
    
    def browse_logo(self):
        """انتخاب لوگو"""
        path, _ = QFileDialog.getOpenFileName(
            self,
            "انتخاب لوگوی شرکت",
            "",
            "Image Files (*.png *.jpg *.jpeg *.bmp);;All Files (*)"
        )
        
        if path:
            self.company_logo_edit.setText(path)
    
    def clear_cache(self):
        """پاک کردن کش"""
        try:
            from ui.forms.reports.utils.optimizations import ReportCache
            cache = ReportCache()
            cache.clear()
            QMessageBox.information(self, "✅ موفق", "کش گزارش‌ها پاک شد.")
        except Exception as e:
            QMessageBox.warning(self, "⚠️ خطا", f"خطا در پاک کردن کش: {str(e)}")
    
    def refresh_performance_stats(self):
        """بروزرسانی آمار عملکرد"""
        try:
            from ui.forms.reports.utils.optimizations import PerformanceMonitor
            monitor = PerformanceMonitor()
            stats = monitor.get_stats()
            
            stats_text = f"""
📊 آمار عملکرد سیستم گزارش‌گیری:

💾 وضعیت کش:
  - تعداد Hit: {stats.get('total_cache_hits', 0)}
  - تعداد Miss: {stats.get('total_cache_misses', 0)}
  - نرخ Hit: {stats.get('cache_hit_rate', 0):.1f}%

⏱️ میانگین زمان لود:
"""
            
            for report_type, avg_time in stats.get('avg_load_times', {}).items():
                stats_text += f"  - {report_type}: {avg_time:.2f} ثانیه\n"
            
            stats_text += f"""
📋 تعداد پرس‌وجوها:
"""
            
            for query_type, count in stats.get('query_counts', {}).items():
                stats_text += f"  - {query_type}: {count}\n"
            
            self.stats_text.setText(stats_text)
            
        except Exception as e:
            self.stats_text.setText(f"❌ خطا در دریافت آمار: {str(e)}")
    
    def load_settings(self):
        """بارگذاری تنظیمات ذخیره شده"""
        try:
            # تنظیمات عمومی
            self.font_combo.setCurrentText(
                self.settings.value("report/font", "B Nazanin")
            )
            self.font_size_spin.setValue(
                int(self.settings.value("report/font_size", 10))
            )
            self.theme_combo.setCurrentText(
                self.settings.value("report/theme", "تاریک")
            )
            self.default_period_combo.setCurrentText(
                self.settings.value("report/default_period", "ماه جاری")
            )
            
            # تنظیمات داده
            self.table_rows_spin.setValue(
                int(self.settings.value("report/table_rows", 20))
            )
            self.show_in_toman_check.setChecked(
                self.settings.value("report/show_in_toman", True, type=bool)
            )
            self.auto_refresh_check.setChecked(
                self.settings.value("report/auto_refresh", False, type=bool)
            )
            self.refresh_interval_spin.setValue(
                int(self.settings.value("report/refresh_interval", 5))
            )
            
            # تنظیمات Excel
            self.excel_template_combo.setCurrentText(
                self.settings.value("export/excel_template", "حرفه‌ای")
            )
            self.include_charts_check.setChecked(
                self.settings.value("export/include_charts", True, type=bool)
            )
            self.compress_excel_check.setChecked(
                self.settings.value("export/compress_excel", True, type=bool)
            )
            self.default_save_path_edit.setText(
                self.settings.value("export/default_path", "")
            )
            
            # تنظیمات PDF
            self.pdf_quality_combo.setCurrentText(
                self.settings.value("export/pdf_quality", "استاندارد")
            )
            self.pdf_orientation_combo.setCurrentText(
                self.settings.value("export/pdf_orientation", "عمودی")
            )
            self.include_header_footer_check.setChecked(
                self.settings.value("export/include_header_footer", True, type=bool)
            )
            self.encrypt_pdf_check.setChecked(
                self.settings.value("export/encrypt_pdf", False, type=bool)
            )
            
            # تنظیمات چاپ
            self.paper_size_combo.setCurrentText(
                self.settings.value("print/paper_size", "A4")
            )
            self.margin_spin.setValue(
                int(self.settings.value("print/margin", 15))
            )
            self.print_orientation_combo.setCurrentText(
                self.settings.value("print/orientation", "عمودی")
            )
            self.show_preview_check.setChecked(
                self.settings.value("print/show_preview", True, type=bool)
            )
            self.print_bw_check.setChecked(
                self.settings.value("print/black_white", False, type=bool)
            )
            
            # تنظیمات سربرگ
            self.company_name_edit.setText(
                self.settings.value("header/company_name", "")
            )
            self.company_logo_edit.setText(
                self.settings.value("header/company_logo", "")
            )
            self.include_logo_check.setChecked(
                self.settings.value("header/include_logo", True, type=bool)
            )
            
            # تنظیمات عملکرد
            self.enable_cache_check.setChecked(
                self.settings.value("performance/enable_cache", True, type=bool)
            )
            self.cache_size_spin.setValue(
                int(self.settings.value("performance/cache_size", 10))
            )
            self.cache_ttl_spin.setValue(
                int(self.settings.value("performance/cache_ttl", 5))
            )
            self.query_limit_spin.setValue(
                int(self.settings.value("performance/query_limit", 1000))
            )
            self.query_timeout_spin.setValue(
                int(self.settings.value("performance/query_timeout", 30))
            )
            self.use_indexes_check.setChecked(
                self.settings.value("performance/use_indexes", True, type=bool)
            )
            
        except Exception as e:
            print(f"⚠️ خطا در بارگذاری تنظیمات: {e}")
    
    def save_settings(self):
        """ذخیره تنظیمات"""
        try:
            # تنظیمات عمومی
            self.settings.setValue("report/font", self.font_combo.currentText())
            self.settings.setValue("report/font_size", self.font_size_spin.value())
            self.settings.setValue("report/theme", self.theme_combo.currentText())
            self.settings.setValue("report/default_period", self.default_period_combo.currentText())
            
            # تنظیمات داده
            self.settings.setValue("report/table_rows", self.table_rows_spin.value())
            self.settings.setValue("report/show_in_toman", self.show_in_toman_check.isChecked())
            self.settings.setValue("report/auto_refresh", self.auto_refresh_check.isChecked())
            self.settings.setValue("report/refresh_interval", self.refresh_interval_spin.value())
            
            # تنظیمات Excel
            self.settings.setValue("export/excel_template", self.excel_template_combo.currentText())
            self.settings.setValue("export/include_charts", self.include_charts_check.isChecked())
            self.settings.setValue("export/compress_excel", self.compress_excel_check.isChecked())
            self.settings.setValue("export/default_path", self.default_save_path_edit.text())
            
            # تنظیمات PDF
            self.settings.setValue("export/pdf_quality", self.pdf_quality_combo.currentText())
            self.settings.setValue("export/pdf_orientation", self.pdf_orientation_combo.currentText())
            self.settings.setValue("export/include_header_footer", self.include_header_footer_check.isChecked())
            self.settings.setValue("export/encrypt_pdf", self.encrypt_pdf_check.isChecked())
            
            # تنظیمات چاپ
            self.settings.setValue("print/paper_size", self.paper_size_combo.currentText())
            self.settings.setValue("print/margin", self.margin_spin.value())
            self.settings.setValue("print/orientation", self.print_orientation_combo.currentText())
            self.settings.setValue("print/show_preview", self.show_preview_check.isChecked())
            self.settings.setValue("print/black_white", self.print_bw_check.isChecked())
            
            # تنظیمات سربرگ
            self.settings.setValue("header/company_name", self.company_name_edit.text())
            self.settings.setValue("header/company_logo", self.company_logo_edit.text())
            self.settings.setValue("header/include_logo", self.include_logo_check.isChecked())
            
            # تنظیمات عملکرد
            self.settings.setValue("performance/enable_cache", self.enable_cache_check.isChecked())
            self.settings.setValue("performance/cache_size", self.cache_size_spin.value())
            self.settings.setValue("performance/cache_ttl", self.cache_ttl_spin.value())
            self.settings.setValue("performance/query_limit", self.query_limit_spin.value())
            self.settings.setValue("performance/query_timeout", self.query_timeout_spin.value())
            self.settings.setValue("performance/use_indexes", self.use_indexes_check.isChecked())
            
            # ارسال سیگنال
            settings_dict = self.get_current_settings()
            self.settings_changed.emit(settings_dict)
            
            QMessageBox.information(self, "✅ موفق", "تنظیمات با موفقیت ذخیره شدند.")
            
        except Exception as e:
            QMessageBox.critical(self, "❌ خطا", f"خطا در ذخیره تنظیمات: {str(e)}")
    
    def reset_to_defaults(self):
        """بازنشانی به تنظیمات پیش‌فرض"""
        reply = QMessageBox.question(
            self,
            "بازنشانی تنظیمات",
            "آیا مطمئن هستید که می‌خواهید تمام تنظیمات به حالت پیش‌فرض بازنشانی شوند؟",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # پاک کردن تمام تنظیمات
            self.settings.clear()
            
            # بارگذاری مجدد تنظیمات پیش‌فرض
            self.load_settings()
            
            QMessageBox.information(self, "✅ موفق", "تنظیمات به حالت پیش‌فرض بازنشانی شدند.")
    
    def get_current_settings(self):
        """دریافت تنظیمات فعلی به صورت دیکشنری"""
        return {
            'report': {
                'font': self.font_combo.currentText(),
                'font_size': self.font_size_spin.value(),
                'theme': self.theme_combo.currentText(),
                'default_period': self.default_period_combo.currentText(),
                'table_rows': self.table_rows_spin.value(),
                'show_in_toman': self.show_in_toman_check.isChecked(),
                'auto_refresh': self.auto_refresh_check.isChecked(),
                'refresh_interval': self.refresh_interval_spin.value()
            },
            'export': {
                'excel_template': self.excel_template_combo.currentText(),
                'include_charts': self.include_charts_check.isChecked(),
                'compress_excel': self.compress_excel_check.isChecked(),
                'default_path': self.default_save_path_edit.text(),
                'pdf_quality': self.pdf_quality_combo.currentText(),
                'pdf_orientation': self.pdf_orientation_combo.currentText(),
                'include_header_footer': self.include_header_footer_check.isChecked(),
                'encrypt_pdf': self.encrypt_pdf_check.isChecked()
            },
            'print': {
                'paper_size': self.paper_size_combo.currentText(),
                'margin': self.margin_spin.value(),
                'orientation': self.print_orientation_combo.currentText(),
                'show_preview': self.show_preview_check.isChecked(),
                'black_white': self.print_bw_check.isChecked()
            },
            'header': {
                'company_name': self.company_name_edit.text(),
                'company_logo': self.company_logo_edit.text(),
                'include_logo': self.include_logo_check.isChecked()
            },
            'performance': {
                'enable_cache': self.enable_cache_check.isChecked(),
                'cache_size': self.cache_size_spin.value(),
                'cache_ttl': self.cache_ttl_spin.value(),
                'query_limit': self.query_limit_spin.value(),
                'query_timeout': self.query_timeout_spin.value(),
                'use_indexes': self.use_indexes_check.isChecked()
            }
        }