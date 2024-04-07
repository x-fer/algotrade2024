from model.resource import Resource
from model.power_plant_type import PowerPlantType
from pydantic import BaseModel
from redis_om import EmbeddedJsonModel, Field, JsonModel, get_redis_connection
from redlock.lock import RedLock


class ResourcesModel(EmbeddedJsonModel):
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


class PowerPlantsModel(EmbeddedJsonModel):
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