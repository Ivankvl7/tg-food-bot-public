import datetime
import re

from aiogram import F
from aiogram.filters import Text
from aiogram.types import CallbackQuery
from aiogram import Router
from keyboards.keyboards import product_action_bar
from filters.callbacks import CallbackFactoryCategories, CallbackFactoryStepBack, CallbackFactoryGoods
from models.methods import select_product
from lexicon.LEXICON import product_columns_mapper
from keyboards.keyboards import create_categories_kb
from middlewares.throttling import TimingMiddleware, IdMiddleware
from sqlalchemy import Row
from utils.utils import send_product_card

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
    product: Row = select_product(callback_data.uuid)
    await send_product_card(callback=callback,
                            callback_data=callback_data,
                            product_action_bar=product_action_bar,
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
    # product: Row = select_product(product_id=callback_data.uuid)
    # print('inside process_pagination')
    # await send_product_card(callback=callback,
    #                         callback_data=callback_data,
    #                         product_action_bar=product_action_bar,
    #                         product=product)
    # print('process_pagination finished')
    print(callback_data.uuid, len(callback_data.uuid))
    await callback.answer()
