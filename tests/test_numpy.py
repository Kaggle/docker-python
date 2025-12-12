import unittest

from distutils.version import StrictVersion

import numpy as np
import io
from contextlib import redirect_stdout

class TestNumpy(unittest.TestCase):
    def test_array(self):
        array = np.array([1, 3])

        self.assertEqual((2,), array.shape)
