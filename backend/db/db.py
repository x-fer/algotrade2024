from redis_om import get_redis_connection
from config import config
from redis_om import Migrator


Migrator().run()


redis_port = config["redis"]["port"]


def get_my_redis_connection():
    return get_redis_connection(port=redis_port)
