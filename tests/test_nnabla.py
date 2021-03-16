import unittest

import numpy as np
import nnabla as nn
import nnabla.functions as F
from nnabla.ext_utils import get_extension_context

from common import gpu_test


class TestNNabla(unittest.TestCase):
    def test_addition(self):
        # entry variables
        a = nn.Variable.from_numpy_array(np.random.random())
        b = nn.Variable.from_numpy_array(np.random.random())

        # add operation
        c = a + b

        # forward
        c.forward()

        self.assertAlmostEqual(c.d, a.d + b.d, places=3)

    @gpu_test
    def test_cuda_ext(self):
        ctx = get_extension_context('cudnn', device_id='0')
        nn.set_default_context(ctx)
