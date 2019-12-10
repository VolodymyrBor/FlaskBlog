import numpy as np
from numpy import ndarray
from keras import backend
from keras import Model

from .loss import Loss
from .defenitions import IMG_HEIGHT, IMG_WIDTH


class Evaluator:

    def __init__(self, model: 'Model', combination_image):
        self.model = model
        self.loss_value = None
        self.grads_values = None
        self.combination_image = combination_image

    def __new__(cls,  model: 'Model', combination_image):

        loss = Loss(model).total_loss(combination_image)
        grads = backend.gradients(loss, combination_image)[0]
        cls.fetch_loss_and_grands = backend.function([combination_image], [loss, grads])
        instance = super().__new__(cls)
        return instance

    def loss(self, x: 'ndarray'):
        assert self.loss_value is None
        x = x.reshape((1, IMG_HEIGHT, IMG_WIDTH, 3))
        outs = self.fetch_loss_and_grands([x])
        loss_value = outs[0]
        grad_value = outs[1].flatten().astype('float64')
        self.loss_value = loss_value
        self.grads_values = grad_value
        return self.loss_value

    def grads(self, x: 'ndarray'):
        assert self.loss_value is not None
        grad_values = np.copy(self.grads_values)
        self.loss_value = None
        self.grads_values = None
        return grad_values
