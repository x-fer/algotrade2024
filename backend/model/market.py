from dataclasses import dataclass
from db.table import Table
from .resource import Resource
from .enum_type import EnumType
from db import database


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
    volume: int

    @classmethod
    async def create(cls, *args, **kwargs) -> int:
        """
        Input: Values for new row
        Returns id of created row
        """
        return await super().create(*args, col_nums=0, **kwargs)

    @classmethod
    async def list_by_game_id_where_tick(cls, game_id, min_tick, max_tick, resource=None):
        resource_query = "" if resource is None else " AND resource=:resource"
        query = f"""
        SELECT * FROM {cls.table_name} 
        WHERE game_id=:game_id AND tick BETWEEN :min_tick AND :max_tick{resource_query}
        ORDER BY tick
        """
        values = {"game_id": game_id,
                  "min_tick": min_tick,
                  "max_tick": max_tick}
        if not resource is None:
            values["resource"] = resource.value
        result = await database.fetch_all(query, values)
        return [cls(**game) for game in result]
