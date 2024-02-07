from model import Resource, Trade
from .market import Market


class ResourceMarket(Market):
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
