import unittest

from distutils.version import StrictVersion

import numpy as np
import io
from contextlib import redirect_stdout

class TestNumpy(unittest.TestCase):
    def test_version(self):
        # b/370860329: newer versions are not capable with current tensorflow
        self.assertEqual(StrictVersion(np.__version__), StrictVersion("1.26.4")) 

    def test_array(self):
        array = np.array([1, 3])

        self.assertEqual((2,), array.shape)

    # Numpy must be linked to the MKL. (Occasionally, a third-party package will muck up the installation
    # and numpy will be reinstalled with an OpenBLAS backing.)
    def test_mkl(self):
        try:
            from numpy.distutils.system_info import get_info
            # This will throw an exception if the MKL is not linked correctly or return an empty dict.
            self.assertTrue(get_info("blas_mkl"))
        except:
            # Fallback to check if mkl is present via show_config()
            config_out = io.StringIO()
            with redirect_stdout(config_out):
                np.show_config()
            self.assertIn("mkl_rt", config_out.getvalue())
