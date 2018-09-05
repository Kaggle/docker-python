import unittest

import numpy as np
import tensorflow as tf

from common import gpu_test


class TestTensorflow(unittest.TestCase):
    def test_addition(self):        
        op = tf.add(2, 3)        
        sess = tf.Session()

        result = sess.run(op)

        self.assertEqual(5, result)
    
    @gpu_test
    def test_gpu(self):
        with tf.device('/gpu:0'):
            m1 = tf.constant([2.0, 3.0], shape=[1, 2], name='a')
            m2 = tf.constant([3.0, 4.0], shape=[2, 1], name='b')
            op = tf.matmul(m1, m2)

            sess = tf.Session()
            result = sess.run(op)

            self.assertEqual(np.array(18, dtype=np.float32, ndmin=2), result)
