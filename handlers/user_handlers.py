from aiogram.types import CallbackQuery, Message
from aiogram.types.input_media_photo import InputMediaPhoto
from aiogram import Router
from aiogram.filters import Command, CommandStart, Text
from keyboards import keyboards
from lexicon.lexicon_ru import command_handlers, start_follow_up_menu
from database.database import image_1, goods, user_status
from lexicon.LEXICON import pagination_buttons

# creating router to navigate common users requests
common_users_router: Router = Router()


# handler for main menu commands, the commands are stored in lexicon.lexicon_ru.basic_commands dict
@common_users_router.message(Command(commands=list(command_handlers.keys())))
async def start_command_handler(message: Message):
    command = message.text.strip('/')
    await message.answer(text=command_handlers[command],
                         reply_markup=keyboards.static_common_buttons_menu())
    await message.answer(text=start_follow_up_menu[command][1],
                         reply_markup=keyboards.generate_follow_up_menu())


# listing avalable categories of goods
@common_users_router.callback_query(Text(text='catalog'))
async def process_catalog_button(callback: CallbackQuery):
    await callback.message.edit_text('Доступные категории товаров')
    await callback.message.edit_reply_markup(reply_markup=keyboards.create_categories_list())


# browsing category1. I believe handling categoires should be processed with FSM
@common_users_router.callback_query(Text(text=list(key for key in goods)))
async def process_products_listing(callback: CallbackQuery):
    user_id = callback.from_user.id
    if user_id not in user_status:
        user_status[user_id] = dict()
    user_status[user_id]['current_page'] = 0
    current_page = user_status[user_id]['current_page']
    user_status[user_id]['browsing_category'] = callback.data
    await callback.message.answer_photo(
        caption='Product description',
        photo='https://eavf3cou74b.exactdn.com/wp-content/uploads/2021/09/21104001/How-to-Photograph-Jewelry-10-768x512.jpg?strip=all&lossy=1&ssl=1',
        reply_markup=keyboards.create_pagination_keyboard(page_num=current_page,
                                                          category=callback.data)
    )


@common_users_router.callback_query(Text(text=list((button for button in pagination_buttons))))
async def process_pagination_buttons(callback: CallbackQuery):
    print(user_status)
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
                              caption='Product description'))

    await callback.message.edit_reply_markup(text='Product description',
                                             reply_markup=keyboards.create_pagination_keyboard(page_num=current_page,
                                                                                               category=browsing_category))
