from dataclasses import dataclass, field
from db.table import Table
from datetime import datetime
import pandas as pd
from .order_types import *


@dataclass
class Order(Table):
    table_name = "orders"

    order_id: int
    game_id: int
    player_id: int

    price: int
    size: int

    order_side: OrderSide
    order_type: OrderType = field(default=OrderType.LIMIT)
    order_status: OrderStatus = field(default=OrderStatus.PENDING)

    filled_size: int = field(default=0)
    filled_money: int = field(default=0)
    filled_price: int = field(default=0)

    timestamp: pd.Timestamp = field(default=0)
    expiration_tick: int = field(default=1)

    resource: int = field(default=0)

    def __hash__(self) -> int:
        return hash(self.order_id)

    def __eq__(self, other) -> bool:
        if not isinstance(other, type(self)):
            return NotImplemented
        return self.order_id == other.order_id and self.timestamp == other.timestamp

    def __lt__(self, other):
        return self.timestamp < other.timestamp