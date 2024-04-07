from datetime import datetime
from redis_om import  Field, HashModel, get_redis_connection


class DatasetData(HashModel):
    dataset_id: str = Field(index=True)
    date: datetime
    tick: int = Field(index=True)

    coal: int
    uranium: int
    biomass: int
    gas: int
    oil: int
    geothermal: int
    wind: int
    solar: int
    hydro: int
    
    coal_price: int
    uranium_price: int
    biomass_price: int
    gas_price: int
    oil_price: int
    energy_demand: int
    max_energy_price: int

    @property
    def dataset_data_id(self) -> str:
        return self.pk

    def __getitem__(self, item):
        return self.__getattribute__(item.lower())

    @classmethod
    async def list_by_game_id_where_tick(cls, dataset_id, game_id, min_tick, max_tick):
        raise Exception()
    
    class Meta:
        database = get_redis_connection(port=6479)