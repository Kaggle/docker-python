import unittest

from sklearn import datasets
from rgf.sklearn import RGFClassifier

class TestRGF(unittest.TestCase):
    def test_classifier(self):
        iris = datasets.load_iris()
        X, y = iris.data, iris.target

        rgf = RGFClassifier(max_leaf=400,
            algorithm="RGF_Sib",
            test_interval=100,
            n_iter=1)

        rgf.fit(X,y)
        