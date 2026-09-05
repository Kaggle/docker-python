import unittest

from sklearn import datasets
from rslearn.linear_model import LogisticRegression
from rslearn.neighbors import KNNClassifier
from rslearn.metrics import evaluate_model # Evaluate any Kindof Model with return type of numpy array.

class TestRslearn(unittest.TestCase):
    def test_KNN_classifier(self):
        iris = datasets.load_iris()
        X, y = iris.data, iris.target
        clf1 = KNNClassifier(k_neighbors=3)
        clf1.fit(X,y, scale=True) # Auto Scale Data by default=True

    def test_logistic_classifier(self):
        iris = datasets.load_iris()
        X, y = iris.data, iris.target
        lr1 = LogisticRegression(solver="saga", lr=0.03)
        lr1.fit(X,y)

    def test_evaluates(self):
        iris = datasets.load_iris()
        X, y = iris.data, iris.target
        lr1 = LogisticRegression()
        lr1.fit(X,y)

        evaluations = lr1.evaluate(X=X, y_true=y)
        evals = evaluate_model(model=lr1, X=X, y_true=y, task="classification")


