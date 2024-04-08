from typing import Optional
from redis_om import JsonModel, Field

from model.resource import ResourceOrEnergy

from .order import Order


class Trade(JsonModel):
    buy_order: Optional[Order] = Field(exclude=True, default=None)
    sell_order: Optional[Order] = Field(exclude=True, default=None)
    tick: int = Field(index=True)

    filled_money: int
    filled_size: int
    filled_price: int

    resource: ResourceOrEnergy = Field(index=True, default=None)
    buy_order_id: str = Field(index=True, default=None)
    sell_order_id: str = Field(index=True, default=None)

    def __post_init__(self):
        if self.buy_order is not None:
            self.buy_order_id = self.buy_order.pk
            self.buy_order_id = self.buy_order.pk
            assert self.buy_order.resource == self.sell_order.resource
            self.resource = self.buy_order.resource.value