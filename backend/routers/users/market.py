from dataclasses import dataclass
from typing import List
from fastapi import APIRouter, Depends, HTTPException
import pandas as pd
from pydantic import BaseModel
from model import Order, OrderSide, OrderType, OrderStatus, Resource
from model.game import Game
from model.player import Player
from .dependencies import game_id, player

# GAME PATHS


router = APIRouter()


@router.get("/game/{game_id}/market/offer/list")
async def offer_list(game_id: int = Depends(game_id)):
    return await Order.list(
        game_id=game_id,
        order_status=OrderStatus.ACTIVE.value
    )


class EnergyPrice(BaseModel):
    price: int


@router.post("/game/{game_id}/player/{player_id}/market/energy/set_price")
async def energy_set_price_player(price: EnergyPrice, game_id: int = Depends(game_id), player: int = Depends(player)):
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


@router.post("/game/{game_id}/player/{player_id}/market/offer/create")
async def offer_create_player(order: UserOrder, game_id: int = Depends(game_id), player: int = Depends(player)):
    if order.type == OrderType.ENERGY:
        raise Exception(
            "Use /game/{game_id}/player/{player_id}/market/energy/set_price to set energy price")

    await Order.create(
        game_id=game_id,
        player_id=player.player_id,

        order_type=order.type.value,
        order_side=order.side.value,
        order_status=OrderStatus.PENDING.value,

        price=order.price,
        size=order.size,
        tick=(await Game.get(game_id=game_id)).current_tick,

        expiration_tick=order.expiration_tick,
        timestamp=pd.Timestamp.now(),

        resource=order.resource.value
    )

    return {"success": True}


@router.post("/game/{game_id}/player/{player_id}/market/offer/list")
async def offer_list_player(game_id: int = Depends(game_id), player: int = Depends(player)):
    return await Order.list(
        game_id=game_id,
        player_id=player.player_id,
        order_status=OrderStatus.ACTIVE.value
    )


class OfferCancel(BaseModel):
    ids: List[int]


@router.post("/game/{game_id}/player/{player_id}/market/offer/cancel")
async def offer_cancel_player(body: OfferCancel, game_id: int = Depends(game_id), player: int = Depends(player)):
    for order_id in body.ids:
        await Order.update(
            order_id=order_id,
            order_status=OrderStatus.CANCELED.value
        )

    return {"success": True}
