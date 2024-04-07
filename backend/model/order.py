from datetime import datetime

from model.enum_type import get_enum

from .order_types import OrderSide, OrderStatus
from .resource import Energy, Resource
from redis_om import  Field, JsonModel, get_redis_connection


class Order(JsonModel):
    game_id: str = Field(index=True)
    player_id: str = Field(index=True)

    price: int
    size: int
    tick: int

    timestamp: datetime
    resource: Resource | Energy

    order_side: OrderSide
    order_status: OrderStatus = Field(index=True, default=OrderStatus.PENDING)

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
        self.resource = get_enum(self.resource, Resource, Energy)

    def __hash__(self) -> int:
        return hash(self.order_id)

    def __eq__(self, other) -> bool:
        if not isinstance(other, type(self)):
            return False
        return self.order_id == other.order_id and self.timestamp == other.timestamp

    def __lt__(self, other):
        if not isinstance(other, type(self)):
            return ValueError("Wrong type")
        return self.timestamp < other.timestamp

    class Meta:
        database = get_redis_connection(port=6479)