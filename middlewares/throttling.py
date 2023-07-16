from typing import Callable, Awaitable, Any
from aiogram.types import CallbackQuery
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from utils.utils import time_validity_check


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

