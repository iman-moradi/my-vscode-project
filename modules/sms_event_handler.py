# modules/sms_event_handler.py
from datetime import datetime, timedelta
from typing import Optional

class SMSEventHandler:
    """مدیریت رویدادهای سیستم و ارسال پیامک خودکار"""
    
    def __init__(self, sms_service, data_manager):
        self.sms_service = sms_service
        self.data_manager = data_manager
        self.event_handlers = {
            'reception_created': self.on_reception_created,
            'repair_started': self.on_repair_started,
            'repair_completed': self.on_repair_completed,
            'device_ready': self.on_device_ready,
            'cheque_due_soon': self.on_cheque_due_soon,
            'low_stock_alert': self.on_low_stock_alert,
        }
    
    def handle_event(self, event_name: str, event_data: dict) -> bool:
        """پردازش یک رویداد سیستم"""
        if event_name in self.event_handlers:
            try:
                return self.event_handlers[event_name](event_data)
            except Exception as e:
                print(f"خطا در پردازش رویداد {event_name}: {e}")
                return False
        return False
    
    def on_reception_created(self, data: dict) -> bool:
        """وقتی پذیرش جدیدی ثبت شد"""
        # دریافت اطلاعات از دیتابیس
        reception = self.data_manager.get_reception_by_id(data.get('reception_id'))
        if not reception or not reception.customer.mobile:
            return False
        
        customer = reception.customer
        device = reception.device
        
        # ارسال پیامک خوش‌آمدگویی
        return self.sms_service.send_auto_sms(
            pattern_name='on_reception',
            phone_number=customer.mobile,
            parameters={
                'customer_name': customer.first_name or 'مشتری گرامی',
                'device_name': device.device_type,
                'reception_number': reception.reception_number,
                'estimated_time': '۲۴-۴۸ ساعت'  # زمان تخمینی تعمیر
            }
        )
    
    def on_repair_started(self, data: dict) -> bool:
        """وقتی تعمیر شروع شد"""
        repair = self.data_manager.get_repair_by_id(data.get('repair_id'))
        if not repair:
            return False
        
        reception = repair.reception
        customer = reception.customer
        
        # ارسال پیامک اطلاع‌رسانی شروع تعمیر
        message = f"""
        مشتری گرامی {customer.first_name}،
        تعمیر دستگاه شما آغاز شد.
        تعمیرکار: {repair.technician_name or 'تعمیرکار مرکز'}
        شماره پیگیری: {reception.reception_number}
        """
        
        return self.sms_manager.send_single_sms(
            to_number=customer.mobile,
            message=message.strip()
        )
    
    def on_repair_completed(self, data: dict) -> bool:
        """وقتی تعمیر تمام شد"""
        repair = self.data_manager.get_repair_by_id(data.get('repair_id'))
        if not repair:
            return False
        
        reception = repair.reception
        customer = reception.customer
        
        return self.sms_service.send_auto_sms(
            pattern_name='on_repair_complete',
            phone_number=customer.mobile,
            parameters={
                'customer_name': customer.first_name,
                'reception_number': reception.reception_number,
                'final_cost': f"{repair.total_cost:,} تومان",
                'ready_time': datetime.now().strftime("%H:%M")
            }
        )
    
    def on_device_ready(self, data: dict) -> bool:
        """وقتی دستگاه آماده تحویل است"""
        reception = self.data_manager.get_reception_by_id(data.get('reception_id'))
        if not reception:
            return False
        
        # ارسال پیامک یادآوری تحویل (اگر بعد از 24 ساعت تحویل گرفته نشد)
        if reception.status == 'تعمیر شده' and reception.ready_since:
            ready_time = datetime.fromisoformat(reception.ready_since)
            if datetime.now() - ready_time > timedelta(hours=24):
                return self.sms_service.send_auto_sms(
                    pattern_name='on_delivery',
                    phone_number=reception.customer.mobile,
                    parameters={
                        'customer_name': reception.customer.first_name,
                        'device_name': reception.device.device_type,
                        'days_passed': '۱ روز'
                    }
                )
        return False
    
    def on_cheque_due_soon(self, data: dict) -> bool:
        """یادآوری سررسید چک (3 روز قبل)"""
        cheque = self.data_manager.get_cheque_by_id(data.get('cheque_id'))
        if not cheque or not cheque.related_customer:
            return False
        
        due_date = datetime.fromisoformat(cheque.due_date)
        days_until_due = (due_date - datetime.now()).days
        
        if 1 <= days_until_due <= 3:  # فقط 1-3 روز قبل از سررسید
            message = f"""
            یادآوری سررسید چک
            مبلغ: {cheque.amount:,} تومان
            تاریخ سررسید: {due_date.strftime('%Y/%m/%d')}
            شماره چک: {cheque.cheque_number}
            """
            
            return self.sms_manager.send_single_sms(
                to_number=cheque.related_customer.mobile,
                message=message.strip()
            )
        return False
    
    def on_low_stock_alert(self, data: dict) -> bool:
        """هشدار موجودی کم به مدیران"""
        # دریافت لیست مدیران از دیتابیس
        admins = self.data_manager.get_users_by_role('مدیر سیستم')
        
        item = data.get('item')
        current_stock = data.get('current_stock')
        min_stock = data.get('min_stock')
        
        message = f"""
        ⚠️ هشدار موجودی کم
        کالا: {item.part_name}
        موجودی فعلی: {current_stock}
        حداقل موجودی: {min_stock}
        انبار: {item.warehouse_type}
        """
        
        success_count = 0
        for admin in admins:
            if admin.person and admin.person.mobile:
                result = self.sms_manager.send_single_sms(
                    to_number=admin.person.mobile,
                    message=message.strip()
                )
                if result.get('success'):
                    success_count += 1
        
        return success_count > 0
    
    def schedule_daily_reminders(self):
        """برنامه‌ریزی یادآوری‌های روزانه"""
        # این تابع باید توسط یک scheduler (مثل APScheduler) صدا زده شود
        
        # 1. یادآوری دستگاه‌های آماده تحویل
        ready_receptions = self.data_manager.get_ready_for_delivery()
        for reception in ready_receptions:
            self.on_device_ready({'reception_id': reception.id})
        
        # 2. یادآوری چک‌های فردا سررسید می‌شوند
        tomorrow_cheques = self.data_manager.get_cheques_due_tomorrow()
        for cheque in tomorrow_cheques:
            self.on_cheque_due_soon({'cheque_id': cheque.id})
        
        # 3. یادآوری قرارهای ملاقات فردا
        tomorrow_appointments = self.data_manager.get_appointments_tomorrow()
        for appointment in tomorrow_appointments:
            self.send_appointment_reminder(appointment)
    
    def send_appointment_reminder(self, appointment):
        """ارسال یادآوری قرار ملاقات"""
        message = f"""
        یادآوری قرار ملاقات
        تاریخ: {appointment.date}
        ساعت: {appointment.time}
        موضوع: {appointment.subject}
        لطفاً راس ساعت مراجعه فرمایید.
        """
        
        return self.sms_manager.send_single_sms(
            to_number=appointment.customer.mobile,
            message=message.strip()
        )