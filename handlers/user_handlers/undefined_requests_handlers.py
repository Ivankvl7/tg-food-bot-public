from aiogram.types import CallbackQuery, Message
from aiogram import Router
from filters.callbacks import CallbackFactoryDeviceSelection
from database.methods.redis_methods import set_user_device
from keyboards.keyboards import create_categories_kb
from middlewares.throttling import DeviceMiddleware

router: Router = Router()
router.callback_query.middleware(DeviceMiddleware())
router.message.middleware((DeviceMiddleware()))


@router.callback_query(CallbackFactoryDeviceSelection.filter())
async def process_device_selection(callback: CallbackQuery,
                                   callback_data: CallbackFactoryDeviceSelection):
    user_id = callback.message.chat.id
    device = callback_data.device
    set_user_device(user_id=user_id, device=device)
    await callback.answer(text='Спасибо, устройство обновлено, можете продолжать использование бота', cache_time=10)




@router.callback_query()
async def processing_non_defined_requests(callback: CallbackQuery):
    print('processing_non_defined_requests')
    print(f"callback_data = {callback.data}")
    await callback.answer('Кнопка неактивна')


@router.message()
async def processing_non_defined_requests(message: Message):
    await message.reply(text='Извините, я не знаю такой команды')
