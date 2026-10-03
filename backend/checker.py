import asyncio
import logging
from urllib.parse import urlsplit
from .adapters import ADAPTERS
from .adapters.base import Observation
from .models import CheckResult, Status
from .ordering_session import OrderingSession, is_verification

logger = logging.getLogger(__name__)
ALLOWED_HOSTS = {'food.order.place', 'csd.order.place', 'order.taitaiteaology.com', 'order.grove.hk', 'ucriqpos.com.hk', 'imapp-hk01.seitopos.com', 'app.eats365pos.com', 'odoui1.azurewebsites.net', 'meal.pin2eat.com', 'app.qlub.io', 'orderonline.foodcloud.hk'}
MOBILE_UA = 'Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Mobile/15E148 Safari/604.1'

# Only collect rendered evidence. Navigation to menus/categories is allowed;
# no form submission, cart changes, or ordering requests are performed.
COLLECT = r'''({menu, product, platform}) => {
  const visible = e => !!e && !!e.getClientRects().length && getComputedStyle(e).visibility !== 'hidden';
  const enabled = e => !e.disabled && e.getAttribute('aria-disabled') !== 'true' && !e.classList.contains('disabled') && getComputedStyle(e).pointerEvents !== 'none';
  const buy = /^(add to cart|add to order|加入購物車|加入购物车|加入訂單|加入订单|加到購物車|立即購買)$/i;
  const menuNodes = [...document.querySelectorAll(menu)].filter(visible);
  const products = [...document.querySelectorAll(product)].filter(visible);
  let purchasable = products.filter(p => menuNodes.some(m => m.contains(p)) && [...p.querySelectorAll('button, a, [role="button"]')].some(e => visible(e) && enabled(e) && buy.test(e.innerText.trim())));
  const services = {};
  // Only explicit current-availability attributes qualify. Labels and URL modes do not.
  for (const key of ['dine_in', 'takeaway']) {
    const e = document.querySelector(`[data-order-service="${key}"][data-available]`);
    if (visible(e) && ['true','false'].includes(e.getAttribute('data-available'))) services[key] = e.getAttribute('data-available') === 'true';
  }
  const text = document.body?.innerText || '';
  let current_order_enabled = false;
  if (['ucr_iqpos', 'foodcloud'].includes(platform)) {
    // Observed UCR controls: product rows contain .item-qty, minus then plus.
    // An enabled category/favorite control is never counted as a purchase control.
    purchasable = products.filter(p => {
      const name = p.querySelector('.font-16-b')?.innerText?.trim() || '';
      const rowText = p.innerText;
      const plus = p.querySelector('.item-qty button:last-of-type');
      return name && !/餐具|飲管|cutlery|utensil|straw|test name/i.test(name) && !/售罄|sold out|unavailable|暫停/i.test(rowText) && visible(plus) && enabled(plus) && /\$\s*\d/.test(p.innerText);
    });
    const match = text.match(/預計自取時間:\s*(\d{4})年(\d{1,2})月(\d{1,2})日\s*即時/);
    const today = new Intl.DateTimeFormat('sv-SE', {timeZone:'Asia/Hong_Kong'}).format(new Date());
    current_order_enabled = !!match && `${match[1]}-${match[2].padStart(2,'0')}-${match[3].padStart(2,'0')}` === today;
    if (current_order_enabled && purchasable.length) services.takeaway = true;
  }
  if (platform === 'seito') {
    purchasable = products.filter(p => {
      const name = p.querySelector('.item-name-left')?.innerText?.trim() || '';
      const plus = p.querySelector('.addQty');
      return name && !/餐具|飲管|cutlery|utensil|straw/i.test(name) && !/售罄|sold out|unavailable|暫停/i.test(p.innerText) && visible(plus) && enabled(plus) && /\$\s*\d/.test(p.innerText);
    });
    // The menu's current order mode qualifies; an entry-page button alone does not.
    const mode = document.querySelector('.orderInfo .infoRight');
    current_order_enabled = visible(mode) && mode.innerText.trim() === '即時點餐';
    const service = document.querySelector('.orderInfo .infoLeft');
    if (current_order_enabled && purchasable.length && visible(service)) {
      if (service.innerText.trim() === '外賣') services.takeaway = true;
      if (service.innerText.trim() === '堂食') services.dine_in = true;
    }
  }
  if (platform === 'tai_tai') {
    purchasable = products.filter(p => {
      const name = p.querySelector('.itemName')?.innerText?.trim() || '';
      const plus = p.querySelector('.addAnddel img[src*="/jia1.png"]');
      return name && !/餐具|飲管|cutlery|utensil|straw/i.test(name) && !p.querySelector('.shouqin') && visible(plus) && enabled(plus) && enabled(plus.parentElement) && /\$\s*\d/.test(p.querySelector('.price')?.innerText || '');
    });
    // A live, positive ordering-session timer plus actual enabled food controls.
    const timer = text.match(/計時:\s*(\d{1,2}):(\d{2})/);
    current_order_enabled = !!timer && Number(timer[1])*60 + Number(timer[2]) > 0;
    if (current_order_enabled && purchasable.length) services.takeaway = true;
  }
  if (platform === 'order_place') {
    purchasable = products.filter(p => {
      const name = p.querySelector('.item-name')?.innerText?.trim() || '';
      const plus = p.querySelector('button.add-btn');
      const sold = p.querySelector('.div-soldout');
      const making = p.querySelector('.div-making');
      return name && !/餐具|飲管|cutlery|utensil|straw/i.test(name) && !visible(sold) && !visible(making) && visible(plus) && enabled(plus) && /\$\s*\d/.test(p.querySelector('[data-testid="item-price"]')?.innerText || '');
    });
    // Active ordering workspace with a confirmed fulfillment selection, not
    // the brand home page or a standalone browsable menu. Preorders never qualify.
    const mode = [...document.querySelectorAll('app-order-page [data-testid="confirmed-mode-selection-box"]')].find(visible);
    const label = mode?.querySelector('[data-testid="order-mode"]')?.innerText?.trim() || '';
    current_order_enabled = !!mode && /^(外賣|堂食|takeaway|dine-in|byod\.modes\.(takeaway|dinein))$/i.test(label) && !/預訂|預約|pre.?order|scheduled order/i.test(text);
    if (current_order_enabled && purchasable.length) {
      if (/外賣|takeaway/i.test(label)) services.takeaway = true;
      if (/堂食|dine.?in/i.test(label)) services.dine_in = true;
    }
  }
  if (platform === 'eats365') {
    const mode = document.querySelector('.order-mode-text');
    const detail = mode?.parentElement?.querySelector('.detail');
    current_order_enabled = visible(mode) && mode.innerText.trim() === 'Pickup' &&
      visible(detail) && detail.innerText.trim() === 'Ready for Pickup Immediately';
    const dialog = [...document.querySelectorAll('.vm--modal[role="dialog"]')].find(visible);
    const name = dialog?.querySelector('.nameAndDesc h1')?.innerText?.trim() || '';
    const add = dialog?.querySelector('.c-add-to-cart-btn');
    const item = products.find(p => menuNodes.some(m => m.contains(p)) &&
      p.querySelector('h3')?.innerText?.trim() === name && /\$\s*\d/.test(p.innerText) &&
      !/sold out|unavailable|售罄|餐具|飲管|cutlery|utensil|straw/i.test(p.innerText));
    // A menu card or an immediate label alone is insufficient. Inspect an
    // enabled purchase control in a matching food's detail, without adding it.
    purchasable = name && item && visible(add) && enabled(add) &&
      !/(^|[-_\s])disabled($|[-_\s])/i.test(add.className) &&
      /^Add for\s*\$\s*\d/i.test(add.innerText.trim()) ? [item] : [];
    if (current_order_enabled && purchasable.length) services.takeaway = true;
  }
  return {text,title:document.title,menu_count:menuNodes.length,purchasable_count:purchasable.length,services,current_order_enabled};
}'''

