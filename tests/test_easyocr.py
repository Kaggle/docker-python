import unittest
import easyocr

class TestEasyOCR(unittest.TestCase):
    def test_readtext(self):
    	reader = easyocr.Reader(['ch_sim','en']) # need to run only once to load model into memory
		result = reader.readtext('chinese.jpg', detail = 0)
        self.assertEqual(len(result), 8)
