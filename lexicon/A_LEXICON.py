from models.models import StaticContentType

field_tips: dict[str, str] = {
    'product_name': '<Наименование продукта> (до 50 симв.)',
    'price': '<Цена> (Число)',
    'description': '<Описание> (до 255 симв.)',
    'category_id': '<Номер категории>',
    StaticContentType.IMAGE.value: 'Ссылка на фото, как минимум 1 ссылка обязательна',
    StaticContentType.VIDEO.value: 'Ссылка на видео, необязательно'

}

fields_example: dict[str, str] = {
    'product_name': 'Nike AirForce 1',
    'price': '10999',
    'description': "Лучшие в мире кроссовки",
    "category_id": 1,
    'photo': 'https:pic1.jpg',
    'video': 'https:video2.jpg'
}

order_status_mapper: dict[str, str] = {
    'order_status_id': 'ID статуса',
    'order_status_name': 'Расшифровка'
}