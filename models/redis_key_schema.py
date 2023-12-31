from typing import Callable, Any
from models.models import StaticContentType

DEFAULT_KEY_PREFIX = "tg_food_shop"


def prefixed_key(f: Callable) -> Callable:
    """Prefixes any given key with default app prefix"""

    def prefixed_method(self, *args, **kwargs) -> str:
        key: Any = f(self, *args, **kwargs)
        return f"{self.prefix}:{key}"

    return prefixed_method


class RedisKeySchema:
    """ methods to generate key names for Redis data structures"""

    def __init__(self, prefix: str = DEFAULT_KEY_PREFIX) -> None:
        self.prefix: str = prefix

    @prefixed_key
    def get_cart_key(self, user_id: int) -> str:
        return f"cart_hash:{user_id}"

    @prefixed_key
    def get_favorite_key(self, user_id: int) -> str:
        return f"favorite:{user_id}"

    @prefixed_key
    def get_user_profile_key(self, user_id: int):
        return f"user_profile:{user_id}"

    @prefixed_key
    def get_selected_device_key(self, user_id: int):
        return f"user_device:{user_id}"

    @prefixed_key
    def get_new_product_attributes_key(self, user_id: int):
        return f"new_product_admin:{user_id}"

    @prefixed_key
    def get_new_product_media(self, user_id: int, content_type: StaticContentType = StaticContentType.IMAGE):
        return f"new_product_{content_type.value}:{user_id}"

    @prefixed_key
    def get_media_cache(self, user_id: int, content_type: StaticContentType = StaticContentType.IMAGE):
        return f"media_cache_{content_type.value}_{user_id}"

