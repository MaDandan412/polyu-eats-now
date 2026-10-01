import asyncio
from contextlib import asynccontextmanager, suppress
from pathlib import Path
from fastapi import FastAPI, Request, Response
from fastapi.staticfiles import StaticFiles
from starlette.middleware.gzip import GZipMiddleware
from .models import Restaurant
from .service import RestaurantService

@asynccontextmanager
async def lifespan(app: FastAPI):
    from .checker import BrowserChecker
    checker = BrowserChecker()
    await checker.start()
    service = RestaurantService(checker)
    app.state.service = service
    service.task = asyncio.create_task(service.loop())
    try:
        yield
    finally:
        service.task.cancel()
        with suppress(asyncio.CancelledError):
            await service.task
        await checker.stop()

app = FastAPI(title='PolyU Eats Now', version='0.1.0', lifespan=lifespan)
app.add_middleware(GZipMiddleware, minimum_size=1024)

@app.get('/api/restaurants', response_model=list[Restaurant])
async def restaurants(request: Request, response: Response):
    response.headers['Cache-Control'] = 'no-store'
    return request.app.state.service.snapshot()

@app.get('/api/health')
async def health(request: Request, response: Response):
    response.headers['Cache-Control'] = 'no-store'
    service = request.app.state.service
    return {'ok': True, 'app': 'polyu-food-now', 'version': '0.1.0', 'checker_ready': bool(service.checker and service.checker.ready), 'last_cycle': service.last_cycle}

# A single origin in production: build Vite, then run this application.
dist = Path(__file__).resolve().parents[1] / 'frontend' / 'dist'
if dist.exists():
    app.mount('/', StaticFiles(directory=dist, html=True), name='frontend')
