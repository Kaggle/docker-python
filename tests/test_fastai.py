import unittest

import fastai
import pandas as pd
import torch

from fastai.tabular import *
from fastai.core import partition
from fastai.torch_core import tensor

class TestFastAI(unittest.TestCase):
    def test_partition(self):
        result = partition([1,2,3,4,5], 2)

        self.assertEqual(3, len(result))

    def test_has_version(self):
        self.assertGreater(len(fastai.__version__), 1)
    
    # based on https://github.com/fastai/fastai/blob/master/tests/test_torch_core.py#L17
    def test_torch_tensor(self):
        a = tensor([1, 2, 3])
        b = torch.tensor([1, 2, 3])

        self.assertTrue(torch.all(a == b))

    def test_tabular(self):
        df = pd.read_csv("/input/tests/data/train.csv")
        procs = [FillMissing, Categorify, Normalize]

        valid_idx = range(len(df)-5, len(df))
        dep_var = "label"
        cont_names = []
        for i in range(784):
            cont_names.append("pixel" + str(i))

        data = (TabularList.from_df(df, path="", cont_names=cont_names, cat_names=[], procs=procs)
            .split_by_idx(valid_idx)
            .label_from_df(cols=dep_var)
            .databunch())
        learn = tabular_learner(data, layers=[200, 100])
        learn.fit(epochs=1)
