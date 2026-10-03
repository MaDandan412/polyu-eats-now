"""Opt-in, isolated browser profile for human-verified ordering sessions."""
import asyncio
import json
from pathlib import Path

RUNTIME = Path(__file__).resolve().parents[1] / '.runtime'
CONFIG_NAME = 'ordering-browser.json'


def is_verification(text):
    return any(value in text.casefold() for value in (
        'verify you are human', 'checking your browser', 'captcha',
        '正在進行安全驗證', '正在进行安全验证', '正在執行安全驗證',
        '確認您不是機器人', '确认您不是机器人', 'access denied'))


class OrderingSession:
    def __init__(self, runtime, directory=RUNTIME):
        self.runtime = runtime
        self.directory = directory
        self.context = None
        self.pages = {}
        self.visible = False
        self.lock = asyncio.Lock()

    def config(self):
        try:
            return json.loads((self.directory / CONFIG_NAME).read_text(encoding='utf-8'))
        except (OSError, ValueError):
            return {}

    async def page(self, url):
        async with self.lock:
            config = self.config()
            if config.get('enabled') is not True:
                return None
            show = config.get('verify_requested') is True
            if show and self.context:
                await self.close()
            if not self.context:
                self.directory.mkdir(parents=True, exist_ok=True)
                self.context = await self.runtime.chromium.launch_persistent_context(
                    str(self.directory / 'order-place-profile'), channel='chrome',
                    headless=not show, chromium_sandbox=True,
                    locale='en-HK', timezone_id='Asia/Hong_Kong',
                    viewport={'width':390, 'height':844},
                    is_mobile=True, has_touch=True,
                )
                context = self.context
                self.visible = show
                context.on('close', lambda _: self._closed(context))
                # Only an explicit local request opens a visible window. Normal
                # sign-in startup reuses this dedicated profile in the background.
                if show:
                    (self.directory / CONFIG_NAME).write_text(
                        json.dumps({'enabled':True, 'verify_requested':False}), encoding='utf-8')
            page = self.pages.get(url)
            if page is None or page.is_closed():
                page = await self.context.new_page()
                self.pages[url] = page
            return page

    def _closed(self, context):
        if self.context is context:
            self.context = None
            self.pages = {}
            self.visible = False

    async def close(self):
        context, self.context = self.context, None
        self.pages = {}
        self.visible = False
        if context:
            await context.close()
