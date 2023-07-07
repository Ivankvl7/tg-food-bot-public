from aiogram.fsm.state import State, StatesGroup


# below class represents possible states while interacting with the bot
class FSMUserShopStates(StatesGroup):
    main_menu_state = State()
    catalog_state = State()
    category_state = State()
    browsing_goods_state = State()
    goods_added_to_cart_state = State()
    in_cart_state = State()
    browsing_orders_state = State()

    @classmethod
    def get_previous_state(cls):
        #здесь будет логика по которой предыдущие состояние будет забираться из редиса
        # при этом либо по прошествии 10-15 минут без активных апдейтов либо в соответствии с другой логикой
        # лог состояние с заданным пользователем будет очищаться
        pass
