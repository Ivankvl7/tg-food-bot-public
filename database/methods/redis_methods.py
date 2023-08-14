from redis import Redis

from database.database import RedisCache
from models.models import SelectedDevice
from models.redis_key_schema import RedisKeySchema

SINGLE_DAY_INTERVAL = 86400
ONE_HOUR_INTERVAL = 3600
ONE_WEEK_INTERVAL = 604800


def add_to_cart(item_uuid: str | int, user_id: int | str = 593908084) -> None:
    key: str = RedisKeySchema().get_cart_key(user_id)
    client: Redis = RedisCache.get_cache(RedisCache())
    client.hincrby(key, item_uuid)
    client.expire(key, ONE_HOUR_INTERVAL)


def get_user_cart(user_id: int | str = 593908084) -> dict[str, str] | None:
    key: str = RedisKeySchema().get_cart_key(user_id)
    client: Redis = RedisCache().get_cache()
    cart: dict = client.hgetall(key)
    return cart


def incr_cart_quantity(user_id: int, product_uuid: str, increment: int = 1) -> None:
    key: str = RedisKeySchema().get_cart_key(user_id)
    client: Redis = RedisCache().get_cache()
    client.hincrby(key, product_uuid, increment)


def remove_item_from_cart(user_id: int, product_uuid: str) -> None:
    client: Redis = RedisCache().get_cache()
    key: str = RedisKeySchema().get_cart_key(user_id)
    client.hdel(key, product_uuid)


def get_product_quantity(user_id: int, product_uuid: str) -> int:
    client: Redis = RedisCache().get_cache()
    key: str = RedisKeySchema().get_cart_key(user_id)
    quantity: str = client.hget(key, product_uuid)
    return int(quantity)


def clear_cart(user_id: int) -> None:
    client: Redis = RedisCache().get_cache()
    key: str = RedisKeySchema().get_cart_key(user_id)
    client.delete(key)


def add_to_favorite(user_id: int, product_uuid: str) -> None:
    client: Redis = RedisCache().get_cache()
    key: str = RedisKeySchema().get_favorite_key(user_id)
    client.rpush(key, product_uuid)
    client.expire(key, ONE_WEEK_INTERVAL)


def remove_from_favorite(user_id: int, product_uuid: str) -> None:
    client: Redis = RedisCache().get_cache()
    key: str = RedisKeySchema().get_favorite_key(user_id)
    client.lrem(key, 1, product_uuid)


# remove_from_favorite(593908084, '6ad73606-2653-4001-8a75-7cd317986274a')


def get_favorite(user_id: int) -> list:
    client: Redis = RedisCache().get_cache()
    key: str = RedisKeySchema().get_favorite_key(user_id)
    return client.lrange(key, 0, -1)


def set_user_profile_attribute(user_id: int, key: str, value: str | int) -> None:
    client: Redis = RedisCache().get_cache()
    hash_key: str = RedisKeySchema().get_user_profile_key(user_id)
    client.hset(hash_key, key, value)
    client.expire(hash_key, SINGLE_DAY_INTERVAL)


def get_user_profile(user_id: int) -> dict[str, str]:
    client: Redis = RedisCache().get_cache()
    key: str = RedisKeySchema().get_user_profile_key(user_id)
    user_profile: dict = client.hgetall(key)
    return user_profile


def set_user_device(user_id: int, device: str = SelectedDevice.MOBILE_DEVICE.value) -> None:
    client: Redis = RedisCache().get_cache()
    key: str = RedisKeySchema().get_selected_device_key(user_id)
    client.set(key, device)
    client.expire(key, ONE_HOUR_INTERVAL)


def get_user_device(user_id: int) -> str:
    client: Redis = RedisCache().get_cache()
    key: str = RedisKeySchema().get_selected_device_key(user_id)
    return client.get(key)
