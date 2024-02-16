from db.table import Table
from dataclasses import dataclass


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
    energy_demand: int
    max_energy_price: int

    def __getitem__(self, item):
        return self.__getattribute__(item.lower())
