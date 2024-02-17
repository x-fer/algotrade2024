from typing import List
import abc
from game.tick.tick_data import TickData
from model import Order, Resource
from . import Bot
from config import config


class ResourceBot(Bot):
    def __init__(self, *args, **kwargs):
        self.prices = {resource.name: 50 for resource in Resource}
        self.order_ids = []
        self.last_tick = -999
        

    async def run(self, tick_data: TickData):
        expiration_ticks = config['bots']['expiration_ticks']
        if tick_data.game.current_tick < self.last_tick + expiration_ticks:
            return
        self.last_tick = tick_data.game.current_tick
        
        resources_sum = {resource.name: 0 for resource in Resource}
        for player in tick_data.players.values():
            for resource in Resource:
                resources_sum[resource.name] += player[resource.name]
        
        resource_wanted_sum = config['bots']['resource_sum']
        default_volume = config['bots']['default_volume']
        min_volume = config['bots']['min_volume']
        max_volume = config['bots']['max_volume']
        min_price = config['bots']['min_price']
        max_price = config['bots']['max_price']

        for resource in Resource:
            resource_sum = resources_sum[resource.name]
            price = self.prices[resource.name]

            # pozitivno ako bot treba otkupiti vise nego prodati
            wanted_diff = resource_wanted_sum - resource_sum

            # koliko bot kupuje s trzista
            buy_volume = default_volume + wanted_diff
            # koliko bot stavlja na trziste
            sell_volume = wanted_diff - wanted_diff

            buy_volume = clamp(min_volume, max_volume, buy_volume)
            sell_volume = clamp(min_volume, max_volume, sell_volume)

            price = clamp(min_price, max_price, price)

            self.price = price

    def get_last_orders(self, tick: int):
        Order.list(player_id=self.player_id, tick=tick)


def clamp(_min, _max, x):
    return max(_min, min(_max, x))