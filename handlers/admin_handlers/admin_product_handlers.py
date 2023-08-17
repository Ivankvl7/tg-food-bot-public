import re
from datetime import datetime

from aiogram import Router, F
from aiogram.filters import Text
from aiogram.filters.state import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from aiogram.utils.keyboard import InlineKeyboardButton, InlineKeyboardMarkup
from sqlalchemy import Row
from lexicon.LEXICON import input_media_type_mapper

from database.admin_methods.redis_admin_methods import get_product_attributes, set_product_attribute, del_tmp_attrs, \
    set_tmp_media, get_tmp_media, get_tmp_media_num, del_tmp_media
from database.admin_methods.rel_bd_admin_methods import get_max_product_id_glob, add_new_product, alter_product_attr, \
    delete_product, get_cat_ids
from database.methods.rel_db_methods import get_category_uuid_by_product_uuid
from filters.admin_callbacks import CallbackFactoryAddProduct, CallbackFactoryProductAddingTips, \
    CallbackFactoryAddProductFinal, CallbackFactoryGetAttrsState, CallbackFactoryChangeExistingProduct, \
    CallbackFactoryAlterProductTip, CallbackFactoryDeleteProduct, CallbackFactoryCatIDs
from filters.callbacks import CallbackFactoryCategories
from keyboards.admin_keyboards import single_close_kb
from keyboards.user_keyboards import create_categories_kb
from lexicon.A_LEXICON import field_tips, fields_example
from middlewares.throttling import TimingMiddleware, IdMiddleware, DeviceMiddleware, AdminModeMiddleware
from models.models import AdminStaticKb, StaticContentType
from states.admin_states import AdminStates
from utils.populate_with_pic import populate_media
from external_services.b2b_process import B2BInstance
from .admin_catalog_handlers import data_listing
from ..user_handlers.catalog_handlers import process_products_listing

# router to navigate catalog related requests
router: Router = Router()
router.callback_query.middleware(TimingMiddleware())
router.callback_query.middleware(IdMiddleware())
router.callback_query.middleware(DeviceMiddleware())
router.message.middleware((DeviceMiddleware()))
router.callback_query.middleware(AdminModeMiddleware())
router.message.middleware(AdminModeMiddleware())


@router.message(Text(AdminStaticKb.PRODUCT_BUTTON.value), StateFilter(AdminStates.admin_start))
async def process_product_change_button(message: Message):
    user_id: int = message.chat.id
    await message.answer(text="Выберите действие",
                         reply_markup=InlineKeyboardMarkup(
                             inline_keyboard=[
                                 [InlineKeyboardButton(
                                     text="Добавить новый товар",
                                     callback_data=CallbackFactoryAddProduct(
                                         user_id=user_id,
                                         timestamp=datetime.utcnow().strftime('%d-%m-%y %H-%M')).pack())],
                                 [InlineKeyboardButton(
                                     text="Изменить существующий товар",
                                     callback_data=CallbackFactoryChangeExistingProduct(
                                         user_id=user_id,
                                         timestamp=datetime.utcnow().strftime('%d-%m-%y %H-%M')).pack())]
                             ]))


def fields_formatting(field_tip: dict):
    return '\n'.join([f"{key} = {value}" for key, value in field_tip.items()])


def _initiate_new_attributes(user_id: int):
    attributes: dict = get_product_attributes(user_id)
    for key in field_tips:
        if key not in attributes:
            set_product_attribute(user_id, key, '----')
    set_product_attribute(user_id, StaticContentType.IMAGE.value, 0)
    set_product_attribute(user_id, StaticContentType.VIDEO.value, 0)


