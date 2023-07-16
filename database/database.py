from sqlalchemy import create_engine, Engine, MetaData, Connection
from sqlalchemy.orm import Session
import redis


class DBInstance:
    __engine: Engine = None

    @classmethod
    def check_engine(cls) -> None:
        if not cls.__engine:
            cls.__engine = create_engine(
                "postgresql+psycopg2://postgres:V5a3n9o3l1o7x777$%^&*@localhost/JewelryShopBotDB")

    @classmethod
    def get_connection(cls) -> Connection:
        cls.check_engine()
        return cls.__engine.connect()

    @classmethod
    def get_session(cls) -> Session:
        cls.check_engine()
        return Session(bind=cls.__engine)

    @classmethod
    def get_metadata(cls) -> MetaData:
        cls.check_engine()
        metadata = MetaData()
        metadata.reflect(bind=cls.__engine)
        return metadata


class RedisCache:
    __cache = None
    __instance = None

    def __new__(cls, *args, **kwargs):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
        if cls.__instance is None:
            cls.__cache = redis.Redis(host='localhost', port=6379, db=0)
        return cls.__instance

    @classmethod
    def get_cache(cls):
        return cls.__cache


