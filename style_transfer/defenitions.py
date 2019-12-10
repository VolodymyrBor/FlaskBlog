from os.path import join, abspath, dirname

from keras_preprocessing.image import load_img

ROOT_DIR = dirname(abspath(__file__))
IMG_PATH = join(ROOT_DIR, 'img')
TARGET_IMAGE_PATH = join(IMG_PATH, 'vlud.jpg')
STYLE_REFERENCE_IMAGE_PATH = join(IMG_PATH, 'red.jpg')


WIDTH, HEIGHT = load_img(TARGET_IMAGE_PATH).size
IMG_HEIGHT = 400
IMG_WIDTH = int(WIDTH * IMG_HEIGHT / HEIGHT)

PERSON_PATH = join(ROOT_DIR, 'vlud')
SAVE_PATH = join(PERSON_PATH, 'red')
RESULT_PREFIX = 'my_result'
ITERATION = 20
