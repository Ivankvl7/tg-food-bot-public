from datetime import datetime
import re
from aiogram.utils.keyboard import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram import F, Router
from aiogram.filters import StateFilter, Text
from aiogram.types import CallbackQuery, InputMediaPhoto, InputMediaVideo, Message
from keyboards.keyboards import product_action_bar, create_cart_kb, create_categories_kb, create_detalisation_kb, \
    create_favorite_goods_kb, close_window_button, static_common_buttons_menu
from filters.callbacks import CallbackFactoryCategories, CallbackFactoryStepBack, CallbackFactoryGoods, \
    CallbackFactoryProductDetails, CallbackFactoryAddToCart, CallbackFactoryFinalizeOrder, \
    CallbackFactoryCartProductSwap, CallbackFactoryQuantityChange, CallbackFactoryProductDetailsFromCart, \
    CallbackFactoryAddToFavorite, CallbackFactoryFavoriteProductsSwap, CallbackFactoryWindowClose, \
    CallbackFactoryOrderConfirmation, CallbackFactoryNameInput, CallbackFactoryQuickConfirmation
from lexicon.LEXICON import product_columns_mapper, order_summary_mapper, order_listing_mapper
from middlewares.throttling import TimingMiddleware, IdMiddleware
from sqlalchemy import Row
from utils.utils import send_product_card, send_product_card_cart_item, send_product_card_favorite_items
from models.methods import get_product, get_static_videos, get_category_uuid_by_product_uuid, get_category, \
    add_user_to_db, add_order_to_db, get_user_id_by_tg_id, get_user_orders, get_first_product, get_user_tg_ids_from_db, \
    get_user_by_tg_id
from database.tmp_database import cart, favorite_products
from utils.order_items import CartItem, PriceRepresentation, UserProfile, ItemListedInUserOrders
from aiogram.fsm.context import FSMContext
from states.user_states import FSMOrderConfirmation
from database.tmp_database import user_profiles
from aiogram.fsm.state import default_state

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


@router.callback_query(CallbackFactoryAddToCart.filter())
async def process_add_to_cart_button(callback: CallbackQuery, callback_data: CallbackFactoryAddToCart):
    user_id = callback.from_user.id
    product = get_product(callback_data.uuid)
    if not cart.get(user_id, []):
        cart[user_id] = list()
    item = CartItem(
        product_name=product.product_name,
        category_name=get_category(get_category_uuid_by_product_uuid(callback_data.uuid)),
        description=product.description,
        price=PriceRepresentation(product.price, 'руб.'),
        quantity=1,
        product_uuid=product.product_uuid,
        article=product.article)
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

    if user_id not in cart:
        return await update.answer('Корзина пуста', show_alert=True)

    else:
        print(cart)
        product = cart[user_id][0]
        await send_product_card_cart_item(update=update,
                                          kb=create_cart_kb,
                                          product=product,
                                          index=0,
                                          callback_data=callback_data)
    print('current_index=0')
    print(cart[user_id])
    print(callback_data)
    await update.answer()
    print('process_finalize_order_button finished')


@router.callback_query(CallbackFactoryProductDetailsFromCart.filter())
async def process_product_details_from_cart_button(callback: CallbackQuery,
                                                   callback_data: CallbackFactoryProductDetailsFromCart):
    user_id = callback_data.user_id
    if not cart.get(user_id, []):
        return await callback.answer('Корзина пуста', show_alert=True)
    product: CartItem = cart[user_id][callback_data.index]
    if callback_data.index == 0:
        index = callback_data.index
    else:
        index = callback_data.index - 1
    media_group_photos = [
        InputMediaPhoto(caption='\n'.join([f"<b>{value}</b>: {getattr(product, key)}" for key, value in
                                           product_columns_mapper.items()]),
                        parse_mode='HTML',
                        media='https://static.ebayinc.com/static/assets/Uploads/Stories/Articles/_resampled/ScaleWidthWzgwMF0/ebay-authenticity-guarantee-fine-jewelry.jpg'),
        InputMediaPhoto(
            media='https://static.ebayinc.com/static/assets/Uploads/Stories/Articles/_resampled/ScaleWidthWzgwMF0/ebay-authenticity-guarantee-fine-jewelry.jpg'),
    ]
    media_group_videos = [
        InputMediaVideo(media=f"{url}") for url in get_static_videos(product.product_uuid)
    ]
    for url in media_group_videos:
        print(url)
    await callback.message.answer_media_group(media=media_group_videos)
    await callback.message.answer_media_group(media=media_group_photos)
    await callback.message.answer(text='Кликните <Назад>, чтобы вернуться в корзину,',
                                  reply_markup=InlineKeyboardMarkup(
                                      inline_keyboard=[[InlineKeyboardButton(text='Назад',
                                                                             callback_data=CallbackFactoryCartProductSwap(
                                                                                 user_id=user_id,
                                                                                 direction='>>',
                                                                                 index=index,
                                                                                 timestamp=datetime.utcnow().strftime(
                                                                                     '%d-%m-%y %H-%M')

                                                                             ).pack())]]))

    await callback.answer()


