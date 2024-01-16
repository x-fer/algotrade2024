from dataclasses import dataclass, field
from enum import Enum

from fastapi import HTTPException
from db.db import database
from db.table import Table
from db.model.player import Player
from config import config


class PowerPlantType(Enum):
    COAL = 1
    URANIUM = 2
    BIOMASS = 3
    GAS = 4
    OIL = 5
    GEOTHERMAL = 6
    WIND = 7
    SOLAR = 8
    HYDRO = 9

    def get_base_price(self):
        return config["power_plant_base_prices"][self.name.lower()]

    async def get_plant_price(self, player_id: int):
        return self.get_base_price() + (5000 * await PowerPlant.count(player_id=player_id, type=self.value))


for power_plant_type in PowerPlantType:
    assert power_plant_type.name.lower(
    ) in config["power_plant_base_prices"], f"Missing price for {power_plant_type.name}"


@dataclass
class PowerPlant(Table):
    table_name = "power_plants"
    power_plant_id: int
    type: int
    player_id: int
    price: int
    powered_on: bool = field(default=False)
    temperature: int = field(default=0)
