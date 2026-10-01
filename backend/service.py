import asyncio
import json
import logging
import os
from datetime import datetime, timezone
from pathlib import Path
from .models import Restaurant, CheckResult, Status

logger = logging.getLogger(__name__)
DATA = Path(__file__).resolve().parents[1] / 'data'
TTL_SECONDS = 180

class RestaurantService:
    def __init__(self, checker=None):
        self.checker = checker
        catalogue = json.loads((DATA / 'restaurants.json').read_text(encoding='utf-8'))
        sources = json.loads((DATA / 'sources.json').read_text(encoding='utf-8')) if (DATA / 'sources.json').exists() else {}
        self.sources = sources
        directory = 'https://www.polyu.edu.hk/cfso/campus-environment-and-facilities/catering-facilities/catering-outlets/'
        self.restaurants = []
        for r in catalogue:
            source = sources.get(r['id'], {})
            services = source.get('reported_services', {})
            self.restaurants.append(Restaurant(**r, platform=source.get('platform'), order_url=source.get('order_url'),
                info_url=source.get('info_url', directory), **services,
                services_source=source.get('services_source', 'not-published'), services_source_url=source.get('services_source_url'),
                online_payment=source.get('online_payment'), mobile_only=source.get('mobile_only', False),
                session_minutes=source.get('session_minutes'), ordering_notes_source_url=source.get('ordering_notes_source_url')))
        self.last_cycle: datetime | None = None
        self.lock = asyncio.Lock()
        self.task: asyncio.Task | None = None
        try:
            concurrency = int(os.getenv('CHECK_CONCURRENCY', '4'))
        except ValueError:
            concurrency = 4
        # Small servers can check fewer pages together; zero must not deadlock
        # the refresh loop. Keep the tested upper bound of four contexts.
        self.semaphore = asyncio.Semaphore(max(1, min(4, concurrency)))

    def snapshot(self):
        now = datetime.now(timezone.utc)
        values = []
        for r in self.restaurants:
            if r.last_checked and (now - r.last_checked).total_seconds() <= TTL_SECONDS:
                values.append(r.model_copy(deep=True))
            else:
                values.append(r.model_copy(update={'status': Status.UNKNOWN, 'dine_in_available': None, 'takeaway_available': None, 'reason': 'Awaiting a fresh automatic availability check.', 'evidence': [], 'check_delayed': False}, deep=True))
        return values

    async def refresh(self):
        if self.lock.locked():
            return
        async with self.lock:
            async def check(index, r):
                async with self.semaphore:
                    source = self.sources.get(r.id, {})
                    try:
                        if not r.order_url:
                            result = CheckResult(reason='Mobile-app ordering only. Web availability cannot be confirmed.')
                        elif self.checker:
                            result = await asyncio.wait_for(self.checker.check(source), timeout=45)
                        else:
                            result = CheckResult(reason='Status checker is unavailable.')
                    except asyncio.CancelledError:
                        raise
                    except Exception as exc:
                        # Never expose tokenized URLs, page dumps, or stack traces to clients.
                        logger.warning('Check failed for %s: %s', r.id, type(exc).__name__)
                        # A failed attempt is not fresh evidence. Keep a verified
                        # result only inside its ORIGINAL validity window, and
                        # tell the UI that the latest attempt failed. Explicit
                        # closure, conflicting evidence and platform barriers
                        # returned by adapters always replace the previous result.
                        if r.status != Status.UNKNOWN and r.last_checked and (datetime.now(timezone.utc) - r.last_checked).total_seconds() <= TTL_SECONDS:
                            self.restaurants[index] = r.model_copy(update={'check_delayed': True}, deep=True)
                            return
                        result = CheckResult(reason='Official ordering system could not be checked.')
                    live = result.model_dump()
                    live['dine_in_available'] = live.pop('dine_in')
                    live['takeaway_available'] = live.pop('takeaway')
                    checked = r.model_copy(update={**live, 'last_checked': datetime.now(timezone.utc), 'check_delayed': False})
                    # Publish each completed result so a slow platform cannot hold
                    # back restaurants that have already been confirmed.
                    self.restaurants[index] = checked
            await asyncio.gather(*(check(index, r) for index, r in enumerate(self.restaurants)))
            self.last_cycle = datetime.now(timezone.utc)

    async def loop(self):
        while True:
            await self.refresh()
            await asyncio.sleep(max(30, int(os.getenv('CHECK_INTERVAL_SECONDS', '60'))))
