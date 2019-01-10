import unittest

import numpy as np
import tensorflow as tf
from tensorflow.contrib import cudnn_rnn
from tensorflow.python.framework import dtypes
from tensorflow.python.ops import variables

from common import gpu_test


class TestTensorflow(unittest.TestCase):
    def test_addition(self):        
        op = tf.add(2, 3)        
        sess = tf.Session()

        result = sess.run(op)

        self.assertEqual(5, result)

    def test_conv2d(self):
        input = tf.random_normal([1,2,2,1])
        filter = tf.random_normal([1,1,1,1])

        op = tf.nn.conv2d(input, filter, strides=[1, 1, 1, 1], padding='SAME')
        with tf.Session() as sess:
            result = sess.run(op)
            self.assertEqual(4, len(result.shape))

    @gpu_test
    def test_cudnn_lstm(self):
        num_layers = 4
        num_units = 2
        batch_size = 8
        dir_count = 1

        inputs = tf.random_uniform([num_layers * dir_count, batch_size, num_units], dtype=dtypes.float32)

        lstm = cudnn_rnn.CudnnLSTM(
            num_layers=num_layers,
            num_units=num_units,
            direction='unidirectional',
            kernel_initializer=tf.constant_initializer(0.),
            bias_initializer=tf.constant_initializer(0.),
            name='test_gru'
        )

        outputs, _ = lstm(inputs)
        total_sum = tf.reduce_sum(outputs)

        with tf.Session() as sess:
            sess.run(variables.global_variables_initializer())
            result = sess.run(total_sum)
            self.assertEqual(0, result)
    
    @gpu_test
    def test_gpu(self):
        with tf.device('/gpu:0'):
            m1 = tf.constant([2.0, 3.0], shape=[1, 2], name='a')
            m2 = tf.constant([3.0, 4.0], shape=[2, 1], name='b')
            op = tf.matmul(m1, m2)

            with tf.Session() as sess:
                result = sess.run(op)

                self.assertEqual(np.array(18, dtype=np.float32, ndmin=2), result)
