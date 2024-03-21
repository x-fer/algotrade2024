from dataclasses import dataclass
from db.table import Table
from model.enum_type import get_enum
from .resource import Resource, Energy
from db import database


@dataclass
class Market(Table):
    table_name = "market"
    game_id: int
    tick: int
    resource: Resource | Energy
    low: int
    high: int
    open: int
    close: int
    market: int
    volume: int

    def __post_init__(self):
        self.resource = get_enum(self.resource, Resource, Energy)

    @classmethod
    async def create(cls, *args, **kwargs) -> int:
        """
        Input: Values for new row
        Returns id of created row
        """
        return await super().create(*args, col_nums=0, **kwargs)

    @classmethod
    async def list_by_game_id_where_tick(cls, game_id, min_tick, max_tick, resource: Resource | Energy = None):
        resource_query = "" if resource is None else " AND resource=:resource"
        query = f"""
        SELECT * FROM {cls.table_name} 
        WHERE game_id=:game_id AND tick BETWEEN :min_tick AND :max_tick{resource_query}
        ORDER BY tick
        """
        values = {"game_id": game_id,
                  "min_tick": min_tick,
                  "max_tick": max_tick}
        if resource is not None:
            values["resource"] = resource.value
        result = await database.fetch_all(query, values)
        return [cls(**game) for game in result]
