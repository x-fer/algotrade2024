from pprint import pprint
from fastapi import HTTPException
from db.db import get_my_redis_connection
from redis_om import Field, JsonModel

from model.dataset_data import DatasetData


class Datasets(JsonModel):
    dataset_name: str = Field(index=True)
    dataset_description: str

    dataset_id: str = Field(index=True, default=None)

    def __init__(self, **data):
        super().__init__(**data)
        self.dataset_id = self.pk

    @staticmethod
    def validate_ticks(dataset_id: str, total_ticks: int):
        if Datasets.find(Datasets.pk == dataset_id).count() == 0:
            raise HTTPException(400, "Dataset not found")
        if DatasetData.find(DatasetData.dataset_id == dataset_id).count() < total_ticks:
            raise HTTPException(400, "Not enough ticks in dataset")

    class Meta:
        database = get_my_redis_connection()
