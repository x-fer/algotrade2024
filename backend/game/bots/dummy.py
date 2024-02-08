from .bot import Bot
from typing import List
from model import Order


class DummyBot(Bot):
    def create_orders(self, *args, **kwargs) -> List[Order]:
        return []
