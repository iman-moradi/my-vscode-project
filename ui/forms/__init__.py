# ui/forms/__init__.py
from .person_form import PersonForm
from .device_form import DeviceForm
from .reception_form import ReceptionForm
from .repair_form.repair_form import RepairForm
from .service_fee_form import ServiceFeeForm
from .device_category_manager_form import DeviceCategoryManagerForm  # تغییر نام
from .device_category_name_form import DeviceCategoryNameForm
from .part_form import PartForm

__all__ = [
    'PersonForm',
    'DeviceForm', 
    'ReceptionForm',
    'RepairForm',
    'ServiceFeeForm',
    'DeviceCategoryManagerForm',  # تغییر نام
    'DeviceCategoryNameForm',
    'PartForm'
]