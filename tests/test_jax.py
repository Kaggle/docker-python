import unittest

import os
import time

import jax
import jax.numpy as np

from common import gpu_test
from jax import grad, jit


class TestJAX(unittest.TestCase):
    def tanh(self, x):
        y = np.exp(-2.0 * x)
        return (1.0 - y) / (1.0 + y)

    def test_grad(self):
        grad_tanh = grad(self.tanh)
        ag = grad_tanh(1.0)
        self.assertEqual(0.4199743, ag)

    def test_backend(self):
        expected_device_kind = 'cpu' if len(os.environ.get('CUDA_VERSION', '')) == 0 else 'gpu'
        self.assertEqual(expected_device_kind, jax.default_backend())
