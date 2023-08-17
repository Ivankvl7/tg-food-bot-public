import os

from database.database import CONFIG
from b2sdk.v2 import B2Api
from b2sdk.transfer.inbound.downloaded_file import DownloadedFile
import requests
from requests import Response
from models.models import StaticContentType, TmpNames
from lexicon.LEXICON import static_extension


class B2BInstance:
    def __init__(self, bucket_name: str = CONFIG.b2b.bucket_name) -> None:
        self.b2_api: B2Api = B2Api()
        self.bucket_name = bucket_name
        self.authorize_account()
        self.bucket = self.get_bucket_api()

    def authorize_account(self) -> None:
        self.b2_api.authorize_account('production',
                                      CONFIG.b2b.aws_access_key_id,
                                      CONFIG.b2b.aws_secret_access_key)

    def get_bucket_api(self):
        return self.b2_api.get_bucket_by_name(self.bucket_name)

    @staticmethod
    def get_media_content(url: str) -> bytes:
        response: Response = requests.get(url)
        if response.status_code == 200:
            return response.content
        else:
            raise ConnectionError('Не удалось установить соединение. Попробуйте другую ссылку')

    def get_destination_path(self, product_id: int,
                             media_type: StaticContentType = StaticContentType.IMAGE) -> str:
        return f"{media_type.value}/{product_id}/"

    def upload_file(self,
                    url: str,
                    product_id: int,
                    file_id: int = None,
                    media_type: StaticContentType = StaticContentType.IMAGE) -> None:
        data_bytes = self.get_media_content(url)
        file_name = self.generate_media_name(product_id=product_id,
                                             media_type=media_type,
                                             file_id=file_id)
        uploaded_file = self.bucket.upload_bytes(data_bytes=data_bytes,
                                                 file_name=file_name)

    def get_static_data(self,
                        product_id: int,
                        media_type: StaticContentType = StaticContentType.IMAGE):
        return self.bucket.ls(self.get_destination_path(product_id=product_id,
                                                        media_type=media_type))

    def generate_media_name(self, product_id: int,
                            media_type: StaticContentType = StaticContentType.IMAGE,
                            file_id: int = None) -> str:

        if file_id:
            id_postfix = file_id
        else:
            file_list = self.get_static_data(product_id=product_id,
                                             media_type=media_type)
            id_postfix = len(list(file_list)) + 1
        file_path = self.get_destination_path(product_id=product_id,
                                              media_type=media_type)
        return f"{file_path}{media_type.value}{product_id}_{id_postfix}{static_extension[media_type]}"

    def download_media(self, product_id: int,
                       file_id: int,
                       media_type: StaticContentType = StaticContentType.IMAGE
                       ) -> DownloadedFile:
        file_name = self.generate_media_name(product_id=product_id,
                                             media_type=media_type,
                                             file_id=file_id)
        print(file_name)
        downloaded_file = self.bucket.download_file_by_name(file_name)
        return downloaded_file
