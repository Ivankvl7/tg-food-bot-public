import os
import asyncio
from config_data.config import load_config, Config
from aiogram import Bot, Dispatcher
from keyboards.set_menu import main_commands_menu
from handlers import user_handlers


# .env should be placed in the same directory as bot.py
async def main():
    path: str = os.getcwd() + '/.env'

    # acquiring config, personal token and admin ids
    config: Config = load_config(path)
    token: str = config.tg_bot.token
    admin_ids: list = config.tg_bot.admin_ids

    # initializing bot and dispatcher
    bot: Bot = Bot(token)
    dp: Dispatcher = Dispatcher()


    # registering main menu commands in root dispatcher
    dp.startup.register(main_commands_menu)

    # registering child routers
    dp.include_routers(user_handlers.common_users_router)

    # skipping updates received while backed was offline
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
