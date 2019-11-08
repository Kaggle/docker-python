import unittest

from nimbusml import FileDataStream, Pipeline
from nimbusml.linear_model import FastLinearClassifier

class TestNimbusML(unittest.TestCase):

    def test_nimbusml_pipeline(self):
        data = FileDataStream.read_csv("/input/tests/data/train.csv", sep=",")

        # train a toy model with three features and two iterations
        model = Pipeline([
            FastLinearClassifier(
                feature=['pixel0', 'pixel1', 'pixel2'],
                label='label',
                maximum_number_of_iterations=2
        )])

        model.fit(data)

        metrics, predictions = model.test(data, output_scores=True)
