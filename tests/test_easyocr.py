import unittest

import easyocr

class TestEasyOCR(unittest.TestCase):
    def test_readtext(self):
        # The model_storage_directory is only need in tests where we overwrite HOME=/tmp
        reader = easyocr.Reader(['en'], gpu=False, model_storage_directory='/root/.EasyOCR/model')
        result = reader.readtext('/input/tests/data/english.png', detail = 0)
        # ['Reduce your risk of coronavirus infection:', 'Clean hands with soap and water', 
        # 'or alcohol based hand rub', 'Cover nose and mouth when coughing and', 
        # 'sneezing with tissue or flexed elbow', 'Avoid close contact with anyone with', 
        # 'cold or flu like symptoms', 'Thoroughly cook meat and eggs', 
        # 'No unprotected contact with live wild', 'or farm animals', 'World Health', 'Organization']
        self.assertEqual(len(result), 12)
