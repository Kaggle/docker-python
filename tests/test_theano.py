import unittest

import theano
from theano import tensor

class TestTheano(unittest.TestCase):
    def test_addition(self):
        # Declare two symbolic floating-point scalars.
        a = tensor.dscalar()
        b = tensor.dscalar()

        # Create a simple expression.
        c = a + b

        # Convert the expression into a callable object that takes (a,b)
        # values as input and computes a value for 'c'.
        f = theano.function([a,b], c)

        # Bind 1.5 to 'a', 2.5 to 'b', and evaluate 'c'.
        self.assertEqual(4.0, f(1.5, 2.5))
