# services/sms_service.py
import threading
import time
from datetime import datetime
from typing import List
from queue import Queue

class SMSService:
    """سرویس ارسال خودکار پیامک‌ها"""
    
    def __init__(self, sms_manager, data_manager):
        self.sms_manager = sms_manager
        self.data_manager = data_manager
        self.message_queue = Queue()
        self.is_running = False
        self.worker_thread = None
        
        # الگوهای ارسال خودکار
        self.auto_patterns = {
            'on_reception': "مشتری گرامی {customer_name}، دستگاه {device_name} شما با شماره پذیرش {reception_number} ثبت شد.",
            'on_repair_complete': "مشتری گرامی {customer_name}، دستگاه شما آماده تحویل است. لطفا مراجعه فرمایید.",
            'on_delivery': "با تشکر از اعتماد شما، امیدواریم از خدمات ما راضی بوده باشید.",
            'payment_reminder': "مشتری گرامی، لطفاً جهت تسویه حساب فاکتور شماره {invoice_number} اقدام فرمایید."
        }
    
    def start(self):
        """شروع سرویس ارسال خودکار"""
        if not self.is_running:
            self.is_running = True
            self.worker_thread = threading.Thread(target=self._process_queue, daemon=True)
            self.worker_thread.start()
            print("سرویس پیامک خودکار شروع به کار کرد.")
    
    def stop(self):
        """توقف سرویس"""
        self.is_running = False
        if self.worker_thread:
            self.worker_thread.join(timeout=5)
        print("سرویس پیامک خودکار متوقف شد.")
    
    def send_auto_sms(self, pattern_name: str, phone_number: str, 
                      parameters: dict) -> bool:
        """
        ارسال خودکار پیامک بر اساس الگو
        
        Args:
            pattern_name: نام الگو از auto_patterns
            phone_number: شماره گیرنده
            parameters: پارامترهای جایگزین در الگو
        """
        if pattern_name not in self.auto_patterns:
            return False
        
        template = self.auto_patterns[pattern_name]
        message = template.format(**parameters)
        
        # اضافه به صف ارسال
        self.message_queue.put({
            'type': 'auto',
            'pattern': pattern_name,
            'phone': phone_number,
            'message': message,
            'parameters': parameters,
            'timestamp': datetime.now()
        })
        
        return True
    
    def _process_queue(self):
        """پردازش صف پیامک‌ها"""
        while self.is_running:
            try:
                if not self.message_queue.empty():
                    sms_data = self.message_queue.get()
                    
                    # ارسال پیامک
                    result = self.sms_manager.send_single_sms(
                        to_number=sms_data['phone'],
                        message=sms_data['message']
                    )
                    
                    # ذخیره لاگ
                    self._log_auto_sms(sms_data, result)
                    
                    # تاخیر برای عدم ارسال سریع
                    time.sleep(2)
                else:
                    time.sleep(1)
                    
            except Exception as e:
                print(f"خطا در پردازش صف پیامک: {e}")
                time.sleep(5)
    
    def _log_auto_sms(self, sms_data: dict, result: dict):
        """ذخیره لاگ پیامک خودکار"""
        try:
            from database.models import Message
            msg = Message(
                message_type=f"خودکار - {sms_data['pattern']}",
                message_text=sms_data['message'],
                mobile_number=sms_data['phone'],
                send_status='ارسال شده' if result.get('success') else 'ناموفق',
                response_data=str(result),
                sent_at=sms_data['timestamp']
            )
            self.data_manager.add(msg)
        except Exception as e:
            print(f"خطا در ذخیره لاگ پیامک خودکار: {e}")
    
    def check_and_send_reminders(self):
        """بررسی و ارسال یادآوری‌ها"""
        # این متد می‌تواند توسط یک کرون جاب صدا زده شود
        # برای ارسال یادآوری سررسید چک‌ها، فاکتورها و غیره
        pass