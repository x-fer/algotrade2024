from dataclasses import dataclass
import pandas as pd

from db import Table, database

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

    async def _list_trades_by_player_id(
            cls, player_id, min_tick, max_tick, side_col, resource=None):
        resource_query = "" if resource is None else " AND trades.resource=:resource"
        query = f"""
        SELECT trades.* FROM trades 
        JOIN orders ON orders.order_id = trades.{side_col}
        WHERE orders.player_id=:player_id
        trades.tick BETWEEN :min_tick AND :max_tick
        {resource_query}
        ORDER BY trades.tick
        """
        values = {"player_id": player_id,
                  "min_tick": min_tick,
                  "max_tick": max_tick}
        if resource is not None:
            values["resource"] = resource.value
        result = await database.fetch_all(query, values)
        return [cls(**game) for game in result]


    async def list_buy_trades_by_player_id(
            cls, player_id, min_tick, max_tick, resource=None):
        return await cls._list_trades_by_player_id(
            player_id=player_id, min_tick=min_tick, max_tick=max_tick,
            side_col="buy_order_id", resource=resource)

    async def list_sell_trades_by_player_id(
            cls, player_id, min_tick, max_tick, resource=None):
        return await cls._list_trades_by_player_id(
            player_id=player_id, min_tick=min_tick, max_tick=max_tick,
            side_col="sell_order_id", resource=resource)

