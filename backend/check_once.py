"""Run read-only status checks without starting the web server."""
import asyncio
import json
import sys
from pathlib import Path
from .checker import BrowserChecker
from .service import RestaurantService

async def main():
    checker = BrowserChecker()
    await checker.start()
    try:
        service = RestaurantService(checker)
        await service.refresh()
        result = [r.model_dump(mode='json') for r in service.snapshot()]
        if len(sys.argv) > 1:
            Path(sys.argv[1]).write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
        # Only print restaurant ids and status; session-style links stay out of logs.
        for r in result:
            print(r['id'], r['status'], r['reason'])
    finally:
        await checker.stop()

if __name__ == '__main__':
    asyncio.run(main())
