from .base import Adapter
from ..models import CheckResult

class QlubAdapter(Adapter):
    # A bill/payment QR is insufficient evidence of food orderability.
    menu_selector = '[data-testid="menu"], [data-menu]'
    product_selector = '[data-testid="menu-item"], [data-product-id]'

    def parse(self, observation, source):
        if '(do not use)' in observation.text.casefold():
            return CheckResult(reason='Ordering page marks its menus as “Do Not Use”. Orderability is unconfirmed.')
        return super().parse(observation, source)
