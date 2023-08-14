import os.path
from datetime import datetime, timedelta
from typing import Callable

from aiogram.filters.callback_data import CallbackQuery
from aiogram.types import Message, FSInputFile
from sqlalchemy import Row

from filters.callbacks import CallbackFactoryCategories as cfc, CallbackFactoryProductDetails as cfp, \
    CallbackFactoryGoods as cfg, CallbackFactoryStepBack as cfsb, CallbackFactoryFinalizeOrder as cffo, \
    CallbackFactoryCartProductSwap as cfcps
from lexicon.LEXICON import product_columns_mapper
from .populate_with_pic import populate_media


async def time_validity_check(callback_data: cfc | cfp | cfg | cfsb):
    return datetime.strptime(callback_data.timestamp, '%d-%m-%y %H-%M') + timedelta(minutes=5) < datetime.utcnow()


def check_if_file_is_empty(path: str):
    with open(path, 'rb') as file:
        data = file.read()
        if not data:
            return True
    return False


def get_file(product: Row, content_type: str = 'photos') -> FSInputFile | None:
    product_id: int = int(product.product_id)
    static_path: str = os.path.join(os.getcwd(), 'static', content_type)
    product_folder = os.path.join(static_path, str(product_id))

    try:
        os.mkdir(product_folder)
        populate_media(product_id=product_id)

    except FileExistsError:
        if not os.listdir(product_folder):
            populate_media(product_id=product_id)

    photo: str | None = None
    for item in os.listdir(product_folder):
        full_path: str = os.path.join(product_folder, item)
        if not check_if_file_is_empty(full_path):
            photo: str | None = full_path
            break
        os.remove(full_path)
    if not photo:
        populate_media(product_id=product_id)

    full_path: str = photo or os.path.join(product_folder, os.listdir(product_folder)[0])
    file: FSInputFile = FSInputFile(full_path)
    return file


async def send_product_card(update: CallbackQuery | Message,
                            kb: Callable,
                            product: Row,
                            admin_mode: bool = False
                            ):
    mapper: dict[str, str] = product_columns_mapper
    if admin_mode is True:
        mapper: dict[str, str] = product_columns_mapper.copy()
        mapper['product_uuid'] = 'UUID код продукта'
        mapper['product_id'] = 'ID код продукта'
    new_update: Message = update
    if isinstance(update, CallbackQuery):
        new_update: Message = update.message
    await new_update.answer_photo(
        caption='\n'.join(
            [f"<b>{value}</b>: {getattr(product, key)}" for key, value in
             mapper.items()]),
        parse_mode='HTML',
        photo=get_file(product),
        reply_markup=kb(product_uuid=product.product_uuid, update=update)
    )


async def send_product_card_cart_item(update: CallbackQuery | Message,
                                      kb: Callable,
                                      product: Row,
                                      callback_data: cffo | cfcps,
                                      index: int,
                                      ):
    new_update: Message = update
    if isinstance(update, CallbackQuery):
        new_update: Message = update.message
    await new_update.answer_photo(
        caption='\n'.join(
            [f"<b>{value}</b>: {getattr(product, key)}" for key, value in
             product_columns_mapper.items()]),
        parse_mode='HTML',
        photo=get_file(product),
        reply_markup=kb(index=index, callback_data=callback_data)
    )


async def send_product_card_favorite_items(update: CallbackQuery | Message,
                                           kb: Callable,
                                           product: Row,
                                           index: int = 0):
    new_update: Message = update
    if isinstance(update, CallbackQuery):
        new_update: Message = update.message
    await new_update.answer_photo(
        caption='\n'.join(
            [f"<b>{value}</b>: {getattr(product, key)}" for key, value in
             product_columns_mapper.items()]),
        parse_mode='HTML',
        photo=get_file(product),
        reply_markup=kb(update=update, index=index)
    )
