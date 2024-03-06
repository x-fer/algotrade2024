import asyncio
import time
from fastapi import FastAPI, Request
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from config import config
from db import database
from game.tick import Ticker
from routers import admin_router, users_router
import psutil
import os
from logger import logger
from docs import tags_metadata, description


async def background_tasks():
    parent_process = psutil.Process(os.getppid())
    children = parent_process.children(
        recursive=True)

    if len(children) == 1 or children[1].pid == os.getpid():
        ticker = Ticker()

        await ticker.run_tick_manager()


@asynccontextmanager
async def lifespan(app: FastAPI):
    await database.connect()
    asyncio.create_task(background_tasks())
    yield
    await database.disconnect()


app = FastAPI(
    title="Algotrade API",
    version="0.0.1",
    description=description,
    openapi_tags=tags_metadata,
    lifespan=lifespan,
    # docs_url=None
)

# app.state.limiter = limiter

# app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# app.add_middleware(SlowAPIMiddleware)


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


@app.get("/", include_in_schema=False)
async def root():
    return {"message": "Hello World"}


app.include_router(admin_router, prefix="/admin")
app.include_router(users_router)
