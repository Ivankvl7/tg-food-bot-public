import random
from datetime import datetime
from typing import Sequence, Any
from sqlalchemy import Table, select, Select, MetaData, Result, Row, func, Insert, insert, Update, update, join
from sqlalchemy.orm import Session
from sqlalchemy.sql.expression import Subquery, CTE
from database.database import DBInstance
from models.models import CartItem, PriceRepresentation


def categories_products_cte() -> CTE:
    with DBInstance.get_session():
        metadata: MetaData = DBInstance.get_metadata()
        categories = Table('categories', metadata)
        products: Table = Table('products', metadata)
        cte: CTE = select(products, categories).join_from(products, categories).cte()
    return cte


def get_categories() -> Sequence:
    with DBInstance.get_session() as session:
        metadata: MetaData = DBInstance.get_metadata()
        categories: Table = Table('categories', metadata)
        select_query: Select = select(categories)
        data: Result = session.execute(select_query)
    return data.all()


def get_product(product_uuid: str | int) -> Row:
    with DBInstance.get_session() as session:
        cte: CTE = categories_products_cte()
        query: Select = select(cte).where(cte.c.product_uuid == product_uuid)
        data: Result = session.execute(query)
    return data.one()


def get_first_product(category_uuid: int | str) -> Row:
    with DBInstance.get_session() as session:
        metadata: MetaData = DBInstance.get_metadata()
        categories: Table = Table('categories', metadata)
        products: Table = Table('products', metadata)
        query: Subquery = select(
            products.c.product_id,
            products.c.product_name,
            categories.c.category_name,
            products.c.price,
            products.c.description,
            products.c.product_uuid).join_from(products, categories).where(
            categories.c.category_uuid == category_uuid).subquery()
        min_id: int = session.execute(func.min(query.c.product_id)).scalar()
        res: Row = session.execute(select(query).where(query.c.product_id == min_id)).first()
    return res


def get_max_product_id(category_uuid: str | int) -> int | str:
    with DBInstance.get_session() as session:
        cte: CTE = categories_products_cte()
        query: Select = select(func.count("*")).select_from(cte).where(
            cte.c.category_uuid == category_uuid)
        data: Result = session.execute(query)
    return data.scalar()


def get_max_product_id_by_cat_id(category_id: int) -> int | str:
    with DBInstance.get_session() as session:
        cte: CTE = categories_products_cte()
        query: Select = select(func.count("*")).select_from(cte).where(
            cte.c.category_id == category_id)
        data: Result = session.execute(query)
    return data.scalar()


def get_category_uuid_by_product_uuid(product_uuid: str | int = None) -> str | int:
    with DBInstance.get_session() as session:
        cte: CTE = categories_products_cte()
        query: Select = select(cte.c.category_uuid).where(cte.c.product_uuid == product_uuid)
        data: Result = session.execute(query)
    return data.scalar()


def products_filtered_by_category_and_numbered(product_uuid: str | int) -> CTE:
    cte: CTE = categories_products_cte()
    cte_new: CTE = select(func.row_number().over(order_by=cte.c.product_id).label('num_id'),
                          cte).where(
        cte.c.category_uuid == get_category_uuid_by_product_uuid(product_uuid)).cte()

    return cte_new


def get_current_product_num_id(product_uuid: str | int) -> str | int:
    with DBInstance.get_session() as session:
        cte: CTE = products_filtered_by_category_and_numbered(product_uuid)
        query: Select = select(cte.c.num_id).where(cte.c.product_uuid == product_uuid)
        data: Result = session.execute(query)
    return data.scalar()


def get_next_product_uuid(current_product_uuid: str | int) -> str | int | None:
    with DBInstance.get_session() as session:
        if get_current_product_num_id(current_product_uuid) == get_max_product_id(
                get_category_uuid_by_product_uuid(current_product_uuid)):
            return 'not allowed'
        cte: CTE = products_filtered_by_category_and_numbered(current_product_uuid)
        query: Select = select(cte.c.product_uuid).where(
            cte.c.num_id == get_current_product_num_id(current_product_uuid) + 1)
        res: Result = session.execute(query)
    return res.scalar()


