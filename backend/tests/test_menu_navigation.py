import asyncio
from datetime import datetime, timedelta, timezone
from playwright.async_api import async_playwright
from backend.checker import COLLECT
from backend.adapters import ADAPTERS
from backend.adapters.base import Observation
from backend.models import CheckResult, Status
from backend.service import RestaurantService


def test_real_platform_product_controls_and_current_mode():
    """Regression shapes captured from FoodCloud cards and SeitoPOS menus.

    No external network or cart operation; the checks must distinguish a real
    food item from cutlery, and immediate ordering from a preorder entry button.
    """
    async def run():
        async with async_playwright() as runtime:
            browser = await runtime.chromium.launch(headless=True)
            page = await browser.new_page()
            date = datetime.now(timezone(timedelta(hours=8)))
            header = f'Test Canteen<br>預計自取時間: {date.year}年{date.month}月{date.day}日 即時'
            card = '''<div class="clickable inner"><div class="font-16-b">{name}</div>
              <span>$10.0</span>{sold_out}<section class="item-qty">
              <button>-</button><span>0</span><button>+</button></section></div>'''
            for name, sold_out, expected in [
                ('Rice bowl', '', Status.OPEN),
                ('Rice bowl', '<div>售罄</div>', Status.UNKNOWN),
                ('外賣餐具 (+$1)', '', Status.UNKNOWN),
                ('飲管 (+$1)', '', Status.UNKNOWN),
            ]:
                await page.set_content(f'<div id="app">{header}{card.format(name=name,sold_out=sold_out)}</div>')
                adapter = ADAPTERS['foodcloud']
                collected = await page.evaluate(COLLECT, {'menu':adapter.menu_selector,'product':adapter.product_selector,'platform':'foodcloud'})
                assert adapter.parse(Observation(**collected), {'identity':['Test Canteen']}).status == expected
            for mode, control, expected in [
                ('即時點餐', '<div class="addQty">+</div>', Status.OPEN),
                ('預訂餐點', '<div class="addQty">+</div>', Status.UNKNOWN),
                ('即時點餐', '<div class="addQty" style="pointer-events:none">+</div>', Status.UNKNOWN),
                ('即時點餐', '<div>售罄</div><div class="addQty">+</div>', Status.UNKNOWN),
            ]:
                await page.set_content(f'''Test Canteen<div class="orderInfo"><div class="infoLeft">外賣</div><div class="infoRight">{mode}</div></div>
                <div class="orderSelectPage"><div class="nav-right-item"><div class="item-name-left">Lunch</div>$88.0{control}</div></div>''')
                adapter = ADAPTERS['seito']
                collected = await page.evaluate(COLLECT, {'menu':adapter.menu_selector,'product':adapter.product_selector,'platform':'seito'})
                result = adapter.parse(Observation(**collected), {'identity':['Test Canteen']})
                assert result.status == expected
                if expected == Status.OPEN:
                    assert result.takeaway is True and result.dine_in is None
            await browser.close()
    asyncio.run(run())


def test_fast_checks_publish_before_slow_platform_finishes():
    async def run():
        fast_done, slow_release = asyncio.Event(), asyncio.Event()
        class Checker:
            async def check(self, source):
                if source['adapter'] == 'order_place' and source['order_url'].startswith('https://food.'):
                    fast_done.set()
                    return CheckResult(status=Status.OPEN, reason='Confirmed current ordering.')
                await slow_release.wait()
                return CheckResult(reason='No reliable evidence.')
        service = RestaurantService(Checker())
        service.restaurants = service.restaurants[:2]
        pending = asyncio.create_task(service.refresh())
        await fast_done.wait()
        # wait_for runs the checker in its own task; allow its parent to publish.
        for _ in range(10):
            if service.snapshot()[0].status == Status.OPEN:
                break
            await asyncio.sleep(0)
        assert service.snapshot()[0].status == Status.OPEN
        assert not pending.done()
        slow_release.set()
        await pending
    asyncio.run(run())


def test_pin2eat_current_chinese_closure_and_seito_identity():
    result = ADAPTERS['pin2eat'].parse(Observation('Chill Cup\n商家休息中\n今日休業\nHot drinks'), {'identity':['Chill Cup']})
    assert result.status == Status.CLOSED
    source = RestaurantService().sources['staff-club']
    result = ADAPTERS['seito'].parse(Observation('U.Green\n外賣\n即時點餐',menu_count=1,purchasable_count=1,current_order_enabled=True),source)
    assert result.status == Status.OPEN
