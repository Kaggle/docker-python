import unittest

import numpy as np
import tensorflow as tf
from tensorflow.contrib.cudnn_rnn import CudnnGRU

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
    def test_cudnn_gru(self):
        input = tf.random_normal([1,2,1])
        init = tf.global_variables_initializer()

        gru = CudnnGRU(
            num_layers=1,
            num_units=1,
            input_mode='skip_input',
            direction='unidirectional',
            kernel_initializer=tf.random_normal_initializer(stddev=0.1)
        )

        gru.build([None, None, 100])
        op = gru(input)

        with tf.Session() as sess:
            sess.run(init)
            # Will fail if Cudnn is not properly installed
            sess.run(op)
    
    @gpu_test
    def test_gpu(self):
        with tf.device('/gpu:0'):
            m1 = tf.constant([2.0, 3.0], shape=[1, 2], name='a')
            m2 = tf.constant([3.0, 4.0], shape=[2, 1], name='b')
            op = tf.matmul(m1, m2)

            with tf.Session() as sess:
                result = sess.run(op)

                self.assertEqual(np.array(18, dtype=np.float32, ndmin=2), result)
