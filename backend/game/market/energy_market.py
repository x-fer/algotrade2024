from collections import defaultdict
from datetime import datetime
from typing import Dict, List
from game.price_tracker.price_tracker import PriceTracker
from model import Trade
from config import config
from model.order import Order
from model.player import Player
from logger import logger


max_energy_per_player = config["player"]["max_energy_per_player"]


class EnergyMarket:
    def __init__(self):
        self.price_tracker = PriceTracker()
        self.orders = {}
        self.trades = []

    def match(self, players: Dict[str, Player], tick: int, demand: int, max_price: int) -> Dict[str, int]:
        """Returns mapping of players to sold energy in integer"""
        max_per_player = int(demand * max_energy_per_player)
        def get_energy(player: Player):
            return max_per_player if player.energy > max_per_player else player.energy

        players_grouped: list[Player] = defaultdict(list)
        for player in players.values():
            if player.energy_price <= max_price and player.energy > 0:
                players_grouped[player.energy_price].append(player)

        self.orders = {}
        self.trades = []

        for price in sorted(players_grouped.keys()):
            player_group: list[Player] = players_grouped[price]
            group_energy_sum = sum(get_energy(player) for player in player_group)

            for player in player_group:
                if group_energy_sum > demand:
                    energy_to_sell = get_energy(player) * demand / group_energy_sum
                    # print("PRINTIG 1", player.energy, energy_to_sell)
                    # print("PRINTIG  ", demand, group_energy_sum)
                else:
                    energy_to_sell = get_energy(player)
                    # print("PRINTIG 2", player.energy, energy_to_sell)
                energy_to_sell = int(energy_to_sell)
                self.create_trade(player, tick, energy_to_sell, price)
            demand -= group_energy_sum
            if demand <= 0:
                break

        self.price_tracker.on_end_match(self.trades)
        return self.orders

    def create_trade(self, player: Player, tick, energy: int, energy_price: int):
        player.money += energy * player.energy_price
        self.trades.append(Trade(
            trade_price=energy_price,
            trade_size=energy,
            total_price=energy * energy_price,
            tick=tick,
            buy_order_id="energy market",
            sell_order_id="energy market",
        ))
        self.orders[player.player_id] = energy