from aiogram.utils.keyboard import KeyboardButton, ReplyKeyboardBuilder, InlineKeyboardButton, InlineKeyboardBuilder, \
    ReplyKeyboardMarkup, InlineKeyboardMarkup
from lexicon.LEXICON import pagination_buttons, product_action_buttons, special_buttons, static_keyboard, \
    start_follow_up_menu
from database.database import goods


def static_common_buttons_menu(**keyboard_options) -> ReplyKeyboardMarkup:
    # creating buttons for main page keyboard
    buttons: list[KeyboardButton] = [KeyboardButton(text=static_keyboard[key]) for key in static_keyboard.keys()]

    # creating kb builder
    static_common_menu: ReplyKeyboardBuilder = ReplyKeyboardBuilder()

    # adding buttons to the builder
    static_common_menu.row(*buttons, width=2)

    return static_common_menu.as_markup(**keyboard_options)


def generate_follow_up_menu() -> InlineKeyboardMarkup:
    # creating keyboard with listed goods categories
    buttons: list[InlineKeyboardButton] = [
        InlineKeyboardButton(text=start_follow_up_menu[key][0], callback_data='catalog')
        for
        key in
        start_follow_up_menu]
    # building categories menu
    follow_up_menu: InlineKeyboardBuilder = InlineKeyboardBuilder()
    follow_up_menu.row(*buttons)

    return follow_up_menu.as_markup()


# generating pagination keyboard which depends on the current page num
def create_pagination_keyboard_and_product_actions(page_num: int, category: str):
    # initializing kb builder
    kb: InlineKeyboardBuilder = InlineKeyboardBuilder()

    # getting number of goods related to chosen category
    number_of_goods_in_category: int = len(goods[category])

    # buttons add_to_cart and proceed_with_the_order
    product_actions: list[InlineKeyboardButton] = [
        InlineKeyboardButton(text=f'{key}', callback_data=f"{product_action_buttons[key]}") for key in
        product_action_buttons]

    # adding buttons to kb builder and adjusting representation
    kb.add(*product_actions)

    # generating correct pagination depending on current page
    page_num_incremented = page_num + 1
    second_row = 2
    if page_num == 0:
        kb.add(
            InlineKeyboardButton(text=f"{page_num_incremented}/{number_of_goods_in_category}", callback_data=page_num),
            InlineKeyboardButton(text=f"{pagination_buttons['forward']}", callback_data='forward'))
    elif 0 < page_num < number_of_goods_in_category - 1:
        kb.add(InlineKeyboardButton(text=f"{pagination_buttons['backward']}", callback_data='backward'),
               InlineKeyboardButton(text=f"{page_num_incremented}/{number_of_goods_in_category}",
                                    callback_data=page_num),
               InlineKeyboardButton(text=f"{pagination_buttons['forward']}", callback_data='forward'))
        second_row = 3
    else:
        kb.add(InlineKeyboardButton(text=f"{pagination_buttons['backward']}", callback_data='backward'),
               InlineKeyboardButton(text=f"{page_num_incremented}/{number_of_goods_in_category}",
                                    callback_data=page_num))

    # adding last 'get back' button
    kb.add(InlineKeyboardButton(text=pagination_buttons['get_one_step_back'], callback_data="get_one_step_back"))

    # adjusting pagination
    kb.adjust(2, second_row, 1)
    return kb.as_markup(resize_keyboard=True)


def create_categories_list():
    kb: InlineKeyboardBuilder = InlineKeyboardBuilder()
    buttons = [InlineKeyboardButton(text=category, callback_data=category) for category in goods]
    kb.row(*buttons)
    kb.add(InlineKeyboardButton(text='Назад', callback_data='get_one_step_back'))
    kb.adjust(1, repeat=True)
    return kb.as_markup()


def create_personal_menu_buttons():
    kb: InlineKeyboardBuilder = InlineKeyboardBuilder()
    buttons = [InlineKeyboardButton(text=personal_menu_buttons[button], callback_data=button) for button in
               personal_menu_buttons]
    kb.add(*buttons)
    kb.add(InlineKeyboardButton(text='Закрыть', callback_data='close_menu_window'))
    kb.adjust(1, repeat=True)
    return kb.as_markup()
