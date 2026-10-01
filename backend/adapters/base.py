from dataclasses import dataclass, field
from ..models import CheckResult, Status

@dataclass
class Observation:
    text: str
    title: str = ''
    http_status: int = 200
    menu_count: int = 0
    purchasable_count: int = 0
    services: dict[str, bool] = field(default_factory=dict)
    current_order_enabled: bool = False
    merchant_verified: bool = False

class Adapter:
    """Read-only evidence parser. HTTP 200 and a menu alone never imply OPEN."""
    menu_selector = '[data-menu], .menu-list, .menu-category'
    product_selector = '[data-product-id], .menu-item, .product-item'
    category_selector = None

    async def prepare(self, page):
        """Enter only observed menu navigation; never touch a purchase control."""
        return

    async def select_category(self, page, category):
        await category.click(timeout=3000)
    closed_lines = ('currently closed', 'not accepting orders', 'ordering is unavailable', 'ordering unavailable', 'orders are unavailable', '現在為非營業時間', '暫停接單', '暫停下單', '暫停點餐', '目前無法點餐', '商店休息中')
    open_lines = ('accepting orders now', 'ordering available now', '即時點餐已開放', '現在可以下單')
    limited_lines = ('limited ordering available', 'limited availability', '僅限外賣', '只限外賣')

    def parse(self, observation: Observation, source: dict) -> CheckResult:
        text = observation.text
        low = text.casefold()
        lines = {' '.join(line.split()).casefold() for line in text.splitlines() if line.strip()}
        if observation.http_status == 429:
            return CheckResult(reason='Ordering system rate-limited this check. Try again later.')
        if observation.http_status >= 400:
            return CheckResult(reason='This platform does not currently allow this automated check to access the ordering page.')
        if any(t in low for t in ('verify you are human', 'enable javascript and cookies to continue', 'checking your browser', 'access denied', 'captcha', '正在執行安全驗證', '正在执行安全验证', '確認您不是機器人', '确认您不是机器人')):
            return CheckResult(reason='Ordering system requires browser verification. Availability is unknown.')
        if text.strip() == 'CONTENT_NOT_FOUND':
            return CheckResult(reason='Official ordering page returned CONTENT_NOT_FOUND; current orderability cannot be verified.')
        if not text.strip():
            return CheckResult(reason='Ordering page did not expose readable status evidence.')
        # Validate the merchant, not just the platform's template or generic homepage.
        identity = source.get('identity', [])
        if not observation.merchant_verified and (not identity or not any(name.casefold() in low for name in identity)):
            return CheckResult(reason='Restaurant identity could not be confirmed on the ordering page.')
        closed = next((line for line in self.closed_lines if line in lines), None)
        opened = next((line for line in self.open_lines if line in lines), None)
        limited = next((line for line in self.limited_lines if line in lines), None)
        if closed and opened:
            return CheckResult(reason='Ordering system shows conflicting availability evidence.')
        if closed:
            return CheckResult(status=Status.CLOSED, reason='Official ordering system explicitly says current ordering is unavailable.', evidence=[closed])
        if any(t in low for t in ('sign in to order', 'login to order', 'log in to order', '請先登入', 'session expired', '工作階段已過期', 'qr code expired', 'invalid qr code')):
            return CheckResult(reason='Ordering requires a sign-in or a fresh restaurant QR code.')
        # Demand a current-order signal AND at least one visible, enabled purchase control within an actual menu product.
        if observation.menu_count > 0 and observation.purchasable_count > 0 and (opened or limited or observation.current_order_enabled):
            service_values = {key: observation.services.get(key) for key in ('dine_in', 'takeaway')}
            partial = service_values['dine_in'] is False and service_values['takeaway'] is True or service_values['takeaway'] is False and service_values['dine_in'] is True
            return CheckResult(status=Status.LIMITED if limited or partial else Status.OPEN,
                               reason='Current ordering enabled with a purchasable menu item.' if not limited and not partial else 'Official system confirms restricted ordering availability.',
                               evidence=[opened or limited or 'Official system offers immediate ordering', 'Visible menu and enabled purchase control'], **service_values)
        return CheckResult(reason='Page is reachable, but current orderability could not be confirmed.')
