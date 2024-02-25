from model import Trade, Resource
from model.order import Order
from config import config
from model.player import Player


class EnergyMarket:
    def match(self, players: dict[int, Player], demand: int, max_price: int) -> dict[int, int]:
        players_sorted = sorted(players.values(), key=lambda x: x.energy_price)
        players_sorted = [
            player for player in players_sorted if player.energy_price <= max_price]

        max_per_player = int(demand * config["max_energy_per_player"])

        orders = {}

        for player in players_sorted:
            to_sell = min(player.energy, demand, max_per_player)

            if to_sell == 0:
                continue

            # player.energy -= to_sell # ne trebamo, zelimo da im se prikaze koliko proizvode
            demand -= to_sell

            player.money += to_sell * player.energy_price

            orders[player.player_id] = to_sell

            if demand == 0:
                break

        return orders
