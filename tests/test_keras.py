import unittest

import keras
import numpy as np
import pandas as pd

from keras.models import Sequential
from keras.layers import Dense, Dropout, Flatten, Conv2D, MaxPooling2D, CuDNNLSTM
from keras.optimizers import RMSprop, SGD
from keras.utils.np_utils import to_categorical

from common import gpu_test

class TestKeras(unittest.TestCase):
    def test_train(self):
        train = pd.read_csv("/input/tests/data/train.csv")

        x_train = train.iloc[:,1:].values.astype('float32')
        y_train = to_categorical(train.iloc[:,0].astype('int32'))

        model = Sequential()
        model.add(Dense(units=10, input_dim=784, activation='softmax'))

        model.compile(
            loss='categorical_crossentropy',
            optimizer=RMSprop(lr=0.001),
            metrics=['accuracy'])

        model.fit(x_train, y_train, epochs=1, batch_size=32)

    # Uses convnet which depends on libcudnn when running on GPU
    def test_conv2d(self):
        # Generate dummy data
        x_train = np.random.random((100, 100, 100, 3))
        y_train = keras.utils.to_categorical(np.random.randint(10, size=(100, 1)), num_classes=10)
        x_test = np.random.random((20, 100, 100, 3))
        y_test = keras.utils.to_categorical(np.random.randint(10, size=(20, 1)), num_classes=10)

        model = Sequential()
        # input: 100x100 images with 3 channels -> (100, 100, 3) tensors.
        # this applies 32 convolution filters of size 3x3 each.
        model.add(Conv2D(32, (3, 3), activation='relu', input_shape=(100, 100, 3)))
        model.add(Conv2D(32, (3, 3), activation='relu'))
        model.add(MaxPooling2D(pool_size=(2, 2)))
        model.add(Dropout(0.25))

        model.add(Conv2D(64, (3, 3), activation='relu'))
        model.add(Conv2D(64, (3, 3), activation='relu'))
        model.add(MaxPooling2D(pool_size=(2, 2)))
        model.add(Dropout(0.25))

        model.add(Flatten())
        model.add(Dense(256, activation='relu'))
        model.add(Dropout(0.5))
        model.add(Dense(10, activation='softmax'))

        sgd = SGD(lr=0.01, decay=1e-6, momentum=0.9, nesterov=True)

        # This throws if libcudnn is not properly installed with on a GPU
        model.compile(loss='categorical_crossentropy', optimizer=sgd)
        model.fit(x_train, y_train, batch_size=32, epochs=1)
        model.evaluate(x_test, y_test, batch_size=32)

    # Tensorflow 2.0 doesn't support the contrib package.
    #
    # Error:
    #   from tensorflow.contrib.cudnn_rnn.python.ops import cudnn_rnn_ops
    # ModuleNotFoundError: No module named 'tensorflow.contrib'
    #
    # tf.keras should be used instead until this is fixed.
    # @gpu_test
    # def test_cudnn_lstm(self):
    #     x_train = np.random.random((100, 100, 100))
    #     y_train = keras.utils.to_categorical(np.random.randint(10, size=(100, 1)), num_classes=10)
    #     x_test = np.random.random((20, 100, 100))
    #     y_test = keras.utils.to_categorical(np.random.randint(10, size=(20, 1)), num_classes=10)

    #     sgd = SGD(lr=0.01, decay=1e-6, momentum=0.9, nesterov=True)

    #     model = Sequential()
    #     model.add(CuDNNLSTM(32, return_sequences=True, input_shape=(100, 100)))
    #     model.add(Flatten())
    #     model.add(Dense(10, activation='softmax'))


    #     model.compile(loss='categorical_crossentropy', optimizer=sgd)
    #     model.fit(x_train, y_train, batch_size=32, epochs=1)
    #     model.evaluate(x_test, y_test, batch_size=32)

