from aiogram.types import CallbackQuery, Message
from aiogram import Router
from middlewares.throttling import TimingMiddleware, IdMiddleware

router: Router = Router()


@router.callback_query()
async def processing_non_defined_requests(callback: CallbackQuery):
    print('processing_non_defined_requests')
    print(f"callback_data = {callback.data}")
    await callback.answer('Кнопка неактивна')


@router.message()
async def processing_non_defined_requests(message: Message):
    await message.reply(text='Извините, я не знаю такой команды')
