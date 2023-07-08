from aiogram.types import CallbackQuery, Message
from aiogram.types.input_media_photo import InputMediaPhoto
from aiogram import Router
from aiogram.filters import Command, CommandStart, Text
from keyboards import keyboards
from lexicon.lexicon_ru import command_handlers, start_follow_up_menu
from database.database import image_1, goods, user_status
from lexicon.LEXICON import pagination_buttons
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from states.states import FSMBrowsingState
from aiogram.fsm.state import default_state

# creating router to navigate common users requests
common_users_router: Router = Router()


def cache_user(callback: CallbackQuery) -> dict:
    user_id: int = callback.from_user.id
    if user_id not in user_status:
        user_status[user_id] = dict()
    return user_status[user_id]


# handler for main menu commands, the commands are stored in lexicon.lexicon_ru.basic_commands dict
@common_users_router.message(Command(commands=list(command_handlers.keys())))
async def start_command_handler(message: Message, state: FSMContext):
    await state.clear()

    command = message.text.strip('/')
    await message.answer(text=command_handlers[command],
                         reply_markup=keyboards.static_common_buttons_menu())
    await message.answer(text=start_follow_up_menu[command][1],
                         reply_markup=keyboards.generate_follow_up_menu())


# listing available categories of goods
@common_users_router.callback_query(StateFilter(default_state), Text('catalog'))
async def process_catalog_button(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text('Доступные категории товаров')
    await callback.message.edit_reply_markup(reply_markup=keyboards.create_categories_list())
    await state.set_state(FSMBrowsingState.browsing_categories)


# opens goods list from selected category
@common_users_router.callback_query(
    StateFilter(FSMBrowsingState.browsing_categories), Text(text=list(category for category in goods)))
async def process_products_listing(callback: CallbackQuery, state: FSMContext):
    user_id: int = callback.from_user.id
    cache_user(callback)
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
@common_users_router.callback_query(StateFilter(FSMBrowsingState.browsing_goods),
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


@common_users_router.callback_query(Text('get_one_step_back'))
async def processing_get_back_button(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()
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
    # await state.set_state(default_state)


@common_users_router.callback_query()
async def processing_non_defined_requests(callback: CallbackQuery):
    await callback.message.reply(text='Извините, я не знаю такой команды')

@common_users_router.message()
async def processing_non_defined_requests(message: Message):
    await message.reply(text='Извините, я не знаю такой команды')
