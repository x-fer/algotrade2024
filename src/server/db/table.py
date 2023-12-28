from databases import Database
from dataclasses import fields

class Table:
    table_name = None

    @classmethod
    def set_db(cls, database: Database):
        cls.database = database

    @classmethod
    async def create(cls, *args):
        """Inserts element in table. Returns element id."""
        cols = [field.name for field in fields(cls)][1:]
        assert len(args) == len(cols), f"Expected {len(cols)} arguments, got {len(args)}"
        query = f"""INSERT INTO {cls.table_name} ({', '.join(cols)}) VALUES ({', '.join(f':{col}' for col in cols)})"""
        values = {cols[i]: args[i] for i in range(len(args))}
        return await cls.database.execute(query=query, values=values)

    @classmethod
    async def list(cls):
        """Returns list of all elements in table"""
        query = f"SELECT * FROM {cls.table_name}"
        # TODO: add try catch, mozda umjesto toga dodati error handler controller na razini fastapija
        result = await cls.database.fetch_all(query)
        return [cls(**team) for team in result]

    @classmethod
    async def get(cls, id: int=None, **kwargs):
        """Finds element with WHERE statement. Throws exception if element doesn't exist"""
        cols = [field.name for field in fields(cls)]
        if id is not None:
            assert cols[0] not in kwargs, "Id column in where statement is set twice"
            kwargs[cols[0]] = id
        assert len(kwargs) >= 1, "Where statement must contain at least one column, but contains zero"
        assert set(kwargs.keys()).issubset(cols[1:]), f"Some columns in where statement don't exist in table {cls.table_name}"

        where = ' AND '.join(f'{col}=:{col}' for col in kwargs)
        query = f"SELECT * FROM {cls.table_name} WHERE {where}"
        result = await cls.database.fetch_one(query, kwargs)
        assert result, f"Requested row in table {cls.__name__} doesn't exist"
        return cls(**result)
