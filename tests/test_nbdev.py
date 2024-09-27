import unittest

import nbdev

class TestNbdev(unittest.TestCase):
    def test(self):
        self.assertGreater(len(nbdev.__version__), 0)

