import unittest

from hyperopt import fmin, tpe, hp

class TestHyperopt(unittest.TestCase):
    def test_find_min(self):
        best = fmin(
            fn=lambda x: x ** 2,
            space=hp.uniform('x', -10, 10),
            algo=tpe.suggest,
            max_evals=1,
        )
        self.assertIn('x', best)