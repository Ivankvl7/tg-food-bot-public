from models.models import CartItem
from aiogram.fsm.state import State








goods = {
    'category1': [
        {
            "id": 1,
            "name": "Product 1",
            "price": '1.0 $',
            "description": "Description for Product 1",
            "image_url": "https://example.com/product1.jpg"
        },
        {
            "id": 2,
            "name": "Product 2",
            "price": '1.0 $',
            "description": "Description for Product 2",
            "image_url": "https://example.com/product2.jpg"
        },
        {
            "id": 3,
            "name": "Product 3",
            "price": '1.0 $',
            "description": "Description for Product 3",
            "image_url": "https://example.com/product3.jpg"
        },
        {
            "id": 4,
            "name": "Product 4",
            "price": '1.0 $',
            "description": "Description for Product 4",
            "image_url": "https://example.com/product4.jpg"
        },
        {
            "id": 5,
            "name": "Product 5",
            "price": '1.0 $',
            "description": "Description for Product 5",
            "image_url": "https://example.com/product5.jpg"
        },
        {
            "id": 6,
            "name": "Product 6",
            "price": '1.0 $',
            "description": "Description for Product 6",
            "image_url": "https://example.com/product6.jpg"
        },
        {
            "id": 7,
            "name": "Product 7",
            "price": '1.0 $',
            "description": "Description for Product 7",
            "image_url": "https://example.com/product7.jpg"
        },
        {
            "id": 8,
            "name": "Product 8",
            "price": '1.0 $',
            "description": "Description for Product 8",
            "image_url": "https://example.com/product8.jpg"
        },
        {
            "id": 9,
            "name": "Product 9",
            "price": '1.0 $',
            "description": "Description for Product 9",
            "image_url": "https://example.com/product9.jpg"
        },
        {
            "id": 10,
            "name": "Product 10",
            "price": '1.0 $',
            "description": "Description for Product 10",
            "image_url": "https://example.com/product10.jpg"
        },
        {
            "id": 11,
            "name": "Product 11",
            "price": '1.0 $',
            "description": "Description for Product 11",
            "image_url": "https://example.com/product11.jpg"
        },
        {
            "id": 12,
            "name": "Product 12",
            "price": '1.0 $',
            "description": "Description for Product 12",
            "image_url": "https://example.com/product12.jpg"
        },
        {
            "id": 13,
            "name": "Product 13",
            "price": '1.0 $',
            "description": "Description for Product 13",
            "image_url": "https://example.com/product13.jpg"
        },
        {
            "id": 14,
            "name": "Product 14",
            "price": '1.0 $',
            "description": "Description for Product 14",
            "image_url": "https://example.com/product14.jpg"
        },
        {
            "id": 15,
            "name": "Product 15",
            "price": '1.0 $',
            "description": "Description for Product 15",
            "image_url": "https://example.com/product15.jpg"
        }
    ],
    'category2': [
        {
            "id": 16,
            "name": "Product 16",
            "price": '1.0 $',
            "description": "Description for Product 16",
            "image_url": "https://example.com/product14.jpg"
        },
        {
            "id": 17,
            "name": "Product 17",
            "price": '1.0 $',
            "description": "Description for Product 17",
            "image_url": "https://example.com/product15.jpg"
        }
    ]
}

image_1 = 'https://eavf3cou74b.exactdn.com/wp-content/uploads/2021/09/21104001/How-to-Photograph-Jewelry-10-768x512.jpg?strip=all&lossy=1&ssl=1'


def get_products(category: str) -> list:
    pass


user_status: dict[str | int, dict[str, str | int]] = {

}

orders: dict[str, list[str]] = {}

cart: dict[str | int, list[CartItem]] = {
    593908084: [CartItem(*goods['category1'][0].values()), CartItem(*goods['category1'][1].values())]}

states_stack: dict[str | int, list[State]] = dict()