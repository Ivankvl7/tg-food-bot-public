from database.database import RedisCache
from models.redis_key_schema import RedisKeySchema
from models.models import CartItem
from models.redis_schema import CartItemSchema

SINGLE_DAY_SECONDS = 86400


def add_to_cart(item_uuid: str | int):
    key = RedisKeySchema().get_cart_key(593908084)
    client = RedisCache().get_cache()
    client.rpush(key, item_uuid)
    client.expire(key, SINGLE_DAY_SECONDS)
