from databases import Database
from dataclasses import fields


class Table:
    table_name = None

    @classmethod
    def set_db(cls, database: Database):
        cls.database = database
        return cls

    @classmethod
    async def create(cls, *args, **kwargs):
        """Inserts element in table. Returns element id."""

        data = cls(0, *args, **kwargs)
        cols = [field.name for field in fields(data)]
        query = f"""INSERT INTO {cls.table_name}
            ({', '.join(cols[1:])}) 
            VALUES ({', '.join(f':{col}' for col in cols[1:])})
            RETURNING {cols[0]}"""
        values = {col: data.__getattribute__(col) for col in cols[1:]}

        return await cls.database.execute(query=query, values=values)

    @classmethod
    async def get(cls, id: int = None, **kwargs):
        """Finds element with WHERE statement. Throws exception if element doesn't exist"""
        cols = [field.name for field in fields(cls)]
        if id is not None:
            assert cols[0] not in kwargs, "Id column in where statement is set twice"
            kwargs[cols[0]] = id
        assert len(
            kwargs) >= 1, "Where statement must contain at least one column, but contains zero"
        assert set(kwargs.keys()).issubset(
            cols), f"Some columns in where statement don't exist in table {cls.table_name}"

        where = ' AND '.join(f'{col}=:{col}' for col in kwargs)
        if where: where = f" WHERE {where}"
        query = f"SELECT * FROM {cls.table_name}{where}"

        if cols[0] in kwargs:
            result = await cls.database.fetch(query, kwargs)
            assert result, f"Requested row in table {cls.__name__} doesn't exist"
            return cls(**result)
        else: 
            result = await cls.database.fetch_all(query, kwargs)
            return [cls(**team) for team in result]
