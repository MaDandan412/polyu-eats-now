import re
from .base import Adapter

class OrderPlaceAdapter(Adapter):
    menu_selector = 'app-order-page app-item-grid, app-menu, .menu-list, [data-menu]'
    product_selector = 'app-order-page app-item-card, app-menu-item, .menu-item, .product-item, [data-product-id]'
    closed_lines = Adapter.closed_lines + ('we are currently closed', 'ordering is currently unavailable', '請於營業時間再試')

    async def prepare(self, page):
        start = page.locator('button.btn-order-now')
        await start.wait_for(state='visible', timeout=10000)
        # The home button renders before store configuration and translations.
        await page.wait_for_timeout(4000)
        consent = page.locator('.snackbar-cookies-consent button.action-btn').filter(has_text=re.compile(r'byod\.cookies\.snackbar\.accept|accept|接受|同意', re.I))
        if await consent.count() == 1 and await consent.is_visible():
            await consent.click(timeout=3000)
        mode = page.locator('app-mode-selector-page mat-expansion-panel-header').filter(has=page.locator('use[href$="#takeaway_ol"]'))
        for _ in range(2):
            if not await start.is_visible():
                break
            await start.click(timeout=4000)
            try:
                await mode.wait_for(state='visible', timeout=4000)
                await mode.click(timeout=3000)
                break
            except Exception:
                # Links can go directly to a closed notice/menu. Only repeat
                # navigation when the unchanged home button is still visible.
                if not await start.is_visible():
                    break
