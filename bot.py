import os
import asyncio
from config_data.config import load_config, Config
from aiogram import Bot, Dispatcher
from keyboards.set_menu import main_commands_menu
from handlers import user_handlers
import logging
import redis
from aiogram.fsm.storage.redis import Redis, RedisStorage
from handlers.user_handlers import static_menu_handlers, catalog_handlers, menu_command_handlers, \
    undefined_requests_handlers


# .env should be placed in the same directory as bot.py
async def main():
    logging.basicConfig(level=logging.INFO)
    path: str = os.getcwd() + '/.env'

    # initializing redis
    redis: Redis = Redis(host='localhost')
    storage: RedisStorage = RedisStorage(redis=redis)

    # acquiring config, personal token and admin ids
    config: Config = load_config(path)
    token: str = config.tg_bot.token
    admin_ids: list = config.tg_bot.admin_ids

    # initializing bot and dispatcher
    bot: Bot = Bot(token)
    dp: Dispatcher = Dispatcher(storage=storage)

    # registering main menu commands in root dispatcher
    dp.startup.register(main_commands_menu)

    # registering child routers
    dp.include_routers(catalog_handlers.router, menu_command_handlers.router, static_menu_handlers.router,
                       undefined_requests_handlers.router)

    # skipping updates received while backed was offline
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