@router.callback_query(CallbackFactoryCartProductSwap.filter())
async def process_product_cart_swap(callback: CallbackQuery, callback_data: CallbackFactoryCartProductSwap):
    print('inside process_product_cart_swap')
    current_index = int(callback_data.index)
    user_id = callback_data.user_id
    print(current_index)
    print(cart[user_id])
    print(callback_data)
    if not cart.get(user_id, []):
        return await callback.answer('Корзина пуста', show_alert=True)
    if callback_data.direction == '<<':
        if current_index < 0:
            return await callback.answer('Вы уже на первой странице')

    elif callback_data.direction == '>>':
        if current_index == len(cart[user_id]):
            return await callback.answer('Вы уже на последней странице')
    product = cart[callback_data.user_id][current_index]
    await send_product_card_cart_item(update=callback,
                                      kb=create_cart_kb,
                                      index=current_index,
                                      product=product,
                                      callback_data=callback_data)

    print('finished process_product_cart_swap')
    await callback.answer()


@router.callback_query(CallbackFactoryQuantityChange.filter())
async def process_quantity_change_button(callback: CallbackQuery, callback_data: CallbackFactoryQuantityChange):
    user_id = callback_data.user_id
    index = int(callback_data.index)
    if not cart.get(user_id, []):
        return await callback.answer('Корзина пуста', show_alert=True)
    item = cart[user_id][index]
    # category = get_category_uuid_by_product_uuid(item.product_uuid)
    if callback_data.action == '+':
        item.quantity += 1
    elif callback_data.action == '-':
        if item.quantity == 1:
            cart[user_id].pop(index)
            await callback.answer('Товар удален из корзины')
        else:
            item.quantity -= 1
    if cart[user_id]:
        if item not in cart[user_id]:
            item = cart[user_id][0]
            index = 0
        await send_product_card_cart_item(update=callback,
                                          kb=create_cart_kb,
                                          product=item,
                                          index=index,
                                          callback_data=CallbackFactoryFinalizeOrder(
                                              user_id=user_id,
                                              uuid=item.product_uuid,
                                              timestamp=datetime.utcnow().strftime(
                                                  '%d-%m-%y %H-%M')
                                          ))
        if callback_data.action == '+':
            await callback.answer('Количество товара увеличено', cache_time=2)
        elif callback_data.action == '-':
            await callback.answer('Количество товара уменьшено', cache_time=2)

    if not cart[user_id]:
        await callback.message.answer(text="Ниже представлены доступные категории товаров",
                                      reply_markup=create_categories_kb(callback))

    await callback.answer()


@router.callback_query(CallbackFactoryAddToFavorite.filter())
async def process_add_to_favorite_button(callback: CallbackQuery, callback_data: CallbackFactoryAddToFavorite):
    user_id = callback.from_user.id
    product_to_add = get_product(callback_data.uuid)
    users_favorite = favorite_products.get(user_id, [])
    if product_to_add in users_favorite:
        return await callback.answer(text='Товар уже в избранном')
    users_favorite.append(product_to_add)
    favorite_products[user_id] = users_favorite
    await callback.answer(text='Товар добавлен в избранное')


@router.callback_query(CallbackFactoryFavoriteProductsSwap.filter())
async def process_favorite_product_swap_button(callback: CallbackQuery,
                                               callback_data: CallbackFactoryFavoriteProductsSwap):
    print('inside process_product_cart_swap')
    current_index = int(callback_data.index)
    user_id = callback_data.user_id
    if not favorite_products.get(user_id, []):
        return await callback.answer('В избранном ничего нет')
    print(current_index)
    print(favorite_products[user_id])
    print(callback_data)

    if callback_data.direction == '<<':
        if current_index < 0:
            return await callback.answer('Вы уже на первой странице')

    elif callback_data.direction == '>>':
        if current_index == len(favorite_products[user_id]):
            return await callback.answer('Вы уже на последней странице')
    product = favorite_products[callback_data.user_id][current_index]
    await send_product_card_favorite_items(update=callback,
                                           kb=create_favorite_goods_kb,
                                           index=current_index,
                                           product=product)

    print('finished process_product_cart_swap')
    await callback.answer()


@router.message(Text('Мои заказы 📖'))
async def process_my_orders_button(message: Message):
    user_id = message.chat.id
    user_orders = get_user_orders(user_id)
    print(user_orders)
    if not user_orders:
        return await message.answer('У вас еще нет заказов')
    ordered_items = [ItemListedInUserOrders(
        order_id=item.order_id,
        order_date=item.order_start_date,
        product_name=item.product_name,
        quantity=item.quantity,
        price=PriceRepresentation(item.quantity * item.price, 'руб'),
        order_status=item.order_status_name) for item in user_orders]

    summary = print_out_formatted_row(attribute_names=list(order_listing_mapper.values()),
                                      cart_items=ordered_items,
                                      user_id=user_id,
                                      mapper=order_listing_mapper)
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


