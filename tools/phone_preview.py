"""Restartable Windows preview launcher. Sign-in startup is configured separately."""
import argparse
import ctypes
from ctypes import wintypes
import hashlib
import html
import json
import os
from pathlib import Path
import re
import socket
import subprocess
import sys
import time
import urllib.request

PROJECT = Path(__file__).resolve().parents[1]
RUNTIME = PROJECT / '.runtime'
LOCAL = 'http://127.0.0.1:8000'

def read_json(path):
    try:
        return json.loads(path.read_text(encoding='utf-8-sig'))
    except (OSError, ValueError):
        return {}

def write_json(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding='utf-8')

def get_json(url, timeout=3):
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    with opener.open(url, timeout=timeout) as response:
        return json.load(response)

def identity(pid):
    """Use kernel process identity so a stale PID from a prior boot is never reused."""
    kernel = ctypes.WinDLL('kernel32', use_last_error=True)
    kernel.OpenProcess.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
    kernel.OpenProcess.restype = wintypes.HANDLE
    kernel.CloseHandle.argtypes = [wintypes.HANDLE]
    kernel.QueryFullProcessImageNameW.argtypes = [wintypes.HANDLE, wintypes.DWORD, wintypes.LPWSTR, ctypes.POINTER(wintypes.DWORD)]
    kernel.GetProcessTimes.argtypes = [wintypes.HANDLE] + [ctypes.POINTER(wintypes.FILETIME)] * 4
    kernel.GetExitCodeProcess.argtypes = [wintypes.HANDLE, ctypes.POINTER(wintypes.DWORD)]
    handle = kernel.OpenProcess(0x1000, False, int(pid))
    if not handle:
        return None
    try:
        code = wintypes.DWORD()
        if not kernel.GetExitCodeProcess(handle, ctypes.byref(code)) or code.value != 259:
            return None
        size = wintypes.DWORD(32768)
        image = ctypes.create_unicode_buffer(size.value)
        stamps = [wintypes.FILETIME() for _ in range(4)]
        if not kernel.QueryFullProcessImageNameW(handle, 0, image, ctypes.byref(size)):
            return None
        if not kernel.GetProcessTimes(handle, *(ctypes.byref(stamp) for stamp in stamps)):
            return None
        return {'pid':int(pid), 'exe':image.value, 'created':(stamps[0].dwHighDateTime << 32) | stamps[0].dwLowDateTime}
    finally:
        kernel.CloseHandle(handle)

def matches(record):
    actual = identity(record.get('pid', 0))
    return bool(actual and actual == {key:record.get(key) for key in ('pid','exe','created')})

def stop_tunnel(record):
    if not matches(record):
        print('This preview connection is already stopped. No other process was changed.')
        return
    # Revalidate using the SAME termination handle to avoid a PID-reuse race.
    kernel = ctypes.WinDLL('kernel32', use_last_error=True)
    kernel.OpenProcess.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
    kernel.OpenProcess.restype = wintypes.HANDLE
    kernel.GetProcessTimes.argtypes = [wintypes.HANDLE] + [ctypes.POINTER(wintypes.FILETIME)] * 4
    kernel.TerminateProcess.argtypes = [wintypes.HANDLE, wintypes.UINT]
    kernel.CloseHandle.argtypes = [wintypes.HANDLE]
    handle = kernel.OpenProcess(0x1001, False, record['pid'])
    if not handle:
        raise RuntimeError('Cannot stop the preview connection.')
    try:
        stamps = [wintypes.FILETIME() for _ in range(4)]
        if not kernel.GetProcessTimes(handle, *(ctypes.byref(stamp) for stamp in stamps)):
            raise RuntimeError('Cannot verify the preview process.')
        created = (stamps[0].dwHighDateTime << 32) | stamps[0].dwLowDateTime
        if created != record['created']:
            raise RuntimeError('Process identity changed; nothing was stopped.')
        if not kernel.TerminateProcess(handle, 0):
            raise RuntimeError('Could not stop the verified preview process.')
    finally:
        kernel.CloseHandle(handle)
    print('Phone preview stopped. Local app and automatic checks stay running.')

