# ui/widgets/dashboard/__init__.py
"""
ویجت‌های داشبورد مدیریتی
"""

from .stats_cards_widget import StatsCardsWidget
from .charts_widget import ChartsWidget
from .alerts_widget import AlertsWidget
from .quick_lists_widget import QuickListsWidget

__all__ = [
    'StatsCardsWidget',
    'ChartsWidget',
    'AlertsWidget',
    'QuickListsWidget'
]