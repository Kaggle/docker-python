import unittest

import numpy as np
import tensorflow as tf

from common import gpu_test


class TestTensorflow(unittest.TestCase):
    def test_addition(self):        
        result = tf.add(2, 3)
        self.assertEqual(5, result.numpy())

    def test_conv2d(self):
        input = tf.random.normal([1,2,2,1])
        filter = tf.random.normal([1,1,1,1])

        result = tf.nn.conv2d(input, filter, strides=[1, 1, 1, 1], padding='SAME')
        self.assertEqual(4, len(result.shape))
    
    def test_tf_keras(self):
        x_train = np.random.random((100, 28, 28))
        y_train = np.random.randint(10, size=(100, 1))
        x_test = np.random.random((20, 28, 28))
        y_test = np.random.randint(10, size=(20, 1))

        model = tf.keras.models.Sequential([
            tf.keras.layers.Flatten(input_shape=(28, 28)),
            tf.keras.layers.Dense(128, activation='relu'),
            tf.keras.layers.Dropout(0.2),
            tf.keras.layers.Dense(10, activation='softmax')
        ])

        model.compile(
            optimizer='adam',
            loss='sparse_categorical_crossentropy',
            metrics=['accuracy'])

        model.fit(x_train, y_train, epochs=1)
        model.evaluate(x_test, y_test)
        

    def test_lstm(self):
        x_train = np.random.random((100, 28, 28))
        y_train = np.random.randint(10, size=(100, 1))
        x_test = np.random.random((20, 28, 28))
        y_test = np.random.randint(10, size=(20, 1))

        model = tf.keras.Sequential([
            tf.keras.layers.Bidirectional(tf.keras.layers.LSTM(64, input_shape=(28, 28))),
            tf.keras.layers.Dense(64, activation='relu'),
            tf.keras.layers.Dense(1, activation='sigmoid')
        ])

        model.compile(
            loss='binary_crossentropy',
            optimizer='adam',
            metrics=['accuracy'])

        model.fit(x_train, y_train, epochs=1)
        model.evaluate(x_test, y_test)
    
    @gpu_test
    def test_gpu(self):
        with tf.device('/gpu:0'):
            m1 = tf.constant([2.0, 3.0], shape=[1, 2], name='a')
            m2 = tf.constant([3.0, 4.0], shape=[2, 1], name='b')
            result = tf.matmul(m1, m2)
            self.assertEqual(np.array(18, dtype=np.float32, ndmin=2), result.numpy())

    @gpu_test
    def test_is_built_with_cuda(self):
        self.assertTrue(tf.test.is_built_with_cuda())

    @gpu_test
    def test_is_gpu_available(self):
        self.assertTrue(tf.test.is_gpu_available(cuda_only=True))
