import unittest

import tensorflow as tf
import numpy as np

from kerastuner.tuners import RandomSearch


class TestKerasTuner(unittest.TestCase):
    def test_search(self):
        def build_model(hp):
            x_train = np.random.random((100, 28, 28))
            y_train = np.random.randint(10, size=(100, 1))
            x_test = np.random.random((20, 28, 28))
            y_test = np.random.randint(10, size=(20, 1))

            model = tf.keras.models.Sequential([
                tf.keras.layers.Flatten(input_shape=(28, 28)),
                tf.keras.layers.Dense(128, activation='relu'),
                tf.keras.layers.Dropout(hp.Choice('dropout_rate', values=[0.2, 0.4])),
                tf.keras.layers.Dense(10, activation='softmax')
            ])

            model.compile(
                optimizer='adam',
                loss='sparse_categorical_crossentropy',
                metrics=['accuracy'])

            return model

            tuner = RandomSearch(build_model, objective='accuracy', max_trials=1, executions_per_trial=1, seed=1)

            tuner.search(x_train, y_train, epochs=1)

            self.assertEqual(0.4, tuner.get_best_hyperparameters(1)[0].get('dropout_rate'))