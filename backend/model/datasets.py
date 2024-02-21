from db.table import Table
from dataclasses import dataclass
from fastapi import HTTPException
from model.dataset_data import DatasetData


@dataclass
class Datasets(Table):
    table_name = "datasets"

    dataset_id: int
    dataset_name: str
    dataset_description: str

    @classmethod
    async def validate_ticks(cls, dataset_id, min_ticks):
        rows = await DatasetData.count(dataset_id=dataset_id)

        if rows < min_ticks:
            raise HTTPException(400, "Dataset does not have enough ticks")

        return dataset_id
