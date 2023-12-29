from dataclasses import dataclass
from table import Table
from datetime import datetime

@dataclass
class Game(Table):
    table_name = "games"
    game_id: int
    game_name: str
    contest: bool
    queue_id: str
    start_time: datetime
    tick_time: int