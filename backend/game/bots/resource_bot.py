from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Tuple

from config import config
from game.tick.tick_data import TickData
from logger import logger
from model import Order, OrderSide, Player, Resource, Team

from . import Bot


resource_wanted_sum = config["bots"]["resource_sum"]
default_volume = config["bots"]["default_volume"]
min_volume = config["bots"]["min_volume"]
max_volume = config["bots"]["max_volume"]
min_price = config["bots"]["min_price"]
max_price = config["bots"]["max_price"]
price_change_coeff = config["bots"]["price_change_coeff"]
max_price_change = config["bots"]["max_price_change"]
expiration_ticks = config["bots"]["expiration_ticks"]
dataset_price_weight = config["bots"]["dataset_price_weight"]


@dataclass
class BuySellPrice:
    buy_price: int
    sell_price: int


@dataclass
class BuySellVolume:
    buy_volume: int
    sell_volume: int


class ResourceBot(Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.last_buy_coeffs = {resource: 0.5 for resource in Resource}
        self.last_sell_coeffs = {resource: 0.5 for resource in Resource}
        self.last_tick = None
        self.player_id = None

    async def run(self, tick_data: TickData):
        if self.player_id is None:
            await self.create_player(tick_data)

        if (
            self.last_tick is not None
            and tick_data.game.current_tick <= self.last_tick + expiration_ticks
        ):
            return

        self.last_tick = tick_data.game.current_tick
        resources_sum = self.get_resources_sum(tick_data)
        orders = await self.get_last_orders()

        for resource in Resource:
            resource_orders = orders[resource]
            resource_sum = resources_sum[resource]

            filled_buy_perc, filled_sell_perc = self.get_filled_perc(resource_orders)
            volume = self.get_volume(resource_sum)
            price = self.get_price(resource, volume, filled_buy_perc, filled_sell_perc)
            price = self.get_mixed_price(tick_data, resource, price)
            await self.create_orders(
                tick_data.game.current_tick, resource, price, volume
            )

    async def create_player(self, tick_data: TickData):
        team = await Team.get(team_secret=config["bots"]["team_secret"])
        self.player_id = await Player.create(
            player_name="resource_bot",
            game_id=tick_data.game.game_id,
            team_id=team.team_id,
            is_bot=True,
        )
        self.game_id = tick_data.game.game_id

    def get_resources_sum(self, tick_data: TickData) -> Dict[Resource, int]:
        """Returns sum of resources of all players"""
        resources_sum = {resource: 0 for resource in Resource}
        for resource in Resource:
            for player in tick_data.players.values():
                resources_sum[resource] += player[resource]
        return resources_sum

    def get_volume(self, resource_sum: int) -> BuySellVolume:
        wanted_volume_change = resource_wanted_sum - resource_sum
        buy_volume = default_volume - wanted_volume_change
        sell_volume = default_volume + wanted_volume_change
        buy_volume = clamp(min_volume, max_volume, int(buy_volume))
        sell_volume = clamp(min_volume, max_volume, int(sell_volume))
        return BuySellVolume(buy_volume=buy_volume, sell_volume=sell_volume)

    def get_price(
        self,
        resource: Resource,
        volume: BuySellVolume,
        filled_buy_perc: float,
        filled_sell_perc: float,
    ) -> BuySellPrice:
        last_buy_coeff = self.last_buy_coeffs[resource]
        last_sell_coeff = self.last_sell_coeffs[resource]

        new_buy_coeff = 1 - filled_buy_perc
        new_sell_coeff = 1 - filled_sell_perc

        buy_coeff = (
            price_change_coeff * new_buy_coeff
            + (1 - price_change_coeff) * last_buy_coeff
        )
        sell_coeff = (
            price_change_coeff * new_sell_coeff
            + (1 - price_change_coeff) * last_sell_coeff
        )

        if buy_coeff >= sell_coeff:
            # uzmi tezinski prosjek ako je buy coef veci
            buy_coeff = sell_coeff = (
                buy_coeff * volume.buy_volume + sell_coeff * volume.sell_volume
            ) / (volume.buy_volume + volume.sell_volume)

        buy_coeff = clamp(0, 1, buy_coeff)
        sell_coeff = clamp(0, 1, sell_coeff)

        self.last_buy_coeffs[resource] = buy_coeff
        self.last_sell_coeffs[resource] = sell_coeff

        buy_price = scale(min_price, max_price, buy_coeff)
        sell_price = scale(min_price, max_price, sell_coeff)

        return BuySellPrice(buy_price=buy_price, sell_price=sell_price)

    def get_filled_perc(self, orders: List[Order]) -> Tuple[int, int]:
        size = {side: 0 for side in OrderSide}
        filled_size = {side: 0 for side in OrderSide}
        for order in orders:
            size[order.order_side] += order.size
            filled_size[order.order_side] += order.filled_size
        filled_perc = {
            side: filled_size[side] / size[side] if size[side] > 0 else 0
            for side in OrderSide
        }
        return filled_perc[OrderSide.BUY], filled_perc[OrderSide.SELL]

    async def get_last_orders(self) -> Dict[str, Order]:
        if self.last_tick is None:
            return []
        orders_list = await Order.list(player_id=self.player_id, tick=self.last_tick)
        orders = {resource: [] for resource in Resource}
        for order in orders_list:
            orders[order.resource].append(order)
        return orders

    def get_mixed_price(
        self, tick_data: TickData, resource: Resource, price: BuySellPrice
    ) -> BuySellPrice:
        buy_price = self.mix_dataset_price(
            tick_data.dataset_row, price.buy_price, resource
        )
        sell_price = self.mix_dataset_price(
            tick_data.dataset_row, price.sell_price, resource
        )
        if buy_price == sell_price:
            sell_price = buy_price + 1
        return BuySellPrice(
            buy_price=buy_price,
            sell_price=sell_price,
        )

    def mix_dataset_price(self, dataset_row, price, resource: Resource):
        return (
            dataset_price_weight * dataset_row[resource.name.lower() + "_price"]
            + (1 - dataset_price_weight) * price
        )

    async def create_orders(
        self, tick, resource: Resource, price: BuySellPrice, volume: BuySellVolume
    ) -> None:
        buy_price = price.buy_price
        sell_price = price.sell_price
        buy_volume = volume.buy_volume
        sell_volume = volume.sell_volume
        logger.debug(
            f"({self.game_id}) Bot creating orders {tick=}, {resource=}, {buy_price=}, {sell_price=}, {buy_volume=}, {sell_volume=}"
        )
        await Order.create(
            game_id=self.game_id,
            player_id=self.player_id,
            price=buy_price,
            tick=tick,
            timestamp=datetime.now(),
            size=buy_volume,
            order_side=OrderSide.BUY,
            resource=resource,
            expiration_tick=tick + expiration_ticks,
        )
        await Order.create(
            game_id=self.game_id,
            player_id=self.player_id,
            price=sell_price,
            tick=tick,
            timestamp=datetime.now(),
            size=sell_volume,
            order_side=OrderSide.SELL,
            resource=resource,
            expiration_tick=tick + expiration_ticks,
        )


def scale(_min, _max, x):
    x = _min + (_max - _min) * x
    return clamp(_min, _max, x)


def clamp(_min, _max, x):
    return max(_min, min(_max, x))
