"""Start the desktop preview silently at Windows sign-in; retry slow boot networking."""
from datetime import datetime
import os
from pathlib import Path
import subprocess
import sys
import time

PROJECT = Path(__file__).resolve().parents[1]
RUNTIME = PROJECT / '.runtime'


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
            with (RUNTIME / 'login-start.log').open('w', encoding='utf-8') as log:
                for attempt in range(10):
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
                            return
                    except (OSError, subprocess.TimeoutExpired) as exc:
                        log.write(f'Startup attempt failed: {exc}\n')
                        log.flush()
                    if attempt < 9:
                        time.sleep(min(15 * (attempt + 1), 60))
                log.write('Startup could not complete. Use Start PolyU Eats Now.cmd to retry.\n')
        finally:
            lock.seek(0)
            msvcrt.locking(lock.fileno(), msvcrt.LK_UNLCK, 1)


if __name__ == '__main__':
    main()
