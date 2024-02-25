import asyncio
import time
from fastapi import FastAPI, HTTPException, Request
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from config import config
from db import database, migration
from game.tick import Ticker
from routers import admin_router, users_router
import psutil
import os
from logger import logger
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.middleware import SlowAPIMiddleware
from slowapi.errors import RateLimitExceeded


async def background_tasks():
    parent_process = psutil.Process(os.getppid())
    children = parent_process.children(
        recursive=True)

    if len(children) == 1 or children[1].pid == os.getpid():
        ticker = Ticker()

        while True:
            t1 = time.time()

            await ticker.run_all_game_ticks()

            t2 = time.time()

            tick_interval = config["game"]["tick_interval"]
            to_wait = tick_interval - time.time() % tick_interval

            if to_wait > 0:
                await asyncio.sleep(to_wait)
            else:
                logger.warn("Tick took too long, duration: ", t2 - t1)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await database.connect()
    asyncio.create_task(background_tasks())
    yield
    await database.disconnect()


def team_secret(request: Request):
    param = request.query_params.get("team_secret")
    if param is None:
        return get_remote_address(request)

    return param


limiter = Limiter(key_func=team_secret, default_limits=[
                  "10/second"], storage_uri="redis://localhost:6379/0")

app = FastAPI(lifespan=lifespan)

app.state.limiter = limiter

app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(SlowAPIMiddleware)


@app.exception_handler(Exception)
async def validation_exception_handler(request: Request, e: Exception):
    detail = str(e) if config["testing"] else "Internal server error"
    return JSONResponse(
        status_code=500,
        content=jsonable_encoder({"detail": detail}),
    )


async def log_request(message):
    logger.debug(message)


@app.middleware("http")
async def log_request_middleware(request: Request, call_next):
    body = await request.body()

    start_time = time.time()
    response = await call_next(request)
    process_time = (time.time() - start_time) * 1000
    formatted_process_time = '{0:.8f}'.format(process_time)
    url = f"{request.url.path}" + \
        (f"?{request.query_params}" if request.query_params else "")

    message = (f"{request.client.host}:{request.client.port} - "
               f"\"{request.method} {url}\" "
               f"[{response.status_code}], "
               f"completed in: {formatted_process_time}ms, "
               f"request body: {body}")
    asyncio.create_task(log_request(message))
    return response


@app.get("/")
async def root():
    return {"message": "Hello World"}


app.include_router(admin_router, prefix="/admin")
app.include_router(users_router)
