import unittest

import fastai
import pandas as pd
import torch

from fastai.docs import *
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

        train_df, valid_df = df[:-5].copy(),df[-5:].copy()
        dep_var = "label"
        cont_names = []
        for i in range(784):
            cont_names.append("pixel" + str(i))

        data = tabular_data_from_df("", train_df, valid_df, dep_var, cont_names=cont_names, cat_names=[])
        learn = get_tabular_learner(data, layers=[200, 100])
        learn.fit(epochs=1)
