import unittest

import cartopy.crs as ccrs

class TestCartopy(unittest.TestCase):
    def test_projection(self):
        ccrs.PlateCarree()
        ccrs.Mollweide()
