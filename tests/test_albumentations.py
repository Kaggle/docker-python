import unittest

import cv2
from albumentations import HorizontalFlip

class TestAlbumentations(unittest.TestCase):
    def test_rotate(self):
        image = cv2.imread('/input/tests/data/dot.png')
        aug = HorizontalFlip(p=1)
        image_rotated = aug(image=image)['image']
