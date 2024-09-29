import unittest

import umap

class TestUmapLearn(unittest.TestCase):
    def test(self):
        self.assertGreater(len(umap.__version__), 0)
