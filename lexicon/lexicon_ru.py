basic_menu: dict = {
    "start": """ Вернуться на главную страницу""",

    "help": """Подсказки по взаимодействию с ботом""",

    "subscribe": """Подписка на обновления магазина""",

    "payment": "Методы оплаты",

    "contacts": "Контактные данные",

    # "/support": "QA for frequently asked questions by the same or a different bot helper"

}

command_handlers: dict = {
    "start": """Добро пожаловать в наш бот-магазин ювелирных изделий! У нас вы найдете широкий ассортимент уникальных и красивых украшений для всех случаев жизни. От классических колец и ожерелий до модных браслетов и серег, наш бот предлагает изысканные изделия из самых качественных материалов. Будьте в тренде и выразите свою индивидуальность с нашими эксклюзивными украшениями. Просто просмотрите наш каталог, выберите свои любимые украшения и оформите заказ прямо в боте. Наша команда готова помочь вам с любыми вопросами и обеспечить высокий уровень обслуживания. Приятного шопинга!""",

    "help": """Мы рады видеть тебя в нашем бот-магазине ювелирных изделий. Наша команда всегда готова помочь тебе с любыми вопросами или проблемами. Если у тебя возникли затруднения с выбором украшений, мы можем предложить тебе персональные рекомендации, учитывая твои предпочтения и бюджет. Если у тебя есть вопросы о нашей политике возврата, доставке или оплате, мы с удовольствием предоставим тебе все необходимые сведения. Просто напиши нам свой вопрос, и мы ответим как можно скорее. Ты можешь положиться на нашу команду, чтобы сделать твою покупку удобной и приятной.""",

    "subscribe": """Хочешь быть в курсе всех изменений и новостей в нашем магазине ювелирных изделий? Подпишись на нашу уведомительную рассылку! Мы будем регулярно информировать тебя о новых поступлениях, специальных акциях, скидках и других интересных предложениях. Ты не пропустишь ни одного шикарного украшения или возможности сэкономить. Просто отправь нам сообщение с текстом "Подписка" или "Хочу получать уведомления", и мы добавим тебя в список рассылки. Благодарим за твою поддержку и интерес к нашим изделиям!""",

    "payment": "There will be available payment methods",

    "contacts": "There will be vendor's contact details",

    # "/support": "QA for frequently asked questions by the same or a different bot helper"

}

start_follow_up_menu: dict = {
    "start": ["Каталог 📕", "Начните ознакамливаться с каталогом товаров "]

}

static_keyboard: dict = {
    'clients_account': 'Личный кабинет 📖',
    'cart': 'Корзина 🛒',
    'balance_info': 'Баланс 💳',
    'help': 'Помощь 🆘'
}

