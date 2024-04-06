from typing import Any
from dataclasses import fields, asdict
from .db import database
from enum import Enum


class Table:
    table_name = None

    @classmethod
    async def create(cls, col_nums: int = 1, *args, **kwargs) -> int:
        data = cls(*[0 for _ in range(col_nums)], *args, **kwargs)
        cols = [field.name for field in fields(data)]
        query = f"""INSERT INTO {cls.table_name}
            ({', '.join(cols[col_nums:])}) 
            VALUES ({', '.join(f':{col}' for col in cols[col_nums:])})
            RETURNING {cols[0]}"""
        values = {col: data.__getattribute__(col) for col in cols[col_nums:]}
        values = _transform_kwargs(values)
        return await database.fetch_val(query=query, values=values)

    @classmethod
    async def update(cls, **kwargs) -> int:
        """
        Input: Updated values, row id must be provided
        Returns: Updated rows including including rows whose values did not change
        """
        cols = [field.name for field in fields(cls)]
        assert set(kwargs.keys()).issubset(
            cols), f"Some columns don't exist in table {cls.table_name}"
        assert cols[0] in kwargs, "Row id wasn't provided"
        set_query = ', '.join(
            f'{col}=:{col}' for col in kwargs if col != cols[0])
        query = f"UPDATE {cls.table_name} SET {set_query} WHERE {cols[0]}=:{cols[0]} RETURNING *"
        kwargs = _transform_kwargs(kwargs)
        return await database.fetch_val(query, kwargs)

    @classmethod
    async def create_many(cls, l: list, col_nums: int = 1) -> int:
        if len(l) == 0:
            return 0

        cols = [field.name for field in fields(cls)]
        def _remove_cols(val):
            for col in cols[:col_nums]:
                val.pop(col, None)
        def _add_num(i, val):
            return f"{val}_{i}"
        def _add_num_val(val):
            i, val = val
            for col in cols[col_nums:]:
                val[_add_num(i, val)] = val.pop[col]
            return val
        def _add_num_form(val):
            i, val = val
            return [_add_num(i, col) for col in cols[col_nums:]]
        def _format_one(val):
            return f"({', '.join(val)})"
        
        values = map(asdict, l)
        values = map(_transform_kwargs, values)
        values = map(_remove_cols, values)
        values = map(_add_num_val, enumerate(values))

        values_format = [f':{col}' for col in cols[col_nums:]]
        values_format = [values_format] * len(values)
        values_format = map(_add_num_form, enumerate(values_format))
        values_format = map(_format_one, values_format)
        values_format = ", ".join(values_format)
        print("values_format", values_format)
        print("values", values)

        query = f"""INSERT INTO {cls.table_name}
            ({', '.join(cols[col_nums:])})
            VALUES [{values_format}]
            RETURNING {cols[0]}"""

        return await database.execute_many(query, values)

    @classmethod
    async def update_many(cls, l: list) -> int:
        if len(l) == 0:
            return 0

        values = [_transform_kwargs(asdict(obj)) for obj in l]

        cols = [field.name for field in fields(cls)]
        set_query = ', '.join(
            f'{col}=:{col}' for col in values[0] if col != cols[0])
        query = f"UPDATE {cls.table_name} SET {set_query} WHERE {cols[0]}=:{cols[0]} RETURNING *"

        return await database.execute_many(query, values)

    @classmethod
    async def delete(cls, **kwargs) -> int:
        """
        Input: Where clause
        Returns number of deleted rows
        """
        cols = [field.name for field in fields(cls)]
        assert set(kwargs.keys()).issubset(
            cols), f"Some columns don't exist in table {cls.table_name}"
        where = ' AND '.join(f'{col}=:{col}' for col in kwargs)
        if where:
            where = f" WHERE {where}"
        query = f"DELETE FROM {cls.table_name}{where} RETURNING *"
        kwargs = _transform_kwargs(kwargs)
        return await database.fetch_val(query, kwargs)

    @classmethod
    async def get(cls, **kwargs):
        """
        Input: Where clause
        Returns selected row
        Throws exception if row doesn't exist
        """
        kwargs = _transform_kwargs(kwargs)
        query, values = cls._select(**kwargs)
        result = await database.fetch_one(query, values)
        assert result, f"Requested row in table {cls.__name__} doesn't exist"
        return cls(**result)

    @classmethod
    async def list(cls, **kwargs):
        """
        Input: Where clause
        Returns selected rows as a list
        """
        query, values = cls._select(**kwargs)
        result = await database.fetch_all(query, values)
        return [cls(**obj) for obj in result]

    @classmethod
    async def count(cls, **kwargs) -> int:
        query, values = cls._select(selected_cols="COUNT(*)", **kwargs)
        result = await database.execute(query, values)
        return result

    @classmethod
    def _select(cls, selected_cols="*", **kwargs):
        cols = [field.name for field in fields(cls)]
        assert set(kwargs.keys()).issubset(
            cols), f"Some columns don't exist in table {cls.table_name}"
        where = ' AND '.join(f'{col}=:{col}' for col in kwargs)
        if where:
            where = f" WHERE {where}"
        query = f"SELECT {selected_cols} FROM {cls.table_name}{where}"

        kwargs = _transform_kwargs(kwargs)
        return query, kwargs


def _transform_kwargs(kwargs):
    return {k: _transform_enum(v) for k, v in kwargs.items()}


def _transform_enum(value) -> Any:
    if isinstance(value, Enum):
        return value.value
    return value
