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

    def __post_init__(self):
        self.resource = get_enum(self.resource, Resource, Energy)

    # @classmethod
    # async def create(cls, *args, **kwargs) -> int:
    #     raise Exception()
    
    # @classmethod
    # async def list_by_game_id_where_tick(cls, game_id, min_tick, max_tick, resource: Resource | Energy = None):
    #     raise Exception()

    class Meta:
        database = get_my_redis_connection()