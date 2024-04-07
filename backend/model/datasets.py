from redis_om import  Field, JsonModel, get_redis_connection


class Datasets(JsonModel):
    dataset_name: str = Field(index=True)
    dataset_description: str

    @property
    def dataset_id(self) -> str:
        return self.pk

    class Meta:
        database = get_redis_connection(port=6479)