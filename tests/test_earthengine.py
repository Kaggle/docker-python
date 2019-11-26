import unittest
import ee

class TestEarthEngine(unittest.TestCase):
    def test_version(self):
        self.assertIsNotNone(ee.__version__)
