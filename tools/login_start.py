"""Start at sign-in and restore a stopped backend without changing the phone URL."""
from contextlib import redirect_stdout
from datetime import datetime
import os
from pathlib import Path
import subprocess
import sys
import time

if __package__:
    from . import phone_preview
else:
    import phone_preview

PROJECT = Path(__file__).resolve().parents[1]
RUNTIME = PROJECT / '.runtime'
DISABLED = RUNTIME / 'watchdog.disabled'


def check_backend():
    try:
        health = phone_preview.get_json(phone_preview.LOCAL + '/api/health')
    except Exception:
        health = None
    if health:
        if health.get('app') != 'polyu-food-now':
            raise RuntimeError('Local port belongs to another app; nothing was changed.')
        if not health.get('checker_ready'):
            raise RuntimeError('The app is running but its checker is not ready; no process was stopped.')
        return False
    # The launcher independently refuses occupied ports and starts only this
    # project's backend. It never terminates another app or changes the URL.
    phone_preview.ensure_backend()
    return True


def monitor_backend(check, should_stop, sleep, report, interval=30):
    failure = None
    while not should_stop():
        try:
            restarted = check()
            if restarted or failure:
                report('Backend restored.' if restarted else 'Backend is healthy again.')
            failure = None
        except Exception as exc:
            message = f'{type(exc).__name__}: {exc}'
            if message != failure:
                report('Backend recovery pending: ' + message)
            failure = message
        sleep(interval)


def main():
    if os.name != 'nt':
        raise RuntimeError('Windows sign-in launcher only.')
    import msvcrt
    RUNTIME.mkdir(exist_ok=True)
    # A manual launch or repeated sign-in must never create parallel retry loops.
    with (RUNTIME / 'login-start.lock').open('a+b') as lock:
        if lock.tell() == 0:
            lock.write(b'0')
            lock.flush()
        lock.seek(0)
        try:
            msvcrt.locking(lock.fileno(), msvcrt.LK_NBLCK, 1)
        except OSError:
            return
        try:
            with (RUNTIME / 'login-start.log').open('a', encoding='utf-8') as log:
                def report(message):
                    log.write(f'{datetime.now().isoformat(timespec="seconds")} {message}\n')
                    log.flush()
                for attempt in range(10):
                    if DISABLED.exists():
                        return
                    log.write(f'{datetime.now().isoformat(timespec="seconds")} startup attempt {attempt + 1}\n')
                    log.flush()
                    try:
                        result = subprocess.run(
                            [str(PROJECT / '.venv/Scripts/python.exe'), '-u',
                             str(PROJECT / 'tools/phone_preview.py'), '--no-open'],
                            cwd=PROJECT, stdin=subprocess.DEVNULL, stdout=log, stderr=log,
                            creationflags=subprocess.CREATE_NO_WINDOW,
                            timeout=240,
                        )
                        if result.returncode == 0:
                            break
                    except (OSError, subprocess.TimeoutExpired) as exc:
                        log.write(f'Startup attempt failed: {exc}\n')
                        log.flush()
                    if attempt < 9:
                        time.sleep(min(15 * (attempt + 1), 60))
                else:
                    report('Phone startup could not complete; backend monitoring remains active. The saved URL stays unchanged.')
                report('Backend watchdog active; checking locally every 30 seconds.')
                with redirect_stdout(log):
                    monitor_backend(check_backend, DISABLED.exists, time.sleep, report)
                report('Backend watchdog disabled; the running app was left untouched.')
        finally:
            lock.seek(0)
            msvcrt.locking(lock.fileno(), msvcrt.LK_UNLCK, 1)


if __name__ == '__main__':
    main()
