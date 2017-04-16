import numpy as np
import os
import cPickle as pickle
import keras.backend as K
from keras.applications import vgg16

class Params(object):
    def __init__(self, image_size, batch_size=16):
        self.image_size = image_size
        self.batch_size = batch_size

def disable_training(model):
    for layer in model.layers:
        layer.trainable = False

def pop_layer(model):
    """Removes the last layer in the model.
    # Raises
        TypeError: if there are no layers in the model.
    Adapted from keras.models.Sequential.pop(...)
    """
    if not model.layers:
        raise TypeError('There are no layers in the model.')

    model.layers.pop()
    if not model.layers:
        model.outputs = []
        model.inbound_nodes = []
        model.outbound_nodes = []
    else:
        model.layers[-1].outbound_nodes = []
        model.outputs = [model.layers[-1].output]
        # update self.inbound_nodes
        model.inbound_nodes[0].output_tensors = model.outputs
        model.inbound_nodes[0].output_shapes = [model.outputs[0]._keras_shape]
    model.built = False

def save_features_and_labels(model, generator, directory, target_size, batch_size, count, output_path):
    flow = generator.flow_from_directory(directory, target_size=target_size, batch_size=batch_size, shuffle=True)
    batch_count = count // batch_size
    features = []
    labels = []
    for batch in xrange(batch_count):
        batch_X, batch_y = flow.next()
        batch_features = model.predict(batch_X, batch_size=batch_size)
        features.append(batch_features)
        labels.append(batch_y)
    labels = np.concatenate(labels)
    features = np.concatenate(features)
    with open(output_path, "wb") as w:
        pickle.dump((features, labels), w)

def load_features_and_labels(path):
    with open(path, "rb") as r:
        features, labels = pickle.load(r)
        return features, labels

class MultiModel(object):
    """A helper class that presents a unified interface to multiple models.
    TODO: It seems like there may be better ways to  do this with Keras."""
    def __init__(self, models):
        self.models = models

    def layer_iter(self):
        for model in self.models:
            for layer in model.layers:
                yield layer

    def predict(self, data):
        result = data
        for model in self.models:
            result = model.predict(result)
        return result

LEARNING_PHASE_TEST=0
LEARNING_PHASE_TRAIN=1

class ClassActivationMap(object):
    """A helper class that builds a class activation map.

    References
    ==========
    http://cnnlocalization.csail.mit.edu/
    """
    # TODO(emmett): automatically populate these values from a model?
    def __init__(self, inputs, gap_layer, dense_layer):
        """Create a class activation map helper.

        Parameters
        ==========
        inputs: list
            Model inputs
        gap_layer: keras.layer
            The GlobalAveragePooling2D layer, preceded by convolutions and with a dense layer afterward that creates the
            final class scores.
        dense_layer: keras.layer.Dense
            The dense layer just after the GlobaAveragePooling2D that creates the final class scores.
        """
        self.inputs = inputs
        self.gap_layer = gap_layer
        self.dense_layer = dense_layer
        self.forward_conv = self._make_forward_conv()
        self.class_weights = self._make_class_weights()

    def _make_forward_conv(self):
        # We need to add the learning phase as params for layers like Dropout
        function_inputs = self.inputs + [K.learning_phase()]
        function_outputs = [self.gap_layer.input, self.dense_layer.output]
        forward_conv = K.function(inputs=function_inputs, outputs=function_outputs)
        # Create a forward function that only returns the output for test phase, disabiling any dropout.
        test_forward_conv = lambda input, forward_conv=forward_conv: forward_conv([input, LEARNING_PHASE_TEST])[0]
        return test_forward_conv

    def _make_class_weights(self):
        class_weights = self.dense_layer.get_weights()[0]
        return class_weights

    def map_for_class(self, data, class_index):
        """Return a spatial class activation map over the image space.

        Parameters
        ==========
        data: numpy.array
            Model input data to call predict on.
        class_index: int
            The class index

        Returns
        =======
        np.array
            A numpy array that is overlayed on the input image and illustrates the relative importance of each subregion
            of the image to the final class score.
        """
        conv_output = self.forward_conv(data)
        map_shape = conv_output.shape[1:3]
        class_activation_map = np.zeros(dtype=np.float32, shape=map_shape)

        for feature_index, weights in enumerate(self.class_weights[:, class_index]):
            class_activation_map += weights * conv_output[0, :, :, feature_index]
        return class_activation_map

    def softmax_total(self, data):
        conv_output = self.forward_conv(data)
        map_shape = conv_output.shape[1:3]

        total_activation = np.zeros(dtype=np.float32, shape=map_shape)

        for class_index in xrange(self.class_weights.shape[1]):
            class_activation_map = np.zeros(dtype=np.float32, shape=map_shape)
            for feature_index, weights in enumerate(self.class_weights[:, class_index]):
                class_activation_map += weights * conv_output[0, :, :, feature_index]
            total_activation += np.exp(class_activation_map)

        return total_activation

    def softmax_map_for_class(self, data, class_index):
        """Return a spatial class softmax activation map over the image space.

        Parameters
        ==========
        data: numpy.array
            Model input data to call predict on.
        class_index: int
            The class index

        Returns
        =======
        np.array
            A numpy array that is overlayed on the input image and illustrates the relative importance of each subregion
            of the image to the final class score.
        """
        total_activation = self.softmax_total(data)
        return np.exp(self.map_for_class(data, class_index)) / total_activation


class FeatureCache():
    """Cache feature outputs for pretrained layers."""
    def __init__(self, params, model, generator, directory, count, cache_path):
        self.features = None
        self.labels = None
        if not os.path.exists(cache_path):
            save_features_and_labels(model, generator, directory, params.image_size, params.batch_size, count,
                                     cache_path)
        features, labels = load_features_and_labels(cache_path)
        self.features = features
        self.labels = labels


def vgg16_image_preprocessor(image):
    """Return a preprocessed image for VGG16."""
    batch_image = np.expand_dims(image, axis=0)
    batch_image = vgg16.preprocess_input(batch_image)
    preprocessed_image = batch_image[0, :, :, :]
    return preprocessed_image
