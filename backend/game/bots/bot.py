from typing import List
import abc
from model import Order


class Bot():
    def __init__(self, *args, **kwargs):
        self.player_id = 0

    @abc.abstractmethod
    async def run(self, *args, **kwargs) -> None:
        pass
