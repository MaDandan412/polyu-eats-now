import asyncio
from datetime import datetime, timedelta, timezone
from fastapi.testclient import TestClient
from backend.adapters.base import Observation
from backend.adapters import ADAPTERS
from backend.models import CheckResult, Status
from backend.service import RestaurantService
from backend.main import app

SOURCE = {'identity': ['Test Canteen']}

def test_menu_alone_is_unknown():
    result = ADAPTERS['eats365'].parse(Observation('Test Canteen\nMenu', menu_count=1, purchasable_count=3), SOURCE)
    assert result.status == Status.UNKNOWN

def test_closed_beats_visible_menu_and_purchase_controls():
    result = ADAPTERS['eats365'].parse(Observation('Test Canteen\nCurrently Closed\nMenu', menu_count=1, purchasable_count=3), SOURCE)
    assert result.status == Status.CLOSED
    assert result.dine_in is None and result.takeaway is None

def test_open_requires_current_signal_and_purchasable_item():
    adapter = ADAPTERS['order_place']
    text = 'Test Canteen\nAccepting orders now'
    assert adapter.parse(Observation(text, menu_count=1), SOURCE).status == Status.UNKNOWN
    result = adapter.parse(Observation(text, menu_count=1, purchasable_count=1), SOURCE)
    assert result.status == Status.OPEN
    assert result.dine_in is None and result.takeaway is None

def test_explicit_single_service_is_limited():
    result = ADAPTERS['order_place'].parse(Observation('Test Canteen\nAccepting orders now', menu_count=1, purchasable_count=1, services={'dine_in':False,'takeaway':True}), SOURCE)
    assert result.status == Status.LIMITED and result.takeaway is True

def test_business_hours_and_item_sold_out_are_not_store_closure():
    result = ADAPTERS['order_place'].parse(Observation('Test Canteen\nBusiness hours 09:00–17:00\nClosed on Sundays\nCoffee sold out'), SOURCE)
    assert result.status == Status.UNKNOWN

def test_conflicting_status_is_unknown():
    result = ADAPTERS['eats365'].parse(Observation('Test Canteen\nCurrently Closed\nAccepting orders now', menu_count=1, purchasable_count=1), SOURCE)
    assert result.status == Status.UNKNOWN

def test_captcha_auth_rate_limit_and_wrong_merchant_are_unknown():
    adapter = ADAPTERS['order_place']
    for o in (Observation('Test Canteen\nVerify you are human\nCurrently Closed'), Observation('正在執行安全驗證\n確認您不是機器人'), Observation('CONTENT_NOT_FOUND'), Observation('Test Canteen\nSign in to order'), Observation('', http_status=429), Observation('Other restaurant\nCurrently Closed')):
        assert adapter.parse(o, SOURCE).status == Status.UNKNOWN

def test_orderplace_observed_chinese_closed_state():
    o = Observation('香港理工大學花園 理\n現在為非營業時間\n請於營業時間再試\n星期一 - 星期五 07:30 - 20:00')
    result = ADAPTERS['order_place'].parse(o, {'identity':['香港理工大學花園']})
    assert result.status == Status.CLOSED

def test_stale_evidence_expires_but_supported_services_remain():
    service = RestaurantService()
    service.restaurants[0].status = Status.OPEN
    service.restaurants[0].dine_in_available = True
    service.restaurants[0].last_checked = datetime.now(timezone.utc) - timedelta(seconds=181)
    assert service.snapshot()[0].status == Status.UNKNOWN
    assert service.snapshot()[0].dine_in is False
    assert service.snapshot()[0].dine_in_available is None

def test_checker_failure_overwrites_previous_open():
    class FailingChecker:
        async def check(self, source): raise RuntimeError('connection failed')
    service = RestaurantService(FailingChecker())
    service.restaurants[0].status = Status.OPEN
    asyncio.run(service.refresh())
    assert service.restaurants[0].status == Status.UNKNOWN
    assert len(service.snapshot()) == 16

def test_supplied_service_metadata_does_not_become_live_flags():
    service = RestaurantService()
    assert service.sources['communal-student']['reported_services']['dine_in'] is False
    assert service.snapshot()[0].dine_in is False
    assert all(r.dine_in_available is None and r.takeaway_available is None for r in service.snapshot())
    assert service.snapshot()[6].dine_in is False # Official online takeaway-only source.

def test_api_returns_sixteen_records_and_no_cache():
    app.state.service = RestaurantService()
    client = TestClient(app)
    response = client.get('/api/restaurants')
    assert response.status_code == 200
    assert response.headers['cache-control'] == 'no-store'
    assert response.headers['content-encoding'] == 'gzip'
    records = response.json()
    assert len(records) == 16
    assert set(records[0]) >= {'name','status','order_url','last_checked','dine_in','takeaway'}
    assert all(r['status'] == 'UNKNOWN' for r in records)

def test_ucr_asap_requires_a_purchasable_food_item():
    adapter = ADAPTERS['ucr_iqpos']
    o = Observation('Test Canteen\n預計自取時間: 即時', menu_count=1, current_order_enabled=True)
    assert adapter.parse(o, SOURCE).status == Status.UNKNOWN
    o.purchasable_count = 1
    o.services = {'takeaway':True}
    result = adapter.parse(o, SOURCE)
    assert result.status == Status.OPEN and result.takeaway is True and result.dine_in is None

def test_pin2eat_observed_closed_today_and_qlub_disabled_menus():
    assert ADAPTERS['pin2eat'].parse(Observation('Test Canteen\nClosed Today'), SOURCE).status == Status.CLOSED
    assert ADAPTERS['qlub'].parse(Observation('Test Canteen\n(Do Not Use) Qlub PolyU ALC Menu'), SOURCE).status == Status.UNKNOWN
