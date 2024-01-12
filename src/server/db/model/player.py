from dataclasses import dataclass, field
from db.table import Table


@dataclass
class Player(Table):
    table_name = "players"
    player_id: int
    player_name: str
    game_id: int
    team_id: int
    is_active: bool = field(default=True)
    is_bot: bool = field(default=False)
    
    money: int = field(default=0)
    energy: int = field(default=0)
    coal: int = field(default=0)
    uranium: int = field(default=0)
    biomass: int = field(default=0)
    gas: int = field(default=0)
    oil: int = field(default=0)
