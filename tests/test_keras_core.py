import unittest

import numpy as np
import os

os.environ["KERAS_BACKEND"] = "tensorflow" 

# Note that keras_core should only be imported after the backend
# has been configured. The backend cannot be changed once the
# package is imported.
import keras_core as keras

class TestKerasCore(unittest.TestCase):
    def test_train(self):
        # Load the data and split it between train and test sets
        (x_train, y_train), (x_test, y_test) = keras.datasets.mnist.load_data(
            path='/input/tests/data/mnist.npz'
        )

        # Scale images to the [0, 1] range
        x_train = x_train.astype("float32") / 255
        x_train = x_train[:100, :]
        y_train = y_train[:100]
        x_test = x_test.astype("float32") / 255
        x_test = x_test[:100, :]
        y_test = y_test[:100]
        # Make sure images have shape (28, 28, 1)
        x_train = np.expand_dims(x_train, -1)
        x_test = np.expand_dims(x_test, -1)

        # Model parameters
        num_classes = 10
        input_shape = (28, 28, 1)

        model = keras.Sequential(
            [
                keras.layers.Input(shape=input_shape),
                keras.layers.Conv2D(64, kernel_size=(3, 3), activation="relu"),
                keras.layers.Conv2D(64, kernel_size=(3, 3), activation="relu"),
                keras.layers.MaxPooling2D(pool_size=(2, 2)),
                keras.layers.Conv2D(128, kernel_size=(3, 3), activation="relu"),
                keras.layers.Conv2D(128, kernel_size=(3, 3), activation="relu"),
                keras.layers.GlobalAveragePooling2D(),
                keras.layers.Dropout(0.5),
                keras.layers.Dense(num_classes, activation="softmax"),
            ]
        )

        model.compile(
            loss=keras.losses.SparseCategoricalCrossentropy(),
            optimizer=keras.optimizers.Adam(learning_rate=1e-3),
            metrics=[
                keras.metrics.SparseCategoricalAccuracy(name="acc"),
            ],
        )

        batch_size = 128
        epochs = 1

        callbacks = [
            keras.callbacks.ModelCheckpoint(filepath="model_at_epoch_{epoch}.keras"), # Saves model checkpoint while training
            keras.callbacks.EarlyStopping(monitor="val_loss", patience=2),
        ]

        model.fit(
            x_train,
            y_train,
            batch_size=batch_size,
            epochs=epochs,
            validation_split=0.15,
            callbacks=callbacks,
        )
        score = model.evaluate(x_test, y_test, verbose=0)
        print(score)
        self.assertNotEqual(0, score)

