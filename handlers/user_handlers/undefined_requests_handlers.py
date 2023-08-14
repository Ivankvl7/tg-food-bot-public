from aiogram import Router
from aiogram.types import CallbackQuery, Message

from database.methods.redis_methods import set_user_device
from filters.callbacks import CallbackFactoryDeviceSelection
from middlewares.throttling import DeviceMiddleware

router: Router = Router()
router.callback_query.middleware(DeviceMiddleware())
router.message.middleware((DeviceMiddleware()))


@router.callback_query(CallbackFactoryDeviceSelection.filter())
async def process_device_selection(callback: CallbackQuery,
                                   callback_data: CallbackFactoryDeviceSelection):
    user_id: int = callback.message.chat.id
    device: str = callback_data.device
    set_user_device(user_id=user_id, device=device)
    await callback.answer(text='Устройство обновлено')


@router.callback_query()
async def processing_non_defined_requests(callback: CallbackQuery):
    await callback.answer('Кнопка неактивна')

@router.message()
async def processing_non_defined_requests(message: Message):
    await message.reply(text='Извините, я не знаю такой команды')
