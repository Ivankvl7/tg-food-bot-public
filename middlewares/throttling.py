from datetime import datetime
from typing import Callable, Awaitable, Any
from aiogram.types import CallbackQuery, Message
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from utils.utils import time_validity_check
from database.methods.redis_methods import get_user_device, set_user_device
from aiogram.utils.keyboard import InlineKeyboardButton, InlineKeyboardMarkup
from models.models import SelectedDevice
from filters.callbacks import CallbackFactoryDeviceSelection
from keyboards.keyboards import create_device_selection_kb


class TimingMiddleware(BaseMiddleware):
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
    async def __call__(
            self,
            handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
            event: (CallbackQuery, Message),
            data: dict[str, Any]) -> Any:
        if isinstance(event, CallbackQuery):
            update = event.message
        else:
            update = event
        user_id = update.chat.id
        user_device = get_user_device(user_id)
        if not user_device:
            set_user_device(user_id)
            return await update.answer(
                text="Прежде чем продолжить, пожалуйста, выберите тип вашего устройства. Это необходимо для вывода информации в подходящем "
                     "для вашего устройства формате",
                reply_markup=create_device_selection_kb(user_id)
            )
        result = await handler(event, data)
        return result
