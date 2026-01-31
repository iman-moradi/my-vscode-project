from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *

try:
    import cv2
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False
    print("⚠️ کتابخانه OpenCV (cv2) نصب نیست. امکان استفاده از دوربین وجود ندارد.")

try:
    from pyzbar.pyzbar import decode
    PYZBAR_AVAILABLE = True
except ImportError:
    PYZBAR_AVAILABLE = False
    print("⚠️ کتابخانه pyzbar نصب نیست. امکان اسکن بارکد وجود ندارد.")

import numpy as np

class BarcodeScannerWidget(QWidget):
    """ویجت اسکن بارکد با استفاده از دوربین"""
    barcode_scanned = Signal(str)  # سیگنال هنگام اسکن بارکد
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.camera = None
        self.timer = QTimer()
        self.scanning = False
        self.setup_ui()
        
        # اگر کتابخانه‌ها نصب نیستند، دکمه شروع را غیرفعال کن
        if not CV2_AVAILABLE or not PYZBAR_AVAILABLE:
            self.btn_start.setEnabled(False)
            self.btn_start.setText("⚠️ کتابخانه‌ها نصب نیستند")
            self.status_label.setText("⚠️ لطفا کتابخانه‌های cv2 و pyzbar را نصب کنید")
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # عنوان
        title = QLabel("📷 اسکنر بارکد")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 14pt; font-weight: bold; color: #4fc3f7;")
        layout.addWidget(title)
        
        # نمایشگر دوربین
        self.camera_label = QLabel("دوربین فعال نشده")
        self.camera_label.setAlignment(Qt.AlignCenter)
        self.camera_label.setMinimumSize(640, 480)
        self.camera_label.setStyleSheet("""
            background-color: #000;
            color: white;
            border: 2px solid #424242;
            border-radius: 8px;
        """)
        layout.addWidget(self.camera_label)
        
        # کنترل‌ها
        control_widget = QWidget()
        control_layout = QHBoxLayout(control_widget)
        control_layout.setContentsMargins(0, 0, 0, 0)
        
        self.btn_start = QPushButton("▶️ شروع اسکن")
        self.btn_start.setObjectName("btnSuccess")
        self.btn_start.clicked.connect(self.start_scanning)
        
        self.btn_stop = QPushButton("⏸️ توقف")
        self.btn_stop.setObjectName("btnDanger")
        self.btn_stop.clicked.connect(self.stop_scanning)
        self.btn_stop.setEnabled(False)
        
        self.btn_manual = QPushButton("⌨️ ورود دستی")
        self.btn_manual.setObjectName("btnSecondary")
        self.btn_manual.clicked.connect(self.manual_entry)
        
        control_layout.addWidget(self.btn_start)
        control_layout.addWidget(self.btn_stop)
        control_layout.addWidget(self.btn_manual)
        control_layout.addStretch()
        
        layout.addWidget(control_widget)
        
        # وضعیت
        self.status_label = QLabel("آماده")
        self.status_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.status_label)
        
        # تنظیم تایمر برای خواندن فریم‌ها
        self.timer.timeout.connect(self.update_frame)
        
    def start_scanning(self):
        """شروع اسکن بارکد"""
        # بررسی وجود کتابخانه‌های مورد نیاز
        if not CV2_AVAILABLE:
            self.show_error("کتابخانه OpenCV نصب نیست. لطفا با دستور 'pip install opencv-python' نصب کنید.")
            return
            
        if not PYZBAR_AVAILABLE:
            self.show_error("کتابخانه pyzbar نصب نیست. لطفا با دستور 'pip install pyzbar' نصب کنید.")
            return
        
        try:
            self.camera = cv2.VideoCapture(0)
            if not self.camera.isOpened():
                self.show_error("دوربین یافت نشد!")
                return
                
            self.scanning = True
            self.btn_start.setEnabled(False)
            self.btn_stop.setEnabled(True)
            self.status_label.setText("در حال اسکن...")
            self.status_label.setStyleSheet("color: #4fc3f7;")
            
            self.timer.start(30)  # 30ms interval
            
        except Exception as e:
            self.show_error(f"خطا در شروع دوربین: {str(e)}")
            
    def stop_scanning(self):
        """توقف اسکن"""
        self.scanning = False
        self.timer.stop()
        
        if self.camera:
            self.camera.release()
            self.camera = None
            
        self.camera_label.setText("دوربین غیرفعال")
        self.camera_label.setPixmap(QPixmap())  # پاک کردن تصویر
        self.btn_start.setEnabled(True)
        self.btn_stop.setEnabled(False)
        self.status_label.setText("متوقف شد")
        self.status_label.setStyleSheet("color: #f44336;")
        
    def update_frame(self):
        """بروزرسانی فریم دوربین و تشخیص بارکد"""
        if not self.scanning or not self.camera:
            return
            
        try:
            ret, frame = self.camera.read()
            if ret:
                # تشخیص بارکد
                barcodes = decode(frame)
                
                # رسم مستطیل دور بارکدها
                for barcode in barcodes:
                    # استخراج داده
                    barcode_data = barcode.data.decode("utf-8")
                    
                    # رسم مستطیل دور بارکد
                    points = barcode.polygon
                    if len(points) == 4:
                        pts = np.array(points, np.int32)
                        pts = pts.reshape((-1, 1, 2))
                        cv2.polylines(frame, [pts], True, (0, 255, 0), 3)
                    
                    # نمایش داده بارکد
                    cv2.putText(frame, barcode_data, 
                               (barcode.rect.left, barcode.rect.top - 10),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                    
                    # ارسال سیگنال
                    self.barcode_scanned.emit(barcode_data)
                    self.status_label.setText(f"بارکد شناسایی شد: {barcode_data}")
                    self.status_label.setStyleSheet("color: #81c784;")
                    
                    # توقف موقت
                    self.stop_scanning()
                    break
                
                # تبدیل فریم برای نمایش در QLabel
                rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                h, w, ch = rgb_image.shape
                bytes_per_line = ch * w
                qt_image = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
                
                # مقیاس‌بندی برای نمایش
                scaled_image = qt_image.scaled(
                    self.camera_label.size(), 
                    Qt.KeepAspectRatio, 
                    Qt.SmoothTransformation
                )
                
                self.camera_label.setPixmap(QPixmap.fromImage(scaled_image))
                
        except Exception as e:
            self.show_error(f"خطا در پردازش تصویر: {str(e)}")
            self.stop_scanning()
            
    def manual_entry(self):
        """ورود دستی بارکد"""
        text, ok = QInputDialog.getText(
            self, 
            "ورود دستی بارکد", 
            "لطفا شماره بارکد را وارد کنید:"
        )
        
        if ok and text:
            self.barcode_scanned.emit(text)
            self.status_label.setText(f"بارکد وارد شد: {text}")
            self.status_label.setStyleSheet("color: #81c784;")
            
    def show_error(self, message):
        """نمایش خطا"""
        self.status_label.setText(message)
        self.status_label.setStyleSheet("color: #f44336;")
        
    def closeEvent(self, event):
        """هنگام بسته شدن ویجت"""
        self.stop_scanning()
        super().closeEvent(event)


# نسخه جایگزین: اسکنر ساده بدون نیاز به کتابخانه‌های خارجی
class SimpleBarcodeScanner(QWidget):
    """اسکنر بارکد ساده بدون دوربین - فقط ورود دستی"""
    barcode_scanned = Signal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        title = QLabel("⌨️ اسکنر بارکد (ورود دستی)")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 14pt; font-weight: bold; color: #4fc3f7;")
        layout.addWidget(title)
        
        # فیلد ورود
        self.txt_barcode = QLineEdit()
        self.txt_barcode.setPlaceholderText("بارکد را اینجا وارد کنید یا از اسکنر فیزیکی استفاده کنید...")
        self.txt_barcode.returnPressed.connect(self.on_barcode_entered)
        
        layout.addWidget(QLabel("بارکد:"))
        layout.addWidget(self.txt_barcode)
        
        # دکمه ثبت
        self.btn_submit = QPushButton("✅ ثبت بارکد")
        self.btn_submit.setObjectName("btnSuccess")
        self.btn_submit.clicked.connect(self.on_barcode_entered)
        
        layout.addWidget(self.btn_submit)
        
        # نمایش آخرین بارکد
        self.lbl_last_barcode = QLabel("")
        self.lbl_last_barcode.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.lbl_last_barcode)
        
        layout.addStretch()
        
    def on_barcode_entered(self):
        """هنگام وارد کردن بارکد"""
        barcode = self.txt_barcode.text().strip()
        if barcode:
            self.barcode_scanned.emit(barcode)
            self.lbl_last_barcode.setText(f"آخرین بارکد: {barcode}")
            self.txt_barcode.clear()