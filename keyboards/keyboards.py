from aiogram.utils.keyboard import KeyboardButton, ReplyKeyboardBuilder, InlineKeyboardButton, InlineKeyboardBuilder, \
    ReplyKeyboardMarkup, InlineKeyboardMarkup
from lexicon.LEXICON import static_keyboard
from aiogram.types import Message, CallbackQuery
from datetime import datetime
from filters.callbacks import CallbackFactoryCategories, CallbackFactoryProductDetails, CallbackFactoryGoods, \
    CallbackFactoryStepBack, CallbackFactoryAddToCart, CallbackFactoryAddToFavorite, CallbackFactoryFinalizeOrder, \
    CallbackFactoryCartProductSwap, CallbackFactoryQuantityChange, CallbackFactoryProductDetailsFromCart, \
    CallbackFactoryFavoriteProductsSwap, CallbackFactoryWindowClose, CallbackFactoryDeleteFromFavorite, \
    CallbackFactoryOrderConfirmation, CallbackFactorTerminateConfirmation, CallbackFactoryQuickConfirmation, \
    CallbackFactoryGetProductDetailsFromFavorite, CallbackFactoryDeviceSelection
from database.methods.rel_db_methods import get_categories, get_first_product, get_previous_product_uuid, \
    get_next_product_uuid, get_max_product_id, get_category_uuid_by_product_uuid, get_current_product_num_id, \
    get_product
from typing import Sequence
from aiogram.fsm.context import FSMContext
from database.methods.redis_methods import get_user_cart, add_to_cart, get_favorite
from models.models import SelectedDevice


def static_common_buttons_menu(**keyboard_options) -> ReplyKeyboardMarkup:
    # creating buttons for persistent kb
    buttons: list[KeyboardButton] = [KeyboardButton(text=static_keyboard[key]) for key in static_keyboard]

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
    user_cart = get_user_cart(user_id)
    product_uuid = list(user_cart.keys())[index]
    left_index = index - 1
    right_index = index + 1
    quantity = user_cart[product_uuid]

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

    button2 = InlineKeyboardButton(text=f"В корзине: {quantity}",
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
    button5 = InlineKeyboardButton(text=f"{index + 1} / {len(user_cart.keys())}",
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
    if isinstance(update, CallbackQuery):
        user_id = update.message.chat.id
    else:
        user_id = update.chat.id
    user_favorite = list(get_favorite(user_id))

    left_index = index - 1
    right_index = index + 1
    product = get_product(user_favorite[index])
    button00 = InlineKeyboardButton(text='Подробнее о товаре',
                                    callback_data=CallbackFactoryGetProductDetailsFromFavorite(
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
    button3 = InlineKeyboardButton(text=f"{index + 1} / {len(user_favorite)}",
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
                        quick_confo: bool = False) -> InlineKeyboardMarkup:
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


def create_device_selection_kb(user_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(
                text=SelectedDevice.DESKTOP.value,
                callback_data=CallbackFactoryDeviceSelection(
                    user_id=user_id,
                    device=SelectedDevice.DESKTOP.value,
                    timestamp=datetime.utcnow().strftime('%d-%m-%y %H-%M')
                ).pack()
            )],
            [InlineKeyboardButton(
                text=SelectedDevice.MOBILE_DEVICE.value,
                callback_data=CallbackFactoryDeviceSelection(
                    user_id=user_id,
                    device=SelectedDevice.MOBILE_DEVICE.value,
                    timestamp=datetime.utcnow().strftime('%d-%m-%y %H-%M')
                ).pack()
            )]
        ]
    )
