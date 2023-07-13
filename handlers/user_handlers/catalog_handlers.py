import asyncio

from aiogram.types import CallbackQuery
from aiogram.types.input_media_photo import InputMediaPhoto
from aiogram import Router
from aiogram.filters import Text
from keyboards import keyboards
from database.database import goods, user_status, states_stack
from lexicon.LEXICON import pagination_buttons, product_action_buttons, start_follow_up_menu
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from states.states import FSMBrowsingState
from aiogram.fsm.state import default_state
from filters.catalog_filter import CatalogFilterCallbacks
from aiogram.utils.keyboard import InlineKeyboardMarkup, InlineKeyboardButton
from database.database import cart
from models.models import CartItem
# creating router to navigate common users requests
router: Router = Router()


# listing available categories of goods
@router.callback_query(StateFilter(default_state), Text('catalog'))
async def process_catalog_button(callback: CallbackQuery, state: FSMContext):
    user_id: int = callback.from_user.id
    await callback.message.edit_text('Доступные категории товаров')
    await callback.message.edit_reply_markup(reply_markup=keyboards.create_categories_list())
    states_stack[user_id].append(FSMBrowsingState.browsing_categories)
    await state.set_state(FSMBrowsingState.browsing_categories)
    print('inside catalog button')
    print(f"states stack is following: {states_stack[user_id]}")


# opens goods list from selected category
@router.callback_query(
    StateFilter(FSMBrowsingState.browsing_categories), Text(text=list(category for category in goods)))
async def process_products_listing(callback: CallbackQuery, state: FSMContext):
    user_id: int = callback.from_user.id
    user_status[user_id]['current_page']: int = 0
    current_page: int = user_status[user_id]['current_page']
    user_status[user_id]['browsing_category']: str = callback.data
    browsing_category: str = user_status[user_id]['browsing_category']
    states_stack[user_id].append(FSMBrowsingState.browsing_goods)
    await state.set_state(FSMBrowsingState.browsing_goods)
    print('setting FSMBrowsingState.browsing_goods state')
    await callback.message.delete()
    await callback.message.answer_photo(
        caption='\n'.join(
            [f"<b>{key}:</b> {value}" for key, value in
             goods[browsing_category][current_page].items()]),
        parse_mode='HTML',
        photo='https://eavf3cou74b.exactdn.com/wp-content/uploads/2021/09/21104001/How-to-Photograph-Jewelry-10-768x512.jpg?strip=all&lossy=1&ssl=1',
        reply_markup=keyboards.create_pagination_keyboard_and_product_actions(page_num=current_page,
                                                                              category=callback.data)
    )
    print('inside product listing')
    print(f"states stack is following: {states_stack[user_id]}")


# handles pagination when browsing goods
@router.callback_query(StateFilter(FSMBrowsingState.browsing_goods),
                       Text(text=list(pag for pag in pagination_buttons)), ~Text(text='get_one_step_back'))
async def process_pagination_buttons(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    browsing_category = user_status[user_id]['browsing_category']
    browsing_category_goods = [item for item in goods[browsing_category]]
    current_page = user_status[user_id]['current_page']
    if callback.data == "forward":
        if user_status[user_id]['current_page'] < len(browsing_category_goods) - 1:
            user_status[user_id]['current_page'] = current_page + 1
        else:
            await callback.answer()
    elif callback.data == "backward":
        if user_status[user_id]['current_page'] > 0:
            user_status[user_id]['current_page'] = current_page - 1
        else:
            await callback.answer()
    current_page = user_status[user_id]['current_page']

    await callback.message.edit_media(
        media=InputMediaPhoto(media='https://media.istockphoto.com/id/954397602/photo/two-golden-sapphire-earr'
                                    'ings-with-small-diamonds.jpg?s=612x612&w=0&k=20&c=QxkA9ZCAQHDicBpV8g5As_0'
                                    '5tbPpaJqZoPvlfSTnQ78=',
                              caption='\n'.join(
                                  [f"<b>{key}:</b> {value}" for key, value in
                                   goods[browsing_category][current_page].items()]),
                              parse_mode='HTML'))

    await callback.message.edit_reply_markup(text='Product description',
                                             reply_markup=keyboards.create_pagination_keyboard_and_product_actions(
                                                 page_num=current_page,
                                                 category=browsing_category))
    print('continuing to browse goods')
    print(f"states stack is following: {states_stack[user_id]}")


@router.callback_query(Text('get_one_step_back'), StateFilter(*[FSMBrowsingState.browsing_categories,
                                                                FSMBrowsingState.browsing_goods,
                                                                ]))
async def processing_get_back_button(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()
    user_id = callback.from_user.id
    if states_stack:
        states_stack[user_id].pop(-1)
    if await state.get_state() == FSMBrowsingState.browsing_categories:
        await state.clear()
        print('inside browsing_categories state')
        await callback.message.answer(text=start_follow_up_menu["start"][1],
                                      reply_markup=keyboards.generate_follow_up_menu())
    elif await state.get_state() == FSMBrowsingState.browsing_goods:
        print('inside browsing_goods state')
        await state.set_state(FSMBrowsingState.browsing_categories)
        await callback.message.answer(text='Доступные категории товаров',
                                      reply_markup=keyboards.create_categories_list())
    print(await state.get_state())
    print('inside processing_get_back_button')
    print(f" renewed states stack is following {states_stack}")


@router.callback_query(CatalogFilterCallbacks(states_obj=FSMBrowsingState,
                                              pag=pagination_buttons,
                                              cats=goods,
                                              action_buttons=product_action_buttons))
async def handling_catalog_queries_out_from_unallowed_states(callback: CallbackQuery, state: FSMContext):
    await callback.answer(text='Закройте все окна помимо каталога, чтобы вернуться в него, '
                               'либо начните просмотр каталога заново, введя команду /start',
                          show_alert=True,
                          cache_time=3
                          )


@router.callback_query(StateFilter(FSMBrowsingState.browsing_goods), Text('proceed_with_the_order'))
async def proceed_with_order_from_goods_browsing(callback: CallbackQuery, state: FSMContext):
    user_id: int = callback.from_user.id
    # await callback.message.delete()
    user_cart = cart.get(user_id, [])
    if not user_cart:
        await callback.answer(text="Корзина пуста\n"
                                   "Сначала добавьте туда товары", show_alert=True)
    else:
        await state.set_state(FSMBrowsingState.browsing_static_cart_page)
        states_stack[user_id].append(FSMBrowsingState.browsing_static_cart_page)
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


@router.callback_query(StateFilter(FSMBrowsingState.browsing_goods), Text('add_to_cart'))
async def process_add_to_cart_button(callback: CallbackQuery, state: FSMContext):
    client_id = callback.from_user.id
    if client_id not in cart:
        cart[client_id] = []
    category = user_status[client_id]['browsing_category']
    item_index = user_status[client_id]['current_page']
    cart[client_id].append(CartItem(*goods[category][item_index].values()))
    await callback.message.answer(text='Товар успшено добавлен в корзину')
    await callback.answer()
    print(cart[client_id])

