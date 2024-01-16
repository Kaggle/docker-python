import unittest

import numpy as np
from numba import jit, cuda

from common import gpu_test

class TestNumba(unittest.TestCase):
    def test_jit(self):
        x = np.arange(100).reshape(10, 10)

        @jit(nopython=True) # Set "nopython" mode for best performance, equivalent to @njit
        def go_fast(a): # Function is compiled to machine code when called the first time
            trace = 0.0
            for i in range(a.shape[0]):   # Numba likes loops
                trace += np.tanh(a[i, i]) # Numba likes NumPy functions
            return a + trace              # Numba likes NumPy broadcasting

        self.assertEqual(10, go_fast(x).shape[0])

    @gpu_test
    def test_cuda_jit(self):
        x = np.arange(10)

        @cuda.jit
        def increment_by_one(an_array):
            pos = cuda.grid(1)
            if pos < an_array.size:
                an_array[pos] += 1

        threadsperblock = 32
        blockspergrid = (x.size + (threadsperblock - 1))
        self.assertEqual(0, x[0])
        increment_by_one[blockspergrid, threadsperblock](x)
        self.assertEqual(1, x[0])
