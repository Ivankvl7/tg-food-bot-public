from aiogram.fsm.state import State, StatesGroup


# below class represents possible states while interacting with the bot
class FSMOrderConfirmation(StatesGroup):
    confirmation_started: State = State()
    input_name: State = State()
    input_address: State = State()
    input_phone: State = State()
    input_age: State = State()
    input_email: State = State()

