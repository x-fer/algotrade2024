from db.table import Table
from dataclasses import dataclass


@dataclass
class Datasets(Table):
    table_name = "datasets"

    dataset_id: int
    dataset_name: str
    dataset_description: str

    @classmethod
    async def exists(cls, dataset_id):
        try:
            Datasets.get(dataset_id)
            return True
        except Exception:
            return False

    @classmethod
    async def validate_string(cls, dataset_string):
        if not Datasets.exists(dataset_string):
            raise Exception("Dataset does not exist")

        return dataset_string

    @classmethod
    async def ensure_ticks(cls, dataset_string, min_ticks):
        Datasets.validate_string(dataset_string)

        if Datasets.count(dataset_string) < min_ticks:
            raise Exception("Dataset does not have enough ticks")

        return dataset_string
