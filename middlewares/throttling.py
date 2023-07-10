from typing import Callable, Awaitable, Any

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from aiogram.fsm.state import default_state


class FSMCheckingMiddleware(BaseMiddleware):
    async def __call__(
            self,
            handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[any]],
            event: TelegramObject,
            data: dict[str, Any]
    ) -> Any:
        print('before handling')
        q = await data['state'].get_state()
        if q is None:
            return
        res = await handler(event, data)
        print('before handling')
        return res
