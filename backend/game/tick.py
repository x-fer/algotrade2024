from datetime import datetime
from db import database
from db import Player, PowerPlant, Game, PowerPlantType
from game.market import Market, Resource

# provjeri jel igra runna

# matchaj ordere

# temperature elektrana

# trosenje energenata u elektranama

# generiranje energije

# svaki 10-ti tick provjeri jel svi ispunjavaju ugovore i plati, inace fee

# increment current tick


async def tick_game(game: Game, markets: list[Market]):
    players = await Player.list(game_id=game.game_id)

    for player in players:
        power_plants = await PowerPlant.list(player_id=player.player_id)

        for power_plant in power_plants:
            plant_type = PowerPlantType(power_plant.type)

            new_t = plant_type.update_temp(power_plant.temperature,
                                           power_plant.powered_on)

            await PowerPlant.update(power_plant_id=power_plant.power_plant_id,
                                    temperature=new_t)

    for market in markets:
        # TODO: match!
        pass


async def run_all_game_ticks():
    markets = {}

    async with database.transaction():
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
                markets[game.game_id] = [
                    Market(resource.value, game.game_id) for resource in Resource]

                # TODO: add active orders to market, regenerate state

            await tick_game(game, markets[game.game_id])
            await Game.update(game_id=game.game_id, current_tick=game.current_tick + 1)

        print("Running all game ticks")
