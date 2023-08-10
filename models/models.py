from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class PriceRepresentation:
    def __init__(self, num, unit):
        self.unit = unit
        self.num = num

    def __repr__(self):
        return f"{self.num} {self.unit}"


@dataclass
class CartItem:
    product_name: str
    category_name: str
    description: str = field(hash=False)
    price: PriceRepresentation = field(hash=False)
    quantity: int = field(hash=False)
    product_uuid: int | str
    article: int
    order_number: int


@dataclass
class UserProfile:
    first_name: str | None = field(default=None)
    last_name: str | None = field(default=None)
    address: str | None = field(default=None)
    age: int | None = field(default=None)
    phone: str | None = field(default=None)
    email: str | None = field(default=None)


# print(UserProfile().__dict__)

@dataclass
class ItemListedInUserOrders:
    order_number: int
    order_date: str
    product_name: str
    quantity: int
    price: PriceRepresentation
    order_status: str
    order_id: int = field

@dataclass
class ItemListedOrdersAdmin:
    order_id: int
    order_number: int
    order_date: str
    product_name: str
    quantity: int
    price: PriceRepresentation
    order_status: str

class SelectedDevice(Enum):
    DESKTOP = 'Desktop'
    MOBILE_DEVICE = 'Mobile'


class CategoryActions(Enum):
    DELETE = 'delete'
    ADD = 'add'


class AdminStaticKb(Enum):
    CATEGORY_BUTTON = 'Изменить категории'
    PRODUCT_BUTTON = 'Изменить данные о продукте'
    ORDER_BUTTON = 'Изменить статус заказа'


