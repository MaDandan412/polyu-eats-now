from .order_place import OrderPlaceAdapter
from .eats365 import Eats365Adapter
from .qlub import QlubAdapter
from .pin2eat import Pin2EatAdapter
from .other import UCRAdapter, FoodCloudAdapter, SeitoAdapter, TaiTaiAdapter, OdouiAdapter

ADAPTERS = {
    'order_place': OrderPlaceAdapter(), 'eats365': Eats365Adapter(),
    'qlub': QlubAdapter(), 'pin2eat': Pin2EatAdapter(),
    'ucr_iqpos': UCRAdapter(), 'foodcloud': FoodCloudAdapter(),
    'seito': SeitoAdapter(), 'tai_tai': TaiTaiAdapter(), 'odoui': OdouiAdapter(),
}
