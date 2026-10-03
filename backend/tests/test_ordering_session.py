import asyncio
import json
from types import SimpleNamespace
from backend.ordering_session import OrderingSession, is_verification


def test_session_is_opt_in_and_consumes_only_explicit_visible_window_request(tmp_path):
    async def run():
        calls = []
        class Page:
            def is_closed(self): return False
        class Context:
            def on(self, event, callback): self.closed = callback
            async def new_page(self): return Page()
            async def close(self): self.closed(self)
        class Chromium:
            async def launch_persistent_context(self, profile, **options):
                calls.append((profile, options))
                return Context()
        session = OrderingSession(SimpleNamespace(chromium=Chromium()), tmp_path)
        assert await session.page('https://food.order.place/store') is None
        assert not calls
        config = tmp_path / 'ordering-browser.json'
        config.write_text(json.dumps({'enabled':True, 'verify_requested':True}))
        first = await session.page('https://food.order.place/store')
        assert calls[0][1]['headless'] is False
        assert session.visible is True
        assert calls[0][1]['chromium_sandbox'] is True
        assert calls[0][0] == str(tmp_path / 'order-place-profile')
        assert json.loads(config.read_text())['verify_requested'] is False
        assert await session.page('https://food.order.place/store') is first
        await session.context.close()
        assert session.context is None and not session.pages
        assert session.visible is False
        await session.page('https://food.order.place/store')
        assert calls[-1][1]['headless'] is True
        assert session.visible is False
        await session.close()
        restarted = OrderingSession(SimpleNamespace(chromium=Chromium()), tmp_path)
        await restarted.page('https://food.order.place/store')
        assert calls[-1][1]['headless'] is True
        await restarted.close()
    asyncio.run(run())


def test_verification_detector_does_not_classify_normal_merchant_menu_as_challenge():
    assert is_verification('正在进行安全验证')
    assert is_verification('Verify you are human')
    assert not is_verification('Test canteen\n外賣\n即時點餐\n$75')
