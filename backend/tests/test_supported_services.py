import asyncio
from backend.models import CheckResult, Status
from backend.service import RestaurantService
from backend.checker import block_y_result, COLLECT
from backend.adapters import ADAPTERS
from backend.adapters.base import Observation
from playwright.async_api import async_playwright

def test_live_refresh_never_erases_supported_order_modes():
    class Checker:
        async def check(self, source):
            return CheckResult(status=Status.CLOSED, reason='Current ordering unavailable.')
    service=RestaurantService(Checker())
    asyncio.run(service.refresh())
    assert service.restaurants[0].dine_in is False
    assert service.restaurants[6].dine_in is False
    assert service.restaurants[6].takeaway is True
    assert service.restaurants[6].takeaway_available is None
    assert service.restaurants[6].status == Status.CLOSED

def test_block_y_preserves_independent_brand_results():
    opened=CheckResult(status=Status.OPEN,reason='Orderable.')
    closed=CheckResult(status=Status.CLOSED,reason='Not accepting orders.')
    unknown=CheckResult(reason='Could not check.')
    assert block_y_result([('Grove',opened),('Tai Tai',opened)]).status == Status.OPEN
    assert block_y_result([('Grove',opened),('Tai Tai',closed)]).status == Status.LIMITED
    assert block_y_result([('Grove',opened),('Tai Tai',unknown)]).status == Status.LIMITED
    assert block_y_result([('Grove',closed),('Tai Tai',closed)]).status == Status.CLOSED
    assert block_y_result([('Grove',closed),('Tai Tai',unknown)]).status == Status.UNKNOWN

def test_tai_tai_timer_and_real_product_controls():
    async def run():
        async with async_playwright() as p:
            browser=await p.chromium.launch()
            page=await browser.new_page()
            adapter=ADAPTERS['tai_tai']
            for timer, sold_out, disabled, expected in [
                ('14:54','','',Status.OPEN),
                ('00:00','','',Status.UNKNOWN),
                ('14:54','<img class="shouqin">','',Status.UNKNOWN),
                ('14:54','','pointer-events:none',Status.UNKNOWN),
            ]:
                await page.set_content(f'''PolyU 計時:{timer}<div class="goodsList"><ul class="rowRight">
                <li><div class="rightlist"><span class="itemName">Lunch</span><span class="price">$38</span>
                <span class="addAnddel"><i style="{disabled}"><img src="https://order.taitaiteaology.com/img/jia1.png"></i></span>{sold_out}</div></li></ul></div>''')
                collected=await page.evaluate(COLLECT,{'menu':adapter.menu_selector,'product':adapter.product_selector,'platform':'tai_tai'})
                result=adapter.parse(Observation(**collected),{'identity':['PolyU']})
                assert result.status == expected
            await browser.close()
    asyncio.run(run())

def test_orderplace_active_workspace_and_enabled_food_required():
    async def run():
        async with async_playwright() as p:
            browser=await p.chromium.launch()
            page=await browser.new_page()
            adapter=ADAPTERS['order_place']
            for mode, control, sold, expected in [
                ('外賣','<button class="add-btn">add</button>','',Status.OPEN),
                ('byod.modes.takeaway','<button class="add-btn">add</button>','',Status.OPEN),
                ('預訂外賣','<button class="add-btn">add</button>','',Status.UNKNOWN),
                ('外賣','<button class="add-btn" disabled>add</button>','',Status.UNKNOWN),
                ('外賣','<button class="add-btn">add</button>','<div class="div-soldout">已售罄</div>',Status.UNKNOWN),
            ]:
                await page.set_content(f'''Test Canteen<app-order-page><div data-testid="confirmed-mode-selection-box"><p data-testid="order-mode">{mode}</p></div>
                <app-item-grid><app-item-card><h3 class="item-name">Rice</h3><p data-testid="item-price">$35</p>{control}{sold}</app-item-card></app-item-grid></app-order-page>''')
                collected=await page.evaluate(COLLECT,{'menu':adapter.menu_selector,'product':adapter.product_selector,'platform':'order_place'})
                assert adapter.parse(Observation(**collected),{'identity':['Test Canteen']}).status==expected
            await browser.close()
    asyncio.run(run())
