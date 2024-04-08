from dataclasses import asdict
from datetime import datetime, timedelta
from typing import Dict, List

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from model import Game
from model.dataset_data import DatasetData
from routers.users.dependencies import game_dep, start_end_tick_dep

router = APIRouter()


class GameData(BaseModel):
    game_id: int
    game_name: str
    is_contest: bool = Field(
        ...,
        description="True if game is either a contest or a competition round. False if it is a normal game",
    )
    start_time: datetime = Field(
        ..., description="Exact time at which this game starts"
    )
    total_ticks: int
    tick_time: int = Field(..., description="Time in milliseconds between ticks")
    current_tick: int = Field(..., description="Current tick in this game")
    is_finished: bool = Field(..., description="True if the game is finished")


@router.get("/game/time")
def server_time() -> datetime:
    return datetime.now()


@router.get(
    "/game/list",
    summary="List all available games.",
    response_description="List of games",
)
def game_list() -> List[GameData]:
    return Game.find().all()


class GameTimeData(GameData):
    current_time: datetime
    next_tick_time: datetime = Field(
        ..., description="Exact time when next tick processing begins"
    )


@router.get(
    "/game/{game_id}",
    summary="Current time on server and time of the next tick in this game.",
)
def get_game(game: Game = Depends(game_dep)) -> GameTimeData:
    next_tick_time = game.start_time + timedelta(
        milliseconds=game.current_tick * game.tick_time
    )
    return GameTimeData(
        **asdict(game), current_time=datetime.now(), next_tick_time=next_tick_time
    )


class DatasetListResponseItem(BaseModel):
    tick: int = Field(..., description="In game tick when this data was used")
    date: datetime = Field(
        ...,
        description="Time when this measurment took place in the real world. Year is not accurate",
    )
    coal: int
    uranium: int
    biomass: int
    gas: int
    oil: int
    geothermal: int
    wind: int
    solar: int
    hydro: int
    energy_demand: int = Field(
        ..., description="Volume of energy that was demanded in the tick"
    )
    max_energy_price: int = Field(
        ...,
        description="Maximum price at which energy was tried to be bought in the tick",
    )

    def __post_init__(self):
        self.date.year = 2012


@router.get(
    "/game/{game_id}/dataset",
    summary="Get power plant production rates for all resources and energy demand for previous ticks.",
)
def dataset_list(
    start_end=Depends(start_end_tick_dep), game: Game = Depends(game_dep)
) -> Dict[int, DatasetListResponseItem]:
    start_tick, end_tick = start_end

    all_entries = DatasetData.find(
        (DatasetData.dataset_id == game.dataset_id)
        & (DatasetData.tick >= start_tick)
        & (DatasetData.tick <= end_tick)
    ).all()
    all_entries_dict = {}
    for entry in all_entries:
        all_entries_dict[entry.tick] = entry
    return all_entries_dict
