"""Tests for general GPU support"""

import unittest

from common import gpu_test


class TestPycuda(unittest.TestCase):
    @gpu_test
    def test_pycuda(self):   
        import pycuda.driver    
        pycuda.driver.init()
        gpu_name = pycuda.driver.Device(0).name() 
        self.assertNotEqual(0, len(gpu_name))
