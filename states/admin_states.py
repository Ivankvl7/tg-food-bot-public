from aiogram.fsm.state import State, StatesGroup


class AdminStates(StatesGroup):
    admin_start: State = State()
