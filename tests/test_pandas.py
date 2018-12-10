import unittest

import pandas as pd

class TestPandas(unittest.TestCase):    
    def test_read_csv(self):
        data = pd.read_csv("/input/tests/data/train.csv")

        self.assertEqual(100, len(data.index))

    def test_read_feather(self):
        data = pd.read_feather("/input/tests/data/feather-0_3_1.feather")

        self.assertEqual(10, data.size)
