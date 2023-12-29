from dataclasses import dataclass, field
from table import Table

@dataclass
class PowerPlant(Table):
    table_name = "power_plants"
    power_plant_id: int
    type: int
    game_id: bool
    player_id: int
    temperature: int = field(default=0)
