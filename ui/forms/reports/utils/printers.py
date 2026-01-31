"""
ماژول چاپ گزارش‌ها
"""

from PySide6.QtPrintSupport import QPrinter, QPrintDialog, QPrintPreviewDialog
from PySide6.QtWidgets import QMessageBox
from PySide6.QtGui import QPainter
from PySide6.QtCore import Qt
import tempfile
import os


class ReportPrinter:
    """کلاس مدیریت چاپ گزارش‌ها"""
    
    def __init__(self, parent=None):
        self.parent = parent
    
    def print_html(self, html_content, title="گزارش"):
        """چاپ محتوای HTML"""
        try:
            printer = QPrinter(QPrinter.HighResolution)
            printer.setFullPage(True)
            printer.setPageOrientation(QPrinter.Portrait)
            printer.setDocName(title)
            
            # ذخیره موقت HTML در فایل
            with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False, encoding='utf-8') as f:
                f.write(html_content)
                temp_file = f.name
            
            # استفاده از QTextDocument برای چاپ
            from PySide6.QtGui import QTextDocument
            document = QTextDocument()
            document.setHtml(html_content)
            
            print_dialog = QPrintDialog(printer, self.parent)
            if print_dialog.exec_() == QPrintDialog.Accepted:
                document.print_(printer)
            
            # حذف فایل موقت
            os.unlink(temp_file)
            
            return True
            
        except Exception as e:
            QMessageBox.critical(
                self.parent,
                "خطا در چاپ",
                f"خطا در چاپ گزارش: {str(e)}"
            )
            return False
    
    def print_preview(self, html_content, title="گزارش"):
        """پیش‌نمایش چاپ"""
        try:
            from PySide6.QtGui import QTextDocument
            
            printer = QPrinter(QPrinter.HighResolution)
            printer.setFullPage(True)
            printer.setPageOrientation(QPrinter.Portrait)
            printer.setDocName(title)
            
            document = QTextDocument()
            document.setHtml(html_content)
            
            preview_dialog = QPrintPreviewDialog(printer, self.parent)
            preview_dialog.setWindowTitle(f"پیش‌نمایش چاپ - {title}")
            
            def print_preview_func(printer):
                document.print_(printer)
            
            preview_dialog.paintRequested.connect(print_preview_func)
            preview_dialog.exec_()
            
            return True
            
        except Exception as e:
            QMessageBox.critical(
                self.parent,
                "خطا در پیش‌نمایش",
                f"خطا در پیش‌نمایش چاپ: {str(e)}"
            )
            return False
    
    def export_to_pdf(self, html_content, file_path, title="گزارش"):
        """خروجی به PDF"""
        try:
            printer = QPrinter(QPrinter.HighResolution)
            printer.setOutputFormat(QPrinter.PdfFormat)
            printer.setOutputFileName(file_path)
            printer.setDocName(title)
            printer.setFullPage(True)
            printer.setPageOrientation(QPrinter.Portrait)
            
            from PySide6.QtGui import QTextDocument
            document = QTextDocument()
            document.setHtml(html_content)
            document.print_(printer)
            
            QMessageBox.information(
                self.parent,
                "ذخیره PDF",
                f"فایل PDF با موفقیت ذخیره شد:\n{file_path}"
            )
            return True
            
        except Exception as e:
            QMessageBox.critical(
                self.parent,
                "خطا در ذخیره PDF",
                f"خطا در ذخیره فایل PDF: {str(e)}"
            )
            return False