from dataclasses import dataclass, fields
from db.table import Table
from db.db import database
from .resource import Resource


@dataclass
class Market(Table):
    table_name = "market"
    game_id: int
    tick: int
    resource: Resource
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
        data = cls(0, *args, **kwargs)
        cols = [field.name for field in fields(data)]
        query = f"""INSERT INTO {cls.table_name}
            ({', '.join(cols)}) 
            VALUES ({', '.join(f':{col}' for col in cols)})
            """
        values = {col: data.__getattribute__(col) for col in cols}
        return await database.fetch_val(query=query, values=values)
