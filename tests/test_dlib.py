import unittest

import cv2
import dlib


class TestDLib(unittest.TestCase):
    def test_dlib_face_detector(self):
        detector = dlib.get_frontal_face_detector()
        image = cv2.imread('/input/tests/data/face.jpg')
        image_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        faces = detector(image_gray, 1)

        self.assertEqual(len(faces), 1)
