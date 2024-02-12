from dataclasses import dataclass, field
from db.table import Table
from model.dataset_data import DatasetData
from model.player import Player
from .power_plant_types import PowerPlantType
from .enum_type import enum_type


PowerPlantField = enum_type(PowerPlantType)


@dataclass
class PowerPlant(Table):
    table_name = "power_plants"
    power_plant_id: int
    type: PowerPlantField
    player_id: int
    price: int
    powered_on: bool = field(default=False)
    temperature: float = field(default=0)

    def has_resources(self, player: Player):
        type = PowerPlantType(self.type)

        if type.is_renewable():
            return True

        return player[type.get_name().lower()] >= 1

    def get_produced_energy(self, dataset_row):
        type = PowerPlantType(self.type)
        return dataset_row[type.get_name().upper()]
