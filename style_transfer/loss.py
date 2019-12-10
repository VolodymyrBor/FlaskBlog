from keras import backend
from keras import Model

from .defenitions import IMG_HEIGHT, IMG_WIDTH


class Loss:

    def __init__(self, model: 'Model'):
        self.model = model

    @staticmethod
    def content_loss(base, combination):
        return backend.mean(backend.square(combination - base))

    @staticmethod
    def gram_matrix(x):
        features = backend.batch_flatten(backend.permute_dimensions(x, (2, 0, 1)))
        gram = backend.dot(features, backend.transpose(features))
        return gram

    @classmethod
    def style_loss(cls, style, combination):
        s = cls.gram_matrix(style)
        c = cls.gram_matrix(combination)
        channels = 3
        size = IMG_HEIGHT * IMG_WIDTH
        return backend.sum(backend.square(s - c)) / (4. * (channels ** 2) * (size ** 2))

    @staticmethod
    def total_variation_loss(x):
        a = backend.square(x[:, :IMG_HEIGHT - 1, :IMG_WIDTH - 1] - x[:, 1, :IMG_WIDTH - 1, :])
        b = backend.square(x[:, :IMG_HEIGHT - 1, :IMG_WIDTH - 1] - x[:, :IMG_HEIGHT - 1, 1:, :])
        return backend.sum(backend.pow(a + b, 1.25))

    def total_loss(self, combination_image):
        outputs_dict = dict((layer.name, layer.output) for layer in self.model.layers)
        content_layer = 'block5_conv2'
        style_layers = [
            'block1_conv1',
            'block2_conv1',
            'block3_conv1',
            'block4_conv1',
            'block5_conv1'
        ]
        total_variation_weight = 1e-4
        style_weight = 1.
        content_weight = 0.05

        loss = backend.variable(0.)
        layer_features = outputs_dict[content_layer]
        target_image_features = layer_features[0, :, :, :]
        combination_features = layer_features[2, :, :, :]

        loss += content_weight * self.content_loss(target_image_features, combination_features)

        for layer_name in style_layers:
            layer_features = outputs_dict[layer_name]
            style_reference_features = layer_features[1, :, :, :]
            combination_features = layer_features[2, :, :, :]
            sl = self.style_loss(style_reference_features, combination_features)
            loss += (style_weight / len(style_layers)) * sl

        loss += total_variation_weight * self.total_variation_loss(combination_image)
        return loss
