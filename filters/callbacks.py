from aiogram.filters.callback_data import CallbackData
from datetime import datetime
import functools


# CallbackFactory for categories buttons
class CallbackFactoryCategories(CallbackData, prefix='c'):
    user_id: int | str
    uuid: str | int
    timestamp: str


# CallbackFactory involved in handling pagination requests while browsing goods
class CallbackFactoryGoods(CallbackData, prefix='g'):
    user_id: int | str
    uuid: str | int
    timestamp: str


# CallbackFactory for requesting product details
class CallbackFactoryProductDetails(CallbackData, prefix='d'):
    user_id: int | str
    uuid: str | int
    timestamp: str


class CallbackFactoryStepBack(CallbackData, prefix='cancel_product_browsing'):
    user_id: int | str
    timestamp: str


class CallbackFactorySwapRight(CallbackData, prefix='r'):
    user_id: int | str
    uuid: str | int
    timestamp: str


class CallbackFactorySwapLeft(CallbackData, prefix='l'):
    user_id: int | str
    uuid: str | int
    timestamp: str
