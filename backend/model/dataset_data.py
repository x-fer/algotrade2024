from dataclasses import dataclass
from datetime import datetime

from fastapi import HTTPException

dataset_data_id = 0
dataset_data_db = {}


@dataclass
class DatasetData:
    table_name = "dataset_data"

    dataset_data_id: int
    dataset_id: int
    date: datetime
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
        global dataset_data_db, dataset_data_id

        return [dataset_data for dataset_data in dataset_data_db.values() if
                dataset_data.dataset_id == dataset_id and
                dataset_data.game_id == game_id and
                min_tick <= dataset_data.tick <= max_tick]

    @classmethod
    async def create_many(cls, data):
        global dataset_data_db, dataset_data_id

        for dataset_data in data:
            dataset_data_id += 1
            dataset_data_db[dataset_data_id] = dataset_data

    @classmethod
    async def get(cls, **kwargs):
        global dataset_data_db, dataset_data_id

        out = [dataset_data for dataset_data in dataset_data_db.values() if all(
            getattr(dataset_data, k) == v for k, v in kwargs.items())]

        if len(out) == 0:
            raise HTTPException(400, "DatasetData does not exist")

        return DatasetData(**out[0].__dict__)

    @classmethod
    async def count(cls, **kwargs):
        global dataset_data_db, dataset_data_id

        return len([dataset_data for dataset_data in dataset_data_db.values() if all(getattr(dataset_data, k) == v for k, v in kwargs.items())])
