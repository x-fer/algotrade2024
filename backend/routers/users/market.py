from collections import defaultdict
from datetime import datetime
from enum import Enum
from typing import List, Dict, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from model.resource import Energy
from pydantic import BaseModel, Field
from model import Order, OrderSide, OrderStatus, Resource
from model.game import Game
from model.market import Market
from model.player import Player
from routers.users.model import EnergyPrice, MarketPricesResponse
from .dependencies import (
    game_dep,
    player_dep,
    check_game_active_dep,
    start_end_tick_dep,
)
from db.db import database
from routers.model import SuccessfulResponse
from config import config


router = APIRouter(dependencies=[Depends(check_game_active_dep)])


@router.get(
    "/game/{game_id}/market/prices", summary="Get market data for previous ticks."
)
async def market_prices(
    start_end=Depends(start_end_tick_dep),
    resource: Resource | Energy = Query(default=None),
    game: Game = Depends(game_dep),
) -> Dict[Resource | Energy, List[MarketPricesResponse]]:
    """
    Returns market data for resources for queried ticks.
    If no trades were made in this tick, data from previous tick is taken.
    """
    start_tick, end_tick = start_end

    all_prices: List[Market] = await Market.find(
        (Market.game_id==game.game_id) &
        (Market.tick >= start_tick) &
        (Market.tick <= end_tick) &
        (Market.resource == resource.value)
    )
    all_prices_dict = defaultdict(list)
    for price in all_prices:
        all_prices_dict[price.resource].append(price)
    return all_prices_dict


@router.post(
    "/game/{game_id}/player/{player_id}/energy/set_price",
    summary="Set price at which you will sell your electricity",
)
async def energy_set_price_player(
    price: EnergyPrice,
    game: Game = Depends(game_dep),
    player: Player = Depends(player_dep),
) -> SuccessfulResponse:
    """
    Set the price for your energy. Our energy engine
    will buy energy from players in price ascending
    order, but cheaper than some maximum price. Make sure
    your price is competitive so you can sell it.
    """
    if price.price <= 0:
        raise HTTPException(status_code=400, detail="Price must be greater than 0")

    await Player.update(player_id=player.player_id, energy_price=price.price)

    return SuccessfulResponse()


class OrderResponse(BaseModel):
    order_id: int
    player_id: int
    price: int = Field(..., description="price per unit of resource")
    size: int = Field(..., description="total volume of this order")
    tick: int = Field(..., description="tick when this order was put in the market")
    timestamp: datetime = Field(..., description="exact time when this order was made")
    order_side: OrderSide
    order_status: OrderStatus
    filled_size: int = Field(..., description="volume of this order that was already traded")
    expiration_tick: int = Field(..., description="tick when this order will be cancelled")


class OrderRestriction(Enum):
    all_orders = "all"
    bot_orders = "bot"
    best_orders = "best"


@router.get("/game/{game_id}/orders", summary="Get orders in this game.")
async def order_list(
    game: Game = Depends(game_dep),
    restriction: OrderRestriction = Query(
        default=OrderRestriction.all_orders,
        description=(
            "all to get all orders in this game for given ticks / "
            "bot for only bot orders / best for those with best prices"
        ),
    ),
) -> Dict[Resource, List[OrderResponse]]:
    if restriction == OrderRestriction.all_orders:
        orders = await Order.list_orders_by_game_id(
            game_id=game.game_id
        )
    elif restriction == OrderRestriction.bot_orders:
        orders = await Order.list_bot_orders_by_game_id(
            game_id=game.game_id,
        )
    elif restriction == OrderRestriction.best_orders:
        best_buy_order = await Order.list_best_orders_by_game_id(
            game_id=game.game_id, order_side=OrderSide.BUY
        )
        best_sell_order = await Order.list_best_orders_by_game_id(
            game_id=game.game_id, order_side=OrderSide.SELL
        )
        orders = best_buy_order + best_sell_order
    return orders_to_dict(orders)


def orders_to_dict(orders: List[Order]) -> Dict[Resource, List[Order]]:
    orders_dict = defaultdict(list)
    for order in orders:
        orders_dict[order.resource].append(order)
    return orders_dict


@router.get(
    "/game/{game_id}/player/{player_id}/orders",
    summary="Get only your orders in this game",
)
async def order_list_player(
    game: Game = Depends(game_dep), player: Player = Depends(player_dep)
) -> Dict[Resource, List[OrderResponse]]:
    """List orders you placed in market that are still active."""
    active_orders = await Order.list(
        game_id=game.game_id,
        player_id=player.player_id,
        order_status=OrderStatus.ACTIVE.value,
    )
    pending_orders = await Order.list(
        game_id=game.game_id,
        player_id=player.player_id,
        order_status=OrderStatus.PENDING.value,
    )
    return orders_to_dict(active_orders + pending_orders)


@router.get(
    "/game/{game_id}/player/{player_id}/orders/{order_id}",
    summary="Get order details for given order_id",
)
async def order_get_player(
    order_id: int, game: Game = Depends(game_dep), player: Player = Depends(player_dep)
) -> OrderResponse:
    order = await Order.get(
        order_id=order_id, game_id=game.game_id, player_id=player.player_id
    )
    return order


class UserOrder(BaseModel):
    resource: Resource = Field(..., description="resource you are buying or selling")
    price: int = Field(..., description="price per unit of resource you are buying or selling")
    size: int = Field(..., description="ammount of resource you want to buy or sell")
    expiration_tick: Optional[int]  = Field(None, description="exact tick in which this order will expire")
    expiration_length: Optional[int] = Field(None, description= "number of ticks from now when this order will expire")
    side: OrderSide = Field(..., description="BUY if you want to buy a resource, SELL if you want to sell it")