@router.callback_query(CallbackFactoryAddProduct.filter(), StateFilter(AdminStates.admin_start))
async def process_add_product_start(callback: CallbackQuery):
    user_id: int = callback.message.chat.id
    _initiate_new_attributes(user_id)
    product_id: int = get_max_product_id_glob() + 1
    set_product_attribute(user_id, 'product_id', product_id)
    await callback.message.answer(
        text='Чтобы добавить новый товар необходимо заполнить ВСЕ поля, представленные ниже\n\n'
             'В одном сообщении нужно отправить один атрибут (его название из таблицы ниже) и его значение в следующем формате:\n' \
             'название_атрибута> = <значение атрибута>\n'
             'Прогресс сохраняется, на каждом этапе вы видите заполненные атрибуты\n\n'
             'Прогресс обнуляется после добавления продукта в таблицу\n\n'
             'Текущий прогресс: \n'
             f"{fields_formatting(get_product_attributes(user_id))}",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(
                    text="Добавить товар",
                    callback_data=CallbackFactoryAddProductFinal(
                        user_id=callback.message.chat.id,
                        timestamp=datetime.utcnow().strftime('%d-%m-%y %H-%M')).pack())],
                [InlineKeyboardButton(
                    text="Текущие атрибуты",
                    callback_data=CallbackFactoryGetAttrsState(
                        user_id=callback.message.chat.id,
                        timestamp=datetime.utcnow().strftime('%d-%m-%y %H-%M')).pack())],
                [InlineKeyboardButton(
                    text="Подсказки по заполнению полей",
                    callback_data=CallbackFactoryProductAddingTips(
                        user_id=callback.message.chat.id,
                        action='tip',
                        timestamp=datetime.utcnow().strftime('%d-%m-%y %H-%M')).pack())],
                [InlineKeyboardButton(
                    text="Примеры заполнения полей",
                    callback_data=CallbackFactoryProductAddingTips(
                        user_id=callback.message.chat.id,
                        action='exm',
                        timestamp=datetime.utcnow().strftime('%d-%m-%y %H-%M')).pack())],
                [InlineKeyboardButton(
                    text="ID категорий",
                    callback_data=CallbackFactoryCatIDs(
                        user_id=callback.message.chat.id,
                        timestamp=datetime.utcnow().strftime('%d-%m-%y %H-%M')).pack())]
            ]
        ),
    )


@router.callback_query(CallbackFactoryProductAddingTips.filter(), StateFilter(AdminStates.admin_start))
async def process_new_product_tips(callback: CallbackQuery, callback_data=CallbackFactoryProductAddingTips):
    fields: dict[str, str] = field_tips
    if callback_data.action == 'exm':
        fields: dict[str, str] = fields_example
    await callback.message.answer(
        text=f"{fields_formatting(fields)}",
        reply_markup=single_close_kb(callback))
    await callback.answer()


@router.callback_query(CallbackFactoryAddProductFinal.filter(), StateFilter(AdminStates.admin_start))
async def process_add_product_final(callback: CallbackQuery):
    attrs: dict = get_product_attributes(callback.message.chat.id)
    if '----' in attrs.values():
        await callback.message.answer('Вы заполнили не все поля')
        return await callback.answer()
    product_id: int = get_max_product_id_glob() + 1
    add_new_product(
        product_id=attrs['product_id'],
        product_name=attrs['product_name'],
        price=attrs['price'],
        description=attrs['description'],
        category_id=attrs['category_id'],
    )
    user_id = callback.message.chat.id
    media_links_photos = get_tmp_media(user_id, StaticContentType.IMAGE)
    media_links_videos = get_tmp_media(user_id, StaticContentType.VIDEO)
    for link in media_links_photos:
        populate_media(
            link=link,
            product_id=product_id,
            media_type=StaticContentType.IMAGE
        )
    for link in media_links_videos:
        populate_media(
            link=link,
            product_id=product_id,
            media_type=StaticContentType.VIDEO
        )

    await callback.message.answer('Товар успешно добавлен')
    del_tmp_attrs(user_id=callback.message.chat.id)
    del_tmp_media(user_id, StaticContentType.IMAGE)
    del_tmp_media(user_id, StaticContentType.VIDEO)
    _initiate_new_attributes(user_id)
    await callback.answer()


