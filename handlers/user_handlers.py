from aiogram.types import CallbackQuery, Message
from aiogram import Router
from aiogram.filters import Command, CommandStart
from keyboards import keyboards
from lexicon.lexicon_ru import command_handlers, start_follow_up_menu

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


@common_users_router.callback_query()
async def process_products_listing(callback: CallbackQuery):
    category = callback.data


