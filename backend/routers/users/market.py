from collections import defaultdict
from datetime import datetime
from enum import Enum
from functools import reduce
from itertools import chain
from operator import attrgetter
from typing import Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field

from config import config
from model import Order, OrderSide, OrderStatus, Resource
from model.game import Game
from model.market import Market
from model.player import Player
from model.resource import Energy, ResourceOrEnergy
from model.trade import Trade
from routers.model import SuccessfulResponse
from logger import logger

from .dependencies import (
    check_game_active_dep,
    game_dep,
    order_dep,
    player_dep,
    start_end_tick_dep,
)

router = APIRouter(dependencies=[Depends(check_game_active_dep)])


class MarketPricesResponse(BaseModel):
    tick: int = Field(..., description="tick of this data")
    low: int = Field(..., description="lowest price of all trades (in this tick)")
    high: int = Field(..., description="highest price of all trades")
    open: int = Field(..., description="price of the first trade")
    close: int = Field(..., description="price of the last trade")
    market: int = Field(
        ..., description="average price of all trades weighted by their volume"
    )
    volume: int = Field(..., description="total volume traded")


@router.get(
    "/game/{game_id}/market/prices", summary="Get market data for previous ticks."
)
def market_prices(
    start_end=Depends(start_end_tick_dep),
    resource: Resource | Energy = Query(default=None),
    game: Game = Depends(game_dep),
) -> Dict[Resource | Energy, List[MarketPricesResponse]]:
    """
    Returns market data for resources for queried ticks.
    If no trades were made in this tick, data from previous tick is taken.
    """
    start_tick, end_tick = start_end

    query = [
        Market.game_id == game.game_id,
        Market.tick >= start_tick,
        Market.tick <= end_tick,
    ]
    if resource is not None:
        query.append(Market.resource == resource.value)

    all_prices: List[Market] = Market.find(*query).all()
    all_prices_dict = defaultdict(list)
    for price in all_prices:
        all_prices_dict[price.resource].append(price)
    return all_prices_dict


class EnergyPrice(BaseModel):
    price: int


