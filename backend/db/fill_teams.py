from model import Team, Player, Game, Datasets
from datetime import datetime, timedelta
from config import config
from logger import logger


async def fill_bots():
    try:
        await Team.get(
            team_name=config["bots"]["team_name"],
            team_secret=config["bots"]["team_secret"],
        )
        logger.info("Bots team already created")
    except Exception:
        logger.info("Creating bots team")
        await Team.create(
            team_name=config["bots"]["team_name"],
            team_secret=config["bots"]["team_secret"],
        )


async def fill_dummy_tables():
    g_team_id = await Team.create(team_name="Goranov_tim", team_secret="gogi")
    k_team_id = await Team.create(team_name="Krunov_tim", team_secret="kruno")
    z_team_id = await Team.create(team_name="Zvonetov_tim", team_secret="zvone")
    m_team_id = await Team.create(team_name="Maja_tim", team_secret="maja")

    teams = [
        ("Goranov_tim", g_team_id),
        ("Krunov_tim", k_team_id),
        ("Zvonetov_tim", z_team_id),
        ("Maja_tim", m_team_id),
    ]

    datasets = await Datasets.list()

    not_nat_game_id = await Game.create(
        game_name="Stalna igra",
        is_contest=False,
        dataset_id=datasets[0].dataset_id,
        start_time=datetime.now() + timedelta(milliseconds=3000),
        total_ticks=2300,
        tick_time=1000,
    )
    # nat_game_id = await Game.create(
    #     game_name="Natjecanje",
    #     is_contest=True,
    #     dataset_id=datasets[1].dataset_id,
    #     start_time=datetime.now() + timedelta(milliseconds=5000),
    #     total_ticks=1800,
    #     tick_time=1000,
    # )

    games = [not_nat_game_id]
    for game_id in games:
        for team_name, team_id in teams:
            await Player.create(
                game_id=game_id,
                team_id=team_id,
                player_name=f"{team_name}_1",
                money=config["player"]["starting_money"],
            )

    logger.info("Filled database with dummy data")
