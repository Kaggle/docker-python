import unittest

from libpysal.weights import lat2W

class TestPysal(unittest.TestCase):
    def test_distance_band(self):
        w = lat2W(4,4)
        self.assertEqual(16, w.n)