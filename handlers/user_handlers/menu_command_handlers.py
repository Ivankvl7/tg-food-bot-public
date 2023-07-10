import asyncio
from aiogram.utils.keyboard import ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
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
from middlewares.throttling import FSMCheckingMiddleware
from services.services import cache_user

# creating router to navigate common users requests
router: Router = Router()


# handler for main menu commands, the commands are stored in lexicon.lexicon_ru.basic_commands dict
@router.message(Command(commands=list(command_handlers.keys())))
async def start_command_handler(message: Message, state: FSMContext):
    # print(await state.get_state())
    await state.clear()
    print(await state.get_state())
    cache_user(message)
    command = message.text.strip('/')
    await message.answer(text=command_handlers[command],
                         reply_markup=keyboards.static_common_buttons_menu())
    await message.answer(text=start_follow_up_menu[command][1],
                         reply_markup=keyboards.generate_follow_up_menu())
