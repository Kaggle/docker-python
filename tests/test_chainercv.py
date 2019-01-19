from __future__ import division
import math
import numpy
import unittest

from chainercv.utils import tile_images


class TestChainerCV(unittest.TestCase):

    def test_tile_images(self):
        B = numpy.random.randint(10, 20)
        n_col = numpy.random.randint(2, 5)
        H = 30
        W = 40
        fill = 128
        pad = 0

        imgs = numpy.random.uniform(255, size=(B, 3, H, W))
        tile = tile_images(imgs, n_col, pad, fill=fill)

        if isinstance(pad, int):
            pad_y = pad
            pad_x = pad
        else:
            pad_y, pad_x = pad
        n_row = int(math.ceil(B / n_col))
        self.assertTrue(n_col >= 1 and n_row >= 1)
        start_y_11 = H + pad_y + pad_y // 2
        start_x_11 = W + pad_x + pad_x // 2
        tile_11 = tile[:,
                       start_y_11:start_y_11 + H,
                       start_x_11:start_x_11 + W]

        numpy.testing.assert_equal(tile_11, imgs[(n_col - 1) + 2])
