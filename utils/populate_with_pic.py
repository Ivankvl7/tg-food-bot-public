def populate_media(product_id: int, link: str = None, type: str = 'photos'):
    """Saves static files from url to a corresponding directory which depends on file type"""

    import requests
    import os
    from requests import Response

    static_path: str = os.path.join(os.getcwd(), 'static', type)
    extension: str = ".jpg"
    if type == "videos":
        extension: str = ".mp4"
    files = os.listdir(static_path)
    folder_name = str(product_id)
    if folder_name not in files:
        os.mkdir(os.path.join(os.path.join(os.getcwd(), 'static', 'videos'), folder_name))
        os.mkdir(os.path.join(os.path.join(os.getcwd(), 'static', 'photos'), folder_name))

    final_path: str = os.path.join(static_path, folder_name)
    postfix: int = len(os.listdir(final_path)) + 1
    try:
        if not link:
            raise ConnectionError
        response: Response = requests.get(url=link)
        if response.status_code:
            with open(os.path.join(final_path, f"image{postfix}{extension}"), 'wb') as file:
                file.write(response.content)
    except BaseException as err:
        with open(os.path.join(static_path, f'default{extension}'), 'rb') as default:
            with open(os.path.join(final_path, f"image{postfix}{extension}"), 'wb') as file:
                file.write(default.read())


def check_media_existance(folder_id: str, media_type: str):
    import os

    path: str = os.path.join(os.getcwd(), 'static', media_type)
    folder_path: str = os.path.join(path, str(folder_id))
    if not os.path.exists(folder_path):
        return False
    if not os.listdir(folder_path):
        return False
    return True
