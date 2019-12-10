from typing import Optional
from os.path import join, abspath, dirname, exists
from os import mkdir, listdir, remove


ROOT_DIR = dirname(abspath(__file__))

IMAGES_PATH = join(ROOT_DIR, 'static', 'images')


class ImagesPath:

    def __init__(self, username: str):
        self.username = username
        self.username_path = join(IMAGES_PATH, username)

        self._create_dir(self.username_path)

    @staticmethod
    def _create_dir(path: str):
        if not exists(path):
            mkdir(path)

    def save_image_path(self, filename: Optional[str] = None) -> str:
        save_path = join(self.username_path, 'saves')
        self._create_dir(save_path)
        return join(save_path, filename) if filename else save_path

    def buffer_image_path(self, filename: Optional[str] = None) -> str:
        buffer_path = join(self.username_path, 'buffer')
        self._create_dir(buffer_path)
        return join(buffer_path, filename) if filename else buffer_path

    def delete_buffer(self):
        buffer_path = self.buffer_image_path()
        for filename in listdir(buffer_path):
            filepath = join(buffer_path, filename)
            remove(filepath)

    def model_buffer(self, filename: Optional[str] = None) -> str:
        buffer_path = join(self.username_path, 'model')
        self._create_dir(buffer_path)
        return join(buffer_path, filename) if filename else buffer_path
