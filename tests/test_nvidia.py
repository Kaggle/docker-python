"""Tests for general GPU support"""

import os
import subprocess
import sys
import unittest

from common import gpu_test


class TestNvidia(unittest.TestCase):
    @gpu_test
    def test_system_management_interface(self):
        smi = subprocess.Popen(['nvidia-smi'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        smi.communicate()
        self.assertEqual(0, smi.returncode)

    @gpu_test
    def test_pycuda(self):   
        import pycuda.driver    
        pycuda.driver.init()
        gpu_name = pycuda.driver.Device(0).name() 
        self.assertNotEqual(0, len(gpu_name))

