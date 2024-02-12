from model import Trade, Resource
from model.order import Order
from .market import Market
from config import config


class EnergyMarket(Market):
    def __init__(self):
        super().__init__(Resource.energy)

    def cancel(self, order: Order):
        pass

    def match(self, order: Order, tick: int):
        pass

    def _update_order(self, order: Order):
        pass

    def _check_trade(self, trade: Trade):
        pass

    def _on_trade(self, trade: Trade):
        pass
