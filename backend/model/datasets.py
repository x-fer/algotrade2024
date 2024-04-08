from dataclasses import dataclass
from fastapi import HTTPException
from model.dataset_data import DatasetData

datasets_id = 0
datasets_db = {}


@dataclass
class Datasets:
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

    @classmethod
    async def get(cls, **kwargs):
        global datasets_db, datasets_id

        out = [dataset for dataset in datasets_db.values() if all(
            getattr(dataset, k) == v for k, v in kwargs.items())]

        if len(out) == 0:
            raise HTTPException(400, "Dataset does not exist")

        return Datasets(**out[0].__dict__)

    @classmethod
    async def list(cls):
        global datasets_db, datasets_id

        return list(datasets_db.values())

    @classmethod
    async def validate_string(cls, name):
        global datasets_db, datasets_id

        if not name:
            raise HTTPException(400, "Dataset name cannot be empty")

        if name not in [dataset.dataset_name for dataset in datasets_db.values()]:
            raise HTTPException(400, "Dataset name does not exist")

        return name

    @classmethod
    async def create(cls, **kwargs):
        global datasets_db, datasets_id

        datasets_id += 1

        dataset = Datasets(dataset_id=datasets_id, **kwargs)
        datasets_db[datasets_id] = dataset

        return datasets_id
