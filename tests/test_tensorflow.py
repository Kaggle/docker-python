import unittest

import tensorflow as tf

class TestTensorflow(unittest.TestCase):
    def test_addition(self):        
        op = tf.add(2, 3)        
        sess = tf.Session()

        result = sess.run(op)

        self.assertEqual(5, result)
