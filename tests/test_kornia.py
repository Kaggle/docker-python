import unittest

import cv2
import torch
import kornia

class TestKornia(unittest.TestCase):
    def test_imread_opencv(self):
        img = cv2.imread('/input/tests/data/dot.png')
        img_t = kornia.image_to_tensor(img)

        self.assertEqual(img.shape, (1, 1, 3))
        self.assertEqual(img_t.shape, (3, 1, 1))

    def test_grayscale_torch(self):
        img_rgb = torch.rand(2, 3, 4, 5)
        img_gray = kornia.rgb_to_grayscale(img_rgb)

        self.assertEqual(img_gray.shape, (2, 1, 4, 5))
