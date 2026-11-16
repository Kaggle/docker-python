import unittest

from PIL import Image
from pdf2image import convert_from_path, pdfinfo_from_path


class TestPdf2Image(unittest.TestCase):
    def test_convert_from_path(self):
        info = pdfinfo_from_path('/input/tests/data/test.pdf')
        pages = convert_from_path('/input/tests/data/test.pdf', dpi=72)

        self.assertEqual(info['Pages'], len(pages))
        self.assertIsInstance(pages[0], Image.Image)
        self.assertGreater(pages[0].width, 0)
        self.assertGreater(pages[0].height, 0)
