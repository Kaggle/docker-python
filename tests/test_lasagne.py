import unittest

import lasagne
import theano.tensor as T

class TestLasagne(unittest.TestCase):
    def test_network_definition(self):
        input_var = T.tensor4('X')

        network = lasagne.layers.InputLayer((None, 3, 32, 32), input_var)
        network = lasagne.layers.Conv2DLayer(network, 64, (3, 3))

        params = lasagne.layers.get_all_params(network, trainable=True)

        self.assertEqual(2, len(params))
