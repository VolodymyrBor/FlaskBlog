import os
import time

from keras import backend
from imageio import imsave
from keras.applications import VGG19
from scipy.optimize import fmin_l_bfgs_b

from .evaluator import Evaluator
from .process_image import ProcessImage
from .defenitions import IMG_HEIGHT, IMG_WIDTH


class StyleTransfer:

    def __init__(self, target_image_path: str, style_reference_image_path: str, save_path: str,
                 iterations: int = 10, prefix: str = 'image'):

        self.target_image = backend.constant(ProcessImage.preprocess_image(target_image_path))
        self.style_reference_image = backend.constant(ProcessImage.preprocess_image(style_reference_image_path))
        self.combination_image = backend.placeholder((1, IMG_HEIGHT, IMG_WIDTH, 3))
        self.iterations = iterations
        self.prefix = prefix
        self.save_path = save_path

        self.x = ProcessImage.preprocess_image(target_image_path).flatten()

    def transfer(self):
        print('Start transfer.')

        input_tensor = backend.concatenate([
            self.target_image,
            self.style_reference_image,
            self.combination_image
        ], axis=0)

        model = VGG19(input_tensor=input_tensor, weights='imagenet', include_top=False)

        evaluator = Evaluator(model, self.combination_image)

        for i in range(self.iterations):
            start_time = time.time()
            self.x, min_val, info = fmin_l_bfgs_b(evaluator.loss, self.x, fprime=evaluator.grads, maxfun=self.iterations)

            print(f'Current loss value: {min_val}.')

            img = self.x.copy().reshape((IMG_HEIGHT, IMG_WIDTH, 3))
            img = ProcessImage.deprocess_image(img)
            fpath = os.path.join(self.save_path, self.prefix + f'_at_iteration_{i}.png')
            imsave(fpath, img)
            print(f'Image saved as {fpath}.')
            end_time = time.time()
            print(f'Iteration {i} completed in {end_time - start_time}.')
