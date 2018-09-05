import unittest

from common import gpu_test
import tensorflow as tf

class TestTensorflow(unittest.TestCase):
    def test_addition(self):        
        op = tf.add(2, 3)        
        sess = tf.Session()

        result = sess.run(op)

        self.assertEqual(5, result)
    
    @gpu_test
    def test_gpu(self):
        with tf.device('/gpu:0'):
            m1 = tf.constant([1.0, 2.0, 3.0, 4.0, 5.0, 6.0], shape=[2, 3], name='a')
            m2 = tf.constant([1.0, 2.0, 3.0, 4.0, 5.0, 6.0], shape=[3, 2], name='b')
            op = tf.matmul(m1, m2)

            sess = tf.Session()
            result = sess.run(op)

            # TODO(rosbo): Adjust assertion
            self.assertEqual(5, result)

