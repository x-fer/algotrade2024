from dataclasses import asdict
from datetime import datetime, timedelta
from typing import Dict, List

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from model import Game
from model.dataset_data import DatasetData
from routers.users.dependencies import game_dep, start_end_tick_dep


class GameData(BaseModel):
    game_id: int
    game_name: str
    is_contest: bool = Field(..., description="True if game is either a contest or a competition round. False if it is a normal game")
    start_time: datetime = Field(..., description="Exact time at which this game starts")
    total_ticks: int
    tick_time: int = Field(..., description="Time in milliseconds between ticks")
    current_tick: int = Field(..., description="Current tick in this game")
    is_finished: bool = Field(..., description="True if the game is finished")


class GameTimeData(GameData):
    current_time: datetime
    next_tick_time: datetime = Field(..., description="Exact time when next tick begins")


class DatasetListResponseItem(BaseModel):
    tick: int = Field(..., description="In game tick when this data was used")
    date: datetime = Field(..., description="Time when this measurment took place in the real world. Year is not accurate")
    coal: int
    uranium: int
    biomass: int
    gas: int
    oil: int
    geothermal: int
    wind: int
    solar: int
    hydro: int
    energy_demand: int = Field(..., description="Volume of energy that was demanded in the tick")
    max_energy_price: int = Field(..., description="Maximum price at which energy was tried to be bought in the tick")

    def __post_init__(self):
        self.date.year = 2012


class MarketPricesResponse(BaseModel):
    tick: int = Field(..., description="tick of this data")
    low: int = Field(..., description="lowest price of all trades (in this tick)")
    high: int = Field(..., description="highest price of all trades")
    open: int = Field(..., description="price of the first trade")
    close: int = Field(..., description="price of the last trade")
    market: int = Field(..., description="average price of all trades weighted by their volume")
    volume: int = Field(..., description="total volume traded")


class EnergyPrice(BaseModel):
    price: int