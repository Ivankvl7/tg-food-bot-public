from datetime import datetime
from aiogram.types import Message
from aiogram import Router
from aiogram.filters import Command
from keyboards import keyboards
from lexicon.LEXICON import command_handlers
from aiogram.filters import Text
from keyboards.keyboards import create_categories_kb
from aiogram.types import Message, CallbackQuery

# creating router to register local handlers
router: Router = Router()


@router.message(Command(commands=["start", "help", "payment", "delivery", "legal"]))
async def process_start_command(message: Message):
    command = message.text.strip('/')
    await message.answer(text=command_handlers[command],
                         reply_markup=keyboards.static_common_buttons_menu())


@router.message(Text('Каталог 📕'))
@router.message(Command('catalog'))
async def process_catalog_command(update: CallbackQuery | Message):
    print('inside catalog')
    print(update.json())
    if isinstance(update, CallbackQuery):
        await update.message.answer(text="Ниже представлены доступные категории товаров",
                                    reply_markup=create_categories_kb(update))
    elif isinstance(update, Message):
        await update.answer(text="Ниже представлены доступные категории товаров",
                            reply_markup=create_categories_kb(update))
    print('catalog processing finished')


