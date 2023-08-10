import re
from datetime import datetime

from aiogram import Router, F
from aiogram.filters import Text
from aiogram.types import CallbackQuery, Message
from aiogram.utils.keyboard import InlineKeyboardButton, InlineKeyboardMarkup

from database.admin_methods.redis_admin_methods import get_product_attributes, set_product_attribute
from database.admin_methods.rel_bd_admin_methods import get_max_product_id_glob, add_new_product, alter_product_attr, \
    delete_product
from filters.admin_callbacks import CallbackFactoryAddProduct, CallbackFactoryProductAddingTips, \
    CallbackFactoryAddProductFinal, CallbackFactoryGetAttrsState, CallbackFactoryChangeExistingProduct, \
    CallbackFactoryAlterProductTip, CallbackFactoryDeleteProduct
from keyboards.user_keyboards import create_categories_kb
from lexicon.A_LEXICON import field_tips, fields_example
from middlewares.throttling import TimingMiddleware, IdMiddleware, DeviceMiddleware, AdminModeMiddleware
from models.models import AdminStaticKb
from aiogram.filters.state import StateFilter
from states.admin_states import AdminStates
from keyboards.admin_keyboards import single_close_kb

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
    user_id = message.chat.id
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


@router.callback_query(CallbackFactoryAddProduct.filter(), StateFilter(AdminStates.admin_start))
async def process_add_product_start(callback: CallbackQuery):
    user_id: int = callback.message.chat.id
    attributes = get_product_attributes(user_id)
    for key in field_tips:
        if key not in attributes:
            set_product_attribute(callback.message.chat.id, key, '----')
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


@router.message(F.text.regexp(re.compile(r'delete *= *\S{36}')), StateFilter(AdminStates.admin_start))
async def process_product_deletion(message: Message):
    _, product_uuid = map(str.strip, message.text.split('='))
    delete_product(product_uuid)
    await message.answer(
        text='Товар успешно удален'
    )


@router.message(F.text.regexp(re.compile(r'[A-Яа-я]\w+ *= *.+')), StateFilter(AdminStates.admin_start))
async def process_new_product_name(message: Message):
    attr_name, value = map(str.strip, message.text.split("="))
    user_id: int = message.chat.id
    set_product_attribute(user_id, attr_name, value)
    return await message.answer('Атрибут обновлен')


@router.callback_query(CallbackFactoryAddProductFinal.filter(), StateFilter(AdminStates.admin_start))
async def process_add_product_final(callback: CallbackQuery):
    attrs: dict = get_product_attributes(callback.message.chat.id)
    if '----' in attrs.values():
        await callback.message.answer('Вы заполнили не все поля')
        return await callback.answer()
    product_id: int = get_max_product_id_glob() + 1
    add_new_product(
        product_id=product_id,
        product_name=attrs['product_name'],
        price=attrs['price'],
        description=attrs['description'],
        category_id=attrs['category_id'],
        article=attrs['article'],
        detailed_description=attrs['detailed_description']
    )
    await callback.message.answer('Товар успешно добавлен')
    await callback.answer()


@router.callback_query(CallbackFactoryGetAttrsState.filter(), StateFilter(AdminStates.admin_start))
async def process_get_current_attrs(callback: CallbackQuery):
    attrs = get_product_attributes(callback.message.chat.id)
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
async def process_product_delete_tip(callback: CallbackQuery):
    await callback.message.answer(
        text="Для удаления товара воспользуйтесь командой: \n"
             "delete=<product_uuid>\n\n"
             "например:\n"
             "delete=832ecc97-1435",
        reply_markup=single_close_kb(callback)
    )
    await callback.answer()
