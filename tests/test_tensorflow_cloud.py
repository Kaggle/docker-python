import unittest

import tensorflow_cloud as tfc


class TestTensorflowCloud(unittest.TestCase):
    def test_remote(self):
        self.assertFalse(tfc.remote())
