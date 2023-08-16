from models.models import StaticContentType

product_action_buttons: dict[str, str] = {'add_to_cart': 'Добавить в корзину',
                                          'proceed_with_order': 'Оформить заказ',
                                          'backward': '<<',
                                          'forward': '>>',
                                          'cancel_product_browsing': 'Назад'
                                          }

pagination_buttons: dict[str, str] = {

}

special_buttons: dict[str, str] = {
    "deposit_funds": "Пополнить счет",
    "set_address": "Обновить адрес доставки",
    "Подтвердить заказ": "confirm order"

}

non_pagination_buttons: dict[str, str] = {
    'Закрыть': 'close_menu_window',
    'Назад': 'get_back',
    "Оформить заказ заказ": "finalize order"
}

static_keyboard: dict[str, str] = {
    'catalog': 'Каталог 📕',
    'clients_account': 'Мои заказы 📖',
    'favorite_products': 'Избранное ⭐️',
    'cart': 'Корзина 🛒',
    'change_device': 'Изменить устройство 🖥 🔛📱',
}

basic_menu: dict[str, str] = {
    "start": "Вернуться на главную страницу",
    "help": "Подсказки по взаимодействию с ботом",
    "payment": "Информация об оплате",
    "delivery": "Информация о доставке",
    "submit_request": "Задать вопрос менеджеру",
    "legal": "Юридическая информация магазина",
    "admin_mode": "Включить режим администратора"

}

command_handlers: dict[str, str] = {
    "start": """🍔🍕🥤 Добро пожаловать в наш фуд-шоп! 🥤🍕🍔
Здесь вы можете заказать вкусные бургеры, пиццу и напитки, чтобы насладиться вкусным обедом или ужином прямо у себя дома или в офисе.
Просто выберите категорию, оформите заказ и мы доставим вам вкусную еду быстро и удобно. 
Если у вас есть какие-либо вопросы или нужна помощь, не стесняйтесь спрашивать: /submit_request. Приятного аппетита! 🍽️😊
                        """,

    "payment": "После подтверждение заказа с вами свяжется менеджера магазина и подберет подходящий метод оплаты",

    "delivery": "После подтверждение заказа с вами свяжется менеджера магазина и уточнит время доставки. \n",

    "legal": "Здесь размещается юридическая информация магазина",

    "submit_request": f"Введите ваш вопрос в формате request=<текст>, например:\n"
                      f"request=Где деньги ?\n"
                      f"Менеджер магазина ответ как можно скорее",

    "help": """Для начала взаимодействия с ботом используйте команду /start
Сформируйте и подтвердите ваш заказ, после чего с вами свяжется менеджер и уточнит условия оплаты и достаки
Чтобы задать вопрос менеджеру, воспользуйтесь командой request=<текст запроса>"""

}

product_columns_mapper: dict[str, str] = {
    'product_name': 'Наименование',
    'category_name': 'Категория',
    'price': 'Цена',
    'description': 'Описание',
}

order_summary_mapper: dict[str, str] = {
    'product_name': 'Наименование',
    'price': 'Цена',
    'quantity': 'Количество'
}

order_listing_mapper: dict[str, int | str] = {
    'order_number': 'Номер заказа',
    'order_date': 'Дата заказа',
    'product_name': 'Наименование товара',
    'quantity': 'Количество',
    'price': 'Общая стоимость',
    'order_status': 'Статус заказа'
}

static_extension: dict[StaticContentType, str] = {
    StaticContentType.IMAGE: '.jpg',
    StaticContentType.VIDEO: '.mp4'
}


