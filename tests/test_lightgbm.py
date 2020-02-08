import unittest

import lightgbm as lgb

from common import gpu_test

class TestLightgbm(unittest.TestCase):
    # Based on the "simple_example" from their documentation:
    # https://github.com/Microsoft/LightGBM/blob/master/examples/python-guide/simple_example.py
    def test_cpu(self):
        lgb_train = lgb.Dataset('/input/tests/data/lgb_train.bin')
        lgb_eval = lgb.Dataset('/input/tests/data/lgb_test.bin', reference=lgb_train)

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

    @gpu_test
    def test_gpu(self):
        lgb_train = lgb.Dataset('/input/tests/data/lgb_train.bin')
        lgb_eval = lgb.Dataset('/input/tests/data/lgb_test.bin', reference=lgb_train)

        params = {
            'boosting_type': 'gbdt',
            'objective': 'regression',
            'metric': 'auc',
            'num_leaves': 31,
            'learning_rate': 0.05,
            'feature_fraction': 0.9,
            'bagging_fraction': 0.8,
            'bagging_freq': 5,
            'verbose': 1,
            'device': 'gpu'
        }
        
        # Run only one round for faster test
        gbm = lgb.train(params,
                        lgb_train,
                        num_boost_round=1,
                        valid_sets=lgb_eval,
                        early_stopping_rounds=1)

        self.assertEqual(1, gbm.best_iteration)
