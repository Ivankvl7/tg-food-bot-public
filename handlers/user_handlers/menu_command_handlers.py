from datetime import datetime

import aiogram
from aiogram.types import Message
from aiogram import Router, F
from aiogram.filters import Command
from keyboards.keyboards import static_common_buttons_menu, create_cart_kb
from lexicon.LEXICON import command_handlers
from aiogram.filters import Text, StateFilter
from keyboards.keyboards import create_categories_kb, create_favorite_goods_kb
from aiogram.types import Message, CallbackQuery
from database.tmp_database import cart, favorite_products
from utils.utils import send_product_card_cart_item, send_product_card_favorite_items
from filters.callbacks import CallbackFactoryFinalizeOrder, CallbackFactoryWindowClose, \
    CallbackFactoryDeleteFromFavorite, CallbackFactoryAddToCartFromFavorite, CallbackFactorTerminateConfirmation
from aiogram.fsm.context import FSMContext
from states.user_states import FSMOrderConfirmation
from aiogram.fsm.state import default_state

# creating router to register local handlers
router: Router = Router()


@router.message(Command(commands=["start", "help", "payment", "delivery", "legal"]))
async def process_start_command(message: Message):
    command = message.text.strip('/')
    await message.answer(text=command_handlers[command],
                         reply_markup=static_common_buttons_menu(is_persistent=True))


@router.message(Text('Каталог 📕'))
# @router.message(Command('catalog'))
async def process_catalog_command(update: Message):
    print('inside catalog')
    print(update.json())
    await update.answer(text="Ниже представлены доступные категории товаров",
                        reply_markup=create_categories_kb(update))


print('catalog processing finished')


@router.callback_query(CallbackFactoryWindowClose.filter())
async def process_back_from_categories_button(callback: CallbackQuery):
    await callback.message.delete()
    await callback.answer()


@router.callback_query(CallbackFactorTerminateConfirmation.filter(), ~StateFilter(default_state))
async def process_confo_termination(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.answer(text="Подтверждение прекращено. Товары по прежнему в корзине",
                                  reply_markup=static_common_buttons_menu(is_persistent=True))
    await callback.answer()


@router.message(Text('Корзина 🛒'))
async def process_cart_static_button(update: Message):
    user_id = update.from_user.id

    if user_id not in cart:
        return await update.answer('Корзина пуста. Попробуйте сначала что-нибудь туда добавить.',
                                   show_alert=True)

    else:
        product = cart[user_id][0]
        await send_product_card_cart_item(update=update,
                                          kb=create_cart_kb,
                                          product=product,
                                          index=0,
                                          callback_data=CallbackFactoryFinalizeOrder(
                                              user_id=user_id,
                                              uuid=product.product_uuid,
                                              timestamp=datetime.utcnow().strftime('%d-%m-%y %H-%M')
                                          ))


@router.message(Text('Избранное ⭐️'))
async def process_favorite_goods_button(message: Message):
    user_id = message.from_user.id
    user_favorite_products = favorite_products.get(user_id, [])
    if not user_favorite_products:
        return await message.answer(text='В избранном еще ничего нету. Попробуйте что-нибудь туда добавить')
    product = favorite_products[user_id][0]
    await send_product_card_favorite_items(update=message,
                                           kb=create_favorite_goods_kb,
                                           product=product)


@router.callback_query(CallbackFactoryDeleteFromFavorite.filter())
async def process_del_from_favorite_button(callback: CallbackQuery, callback_data: CallbackFactoryDeleteFromFavorite):
    index = int(callback_data.index)
    user_id = callback.from_user.id
    user_favorite_products = favorite_products.get(user_id, [])
    if not user_favorite_products:
        return await callback.answer(text='В избранном ничего нет')
    if len(user_favorite_products) == 1:
        user_favorite_products.pop(index)
        await callback.answer(text='В избранном больше ничего нет')
        await callback.message.answer(text="Ниже представлены доступные категории товаров",
                                      reply_markup=create_categories_kb(callback))
    else:
        user_favorite_products.pop(0)
        product = favorite_products[user_id][0]
        await send_product_card_favorite_items(update=callback,
                                               kb=create_favorite_goods_kb,
                                               product=product
                                               )
        await callback.answer()
