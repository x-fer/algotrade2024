from dataclasses import dataclass, field
from datetime import datetime

from db.db import database
from db.table import Table
from model.enum_type import get_enum

from .order_types import OrderSide, OrderStatus, OrderType
from .resource import Energy, Resource


@dataclass
class Order(Table):
    table_name = "orders"

    order_id: int
    game_id: int
    player_id: int

    price: int
    size: int
    tick: int

    timestamp: datetime
    resource: Resource | Energy

    order_side: OrderSide
    order_type: OrderType = field(default=OrderType.LIMIT)
    order_status: OrderStatus = field(default=OrderStatus.PENDING)

    filled_size: int = field(default=0)
    filled_money: int = field(default=0)
    filled_price: float = field(default=0)

    expiration_tick: int = field(default=0)

    def __post_init__(self):
        self.order_side = get_enum(self.order_side, OrderSide)
        self.order_type = get_enum(self.order_type, OrderType)
        self.order_status = get_enum(self.order_status, OrderStatus)
        self.resource = get_enum(self.resource, Resource, Energy)

    def __hash__(self) -> int:
        return hash(self.order_id)

    def __eq__(self, other) -> bool:
        if not isinstance(other, type(self)):
            return NotImplemented  # pragma: no cover
        return self.order_id == other.order_id and self.timestamp == other.timestamp

    def __lt__(self, other):  # pragma: no cover
        return self.timestamp < other.timestamp  # pragma: no cover

    @classmethod
    async def cancel_player_orders(cls, player_id):
        query = f"""
        UPDATE {cls.table_name}
        SET order_status=:new_order_status
        WHERE player_id=:player_id 
        AND order_status=:order_status
        """
        values = {
            "player_id": player_id,
            "new_order_status": OrderStatus.USER_CANCELLED,
            "order_status": OrderStatus.ACTIVE,
        }
        await database.fetch_val(query, values)
        values = {
            "player_id": player_id,
            "new_order_status": OrderStatus.PENDING,
            "order_status": OrderStatus.CANCELLED,
        }
        await database.fetch_val(query, values)

    @classmethod
    async def count_player_orders(cls, game_id, player_id, resource: Resource):
        query = f"""
        SELECT COUNT(*) FROM {cls.table_name}
        WHERE game_id=:game_id
        AND player_id=:player_id
        AND (order_status='ACTIVE'
        OR order_status='PENDING'
        OR order_status='IN_QUEUE')
        AND resource=:resource
        """
        values = {
            "game_id": game_id,
            "player_id": player_id,
            "resource": resource.value,
        }
        result = await database.execute(query, values)
        return result

    @classmethod
    async def list_orders_by_game_id(cls, game_id):
        query = f"""
        SELECT orders.* FROM {cls.table_name} 
        JOIN players ON orders.player_id = players.player_id
        WHERE orders.game_id=:game_id
        AND (
            orders.order_status='ACTIVE'
            OR (
            orders.order_status='PENDING'
            AND players.is_bot IS TRUE
            ))
        """
        values = {"game_id": game_id}
        result = await database.fetch_all(query, values)
        return [cls(**x) for x in result]

    @classmethod
    async def list_bot_orders_by_game_id(cls, game_id):
        query = f"""
        SELECT orders.* FROM {cls.table_name} 
        JOIN players ON orders.player_id = players.player_id
        WHERE orders.game_id=:game_id
        AND players.is_bot IS TRUE
        AND (orders.order_status='ACTIVE'
        OR orders.order_status='PENDING')
        """
        values = {"game_id": game_id}
        result = await database.fetch_all(query, values)
        return [cls(**x) for x in result]

    @classmethod
    async def delete_bot_orders(cls, game_id):
        query = f"""
        DELETE FROM {cls.table_name}
        USING players 
        WHERE orders.player_id = players.player_id
        AND orders.game_id=:game_id 
        AND players.is_bot IS TRUE
        AND (orders.order_status='PENDING'
        OR orders.order_status='ACTIVE')
        """
        values = {"game_id": game_id}
        await database.execute(query, values)

    @classmethod
    async def list_best_orders_by_game_id(cls, game_id, order_side: OrderSide):
        best_orders = []
        for resource in Resource:
            asc_desc = "ASC" if order_side == OrderSide.BUY else "DESC"
            query = f"""
            SELECT orders.* FROM {cls.table_name} 
            JOIN players ON orders.player_id = players.player_id
            WHERE orders.game_id=:game_id
            AND (orders.order_status='ACTIVE'
            OR (
            orders.order_status='PENDING'
            AND players.is_bot IS TRUE
            ))
            AND order_side=:order_side
            AND resource=:resource
            ORDER BY price {asc_desc}, size - filled_size DESC
            LIMIT 1
            """
            values = {
                "game_id": game_id,
                "order_side": order_side.value,
                "resource": resource.value,
            }
            result = await database.fetch_all(query, values)
            best_orders.extend(result)

        return [cls(**x) for x in best_orders]
