import asyncio
import time
from fastapi import FastAPI
from contextlib import asynccontextmanager
from config import config
from db import database, migration
from game.tick import Ticker
from routers import admin_router, users_router
import psutil
import os
from logger import logger


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

            # logger.info(f"Tick took: {t2 - t1} seconds")
            if to_wait > 0:
                await asyncio.sleep(to_wait)
            else:
                logger.info("Tick took too long: ", t2 - t1)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await database.connect()
    asyncio.create_task(background_tasks())
    yield
    await database.disconnect()


app = FastAPI(lifespan=lifespan)


@app.middleware("http")
async def log_requests(request, call_next):
    start_time = time.time()
    
    response = await call_next(request)
    
    process_time = (time.time() - start_time) * 1000
    formatted_process_time = '{0:.2f}'.format(process_time)
    logger.debug(f"{request.client.host}:{request.client.port} - \"{request.method} {request.url.path}\" [{response.status_code}] completed_in={formatted_process_time}ms")
    
    return response

@app.get("/")
async def root():
    return {"message": "Hello World"}

app.include_router(admin_router, prefix="/admin")
app.include_router(users_router)
