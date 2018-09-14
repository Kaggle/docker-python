import unittest

import pandas as pd

from keras.models import Sequential
from keras.layers import Dense
from keras.optimizers import RMSprop
from keras.utils.np_utils import to_categorical

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
