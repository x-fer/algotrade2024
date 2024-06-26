from dataclasses import dataclass, field
from typing import Dict, List
from model import Player, Game, Order, DatasetData
from game.market import ResourceMarket, EnergyMarket
from game.bots.bot import Bot
from model.trade import Trade


@dataclass
class TickData:
    game: Game
    players: Dict[str, Player]
    markets: Dict[str, ResourceMarket]
    energy_market: EnergyMarket
    bots: List[Bot]

    dataset_row: DatasetData

    pending_orders: List[Order] = field(default_factory=list)
    user_cancelled_orders: List[Order] = field(default_factory=list)
    updated_orders: Dict[str, Order] = field(default_factory=dict)
    tick_trades: List[Trade] = field(default_factory=list)
