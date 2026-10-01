import pytest
from tools import phone_preview


def fixed_config(monkeypatch, url='https://polyueatsnow.example-net.ts.net'):
    monkeypatch.setattr(phone_preview, 'read_json', lambda _: {'provider': 'tailscale', 'url': url})
    monkeypatch.setattr(phone_preview, 'spawn', lambda *_: pytest.fail('Must not create a random tunnel after choosing a fixed address'))


def test_fixed_address_survives_network_failure_without_random_fallback(monkeypatch):
    fixed_config(monkeypatch)
    def disconnected(*args, **kwargs):
        raise OSError('No network at sign-in')
    monkeypatch.setattr(phone_preview, 'get_json', disconnected)
    with pytest.raises(RuntimeError, match='saved address stays unchanged'):
        phone_preview.ensure_tunnel()


def test_fixed_address_rejects_other_app_at_the_public_endpoint(monkeypatch):
    fixed_config(monkeypatch)
    monkeypatch.setattr(phone_preview, 'get_json', lambda *args, **kwargs: {'app': 'another-app', 'checker_ready': True})
    with pytest.raises(RuntimeError, match='does not reach this app'):
        phone_preview.ensure_tunnel()


def test_fixed_address_reuses_verified_ready_endpoint(monkeypatch):
    fixed_config(monkeypatch)
    monkeypatch.setattr(phone_preview, 'get_json', lambda *args, **kwargs: {'app': 'polyu-food-now', 'checker_ready': True})
    assert phone_preview.ensure_tunnel() == 'https://polyueatsnow.example-net.ts.net'


def test_fixed_address_cannot_be_redirected_to_an_arbitrary_host(monkeypatch):
    fixed_config(monkeypatch, url='https://unrelated.example.com')
    monkeypatch.setattr(phone_preview, 'get_json', lambda *_: pytest.fail('Invalid host must not be contacted'))
    with pytest.raises(RuntimeError, match='Invalid fixed phone configuration'):
        phone_preview.ensure_tunnel()
