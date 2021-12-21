import unittest

import numpy as np

from implicit.als import AlternatingLeastSquares
from scipy.sparse import csr_matrix


class TestImplicit(unittest.TestCase):
    def test_model(self):
        raw = [
            [0.0, 2.0, 1.5, 1.33333333, 1.25, 1.2, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
            [0.0, 0.0, 2.0, 1.5, 1.33333333, 1.25, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
            [0.0, 0.0, 0.0, 2.0, 1.5, 1.33333333, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
            [0.0, 0.0, 0.0, 0.0, 2.0, 1.5, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
            [0.0, 0.0, 0.0, 0.0, 0.0, 2.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
            [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
            [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 2.0, 1.5, 1.33333333, 1.25, 1.2],
            [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 2.0, 1.5, 1.33333333, 1.25],
            [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 2.0, 1.5, 1.33333333],
            [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 2.0, 1.5],
            [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 2.0],
            [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        ]
        counts = csr_matrix(raw, dtype=np.float64)

        model = AlternatingLeastSquares(factors=3)
        model.fit(counts, show_progress=False)
        rows, cols = model.item_factors, model.user_factors

        assert not np.isnan(np.sum(cols))
        assert not np.isnan(np.sum(rows))
