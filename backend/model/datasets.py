from db.db import get_my_redis_connection
from redis_om import  Field, JsonModel


class Datasets(JsonModel):
    dataset_name: str = Field(index=True)
    dataset_description: str

    @property
    def dataset_id(self) -> str:
        return self.pk

    class Meta:
        database = get_my_redis_connection()