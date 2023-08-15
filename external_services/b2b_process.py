import boto3
from boto3.resources.factory import ServiceResource
from botocore.config import Config
from database.database import CONFIG, PATH
from b2sdk.v2 import B2Api
import requests
from requests import Response


class B2BInstance:

    @classmethod
    def get_b2b_resource(cls):
        return boto3.resource(
            service_name=CONFIG.b2b.service_name,
            endpoint_url=CONFIG.b2b.endpoint,
            aws_access_key_id=CONFIG.b2b.aws_access_key_id,
            aws_secret_access_key=CONFIG.b2b.aws_secret_access_key,
            config=Config(
                signature_version='s3v4'))

    @classmethod
    def get_b2b_client(cls):
        return boto3.client(
            service_name=CONFIG.b2b.service_name,
            endpoint_url=CONFIG.b2b.endpoint,
            aws_access_key_id=CONFIG.b2b.aws_access_key_id,
            aws_secret_access_key=CONFIG.b2b.aws_secret_access_key,
            config=CONFIG.b2b.config)

    @classmethod
    def get_media_content(cls, url: str) -> str:
        pass

    @classmethod
    def create_destination_path(cls, product_id: int) -> str:
        pass

    @classmethod
    def upload_file(cls, destination: str, file: str):
        pass


class B2BInstance:

    def __init__(self) -> None:
        self.b2_api: B2Api = B2Api()

    def authorize_account(self) -> None:
        self.b2_api.authorize_account('production',
                                      CONFIG.b2b.aws_access_key_id,
                                      CONFIG.b2b.aws_secret_access_key)

    def get_media_content(self, url: str) -> bytes:
        response: Response = requests.get(url)
        if response.status_code == 200:
            return response.content
        else:
            raise ConnectionError('Не удалось установить соединение. Попробуйте другую ссылку')

    def create_destination_path(self, product_id: int, media_type: str = 'photos') -> str:
        return f"{media_type}"


    def upload_file(self, destination: str, file: str):
        pass
