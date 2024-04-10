from enum import Enum

from pydantic import BaseModel
from db.db import get_my_redis_connection
from redis_om import EmbeddedJsonModel, Field


class EnumGetterSettr:
    def __getitem__(self, key):
        if isinstance(key, Enum):
            return self.__getattribute__(key.value)
        return self.__getattribute__(key)

    def __setitem__(self, key, value):
        if isinstance(key, Enum):
            return self.__setattr__(key.value, value)
        self.__setattr__(key, value)


class ResourcesModel(EmbeddedJsonModel, EnumGetterSettr):
    coal: int = Field(index=False, default=0)
    uranium: int = Field(index=False, default=0)
    biomass: int = Field(index=False, default=0)
    gas: int = Field(index=False, default=0)
    oil: int = Field(index=False, default=0)

    class Meta:
        database = get_my_redis_connection()


class PowerPlantsModel(EmbeddedJsonModel, EnumGetterSettr):
    coal: int = Field(index=False, default=0)
    uranium: int = Field(index=False, default=0)
    biomass: int = Field(index=False, default=0)
    gas: int = Field(index=False, default=0)
    oil: int = Field(index=False, default=0)
    geothermal: int = Field(index=False, default=0)
    wind: int = Field(index=False, default=0)
    solar: int = Field(index=False, default=0)
    hydro: int = Field(index=False, default=0)

    class Meta:
        database = get_my_redis_connection()



class ResourcesApiModel(BaseModel):
    coal: int
    uranium: int
    biomass: int
    gas: int
    oil: int


class PowerPlantsApiModel(BaseModel):
    coal: int
    uranium: int
    biomass: int
    gas: int
    oil: int
    geothermal: int
    wind: int
    solar: int
    hydro: int
