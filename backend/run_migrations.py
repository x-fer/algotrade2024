import asyncio
from datetime import datetime, timedelta
import os
import psutil
from redis_om import Field, HashModel, Migrator
from db.fill_datasets import fill_datasets
from db.run_redis import create_teams_and_games, drop_tables
from game.tick.ticker import Ticker
from model import Game, Team, Order, Player, DatasetData, Datasets
from config import config
from logger import logger


Migrator().run()


def run_all():
    if config["drop_tables"]:
        drop_tables()
    if config["fill_datasets"]:
        fill_datasets()
    if config["fill_tables"]:
        create_teams_and_games()


if __name__ == "__main__":
    run_all()
