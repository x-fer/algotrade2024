from dataclasses import dataclass, field
from db.table import Table
from datetime import datetime
from orderbook import *
import pandas as pd


@dataclass
class Orders(Table):
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
