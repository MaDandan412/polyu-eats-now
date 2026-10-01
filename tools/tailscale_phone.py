"""Configure ONLY the PolyU Eats Now localhost service as a persistent Funnel."""
import argparse
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import time

from phone_preview import LOCAL, PROJECT, RUNTIME, ensure_backend, get_json, save_preview, write_json


def executable():
    candidate = Path(os.environ.get('ProgramFiles', r'C:\Program Files')) / 'Tailscale/tailscale.exe'
    if candidate.is_file():
        return str(candidate)
    found = shutil.which('tailscale')
    if found:
        return found
    raise RuntimeError('Install the official Tailscale Windows app and log in first.')


def command(*args, timeout=15):
    result = subprocess.run([executable(), *args], capture_output=True, text=True,
                            encoding='utf-8', errors='replace', timeout=timeout,
                            creationflags=subprocess.CREATE_NO_WINDOW)
    if result.returncode:
        raise RuntimeError(result.stderr.strip() or 'Tailscale command failed.')
    return result.stdout


def status():
    state = json.loads(command('status', '--json'))
    if state.get('BackendState') != 'Running':
        raise RuntimeError('Tailscale is not connected. Use its tray icon > Log in, then try again.')
    return state


def own_funnel(config, hostname):
    web = config.get('Web', {}).get(hostname + ':443', {})
    return (web.get('Handlers', {}).get('/', {}).get('Proxy') == LOCAL
            and config.get('AllowFunnel', {}).get(hostname + ':443') is True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--enable', action='store_true')
    args = parser.parse_args()
    if os.name != 'nt':
        raise RuntimeError('This helper is for Windows.')
    RUNTIME.mkdir(exist_ok=True)
    state = status()
    hostname = state.get('Self', {}).get('DNSName', '').rstrip('.')
    config = json.loads(command('funnel', 'status', '--json'))
    if args.enable:
        # Never clear or replace an existing unrelated Serve/Funnel setup.
        if config and not (hostname.startswith('polyueatsnow.') and own_funnel(config, hostname)):
            raise RuntimeError('An existing Tailscale service is configured. Nothing was changed; inspect it before proceeding.')
        ensure_backend()
        command('set', '--hostname=polyueatsnow', '--accept-dns=false')
        for _ in range(20):
            hostname = status().get('Self', {}).get('DNSName', '').rstrip('.')
            if re.fullmatch(r'polyueatsnow(?:-[0-9]+)?\.[a-z0-9-]+\.ts\.net', hostname):
                break
            time.sleep(.5)
        else:
            raise RuntimeError('Waiting for Tailscale to assign the requested device name. Retry shortly.')
        # Show any first-use browser approval link rather than accepting it silently.
        subprocess.run([executable(), 'funnel', '--bg', '--https=443', LOCAL],
                       check=True, timeout=300)
        config = json.loads(command('funnel', 'status', '--json'))
    if not own_funnel(config, hostname):
        raise RuntimeError('The PolyU Eats Now public Funnel is not enabled yet.')
    url = 'https://' + hostname
    if not re.fullmatch(r'https://polyueatsnow(?:-[0-9]+)?\.[a-z0-9-]+\.ts\.net', url):
        raise RuntimeError('Unexpected hostname. No fixed address was saved.')
    health = get_json(url + '/api/health', timeout=15)
    if health.get('app') != 'polyu-food-now' or not health.get('checker_ready'):
        raise RuntimeError('Public URL does not reach this app with a ready checker.')
    write_json(RUNTIME / 'fixed-phone.json', {'provider': 'tailscale', 'url': url, 'target': LOCAL})
    save_preview(url)
    print('Fixed phone address verified: ' + url)
    print('Saved link and QR: PHONE_PREVIEW.html')


if __name__ == '__main__':
    try:
        main()
    except Exception as exc:
        print('Fixed phone setup: ' + str(exc), file=sys.stderr)
        sys.exit(1)
