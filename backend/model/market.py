from dataclasses import dataclass
from db.table import Table
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
