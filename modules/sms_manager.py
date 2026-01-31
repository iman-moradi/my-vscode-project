# modules/sms_manager.py
import requests
import json
from datetime import datetime
from typing import Dict, List, Optional, Tuple

class SMSManager:
    """مدیریت مرکزی ارسال و دریافت پیامک"""
    
    # تنظیمات پیش‌فرض برای اتصال به API ملی پیامک (به عنوان مثال)
    DEFAULT_API_URL = "https://api.melipayamak.com"
    
    def __init__(self, data_manager, api_key: str = None, api_url: str = None):
        self.data_manager = data_manager
        self.api_key = api_key
        self.api_url = api_url or self.DEFAULT_API_URL
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
    
    def send_single_sms(self, to_number: str, message: str, 
                        line_number: str = None) -> Dict:
        """
        ارسال یک پیامک به یک شماره
        
        Args:
            to_number: شماره گیرنده (با پیش‌شماره 98)
            message: متن پیامک
            line_number: شماره خط اختصاصی
        
        Returns:
            دیکشنری حاوی نتیجه عملیات
        """
        try:
            # آماده‌سازی پارامترها برای API ملی پیامک
            # (مستندات هر پنل متفاوت است، این یک نمونه است)
            payload = {
                'username': self.api_key,  # یا 'apiKey' بسته به پنل
                'from': line_number or self._get_default_line(),
                'to': to_number,
                'text': message,
                'isFlash': False  # پیامک عادی، نه فلش
            }
            
            # ارسال درخواست POST به API[citation:7][citation:10]
            response = self.session.post(
                f"{self.api_url}/api/send/simple",
                json=payload,
                timeout=10
            )
            
            result = response.json()
            
            # ذخیره در تاریخچه
            self._save_to_history(
                to_number=to_number,
                message=message,
                status='ارسال شده' if result.get('status') == 1 else 'ناموفق',
                message_id=result.get('messageId'),
                response=result
            )
            
            return {
                'success': result.get('status') == 1,
                'message_id': result.get('messageId'),
                'status_code': result.get('status'),
                'message': result.get('message', ''),
                'raw_response': result
            }
            
        except requests.exceptions.Timeout:
            return {'success': False, 'error': 'Timeout: اتصال به سرور پیامکی timed out'}
        except requests.exceptions.ConnectionError:
            return {'success': False, 'error': 'ConnectionError: خطا در اتصال به اینترنت'}
        except Exception as e:
            return {'success': False, 'error': f'خطای ناشناخته: {str(e)}'}
    
    def send_bulk_sms(self, numbers: List[str], message: str, 
                      line_number: str = None) -> Dict:
        """ارسال پیامک به چندین شماره"""
        # پیاده‌سازی مشابه send_single_sms اما با لیست شماره‌ها
        pass
    
    def send_pattern_sms(self, pattern_code: str, to_number: str, 
                         parameters: Dict) -> Dict:
        """ارسال پیامک با قالب (پترن) - برای کد تایید OTP"""
        # مناسب برای پیام‌های خودکار مانند کد تایید[citation:1][citation:8]
        pass
    
    def get_delivery_status(self, message_id: str) -> Dict:
        """بررسی وضعیت تحویل پیامک"""
        pass
    
    def get_credit(self) -> float:
        """دریافت اعتبار باقی‌مانده پنل"""
        try:
            response = self.session.post(
                f"{self.api_url}/api/credit",
                json={'apiKey': self.api_key}
            )
            return response.json().get('credit', 0)
        except:
            return 0
    
    def _save_to_history(self, to_number: str, message: str, 
                         status: str, message_id: str, response: Dict):
        """ذخیره پیامک در تاریخچه"""
        try:
            from database.models import Message
            msg = Message(
                message_type='ارسال دستی',
                message_text=message,
                mobile_number=to_number,
                send_status=status,
                response_data=json.dumps(response),
                message_id=message_id,
                sent_at=datetime.now()
            )
            self.data_manager.add(msg)
        except Exception as e:
            print(f"خطا در ذخیره تاریخچه پیامک: {e}")
    
    def _get_default_line(self) -> str:
        """دریافت شماره خط پیش‌فرض از تنظیمات"""
        # دریافت از دیتابیس یا فایل config
        return "5000xxx"  # شماره خط نمونه