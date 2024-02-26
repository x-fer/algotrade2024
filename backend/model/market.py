from dataclasses import dataclass
from db.table import Table
from db.db import database
from .resource import Resource
from .enum_type import EnumType


class ResourceField(EnumType):
    cls = Resource


@dataclass
class Market(Table):
    table_name = "market"
    game_id: int
    tick: int
    resource: ResourceField
    low: int
    high: int
    open: int
    close: int
    market: int

    @classmethod
    async def create(cls, *args, **kwargs) -> int:
        """
        Input: Values for new row
        Returns id of created row
        """
        return await super().create(*args, col_nums=0, **kwargs)

    @classmethod
    async def list_by_game_id_where_tick(cls, game_id, min_tick, max_tick):
        query = f"""
        SELECT * FROM {cls.table_name} 
        WHERE game_id=:game_id AND tick BETWEEN :min_tick AND :max_tick
        ORDER BY tick
        """
        values = {"game_id": game_id,
                  "min_tick": min_tick, "max_tick": max_tick}
        result = await database.fetch_all(query, values)
        return [cls(**game) for game in result]