def spawn(command, label):
    with (RUNTIME / f'{label}.stdout.log').open('wb') as out, (RUNTIME / f'{label}.stderr.log').open('wb') as err:
        process = subprocess.Popen(command, cwd=PROJECT, stdin=subprocess.DEVNULL, stdout=out, stderr=err,
            close_fds=True, creationflags=subprocess.CREATE_NO_WINDOW | subprocess.CREATE_NEW_PROCESS_GROUP)
    record = None
    for _ in range(20):
        record = identity(process.pid)
        if record:
            break
        if process.poll() is not None:
            raise RuntimeError(f'{label} exited. See .runtime/{label}.stderr.log')
        time.sleep(.1)
    if not record:
        raise RuntimeError(f'Cannot record {label} process identity.')
    write_json(RUNTIME / f'{label}.json', record)
    return record

def ensure_backend():
    try:
        health = get_json(LOCAL + '/api/health')
    except Exception:
        health = None
    if health and health.get('app') == 'polyu-food-now':
        if not health.get('checker_ready'):
            raise RuntimeError('App is running but the checker is not ready. See .runtime/backend.stderr.log')
        print('Automatic checker is already running.')
        return
    try:
        with socket.create_connection(('127.0.0.1',8000), timeout=1):
            raise RuntimeError('Port 8000 is in use by another or unhealthy service. No process was stopped.')
    except (ConnectionRefusedError, socket.timeout, OSError):
        pass
    python = PROJECT / '.venv/Scripts/python.exe'
    if not python.exists() or not (PROJECT / 'frontend/dist/index.html').exists():
        raise RuntimeError('Run start.ps1 -Setup first to install dependencies and build the app.')
    print('Starting app and automatic checker...')
    record = spawn([str(python), '-m', 'uvicorn', 'backend.main:app', '--host','127.0.0.1','--port','8000'], 'backend')
    for _ in range(60):
        try:
            health = get_json(LOCAL + '/api/health', timeout=1)
            if health.get('app') == 'polyu-food-now' and health.get('checker_ready'):
                print('Checker ready; outlet results will appear as checks finish.')
                return
        except Exception:
            pass
        if not matches(record):
            raise RuntimeError('App stopped during startup. See .runtime/backend.stderr.log')
        time.sleep(1)
    raise RuntimeError('Checker startup timed out. See .runtime/backend.stderr.log')

def cloudflared():
    local = PROJECT / 'tools/cloudflared.exe'
    previous = PROJECT.parent.parent / 'work/cloudflared.exe'
    for candidate in (local, previous):
        if candidate.exists():
            return candidate
    print('Downloading cloudflared from the official Cloudflare release...')
    release = get_json('https://api.github.com/repos/cloudflare/cloudflared/releases/latest', timeout=30)
    asset = next(asset for asset in release['assets'] if asset['name']=='cloudflared-windows-amd64.exe')
    expected = asset.get('digest','')
    if not expected.startswith('sha256:'):
        raise RuntimeError('Official release checksum unavailable; download was not run.')
    request = urllib.request.Request(asset['browser_download_url'],headers={'User-Agent':'PolyU-Eats-Now-Preview'})
    with urllib.request.urlopen(request, timeout=60) as response:
        data=response.read()
    if 'sha256:'+hashlib.sha256(data).hexdigest()!=expected:
        raise RuntimeError('Cloudflare download checksum mismatch; nothing was installed.')
    local.write_bytes(data)
    return local

def ensure_tunnel():
    fixed = read_json(RUNTIME/'fixed-phone.json')
    if fixed:
        url = fixed.get('url', '')
        if fixed.get('provider') != 'tailscale' or not re.fullmatch(r'https://polyueatsnow(?:-[0-9]+)?\.[a-z0-9-]+\.ts\.net', url):
            raise RuntimeError('Invalid fixed phone configuration; no alternate address was created.')
        try:
            health = get_json(url + '/api/health', timeout=10)
        except Exception as exc:
            raise RuntimeError('Fixed phone connection is not reachable yet. Check Tailscale login/network; the saved address stays unchanged.') from exc
        if health.get('app') != 'polyu-food-now' or not health.get('checker_ready'):
            raise RuntimeError('Fixed phone address does not reach this app with a ready checker.')
        print('Fixed Tailscale phone address is ready.')
        return url
    record=read_json(RUNTIME/'tunnel.json')
    if matches(record):
        if record.get('url'):
            print('Reusing this running phone preview connection.')
            return record['url']
        print('Waiting for the existing preview connection to finish starting...')
    else:
        record=spawn([str(cloudflared()),'--no-autoupdate','tunnel','--url',LOCAL,'--protocol','http2'], 'tunnel')
    print('Creating a new temporary HTTPS address...')
    for _ in range(60):
        log=(RUNTIME/'tunnel.stderr.log').read_text(encoding='utf-8', errors='replace')
        found=re.search(r'https://[a-z0-9-]+\.trycloudflare\.com',log)
        if found and 'Registered tunnel connection' in log:
            record['url']=found.group()
            write_json(RUNTIME/'tunnel.json',record)
            return record['url']
        if not matches(record):
            raise RuntimeError('Phone connection stopped. See .runtime/tunnel.stderr.log')
        time.sleep(1)
    raise RuntimeError('Phone connection startup timed out. See .runtime/tunnel.stderr.log')

