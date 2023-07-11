import asyncio
import re

from aiogram.utils.keyboard import ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.types import CallbackQuery, Message
from aiogram.types.input_media_photo import InputMediaPhoto
from aiogram import Router, F
from aiogram.filters import Command, CommandStart, Text
from keyboards import keyboards
from lexicon.lexicon_ru import command_handlers, start_follow_up_menu
from database.database import image_1, goods, user_status, cart, states_stack
from lexicon.LEXICON import pagination_buttons
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from states.states import FSMBrowsingState
from aiogram.fsm.state import default_state
from middlewares.throttling import FSMCheckingMiddleware
from services.services import cache_user

# creating router to navigate common users requests
router: Router = Router()


@router.message(Text('Личный кабинет 📖'))
async def process_client_account__static_button(message: Message, state: FSMContext):
    user_id: int = message.from_user.id
    states_stack[user_id].append(FSMBrowsingState.browsing_personal_account)
    await state.set_state(FSMBrowsingState.browsing_personal_account)

    await asyncio.sleep(2)
    await message.delete()
    await message.answer(
        text=f"<b>Полное имя:</b> {message.from_user.full_name}\n"
             f"<b>Баланс:</b> {user_status[user_id]['balance']}\n"
             f"<b>Адрес доставки:</b> {user_status[user_id]['delivery address']}\n"
             f"<b>Заказы:</b> Нет заказов\n"
             f"<b>id:</b> {message.from_user.id}\n"
        ,
        parse_mode="HTML",
        reply_markup=keyboards.create_personal_menu_buttons())


@router.callback_query(Text(text="set_address"), StateFilter(FSMBrowsingState.browsing_personal_account))
async def process_set_address_button(callback: CallbackQuery, state: FSMContext):
    print('inside set address')
    await callback.message.edit_text(text='Пожалуйста, введите адрес в следующем формате: \n'
                                          'Страна, город, улица, дом, квартира \n'
                                          'Например: РФ, Калининград, Строителей, 16, 2',
                                     reply_markup=InlineKeyboardMarkup(
                                         inline_keyboard=[
                                             [InlineKeyboardButton(text='Назад', callback_data='get_one_step_back')]]))
    await state.set_state(FSMBrowsingState.browsing_personal_address)


@router.message(Text('Баланс 💳'))
async def process_balance_static_button(message: Message, state: FSMContext):
    user_id: int = message.from_user.id
    states_stack[user_id].append(FSMBrowsingState.browsing_static_balance_page)
    await state.set_state(FSMBrowsingState.browsing_static_balance_page)
    await asyncio.sleep(2)
    await message.delete()
    await message.answer(
        text=f"<b>Полное имя:</b> {message.from_user.full_name}\n"
             f"<b>Баланс:</b> {user_status[user_id]['balance']}\n"
             f"<b>id:</b> {message.from_user.id}\n"
        ,
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[[InlineKeyboardButton(text="Пополнить счет", callback_data="deposit_funds")],
                             [InlineKeyboardButton(text='Закрыть', callback_data='get_one_step_back')]]))


@router.message(Text('Корзина 🛒'))
async def process_cart_static_button(message: Message, state: FSMContext):
    user_id: int = message.from_user.id
    states_stack[user_id].append(FSMBrowsingState.browsing_static_balance_page)
    await state.set_state(FSMBrowsingState.browsing_static_balance_page)
    await asyncio.sleep(2)
    await message.delete()
    await message.answer(
        text=f"\n\n{'*' * 20}\n\n".join(
            ['\n'.join([f"<b>{key}:</b> {value}" for key, value in item.__dict__.items()]) for item in cart[user_id]])
             + '\n' * 2 + f"<b>Общая сумма заказа:</b> "
                          f"{float(sum(float(item.price.split()[0]) * item.quantity for item in cart[user_id]))} $",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[[InlineKeyboardButton(text="Оформить заказ", callback_data="proceed_with_the_order")],
                             [InlineKeyboardButton(text='Закрыть', callback_data='get_one_step_back')]]))


@router.message(Text('Помощь 🆘'))
async def process_client_account__static_button(message: Message, state: FSMContext):
    user_id: int = message.from_user.id
    states_stack[user_id].append(FSMBrowsingState.browsing_static_help_page)
    await state.set_state(FSMBrowsingState.browsing_static_help_page)
    await asyncio.sleep(2)
    await message.delete()
    await message.answer(
        text=command_handlers['help'],
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[[InlineKeyboardButton(text="Задать вопрос менеджеру", callback_data="ask_manager")],
                             [InlineKeyboardButton(text='Закрыть', callback_data='get_one_step_back')]]))


@router.callback_query(Text('ask_manager'), StateFilter(FSMBrowsingState.browsing_static_help_page))
async def process_ask_manager_inline_button(callback: CallbackQuery, state: FSMContext):
    user_id: int = callback.message.from_user.id
    states_stack[user_id].append(FSMBrowsingState.browsing_personal_query_page)
    await state.set_state(FSMBrowsingState.browsing_personal_query_page)
    await asyncio.sleep(2)
    await callback.message.delete()
    await callback.message.answer(
        text='Напиши ваш вопрос и отправьте его как обычное сообщение. Наш менеджер получит его и свяжется с вами'
             ' в ближайшее время',
        parse_mode="HTML",
        # reply_markup=InlineKeyboardMarkup(
        #     inline_keyboard=[[InlineKeyboardButton(text='Закрыть', callback_data='get_one_step_back')]])
    )


@router.message(F.text, StateFilter(FSMBrowsingState.browsing_personal_query_page))
async def process_ask_manager_inline_button(message: Message, state: FSMContext):
    await asyncio.sleep(2)
    await message.delete()
    await message.forward(chat_id=593908084)
    await message.answer(
        text='Ваш запрос отправлен\n'
             'Для продолжения вернитесь в главное меню командой  /start',
        parse_mode="HTML",
        # reply_markup=InlineKeyboardMarkup(
        #     inline_keyboard=[[InlineKeyboardButton(text='Закрыть', callback_data='get_one_step_back')]])
    )
