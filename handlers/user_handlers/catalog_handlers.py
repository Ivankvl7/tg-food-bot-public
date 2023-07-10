import asyncio
from aiogram.utils.keyboard import ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.types import CallbackQuery, Message
from aiogram.types.input_media_photo import InputMediaPhoto
from aiogram import Router
from aiogram.filters import Command, CommandStart, Text
from keyboards import keyboards
from lexicon.lexicon_ru import command_handlers, start_follow_up_menu
from database.database import image_1, goods, user_status
from lexicon.LEXICON import pagination_buttons, product_action_buttons
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from states.states import FSMBrowsingState
from aiogram.fsm.state import default_state
from middlewares.throttling import FSMCheckingMiddleware
from services.services import cache_user
from filters.catalog_filter import CatalogFilterCallbacks

# creating router to navigate common users requests
router: Router = Router()


# listing available categories of goods
@router.callback_query(StateFilter(default_state), Text('catalog'))
async def process_catalog_button(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text('Доступные категории товаров')
    await callback.message.edit_reply_markup(reply_markup=keyboards.create_categories_list())
    await state.set_state(FSMBrowsingState.browsing_categories)


# opens goods list from selected category
@router.callback_query(
    StateFilter(FSMBrowsingState.browsing_categories), Text(text=list(category for category in goods)))
async def process_products_listing(callback: CallbackQuery, state: FSMContext):
    user_id: int = callback.from_user.id
    user_status[user_id]['current_page']: int = 0
    current_page: int = user_status[user_id]['current_page']
    user_status[user_id]['browsing_category']: str = callback.data
    browsing_category: str = user_status[user_id]['browsing_category']
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


# handles pagination when browsing goods
@router.callback_query(StateFilter(FSMBrowsingState.browsing_goods),
                       Text(text=list(pag for pag in pagination_buttons)), ~Text(text='get_one_step_back'))
async def process_pagination_buttons(callback: CallbackQuery, state: FSMContext):
    print(user_status)
    print(callback)
    print(state.get_state())
    user_id = callback.from_user.id
    browsing_category = user_status[user_id]['browsing_category']
    browsing_category_goods = [item for item in goods[browsing_category]]
    current_page = user_status[user_id]['current_page']
    if callback.data == "forward":
        if user_status[user_id]['current_page'] < len(browsing_category_goods) - 1:
            print('incrementing current_page')
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


@router.callback_query(Text('get_one_step_back'))
async def processing_get_back_button(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()
    print('inside processing_get_back_button')
    print(await state.get_state())
    print(user_status)
    print(callback.data)
    print(callback.from_user.id)
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
    elif await state.get_state() == FSMBrowsingState.browsing_personal_account:
        print('handling step back from setting personal account browsing')
    elif await state.get_state() == FSMBrowsingState.browsing_personal_address:
        user_id: int = callback.from_user.id
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
    else:

        print('Улетело вникуда')
        print(await state.get_state())



    # await state.set_state(default_state)


@router.callback_query(CatalogFilterCallbacks(states_obj=FSMBrowsingState, pag=pagination_buttons, cats=goods))
async def handling_catalog_queries_out_from_unallowed_states(callback: CallbackQuery, state: FSMContext):
    await callback.answer(text='Закройте все окна помимо каталога, чтобы вернуться в него, '
                          'либо начните просмотр каталога заново, введя команду /start',
                          show_alert=True,
                          cache_time=3
                          )
