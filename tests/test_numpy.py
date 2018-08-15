import unittest

import numpy as np
from numpy.distutils.system_info import get_info

class TestNumpy(unittest.TestCase):    
    def test_array(self):
        array = np.array([1, 3])

        self.assertEqual((2,), array.shape)

    # Numpy must be linked to the MKL. (Occasionally, a third-party package will muck up the installation
    # and numpy will be reinstalled with an OpenBLAS backing.)
    def test_mkl(self):
        # This will throw an exception if the MKL is not linked correctly.
        get_info("blas_mkl")