class BrowserChecker:
    def __init__(self):
        self.runtime = None
        self.browser = None
        self.ready = False
        self.ordering_session = None

    async def start(self):
        try:
            from playwright.async_api import async_playwright
            self.runtime = await async_playwright().start()
            self.browser = await self.runtime.chromium.launch(headless=True)
            self.ordering_session = OrderingSession(self.runtime)
            self.ready = True
        except Exception as exc:
            logger.warning('Browser checker unavailable: %s', type(exc).__name__)

    async def stop(self):
        self.ready = False
        if self.ordering_session:
            await self.ordering_session.close()
        if self.browser:
            await self.browser.close()
        if self.runtime:
            await self.runtime.stop()

    async def observe(self, page, adapter, source):
        # QR landing pages sometimes redirect in JavaScript after DOMContentLoaded.
        for attempt in range(4):
            try:
                return await page.evaluate(COLLECT, {'menu':adapter.menu_selector, 'product':adapter.product_selector, 'platform':source.get('adapter')})
            except Exception as exc:
                if 'Execution context was destroyed' not in str(exc) or attempt == 3:
                    raise
                await page.wait_for_timeout(300)
                await page.wait_for_load_state('domcontentloaded', timeout=5000)

    async def check(self, source: dict) -> CheckResult:
        if not self.ready:
            return CheckResult(reason='Browser checker is not installed or ready. Availability is unknown.')
        url = source.get('check_url') or source.get('order_url')
        if not url:
            return CheckResult(reason='No web ordering address is available.')
        parsed = urlsplit(url)
        if parsed.scheme != 'https' or parsed.hostname not in ALLOWED_HOSTS:
            return CheckResult(reason='Ordering address is not an approved platform source.')
        adapter = ADAPTERS.get(source.get('adapter'))
        if not adapter:
            return CheckResult(reason='This platform has no verified web checker yet.')
        shared_page = None
        if source.get('adapter') == 'order_place' and self.ordering_session:
            try:
                shared_page = await self.ordering_session.page(url)
            except Exception as exc:
                logger.warning('Isolated ordering browser unavailable: %s', type(exc).__name__)
                await self.ordering_session.close()
        options = dict(locale='en-HK', timezone_id='Asia/Hong_Kong',
                       viewport={'width':390,'height':844}, screen={'width':390,'height':844},
                       is_mobile=True, has_touch=True, device_scale_factor=3)
        # Eats365 serves different page structures to Safari and Chromium.
        # Use this Chromium browser's own user agent with the observed adapter.
        if source.get('adapter') != 'eats365':
            options['user_agent'] = MOBILE_UA
        context = shared_page.context if shared_page else await self.browser.new_context(**options)
        try:
            if source.get('adapter') == 'tai_tai':
                return await self.check_block_y(context, adapter, source)
            page = shared_page or await context.new_page()
            # Leave a challenge visible for the human to complete; do not refresh
            # it every cycle or solve it automatically. After verification, fresh
            # normal navigation supplies new ordering evidence as usual.
            verifying = (shared_page and self.ordering_session.visible and
                         is_verification((await self.observe(page, adapter, source))['text']))
            if verifying:
                code = 200
            else:
                response = await page.goto(url, wait_until='domcontentloaded', timeout=25_000)
                code = response.status if response else 0
            if code >= 400:
                observed = await self.observe(page, adapter, source)
                return adapter.parse(Observation(**observed, http_status=code), source)
            if urlsplit(page.url).hostname not in ALLOWED_HOSTS:
                return CheckResult(reason='Ordering page redirected to an unverified site or a sign-in page.')
            early = await self.observe(page, adapter, source)
            early_result = adapter.parse(Observation(**early, http_status=code), source)
            if early_result.status.value != 'UNKNOWN' or 'verification' in early_result.reason or 'CONTENT_NOT_FOUND' in early_result.reason:
                return early_result
            try:
                await adapter.prepare(page)
            except Exception:
                # A closed-store notice can replace the menu while navigation
                # waits for tabs. Preserve that current, explicit closure evidence.
                fallback = adapter.parse(Observation(**await self.observe(page, adapter, source), http_status=code), source)
                if fallback.status.value != 'UNKNOWN' or 'verification' in fallback.reason or 'CONTENT_NOT_FOUND' in fallback.reason:
                    return fallback
                raise
            # Give JavaScript stores time to reveal status; never treat a loading shell as CLOSED.
            result = CheckResult(reason='Ordering page did not expose reliable evidence.')
            for _ in range(12):
                await asyncio.sleep(1)
                collected = await self.observe(page, adapter, source)
                result = adapter.parse(Observation(**collected, http_status=code), source)
                if result.status.value != 'UNKNOWN' or 'verification' in result.reason or 'sign-in' in result.reason or 'CONTENT_NOT_FOUND' in result.reason:
                    break
                if collected['menu_count'] > 0 and adapter.category_selector:
                    break
            # Some platforms open on cutlery or a sold-out meal category. Inspect
            # the other current categories before declaring the shop unknown.
            if result.status.value == 'UNKNOWN' and adapter.category_selector and collected['menu_count']:
                categories = page.locator(adapter.category_selector)
                count = await categories.count()
                for index in range(min(count, 25)):
                    category = categories.nth(index)
                    if await category.get_attribute('aria-selected') == 'true':
                        continue
                    await adapter.select_category(page, category)
                    await page.wait_for_timeout(700)
                    collected = await self.observe(page, adapter, source)
                    result = adapter.parse(Observation(**collected, http_status=code), source)
                    if result.status.value != 'UNKNOWN':
                        if result.status.value in ('OPEN', 'LIMITED'):
                            label = (await category.inner_text()).strip().strip('~').strip()
                            result.evidence.append(f'Orderable menu category: {label}')
                            result.reason = f'Ordering confirmed in the current “{label}” menu, with a purchasable food or drink.'
                        break
            return result
        finally:
            if not shared_page:
                await context.close()

    async def check_block_y(self, context, adapter, source):
        results = []
        for brand, selector in [('Tai Tai', 'btn_taitai'), ('Grove', 'btn_grove')]:
            page = await context.new_page()
            try:
                await page.goto(source['order_url'], wait_until='domcontentloaded', timeout=15000)
                await page.locator(f'#brandBox img[src*="{selector}"]').click(timeout=4000)
                await page.wait_for_url(source['brand_routes'][brand], timeout=8000)
                # Confirm the exact campus storefront reached from the official brand chooser.
                if page.url != source['brand_routes'][brand]:
                    results.append((brand, CheckResult(reason='Restaurant identity could not be confirmed on the ordering page.')))
                    continue
                await page.locator('.popTimeTips button').wait_for(state='visible', timeout=8000)
                await page.locator('.popTimeTips button').click(timeout=3000)
                await page.locator('.goodsList .rowRight .rightlist').first.wait_for(state='visible', timeout=6000)
                observed = await self.observe(page, adapter, source)
                results.append((brand, adapter.parse(Observation(**observed, merchant_verified=True), source)))
            except Exception:
                results.append((brand, CheckResult(reason='Official ordering system could not be checked.')))
            finally:
                await page.close()
        return block_y_result(results)


def block_y_result(results):
    """A shared outlet must not imply that both independent brands accept orders."""
    available = [(name, r) for name, r in results if r.status in (Status.OPEN, Status.LIMITED)]
    evidence = [f'{name}: {r.status.value}' for name, r in results]
    if len(available) == 2 and all(r.status == Status.OPEN for _, r in available):
        return CheckResult(status=Status.OPEN, takeaway=True, reason='Grove and Tai Tai both show current ordering with purchasable food or drink.', evidence=evidence)
    if available:
        names = ', '.join(name for name, _ in available)
        return CheckResult(status=Status.LIMITED, takeaway=True, reason=f'Ordering confirmed for {names}; both brands are not confirmed fully available.', evidence=evidence)
    if len(results) == 2 and all(r.status == Status.CLOSED for _, r in results):
        return CheckResult(status=Status.CLOSED, reason='Both Block Y brands explicitly say current ordering is unavailable.', evidence=evidence)
    return CheckResult(reason='Block Y brand menus could not confirm current ordering availability.', evidence=evidence)
