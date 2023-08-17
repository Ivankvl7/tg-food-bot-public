from datetime import datetime

from aiogram import Router
from aiogram.types import CallbackQuery, InputMediaPhoto, InputMediaVideo
from aiogram.utils.keyboard import InlineKeyboardMarkup, InlineKeyboardButton
from sqlalchemy import Row

from database.methods.redis_methods import add_to_cart, incr_cart_quantity, remove_item_from_cart, get_user_cart
from database.methods.rel_db_methods import get_product
from filters.callbacks import CallbackFactoryAddToCart, CallbackFactoryFinalizeOrder, CallbackFactoryCartProductSwap, \
    CallbackFactoryQuantityChange, CallbackFactoryProductDetailsFromCart
from keyboards.user_keyboards import create_cart_kb, create_categories_kb
from lexicon.LEXICON import product_columns_mapper
from middlewares.throttling import TimingMiddleware, IdMiddleware, DeviceMiddleware
from utils.utils import get_file
from utils.utils import send_product_card_cart_item
from models.models import StaticContentType

# router to navigate catalog related requests
router: Router = Router()
router.callback_query.middleware(TimingMiddleware())
router.callback_query.middleware(IdMiddleware())
router.callback_query.middleware(DeviceMiddleware())
router.message.middleware(DeviceMiddleware())


@router.callback_query(CallbackFactoryAddToCart.filter())
async def process_add_to_cart_button(callback: CallbackQuery, callback_data: CallbackFactoryAddToCart):
    user_id: str | int = callback.message.chat.id
    add_to_cart(callback_data.uuid, user_id)
    await callback.answer('Добавлено в корзину')


@router.callback_query(CallbackFactoryFinalizeOrder.filter())
async def process_finalize_order_button(update: CallbackQuery,
                                        callback_data: CallbackFactoryFinalizeOrder,
                                        ):
    user_id: str | int = update.message.chat.id
    user_cart: dict[str, str] = get_user_cart(user_id)
    product_uuids: list = list(user_cart.keys())
    if not user_cart:
        return await update.answer('Корзина пуста', show_alert=True)

    else:
        product_uuid: str = product_uuids[0]
        product: Row = get_product(product_uuid)
        await send_product_card_cart_item(update=update,
                                          kb=create_cart_kb,
                                          product=product,
                                          index=0,
                                          callback_data=callback_data,
                                          )
    await update.answer()


def get_media_group(uuids_seq: dict | list, index: int, user_id: int):
    product_uuids: list = list(uuids_seq)
    product: Row = get_product(product_uuids[index])
    media_group_photos = [
        InputMediaPhoto(caption='\n'.join([f"<b>{value}</b>: {getattr(product, key)}" for key, value in
                                           product_columns_mapper.items()]),
                        parse_mode='HTML',
                        media=get_file(product, user_id)),
    ]
    media_group_videos = [
        InputMediaVideo(media=get_file(product, user_id, content_type=StaticContentType.VIDEO))]
    return media_group_photos, media_group_videos


@router.callback_query(CallbackFactoryProductDetailsFromCart.filter())
async def process_product_details_from_cart_button(callback: CallbackQuery,
                                                   callback_data: CallbackFactoryProductDetailsFromCart):
    user_id: int = callback_data.user_id
    user_cart: dict = get_user_cart(user_id)
    if not user_cart:
        return await callback.answer('Корзина пуста', show_alert=True)
    if callback_data.index == 0:
        index: int = callback_data.index
    else:
        index: int = callback_data.index - 1

    media_group_photos, media_group_videos = get_media_group(uuids_seq=user_cart,
                                                             index=index,
                                                             user_id=user_id)

    await callback.message.answer_media_group(media=media_group_videos)
    await callback.message.answer_media_group(media=media_group_photos)
    await callback.message.answer(text='Кликните <Назад>, чтобы вернуться в корзину,',
                                  reply_markup=InlineKeyboardMarkup(
                                      inline_keyboard=[[InlineKeyboardButton(text='Назад',
                                                                             callback_data=CallbackFactoryCartProductSwap(
                                                                                 user_id=user_id,
                                                                                 direction='>>',
                                                                                 index=index,
                                                                                 timestamp=datetime.utcnow().strftime(
                                                                                     '%d-%m-%y %H-%M')

                                                                             ).pack())]]))

    await callback.answer()


@router.callback_query(CallbackFactoryCartProductSwap.filter())
async def process_product_cart_swap(callback: CallbackQuery, callback_data: CallbackFactoryCartProductSwap):
    index: int = int(callback_data.index)
    user_id: int = callback_data.user_id
    user_cart: dict[str, str] = get_user_cart(user_id)
    product_uuids: list = list(user_cart.keys())
    if not user_cart:
        return await callback.answer('Корзина пуста', show_alert=True)
    if callback_data.direction == '<<':
        if index < 0:
            return await callback.answer('Вы уже на первой странице')

    elif callback_data.direction == '>>':
        if index == len(user_cart):
            return await callback.answer('Вы уже на последней странице')
    product: Row = get_product(product_uuids[index])
    await send_product_card_cart_item(update=callback,
                                      kb=create_cart_kb,
                                      index=index,
                                      product=product,
                                      callback_data=callback_data)
    await callback.answer()


@router.callback_query(CallbackFactoryQuantityChange.filter())
async def process_quantity_change_button(callback: CallbackQuery, callback_data: CallbackFactoryQuantityChange):
    user_id: int = callback_data.user_id
    user_cart: dict[str, str] = get_user_cart(user_id)
    index: int = int(callback_data.index)
    product_uuid: str = list(user_cart.keys())[index]
    item: Row = get_product(product_uuid)
    if not user_cart:
        return await callback.answer('Корзина пуста', show_alert=True)
    quantity: int = int(user_cart[product_uuid])

    if callback_data.action == '+':
        incr_cart_quantity(user_id, product_uuid)
    elif callback_data.action == '-':
        if quantity == 1:
            remove_item_from_cart(user_id, product_uuid)
            await callback.answer('Товар удален из корзины')
        else:
            incr_cart_quantity(user_id, product_uuid, -1)
    user_cart: dict = get_user_cart(user_id)
    if user_cart:
        if product_uuid not in user_cart:
            first_product_in_cart: str = list(user_cart.keys())[0]
            item: Row = get_product(first_product_in_cart)
            index: int = 0
        await send_product_card_cart_item(update=callback,
                                          kb=create_cart_kb,
                                          product=item,
                                          index=index,
                                          callback_data=CallbackFactoryFinalizeOrder(
                                              user_id=user_id,
                                              uuid=item.product_uuid,
                                              timestamp=datetime.utcnow().strftime(
                                                  '%d-%m-%y %H-%M')
                                          ))
        if callback_data.action == '+':
            await callback.answer('Количество товара увеличено', cache_time=2)
        elif callback_data.action == '-':
            await callback.answer('Количество товара уменьшено', cache_time=2)

    if not user_cart:
        await callback.message.answer(text="Ниже представлены доступные категории товаров",
                                      reply_markup=create_categories_kb(callback))
    await callback.answer()
