from datetime import datetime, timedelta
from aiogram.filters.callback_data import CallbackData, CallbackQuery
from filters.callbacks import CallbackFactoryCategories as cfc, CallbackFactoryProductDetails as cfp, \
    CallbackFactoryGoods as cfg, CallbackFactoryStepBack as cfsb, CallbackFactoryFinalizeOrder as cffo, \
    CallbackFactoryCartProductSwap as cfcps
from lexicon.LEXICON import product_columns_mapper, order_summary_mapper
from typing import Callable
from sqlalchemy import Row
from aiogram.types import Message


async def time_validity_check(callback_data: cfc | cfp | cfg | cfsb):
    return datetime.strptime(callback_data.timestamp, '%d-%m-%y %H-%M') + timedelta(minutes=5) < datetime.utcnow()


async def send_product_card(update: CallbackQuery | Message,
                            kb: Callable,
                            product: Row,
                            admin_mode: bool = False
                            ):
    mapper = product_columns_mapper
    if admin_mode is True:
        mapper = product_columns_mapper.copy()
        mapper['product_uuid'] = 'Идентификатор продукта'
    print(mapper)
    if isinstance(update, CallbackQuery):
        new_update = update.message
    else:
        new_update = update
    await new_update.answer_photo(
        caption='\n'.join(
            [f"<b>{value}</b>: {getattr(product, key)}" for key, value in
             mapper.items()]),
        parse_mode='HTML',
        photo='https://eavf3cou74b.exactdn.com/wp-content/uploads/2021/09/21104001/How-to-Photograph-Jewelry-10-768x512.jpg?strip=all&lossy=1&ssl=1',
        reply_markup=kb(product_uuid=product.product_uuid, update=update)

    )


async def send_product_card_cart_item(update: CallbackQuery | Message,
                                      kb: Callable,
                                      product: Row,
                                      callback_data: cffo | cfcps,
                                      index: int,
                                      ):
    if isinstance(update, CallbackQuery):
        new_update = update.message
    else:
        new_update = update
    await new_update.answer_photo(
        caption='\n'.join(
            [f"<b>{value}</b>: {getattr(product, key)}" for key, value in
             mapper.items()]),
        parse_mode='HTML',
        photo='https://eavf3cou74b.exactdn.com/wp-content/uploads/2021/09/21104001/How-to-Photograph-Jewelry-10-768x512.jpg?strip=all&lossy=1&ssl=1',
        reply_markup=kb(index=index, callback_data=callback_data)

    )


async def send_product_card_favorite_items(update: CallbackQuery | Message,
                                           kb: Callable,
                                           product: Row,
                                           index: int = 0):
    if isinstance(update, CallbackQuery):
        new_update = update.message
    else:
        new_update = update
    await new_update.answer_photo(
        caption='\n'.join(
            [f"<b>{value}</b>: {getattr(product, key)}" for key, value in
             product_columns_mapper.items()]),
        parse_mode='HTML',
        photo='https://eavf3cou74b.exactdn.com/wp-content/uploads/2021/09/21104001/How-to-Photograph-Jewelry-10-768x512.jpg?strip=all&lossy=1&ssl=1',
        reply_markup=kb(update=update, index=index)

    )
