from dataclasses import dataclass, field
from game.orderbook import OrderBook
from game.price_tracker import PriceTracker
from model import Order, Player, Trade, Game, Contract, Resource
import abc


@dataclass
class TickData:
    game: Game
    players: dict[int, Player]
    updated_orders: dict[int, Order] = field(default_factory=dict)
    new_contracts: list[Contract] = field(default_factory=list)


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

    def init_tick_data(self, tick_data: TickData):
        self._players = tick_data.players
        self._updated_orders = tick_data.updated_orders
        self._tick_data = tick_data

    def _update_order(self, order: Order):
        self._updated_orders[order.order_id] = order

    @abc.abstractmethod
    def _check_trade(self, trade: Trade):
        pass

    @abc.abstractmethod
    def _on_trade(self, trade: Trade):
        pass
