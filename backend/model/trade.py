from typing import Optional
from redis_om import JsonModel, Field

from db.db import get_my_redis_connection
from model.order import Order
from model.resource import ResourceOrEnergy


class Trade(JsonModel):
    tick: int = Field(index=True)

    total_price: int
    trade_size: int
    trade_price: int

    resource: ResourceOrEnergy = Field(index=True, default=None)
    buy_order_id: str = Field(index=True, default=None)
    sell_order_id: str = Field(index=True, default=None)

    def __post_init__(self):
        if hasattr(self, "buy_order"):
            assert hasattr(self, "sell_order")
            self.buy_order: Order
            self.sell_order: Order
            self.buy_order_id = self.buy_order.pk
            self.buy_order_id = self.buy_order.pk
            assert self.buy_order.resource == self.sell_order.resource
            self.resource = self.buy_order.resource.value

    class Meta:
        database = get_my_redis_connection()