from databases import Database

async def drop_tables(database: Database):
    await database.connect()
    
    await database.execute('DROP TABLE IF EXISTS power_plants')
    await database.execute('DROP TABLE IF EXISTS trades')
    await database.execute('DROP TABLE IF EXISTS pending_orders')
    await database.execute('DROP TABLE IF EXISTS orders')
    await database.execute('DROP TABLE IF EXISTS players')
    await database.execute('DROP TABLE IF EXISTS games')
    await database.execute('DROP TABLE IF EXISTS teams')
    
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
              start_time TIMESTAMP NOT NULL,
              total_ticks INT NOT NULL,
              tick_time INT NOT NULL,
              current_tick INT NOT NULL DEFAULT 0
              )''')

    await database.execute('''
              CREATE TABLE IF NOT EXISTS players (
              player_id SERIAL PRIMARY KEY,
              player_name TEXT,
              is_active BOOLEAN NOT NULL,
              is_bot BOOLEAN NOT NULL,
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
              price INT NOT NULL,
              is_active BOOLEAN NOT NULL,
              temperature INT NOT NULL DEFAULT 0,
              
              FOREIGN KEY (player_id) REFERENCES players(player_id)
              )''')

    await database.execute('''
              CREATE TABLE IF NOT EXISTS orders (
              order_id SERIAL PRIMARY KEY,
              resource INT NOT NULL,
              side INT NOT NULL,
              price INT NOT NULL,
              size INT NOT NULL,
              timestamp TIMESTAMP NOT NULL,
              expiration_tick INT NOT NULL,
              game_id INT NOT NULL,
              player_id INT NOT NULL,
              is_processed BOOLEAN NOT NULL,
              
              FOREIGN KEY (player_id) REFERENCES players(player_id),
              FOREIGN KEY (game_id) REFERENCES games(game_id)
              )''')
    # orders tablica
    # koristi se prilikom dodavanja novog ordera, a na kraju svakog ticka se dohvacaju
    # svi novi orderi i obraduju se (ubacuju se u matching engine)
    # TODO:
    # price = -1 ako je market. expiration_tick = -1 ako ne postoji
    # ova zapravo krsi neku normalnu formu, jer game_id moze biti drugaciji nego player.game_id
    # mozda je glupo izbaciti game id, jer se onda mora dohvacati posebno, mozda i ne...
    # sto ako je market price i na BUY orderu i na SELL orderu?

    # pending_orders tablica
    # ova tablica se koristi samo za evidenciju, inace je sve spremljeno u matching_engine 
    # objektu
    # Nakon obrade matcheva se svi pending orderi od matchera ubacuju ovdje, ali se brisu
    # svi prethodni (prethodni pending orderi su zapravo nebitni cak i u buducnosti, ako
    # postoji neka tablica s prethodno sklopljenim tradeovima)
    # Mozda treba tablica koja u svaki tick zapisuje current_price za svaki resurs...
    await database.execute('''
              CREATE TABLE IF NOT EXISTS pending_orders (
              order_id SERIAL PRIMARY KEY,
              resource INT NOT NULL,
              side INT NOT NULL,
              price INT NOT NULL,
              size INT NOT NULL,
              timestamp TIMESTAMP NOT NULL,
              expiration_tick INT NOT NULL,
              game_id INT NOT NULL,
              player_id INT NOT NULL,
              is_processed BOOLEAN NOT NULL,
              
              FOREIGN KEY (player_id) REFERENCES players(player_id),
              FOREIGN KEY (game_id) REFERENCES games(game_id)
              )''')

    # trades tablica
    # ova tablica se koristi samo za evidenciju, inace je sve spremljeno u matching_engine 
    # objektu
    # tick je tick u kojem je trade napravljen
    # krsi normalnu formu jer dva playera mogu biti u razlicitim igrama, to mozemo zanemariti
    await database.execute('''
              CREATE TABLE IF NOT EXISTS trades (
              trade_id SERIAL PRIMARY KEY,
              resource INT NOT NULL,
              price INT NOT NULL,
              size INT NOT NULL,
              tick INT NOT NULL,
              game_id INT NOT NULL,
              buyer_id INT NOT NULL,
              seller_id INT NOT NULL,

              FOREIGN KEY (buyer_id) REFERENCES players(player_id),
              FOREIGN KEY (seller_id) REFERENCES players(player_id),
              FOREIGN KEY (game_id) REFERENCES games(game_id)
              )''')

if __name__ == "main":
    database = Database("sqlite:///test.db")
    run_migrations(database)