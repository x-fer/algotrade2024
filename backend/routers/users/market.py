from dataclasses import dataclass
from typing import List, Dict
from fastapi import APIRouter, Depends, HTTPException, Query
import pandas as pd
from pydantic import BaseModel
from model import Order, OrderSide, OrderType, OrderStatus, Resource
from model.game import Game
from model.market import Market
from model.player import Player
from .dependencies import game_dep, player_dep, check_game_active_dep

# GAME PATHS


router = APIRouter(dependencies=[Depends(check_game_active_dep)])


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
async def order_list(game: Game = Depends(game_dep)) -> List[OrderResponse]:
    return await Order.list(
        game_id=game.game_id,
        order_status=OrderStatus.ACTIVE.value
    )


class MarketPricesResponse(BaseModel):
    tick: int
    low: int
    high: int
    open: int
    close: int
    market: int


@router.get("/game/{game_id}/market/prices")
async def market_prices(start_tick: int = Query(default=None),
                       end_tick: int = Query(default=None),
                       resource: Resource = Query(default=None),
                       game: Game = Depends(game_dep)) -> Dict[Resource, List[MarketPricesResponse]]:
    if start_tick is None and end_tick is None:
        current_tick = game.current_tick - 1
        start_tick = current_tick
        end_tick = current_tick
    if start_tick is None:
        start_tick = end_tick
    if end_tick is None:
        end_tick = start_tick

    if start_tick < 0 or end_tick < 0:
        raise HTTPException(
            status_code=400, detail="Tick must be greater than 0")

    if end_tick < start_tick:
        raise HTTPException(
            status_code=400, detail="End tick must be greater than start tick")

    all_prices = await Market.list_by_game_id_where_tick(
        game_id=game.game_id,
        min_tick=start_tick,
        max_tick=end_tick,
        resource=resource,
    )
    all_prices_dict = dict()
    for price in all_prices:
        if not price.resource in all_prices_dict:
            all_prices_dict[price.resource] = []
        all_prices_dict[price.resource].append(price)
    return all_prices_dict


class EnergyPrice(BaseModel):
    price: int


class EnergyPriceResponse(BaseModel):
    success: bool


@router.post("/game/{game_id}/player/{player_id}/market/energy/set_price")
async def energy_set_price_player(price: EnergyPrice, game: Game = Depends(game_dep), player: int = Depends(player_dep)) -> EnergyPriceResponse:
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
async def order_create_player(order: UserOrder, game: Game = Depends(game_dep), player: Player = Depends(player_dep)) -> OrderCreateResponse:
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
        tick=game.current_tick,
        expiration_tick=order.expiration_tick,
        resource=order.resource.value
    )

    return {"success": True}


@router.post("/game/{game_id}/player/{player_id}/market/order/list")
async def order_list_player(game: Game = Depends(game_dep), player: Player = Depends(player_dep)) -> List[OrderResponse]:
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
async def order_cancel_player(body: OrderCancel, game: Game = Depends(game_dep), player: Player = Depends(player_dep)) -> OrderCancelResponse:
    for order_id in body.ids:
        await Order.update(
            order_id=order_id,
            order_status=OrderStatus.CANCELED.value
        )

    return {"success": True}
