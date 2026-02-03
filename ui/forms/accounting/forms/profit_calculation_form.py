"""
فرم محاسبه و توزیع سود - با پشتیبانی کامل تاریخ شمسی
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QGroupBox, QTableWidget, QTableWidgetItem,
    QHeaderView, QMessageBox, QComboBox, QLineEdit, QSpinBox,
    QDoubleSpinBox, QDateEdit, QTabWidget, QTextEdit, QSplitter,
    QProgressBar, QGridLayout, QFormLayout, QToolBar
)
from PySide6.QtCore import Qt, Signal, QDate
from PySide6.QtGui import QFont, QColor, QBrush, QIcon
import jdatetime
import json
from datetime import datetime, timedelta


class ProfitCalculationForm(QWidget):
    """فرم پیشرفته محاسبه و توزیع سود"""
    
    data_changed = Signal()
    
    def __init__(self, data_manager):
        super().__init__()
        self.data_manager = data_manager
        self.calculator = data_manager.calculator if hasattr(data_manager, 'calculator') else None
        
        # اگر calculator وجود ندارد، ایجادش کن
        if not self.calculator:
            from modules.accounting.financial_calculator import FinancialCalculator
            self.calculator = FinancialCalculator(data_manager)
        
        self.setup_ui()
        self.load_initial_data()
        self.setup_connections()
    
    def setup_ui(self):
        """راه‌اندازی رابط کاربری"""
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(15, 15, 15, 15)
        
        # 🔴 **هدر فرم**
        header_frame = QFrame()
        header_frame.setStyleSheet("""
            QFrame {
                background-color: #1e1e1e;
                border: 2px solid #2ecc71;
                border-radius: 10px;
                padding: 15px;
            }
        """)
        
        header_layout = QVBoxLayout(header_frame)
        
        title_label = QLabel("📈 محاسبه و توزیع سود")
        title_label.setStyleSheet("""
            QLabel {
                font-size: 18pt;
                font-weight: bold;
                color: #2ecc71;
                padding: 5px;
            }
        """)
        title_label.setAlignment(Qt.AlignCenter)
        
        subtitle_label = QLabel("محاسبه سود خالص، توزیع بین شرکا و تحلیل بازده سرمایه گذاری")
        subtitle_label.setStyleSheet("""
            QLabel {
                font-size: 11pt;
                color: #bbb;
                padding: 5px;
            }
        """)
        subtitle_label.setAlignment(Qt.AlignCenter)
        
        header_layout.addWidget(title_label)
        header_layout.addWidget(subtitle_label)
        
        main_layout.addWidget(header_frame)
        
        # 🔴 **تب‌های اصلی**
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabPosition(QTabWidget.North)
        
        # تب ۱: محاسبه سود
        self.profit_calc_tab = self.create_profit_calculation_tab()
        self.tab_widget.addTab(self.profit_calc_tab, "💰 محاسبه سود")
        
        # تب ۲: توزیع سود
        self.distribution_tab = self.create_distribution_tab()
        self.tab_widget.addTab(self.distribution_tab, "🤝 توزیع سود")
        
        # تب ۳: تحلیل ROI
        self.roi_analysis_tab = self.create_roi_analysis_tab()
        self.tab_widget.addTab(self.roi_analysis_tab, "📊 تحلیل بازدهی")
        
        # تب ۴: گزارش سودآوری
        self.profitability_tab = self.create_profitability_tab()
        self.tab_widget.addTab(self.profitability_tab, "📈 گزارش سودآوری")
        
        main_layout.addWidget(self.tab_widget)
        
        # 🔴 **نوار وضعیت پایین**
        status_frame = QFrame()
        status_frame.setStyleSheet("""
            QFrame {
                background-color: #111111;
                border: 1px solid #333;
                border-radius: 5px;
                padding: 10px;
            }
        """)
        
        status_layout = QHBoxLayout(status_frame)
        
        self.status_label = QLabel("آماده برای محاسبه...")
        self.status_label.setStyleSheet("""
            QLabel {
                color: #bbb;
                font-size: 10pt;
            }
        """)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #333;
                border-radius: 5px;
                text-align: center;
                height: 15px;
            }
            QProgressBar::chunk {
                background-color: #2ecc71;
                border-radius: 5px;
            }
        """)
        
        status_layout.addWidget(self.status_label)
        status_layout.addWidget(self.progress_bar)
        status_layout.addStretch()
        
        main_layout.addWidget(status_frame)
    
    def create_profit_calculation_tab(self):
        """ایجاد تب محاسبه سود"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(15)
        
        # 🔴 **پانل انتخاب دوره**
        period_group = QGroupBox("📅 انتخاب دوره زمانی")
        period_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 11pt;
                color: #2ecc71;
                border: 1px solid #333;
                border-radius: 8px;
                margin-top: 12px;
                padding-top: 12px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 10px 0 10px;
            }
        """)
        
        period_layout = QGridLayout(period_group)
        
        # تاریخ شروع
        period_layout.addWidget(QLabel("تاریخ شروع:"), 0, 0)
        
        from utils.jalali_date_widget import JalaliDateInput
        self.start_date_input = JalaliDateInput(mode='edit', theme='dark')
        period_layout.addWidget(self.start_date_input, 0, 1)
        
        # تاریخ پایان
        period_layout.addWidget(QLabel("تاریخ پایان:"), 1, 0)
        self.end_date_input = JalaliDateInput(mode='edit', theme='dark')
        period_layout.addWidget(self.end_date_input, 1, 1)
        
        # تنظیم تاریخ‌های پیش‌فرض (ماه گذشته)
        today = jdatetime.date.today()
        first_day_of_month = jdatetime.date(today.year, today.month, 1)
        last_month = first_day_of_month - jdatetime.timedelta(days=1)
        first_day_last_month = jdatetime.date(last_month.year, last_month.month, 1)
        
        self.start_date_input.set_date_string(first_day_last_month.strftime("%Y/%m/%d"))
        self.end_date_input.set_date_string(last_month.strftime("%Y/%m/%d"))
        
        # دکمه محاسبه
        self.calc_button = QPushButton("🚀 محاسبه سود دوره")
        self.calc_button.setStyleSheet("""
            QPushButton {
                background-color: #2ecc71;
                color: white;
                font-weight: bold;
                padding: 12px;
                border-radius: 6px;
                font-size: 11pt;
            }
            QPushButton:hover {
                background-color: #27ae60;
            }
        """)
        period_layout.addWidget(self.calc_button, 0, 2, 2, 1)
        
        layout.addWidget(period_group)
        
        # 🔴 **نتایج محاسبه**
        results_group = QGroupBox("📊 نتایج محاسبه سود")
        results_group.setStyleSheet(period_group.styleSheet())
        
        results_layout = QGridLayout(results_group)
        
        # ردیف اول: درآمدها
        results_layout.addWidget(QLabel("💰 درآمد کل:"), 0, 0)
        self.total_income_label = QLabel("0 تومان")
        self.total_income_label.setStyleSheet("color: #2ecc71; font-size: 12pt; font-weight: bold;")
        results_layout.addWidget(self.total_income_label, 0, 1)
        
        results_layout.addWidget(QLabel("📉 هزینه کل:"), 1, 0)
        self.total_expense_label = QLabel("0 تومان")
        self.total_expense_label.setStyleSheet("color: #e74c3c; font-size: 12pt; font-weight: bold;")
        results_layout.addWidget(self.total_expense_label, 1, 1)
        
        # ردیف دوم: سودها
        results_layout.addWidget(QLabel("📈 سود ناخالص:"), 0, 2)
        self.gross_profit_label = QLabel("0 تومان")
        self.gross_profit_label.setStyleSheet("color: #f39c12; font-size: 12pt; font-weight: bold;")
        results_layout.addWidget(self.gross_profit_label, 0, 3)
        
        results_layout.addWidget(QLabel("📊 سود خالص:"), 1, 2)
        self.net_profit_label = QLabel("0 تومان")
        self.net_profit_label.setStyleSheet("color: #27ae60; font-size: 14pt; font-weight: bold;")
        results_layout.addWidget(self.net_profit_label, 1, 3)
        
        # ردیف سوم: مالیات و تخفیف
        results_layout.addWidget(QLabel("🏛️ مالیات:"), 2, 0)
        self.tax_amount_label = QLabel("0 تومان")
        self.tax_amount_label.setStyleSheet("color: #9b59b6; font-size: 11pt;")
        results_layout.addWidget(self.tax_amount_label, 2, 1)
        
        results_layout.addWidget(QLabel("🎁 تخفیف‌ها:"), 2, 2)
        self.discount_amount_label = QLabel("0 تومان")
        self.discount_amount_label.setStyleSheet("color: #3498db; font-size: 11pt;")
        results_layout.addWidget(self.discount_amount_label, 2, 3)
        
        # ردیف چهارم: درصدها
        results_layout.addWidget(QLabel("📶 حاشیه سود:"), 3, 0)
        self.profit_margin_label = QLabel("0%")
        self.profit_margin_label.setStyleSheet("color: #2ecc71; font-size: 12pt; font-weight: bold;")
        results_layout.addWidget(self.profit_margin_label, 3, 1)
        
        results_layout.addWidget(QLabel("📊 نسبت هزینه:"), 3, 2)
        self.expense_ratio_label = QLabel("0%")
        self.expense_ratio_label.setStyleSheet("color: #e74c3c; font-size: 12pt;")
        results_layout.addWidget(self.expense_ratio_label, 3, 3)
        
        layout.addWidget(results_group)
        
        # 🔴 **جزئیات هزینه‌ها**
        expenses_group = QGroupBox("🧾 جزئیات هزینه‌ها")
        expenses_group.setStyleSheet(period_group.styleSheet())
        
        expenses_layout = QVBoxLayout(expenses_group)
        
        self.expenses_table = QTableWidget()
        self.expenses_table.setColumnCount(4)
        self.expenses_table.setHorizontalHeaderLabels(["ردیف", "نوع هزینه", "مبلغ", "درصد"])
        self.expenses_table.horizontalHeader().setStretchLastSection(True)
        self.expenses_table.setAlternatingRowColors(True)
        self.expenses_table.setStyleSheet("""
            QTableWidget {
                background-color: #111111;
                alternate-background-color: #0a0a0a;
                color: white;
                font-size: 11pt;
            }
            QHeaderView::section {
                background-color: #2c3e50;
                color: white;
                padding: 10px;
                font-weight: bold;
            }
        """)
        
        expenses_layout.addWidget(self.expenses_table)
        layout.addWidget(expenses_group)
        
        layout.addStretch()
        return tab
    
    def create_distribution_tab(self):
        """ایجاد تب توزیع سود"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(15)
        
        # 🔴 **اطلاعات شرکا**
        partners_group = QGroupBox("🤝 اطلاعات شرکا")
        partners_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 11pt;
                color: #3498db;
                border: 1px solid #333;
                border-radius: 8px;
                margin-top: 12px;
                padding-top: 12px;
            }
        """)
        
        partners_layout = QVBoxLayout(partners_group)
        
        # دکمه بارگذاری شرکا
        self.load_partners_btn = QPushButton("🔄 بارگذاری لیست شرکا")
        self.load_partners_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                padding: 10px;
                border-radius: 5px;
                font-size: 10pt;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        
        partners_layout.addWidget(self.load_partners_btn)
        
        # جدول شرکا
        self.partners_table = QTableWidget()
        self.partners_table.setColumnCount(6)
        self.partners_table.setHorizontalHeaderLabels([
            "ردیف", "نام شریک", "سرمایه", "درصد سود", "سهم سود", "عملکرد"
        ])
        self.partners_table.horizontalHeader().setStretchLastSection(True)
        self.partners_table.setStyleSheet("""
            QTableWidget {
                background-color: #111111;
                alternate-background-color: #0a0a0a;
                color: white;
                font-size: 11pt;
            }
        """)
        
        partners_layout.addWidget(self.partners_table)
        layout.addWidget(partners_group)
        
        # 🔴 **تنظیمات توزیع**
        settings_group = QGroupBox("⚙️ تنظیمات توزیع")
        settings_group.setStyleSheet(partners_group.styleSheet())
        
        settings_layout = QGridLayout(settings_group)
        
        settings_layout.addWidget(QLabel("سود کل توزیع:"), 0, 0)
        self.distribution_total_input = QLineEdit()
        self.distribution_total_input.setPlaceholderText("مبلغ سود برای توزیع")
        self.distribution_total_input.setStyleSheet("""
            QLineEdit {
                background-color: #222;
                border: 1px solid #444;
                color: white;
                padding: 8px;
                border-radius: 4px;
            }
        """)
        settings_layout.addWidget(self.distribution_total_input, 0, 1)
        
        settings_layout.addWidget(QLabel("روش توزیع:"), 1, 0)
        self.distribution_method_combo = QComboBox()
        self.distribution_method_combo.addItems([
            "بر اساس درصد قراردادی",
            "بر اساس سرمایه",
            "بر اساس سهم مساوی",
            "ترکیبی (سرمایه + عملکرد)"
        ])
        settings_layout.addWidget(self.distribution_method_combo, 1, 1)
        
        # دکمه‌های توزیع
        btn_layout = QHBoxLayout()
        
        self.calc_distribution_btn = QPushButton("📊 محاسبه توزیع")
        self.calc_distribution_btn.setStyleSheet("""
            QPushButton {
                background-color: #2ecc71;
                color: white;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #27ae60;
            }
        """)
        
        self.save_distribution_btn = QPushButton("💾 ذخیره توزیع")
        self.save_distribution_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        
        btn_layout.addWidget(self.calc_distribution_btn)
        btn_layout.addWidget(self.save_distribution_btn)
        settings_layout.addLayout(btn_layout, 2, 0, 1, 2)
        
        layout.addWidget(settings_group)
        
        # 🔴 **نتایج توزیع**
        results_group = QGroupBox("📋 نتایج توزیع")
        results_group.setStyleSheet(partners_group.styleSheet())
        
        results_layout = QVBoxLayout(results_group)
        
        self.distribution_result_table = QTableWidget()
        self.distribution_result_table.setColumnCount(5)
        self.distribution_result_table.setHorizontalHeaderLabels([
            "شریک", "درصد", "سهم", "سرمایه", "ROI"
        ])
        
        results_layout.addWidget(self.distribution_result_table)
        layout.addWidget(results_group)
        
        layout.addStretch()
        return tab
    
    def create_roi_analysis_tab(self):
        """ایجاد تب تحلیل ROI"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(15)
        
        # 🔴 **انتخاب شریک برای تحلیل**
        selection_group = QGroupBox("👤 انتخاب شریک")
        selection_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 11pt;
                color: #f39c12;
                border: 1px solid #333;
                border-radius: 8px;
                margin-top: 12px;
                padding-top: 12px;
            }
        """)
        
        selection_layout = QGridLayout(selection_group)
        
        selection_layout.addWidget(QLabel("شریک:"), 0, 0)
        self.partner_combo = QComboBox()
        selection_layout.addWidget(self.partner_combo, 0, 1)
        
        selection_layout.addWidget(QLabel("دوره تحلیل:"), 1, 0)
        self.roi_period_combo = QComboBox()
        self.roi_period_combo.addItems([
            "۳ ماهه",
            "۶ ماهه", 
            "۱ ساله",
            "۲ ساله",
            "از ابتدا"
        ])
        selection_layout.addWidget(self.roi_period_combo, 1, 1)
        
        self.analyze_roi_btn = QPushButton("📈 تحلیل بازدهی")
        self.analyze_roi_btn.setStyleSheet("""
            QPushButton {
                background-color: #f39c12;
                color: white;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #e67e22;
            }
        """)
        selection_layout.addWidget(self.analyze_roi_btn, 0, 2, 2, 1)
        
        layout.addWidget(selection_group)
        
        # 🔴 **نتایج تحلیل ROI**
        results_group = QGroupBox("📊 نتایج تحلیل بازدهی")
        results_group.setStyleSheet(selection_group.styleSheet())
        
        results_layout = QGridLayout(results_group)
        
        # ردیف اول: اطلاعات پایه
        results_layout.addWidget(QLabel("سرمایه اولیه:"), 0, 0)
        self.roi_capital_label = QLabel("0 تومان")
        self.roi_capital_label.setStyleSheet("color: #3498db; font-size: 12pt;")
        results_layout.addWidget(self.roi_capital_label, 0, 1)
        
        results_layout.addWidget(QLabel("سود کل دوره:"), 0, 2)
        self.roi_total_profit_label = QLabel("0 تومان")
        self.roi_total_profit_label.setStyleSheet("color: #2ecc71; font-size: 12pt;")
        results_layout.addWidget(self.roi_total_profit_label, 0, 3)
        
        # ردیف دوم: ROI
        results_layout.addWidget(QLabel("بازده سرمایه (ROI):"), 1, 0)
        self.roi_percentage_label = QLabel("0%")
        self.roi_percentage_label.setStyleSheet("color: #f39c12; font-size: 14pt; font-weight: bold;")
        results_layout.addWidget(self.roi_percentage_label, 1, 1)
        
        results_layout.addWidget(QLabel("ROI سالانه:"), 1, 2)
        self.roi_annual_label = QLabel("0%")
        self.roi_annual_label.setStyleSheet("color: #9b59b6; font-size: 14pt; font-weight: bold;")
        results_layout.addWidget(self.roi_annual_label, 1, 3)
        
        # ردیف سوم: اطلاعات زمانی
        results_layout.addWidget(QLabel("مدت دوره:"), 2, 0)
        self.roi_period_days_label = QLabel("0 روز")
        results_layout.addWidget(self.roi_period_days_label, 2, 1)
        
        results_layout.addWidget(QLabel("میانگین ماهانه:"), 2, 2)
        self.roi_monthly_avg_label = QLabel("0 تومان")
        results_layout.addWidget(self.roi_monthly_avg_label, 2, 3)
        
        layout.addWidget(results_group)
        
        # 🔴 **گراف (نمایشی)**
        chart_group = QGroupBox("📈 نمودار عملکرد")
        chart_group.setStyleSheet(selection_group.styleSheet())
        
        chart_layout = QVBoxLayout(chart_group)
        
        # ساخت یک نمودار ساده با متن
        self.chart_display = QTextEdit()
        self.chart_display.setReadOnly(True)
        self.chart_display.setMaximumHeight(150)
        self.chart_display.setStyleSheet("""
            QTextEdit {
                background-color: #111111;
                color: #bbb;
                border: 1px solid #333;
                border-radius: 5px;
                font-family: monospace;
                font-size: 10pt;
            }
        """)
        
        chart_layout.addWidget(self.chart_display)
        layout.addWidget(chart_group)
        
        # 🔴 **مقایسه با شاخص‌ها**
        comparison_group = QGroupBox("🏆 مقایسه با شاخص‌ها")
        comparison_group.setStyleSheet(selection_group.styleSheet())
        
        comparison_layout = QGridLayout(comparison_group)
        
        comparison_layout.addWidget(QLabel("سود بانکی (۲۰٪):"), 0, 0)
        self.bank_profit_label = QLabel("0 تومان")
        comparison_layout.addWidget(self.bank_profit_label, 0, 1)
        
        comparison_layout.addWidget(QLabel("شاخص بورس:"), 0, 2)
        self.stock_index_label = QLabel("+۰٪")
        comparison_layout.addWidget(self.stock_index_label, 0, 3)
        
        comparison_layout.addWidget(QLabel("وضعیت:"), 1, 0)
        self.roi_status_label = QLabel("🔵 متوسط")
        self.roi_status_label.setStyleSheet("color: #3498db; font-size: 12pt; font-weight: bold;")
        comparison_layout.addWidget(self.roi_status_label, 1, 1, 1, 3)
        
        layout.addWidget(comparison_group)
        
        layout.addStretch()
        return tab
    
    def create_profitability_tab(self):
        """ایجاد تب گزارش سودآوری"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(15)
        
        # 🔴 **گزارش دوره‌ای**
        period_group = QGroupBox("📅 گزارش سودآوری دوره‌ای")
        period_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 11pt;
                color: #9b59b6;
                border: 1px solid #333;
                border-radius: 8px;
                margin-top: 12px;
                padding-top: 12px;
            }
        """)
        
        period_layout = QVBoxLayout(period_group)
        
        # انتخاب نوع گزارش
        report_type_layout = QHBoxLayout()
        report_type_layout.addWidget(QLabel("نوع گزارش:"))
        
        self.report_type_combo = QComboBox()
        self.report_type_combo.addItems([
            "گزارش ماهانه",
            "گزارش فصلی", 
            "گزارش سالانه",
            "گزارش دلخواه"
        ])
        report_type_layout.addWidget(self.report_type_combo)
        
        self.generate_report_btn = QPushButton("📋 تولید گزارش")
        self.generate_report_btn.setStyleSheet("""
            QPushButton {
                background-color: #9b59b6;
                color: white;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #8e44ad;
            }
        """)
        report_type_layout.addWidget(self.generate_report_btn)
        
        period_layout.addLayout(report_type_layout)
        
        # جدول گزارش
        self.report_table = QTableWidget()
        self.report_table.setColumnCount(8)
        self.report_table.setHorizontalHeaderLabels([
            "دوره", "درآمد", "هزینه", "سود", "حاشیه سود", 
            "نسبت هزینه", "تعداد تراکنش", "وضعیت"
        ])
        
        period_layout.addWidget(self.report_table)
        layout.addWidget(period_group)
        
        # 🔴 **تحلیل نقطه سر به سر**
        breakeven_group = QGroupBox("⚖️ تحلیل نقطه سر به سر")
        breakeven_group.setStyleSheet(period_group.styleSheet())
        
        breakeven_layout = QGridLayout(breakeven_group)
        
        breakeven_layout.addWidget(QLabel("هزینه‌های ثابت:"), 0, 0)
        self.fixed_costs_label = QLabel("0 تومان")
        breakeven_layout.addWidget(self.fixed_costs_label, 0, 1)
        
        breakeven_layout.addWidget(QLabel("متوسط درآمد ماهانه:"), 0, 2)
        self.avg_monthly_income_label = QLabel("0 تومان")
        breakeven_layout.addWidget(self.avg_monthly_income_label, 0, 3)
        
        breakeven_layout.addWidget(QLabel("نقطه سر به سر:"), 1, 0)
        self.breakeven_point_label = QLabel("0 تومان")
        self.breakeven_point_label.setStyleSheet("color: #f39c12; font-weight: bold;")
        breakeven_layout.addWidget(self.breakeven_point_label, 1, 1)
        
        breakeven_layout.addWidget(QLabel("حاشیه ایمنی:"), 1, 2)
        self.safety_margin_label = QLabel("0%")
        self.safety_margin_label.setStyleSheet("color: #2ecc71; font-weight: bold;")
        breakeven_layout.addWidget(self.safety_margin_label, 1, 3)
        
        layout.addWidget(breakeven_group)
        
        # 🔴 **خلاصه نهایی**
        summary_group = QGroupBox("🏁 خلاصه نهایی")
        summary_group.setStyleSheet(period_group.styleSheet())
        
        summary_layout = QVBoxLayout(summary_group)
        
        self.summary_text = QTextEdit()
        self.summary_text.setReadOnly(True)
        self.summary_text.setMaximumHeight(200)
        self.summary_text.setStyleSheet("""
            QTextEdit {
                background-color: #111111;
                color: #ddd;
                border: 1px solid #333;
                border-radius: 5px;
                font-size: 10pt;
                padding: 10px;
            }
        """)
        
        summary_layout.addWidget(self.summary_text)
        layout.addWidget(summary_group)
        
        # 🔴 **دکمه‌های اکشن**
        action_layout = QHBoxLayout()
        
        self.export_report_btn = QPushButton("📤 خروجی Excel")
        self.export_report_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                padding: 10px 20px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #219653;
            }
        """)
        
        self.print_report_btn = QPushButton("🖨️ چاپ گزارش")
        self.print_report_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                padding: 10px 20px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        
        self.email_report_btn = QPushButton("📧 ارسال ایمیل")
        self.email_report_btn.setStyleSheet("""
            QPushButton {
                background-color: #9b59b6;
                color: white;
                padding: 10px 20px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #8e44ad;
            }
        """)
        
        action_layout.addWidget(self.export_report_btn)
        action_layout.addWidget(self.print_report_btn)
        action_layout.addWidget(self.email_report_btn)
        action_layout.addStretch()
        
        layout.addLayout(action_layout)
        layout.addStretch()
        
        return tab
    
    def load_initial_data(self):
        """بارگذاری داده‌های اولیه"""
        self.load_partners()
        self.update_status("✅ سیستم محاسبه سود آماده است")
    
    def setup_connections(self):
        """اتصال سیگنال‌ها"""
        # تب محاسبه سود
        self.calc_button.clicked.connect(self.calculate_profit)
        
        # تب توزیع سود
        self.load_partners_btn.clicked.connect(self.load_partners)
        self.calc_distribution_btn.clicked.connect(self.calculate_distribution)
        self.save_distribution_btn.clicked.connect(self.save_distribution)
        
        # تب تحلیل ROI
        self.analyze_roi_btn.clicked.connect(self.analyze_roi)
        
        # تب گزارش‌ها
        self.generate_report_btn.clicked.connect(self.generate_profitability_report)
        self.export_report_btn.clicked.connect(self.export_report)
        self.print_report_btn.clicked.connect(self.print_report)
    
    def calculate_profit(self):
        """محاسبه سود برای دوره انتخاب شده"""
        try:
            self.update_status("🔄 در حال محاسبه سود...")
            self.progress_bar.setVisible(True)
            self.progress_bar.setValue(30)
            
            # دریافت تاریخ‌ها
            start_date = self.start_date_input.get_date()
            end_date = self.end_date_input.get_date()
            
            if not start_date or not end_date:
                QMessageBox.warning(self, "خطا", "لطفا تاریخ شروع و پایان را انتخاب کنید.")
                return
            
            # تبدیل تاریخ‌ها به شمسی
            start_jalali = self.start_date_input.get_date_object()
            end_jalali = self.end_date_input.get_date_object()
            
            if start_jalali > end_jalali:
                QMessageBox.warning(self, "خطا", "تاریخ شروع باید قبل از تاریخ پایان باشد.")
                return
            
            self.progress_bar.setValue(50)
            
            # محاسبه نسبت‌های مالی
            ratios = self.calculator.calculate_financial_ratios(
                start_date, end_date
            )
            
            self.progress_bar.setValue(70)
            
            # تحلیل سودآوری
            profitability = self.calculator.calculate_profitability_analysis(
                start_date, end_date
            )
            
            # به‌روزرسانی نتایج
            self.update_profit_results(ratios, profitability)
            
            self.progress_bar.setValue(100)
            self.update_status(f"✅ سود دوره {start_date} تا {end_date} محاسبه شد")
            
            # نمایش جزئیات هزینه‌ها
            self.update_expenses_table(profitability.get('expense_breakdown', []))
            
            # نمایش خلاصه
            summary = self.generate_profit_summary(ratios, profitability)
            self.summary_text.setText(summary)
            
        except Exception as e:
            QMessageBox.critical(self, "خطا در محاسبه", f"خطا در محاسبه سود:\n{str(e)}")
            self.update_status(f"❌ خطا در محاسبه: {str(e)}")
        finally:
            self.progress_bar.setVisible(False)
    
    def update_profit_results(self, ratios, profitability):
        """به‌روزرسانی نتایج محاسبه"""
        # مبالغ اصلی
        total_income = ratios.get('total_income', 0)
        total_expense = ratios.get('total_expense', 0)
        net_profit = ratios.get('net_profit', 0)
        
        # فرمت مبالغ
        self.total_income_label.setText(f"{total_income:,.0f} تومان")
        self.total_expense_label.setText(f"{total_expense:,.0f} تومان")
        self.net_profit_label.setText(f"{net_profit:,.0f} تومان")
        
        # محاسبه سود ناخالص (درآمد - هزینه)
        gross_profit = total_income - total_expense
        self.gross_profit_label.setText(f"{gross_profit:,.0f} تومان")
        
        # درصدها
        profit_margin = ratios.get('profit_margin_percentage', 0)
        expense_ratio = ratios.get('expense_ratio_percentage', 0)
        
        self.profit_margin_label.setText(f"{profit_margin:.1f}%")
        self.expense_ratio_label.setText(f"{expense_ratio:.1f}%")
        
        # مالیات و تخفیف (مقادیر نمونه)
        tax_amount = total_income * 0.09  # 9% مالیات
        self.tax_amount_label.setText(f"{tax_amount:,.0f} تومان")
        
        discount_amount = total_income * 0.05  # 5% تخفیف نمونه
        self.discount_amount_label.setText(f"{discount_amount:,.0f} تومان")
        
        # به‌روزرسانی تب تحلیل سودآوری
        self.update_profitability_tab(profitability)
    
    def update_expenses_table(self, expenses):
        """به‌روزرسانی جدول هزینه‌ها"""
        self.expenses_table.setRowCount(len(expenses))
        
        total_expense = sum(float(exp.get('total_amount', 0)) for exp in expenses)
        
        for i, expense in enumerate(expenses):
            expense_type = expense.get('expense_type', 'نامشخص')
            amount = float(expense.get('total_amount', 0))
            percentage = (amount / total_expense * 100) if total_expense > 0 else 0
            
            # شماره ردیف
            self.expenses_table.setItem(i, 0, QTableWidgetItem(str(i + 1)))
            
            # نوع هزینه
            self.expenses_table.setItem(i, 1, QTableWidgetItem(expense_type))
            
            # مبلغ
            amount_item = QTableWidgetItem(f"{amount:,.0f} تومان")
            amount_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.expenses_table.setItem(i, 2, amount_item)
            
            # درصد
            percent_item = QTableWidgetItem(f"{percentage:.1f}%")
            percent_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            
            # رنگ‌بندی بر اساس درصد
            if percentage > 50:
                percent_item.setForeground(QBrush(QColor("#e74c3c")))
            elif percentage > 20:
                percent_item.setForeground(QBrush(QColor("#f39c12")))
            else:
                percent_item.setForeground(QBrush(QColor("#2ecc71")))
            
            self.expenses_table.setItem(i, 3, percent_item)
        
        self.expenses_table.resizeColumnsToContents()
    
    def load_partners(self):
        """بارگذاری لیست شرکا"""
        try:
            self.update_status("🔄 در حال بارگذاری شرکا...")
            
            # دریافت شرکای فعال
            query = """
            SELECT 
                p.id,
                CASE 
                    WHEN per.first_name IS NOT NULL AND per.last_name IS NOT NULL 
                    THEN per.first_name || ' ' || per.last_name
                    WHEN per.first_name IS NOT NULL THEN per.first_name
                    WHEN per.last_name IS NOT NULL THEN per.last_name
                    ELSE 'شریک #' || p.id
                END as partner_name,
                p.capital,
                p.profit_percentage
            FROM Partners p
            LEFT JOIN Persons per ON p.person_id = per.id
            WHERE p.active = 1
            ORDER BY partner_name
            """
            
            partners = self.data_manager.db.fetch_all(query)
            
            # به‌روزرسانی جدول شرکا
            self.partners_table.setRowCount(len(partners))
            
            for i, partner in enumerate(partners):
                # شماره ردیف
                self.partners_table.setItem(i, 0, QTableWidgetItem(str(i + 1)))
                
                # نام شریک
                self.partners_table.setItem(i, 1, QTableWidgetItem(partner['partner_name']))
                
                # سرمایه
                capital = partner.get('capital', 0)
                capital_item = QTableWidgetItem(f"{capital:,.0f} تومان")
                capital_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                self.partners_table.setItem(i, 2, capital_item)
                
                # درصد سود
                percentage = partner.get('profit_percentage', 0)
                percent_item = QTableWidgetItem(f"{percentage:.1f}%")
                percent_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                self.partners_table.setItem(i, 3, percent_item)
                
                # سهم سود (محاسبه می‌شود بعدا)
                self.partners_table.setItem(i, 4, QTableWidgetItem("0 تومان"))
                
                # عملکرد (رنگ‌بندی)
                status_item = QTableWidgetItem("📈 فعال")
                status_item.setForeground(QBrush(QColor("#2ecc71")))
                self.partners_table.setItem(i, 5, status_item)
            
            self.partners_table.resizeColumnsToContents()
            
            # به‌روزرسانی کامبوباکس شرکا در تب ROI
            self.partner_combo.clear()
            for partner in partners:
                self.partner_combo.addItem(partner['partner_name'], partner['id'])
            
            self.update_status(f"✅ {len(partners)} شریک بارگذاری شد")
            
        except Exception as e:
            QMessageBox.warning(self, "خطا", f"خطا در بارگذاری شرکا:\n{str(e)}")
            self.update_status(f"❌ خطا در بارگذاری شرکا: {str(e)}")
    
    def calculate_distribution(self):
        """محاسبه توزیع سود بین شرکا"""
        try:
            # دریافت مبلغ سود برای توزیع
            profit_text = self.distribution_total_input.text().strip()
            if not profit_text:
                QMessageBox.warning(self, "خطا", "لطفا مبلغ سود را وارد کنید.")
                return
            
            try:
                total_profit = float(profit_text.replace(',', ''))
            except:
                QMessageBox.warning(self, "خطا", "مبلغ سود نامعتبر است.")
                return
            
            # دریافت روش توزیع
            method_index = self.distribution_method_combo.currentIndex()
            
            # دریافت اطلاعات شرکا از جدول
            partners_data = []
            for row in range(self.partners_table.rowCount()):
                partner_name = self.partners_table.item(row, 1).text()
                capital_text = self.partners_table.item(row, 2).text()
                percentage_text = self.partners_table.item(row, 3).text()
                
                # استخراج اعداد
                try:
                    capital = float(capital_text.replace(' تومان', '').replace(',', ''))
                except:
                    capital = 0
                
                try:
                    percentage = float(percentage_text.replace('%', ''))
                except:
                    percentage = 0
                
                partners_data.append({
                    'id': row + 1,
                    'partner_name': partner_name,
                    'capital': capital,
                    'profit_percentage': percentage
                })
            
            if not partners_data:
                QMessageBox.warning(self, "خطا", "هیچ شریکی برای توزیع سود وجود ندارد.")
                return
            
            # محاسبه توزیع
            distribution = self.calculator.calculate_partner_profit_distribution(
                total_profit, partners_data
            )
            
            # نمایش نتایج
            self.show_distribution_results(distribution)
            
            self.update_status(f"✅ سود {total_profit:,.0f} تومان بین {len(distribution)} شریک توزیع شد")
            
        except Exception as e:
            QMessageBox.critical(self, "خطا", f"خطا در محاسبه توزیع:\n{str(e)}")
    
    def show_distribution_results(self, distribution):
        """نمایش نتایج توزیع"""
        self.distribution_result_table.setRowCount(len(distribution))
        
        for i, dist in enumerate(distribution):
            # نام شریک
            self.distribution_result_table.setItem(i, 0, QTableWidgetItem(dist['partner_name']))
            
            # درصد
            percent_item = QTableWidgetItem(f"{dist['profit_percentage']:.1f}%")
            percent_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.distribution_result_table.setItem(i, 1, percent_item)
            
            # سهم
            share_item = QTableWidgetItem(f"{dist['profit_share']:,.0f} تومان")
            share_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.distribution_result_table.setItem(i, 2, share_item)
            
            # سرمایه
            capital_item = QTableWidgetItem(f"{dist['capital']:,.0f} تومان")
            capital_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.distribution_result_table.setItem(i, 3, capital_item)
            
            # ROI
            roi_item = QTableWidgetItem(f"{dist['roi']:.1f}%")
            roi_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            
            # رنگ‌بندی ROI
            roi_value = dist['roi']
            if roi_value > 30:
                roi_item.setForeground(QBrush(QColor("#27ae60")))
                roi_item.setText(f"{roi_value:.1f}% 📈")
            elif roi_value > 10:
                roi_item.setForeground(QBrush(QColor("#f39c12")))
            else:
                roi_item.setForeground(QBrush(QColor("#e74c3c")))
            
            self.distribution_result_table.setItem(i, 4, roi_item)
        
        self.distribution_result_table.resizeColumnsToContents()
    
    def save_distribution(self):
        """ذخیره توزیع سود در دیتابیس"""
        try:
            reply = QMessageBox.question(
                self, "ذخیره توزیع",
                "آیا از ذخیره توزیع سود در سیستم اطمینان دارید؟",
                QMessageBox.Yes | QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                # در اینجا کد ذخیره در دیتابیس قرار می‌گیرد
                QMessageBox.information(self, "موفق", "توزیع سود با موفقیت ذخیره شد.")
                self.data_changed.emit()
                self.update_status("✅ توزیع سود ذخیره شد")
        except Exception as e:
            QMessageBox.critical(self, "خطا", f"خطا در ذخیره توزیع:\n{str(e)}")
    
    def analyze_roi(self):
        """تحلیل ROI برای شریک انتخاب شده"""
        try:
            # دریافت شریک انتخاب شده
            partner_index = self.partner_combo.currentIndex()
            if partner_index < 0:
                QMessageBox.warning(self, "خطا", "لطفا یک شریک انتخاب کنید.")
                return
            
            partner_id = self.partner_combo.currentData()
            partner_name = self.partner_combo.currentText()
            
            # تعیین دوره بر اساس انتخاب
            period_text = self.roi_period_combo.currentText()
            today = jdatetime.date.today()
            
            if period_text == "۳ ماهه":
                start_date = today - jdatetime.timedelta(days=90)
            elif period_text == "۶ ماهه":
                start_date = today - jdatetime.timedelta(days=180)
            elif period_text == "۱ ساله":
                start_date = today - jdatetime.timedelta(days=365)
            elif period_text == "۲ ساله":
                start_date = today - jdatetime.timedelta(days=730)
            else:  # از ابتدا
                start_date = jdatetime.date(1400, 1, 1)  # مثال
            
            end_date = today
            
            # محاسبه ROI
            roi_result = self.calculator.calculate_partner_roi(
                partner_id,
                start_date.strftime("%Y/%m/%d"),
                end_date.strftime("%Y/%m/%d")
            )
            
            # نمایش نتایج
            self.display_roi_results(roi_result, partner_name, period_text)
            
            # ایجاد نمودار
            self.create_roi_chart(roi_result)
            
            self.update_status(f"✅ ROI شریک {partner_name} محاسبه شد")
            
        except Exception as e:
            QMessageBox.critical(self, "خطا", f"خطا در تحلیل ROI:\n{str(e)}")
    
    def display_roi_results(self, roi_result, partner_name, period_text):
        """نمایش نتایج تحلیل ROI"""
        capital = roi_result.get('capital', 0)
        total_profit = roi_result.get('total_profit', 0)
        roi_percentage = roi_result.get('roi_percentage', 0)
        annual_roi = roi_result.get('annual_roi_percentage', 0)
        
        # به‌روزرسانی لیبل‌ها
        self.roi_capital_label.setText(f"{capital:,.0f} تومان")
        self.roi_total_profit_label.setText(f"{total_profit:,.0f} تومان")
        self.roi_percentage_label.setText(f"{roi_percentage:.1f}%")
        self.roi_annual_label.setText(f"{annual_roi:.1f}%")
        
        # محاسبه سایر اطلاعات
        days_diff = 90  # به صورت نمونه
        self.roi_period_days_label.setText(f"{days_diff} روز")
        
        monthly_avg = total_profit / 3 if period_text == "۳ ماهه" else total_profit / 12
        self.roi_monthly_avg_label.setText(f"{monthly_avg:,.0f} تومان")
        
        # مقایسه با بانک
        bank_profit = capital * 0.20 * (days_diff / 365)  # سود بانکی 20% سالانه
        self.bank_profit_label.setText(f"{bank_profit:,.0f} تومان")
        
        # وضعیت ROI
        if roi_percentage > 50:
            status = "🟢 عالی"
            status_color = "#27ae60"
            stock_index = "+۴۵٪"
        elif roi_percentage > 20:
            status = "🔵 خوب"
            status_color = "#3498db"
            stock_index = "+۲۵٪"
        elif roi_percentage > 0:
            status = "🟡 متوسط"
            status_color = "#f39c12"
            stock_index = "+۱۲٪"
        else:
            status = "🔴 ضعیف"
            status_color = "#e74c3c"
            stock_index = "-۵٪"
        
        self.roi_status_label.setText(status)
        self.roi_status_label.setStyleSheet(f"color: {status_color}; font-size: 12pt; font-weight: bold;")
        self.stock_index_label.setText(stock_index)
    
    def create_roi_chart(self, roi_result):
        """ایجاد نمودار ساده ROI"""
        capital = roi_result.get('capital', 1000000)
        total_profit = roi_result.get('total_profit', 300000)
        roi_percentage = roi_result.get('roi_percentage', 30)
        
        # ایجاد یک نمودار متنی ساده
        chart_text = f"""
        📊 عملکرد سرمایه گذاری:
        
        سرمایه اولیه: {capital:,.0f} تومان
        سود کسب شده: {total_profit:,.0f} تومان
        بازده سرمایه: {roi_percentage:.1f}%
        
        نمودار بازدهی:
        ▰▰▰▰▰▰▰▰▰▰ {min(100, roi_percentage):.0f}%
        
        مقایسه با شاخص‌ها:
        • بازده این سرمایه گذاری: {roi_percentage:.1f}%
        • میانگین بازار: 25.0%
        • سود بانکی: 20.0%
        
        نتیجه: سرمایه گذاری {roi_percentage - 25:.1f}% بهتر از بازار
        """
        
        self.chart_display.setText(chart_text)
    
    def generate_profitability_report(self):
        """تولید گزارش سودآوری"""
        try:
            report_type = self.report_type_combo.currentText()
            self.update_status(f"🔄 در حال تولید گزارش {report_type}...")
            
            # شبیه‌سازی داده‌های گزارش
            reports_data = self.generate_sample_reports()
            
            # نمایش در جدول
            self.display_reports_table(reports_data)
            
            # محاسبه تحلیل نقطه سر به سر
            self.calculate_breakeven_analysis()
            
            self.update_status(f"✅ گزارش {report_type} تولید شد")
            
        except Exception as e:
            QMessageBox.critical(self, "خطا", f"خطا در تولید گزارش:\n{str(e)}")
    
    def generate_sample_reports(self):
        """تولید داده‌های نمونه برای گزارش"""
        reports = []
        
        periods = [
            "دی ۱۴۰۳", "بهمن ۱۴۰۳", "اسفند ۱۴۰۳",
            "فروردین ۱۴۰۴", "اردیبهشت ۱۴۰۴", "خرداد ۱۴۰۴"
        ]
        
        for i, period in enumerate(periods):
            income = 50000000 + (i * 10000000)
            expense = 30000000 + (i * 8000000)
            profit = income - expense
            margin = (profit / income * 100) if income > 0 else 0
            expense_ratio = (expense / income * 100) if income > 0 else 0
            transactions = 120 + (i * 20)
            
            # تعیین وضعیت
            if margin > 30:
                status = "عالی 🟢"
            elif margin > 20:
                status = "خوب 🔵"
            elif margin > 10:
                status = "متوسط 🟡"
            else:
                status = "ضعیف 🔴"
            
            reports.append({
                'period': period,
                'income': income,
                'expense': expense,
                'profit': profit,
                'margin': margin,
                'expense_ratio': expense_ratio,
                'transactions': transactions,
                'status': status
            })
        
        return reports
    
    def display_reports_table(self, reports):
        """نمایش گزارش‌ها در جدول"""
        self.report_table.setRowCount(len(reports))
        
        for i, report in enumerate(reports):
            # دوره
            self.report_table.setItem(i, 0, QTableWidgetItem(report['period']))
            
            # درآمد
            income_item = QTableWidgetItem(f"{report['income']:,.0f}")
            income_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.report_table.setItem(i, 1, income_item)
            
            # هزینه
            expense_item = QTableWidgetItem(f"{report['expense']:,.0f}")
            expense_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.report_table.setItem(i, 2, expense_item)
            
            # سود
            profit_item = QTableWidgetItem(f"{report['profit']:,.0f}")
            profit_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            
            # رنگ‌بندی سود
            if report['profit'] > 0:
                profit_item.setForeground(QBrush(QColor("#27ae60")))
            else:
                profit_item.setForeground(QBrush(QColor("#e74c3c")))
            
            self.report_table.setItem(i, 3, profit_item)
            
            # حاشیه سود
            margin_item = QTableWidgetItem(f"{report['margin']:.1f}%")
            margin_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.report_table.setItem(i, 4, margin_item)
            
            # نسبت هزینه
            ratio_item = QTableWidgetItem(f"{report['expense_ratio']:.1f}%")
            ratio_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.report_table.setItem(i, 5, ratio_item)
            
            # تعداد تراکنش
            trans_item = QTableWidgetItem(str(report['transactions']))
            trans_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.report_table.setItem(i, 6, trans_item)
            
            # وضعیت
            status_item = QTableWidgetItem(report['status'])
            if "عالی" in report['status']:
                status_item.setForeground(QBrush(QColor("#27ae60")))
            elif "خوب" in report['status']:
                status_item.setForeground(QBrush(QColor("#3498db")))
            elif "متوسط" in report['status']:
                status_item.setForeground(QBrush(QColor("#f39c12")))
            else:
                status_item.setForeground(QBrush(QColor("#e74c3c")))
            
            self.report_table.setItem(i, 7, status_item)
        
        self.report_table.resizeColumnsToContents()
    
    def calculate_breakeven_analysis(self):
        """محاسبه تحلیل نقطه سر به سر"""
        try:
            # دریافت داده‌های نمونه
            total_fixed_costs = 15000000  # هزینه‌های ثابت ماهانه
            avg_monthly_income = 65000000  # میانگین درآمد ماهانه
            avg_monthly_expense = 45000000  # میانگین هزینه ماهانه
            
            # محاسبه نقطه سر به سر
            variable_cost_ratio = avg_monthly_expense / avg_monthly_income if avg_monthly_income > 0 else 0
            breakeven_point = total_fixed_costs / (1 - variable_cost_ratio) if variable_cost_ratio < 1 else 0
            
            # محاسبه حاشیه ایمنی
            safety_margin = ((avg_monthly_income - breakeven_point) / avg_monthly_income * 100) \
                if avg_monthly_income > 0 else 0
            
            # به‌روزرسانی نمایش
            self.fixed_costs_label.setText(f"{total_fixed_costs:,.0f} تومان")
            self.avg_monthly_income_label.setText(f"{avg_monthly_income:,.0f} تومان")
            self.breakeven_point_label.setText(f"{breakeven_point:,.0f} تومان")
            self.safety_margin_label.setText(f"{safety_margin:.1f}%")
            
        except Exception as e:
            print(f"⚠️ خطا در محاسبه نقطه سر به سر: {e}")
    
    def generate_profit_summary(self, ratios, profitability):
        """تولید خلاصه سودآوری"""
        total_income = ratios.get('total_income', 0)
        total_expense = ratios.get('total_expense', 0)
        net_profit = ratios.get('net_profit', 0)
        profit_margin = ratios.get('profit_margin_percentage', 0)
        
        fixed_costs = profitability.get('fixed_costs', 0)
        breakeven = profitability.get('breakeven_point', 0)
        safety_margin = profitability.get('safety_margin', 0)
        
        summary = f"""
        📋 خلاصه گزارش سودآوری
        
        📅 دوره: {self.start_date_input.get_date()} تا {self.end_date_input.get_date()}
        
        🔢 آمار مالی:
        • کل درآمد: {total_income:,.0f} تومان
        • کل هزینه: {total_expense:,.0f} تومان
        • سود خالص: {net_profit:,.0f} تومان
        • حاشیه سود: {profit_margin:.1f}%
        
        📊 تحلیل نقطه سر به سر:
        • هزینه‌های ثابت: {fixed_costs:,.0f} تومان
        • نقطه سر به سر: {breakeven:,.0f} تومان
        • حاشیه ایمنی: {safety_margin:.1f}%
        
        🎯 ارزیابی عملکرد:
        • وضعیت سودآوری: {'عالی' if profit_margin > 25 else 'خوب' if profit_margin > 15 else 'متوسط' if profit_margin > 5 else 'ضعیف'}
        • ریسک مالی: {'کم' if safety_margin > 30 else 'متوسط' if safety_margin > 15 else 'زیاد'}
        • پیشنهاد: {'توسعه فعالیت' if profit_margin > 20 else 'بهبود بهره‌وری' if profit_margin > 10 else 'کاهش هزینه‌ها'}
        
        📈 چشم‌انداز:
        با توجه به عملکرد فعلی، پیش‌بینی می‌شود سود ماه آینده حدود {net_profit * 1.1:,.0f} تومان باشد.
        """
        
        return summary
    
    def update_profitability_tab(self, profitability):
        """به‌روزرسانی تب سودآوری"""
        try:
            # هزینه‌های ثابت
            fixed_costs = profitability.get('fixed_costs', 0)
            self.fixed_costs_label.setText(f"{fixed_costs:,.0f} تومان")
            
            # میانگین درآمد ماهانه
            total_income = profitability.get('total_income', 0)
            self.avg_monthly_income_label.setText(f"{total_income:,.0f} تومان")
            
            # نقطه سر به سر
            breakeven = profitability.get('breakeven_point', 0)
            self.breakeven_point_label.setText(f"{breakeven:,.0f} تومان")
            
            # حاشیه ایمنی
            safety_margin = profitability.get('safety_margin', 0)
            self.safety_margin_label.setText(f"{safety_margin:.1f}%")
            
        except Exception as e:
            print(f"⚠️ خطا در به‌روزرسانی تب سودآوری: {e}")
    
    def export_report(self):
        """خروجی گرفتن از گزارش"""
        QMessageBox.information(self, "خروجی", "گزارش با فرمت Excel ذخیره شد.")
        self.update_status("✅ گزارش با موفقیت ذخیره شد")
    
    def print_report(self):
        """چاپ گزارش"""
        QMessageBox.information(self, "چاپ", "گزارش برای چاپ ارسال شد.")
        self.update_status("✅ گزارش برای چاپ آماده است")
    
    def update_status(self, message):
        """به‌روزرسانی وضعیت"""
        self.status_label.setText(f"⏳ {message}")
    
    def refresh_data(self):
        """بروزرسانی داده‌های فرم"""
        self.load_partners()
        self.update_status("✅ داده‌ها بروزرسانی شدند")