@router.callback_query(CallbackFactoryGetAttrsState.filter(), StateFilter(AdminStates.admin_start))
async def process_get_current_attrs(callback: CallbackQuery):
    attrs: dict = get_product_attributes(callback.message.chat.id)
    await callback.message.answer(
        text=f"{fields_formatting(attrs)}"
    )
    await callback.answer()


@router.callback_query(CallbackFactoryChangeExistingProduct.filter(), StateFilter(AdminStates.admin_start))
async def process_prod_change_cat_choice(callback: CallbackQuery):
    await callback.message.answer(
        text='Выберите категорию',
        reply_markup=create_categories_kb(callback))
    await callback.answer()


@router.callback_query(CallbackFactoryAlterProductTip.filter(), StateFilter(AdminStates.admin_start))
async def process_product_alter(callback: CallbackQuery):
    await callback.message.answer(
        text="Для изменения атрибутов товара воспользуйтесь командой: \n"
             "<uuid>=<название_атрибута>=<новое значение> \n\n"
             "например: \n"
             "832ecc97-1435-4b3d-601a5de58f3a=product_name=Nike AirForce 1\n\n"
             "Для просмотра доступных к редактированию полей нажмите кнопку <Доступные поля>",
        reply_markup=single_close_kb(callback)
    )
    await callback.answer()


@router.message(F.text.regexp(re.compile(r'\S{36} *= *\S+= *.+')), StateFilter(AdminStates.admin_start))
async def process_alter_attr(message: Message):
    uuid, attr, value = map(str.strip, message.text.split('='))
    alter_product_attr(
        product_uuid=uuid,
        attr_name=attr,
        value=value)
    await message.answer(
        text='Атрибут успешно обновлен'
    )


@router.callback_query(CallbackFactoryDeleteProduct.filter(), StateFilter(AdminStates.admin_start))
async def process_product_delete_tip(callback: CallbackQuery,
                                     callback_data: CallbackFactoryDeleteProduct,
                                     state: FSMContext):
    product_uuid: str = callback_data.product_uuid
    category_uuid: int = get_category_uuid_by_product_uuid(product_uuid)
    delete_product(product_uuid)
    await callback.answer(
        text='Товар удален'
    )
    await process_products_listing(
        callback=callback,
        callback_data=CallbackFactoryCategories(
            user_id=callback.message.chat.id,
            uuid=category_uuid,
            timestamp=datetime.utcnow().strftime('%d-%m-%y %H-%M')),
        state=state
    )
    await callback.answer()


@router.message(F.text.regexp(re.compile(r'image *= *.+|video * \d+ *= *.+')))
async def process_photo_add(message: Message):
    media_info, link = message.text.split('=', 1)
    user_id = message.chat.id
    media = media_info.split()
    if len(media) > 1:
        media_type, product_id = media

        product_id = int(product_id.strip())
        link = link.strip()
        populate_media(
            link=link,
            product_id=product_id,
            media_type=input_media_type_mapper[media_type]
        )

    else:
        media_type = media_info.strip()
        set_tmp_media(user_id=user_id,
                      link=link,
                      content_type=input_media_type_mapper[media_type])
    media_num = get_tmp_media_num(user_id, input_media_type_mapper[media_type])
    set_product_attribute(user_id, media_type, media_num)
    return await message.answer('Медиа успешно добавлено')


@router.message(F.text.regexp(re.compile(r'[A-Яа-я]\w+ *= *.+')), StateFilter(AdminStates.admin_start))
async def process_new_product_name(message: Message):
    attr_name, value = map(str.strip, message.text.split("="))
    if attr_name not in field_tips:
        return await message.answer('Неверная команда')
    user_id: int = message.chat.id
    set_product_attribute(user_id, attr_name, value)
    return await message.answer('Атрибут обновлен')


@router.callback_query(CallbackFactoryCatIDs.filter(), StateFilter(AdminStates.admin_start))
async def provide_cat_ids(callback: CallbackQuery):
    table: list[Row] = get_cat_ids()
    await callback.message.answer(
        text=data_listing(table, 'category_id', 'category_name'),
        reply_markup=single_close_kb(callback)
    )
    await callback.answer()
