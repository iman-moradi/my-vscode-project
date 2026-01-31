"""
دیالوگ‌های حسابداری
"""

from .account_dialog import AccountDialog
from .transaction_dialog import TransactionDialog
from .account_details_dialog import AccountDetailsDialog
from .transfer_dialog import TransferDialog
from .transaction_details_dialog import TransactionDetailsDialog  # اضافه شد
from .customer_selection_dialog import CustomerSelectionDialog
from .reception_selection_dialog import ReceptionSelectionDialog
from .payment_dialog import PaymentDialog
from .partner_dialog import PartnerDialog
from .partner_profits_dialog import PartnerProfitsDialog

__all__ = [
    'AccountDialog',
    'TransactionDialog',
    'AccountDetailsDialog',
    'TransferDialog',
    'TransactionDetailsDialog',  # اضافه شد
    'CustomerSelectionDialog',
    'ReceptionSelectionDialog',
    'PaymentDialog',
    'PartnerDialog',
    'PartnerProfitsDialog'
]