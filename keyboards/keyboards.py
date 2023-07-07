from aiogram.utils.keyboard import KeyboardButton, ReplyKeyboardBuilder, InlineKeyboardButton, InlineKeyboardBuilder, \
    ReplyKeyboardMarkup, InlineKeyboardMarkup
from aiogram.types import CallbackQuery, Message
from lexicon.lexicon_ru import static_keyboard, categories, start_follow_up_menu


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
    buttons: list[InlineKeyboardButton] = [InlineKeyboardButton(text=start_follow_up_menu[key][0], callback_data=key) for
                                           key in
                                           start_follow_up_menu]
    # building categories menu
    follow_up_menu: InlineKeyboardBuilder = InlineKeyboardBuilder()
    follow_up_menu.row(*buttons)

    return follow_up_menu.as_markup()


def catalog() -> InlineKeyboardMarkup:
    # creating keyboard with listed goods categories
    buttons: list[InlineKeyboardButton] = [InlineKeyboardButton(text=categories[key], callback_data=key) for key in
                                           categories]
    # building categories menu
    inline_categories_menu: InlineKeyboardBuilder = InlineKeyboardBuilder()
    inline_categories_menu.row(*buttons)

    return inline_categories_menu.as_markup()
