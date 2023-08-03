from datetime import datetime
from aiogram.utils.keyboard import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram import Router
from aiogram.filters import Text
from aiogram.types import CallbackQuery, InputMediaPhoto, InputMediaVideo, Message
from keyboards.keyboards import product_action_bar, create_categories_kb, create_detalisation_kb
from filters.callbacks import CallbackFactoryCategories, CallbackFactoryStepBack, CallbackFactoryGoods, \
    CallbackFactoryProductDetails,  CallbackFactoryWindowClose
from lexicon.LEXICON import product_columns_mapper, order_listing_mapper
from middlewares.throttling import TimingMiddleware, IdMiddleware, DeviceMiddleware
from sqlalchemy import Row
from utils.utils import send_product_card
from database.methods.rel_db_methods import get_product, get_static_videos, get_user_orders, get_first_product
from models.models import PriceRepresentation, ItemListedInUserOrders
from .order_processing import print_out_formatted_row
from database.methods.redis_methods import get_user_device

# router to navigate catalog related requests
router: Router = Router()
router.callback_query.middleware(TimingMiddleware())
router.callback_query.middleware(IdMiddleware())
router.callback_query.middleware(DeviceMiddleware())
router.message.middleware((DeviceMiddleware()))


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
    print('inside process_pagination')
    if callback_data.uuid == 'not allowed':
        return await callback.answer(text='Прокрута в выбранном направлении невозможна')
    product: Row = get_product(product_uuid=callback_data.uuid)
    # if not select_last_or_first_in_category_or_none(product_uuid=callback_data.uuid, which_one='last'):
    #     return await callback.answer(text='Вы уже на последней странице')
    # elif not select_last_or_first_in_category_or_none(product_uuid=callback_data.uuid, which_one='first'):
    #     return await callback.answer(text='Вы уже на первой странице')
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


@router.message(Text('Мои заказы 📖'))
async def process_my_orders_button(message: Message):
    user_id = message.chat.id
    user_orders = get_user_orders(user_id)
    print(user_orders)
    if not user_orders:
        return await message.answer('У вас еще нет заказов')
    ordered_items = [ItemListedInUserOrders(
        order_number=item.order_number,
        order_date=item.order_start_date,
        product_name=item.product_name,
        quantity=item.quantity,
        price=PriceRepresentation(item.quantity * item.price, 'руб'),
        order_status=item.order_status_name) for item in user_orders]
    device = get_user_device(user_id)
    summary = print_out_formatted_row(attribute_names=list(order_listing_mapper.values()),
                                      cart_items=ordered_items,
                                      mapper=order_listing_mapper,
                                      device=device)
    print(summary)
    await message.answer(text=summary,
                         reply_markup=InlineKeyboardMarkup(
                             inline_keyboard=[
                                 [InlineKeyboardButton(
                                     text='Закрыть',
                                     callback_data=CallbackFactoryWindowClose(
                                         user_id=user_id,
                                         timestamp=datetime.utcnow().strftime(
                                             '%d-%m-%y %H-%M')
                                     ).pack())]]),
                         parse_mode='HTML')
