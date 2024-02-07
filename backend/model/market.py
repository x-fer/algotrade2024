from dataclasses import dataclass, fields
from db.table import Table
from db.db import database
from .resource import Resource
from .enum_type import enum_type


ResourceField = enum_type(Resource)


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
