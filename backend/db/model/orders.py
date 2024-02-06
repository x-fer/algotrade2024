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

    order_type: OrderType
    order_side: OrderSide
    order_status: OrderStatus

    price: int
    size: int

    expiration_tick: int
    timestamp: pd.Timestamp

    resource: int

    filled_size: int = 0
    filled_money: int = 0
    filled_price: int = 0

    def __hash__(self) -> int:
        return hash(self.order_id)

    def __eq__(self, other) -> bool:
        if not isinstance(other, type(self)):
            return NotImplemented
        return self.order_id == other.order_id and self.timestamp == other.timestamp

    def __lt__(self, other):
        return self.timestamp < other.timestamp