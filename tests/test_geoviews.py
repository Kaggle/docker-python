import unittest

import geoviews.feature as gf
import holoviews as hv
from cartopy import crs

class TestGeoviews(unittest.TestCase):
    def test_viz(self):
        hv.extension('matplotlib')
        (gf.ocean + gf.land + gf.ocean * gf.land * gf.coastline * gf.borders).options(
            'Feature', projection=crs.Geostationary(), global_extent=True
        ).cols(3)
