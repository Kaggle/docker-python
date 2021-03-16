import unittest

import numpy as np
import xgboost

from distutils.version import StrictVersion
from xgboost import XGBClassifier

class TestXGBoost(unittest.TestCase):
    def test_version(self):
        # b/175051617 prevent xgboost version downgrade.
        self.assertGreaterEqual(StrictVersion(xgboost.__version__), StrictVersion("1.2.1"))

    def test_classifier(self):
        X_train = np.random.random((100, 28))
        y_train = np.random.randint(10, size=(100, 1))
        X_test = np.random.random((100, 28))
        y_test = np.random.randint(10, size=(100, 1))

        xgb1 = XGBClassifier(n_estimators=3, use_label_encoder=False)
        xgb1.fit(
            X_train, y_train,
            eval_set=[(X_train, y_train), (X_test, y_test)],
            eval_metric='mlogloss',
        )
        self.assertIn("validation_0", xgb1.evals_result())
