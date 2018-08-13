import unittest

import cv2

class TestOpenCV(unittest.TestCase):
    def test_imread(self):
        img = cv2.imread('/input/tests/data/dot.png')

        self.assertEqual(1, img.shape[0])
