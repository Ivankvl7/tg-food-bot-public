import requests
import os
from requests import Response
from models.models import TmpNames, StaticContentType
from lexicon.LEXICON import static_extension
from models.static_name_schema import StaticNameSchema


def populate_media(product_id: int, link: str = None, media_type: StaticContentType = StaticContentType.IMAGE):
    """Saves static files from url to a corresponding directory which depends on file type"""

    path_schema = StaticNameSchema(media_type=media_type)
    static_path: str = path_schema.get_static_path()
    extension: str = static_extension[media_type]
    files = os.listdir(static_path)
    folder_name = str(product_id)
    if folder_name not in files:
        os.mkdir(os.path.join(os.path.join(os.getcwd(), 'static', 'image'), folder_name))
        os.mkdir(os.path.join(os.path.join(os.getcwd(), 'static', 'video'), folder_name))

    final_path: str = path_schema.get_folder_path(product_id=product_id)
    postfix: int = len(os.listdir(final_path)) + 1
    try:
        if not link:
            raise ConnectionError
        response: Response = requests.get(url=link)
        if response.status_code:
            with open(path_schema.get_full_path(product_id=product_id,
                                                file_id=postfix), 'wb') as file:
                file.write(response.content)
    except BaseException as err:
        with open(os.path.join(static_path, f'default{extension}'), 'rb') as default:
            with open(os.path.join(final_path, f"image{product_id}_{postfix}{extension}"), 'wb') as file:
                file.write(default.read())


def check_media_existance(folder_id: str, media_type: StaticContentType = StaticContentType.IMAGE):
    path: str = os.path.join(os.getcwd(), 'static', media_type.value)
    folder_path: str = os.path.join(path, str(folder_id))
    if not os.path.exists(folder_path):
        return False
    if not os.listdir(folder_path):
        return False
    return True


def populate_b2b_media(file_to_write: str,
                       media_type: StaticContentType = StaticContentType.IMAGE):
    with open(file_to_write, 'wb') as destination:
        with open(TmpNames[media_type.name].value, 'rb') as source:
            destination.write(source.read())
