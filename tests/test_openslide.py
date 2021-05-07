import unittest

from openslide import open_slide

class TestOpenslide(unittest.TestCase):
    def test_read_tif(self):
        with open_slide('/input/tests/data/test.tif') as slide:
            self.assertEqual(1, slide.level_count)
