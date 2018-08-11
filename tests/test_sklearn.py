import unittest

from sklearn import datasets
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LinearRegression

class TestSklearn(unittest.TestCase):
    def test_random_forest_classifier(self):
        iris = datasets.load_iris()
        X, y = iris.data, iris.target
        rf1 = RandomForestClassifier()
        rf1.fit(X,y)

    def test_linearn_classifier(self):
        boston = datasets.load_boston()
        X, y = boston.data, boston.target
        lr1 = LinearRegression()
        lr1.fit(X,y)
