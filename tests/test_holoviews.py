import unittest

import holoviews as hv

class TestHoloviews(unittest.TestCase):
    def test_curve(self):
        xs = range(-10,11)
        ys = [100-x**2 for x in xs]

        hv.Curve((xs, ys))
