import unittest

from bayes_opt import BayesianOptimization


class TestBayesOpt(unittest.TestCase):
    def test_optimize(self):
        # Bounded region of parameter space
        pbounds = {'x': (2, 4), 'y': (-3, 3)}

        optimizer = BayesianOptimization(
            f=black_box_function,
            pbounds=pbounds,
            random_state=1,
        )

        optimizer.maximize(
            init_points=2,
            n_iter=1,
        )       

        self.assertAlmostEqual(-7, optimizer.max['target'], places=0) # compares using 0 decimal
    

def black_box_function(x, y):
    """Function with unknown internals we wish to maximize.

    This is just serving as an example, for all intents and
    purposes think of the internals of this function, i.e.: the process
    which generates its output values, as unknown.
    """
    return -x ** 2 - (y - 1) ** 2 + 1