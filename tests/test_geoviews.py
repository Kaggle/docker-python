import unittest

import geoviews.feature as gf

from cartopy import crs

class TestGeoviews(unittest.TestCase):
    def test_viz(self):
        (gf.ocean + gf.land + gf.ocean * gf.land * gf.coastline * gf.borders).options(
            'Feature', projection=crs.Geostationary(), global_extent=True, height=325
        ).cols(3)
