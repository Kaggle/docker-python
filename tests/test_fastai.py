import unittest

import fastai

from fastai.tabular.all import *

class TestFastAI(unittest.TestCase):
    # Basic import
    def test_basic(self):
        import fastai
        import fastcore
        import fastprogress
        import fastdownload

    def test_has_version(self):
        self.assertGreater(len(fastai.__version__), 2)
    
    # based on https://github.com/fastai/fastai/blob/master/tests/test_torch_core.py#L17
    def test_torch_tensor(self):
        a = tensor([1, 2, 3])
        b = torch.tensor([1, 2, 3])

        self.assertTrue(torch.all(a == b))

    def test_tabular(self):
        dls = TabularDataLoaders.from_csv(
            "/input/tests/data/train.csv",
            cont_names=["pixel"+str(i) for i in range(784)],
            y_names='label',
            procs=[FillMissing, Categorify, Normalize])
        learn = tabular_learner(dls, layers=[200, 100])
        with learn.no_bar():
            learn.fit_one_cycle(n_epoch=1)
        
            self.assertGreater(learn.smooth_loss, 0)
