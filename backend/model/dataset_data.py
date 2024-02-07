from db.table import Table
from dataclasses import dataclass


@dataclass
class DatasetData(Table):
    table_name = "dataset_data"

    dataset_data_id: int
    dataset_id: int
    date: str
    temp: float
    rain: float
    wind: float
    uv: float
    energy: float
    river: float
