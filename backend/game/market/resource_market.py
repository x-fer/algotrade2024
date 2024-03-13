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
            'on_end_match': self._on_end_match,
        }

        for callback_type, callback in callbacks.items():
            self.orderbook.register_callback(callback_type, callback)

        self.players: Dict[int, Player] = None
        self._updated: Dict[int, Order] = {}
        self.tick_trades: List[Trade] = None

    def set_players(self, players: Dict[int, Player]):
        self.players = players

    def cancel(self, orders: List[Order]) -> Dict[int, Order]:
        self._updated = {}
        for order in orders:
            try:
                self.orderbook.cancel_order(order.order_id)
            except ValueError as e:
                logger.warn(
                    f"Error cancelling order for order_id {order.order_id}: {e}")
                order.order_status = OrderStatus.CANCELLED
                self._update_order(order)

        return self._updated

    def match(self, orders: List[Order], tick: int) -> Dict[int, Order]:
        self._updated = {}
        for order in orders:
            try:
                self.orderbook.add_order(order)
            except ValueError as e:
                logger.warn(
                    f"Error adding order for order_id {order.order_id}: {e}")
        self.orderbook.match(tick)

        logger.debug(f"Matching:\n"
                     + self.resource.name + " " + str(tick) + "\n"
                     + self.orderbook.__str__() + "\n")
        return self._updated

    def _update_order(self, order: Order):
        self._updated[order.order_id] = order

    def _check_trade(self, trade: Trade):
        buyer_id = trade.buy_order.player_id
        seller_id = trade.sell_order.player_id

        buyer = self._get_player(buyer_id)
        seller = self._get_player(seller_id)

        if buyer is None:
            can_buy = False
        elif buyer.is_bot:
            can_buy = True
        else:
            can_buy = buyer.money >= trade.filled_money

        if seller is None:
            can_buy = False
        elif seller.is_bot:
            can_sell = True
        else:
            can_sell = seller[self.resource.name] >= trade.filled_size

        return {"can_buy": can_buy, "can_sell": can_sell}

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

    def _get_player(self, player_id: int) -> Player:
        if self.players is None:
            raise ValueError("Players dictionary not set")
        if player_id not in self.players:
            logger.warn(f"Player with id {player_id} not in dictionary")
            return None
        return self.players[player_id]

    def _on_end_match(self, match_trades: List[Order]):
        self.tick_trades = match_trades

    def get_last_tick_trades(self):
        return self.tick_trades
