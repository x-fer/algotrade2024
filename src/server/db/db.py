from databases import Database
from db.migration import run_migrations
from config import config

if config['testing']:
    database = Database(config['database']['url'], force_rollback=True)
    print("Testing database created")
else:
    database = Database(config['database']['url'])
    print("Database object created")
