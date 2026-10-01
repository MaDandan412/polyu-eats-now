import asyncio
from datetime import datetime, timedelta, timezone
from backend.models import CheckResult, Status
from backend.service import RestaurantService, TTL_SECONDS

class FailingChecker:
    async def check(self, source):
        raise TimeoutError()

def verified(service, seconds=30):
    stamp=datetime.now(timezone.utc)-timedelta(seconds=seconds)
    service.restaurants[0]=service.restaurants[0].model_copy(update={
        'status':Status.OPEN,'last_checked':stamp,'reason':'Verified current menu.',
        'takeaway_available':True,'evidence':['Immediate ordering and purchasable food']})
    return stamp

def test_transient_failure_retains_valid_evidence_without_extending_its_age():
    service=RestaurantService(FailingChecker())
    stamp=verified(service)
    asyncio.run(service.refresh())
    r=service.snapshot()[0]
    assert r.status==Status.OPEN and r.last_checked==stamp and r.check_delayed
    assert r.takeaway_available is True and r.dine_in is False
    service.restaurants[0].last_checked=datetime.now(timezone.utc)-timedelta(seconds=TTL_SECONDS+1)
    r=service.snapshot()[0]
    assert r.status==Status.UNKNOWN and not r.check_delayed and not r.evidence

def test_expired_evidence_cannot_survive_a_failed_attempt():
    service=RestaurantService(FailingChecker())
    verified(service,TTL_SECONDS+1)
    asyncio.run(service.refresh())
    assert service.snapshot()[0].status==Status.UNKNOWN

def test_explicit_closed_and_new_uncertainty_replace_previous_open():
    class Checker:
        result=CheckResult(status=Status.CLOSED,reason='Official closed notice.')
        async def check(self, source):return self.result
    async def run():
        checker=Checker()
        service=RestaurantService(checker)
        verified(service)
        await service.refresh()
        assert service.snapshot()[0].status==Status.CLOSED
        assert not service.snapshot()[0].check_delayed
        verified(service)
        checker.result=CheckResult(reason='Sign-in required.')
        await service.refresh()
        assert service.snapshot()[0].status==Status.UNKNOWN
    asyncio.run(run())
