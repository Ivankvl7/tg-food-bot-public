from typing import Callable, Awaitable, Any

from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery, Message
from aiogram.types import TelegramObject

from database.methods.redis_methods import get_user_device, set_user_device
from keyboards.user_keyboards import create_device_selection_kb
from utils.utils import time_validity_check


class TimingMiddleware(BaseMiddleware):
    """Checks if keyboard has been expired. Default time is 5 minutes"""
    async def __call__(
            self,
            handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
            event: CallbackQuery,
            data: dict[str, Any]) -> Any:
        if await time_validity_check(data['callback_data']):
            return await event.answer(text='Меню устарело', show_alert=True)
        result = await handler(event, data)
        return result


class IdMiddleware(BaseMiddleware):
    """Drops a user request if chat.id and user.id are inconsistent"""
    async def __call__(
            self,
            handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
            event: CallbackQuery,
            data: dict[str, Any]) -> Any:
        if event.from_user.id != data['callback_data'].user_id:
            return await event.answer(text='Вы БОТ!', show_alert=True)
        result = await handler(event, data)
        return result


class DeviceMiddleware(BaseMiddleware):
    """Offers a user to choose device type which will determine text messages formatting"""
    async def __call__(
            self,
            handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
            event: CallbackQuery | Message,
            data: dict[str, Any]) -> Any:
        if isinstance(event, CallbackQuery):
            update: Message = event.message
        else:
            update: Message = event
        user_id: int = update.chat.id
        user_device: str = get_user_device(user_id)
        if not user_device:
            set_user_device(user_id)
            return await update.answer(
                text="Прежде чем продолжить, пожалуйста, выберите тип вашего устройства. Это необходимо для вывода информации в подходящем "
                     "для вашего устройства формате\n"
                     "Для продолжения нажмите /start",
                reply_markup=create_device_selection_kb(user_id)
            )
        result = await handler(event, data)
        return result


class AdminModeMiddleware(BaseMiddleware):
    """Filters admin requests"""
    async def __call__(
            self,
            handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
            event: CallbackQuery | Message,
            data: dict[str, Any]) -> Any:
        from handlers.admin_handlers.initiate_admin_mode import get_admin_ids
        if isinstance(event, CallbackQuery):
            user_id: int = event.message.chat.id
            update: Message = event.message
        else:
            user_id: int = event.chat.id
            update: Message = event
        if user_id not in get_admin_ids():
            return await update.answer('В доступе отказано')
        result = await handler(event, data)
        return result
