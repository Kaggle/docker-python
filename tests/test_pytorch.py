import unittest

import torch
import torch.nn as tnn
import torch.autograd as autograd

class TestPyTorch(unittest.TestCase):
    # PyTorch smoke test based on http://pytorch.org/tutorials/beginner/nlp/deep_learning_tutorial.html
    def test_nn(self):
        torch.manual_seed(31337)
        linear_torch = tnn.Linear(5,3)
        data_torch = autograd.Variable(torch.randn(2, 5))
        linear_torch(data_torch)
