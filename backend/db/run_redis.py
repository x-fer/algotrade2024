import asyncio
from datetime import datetime, timedelta
import os
from typing import List
import psutil
from redis_om import Field, HashModel, Migrator
from db.fill_datasets import fill_datasets
from game.tick.ticker import Ticker
from model import Game, Team, Order, Player, DatasetData, Datasets
from config import config
from logger import logger


def drop_tables():
    pipe = DatasetData.db().pipeline()
    logger.info("Deleting tables")
    for cls in [DatasetData, Datasets, Order, Team, Game, Player]:
        try:
            cls.delete_many(cls.find().all(), pipe)
        except Exception:
            logger.warning(f"Class {cls.__name__} probably changed in model")
            for pk in cls.all_pks():
                cls.delete(pk, pipe)
    pipe.execute()


def create_teams_and_games():
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
        Team.team_name == bots_team_name,
        Team.team_secret == bots_team_secret,
    ).count() > 0:
        logger.info("Bots team already created")
    else:
        logger.info("Creating bots team")
        Team(
            team_name=bots_team_name,
            team_secret=bots_team_secret,
        ).save()

    logger.info("Getting all pks for datasets")
    datasets: List[Datasets] = Datasets.find().all()
    assert len(datasets) > 0

    logger.info("Creating games")
    games = [
        Game(
            game_name="Stalna igra",
            is_contest=int(False),
            dataset_id=datasets[0].dataset_id,
            start_time=datetime.now() + timedelta(milliseconds=3000),
            total_ticks=2300,
            tick_time=3000
        ),
        Game(
            game_name="Natjecanje",
            is_contest=int(True),
            dataset_id=datasets[1].dataset_id,
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
