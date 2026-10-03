"""Regress the live Eats365 detail dialog without cart or external requests."""
import asyncio
from playwright.async_api import async_playwright
from backend.adapters import ADAPTERS
from backend.adapters.base import Observation
from backend.checker import COLLECT
from backend.models import Status


def test_eats365_requires_immediate_pickup_and_matching_enabled_food_detail():
    async def run():
        async with async_playwright() as runtime:
            browser = await runtime.chromium.launch(headless=True)
            page = await browser.new_page()
            adapter = ADAPTERS['eats365']
            for timing, button, modal_name, card_text, closed, expected in [
                ('Ready for Pickup Immediately', 'Add for $75.00', 'Gimbap', '$75.00', '', Status.OPEN),
                ('Ready for Pickup Tomorrow', 'Add for $75.00', 'Gimbap', '$75.00', '', Status.UNKNOWN),
                ('Ready for Pickup Immediately', '', 'Gimbap', '$75.00', '', Status.UNKNOWN),
                ('Ready for Pickup Immediately', 'Add for $75.00', 'Other food', '$75.00', '', Status.UNKNOWN),
                ('Ready for Pickup Immediately', 'Add for $75.00', 'Gimbap', '$75.00 Sold out', '', Status.UNKNOWN),
                ('Ready for Pickup Immediately', 'Add for $75.00', 'Gimbap', '$75.00', 'Currently Closed', Status.CLOSED),
            ]:
                await page.set_content(f'''Test Canteen<p>{closed}</p>
                <div class="text"><div class="order-mode-text">Pickup</div><div class="detail">{timing}</div></div>
                <section id="cat-1"><div id="menu_product_1"><h3>Gimbap</h3>{card_text}</div></section>
                <div class="vm--modal" role="dialog"><div class="nameAndDesc"><h1>{modal_name}</h1></div>
                  <div class="c-add-to-cart-btn">{button}</div></div>''')
                observed = await page.evaluate(COLLECT, {'menu':adapter.menu_selector, 'product':adapter.product_selector, 'platform':'eats365'})
                result = adapter.parse(Observation(**observed), {'identity':['Test Canteen']})
                assert result.status == expected
                if expected == Status.OPEN:
                    assert result.takeaway is True and result.dine_in is None
                    original = await page.content()
                    for attribute in ['class="c-add-to-cart-btn c-btn--disabled"',
                                      'class="c-add-to-cart-btn" aria-disabled="true"',
                                      'class="c-add-to-cart-btn" style="pointer-events:none"']:
                        await page.set_content(original.replace('class="c-add-to-cart-btn"', attribute))
                        observed = await page.evaluate(COLLECT, {'menu':adapter.menu_selector, 'product':adapter.product_selector, 'platform':'eats365'})
                        assert adapter.parse(Observation(**observed), {'identity':['Test Canteen']}).status == Status.UNKNOWN
            await browser.close()
    asyncio.run(run())


def test_security_check_remains_unknown_even_with_menu_or_closed_text():
    adapter = ADAPTERS['order_place']
    for status in (200, 403):
        result = adapter.parse(Observation('Test Canteen\n正在进行安全验证\nCurrently Closed',
                              http_status=status, menu_count=1, purchasable_count=1,
                              current_order_enabled=True), {'identity':['Test Canteen']})
        assert result.status == Status.UNKNOWN and 'verification' in result.reason


def test_eats365_fresh_session_selects_pickup_and_inspects_food_without_cart_changes():
    async def run():
        async with async_playwright() as runtime:
            browser = await runtime.chromium.launch(headless=True)
            page = await browser.new_page()
            await page.set_content('''Test Canteen
              <button onclick="this.remove();document.querySelector('main').hidden=false">Pickup</button>
              <main hidden>
                <div><div class="order-mode-text">Pickup</div><div class="detail">Ready for Pickup Immediately</div></div>
                <section id="cat-1">
                  <div id="menu_product_1"><h3>Summer menu</h3></div>
                  <div id="menu_product_2"><h3 onclick="document.querySelector('[role=dialog]').hidden=false">Gimbap</h3>$75.00</div>
                </section>
              </main>
              <div class="vm--modal" role="dialog" hidden>
                <div class="nameAndDesc"><h1>Gimbap</h1></div>
                <div class="c-add-to-cart-btn" onclick="document.querySelector('#cart').textContent='1'">Add for $75.00</div>
              </div><output id="cart">0</output>''')
            adapter = ADAPTERS['eats365']
            await adapter.prepare(page)
            observed = await page.evaluate(COLLECT, {'menu':adapter.menu_selector, 'product':adapter.product_selector, 'platform':'eats365'})
            assert adapter.parse(Observation(**observed), {'identity':['Test Canteen']}).status == Status.OPEN
            assert await page.locator('#cart').inner_text() == '0'
            await browser.close()
    asyncio.run(run())
