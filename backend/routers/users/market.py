from dataclasses import dataclass
from enum import Enum
from fastapi import APIRouter, Depends
import pandas as pd
from db.model import Orders
from game.market import Resource
from orderbook.enums import OrderSide, OrderType
from routers.users.dependencies import game_id, player
from orderbook import OrderStatus

# GAME PATHS


router = APIRouter()


@router.get("/game/{game_id}/market/offer/list")
async def offer_list(game_id: int = Depends(game_id)):
    return await Orders.list(
        game_id=game_id,
        order_status=OrderStatus.ACTIVE.value
    )


@dataclass
class UserOrder:
    resource: Resource
    price: int
    size: int
    expiration_tick: int
    side: OrderSide
    type: OrderType


@router.post("/game/{game_id}/player/{player_id}/market/offer/create")
async def offer_create(order: UserOrder, game_id: int = Depends(game_id), player: int = Depends(player)):
    await Orders.create(
        game_id=game_id,
        player_id=player.player_id,

        order_type=order.type.value,
        order_side=order.side.value,
        order_status=OrderStatus.PENDING.value,

        price=order.price,
        size=order.size,

        expiration_tick=order.expiration_tick,
        timestamp=pd.Timestamp.now(),

        resource=order.resource.value
    )

    return {"success": True}
