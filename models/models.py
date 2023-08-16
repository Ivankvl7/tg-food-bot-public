from dataclasses import dataclass, field
from enum import Enum


class PriceRepresentation:
    def __init__(self, num: int | float, unit: str) -> None:
        self.num: float | int = num
        self.unit: str = unit

    def __repr__(self) -> str:
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
    DESKTOP: str = 'Desktop'
    MOBILE_DEVICE: str = 'Mobile'


class CategoryActions(Enum):
    DELETE: str = 'delete'
    ADD: str = 'add'


class AdminStaticKb(Enum):
    CATEGORY_BUTTON: str = 'Изменить категории'
    PRODUCT_BUTTON: str = 'Изменить данные о продукте'
    ORDER_BUTTON: str = 'Изменить статус заказа'


class StaticContentType(Enum):
    IMAGE: str = 'image'
    VIDEO: str = 'video'

