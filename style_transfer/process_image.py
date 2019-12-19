import numpy as np
from numpy import ndarray
from keras_preprocessing.image import load_img, img_to_array
from keras.applications import vgg19


class ProcessImage:

    def __init__(self,  img_height: int, img_width: int):
        self.img_height = img_height
        self.img_width = img_width

    def preprocess_image(self, image_path: str) -> ndarray:
        img = load_img(image_path, target_size=(self.img_height, self.img_width))
        img = img_to_array(img)
        img = np.expand_dims(img, axis=0)
        img = vgg19.preprocess_input(img)
        return img

    @staticmethod
    def deprocess_image(img: ndarray) -> ndarray:
        img[:, :, 0] += 103.939
        img[:, :, 1] += 116.779
        img[:, :, 2] += 123.68
        img = img[:, :, ::-1]
        img = np.clip(img, 0, 255).astype('uint8')
        return img
