from aiogram.filters import BaseFilter
from database.database import goods
from lexicon.LEXICON import pagination_buttons
from aiogram.types import CallbackQuery
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from states.states import FSMBrowsingState


# instead of goods import categories table from db will be used
class CatalogFilterCallbacks(BaseFilter):

    def __init__(self, states_obj, pag=None, cats=None):
        if pag is None:
            pag = pagination_buttons
        if cats is None:
            cats = goods
        states = list(state for state in states_obj.__all_states__ if
                          state not in (states_obj.browsing_categories,
                                        states_obj.browsing_goods))

        text1 = list(key for key in pag)
        text2 = list(category for category in cats)
        text1.extend(text2)
        text1.append('catalog')
        self.callback_data = text1
        self.states = states

    async def __call__(self, callback: CallbackQuery, state: FSMContext):
        return callback.data in self.callback_data and await state.get_state() in self.states


# obj1 = CatalogFilterCallbacks(FSMBrowsingState, pag=pagination_buttons, cats=goods)
# print(obj1.__dict__)