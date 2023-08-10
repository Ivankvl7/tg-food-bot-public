field_tips: dict = {
    'product_name': '<Наименование продукта> (до 50 симв.)',
    'price': '<Цена> (Число)',
    'description': '<Описание> (до 255 симв.)',
    'category_id': '<Номер категории>',
    'article': '<Артикул товара>',
    'detailed_description': 'Детализированное описание (по желанию)'
}

fields_example: dict = {
    'product_name': 'Nike AirForce 1',
    'price': '10999',
    'descriptiom': "Лучшие в мире кроссовки",
    "category_id": 1,
    "article": 12345678
}

order_status_mapper: dict[str, str] = {
    'order_status_id': 'ID статуса',
    'order_status_name': 'Расшифровка'
}