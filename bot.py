import asyncio
import logging
import os

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.redis import Redis, RedisStorage

from config_data.config import load_config, Config
from handlers.admin_handlers import admin_catalog_handlers, admin_product_handlers, initiate_admin_mode
from handlers.user_handlers import menu_command_handlers, catalog_handlers, cart_handlers, order_processing, \
    favorite_handlers, undefined_requests_handlers
from keyboards.set_menu import main_commands_menu


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

    # initializing bot and dispatcher
    bot: Bot = Bot(token)
    dp: Dispatcher = Dispatcher(storage=storage)

    # registering main menu commands in root dispatcher
    dp.startup.register(main_commands_menu)

    # registering child routers
    dp.include_routers(menu_command_handlers.router, catalog_handlers.router, cart_handlers.router,
                       order_processing.router, favorite_handlers.router)
    dp.include_routers(initiate_admin_mode.router, admin_catalog_handlers.router, admin_product_handlers.router)
    dp.include_routers(undefined_requests_handlers.router)

    # skipping updates received while backed was offline
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