@router.post(
    "/game/{game_id}/player/{player_id}/orders/create",
    summary="Create a new order on the market",
)
async def order_create_player(
    order: UserOrder,
    game: Game = Depends(game_dep),
    player: Player = Depends(player_dep),
) -> int:
    f"""
    - If side is buy, price is maximum price you will accept.
    - If side is sell, price is minimum price at which you will sell.
    - Exactly one of expiration_tick or expiration_length must be set

    Orders will be placed in matching engine by the time of arrival at the end of the tick.
    However, they will be matched in price-time priority. See external docs for details.

    **Important notes:**
    - Make sure you have *enough* resources or money for this order in the time
    of *placing the order* and in time when *order is matched*. Otherwise **it will be cancelled**.
    - Orders can be **partially** matched, see external docs for details.
    - You can have a **maximum of {config['player']['max_orders']} orders** at a time for a resource.
    """
    if order.expiration_tick is None == order.expiration_length is None:
        raise HTTPException(
            status_code=400,
            detail="Exactly one of expiration_tick and expiration_length must not be None",
        )
    if order.expiration_length is not None:
        if order.expiration_length <= 0:
            raise HTTPException(
                status_code=400,
                detail=f"Expiration length ({order.expiration_length}) must be greater than 0",
            )
        order.expiration_tick = game.current_tick + order.expiration_length
    if order.expiration_tick <= game.current_tick:
        raise HTTPException(
            status_code=400,
            detail=f"Expiration tick ({order.expiration_tick}) must be in the future, current_tick ({game.current_tick})",
        )
    if order.price <= 0:
        raise HTTPException(
            status_code=400, detail=f"Price ({order.price}) must be greater than 0"
        )
    if order.size <= 0:
        raise HTTPException(
            status_code=400, detail=f"Size ({order.size}) must be greater than 0"
        )

    total_orders_not_processed = await Order.count_player_orders(
        game_id=game.game_id, player_id=player.player_id, resource=order.resource
    )

    if total_orders_not_processed >= config["player"]["max_orders"]:
        raise HTTPException(
            status_code=400,
            detail=f'Maximum {config["player"]["max_orders"]} orders can be active at a time',
        )

    resources = player[order.resource]
    cost = order.price * order.size
    if order.side is OrderSide.SELL and resources < order.size:
        raise HTTPException(
            status_code=400,
            detail=f"Not enough resources: has ({resources}), sells ({order.size})",
        )
    elif order.side is OrderSide.BUY and player.money < cost:
        raise HTTPException(
            status_code=400,
            detail=f"Not enough money: has ({player.money}), order_cost({cost}) = size({order.size})*price({order.price})",
        )

    return await Order.create(
        game_id=game.game_id,
        player_id=player.player_id,
        order_side=order.side.value,
        order_status=OrderStatus.PENDING,
        timestamp=datetime.now(),
        price=order.price,
        size=order.size,
        tick=game.current_tick,
        expiration_tick=order.expiration_tick,
        resource=order.resource,
    )


class OrderCancel(BaseModel):
    ids: List[int]


@router.post(
    "/game/{game_id}/player/{player_id}/orders/cancel",
    summary="Cancel the list of orders",
)
async def order_cancel_player(
    body: OrderCancel,
    game: Game = Depends(game_dep),
    player: Player = Depends(player_dep),
) -> SuccessfulResponse:
    async with database.transaction():
        for order_id in body.ids:
            order_to_cancel = await Order.get(order_id=order_id)
            if order_to_cancel.player_id != player.player_id:
                raise HTTPException(
                    status_code=400, detail="You can only cancel your own orders"
                )
            elif order_to_cancel.order_status == OrderStatus.PENDING.value:
                await Order.update(
                    order_id=order_id, order_status=OrderStatus.CANCELLED.value
                )
            elif order_to_cancel.order_status == OrderStatus.ACTIVE.value:
                await Order.update(
                    order_id=order_id, order_status=OrderStatus.USER_CANCELLED.value
                )
            else:
                raise HTTPException(
                    status_code=400,
                    detail="Only pending or active orders can be cancelled",
                )
    return SuccessfulResponse()


class UserTrade(BaseModel):
    trade_id: int
    buy_order_id: int = Field(..., description="order_id of buyer side in this trade")
    sell_order_id: int = Field(..., description="order_id of seller side in this trade")
    tick: int = Field(..., description="Tick when this trade took place")

    filled_money: int = Field(..., description="Total value of the trade = filled_size * filled_price")
    filled_size: int = Field(..., description="Ammount of resources that was traded")
    filled_price: int = Field(..., description="Price at which the unit of resource was traded")


@router.get(
    "/game/{game_id}/player/{player_id}/trades",
    summary="Get your matched trades for previous ticks",
)
async def get_trades_player(
    start_end=Depends(start_end_tick_dep),
    player: Player = Depends(player_dep),
    resource: Resource = Query(default=None),
) -> Dict[OrderSide, List[UserTrade]]:
    """
    Trade is when two orders match.
    Get all trades for your player in querried ticks.
    """
    start_tick, end_tick = start_end

    buy_trades = await TradeDb.list_buy_trades_by_player_id(
        player_id=player.player_id,
        min_tick=start_tick,
        max_tick=end_tick,
        resource=resource,
    )
    sell_trades = await TradeDb.list_sell_trades_by_player_id(
        player_id=player.player_id,
        min_tick=start_tick,
        max_tick=end_tick,
        resource=resource,
    )
    return {
        OrderSide.BUY: buy_trades,
        OrderSide.SELL: sell_trades,
    }