@router.post(
    "/game/{game_id}/player/{player_id}/energy/set_price",
    summary="Set price at which you will sell your electricity",
)
def energy_set_price_player(
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

    with player.lock():
        player.energy_price=price.price
        player.save()

    return SuccessfulResponse()


class OrderResponse(BaseModel):
    order_id: str
    player_id: str
    price: int = Field(..., description="price per unit of resource")
    size: int = Field(..., description="total volume of this order")
    tick: int = Field(..., description="tick when this order was put in the market")
    timestamp: datetime = Field(..., description="exact time when this order was made")
    order_side: OrderSide
    order_status: OrderStatus
    filled_size: int = Field(
        ..., description="volume of this order that was already traded"
    )
    expiration_tick: int = Field(
        ..., description="tick when this order will be cancelled"
    )


class OrderRestriction(Enum):
    all_orders = "all"
    bot_orders = "bot"
    best_orders = "best"


@router.get("/game/{game_id}/orders", summary="Get orders in this game.")
def order_list(
    game: Game = Depends(game_dep),
    restriction: OrderRestriction = Query(
        default=OrderRestriction.all_orders,
        description=(
            "all to get all orders in this game for given ticks / "
            "bot for only bot orders / best for those with best prices"
        ),
    ),
) -> Dict[str, Dict[str, List[OrderResponse]]]:
    bots = Player.find(Player.is_bot == int(True)).all()
    bot_ids = set(map(attrgetter("pk"), bots))

    active_orders = Order.find(
        Order.game_id == game.game_id,
        Order.order_status == OrderStatus.ACTIVE.value
    ).all()
    pending_orders = Order.find(
        Order.game_id == game.game_id,
        Order.order_status == OrderStatus.PENDING.value
    ).all()

    def is_bot_order(order: Order):
        return order.player_id in bot_ids

    all_orders = active_orders + list(filter(is_bot_order, pending_orders))

    if restriction == OrderRestriction.all_orders:
        return orders_to_dict(all_orders)
    elif restriction == OrderRestriction.bot_orders:
        bot_orders = list(filter(is_bot_order, chain(pending_orders, active_orders)))
        return orders_to_dict(bot_orders)
    elif restriction == OrderRestriction.best_orders:
        orders = orders_to_dict(all_orders)
        for resource in orders:
            for order_side in orders[resource]:
                orders[resource][order_side] = [reduce(
                    is_better_order, orders[resource][order_side]
                )]
        return orders


def is_better_order(order_1: Order, order_2: Order):
    if order_1.order_side != order_2.order_side:
        raise Exception("This is because order sides don't match and shouldn't happen")
    if order_1.order_side == OrderSide.BUY:
        return order_1 if order_1.price > order_2.price else order_2
    else:
        return order_1 if order_1.price < order_2.price else order_2


def orders_to_dict(orders: List[Order]) -> Dict[ResourceOrEnergy, Dict[OrderSide, List[Order]]]:
    orders_dict = dict()
    for order in orders:
        if order.resource.value not in orders_dict:
            orders_dict[order.resource.value] = dict()
        if order.order_side.value not in orders_dict[order.resource.value]:
            orders_dict[order.resource.value][order.order_side.value] = list()
        orders_dict[order.resource.value][order.order_side.value].append(order)
    return orders_dict


@router.get(
    "/game/{game_id}/player/{player_id}/orders",
    summary="Get only your orders in this game",
)
def order_list_player(
    game: Game = Depends(game_dep), player: Player = Depends(player_dep)
) -> Dict[str, Dict[str, List[OrderResponse]]]:
    """List orders you placed in market that are still active."""
    active_orders = Order.find(
        Order.player_id == player.player_id,
        Order.game_id == game.game_id,
        Order.order_status == OrderStatus.ACTIVE.value
    ).all()
    pending_orders = Order.find(
        Order.player_id == player.player_id,
        Order.game_id == game.game_id,
        Order.order_status == OrderStatus.PENDING.value
    ).all()
    return orders_to_dict(active_orders + pending_orders)


@router.get(
    "/game/{game_id}/player/{player_id}/orders/{order_id}",
    summary="Get order details for given order_id",
)
def order_get_player(
    order: Order = Depends(order_dep),
    game: Game = Depends(game_dep),
    player: Player = Depends(player_dep),
) -> OrderResponse:
    return order


class UserOrder(BaseModel):
    resource: Resource = Field(..., description="resource you are buying or selling")
    price: int = Field(
        ..., description="price per unit of resource you are buying or selling"
    )
    size: int = Field(..., description="ammount of resource you want to buy or sell")
    expiration_tick: Optional[int] = Field(
        None, description="exact tick in which this order will expire"
    )
    expiration_length: Optional[int] = Field(
        None, description="number of ticks from now when this order will expire"
    )
    side: OrderSide = Field(
        ...,
        description="BUY if you want to buy a resource, SELL if you want to sell it",
    )


@router.post(
    "/game/{game_id}/player/{player_id}/orders/create",
    summary="Create a new order on the market",
)
def order_create_player(
    order: UserOrder,
    game: Game = Depends(game_dep),
    player: Player = Depends(player_dep),
) -> str:
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

    total_orders_not_processed = Order.find(
        Order.game_id == game.game_id,
        Order.player_id == player.player_id,
        Order.resource == order.resource.value,
        (Order.order_status == OrderStatus.ACTIVE.value)
        | (Order.order_status == OrderStatus.PENDING.value)
    ).count()

    if total_orders_not_processed >= config["player"]["max_orders"]:
        raise HTTPException(
            status_code=400,
            detail=f'Maximum {config["player"]["max_orders"]} orders can be active at a time',
        )

    resources = player.resources[order.resource]
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

    return (
        Order(
            game_id=game.game_id,
            player_id=player.player_id,
            order_side=order.side.value,
            order_status=OrderStatus.PENDING.value,
            timestamp=datetime.now(),
            price=order.price,
            size=order.size,
            tick=game.current_tick,
            expiration_tick=order.expiration_tick,
            resource=order.resource.value,
        )
        .save()
        .pk
    )


@router.get(
    "/game/{game_id}/player/{player_id}/orders/{order_id}/cancel",
    summary="Cancel the order",
)
def order_cancel_player(
    order: Order = Depends(order_dep),
    game: Game = Depends(game_dep),
    player: Player = Depends(player_dep),
) -> SuccessfulResponse:
    with player.lock():
        order_to_cancel = Order.get(order.order_id)
        if order_to_cancel.player_id != player.player_id:
            raise HTTPException(
                status_code=400, detail="You can only cancel your own orders"
            )
        elif order_to_cancel.order_status == OrderStatus.PENDING.value:
            order.order_status=OrderStatus.CANCELLED.value
            order.save()
        elif order_to_cancel.order_status == OrderStatus.ACTIVE.value:
            order.order_status=OrderStatus.USER_CANCELLED.value
            order.save()
        else:
            raise HTTPException(
                status_code=400,
                detail="Only pending or active orders can be cancelled",
            )
    return SuccessfulResponse()


class UserTrade(BaseModel):
    buy_order_id: str = Field(..., description="order_id of buyer side in this trade")
    sell_order_id: str = Field(..., description="order_id of seller side in this trade")

    buy_player_id: str
    sell_player_id: str

    resource: ResourceOrEnergy

    tick: int = Field(..., description="Tick when this trade took place")

    total_price: int = Field(
        ..., description="Total value of the trade = filled_size * filled_price"
    )
    trade_size: int = Field(..., description="Ammount of resources that was traded")
    trade_price: int = Field(
        ..., description="Price at which the unit of resource was traded"
    )


@router.get(
    "/game/{game_id}/player/{player_id}/trades",
    summary="Get your matched trades for previous ticks",
)
def get_trades_player(
    start_end=Depends(start_end_tick_dep),
    player: Player = Depends(player_dep),
    resource: ResourceOrEnergy = Query(default=None),
) -> Dict[OrderSide, List[UserTrade]]:
    """
    Trade is when two orders match.
    Get all trades for your player in querried ticks.
    """
    start_tick, end_tick = start_end

    conditions = [Trade.tick <= end_tick, Trade.tick >= start_tick]
    if resource is not None:
        conditions.append(Trade.resource == resource.value)

    buy_trades = Trade.find(Trade.buy_player_id == player.player_id, *conditions).all()
    sell_trades = Trade.find(
        Trade.sell_player_id == player.player_id, *conditions
    ).all()
    logger.info(f"{player.player_name} {len(buy_trades)}, {len(sell_trades)}")
    return {
        OrderSide.BUY: buy_trades,
        OrderSide.SELL: sell_trades,
    }
