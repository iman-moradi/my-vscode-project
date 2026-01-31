# config/profit_calculation_config.py

PROFIT_CALCULATION_CONFIG = {
    'default_periods': {
        '3_month': '۳ ماهه',
        '6_month': '۶ ماهه', 
        '1_year': '۱ ساله',
        '2_year': '۲ ساله',
        'all_time': 'از ابتدا'
    },
    
    'distribution_methods': [
        'بر اساس درصد قراردادی',
        'بر اساس سرمایه',
        'بر اساس سهم مساوی',
        'ترکیبی (سرمایه + عملکرد)'
    ],
    
    'report_types': [
        'گزارش ماهانه',
        'گزارش فصلی', 
        'گزارش سالانه',
        'گزارش دلخواه'
    ],
    
    'roi_thresholds': {
        'excellent': 30,
        'good': 20,
        'average': 10,
        'poor': 0
    },
    
    'colors': {
        'excellent': '#27ae60',
        'good': '#3498db',
        'average': '#f39c12',
        'poor': '#e74c3c',
        'header': '#2ecc71',
        'partners': '#3498db',
        'roi': '#f39c12',
        'reports': '#9b59b6'
    }
}