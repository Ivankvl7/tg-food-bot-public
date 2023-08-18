from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from config_data.config import Config, load_config
from keyboards.user_keyboards import static_common_buttons_menu
from middlewares.throttling import TimingMiddleware, IdMiddleware
from states.admin_states import AdminStates


router: Router = Router()
router.callback_query.middleware(TimingMiddleware())
router.callback_query.middleware(IdMiddleware())


def get_admin_ids() -> list[int]:
    import os
    path: str = os.path.dirname(os.path.dirname(os.path.dirname(os.getcwd()))) + '/.env'
    config: Config = load_config(path)
    admin_ids: list[int] = config.tg_bot.admin_ids
    return admin_ids


@router.message(Command(commands=["admin_mode"]))
async def process_admin_mode_command(message: Message, state: FSMContext) -> None:
    user_id: int = message.chat.id
    admin_ids: list[int] = get_admin_ids()
    if user_id in admin_ids:
        await state.set_state(AdminStates.admin_start)
        await message.answer(text='Режим администратора успешно активирован',
                             reply_markup=static_common_buttons_menu(admin_mode=True))
    else:
        await message.answer(
            'Вы не прошли аутентификацию. Свяжитесь с администратором магазина, если считаете, что это ошибка')
