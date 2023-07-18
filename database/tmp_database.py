from models.models import CartItem
from aiogram.fsm.state import State

cart: dict[str | int, list] = {}
