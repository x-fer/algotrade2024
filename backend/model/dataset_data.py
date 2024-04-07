from datetime import datetime
from redis_om import  Field, JsonModel, get_redis_connection

from model.power_plant_model import PowerPlantsModel, ResourcesModel


class DatasetData(JsonModel):
    dataset_id: str = Field(index=True)
    date: datetime
    tick: int = Field(index=True)

    energy_demand: int
    max_energy_price: int

    resource_prices: ResourcesModel = Field(default_factory=ResourcesModel)
    power_plants_output: PowerPlantsModel = Field(default_factory=PowerPlantsModel)

    @property
    def dataset_data_id(self) -> str:
        return self.pk

    @classmethod
    async def list_by_game_id_where_tick(cls, dataset_id, game_id, min_tick, max_tick):
        raise Exception()
    
    class Meta:
        database = get_redis_connection(port=6479)