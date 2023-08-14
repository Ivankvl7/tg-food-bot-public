import os

import redis
from sqlalchemy import create_engine, Engine, MetaData, Connection
from sqlalchemy.orm import Session

from config_data.config import load_redis_config


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
    __config = None
    __env_path = os.path.dirname(os.getcwd()) + '/.env'

    def __new__(cls, *args, **kwargs):
        if cls.__config is None:
            cls.__config = load_redis_config(cls.__env_path)
        return super().__new__(cls)

    def get_cache(self):
        return redis.Redis(host=self.__class__.__config.host,
                           port=self.__class__.__config.port,
                           username=self.__class__.__config.user,
                           password=self.__class__.__config.password,
                           decode_responses=True)

