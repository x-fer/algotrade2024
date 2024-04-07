from datetime import datetime, timedelta
from redis_om import Field, HashModel, Migrator
from db.fill_datasets import fill_datasets
from model import Game, Team, Order, Player, DatasetData, Datasets
from config import config
from logger import logger

Migrator().run()

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

fill_datasets()

datasets = list(Datasets.all_pks())
assert len(datasets) > 0

logger.info("Creating games")
games = [
    Game(
        game_name="Stalna igra",
        is_contest=False,
        dataset_id=datasets[0],
        start_time=datetime.now() + timedelta(milliseconds=3000),
        total_ticks=2300,
        tick_time=3000
    ),
    Game(
        game_name="Natjecanje",
        is_contest=True,
        dataset_id=datasets[1],
        start_time=datetime.now() + timedelta(milliseconds=5000),
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