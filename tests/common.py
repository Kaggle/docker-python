"""Common testing setup"""

import os
import unittest

gpu_test = unittest.skipIf(len(os.environ.get('CUDA_VERSION', '')) == 0, 'Not running GPU tests')
