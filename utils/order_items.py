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
