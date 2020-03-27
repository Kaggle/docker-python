import unittest

from openslide import open_slide

class TestOpenslide(unittest.TestCase):
    def test_read_tif(self):
        slide = open_slide('/input/tests/data/test.tif')
        
        self.assertEqual(1, slide.level_count)
