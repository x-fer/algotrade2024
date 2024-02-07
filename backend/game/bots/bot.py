from typing import List
import abc
from model import Order


class Bot():
    def __init__(self, *args, **kwargs):
        pass

    @abc.abstractmethod
    def create_orders(self, *args, **kwargs) -> List[Order]:
        pass