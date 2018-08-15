import unittest

import mxnet as mx

class TestMxNet(unittest.TestCase):
    def test_array(self):    
        x = mx.nd.array([[1, 2, 3], [4, 5, 6]])

        self.assertEqual((2, 3), x.shape)
