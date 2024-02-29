from collections import defaultdict
from pprint import pprint
from typing import Dict, List
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from dataclasses import asdict
from model import Game
from model.dataset_data import DatasetData
from routers.users.dependencies import game_dep, start_end_tick_dep
from datetime import datetime
import pandas as pd


router = APIRouter()


class GameData(BaseModel):
    game_id: int
    game_name: str
    is_contest: bool
    start_time: datetime
    total_ticks: int
    tick_time: int
    current_tick: int
    is_finished: bool


@router.get("/game/list")
async def game_list() -> List[GameData]:
    games = await Game.list()
    return games


class GameTimeData(GameData):
    current_time: datetime


@router.get("/game/{game_id}")
async def get_game(game_id: int) -> GameTimeData:
    game = await Game.get(game_id=game_id)
    return GameTimeData(**asdict(game), current_time=pd.Timestamp.now())


class DatasetListResponseItem(BaseModel):
    tick: int
    date: str
    coal: int
    uranium: int
    biomass: int
    gas: int
    oil: int
    geothermal: int
    wind: int
    solar: int
    hydro: int
    energy_demand: int
    max_energy_price: int


@router.get("/game/{game_id}/dataset")
async def dataset_list(start_end=Depends(start_end_tick_dep),
                       game: Game = Depends(game_dep)) -> Dict[int, DatasetListResponseItem]:
    start_tick, end_tick = start_end

    all_entries = await DatasetData.list_by_game_id_where_tick(
        dataset_id=game.dataset_id,
        game_id=game.game_id,
        min_tick=start_tick,
        max_tick=end_tick,
    )
    all_entries_dict = {}
    for entry in all_entries:
        entry.date = str(entry.date)
        all_entries_dict[entry.tick] = entry

    return all_entries_dict
