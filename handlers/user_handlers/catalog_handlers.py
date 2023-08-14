from datetime import datetime
from typing import Callable, Sequence

from aiogram import Router
from aiogram.filters import Text
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InputMediaPhoto, InputMediaVideo, Message
from aiogram.utils.keyboard import InlineKeyboardMarkup, InlineKeyboardButton
from sqlalchemy import Row

from database.methods.redis_methods import get_user_device
from database.methods.rel_db_methods import get_product, get_user_orders, get_first_product
from filters.callbacks import CallbackFactoryCategories, CallbackFactoryStepBack, CallbackFactoryGoods, \
    CallbackFactoryProductDetails, CallbackFactoryWindowClose
from keyboards.admin_keyboards import product_action_bar_admin
from keyboards.user_keyboards import product_action_bar, create_categories_kb, create_detalisation_kb
from lexicon.LEXICON import product_columns_mapper, order_listing_mapper
from middlewares.throttling import TimingMiddleware, IdMiddleware, DeviceMiddleware
from models.models import PriceRepresentation, ItemListedInUserOrders
from states.admin_states import AdminStates
from utils.populate_with_pic import check_media_existance
from utils.utils import get_file
from utils.utils import send_product_card
from .order_processing import print_out_formatted_row

# router to navigate catalog related requests
router: Router = Router()
router.callback_query.middleware(TimingMiddleware())
router.callback_query.middleware(IdMiddleware())
router.callback_query.middleware(DeviceMiddleware())
router.message.middleware((DeviceMiddleware()))


@router.callback_query(CallbackFactoryCategories.filter())
async def process_products_listing(callback: CallbackQuery,
                                   callback_data: CallbackFactoryCategories,
                                   state: FSMContext):
    admin_mode: bool = False
    if await state.get_state() == AdminStates.admin_start:
        admin_mode: bool = True
    kb: Callable = product_action_bar
    if await state.get_state() == AdminStates.admin_start:
        kb: Callable = product_action_bar_admin
    product: Row = get_first_product(category_uuid=callback_data.uuid)
    if not product:
        await callback.message.answer(
            text='В выбранном категории нет товаров. Рассмотрите другие категории',
            reply_markup=create_categories_kb(callback)
        )
        return await callback.answer()
    await send_product_card(update=callback,
                            kb=kb,
                            product=product,
                            admin_mode=admin_mode)
    await callback.answer()


@router.callback_query(CallbackFactoryStepBack.filter())
async def get_back_into_categories(callback: CallbackQuery):
    await callback.message.answer(text="Ниже представлены доступные категории товаров",
                                  reply_markup=create_categories_kb(callback))
    await callback.answer()


@router.callback_query(CallbackFactoryGoods.filter())
async def process_pagination(callback: CallbackQuery,
                             callback_data: CallbackFactoryGoods,
                             state: FSMContext):
    admin_mode: bool = False
    if await state.get_state() == AdminStates.admin_start:
        admin_mode: bool = True
    if callback_data.uuid == 'not allowed':
        return await callback.answer(text='Прокрута в выбранном направлении невозможна')
    kb: Callable = product_action_bar
    if await state.get_state() == AdminStates.admin_start:
        kb: Callable = product_action_bar_admin
    product: Row = get_product(product_uuid=callback_data.uuid)
    await send_product_card(update=callback,
                            kb=kb,
                            product=product,
                            admin_mode=admin_mode)
    await callback.answer()


@router.callback_query(CallbackFactoryProductDetails.filter())
async def process_detalization_button(callback: CallbackQuery,
                                      callback_data: CallbackFactoryProductDetails,
                                      state: FSMContext):
    product: Row = get_product(product_uuid=callback_data.uuid)
    admin_mode: bool = False
    if await state.get_state() == AdminStates.admin_start:
        admin_mode: bool = True

    media_group_photos: list[InputMediaPhoto] = [
        InputMediaPhoto(caption='\n'.join([f"<b>{value}</b>: {getattr(product, key)}" for key, value in
                                           product_columns_mapper.items()]),
                        parse_mode='HTML',
                        media=get_file(product)),
    ]
    if check_media_existance(product.product_id, 'videos'):
        media_group_videos: list[InputMediaVideo] = [
            InputMediaVideo(media=get_file(product, "videos"))
        ]
        await callback.message.answer_media_group(media=media_group_videos)
    await callback.message.answer_media_group(media=media_group_photos)
    await callback.message.answer(text='Кликните <Назад>, чтобы вернуться к просмотру товаров',
                                  reply_markup=create_detalisation_kb(callback_data=callback_data,
                                                                      admin_mode=admin_mode))
    await callback.answer()


@router.message(Text('Мои заказы 📖'))
async def process_my_orders_button(message: Message, state: FSMContext):
    admin_mode: bool = False
    if await state.get_state() == AdminStates.admin_start:
        admin_mode: bool = True
    user_id: int = message.chat.id
    user_orders: Sequence[Row[tuple]] = get_user_orders(user_id, admin_mode=admin_mode)
    if not user_orders:
        return await message.answer('У вас еще нет заказов')
    ordered_items: list[ItemListedInUserOrders] = [ItemListedInUserOrders(
        order_number=item.order_number,
        order_date=item.order_start_date,
        product_name=item.product_name,
        quantity=item.quantity,
        price=PriceRepresentation(item.quantity * item.price, 'руб'),
        order_status=item.order_status_name) for item in user_orders]

    device: str = get_user_device(user_id)
    summary: str = print_out_formatted_row(attribute_names=list(order_listing_mapper.values()),
                                      cart_items=ordered_items,
                                      mapper=order_listing_mapper,
                                      device=device)
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
