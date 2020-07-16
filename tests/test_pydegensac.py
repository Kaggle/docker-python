import unittest

import pydegensac
import numpy as np


class TestPydegensac(unittest.TestCase):
    def test_find_homography(self):
        src_pts = np.float32([ [0,0],[0,1],[1,1],[1,0] ]).reshape(-1,2)
        dst_pts = np.float32([ [0,0],[0,-1],[-1,-1],[-1,0] ]).reshape(-1,2)

        H, mask = pydegensac.findHomography(src_pts, dst_pts, 4, 1)

        self.assertEqual(3, len(H))
        self.assertEqual(4, len(mask))