def get_previous_product_uuid(current_product_uuid: str | int) -> str | int | None:
    with DBInstance.get_session() as session:
        if get_current_product_num_id(current_product_uuid) == 1:
            return 'not allowed'
        cte: CTE = products_filtered_by_category_and_numbered(current_product_uuid)
        query: Select = select(cte.c.product_uuid).where(
            cte.c.num_id == get_current_product_num_id(current_product_uuid) - 1)
        res: Result = session.execute(query)
    return res.scalar()


def get_static_videos(product_uuid: int | str) -> list[str]:
    with DBInstance.get_session() as session:
        metadata: MetaData = DBInstance.get_metadata()
        products: Table = Table('products', metadata)
        static_media_videos: Table = Table('static_media_videos', metadata)
        query: Select = select(static_media_videos.c.video_url).join_from(products, static_media_videos).where(
            products.c.product_uuid == product_uuid)
        data: Result = session.execute(query)
    return [row.video_url for row in data]


def get_category(category_uuid: str | int):
    with DBInstance.get_session() as session:
        metadata: MetaData = DBInstance.get_metadata()
        categories: Table = Table('categories', metadata)
        query: Select = select(categories.c.category_name).where(categories.c.category_uuid == category_uuid)
        data: Result = session.execute(query)
    return data.scalar()


def select_last_or_first_in_category_or_none(product_uuid: str | int, which_one='first'):
    with DBInstance.get_session() as session:
        cte: CTE = products_filtered_by_category_and_numbered(product_uuid=product_uuid)
        query: Select = select(cte.c.num_id).where(cte.c.product_uuid == product_uuid)
        if which_one == 'first':
            num_id: int = int(session.execute(query).scalar()) - 1
        else:
            num_id: int = int(session.execute(query).scalar()) + 1
        query2: Select = select(cte.c.product_uuid).where(cte.c.num_id == num_id)
        res: Result = session.execute(query2)
    return res.one_or_none()


def get_user_orders(user_id: str | int, admin_mode=False):
    with DBInstance.get_session() as session:
        metadata: MetaData = DBInstance.get_metadata()
        orders: Table = Table('orders', metadata)
        users: Table = Table('users', metadata)
        products: Table = Table('products', metadata)
        order_status: Table = Table('order_status', metadata)
        query: Select = select('*').select_from(
            join(orders, products).join(users).join(order_status)).where(users.c.telegram_id == user_id,
                                                                         order_status.c.order_status_id < 4)
        if admin_mode:
            query: Select = select('*').select_from(
                join(orders, products).join(users).join(order_status)).where(order_status.c.order_status_id < 4)
        data: Sequence[Row[tuple | Any]] = session.execute(query).all()
    return data


def get_user_id_by_tg_id(user_tg_id: str | int):
    with DBInstance.get_session() as session:
        metadata: MetaData = DBInstance.get_metadata()
        users: Table = Table('users', metadata)
        user_id: int = session.execute(select(users.c.user_id).where(users.c.telegram_id == user_tg_id)).scalar()
    return user_id


def get_user_by_tg_id(user_tg_id: str | int):
    with DBInstance.get_session() as session:
        metadata: MetaData = DBInstance.get_metadata()
        users: Table = Table('users', metadata)
        user_data: Row = session.execute(select(users).where(users.c.telegram_id == user_tg_id)).one()
    return user_data


def get_order_number() -> int:
    with DBInstance.get_session() as session:
        metadata: MetaData = DBInstance.get_metadata()
        orders: Table = Table('orders', metadata)
        query: Select = select(func.max(orders.c.order_number))
        res: Row = session.execute(query).one_or_none()
    if not res[-1]:
        return 1
    return res[-1] + 1


