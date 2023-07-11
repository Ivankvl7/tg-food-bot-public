from aiogram.types import Message
from database.database import user_status, states_stack


def cache_user(message: Message) -> dict:
    user_id: int = message.from_user.id
    if user_id not in user_status:
        user_status[user_id] = dict()
        user_status[user_id]['balance'] = 0
        user_status[user_id]['delivery address'] = 'Не указан'
        states_stack[user_id] = []

    return user_status[user_id]
