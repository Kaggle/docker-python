import unittest

from common import gpu_test, p100_exempt


class TestCuml(unittest.TestCase):
    @gpu_test
    @p100_exempt # b/342143152: cuML(>=24.4v) is inompatible with p100 GPUs.
    def test_pca_fit_transform(self):
        import unittest
        import numpy as np
        from cuml.decomposition import PCA

        x = np.array([[1.0, 2.0], [2.0, 4.0], [3.0, 6.0], [-1.0, -2.0], [-2.0, -4.0]])  
        pca = PCA(n_components=1)

        x_transformed = pca.fit_transform(x)

        self.assertEqual(x_transformed.shape, (5, 1))
