from datetime import datetime
import re
from aiogram.utils.keyboard import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram import F, Router
from aiogram.filters import StateFilter
from aiogram.types import CallbackQuery, Message
from keyboards.user_keyboards import close_window_button, static_common_buttons_menu
from filters.callbacks import CallbackFactoryWindowClose, CallbackFactoryOrderConfirmation, CallbackFactoryNameInput, \
    CallbackFactoryQuickConfirmation
from lexicon.LEXICON import order_summary_mapper
from middlewares.throttling import TimingMiddleware, IdMiddleware, DeviceMiddleware
from sqlalchemy import Row
from database.methods.rel_db_methods import get_product, add_user_to_db, add_order_to_db, \
    get_user_id_by_tg_id, get_user_orders, get_user_tg_ids_from_db, from_product_to_cart_item, \
    get_order_number, get_user_fields
from models.models import CartItem, PriceRepresentation, SelectedDevice
from aiogram.fsm.context import FSMContext
from states.user_states import FSMOrderConfirmation
from aiogram.fsm.state import default_state
from database.methods.redis_methods import get_user_cart, clear_cart, get_user_profile, set_user_profile_attribute, \
    get_user_device, get_product_quantity

# router to navigate catalog related requests
router: Router = Router()
router.callback_query.middleware(TimingMiddleware())
router.callback_query.middleware(IdMiddleware())
router.callback_query.middleware(DeviceMiddleware())
router.message.middleware((DeviceMiddleware()))


def define_appropriate_lengths(cart_items: list[CartItem | Row], mapper: dict) -> list[int]:
    final_length = []
    tmp_lengths = []
    for attribute in mapper:
        attributes_list = [str(getattr(item, attribute)) for item in cart_items]
        max_length = len(max(attributes_list, key=len))
        tmp_lengths.append(max_length)
    comparatabe = list(zip([len(item) for item in list(mapper.values())], tmp_lengths))
    for index in range(len(comparatabe)):
        final_length.append(max(comparatabe[index]))
        print(final_length)
    order_sum = str(PriceRepresentation(num=sum([item.price.num * int(item.quantity) for item in cart_items]),
                                        unit='руб.'))
    final_length[-2] = max(len(order_sum), final_length[-2])
    return final_length


def print_out_formatted_row(attribute_names: list, cart_items: list, mapper: dict, device: str) -> str:
    rows = []
    row_elements = []
    length = define_appropriate_lengths(cart_items=cart_items,
                                        mapper=mapper)
    for index in range(len(attribute_names)):
        row_elements.append(f"{attribute_names[index]}".ljust(length[index]))
    if device == SelectedDevice.DESKTOP.value:
        rows.append(f"<pre>{' | '.join(row_elements)}</pre>")
    else:
        rows.append(f"{' | '.join(row_elements)}")

    row_elements.clear()
    for item in cart_items:
        for index, attribute in enumerate(list(mapper.keys())):
            row_elements.append(f"{getattr(item, attribute)}".ljust(length[index]))
        if device == SelectedDevice.DESKTOP.value:
            rows.append(f"<pre>{' | '.join(row_elements)}</pre>")
        else:
            rows.append(f"{' | '.join(row_elements)}")

        row_elements.clear()
    order_sum = str(PriceRepresentation(num=sum([item.price.num * int(item.quantity) for item in cart_items]),
                                        unit='руб.'))
    final_row = [''.ljust(index) for index in length]
    final_row[-3] = 'Итого:'.ljust(length[-3])
    final_row[-2] = order_sum.ljust(length[-2])
    if device == SelectedDevice.DESKTOP.value:
        rows.append(f"<pre>{' | '.join(final_row)}</pre>")
    else:
        rows.append(f"{' | '.join(final_row)}")

    if device == SelectedDevice.DESKTOP.value:
        return '\n'.join(rows)
    headers = rows[0].split(' | ')
    print(headers)
    res = []
    for row in rows[1:-1]:
        split_row = row.split(' | ')
        tmp_res = []
        for header, value in zip(headers, split_row):
            data_row = f"<b>{header.strip()}</b>: {value.strip()}\n"
            print(data_row)
            tmp_res.append(data_row)
        res.append(''.join(tmp_res))
        res.append('\n\n')
    total_sum_key = rows[-1].split(' | ')[-3].strip()
    total_sum = rows[-1].split(' | ')[-2].strip()
    res.append(' '.join([f"<b>{total_sum_key}</b>", total_sum]))
    return ''.join(res)


