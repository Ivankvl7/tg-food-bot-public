from database.database import DBInstance
from sqlalchemy import Table, select, Select, MetaData, Result, Row, func
from sqlalchemy.orm import Session, Query
from typing import Sequence
from lexicon.LEXICON import product_columns_mapper
from sqlalchemy.sql.expression import Subquery


def select_categories() -> Sequence:
    with DBInstance.get_session() as session:
        metadata: MetaData = DBInstance.get_metadata()
        categories: Table = Table('categories', metadata)
        select_query: Select = select(categories)
        data: Result = session.execute(select_query)
        return data.all()


def select_product(category_uuid: int | str | None = None, product_id: int | str = 1) -> Row:
    with DBInstance.get_session() as session:
        metadata: MetaData = DBInstance.get_metadata()
        products = Table('products', metadata)
        categories: Table = Table('categories', metadata)
        if category_uuid:
            query: Select = select(
                products.c.name.label('product_name'),
                categories.c.name.label('category_name'),
                products.c.price,
                products.c.description,
                products.c.image_url,
                products.c.uuid).join_from(products, categories).where(
                categories.c.uuid == category_uuid)
        if isinstance(product_id, str):
            query: Select = select(
                products.c.name.label('product_name'),
                categories.c.name.label('category_name'),
                products.c.price,
                products.c.description,
                products.c.image_url,
                products.c.uuid).join_from(products, categories).where(
                products.c.uuid == product_id)
            selected_data: Result = session.execute(query)
            return selected_data.one()
        selected_data: Result = session.execute(query)
        return selected_data.all()[product_id - 1]


def select_max_product_id(category_uuid: str | int):
    with DBInstance.get_session() as session:
        metadata: MetaData = DBInstance.get_metadata()
        products: Table = Table('products', metadata)
        categories: Table = Table('categories', metadata)
        query: Select = select(func.count("*")).join_from(products, categories).where(
            categories.c.uuid == category_uuid)
        data: Result = session.execute(query)
    return data.scalar()


product = select_product(product_id='818dafc2-3830-4152-b286-c4481557d6f9',
                         category_uuid='55b9124f-7a1b-4d76-a729-98fc53010545')

class