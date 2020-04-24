"""Tests for general GPU support"""

import subprocess
import unittest

from common import gpu_test


class TestNvidia(unittest.TestCase):
    @gpu_test
    def test_system_management_interface(self):
        smi = subprocess.Popen(['nvidia-smi'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        smi.communicate()
        self.assertEqual(0, smi.returncode)
