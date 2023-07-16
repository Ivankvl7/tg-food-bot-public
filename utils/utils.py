from datetime import datetime, timedelta
from aiogram.filters.callback_data import CallbackData, CallbackQuery
from filters.callbacks import CallbackFactoryCategories as cfc, CallbackFactoryProductDetails as cfp, \
    CallbackFactoryGoods as cfg, CallbackFactoryStepBack as cfsb
from lexicon.LEXICON import product_columns_mapper
from typing import Callable
from sqlalchemy import Row


async def time_validity_check(callback_data: cfc | cfp | cfg | cfsb):
    return datetime.strptime(callback_data.timestamp, '%d-%m-%y %H-%M') + timedelta(minutes=5) < datetime.utcnow()


async def send_product_card(callback: CallbackQuery,
                            product_action_bar: Callable,
                            product: Row):

    await callback.message.answer_photo(
        caption='\n'.join(
            [f"<b>{value}</b>: {getattr(product, key)}" for key, value in
             product_columns_mapper.items()]),
        parse_mode='HTML',
        photo='https://eavf3cou74b.exactdn.com/wp-content/uploads/2021/09/21104001/How-to-Photograph-Jewelry-10-768x512.jpg?strip=all&lossy=1&ssl=1',
        reply_markup=product_action_bar(product_uuid=product.product_uuid, update=callback)

    )
