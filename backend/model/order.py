from dataclasses import dataclass, field
from db.table import Table
import pandas as pd
from .order_types import OrderSide, OrderStatus, OrderType
from .enum_type import EnumType
from .resource import Resource


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
    filled_price: int = field(default=0)

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
