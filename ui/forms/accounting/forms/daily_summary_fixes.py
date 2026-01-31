# daily_summary_fixes.py
"""
رفع خطاهای کوئری‌های خلاصه روزانه
"""

def get_fixed_daily_summary_queries():
    """کوئری‌های اصلاح شده برای خلاصه روزانه"""
    
    queries = {
        # کوئری اصلاح شده برای شمارش چک‌های امروز
        'count_checks_today': """
            SELECT COUNT(*) as count
            FROM Checks
            WHERE DATE(issue_date) = ?
        """,
        
        # کوئری اصلاح شده برای شمارش فاکتورهای امروز
        'count_invoices_today': """
            SELECT COUNT(*) as count
            FROM Invoices
            WHERE DATE(invoice_date) = ?
        """,
        
        # کوئری اصلاح شده برای شمارش پذیرش‌های امروز
        'count_receptions_today': """
            SELECT COUNT(*) as count
            FROM Receptions
            WHERE DATE(reception_date) = ?
        """,
        
        # کوئری اصلاح شده برای خلاصه مالی امروز
        'daily_financial_summary': """
            SELECT 
                COUNT(*) as total_transactions,
                SUM(CASE WHEN transaction_type IN ('دریافت', 'درآمد') THEN amount ELSE 0 END) as total_income,
                SUM(CASE WHEN transaction_type IN ('پرداخت', 'هزینه') THEN amount ELSE 0 END) as total_expense
            FROM AccountingTransactions
            WHERE DATE(transaction_date) = ?
        """
    }
    
    return queries