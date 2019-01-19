import numpy
import unittest

from chainer import cuda

from chainer_chemistry.models.mlp import MLP


class TestChainerChemistry(unittest.TestCase):

    def test_mlp(self):
        batch_size = 2
        input_dim = 16
        out_dim = 4

        model = MLP(out_dim=out_dim)
        data = numpy.random.rand(batch_size, input_dim).astype(numpy.float32)
        y_actual = cuda.to_cpu(model(data).data)
        assert y_actual.shape == (batch_size, out_dim)
