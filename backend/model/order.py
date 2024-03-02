from dataclasses import dataclass, field
from db.table import Table
import pandas as pd
from .order_types import OrderSide, OrderStatus, OrderType
from .enum_type import EnumType
from .resource import Resource
from db.db import database


class ResourceField(EnumType):
    cls = Resource


class OrderSideField(EnumType):
    cls = OrderSide


class OrderStatusField(EnumType):
    cls = OrderStatus


class OrderTypeField(EnumType):
    cls = OrderType


@dataclass
class Order(Table):
    table_name = "orders"

    order_id: int
    game_id: int
    player_id: int

    price: int
    size: int
    tick: int

    timestamp: pd.Timestamp

    order_side: OrderSideField
    order_type: OrderTypeField = OrderTypeField(default=OrderType.LIMIT)
    order_status: OrderStatusField = OrderStatusField(
        default=OrderStatus.PENDING)

    filled_size: int = field(default=0)
    filled_money: int = field(default=0)
    filled_price: float = field(default=0)

    expiration_tick: int = field(default=1)

    resource: ResourceField = ResourceField(default=0)

    def __hash__(self) -> int:
        return hash(self.order_id)

    def __eq__(self, other) -> bool:
        if not isinstance(other, type(self)):
            return NotImplemented  # pragma: no cover
        return self.order_id == other.order_id and self.timestamp == other.timestamp

    def __lt__(self, other):  # pragma: no cover
        return self.timestamp < other.timestamp  # pragma: no cover

    @classmethod
    async def list_bot_orders_by_game_id(cls, game_id):
        query = f"""
        SELECT orders.* FROM {cls.table_name} 
        JOIN players ON orders.player_id = players.player_id
        WHERE orders.game_id=:game_id 
        AND players.is_bot IS TRUE
        AND orders.order_status=:order_status
        """
        values = {"game_id": game_id, "order_status": OrderStatus.ACTIVE.value}
        result = await database.fetch_all(query, values)
        return [cls(**x) for x in result]

    @classmethod
    async def list_best_orders_by_game_id(cls, game_id, order_side: OrderSide):
        best_orders = []
        for resource in Resource:
            if resource == Resource.energy:
                continue

            asc_desc = "ASC" if order_side == OrderSide.BUY else "DESC"
            query = f"""
            SELECT * FROM {cls.table_name}
            WHERE game_id=:game_id
            AND order_status=:order_status
            AND order_side=:order_side
            AND resource=:resource
            ORDER BY price {asc_desc}, size - filled_size DESC
            LIMIT 1
            """
            values = {"game_id": game_id,
                      "order_status": OrderStatus.ACTIVE.value,
                      "order_side": order_side.value,
                      "resource": resource.value}
            result = await database.fetch_all(query, values)
            best_orders.extend(result)

        return [cls(**x) for x in best_orders]
