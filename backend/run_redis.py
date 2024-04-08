import asyncio
from datetime import datetime, timedelta
import os
import psutil
from redis_om import Field, HashModel, Migrator
from db.fill_datasets import fill_datasets
from game.tick.ticker import Ticker
from model import Game, Team, Order, Player, DatasetData, Datasets
from config import config
from logger import logger

Migrator().run()

print("Old datasets", list(Datasets.find().all()))

logger.info("Deleting tables")
for cls in [DatasetData, Datasets, Order, Team, Game, Player]:
    for pk in cls.all_pks():
        cls.delete(pk)

logger.info("Creating teams")
teams = [
    Team(team_name="Goranov_tim", team_secret="gogi"),
    Team(team_name="Krunov_tim", team_secret="kruno"),
    Team(team_name="Zvonetov_tim", team_secret="zvone"),
    Team(team_name="Maja_tim", team_secret="maja")
]
for team in teams:
    team.save()


bots_team_name = config["bots"]["team_name"]
bots_team_secret = config["bots"]["team_secret"]
if Team.find(
    Team.team_name==bots_team_name,
    Team.team_secret==bots_team_secret,
    ).count() > 0:
    logger.info("Bots team already created")
else:
    logger.info("Creating bots team")
    Team(
        team_name=bots_team_name,
        team_secret=bots_team_secret,
    ).save()

fill_datasets()

datasets = list(Datasets.all_pks())
assert len(datasets) > 0

logger.info("Creating games")
games = [
    # Game(
    #     game_name="Stalna igra",
    #     is_contest=False,
    #     dataset_id=datasets[0],
    #     start_time=datetime.now() + timedelta(milliseconds=3000),
    #     total_ticks=2300,
    #     tick_time=3000
    # ),
    Game(
        game_name="Natjecanje",
        is_contest=True,
        dataset_id=datasets[1],
        start_time=datetime.now() + timedelta(milliseconds=3000),
        total_ticks=1800,
        tick_time=1000,
    )
]
for game in games:
    game.save()

logger.info("Creating players")
for game in games:
    for team in teams:
        Player(
            game_id=game.pk,
            team_id=team.pk,
            player_name=f"{team.team_name}_1",
            money=config["player"]["starting_money"],
        ).save()

logger.info("Filled database with dummy data")




tick_event = asyncio.Event()

async def run_game_ticks():
    parent_process = psutil.Process(os.getppid())
    children = parent_process.children(
        recursive=True)

    if config["in_tests"]:
        assert len(children) == 1

    if len(children) == 1 or children[1].pid == os.getpid():
        ticker = Ticker()

        if config["in_tests"]:
            await ticker.run_tick_manager(tick_event=tick_event)
        else:
            await ticker.run_tick_manager()

asyncio.run(run_game_ticks())