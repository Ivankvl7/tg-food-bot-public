from aiogram import Bot
from aiogram.types import BotCommand
from lexicon.LEXICON import basic_menu


async def main_commands_menu(bot: Bot) -> None:
    main_menu_commands: list[BotCommand] = [BotCommand(command=f"/{key}", description=basic_menu[key]) for key in
                                            basic_menu.keys()]

    await bot.set_my_commands(main_menu_commands)
