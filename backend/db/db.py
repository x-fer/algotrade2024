from redis_om import get_redis_connection


def get_my_redis_connection():
    return get_redis_connection(port=6379)