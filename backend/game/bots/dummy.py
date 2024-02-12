from .bot import Bot
from typing import List
from model import Order


class DummyBot(Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = "dummy"

    async def run(self, *args, **kwargs) -> None:
        return
