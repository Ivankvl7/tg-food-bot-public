import datetime
import re
from aiogram.utils.keyboard import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram import F
from aiogram.filters import Text
from aiogram.types import CallbackQuery, InputMediaPhoto, InputMediaVideo, Message
from aiogram import Router
from keyboards.keyboards import product_action_bar, create_cart_kb, create_categories_kb, create_detalisation_kb
from filters.callbacks import CallbackFactoryCategories, CallbackFactoryStepBack, CallbackFactoryGoods, \
    CallbackFactoryProductDetails, CallbackFactoryAddToCart, CallbackFactoryFinalizeOrder, \
    CallbackFactoryCartProductSwap, CallbackFactoryQuantityChange, CallbackFactoryProductDetailsFromCart, \
    CallbackFactoryAddToFavorite
from models.methods import get_first_product
from lexicon.LEXICON import product_columns_mapper
from middlewares.throttling import TimingMiddleware, IdMiddleware
from sqlalchemy import Row
from utils.utils import send_product_card, send_product_card_cart_item
from models.methods import get_product, get_static_videos, get_category_uuid_by_product_uuid, get_category
from database.tmp_database import cart
from utils.order_items import CartItem, PriceRepresentation

# router to navigate catalog related requests
router: Router = Router()
router.callback_query.middleware(TimingMiddleware())
router.callback_query.middleware(IdMiddleware())


@router.callback_query(CallbackFactoryCategories.filter())
async def process_products_listing(callback: CallbackQuery, callback_data: CallbackFactoryCategories):
    print('inside product listing')

    print(f"callback.message.from_user.id = {callback.message.from_user.id}")
    print(f"callback.from_user.id = {callback.from_user.id}")
    print(f"callback_data.user_id = {callback_data.user_id}")
    product: Row = get_first_product(category_uuid=callback_data.uuid)
    await send_product_card(update=callback,
                            kb=product_action_bar,
                            product=product)
    print('product listing finished')
    await callback.answer()


@router.callback_query(CallbackFactoryStepBack.filter())
async def get_back_into_categories(callback: CallbackQuery):
    print('inside get_back_into_categories')
    await callback.message.answer(text="Ниже представлены доступные категории товаров",
                                  reply_markup=create_categories_kb(callback))
    print('get_back_into_categories finished')
    await callback.answer()


@router.callback_query(CallbackFactoryGoods.filter())
async def process_pagination(callback: CallbackQuery, callback_data: CallbackFactoryGoods):
    product: Row = get_product(product_uuid=callback_data.uuid)
    print('inside process_pagination')
    await send_product_card(update=callback,
                            kb=product_action_bar,
                            product=product)
    print('process_pagination finished')
    print(callback_data.pack(), len(callback_data.pack()))
    await callback.answer()


@router.callback_query(CallbackFactoryProductDetails.filter())
async def process_detalization_button(callback: CallbackQuery, callback_data: CallbackFactoryProductDetails):
    product: Row = get_product(product_uuid=callback_data.uuid)
    media_group_photos = [
        InputMediaPhoto(caption='\n'.join([f"<b>{value}</b>: {getattr(product, key)}" for key, value in
                                           product_columns_mapper.items()]),
                        parse_mode='HTML',
                        media='https://static.ebayinc.com/static/assets/Uploads/Stories/Articles/_resampled/ScaleWidthWzgwMF0/ebay-authenticity-guarantee-fine-jewelry.jpg'),
        InputMediaPhoto(
            media='https://static.ebayinc.com/static/assets/Uploads/Stories/Articles/_resampled/ScaleWidthWzgwMF0/ebay-authenticity-guarantee-fine-jewelry.jpg'),
    ]
    media_group_videos = [
        InputMediaVideo(media=f"{url}") for url in get_static_videos(callback_data.uuid)
    ]
    for url in media_group_videos:
        print(url)
    await callback.message.answer_media_group(media=media_group_videos)
    await callback.message.answer_media_group(media=media_group_photos)
    await callback.message.answer(text='Кликните <Назад>, чтобы вернуться к просмотру товаров',
                                  reply_markup=create_detalisation_kb(callback_data=callback_data))
    await callback.answer()


@router.callback_query(CallbackFactoryAddToCart.filter())
async def process_add_to_cart_button(callback: CallbackQuery, callback_data: CallbackFactoryAddToCart):
    user_id = callback.from_user.id
    product = get_product(callback_data.uuid)
    if user_id not in cart:
        cart[user_id] = list()
    item = CartItem(
        product_name=product.product_name,
        category_name=get_category(get_category_uuid_by_product_uuid(callback_data.uuid)),
        description=product.description,
        price=PriceRepresentation(product.price, 'rubles'),
        quantity=1,
        product_uuid=product.product_uuid)
    flag = True
    for cart_item in cart[user_id]:
        if cart_item == item:
            cart_item.quantity += 1
            flag = False
    if flag is True:
        cart[user_id].append(item)
    await callback.answer('Добавлено в корзину')


@router.callback_query(CallbackFactoryFinalizeOrder.filter())
async def process_finalize_order_button(update: CallbackQuery,
                                        callback_data: CallbackFactoryFinalizeOrder = None):
    print('inside process_finalize_order_button')
    user_id = update.from_user.id
    print('current_index=0')
    print(cart[user_id])
    print(callback_data)
    if user_id not in cart:
        return await update.answer('Корзина пуста', show_alert=True)
    else:
        product = cart[user_id][0]
        await send_product_card_cart_item(update=update,
                                          kb=create_cart_kb,
                                          product=product,
                                          index=0,
                                          callback_data=callback_data)
    await update.answer()
    print('process_finalize_order_button finished')


@router.callback_query(CallbackFactoryProductDetailsFromCart.filter())
async def process_product_details_from_cart_button(callback: CallbackQuery,
                                                   callback_data: CallbackFactoryProductDetailsFromCart):




@router.callback_query(CallbackFactoryCartProductSwap.filter())
async def process_product_cart_swap(callback: CallbackQuery, callback_data: CallbackFactoryCartProductSwap):
    print('inside process_product_cart_swap')
    current_index = int(callback_data.index)
    product = cart[callback_data.user_id][current_index]
    user_id = callback_data.user_id
    print(current_index)
    print(cart[user_id])
    print(callback_data)
    if user_id not in cart:
        return await callback.answer('Корзина пуста', show_alert=True)
    if callback_data.direction == '<<':
        if current_index < 0:
            return await callback.answer('Вы уже на первой странице')

    elif callback_data.direction == '>>':
        if current_index == len(cart[user_id]):
            return await callback.answer('Вы уже на последней странице')

    await send_product_card_cart_item(update=callback,
                                      kb=create_cart_kb,
                                      index=current_index,
                                      product=product,
                                      callback_data=callback_data)


    print('finished process_product_cart_swap')
    await callback.answer()
