from dataclasses import dataclass
import pandas as pd
from .enums import *


@dataclass
class Order:
    timestamp: pd.Timestamp
    expiration: pd.Timestamp
    order_id: int
    trader_id: int

    price: int
    size: int

    filled_money: int
    filled_size: int

    side: OrderSide
    type: OrderType
    status: TradeStatus = TradeStatus.PENDING

    def __hash__(self) -> int:
        return hash(self.order_id)

    def __eq__(self, other) -> bool:
        if not isinstance(other, type(self)):
            return NotImplemented
        return self.order_id == other.order_id and self.timestamp == other.timestamp

    def __lt__(self, other):
        return self.timestamp < other.timestamp