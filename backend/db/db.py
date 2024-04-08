from config import config
import asyncio
from collections import defaultdict
from model import Player
from .fill_datasets import fill_datasets
from .fill_teams import fill_bots

from contextlib import asynccontextmanager


class GameIdLock:
    def __init__(self):
        self.locks = defaultdict(asyncio.Lock)

    @asynccontextmanager
    async def lock(self, game_id):
        async with self.locks[game_id]:
            yield


game_id_lock = GameIdLock()


async def init_db():
    print("Initializing game_db")
    await fill_datasets()
    await fill_bots()
