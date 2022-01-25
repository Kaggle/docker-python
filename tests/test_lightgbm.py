import unittest

import lightgbm as lgb
import pandas as pd

from common import gpu_test

class TestLightgbm(unittest.TestCase):
    # Based on the "simple_example" from their documentation:
    # https://github.com/Microsoft/LightGBM/blob/master/examples/python-guide/simple_example.py
    def test_cpu(self):
        lgb_train, lgb_eval = self.load_datasets()

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
            'force_row_wise': True,
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
        lgb_train, lgb_eval = self.load_datasets()
        
        params = {
            'boosting_type': 'gbdt',
            'objective': 'regression',
            'metric': 'auc',
            'num_leaves': 31,
            'learning_rate': 0.05,
            'feature_fraction': 0.9,
            'bagging_fraction': 0.8,
            'bagging_freq': 5,
            'force_row_wise': True,
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
    
    def load_datasets(self):
        df_train = pd.read_csv('/input/tests/data/lgb_train.csv', header=None, sep='\t')
        df_test = pd.read_csv('/input/tests/data/lgb_test.csv', header=None, sep='\t')
        
        y_train = df_train[0]
        y_test = df_test[0]
        X_train = df_train.drop(0, axis=1)
        X_test = df_test.drop(0, axis=1)

        lgb_train = lgb.Dataset(X_train, y_train)
        lgb_eval = lgb.Dataset(X_test, y_test, reference=lgb_train)

        return (lgb_train, lgb_eval)
