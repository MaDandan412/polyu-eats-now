from .base import Adapter

class Eats365Adapter(Adapter):
    # These menu selectors were observed on the actual Theatre Lounge store.
    menu_selector = '[id^="cat-"]'
    product_selector = '[id^="menu_product_"]'
    closed_lines = Adapter.closed_lines + ('service unavailable during designated time period',)
