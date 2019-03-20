import unittest
import io
import pytesseract
import numpy as np
from PIL import Image
from wand.image import Image as wandimage

class TestPytesseract(unittest.TestCase):
    def test_tesseract(self):
        # Open pdf with Wand
        with wandimage(filename='/input/tests/data/test.pdf') as wand_image:
            img_buffer = np.asarray(bytearray(wand_image.make_blob(format='png')), dtype='uint8')
            bytesio = io.BytesIO(img_buffer)
            test_string = pytesseract.image_to_string(Image.open(bytesio))
            self.assertTrue(type(test_string) == str)
