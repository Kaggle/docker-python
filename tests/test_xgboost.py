import unittest

from sklearn import datasets
from xgboost import XGBClassifier

class TestXGBoost(unittest.TestCase):
    def test_classifier(self):
        boston = datasets.load_boston()
        X, y = boston.data, boston.target

        xgb1 = XGBClassifier(n_estimators=3)
        xgb1.fit(X[0:70],y[0:70])
