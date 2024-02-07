from game.orderbook import OrderBook
from game.price_tracker import PriceTracker
from model import Order, Player, Resource, Trade


class Market():
    orderbook: OrderBook
    price_tracker = PriceTracker
    updated_orders: dict[int, Order]
    players: dict[int, Player]

    def __init__(self, resource: Resource, game_id: int):
        self.orderbook = OrderBook()
        self.price_tracker = PriceTracker(self.orderbook)
        self.resource = resource
        self.game_id = game_id

        callbacks = {
            'check_trade': self._check_trade,
            'on_trade': self._on_trade,
            'on_order_update': self._update_order,
        }

        for callback_type, callback in callbacks.items():
            self.orderbook.register_callback(callback_type, callback)


    def set_players(self, players: dict[int, Player]):
        self.updated_orders = dict()
        self.players = players


    def _update_order(self, order: Order):
        self.updated_orders[order.order_id] = order


    def _check_trade(self, trade: Trade):
        buyer_id = trade.buy_order.player_id
        seller_id = trade.sell_order.player_id

        can_buy = self.players[buyer_id].money >= trade.filled_money
        can_sell = self.players[seller_id][self.resource.name] >= trade.filled_size

        if not can_buy or not can_sell:
            return {"can_buy": can_buy, "can_sell": can_sell}
        return {"can_buy": True, "can_sell": True}


    def _on_trade(self, trade: Trade):
        buyer_id = trade.buy_order.player_id
        seller_id = trade.sell_order.player_id

        self.players[buyer_id].money -= trade.filled_money
        self.players[buyer_id][self.resource.name] += trade.filled_size

        self.players[seller_id].money += trade.filled_money
        self.players[seller_id][self.resource.name] -= trade.filled_size
