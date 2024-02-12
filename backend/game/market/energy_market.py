from model import Trade, Resource
from .market import Market
from config import config


class EnergyMarket(Market):
    def __init__(self):
        super().__init__(Resource.energy)
