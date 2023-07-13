import asyncio

from aiogram.utils.keyboard import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.types import CallbackQuery, Message
from aiogram import Router, F
from aiogram.filters import Text
from keyboards import keyboards
from database.database import user_status, cart, states_stack
from lexicon.LEXICON import non_pagination_buttons, command_handlers
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from states.states import FSMBrowsingState

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
                                             [InlineKeyboardButton(text='Назад', callback_data='get_back')]]))
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
                             [InlineKeyboardButton(text='Закрыть', callback_data='close_menu_window')]]))


@router.message(Text('Корзина 🛒'))
async def process_cart_static_button(message: Message, state: FSMContext):
    user_id: int = message.from_user.id
    states_stack[user_id].append(FSMBrowsingState.browsing_static_cart_page)
    await state.set_state(FSMBrowsingState.browsing_static_cart_page)
    await asyncio.sleep(2)
    await message.delete()
    await message.answer(
        text=f"<b>Выбранные товары</b>  🛍"
             f"\n\n{'*' * 20}\n\n".join(
            ['\n'.join([f"<b>{key}:</b> {value}" for key, value in item.__dict__.items()]) for item in cart[user_id]])
             + '\n' * 2 + f"<b>Общая сумма заказа:</b> "
                          f"{float(sum(float(item.price.split()[0]) * item.quantity for item in cart[user_id]))} $",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[[InlineKeyboardButton(text="Подтверждение заказа", callback_data="finalize_order")],
                             [InlineKeyboardButton(text='Закрыть', callback_data='close_menu_window')]]))


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
                             [InlineKeyboardButton(text='Закрыть', callback_data='close_menu_window')]]))


@router.callback_query(Text('ask_manager'), StateFilter(FSMBrowsingState.browsing_static_help_page))
async def process_ask_manager_inline_button(callback: CallbackQuery, state: FSMContext):
    user_id: int = callback.from_user.id
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
    user_id: int = message.from_user.id
    await asyncio.sleep(2)
    await message.forward(chat_id=593908084)
    await message.delete()
    await message.answer(
        text='Ваш запрос отправлен\n'
             'Для продолжения вернитесь в главное меню командой  /start',
        parse_mode="HTML",
        # reply_markup=InlineKeyboardMarkup(
        #     inline_keyboard=[[InlineKeyboardButton(text='Закрыть', callback_data='get_one_step_back')]])
    )
    await state.set_state(states_stack[user_id][-1])
    print(states_stack[user_id])
    print(await state.get_state())


@router.callback_query(Text([*[callback_data for callback_data in non_pagination_buttons.values()]]))
async def processing_step_back_from_non_catalog(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()
    user_id: int = callback.from_user.id
    if states_stack:
        states_stack[user_id].pop(-1)
    if await state.get_state() == FSMBrowsingState.browsing_personal_address:
        await state.set_state(FSMBrowsingState.browsing_personal_account)
        print('handling step back from setting address state')
        # обязательно вынести код в одну фукнцию, он дублируется в хендлере ниже
        await callback.message.answer(
            text=f"<b>Полное имя:</b> {callback.message.from_user.full_name}\n"
                 f"<b>Баланс:</b> {user_status[user_id]['balance']}\n"
                 f"<b>Адрес доставки:</b> {user_status[user_id]['delivery address']}\n"
                 f"<b>Заказы:</b> Нет заказов\n",
            parse_mode="HTML",
            reply_markup=keyboards.create_personal_menu_buttons())
    elif await state.get_state() == FSMBrowsingState.finalizing_order:
        await state.set_state(FSMBrowsingState.browsing_static_cart_page)
        await callback.message.answer(
            text=
            f"\n\n{'*' * 20}\n\n".join(
                ['\n'.join([f"<b>{key}:</b> {value}" for key, value in item.__dict__.items()]) for item in
                 cart[user_id]])
            + '\n' * 2 + f"<b>Общая сумма заказа:</b> "
                         f"{float(sum(float(item.price.split()[0]) * item.quantity for item in cart[user_id]))} $",
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[[InlineKeyboardButton(text="Подтверждение заказа", callback_data="finalize_order")],
                                 [InlineKeyboardButton(text='Закрыть', callback_data='close_menu_window')]]))

    else:
        if states_stack[user_id]:
            await state.set_state(states_stack[user_id][-1])
        else:
            await state.clear()
        print('Улетело вникуда')
    print(await state.get_state())
    print('inside processing_get_back_button')
    print(f" renewed states stack is following {states_stack}")

    # await state.set_state(default_state)


@router.callback_query(StateFilter(*[FSMBrowsingState.browsing_static_cart_page]),
                       Text('finalize_order'))
async def proceed_with_the_order_button(callback: CallbackQuery, state: FSMContext):
    user_id: int = callback.from_user.id
    states_stack[user_id].append(FSMBrowsingState.finalizing_order)
    await state.set_state(FSMBrowsingState.finalizing_order)
    await callback.message.delete()
    await callback.message.answer(text="После подтверждения заказа Ваш заказ будет принят в обработку "
                                       "и наш менеджер свяжется с вами для уточнения деталей",
                                  reply_markup=InlineKeyboardMarkup(
                                      inline_keyboard=[[InlineKeyboardButton(text="Подтвердить заказ",
                                                                             callback_data="confirm order")],
                                                       [InlineKeyboardButton(text="Назад",
                                                                             callback_data="get_back")]]))
@router.callback_query(StateFilter(*[FSMBrowsingState.finalizing_order]),
                       Text('confirm order'))
async def proceed_with_the_order_button(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()
    await callback.message.answer(text="Заказ подтвержден")