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


async def background_tasks():
    parent_process = psutil.Process(os.getppid())
    children = parent_process.children(
        recursive=True)

    ticker = Ticker()

    if len(children) == 1 or children[1].pid == os.getpid():
        while True:
            t1 = time.time()

            await ticker.run_all_game_ticks()

            t2 = time.time()

            tick_interval = config["game"]["tick_interval"]
            to_wait = tick_interval - time.time() % tick_interval

            if to_wait > 0:
                await asyncio.sleep(to_wait)
            else:
                print("Tick took too long: ", t2 - t1)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await database.connect()
    if config['testing']:
        await migration.drop_tables()
        await migration.run_migrations()
        await migration.fill_tables()
    else:
        await migration.run_migrations()
    # await print_hello()
    asyncio.create_task(background_tasks())
    yield

    await database.disconnect()


app = FastAPI(lifespan=lifespan)


@app.get("/")
async def root():
    return {"message": "Hello World"}


app.include_router(admin_router, prefix="/admin")
app.include_router(users_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app,
                host=config["server"]['host'],
                port=config["server"]['port'])