@router.callback_query(CallbackFactoryOrderConfirmation.filter())
async def process_start_order_confirmation_button(callback: CallbackQuery,
                                                  state: FSMContext):
    user_id = callback.message.chat.id
    order_number = get_order_number()
    cart = [from_product_to_cart_item(order_number, get_product(uuid), get_product_quantity(user_id, uuid)) for uuid in
            get_user_cart(user_id)]
    if not cart:
        return await callback.answer('Корзина пуста', show_alert=True)

    user_id = callback.message.chat.id
    device = get_user_device(user_id)
    summary = print_out_formatted_row(attribute_names=list(order_summary_mapper.values()),
                                      cart_items=cart,
                                      mapper=order_summary_mapper,
                                      device=device)
    print(summary)
    await callback.message.answer(text=summary,
                                  reply_markup=InlineKeyboardMarkup(
                                      inline_keyboard=[
                                          [InlineKeyboardButton(
                                              text='Назад',
                                              callback_data=CallbackFactoryWindowClose(
                                                  user_id=user_id,
                                                  timestamp=datetime.utcnow().strftime(
                                                      '%d-%m-%y %H-%M')
                                              ).pack()
                                          )],
                                          [InlineKeyboardButton(
                                              text='Продолжить',
                                              callback_data=CallbackFactoryNameInput(
                                                  user_id=user_id,
                                                  timestamp=datetime.utcnow().strftime(
                                                      '%d-%m-%y %H-%M')).pack())]]

                                  ),
                                  parse_mode='HTML')
    await state.set_state(FSMOrderConfirmation.confirmation_started)
    await callback.answer()


@router.callback_query(CallbackFactoryNameInput.filter(), FSMOrderConfirmation.confirmation_started)
async def process_input_name(callback: CallbackQuery,
                             state: FSMContext):
    user_id = callback.message.chat.id
    order_number = get_order_number()
    cart = [from_product_to_cart_item(order_number, get_product(uuid)) for uuid in get_user_cart(user_id)]
    if not cart:
        return await callback.answer('Действие невозможно', show_alert=True)
    text = 'Введите ваше имя в формате Имя Фамилия, \nнапример: <strong>Федор Достоевский</strong>\n'
    quick_confo = False
    user_profile = get_user_fields(user_id).one_or_none()
    if user_profile:
        print('changin text to broaden variant')
        text = f'Я вижу, что вы уже оформляли у нас заказ и вводили запрашиваемые данные, ' \
               'чтобы не вводить их повторно, можете нажать на кнопку "Подтвердить мгновенно."\n\n' \
               'Заказ будет оформлен на ваш профиль \n\n' \
               'Если данные поменялись, то введите их заново. \n\n' \
               'Введите ваше имя в формате Имя Фамилия, \nнапример: <strong>Федор Достоевский</strong>\n\n'
        keys = get_user_fields(user_id).keys()
        values = get_user_fields(user_id).one()
        print(f"keys={keys}")
        print(f"values={values}")
        for key in keys:
            set_user_profile_attribute(user_id=user_id,
                                       key=key,
                                       value=str(getattr(values, key)))
        quick_confo = True
    print(user_id)
    print(get_user_tg_ids_from_db())
    await callback.message.answer(
        text=text,
        parse_mode='HTML',

        reply_markup=close_window_button(text='Прекратить подтверждение',
                                         update=callback,
                                         state=state,
                                         quick_confo=quick_confo))
    print(await state.get_state())
    await state.set_state(FSMOrderConfirmation.input_name)
    await callback.answer()


@router.message(F.text.regexp(re.compile(r'\w+ \w+ *')), FSMOrderConfirmation.input_name)
async def process_input_name_successful(message: Message, state: FSMContext):
    user_id = message.chat.id
    first_name, last_name = message.text.split()
    set_user_profile_attribute(user_id=user_id,
                               key='first_name',
                               value=first_name)
    set_user_profile_attribute(user_id=user_id,
                               key='last_name',
                               value=last_name)
    await message.answer(text='Спасибо! Теперь введите адрес доставки в произвольном формате',
                         reply_markup=close_window_button(text='Прекратить подтверждение',
                                                          update=message,
                                                          state=state))
    await state.set_state(FSMOrderConfirmation.input_address)


@router.message(FSMOrderConfirmation.input_name)
async def process_input_name_unsuccessful(message: Message, state: FSMContext):
    await message.answer(text='Похоже, что вы неверно ввели имя, попробуйте еще раз',
                         reply_markup=close_window_button(text='Прекратить подтверждение',
                                                          update=message,
                                                          state=state))


