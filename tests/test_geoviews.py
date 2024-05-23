import unittest

from common import p100_exempt

@p100_exempt
class TestGeoviews(unittest.TestCase):
    import geoviews.feature as gf
    import holoviews as hv
    from cartopy import crs

    def test_viz(self):
        hv.extension('matplotlib')
        (gf.ocean + gf.land + gf.ocean * gf.land * gf.coastline * gf.borders).options(
            'Feature', projection=crs.Geostationary(), global_extent=True
        ).cols(3)
