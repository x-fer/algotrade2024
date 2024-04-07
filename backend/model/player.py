from model.power_plant_model import PowerPlantsModel, ResourcesModel
from model.resource import Resource
from model.power_plant_type import PowerPlantType
from pydantic import BaseModel
from redis_om import EmbeddedJsonModel, Field, JsonModel, get_redis_connection
from redlock.lock import RedLock


class Networth(BaseModel):
    total: int = Field(index=False, default=0)
    money: int = Field(index=False, default=0)
    resources: ResourcesModel
    resources_value: ResourcesModel
    power_plants_owned: PowerPlantsModel
    power_plants_value: PowerPlantsModel


class Player(JsonModel):
    player_name: str
    game_id: str = Field(index=True)
    team_id: str = Field(index=True)
    is_active: bool = Field(default=True)
    is_bot: bool = Field(default=False)

    energy_price: int = Field(default=1e9)

    money: int = Field(default=0)
    energy: int = Field(default=0)

    resources: ResourcesModel = Field(default_factory=ResourcesModel)

    power_plants_owned: PowerPlantsModel = Field(default_factory=PowerPlantsModel)
    power_plants_powered: PowerPlantsModel = Field(default_factory=PowerPlantsModel)

    @property
    def player_id(self) -> str:
        return self.pk

    def __setitem__(self, key, value):
        if isinstance(key, Resource):
            return self.__setattr__(key.name, value)
        self.__setattr__(key, value)
    
    def lock(self, *args):
        return RedLock(self.pk, *args)

    async def get_networth(self, game):
        raise Exception("Not implemented")

    class Meta:
        database = get_redis_connection(port=6479)