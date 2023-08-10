from aiogram.utils.keyboard import KeyboardButton, ReplyKeyboardBuilder, InlineKeyboardButton, InlineKeyboardBuilder, \
    ReplyKeyboardMarkup, InlineKeyboardMarkup
from lexicon.LEXICON import static_keyboard
from aiogram.types import Message, CallbackQuery
from datetime import datetime
from database.methods.rel_db_methods import get_categories, get_first_product, get_previous_product_uuid, \
    get_next_product_uuid, get_max_product_id, get_category_uuid_by_product_uuid, get_current_product_num_id, \
    get_product
from typing import Sequence
from aiogram.fsm.context import FSMContext
from database.methods.redis_methods import get_user_cart, add_to_cart, get_favorite
from models.models import SelectedDevice
from filters.admin_callbacks import CallbackFactoryAddCategory, CallbackFactoryDelCategory, CallbackFactoryDeletedCat, \
    CallbackFactoryAlterProductTip, CallbackFactoryProductAddingTips, CallbackFactoryDeleteProduct, \
    CallbackFactoryActiveOrders, CallbackFactoryStatusList
from models.models import CategoryActions
from database.admin_methods.rel_bd_admin_methods import get_existing_categories
from filters.callbacks import CallbackFactoryProductDetails, CallbackFactoryStepBack, CallbackFactoryWindowClose
from lexicon.A_LEXICON import field_tips
from keyboards.user_keyboards import create_pagination
from filters.callbacks import CallbackFactoryGoods


def create_admin_categories_actions_kb(message: Message):
    kb: InlineKeyboardBuilder = InlineKeyboardBuilder()
    button_1: InlineKeyboardButton = InlineKeyboardButton(
        text="Добавить категорию",
        callback_data=CallbackFactoryAddCategory(
            user_id=message.chat.id,
            timestamp=datetime.utcnow().strftime('%d-%m-%y %H-%M')).pack())

    button_2: InlineKeyboardButton = InlineKeyboardButton(
        text="Удалить категорию",
        callback_data=CallbackFactoryDelCategory(
            user_id=message.chat.id,
            timestamp=datetime.utcnow().strftime('%d-%m-%y %H-%M')).pack())

    kb.add(button_1, button_2)
    kb.adjust(1, repeat=True)

    return kb.as_markup()


def create_categories_deletion_kb(callback: CallbackQuery):
    kb: InlineKeyboardBuilder = InlineKeyboardBuilder()
    categories = get_existing_categories()
    buttons = [InlineKeyboardButton(
        text=item.category_name,
        callback_data=CallbackFactoryDeletedCat(
            user_id=callback.message.chat.id,
            cat_id=item.category_id,
            timestamp=datetime.utcnow().strftime('%d-%m-%y %H-%M')).pack()) for item in categories]

    kb.add(*buttons)
    kb.adjust(1, repeat=True)
    return kb.as_markup()


def product_action_bar_admin(
        update: CallbackQuery,
        category_uuid: int | str = None,
        product_uuid: str = None,
        **keyboard_options):
    if category_uuid is not None:
        product_uuid = get_first_product(category_uuid=category_uuid).product_uuid
    user_id = update.message.chat.id
    kb: InlineKeyboardBuilder = InlineKeyboardBuilder()
    buttons: list[InlineKeyboardButton] = [
        InlineKeyboardButton(
            text=f"Подсказка по изменению полей",
            callback_data=CallbackFactoryAlterProductTip(
                user_id=update.from_user.id,
                timestamp=datetime.utcnow().strftime(
                    '%d-%m-%y %H-%M')
            ).pack()),
        InlineKeyboardButton(
            text="Доступные поля",
            callback_data=CallbackFactoryProductAddingTips(
                user_id=update.message.chat.id,
                action='tip',
                timestamp=datetime.utcnow().strftime('%d-%m-%y %H-%M')).pack()),
        InlineKeyboardButton(
            text=f"Подсказка по удалению товара",
            callback_data=CallbackFactoryDeleteProduct(
                user_id=update.from_user.id,
                timestamp=datetime.utcnow().strftime(
                    '%d-%m-%y %H-%M')
            ).pack()),
        InlineKeyboardButton(
            text=f"Подробнее о товаре",
            callback_data=CallbackFactoryProductDetails(
                user_id=update.from_user.id,
                uuid=product_uuid,
                timestamp=datetime.utcnow().strftime(
                    '%d-%m-%y %H-%M')
            ).pack()),
    ]
    # buttons.extend([InlineKeyboardButton(
    #     text=f"Изменить {value}",
    #     callback_data=CallbackFactoryAlterProductAttr(
    #         user_id=user_id,
    #         attr=key,
    #         timestamp=datetime.utcnow().strftime('%d-%m-%y %H-%M')).pack()) for key, value in field_tips.items()])

    buttons.extend(create_pagination(update=update,
                                     product_uuid=product_uuid))
    buttons.append(InlineKeyboardButton(
        text="Назад",
        callback_data=CallbackFactoryStepBack(
            user_id=update.from_user.id,
            timestamp=datetime.utcnow().strftime('%d-%m-%y %H-%M')
        ).pack()))
    kb.add(*buttons)
    kb.adjust(1, 1, 1, 1, 3)
    return kb.as_markup()


def create_detalisation_kb_admin(callback_data: CallbackFactoryProductDetails) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(
                text='Назад',
                callback_data=CallbackFactoryGoods(
                    user_id=callback_data.user_id,
                    uuid=callback_data.uuid,
                    timestamp=datetime.utcnow().strftime('%d-%m-%y %H-%M')
                ).pack()),
            ]])


def single_close_kb(callback: CallbackQuery) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(
                text='Закрыть',
                callback_data=CallbackFactoryWindowClose(
                    user_id=callback.message.chat.id,
                    timestamp=datetime.utcnow().strftime('%d-%m-%y %H-%M')).pack())]])


def order_status_change_kb(message: Message):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(
                text='Активные заказы',
                callback_data=CallbackFactoryActiveOrders(
                    user_id=message.chat.id,
                    timestamp=datetime.utcnow().strftime('%d-%m-%y %H-%M')).pack())],
            [InlineKeyboardButton(
                text='Список статусов',
                callback_data=CallbackFactoryStatusList(
                    user_id=message.chat.id,
                    timestamp=datetime.utcnow().strftime('%d-%m-%y %H-%M')).pack())]
        ])
