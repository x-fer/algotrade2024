from dataclasses import dataclass, field
from model import Player, PowerPlant, Game, Order
from game.market import ResourceMarket
from game.bots.bot import Bot


@dataclass
class TickData:
    game: Game
    players: dict[int, Player]
    power_plants: dict[int, list[PowerPlant]]
    markets: dict[int, ResourceMarket]
    bots: list[Bot]
    power_plants: dict[int, list[PowerPlant]]

    dataset_row: dict = field(default_factory=dict)

    pending_orders: list[Order] = field(default_factory=list)
    user_cancelled_orders: list[Order] = field(default_factory=list)
    updated_orders: dict[int, Order] = field(default_factory=dict)
