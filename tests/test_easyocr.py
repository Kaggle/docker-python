import unittest
import easyocr

class TestEasyOCR(unittest.TestCase):
    def test_readtext(self):
        reader = easyocr.Reader(['en'], gpu=False)  # need to run only once to load model into memory
        result = reader.readtext('/input/tests/data/english.png', detail = 0)
        self.assertEqual(len(result), 7)
