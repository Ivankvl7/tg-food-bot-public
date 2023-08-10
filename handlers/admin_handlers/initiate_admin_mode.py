from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from keyboards.user_keyboards import static_common_buttons_menu
from middlewares.throttling import TimingMiddleware, IdMiddleware
from config_data.config import load_config
from aiogram.fsm.context import FSMContext
from states.admin_states import AdminStates

# router to navigate catalog related requests
router: Router = Router()
router.callback_query.middleware(TimingMiddleware())
router.callback_query.middleware(IdMiddleware())


def get_admin_ids() -> list[int]:
    import os
    path = os.path.dirname(os.path.dirname(os.path.dirname(os.getcwd()))) + '/.env'
    config = load_config(path)
    admin_ids = config.tg_bot.admin_ids
    return admin_ids


@router.message(Command(commands=["turn_on_admin_mode"]))
async def process_admin_mode_command(message: Message, state: FSMContext) -> None:
    user_id: int = message.chat.id
    admin_ids = get_admin_ids()
    if user_id in admin_ids:
        await state.set_state(AdminStates.admin_start)
        print(f"setting admin_start state, curr state = ", end='')
        print(await state.get_state())
        await message.answer(text='Режим администратора успешно активирован',
                             reply_markup=static_common_buttons_menu(admin_mode=True))
    else:
        await message.answer(
            'Вы не прошли аутентификацию. Свяжитесь с администратором магазина, если считаете, что это ошибка')
