import unittest

import lightgbm as lgb

from sklearn.datasets import load_iris

class TestLightgbm(unittest.TestCase):
    # Based on the "simple_example" from their documentation:
    # https://github.com/Microsoft/LightGBM/blob/master/examples/python-guide/simple_example.py
    def test_simple(self):
        # Load a dataset aleady on disk
        iris = load_iris()

        lgb_train = lgb.Dataset(iris.data[:100], iris.target[:100])
        lgb_eval = lgb.Dataset(iris.data[100:], iris.target[100:], reference=lgb_train)

        params = {
            'task': 'train',
            'boosting_type': 'gbdt',
            'objective': 'regression',
            'metric': {'l2', 'auc'},
            'num_leaves': 31,
            'learning_rate': 0.05,
            'feature_fraction': 0.9,
            'bagging_fraction': 0.8,
            'bagging_freq': 5,
            'verbose': 0
        }

        # Run only one round for faster test
        gbm = lgb.train(params,
                        lgb_train,
                        num_boost_round=1,
                        valid_sets=lgb_eval,
                        early_stopping_rounds=1)

        self.assertEqual(1, gbm.best_iteration)
