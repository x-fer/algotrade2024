from redis_om import JsonModel, Field

from .order import Order


class Trade(JsonModel):
    buy_order: Order = Field(exclude=True)
    sell_order: Order = Field(exclude=True)
    tick: int

    filled_money: int
    filled_size: int
    filled_price: int

    buy_order_id: str = Field(default=None)
    sell_order_id: str = Field(default=None)

    def __post_init__(self):
        self.buy_order_id = self.buy_order.pk
        self.buy_order_id = self.buy_order.pk