from dataclasses import dataclass, field
from datetime import datetime


class PriceRepresentation(float):
    def __new__(cls, num, unit, *args, **kwargs):
        instance = super().__new__(cls)
        instance.unit = unit
        instance.num = num
        return instance

    def __init__(self, num, unit):
        super().__init__()
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
    order_id: int
    order_date: str
    product_name: str
    quantity: int
    price: PriceRepresentation
    order_status: str
