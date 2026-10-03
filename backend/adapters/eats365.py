import re
from .base import Adapter

class Eats365Adapter(Adapter):
    # These menu selectors were observed on the actual Theatre Lounge store.
    menu_selector = '[id^="cat-"]'
    product_selector = '[id^="menu_product_"]'
    closed_lines = Adapter.closed_lines + ('service unavailable during designated time period',)

    async def prepare(self, page):
        # A fresh session must select the official pickup flow. Navigating
        # straight to /menu can redirect to the home page before products load.
        if not await page.locator(self.product_selector).first.is_visible():
            pickup = page.get_by_role('button', name='Pickup', exact=True)
            await pickup.wait_for(state='visible', timeout=10000)
            await pickup.click(timeout=3000)
        # A priced card opens a detail dialog, not a cart operation. The actual
        # purchase control lives in that dialog on the observed Eats365 store.
        await page.locator(self.product_selector).first.wait_for(state='visible', timeout=12000)
        cards = page.locator(self.product_selector)
        candidates = []
        for index in range(min(await cards.count(), 60)):
            card = cards.nth(index)
            text = await card.inner_text()
            if (re.search(r'\$\s*\d', text) and not re.search(
                    r'cutlery|utensil|straw|sold out|unavailable|餐具|飲管|售罄', text, re.I)):
                # Try simple items first; mandatory customizations can keep the
                # add button disabled without meaning the whole store is closed.
                candidates.append(('customizable' in text.casefold(), index))
        for _, index in sorted(candidates)[:8]:
            card = cards.nth(index)
            if not await card.is_visible():
                continue
            await card.locator('h3').click(timeout=3000)
            dialog = page.locator('.vm--modal[role="dialog"]')
            await dialog.wait_for(state='visible', timeout=3000)
            buy = dialog.locator('.c-add-to-cart-btn')
            if await buy.count() and await buy.is_visible():
                # COLLECT independently verifies the current mode, matched food,
                # price, and enabled button. Never click the add button.
                if await buy.evaluate("e => !e.hasAttribute('disabled') && e.getAttribute('aria-disabled') !== 'true' && !/(^|[-_\\s])disabled($|[-_\\s])/i.test(e.className) && getComputedStyle(e).pointerEvents !== 'none'"):
                    return
            await dialog.locator('.c-modal__close-btn.action-button').click(timeout=3000)
            await dialog.wait_for(state='hidden', timeout=3000)
