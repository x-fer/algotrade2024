from dataclasses import dataclass, field
from datetime import datetime

from fastapi import HTTPException

_game_id = 0
game_db = {}


@dataclass
class Game:
    table_name = "games"
    game_id: int
    game_name: str
    is_contest: bool
    dataset_id: int
    start_time: datetime
    total_ticks: int
    tick_time: int
    current_tick: int = field(default=0)
    is_finished: bool = field(default=False)

    @classmethod
    async def create(cls, **kwargs):
        global game_db, _game_id

        _game_id += 1

        game = Game(game_id=_game_id, **kwargs)
        game_db[_game_id] = game

        return _game_id

    @classmethod
    async def get(cls, **kwargs):
        global game_db, _game_id

        out = [game for game in game_db.values() if all(
            getattr(game, k) == v for k, v in kwargs.items())]

        if len(out) == 0:
            raise HTTPException(400, "Game does not exist")

        return Game(**out[0].__dict__)

    @classmethod
    async def list(cls):
        global game_db, _game_id

        return list(game_db.values())

    @classmethod
    async def update(cls, game_id, **kwargs):
        global game_db, _game_id

        game = game_db[game_id]
        for k, v in kwargs.items():
            setattr(game, k, v)

        return game_id
