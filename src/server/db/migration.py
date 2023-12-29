from databases import Database

async def drop_tables(database: Database):
    await database.connect()
    
    await database.execute('DROP TABLE power_plants')
    await database.execute('DROP TABLE players')
    await database.execute('DROP TABLE games')
    await database.execute('DROP TABLE teams')
    
async def run_migrations(database: Database):
    await database.connect()

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
              contest BOOLEAN NOT NULL,
              queue_id TEXT NOT NULL,
              start_time timestamp NOT NULL,
              tick_time INT NOT NULL
              )''')

    await database.execute('''
              CREATE TABLE IF NOT EXISTS players (
              player_id SERIAL PRIMARY KEY,
              player_name TEXT,
              active BOOLEAN NOT NULL,
              game_id INT NOT NULL,
              team_id INT NOT NULL,
              
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
              temperature INT NOT NULL DEFAULT 0,
              
              FOREIGN KEY (player_id) REFERENCES players(player_id)
              )''')

if __name__ == "main":
    database = Database("sqlite:///test.db")
    run_migrations(database)