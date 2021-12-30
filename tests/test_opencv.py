import unittest

import cv2


class TestOpenCV(unittest.TestCase):
    def test_imread(self):
        img = cv2.imread('/input/tests/data/dot.png')

        self.assertEqual(1, img.shape[0])

    def test_classifier(self):
        face_classifier = cv2.CascadeClassifier()
        # Pretrained classifier downloaded from here: https://github.com/opencv/opencv/tree/4.x/data/haarcascades
        face_classifier.load('/input/tests/data/haarcascade_frontalface_alt.xml')

        img = cv2.imread('/input/tests/data/face.jpg')
        frame_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        frame_gray = cv2.equalizeHist(frame_gray)
        faces = face_classifier.detectMultiScale(frame_gray)
        self.assertEqual(1, len(faces))
