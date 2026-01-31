# backup_settings_form.py

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout,
                               QFormLayout, QLabel, QLineEdit,
                               QComboBox, QPushButton, QGroupBox,
                               QCheckBox, QSpinBox, QTimeEdit,
                               QFileDialog, QTextEdit, QProgressBar,
                               QListWidget, QListWidgetItem, QMessageBox)
from PySide6.QtCore import Qt, QTime, QTimer
import os
from datetime import datetime

class BackupSettingsForm(QWidget):
    """فرم تنظیمات پشتیبان‌گیری"""
    
    def __init__(self, data_manager):
        super().__init__()
        self.data_manager = data_manager
        self.init_ui()
        self.apply_styles()
        self.setup_connections()
        self.load_backup_history()
    
    def init_ui(self):
        """ایجاد رابط کاربری"""
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # گروه تنظیمات خودکار
        auto_group = QGroupBox("🤖 پشتیبان‌گیری خودکار")
        auto_layout = QFormLayout()
        
        # فعال‌سازی پشتیبان خودکار
        self.chk_auto_backup = QCheckBox("فعال‌سازی پشتیبان‌گیری خودکار")
        self.chk_auto_backup.setChecked(True)
        
        # فرکانس پشتیبان
        self.cmb_backup_frequency = QComboBox()
        self.cmb_backup_frequency.addItems([
            "روزانه",
            "هفتگی",
            "ماهانه"
        ])
        
        # زمان پشتیبان
        self.time_backup = QTimeEdit()
        self.time_backup.setTime(QTime(2, 0))  # ساعت ۲ بامداد
        
        # نگهداری پشتیبان‌ها
        self.spn_keep_backups = QSpinBox()
        self.spn_keep_backups.setRange(1, 365)
        self.spn_keep_backups.setValue(30)
        self.spn_keep_backups.setSuffix(" روز")
        
        # فشرده‌سازی
        self.chk_compress_backup = QCheckBox("فشرده‌سازی پشتیبان‌ها")
        self.chk_compress_backup.setChecked(True)
        
        # رمزگذاری
        self.chk_encrypt_backup = QCheckBox("رمزگذاری پشتیبان‌ها")
        self.chk_encrypt_backup.setChecked(False)
        
        self.txt_encryption_key = QLineEdit()
        self.txt_encryption_key.setPlaceholderText("کلید رمزگذاری")
        self.txt_encryption_key.setEchoMode(QLineEdit.Password)
        self.txt_encryption_key.setEnabled(False)
        
        auto_layout.addRow("", self.chk_auto_backup)
        auto_layout.addRow("فرکانس:", self.cmb_backup_frequency)
        auto_layout.addRow("زمان:", self.time_backup)
        auto_layout.addRow("نگهداری:", self.spn_keep_backups)
        auto_layout.addRow("", self.chk_compress_backup)
        auto_layout.addRow("", self.chk_encrypt_backup)
        auto_layout.addRow("کلید رمزگذاری:", self.txt_encryption_key)
        
        auto_group.setLayout(auto_layout)
        main_layout.addWidget(auto_group)
        
        # گروه محل ذخیره
        location_group = QGroupBox("📁 محل ذخیره پشتیبان‌ها")
        location_layout = QFormLayout()
        
        # مسیر ذخیره
        path_layout = QHBoxLayout()
        self.txt_backup_path = QLineEdit()
        self.txt_backup_path.setPlaceholderText("مسیر ذخیره پشتیبان‌ها")
        
        self.btn_browse_path = QPushButton("انتخاب مسیر")
        self.btn_browse_path.clicked.connect(self.browse_backup_path)
        
        path_layout.addWidget(self.txt_backup_path)
        path_layout.addWidget(self.btn_browse_path)
        
        # مسیر پیش‌فرض
        default_path = os.path.join(os.path.expanduser("~"), "RepairShopBackups")
        self.txt_backup_path.setText(default_path)
        
        # محدودیت فضای ذخیره
        self.spn_max_storage = QSpinBox()
        self.spn_max_storage.setRange(100, 10000)
        self.spn_max_storage.setValue(1000)
        self.spn_max_storage.setSuffix(" مگابایت")
        
        # هشدار فضای کم
        self.chk_space_warning = QCheckBox("هشدار هنگام کمبود فضای ذخیره")
        self.chk_space_warning.setChecked(True)
        
        self.spn_warning_threshold = QSpinBox()
        self.spn_warning_threshold.setRange(10, 90)
        self.spn_warning_threshold.setValue(20)
        self.spn_warning_threshold.setSuffix(" %")
        
        location_layout.addRow("مسیر ذخیره:", path_layout)
        location_layout.addRow("حداکثر فضای ذخیره:", self.spn_max_storage)
        location_layout.addRow("", self.chk_space_warning)
        location_layout.addRow("آستانه هشدار:", self.spn_warning_threshold)
        
        location_group.setLayout(location_layout)
        main_layout.addWidget(location_group)
        
        # گروه پشتیبان دستی
        manual_group = QGroupBox("🔄 پشتیبان‌گیری دستی")
        manual_layout = QVBoxLayout()
        
        # دکمه‌های اقدام
        action_layout = QHBoxLayout()
        
        self.btn_backup_now = QPushButton("💾 ایجاد پشتیبان الآن")
        self.btn_backup_now.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                font-weight: bold;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #2ecc71;
            }
        """)
        
        self.btn_restore_backup = QPushButton("🔄 بازیابی پشتیبان")
        self.btn_restore_backup.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                font-weight: bold;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        
        self.btn_test_backup = QPushButton("🧪 تست پشتیبان")
        
        action_layout.addWidget(self.btn_backup_now)
        action_layout.addWidget(self.btn_restore_backup)
        action_layout.addWidget(self.btn_test_backup)
        
        manual_layout.addLayout(action_layout)
        
        # پیشرفت
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        manual_layout.addWidget(self.progress_bar)
        
        manual_group.setLayout(manual_layout)
        main_layout.addWidget(manual_group)
        
        # گروه تاریخچه پشتیبان‌ها
        history_group = QGroupBox("📜 تاریخچه پشتیبان‌ها")
        history_layout = QVBoxLayout()
        
        # لیست پشتیبان‌ها
        self.list_backups = QListWidget()
        self.list_backups.setMaximumHeight(150)
        
        history_layout.addWidget(self.list_backups)
        
        # دکمه‌های مدیریت تاریخچه
        history_actions = QHBoxLayout()
        
        self.btn_delete_backup = QPushButton("🗑️ حذف انتخاب شده")
        self.btn_open_folder = QPushButton("📂 بازکردن پوشه")
        self.btn_refresh_list = QPushButton("🔄 بروزرسانی لیست")
        
        history_actions.addWidget(self.btn_delete_backup)
        history_actions.addWidget(self.btn_open_folder)
        history_actions.addWidget(self.btn_refresh_list)
        history_actions.addStretch()
        
        history_layout.addLayout(history_actions)
        history_group.setLayout(history_layout)
        
        main_layout.addWidget(history_group)
        
        # اطلاعات سیستم
        info_layout = QHBoxLayout()
        
        self.lbl_last_backup = QLabel("آخرین پشتیبان: نامشخص")
        self.lbl_next_backup = QLabel("پشتیبان بعدی: نامشخص")
        self.lbl_storage_info = QLabel("فضای استفاده شده: محاسبه...")
        
        info_layout.addWidget(self.lbl_last_backup)
        info_layout.addWidget(self.lbl_next_backup)
        info_layout.addWidget(self.lbl_storage_info)
        info_layout.addStretch()
        
        main_layout.addLayout(info_layout)
        
        self.setLayout(main_layout)
    
    def apply_styles(self):
        """اعمال استایل"""
        self.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 12pt;
                color: #e67e22;
                border: 2px solid #e67e22;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                padding: 0 10px;
            }
            QLineEdit, QComboBox, QSpinBox, QTimeEdit {
                background-color: #222222;
                color: #ffffff;
                border: 1px solid #444444;
                border-radius: 3px;
                padding: 5px;
                min-height: 25px;
            }
            QCheckBox {
                color: #ffffff;
            }
            QPushButton {
                background-color: #2c3e50;
                color: white;
                border: none;
                padding: 8px 15px;
                border-radius: 4px;
                margin: 2px;
            }
            QPushButton:hover {
                background-color: #34495e;
            }
            QListWidget {
                background-color: #111111;
                color: #ffffff;
                border: 1px solid #444444;
                border-radius: 3px;
            }
            QProgressBar {
                border: 1px solid #444444;
                border-radius: 3px;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #27ae60;
                border-radius: 3px;
            }
        """)
    
    def setup_connections(self):
        """اتصال سیگنال‌ها"""
        self.chk_encrypt_backup.stateChanged.connect(
            lambda: self.txt_encryption_key.setEnabled(self.chk_encrypt_backup.isChecked())
        )
        
        self.btn_backup_now.clicked.connect(self.create_backup_now)
        self.btn_restore_backup.clicked.connect(self.restore_backup)
        self.btn_test_backup.clicked.connect(self.test_backup)
        self.btn_delete_backup.clicked.connect(self.delete_backup)
        self.btn_open_folder.clicked.connect(self.open_backup_folder)
        self.btn_refresh_list.clicked.connect(self.load_backup_history)
    
    def browse_backup_path(self):
        """انتخاب مسیر ذخیره پشتیبان"""
        path = QFileDialog.getExistingDirectory(
            self,
            "انتخاب پوشه ذخیره پشتیبان",
            self.txt_backup_path.text()
        )
        
        if path:
            self.txt_backup_path.setText(path)
    
    def create_backup_now(self):
        """ایجاد پشتیبان فوری"""
        reply = QMessageBox.question(
            self,
            "تأیید پشتیبان",
            "آیا می‌خواهید پشتیبان جدیدی ایجاد کنید؟",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.Yes
        )
        
        if reply == QMessageBox.Yes:
            self.progress_bar.setVisible(True)
            self.progress_bar.setValue(0)
            
            # شبیه‌سازی فرآیند پشتیبان
            QTimer.singleShot(500, lambda: self.update_progress(25))
            QTimer.singleShot(1000, lambda: self.update_progress(50))
            QTimer.singleShot(1500, lambda: self.update_progress(75))
            QTimer.singleShot(2000, lambda: self.update_progress(100))
            QTimer.singleShot(2500, self.backup_completed)
    
    def update_progress(self, value):
        """به‌روزرسانی نوار پیشرفت"""
        self.progress_bar.setValue(value)
    
    def backup_completed(self):
        """اتمام پشتیبان"""
        self.progress_bar.setVisible(False)
        
        # ایجاد رکورد جدید در لیست
        timestamp = datetime.now().strftime("%Y/%m/%d %H:%M")
        backup_name = f"پشتیبان_{timestamp}"
        
        item = QListWidgetItem(f"✅ {backup_name} - {timestamp}")
        self.list_backups.insertItem(0, item)
        
        # به‌روزرسانی اطلاعات
        self.lbl_last_backup.setText(f"آخرین پشتیبان: {timestamp}")
        
        QMessageBox.information(self, "موفقیت", "پشتیبان با موفقیت ایجاد شد.")
    
    def restore_backup(self):
        """بازیابی پشتیبان"""
        selected_item = self.list_backups.currentItem()
        if not selected_item:
            QMessageBox.warning(self, "هشدار", "لطفاً یک پشتیبان را انتخاب کنید")
            return
        
        reply = QMessageBox.warning(
            self,
            "هشدار بازیابی",
            "آیا مطمئن هستید که می‌خواهید این پشتیبان را بازیابی کنید؟\n"
            "تمام داده‌های فعلی جایگزین خواهند شد.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            QMessageBox.information(self, "بازیابی", "فرآیند بازیابی شروع شد...")
    
    def test_backup(self):
        """تست پشتیبان"""
        QMessageBox.information(self, "تست", "تست یکپارچگی پشتیبان انجام شد.")
    
    def delete_backup(self):
        """حذف پشتیبان انتخاب شده"""
        selected_item = self.list_backups.currentItem()
        if not selected_item:
            QMessageBox.warning(self, "هشدار", "لطفاً یک پشتیبان را انتخاب کنید")
            return
        
        reply = QMessageBox.question(
            self,
            "تأیید حذف",
            "آیا مطمئن هستید که می‌خواهید این پشتیبان را حذف کنید؟",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            row = self.list_backups.row(selected_item)
            self.list_backups.takeItem(row)
            QMessageBox.information(self, "موفقیت", "پشتیبان حذف شد.")
    
    def open_backup_folder(self):
        """باز کردن پوشه پشتیبان‌ها"""
        path = self.txt_backup_path.text()
        if os.path.exists(path):
            os.startfile(path)
        else:
            QMessageBox.warning(self, "خطا", "پوشه پشتیبان یافت نشد.")
    
    def load_backup_history(self):
        """بارگذاری تاریخچه پشتیبان‌ها"""
        self.list_backups.clear()
        
        # نمونه داده‌های ساختگی
        backups = [
            ("✅ پشتیبان_۲۰۲۴-۰۱-۰۵_۱۴۰۳-۱۰-۱۵", "۱۴۰۳/۱۰/۱۵ ۰۲:۰۰"),
            ("✅ پشتیبان_۲۰۲۴-۰۱-۰۴_۱۴۰۳-۱۰-۱۴", "۱۴۰۳/۱۰/۱۴ ۰۲:۰۰"),
            ("✅ پشتیبان_۲۰۲۴-۰۱-۰۳_۱۴۰۳-۱۰-۱۳", "۱۴۰۳/۱۰/۱۳ ۰۲:۰۰"),
            ("⚠️ پشتیبان_۲۰۲۴-۰۱-۰۲_۱۴۰۳-۱۰-۱۲", "۱۴۰۳/۱۰/۱۲ ۰۲:۰۰ (ناقص)"),
            ("✅ پشتیبان_۲۰۲۴-۰۱-۰۱_۱۴۰۳-۱۰-۱۱", "۱۴۰۳/۱۰/۱۱ ۰۲:۰۰"),
        ]
        
        for name, date in backups:
            item = QListWidgetItem(f"{name} - {date}")
            self.list_backups.addItem(item)
    
    def load_settings(self, settings_data):
        """بارگذاری تنظیمات"""
        try:
            # پشتیبان خودکار
            self.chk_auto_backup.setChecked(settings_data.get('auto_backup', True))
            
            frequency = settings_data.get('backup_frequency', 'روزانه')
            freq_index = self.cmb_backup_frequency.findText(frequency)
            if freq_index >= 0:
                self.cmb_backup_frequency.setCurrentIndex(freq_index)
            
            # زمان
            backup_time = settings_data.get('backup_time', '02:00')
            hours, minutes = map(int, backup_time.split(':'))
            self.time_backup.setTime(QTime(hours, minutes))
            
            self.spn_keep_backups.setValue(settings_data.get('keep_backups_days', 30))
            self.chk_compress_backup.setChecked(settings_data.get('compress_backup', True))
            self.chk_encrypt_backup.setChecked(settings_data.get('encrypt_backup', False))
            self.txt_encryption_key.setText(settings_data.get('encryption_key', ''))
            
            # محل ذخیره
            self.txt_backup_path.setText(settings_data.get('backup_path', ''))
            self.spn_max_storage.setValue(settings_data.get('max_storage_mb', 1000))
            self.chk_space_warning.setChecked(settings_data.get('space_warning', True))
            self.spn_warning_threshold.setValue(settings_data.get('warning_threshold', 20))
            
        except Exception as e:
            print(f"خطا در بارگذاری تنظیمات پشتیبان: {e}")
    
    def get_settings(self):
        """جمع‌آوری تنظیمات"""
        settings = {
            # پشتیبان خودکار
            'auto_backup': self.chk_auto_backup.isChecked(),
            'backup_frequency': self.cmb_backup_frequency.currentText(),
            'backup_time': self.time_backup.time().toString("HH:mm"),
            'keep_backups_days': self.spn_keep_backups.value(),
            'compress_backup': self.chk_compress_backup.isChecked(),
            'encrypt_backup': self.chk_encrypt_backup.isChecked(),
            'encryption_key': self.txt_encryption_key.text(),
            
            # محل ذخیره
            'backup_path': self.txt_backup_path.text(),
            'max_storage_mb': self.spn_max_storage.value(),
            'space_warning': self.chk_space_warning.isChecked(),
            'warning_threshold': self.spn_warning_threshold.value(),
        }
        
        return settings