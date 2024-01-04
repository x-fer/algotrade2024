from dataclasses import dataclass
from db.table import Table


@dataclass
class Team(Table):
    table_name = "teams"
    team_id: int
    team_name: str
    team_secret: str
