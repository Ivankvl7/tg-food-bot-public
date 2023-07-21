from aiogram.filters.callback_data import CallbackData
from datetime import datetime
import functools


class CallbackFactoryWindowClose(CallbackData, prefix='start_page'):
    user_id: int | str
    timestamp: str


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


class CallbackFactoryProductDetailsFromCart(CallbackData, prefix='q'):
    user_id: int | str
    index: int
    timestamp: str


class CallbackFactoryStepBack(CallbackData, prefix='cancel_product_browsing'):
    user_id: int | str
    timestamp: str


class CallbackFactoryAddToCart(CallbackData, prefix='p'):
    user_id: int | str
    uuid: str | int
    timestamp: str


class CallbackFactoryAddToFavorite(CallbackData, prefix='f'):
    user_id: int | str
    uuid: str | int
    timestamp: str


class CallbackFactoryFinalizeOrder(CallbackData, prefix='fo'):
    user_id: int | str
    uuid: int | str
    timestamp: str


class CallbackFactoryCartProductSwap(CallbackData, prefix='cart'):
    user_id: int | str
    direction: str
    index: str | int
    timestamp: str


class CallbackFactoryQuantityChange(CallbackData, prefix='quantity_change'):
    action: str
    index: str | int
    user_id: int | str
    timestamp: str


class CallbackFactoryFavoriteProductsSwap(CallbackData, prefix='fav_g'):
    user_id: int | str
    direction: str
    index: str | int
    timestamp: str


class CallbackFactoryDeleteFromFavorite(CallbackData, prefix='fav_del'):
    user_id: int | str
    index: str | int
    timestamp: str


class CallbackFactoryAddToCartFromFavorite(CallbackData, prefix='fav_cart_add'):
    user_id: int | str
    index: str | int
    timestamp: str


class CallbackFactoryOrderConfirmation(CallbackData, prefix='order_confirm'):
    user_id: int | str
    timestamp: str


class CallbackFactoryNameInput(CallbackData, prefix='name_input'):
    user_id: int | str
    timestamp: str


class CallbackFactorTerminateConfirmation(CallbackData, prefix='terminate_confo'):
    user_id: int | str
    timestamp: str


class CallbackFactoryQuickConfirmation(CallbackData, prefix='quick_confirm'):
    user_id: int | str
    timestamp: str
