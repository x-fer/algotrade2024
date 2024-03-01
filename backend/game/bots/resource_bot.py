from typing import Dict, List
import pandas as pd
from game.tick.tick_data import TickData
from model import Order, Resource, OrderSide, Team, Player
from . import Bot
from config import config
from logger import logger


resource_wanted_sum = config['bots']['resource_sum']
default_volume = config['bots']['default_volume']
min_volume = config['bots']['min_volume']
max_volume = config['bots']['max_volume']
min_price = config['bots']['min_price']
max_price = config['bots']['max_price']
price_change_coeff = config['bots']['price_change_coeff']
max_price_change = config['bots']['max_price_change']
expiration_ticks = config['bots']['expiration_ticks']


class ResourceBot(Bot):
    def __init__(self, player_id=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.buy_prices = {resource: 50 for resource in Resource}
        self.sell_prices = {resource: 50 for resource in Resource}
        self.last_tick = None
        self.player_id = None

    async def run(self, tick_data: TickData):
        if self.player_id is None:
            team = await Team.get(team_secret=config['bots']['team_secret'])
            self.player_id = await Player.create(
                player_name="resource_bot",
                game_id=tick_data.game.game_id,
                team_id=team.team_id,
                is_bot=True
            )
            self.game_id = tick_data.game.game_id

        if self.last_tick is not None and tick_data.game.current_tick < self.last_tick + expiration_ticks:
            return
        self.last_tick = tick_data.game.current_tick

        resources_sum = {resource: 0 for resource in Resource}
        for resource in Resource:
            for player in tick_data.players.values():
                resources_sum[resource] += player[resource.name]

        orders = await self.get_last_orders()

        for resource in Resource:
            if resource == Resource.energy:
                continue

            resource_orders = orders[resource]
            resource_sum = resources_sum[resource]
            buy_price = self.buy_prices[resource]
            sell_price = self.sell_prices[resource]

            # pozitivno ako bot treba otkupiti vise nego prodati
            wanted_volume_change = resource_wanted_sum - resource_sum
            # koliko bot kupuje s trzista
            buy_volume = default_volume + wanted_volume_change
            # koliko bot stavlja na trziste
            sell_volume = wanted_volume_change - wanted_volume_change
            buy_volume = clamp(min_volume, max_volume, int(buy_volume))
            sell_volume = clamp(min_volume, max_volume, int(sell_volume))

            filled_buy_perc, filled_sell_perc = self.get_filled_perc(
                resource_orders)
            buy_price -= price_change_coeff * buy_price * (1-2*filled_buy_perc)
            sell_price += price_change_coeff * \
                sell_price * (1-2*filled_sell_perc)

            if buy_price >= sell_price:
                price = (buy_price * buy_volume + sell_price *
                         sell_volume) / (buy_volume + sell_volume)
                buy_price = price
                sell_price = price
            buy_price = clamp(min_price, max_price, int(buy_price))
            sell_price = clamp(min_price, max_price, int(sell_price))
            if buy_price == sell_price:
                buy_price = sell_price - 1

            buy_price = self.mix_dataset_price(
                tick_data.dataset_row, buy_price, resource)
            sell_price = self.mix_dataset_price(
                tick_data.dataset_row, sell_price, resource)

            await self.create_orders(tick_data.game.current_tick,
                                     resource, buy_price, sell_price, buy_volume, sell_volume)
            self.buy_prices[resource] = buy_price
            self.sell_prices[resource] = sell_price

    def mix_dataset_price(self, dataset_row, price, resource):
        return config['bots']['dataset_price_weight'] * dataset_row[resource.name.lower() + "_price"] + (1 - config['bots']['dataset_price_weight']) * price

    def get_filled_perc(self, orders: List[Order]):
        size = {side: 0 for side in OrderSide}
        filled_size = {side: 0 for side in OrderSide}
        for order in orders:
            size[order.order_side] += order.size
            filled_size[order.order_side] += order.filled_size
        filled_perc = {side: filled_size[side] / size[side]
                       if size[side] > 0 else 0
                       for side in OrderSide}
        return filled_perc[OrderSide.BUY], filled_perc[OrderSide.SELL]

    async def get_last_orders(self) -> Dict[str, Order]:
        if self.last_tick is None:
            return []
        orders_list = await Order.list(player_id=self.player_id, tick=self.last_tick)
        orders = {resource: [] for resource in Resource}
        for order in orders_list:
            orders[order.resource].append(order)
        return orders

    async def create_orders(self, tick, resource, buy_price, sell_price, buy_volume, sell_volume) -> None:
        logger.debug(
            f"({self.game_id}) Bot creating orders {tick=}, {resource=}, {buy_price=}, {sell_price=}, {buy_volume=}, {sell_volume=}")
        await Order.create(
            game_id=self.game_id,
            player_id=self.player_id,
            price=buy_price,
            tick=tick,
            timestamp=pd.Timestamp.now(),
            size=buy_volume,
            order_side=OrderSide.BUY,
            resource=resource,
            expiration_tick=tick+expiration_ticks
        )
        await Order.create(
            game_id=self.game_id,
            player_id=self.player_id,
            price=sell_price,
            tick=tick,
            timestamp=pd.Timestamp.now(),
            size=sell_volume,
            order_side=OrderSide.SELL,
            resource=resource,
            expiration_tick=tick+expiration_ticks
        )


def clamp(_min, _max, x):
    return max(_min, min(_max, x))
