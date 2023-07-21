from aiogram.utils.keyboard import KeyboardButton, ReplyKeyboardBuilder, InlineKeyboardButton, InlineKeyboardBuilder, \
    ReplyKeyboardMarkup, InlineKeyboardMarkup
from lexicon.LEXICON import pagination_buttons, product_action_buttons, special_buttons, static_keyboard
from aiogram.types import TelegramObject, Message, CallbackQuery
from datetime import datetime
from lexicon.LEXICON import categories_uuid
from filters.callbacks import CallbackFactoryCategories, CallbackFactoryProductDetails, CallbackFactoryGoods, \
    CallbackFactoryStepBack, CallbackFactoryAddToCart, CallbackFactoryAddToFavorite, CallbackFactoryFinalizeOrder, \
    CallbackFactoryCartProductSwap, CallbackFactoryQuantityChange, CallbackFactoryProductDetailsFromCart, \
    CallbackFactoryFavoriteProductsSwap, CallbackFactoryWindowClose, CallbackFactoryDeleteFromFavorite, \
    CallbackFactoryOrderConfirmation, CallbackFactorTerminateConfirmation, CallbackFactoryQuickConfirmation
from models.methods import get_categories, get_first_product, get_previous_product_uuid, get_next_product_uuid, \
    get_max_product_id, get_category_uuid_by_product_uuid, get_current_product_num_id
from typing import Sequence, Any
from database.tmp_database import cart, favorite_products
from aiogram.fsm.context import FSMContext


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
    categories: Sequence = get_categories()
    kb.add(*[InlineKeyboardButton(text=row.category_name,
                                  callback_data=CallbackFactoryCategories(
                                      user_id=user_id,
                                      uuid=row.category_uuid,
                                      timestamp=datetime.utcnow().strftime('%d-%m-%y %H-%M')
                                  ).pack())
             for row in categories])
    # kb.add(*[InlineKeyboardButton(text='Назад',
    #                               callback_data=CallbackFactoryStartPage(
    #                                   user_id=user_id,
    #                                   timestamp=datetime.utcnow().strftime('%d-%m-%y %H-%M')
    #                               ).pack())])
    kb.adjust(1, repeat=True)
    return kb.as_markup(**kwargs)


def create_pagination(update: CallbackQuery,
                      product_uuid: str):
    return [
        InlineKeyboardButton(
            text="<<",
            callback_data=CallbackFactoryGoods(
                user_id=update.from_user.id,
                uuid=get_previous_product_uuid(current_product_uuid=product_uuid),
                timestamp=datetime.utcnow().strftime('%d-%m-%y %H-%M')).pack()
        ),
        InlineKeyboardButton(
            text=f"{get_current_product_num_id(product_uuid=product_uuid)} / "
                 f"{get_max_product_id(category_uuid=get_category_uuid_by_product_uuid(product_uuid=product_uuid))}",
            callback_data='page_num'),
        InlineKeyboardButton(
            text=">>",
            callback_data=CallbackFactoryGoods(
                user_id=update.from_user.id,
                uuid=get_next_product_uuid(current_product_uuid=product_uuid),
                timestamp=datetime.utcnow().strftime('%d-%m-%y %H-%M')).pack()
        )]


def product_action_bar(update: CallbackQuery,
                       category_uuid: int | str = None,
                       product_uuid: str = None,
                       **keyboard_options):
    if category_uuid is not None:
        product_uuid = get_first_product(category_uuid=category_uuid).product_uuid

    kb: InlineKeyboardBuilder = InlineKeyboardBuilder()
    buttons: list[InlineKeyboardButton] = [
        InlineKeyboardButton(
            text=f"Подробнее о товаре",
            callback_data=CallbackFactoryProductDetails(
                user_id=update.from_user.id,
                uuid=product_uuid,
                timestamp=datetime.utcnow().strftime(
                    '%d-%m-%y %H-%M')
            ).pack()
        ),
        InlineKeyboardButton(
            text=f"Добавить в избранное",
            callback_data=CallbackFactoryAddToFavorite(
                user_id=update.from_user.id,
                uuid=product_uuid,
                timestamp=datetime.utcnow().strftime('%d-%m-%y %H-%M')
            ).pack()
        ),
        InlineKeyboardButton(
            text="Добавить в корзину",
            callback_data=CallbackFactoryAddToCart(
                user_id=update.from_user.id,
                uuid=product_uuid,
                timestamp=datetime.utcnow().strftime('%d-%m-%y %H-%M')
            ).pack()),
        InlineKeyboardButton(
            text="Оформить заказ",
            callback_data=CallbackFactoryFinalizeOrder(
                user_id=update.from_user.id,
                uuid=product_uuid,
                timestamp=datetime.utcnow().strftime('%d-%m-%y %H-%M')
            ).pack())]
    buttons.extend(create_pagination(update=update,
                                     product_uuid=product_uuid))
    buttons.append(InlineKeyboardButton(
        text="Назад",
        callback_data=CallbackFactoryStepBack(
            user_id=update.from_user.id,
            timestamp=datetime.utcnow().strftime('%d-%m-%y %H-%M')
        ).pack()))
    kb.add(*buttons)
    kb.adjust(1, 1, 2, 3)
    return kb.as_markup()


