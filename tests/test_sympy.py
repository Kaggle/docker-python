import unittest

import numpy as np
import sympy

class TestSympy(unittest.TestCase):
    def test_matrix(self):
        self.assertEqual((2, 2), sympy.Matrix([[0, 1], [1, 0]]).shape)