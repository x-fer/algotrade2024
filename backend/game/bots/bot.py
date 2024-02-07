from typing import List
import abc
from db import Order
from ..tick_data import TickData


class Bot():
    def __init__(self, *args, **kwargs):
        pass

    @abc.abstractmethod
    def create_orders(self, tick_data: TickData) -> List[Order]:
        pass