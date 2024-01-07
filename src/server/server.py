import time
from fastapi import FastAPI
from db.db import database
from db import run_migrations
from contextlib import asynccontextmanager
from config import config

from routers import admin_router
from db import Table


@asynccontextmanager
async def lifespan(app: FastAPI):
    await database.connect()
    await run_migrations(database)

    yield

    await database.disconnect()


app = FastAPI(lifespan=lifespan)


@app.get("/")
async def root():
    return {"message": "Hello World"}

app.include_router(admin_router, prefix="/admin")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=config['host'], port=config['port'])
