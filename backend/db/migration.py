from logger import logger
from .fill_teams import fill_bots, fill_dummy_tables
from .fill_datasets import fill_datasets


async def delete_tables():
    await database_.execute('TRUNCATE orders, players, games, teams, market, datasets, dataset_data CASCADE')


async def drop_tables():
    for table_name in ["orders", "players", "games", "teams", "market", "datasets", "dataset_data"]:
        await database_.execute(f'DROP TABLE IF EXISTS {table_name} CASCADE')


async def run_migrations():
    logger.info("Running migration script")
    await create_tables()
    await fill_datasets()
    await fill_bots()
    logger.info("Migrated database")


async def create_tables():
    await database_.execute('''
              CREATE TABLE IF NOT EXISTS teams (
              team_id SERIAL PRIMARY KEY,
              team_name TEXT,
              team_secret TEXT UNIQUE
              )''')

    await database_.execute('CREATE INDEX CONCURRENTLY team_secret_idx ON teams (team_secret);')

    await database_.execute('''
                CREATE TABLE IF NOT EXISTS datasets (
                dataset_id SERIAL PRIMARY KEY,
                dataset_name TEXT,
                dataset_description TEXT
                )''')

    await database_.execute('''
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

    await database_.execute('''
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

    await database_.execute('CREATE INDEX CONCURRENTLY player_idx ON players (player_id, game_id);')

    await database_.execute('''
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

    await database_.execute('CREATE INDEX CONCURRENTLY orders_idx ON orders (order_id);')
    await database_.execute('CREATE INDEX CONCURRENTLY orders_idx2 ON orders (game_id, order_status, player_id);')

    await database_.execute('''
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

    await database_.execute('''
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

    await database_.execute('CREATE INDEX CONCURRENTLY tick_idx ON market (tick);')

    await database_.execute('''
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
