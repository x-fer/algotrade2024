from pprint import pprint
from typing import List, Dict
from model.order_types import OrderStatus
from game.orderbook.orderbook import OrderBook
from game.price_tracker.price_tracker import PriceTracker
from model import Resource, Trade, Order
from model.player import Player
from logger import logger


class ResourceMarket:
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

        self.logger = logger

        def _get_player(player_id):
            raise NotImplementedError(
                "ResourceMarket._get_player must be set before using the market")

        self._get_player = _get_player

    def set_get_player(self, get_player):
        self._get_player = get_player

    def cancel(self, orders: List[Order]):
        self._updated = {}
        for order in orders:

            try:
                self.orderbook.cancel_order(order.order_id)
            except ValueError as e:
                logger.error(
                    f"Error cancelling order for id {order.order_id}: {e}, updating **only** in db, not orderbook.")

                order.order_status = OrderStatus.CANCELLED
                self._update_order(order)

        return self._updated

    def match(self, orders: Order, tick: int):
        self._updated = {}
        for order in orders:
            self.orderbook.add_order(order)
        self.orderbook.match(tick)

        print(self.resource)
        print(self.orderbook)

        return self._updated

    def _update_order(self, order: Order):
        self._updated[order.order_id] = order

    def _check_trade(self, trade: Trade):
        buyer_id = trade.buy_order.player_id
        seller_id = trade.sell_order.player_id

        buyer = self._get_player(buyer_id)
        seller = self._get_player(seller_id)

        can_buy = buyer.money >= trade.filled_money
        can_sell = seller[self.resource.name] >= trade.filled_size

        if buyer.is_bot:
            can_buy = True

        if seller.is_bot:
            can_sell = True

        if not can_buy or not can_sell:
            return {"can_buy": can_buy, "can_sell": can_sell}

        return {"can_buy": True, "can_sell": True}

    def _on_trade(self, trade: Trade):
        buyer_id = trade.buy_order.player_id
        seller_id = trade.sell_order.player_id

        buyer = self._get_player(buyer_id)
        seller = self._get_player(seller_id)

        if not buyer.is_bot:
            buyer.money -= trade.filled_money
            buyer[self.resource.name] += trade.filled_size

        if not seller.is_bot:
            seller.money += trade.filled_money
            seller[self.resource.name] -= trade.filled_size
