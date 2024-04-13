from model.game import Game
from model import Game, Team, Order, Player, DatasetData, Datasets
from operator import attrgetter
from pprint import pprint
from typing import List
from logger import logger
from datetime import datetime, timedelta
from config import config


if __name__ == "__main__":
    logger.info("Creating games")
    datasets: List[Datasets] = Datasets.find().all()
    datasets.sort(key=attrgetter("dataset_name"))
    assert len(datasets) > 0
    # pprint(datasets)
    # print("Creating First testing round")

    # for i, dataset in enumerate(datasets):
    #     dataset_id = dataset.dataset_id
    #     # print(dataset_id)
    #     dataset_data = DatasetData.find(DatasetData.dataset_id == dataset_id).all()
    #     print(i, dataset_id, len(dataset_data))



    games = [
        # Game(
        #     game_name="First contest round",
        #     is_contest=int(True),
        #     dataset_id=datasets[6].dataset_id,
        #     start_time=datetime.now() + timedelta(milliseconds=15*1000*60),
        #     total_ticks=1800,
        #     tick_time=1000
        # ),
        Game(
            game_name="Fifth normal round",
            is_contest=int(False),
            dataset_id=datasets[13].dataset_id,
            start_time=datetime.now() + timedelta(milliseconds=5000),
            total_ticks=5000,
            tick_time=3000
        ),
    ]
    for game in games:
        game.save()
        print(game.pk)

    # bots_team_name = config["bots"]["team_name"]
    # bots_team_secret = config["bots"]["team_secret"]
    # if Team.find(
    #     Team.team_name == bots_team_name,
    #     Team.team_secret == bots_team_secret,
    # ).count() > 0:
    #     logger.info("Bots team already created")
    # else:
    #     logger.info("Creating bots team")
    #     Team(
    #         team_name=bots_team_name,
    #         team_secret=bots_team_secret,
    #     ).save()
