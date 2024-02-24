import dataclasses
from datetime import datetime
from typing import Tuple
import pandas as pd
from model import Player, PowerPlantType, Game, Order, OrderStatus, Resource, DatasetData, OrderSide, OrderType
from game.market import ResourceMarket, EnergyMarket
from game.bots import Bots
from .tick_data import TickData
from logger import logger
from db import database


class GameData:
    def __init__(self, game: Game, players: dict[int, Player]):
        self.markets: dict[int, ResourceMarket] = {
            resource.value: ResourceMarket(resource, players)
            for resource in Resource
        }
        self.energy_market = EnergyMarket()
        self.bots = Bots.create_bots(game.bots)


class Ticker:
    def __init__(self):
        self.game_data: dict[int, GameData] = {}

    async def run_all_game_ticks(self):
        games = await Game.list()

        for game in games:
            if game.is_finished:
                continue

            if datetime.now() < game.start_time:
                continue

            if game.current_tick >= game.total_ticks:
                try:
                    await Game.update(game_id=game.game_id, is_finished=True)
                    if self.game_data.get(game.game_id) is not None:
                        del self.game_data[game.game_id]
                    logger.info(
                        f"Finished game ({game.game_id}) {game.game_name}")
                except Exception as e:
                    logger.critical(
                        f"Failed finishing game ({game.game_id}) {game.current_tick} with error: " + str(e))
                continue

            if self.game_data.get(game.game_id) is None:
                try:
                    logger.info(
                        f"Starting game ({game.game_id}) {game.game_name}")
                    self.game_data[game.game_id] = GameData(game, {})
                except Exception as e:
                    logger.critical(
                        f"Failed creating game ({game.game_id}) {game.current_tick} with error: " + str(e))
                    continue

            try:

                async with database.transaction():
                    await database.execute(
                        f"LOCK TABLE orders, players IN SHARE ROW EXCLUSIVE MODE")

                    await self.run_game_tick(game)

            except Exception as e:
                logger.critical(
                    f"({game.game_id}) {game.game_name} tick {game.current_tick} failed with error: " + str(e))

    async def run_game_tick(self, game: Game):
        logger.debug(
            f"({game.game_id}) {game.game_name}: {game.current_tick} tick")
        tick_data = await self.get_tick_data(game)
        tick_data = self.run_markets(tick_data)
        tick_data = self.run_power_plants(tick_data)
        tick_data, energy_sold = self.run_electricity_market(
            tick_data, self.game_data[game.game_id].energy_market)
        await self.save_electricity_orders(
            game, tick_data.players, energy_sold, game.current_tick)

        await self.save_tick_data(tick_data)
        await Game.update(game_id=game.game_id, current_tick=game.current_tick + 1)

        await self.run_bots(tick_data)

    async def get_tick_data(self, game: Game) -> TickData:
        players = {
            player.player_id: player
            for player in await Player.list(game_id=game.game_id)
        }

        pending_orders = await Order.list(game_id=game.game_id, order_status=OrderStatus.PENDING)
        user_cancelled_orders = await Order.list(game_id=game.game_id, order_status=OrderStatus.USER_CANCELLED)
        dataset_row = await DatasetData.get(dataset_id=game.dataset_id, tick=game.current_tick)
        markets = self.game_data[game.game_id].markets

        tick_data = TickData(
            game=game,
            players=players,
            markets=markets,
            bots=self.game_data[game.game_id].bots,
            pending_orders=pending_orders,
            user_cancelled_orders=user_cancelled_orders,
            dataset_row=dataset_row
        )

        return tick_data

    def run_markets(self, tick_data: TickData):
        updated_orders = {}

        for order in tick_data.user_cancelled_orders:
            game_data = self.game_data[tick_data.game.game_id]
            market = game_data.markets[order.resource.value]

            updated = market.cancel(order)
            updated_orders.update(updated)

        for order in tick_data.pending_orders:
            game_data = self.game_data[tick_data.game.game_id]
            market = game_data.markets[order.resource.value]

            updated = market.match(order, tick_data.game.current_tick)
            updated_orders.update(updated)

        tick_data.updated_orders.update(updated_orders)

        return tick_data

    def run_power_plants(self, tick_data: TickData):

        for player_id in tick_data.players.keys():
            player = tick_data.players[player_id]

            player.energy = 0

            for type in PowerPlantType:
                to_consume = player[type.name.lower() + "_plants_powered"]

                if not type.is_renewable():
                    to_consume = min(to_consume, player[type.name.lower()])
                    player[type.name.lower()] -= to_consume

                player.energy += to_consume * type.get_produced_energy(
                    tick_data.dataset_row)

        return tick_data

    def run_electricity_market(self, tick_data: TickData, energy_market: EnergyMarket) -> Tuple[TickData, dict[int, int]]:
        energy_sold = energy_market.match(
            tick_data.players, tick_data.dataset_row.energy_demand, tick_data.dataset_row.max_energy_price)

        return tick_data, energy_sold

    async def save_electricity_orders(self, players: dict[int, Player], game: Game, energy_sold: dict[int, int], tick: int):
        for player_id, energy in energy_sold.items():
            await Order.create(
                game_id=game.game_id,
                player_id=player_id,
                order_type=OrderType.LIMIT,
                order_side=OrderSide.SELL,
                timestamp=pd.Timestamp.now(),
                order_status=OrderStatus.COMPLETED,
                price=players[player_id].energy_price,
                size=energy,
                tick=tick,
                filled_size=energy,
                filled_money=players[player_id].energy_price * energy,
                filled_price=players[player_id].energy_price,
                expiration_tick=tick,
                resource=Resource.energy.value
            )

    async def save_tick_data(self, tick_data: TickData):
        for player in tick_data.players.values():
            await Player.update(**dataclasses.asdict(player))

        for order in tick_data.updated_orders.values():
            await Order.update(**dataclasses.asdict(order))

    async def run_bots(self, tick_data: TickData):
        bots = self.game_data[tick_data.game.game_id].bots

        for bot in bots:
            await bot.run(tick_data)
