import unittest

from shapely.geometry import Point

class TestShapely(unittest.TestCase):
    def test_geometry(self):
        p = Point(0.0, 0.0)

        self.assertEqual("Point", p.geom_type)
