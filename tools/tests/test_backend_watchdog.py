import pytest
from tools import login_start


def test_missing_backend_is_restored_but_healthy_backend_is_left_running(monkeypatch):
    attempts = []
    def offline(*args):
        raise ConnectionError('Stopped backend')
    monkeypatch.setattr(login_start.phone_preview, 'get_json', offline)
    monkeypatch.setattr(login_start.phone_preview, 'ensure_backend', lambda: attempts.append('start'))
    assert login_start.check_backend() is True
    monkeypatch.setattr(login_start.phone_preview, 'get_json', lambda _: {'app':'polyu-food-now', 'checker_ready':True})
    assert login_start.check_backend() is False
    assert attempts == ['start']


@pytest.mark.parametrize('health', [
    {'app':'another-app', 'checker_ready':True},
    {'app':'polyu-food-now', 'checker_ready':False},
])
def test_live_unrelated_or_unready_service_is_never_replaced(monkeypatch, health):
    monkeypatch.setattr(login_start.phone_preview, 'get_json', lambda _: health)
    monkeypatch.setattr(login_start.phone_preview, 'ensure_backend', lambda: pytest.fail('Must not replace a running service'))
    with pytest.raises(RuntimeError):
        login_start.check_backend()


def test_watchdog_keeps_retrying_after_failure_and_stops_when_disabled():
    sleeps, events, calls = [], [], []
    def check():
        calls.append(1)
        if len(calls) < 3:
            raise RuntimeError('Occupied port')
        return True
    login_start.monitor_backend(check, lambda:len(sleeps) == 3, sleeps.append, events.append)
    assert len(calls) == 3 and sleeps == [30, 30, 30]
    assert events == ['Backend recovery pending: RuntimeError: Occupied port', 'Backend restored.']


def test_disabled_watchdog_does_not_contact_or_start_backend():
    login_start.monitor_backend(lambda:pytest.fail('Disabled'), lambda:True,
                                lambda _:pytest.fail('Disabled'), lambda _:pytest.fail('Disabled'))
