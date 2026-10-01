from .base import Adapter
from ..models import CheckResult

class UCRAdapter(Adapter):
    menu_selector = '#app'
    product_selector = '.clickable.row--dense'
    category_selector = '.v-tab'
    closed_lines = Adapter.closed_lines + ('非營業時間', '現在未能下單', '未能下單', 'not available for ordering')

    async def prepare(self, page):
        await page.locator('.v-tab').first.wait_for(state='visible', timeout=12000)
        # Close only the observed advertising carousel, not authentication/terms dialogs.
        await self.close_ad(page)

    async def close_ad(self, page):
        ad_close = page.locator('.v-dialog--active:has(.v-carousel) button.pos-a.t-2.r-2')
        if await ad_close.is_visible():
            await ad_close.click(timeout=3000)
            await ad_close.wait_for(state='hidden', timeout=3000)

    async def select_category(self, page, category):
        await self.close_ad(page)
        try:
            await category.click(timeout=3000)
        except Exception:
            # The promotion can arrive between the visibility check and click.
            # Retry only if that specific dismissible carousel appeared.
            ad_close = page.locator('.v-dialog--active:has(.v-carousel) button.pos-a.t-2.r-2')
            if not await ad_close.is_visible():
                raise
            await self.close_ad(page)
            await category.click(timeout=3000)

class FoodCloudAdapter(UCRAdapter):
    product_selector = '.clickable.inner, .clickable.row--dense'

class SeitoAdapter(Adapter):
    menu_selector = '.orderSelectPage'
    product_selector = '.nav-right-item'
    category_selector = '.nav-left-item'
    closed_lines = Adapter.closed_lines + ('目前未能點餐', '停止接受訂單')

    async def prepare(self, page):
        start = page.locator('.startText:not(.preorder)')
        await start.wait_for(state='visible', timeout=15000)
        await start.click(timeout=3000)
        for _ in range(20):
            if await page.locator('.orderSelectPage').is_visible():
                return
            close = page.locator('.closeMediaBtn')
            if await close.is_visible():
                await close.click(timeout=3000)
            await page.wait_for_timeout(400)

class TaiTaiAdapter(Adapter):
    menu_selector = '.goodsList .rowRight'
    product_selector = '.rowRight .rightlist'
    closed_lines = Adapter.closed_lines + ('暫停營業', '店鋪已關閉', '店鋪休息中', '目前不接受訂單')

    def parse(self, observation, source):
        if not observation.text.strip() and observation.title == 'Grove Mobile Order':
            return CheckResult(reason='Brand selection is reachable, but this platform’s food menus have not loaded for automated checks.')
        return super().parse(observation, source)

class OdouiAdapter(Adapter):
    def parse(self, observation, source):
        if '未知錯誤' in observation.text:
            return CheckResult(reason='The official ordering page reports an error before a restaurant menu can load.')
        return super().parse(observation, source)
