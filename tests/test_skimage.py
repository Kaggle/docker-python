import unittest

from skimage import data, filters

class TestSkImage(unittest.TestCase):
    def test_filter(self):
        image = data.coins()
        filters.sobel(image)
