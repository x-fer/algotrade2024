from databases import Database
from config import config


if config['testing']:
    database = Database(config['test_database']['url'])
    print("Testing database created")
else:
    database = Database(config['database']['url'])
    print("Database object created")
