from databases import Database
from db.db import database
from db.model import *
from datetime import datetime


async def fill_tables():
    g_team_id = await Team.create(team_name="Goranov_tim", team_secret="gogi")
    k_team_id = await Team.create(team_name="Krunov_tim", team_secret="kruno")
    z_team_id = await Team.create(team_name="Zvonetov_tim", team_secret="zvone")
    # Treba li ovo ovako?
    b_team_id = await Team.create(team_name="Botovi", team_secret="bots")

    not_nat_game_id = await Game.create(game_name="Stalna igra", is_contest=False, bots="lagani", dataset="prvi", start_time=datetime.now(), total_ticks=2400, tick_time=3000)
    nat_game_id = await Game.create(game_name="Natjecanje", is_contest=True, bots="teski, lagani", dataset="drugi", start_time=datetime.now(), total_ticks=10, tick_time=1000)

    for game_id in [not_nat_game_id, nat_game_id]:
        await Player.create(player_name="Goran", is_active=True, is_bot=False, game_id=game_id, team_id=g_team_id, money=15000)
        await Player.create(player_name="Kruno", is_active=True, is_bot=False, game_id=game_id, team_id=k_team_id)
        await Player.create(player_name="Zvone", is_active=True, is_bot=False, game_id=game_id, team_id=z_team_id)

    await Player.create(player_name="lagani", is_active=True, is_bot=True, game_id=not_nat_game_id, team_id=b_team_id)
    await Player.create(player_name="lagani", is_active=True, is_bot=True, game_id=nat_game_id, team_id=b_team_id)
    await Player.create(player_name="teski", is_active=True, is_bot=True, game_id=nat_game_id, team_id=b_team_id)

    await PowerPlant.create(type=PowerPlantType.COAL.value, player_id=1, price=1, powered_on=True)

    print("Filled database with dummy data")


async def delete_tables():
    await database.execute('TRUNCATE power_plants, trades, orders, players, games, teams CASCADE')


async def drop_tables():
    for table_name in ["power_plants", "trades", "orders", "players", "games", "teams"]:
        await database.execute(f'DROP TABLE IF EXISTS {table_name}')


async def run_migrations():
    await database.execute('''
              CREATE TABLE IF NOT EXISTS teams (
              team_id SERIAL PRIMARY KEY,
              team_name TEXT,
              team_secret TEXT UNIQUE
              )''')

    await database.execute('''
              CREATE TABLE IF NOT EXISTS games (
              game_id SERIAL PRIMARY KEY,
              game_name TEXT,
              is_contest BOOLEAN NOT NULL,
              bots TEXT,
              dataset TEXT,
              start_time TIMESTAMP NOT NULL,
              total_ticks INT NOT NULL,
              tick_time INT NOT NULL,
              is_finished BOOLEAN NOT NULL DEFAULT false,
              current_tick INT NOT NULL DEFAULT 0
              )''')

    await database.execute('''
              CREATE TABLE IF NOT EXISTS players (
              player_id SERIAL PRIMARY KEY,
              player_name TEXT,
              game_id INT NOT NULL,
              team_id INT NOT NULL,
              is_active BOOLEAN NOT NULL DEFAULT true,
              is_bot BOOLEAN NOT NULL DEFAULT false,
              
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
                timestamp TIMESTAMP NOT NULL,
                expiration_tick INT NOT NULL,
                resource INT NOT NULL,
                           
                filled_size INT NOT NULL DEFAULT 0,
                filled_money INT NOT NULL DEFAULT 0,
                filled_price INT NOT NULL DEFAULT 0,
                
                FOREIGN KEY (player_id) REFERENCES players(player_id),
                FOREIGN KEY (game_id) REFERENCES games(game_id)
                )''')

    await database.execute('''
              CREATE TABLE IF NOT EXISTS market (
              game_id INT PRIMARY KEY,
              tick INT PRIMARY KEY,
              resource INT PRIMARY KEY,
              low INT,
              high INT,
              open INT,
              close INT,
              market INT,
              )''')