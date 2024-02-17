from dataclasses import dataclass, field
from db.table import Table
from datetime import datetime


@dataclass
class Game(Table):
    table_name = "games"
    game_id: int
    game_name: str
    is_contest: bool
    bots: str
    dataset_id: int
    start_time: datetime
    total_ticks: int
    tick_time: int  # TODO??
    current_tick: int = field(default=0)
    is_finished: bool = field(default=False)
