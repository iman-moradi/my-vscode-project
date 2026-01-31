# ui/widgets/dashboard/charts_widget.py
"""
ویجت نمودارهای داشبورد
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QFrame, QComboBox, QSizePolicy
)
from PySide6.QtCore import Qt, QTimer, QRectF
from PySide6.QtGui import (
    QPainter, QPen, QBrush, QColor, QLinearGradient, 
    QFont, QFontMetrics
)
from PySide6.QtCharts import (
    QChart, QChartView, QBarSeries, QBarSet, 
    QBarCategoryAxis, QValueAxis, QPieSeries, QPieSlice,
    QLineSeries, QSplineSeries
)
import math


class SimplePieChart(QWidget):
    """نمودار دایره‌ای ساده (بدون QtCharts)"""
    
    def __init__(self, title="", parent=None):
        super().__init__(parent)
        self.title = title
        self.data = []
        self.colors = []
        self.setup_ui()
    
    def setup_ui(self):
        self.setMinimumSize(300, 300)
        
        # عنوان
        self.title_label = QLabel(self.title)
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setStyleSheet("""
            font-weight: bold;
            font-size: 14px;
            color: white;
            padding: 10px;
        """)
        
        layout = QVBoxLayout(self)
        layout.addWidget(self.title_label)
        layout.setContentsMargins(10, 10, 10, 10)
    
    def set_data(self, labels, data, colors):
        """تنظیم داده‌های نمودار"""
        self.data = list(zip(labels, data, colors))
        self.update()
    
    def paintEvent(self, event):
        """رسم نمودار دایره‌ای"""
        if not self.data:
            return
        
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # محاسبه مجموع
        total = sum(item[1] for item in self.data)
        if total == 0:
            return
        
        # محدوده رسم
        chart_rect = QRectF(50, 50, self.width() - 100, self.height() - 100)
        radius = min(chart_rect.width(), chart_rect.height()) / 2
        
        # رسم نمودار دایره‌ای
        start_angle = 0
        center_x = chart_rect.center().x()
        center_y = chart_rect.center().y()
        
        # رسم هر بخش
        for label, value, color_str in self.data:
            if value == 0:
                continue
            
            # محاسبه زاویه
            angle = (value / total) * 360 * 16  # درجه به 1/16 درجه
            
            # تنظیم رنگ
            color = QColor(color_str)
            painter.setBrush(QBrush(color))
            painter.setPen(QPen(QColor(30, 30, 30), 2))
            
            # رسم بخش
            painter.drawPie(center_x - radius, center_y - radius, 
                          radius * 2, radius * 2, 
                          start_angle, angle)
            
            start_angle += angle
        
        # رسم توضیحات (legend)
        painter.setFont(QFont("B Nazanin", 9))
        legend_x = 20
        legend_y = self.height() - 100
        
        for i, (label, value, color_str) in enumerate(self.data):
            if value == 0:
                continue
            
            color = QColor(color_str)
            
            # مربع رنگ
            painter.setBrush(QBrush(color))
            painter.setPen(QPen(QColor(200, 200, 200)))
            painter.drawRect(legend_x, legend_y + i * 25, 15, 15)
            
            # متن
            percentage = (value / total) * 100
            text = f"{label}: {value} ({percentage:.1f}%)"
            painter.setPen(QPen(QColor(255, 255, 255)))
            painter.drawText(legend_x + 25, legend_y + i * 25 + 12, text)


class SimpleBarChart(QWidget):
    """نمودار میله‌ای ساده"""
    
    def __init__(self, title="", parent=None):
        super().__init__(parent)
        self.title = title
        self.labels = []
        self.values = []
        self.colors = []
        self.setup_ui()
    
    def setup_ui(self):
        self.setMinimumSize(400, 300)
        
        # عنوان
        self.title_label = QLabel(self.title)
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setStyleSheet("""
            font-weight: bold;
            font-size: 14px;
            color: white;
            padding: 10px;
        """)
        
        layout = QVBoxLayout(self)
        layout.addWidget(self.title_label)
        layout.setContentsMargins(20, 10, 20, 20)
    
    def set_data(self, labels, values, colors=None):
        """تنظیم داده‌های نمودار"""
        self.labels = labels
        self.values = values
        self.colors = colors or ['#3498db'] * len(labels)
        self.update()
    
    def paintEvent(self, event):
        """رسم نمودار میله‌ای"""
        if not self.labels or not self.values:
            return
        
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # فونت
        font = QFont("B Nazanin", 9)
        painter.setFont(font)
        metrics = QFontMetrics(font)
        
        # محاسبه مقادیر
        max_value = max(self.values) if self.values else 1
        chart_height = self.height() - 100
        chart_width = self.width() - 100
        bar_width = (chart_width - 50) / len(self.labels)
        
        # رسم محورها
        painter.setPen(QPen(QColor(150, 150, 150), 1))
        
        # محور Y
        painter.drawLine(70, 50, 70, 50 + chart_height)
        
        # محور X
        painter.drawLine(70, 50 + chart_height, 70 + chart_width, 50 + chart_height)
        
        # تقسیم‌بندی محور Y
        y_ticks = 5
        for i in range(y_ticks + 1):
            y = 50 + chart_height - (i * chart_height / y_ticks)
            
            # خط تقسیم
            painter.setPen(QPen(QColor(100, 100, 100), 1, Qt.DashLine))
            painter.drawLine(70, y, 70 + chart_width, y)
            
            # مقدار
            value = (i * max_value / y_ticks)
            value_text = f"{value:,.0f}"
            if max_value >= 1000:
                value_text = f"{value/1000:,.0f}k"
            
            painter.setPen(QPen(QColor(200, 200, 200)))
            text_width = metrics.horizontalAdvance(value_text)
            painter.drawText(70 - text_width - 5, y + 5, value_text)
        
        # رسم میله‌ها
        for i, (label, value, color) in enumerate(zip(self.labels, self.values, self.colors)):
            x = 70 + (i * bar_width) + 10
            bar_height = (value / max_value) * chart_height if max_value > 0 else 0
            
            # گرادیانت برای میله
            gradient = QLinearGradient(x, 50 + chart_height - bar_height, 
                                      x + bar_width - 20, 50 + chart_height)
            base_color = QColor(color)
            gradient.setColorAt(0, base_color.lighter(120))
            gradient.setColorAt(1, base_color)
            
            painter.setBrush(QBrush(gradient))
            painter.setPen(QPen(QColor(30, 30, 30), 1))
            
            painter.drawRect(x, 50 + chart_height - bar_height, 
                           bar_width - 20, bar_height)
            
            # مقدار روی میله
            if bar_height > 20:
                value_text = f"{value:,.0f}"
                painter.setPen(QPen(QColor(255, 255, 255)))
                text_width = metrics.horizontalAdvance(value_text)
                painter.drawText(x + (bar_width - 20 - text_width) / 2, 
                               50 + chart_height - bar_height - 5, 
                               value_text)
            
            # برچسب زیر میله
            painter.setPen(QPen(QColor(200, 200, 200)))
            
            # اگر برچسب طولانی است، آن را بچرخان
            if metrics.horizontalAdvance(label) > bar_width - 20:
                # چرخش 45 درجه
                painter.save()
                painter.translate(x + (bar_width - 20) / 2, 50 + chart_height + 20)
                painter.rotate(45)
                painter.drawText(0, 0, label)
                painter.restore()
            else:
                painter.drawText(x, 50 + chart_height + 20, label)


class ChartsWidget(QWidget):
    """ویجت نمودارهای داشبورد"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.dashboard_manager = None
        self.charts = {}
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(15)
        
        # عنوان بخش
        title_label = QLabel("📊 نمودارهای مدیریتی")
        title_label.setStyleSheet("""
            font-size: 16px;
            font-weight: bold;
            color: #3498db;
            padding-bottom: 10px;
            border-bottom: 2px solid #3498db;
        """)
        layout.addWidget(title_label)
        
        # کنترل‌های نمودار
        controls_layout = QHBoxLayout()
        
        # انتخاب نوع نمودار
        self.chart_type_combo = QComboBox()
        self.chart_type_combo.addItems([
            "وضعیت پذیرش‌ها",
            "درآمد روزانه",
            "روند ماهانه",
            "موجودی انبار"
        ])
        self.chart_type_combo.setStyleSheet("""
            QComboBox {
                background-color: #2c2c2c;
                color: white;
                border: 1px solid #444;
                border-radius: 5px;
                padding: 8px;
                min-width: 150px;
            }
        """)
        self.chart_type_combo.currentIndexChanged.connect(self.on_chart_type_changed)
        
        # دکمه بروزرسانی
        refresh_btn = QLabel("🔄")
        refresh_btn.setCursor(Qt.PointingHandCursor)
        refresh_btn.setStyleSheet("font-size: 20px; padding: 5px;")
        refresh_btn.mousePressEvent = lambda e: self.refresh_charts()
        
        controls_layout.addWidget(QLabel("نمودار:"))
        controls_layout.addWidget(self.chart_type_combo)
        controls_layout.addStretch()
        controls_layout.addWidget(refresh_btn)
        
        layout.addLayout(controls_layout)
        
        # ویجت نمودار
        self.chart_container = QFrame()
        self.chart_container.setStyleSheet("""
            QFrame {
                background-color: #1a1a1a;
                border-radius: 10px;
                border: 1px solid #333;
            }
        """)
        
        chart_layout = QVBoxLayout(self.chart_container)
        chart_layout.setContentsMargins(20, 20, 20, 20)
        
        # نمودار فعلی
        self.current_chart = None
        
        layout.addWidget(self.chart_container)
    
    def set_dashboard_manager(self, dashboard_manager):
        """تنظیم مدیر داشبورد"""
        self.dashboard_manager = dashboard_manager
    
    def on_chart_type_changed(self, index):
        """تغییر نوع نمودار"""
        chart_types = [
            'reception_status',
            'daily_income',
            'monthly_trends',
            'inventory_status'
        ]
        
        if index < len(chart_types):
            self.show_chart(chart_types[index])
    
    def show_chart(self, chart_type):
        """نمایش نمودار خاص"""
        # پاک کردن نمودار قبلی
        if self.current_chart:
            self.current_chart.setParent(None)
            self.current_chart.deleteLater()
        
        # دریافت داده‌ها
        if not self.dashboard_manager:
            return
        
        charts_data = self.dashboard_manager.get_charts_data()
        
        if chart_type == 'reception_status':
            self.show_reception_chart(charts_data.get('reception_status', {}))
        elif chart_type == 'daily_income':
            self.show_income_chart(charts_data.get('daily_income', {}))
        elif chart_type == 'monthly_trends':
            self.show_trends_chart(charts_data.get('monthly_trends', {}))
        elif chart_type == 'inventory_status':
            self.show_inventory_chart(charts_data.get('inventory_status', {}))
    
    def show_reception_chart(self, chart_data):
        """نمایش نمودار وضعیت پذیرش‌ها"""
        if not chart_data:
            return
        
        pie_chart = SimplePieChart("وضعیت پذیرش‌ها")
        pie_chart.set_data(
            chart_data.get('labels', []),
            chart_data.get('data', []),
            chart_data.get('colors', [])
        )
        
        self.current_chart = pie_chart
        self.chart_container.layout().addWidget(pie_chart)
    
    def show_income_chart(self, chart_data):
        """نمایش نمودار درآمد روزانه"""
        if not chart_data:
            return
        
        dates = chart_data.get('dates', [])
        income = chart_data.get('income', [])
        
        if not dates or not income:
            return
        
        # ایجاد برچسب‌های کوتاه‌تر
        short_dates = []
        for date in dates:
            parts = date.split('/')
            if len(parts) == 2:
                short_dates.append(f"{parts[1]}/{parts[0]}")
            else:
                short_dates.append(date)
        
        bar_chart = SimpleBarChart("درآمد روزانه (هفته جاری)")
        bar_chart.set_data(short_dates, income)
        
        self.current_chart = bar_chart
        self.chart_container.layout().addWidget(bar_chart)
    
    def show_trends_chart(self, chart_data):
        """نمایش نمودار روند ماهانه"""
        if not chart_data:
            return
        
        months = chart_data.get('months', [])
        receptions = chart_data.get('receptions', [])
        
        if not months or not receptions:
            return
        
        bar_chart = SimpleBarChart("روند پذیرش‌های ماهانه")
        bar_chart.set_data(months, receptions, ['#3498db'] * len(months))
        
        self.current_chart = bar_chart
        self.chart_container.layout().addWidget(bar_chart)
    
    def show_inventory_chart(self, chart_data):
        """نمایش نمودار موجودی انبار"""
        if not chart_data:
            return
        
        pie_chart = SimplePieChart("وضعیت موجودی انبار")
        pie_chart.set_data(
            chart_data.get('labels', []),
            chart_data.get('data', []),
            chart_data.get('colors', [])
        )
        
        self.current_chart = pie_chart
        self.chart_container.layout().addWidget(pie_chart)
    
    def refresh_charts(self):
        """بروزرسانی نمودارها"""
        self.on_chart_type_changed(self.chart_type_combo.currentIndex())
    
    def update_charts(self, charts_data):
        """بروزرسانی داده‌های نمودارها"""
        if not charts_data:
            return
        
        # بروزرسانی نمودار فعلی
        self.refresh_charts()


if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication
    import sys
    
    app = QApplication(sys.argv)
    
    widget = ChartsWidget()
    widget.setFixedSize(600, 500)
    widget.show()
    
    # تست با داده‌های نمونه
    test_charts = {
        'reception_status': {
            'labels': ['در انتظار', 'در حال تعمیر', 'تعمیر شده', 'تحویل داده شده'],
            'data': [5, 8, 12, 20],
            'colors': ['#f39c12', '#3498db', '#27ae60', '#9b59b6']
        },
        'daily_income': {
            'dates': ['01/15', '01/16', '01/17', '01/18', '01/19', '01/20', '01/21'],
            'income': [1500000, 1200000, 1800000, 900000, 2100000, 1500000, 1700000]
        }
    }
    
    # شبیه‌سازی داشبورد منیجر
    class MockDashboardManager:
        def get_charts_data(self):
            return test_charts
    
    widget.set_dashboard_manager(MockDashboardManager())
    widget.on_chart_type_changed(0)  # نمایش اولین نمودار
    
    sys.exit(app.exec())