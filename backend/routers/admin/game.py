from collections import defaultdict
from dataclasses import dataclass
import dataclasses
from datetime import datetime
import json
from fastapi import APIRouter, HTTPException, WebSocket
from websockets.exceptions import ConnectionClosedOK
from model import Game, Datasets, Player, DatasetData, Market, Order, OrderStatus, OrderSide
from game.bots import Bots
from pydantic import BaseModel
from datetime import datetime
from typing import List
from model.team import Team
from routers.model import SuccessfulResponse
from db import limiter, database
import asyncio


router = APIRouter()


class CreateGameParams(BaseModel):
    game_name: str
    contest: bool
    dataset_id: int
    start_time: datetime
    total_ticks: int
    tick_time: int


@router.post("/game/create")
@limiter.exempt
async def game_create(params: CreateGameParams) -> SuccessfulResponse:
    await Datasets.validate_ticks(params.dataset_id, params.total_ticks)

    if params.start_time < datetime.now():
        raise HTTPException(400, "Start time must be in the future")

    await Game.create(
        game_name=params.game_name,
        is_contest=params.contest,
        dataset_id=params.dataset_id,
        start_time=params.start_time,
        total_ticks=params.total_ticks,
        tick_time=params.tick_time,
        is_finished=False,
        current_tick=0
    )
    return SuccessfulResponse()


@router.get("/game/list")
@limiter.exempt
async def game_list() -> List[Game]:
    return await Game.list()


@router.get("/game/{game_id}/player/list")
@limiter.exempt
async def player_list(game_id: int) -> List[Player]:
    return await Player.list(game_id=game_id)


@router.post("/game/{game_id}/delete")
@limiter.exempt
async def game_delete(game_id: int) -> SuccessfulResponse:
    # TODO ne baca exception ako je vec zavrsena
    await Game.update(game_id=game_id, is_finished=True)
    return SuccessfulResponse()


class EditGameParams(BaseModel):
    game_name: str | None
    contest: bool | None
    dataset_id: int | None
    start_time: datetime | None
    total_ticks: int | None
    tick_time: int | None


@router.post("/game/{game_id}/edit")
@limiter.exempt
async def game_edit(game_id: int, params: EditGameParams) -> SuccessfulResponse:
    try:
        Bots.parse_string(params.bots)
    except:
        raise HTTPException(400, "Invalid bots string")
    if params.dataset is not None:
        Datasets.validate_string(params.dataset)

    if params.total_ticks is not None:
        dataset = await Game.get(game_id=game_id)
        dataset = dataset.dataset

        if params.dataset is not None:
            dataset = params.dataset

        await Datasets.validate_ticks(dataset, params.total_ticks)

    if params.start_time is not None and params.start_time < datetime.now():
        raise HTTPException(400, "Start time must be in the future")

    await Game.update(
        game_id=game_id,
        **params.dict(exclude_unset=True)
    )
    return SuccessfulResponse()


@dataclass
class NetworthData:
    team_id: int
    team_name: str
    player_id: int
    player_name: str
    networth: int


@router.get("/game/{game_id}/networth")
@limiter.exempt
async def game_networth(game_id: int) -> List[NetworthData]:
    game = await Game.get(game_id=game_id)

    if game.current_tick == 0:
        raise HTTPException(
            400, "Game has not started yet or first tick has not been processed")

    players = await Player.list(game_id=game_id)

    team_networths = []

    for player in players:
        team_networths.append({
            "team_id": player.team_id,
            "team_name": (await Team.get(team_id=player.team_id)).team_name,
            "player_id": player.player_id,
            "player_name": player.player_name,
            "networth": (await player.get_networth(game))["total"]
        })

    return team_networths


@router.websocket("/game/{game_id}/dashboard/graphs")
@limiter.exempt
async def dashboard(websocket: WebSocket, game_id: int):
    await websocket.accept()

    try:
        while True:
            game = await Game.get(game_id=game_id)

            current_tick = game.current_tick

            if current_tick == 0:
                await asyncio.sleep(game.tick_time / 1000)
                continue

            dataset = (await DatasetData.list_by_game_id_where_tick(
                game.dataset_id, game.game_id, current_tick - 1, current_tick - 1))[0]

            dataset = dataclasses.asdict(dataset)

            all_prices = await Market.list_by_game_id_where_tick(
                game_id=game.game_id,
                min_tick=current_tick - 1,
                max_tick=current_tick - 1,
            )

            all_prices = [dataclasses.asdict(price) for price in all_prices]

            await websocket.send_json(json.dumps({
                **dataset,
                "prices": all_prices
            }, default=str))

            await asyncio.sleep(game.tick_time / 1000)
    except ConnectionClosedOK:
        pass


@router.websocket("/game/{game_id}/dashboard/players")
@limiter.exempt
async def dashboard(websocket: WebSocket, game_id: int):
    await websocket.accept()

    try:
        while True:
            game = await Game.get(game_id=game_id)

            current_tick = game.current_tick

            if current_tick == 0:
                await asyncio.sleep(game.tick_time / 1000)
                continue

            players = await Player.list(game_id=game_id)

            networths = {
                player.player_id: (await player.get_networth(game))["total"] for player in players}

            players = [{**dataclasses.asdict(player),
                        "networth": networths[player.player_id]
                        } for player in players]

            await websocket.send_json(json.dumps({
                "current_tick": current_tick,
                "players": players,
            }, default=str))

            await asyncio.sleep(game.tick_time / 1000)
    except ConnectionClosedOK:
        pass


@router.websocket("/game/{game_id}/dashboard/orderbooks")
@limiter.exempt
async def dashboard(websocket: WebSocket, game_id: int):
    await websocket.accept()

    try:
        while True:
            game = await Game.get(game_id=game_id)

            orders = await Order.list(game_id=game_id, order_status=OrderStatus.ACTIVE)

            orders = [dataclasses.asdict(order) for order in orders]

            orders_by_resource = defaultdict(
                lambda: {str(OrderSide.BUY): [], str(OrderSide.SELL): []})

            for order in orders:
                orders_by_resource[str(order["resource"])
                                   ][str(order["order_side"])].append(order)

            await websocket.send_json(json.dumps(orders_by_resource, default=str))

            await asyncio.sleep(game.tick_time / 1000)
    except ConnectionClosedOK:
        pass
