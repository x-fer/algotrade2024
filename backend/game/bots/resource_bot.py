from typing import List
import dataclasses
import abc
from game.tick.tick_data import TickData
from model import Order, Resource, OrderSide
from . import Bot
from config import config


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
    def __init__(self, *args, **kwargs):
        self.buy_prices = {resource: 50 for resource in Resource}
        self.sell_prices = {resource: 50 for resource in Resource}
        self.last_tick = None

    async def run(self, tick_data: TickData):
        if self.last_tick is not None and tick_data.game.current_tick < self.last_tick + expiration_ticks:
            return
        self.last_tick = tick_data.game.current_tick
        
        resources_sum = {resource: 0 for resource in Resource}
        for resource in Resource:
            for player in tick_data.players.values():
                resources_sum[resource] += player[resource]

        orders = await self.get_last_orders()

        for resource in Resource:
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
            buy_volume = clamp(min_volume, max_volume, buy_volume)
            sell_volume = clamp(min_volume, max_volume, sell_volume)

            filled_buy_perc, filled_sell_perc = self.get_filled_perc(resource_orders)
            buy_price -= price_change_coeff * buy_price * (1-2*filled_buy_perc)
            sell_price += price_change_coeff * sell_price * (1-2*filled_sell_perc)

            if buy_price >= sell_price:
                price = (buy_price * buy_volume + sell_price * sell_volume) / (buy_volume + sell_volume)
                buy_price = price
                sell_price = price
            buy_price = clamp(min_price, max_price, buy_price)
            sell_price = clamp(min_price, max_price, sell_price)
            if buy_price == sell_price:
                buy_price = sell_price - 1

            await self.create_orders(tick_data.game.current_tick,
                                     resource, buy_price, sell_price, buy_volume, sell_volume)
            self.buy_prices[resource] = buy_price
            self.sell_prices[resource] = sell_price

    def get_filled_perc(self, orders: list[Order]):
        size = {side: 0 for side in OrderSide}
        filled_size = {side: 0 for side in OrderSide}
        for order in orders:
            size[order.order_side] += order.size
            filled_size[order.order_side] += order.filled_size
        filled_perc = {side: filled_size[side] / size[side] for side in OrderSide}
        return filled_perc[OrderSide.BUY], filled_perc[OrderSide.SELL]

    async def get_last_orders(self) -> dict[str, Order]:
        if self.last_tick is None: return []
        orders_list = await Order.list(player_id=self.player_id, tick=self.last_tick)
        orders = {resource: [] for resource in Resource}
        for order in orders_list:
            orders[order.resource].append(order)
        return orders
    
    async def create_orders(self, tick, resource, buy_price, sell_price, buy_volume, sell_volume) -> None:
        Order.create(**dataclasses.asdict(Order(
            game_id=self.game_id,
            player_id=self.player_id,
            price=buy_price,
            tick=tick,
            timestamp=tick,
            size=buy_volume,
            order_side=OrderSide.BUY,
            resource=resource,
            expiration_tick=tick+expiration_ticks
        )))
        Order.create(**dataclasses.asdict(Order(
            game_id=self.game_id,
            player_id=self.player_id,
            price=sell_price,
            tick=tick,
            timestamp=tick,
            size=sell_volume,
            order_side=OrderSide.SELL,
            resource=resource,
            expiration_tick=tick+expiration_ticks
        )))


def clamp(_min, _max, x):
    return max(_min, min(_max, x))