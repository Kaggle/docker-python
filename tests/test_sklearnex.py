import unittest

import numpy as np

class TestSklearnex(unittest.TestCase):
    def test_dbscan(self):
        from sklearnex.cluster import DBSCAN
        X = np.array([[1., 2.], [2., 2.], [2., 3.],
            [8., 7.], [8., 8.], [25., 80.]], dtype=np.float32)

        clustering = DBSCAN(eps=3, min_samples=2).fit(X)
        np.testing.assert_array_equal(np.array([0, 0, 0, 1, 1, -1]), clustering.labels_)