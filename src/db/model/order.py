from dataclasses import dataclass, field
from db.table import Table
from datetime import datetime
from orderbook.enums import *


@dataclass
class Order(Table):
    table_name = "orders"

    order_id: int
    game_id: int
    trader_id: int

    order_type: OrderType
    order_side: OrderSide
    order_status: OrderStatus

    price: int
    size: int

    expiration_tick: int
    timestamp: datetime = datetime

    resource: int = 0

    filled_size: int = 0
    filled_money: int = 0
    filled_price: int = 0
