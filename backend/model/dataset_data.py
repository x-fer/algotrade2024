from pprint import pprint
from db.table import Table
from dataclasses import dataclass
from db.db import database


@dataclass
class DatasetData(Table):
    table_name = "dataset_data"

    dataset_data_id: int
    dataset_id: int
    date: str
    tick: int

    coal: int
    uranium: int
    biomass: int
    gas: int
    oil: int
    geothermal: int
    wind: int
    solar: int
    hydro: int
    coal_price: int
    uranium_price: int
    biomass_price: int
    gas_price: int
    oil_price: int
    energy_demand: int
    max_energy_price: int

    def __getitem__(self, item):
        return self.__getattribute__(item.lower())

    @classmethod
    async def list_by_game_id_where_tick(cls, dataset_id, game_id, min_tick, max_tick):
        query = f"""
        SELECT dataset_data.* FROM {cls.table_name} 
        JOIN games ON dataset_data.dataset_id = games.dataset_id
        WHERE dataset_data.dataset_id=:dataset_id AND game_id=:game_id AND tick BETWEEN :min_tick AND :max_tick
        ORDER BY tick
        """
        values = {"dataset_id": dataset_id,
                  "game_id": game_id,
                  "min_tick": min_tick,
                  "max_tick": max_tick}
        result = await database.fetch_all(query, values)

        return [cls(**x) for x in result]
