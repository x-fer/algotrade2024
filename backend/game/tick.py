from dataclasses import dataclass, field
from datetime import datetime
from db import database
from model import Player, PowerPlant, Game, Order, OrderStatus, Resource, Team
from model import Market as MarketTable
from game.power_plants import update_energy_and_power_plants
from game.market import Market
from game.bots import Bots, Bot
from config import config


class GameData:
    def __init__(self, game: Game):
        self.markets: dict[int, Market] = {
            resource.value: Market(resource.value, game.game_id) for resource in Resource
        }
        self.bots = Bots.create_bots(game.bots)


async def run_all_game_ticks():
    games = dict()
    bot_team = await Team.get(team_name=config["bots"]["team_name"])
    bot_team_id = bot_team.team_id

    for game in await Game.list():
        print(f"{game.current_tick} tick {game.game_name}")
        if game.is_finished:
            continue

        if datetime.now() < game.start_time:
            continue

        if game.current_tick >= game.total_ticks:
            await Game.update(game_id=game.game_id, is_finished=True)
            continue

        if game.game_id not in games:
            game_data = await create_game(game, bot_team_id)
            if game_data is not None:
                games[game.game_id] = game_data

        async with database.transaction():
            await tick_game_with_db(game, games[game.game_id])


async def create_game(game: Game, bot_team_id: int):
    game_data = GameData(game)
    for i, bot in enumerate(game_data.bots):
        bot_name = f"{type(bot).__name__}_{i}"
        try:
            bot.player_id = await Player.create(
                player_name=bot_name,
                game_id=game.game_id,
                team_id=bot_team_id
            )
        except:
            bot.player_id = (await Player.get(
                player_name=bot_name,
                game_id=game.game_id,
                team_id=bot_team_id
            )).player_id
    return game_data


async def tick_game_with_db(game: Game, game_data: GameData):
    # Dohvacanje stanja iz baze
    players = await Player.list(game_id=game.game_id)
    new_orders = await Order.list(game_id=game.game_id, order_status=OrderStatus.PENDING)
    cancelled_orders = await Order.list(game_id=game.game_id, order_status=OrderStatus.CANCELLED)
    power_plants = dict()
    for player in players:
        power_plants[player.player_id] = await PowerPlant.list(player_id=player.player_id)

    # Dohvacanje in ram podataka
    markets = game_data.markets
    bots = game_data.bots

    # Tick
    tick_data = TickData(
        game=game,
        players=players,
        new_orders=new_orders,
        cancelled_orders=cancelled_orders,
        power_plants=power_plants,
        markets=markets,
        bots=bots
        )
    tick_game(tick_data)

    # Spremanje stanje u bazu
    for market in markets.values():
        for order in market.updated_orders.values():
            await Order.update(order.get_kwargs())
        await MarketTable.create(game_id=game.game_id,
                                 tick=game.current_tick,
                                 resource=market.resource,
                                 low=market.price_tracker.get_low(),
                                 high=market.price_tracker.get_high(),
                                 open=market.price_tracker.get_open(),
                                 close=market.price_tracker.get_close(),
                                 market=market.price_tracker.get_market()
                                 )
    for bot_order in tick_data.bot_orders:
        await Order.create(**bot_order.get_kwargs())
    for player in players:
        await Player.update(**player.get_kwargs())
        for power_plant in power_plants[player.player_id]:
            await PowerPlant.update(**power_plant.get_kwargs())
    await Game.update(game_id=game.game_id, current_tick=game.current_tick + 1)


@dataclass
class TickData:
    game: Game
    players: list[Player]
    new_orders: list[Order]
    cancelled_orders: list[Order]
    power_plants: dict[int, PowerPlant]
    markets: dict[int, Market]
    bots: list[Bot]
    bot_orders: list[Order] = field(default_factory=list)


def tick_game(tick_data: TickData):
    game = tick_data.game
    players = tick_data.players
    power_plants = tick_data.power_plants
    markets = tick_data.markets

    # Update markets
    player_dict = {player.player_id: player for player in players}
    for market in markets.values():
        market.set_players(player_dict)

    # Power plants and energy
    for player in players:
        update_energy_and_power_plants(game, player, power_plants)

    # Add new orders
    for order in tick_data.new_orders:
        markets[order.resource].orderbook.add_order(order)
    for order in tick_data.cancelled_orders:
        markets[order.resource].orderbook.cancel_order(order)

    # Match orders
    for market in markets.values():
        market.orderbook.match(game.current_tick)
