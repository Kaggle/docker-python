"""Common testing setup"""

import os
import unittest

from threading import BoundedSemaphore

gpu_test = unittest.skipIf(len(os.environ.get('CUDA_VERSION', '')) == 0, 'Not running GPU tests')

# Tests using the GPU heavily must not be run concurrently.
gpu_semaphore = BoundedSemaphore(1)