@router.message(FSMOrderConfirmation.input_address)
async def process_input_age(message: Message, state: FSMContext):
    await message.answer(text='Спасибо! Введите пожалуйста ваш возраст или 0, если хотите пропустить этот шаг',
                         reply_markup=close_window_button(text='Прекратить подтверждение',
                                                          update=message,
                                                          state=state))
    user_id = message.chat.id
    set_user_profile_attribute(user_id=user_id,
                               key='address',
                               value=message.text)
    await state.set_state(FSMOrderConfirmation.input_age)


@router.message(F.text.regexp(re.compile(r'\d{1,2}')), FSMOrderConfirmation.input_age)
async def process_input_phone(message: Message, state: FSMContext):
    user_id = message.chat.id
    set_user_profile_attribute(user_id=user_id,
                               key='age',
                               value=message.text)
    await message.answer(
        text='Спасибо! Теперь введите, пожалуйста ваш номер телефона, к которому привязан телеграм в следующем формате:\n'
             '+7 999 888 77 66',
        reply_markup=close_window_button(text='Прекратить подтверждение',
                                         update=message,
                                         state=state))
    await state.set_state(FSMOrderConfirmation.input_phone)


@router.message(FSMOrderConfirmation.input_age)
async def process_input_age_unsuccessful(message: Message):
    await message.answer('Похоже вы ввели некорректный возраст, пожалуйста, введите еще раз')


@router.message(F.text.regexp(re.compile(r'\+\d \d{3} \d{3} \d{2} \d{2}')), FSMOrderConfirmation.input_phone)
async def process_input_phone_successful(message: Message, state: FSMContext):
    print(await state.get_state())
    await state.clear()
    user_id = message.chat.id
    set_user_profile_attribute(user_id=user_id,
                               key='phone',
                               value=message.text)
    await message.answer(
        text='Спасибо. Остался email в формате SergeyIvanov@gmail.com (регистр не важен)',
        reply_markup=close_window_button(text='Прекратить подтверждение',
                                         update=message,
                                         state=state))
    await state.set_state(FSMOrderConfirmation.input_email)


@router.message(FSMOrderConfirmation.input_phone)
async def process_input_phone_unsuccessful(message: Message):
    await message.answer(text=f"Кажется, введенынй вами номер не соответсвует указанному формату.\nПопробуйте еще раз")


@router.callback_query(CallbackFactoryQuickConfirmation.filter(), ~StateFilter(default_state))
@router.message(F.text.regexp(re.compile(r'[A-Za-z]+[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b')),
                FSMOrderConfirmation.input_email)
async def process_input_email_successful(update: Message | CallbackQuery, state: FSMContext):
    print(await state.get_state())
    await state.clear()
    message = update
    if isinstance(update, CallbackQuery):
        user_id: int = update.message.chat.id
        username = update.from_user.username
        message = update.message
    else:
        user_id: int = update.chat.id
        email: str = update.text
        username = update.from_user.username
        set_user_profile_attribute(user_id=user_id,
                                   key='email',
                                   value=email)
    user_profile = get_user_profile(user_id)
    order_number = get_order_number()
    cart = [from_product_to_cart_item(order_number=order_number,
                                      product=get_product(uuid),
                                      quantity=get_product_quantity(
                                          user_id=user_id,
                                          product_uuid=uuid)) for uuid in get_user_cart(user_id)]
    if user_id in get_user_tg_ids_from_db():
        action = 'update'
    else:
        action = 'add'
    add_user_to_db(
        action=action,
        user_tg_id=user_id,
        username=username,
        first_name=user_profile['first_name'],
        last_name=user_profile['last_name'],
        phone=user_profile['phone'],
        age=user_profile['age'],
        email=user_profile['email'],
        address=user_profile['address'],
    )
    add_order_to_db(
        user_tg_id=user_id,
        user_cart=cart
    )
    user_db_id: int = get_user_id_by_tg_id(user_id)
    print(get_user_orders(user_db_id))
    clear_cart(user_id)

    await message.answer(
        text='Спасибо за заказ! Для уточнения остальных деталей с вами в ближайшее время свяжется менеджер магазина',
        reply_markup=static_common_buttons_menu(is_persistent=True))
    if isinstance(update, CallbackQuery):
        await update.answer()


@router.message(FSMOrderConfirmation.input_email)
async def process_input_email_unsuccessful(message: Message):
    await message.answer(text=f"Кажется, введенынй вами email не соответсвует указанному формату.\nПопробуйте еще раз")
