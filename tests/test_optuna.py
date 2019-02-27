import unittest

import optuna


class TestOptuna(unittest.TestCase):

    def test_study(self):

        def objective(trial):
            x = trial.suggest_uniform('x', -1., 1.)
            return x ** 2

        n_trials = 20
        study = optuna.create_study()
        study.optimize(objective, n_trials=n_trials)
        self.assertEqual(len(study.trials), n_trials)
