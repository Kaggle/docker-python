import unittest

import geopandas

class TestGeopandas(unittest.TestCase):
    def test_read(self):
        df = geopandas.read_file(geopandas.datasets.get_path('nybb'))
        self.assertTrue(df.size > 1)
