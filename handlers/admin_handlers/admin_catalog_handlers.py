import re
from typing import Coroutine

from typing import Sequence
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.filters import Text, StateFilter
from aiogram.types import CallbackQuery, Message

from database.admin_methods.rel_bd_admin_methods import get_existing_categories, delete_category, add_new_category, \
    change_order_status, get_order_status_table
from database.methods.redis_methods import get_user_device
from filters.admin_callbacks import CallbackFactoryAddCategory, CallbackFactoryDelCategory, CallbackFactoryDeletedCat, \
    CallbackFactoryActiveOrders, CallbackFactoryStatusList
from keyboards.admin_keyboards import create_admin_categories_actions_kb, create_categories_deletion_kb, \
    order_status_change_kb, single_close_kb
from middlewares.throttling import TimingMiddleware, IdMiddleware, DeviceMiddleware, AdminModeMiddleware
from states.admin_states import AdminStates
from models.models import AdminStaticKb
from ..user_handlers.catalog_handlers import process_my_orders_button
from lexicon.A_LEXICON import order_status_mapper
from sqlalchemy import Row

# router to navigate catalog related requests
router: Router = Router()
router.callback_query.middleware(TimingMiddleware())
router.callback_query.middleware(IdMiddleware())
router.callback_query.middleware(DeviceMiddleware())
router.message.middleware((DeviceMiddleware()))
router.callback_query.middleware(AdminModeMiddleware())
router.message.middleware(AdminModeMiddleware())


def data_listing(table: list[Row], *column_name) -> str:
    res = []
    for column in column_name:
        tmp = []
        for row in table:
            tmp.append(getattr(row, column))
        res.append(tmp)
    data = []
    for data_row in zip(*res):
        data.append(' '.join(map(str, data_row)))
    return '\n'.join(data)


@router.message(Text('Изменить категории'), StateFilter(AdminStates.admin_start))
async def change_category(message: Message) -> None:
    await message.answer(text="Выберите действие",
                         reply_markup=create_admin_categories_actions_kb(message))


@router.callback_query(CallbackFactoryDelCategory.filter(), StateFilter(AdminStates.admin_start))
async def process_category_deletion(callback: CallbackQuery) -> None:
    await callback.message.answer(text=f"Выберите категорию",
                                  reply_markup=create_categories_deletion_kb(callback))
    await callback.answer()


@router.callback_query(CallbackFactoryDeletedCat.filter(), StateFilter(AdminStates.admin_start))
async def finish_category_deletion(callback: CallbackQuery, callback_data: CallbackFactoryDeletedCat) -> None:
    delete_category(callback_data.cat_id)
    await callback.answer()


@router.callback_query(CallbackFactoryAddCategory.filter(), StateFilter(AdminStates.admin_start))
async def add_category_start(callback: CallbackQuery) -> None:
    await callback.message.answer(
        text="Введите название категории в следующем формате: \n"
             "Категория = <название категории>\n"
             "Например, Категория = Туфли"
    )
    await callback.answer()


@router.message(F.text.regexp(re.compile(r'[Кк]атегория ?= ?.+')), StateFilter(AdminStates.admin_start))
async def add_category_finish(message: Message) -> None:
    category_name: str = message.text.split("=")[-1].strip()
    add_new_category(category_name=category_name)
    await message.answer(
        text='Категория успешно добавлена'
    )


@router.message(Text(AdminStaticKb.ORDER_BUTTON.value), StateFilter(AdminStates.admin_start))
async def process_order_status_change_start(message: Message) -> None:
    await message.answer(
        text='Для изменения статуса заказа воспользуйтесь командой\n'
             'order_id <id>=<status_id>\n\n'
             'например:\n'
             'order_id 1=2',
        reply_markup=order_status_change_kb(message)
    )


@router.message(F.text.regexp(re.compile(r'order_id *\d+ *= *\d+')), StateFilter(AdminStates.admin_start))
async def process_order_status_change_finish(message: Message) -> None:
    order_info, status_id = map(str.strip, message.text.split('='))
    order_id = int(order_info.split()[-1])
    status_id: int = int(status_id)
    print(f"order_id={order_id}\n"
          f"status_id={status_id}")
    change_order_status(order_id, status_id)
    await message.answer(
        text='Статус успешно обновлен'
    )


@router.callback_query(CallbackFactoryActiveOrders.filter(), StateFilter(AdminStates.admin_start))
async def process_active_orders(callback: CallbackQuery,
                                state: FSMContext) -> None:
    return await process_my_orders_button(callback.message, state)


@router.callback_query(CallbackFactoryStatusList.filter(), StateFilter(AdminStates.admin_start))
async def process_status_list(callback: CallbackQuery) -> None:
    table: list[Row] = get_order_status_table()
    await callback.message.answer(
        text=data_listing(table, 'order_status_id', 'order_status_name'),
        reply_markup=single_close_kb(callback)
    )
    await callback.answer()

