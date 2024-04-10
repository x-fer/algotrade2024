from db.db import get_my_redis_connection
from model.enum_type import get_enum
from .resource import Resource, Energy
from redis_om import JsonModel, Field


class Market(JsonModel):
    game_id: str = Field(index=True)
    tick: int = Field(index=True)
    resource: Resource | Energy
    low: int
    high: int
    open: int
    close: int
    market: int
    volume: int

    class Meta:
        database = get_my_redis_connection()