def add_order_to_db(user_tg_id: int, user_cart: list[CartItem]):
    def get_product_id(session: Session, metadata: MetaData, product_uuid: str | int) -> int:
        with session as s:
            products: Table = Table('products', metadata)
            query: Select = select(products.c.product_id).where(products.c.product_uuid == product_uuid)
            return session.execute(query).scalar()

    with DBInstance.get_session() as session:
        metadata: MetaData = DBInstance.get_metadata()
        orders: Table = Table('orders', metadata)
        user_id: int = get_user_id_by_tg_id(user_tg_id=user_tg_id)
        for item in user_cart:
            query: Insert = insert(orders).values(
                user_id=user_id,
                product_id=get_product_id(session=session,
                                          metadata=metadata,
                                          product_uuid=item.product_uuid),
                order_start_date=datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'),
                quantity=item.quantity,
                order_status_id=1,
                order_number=item.order_number,

            )
            session.execute(query)
            session.commit()


def add_user_to_db(
        action: str,
        user_tg_id: int,
        username: str,
        first_name: str,
        last_name: str,
        phone: str,
        age: int,
        email: str,
        address: str,
        user_type_id: int = 3,
        registration_date=datetime.now().strftime('%d-%m-%y')):
    with DBInstance.get_session() as session:
        metadata: MetaData = DBInstance.get_metadata()
        users_table: Table = Table('users', metadata)
        if action == 'add':
            query: Insert = insert(users_table).values(telegram_id=user_tg_id,
                                                       username=username,
                                                       first_name=first_name,
                                                       last_name=last_name,
                                                       user_type_id=user_type_id,
                                                       phone=phone,
                                                       age=age,
                                                       email=email,
                                                       address=address,
                                                       registration_date=registration_date
                                                       )
        else:
            query: Update = update(users_table).values(telegram_id=user_tg_id,
                                                       username=username,
                                                       first_name=first_name,
                                                       last_name=last_name,
                                                       user_type_id=user_type_id,
                                                       phone=phone,
                                                       age=age,
                                                       email=email,
                                                       address=address,
                                                       registration_date=registration_date
                                                       ).where(users_table.c.telegram_id == user_tg_id)
        session.execute(query)
        session.commit()


def get_user_tg_ids_from_db():
    with DBInstance.get_session() as session:
        metadata: MetaData = DBInstance.get_metadata()
        users: Table = Table('users', metadata)
        users_tg_ids: list[int] = [item.telegram_id for item in session.execute(select(users.c.telegram_id)).all()]
    return users_tg_ids


def from_product_to_cart_item(order_number: int, product: Row, quantity=1) -> CartItem:
    return CartItem(
        product_name=product.product_name,
        category_name=get_category(get_category_uuid_by_product_uuid(product.product_uuid)),
        description=product.description,
        price=PriceRepresentation(product.price, 'руб.'),
        quantity=quantity,
        product_uuid=product.product_uuid,
        article=product.article,
        order_number=order_number)


def get_random_products(num: int) -> list[CartItem]:
    with DBInstance.get_session() as session:
        table: CTE = categories_products_cte()
        ids: Sequence[Row] = session.execute(select(table.c.product_uuid)).all()
        random_ids = [item.product_uuid for item in random.choices(ids, k=num)]
    return random_ids


def get_user_fields(user_tg_id: int):
    with DBInstance.get_session() as session:
        metadata: MetaData = DBInstance.get_metadata()
        users: Table = Table('users', metadata)
        query: Select = select(users).where(users.c.user_id == get_user_id_by_tg_id(user_tg_id))
        data: Result = session.execute(query)
    return data


def get_product_id_by_uuid(product_uuid: str) -> int:
    with DBInstance.get_session() as session:
        metadata: MetaData = DBInstance.get_metadata()
        products: Table = Table('products', metadata)
        query: Select = select(products.c.product_id).where(products.c.product_uuid == product_uuid)
        data: Result = session.execute(query)
    return data.scalar()
