import os
from databases import Database
import pandas as pd
from db.db import database
from model import Team, Player, PowerPlant, PowerPlantType, Game, Datasets, DatasetData
from datetime import datetime
from config import config


async def fill_tables():
    g_team_id = await Team.create(team_name="Goranov_tim", team_secret="gogi")
    k_team_id = await Team.create(team_name="Krunov_tim", team_secret="kruno")
    z_team_id = await Team.create(team_name="Zvonetov_tim", team_secret="zvone")

    # dataset_id = await Datasets.create(dataset_name="Dummy dataset", dataset_description="Opis")
    datasets = await Datasets.list()

    not_nat_game_id = await Game.create(game_name="Stalna igra", is_contest=False, bots="dummy:3", dataset_id=1, start_time=datetime.now(), total_ticks=2400, tick_time=3000)
    nat_game_id = await Game.create(game_name="Natjecanje", is_contest=True, bots="dummy:2", dataset_id=1, start_time=datetime.now(), total_ticks=10, tick_time=1000)

    for game_id in [not_nat_game_id, nat_game_id]:
        await Player.create(player_name="Goran", is_active=True, is_bot=False, game_id=game_id, team_id=g_team_id, money=15000, coal=1000)
        await Player.create(player_name="Kruno", is_active=True, is_bot=False, game_id=game_id, team_id=k_team_id)
        await Player.create(player_name="Zvone", is_active=True, is_bot=False, game_id=game_id, team_id=z_team_id)

    await PowerPlant.create(type=PowerPlantType.COAL, player_id=1, price=1, powered_on=True)

    print("Filled database with dummy data")


async def delete_tables():
    await database.execute('TRUNCATE power_plants, orders, players, games, teams, market, datasets, dataset_data CASCADE')


async def drop_tables():
    for table_name in ["power_plants", "orders", "players", "games", "teams", "market", "datasets", "dataset_data"]:
        await database.execute(f'DROP TABLE IF EXISTS {table_name} CASCADE')


async def run_migrations():
    await database.execute('''
              CREATE TABLE IF NOT EXISTS teams (
              team_id SERIAL PRIMARY KEY,
              team_name TEXT,
              team_secret TEXT UNIQUE
              )''')

    # dataset_id, dataset_name, dataset_path, dataset_description
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
              bots TEXT,
              dataset_id int,
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
                           
              energy_price INT NOT NULL DEFAULT 1e9,
              
              money INT NOT NULL DEFAULT 0,
              energy INT NOT NULL DEFAULT 0,
              coal INT NOT NULL DEFAULT 0,
              uranium INT NOT NULL DEFAULT 0,
              biomass INT NOT NULL DEFAULT 0,
              gas INT NOT NULL DEFAULT 0,
              oil INT NOT NULL DEFAULT 0,
              
              FOREIGN KEY (game_id) REFERENCES games(game_id),
              FOREIGN KEY (team_id) REFERENCES teams(team_id)
              )''')

    await database.execute('''
              CREATE TABLE IF NOT EXISTS power_plants (
              power_plant_id SERIAL PRIMARY KEY,
              type INT NOT NULL,
              player_id INT NOT NULL,
              price INT NOT NULL,
              powered_on BOOLEAN NOT NULL DEFAULT false,
              temperature REAL NOT NULL DEFAULT 0,
              FOREIGN KEY (player_id) REFERENCES players(player_id)
              )''')

    await database.execute('''
                CREATE TABLE IF NOT EXISTS orders (
                order_id SERIAL PRIMARY KEY,
                game_id INT NOT NULL,
                player_id INT NOT NULL,
                order_type INT NOT NULL,
                order_side INT NOT NULL,
                order_status INT NOT NULL,
                price INT NOT NULL,
                size INT NOT NULL,
                tick INT NOT NULL,
                timestamp TIMESTAMP NOT NULL,
                expiration_tick INT NOT NULL,
                resource INT NOT NULL,
                           
                filled_size INT NOT NULL DEFAULT 0,
                filled_money INT NOT NULL DEFAULT 0,
                filled_price INT NOT NULL DEFAULT 0,
                
                FOREIGN KEY (player_id) REFERENCES players(player_id),
                FOREIGN KEY (game_id) REFERENCES games(game_id)
                )''')

    # Remove duplicate primary key declarations
    await database.execute('''
              CREATE TABLE IF NOT EXISTS market (
              game_id INT,
              tick INT,
              resource INT,
              low INT,
              high INT,
              open INT,
              close INT,
              market INT,
              PRIMARY KEY (game_id, tick, resource)
              )''')

    await database.execute('''
                CREATE TABLE IF NOT EXISTS dataset_data (
                dataset_data_id SERIAL PRIMARY KEY,
                dataset_id INT NOT NULL,
                date TIMESTAMP NOT NULL,
                tick INT NOT NULL,
                coal INT NOT NULL,
                uranium INT NOT NULL,
                biomass INT NOT NULL,
                gas INT NOT NULL,
                oil INT NOT NULL,
                geothermal INT NOT NULL,
                wind INT NOT NULL,
                solar INT NOT NULL,
                hydro INT NOT NULL,
                energy_demand INT NOT NULL,
                max_energy_price INT NOT NULL,
                FOREIGN KEY (dataset_id) REFERENCES datasets(dataset_id)
                )''')

    datasets_path = config["datasets_path"]

    try:
        await Team.create(
            team_name=config["bots"]["team_name"],
            team_secret=config["bots"]["team_secret"]
        )
        print("Created bots team")
    except:
        print("Bots team already created")

    for x in os.listdir(datasets_path):
        try:
            if not x.endswith(".csv"):
                continue

            df = pd.read_csv(f"{datasets_path}/{x}")

            # TODO: asserts

            dataset_id = await Datasets.create(dataset_name=x, dataset_description="Opis")

            # date,COAL,URANIUM,BIOMASS,GAS,OIL,GEOTHERMAL,WIND,SOLAR,HYDRO,ENERGY_DEMAND,MAX_ENERGY_PRICE
            i = 0
            for index, row in df.iterrows():
                await DatasetData.create(dataset_id=dataset_id,
                                         tick=i,
                                         date=datetime.strptime(
                                             row["date"], "%Y-%m-%d %H:%M:%S"),
                                         coal=row["COAL"],
                                         uranium=row["URANIUM"],
                                         biomass=row["BIOMASS"],
                                         gas=row["GAS"],
                                         oil=row["OIL"],
                                         geothermal=row["GEOTHERMAL"],
                                         wind=row["WIND"],
                                         solar=row["SOLAR"],
                                         hydro=row["HYDRO"],
                                         energy_demand=row["ENERGY_DEMAND"],
                                         max_energy_price=row["MAX_ENERGY_PRICE"]
                                         )
                i += 1
            print(f"Added dataset {x}")
        except Exception as e:
            print(e)
            raise e
            # print(f"Dataset {x} already created")

    print("Migrated database")
