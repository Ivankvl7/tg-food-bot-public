from database.database import DBInstance


def add_new_category(category_name: str) -> None:
    pass


def delete_category(category_uuid: str) -> None:
    pass


def add_new_product(product_name: str,
                    product_description: str,
                    product_price: str,
                    front_photo: str,
                    additional_photos: list[str] = None,
                    additional_videos: list[str] = None) -> None:
    pass


def change_product_name(new_name: str) -> None:
    pass


def change_product_description(new_description: str) -> None:
    pass


def change_product_price(new_price: int) -> None:
    pass


def change_order_status(new_status: str) -> None:
    pass


def delete_product(product_uuid: str) -> None:
    pass


def add_photo_link(link: str) -> None:
    pass


def add_video_link(link: str) -> None:
    pass
