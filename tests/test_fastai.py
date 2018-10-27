import unittest

import fastai
import pandas as pd
import torch

from fastai.core import partition
from fastai.layer_optimizer import LayerOptimizer

class TestFastAI(unittest.TestCase):
    def test_partition(self):
        result = partition([1,2,3,4,5], 2)

        self.assertEqual(3, len(result))

    # based on https://github.com/fastai/fastai/blob/0.7.0/tests/test_layer_optimizer.py
    def test_layer_optimizer(self):
        lo = LayerOptimizer(FakeOpt, fastai_params_('A', 'B', 'C'), 1e-2, 1e-4)
        fast_check_optimizer_(lo.opt, [(nm, 1e-2, 1e-4) for nm in 'ABC'])


class Par(object):
    def __init__(self, x, grad=True):
        self.x = x
        self.requires_grad = grad
    def parameters(self): return [self]


class FakeOpt(object):
    def __init__(self, params): self.param_groups = params


def fastai_params_(*names): return [Par(nm) for nm in names]

def fast_check_optimizer_(opt, expected):
    actual = opt.param_groups
    assert len(actual) == len(expected)
    for (a, e) in zip(actual, expected): fastai_check_param_(a, *e)

def fastai_check_param_(par, nm, lr, wd):
    assert par['params'][0].x == nm
    assert par['lr'] == lr
    assert par['weight_decay'] == wd
