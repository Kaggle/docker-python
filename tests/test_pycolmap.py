import unittest

import numpy as np
import cv2
import pycolmap

class TestPycolmap(unittest.TestCase):
    def test_sift(self):
        img = cv2.cvtColor(cv2.imread('/input/tests/data/face.jpg'), cv2.COLOR_BGR2GRAY)
        img = img.astype(np.float32)/255.
        sift = pycolmap.Sift()
        keypoints, scores, descriptors = sift.extract(img)
        self.assertEqual(keypoints.shape, (64, 4))
