from aiogram.fsm.state import State
from utils.order_items import CartItem
from utils.order_items import PriceRepresentation
from utils.order_items import UserProfile

# cart: dict[str | int, list] = {593908084: [CartItem(product_name='Silver Necklace',
#                                                     category_name='Necklaces',
#                                                     description='Elegant silver necklace for any occasion.',
#                                                     price=PriceRepresentation(250, 'rubles'),
#                                                     quantity=1,
#                                                     product_uuid='832ecc97-1435-4b3d-954b-601a5de58f3a',
#                                                     article=8013834)]}

cart: dict[str | int, list] = dict()

favorite_products: dict[str | int, list] = {}

user_profiles: dict[str | int: UserProfile] = {}
