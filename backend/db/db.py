from databases import Database
from config import config


if config['testing']:
    database = Database(config['test_database']['url'])
else:
    database = Database(config['database']['url'])