def define_appropriate_lengths(cart_items: list[CartItem | Row], mapper: dict) -> int:
    final_length = []
    tmp_lengths = []
    for attribute in mapper:
        attributes_list = [str(getattr(item, attribute)) for item in cart_items]
        max_length = len(max(attributes_list, key=len))
        tmp_lengths.append(max_length)
    for pair in zip([len(item) for item in list(mapper.values())], tmp_lengths):
        final_length.append(max(pair))
    return max(final_length)


def print_out_formatted_row(attribute_names: list, cart_items: list, user_id: str | int, mapper: dict) -> str:
    rows = []
    row_elements = []
    length = max(define_appropriate_lengths(cart_items=cart_items,
                                            mapper=mapper), len('Итого'))
    for index in range(len(attribute_names)):
        row_elements.append(f"{attribute_names[index]}".ljust(length))
    rows.append(f"<pre>{' | '.join(row_elements)}</pre>")

    row_elements.clear()
    for item in cart_items:
        for attribute in mapper:
            row_elements.append(f"{getattr(item, attribute)}".ljust(length))
        rows.append(f"<pre>{' | '.join(row_elements)}</pre>")
        row_elements.clear()
    order_sum = str(PriceRepresentation(num=sum([item.price.num * int(item.quantity) for item in cart_items]),
                                        unit='руб.'))
    rows.append(
        f"<pre>{' | '.join([''.ljust(length), 'Итого:'.ljust(length), order_sum.ljust(length), ''.ljust(length)])}</pre>")
    return '\n'.join(rows)


@router.callback_query(CallbackFactoryOrderConfirmation.filter())
async def process_start_order_confirmation_button(callback: CallbackQuery,
                                                  callback_data: CallbackFactoryOrderConfirmation,
                                                  state: FSMContext):
    user_id = callback.message.chat.id
    if not cart.get(user_id, []):
        return await callback.answer('Корзина пуста', show_alert=True)

    user_id = callback.message.chat.id
    summary = print_out_formatted_row(attribute_names=list(order_summary_mapper.values()),
                                      cart_items=cart[user_id],
                                      user_id=user_id,
                                      mapper=order_summary_mapper)
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
    if not cart.get(user_id, []):
        return await callback.answer('Действие невозможно', show_alert=True)
    text = 'Введите ваше имя в формате Имя Фамилия, \nнапример: <strong>Федор Достоевский</strong>\n'
    quick_confo = False
    if user_id in get_user_tg_ids_from_db():
        print('changin text to broaden variant')
        text = f'Я вижу, что вы уже оформляли у нас заказ и вводили запрашиваемые данные, ' \
               'чтобы не вводить их повторно, можете нажать на кнопку "Подтвердить мгновенно."\n\n' \
               'Заказ будет оформлен на ваш профиль \n\n' \
               'Если данные поменялись, то введите их заново. \n\n' \
               'Введите ваше имя в формате Имя Фамилия, \nнапример: <strong>Федор Достоевский</strong>\n\n'
    quick_confo = True
    user_db_data = get_user_by_tg_id(user_id)
    user_profile = UserProfile()
    for key in user_profile.__dict__:
        user_profile.__dict__[key] = getattr(user_db_data, key)
    user_profiles[user_id] = user_profile
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


@router.message(F.text.regexp(re.compile(r'\w+ \w+')), FSMOrderConfirmation.input_name)
async def process_input_name_successful(message: Message, state: FSMContext):
    first_name, last_name = message.text.split()
    user_profile = UserProfile()
    user_profile.first_name, user_profile.last_name = first_name, last_name
    user_id = message.chat.id
    user_profiles[user_id] = user_profile
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
    user_profiles[user_id].address = message.text
    await state.set_state(FSMOrderConfirmation.input_age)


@router.message(F.text.regexp(re.compile(r'\d{1,2}')), FSMOrderConfirmation.input_age)
async def process_input_phone(message: Message, state: FSMContext):
    user_id = message.chat.id
    user_profiles[user_id].age = message.text
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
    user_profiles[user_id].phone = message.text
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
        user_profiles[user_id].email = email
    user_profile: UserProfile = user_profiles[user_id]
    if user_id in get_user_tg_ids_from_db():
        action = 'update'
    else:
        action = 'add'
    add_user_to_db(
        action=action,
        user_tg_id=user_id,
        username=username,
        first_name=user_profile.first_name,
        last_name=user_profile.last_name,
        phone=user_profile.phone,
        age=user_profile.age,
        email=user_profile.email,
        address=user_profile.address,
    )
    add_order_to_db(
        user_tg_id=user_id,
        user_cart=cart[user_id]
    )
    user_db_id = get_user_id_by_tg_id(user_id)
    print(cart[user_id])
    print(user_profiles[user_id])
    print(get_user_orders(user_db_id))
    cart[user_id].clear()

    await message.answer(
        text='Спасибо за заказ! Для уточнения остальных деталей с вами в ближайшее время свяжется менеджер магазина',
        reply_markup=static_common_buttons_menu(is_persistent=True))


@router.message(FSMOrderConfirmation.input_email)
async def process_input_email_unsuccessful(message: Message):
    await message.answer(text=f"Кажется, введенынй вами email не соответсвует указанному формату.\nПопробуйте еще раз")
