from pprint import pprint
from typing import List, Dict
from game.orderbook.orderbook import OrderBook
from game.price_tracker.price_tracker import PriceTracker
from model import Resource, Trade, Order
from model.player import Player


class ResourceMarket:
    def __init__(self, resource: Resource, players: Dict[int, Player]):
        self.resource = resource
        self.orderbook = OrderBook()
        self.price_tracker = PriceTracker(self.orderbook)
        self._players = players

        callbacks = {
            'check_trade': self._check_trade,
            'on_trade': self._on_trade,
            'on_order_update': self._update_order,
        }

        for callback_type, callback in callbacks.items():
            self.orderbook.register_callback(callback_type, callback)

    def cancel(self, orders: List[Order]):
        self._updated = {}
        for order in orders:
            self.orderbook.cancel_order(order.order_id)
        return self._updated

    def match(self, orders: Order, tick: int):
        self._updated = {}
        for order in orders:
            self.orderbook.add_order(order)
        self.orderbook.match(tick)
        return self._updated

    def _update_order(self, order: Order):
        self._updated[order.order_id] = order

    def _check_trade(self, trade: Trade):
        buyer_id = trade.buy_order.player_id
        seller_id = trade.sell_order.player_id

        can_buy = self._players[buyer_id].money >= trade.filled_money
        can_sell = self._players[seller_id][self.resource.name] >= trade.filled_size

        if not can_buy or not can_sell:
            return {"can_buy": can_buy, "can_sell": can_sell}
        return {"can_buy": True, "can_sell": True}

    def _on_trade(self, trade: Trade):
        buyer_id = trade.buy_order.player_id
        seller_id = trade.sell_order.player_id

        self._players[buyer_id].money -= trade.filled_money
        self._players[buyer_id][self.resource.name] += trade.filled_size

        self._players[seller_id].money += trade.filled_money
        self._players[seller_id][self.resource.name] -= trade.filled_size
