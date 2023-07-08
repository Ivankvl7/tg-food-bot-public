from aiogram.filters.state import State, StatesGroup


class FSMBrowsingState(StatesGroup):
    browsing_main_menu_catalog = State()
    browsing_categories: State = State()
    browsing_goods: State = State()
