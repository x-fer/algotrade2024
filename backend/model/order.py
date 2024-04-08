from datetime import datetime
from typing import Union

from db.db import get_my_redis_connection
from model.enum_type import get_enum

from .order_types import OrderSide, OrderStatus
from .resource import Energy, Resource, ResourceOrEnergy
from redis_om import  Field, JsonModel


class Order(JsonModel):
    game_id: str = Field(index=True)
    player_id: str = Field(index=True)

    price: int
    size: int
    tick: int = Field(index=True)

    timestamp: datetime
    resource: ResourceOrEnergy = Field(index=True)

    order_side: OrderSide
    order_status: OrderStatus = Field(index=True, default=OrderStatus.PENDING.value)

    filled_size: int = Field(index=False, default=0)
    filled_money: int = Field(index=False, default=0)
    filled_price: float = Field(index=False, default=0)

    expiration_tick: int = Field(index=False, default=0)

    @property
    def order_id(self) -> str:
        return self.pk

    def __post_init__(self):
        self.order_side = get_enum(self.order_side, OrderSide)
        self.order_status = get_enum(self.order_status, OrderStatus)
        self.resource = get_enum(self.resource, ResourceOrEnergy)

    def __hash__(self) -> int:
        return hash(self.pk)

    def __eq__(self, other) -> bool:
        if not isinstance(other, type(self)):
            return ValueError("Not implemented")
        return self.pk == other.pk

    def __lt__(self, other):
        if not isinstance(other, type(self)):
            return ValueError("Wrong type")
        return self.timestamp < other.timestamp

    class Meta:
        database = get_my_redis_connection()