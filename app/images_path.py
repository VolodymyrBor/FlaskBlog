from typing import Optional, List
from os.path import join, exists
from os import mkdir, listdir, remove
from shutil import copyfile
from uuid import uuid4


class ImagesPath:
    # STATIC_PATH = current_app.static_folder
    # IMAGES_PATH = join(STATIC_PATH, 'images')
    static_path = 'static'

    def __init__(self, username: str, static_path: str):
        self.username = username
        self.static_path = static_path

        self.image_path = 'images'
        self.username_path = join(self.image_path, username)

        self._create_dir(self.username_path)

    def _create_dir(self, path: str):
        path = join(self.static_path, path)
        if not exists(path):
            mkdir(path)

    def save_image_path(self, filename: Optional[str] = None, absolute: bool = False) -> str:
        save_path = join(self.username_path, 'saves')
        self._create_dir(save_path)
        res = join(save_path, filename) if filename else save_path
        return self.abs_path(res) if absolute else res

    def buffer_image_path(self, filename: Optional[str] = None, absolute: bool = False) -> str:
        buffer_path = join(self.username_path, 'buffer')
        self._create_dir(buffer_path)
        res = join(buffer_path, filename) if filename else buffer_path
        return self.abs_path(res) if absolute else res

    def delete_buffer(self):
        buffer_path = self.buffer_image_path(absolute=True)
        for filename in listdir(buffer_path):
            filepath = join(buffer_path, filename)
            remove(filepath)

    def model_buffer(self, filename: Optional[str] = None, absolute: bool = False) -> str:
        buffer_path = join(self.username_path, 'model')
        self._create_dir(buffer_path)
        res = join(buffer_path, filename) if filename else buffer_path
        return self.abs_path(res) if absolute else res

    def last_result_file_name(self):
        model_buffer = self.model_buffer()
        last_file_name = listdir(join(self.static_path, model_buffer))[-1]
        return last_file_name

    def last_file_path(self, absolute: bool = False) -> str:
        res = join(self.model_buffer(), self.last_result_file_name())
        return self.abs_path(res) if absolute else res

    def abs_path(self, path: str) -> str:
        return join(self.static_path, path)

    @staticmethod
    def convert(path: str):
        return path.replace('\\', '/')

    def get_save_images_name(self) -> List[str]:
        save_images_path = self.save_image_path(absolute=True)
        return listdir(save_images_path)
