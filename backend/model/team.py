from dataclasses import dataclass

from fastapi import HTTPException

team_id = 0
team_db = {}


@dataclass
class Team:
    table_name = "teams"
    team_id: int
    team_name: str
    team_secret: str

    @classmethod
    async def create(cls, **kwargs):
        global team_db, team_id

        team_id += 1

        team = Team(team_id=team_id, **kwargs)
        team_db[team_id] = team

        return team_id

    @classmethod
    async def get(cls, **kwargs):
        global team_db, team_id

        out = [team for team in team_db.values() if all(
            getattr(team, k) == v for k, v in kwargs.items())]

        if len(out) == 0:
            raise HTTPException(400, "Team does not exist")

        return Team(**out[0].__dict__)

    @classmethod
    async def list(cls):
        global team_db, team_id

        return list(team_db.values())

    @classmethod
    async def delete(cls, _team_id):
        global team_db, team_id

        del team_db[_team_id]
        return _team_id
