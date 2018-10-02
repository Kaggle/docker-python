import unittest

import numpy as np

from hep_ml.preprocessing import BinTransformer

class TestHepML(unittest.TestCase):
    def test_preprocessing(self):
        X = np.array([[1.1, 1.2, 1.3],[5.1, 6.4, 10.5]])
        transformer = BinTransformer().fit(X)
        new_X = transformer.transform(X)

        self.assertEqual((2, 3), new_X.shape)
