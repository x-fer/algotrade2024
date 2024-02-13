from dataclasses import dataclass, field
import dataclasses
from datetime import datetime
from pprint import pprint
from typing import Tuple
from db import database
from model import Player, PowerPlant, Game, Order, OrderStatus, Resource, Team
from game.market import ResourceMarket, EnergyMarket
from game.bots import Bots, Bot
from config import config
from model.order_types import OrderSide, OrderType
from model.power_plant_types import PowerPlantType
from model.trade import Trade


class GameData:
    def __init__(self, game: Game):
        self.markets: dict[int, ResourceMarket] = {
            resource.value: ResourceMarket(resource.value)
            for resource in Resource
        }

        self.energy_market = EnergyMarket()
        self.bots = Bots.create_bots(game.bots)


@dataclass
class TickData:
    game: Game
    players: dict[int, Player]
    power_plants: dict[int, list[PowerPlant]]
    markets: dict[int, ResourceMarket]
    bots: list[Bot]

    dataset_row: dict = field(default_factory=dict)

    pending_orders: list[Order] = field(default_factory=list)
    user_cancelled_orders: list[Order] = field(default_factory=list)
    updated_orders: dict[int, Order] = field(default_factory=dict)


class Ticker:

    # in ram data
    def __init__(self):
        self.game_data: dict[int, GameData] = {}

    async def run_all_game_ticks(self):
        games = await Game.list()

        print("Running game ticks:")

        for game in games:
            if game.is_finished:
                print(f" {game.game_name} is finished")
                continue

            if datetime.now() < game.start_time:
                print(f" {game.game_name} has not started")
                continue

            if game.current_tick >= game.total_ticks:
                await Game.update(game_id=game.game_id, is_finished=True)
                print(f" {game.game_name} has just finished")

                if self.game_data.get(game.game_id) is not None:
                    del self.game_data[game.game_id]
                continue

            if self.game_data.get(game.game_id) is None:
                self.game_data[game.game_id] = GameData(game)

            await self.run_game_tick(game)

    async def run_game_tick(self, game: Game):

        tick_data = await self.get_tick_data(game)
        tick_data = self.run_markets(tick_data, game.current_tick)
        tick_data = self.run_power_plants(tick_data)
        tick_data, energy_sold = self.run_electricity_market(
            tick_data, self.game_data[game.game_id].energy_market)
        await self.save_electricity_orders(
            game, tick_data.players, energy_sold, game.current_tick)

        await self.save_tick_data(game, tick_data)
        await Game.update(game_id=game.game_id, current_tick=game.current_tick + 1)

        await self.run_bots(game)

    def run_electricity_market(self, tick_data: TickData, energy_market: EnergyMarket) -> Tuple[TickData, dict[int, int]]:
        energy_sold = energy_market.match(
            tick_data.players, tick_data.dataset_row["ENERGY_DEMAND"], tick_data.dataset_row["MAX_ENERGY_PRICE"])

        return tick_data, energy_sold

    async def save_electricity_orders(self, players: dict[int, Player], game: Game, energy_sold: dict[int, int], tick: int):
        for player_id, energy in energy_sold.items():
            await Order.create(
                game_id=game.game_id,
                player_id=player_id,
                order_type=OrderType.ENERGY.value,
                order_side=OrderSide.SELL.value,
                order_status=OrderStatus.COMPLETED.value,
                price=players[player_id].energy_price,
                size=energy,
                tick=tick,
                filled_size=energy,
                filled_money=players[player_id].energy_price * energy,
                filled_price=players[player_id].energy_price,
                expiration_tick=tick,
                timestamp=datetime.now(),
                resource=Resource.ENERGY.value
            )

    async def run_bots(self, game: Game):
        bots = self.game_data[game.game_id].bots

        for bot in bots:
            await bot.run()

    def run_markets(self, tick_data: TickData, tick: int):
        updated_orders = {}

        for order in tick_data.user_cancelled_orders:
            game_data = self.game_data[tick_data.game.game_id]
            market = game_data.markets[order.resource.value]

            updated = market.cancel(order)
            updated_orders.update(updated)

        for order in tick_data.pending_orders:
            game_data = self.game_data[tick_data.game.game_id]
            market = game_data.markets[order.resource.value]

            updated = market.match(order, tick)
            updated_orders.update(updated)

        tick_data.updated_orders.extend(updated_orders)

        return tick_data

    def run_power_plants(self, tick_data: TickData):
        for player_id in tick_data.power_plants.keys():
            tick_data.players[player_id].energy = 0

        for player_id in tick_data.players.keys():
            power_plants = tick_data.power_plants[player_id]
            player = tick_data.players[player_id]

            for power_plant in power_plants:
                # update temperature

                type = PowerPlantType(power_plant.type)

                if not power_plant.has_resources(player):
                    power_plant.powered_on = False

                power_plant.temperature = type.get_new_temp(
                    power_plant.temperature, power_plant.powered_on)

                if power_plant.temperature > 0.99:
                    player.energy += power_plant.get_produced_energy(
                        tick_data.dataset_row)

        return tick_data

    async def get_tick_data(self, game: Game) -> TickData:
        players = {
            player.player_id: player
            for player in await Player.list(game_id=game.game_id)
        }

        power_plants = {
            player_id: await PowerPlant.list(player_id=player_id)
            for player_id in players.keys()
        }

        pending_orders = await Order.list(game_id=game.game_id, order_status=OrderStatus.PENDING)
        user_cancelled_orders = await Order.list(game_id=game.game_id, order_status=OrderStatus.USER_CANCELLED)

        markets = self.game_data[game.game_id].markets

        tick_data = TickData(
            game=game,
            players=players,
            power_plants=power_plants,
            markets=markets,
            bots=self.game_data[game.game_id].bots,
            pending_orders=pending_orders,
            user_cancelled_orders=user_cancelled_orders,
            dataset_row={"COAL": 1,
                         "URANIUM": 2,
                         "BIOMASS": 3,
                         "GAS": 4,
                         "OIL": 5,
                         "GEOTHERMAL": 6,
                         "WIND": 7,
                         "SOLAR": 8,
                         "HYDRO": 9,
                         "ENERGY_DEMAND": 100,
                         "MAX_ENERGY_PRICE": 1000
                         }
        )

        return tick_data

    async def save_tick_data(self, game: Game, tick_data: TickData):
        for player in tick_data.players.values():
            await Player.update(**dataclasses.asdict(player))

        for power_plants in tick_data.power_plants.values():
            for power_plant in power_plants:
                await PowerPlant.update(**dataclasses.asdict(power_plant))

        for order in tick_data.updated_orders.values():
            await Order.update(**dataclasses.asdict(order))
