import os
from dataclasses import dataclass, field
from environs import Env
from botocore.config import Config

PATH = os.path.join(os.getcwd() + '.env')


@dataclass
class DatabaseConfig:
    database: str  # bd name
    db_host: str  # bd URL
    db_user: str  # bd username
    db_password: str  # bd pass
    local_engine: str
    remote_engine: str


@dataclass
class TgBot:
    token: str  # Bot token
    admin_ids: list[int]  # admin ids
    shop_managers: list[int]


@dataclass
class RedisConfig:
    host: str
    port: str | int
    user: str
    password: str


@dataclass
class B2BConfig:
    endpoint: str
    aws_access_key_id: str | int
    aws_secret_access_key: str | int
    service_name: str = field(default='s3')
    config: Config = field(default=Config(signature_version='s3v4'))


@dataclass
class Config:
    tg_bot: TgBot
    db: DatabaseConfig
    redis: RedisConfig
    b2b: B2BConfig


def load_config(path: str | None) -> Config:
    env: Env = Env()
    env.read_env(path)

    return Config(tg_bot=TgBot(token=env('BOT_TOKEN'),
                               admin_ids=list(map(int, env.list('ADMIN_IDS'))),
                               shop_managers=list(map(int, env.list('SHOP_MANAGERS')))),
                  db=DatabaseConfig(database=env('DATABASE'),
                                    db_host=env('DB_HOST'),
                                    db_user=env('DB_USER'),
                                    db_password=env('DB_PASSWORD'),
                                    local_engine=env('LOCAL_ENGINE'),
                                    remote_engine=env('REMOTE_ENGINE')
                                    ),
                  redis=RedisConfig(
                      host=env('redis_host'),
                      port=env('redis_port'),
                      user=env('redis_user'),
                      password=env('redis_pass')
                  ),
                  b2b=B2BConfig(
                      endpoint=env('ENDPOINT'),
                      aws_access_key_id=env('KEY_ID_B2B'),
                      aws_secret_access_key=env('APPLICATION_KEY_B2B')))
