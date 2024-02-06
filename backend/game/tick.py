from datetime import datetime
from db import database
from db import Player, PowerPlant, Game, PowerPlantType, Order
from db.model.order_types import OrderStatus
from . import energy_service
from game.market import Market, Resource
from config import config


async def run_all_game_ticks():
    markets = {}

    games = await Game.list()

    for game in games:
        if game.is_finished:
            continue

        if datetime.now() < game.start_time:
            continue

        if game.current_tick >= game.total_ticks:
            await Game.update(game_id=game.game_id, is_finished=True)
            continue

        if game.game_id not in markets:
            markets[game.game_id] = {
                resource.value: Market(resource.value, game.game_id) for resource in Resource
            }

        async with database.transaction():
            await tick_game_with_db(game, markets[game.game_id])


async def tick_game_with_db(game: Game, markets: dict[int, Market]):
    # Dohvacanje stanja iz baze
    players = await Player.list(game_id=game.game_id)
    new_orders = await Order.list(game_id=game.game_id, order_status=OrderStatus.PENDING.value)
    cancelled_orders = await Order.list(game_id=game.game_id, order_status=OrderStatus.CANCELLED.value)
    power_plants = dict()
    for player in players:
        power_plants[player.player_id] = await PowerPlant.list(player_id=player.player_id)
    
    tick_game(TickData(game=game,
                       players=players,
                       new_orders=new_orders,
                       cancelled_orders=cancelled_orders,
                       power_plants=power_plants,
                       markets=markets))

    for market in markets:
        for order in market.updated_orders.values():
            await Order.update(order.get_kwargs())
    for player in players:
        Player.update(player.get_kwargs())
        for power_plant in power_plants[player.player_id]:
            PowerPlant.update(power_plant.get_kwargs())
    await Game.update(game_id=game.game_id, current_tick=game.current_tick + 1)


class TickData:
    game: Game
    players: list[Player]
    new_orders: list[Order]
    cancelled_orders: list[Order]
    power_plants: dict[int, PowerPlant]
    markets: list[Market]


def tick_game(tick_data: TickData):
    game = tick_data.game
    players = tick_data.players
    power_plants = tick_data.power_plants
    markets = tick_data.markets

    # Update markets
    player_dict = {player.player_id: player for player in players}
    for market in markets:
        market.begin_tick(player_dict)

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
        market.orderbook.match()


def update_energy_and_power_plants(game: Game, player: Player, power_plants: dict[int, PowerPlantType]):
    player.energy = 0
    for power_plant in power_plants[player.player_id]:
        plant_type = PowerPlantType(power_plant.type)
        resources = player[plant_type.get_name()]
        if power_plant.temperature==1 and power_plant.powered_on:
            resources_per_tick = config["power_plant"]["resources_per_tick"]
            if plant_type.is_renewable():
                player.energy += energy_service.get_produced_renewable_energy(game.dataset, game.current_tick, plant_type)
            elif resources > resources_per_tick:
                player.energy += energy_service.get_produced_energy(game.dataset, game.current_tick, plant_type)
                resources -= resources_per_tick
            else:
                power_plant.powered_on = False
        power_plant.temperature = plant_type.get_new_temp(power_plant.temperature,
                                                        power_plant.powered_on)