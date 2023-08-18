import redis
from sqlalchemy import create_engine, Engine, MetaData, Connection
from sqlalchemy.orm import Session
from config_data.config import load_config, PATH

CONFIG = load_config(PATH)


class DBInstance:
    __engine: Engine = None

    @classmethod
    def check_engine(cls) -> None:
        if not cls.__engine:
            cls.__engine = create_engine(CONFIG.db.local_engine)

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

    @staticmethod
    def get_cache():
        return redis.Redis(host=CONFIG.redis.host,
                           port=CONFIG.redis.port,
                           username=CONFIG.redis.user,
                           password=CONFIG.redis.password,
                           decode_responses=True)
