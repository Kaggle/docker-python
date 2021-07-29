import unittest

# b/194837139 importing tensorflow before tfp was trigerring an error. Adding this import to prevent regression.
import tensorflow
import tensorflow_probability as tfp


class TestTensorFlowProbability(unittest.TestCase):
    def test_distribution(self):
        tfd = tfp.distributions
        dist = tfd.Bernoulli(logits=[-1, 1, 1])
        self.assertEqual('Bernoulli', dist.name)