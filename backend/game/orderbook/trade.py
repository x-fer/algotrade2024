from dataclasses import dataclass
import pandas as pd
from .db import Order


@dataclass
class Trade:
    buy_order: Order
    sell_order: Order
    timestamp: pd.Timestamp

    filled_money: int
    filled_size: int
    filled_price: int