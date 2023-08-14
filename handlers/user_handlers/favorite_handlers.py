from datetime import datetime

from aiogram import Router
from aiogram.types import CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardButton, InlineKeyboardMarkup
from sqlalchemy import Row

from database.methods.redis_methods import get_favorite, add_to_favorite, remove_from_favorite
from database.methods.rel_db_methods import get_product
from filters.callbacks import CallbackFactoryAddToFavorite, CallbackFactoryFavoriteProductsSwap, \
    CallbackFactoryGetProductDetailsFromFavorite, CallbackFactoryDeleteFromFavorite
from keyboards.user_keyboards import create_favorite_goods_kb, create_categories_kb
from middlewares.throttling import TimingMiddleware, IdMiddleware, DeviceMiddleware
from utils.utils import send_product_card_favorite_items
from .cart_handlers import get_media_group

# router to navigate catalog related requests
router: Router = Router()
router.callback_query.middleware(TimingMiddleware())
router.callback_query.middleware(IdMiddleware())
router.callback_query.middleware(DeviceMiddleware())
router.message.middleware((DeviceMiddleware()))


@router.callback_query(CallbackFactoryAddToFavorite.filter())
async def process_add_to_favorite_button(callback: CallbackQuery, callback_data: CallbackFactoryAddToFavorite):
    user_id: int = callback.message.chat.id
    product_to_add: str = callback_data.uuid
    user_favorite: list[str] = get_favorite(user_id)
    if product_to_add in user_favorite:
        return await callback.answer(text='Товар уже в избранном')
    add_to_favorite(user_id, product_to_add)
    await callback.answer(text='Товар добавлен в избранное')


@router.callback_query(CallbackFactoryFavoriteProductsSwap.filter())
async def process_favorite_product_swap_button(callback: CallbackQuery,
                                               callback_data: CallbackFactoryFavoriteProductsSwap):
    current_index: int = int(callback_data.index)
    user_id: int = callback_data.user_id
    user_favorite: list[str] = get_favorite(user_id)
    if not user_favorite:
        return await callback.answer('В избранном ничего нет')
    if callback_data.direction == '<<':
        if current_index < 0:
            return await callback.answer('Вы уже на первой странице')
    elif callback_data.direction == '>>':
        if current_index == len(user_favorite):
            return await callback.answer('Вы уже на последней странице')
    product: Row = get_product(user_favorite[current_index])
    await send_product_card_favorite_items(update=callback,
                                           kb=create_favorite_goods_kb,
                                           index=current_index,
                                           product=product)

    await callback.answer()


@router.callback_query(CallbackFactoryGetProductDetailsFromFavorite.filter())
async def process_product_details_from_favorite_button(callback: CallbackQuery,
                                                       callback_data: CallbackFactoryGetProductDetailsFromFavorite):
    user_id: int = callback_data.user_id
    user_favorite: list[str] = get_favorite(user_id)
    if not user_favorite:
        return await callback.answer('Корзина пуста', show_alert=True)
    index: int = callback_data.index
    media_group_photos, media_group_videos = get_media_group(uuids_seq=user_favorite,
                                                             index=index)
    await callback.message.answer_media_group(media=media_group_videos)
    await callback.message.answer_media_group(media=media_group_photos)
    await callback.message.answer(text='Кликните <Назад>, чтобы вернуться в избранное,',
                                  reply_markup=InlineKeyboardMarkup(
                                      inline_keyboard=[[InlineKeyboardButton(text='Назад',
                                                                             callback_data=CallbackFactoryFavoriteProductsSwap(
                                                                                 user_id=user_id,
                                                                                 direction=">>",
                                                                                 index=index,
                                                                                 timestamp=datetime.utcnow().strftime(
                                                                                     '%d-%m-%y %H-%M')

                                                                             ).pack())]]))

    await callback.answer()


@router.callback_query(CallbackFactoryDeleteFromFavorite.filter())
async def process_del_from_favorite_button(callback: CallbackQuery, callback_data: CallbackFactoryDeleteFromFavorite):
    index = int(callback_data.index)
    user_id: int = callback.message.chat.id
    user_favorite: list[str] = get_favorite(user_id)
    if not user_favorite:
        return await callback.answer(text='В избранном ничего нет')
    if len(user_favorite) == 1:
        remove_from_favorite(user_id, user_favorite[index])
        await callback.answer(text='В избранном больше ничего нет')
        await callback.message.answer(text="Ниже представлены доступные категории товаров",
                                      reply_markup=create_categories_kb(callback))
    else:
        remove_from_favorite(user_id, user_favorite[index])
        user_favorite: list[str] = get_favorite(user_id)
        product: Row = get_product(user_favorite[0])
        await send_product_card_favorite_items(update=callback,
                                               kb=create_favorite_goods_kb,
                                               product=product
                                               )
        await callback.answer()
