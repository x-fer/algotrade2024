from pydantic import BaseModel

from .order import Order


class Trade(BaseModel):
    buy_order: Order
    sell_order: Order
    tick: int

    filled_money: int
    filled_size: int
    filled_price: int
