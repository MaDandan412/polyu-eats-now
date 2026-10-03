"""Ask the local checker to show its own isolated verification window."""
import json
from pathlib import Path


def main():
    runtime = Path(__file__).resolve().parents[1] / '.runtime'
    runtime.mkdir(exist_ok=True)
    target = runtime / 'ordering-browser.json'
    temporary = runtime / 'ordering-browser.request.tmp'
    temporary.write_text(json.dumps({'enabled':True, 'verify_requested':True}), encoding='utf-8')
    temporary.replace(target)
    print('The checker will open its isolated Chrome window on the next check.')
    print('Complete official browser verification yourself. No account password is needed.')


if __name__ == '__main__':
    main()
