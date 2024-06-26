from datetime import datetime
from db.db import get_my_redis_connection
from redis_om import Field, JsonModel

from model.power_plant_model import PowerPlantsModel, ResourcesModel


class DatasetData(JsonModel):
    dataset_id: str = Field(index=True)
    date: datetime
    tick: int = Field(index=True)

    energy_demand: int
    max_energy_price: int

    resource_prices: ResourcesModel = Field(default_factory=ResourcesModel)
    power_plants_output: PowerPlantsModel = Field(
        default_factory=PowerPlantsModel)

    @property
    def dataset_data_id(self) -> str:
        return self.pk

    class Meta:
        database = get_my_redis_connection()
