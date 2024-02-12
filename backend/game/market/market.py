from dataclasses import dataclass, field
from game.orderbook import OrderBook
from game.price_tracker import PriceTracker
from model import Order, Player, Trade, Game, Resource
import abc


class Market():
    def __init__(self, resource: Resource):
        self.resource = resource
        self.orderbook = OrderBook()
        self.price_tracker = PriceTracker(self.orderbook)

        callbacks = {
            'check_trade': self._check_trade,
            'on_trade': self._on_trade,
            'on_order_update': self._update_order,
        }

        for callback_type, callback in callbacks.items():
            self.orderbook.register_callback(callback_type, callback)

    @abc.abstractmethod
    def cancel(self, order: Order):
        pass

    @abc.abstractmethod
    def match(self, order: Order, tick: int):
        pass

    @abc.abstractmethod
    def _update_order(self, order: Order):
        pass

    @abc.abstractmethod
    def _check_trade(self, trade: Trade):
        pass

    @abc.abstractmethod
    def _on_trade(self, trade: Trade):
        pass
