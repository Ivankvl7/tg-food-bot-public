from aiogram.filters.state import State, StatesGroup


class FSMBrowsingState(StatesGroup):
    browsing_main_menu_catalog = State()
    browsing_categories: State = State()
    browsing_goods: State = State()
    browsing_personal_account: State = State()
    browsing_personal_address: State = State()
    browsing_static_balance_page: State = State()
    browsing_static_help_page: State = State()
    browsing_static_cart_page: State = State()
    browsing_increase_balance_page: State() = State()
    browsing_personal_query_page: State() = State()
