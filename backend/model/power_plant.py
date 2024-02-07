from dataclasses import dataclass, field
from db.table import Table
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
