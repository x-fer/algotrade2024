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
        """
        Input: Values for new row
        Returns id of created row
        """
        data = cls(0, *args, **kwargs)
        cols = [field.name for field in fields(data)]
        query = f"""INSERT INTO {cls.table_name}
            ({', '.join(cols[1:])}) 
            VALUES ({', '.join(f':{col}' for col in cols[1:])})
            RETURNING {cols[0]}"""
        values = {col: data.__getattribute__(col) for col in cols[1:]}
        return await cls.database.execute(query=query, values=values)
        
    
    @classmethod
    async def update(cls, **kwargs):
        """
        Input: Updated values, row id must be provided
        Returns ??
        """
        cols = [field.name for field in fields(cls)]
        assert set(kwargs.keys()).issubset(cols), f"Some columns don't exist in table {cls.table_name}"
        assert cols[0] in kwargs, "Row id wasn't provided"
        set_query = ', '.join(f'{col}=:{col}' for col in kwargs if col != cols[0])
        query = f"UPDATE {cls.table_name} SET {set_query} WHERE {cols[0]}=:{cols[0]}"
        return await cls.database.execute(query, kwargs)

    @classmethod
    async def delete(cls, **kwargs):
        """
        Input: Where clause
        Returns number of deleted rows
        """
        cols = [field.name for field in fields(cls)]
        assert set(kwargs.keys()).issubset(cols), f"Some columns don't exist in table {cls.table_name}"
        where = ' AND '.join(f'{col}=:{col}' for col in kwargs)
        if where: where = f" WHERE {where}"
        query = f"DELETE FROM {cls.table_name}{where}"
        return await cls.database.execute(query, kwargs)
    
    @classmethod
    async def get(cls, **kwargs):
        """
        Input: Where clause
        Returns selected row
        Throws exception if row doesn't exist
        """
        query, values = cls._select(**kwargs)
        result = await cls.database.fetch_one(query, values)
        assert result, f"Requested row in table {cls.__name__} doesn't exist"
        return cls(**result)
    
    @classmethod
    async def list(cls, **kwargs):
        """
        Input: Where clause
        Returns selected rows as a list
        """
        query, values = cls._select(**kwargs)
        result = await cls.database.fetch_all(query, values)
        return [cls(**team) for team in result]

    @classmethod
    def _select(cls, **kwargs):
        cols = [field.name for field in fields(cls)]
        assert set(kwargs.keys()).issubset(
            cols), f"Some columns don't exist in table {cls.table_name}"
        where = ' AND '.join(f'{col}=:{col}' for col in kwargs)
        if where: where = f" WHERE {where}"
        query = f"SELECT * FROM {cls.table_name}{where}"
        return query, kwargs
