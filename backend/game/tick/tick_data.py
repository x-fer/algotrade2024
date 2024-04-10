from dataclasses import dataclass, field
from typing import Dict, List
from model import Player, Game, Order, DatasetData
from game.market import ResourceMarket, EnergyMarket
from game.bots.bot import Bot


@dataclass
class TickData:
    game: Game
    players: Dict[int, Player]
    markets: Dict[str, ResourceMarket]
    energy_market: EnergyMarket
    bots: List[Bot]

    dataset_row: DatasetData

    pending_orders: List[Order] = field(default_factory=list)
    user_cancelled_orders: List[Order] = field(default_factory=list)
    updated_orders: Dict[int, Order] = field(default_factory=dict)
    tick_trades: Dict[int, Order] = field(default_factory=list)
