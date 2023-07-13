from aiogram.types import CallbackQuery, Message
from aiogram import Router

router: Router = Router()


@router.callback_query()
async def processing_non_defined_requests(callback: CallbackQuery):
    print(callback.data)
    await callback.answer()


@router.message()
async def processing_non_defined_requests(message: Message):
    await message.reply(text='Извините, я не знаю такой команды')
