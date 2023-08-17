import io
import os.path
from datetime import datetime, timedelta
from typing import Callable
from models.models import StaticContentType, TmpNames
from aiogram.filters.callback_data import CallbackQuery
from aiogram.types import Message, FSInputFile, InputFile
from sqlalchemy import Row
from external_services.b2b_process import B2BInstance
from models.static_name_schema import StaticNameSchema
from filters.callbacks import CallbackFactoryCategories as cfc, CallbackFactoryProductDetails as cfp, \
    CallbackFactoryGoods as cfg, CallbackFactoryStepBack as cfsb, CallbackFactoryFinalizeOrder as cffo, \
    CallbackFactoryCartProductSwap as cfcps
from lexicon.LEXICON import product_columns_mapper
from .populate_with_pic import populate_media, populate_b2b_media
from database.admin_methods.redis_admin_methods import get_media_id, add_media_id
from models.static_name_schema import StaticNameSchema
from aiogram.methods.send_photo import SendPhoto


async def time_validity_check(callback_data: cfc | cfp | cfg | cfsb):
    return datetime.strptime(callback_data.timestamp, '%d-%m-%y %H-%M') + timedelta(minutes=5) < datetime.utcnow()


def check_if_file_is_empty(path: str):
    with open(path, 'rb') as file:
        data = file.read()
        if not data:
            return True
    return False


def add_media_to_cache(user_id: int,
                       product_id: int,
                       res: Message,
                       media_file_id: int = 1,
                       media_type: StaticContentType = StaticContentType.IMAGE
                       ) -> None:
    path_schema = StaticNameSchema()
    file_name = path_schema.get_file_name(product_id=product_id,
                                          file_id=media_file_id)
    if media_type == StaticContentType.IMAGE:
        media_tg_id = res.photo[-1].file_id
    else:
        media_tg_id = res.video.file_id
    print(f"media_tg_id = {media_tg_id}")
    add_media_id(user_id=user_id,
                 file_name=file_name,
                 media_id=media_tg_id,
                 content_type=media_type)


def get_file_b2b(product_id: int,
                 file_id: int = 1,
                 media_type: StaticContentType = StaticContentType.IMAGE):
    b2_instance = B2BInstance()
    file = b2_instance.download_media(
        product_id=product_id,
        file_id=file_id,
        media_type=media_type)
    file.save_to(f"{TmpNames[media_type.name].value}")


def get_file(product: Row,
             user_id: int,
             content_type: StaticContentType = StaticContentType.IMAGE) -> str | FSInputFile | None:
    path_schema = StaticNameSchema(media_type=content_type)
    product_id: int = int(product.product_id)
    static_path: str = os.path.join(os.getcwd(), 'static', content_type.value)
    product_folder: str = os.path.join(static_path, str(product_id))

    file_id = 1  #
    file_name = path_schema.get_file_name(product_id=product_id,
                                          file_id=file_id)
    cached_id = get_media_id(user_id=user_id,
                             file_name=file_name,
                             content_type=content_type)
    if cached_id:
        print('taking media id from telegram server as it was sent before')
        return str(cached_id)

    def check_b2b_storage():
        bucket = B2BInstance()
        b2b_files = list(bucket.get_static_data(product_id=product_id,
                                                media_type=content_type))
        print(f"b2b_Files = {b2b_files}")
        if b2b_files:
            get_file_b2b(product_id=product_id,
                         media_type=content_type)
            complete_path = path_schema.get_full_path(product_id=product_id,
                                                      file_id=file_id)
            print(f"complete_path = {complete_path}")
            populate_b2b_media(file_to_write=complete_path,
                               media_type=content_type)
            return FSInputFile(complete_path)
        return

    try:
        os.mkdir(product_folder)
        b2b_res = check_b2b_storage()
        if b2b_res:
            return b2b_res
        return FSInputFile(path_schema.get_default_path(media_type=content_type))

    except FileExistsError:
        if not os.listdir(product_folder):
            b2b_res = check_b2b_storage()
            if b2b_res:
                return b2b_res
            return FSInputFile(path_schema.get_default_path(media_type=content_type))

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

    user_id = new_update.chat.id
    res = await new_update.answer_photo(
        caption='\n'.join(
            [f"<b>{value}</b>: {getattr(product, key)}" for key, value in
             mapper.items()]),
        parse_mode='HTML',
        photo=get_file(product, user_id),
        reply_markup=kb(product_uuid=product.product_uuid, update=update)
    )
    product_id = product.product_id
    add_media_to_cache(user_id=user_id,
                       product_id=product_id,
                       res=res)


async def send_product_card_cart_item(update: CallbackQuery | Message,
                                      kb: Callable,
                                      product: Row,
                                      callback_data: cffo | cfcps,
                                      index: int,
                                      ):
    new_update: Message = update
    if isinstance(update, CallbackQuery):
        new_update: Message = update.message
    user_id = new_update.chat.id
    res = await new_update.answer_photo(
        caption='\n'.join(
            [f"<b>{value}</b>: {getattr(product, key)}" for key, value in
             product_columns_mapper.items()]),
        parse_mode='HTML',
        photo=get_file(product, user_id),
        reply_markup=kb(index=index, callback_data=callback_data)
    )
    product_id = product.product_id
    add_media_to_cache(user_id=user_id,
                       product_id=product_id,
                       res=res)


async def send_product_card_favorite_items(update: CallbackQuery | Message,
                                           kb: Callable,
                                           product: Row,
                                           index: int = 0):
    new_update: Message = update
    if isinstance(update, CallbackQuery):
        new_update: Message = update.message
    user_id = new_update.chat.id
    res = await new_update.answer_photo(
        caption='\n'.join(
            [f"<b>{value}</b>: {getattr(product, key)}" for key, value in
             product_columns_mapper.items()]),
        parse_mode='HTML',
        photo=get_file(product, user_id),
        reply_markup=kb(update=update, index=index)
    )
    product_id = product.product_id
    add_media_to_cache(user_id=user_id,
                       product_id=product_id,
                       res=res)