def create_detalisation_kb(callback_data: CallbackFactoryProductDetails):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(
                text='Добавить в корзину',
                callback_data=CallbackFactoryAddToCart(
                    user_id=callback_data.user_id,
                    uuid=callback_data.uuid,
                    timestamp=datetime.utcnow().strftime('%d-%m-%y %H-%M')
                ).pack())],
            [InlineKeyboardButton(
                text='Добавить в избранное',
                callback_data=CallbackFactoryAddToFavorite(
                    user_id=callback_data.user_id,
                    uuid=callback_data.uuid,
                    timestamp=datetime.utcnow().strftime('%d-%m-%y %H-%M')
                ).pack())],
            [InlineKeyboardButton(
                text="Оформить заказ",
                callback_data=CallbackFactoryFinalizeOrder(
                    user_id=callback_data.user_id,
                    uuid=callback_data.uuid,
                    timestamp=datetime.utcnow().strftime('%d-%m-%y %H-%M')
                ).pack())],
            [InlineKeyboardButton(
                text='Назад',
                callback_data=CallbackFactoryGoods(
                    user_id=callback_data.user_id,
                    uuid=callback_data.uuid,
                    timestamp=datetime.utcnow().strftime('%d-%m-%y %H-%M')
                ).pack()),
            ]])


def create_cart_kb(index: int, callback_data: CallbackFactoryFinalizeOrder | CallbackFactoryCartProductSwap):
    kb: InlineKeyboardBuilder = InlineKeyboardBuilder()
    user_id = callback_data.user_id
    index = int(index)
    if isinstance(callback_data, CallbackFactoryFinalizeOrder):
        product_uuid = callback_data.uuid
    else:

        product_uuid = cart[callback_data.user_id][index].product_uuid
    left_index = index - 1
    right_index = index + 1

    button00 = InlineKeyboardButton(text='Перейти к подтверждению заказа',
                                    callback_data=CallbackFactoryOrderConfirmation(
                                        user_id=user_id,
                                        timestamp=datetime.utcnow().strftime(
                                            '%d-%m-%y %H-%M')
                                    ).pack())
    button0 = InlineKeyboardButton(text='Подробнее о товаре',
                                   callback_data=CallbackFactoryProductDetailsFromCart(
                                       user_id=callback_data.user_id,
                                       index=index,
                                       timestamp=datetime.utcnow().strftime(
                                           '%d-%m-%y %H-%M')
                                   ).pack()
                                   )
    button1 = InlineKeyboardButton(text='-',
                                   callback_data=CallbackFactoryQuantityChange(
                                       action='-',
                                       index=index,
                                       user_id=user_id,
                                       timestamp=datetime.utcnow().strftime('%d-%m-%y %H-%M')
                                   ).pack())

    button2 = InlineKeyboardButton(text=f"В корзине: {cart[user_id][index].quantity}",
                                   callback_data='non_active_button', )
    button3 = InlineKeyboardButton(text='+',
                                   callback_data=CallbackFactoryQuantityChange(
                                       action='+',
                                       index=index,
                                       user_id=user_id,
                                       timestamp=datetime.utcnow().strftime('%d-%m-%y %H-%M')
                                   ).pack())
    button4 = InlineKeyboardButton(text='<<',
                                   callback_data=CallbackFactoryCartProductSwap(
                                       user_id=user_id,
                                       direction='<<',
                                       index=left_index,
                                       timestamp=datetime.utcnow().strftime('%d-%m-%y %H-%M')
                                   ).pack())
    button5 = InlineKeyboardButton(text=f"{index + 1} / {len(cart[user_id])}",
                                   callback_data='non_active_button', )
    button6 = InlineKeyboardButton(text='>>',
                                   callback_data=CallbackFactoryCartProductSwap(
                                       user_id=user_id,
                                       direction='>>',
                                       index=right_index,
                                       timestamp=datetime.utcnow().strftime('%d-%m-%y %H-%M')
                                   ).pack())
    button7 = InlineKeyboardButton(text='Закрыть',
                                   callback_data=CallbackFactoryWindowClose(
                                       user_id=user_id,
                                       uuid=product_uuid,
                                       timestamp=datetime.utcnow().strftime('%d-%m-%y %H-%M')
                                   ).pack())
    kb.add(button0, button00, button1, button2, button3, button4, button5, button6, button7)
    kb.adjust(1, 1, 3, 3)
    return kb.as_markup()


