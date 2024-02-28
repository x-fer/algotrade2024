from dataclasses import dataclass, field
from typing import Dict, List
from model import Player, Game, Order
from game.market import ResourceMarket
from game.bots.bot import Bot


@dataclass
class TickData:
    game: Game
    players: Dict[int, Player]
    markets: Dict[int, ResourceMarket]
    bots: List[Bot]

    dataset_row: dict = field(default_factory=dict)

    pending_orders: List[Order] = field(default_factory=list)
    user_cancelled_orders: List[Order] = field(default_factory=list)
    updated_orders: Dict[int, Order] = field(default_factory=dict)
