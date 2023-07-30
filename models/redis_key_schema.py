from typing import Callable

DEFAULT_KEY_PREFIX = "tg_jw_shop_01"


def prefixed_key(f: Callable):
    """Prefixes any given key with default app prefix"""

    def prefixed_method(self, *args, **kwargs):
        key = f(self, *args, **kwargs)
        return f"{self.prefix}:{key}"

    return prefixed_method


class RedisKeySchema:
    """ methods to generate key names for Redis data structures"""

    def __init__(self, prefix: str = DEFAULT_KEY_PREFIX) -> None:
        self.prefix: str = prefix

    @prefixed_key
    def get_cart_key(self, user_id: int | str) -> str:
        return f"cart:{user_id}"

    @prefixed_key
    def get_favorite_key(self, user_id: int | str) -> str:
        return f"favorite:{user_id}"

