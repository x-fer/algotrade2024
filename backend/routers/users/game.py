from dataclasses import asdict
from datetime import datetime, timedelta
from typing import Dict, List

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from model import Game
from model.dataset_data import DatasetData
from routers.users.dependencies import game_dep, start_end_tick_dep
from routers.users.model import DatasetListResponseItem, GameData, GameTimeData


router = APIRouter()


@router.get("/game/time")
async def server_time() -> datetime:
    return datetime.now()


@router.get(
    "/game/list",
    summary="List all available games.",
    response_description="List of games",
)
async def game_list() -> List[GameData]:
    games = await Game.find().all()
    return games


@router.get(
    "/game/{game_id}",
    summary="Current time on server and time of the next tick in this game.",
)
async def get_game(game: Game = Depends(game_dep)) -> GameTimeData:
    next_tick_time = game.start_time + timedelta(
        milliseconds=game.current_tick * game.tick_time
    )
    return GameTimeData(
        **asdict(game),
        current_time=datetime.now(),
        next_tick_time=next_tick_time
    )


@router.get(
    "/game/{game_id}/dataset",
    summary="Get power plant production rates for all resources and energy demand for previous ticks.",
)
async def dataset_list(
    start_end=Depends(start_end_tick_dep), game: Game = Depends(game_dep)
) -> Dict[int, DatasetListResponseItem]:
    start_tick, end_tick = start_end

    all_entries = DatasetData.find(
        (DatasetData.dataset_id == game.dataset_id) &
        (DatasetData.tick >= start_tick) &
        (DatasetData.tick <= end_tick)
    ).all()
    all_entries_dict = {}
    for entry in all_entries:
        all_entries_dict[entry.tick] = entry
    return all_entries_dict
