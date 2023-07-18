product_action_buttons = {'add_to_cart': 'Добавить в корзину',
                          'proceed_with_order': 'Оформить заказ',
                          'backward': '<<',
                          'forward': '>>',
                          'cancel_product_browsing': 'Назад'
                          }

pagination_buttons: dict = {

}

special_buttons: dict = {
    "deposit_funds": "Пополнить счет",
    "set_address": "Обновить адрес доставки",
    "Подтвердить заказ": "confirm order"

}

non_pagination_buttons: dict = {
    'Закрыть': 'close_menu_window',
    'Назад': 'get_back',
    "Оформить заказ заказ": "finalize order"
}

static_keyboard: dict = {
    'catalog': 'Каталог 📕',
    'clients_account': 'Мои заказы 📖',
    'favorite_products': 'Избранное ⭐️',
    'cart': 'Корзина 🛒',
    'help': 'Помощь 🆘'
}

basic_menu: dict = {
    "start": "Вернуться на главную страницу",
    "catalog": "Перейти в каталог",
    "help": "Подсказки по взаимодействию с ботом",
    "payment": "Информация об оплате",
    "delivery": "Информация о доставке",
    "submit_request": "Задать вопрос менеджеру",
    "legal": "Юридическая информация о магазине"

}

command_handlers: dict = {
    "start": """Добро пожаловать в наш бот-магазин ювелирных изделий! У нас вы найдете широкий ассортимент уникальных и красивых украшений для всех случаев жизни. От классических колец и ожерелий до модных браслетов и серег, наш бот предлагает изысканные изделия из самых качественных материалов. Будьте в тренде и выразите свою индивидуальность с нашими эксклюзивными украшениями. Просто просмотрите наш каталог, выберите свои любимые украшения и оформите заказ прямо в боте. Наша команда готова помочь вам с любыми вопросами и обеспечить высокий уровень обслуживания. Приятного шопинга!""",

    "help": """Мы рады видеть тебя в нашем бот-магазине ювелирных изделий. Наша команда всегда готова помочь тебе с любыми вопросами или проблемами. Ниже представлен FAQ с частыми вопросами. Если ответа на твой вопрос там нет, пожалуйста, используй кнопку \"Задать вопрос менеджеру\" и затем отправь свой вопрос как обычное сообщение. Менеджер магазина ответит тебе в лс как можно скорее.""",

    "subscribe": """Хочешь быть в курсе всех изменений и новостей в нашем магазине ювелирных изделий? Подпишись на нашу уведомительную рассылку! Мы будем регулярно информировать тебя о новых поступлениях, специальных акциях, скидках и других интересных предложениях. Ты не пропустишь ни одного шикарного украшения или возможности сэкономить. Просто отправь нам сообщение с текстом "Подписка" или "Хочу получать уведомления", и мы добавим тебя в список рассылки. Благодарим за твою поддержку и интерес к нашим изделиям!""",

    "payment": "There will be available payment methods",

    "contacts": "There will be vendor's contact details",

    # "/support": "QA for frequently asked questions by the same or a different bot helper"

}

categories_uuid: dict = {
    '55b9124f-7a1b-4d76-a729-98fc53010545': 1,
    '4e1d1603-6d45-4587-aea8-81b295fe6499': 2,
    'c1bd5c53-887e-4d0d-af5f-f9142a2f341a': 3
}

product_columns_mapper: dict = {
    'product_name': 'Наименование',
    'category_name': 'Категория',
    'price': 'Цена',
    'description': 'Описание',
}
