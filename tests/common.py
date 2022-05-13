"""Common testing setup"""

import os
import unittest

gpu_test = unittest.skipIf(len(os.environ.get('CUDA_VERSION', '')) == 0, 'Not running GPU tests')
tpu_test = unittest.skipIf(len(os.environ.get('ISTPUVM', '')) == 0, 'Not running TPU tests')
