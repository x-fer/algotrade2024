from typing import Dict
import pandas as pd
from game.price_tracker.price_tracker import PriceTracker
from model import Trade
from config import config
from model.player import Player


class EnergyMarket:

    def __init__(self):
        self.price_tracker = PriceTracker()

    def match(self, players: Dict[int, Player], demand: int, max_price: int) -> Dict[int, int]:
        players_sorted = sorted(players.values(), key=lambda x: x.energy_price)
        players_sorted = [
            player for player in players_sorted if player.energy_price <= max_price]

        max_per_player = int(demand * config["max_energy_per_player"])

        orders = {}
        trades = []

        for player in players_sorted:
            to_sell = min(player.energy, demand, max_per_player)

            if to_sell <= 0:
                continue

            # player.energy -= to_sell # ne trebamo, zelimo da im se prikaze koliko proizvode
            demand -= to_sell

            player.money += to_sell * player.energy_price

            trades.append(Trade(
                buy_order=None,
                sell_order=None,
                filled_price=player.energy_price,
                filled_size=to_sell,
                filled_money=to_sell * player.energy_price,
                tick=pd.Timestamp.now(),
            ))

            orders[player.player_id] = to_sell

            if demand == 0:
                break

        self.price_tracker.on_end_match(trades)

        return orders