def save_preview(url):
    (PROJECT/'PHONE_URL.txt').write_text(url+'\n', encoding='utf-8')
    qr=''
    try:
        import qrcode
        qrcode.make(url).save(RUNTIME/'phone-preview.png')
        qr='<img src=".runtime/phone-preview.png" width="260" height="260" alt="Phone preview QR code">'
    except ImportError:
        pass
    address_note = ('这是固定手机网址，重启电脑后仍使用同一地址。手机和朋友无需安装 Tailscale，直接在浏览器打开即可。'
                    if url.endswith('.ts.net') else
                    '目前手机使用临时网址，每次新建连接都会变化，请使用本页最新链接或二维码。')
    (PROJECT/'PHONE_PREVIEW.html').write_text('''<!doctype html><html lang="zh-Hans"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>PolyU Eats Now 手机入口</title><style>body{font:16px/1.8 system-ui;max-width:660px;margin:60px auto;padding:24px;background:#faf9f6;color:#30352c}h1,a{color:#a82635}a{overflow-wrap:anywhere}img{display:block;margin:24px 0}aside{padding:18px;background:#f3ecdf;border-radius:12px}</style><h1>PolyU Eats Now 手机入口</h1><p><a href="'''+html.escape(url,quote=True)+'">'+html.escape(url)+'</a></p>'+qr+'''<aside>电脑需要保持开机、联网且不休眠。已启用自动启动时，登录 Windows 后会在后台恢复；未启用时，双击「Start PolyU Eats Now.cmd」。'''+address_note+'''</aside><p>后台自动检查需要一点时间，已确认餐厅会逐家出现。三分钟以前的证据不能用于判断现在可下单。</p><p>电脑网页：<a href="http://127.0.0.1:8000">http://127.0.0.1:8000</a></p><p>电脑关机或休眠时不能获取实时数据；持续在线需要云端部署。</p></html>''',encoding='utf-8')

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--stop',action='store_true')
    parser.add_argument('--no-open',action='store_true')
    args=parser.parse_args()
    if os.name!='nt':
        raise RuntimeError('This desktop preview launcher is for Windows. Use Docker for Linux hosting.')
    RUNTIME.mkdir(exist_ok=True)
    if args.stop:
        stop_tunnel(read_json(RUNTIME/'tunnel.json'))
        return
    import msvcrt
    with (RUNTIME/'launcher.lock').open('a+b') as lock:
        if lock.tell()==0:
            lock.write(b'0')
            lock.flush()
        lock.seek(0)
        try:
            msvcrt.locking(lock.fileno(),msvcrt.LK_NBLCK,1)
        except OSError:
            print('The preview launcher is already starting. Wait for its link page; no duplicate was started.')
            return
        try:
            ensure_backend()
            url=ensure_tunnel()
            save_preview(url)
        finally:
            lock.seek(0)
            msvcrt.locking(lock.fileno(),msvcrt.LK_UNLCK,1)
    print('\nPhone preview: '+url)
    print('Local app: '+LOCAL)
    print('Saved phone link + optional QR: PHONE_PREVIEW.html')
    print('Keep the computer awake and connected. Fixed Tailscale URLs survive restart; temporary URLs change.')
    if not args.no_open:
        os.startfile(PROJECT/'PHONE_PREVIEW.html')

if __name__=='__main__':
    try:
        main()
    except Exception as exc:
        print('Preview could not start: '+str(exc),file=sys.stderr)
        sys.exit(1)
