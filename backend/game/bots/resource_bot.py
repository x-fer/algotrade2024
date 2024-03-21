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
expiration_ticks = config["bots"]["expiration_ticks"]
extra_orders = config["bots"]["extra_orders"]
extra_orders_price_diff = config["bots"]["extra_orders_price_diff"]
extra_orders_volume_diff = config["bots"]["extra_orders_volume_diff"]
final_volume_multiplier = config["bots"]["final_volume_multiplier"]
final_price_multiplier = config["bots"]["final_price_multiplier"]


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

        # order_count = dict()
        # for resource in Resource:
        #     order_count[resource] = await Order.count_player_orders(
        #         game_id=tick_data.game.game_id,
        #         player_id=self.player_id,
        #         resource=resource)
        if (
            self.last_tick is not None
            and tick_data.game.current_tick <= self.last_tick + expiration_ticks
        ):
            # for resource in Resource:
            #     if order_count[resource] == 0:
            #         logger.warning(f"Game ({tick_data.game.game_id}) No orders for bot ({self.player_id}) in tick {tick_data.game.current_tick}, resource {resource.name}")
            return

        # for resource in Resource:
        #     if order_count[resource] > 0:
        #         logger.warning(f"Game ({tick_data.game.game_id}) Duplicate orders for bot ({self.player_id}) in tick {tick_data.game.current_tick}, resource {resource.name}")

        self.last_tick = tick_data.game.current_tick
        resources_sum = self.get_resources_sum(tick_data)
        orders = await self.get_last_orders()

        for resource in Resource:
            resource_orders = orders[resource]
            resource_sum = resources_sum[resource]

            filled_buy_perc, filled_sell_perc = self.get_filled_perc(
                resource_orders)
            volume = self.get_volume(resource_sum)
            price = self.get_price(
                resource, volume, filled_buy_perc, filled_sell_perc)
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
        return dataset_row[resource.name.lower() + "_price"] + price

    async def create_orders(
        self, tick, resource: Resource, price: BuySellPrice, volume: BuySellVolume
    ) -> None:
        buy_price = int(price.buy_price * final_price_multiplier)
        sell_price = int(price.sell_price * final_price_multiplier)
        buy_volume = int(volume.buy_volume * final_volume_multiplier)
        sell_volume = int(volume.sell_volume * final_volume_multiplier)
        if buy_price == sell_price:
            sell_price = buy_price + 1

        buy_volume_sum = 0
        sell_volume_sum = 0
        for i in range(extra_orders+1):
            buy_volume_sum += self.get_i_price(1, i)
            sell_volume_sum += self.get_i_price(1, i)
        if buy_volume_sum <= 0 or sell_volume_sum <= 0:
            logger.warning("Total sum of distributed orders is less than 0")
            return

        for i in range(extra_orders+1):
            new_buy_volume = self.get_i_price(buy_volume, i) / buy_volume_sum
            new_sell_volume = self.get_i_price(
                sell_volume, i) / sell_volume_sum
            new_buy_price = buy_price * (1 - i * extra_orders_price_diff)
            new_sell_price = sell_price * (1 + i * extra_orders_price_diff)
            await self.create_order(
                tick,
                resource,
                order_side=OrderSide.BUY,
                price=int(new_buy_price),
                volume=int(new_buy_volume),
            )
            await self.create_order(
                tick,
                resource,
                order_side=OrderSide.SELL,
                price=int(new_sell_price),
                volume=int(new_sell_volume),
            )

    def get_i_price(self, x, i):
        return x * (1 - i * extra_orders_volume_diff)

    async def create_order(
        self, tick, resource: Resource, order_side: OrderSide, price: int, volume: int
    ):
        logger.debug(
            f"({self.game_id}) Bot creating orders {tick=}, {order_side.value} {resource=}, {price=}"
        )
        if price <= 0:
            logger.warning(f"Volume ({volume}) is less than 0!")
            return
        if price <= 0:
            logger.warning(f"Price ({price}) is less than 0!")
            return
        await Order.create(
            game_id=self.game_id,
            player_id=self.player_id,
            price=price,
            tick=tick,
            timestamp=datetime.now(),
            size=volume,
            order_side=order_side,
            resource=resource,
            expiration_tick=tick + expiration_ticks + 1,
        )


def scale(_min, _max, x):
    x = _min + (_max - _min) * x
    return clamp(_min, _max, x)


def clamp(_min, _max, x):
    return max(_min, min(_max, x))
