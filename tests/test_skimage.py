import unittest

from skimage import data, filters, io

class TestSkImage(unittest.TestCase):
    def test_filter(self):
        image = data.coins()
        filters.sobel(image)

    def test_codecs(self):
        img = io.MultiImage('/input/tests/data/test.tif')
        
        self.assertEqual((10, 10, 4), img[0].shape)