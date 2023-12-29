from dataclasses import dataclass
from table import Table

@dataclass
class Game(Table):
    table_name = "games"
    game_id: int
    game_name: str
    contest: bool
    queue_id: str
    start_time: str
    tick_time: int
    
    def __repr__(self):
        return f"Game({self.game_id} {self.game_name} {self.contest} {self.start_time} {self.tick_time})"