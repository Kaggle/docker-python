import unittest

import geopandas

class TestGeopandas(unittest.TestCase):
    def test_read(self):
        df = geopandas.read_file(geopandas.datasets.get_path('nybb'))
        self.assertTrue(df.size > 1)

    def test_spatial_join(self):
        cities = geopandas.read_file(geopandas.datasets.get_path('naturalearth_cities'))
        world = geopandas.read_file(geopandas.datasets.get_path('naturalearth_lowres'))
        countries = world[['geometry', 'name']]
        countries = countries.rename(columns={'name':'country'})
        cities_with_country = geopandas.sjoin(cities, countries, how="inner", op='intersects')
        self.assertTrue(cities_with_country.size > 1)