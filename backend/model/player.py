from model.resource import Resource
from model.power_plant_type import PowerPlantType
from pydantic import BaseModel
from redis_om import EmbeddedJsonModel, Field, JsonModel, get_redis_connection
from redlock.lock import RedLock


class PlayerResources(EmbeddedJsonModel):
    coal: int = Field(index=False, default=0)
    uranium: int = Field(index=False, default=0)
    biomass: int = Field(index=False, default=0)
    gas: int = Field(index=False, default=0)
    oil: int = Field(index=False, default=0)

    def __getitem__(self, key):
        if isinstance(key, Resource):
            return self.__getattribute__(key.value)
        return self.__getattribute__(key)
    class Meta:
        database = get_redis_connection(port=6479)


class PlayerPowerPlants(EmbeddedJsonModel):
    coal: int = Field(index=False, default=0)
    uranium: int = Field(index=False, default=0)
    biomass: int = Field(index=False, default=0)
    gas: int = Field(index=False, default=0)
    oil: int = Field(index=False, default=0)
    geothermal: int = Field(index=False, default=0)
    wind: int = Field(index=False, default=0)
    solar: int = Field(index=False, default=0)
    hydro: int = Field(index=False, default=0)

    def __getitem__(self, key):
        if isinstance(key, PowerPlantType):
            return self.__getattribute__(key.value)
        return self.__getattribute__(key)
    class Meta:
        database = get_redis_connection(port=6479)


class Networth(BaseModel):
    total: int = Field(index=False, default=0)
    money: int = Field(index=False, default=0)
    resources: PlayerResources
    resources_value: PlayerResources
    power_plants_owned: PlayerPowerPlants
    power_plants_value: PlayerPowerPlants


class Player(JsonModel):
    player_name: str
    game_id: str = Field(index=True)
    team_id: str = Field(index=True)
    is_active: bool = Field(default=True)
    is_bot: bool = Field(default=False)

    energy_price: int = Field(default=1e9)

    money: int = Field(default=0)
    energy: int = Field(default=0)

    resources: PlayerResources = Field(default_factory=PlayerResources)

    power_plants_owned: PlayerPowerPlants = Field(default_factory=PlayerPowerPlants)
    power_plants_powered: PlayerPowerPlants = Field(default_factory=PlayerPowerPlants)

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