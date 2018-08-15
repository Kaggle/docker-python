import unittest

import pandas as pd

class TestPandas(unittest.TestCase):    
    def test_read_csv(self):
        data = pd.read_csv("/input/tests/data/train.csv")

        self.assertEqual(2, len(data.shape))
