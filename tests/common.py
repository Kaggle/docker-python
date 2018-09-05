"""Common testing setup"""

import os
import unittest

gpu_test = unittest.skipIf(os.environ.get('HAS_GPU', False) == False, 'Not running GPU tests')
