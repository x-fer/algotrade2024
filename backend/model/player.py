from db.db import get_my_redis_connection
from model.dataset_data import DatasetData
from model.game import Game
from model.order import Order
from model.power_plant_model import PowerPlantsModel, ResourcesModel
from pydantic import BaseModel
import pydantic
from redis_om import Field, JsonModel
from redlock.lock import RedLock

from model.power_plant_type import PowerPlantType
from model.resource import Resource


class Networth(BaseModel):
    total: int = pydantic.Field(..., description="Total players networth. This is your score in competition rounds!")
    money: int
    resources: ResourcesModel = Field(..., description="Resources owned by the player")
    resources_value: ResourcesModel = Field(..., description="Players networth based on resources prices on the market")
    power_plants_owned: PowerPlantsModel = Field(..., description="Power plants owned by the player")
    power_plants_value: PowerPlantsModel = Field(..., description="Players networth based only on power plants sell prices")


class Player(JsonModel):
    player_name: str
    game_id: str = Field(index=True)
    team_id: str = Field(index=True)
    is_active: int = Field(default=int(True), index=True)
    is_bot: int = Field(default=int(False), index=True)

    energy_price: int = Field(default=1e9)

    money: int = Field(default=0)
    energy: int = Field(default=0)

    resources: ResourcesModel = Field(default_factory=ResourcesModel)

    power_plants_owned: PowerPlantsModel = Field(default_factory=PowerPlantsModel)
    power_plants_powered: PowerPlantsModel = Field(default_factory=PowerPlantsModel)

    player_id: str = Field(default=None)

    def __init__(self, **data):
        super().__init__(**data)
        self.player_id=self.pk

    def lock(self, *args):
        return RedLock(self.pk, *args)

    def cancel_orders(self, pipe=None) -> int:
        """Returns number of canceled orders"""
        return Order.delete_many(Order.find(Order.player_id == self.player_id).all(), pipe)

    def get_networth(self, game: Game, dataset_data: DatasetData = None):
        # TODO: nije pod lockom jer bi kocilo tick, a ovo stalno uzimaju igraci
        if dataset_data is None:
            dataset_data = DatasetData.find(
                DatasetData.tick==game.current_tick,
                DatasetData.dataset_id==game.dataset_id
            ).first()
        total = self.money
        resources_value = ResourcesModel()
        for resource in Resource:
            resource_value = dataset_data.resource_prices[resource] * self.resources[resource]
            resources_value[resource] = resource_value
            total += resource_value
        power_plants_value = PowerPlantsModel()
        for type in PowerPlantType:
            for i in range(1, self.power_plants_owned[type] + 1):
                power_plants_value[type] += PowerPlantType.get_sell_price()
            total += power_plants_value[type]

        return Networth(
            total = total,
            money = self.money,
            resources = self.resources,
            resources_value = resources_value,
            power_plants_owned = self.power_plants_owned,
            power_plants_value = power_plants_value,
        )

    class Meta:
        database = get_my_redis_connection()
