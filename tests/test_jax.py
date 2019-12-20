import unittest

import time

from common import gpu_test


class TestJAX(unittest.TestCase):
    def tanh(self, x):
        import jax.numpy as np
        y = np.exp(-2.0 * x)
        return (1.0 - y) / (1.0 + y)

    @gpu_test
    def test_JAX(self):
        # importing inside the gpu-only test because these packages can't be
        # imported on the CPU image since they are not present there.
        from jax import grad, jit

        grad_tanh = grad(self.tanh)
        ag = grad_tanh(1.0)
        self.assertEqual(0.4199743, ag)
