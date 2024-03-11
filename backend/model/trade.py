from dataclasses import dataclass
import pandas as pd

from db import Table

from .order import Order


@dataclass
class Trade:
    buy_order: Order
    sell_order: Order
    tick: int

    filled_money: int
    filled_size: int
    filled_price: int

@dataclass
class TradeDb(Table):
    table_name = "trades"

    trade_id: int
    buy_order_id: int
    sell_order_id: int
    tick: int

    filled_money: int
    filled_size: int
    filled_price: int

    @staticmethod
    def from_trade(trade: Trade):
        return TradeDb(
            trade_id=0,
            buy_order_id=trade.buy_order.order_id,
            sell_order_id=trade.sell_order.order_id,
            tick=trade.tick,
            filled_money=trade.filled_money,
            filled_price=trade.filled_price,
            filled_size=trade.filled_size
        )

    async def _get_trades_by_player_id():
        pass

    async def get_buy_trades_by_player_id():
        pass

    async def get_sell_trades_by_player_id():
        pass

