import unittest

from common import p100_exempt

class TestGeoviews(unittest.TestCase):

    @p100_exempt # b/342143152: Uses cuDF(>=24.4v), which is no longer capitble with p100 GPUs.

    def test_viz(self):
        import geoviews.feature as gf
        import holoviews as hv
        from cartopy import crs

        hv.extension('matplotlib')
        (gf.ocean + gf.land + gf.ocean * gf.land * gf.coastline * gf.borders).options(
            'Feature', projection=crs.Geostationary(), global_extent=True
        ).cols(3)
