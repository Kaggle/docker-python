import unittest

import pandas as pd
from pandarallel import pandarallel

pandarallel.initialize()

class TestPandarallel(unittest.TestCase):    
    def test_pandarallel(self):
        data = pd.read_csv("/input/tests/data/train.csv")
        data['label_converted'] = data['label'].parallel_apply(lambda x: x+1)