def create_favorite_goods_kb(update: Message | CallbackQuery, index: int | str):
    if isinstance(index, str):
        index = int(index)
    kb: InlineKeyboardBuilder = InlineKeyboardBuilder()
    user_id = update.from_user.id
    left_index = index - 1
    right_index = index + 1
    product = favorite_products[user_id][index]
    button00 = InlineKeyboardButton(text='Подробнее о товаре',
                                    callback_data=CallbackFactoryProductDetailsFromCart(
                                        user_id=user_id,
                                        index=index,
                                        timestamp=datetime.utcnow().strftime(
                                            '%d-%m-%y %H-%M')
                                    ).pack()
                                    )
    button0 = InlineKeyboardButton(text='Удалить из избранного',
                                   callback_data=CallbackFactoryDeleteFromFavorite(
                                       user_id=user_id,
                                       index=index,
                                       timestamp=datetime.utcnow().strftime(
                                           '%d-%m-%y %H-%M')
                                   ).pack()
                                   )
    button1 = InlineKeyboardButton(text='Добавить в корзину',
                                   callback_data=CallbackFactoryAddToCart(
                                       user_id=user_id,
                                       uuid=product.product_uuid,
                                       timestamp=datetime.utcnow().strftime('%d-%m-%y %H-%M')
                                   ).pack())
    button2 = InlineKeyboardButton(text='<<',
                                   callback_data=CallbackFactoryFavoriteProductsSwap(
                                       user_id=user_id,
                                       direction='<<',
                                       index=left_index,
                                       timestamp=datetime.utcnow().strftime('%d-%m-%y %H-%M')
                                   ).pack())
    button3 = InlineKeyboardButton(text=f"{index + 1} / {len(favorite_products[user_id])}",
                                   callback_data='non_active_button', )
    button4 = InlineKeyboardButton(text='>>',
                                   callback_data=CallbackFactoryFavoriteProductsSwap(
                                       user_id=user_id,
                                       direction='>>',
                                       index=right_index,
                                       timestamp=datetime.utcnow().strftime('%d-%m-%y %H-%M')
                                   ).pack())
    button5 = InlineKeyboardButton(text='Закрыть',
                                   callback_data=CallbackFactoryWindowClose(
                                       user_id=user_id,
                                       timestamp=datetime.utcnow().strftime('%d-%m-%y %H-%M')
                                   ).pack())
    kb.add(button00, button0, button1, button2, button3, button4, button5)
    kb.adjust(1, 1, 1, 3)
    return kb.as_markup()


def close_window_button(text: str,
                        update: CallbackQuery | Message,
                        state: FSMContext | None = None,
                        quick_confo: bool = False):
    if isinstance(update, CallbackQuery):
        user_id = update.message.chat.id
    else:
        user_id = update.chat.id
    if state:
        callback_data = CallbackFactorTerminateConfirmation(
            user_id=user_id,
            timestamp=datetime.utcnow().strftime(
                '%d-%m-%y %H-%M')
        ).pack()
    else:
        callback_data = CallbackFactoryWindowClose(
            user_id=user_id,
            timestamp=datetime.utcnow().strftime(
                '%d-%m-%y %H-%M')
        ).pack()
    kb = [[InlineKeyboardButton(
        text=text,
        callback_data=callback_data)]]
    if quick_confo is True:
        kb.append([InlineKeyboardButton(
            text='Подтвердить мгновенно',
            callback_data=CallbackFactoryQuickConfirmation(
                user_id=user_id,
                timestamp=datetime.utcnow().strftime(
                    '%d-%m-%y %H-%M')).pack())])

    return InlineKeyboardMarkup(
        inline_keyboard=kb)
