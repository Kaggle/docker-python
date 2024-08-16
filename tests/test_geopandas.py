import unittest

import geopandas
from shapely.geometry import Polygon

class TestGeopandas(unittest.TestCase):
    def test_GeoSeries(self):
        p1 = Polygon([(0, 0), (1, 0), (1, 1)])
        p2 = Polygon([(0, 0), (1, 0), (1, 1), (0, 1)])
        p3 = Polygon([(2, 0), (3, 0), (3, 1), (2, 1)])
        g = geopandas.GeoSeries([p1, p2, p3])