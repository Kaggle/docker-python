import unittest

import theano
from theano import tensor

class TestTheano(unittest.TestCase):
    def test_addition(self):
        # declare two symbolic floating-point scalars
        a = tensor.dscalar()
        b = tensor.dscalar()

        # create a simple expression
        c = a + b

        # convert the expression into a callable object that takes (a,b)
        # values as input and computes a value for c
        f = theano.function([a,b], c)

        # bind 1.5 to 'a', 2.5 to 'b', and evaluate 'c'
        self.assertEqual(4.0, f(1.5, 2.5))
