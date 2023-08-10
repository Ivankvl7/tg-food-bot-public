import uuid
from database.database import DBInstance
from sqlalchemy import Table, select, Select, MetaData, Result, Row, func, Insert, insert, Update, update, join, Delete, \
    delete
from sqlalchemy.orm import Session, Query
from typing import Sequence, Any
from lexicon.LEXICON import product_columns_mapper
from sqlalchemy.sql.expression import Subquery, CTE
from models.models import CartItem, PriceRepresentation
from datetime import datetime
import random
from ..methods.rel_db_methods import get_max_product_id_by_cat_id


def get_max_product_id_glob() -> int:
    with DBInstance.get_session() as session:
        metadata: MetaData = DBInstance.get_metadata()
        table: Table = Table('products', metadata)
        query: Select = select(func.max(table.c.product_id))
        data: int = int(session.execute(query).scalar())
    return data


def get_existing_categories() -> list[(str, str)]:
    with DBInstance.get_session() as session:
        metadata: MetaData = DBInstance.get_metadata()
        table: Table = Table('categories', metadata)
        query: Select = select(table.c.category_id, table.c.category_name)
        data: list[(str, str)] = list(session.execute(query).all())
    return data


def get_max_cat_id() -> int:
    with DBInstance.get_session() as session:
        metadata: MetaData = DBInstance.get_metadata()
        table: Table = Table('categories', metadata)
        query: Select = select(func.max(table.c.category_id))
        max_id: int = int(session.execute(query).scalar())
    return max_id


def add_new_category(category_name: str) -> None:
    with DBInstance.get_session() as session:
        metadata: MetaData = DBInstance.get_metadata()
        table: Table = Table('categories', metadata)
        query: Insert = insert(table).values(
            category_id=get_max_cat_id() + 1,
            category_name=category_name,
            category_uuid=uuid.uuid4())
        session.execute(query)
        session.commit()
    return


def delete_category(category_id: int) -> None:
    with DBInstance.get_session() as session:
        metadata: MetaData = DBInstance.get_metadata()
        table: Table = Table('categories', metadata)
        query: Delete = delete(table).where(table.c.category_id == category_id)
        session.execute(query)
        session.commit()
    return


def add_new_product(
        product_id: int,
        product_name: str,
        price: str,
        description: str,
        category_id: int,
        article: int,
        detailed_description: str = None,
        front_photo: str = None,
        additional_photos: list[str] = None,
        additional_videos: list[str] = None) -> None:
    with DBInstance.get_session() as session:
        metadata: MetaData = DBInstance.get_metadata()
        table: Table = Table('products', metadata)
        query: Insert = insert(table).values(
            product_id=product_id,
            product_name=product_name,
            price=price,
            description=description,
            category_id=category_id,
            article=article,
            product_uuid=uuid.uuid4(),
            detailed_description=detailed_description
        )
        session.execute(query)
        session.commit()
    return


def alter_product_attr(product_uuid: str, attr_name: str, value: str | int) -> None:
    with DBInstance.get_session() as session:
        metadata: MetaData = DBInstance.get_metadata()
        table: Table = Table('products', metadata)
        stmt = update(table).where(table.c.product_uuid == product_uuid).values(
            {getattr(table.c, attr_name): value})
        session.execute(stmt)
        session.commit()


def change_order_status(order_id: int, new_status: int) -> None:
    with DBInstance.get_session() as session:
        metadata: MetaData = DBInstance.get_metadata()
        table: Table = Table('orders', metadata)
        query: Update = update(table).where(table.c.order_number == order_id).values(
            {table.c.order_status_id: new_status})
        session.execute(query)
        session.commit()


def delete_product(product_uuid: str) -> None:
    with DBInstance.get_session() as session:
        metadata: MetaData = DBInstance.get_metadata()
        table: Table = Table('products', metadata)
        stmt: Delete = delete(table).where(table.c.product_uuid == product_uuid)
        session.execute(stmt)
        session.commit()


def add_photo_link(link: str) -> None:
    pass


def add_video_link(link: str) -> None:
    pass


def get_order_status_table() -> list[Row]:
    with DBInstance.get_session() as session:
        metadata: MetaData = DBInstance.get_metadata()
        table: Table = Table('order_status', metadata)
        query: Select = select(table)
        res = list(session.execute(query).all())
    return res

