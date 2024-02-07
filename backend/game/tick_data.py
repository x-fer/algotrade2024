from db import Game, Player, Order, PowerPlant
from .market import Market


class TickData:
    game: Game
    players: list[Player]
    new_orders: list[Order]
    cancelled_orders: list[Order]
    power_plants: dict[int, PowerPlant]
    markets: dict[int, Market]
