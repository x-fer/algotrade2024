import asyncio
from contextlib import ExitStack
from itertools import chain
from operator import attrgetter, methodcaller
import sys
import traceback
from datetime import datetime, timedelta
from typing import Dict, Iterator, List, Tuple

from pyinstrument import Profiler
from game.bots.bot import Bot
from game.bots.resource_bot import ResourceBot
from model import Player, PowerPlantType, Game, Order, OrderStatus, Resource, DatasetData, OrderSide
from game.market import ResourceMarket, EnergyMarket
from game.bots import Bots
from model.market import Market
from model.resource import Energy
from .tick_data import TickData
from logger import logger
from redlock.lock import RedLock


class GameData:
    def __init__(self, game: Game):
        self.markets: Dict[str, ResourceMarket] = {
            resource.value: ResourceMarket(resource, game.game_id)
            for resource in Resource
        }
        self.energy_market = EnergyMarket()
        self.bot: Bot = ResourceBot()


class Ticker:
    def __init__(self):
        self.game_data: Dict[str, GameData] = {}
        self.game_futures: Dict[str, asyncio.Future] = {}
        self.tick_event = None

    async def run_tick_manager(self, iters=None, tick_event=None):
        for i in range(iters or sys.maxsize):
            games: List[Game] = Game.find().all()

            for game in games:
                if game.is_finished:
                    continue
                if game.start_time < datetime.now():
                    continue
                if game.game_id not in self.game_data:
                    await self.start_game(game, tick_event=None)
                    continue
            await asyncio.sleep(0.1)

    async def end_game(self, game: Game):
        try:
            logger.info(f"Ending game ({game.game_id}) {game.game_name}")
            # TODO: check if this works
            game.update(is_finished=True)
            if self.game_data.get(game.game_id) is not None:
                del self.game_data[game.game_id]
                self.game_futures[game.game_id].cancel()

        except Exception:
            logger.critical(
                f"Failed ending game ({game.game_id}) (tick {game.current_tick}) with error:\n{traceback.format_exc()}")

    async def start_game(self, game: Game, tick_event=None):
        self.tick_event = tick_event
        try:
            logger.info(
                f"Starting game ({game.game_id}) {game.game_name} with tick {game.current_tick}/{game.total_ticks}")

            self.delete_all_running_bots(game.game_id)

            self.game_data[game.game_id] = GameData(game)

            self.load_previous_oderbook(game.game_id)

            self.game_futures[game.game_id] = asyncio.create_task(
                self.run_game(game), name=f"game_{game.game_id}")

        except Exception:
            logger.critical(
                f"Failed creating game ({game.game_id}) (tick {game.current_tick}) with error:\n{traceback.format_exc()}")

    async def run_game(self, game: Game, iters=None):
        for i in range(iters or sys.maxsize):
            game = Game.get(game.game_id)
            try:
                if self.tick_event is not None:
                    await self.tick_event.wait()
                    self.tick_event.clear()

                if game.current_tick >= game.total_ticks:
                    await self.end_game(game)
                    return

                # wait until the tick should start
                should_start = game.start_time + \
                    timedelta(milliseconds=game.current_tick *
                              game.tick_time)

                to_wait = max(
                    0, (should_start - datetime.now()).total_seconds())

                if to_wait < 0.1 and game.current_tick > 0:
                    logger.warning(
                        f"({game.game_id}) {game.game_name} has short waiting time: {to_wait}s in tick ({game.current_tick}), catching up or possible overload")

                await asyncio.sleep(to_wait)
                
                start_time = datetime.now()
                with ExitStack() as stack:
                    for player_lock in self.get_player_locks(game):
                        stack.enter_context(player_lock)
                    self.run_game_tick(game)
                interval = (datetime.now() - start_time).total_seconds()
                logger.info(
                    f"{interval:.6} Ticking game ({game.game_id}) {game.game_name} with tick {game.current_tick}/{game.total_ticks}")

            except Exception:
                logger.critical(
                    f"({game.game_id}) {game.game_name} (tick {game.current_tick}) failed with error:\n{traceback.format_exc()}")
                await asyncio.sleep(0.5)
    
    def get_player_locks(self, game: Game) -> Iterator[RedLock]:
        players = Player.find(Player.game_id == game.game_id).all()
        return list(map(methodcaller('lock'), players))

    def load_previous_oderbook(self, game_id: str):
        # in case of restart these need to be reloaded
        # IN_QUEUE = "IN_QUEUE"
        # ACTIVE = "ACTIVE"
        orders: List[Order] = Order.find(
            Order.game_id == game_id,
            Order.order_status == OrderStatus.IN_QUEUE.value).all()
        orders += Order.find(
            Order.game_id==game_id,
            Order.order_status==OrderStatus.ACTIVE.value).all()
        for order in orders:
            markets = self.game_data[game_id].markets
            markets[order.resource.value].orderbook.add_order(order)

    def delete_all_running_bots(self, game_id: int):
        bots = Player.find(
            (Player.game_id==game_id) & 
            (Player.is_bot==int(True))
        ).all()

        for bot in bots:
            bot.update(is_active=False)
        
        Order.delete_many(
            Order.find(Order.game_id==game_id).all()
        )

    def run_game_tick(self, game: Game):
        # profiler =  Profiler()
        # profiler.start()

        self.pipe = Order.db().pipeline()

        tick_data = self.get_tick_data(game)

        tick_data = self.run_markets(tick_data)

        tick_data = self.run_power_plants(tick_data)    

        tick_data, energy_sold = self.run_electricity_market(
            tick_data, self.game_data[game.game_id].energy_market)

        self.save_electricity_orders(
            game, tick_data.players, energy_sold, game.current_tick)

        self.save_tick_data(tick_data)
        self.save_market_data(tick_data)
        game.current_tick += 1
        game.save(self.pipe)
        self.game_data[tick_data.game.game_id].bot.run(self.pipe, tick_data)

        self.pipe.execute()

        # profiler.stop()
        # profiler.print()

    def get_tick_data(self, game: Game) -> TickData:
        players = {
            player.player_id: player
            for player in Player.find(Player.game_id==game.game_id).all()
        }

        pending_orders = Order.find(
            Order.game_id==game.game_id,
            Order.order_status==OrderStatus.PENDING.value).all()
        print("Pending orders", len(pending_orders))
        user_cancelled_orders = Order.find(
            Order.game_id==game.game_id,
            Order.order_status==OrderStatus.USER_CANCELLED.value).all()
        dataset_row = DatasetData.find(
            DatasetData.dataset_id==game.dataset_id,
            DatasetData.tick==game.current_tick).first()
        markets = self.game_data[game.game_id].markets

        tick_data = TickData(
            game=game,
            players=players,
            markets=markets,
            energy_market=self.game_data[game.game_id].energy_market,
            bots=[self.game_data[game.game_id].bot], #TODO pretvoriti u jednog bota
            pending_orders=pending_orders,
            user_cancelled_orders=user_cancelled_orders,
            dataset_row=dataset_row
        )
        return tick_data

    def run_markets(self, tick_data: TickData) -> TickData:
        for resource in tick_data.markets.keys():
            market = tick_data.markets[resource]
            market.set_players(tick_data.players)

        for resource in tick_data.markets.keys():
            market = tick_data.markets[resource]
            canceled_resource_orders = list(filter(
                lambda order: order.resource.value == resource, tick_data.user_cancelled_orders))

            updated = market.cancel(
                canceled_resource_orders)

            tick_data.updated_orders.update(updated)

        for resource in tick_data.markets.keys():
            market = tick_data.markets[resource]
            pending_resource_orders = list(filter(
                lambda order: order.resource.value == resource, tick_data.pending_orders))

            updated = market.match(
                pending_resource_orders, tick_data.game.current_tick)

            tick_data.updated_orders.update(updated)

        # tick_data.tick_trades = []
        for market in tick_data.markets.values():
            tick_data.tick_trades.extend(
                market.get_last_tick_trades())
        # tick_data.tick_trades = list(map(
        #     TradeDb.from_trade, tick_data.tick_trades))

        return tick_data

    def run_power_plants(self, tick_data: TickData) -> TickData:
        for player_id in tick_data.players.keys():
            player = tick_data.players[player_id]

            player.energy = 0

            for type in PowerPlantType:
                to_consume = player.power_plants_powered[type]

                if not type.is_renewable():
                    to_consume = min(to_consume, player.resources[type])
                    player.resources[type] -= to_consume
                player.energy += to_consume * tick_data.dataset_row.power_plants_output[type]

        return tick_data

    def run_electricity_market(self, tick_data: TickData,
                               energy_market: EnergyMarket
                               ) -> Tuple[TickData, Dict[int, int]]:
        energy_sold = energy_market.match(
            tick_data.players, tick_data.dataset_row.energy_demand,
            tick_data.dataset_row.max_energy_price)
        return tick_data, energy_sold

    def save_electricity_orders(self, game: Game, players: Dict[int, Player],
                                      energy_sold: Dict[int, int], tick: int):
        electricity_orders = []
        # pipe = Order.db().pipeline()
        for player_id, energy in energy_sold.items():
            Order(
                game_id=game.game_id,
                player_id=player_id,
                order_side=OrderSide.SELL,
                timestamp=datetime.now(),
                order_status=OrderStatus.COMPLETED,
                price=players[player_id].energy_price,
                size=energy,
                tick=tick,
                filled_size=energy,
                filled_money=players[player_id].energy_price * energy,
                filled_price=players[player_id].energy_price,
                expiration_tick=tick,
                resource=Energy.energy.value
            ).save(self.pipe)

    def save_tick_data(self, tick_data: TickData):
        # pipe = Player.db().pipeline()
        # for order in tick_data.players.values():
        #     order.save(self.pipe)
        list(map(methodcaller('save', self.pipe), tick_data.players.values()))
        # for order in tick_data.updated_orders.values():
        #     order.save(self.pipe)
        # pipe.execute()
        list(map(methodcaller('save', self.pipe), tick_data.updated_orders.values()))
        
        # TradeDb.create_many(tick_data.tick_trades)

    def save_market_data(self, tick_data: TickData):
        tick = tick_data.game.current_tick
        game_id = tick_data.game.game_id

        # pipe = Market.db().pipeline()
        for resource, market in chain(
                tick_data.markets.items(),
                [(Energy.ENERGY.value, tick_data.energy_market)]):
            price_tracker = market.price_tracker
            Market(
                game_id=game_id,
                tick=tick,
                resource=resource,
                low=price_tracker.get_low(),
                high=price_tracker.get_high(),
                open=price_tracker.get_open(),
                close=price_tracker.get_close(),
                market=price_tracker.get_average(),
                volume=price_tracker.get_volume()
            ).save(self.pipe)
