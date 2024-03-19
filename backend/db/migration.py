import os
import pandas as pd
from db.db import database
from model import Team, Player, Game, Datasets, DatasetData
from datetime import datetime, timedelta
from config import config
from logger import logger


async def fill_tables():
    g_team_id = await Team.create(team_name="Goranov_tim", team_secret="gogi")
    k_team_id = await Team.create(team_name="Krunov_tim", team_secret="kruno")
    z_team_id = await Team.create(team_name="Zvonetov_tim", team_secret="zvone")

    datasets = await Datasets.list()

    dataset_id = datasets[0].dataset_id

    not_nat_game_id = await Game.create(
        game_name="Stalna igra",
        is_contest=False,
        dataset_id=dataset_id,
        start_time=datetime.now() + timedelta(milliseconds=3000),
        total_ticks=2300,
        tick_time=5000)
    nat_game_id = await Game.create(
        game_name="Natjecanje",
        is_contest=True,
        dataset_id=dataset_id,
        start_time=datetime.now() + timedelta(milliseconds=5000),
        total_ticks=100,
        tick_time=1000)

    for game_id in [not_nat_game_id, nat_game_id]:
        await Player.create(player_name="Goran", is_active=True, is_bot=False, game_id=game_id, team_id=g_team_id, money=350000, coal=1000)
        await Player.create(player_name="Kruno", is_active=True, is_bot=False, game_id=game_id, team_id=k_team_id, money=350000, coal=1000)
        await Player.create(player_name="Zvone", is_active=True, is_bot=False, game_id=game_id, team_id=z_team_id, money=350000, coal=1000)

    logger.info("Filled database with dummy data")


async def delete_tables():
    await database.execute('TRUNCATE orders, players, games, teams, market, datasets, dataset_data CASCADE')


async def drop_tables():
    for table_name in ["orders", "players", "games", "teams", "market", "datasets", "dataset_data"]:
        await database.execute(f'DROP TABLE IF EXISTS {table_name} CASCADE')


