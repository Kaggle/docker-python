import unittest

import time

import jax.numpy as np
from jax import grad, jit


class TestJAX(unittest.TestCase):
    def tanh(self, x):
        y = np.exp(-2.0 * x)
        return (1.0 - y) / (1.0 + y)

    @gpu_test
    def test_JAX(self):
        grad_tanh = grad(self.tanh)
        ag = grad_tanh(1.0)
        print(f'JAX autograd test: {ag}')
        assert ag==0.4199743
