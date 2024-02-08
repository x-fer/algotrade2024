from model import Trade, Contract, Resource
from .market import Market
from config import config


class EnergyMarket(Market):
    def __init__(self):
        super().__init__(Resource.energy)
    

    def _check_trade(self, trade: Trade):
        bot_id = trade.buy_order.player_id
        player_id = trade.sell_order.player_id

        down_payment = Contract.get_down_payment(trade.filled_size, trade.filled_price)

        can_buy = self._players[bot_id].money >= trade.filled_money
        can_sell = self._players[player_id].money >= down_payment

        if not can_buy or not can_sell:
            return {"can_buy": can_buy, "can_sell": can_sell}
        return {"can_buy": True, "can_sell": True}


    def _on_trade(self, trade: Trade):
        bot_id = trade.buy_order.player_id
        player_id = trade.sell_order.player_id

        down_payment = Contract.get_down_payment(trade.filled_size, trade.filled_price)

        self._players[bot_id].money -= trade.filled_money
        self._players[player_id].money -= down_payment

        new_contract = Contract(
            contract_id=0,
            game_id=trade.buy_order.game_id,
            player_id=player_id,
            bot_id=bot_id,
            size=trade.filled_size,
            price=trade.filled_money,
            down_payment=down_payment,
            start_tick=self._tick_data.game.current_tick,
            end_tick=self._tick_data.game.current_tick + config["contracts"]["length"],
        )

        self._tick_data.new_contracts.append(new_contract)
