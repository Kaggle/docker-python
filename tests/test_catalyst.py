import unittest

import catalyst

class TestCatalyst(unittest.TestCase):

    def test_version(self):
        self.assertIsNotNone(catalyst.__version__)
