from datetime import datetime
from aiogram import Router, F
from aiogram.filters import Command
from keyboards.keyboards import static_common_buttons_menu, create_cart_kb
from lexicon.LEXICON import command_handlers
from aiogram.filters import Text, StateFilter
from keyboards.keyboards import create_categories_kb, create_favorite_goods_kb, create_device_selection_kb
from aiogram.types import Message, CallbackQuery
from utils.utils import send_product_card_cart_item, send_product_card_favorite_items
from filters.callbacks import CallbackFactoryFinalizeOrder, CallbackFactoryWindowClose, \
    CallbackFactorTerminateConfirmation
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from database.methods.redis_methods import get_user_cart, get_favorite
from database.methods.rel_db_methods import get_product
from middlewares.throttling import DeviceMiddleware

# creating router to register local handlers
router: Router = Router()
router.callback_query.middleware(DeviceMiddleware())
router.message.middleware((DeviceMiddleware()))


@router.message(Command(commands=["start", "help", "payment", "delivery", "legal"]))
async def process_start_command(message: Message):
    command = message.text.strip('/')
    await message.answer(text=command_handlers[command],
                         reply_markup=static_common_buttons_menu(is_persistent=True))


@router.message(Text('Каталог 📕'))
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
    user_id = update.chat.id
    user_cart = get_user_cart(user_id)
    if not user_cart:
        return await update.answer('Корзина пуста. Попробуйте сначала что-нибудь туда добавить.',
                                   show_alert=True)
    else:
        product = get_product(list(user_cart)[0])
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
    user_id = message.chat.id
    user_favorite = get_favorite(user_id)
    if not user_favorite:
        return await message.answer(text='В избранном еще ничего нету. Попробуйте что-нибудь туда добавить')
    product = get_product(list(user_favorite)[0])
    await send_product_card_favorite_items(update=message,
                                           kb=create_favorite_goods_kb,
                                           product=product)


@router.message(Text('Изменить устройство 🖥 🔛📱'))
async def process_change_device_button(message: Message):
    user_id = message.chat.id
    await message.answer(
        text='Пожалуйста, выберите ваше текущее устройство',
        reply_markup=create_device_selection_kb(user_id))

