from dataclasses import dataclass, field


@dataclass
class CartItem:
    id: str | int
    name: str
    price: str | int
    description: str
    image_url: str
    quantity: int = field(default=1)
