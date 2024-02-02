from enum import Enum
from orderbook import *
from price_tracker import *


class Resource(Enum):
    coal = 0
    uranium = 1
    biomass = 2
    gas = 3
    oil = 4


class Market:
    def __init__(self, resource: Resource):
        self.orderbook = OrderBook()
        self.price_tracker = PriceTracker(self.orderbook)
        self.resource = resource

    def check_add(self):
        pass

    def on_cancel(self):
        pass

    def on_begin_match(self):
        pass

    def check_trade(self):
        pass

    def on_trade(self):
        pass

    def on_end_match(self):
        pass

    def on_complete(self):
        pass

    def on_add_fail(self):
        pass


markets = {
    x.value: Market()
    for x in Resource
}
