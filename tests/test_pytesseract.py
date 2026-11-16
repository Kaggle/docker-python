import unittest

import pytesseract
from pdf2image import convert_from_path

class TestPytesseract(unittest.TestCase):
    def test_tesseract(self):
        # Rasterize the pdf with pdf2image (poppler). ImageMagick's PDF coder is
        # disabled by patches/imagemagick-policy.xml.
        pages = convert_from_path('/input/tests/data/test.pdf')
        self.assertGreater(len(pages), 0)
        test_string = pytesseract.image_to_string(pages[0])
        self.assertTrue(type(test_string) == str)
