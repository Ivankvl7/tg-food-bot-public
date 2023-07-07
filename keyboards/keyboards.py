from aiogram.utils.keyboard import KeyboardButton, ReplyKeyboardBuilder, InlineKeyboardButton, InlineKeyboardBuilder, \
    ReplyKeyboardMarkup, InlineKeyboardMarkup
from aiogram.types import CallbackQuery, Message
from lexicon.lexicon_ru import static_keyboard, start_follow_up_menu
from lexicon.LEXICON import pagination_buttons
from database.database import goods


def static_common_buttons_menu() -> ReplyKeyboardMarkup:
    # creating buttons for main page keyboard
    buttons: list[KeyboardButton] = [KeyboardButton(text=static_keyboard[key]) for key in static_keyboard.keys()]

    # creating kb builder
    static_common_menu: ReplyKeyboardBuilder = ReplyKeyboardBuilder()

    # adding buttons to the builder
    static_common_menu.row(*buttons, width=2)

    return static_common_menu.as_markup()


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
def create_pagination_keyboard(page_num: int, category: str):
    kb: InlineKeyboardBuilder = InlineKeyboardBuilder()
    number_of_goods_in_category: int = len(goods[category])
    page_num_incremented = page_num + 1
    if page_num == 0:
        kb.add(InlineKeyboardButton(text=f"{page_num_incremented}/{number_of_goods_in_category}", callback_data=page_num),
               InlineKeyboardButton(text=f"{pagination_buttons['forward']}", callback_data='forward'))
    elif 0 < page_num < number_of_goods_in_category - 1:
        kb.add(InlineKeyboardButton(text=f"{pagination_buttons['backward']}", callback_data='backward'),
               InlineKeyboardButton(text=f"{page_num_incremented}/{number_of_goods_in_category}", callback_data=page_num),
               InlineKeyboardButton(text=f"{pagination_buttons['forward']}", callback_data='forward'))
    else:
        kb.add(InlineKeyboardButton(text=f"{pagination_buttons['backward']}", callback_data='backward'),
               InlineKeyboardButton(text=f"{page_num_incremented}/{number_of_goods_in_category}", callback_data=page_num))
    kb.adjust(3)
    return kb.as_markup(resize_keyboard=True)


def create_categories_list():
    kb: InlineKeyboardBuilder = InlineKeyboardBuilder()
    buttons = [InlineKeyboardButton(text=category, callback_data=category) for category in goods]
    kb.row(*buttons)
    kb.add(InlineKeyboardButton(text='Назад', callback_data='return_back'))
    kb.adjust(1, repeat=True)
    return kb.as_markup()
