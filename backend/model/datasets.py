from db.table import Table
from dataclasses import dataclass

from model.dataset_data import DatasetData


@dataclass
class Datasets(Table):
    table_name = "datasets"

    dataset_id: int
    dataset_name: str
    dataset_description: str

    @classmethod
    async def ensure_ticks(cls, dataset_id, min_ticks):

        row = await DatasetData.list(dataset_id=dataset_id)

        if len(row) < min_ticks:
            raise Exception("Dataset does not have enough ticks")

        return dataset_id
