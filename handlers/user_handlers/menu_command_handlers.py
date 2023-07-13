from aiogram.types import Message
from aiogram import Router
from aiogram.filters import Command
from keyboards import keyboards
from lexicon.LEXICON import command_handlers, start_follow_up_menu
from aiogram.fsm.context import FSMContext
from utils.utils import cache_user
from database.database import states_stack

# creating router to navigate common users requests
router: Router = Router()


# handler for main menu commands, the commands are stored in lexicon.lexicon_ru.basic_commands dict
@router.message(Command(commands=list(command_handlers.keys())))
async def start_command_handler(message: Message, state: FSMContext):
    # print(await state.get_state())
    await state.clear()
    user_id: int = message.from_user.id
    print(await state.get_state())
    cache_user(message)
    command = message.text.strip('/')
    states_stack[user_id].clear()
    await message.answer(text=command_handlers[command],
                         reply_markup=keyboards.static_common_buttons_menu())
    await message.answer(text=start_follow_up_menu[command][1],
                         reply_markup=keyboards.generate_follow_up_menu())
