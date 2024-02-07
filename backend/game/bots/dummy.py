from .bot import Bot
from typing import List
from db import Order
from ..tick_data import TickData


class DummyBot(Bot):
    def create_orders(self, tick_data: TickData) -> List[Order]:
        return []