from enum import Enum
from orderbook import *
from game.price_tracker import *
from db.model import *


class Resource(Enum):
    coal = 0
    uranium = 1
    biomass = 2
    gas = 3
    oil = 4


class Market:
    def __init__(self, resource: Resource, game_id: int):
        self.orderbook = OrderBook()
        self.price_tracker = PriceTracker(self.orderbook)
        self.resource = resource
        self.game_id = game_id

        callbacks = {
            'check_add': self._check_add,
            'on_cancel': self._on_cancel,
            'on_begin_match': self._on_begin_match,
            'check_trade': self._check_trade,
            'on_trade': self._on_trade,
            'on_end_match': self._on_end_match,
            'on_complete': self._on_complete,
            'on_add_fail': self._on_add_fail
        }

        for callback_type, callback in callbacks.items():
            self.orderbook.register_callback(callback_type, callback)

    def _check_add(self, order: Order):
        player = Player.get(order.player_id)

        print(player)

    def _on_cancel(self):
        pass

    def _on_begin_match(self):
        pass

    def _check_trade(self):
        pass

    def _on_trade(self):
        pass

    def _on_end_match(self):
        pass

    def _on_complete(self):
        pass

    def _on_add_fail(self):
        pass
