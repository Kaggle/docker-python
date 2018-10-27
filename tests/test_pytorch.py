import unittest

import torch
import torch.nn as tnn
import torch.autograd as autograd

from common import gpu_test


class TestPyTorch(unittest.TestCase):
    # PyTorch smoke test based on http://pytorch.org/tutorials/beginner/nlp/deep_learning_tutorial.html
    def test_nn(self):
        torch.manual_seed(31337)
        linear_torch = tnn.Linear(5,3)
        data_torch = autograd.Variable(torch.randn(2, 5))
        linear_torch(data_torch)

    @gpu_test
    def test_gpu_computation(self):
        cuda = torch.device('cuda')  
        a = torch.tensor([1., 2.], device=cuda)

        result = a.sum()

        self.assertEqual(torch.tensor([3.], device=cuda), result)

    @gpu_test
    def test_cuda_nn(self):
        # These throw if cuda is misconfigured
        tnn.GRUCell(10,10).cuda()
        tnn.RNNCell(10,10).cuda()
        tnn.LSTMCell(10,10).cuda()
        tnn.GRU(10,10).cuda()
        tnn.LSTM(10,10).cuda()
        tnn.RNN(10,10).cuda()
