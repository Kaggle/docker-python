import unittest

import zarr
from numcodecs import Blosc

class TestZARR(unittest.TestCase):
    def test_zarr(self):
        z = zarr.zeros((10, 10), chunks=(2, 2), dtype='i4')
        z.resize(20, 20)
        z[:] = 42
        self.assertEqual(42, z[0,0])
    
    def test_zarr_with_specified_compression(self):
        compressor = Blosc(cname='zstd', clevel=3, shuffle=Blosc.BITSHUFFLE)
        z = zarr.zeros((10, 10), chunks=(2, 2), dtype='i4', compressor=compressor)
        self.assertIsNotNone(z.compressor)