async def run_migrations():
    logger.info("Running migration script")
    await database.execute('''
              CREATE TABLE IF NOT EXISTS teams (
              team_id SERIAL PRIMARY KEY,
              team_name TEXT,
              team_secret TEXT UNIQUE
              )''')

    await database.execute('CREATE INDEX CONCURRENTLY team_secret_idx ON teams (team_secret);')

    await database.execute('''
                CREATE TABLE IF NOT EXISTS datasets (
                dataset_id SERIAL PRIMARY KEY,
                dataset_name TEXT,
                dataset_description TEXT
                )''')

    await database.execute('''
              CREATE TABLE IF NOT EXISTS games (
              game_id SERIAL PRIMARY KEY,
              game_name TEXT,
              is_contest BOOLEAN NOT NULL,
              dataset_id INT,
              start_time TIMESTAMP NOT NULL,
              total_ticks INT NOT NULL,
              tick_time INT NOT NULL,
              is_finished BOOLEAN NOT NULL DEFAULT false,
              current_tick INT NOT NULL DEFAULT 0,
              FOREIGN KEY (dataset_id) REFERENCES datasets(dataset_id)
              )''')

    await database.execute('''
              CREATE TABLE IF NOT EXISTS players (
              player_id SERIAL PRIMARY KEY,
              player_name TEXT,
              game_id INT NOT NULL,
              team_id INT NOT NULL,
              is_active BOOLEAN NOT NULL DEFAULT true,
              is_bot BOOLEAN NOT NULL DEFAULT false,
                           
              energy_price BIGINT NOT NULL DEFAULT 1e9,
              
              money BIGINT NOT NULL DEFAULT 0,
              energy BIGINT NOT NULL DEFAULT 0,
              coal BIGINT NOT NULL DEFAULT 0,
              uranium BIGINT NOT NULL DEFAULT 0,
              biomass BIGINT NOT NULL DEFAULT 0,
              gas BIGINT NOT NULL DEFAULT 0,
              oil BIGINT NOT NULL DEFAULT 0,
                           
              coal_plants_owned INT NOT NULL DEFAULT 0,
              uranium_plants_owned INT NOT NULL DEFAULT 0,
              biomass_plants_owned INT NOT NULL DEFAULT 0,
              gas_plants_owned INT NOT NULL DEFAULT 0,
              oil_plants_owned INT NOT NULL DEFAULT 0,
              geothermal_plants_owned INT NOT NULL DEFAULT 0,
              wind_plants_owned INT NOT NULL DEFAULT 0,
              solar_plants_owned INT NOT NULL DEFAULT 0,
              hydro_plants_owned INT NOT NULL DEFAULT 0,    
                           
              coal_plants_powered INT NOT NULL DEFAULT 0,
              uranium_plants_powered INT NOT NULL DEFAULT 0,
              biomass_plants_powered INT NOT NULL DEFAULT 0,
              gas_plants_powered INT NOT NULL DEFAULT 0,
              oil_plants_powered INT NOT NULL DEFAULT 0,
              geothermal_plants_powered INT NOT NULL DEFAULT 0,
              wind_plants_powered INT NOT NULL DEFAULT 0,
              solar_plants_powered INT NOT NULL DEFAULT 0,
              hydro_plants_powered INT NOT NULL DEFAULT 0,       
              
              FOREIGN KEY (game_id) REFERENCES games(game_id),
              FOREIGN KEY (team_id) REFERENCES teams(team_id)
              )''')

    await database.execute('''
                CREATE TABLE IF NOT EXISTS orders (
                order_id SERIAL PRIMARY KEY,
                game_id INT NOT NULL,
                player_id INT NOT NULL,
                order_type TEXT NOT NULL,
                order_side TEXT NOT NULL,
                order_status TEXT NOT NULL,
                price BIGINT NOT NULL,
                size BIGINT NOT NULL,
                tick INT NOT NULL,
                timestamp TIMESTAMP NOT NULL,
                expiration_tick INT NOT NULL,
                resource TEXT NOT NULL,
                           
                filled_size BIGINT NOT NULL DEFAULT 0,
                filled_money BIGINT NOT NULL DEFAULT 0,
                filled_price DOUBLE PRECISION NOT NULL DEFAULT 0,
                
                FOREIGN KEY (player_id) REFERENCES players(player_id),
                FOREIGN KEY (game_id) REFERENCES games(game_id)
                )''')

    await database.execute('''
              CREATE TABLE IF NOT EXISTS trades (
              trade_id SERIAL PRIMARY KEY,
            
              buy_order_id INT,
              sell_order_id INT,
              tick INT,

              filled_money BIGINT,
              filled_size BIGINT,
              filled_price BIGINT,

              FOREIGN KEY (buy_order_id) REFERENCES orders(order_id),
              FOREIGN KEY (sell_order_id) REFERENCES orders(order_id)
              )''')

    await database.execute('''
              CREATE TABLE IF NOT EXISTS market (
              game_id INT,
              tick INT,
              resource TEXT,
              low BIGINT,
              high BIGINT,
              open BIGINT,
              close BIGINT,
              market BIGINT,
              volume BIGINT,
              PRIMARY KEY (game_id, tick, resource)
              )''')

    await database.execute('CREATE INDEX CONCURRENTLY tick_idx ON market (tick);')

    await database.execute('''
                CREATE TABLE IF NOT EXISTS dataset_data (
                dataset_data_id SERIAL PRIMARY KEY,
                dataset_id INT NOT NULL,
                date TIMESTAMP NOT NULL,
                tick INT NOT NULL,
                coal BIGINT NOT NULL,
                uranium BIGINT NOT NULL,
                biomass BIGINT NOT NULL,
                gas BIGINT NOT NULL,
                oil BIGINT NOT NULL,
                coal_price BIGINT NOT NULL,
                uranium_price BIGINT NOT NULL,
                biomass_price BIGINT NOT NULL,
                gas_price BIGINT NOT NULL,
                oil_price BIGINT NOT NULL,
                geothermal BIGINT NOT NULL,
                wind BIGINT NOT NULL,
                solar BIGINT NOT NULL,
                hydro BIGINT NOT NULL,
                energy_demand BIGINT NOT NULL,
                max_energy_price BIGINT NOT NULL,
                FOREIGN KEY (dataset_id) REFERENCES datasets(dataset_id)
                )''')

    try:
        await Team.get(
            team_name=config["bots"]["team_name"],
            team_secret=config["bots"]["team_secret"]
        )
        logger.info("Bots team already created")
    except:
        logger.info("Creating bots team")
        await Team.create(
            team_name=config["bots"]["team_name"],
            team_secret=config["bots"]["team_secret"]
        )

    logger.info("Filling datasets")
    datasets_path = config["dataset"]["datasets_path"]
    for x in os.listdir(datasets_path):
        if not x.endswith(".csv"):
            continue
        try:
            await Datasets.get(dataset_name=x)
            logger.debug(f"Dataset {x} already created")
            continue
        except:
            pass

        df = pd.read_csv(f"{datasets_path}/{x}")

        # TODO: asserts, async transaction - ne zelimo da se dataset kreira ako faila kreiranje redaka
        dataset_id = await Datasets.create(dataset_name=x, dataset_description="Opis")

        price_multipliers = config["dataset"]["price_multiplier"]
        energy_output_multipliers = config["dataset"]["energy_output_multiplier"]
        energy_demand_multiplier = config["dataset"]["energy_demand_multiplier"]

        # date,COAL,URANIUM,BIOMASS,GAS,OIL,GEOTHERMAL,WIND,SOLAR,HYDRO,ENERGY_DEMAND,MAX_ENERGY_PRICE
        tick = 0
        dataset_data = []
        for index, row in df.iterrows():
            dataset_data.append(DatasetData(
                dataset_data_id=0,
                dataset_id=dataset_id,
                tick=tick,
                date=datetime.strptime(
                    row["date"], "%Y-%m-%d %H:%M:%S"),
                coal=(
                    energy_output_multipliers["coal"] *
                    row["COAL"] // 1_000_000),
                uranium=(
                    energy_output_multipliers["uranium"] *
                    row["URANIUM"] // 1_000_000),
                biomass=(
                    energy_output_multipliers["biomass"] *
                    row["BIOMASS"] // 1_000_000),
                gas=(
                    energy_output_multipliers["gas"] *
                    row["GAS"] // 1_000_000),
                oil=(
                    energy_output_multipliers["oil"] *
                    row["OIL"] // 1_000_000),
                geothermal=(
                    energy_output_multipliers["geothermal"] *
                    row["GEOTHERMAL"] // 1_000_000),
                wind=(
                    energy_output_multipliers["wind"] *
                    row["WIND"] // 1_000_000),
                solar=(
                    energy_output_multipliers["solar"] *
                    row["SOLAR"] // 1_000_000),
                hydro=(
                    energy_output_multipliers["hydro"] *
                    row["HYDRO"] // 1_000_000),
                energy_demand=(
                    energy_demand_multiplier *
                    row["ENERGY_DEMAND"] // 1_000_000),
                max_energy_price=(
                    price_multipliers["energy"] *
                    row["MAX_ENERGY_PRICE"] // 1_000_000),
                coal_price=(
                    price_multipliers["coal"] *
                    row["COAL_PRICE"] // 1_000_000),
                uranium_price=(
                    price_multipliers["uranium"] *
                    row["URANIUM_PRICE"] // 1_000_000),
                biomass_price=(
                    price_multipliers["biomass"] *
                    row["BIOMASS_PRICE"] // 1_000_000),
                gas_price=(
                    price_multipliers["gas"] *
                    row["GAS_PRICE"] // 1_000_000),
                oil_price=(
                    price_multipliers["oil"] *
                    row["OIL_PRICE"] // 1_000_000),
            ))
            tick += 1

        for x in dataset_data:
            assert x.coal_price > -config["bots"]["min_price"]
            assert x.uranium_price > -config["bots"]["min_price"]
            assert x.biomass_price > -config["bots"]["min_price"]
            assert x.gas_price > -config["bots"]["min_price"]
            assert x.oil_price > -config["bots"]["min_price"]

        await DatasetData.create_many(dataset_data)
        logger.info(f"Added dataset {x}")
    logger.info("Migrated database")
