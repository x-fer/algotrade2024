from databases import Database

async def run_migrations(database: Database):
    await database.connect()

    # await database.execute('DROP TABLE teams')
    # await database.execute('DROP TABLE games')
    # await database.execute('DROP TABLE players')
    # await database.execute('DROP TABLE power_plants')
    
    await database.execute('''
              CREATE TABLE IF NOT EXISTS teams (
              team_id INTEGER PRIMARY KEY AUTOINCREMENT,
              team_name TEXT UNIQUE,
              team_secret TEXT UNIQUE
              )''')
              
    await database.execute('''
              CREATE TABLE IF NOT EXISTS games (
              game_id INTEGER PRIMARY KEY AUTOINCREMENT,
              game_name TEXT UNIQUE,
              contest BOOL NOT NULL,
              queue_id TEXT NOT NULL,
              start_time DATETIME NOT NULL,
              tick_time INTEGER NOT NULL
              )''')

    await database.execute('''
              CREATE TABLE IF NOT EXISTS players (
              player_id INTEGER PRIMARY KEY AUTOINCREMENT,
              player_name TEXT,
              active BOOL DEFAULT 1,
              game_id INTEGER NOT NULL,
              team_id INTEGER NOT NULL,
              
              money INTEGER NOT NULL DEFAULT 0,
              energy INTEGER NOT NULL DEFAULT 0,
              coal INTEGER NOT NULL DEFAULT 0,
              uranium INTEGER NOT NULL DEFAULT 0,
              gas INTEGER NOT NULL DEFAULT 0,
              oil INTEGER NOT NULL DEFAULT 0,
              
              FOREIGN KEY (game_id) REFERENCES games(game_id),
              FOREIGN KEY (team_id) REFERENCES teams(team_id)
              )''')

    await database.execute('''
              CREATE TABLE IF NOT EXISTS power_plants (
              power_plant_id INTEGER PRIMARY KEY AUTOINCREMENT,
              type INTEGER NOT NULL,
              game_id INTEGER NOT NULL,
              player_id INTEGER NOT NULL,
              temperature INTEGER NOT NULL DEFAULT 0,
              
              FOREIGN KEY (game_id) REFERENCES games(game_id),
              FOREIGN KEY (player_id) REFERENCES players(player_id)
              )''')

if __name__ == "main":
    database = Database("sqlite:///test.db")
    run_migrations(database)