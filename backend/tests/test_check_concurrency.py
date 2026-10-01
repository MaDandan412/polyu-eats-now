import asyncio
import pytest
from backend.models import CheckResult
from backend.service import RestaurantService


@pytest.mark.parametrize('configured, expected', [('2', 2), ('0', 1)])
def test_small_server_checks_finish_with_bounded_parallelism(monkeypatch, configured, expected):
    monkeypatch.setenv('CHECK_CONCURRENCY', configured)

    class CountingChecker:
        active = 0
        peak = 0
        calls = 0

        async def check(self, source):
            self.active += 1
            self.peak = max(self.peak, self.active)
            try:
                await asyncio.sleep(0.01)
                self.calls += 1
                return CheckResult(reason='No live ordering evidence in this controlled check.')
            finally:
                self.active -= 1

    async def run():
        checker = CountingChecker()
        service = RestaurantService(checker)
        await asyncio.wait_for(service.refresh(), timeout=2)
        assert checker.calls == sum(bool(r.order_url) for r in service.restaurants)
        assert checker.peak == expected
        assert service.last_cycle is not None

    asyncio.run(run())
