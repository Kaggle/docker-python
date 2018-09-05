"""Tests for general GPU support"""

import os
import subprocess
import sys
import unittest

import common
import pycuda

from common import gpu_test


class TestNvidia(unittest.TestCase):
    @gpu_test
    def test_system_management_interface(self):
        smi = subprocess.Popen(['nvidia-smi'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        print(smi.communicate()[0].decode())
        # TODO(rosbo): Add assertion

    @gpu_test
    def test_pycuda(self):       
        result = pycuda.driver.Device(0).name() 
        print(result)
        # TODO(rosbo): Add assertion

