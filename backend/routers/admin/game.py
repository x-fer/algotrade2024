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
from db import limiter
import asyncio
from logger import logger


router = APIRouter()


class CreateGameParams(BaseModel):
    game_name: str
    contest: bool
    dataset_id: str
    start_time: datetime
    total_ticks: int
    tick_time: int


@router.post("/game/create")
@limiter.exempt
def game_create(params: CreateGameParams) -> SuccessfulResponse:
    Datasets.validate_ticks(params.dataset_id, params.total_ticks)

    if params.start_time < datetime.now():
        raise HTTPException(400, "Start time must be in the future")

    Game(
        game_name=params.game_name,
        is_contest=params.contest,
        dataset_id=params.dataset_id,
        start_time=params.start_time,
        total_ticks=params.total_ticks,
        tick_time=params.tick_time,
        is_finished=False,
        current_tick=0
    ).save()

    return SuccessfulResponse()


@router.get("/game/list")
@limiter.exempt
def game_list() -> List[Game]:
    return Game.find().all()


@router.get("/game/{game_id}/player/list")
@limiter.exempt
def player_list(game_id: str) -> List[Player]:
    return Player.find(Player.game_id == game_id).all()


@router.post("/game/{game_id}/delete")
@limiter.exempt
def game_delete(game_id: str) -> SuccessfulResponse:
    try:
        g = Game.get(game_id)
        g.is_finished=True
        g.save()
        return SuccessfulResponse()
    except Exception:
        raise HTTPException(400, "Invalid game id")


@dataclass
class NetworthData:
    team_id: str
    team_name: str
    player_id: str
    player_name: str
    networth: int


@router.get("/game/{game_id}/networth")
@limiter.exempt
def game_networth(game_id: str) -> List[NetworthData]:
    # game = await Game.get(game_id=game_id)
    try:
        game = Game.get(game_id)
    except Exception:
        raise HTTPException(400, "Invalid game id")

    if game.current_tick == 0:
        raise HTTPException(
            400, "Game has not started yet or first tick has not been processed")

    # players = await Player.list(game_id=game_id)
    players = Player.find(Player.game_id == game_id).all()

    team_networths = []

    for player in players:
        team_networths.append({
            "team_id": player.team_id,
            # "team_name": (await Team.get(team_id=player.team_id)).team_name,
            "team_name": Team.find(Team.team_id == player.team_id).first().team_name,
            "player_id": player.player_id,
            "player_name": player.player_name,
            "networth": (player.get_networth(game)).total
        })

    return team_networths


class WebSocketWrapper:
    def __init__(self, websocket: WebSocket):
        self.websocket = websocket
    async def __aenter__(self):
        await self.websocket.accept()
    async def __aexit__(self, *args, **kwargs):
        await self.websocket.close()



@router.websocket("/game/{game_id}/dashboard/graphs")
@limiter.exempt
async def dashboard_graphs(websocket: WebSocket, game_id: str):
    async with WebSocketWrapper(websocket):
        try:
            game = Game.get(game_id)
        except Exception:
            raise HTTPException(400, "Invalid game id")

        try:
            while True:
                current_tick = game.current_tick

                if current_tick == 0:
                    await asyncio.sleep(game.tick_time / 1000)
                    continue

                # dataset = (await DatasetData.list_by_game_id_where_tick(
                #     game.dataset_id, game.game_id, current_tick - 1, current_tick - 1))[0]
                dataset = DatasetData.find(
                    (DatasetData.dataset_id == game.dataset_id) &
                    (DatasetData.tick == current_tick - 1)
                ).first()

                dataset = dataset.dict()

                # all_prices = await Market.list_by_game_id_where_tick(
                #     game_id=game.game_id,
                #     min_tick=current_tick - 1,
                #     max_tick=current_tick - 1,
                # )

                all_prices = Market.find(
                    (Market.game_id == game.game_id) &
                    (Market.tick == current_tick - 1)
                ).all()

                all_prices = [price.dict() for price in all_prices]

                await websocket.send_json(json.dumps({
                    **dataset,
                    "prices": all_prices
                }, default=str))

                await asyncio.sleep(game.tick_time / 1000)
        except ConnectionClosedOK:
            pass
        except HTTPException as e:
            raise e
        except Exception:
            logger.warning("Error in websocets")
            return


@router.websocket("/game/{game_id}/dashboard/players")
@limiter.exempt
async def dashboard_players(websocket: WebSocket, game_id: str):
    async with WebSocketWrapper(websocket):
        try:
            game = Game.get(game_id)
        except Exception:
            raise HTTPException(400, "Invalid game id")

        try:
            while True:
                current_tick = game.current_tick

                if current_tick == 0:
                    await asyncio.sleep(game.tick_time / 1000)
                    continue

                players = Player.find(Player.game_id == game_id).all()

                networths = {
                    player.player_id: (player.get_networth(game)).total for player in players}

                players = [
                    {
                        **player.dict(),
                        "networth": networths[player.player_id]
                    } for player in players
                ]

                await websocket.send_json(json.dumps({
                    "current_tick": current_tick,
                    "players": players,
                }, default=str))

                await asyncio.sleep(game.tick_time / 1000)
        except ConnectionClosedOK:
            pass
        except Exception:
            logger.warning("Error in websocets")
            return


@router.websocket("/game/{game_id}/dashboard/orderbooks")
@limiter.exempt
async def dashboard_orderbooks(websocket: WebSocket, game_id: str):
    async with WebSocketWrapper(websocket):
        try:
            game = Game.get(game_id)
        except Exception:
            raise HTTPException(400, "Invalid game id")

        try:
            while True:
                # orders = await Order.list(game_id=game_id, order_status=OrderStatus.ACTIVE)
                orders = Order.find(
                    (Order.game_id == game.game_id) &
                    (Order.order_status == OrderStatus.ACTIVE.value)
                ).all()

                # orders = [dataclasses.asdict(order) for order in orders]
                orders = [order.dict() for order in orders]

                orders_by_resource = defaultdict(
                    lambda: {str(OrderSide.BUY): [], str(OrderSide.SELL): []})

                for order in orders:
                    orders_by_resource[str(order["resource"])
                                    ][str(order["order_side"])].append(order)

                await websocket.send_json(json.dumps(orders_by_resource, default=str))

                await asyncio.sleep(game.tick_time / 1000)
        except ConnectionClosedOK:
            pass
        except Exception:
            logger.warning("Error in websocets")
            return
