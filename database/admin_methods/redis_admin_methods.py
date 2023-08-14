from redis import Redis

from database.database import RedisCache
from models.redis_key_schema import RedisKeySchema
from ..methods.redis_methods import ONE_HOUR_INTERVAL


def get_product_attributes(user_id: int) -> dict:
    client: Redis = RedisCache().get_cache()
    key: str = RedisKeySchema().get_new_product_attributes_key(user_id)
    return client.hgetall(key)


def set_product_attribute(user_id: int, attr: str, value: str | int) -> None:
    client: Redis = RedisCache().get_cache()
    key: str = RedisKeySchema().get_new_product_attributes_key(user_id)
    client.hset(key, attr, value)
    client.expire(key, ONE_HOUR_INTERVAL)


def incr_product_attr(user_id: int, attr: str, value: int) -> None:
    client: Redis = RedisCache().get_cache()
    key: str = RedisKeySchema().get_new_product_attributes_key(user_id)
    client.hincrby(key, attr, value)


def del_tmp_attrs(user_id: int) -> None:
    client: Redis = RedisCache().get_cache()
    key: str = RedisKeySchema().get_new_product_attributes_key(user_id)
    client.delete(key)


def set_tmp_media(user_id: int, link: str, content_type: str = 'photos') -> None:
    client: Redis = RedisCache().get_cache()
    key: str = RedisKeySchema().get_new_product_media(user_id=user_id,
                                                      content_type=content_type)
    client.rpush(key, link)
    client.expire(key, ONE_HOUR_INTERVAL)


def get_tmp_media_num(user_id: int, content_type: str = 'photos') -> int:
    client: Redis = RedisCache().get_cache()
    key: str = RedisKeySchema().get_new_product_media(user_id=user_id,
                                                      content_type=content_type)
    return client.llen(key)


def get_tmp_media(user_id: int, content_type: str = 'photos') -> list[str]:
    client: Redis = RedisCache().get_cache()
    key: str = RedisKeySchema().get_new_product_media(user_id=user_id,
                                                      content_type=content_type)
    return client.lrange(key, 0, -1)


def del_tmp_media(user_id: int, content_type: str = 'photos') -> None:
    client: Redis = RedisCache().get_cache()
    key: str = RedisKeySchema().get_new_product_media(user_id=user_id,
                                                      content_type=content_type)
    client.delete(key)
