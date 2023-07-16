from aiogram.utils.keyboard import KeyboardButton, ReplyKeyboardBuilder, InlineKeyboardButton, InlineKeyboardBuilder, \
    ReplyKeyboardMarkup, InlineKeyboardMarkup
from lexicon.LEXICON import pagination_buttons, product_action_buttons, special_buttons, static_keyboard
from aiogram.types import TelegramObject, Message, CallbackQuery
from datetime import datetime
from lexicon.LEXICON import categories_uuid
from filters.callbacks import CallbackFactoryCategories, CallbackFactoryProductDetails, CallbackFactoryGoods, \
    CallbackFactoryStepBack
from models.methods import select_categories, select_max_product_id, select_product
from typing import Sequence


def static_common_buttons_menu(**keyboard_options) -> ReplyKeyboardMarkup:
    # creating buttons for main page keyboard
    buttons: list[KeyboardButton] = [KeyboardButton(text=static_keyboard[key]) for key in static_keyboard.keys()]

    # creating kb builder
    static_common_menu: ReplyKeyboardBuilder = ReplyKeyboardBuilder()

    # adding buttons to the builder
    static_common_menu.add(*buttons)
    static_common_menu.adjust(1, repeat=True)

    return static_common_menu.as_markup(**keyboard_options)


def create_categories_kb(update: CallbackQuery | Message, **kwargs):
    if isinstance(update, CallbackQuery):
        user_id = update.from_user.id
        print('inside create_categories_kb; update=CallbackQuery; user_id = update.from_user.id')
    else:
        user_id = update.from_user.id
        print('inside create_categories_kb; update = Message; user_id = update.from_user.id')
    kb: InlineKeyboardBuilder = InlineKeyboardBuilder()
    categories: Sequence = select_categories()
    kb.add(*[InlineKeyboardButton(text=row.name,
                                  callback_data=CallbackFactoryCategories(
                                      user_id=user_id,
                                      uuid=row.uuid,
                                      timestamp=datetime.utcnow().strftime('%d-%m-%y %H-%M')
                                  ).pack())
             for row in categories])
    kb.adjust(1, repeat=True)
    return kb.as_markup(**kwargs)


def product_action_bar(category_uuid: int | str, update: CallbackQuery, product_id: int | str = 1, **keyboard_options):
    kb: InlineKeyboardBuilder = InlineKeyboardBuilder()
    buttons: list[InlineKeyboardButton] = [InlineKeyboardButton(text=value,
                                                                callback_data=key) for key, value in
                                           product_action_buttons.items()]
    new_product_id = product_id
    if product_id > 1:
        new_product_id = product_id - 1
    buttons[2] = InlineKeyboardButton(text="<<",
                                      callback_data=CallbackFactoryGoods(
                                          user_id=update.from_user.id,
                                          uuid=select_product(category_uuid=category_uuid,
                                                              product_id=new_product_id).uuid,
                                          timestamp=datetime.utcnow().strftime('%d-%m-%y %H-%M')).pack()
                                      )
    if product_id < select_max_product_id(category_uuid=category_uuid):
        new_product_id = product_id + 1
    buttons[3] = InlineKeyboardButton(text=">>",
                                      callback_data=CallbackFactoryGoods(
                                          user_id=update.from_user.id,
                                          uuid=select_product(category_uuid=category_uuid,
                                                              product_id=new_product_id).uuid,
                                          timestamp=datetime.utcnow().strftime('%d-%m-%y %H-%M')).pack()
                                      )

    buttons.insert(3, InlineKeyboardButton(text=f"{product_id} / {select_max_product_id(category_uuid=category_uuid)}",
                                           callback_data='add_to_favorite'))
    buttons.insert(0, InlineKeyboardButton(text=f"Подробнее о товаре",
                                           callback_data=CallbackFactoryProductDetails(
                                               user_id=update.from_user.id,
                                               uuid=select_product(category_uuid=category_uuid,
                                                                   product_id=product_id).uuid,
                                               timestamp=datetime.utcnow().strftime('%d-%m-%y %H-%M')
                                           ).pack()
                                           )
                   )
    buttons[-1] = InlineKeyboardButton(text="Назад",
                                       callback_data=CallbackFactoryStepBack(
                                           user_id=update.from_user.id,
                                           timestamp=datetime.utcnow().strftime('%d-%m-%y %H-%M')
                                       ).pack())
    kb.add(*buttons)
    kb.adjust(1, 2, 3)
    return kb.as_markup()
