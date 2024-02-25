from dataclasses import dataclass
from typing import List
from fastapi import APIRouter, Depends, HTTPException
import pandas as pd
from pydantic import BaseModel
from model import Order, OrderSide, OrderType, OrderStatus, Resource
from model.game import Game
from model.market import Market
from model.player import Player
from .dependencies import game, player, check_game_active

# GAME PATHS


router = APIRouter(dependencies=[Depends(game), Depends(check_game_active)])


class OrderResponse(BaseModel):
    order_id: int
    game_id: int
    player_id: int
    price: int
    size: int
    tick: int
    timestamp: pd.Timestamp
    order_side: OrderSide
    order_type: OrderType
    order_status: OrderStatus
    filled_size: int
    filled_money: int
    filled_price: int
    expiration_tick: int
    resource: Resource


@router.get("/game/{game_id}/market/order/list")
async def order_list(game: Game) -> List[OrderResponse]:
    return await Order.list(
        game_id=game.game_id,
        order_status=OrderStatus.ACTIVE.value
    )


@router.get("/game/{game_id}/market/order/prices/from/{start_tick}/to/{end_tick}")
async def orded_list(game: Game, start_tick: int = 0, end_tick: int = 0) -> List[OrderResponse]:
    if start_tick < 0 or end_tick < 0:
        raise HTTPException(
            status_code=400, detail="Tick must be greater than 0")

    if end_tick < start_tick:
        raise HTTPException(
            status_code=400, detail="End tick must be greater than start tick")

    # TODO: add new method
    all_market = await Market.list(
        game_id=Game.game_id,
    )

    return list(filter(lambda x: start_tick <= x.tick <= end_tick, all_market))


class EnergyPrice(BaseModel):
    price: int


class EnergyPriceResponse(BaseModel):
    success: bool


@router.post("/game/{game_id}/player/{player_id}/market/energy/set_price")
async def energy_set_price_player(price: EnergyPrice, game: Game, player: int = Depends(player)) -> EnergyPriceResponse:
    if price <= 0:
        raise HTTPException(
            status_code=400, detail="Price must be greater than 0")

    await Player.update(
        player_id=player.player_id,
        energy_price=price.price
    )

    return {"success": True}


class UserOrder(BaseModel):
    resource: Resource
    price: int
    size: int
    expiration_tick: int
    side: OrderSide
    type: OrderType


class OrderCreateResponse(BaseModel):
    success: bool


@router.post("/game/{game_id}/player/{player_id}/market/order/create")
async def order_create_player(order: UserOrder, game: int = Depends(game), player: int = Depends(player)) -> OrderCreateResponse:
    if order.type == OrderType.ENERGY:
        raise Exception(
            "Use /game/{game_id}/player/{player_id}/market/energy/set_price to set energy price")

    await Order.create(
        game_id=game.game_id,
        player_id=player.player_id,
        order_type=order.type,
        order_side=order.side,
        order_status=OrderStatus.PENDING,
        timestamp=pd.Timestamp.now(),
        price=order.price,
        size=order.size,
        tick=(await Game.get(game_id=game.game_id)).current_tick,
        expiration_tick=order.expiration_tick,
        resource=order.resource.value
    )

    return {"success": True}


@router.post("/game/{game_id}/player/{player_id}/market/order/list")
async def order_list_player(game: Game, player: int = Depends(player)) -> List[OrderResponse]:
    return await Order.list(
        game_id=game.game_id,
        player_id=player.player_id,
        order_status=OrderStatus.ACTIVE.value
    )


class OrderCancel(BaseModel):
    ids: List[int]


class OrderCancelResponse(BaseModel):
    success: bool


@router.post("/game/{game_id}/player/{player_id}/market/order/cancel")
async def order_cancel_player(body: OrderCancel, game: Game, player: int = Depends(player)) -> OrderCancelResponse:
    for order_id in body.ids:
        await Order.update(
            order_id=order_id,
            order_status=OrderStatus.CANCELED.value
        )

    return {"success": True}
