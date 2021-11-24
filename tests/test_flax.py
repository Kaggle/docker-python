import unittest

import jax.numpy as jnp
import numpy as np

from flax import linen as nn


class TestFlax(unittest.TestCase):

    def test_bla(self):
        x = jnp.full((1, 3, 3, 1), 2.)
        mul_reduce = lambda x, y: x * y
        y = nn.pooling.pool(x, 1., mul_reduce, (2, 2), (1, 1), 'VALID')
        np.testing.assert_allclose(y, np.full((1, 2, 2, 1), 2. ** 4))
