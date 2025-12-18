import unittest

from distutils.version import StrictVersion

import jiter

class TestJiter(unittest.TestCase):
    def test_version(self):
        self.assertEqual(StrictVersion(jiter.__version__), StrictVersion("0.10.0"))
