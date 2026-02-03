# ui/forms/display_settings_form.py
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QFormLayout, QLabel, 
    QLineEdit, QComboBox, QSpinBox, QPushButton,
    QGroupBox, QColorDialog, QFontDialog, QHBoxLayout, QCheckBox
)
from PySide6.QtGui import QColor, QFont
from PySide6.QtCore import Qt

class DisplaySettingsForm(QWidget):
    """فرم تنظیمات نمایش (تم، فونت، رنگ)"""
    
    def __init__(self, data_manager, config_manager=None):
        super().__init__()
        self.data_manager = data_manager
        self.config_manager = config_manager
        self.init_ui()
        self.load_settings()
    
    def init_ui(self):
        """ایجاد رابط کاربری"""
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # گروه تم و رنگ
        theme_group = QGroupBox("🎨 تنظیمات تم و رنگ")
        theme_layout = QFormLayout()
        
        # انتخاب تم
        self.cmb_theme = QComboBox()
        self.cmb_theme.addItems(["تاریک", "روشن", "آبی", "سبز"])
        self.cmb_theme.currentTextChanged.connect(self.on_theme_changed)
        
        # انتخاب رنگ متن
        color_text_layout = QHBoxLayout()
        self.txt_text_color = QLineEdit("#FFFFFF")
        self.txt_text_color.setReadOnly(True)
        self.btn_text_color = QPushButton("انتخاب رنگ")
        self.btn_text_color.clicked.connect(self.choose_text_color)
        
        color_text_layout.addWidget(self.txt_text_color)
        color_text_layout.addWidget(self.btn_text_color)
        
        # انتخاب رنگ پس‌زمینه
        color_bg_layout = QHBoxLayout()
        self.txt_bg_color = QLineEdit("#000000")
        self.txt_bg_color.setReadOnly(True)
        self.btn_bg_color = QPushButton("انتخاب رنگ")
        self.btn_bg_color.clicked.connect(self.choose_bg_color)
        
        color_bg_layout.addWidget(self.txt_bg_color)
        color_bg_layout.addWidget(self.btn_bg_color)
        
        theme_layout.addRow("تم:", self.cmb_theme)
        theme_layout.addRow("رنگ متن:", color_text_layout)
        theme_layout.addRow("رنگ پس‌زمینه:", color_bg_layout)
        
        theme_group.setLayout(theme_layout)
        main_layout.addWidget(theme_group)
        
        # گروه فونت
        font_group = QGroupBox("🔤 تنظیمات فونت")
        font_layout = QFormLayout()
        
        # انتخاب فونت
        font_select_layout = QHBoxLayout()
        self.txt_font_name = QLineEdit("B Nazanin")
        self.txt_font_name.setReadOnly(True)
        self.btn_choose_font = QPushButton("انتخاب فونت")
        self.btn_choose_font.clicked.connect(self.choose_font)
        
        font_select_layout.addWidget(self.txt_font_name)
        font_select_layout.addWidget(self.btn_choose_font)
        
        # سایز فونت
        self.spn_font_size = QSpinBox()
        self.spn_font_size.setRange(8, 20)
        self.spn_font_size.setValue(11)
        self.spn_font_size.setSuffix(" pt")
        
        # پیش‌نمایش فونت
        self.lbl_font_preview = QLabel("نمونه فونت: سیستم مدیریت تعمیرگاه شیروین")
        self.lbl_font_preview.setAlignment(Qt.AlignCenter)
        self.lbl_font_preview.setStyleSheet("""
            QLabel {
                padding: 10px;
                border: 1px solid #555;
                border-radius: 5px;
                background-color: #222;
            }
        """)
        
        font_layout.addRow("نام فونت:", font_select_layout)
        font_layout.addRow("سایز فونت:", self.spn_font_size)
        font_layout.addRow("پیش‌نمایش:", self.lbl_font_preview)
        
        font_group.setLayout(font_layout)
        main_layout.addWidget(font_group)
        
        # گروه نمایش تاریخ
        date_group = QGroupBox("📅 تنظیمات نمایش تاریخ")
        date_layout = QFormLayout()
        
        self.cmb_date_format = QComboBox()
        self.cmb_date_format.addItems([
            "شمسی (۱۴۰۳/۱۰/۱۵)",
            "میلادی (2025/01/05)",
            "مخلوط (۱۴۰۳-۱۰-۱۵)"
        ])
        
        self.chk_show_time = QCheckBox("نمایش ساعت")
        self.chk_show_time.setChecked(True)
        
        date_layout.addRow("فرمت تاریخ:", self.cmb_date_format)
        date_layout.addRow("", self.chk_show_time)
        
        date_group.setLayout(date_layout)
        main_layout.addWidget(date_group)
        
        # دکمه‌ها
        btn_layout = QHBoxLayout()
        
        self.btn_apply = QPushButton("💾 اعمال تنظیمات")
        self.btn_apply.clicked.connect(self.apply_settings)
        self.btn_apply.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
            }
        """)
        
        self.btn_preview = QPushButton("👁️ پیش‌نمایش")
        self.btn_preview.clicked.connect(self.preview_settings)
        
        self.btn_reset = QPushButton("🔄 بازنشانی")
        self.btn_reset.clicked.connect(self.reset_to_default)
        
        btn_layout.addWidget(self.btn_apply)
        btn_layout.addWidget(self.btn_preview)
        btn_layout.addWidget(self.btn_reset)
        btn_layout.addStretch()
        
        main_layout.addLayout(btn_layout)
        main_layout.addStretch()
        
        self.setLayout(main_layout)
    
    def choose_text_color(self):
        """انتخاب رنگ متن"""
        color = QColorDialog.getColor(QColor(self.txt_text_color.text()))
        if color.isValid():
            self.txt_text_color.setText(color.name())
    
    def choose_bg_color(self):
        """انتخاب رنگ پس‌زمینه"""
        color = QColorDialog.getColor(QColor(self.txt_bg_color.text()))
        if color.isValid():
            self.txt_bg_color.setText(color.name())
    
    def choose_font(self):
        """انتخاب فونت"""
        font, ok = QFontDialog.getFont()
        if ok:
            self.txt_font_name.setText(font.family())
            self.spn_font_size.setValue(font.pointSize())
    
    def on_theme_changed(self, theme_name):
        """وقتی تم تغییر کرد"""
        theme_colors = {
            "تاریک": {"bg": "#000000", "text": "#FFFFFF"},
            "روشن": {"bg": "#FFFFFF", "text": "#000000"},
            "آبی": {"bg": "#0d1b2a", "text": "#e0e1dd"},
            "سبز": {"bg": "#1b4332", "text": "#d8f3dc"}
        }
        
        if theme_name in theme_colors:
            colors = theme_colors[theme_name]
            self.txt_bg_color.setText(colors["bg"])
            self.txt_text_color.setText(colors["text"])
    
    def load_settings(self):
        """بارگذاری تنظیمات از config_manager"""
        try:
            if not self.config_manager:
                return
            
            # بارگذاری تنظیمات نمایش
            font_name = self.config_manager.get('display', 'font_family', 'B Nazanin')
            font_size = self.config_manager.get('display', 'font_size', 11)
            text_color = self.config_manager.get('display', 'text_color', '#FFFFFF')
            bg_color = self.config_manager.get('display', 'bg_color', '#000000')
            theme = self.config_manager.get('general', 'theme', 'dark')
            
            # تنظیم فیلدها
            self.txt_font_name.setText(font_name)
            self.spn_font_size.setValue(font_size)
            self.txt_text_color.setText(text_color)
            self.txt_bg_color.setText(bg_color)
            
            # تنظیم تم
            theme_map = {"dark": "تاریک", "light": "روشن", "blue": "آبی", "green": "سبز"}
            theme_display = theme_map.get(theme, "تاریک")
            index = self.cmb_theme.findText(theme_display)
            if index >= 0:
                self.cmb_theme.setCurrentIndex(index)
            
            # بارگذاری سایر تنظیمات
            date_format = self.config_manager.get('display', 'date_format', 'شمسی')
            if "شمسی" in date_format:
                self.cmb_date_format.setCurrentIndex(0)
            elif "میلادی" in date_format:
                self.cmb_date_format.setCurrentIndex(1)
            else:
                self.cmb_date_format.setCurrentIndex(2)
            
            show_time = self.config_manager.get('display', 'show_time', True)
            self.chk_show_time.setChecked(show_time)
            
            # بروزرسانی پیش‌نمایش
            self.update_preview()
            
        except Exception as e:
            print(f"⚠️ خطا در بارگذاری تنظیمات نمایش: {e}")
    
    def update_preview(self):
        """بروزرسانی پیش‌نمایش فونت"""
        font_family = self.txt_font_name.text()
        font_size = self.spn_font_size.value()
        text_color = self.txt_text_color.text()
        bg_color = self.txt_bg_color.text()
        
        style = f"""
            font-family: '{font_family}';
            font-size: {font_size}pt;
            color: {text_color};
            background-color: {bg_color};
        """
        
        self.lbl_font_preview.setStyleSheet(f"QLabel {{{style}}}")
    
    def preview_settings(self):
        """پیش‌نمایش تنظیمات"""
        self.update_preview()
    
    def reset_to_default(self):
        """بازنشانی به تنظیمات پیش‌فرض"""
        self.txt_font_name.setText("B Nazanin")
        self.spn_font_size.setValue(11)
        self.txt_text_color.setText("#FFFFFF")
        self.txt_bg_color.setText("#000000")
        self.cmb_theme.setCurrentText("تاریک")
        self.update_preview()
    
    def apply_settings(self):
        """اعمال تنظیمات"""
        try:
            if not self.config_manager:
                return False
            
            # جمع‌آوری تنظیمات
            settings = {
                'font_family': self.txt_font_name.text(),
                'font_size': self.spn_font_size.value(),
                'text_color': self.txt_text_color.text(),
                'bg_color': self.txt_bg_color.text(),
                'show_time': self.chk_show_time.isChecked()
            }
            
            # تنظیم تم
            theme_map = {"تاریک": "dark", "روشن": "light", "آبی": "blue", "سبز": "green"}
            theme = theme_map.get(self.cmb_theme.currentText(), "dark")
            
            # تنظیم فرمت تاریخ
            date_format_index = self.cmb_date_format.currentIndex()
            date_formats = ["شمسی", "میلادی", "مخلوط"]
            settings['date_format'] = date_formats[date_format_index]
            
            # ذخیره در config_manager
            for key, value in settings.items():
                self.config_manager.set('display', key, value, save_to_db=True)
            
            # ذخیره تم در تنظیمات عمومی
            self.config_manager.set('general', 'theme', theme, save_to_db=True)
            
            print("✅ تنظیمات نمایش ذخیره شد")
            return True
            
        except Exception as e:
            print(f"⚠️ خطا در اعمال تنظیمات نمایش: {e}")
            return False
    
    def get_settings(self):
        """دریافت تنظیمات از فرم"""
        return {
            'font_family': self.txt_font_name.text(),
            'font_size': self.spn_font_size.value(),
            'text_color': self.txt_text_color.text(),
            'bg_color': self.txt_bg_color.text(),
            'date_format': self.cmb_date_format.currentText(),
            'show_time': self.chk_show_time.isChecked()
        }