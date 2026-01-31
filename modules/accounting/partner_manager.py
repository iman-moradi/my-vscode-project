# modules/accounting/partner_manager.py
"""
مدیریت شرکا و محاسبه سود
"""

from PySide6.QtCore import QObject, Signal
import jdatetime
from datetime import datetime

class PartnerManager(QObject):
    """مدیریت کامل شرکا و سود"""
    
    data_changed = Signal(str)
    
    def __init__(self, data_manager):
        super().__init__()
        self.data_manager = data_manager
        self.db = data_manager.db
    
    # ---------- مدیریت شرکا ----------
    
    def create_partner(self, partner_data):
        """افزودن شریک جدید"""
        try:
            # اعتبارسنجی
            person_id = partner_data.get('person_id')
            if not person_id:
                return False, "شخص باید مشخص شود"
            
            # بررسی تکراری نبودن
            existing = self.db.fetch_one(
                "SELECT id FROM Partners WHERE person_id = ? AND active = 1",
                (person_id,)
            )
            if existing:
                return False, "این شخص قبلاً به عنوان شریک فعال ثبت شده است"
            
            # تاریخ‌ها
            start_date = partner_data.get('partnership_start')
            end_date = partner_data.get('partnership_end')
            
            if start_date:
                start_date = self.db.jalali_to_gregorian(start_date)
            else:
                start_date = datetime.now().strftime("%Y-%m-%d")
            
            if end_date:
                end_date = self.db.jalali_to_gregorian(end_date)
            
            query = """
            INSERT INTO Partners (
                person_id, partnership_start, partnership_end,
                active, capital, profit_percentage, description
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """
            
            # تبدیل سرمایه به ریال
            capital = float(partner_data.get('capital', 0)) * 10
            
            params = (
                person_id,
                start_date,
                end_date,
                partner_data.get('active', 1),
                capital,
                float(partner_data.get('profit_percentage', 0)),
                partner_data.get('description', '')
            )
            
            success = self.db.execute_query(query, params)
            
            if success:
                self.data_changed.emit("Partners")
                return True, "شریک با موفقیت ثبت شد"
            return False, "خطا در ثبت شریک"
            
        except Exception as e:
            return False, f"خطا: {str(e)}"
    
    def get_all_partners(self, active_only=True):
        """دریافت تمام شرکا"""
        if active_only:
            query = """
            SELECT 
                p.*,
                per.first_name || ' ' || per.last_name as partner_name,
                per.mobile, per.phone,
                (SELECT SUM(share_amount) FROM PartnerShares ps WHERE ps.partner_id = p.id) as total_profit
            FROM Partners p
            JOIN Persons per ON p.person_id = per.id
            WHERE p.active = 1
            ORDER BY p.partnership_start DESC
            """
        else:
            query = """
            SELECT 
                p.*,
                per.first_name || ' ' || per.last_name as partner_name,
                per.mobile, per.phone,
                (SELECT SUM(share_amount) FROM PartnerShares ps WHERE ps.partner_id = p.id) as total_profit
            FROM Partners p
            JOIN Persons per ON p.person_id = per.id
            ORDER BY p.active DESC, p.partnership_start DESC
            """
        
        partners = self.db.fetch_all(query)
        
        # تبدیل تاریخ‌ها و مبالغ
        for partner in partners:
            partner['partnership_start_shamsi'] = self.db.gregorian_to_jalali(partner['partnership_start'])
            
            if partner['partnership_end']:
                partner['partnership_end_shamsi'] = self.db.gregorian_to_jalali(partner['partnership_end'])
            
            partner['capital_toman'] = partner['capital'] / 10 if partner['capital'] else 0
            partner['total_profit_toman'] = partner['total_profit'] / 10 if partner['total_profit'] else 0
        
        return partners
    
    def get_partner_by_id(self, partner_id):
        """دریافت شریک با شناسه"""
        query = """
        SELECT 
            p.*,
            per.first_name || ' ' || per.last_name as partner_name,
            per.mobile, per.phone, per.address, per.national_id
        FROM Partners p
        JOIN Persons per ON p.person_id = per.id
        WHERE p.id = ?
        """
        
        partner = self.db.fetch_one(query, (partner_id,))
        
        if partner:
            partner['partnership_start_shamsi'] = self.db.gregorian_to_jalali(partner['partnership_start'])
            
            if partner['partnership_end']:
                partner['partnership_end_shamsi'] = self.db.gregorian_to_jalali(partner['partnership_end'])
            
            partner['capital_toman'] = partner['capital'] / 10 if partner['capital'] else 0
        
        return partner
    
    def update_partner(self, partner_id, partner_data):
        """ویرایش اطلاعات شریک"""
        try:
            # تاریخ‌ها
            start_date = partner_data.get('partnership_start')
            end_date = partner_data.get('partnership_end')
            
            if start_date:
                start_date = self.db.jalali_to_gregorian(start_date)
            
            if end_date:
                end_date = self.db.jalali_to_gregorian(end_date)
            
            query = """
            UPDATE Partners SET
                partnership_start = ?,
                partnership_end = ?,
                active = ?,
                capital = ?,
                profit_percentage = ?,
                description = ?
            WHERE id = ?
            """
            
            # تبدیل سرمایه به ریال
            capital = float(partner_data.get('capital', 0)) * 10
            
            params = (
                start_date,
                end_date,
                partner_data.get('active', 1),
                capital,
                float(partner_data.get('profit_percentage', 0)),
                partner_data.get('description', ''),
                partner_id
            )
            
            success = self.db.execute_query(query, params)
            
            if success:
                self.data_changed.emit("Partners")
                return True, "اطلاعات شریک با موفقیت ویرایش شد"
            return False, "خطا در ویرایش اطلاعات شریک"
            
        except Exception as e:
            return False, f"خطا: {str(e)}"
    
    def deactivate_partner(self, partner_id):
        """غیرفعال کردن شریک"""
        query = "UPDATE Partners SET active = 0 WHERE id = ?"
        success = self.db.execute_query(query, (partner_id,))
        
        if success:
            self.data_changed.emit("Partners")
            return True, "شریک غیرفعال شد"
        return False, "خطا در غیرفعال کردن شریک"
    
    # ---------- مدیریت سود شرکا ----------
    
    def calculate_partner_profit(self, transaction_type, transaction_id, total_amount):
        """محاسبه سود شرکا از یک تراکنش"""
        try:
            # دریافت شرکای فعال
            partners = self.get_all_partners(active_only=True)
            if not partners:
                return True, "هیچ شریک فعالی وجود ندارد"
            
            # محاسبه سهم بر اساس درصد سود هر شریک
            total_percentage = sum(partner.get('profit_percentage', 0) for partner in partners)
            
            if total_percentage == 0:
                # تقسیم مساوی
                share_percentage = 100.0 / len(partners)
                for partner in partners:
                    partner['share_percentage'] = share_percentage
            else:
                # تقسیم بر اساس درصد تعیین شده
                for partner in partners:
                    partner['share_percentage'] = partner.get('profit_percentage', 0)
            
            # ثبت سهم‌ها
            for partner in partners:
                share_amount = total_amount * (partner['share_percentage'] / 100)
                
                query = """
                INSERT INTO PartnerShares (
                    partner_id, transaction_type, transaction_id,
                    share_percentage, share_amount, calculation_date, description
                ) VALUES (?, ?, ?, ?, ?, datetime('now'), ?)
                """
                
                params = (
                    partner['id'],
                    transaction_type,
                    transaction_id,
                    partner['share_percentage'],
                    share_amount,
                    f"سهم از {transaction_type} #{transaction_id}"
                )
                
                self.db.execute_query(query, params)
            
            self.data_changed.emit("PartnerShares")
            return True, f"سود برای {len(partners)} شریک محاسبه شد"
            
        except Exception as e:
            return False, f"خطا در محاسبه سود: {str(e)}"
    
    def get_partner_profits(self, partner_id, start_date=None, end_date=None):
        """دریافت سودهای یک شریک"""
        query = """
        SELECT 
            ps.*,
            CASE 
                WHEN ps.transaction_type LIKE '%فاکتور%' THEN i.invoice_number
                WHEN ps.transaction_type LIKE '%چک%' THEN c.check_number
                ELSE 'سایر'
            END as transaction_ref
        FROM PartnerShares ps
        LEFT JOIN Invoices i ON ps.transaction_type LIKE '%فاکتور%' AND ps.transaction_id = i.id
        LEFT JOIN Checks c ON ps.transaction_type LIKE '%چک%' AND ps.transaction_id = c.id
        WHERE ps.partner_id = ?
        """
        
        params = [partner_id]
        
        if start_date:
            query += " AND DATE(ps.calculation_date) >= ?"
            params.append(start_date)
        
        if end_date:
            query += " AND DATE(ps.calculation_date) <= ?"
            params.append(end_date)
        
        query += " ORDER BY ps.calculation_date DESC"
        
        profits = self.db.fetch_all(query, params)
        
        # تبدیل تاریخ‌ها و مبالغ
        for profit in profits:
            profit['calculation_date_shamsi'] = self.db.gregorian_to_jalali(profit['calculation_date'])
            profit['share_amount_toman'] = profit['share_amount'] / 10
        
        return profits
    
    def get_profit_summary(self, start_date=None, end_date=None):
        """خلاصه سود شرکا"""
        query = """
        SELECT 
            p.id,
            per.first_name || ' ' || per.last_name as partner_name,
            COUNT(ps.id) as transaction_count,
            SUM(ps.share_amount) as total_profit,
            AVG(ps.share_percentage) as avg_percentage
        FROM Partners p
        JOIN Persons per ON p.person_id = per.id
        LEFT JOIN PartnerShares ps ON p.id = ps.partner_id
        WHERE p.active = 1
        """
        
        params = []
        
        if start_date:
            query += " AND DATE(ps.calculation_date) >= ?"
            params.append(start_date)
        
        if end_date:
            query += " AND DATE(ps.calculation_date) <= ?"
            params.append(end_date)
        
        query += """
        GROUP BY p.id, partner_name
        ORDER BY total_profit DESC
        """
        
        summary = self.db.fetch_all(query, params)
        
        # تبدیل مبالغ به تومان
        for item in summary:
            item['total_profit_toman'] = item['total_profit'] / 10 if item['total_profit'] else 0
        
        return summary
    
    def distribute_monthly_profit(self, month=None, year=None):
        """توزیع سود ماهانه بین شرکا"""
        try:
            if not month or not year:
                today = jdatetime.datetime.now()
                month = today.month
                year = today.year
            
            # محدوده ماه شمسی
            start_jalali = f"{year}/{month:02d}/01"
            end_jalali = f"{year}/{month:02d}/31"
            
            start_gregorian = self.db.jalali_to_gregorian(start_jalali)
            end_gregorian = self.db.jalali_to_gregorian(end_jalali)
            
            # دریافت کل درآمد ماه
            query = """
            SELECT SUM(total) as total_income
            FROM Invoices
            WHERE invoice_type IN ('فروش', 'خدمات')
            AND DATE(invoice_date) BETWEEN ? AND ?
            AND payment_status != 'پرداخت نشده'
            """
            
            result = self.db.fetch_one(query, (start_gregorian, end_gregorian))
            total_income = result.get('total_income', 0) if result else 0
            
            if total_income <= 0:
                return False, "درآمدی برای توزیع وجود ندارد"
            
            # محاسبه سود قابل توزیع (مثلاً 70% درآمد)
            distributable_profit = total_income * 0.7
            
            # دریافت شرکا
            partners = self.get_all_partners(active_only=True)
            if not partners:
                return False, "هیچ شریک فعالی وجود ندارد"
            
            # توزیع بر اساس سرمایه یا درصد تعیین شده
            total_capital = sum(partner.get('capital', 0) for partner in partners)
            
            if total_capital > 0:
                # توزیع بر اساس سرمایه
                for partner in partners:
                    share_percentage = (partner.get('capital', 0) / total_capital) * 100
                    share_amount = distributable_profit * (share_percentage / 100)
                    
                    # ثبت سهم
                    self._record_profit_distribution(
                        partner['id'], 
                        share_amount, 
                        share_percentage,
                        f"توزیع سود ماهانه {year}/{month:02d}"
                    )
            else:
                # توزیع بر اساس درصد سود تعیین شده
                total_percentage = sum(partner.get('profit_percentage', 0) for partner in partners)
                
                if total_percentage > 0:
                    for partner in partners:
                        share_percentage = partner.get('profit_percentage', 0)
                        share_amount = distributable_profit * (share_percentage / 100)
                        
                        self._record_profit_distribution(
                            partner['id'], 
                            share_amount, 
                            share_percentage,
                            f"توزیع سود ماهانه {year}/{month:02d}"
                        )
                else:
                    # توزیع مساوی
                    share_percentage = 100.0 / len(partners)
                    share_amount = distributable_profit * (share_percentage / 100)
                    
                    for partner in partners:
                        self._record_profit_distribution(
                            partner['id'], 
                            share_amount, 
                            share_percentage,
                            f"توزیع سود ماهانه {year}/{month:02d}"
                        )
            
            self.data_changed.emit("PartnerShares")
            
            month_name = self._get_persian_month_name(month)
            return True, f"سود ماه {month_name} {year} بین {len(partners)} شریک توزیع شد"
            
        except Exception as e:
            return False, f"خطا در توزیع سود: {str(e)}"
    
    def _record_profit_distribution(self, partner_id, share_amount, share_percentage, description):
        """ثبت توزیع سود"""
        query = """
        INSERT INTO PartnerShares (
            partner_id, transaction_type, transaction_id,
            share_percentage, share_amount, calculation_date, description
        ) VALUES (?, ?, ?, ?, ?, datetime('now'), ?)
        """
        
        params = (
            partner_id,
            'توزیع سود',
            0,  # transaction_id برای توزیع سود 0 است
            share_percentage,
            share_amount,
            description
        )
        
        self.db.execute_query(query, params)
    
    def _get_persian_month_name(self, month):
        """نام ماه فارسی"""
        months = {
            1: "فروردین", 2: "اردیبهشت", 3: "خرداد",
            4: "تیر", 5: "مرداد", 6: "شهریور",
            7: "مهر", 8: "آبان", 9: "آذر",
            10: "دی", 11: "بهمن", 12: "اسفند"
        }
        return months.get(month, "")
    
    def get_profit_trend(self, months=6):
        """روند سوددهی در ماه‌های اخیر"""
        import datetime as dt
        
        end_date = dt.datetime.now()
        start_date = end_date - dt.timedelta(days=30*months)
        
        query = """
        SELECT 
            strftime('%Y-%m', calculation_date) as month,
            COUNT(*) as transaction_count,
            SUM(share_amount) as total_profit,
            AVG(share_percentage) as avg_percentage
        FROM PartnerShares
        WHERE calculation_date BETWEEN ? AND ?
        GROUP BY strftime('%Y-%m', calculation_date)
        ORDER BY month
        """
        
        trend = self.db.fetch_all(query, (start_date, end_date))
        
        # تبدیل تاریخ به شمسی و مبالغ به تومان
        for item in trend:
            # تبدیل نام ماه میلادی به شمسی
            year_month = item['month'].split('-')
            if len(year_month) == 2:
                year, month = map(int, year_month)
                # تقریباً 621 سال تفاوت
                jalali_year = year - 621
                month_name = self._get_persian_month_name(month)
                item['month_name'] = f"{month_name} {jalali_year}"
            
            item['total_profit_toman'] = item['total_profit'] / 10 if item['total_profit'] else 0
        
        return trend