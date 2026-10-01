from .base import Adapter

class Pin2EatAdapter(Adapter):
    menu_selector = '.goods-list, .menu-list, [data-menu]'
    product_selector = '.goods-item, .menu-item, [data-product-id]'
    closed_lines = Adapter.closed_lines + ('closed today', '商家休息中', '今日休業', '店鋪休息中', '店铺休息中', '暫不接單', '暂不接单')
