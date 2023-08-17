from .models import StaticContentType
from lexicon.LEXICON import static_extension
import os


class StaticNameSchema:

    def __init__(self,
                 media_type: StaticContentType = StaticContentType.IMAGE):
        self.media_type = media_type

    def get_file_name(self,
                      product_id: int,
                      file_id: int = 1
                      ) -> str:
        file_name = f"{self.media_type.value}{product_id}_{file_id}{static_extension[self.media_type]}"
        print(f"file_name = {file_name}")
        return file_name

    def get_static_path(self) -> str:
        static_path = os.path.join(os.getcwd(), 'static', self.media_type.value)
        print(f"static_path = {static_path}")
        return static_path

    def get_folder_path(self,
                        product_id: int) -> str:
        folder_path = os.path.join(self.get_static_path(), str(product_id))
        print(f"get_folder_path = {folder_path}")
        return folder_path

    def get_full_path(self,
                      product_id: int,
                      file_id: int = 1) -> str:
        full_path = os.path.join(self.get_folder_path(product_id=product_id), self.get_file_name(product_id=product_id,
                                                                                                 file_id=file_id))
        print(f"full_path = {full_path}")
        return full_path

    def get_default_path(self, media_type: StaticContentType) -> str:
        default_path = os.path.join(self.get_static_path(), f'default{static_extension[media_type]}')
        print(f"default_path = {default_path}")
        return default_path
