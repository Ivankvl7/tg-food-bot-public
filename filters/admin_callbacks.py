from aiogram.filters.callback_data import CallbackData


class CallbackFactoryAddCategory(CallbackData, prefix='add_c'):
    user_id: int
    timestamp: str


class CallbackFactoryDelCategory(CallbackData, prefix='del_c'):
    user_id: int
    timestamp: str


class CallbackFactoryDeletedCat(CallbackData, prefix='cat_to_del'):
    user_id: int
    cat_id: int
    timestamp: str


class CallbackFactoryAddProduct(CallbackData, prefix="s_add_p"):
    user_id: int
    timestamp: str


class CallbackFactoryChangeExistingProduct(CallbackData, prefix="ch_p"):
    user_id: int
    timestamp: str


class CallbackFactoryProductAddingTips(CallbackData, prefix='tips'):
    user_id: int
    action: str
    timestamp: str


class CallbackFactoryAddProductFinal(CallbackData, prefix='add_p'):
    user_id: int
    timestamp: str


class CallbackFactoryGetAttrsState(CallbackData, prefix='attrs_s'):
    user_id: int
    timestamp: str


class CallbackFactoryAlterProductTip(CallbackData, prefix='alt_prod'):
    user_id: int
    timestamp: str


class CallbackFactoryAvailableFields(CallbackData, prefix='av_fs'):
    user_id: int
    timestamp: str


class CallbackFactoryDeleteProduct(CallbackData, prefix='dp'):
    user_id: int
    product_uuid: str
    timestamp: str


class CallbackFactoryActiveOrders(CallbackData, prefix='act_ord'):
    user_id: int
    timestamp: str


class CallbackFactoryStatusList(CallbackData, prefix='st_l'):
    user_id: int
    timestamp: str


class CallbackFactoryCatIDs(CallbackData, prefix='cat_ids'):
    user_id: int
    timestamp: str
