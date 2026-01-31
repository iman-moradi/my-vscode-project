# modules/accounting/financial_calculator.py
"""
ماژول محاسبات مالی پیشرفته
محاسبه سود و زیان، مالیات، تخفیف، سود شرکا و تحلیل‌های مالی
"""

import jdatetime
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import statistics


class FinancialCalculator:
    """کلاس محاسبات مالی پیشرفته"""
    
    def __init__(self, data_manager):
        """
        مقداردهی اولیه ماشین حساب مالی
        
        Args:
            data_manager: شیء مدیریت داده‌ها
        """
        self.data_manager = data_manager
        
    # ==================== محاسبات عمومی ====================
    
    def calculate_tax(self, amount: float, tax_percentage: float = 9) -> Dict[str, float]:
        """
        محاسبه مالیات و عوارض
        
        Args:
            amount: مبلغ پایه
            tax_percentage: درصد مالیات (پیش‌فرض 9%)
            
        Returns:
            dict: شامل مبلغ مالیات و مبلغ کل
        """
        try:
            tax_amount = (amount * tax_percentage) / 100
            total_amount = amount + tax_amount
            
            return {
                'base_amount': amount,
                'tax_percentage': tax_percentage,
                'tax_amount': tax_amount,
                'total_amount': total_amount
            }
        except Exception as e:
            print(f"❌ خطا در محاسبه مالیات: {e}")
            return {'base_amount': amount, 'tax_amount': 0, 'total_amount': amount}
    
    def calculate_discount(self, amount: float, discount_percentage: float = 0, 
                          discount_amount: float = 0) -> Dict[str, float]:
        """
        محاسبه تخفیف
        
        Args:
            amount: مبلغ اولیه
            discount_percentage: درصد تخفیف
            discount_amount: مبلغ ثابت تخفیف
            
        Returns:
            dict: شامل مبلغ تخفیف و مبلغ نهایی
        """
        try:
            if discount_percentage > 0:
                discount = (amount * discount_percentage) / 100
            else:
                discount = discount_amount
            
            # تخفیف نمی‌تواند بیشتر از مبلغ باشد
            discount = min(discount, amount)
            final_amount = amount - discount
            
            return {
                'original_amount': amount,
                'discount_percentage': discount_percentage,
                'discount_amount': discount,
                'final_amount': final_amount,
                'discount_rate': (discount / amount * 100) if amount > 0 else 0
            }
        except Exception as e:
            print(f"❌ خطا در محاسبه تخفیف: {e}")
            return {'original_amount': amount, 'discount_amount': 0, 'final_amount': amount}
    
    def calculate_compound_amount(self, principal: float, 
                                 monthly_rate: float, 
                                 months: int) -> Dict[str, float]:
        """
        محاسبه مقدار مرکب (سود مرکب)
        
        Args:
            principal: سرمایه اولیه
            monthly_rate: نرخ ماهانه (درصد)
            months: تعداد ماه‌ها
            
        Returns:
            dict: شامل سرمایه اولیه، سود و مبلغ نهایی
        """
        try:
            monthly_decimal = monthly_rate / 100
            final_amount = principal * ((1 + monthly_decimal) ** months)
            interest = final_amount - principal
            
            return {
                'principal': principal,
                'monthly_rate': monthly_rate,
                'months': months,
                'total_interest': interest,
                'final_amount': final_amount,
                'annual_rate': monthly_rate * 12
            }
        except Exception as e:
            print(f"❌ خطا در محاسبه سود مرکب: {e}")
            return {'principal': principal, 'total_interest': 0, 'final_amount': principal}
    
    # ==================== محاسبات مربوط به شرکا ====================
    
    def calculate_partner_profit_distribution(self, total_profit: float, 
                                             partners_data: List[Dict]) -> List[Dict]:
        """
        محاسبه توزیع سود بین شرکا
        
        Args:
            total_profit: کل سود
            partners_data: لیست اطلاعات شرکا
            
        Returns:
            list: توزیع سود برای هر شریک
        """
        try:
            if not partners_data:
                return []
            
            # محاسبه جمع درصدها
            total_percentage = sum(p.get('profit_percentage', 0) for p in partners_data)
            
            # اگر جمع درصدها 100 نبود، نرمال‌سازی کنیم
            if abs(total_percentage - 100) > 0.01:
                normalized_partners = []
                for partner in partners_data:
                    normalized_percentage = (partner.get('profit_percentage', 0) / total_percentage) * 100
                    normalized_partners.append({
                        **partner,
                        'profit_percentage': normalized_percentage
                    })
                partners_data = normalized_partners
                total_percentage = 100
            
            distribution = []
            for partner in partners_data:
                percentage = partner.get('profit_percentage', 0)
                capital = partner.get('capital', 0)
                profit_share = (total_profit * percentage) / 100
                
                distribution.append({
                    'partner_id': partner.get('id'),
                    'partner_name': partner.get('partner_name', 'نامشخص'),
                    'profit_percentage': percentage,
                    'capital': capital,
                    'profit_share': profit_share,
                    'roi': (profit_share / capital * 100) if capital > 0 else 0
                })
            
            return distribution
            
        except Exception as e:
            print(f"❌ خطا در توزیع سود شرکا: {e}")
            return []
    

    def calculate_partner_roi(self, partner_id: int, start_date: str, end_date: str) -> Dict:
        """
        محاسبه بازده سرمایه (ROI) برای یک شریک - نسخه اصلاح شده
        """
        try:
            # دریافت سرمایه اولیه
            capital_query = """
            SELECT COALESCE(capital, 0) as capital
            FROM Partners
            WHERE id = ?
            """
            
            capital_result = self.data_manager.db.fetch_one(capital_query, (partner_id,))
            capital = capital_result.get('capital', 0) if capital_result else 0
            
            # دریافت سود کل
            profit_query = """
            SELECT COALESCE(SUM(share_amount), 0) as total_profit
            FROM PartnerShares
            WHERE partner_id = ?
            AND DATE(calculation_date) BETWEEN ? AND ?
            """
            
            profit_result = self.data_manager.db.fetch_one(
                profit_query, 
                (partner_id, start_date, end_date)
            )
            total_profit = profit_result.get('total_profit', 0) if profit_result else 0
            
            # محاسبه ROI - با کنترل تقسیم بر صفر
            if capital > 0:
                roi_percentage = (total_profit / capital) * 100
            else:
                roi_percentage = 0
            
            # محاسبه ROI سالانه
            try:
                start_obj = jdatetime.datetime.strptime(start_date, "%Y/%m/%d")
                end_obj = jdatetime.datetime.strptime(end_date, "%Y/%m/%d")
                days_diff = (end_obj - start_obj).days
                
                if days_diff > 0:
                    annual_roi_percentage = roi_percentage * (365 / days_diff)
                else:
                    annual_roi_percentage = roi_percentage
            except:
                annual_roi_percentage = roi_percentage
            
            return {
                'partner_id': partner_id,
                'capital': capital,
                'total_profit': total_profit,
                'roi_percentage': roi_percentage,
                'annual_roi_percentage': annual_roi_percentage,
                'period': f"{start_date} تا {end_date}"
            }
            
        except Exception as e:
            print(f"❌ خطا در محاسبه ROI: {e}")
            return {'error': str(e)}

    # ==================== تحلیل‌های مالی ====================
    def calculate_financial_ratios(self, start_date: str, end_date: str) -> Dict:
        """محاسبه نسبت‌های مالی - نسخه نهایی اصلاح شده"""
        try:
            # تبدیل تاریخ به میلادی با کنترل خطا
            try:
                start_gregorian = self.data_manager.db.jalali_to_gregorian(start_date)
                end_gregorian = self.data_manager.db.jalali_to_gregorian(end_date)
            except:
                # اگر تبدیل تاریخ مشکل داشت، از تاریخ پیش‌فرض استفاده کن
                start_gregorian = "2026-01-01"
                end_gregorian = "2026-01-29"
            
            # 🔴 کوئری با کنترل کامل Null
            income_query = """
            SELECT 
                COALESCE(SUM(CASE 
                    WHEN transaction_type IN ('دریافت', 'درآمد', 'فروش') 
                    THEN amount ELSE 0 
                END), 0) as total_income
            FROM AccountingTransactions
            WHERE DATE(transaction_date) BETWEEN ? AND ?
            """
            
            expense_query = """
            SELECT 
                COALESCE(SUM(CASE 
                    WHEN transaction_type IN ('پرداخت', 'هزینه', 'خرید') 
                    THEN amount ELSE 0 
                END), 0) as total_expense
            FROM AccountingTransactions
            WHERE DATE(transaction_date) BETWEEN ? AND ?
            """
            
            income_result = self.data_manager.db.fetch_one(income_query, (start_gregorian, end_gregorian))
            expense_result = self.data_manager.db.fetch_one(expense_query, (start_gregorian, end_gregorian))
            
            # 🔴 استفاده از get با مقدار پیش‌فرض
            total_income = income_result.get('total_income', 0) if income_result else 0
            total_expense = expense_result.get('total_expense', 0) if expense_result else 0
            
            # محاسبات با کنترل کامل
            net_profit = float(total_income or 0) - float(total_expense or 0)
            
            # 🔴 محاسبه نسبت‌ها با جلوگیری از تقسیم بر صفر
            if total_income and float(total_income) > 0:
                profit_margin_percentage = (net_profit / float(total_income)) * 100
                expense_ratio_percentage = (float(total_expense or 0) / float(total_income)) * 100
            else:
                profit_margin_percentage = 0
                expense_ratio_percentage = 0
            
            return {
                'profit_margin_percentage': round(profit_margin_percentage, 1),
                'expense_ratio_percentage': round(expense_ratio_percentage, 1),
                'net_profit': net_profit,
                'total_income': float(total_income or 0),
                'total_expense': float(total_expense or 0),
                'current_ratio': 0,  # نیاز به داده‌های بیشتر
                'quick_ratio': 0,    # نیاز به داده‌های بیشتر
                'roa_percentage': 0  # نیاز به داده‌های بیشتر
            }
            
        except Exception as e:
            print(f"⚠️ خطا در محاسبه نسبت‌های مالی: {e}")
            # بازگرداندن مقادیر پیش‌فرض
            return {
                'profit_margin_percentage': 0,
                'expense_ratio_percentage': 0,
                'net_profit': 0,
                'total_income': 0,
                'total_expense': 0,
                'current_ratio': 0,
                'quick_ratio': 0,
                'roa_percentage': 0
            }

   
    def _calculate_current_ratio(self) -> float:
        """محاسبه نسبت جاری"""
        try:
            # دریافت دارایی‌های جاری (موجودی نقدی + حساب‌های دریافتی)
            current_assets_query = """
            SELECT SUM(current_balance) as total
            FROM Accounts
            WHERE account_type IN ('نقدی', 'جاری', 'صندوق')
            AND is_active = 1
            """
            assets_result = self.data_manager.db.fetch_one(current_assets_query)
            current_assets = assets_result.get('total', 0) if assets_result else 0
            
            # دریافت بدهی‌های جاری (چک‌های پرداختی + حساب‌های پرداختی)
            current_liabilities_query = """
            SELECT SUM(amount) as total
            FROM Checks
            WHERE check_type = 'پرداختی'
            AND status IN ('وصول نشده', 'پاس نشده')
            """
            liabilities_result = self.data_manager.db.fetch_one(current_liabilities_query)
            current_liabilities = liabilities_result.get('total', 0) if liabilities_result else 0
            
            return current_assets / current_liabilities if current_liabilities > 0 else 0
            
        except Exception as e:
            print(f"⚠️ خطا در محاسبه نسبت جاری: {e}")
            return 0
    
    def _calculate_quick_ratio(self) -> float:
        """محاسبه نسبت آنی"""
        try:
            # دریافت دارایی‌های سریع (نقدی + حساب‌های دریافتی کوتاه مدت)
            quick_assets_query = """
            SELECT SUM(current_balance) as total
            FROM Accounts
            WHERE account_type IN ('نقدی', 'صندوق')
            AND is_active = 1
            """
            assets_result = self.data_manager.db.fetch_one(quick_assets_query)
            quick_assets = assets_result.get('total', 0) if assets_result else 0
            
            # دریافت بدهی‌های جاری
            current_liabilities_query = """
            SELECT SUM(amount) as total
            FROM Checks
            WHERE check_type = 'پرداختی'
            AND status IN ('وصول نشده', 'پاس نشده')
            """
            liabilities_result = self.data_manager.db.fetch_one(current_liabilities_query)
            current_liabilities = liabilities_result.get('total', 0) if liabilities_result else 0
            
            return quick_assets / current_liabilities if current_liabilities > 0 else 0
            
        except Exception as e:
            print(f"⚠️ خطا در محاسبه نسبت آنی: {e}")
            return 0
    
    def _calculate_debt_to_equity_ratio(self) -> float:
        """محاسبه نسبت بدهی به سرمایه"""
        try:
            # دریافت کل بدهی‌ها
            total_debt_query = """
            SELECT SUM(amount) as total
            FROM Checks
            WHERE check_type = 'پرداختی'
            AND status IN ('وصول نشده', 'پاس نشده')
            """
            debt_result = self.data_manager.db.fetch_one(total_debt_query)
            total_debt = debt_result.get('total', 0) if debt_result else 0
            
            # دریافت سرمایه شرکا
            total_equity_query = """
            SELECT SUM(capital) as total
            FROM Partners
            WHERE active = 1
            """
            equity_result = self.data_manager.db.fetch_one(total_equity_query)
            total_equity = equity_result.get('total', 0) if equity_result else 0
            
            return total_debt / total_equity if total_equity > 0 else 0
            
        except Exception as e:
            print(f"⚠️ خطا در محاسبه نسبت بدهی به سرمایه: {e}")
            return 0
    
    # ==================== پیش‌بینی و تحلیل ====================
    
    def forecast_revenue(self, periods: int = 12, method: str = 'linear') -> List[Dict]:
        """
        پیش‌بینی درآمد برای دوره‌های آینده
        
        Args:
            periods: تعداد دوره‌های آینده (ماهانه)
            method: روش پیش‌بینی (linear, exponential, moving_average)
            
        Returns:
            list: پیش‌بینی درآمد برای هر دوره
        """
        try:
            # دریافت داده‌های تاریخی
            historical_query = """
            SELECT 
                strftime('%Y-%m', transaction_date) as month,
                SUM(amount) as monthly_income
            FROM AccountingTransactions
            WHERE transaction_type IN ('دریافت', 'درآمد')
            GROUP BY strftime('%Y-%m', transaction_date)
            ORDER BY month DESC
            LIMIT 24
            """
            
            historical_data = self.data_manager.db.fetch_all(historical_query)
            
            if not historical_data:
                return []
            
            # تبدیل به لیست عددی
            monthly_incomes = [float(item['monthly_income']) for item in historical_data]
            monthly_incomes.reverse()  # قدیمی‌ترین به جدیدترین
            
            # پیش‌بینی بر اساس روش انتخابی
            forecast = []
            if method == 'linear':
                forecast = self._linear_regression_forecast(monthly_incomes, periods)
            elif method == 'exponential':
                forecast = self._exponential_smoothing_forecast(monthly_incomes, periods)
            elif method == 'moving_average':
                forecast = self._moving_average_forecast(monthly_incomes, periods)
            else:
                forecast = self._linear_regression_forecast(monthly_incomes, periods)
            
            # ساختاردهی نتایج
            today = jdatetime.datetime.now()
            results = []
            for i, value in enumerate(forecast):
                forecast_date = today + jdatetime.timedelta(days=30 * (i + 1))
                results.append({
                    'period': i + 1,
                    'forecast_date': forecast_date.strftime("%Y/%m/%d"),
                    'forecast_month': forecast_date.strftime("%Y/%m"),
                    'forecast_amount': value,
                    'confidence_interval': self._calculate_confidence_interval(monthly_incomes, value)
                })
            
            return results
            
        except Exception as e:
            print(f"❌ خطا در پیش‌بینی درآمد: {e}")
            return []
    
    def _linear_regression_forecast(self, data: List[float], periods: int) -> List[float]:
        """پیش‌بینی با رگرسیون خطی"""
        n = len(data)
        if n < 2:
            return [data[-1] if data else 0] * periods
        
        # محاسبه شیب و عرض از مبدا
        sum_x = sum(range(n))
        sum_y = sum(data)
        sum_xy = sum(i * data[i] for i in range(n))
        sum_x2 = sum(i ** 2 for i in range(n))
        
        slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x ** 2)
        intercept = (sum_y - slope * sum_x) / n
        
        # پیش‌بینی
        forecast = []
        for i in range(n, n + periods):
            forecast.append(intercept + slope * i)
        
        return forecast
    
    def _exponential_smoothing_forecast(self, data: List[float], periods: int, 
                                      alpha: float = 0.3) -> List[float]:
        """پیش‌بینی با هموارسازی نمایی"""
        if not data:
            return []
        
        forecast_values = [data[0]]
        for i in range(1, len(data)):
            forecast_values.append(alpha * data[i] + (1 - alpha) * forecast_values[i - 1])
        
        # ادامه دادن پیش‌بینی
        last_forecast = forecast_values[-1]
        return [last_forecast] * periods
    
    def _moving_average_forecast(self, data: List[float], periods: int, 
                                window: int = 3) -> List[float]:
        """پیش‌بینی با میانگین متحرک"""
        if len(data) < window:
            return [sum(data) / len(data) if data else 0] * periods
        
        last_values = data[-window:]
        avg = sum(last_values) / window
        return [avg] * periods
    
    def _calculate_confidence_interval(self, data: List[float], 
                                      predicted: float, 
                                      confidence: float = 0.95) -> Dict[str, float]:
        """محاسبه فاصله اطمینان"""
        if len(data) < 2:
            return {'lower': predicted, 'upper': predicted, 'margin': 0}
        
        mean = statistics.mean(data)
        stdev = statistics.stdev(data) if len(data) > 1 else 0
        
        # محاسبه margin (ساده شده)
        margin = stdev * 1.96  # برای سطح اطمینان 95%
        
        return {
            'lower': max(0, predicted - margin),
            'upper': predicted + margin,
            'margin': margin,
            'confidence_level': confidence
        }
    
    # ==================== تحلیل ریسک ====================
    
    def calculate_risk_metrics(self) -> Dict[str, float]:
        """
        محاسبه معیارهای ریسک مالی
        """
        try:
            # دریافت واریانس درآمد ماهانه
            monthly_income_query = """
            SELECT 
                strftime('%Y-%m', transaction_date) as month,
                SUM(amount) as monthly_income
            FROM AccountingTransactions
            WHERE transaction_type IN ('دریافت', 'درآمد')
            GROUP BY strftime('%Y-%m', transaction_date)
            ORDER BY month DESC
            LIMIT 12
            """
            
            monthly_data = self.data_manager.db.fetch_all(monthly_income_query)
            monthly_incomes = [float(item['monthly_income']) for item in monthly_data]
            
            if len(monthly_incomes) < 2:
                return {'error': 'داده کافی برای تحلیل ریسک وجود ندارد'}
            
            # محاسبه معیارها
            mean_income = statistics.mean(monthly_incomes)
            income_std = statistics.stdev(monthly_incomes)
            cv = (income_std / mean_income * 100) if mean_income > 0 else 0
            
            # نسبت شارپ (ساده شده)
            risk_free_rate = 0.18  # نرخ بدون ریسک فرضی (سالانه)
            sharpe_ratio = ((mean_income * 12) - risk_free_rate) / income_std if income_std > 0 else 0
            
            # ارزش در معرض ریسک (VaR) - ساده شده
            sorted_incomes = sorted(monthly_incomes)
            var_95 = sorted_incomes[int(len(sorted_incomes) * 0.05)] if len(sorted_incomes) > 5 else 0
            
            return {
                'mean_monthly_income': mean_income,
                'income_standard_deviation': income_std,
                'coefficient_of_variation': cv,
                'sharpe_ratio': sharpe_ratio,
                'value_at_risk_95': var_95,
                'max_drawdown': self._calculate_max_drawdown(monthly_incomes),
                'income_stability': 100 - min(cv, 100)
            }
            
        except Exception as e:
            print(f"❌ خطا در محاسبه معیارهای ریسک: {e}")
            return {'error': str(e)}
    
    def _calculate_max_drawdown(self, data: List[float]) -> float:
        """محاسبه بیشترین کاهش (Max Drawdown)"""
        if not data:
            return 0
        
        peak = data[0]
        max_drawdown = 0
        
        for value in data:
            if value > peak:
                peak = value
            drawdown = (peak - value) / peak * 100 if peak > 0 else 0
            max_drawdown = max(max_drawdown, drawdown)
        
        return max_drawdown
    
    # ==================== تحلیل سودآوری ====================
    

    def calculate_profitability_analysis(self, start_date: str, end_date: str) -> Dict:
        """
        تحلیل سودآوری کسب‌وکار - نسخه اصلاح شده
        """
        try:
            start_gregorian = self.data_manager.db.jalali_to_gregorian(start_date)
            end_gregorian = self.data_manager.db.jalali_to_gregorian(end_date)
            
            # دریافت درآمد کل با کنترل Null
            total_income_query = """
            SELECT COALESCE(SUM(amount), 0) as total
            FROM AccountingTransactions
            WHERE transaction_type IN ('دریافت', 'درآمد')
            AND DATE(transaction_date) BETWEEN ? AND ?
            """
            income_result = self.data_manager.db.fetch_one(
                total_income_query, 
                (start_gregorian, end_gregorian)
            )
            total_income = income_result.get('total', 0) if income_result else 0
            total_income = float(total_income or 0)
            
            # دریافت هزینه‌ها به تفکیک نوع
            expenses_by_type_query = """
            SELECT 
                CASE 
                    WHEN description LIKE '%اجرت%' OR description LIKE '%دستمزد%' THEN 'هزینه پرسنلی'
                    WHEN description LIKE '%قطعه%' OR description LIKE '%لوازم%' THEN 'هزینه قطعات'
                    WHEN description LIKE '%اجاره%' OR description LIKE '%حقوق%' THEN 'هزینه ثابت'
                    ELSE 'هزینه متفرقه'
                END as expense_type,
                COALESCE(SUM(amount), 0) as total_amount
            FROM AccountingTransactions
            WHERE transaction_type IN ('پرداخت', 'هزینه')
            AND DATE(transaction_date) BETWEEN ? AND ?
            GROUP BY expense_type
            """
            
            expenses_result = self.data_manager.db.fetch_all(
                expenses_by_type_query, 
                (start_gregorian, end_gregorian)
            )
            
            total_expense = sum(float(item.get('total_amount', 0) or 0) for item in expenses_result)
            gross_profit = total_income - total_expense
            
            # تحلیل نقطه سر به سر
            fixed_costs = sum(float(item.get('total_amount', 0) or 0) for item in expenses_result 
                            if item.get('expense_type') == 'هزینه ثابت')
            
            variable_cost_ratio = sum(float(item.get('total_amount', 0) or 0) for item in expenses_result 
                                    if item.get('expense_type') != 'هزینه ثابت') / total_income \
                                if total_income > 0 else 0
            
            breakeven_point = fixed_costs / (1 - variable_cost_ratio) if variable_cost_ratio < 1 else 0
            
            return {
                'total_income': total_income,
                'total_expense': total_expense,
                'gross_profit': gross_profit,
                'profit_margin': (gross_profit / total_income * 100) if total_income > 0 else 0,
                'expense_breakdown': expenses_result,
                'fixed_costs': fixed_costs,
                'variable_cost_ratio': variable_cost_ratio,
                'breakeven_point': breakeven_point,
                'safety_margin': ((total_income - breakeven_point) / total_income * 100) \
                                if total_income > 0 else 0,
                'period': f"{start_date} تا {end_date}"
            }
            
        except Exception as e:
            print(f"❌ خطا در تحلیل سودآوری: {e}")
            import traceback
            traceback.print_exc()
            return {'error': str(e)}

    # ==================== ابزارهای کمکی ====================
    
    def convert_currency(self, amount: float, from_currency: str = 'ریال', 
                        to_currency: str = 'تومان') -> float:
        """
        تبدیل واحد پولی
        
        Args:
            amount: مبلغ
            from_currency: واحد مبدا
            to_currency: واحد مقصد
            
        Returns:
            float: مبلغ تبدیل شده
        """
        conversion_rates = {
            'ریال': {'تومان': 0.1, 'دلار': 0.000024, 'یورو': 0.000022},
            'تومان': {'ریال': 10, 'دلار': 0.00024, 'یورو': 0.00022},
            'دلار': {'ریال': 41667, 'تومان': 4166.7, 'یورو': 0.92},
            'یورو': {'ریال': 45455, 'تومان': 4545.5, 'دلار': 1.09}
        }
        
        if from_currency == to_currency:
            return amount
        
        rate = conversion_rates.get(from_currency, {}).get(to_currency)
        if rate:
            return amount * rate
        else:
            print(f"⚠️ نرخ تبدیل برای {from_currency} به {to_currency} یافت نشد")
            return amount
    
    def format_money(self, amount: float, currency: str = 'تومان') -> str:
        """
        قالب‌بندی مبلغ برای نمایش
        
        Args:
            amount: مبلغ
            currency: واحد پول
            
        Returns:
            str: مبلغ قالب‌بندی شده
        """
        try:
            # تبدیل به تومان اگر ریال است
            if currency == 'ریال':
                amount_toman = amount / 10
                return f"{amount_toman:,.0f} تومان ({amount:,.0f} ریال)"
            else:
                return f"{amount:,.0f} {currency}"
        except:
            return f"{amount} {currency}"
    
    def get_financial_health_score(self) -> Dict[str, any]:
        """
        محاسبه امتیاز سلامت مالی کسب‌وکار
        
        Returns:
            dict: امتیاز و جزئیات سلامت مالی
        """
        try:
            scores = []
            details = []
            
            # 1. بررسی نسبت‌های مالی
            ratios = self.calculate_financial_ratios(
                jdatetime.datetime.now().replace(day=1).strftime("%Y/%m/%d"),
                jdatetime.datetime.now().strftime("%Y/%m/%d")
            )
            
            if 'ratios' in ratios:
                # نسبت جاری
                current_ratio = ratios['ratios'].get('current_ratio', 0)
                if current_ratio >= 2:
                    scores.append(10)
                    details.append('نسبت جاری عالی (≥2)')
                elif current_ratio >= 1.5:
                    scores.append(8)
                    details.append('نسبت جاری خوب (1.5-2)')
                elif current_ratio >= 1:
                    scores.append(6)
                    details.append('نسبت جاری قابل قبول (1-1.5)')
                else:
                    scores.append(3)
                    details.append('نسبت جاری ضعیف (<1)')
            
            # 2. بررسی سودآوری
            profit_margin = ratios.get('gross_profit', 0) / ratios.get('total_income', 1) * 100 \
                          if ratios.get('total_income', 0) > 0 else 0
            
            if profit_margin >= 30:
                scores.append(10)
                details.append('حاشیه سود عالی (≥30%)')
            elif profit_margin >= 20:
                scores.append(8)
                details.append('حاشیه سود خوب (20-30%)')
            elif profit_margin >= 10:
                scores.append(6)
                details.append('حاشیه سود متوسط (10-20%)')
            else:
                scores.append(4)
                details.append('حاشیه سود پایین (<10%)')
            
            # 3. بررسی جریان نقدی
            cash_query = """
            SELECT SUM(current_balance) as cash_balance
            FROM Accounts
            WHERE account_type IN ('نقدی', 'صندوق')
            AND is_active = 1
            """
            cash_result = self.data_manager.db.fetch_one(cash_query)
            cash_balance = cash_result.get('cash_balance', 0) if cash_result else 0
            
            avg_monthly_expense = ratios.get('total_expense', 0) / 12  # فرض: داده‌های یک سال
            
            months_of_runway = cash_balance / avg_monthly_expense if avg_monthly_expense > 0 else 0
            
            if months_of_runway >= 6:
                scores.append(10)
                details.append('ذخیره نقدی عالی (≥6 ماه)')
            elif months_of_runway >= 3:
                scores.append(8)
                details.append('ذخیره نقدی خوب (3-6 ماه)')
            elif months_of_runway >= 1:
                scores.append(6)
                details.append('ذخیره نقدی قابل قبول (1-3 ماه)')
            else:
                scores.append(3)
                details.append('ذخیره نقدی ناکافی (<1 ماه)')
            
            # 4. بررسی بدهی‌ها
            debt_query = """
            SELECT SUM(amount) as total_debt
            FROM Checks
            WHERE check_type = 'پرداختی'
            AND status IN ('وصول نشده', 'پاس نشده')
            """
            debt_result = self.data_manager.db.fetch_one(debt_query)
            total_debt = debt_result.get('total_debt', 0) if debt_result else 0
            
            debt_to_income = total_debt / ratios.get('total_income', 1) \
                           if ratios.get('total_income', 0) > 0 else 0
            
            if debt_to_income <= 0.3:
                scores.append(10)
                details.append('سطح بدهی مناسب (≤30%)')
            elif debt_to_income <= 0.5:
                scores.append(7)
                details.append('سطح بدهی متوسط (30-50%)')
            elif debt_to_income <= 0.7:
                scores.append(4)
                details.append('سطح بدهی بالا (50-70%)')
            else:
                scores.append(2)
                details.append('سطح بدهی خطرناک (>70%)')
            
            # محاسبه میانگین امتیاز
            final_score = sum(scores) / len(scores) if scores else 0
            
            # تعیین وضعیت
            if final_score >= 9:
                status = "عالی"
                status_color = "#27ae60"
            elif final_score >= 7:
                status = "خوب"
                status_color = "#3498db"
            elif final_score >= 5:
                status = "متوسط"
                status_color = "#f39c12"
            else:
                status = "نیاز به توجه"
                status_color = "#e74c3c"
            
            return {
                'overall_score': round(final_score, 1),
                'max_score': 10,
                'status': status,
                'status_color': status_color,
                'details': details,
                'metrics': {
                    'current_ratio': round(current_ratio, 2),
                    'profit_margin': round(profit_margin, 1),
                    'months_of_runway': round(months_of_runway, 1),
                    'debt_to_income': round(debt_to_income * 100, 1)
                }
            }
            
        except Exception as e:
            print(f"❌ خطا در محاسبه سلامت مالی: {e}")
            return {
                'overall_score': 0,
                'status': 'خطا در محاسبه',
                'details': [f'خطا: {str(e)}']
            }