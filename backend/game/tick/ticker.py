import asyncio
import sys
import traceback
from datetime import datetime, timedelta
from pprint import pprint
from typing import Dict, Tuple
import pandas as pd
from model import Player, PowerPlantType, Game, Order, OrderStatus, Resource, DatasetData, OrderSide, OrderType
from game.market import ResourceMarket, EnergyMarket
from game.bots import Bots
from model.market import Market
from .tick_data import TickData
from logger import logger
from db import database


class GameData:
    def __init__(self, game: Game, players: Dict[int, Player]):
        self.markets: Dict[int, ResourceMarket] = {
            resource.value: ResourceMarket(resource, players)
            for resource in Resource
        }
        self.energy_market = EnergyMarket()
        self.bots = Bots.create_bots("resource_bot:1")


class Ticker:
    def __init__(self):
        self.game_data: Dict[int, GameData] = {}
        self.game_futures: Dict[int, asyncio.Future] = {}

    async def run_tick_manager(self, iters=None):
        for i in range(iters or sys.maxsize):
            games = await Game.list()

            for game in games:
                if game.is_finished:
                    continue

                if datetime.now() < game.start_time:
                    continue

                if not game.game_id in self.game_data:
                    await self.start_game(game)
                    continue

            await asyncio.sleep(0.1)

    async def end_game(self, game: Game):
        try:
            logger.info(
                f"Ending game ({game.game_id}) {game.game_name}")
            await Game.update(game_id=game.game_id, is_finished=True)
            if self.game_data.get(game.game_id) is not None:
                del self.game_data[game.game_id]
                self.game_futures[game.game_id].cancel()

        except Exception as e:
            logger.critical(
                f"Failed ending game ({game.game_id}) (tick {game.current_tick}) with error:\n{traceback.format_exc()}")

    async def start_game(self, game: Game):
        try:
            logger.info(
                f"Starting game ({game.game_id}) {game.game_name}")

            await self.delete_all_running_bots(game.game_id)

            self.game_data[game.game_id] = GameData(game, {})
            self.game_futures[game.game_id] = asyncio.create_task(
                self.run_game(game), name=f"game_{game.game_id}")

        except Exception as e:
            logger.critical(
                f"Failed creating game ({game.game_id}) (tick {game.current_tick}) with error:\n{traceback.format_exc()}")

    async def run_game(self, game: Game, iters=None):
        for i in range(iters or sys.maxsize):
            game = await Game.get(game_id=game.game_id)
            try:
                if game.current_tick >= game.total_ticks:
                    await self.end_game(game)
                    return

                # wait until the tick should start
                should_start = game.start_time + \
                    timedelta(milliseconds=game.current_tick *
                              game.tick_time)

                to_wait = max(
                    0, (should_start - datetime.now()).total_seconds())

                if to_wait < 0.1:
                    logger.warning(
                        f"({game.game_id}) {game.game_name} has short waiting time: {to_wait}, catching up or possible overload")

                await asyncio.sleep(to_wait)

                # run the tick
                async with database.transaction():
                    await database.execute(
                        f"LOCK TABLE orders, players IN SHARE ROW EXCLUSIVE MODE")

                    await self.run_game_tick(game)

            except Exception as e:
                logger.critical(
                    f"({game.game_id}) {game.game_name} (tick {game.current_tick}) failed with error:\n{traceback.format_exc()}")

    async def delete_all_running_bots(self, game_id: int):
        bots = await Player.list(game_id=game_id, is_bot=True)

        for bot in bots:
            await Player.update(player_id=bot.player_id, is_active=False)

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
        await self.save_market_data(tick_data)
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
        for resource in Resource:
            market = tick_data.markets[resource.value]
            filtered_orders = list(filter(
                lambda order: order.resource.value == resource.value, tick_data.user_cancelled_orders))

            updated = market.cancel(
                filtered_orders)

            tick_data.updated_orders.update(updated)

        for resource in Resource:
            market = tick_data.markets[resource.value]
            filtered_orders = list(filter(
                lambda order: order.resource.value == resource.value, tick_data.pending_orders))

            updated = market.match(
                filtered_orders, tick_data.game.current_tick)

            tick_data.updated_orders.update(updated)

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

    def run_electricity_market(self, tick_data: TickData, energy_market: EnergyMarket) -> Tuple[TickData, Dict[int, int]]:
        energy_sold = energy_market.match(
            tick_data.players, tick_data.dataset_row.energy_demand, tick_data.dataset_row.max_energy_price)

        return tick_data, energy_sold

    async def save_electricity_orders(self, players: Dict[int, Player], game: Game, energy_sold: Dict[int, int], tick: int):
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
        await Player.update_many(tick_data.players.values())
        await Order.update_many(tick_data.updated_orders.values())
        for bot in tick_data.bots:
            await Player.update(player_id=bot.player_id, money=int(1e9))

    async def save_market_data(self, tick_data: TickData):
        tick = tick_data.game.current_tick
        game_id = tick_data.game.game_id

        for resource in Resource:
            await Market.create(
                game_id=game_id,
                tick=tick,
                resource=resource.value,
                low=tick_data.markets[resource.value].price_tracker.get_low(),
                high=tick_data.markets[resource.value].price_tracker.get_high(
                ),
                open=tick_data.markets[resource.value].price_tracker.get_open(
                ),
                close=tick_data.markets[resource.value].price_tracker.get_close(
                ),
                market=tick_data.markets[resource.value].price_tracker.get_average(
                ),
                volume=tick_data.markets[resource.value].price_tracker.get_volume(
                )
            )

    async def run_bots(self, tick_data: TickData):
        bots = self.game_data[tick_data.game.game_id].bots

        for bot in bots:
            await bot.run(tick_data)
