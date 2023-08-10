from redis import Redis

from database.database import RedisCache
from models.redis_key_schema import RedisKeySchema
from models.models import SelectedDevice
from ..methods.redis_methods import TEN_MIN_INTERVAL


def add_product_attributes(user_id: int, attr_name: str, value: str | int) -> None:
    client: Redis = RedisCache().get_cache()
    key: str = RedisKeySchema().get_new_product_attributes_key(user_id)
    client.hset(key, attr_name, value)
    client.expire(key, TEN_MIN_INTERVAL)


def get_product_attributes(user_id: int) -> dict:
    client: Redis = RedisCache().get_cache()
    key: str = RedisKeySchema().get_new_product_attributes_key(user_id)
    return client.hgetall(key)


def set_product_attribute(user_id: int, attr: str, value: str) -> None:
    client: Redis = RedisCache().get_cache()
    key: str = RedisKeySchema().get_new_product_attributes_key(user_id)
    client.hset(key, attr, value)


